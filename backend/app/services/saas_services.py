"""Iteration 1: administrative subscriptions; no payment provider integration."""
from datetime import datetime, timezone
from fastapi import HTTPException
from psycopg2.errors import UndefinedTable
from psycopg2.extras import Json
from app.classes.postgres import transaction
from app.config import Config


def _schema():
    return Config.SCHEMA or 'comercio'


def _error(status, code, message):
    raise HTTPException(status_code=status, detail={'code': code, 'message': message})


def auditar(db, actor, empresa, accion, datos):
    db.execute_query(f'''INSERT INTO {_schema()}.t_bitacora
        (id_usuario,id_empresa,modulo,accion,entidad,resultado,nivel,descripcion,datos_nuevos)
        VALUES (%s,%s,'SAAS',%s,'empresa','EXITO','INFO',%s,%s)''',
        (actor.get('id_usuario') or actor.get('nro_usuario'), empresa, accion, accion, Json(datos)))


def listar_planes():
    try:
        with transaction() as db:
            rows = db.execute_query(f'SELECT codigo,nombre,max_sucursales,reportes_generativos,activo FROM {_schema()}.t_plan ORDER BY max_sucursales', fetchall=True)
            return [dict(zip(('codigo','nombre','max_sucursales','reportes_generativos','activo'), row)) for row in rows]
    except UndefinedTable:
        _error(503, 'MIGRACION_PENDIENTE', 'La migración SaaS todavía no fue aplicada.')


def actualizar_plan(codigo, nombre, activo, actor):
    with transaction() as db:
        row = db.execute_query(f'UPDATE {_schema()}.t_plan SET nombre=%s,activo=%s WHERE codigo=%s RETURNING codigo',
                               (nombre, activo, codigo), fetchone=True)
        if not row:
            _error(404, 'PLAN_NO_ENCONTRADO', 'Plan inexistente.')
        auditar(db, actor, None, 'PLAN_ACTUALIZADO', {'codigo': codigo, 'nombre': nombre, 'activo': activo})
    return next(p for p in listar_planes() if p['codigo'] == codigo)


def _empresa(db, empresa, lock=False):
    row = db.execute_query(f'SELECT estado FROM {_schema()}.empresa WHERE id_empresa=%s' + (' FOR UPDATE' if lock else ''),
                           (empresa,), fetchone=True)
    if not row:
        _error(404, 'EMPRESA_NO_ENCONTRADA', 'Empresa inexistente.')
    return row[0]


def historial(empresa):
    with transaction() as db:
        _empresa(db, empresa)
        rows = db.execute_query(f'''SELECT id_suscripcion,id_empresa,codigo_plan,inicio,fin,estado,motivo,creado_por,creado_en
            FROM {_schema()}.t_suscripcion WHERE id_empresa=%s ORDER BY inicio DESC,id_suscripcion DESC''', (empresa,), fetchall=True)
        return [dict(zip(('id_suscripcion','id_empresa','codigo_plan','inicio','fin','estado','motivo','creado_por','creado_en'), row)) for row in rows]


def consultar_plan(empresa):
    try:
        with transaction() as db:
            estado_empresa = _empresa(db, empresa)
            row = db.execute_query(f'''SELECT s.id_suscripcion,s.codigo_plan,s.inicio,s.fin,p.max_sucursales,p.reportes_generativos
                FROM {_schema()}.t_suscripcion s JOIN {_schema()}.t_plan p ON p.codigo=s.codigo_plan
                WHERE s.id_empresa=%s AND s.estado='ACTIVA' AND s.inicio<=now() AND s.fin>now()''', (empresa,), fetchone=True)
            usadas = db.execute_query(f'SELECT COUNT(*) FROM {_schema()}.t_sucursal WHERE id_empresa=%s AND COALESCE(activo,estado,FALSE)',
                                      (empresa,), fetchone=True)[0]
            estado = 'VIGENTE' if row else 'SIN_SUSCRIPCION'
            if not row:
                ultima = db.execute_query(f'''SELECT estado,fin,inicio FROM {_schema()}.t_suscripcion
                    WHERE id_empresa=%s ORDER BY fin DESC LIMIT 1''', (empresa,), fetchone=True)
                if ultima:
                    estado = 'CANCELADA' if ultima[0] == 'CANCELADA' else ('PROGRAMADA' if ultima[2] > datetime.now(timezone.utc) else 'VENCIDA')
            if estado_empresa != 'ACTIVO':
                estado = 'EMPRESA_INACTIVA'
            vigente = estado == 'VIGENTE'
            return {'id_empresa': empresa, 'estado': estado, 'vigente': vigente,
                    'id_suscripcion': row[0] if row else None, 'codigo_plan': row[1] if row else None,
                    'inicio': row[2] if row else None, 'fin': row[3] if row else None,
                    'limites': {'sucursales_activas': row[4] if row else None},
                    'uso': {'sucursales_activas': usadas},
                    'disponibles': max(0, row[4]-usadas) if vigente else 0,
                    'capacidades': {'reportes_generativos': bool(vigente and row[5]) if row else False}}
    except UndefinedTable:
        _error(503, 'MIGRACION_PENDIENTE', 'La migración SaaS todavía no fue aplicada.')


def exigir_vigencia(empresa, reportes=False):
    estado = consultar_plan(empresa)
    if not estado['vigente']:
        _error(403, 'SUSCRIPCION_NO_VIGENTE', 'La empresa no tiene una suscripción vigente.')
    if reportes and not estado['capacidades']['reportes_generativos']:
        _error(403, 'PLAN_NO_HABILITA_REPORTES', 'El motor de reportes requiere el plan Profesional.')
    return estado


def crear_suscripcion(empresa, datos, actor):
    inicio, fin = datos['inicio'], datos['fin']
    now = datetime.now(timezone.utc)
    if inicio.tzinfo is None or fin.tzinfo is None or fin <= inicio or fin <= now:
        _error(422, 'PERIODO_INVALIDO', 'Indique fechas con zona horaria, fin futuro y posterior al inicio.')
    with transaction() as db:
        if _empresa(db, empresa, lock=True) != 'ACTIVO':
            _error(409, 'EMPRESA_INACTIVA', 'Active la empresa antes de asignar la suscripción.')
        plan = db.execute_query(f'SELECT max_sucursales FROM {_schema()}.t_plan WHERE codigo=%s AND activo FOR SHARE', (datos['codigo_plan'],), fetchone=True)
        if not plan:
            _error(404, 'PLAN_NO_ENCONTRADO', 'El plan no existe o está inactivo.')
        usadas = db.execute_query(f'SELECT COUNT(*) FROM {_schema()}.t_sucursal WHERE id_empresa=%s AND COALESCE(activo,estado,FALSE)', (empresa,), fetchone=True)[0]
        if usadas > plan[0]:
            _error(409, 'LIMITE_SUCURSALES', 'Reduzca las sucursales activas antes de asignar este plan.')
        overlap = db.execute_query(f"SELECT 1 FROM {_schema()}.t_suscripcion WHERE id_empresa=%s AND estado='ACTIVA' AND inicio<%s AND fin>%s", (empresa, fin, inicio), fetchone=True)
        if overlap:
            _error(409, 'PERIODO_SOLAPADO', 'El periodo se superpone con otra suscripción activa.')
        row = db.execute_query(f'''INSERT INTO {_schema()}.t_suscripcion(id_empresa,codigo_plan,inicio,fin,motivo,creado_por)
            VALUES (%s,%s,%s,%s,%s,%s) RETURNING id_suscripcion''',
            (empresa, datos['codigo_plan'], inicio, fin, datos['motivo'], actor['id_usuario']), fetchone=True)
        auditar(db, actor, empresa, 'SUSCRIPCION_CREADA', {'id_suscripcion': row[0], 'codigo_plan': datos['codigo_plan'],
                'inicio': inicio.isoformat(), 'fin': fin.isoformat(), 'motivo': datos['motivo']})
    return next(s for s in historial(empresa) if s['id_suscripcion'] == row[0])


def cancelar_suscripcion(empresa, suscripcion, motivo, actor):
    with transaction() as db:
        _empresa(db, empresa, lock=True)
        row = db.execute_query(f'''UPDATE {_schema()}.t_suscripcion SET estado='CANCELADA'
            WHERE id_suscripcion=%s AND id_empresa=%s AND estado='ACTIVA' RETURNING id_suscripcion''', (suscripcion, empresa), fetchone=True)
        if not row:
            _error(404, 'SUSCRIPCION_NO_ENCONTRADA', 'Suscripción inexistente o ya cancelada.')
        auditar(db, actor, empresa, 'SUSCRIPCION_CANCELADA', {'id_suscripcion': suscripcion, 'motivo': motivo})
    return {'id_suscripcion': suscripcion, 'estado': 'CANCELADA'}
