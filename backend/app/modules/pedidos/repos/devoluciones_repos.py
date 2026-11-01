"""
AuroraStore Iteración 3 — Repositorio de Devoluciones (CU24W / CU25W)
Garantiza aislamiento multitenant, verificación de sucursales, concurrencia segura
mediante bloqueos FOR UPDATE y registro de movimientos de inventario.
"""
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime, timezone
import json
from fastapi import HTTPException, status
from app.core.postgres import PostgreSQL, atomic
from app.core.inventory_integrity import lock_items, lock_position
from app.modules.pedidos.repos.devolucion_importes import line_entitlements, partial_amount, cents
from decimal import Decimal
from app.core.config import Config

def _unique_items(items, key):
    ids = [int(item.get(key, 0)) for item in items]
    if not ids or any(value <= 0 for value in ids) or len(ids) != len(set(ids)):
        raise HTTPException(400, 'Debe indicar artículos válidos, sin detalles repetidos.')


def _check_sync(db, schema, sale, tenant):
    # Receipts store data.id_venta. Missing infrastructure must not fail open.
    if not db.execute_query('SELECT to_regclass(%s)', (f'{schema}.t_sync_operacion',), fetchone=True)[0]:
        raise HTTPException(503, 'No está disponible la verificación persistente de operaciones.')
    ready = db.execute_query('''SELECT EXISTS(SELECT 1 FROM information_schema.columns
        WHERE table_schema=%s AND table_name='t_sync_operacion' AND column_name='request_hash')''',
        (schema,), fetchone=True)
    if not ready or not ready[0]:
        raise HTTPException(503, 'Falta la infraestructura de huellas persistentes de operaciones.')
    rows = db.execute_query(f'''SELECT status,conflict_code,request_hash,response_json,
        operation_id::text,id_usuario,id_empresa FROM {schema}.t_sync_operacion
        WHERE id_empresa=%s AND COALESCE(response_json->'data'->>'id_venta',response_json->>'id_venta')=%s''',
        (tenant, str(sale)), fetchall=True) or []
    for row in rows:
        if row[0] != 'synced':
            return row[:2]
        receipt = row[3] if isinstance(row[3],dict) else {}
        expected = dict(operation_id=row[4],id_usuario=row[5],id_empresa=row[6],request_hash=row[2])
        if not row[2] or receipt.get('confirmation_verified') is not True or receipt.get('confirmation') != expected:
            return ('reconciliation_required','UNVERIFIED_SYNC_RECEIPT')
    return None


def _require_structure(db, schema):
    row = db.execute_query('''SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema=%s AND ((table_name='t_devolucion' AND column_name='codigo_devolucion')
        OR (table_name='t_detalle_devolucion' AND column_name='id_detalle_venta'))''', (schema,), fetchone=True)
    if not row or row[0] != 2:
        raise HTTPException(503, 'RETURNS_SCHEMA_NOT_READY: migración de devoluciones pendiente de aprobación; no se escribió la base.')


def _validate_branch(db, schema, branch, tenant):
    row = db.execute_query(f'SELECT id_empresa FROM {schema}.t_sucursal WHERE id_sucursal=%s FOR SHARE', (branch,), fetchone=True)
    if not row or row[0] != tenant:
        raise HTTPException(403, 'Sucursal ajena a la empresa de la venta.')


def contexto_devolucion(id_devolucion):
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        _require_structure(db,schema)
        row = db.execute_query(f'''SELECT d.id_empresa,d.id_sucursal,v.id_empresa,v.id_sucursal,s.id_empresa,src.id_empresa
            FROM {schema}.t_devolucion d JOIN {schema}.t_venta v ON v.id_venta=d.id_venta
            JOIN {schema}.t_sucursal s ON s.id_sucursal=d.id_sucursal
            JOIN {schema}.t_sucursal src ON src.id_sucursal=v.id_sucursal
            WHERE d.id_devolucion=%s''', (id_devolucion,), fetchone=True)
        if not row:
            raise HTTPException(404, 'Devolución no encontrada.')
        if row[0] != row[2] or row[0] != row[4] or row[0] != row[5]:
            raise HTTPException(409, 'RETURN_RECONCILIATION_REQUIRED: pertenencia inconsistente.')
        return row[0], row[1], row[3]
    finally:
        db.close_connection()


def _request_replay(db, schema, sale, user, kind, reason, description, evidence, items, branch=None):
    """Conservative replay: identical intent on a sale returns its persistent request.

    The locked sale serializes lookup/insert. An identical second intentional
    request needs a distinct description until explicit action keys are approved.
    """
    rows = db.execute_query(f'''SELECT id_devolucion,codigo_devolucion,estado,monto_reembolso,fecha_devolucion
        FROM {schema}.t_devolucion WHERE id_venta=%s AND id_usuario=%s AND tipo_devolucion=%s
        AND motivo=%s AND descripcion_cliente IS NOT DISTINCT FROM %s AND evidencia_url IS NOT DISTINCT FROM %s
        AND estado IS DISTINCT FROM 'RECHAZADA' AND (%s IS NULL OR id_sucursal=%s)
        ORDER BY id_devolucion''', (sale,user,kind,reason,description,evidence,branch,branch), fetchall=True) or []
    requested = sorted((int(i['id_detalle_venta']),int(i['cantidad']),i.get('condicion','REVENDIBLE').upper()) for i in items)
    for row in rows:
        details = db.execute_query(f'''SELECT id_detalle_venta,cantidad,COALESCE(condicion,'REVENDIBLE')
            FROM {schema}.t_detalle_devolucion WHERE id_devolucion=%s''', (row[0],), fetchall=True) or []
        if sorted(details) == requested:
            return dict(success=True,id_devolucion=row[0],codigo_devolucion=row[1],estado=row[2],
                        monto_reembolso=float(row[3]),fecha_devolucion=row[4].isoformat(),idempotent_replay=True)
    return None


def _check_money_cap(db,schema,sale,entitlements,details):
    rows = db.execute_query(f'''SELECT dd.id_detalle_venta,SUM(dd.monto_reembolso)
        FROM {schema}.t_detalle_devolucion dd JOIN {schema}.t_devolucion d ON d.id_devolucion=dd.id_devolucion
        WHERE d.id_venta=%s AND d.estado IS DISTINCT FROM 'RECHAZADA' GROUP BY dd.id_detalle_venta''', (sale,), fetchall=True) or []
    previous = {row[0]: cents(row[1]) for row in rows}
    for detail in details:
        key = detail['id_detalle_venta']
        if previous.get(key,0) + cents(detail['monto_reembolso']) > entitlements[key]:
            raise HTTPException(409, 'REFUND_RECONCILIATION_REQUIRED: importe acumulado superior al neto vendido.')

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

def _generar_codigo_devolucion() -> str:
    fecha_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    sufijo = uuid.uuid4().hex[:6].upper()
    return f"DEV-{fecha_str}-{sufijo}"

def consultar_venta_elegible(
    id_venta: int,
    id_usuario: int,
    id_empresa: Optional[int] = None,
    es_personal: bool = False,
    sucursales_autorizadas: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Consulta los datos de una venta y calcula los ítems y cantidades elegibles para devolución.
    Resta devoluciones previas que no hayan sido rechazadas.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        _require_structure(db,schema)

        # 1. Cabecera de la venta
        sql_venta = f"""
            SELECT 
                v.id_venta,
                v.numero_venta,
                v.fecha_venta,
                v.subtotal,
                v.descuento,
                v.total,
                v.estado,
                v.tipo_venta,
                v.id_empresa,
                v.id_sucursal,
                v.id_cliente,
                c.id_usuario AS id_usuario_cliente,
                s.nombre AS nombre_sucursal,
                emp.nombre_empresa
            FROM {schema}.t_venta v
            LEFT JOIN {schema}.t_cliente c ON c.id_cliente = v.id_cliente
            LEFT JOIN {schema}.t_sucursal s ON s.id_sucursal = v.id_sucursal
            LEFT JOIN {schema}.empresa emp ON emp.id_empresa = v.id_empresa
            WHERE v.id_venta = %s
            LIMIT 1;
        """
        row_v = db.execute_query(sql_venta, (id_venta,), fetchone=True)
        if not row_v:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada.")

        v_id, v_num, v_fecha, v_sub, v_desc, v_tot, v_estado, v_tipo, v_emp, v_suc, v_cli, v_uid_cli, v_suc_nom, v_emp_nom = row_v

        # 2. Validaciones de Autorización y Multitenant
        if id_empresa and v_emp != id_empresa:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene autorización para acceder a ventas de otra empresa.")

        if not es_personal:
            # Cliente autenticado: debe ser el dueño de la venta
            if v_uid_cli != id_usuario:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene autorización para consultar esta venta.")
        else:
            # Personal: validar sucursal si está restringida
            if sucursales_autorizadas is not None and v_suc not in sucursales_autorizadas:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos sobre la sucursal de esta venta.")

        _validate_branch(db,schema,v_suc,v_emp)
        # 3. Comprobar si la venta está completada/pagada
        estado_normalizado = (v_estado or "").strip().upper()
        es_elegible_estado = estado_normalizado in ('COMPLETADA', 'PAGADO', 'ENTREGADO')
        motivo_bloqueo = None
        if not es_elegible_estado:
            motivo_bloqueo = f"La venta se encuentra en estado '{v_estado}'. Solo pueden devolverse ventas completadas o pagadas."

        # 4. Comprobar si la venta está bajo conciliación o sin sincronizar en t_sync_operacion
        sync_row = _check_sync(db,schema,id_venta,v_emp)
        if sync_row:
            es_elegible_estado = False
            motivo_bloqueo = f'Venta pendiente de conciliacion central ({sync_row[1] or sync_row[0]}).'

        # 5. Obtener los ítems originales de la venta
        sql_items = f"""
            SELECT 
                dv.id_detalle_venta,
                dv.id_variante,
                dv.cantidad,
                dv.precio_unitario,
                dv.descuento,
                dv.subtotal,
                p.nombre AS producto_nombre,
                v.sku,
                t.nombre AS talla_nombre,
                col.nombre AS color_nombre,
                (
                    SELECT img.imagen_url 
                    FROM {schema}.t_producto_imagen img 
                    WHERE img.id_producto = p.id_producto 
                    ORDER BY img.es_principal DESC, img.orden ASC, img.id_imagen ASC 
                    LIMIT 1
                ) AS imagen_url
            FROM {schema}.t_detalle_venta dv
            JOIN {schema}.t_producto_talla_color v ON v.id_variante = dv.id_variante
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla
            JOIN {schema}.t_color col ON col.id_color = v.id_color
            WHERE dv.id_venta = %s
            ORDER BY dv.id_detalle_venta ASC;
        """
        rows_items = db.execute_query(sql_items, (id_venta,), fetchall=True) or []

        # 6. Calcular devoluciones activas o completadas para cada detalle de venta
        sql_dev_cant = f"""
            SELECT 
                dd.id_detalle_venta,
                COALESCE(SUM(dd.cantidad), 0) AS cant_devuelta
            FROM {schema}.t_detalle_devolucion dd
            JOIN {schema}.t_devolucion d ON d.id_devolucion = dd.id_devolucion
            WHERE d.id_venta = %s 
              AND d.estado IS DISTINCT FROM 'RECHAZADA'
            GROUP BY dd.id_detalle_venta;
        """
        rows_dev = db.execute_query(sql_dev_cant, (id_venta,), fetchall=True) or []
        mapa_devueltos = {r[0]: int(r[1]) for r in rows_dev}

        entitlements = line_entitlements(rows_items,v_sub,v_desc,v_tot)
        items_resultado = []
        total_elegible_general = 0

        for it in rows_items:
            id_det_v = it[0]
            cant_original = int(it[2])
            cant_devuelta = mapa_devueltos.get(id_det_v, 0)
            cant_elegible = max(0, cant_original - cant_devuelta)
            
            # Cálculo de precio neto unitario proporcional a los descuentos aplicados
            subtotal_det = float(it[5])
            precio_neto_unitario = float(Decimal(entitlements[id_det_v]) / Decimal(100) / cant_original)

            total_elegible_general += cant_elegible

            items_resultado.append({
                "id_detalle_venta": id_det_v,
                "id_variante": it[1],
                "cantidad_original": cant_original,
                "cantidad_devuelta": cant_devuelta,
                "cantidad_elegible": cant_elegible,
                "precio_unitario": float(it[3]),
                "descuento_unitario": float(it[4]),
                "subtotal": subtotal_det,
                "precio_neto_unitario": precio_neto_unitario,
                "producto_nombre": it[6],
                "sku": it[7],
                "talla": it[8],
                "color": it[9],
                "imagen_url": it[10]
            })

        if total_elegible_general == 0 and not motivo_bloqueo:
            es_elegible_estado = False
            motivo_bloqueo = "Todos los artículos de esta venta ya han sido devueltos o están en proceso de solicitud."

        return {
            "venta": {
                "id_venta": v_id,
                "numero_venta": v_num,
                "fecha_venta": v_fecha.isoformat() if hasattr(v_fecha, 'isoformat') else str(v_fecha),
                "subtotal": float(v_sub or 0),
                "descuento": float(v_desc or 0),
                "total": float(v_tot or 0),
                "estado": v_estado,
                "tipo_venta": v_tipo,
                "id_empresa": v_emp,
                "nombre_empresa": v_emp_nom,
                "id_sucursal": v_suc,
                "nombre_sucursal": v_suc_nom
            },
            "es_elegible": es_elegible_estado,
            "motivo_bloqueo": motivo_bloqueo,
            "items": items_resultado
        }
    finally:
        db.close_connection()

@atomic
def crear_solicitud_cliente(
    id_venta: int,
    id_usuario: int,
    id_empresa: int,
    motivo: str,
    descripcion: Optional[str],
    evidencia_url: Optional[str],
    items_solicitados: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    CU25W: Crea atómicamente una solicitud de devolución online en estado 'SOLICITADA'.
    Usa transacciones con bloqueos FOR UPDATE para evitar condiciones de carrera.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        _require_structure(db,schema)
        _unique_items(items_solicitados,"id_detalle_venta")
        
        # Iniciar transacción

        # Bloqueo y verificación de la venta
        sql_v = f"""
            SELECT id_venta, id_cliente, id_empresa, id_sucursal, estado, total, subtotal, descuento
            FROM {schema}.t_venta
            WHERE id_venta = %s
            FOR UPDATE;
        """
        row_v = db.execute_query(sql_v, (id_venta,), fetchone=True)
        if not row_v:
            db.rollback()
            raise HTTPException(status_code=404, detail="Venta no encontrada.")

        v_id, v_cli, v_emp, v_suc, v_estado, v_tot, v_sub, v_desc = row_v

        # Validar pertenencia del cliente
        owner = db.execute_query(f'SELECT id_usuario FROM {schema}.t_cliente WHERE id_cliente=%s', (v_cli,), fetchone=True)
        if not owner or owner[0] != id_usuario:
            db.rollback()
            raise HTTPException(status_code=403, detail="No tiene autorización para solicitar devoluciones sobre compras ajenas.")

        if id_empresa is not None and v_emp != id_empresa:
            db.rollback()
            raise HTTPException(status_code=403, detail="La venta no pertenece a la empresa actual.")

        id_empresa = v_emp
        _validate_branch(db,schema,v_suc,v_emp)
        if _check_sync(db,schema,id_venta,v_emp):
            raise HTTPException(409,'Venta pendiente de conciliacion central.')
        replay = _request_replay(db,schema,id_venta,id_usuario,'SOLICITUD_CLIENTE',motivo,descripcion,evidencia_url,items_solicitados)
        if replay:
            return replay

        estado_norm = (v_estado or "").strip().upper()
        if estado_norm not in ('COMPLETADA', 'PAGADO', 'ENTREGADO'):
            db.rollback()
            raise HTTPException(status_code=400, detail=f"No se pueden devolver ventas en estado '{v_estado}'.")

        # Bloqueo de los detalles de la venta
        sql_dv = f"""
            SELECT id_detalle_venta, id_variante, cantidad, precio_unitario, descuento, subtotal
            FROM {schema}.t_detalle_venta
            WHERE id_venta = %s
            FOR UPDATE;
        """
        rows_dv = db.execute_query(sql_dv, (id_venta,), fetchall=True) or []
        mapa_dv = {r[0]: r for r in rows_dv}
        entitlements = line_entitlements(rows_dv,v_sub,v_desc,v_tot)

        # Calcular cantidades devueltas previamente no rechazadas
        sql_dev = f"""
            SELECT dd.id_detalle_venta, COALESCE(SUM(dd.cantidad), 0)
            FROM {schema}.t_detalle_devolucion dd
            JOIN {schema}.t_devolucion d ON d.id_devolucion = dd.id_devolucion
            WHERE d.id_venta = %s AND d.estado IS DISTINCT FROM 'RECHAZADA'
            GROUP BY dd.id_detalle_venta;
        """
        rows_dev = db.execute_query(sql_dev, (id_venta,), fetchall=True) or []
        mapa_devueltas = {r[0]: int(r[1]) for r in rows_dev}

        # Validar ítems solicitados
        if not items_solicitados:
            db.rollback()
            raise HTTPException(status_code=400, detail="Debe seleccionar al menos un artículo para devolver.")

        monto_total_reembolso = Decimal('0.00')
        detalles_a_insertar = []

        for req in items_solicitados:
            id_det_v = req.get("id_detalle_venta")
            cant_req = int(req.get("cantidad", 0))

            if cant_req <= 0:
                db.rollback()
                raise HTTPException(status_code=400, detail="La cantidad a devolver debe ser mayor a 0.")

            if id_det_v not in mapa_dv:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"El detalle de venta {id_det_v} no pertenece a esta venta.")

            dv_row = mapa_dv[id_det_v]
            cant_original = int(dv_row[2])
            subtotal_orig = dv_row[5]
            cant_ya_dev = mapa_devueltas.get(id_det_v, 0)
            cant_disp = cant_original - cant_ya_dev

            if cant_req > cant_disp:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"La cantidad solicitada ({cant_req}) supera la cantidad elegible disponible ({cant_disp}) para el artículo."
                )

            # Cálculo de reembolso unitario neto
            subtotal_item_reembolso = partial_amount(entitlements[id_det_v],cant_original,cant_ya_dev,cant_req)
            monto_total_reembolso += subtotal_item_reembolso

            detalles_a_insertar.append({
                "id_detalle_venta": id_det_v,
                "cantidad": cant_req,
                "precio_unitario": dv_row[3],
                "descuento_unitario": dv_row[4],
                "monto_reembolso": subtotal_item_reembolso,
                "estado_item": "SOLICITADO"
            })

        _check_money_cap(db,schema,id_venta,entitlements,detalles_a_insertar)
        # Generar código de referencia
        codigo_dev = _generar_codigo_devolucion()

        # Insertar cabecera t_devolucion
        sql_ins_dev = f"""
            INSERT INTO {schema}.t_devolucion (
                id_venta, id_usuario, id_empresa, id_sucursal, codigo_devolucion,
                tipo_devolucion, motivo, descripcion_cliente, evidencia_url,
                monto_reembolso, estado, fecha_devolucion
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
            ) RETURNING id_devolucion, fecha_devolucion;
        """
        params_ins_dev = (
            id_venta, id_usuario, id_empresa, v_suc, codigo_dev,
            'SOLICITUD_CLIENTE', motivo, descripcion, evidencia_url,
            monto_total_reembolso, 'SOLICITADA'
        )
        row_dev = db.execute_query(sql_ins_dev, params_ins_dev, fetchone=True)
        id_devolucion, fecha_dev = row_dev

        # Insertar detalles en t_detalle_devolucion
        sql_ins_det = f"""
            INSERT INTO {schema}.t_detalle_devolucion (
                id_devolucion, id_detalle_venta, cantidad, precio_unitario,
                descuento_unitario, monto_reembolso, estado_item
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            );
        """
        for d in detalles_a_insertar:
            db.execute_query(sql_ins_det, (
                id_devolucion, d["id_detalle_venta"], d["cantidad"],
                d["precio_unitario"], d["descuento_unitario"],
                d["monto_reembolso"], d["estado_item"]
            ))

        db.commit()

        return {
            "success": True,
            "id_devolucion": id_devolucion,
            "codigo_devolucion": codigo_dev,
            "estado": "SOLICITADA",
            "monto_reembolso": float(monto_total_reembolso),
            "id_empresa": v_emp,
            "id_sucursal": v_suc,
            "fecha_devolucion": fecha_dev.isoformat() if hasattr(fecha_dev, 'isoformat') else str(fecha_dev)
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close_connection()

@atomic
def registrar_devolucion_presencial(
    id_venta: int,
    id_usuario_cajero: int,
    id_empresa: int,
    id_sucursal: int,
    motivo: str,
    observaciones: Optional[str],
    items_recibidos: List[Dict[str, Any]],
    registrar_reembolso_inmediato: bool = False,
    metodo_reembolso: Optional[str] = None,
    referencia_reembolso: Optional[str] = None
) -> Dict[str, Any]:
    """
    CU24W: Registra una devolución presencial directa en mostrador/caja.
    Ajusta inventario de forma atómica para unidades 'REVENDIBLE'.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        _require_structure(db,schema)
        _unique_items(items_recibidos,"id_detalle_venta")

        # Bloqueo y verificación de venta
        sql_v = f"""
            SELECT id_venta, id_empresa, id_sucursal, estado, total, id_cliente, subtotal, descuento
            FROM {schema}.t_venta
            WHERE id_venta = %s
            FOR UPDATE;
        """
        row_v = db.execute_query(sql_v, (id_venta,), fetchone=True)
        if not row_v:
            db.rollback()
            raise HTTPException(status_code=404, detail="Venta no encontrada.")

        v_id, v_emp, v_suc, v_estado, v_tot, v_cli, v_sub, v_desc = row_v

        if v_emp != id_empresa:
            db.rollback()
            raise HTTPException(status_code=403, detail="La venta no pertenece a la empresa actual.")

        _validate_branch(db,schema,id_sucursal,v_emp)
        if _check_sync(db,schema,id_venta,v_emp):
            raise HTTPException(409,'Venta pendiente de conciliacion central.')
        if registrar_reembolso_inmediato:
            raise HTTPException(409,'REFUND_EVIDENCE_REQUIRED: reembolso bloqueado hasta contar con evidencia financiera persistente y salida de caja.')
        replay = _request_replay(db,schema,id_venta,id_usuario_cajero,'PRESENCIAL_MOSTRADOR',motivo,None,None,items_recibidos,id_sucursal)
        if replay:
            return replay

        estado_norm = (v_estado or "").strip().upper()
        if estado_norm not in ('COMPLETADA', 'PAGADO', 'ENTREGADO'):
            db.rollback()
            raise HTTPException(status_code=400, detail=f"No se pueden devolver ventas en estado '{v_estado}'.")

        # Bloqueo de detalles de la venta
        sql_dv = f"""
            SELECT dv.id_detalle_venta, dv.id_variante, dv.cantidad, dv.precio_unitario, dv.descuento, dv.subtotal
            FROM {schema}.t_detalle_venta dv
            WHERE dv.id_venta = %s
            FOR UPDATE;
        """
        rows_dv = db.execute_query(sql_dv, (id_venta,), fetchall=True) or []
        mapa_dv = {r[0]: r for r in rows_dv}
        entitlements = line_entitlements(rows_dv,v_sub,v_desc,v_tot)

        # Calcular devueltas previas
        sql_dev = f"""
            SELECT dd.id_detalle_venta, COALESCE(SUM(dd.cantidad), 0)
            FROM {schema}.t_detalle_devolucion dd
            JOIN {schema}.t_devolucion d ON d.id_devolucion = dd.id_devolucion
            WHERE d.id_venta = %s AND d.estado IS DISTINCT FROM 'RECHAZADA'
            GROUP BY dd.id_detalle_venta;
        """
        rows_dev = db.execute_query(sql_dev, (id_venta,), fetchall=True) or []
        mapa_devueltas = {r[0]: int(r[1]) for r in rows_dev}

        if not items_recibidos:
            db.rollback()
            raise HTTPException(status_code=400, detail="Debe especificar al menos una prenda a devolver.")

        monto_total_reembolso = Decimal('0.00')
        detalles_a_procesar = []

        for req in items_recibidos:
            id_det_v = req.get("id_detalle_venta")
            cant_req = int(req.get("cantidad", 0))
            condicion = (req.get("condicion") or "REVENDIBLE").strip().upper()
            if condicion not in ('REVENDIBLE','DEFECTUOSO','NO_REVENDIBLE'):
                raise HTTPException(400,'Condicion de prenda invalida.')

            if cant_req <= 0:
                db.rollback()
                raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0.")

            if id_det_v not in mapa_dv:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"El ítem {id_det_v} no pertenece a la venta.")

            dv_row = mapa_dv[id_det_v]
            id_variante = dv_row[1]
            cant_orig = int(dv_row[2])
            subtotal_orig = dv_row[5]
            cant_ya_dev = mapa_devueltas.get(id_det_v, 0)
            cant_disp = cant_orig - cant_ya_dev

            if cant_req > cant_disp:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"La cantidad ({cant_req}) supera el saldo elegible ({cant_disp}) para el ítem {id_det_v}."
                )

            subtotal_item_reembolso = partial_amount(entitlements[id_det_v],cant_orig,cant_ya_dev,cant_req)
            monto_total_reembolso += subtotal_item_reembolso

            detalles_a_procesar.append({
                "id_detalle_venta": id_det_v,
                "id_variante": id_variante,
                "cantidad": cant_req,
                "condicion": condicion,
                "precio_unitario": dv_row[3],
                "descuento_unitario": dv_row[4],
                "monto_reembolso": subtotal_item_reembolso
            })

        _check_money_cap(db,schema,id_venta,entitlements,detalles_a_procesar)
        lock_items(db,schema,id_sucursal,detalles_a_procesar,id_empresa,allow_missing=True)
        # Determinar estado
        estado_final = "COMPLETADA" if registrar_reembolso_inmediato else "PENDIENTE_REEMBOLSO"
        codigo_dev = _generar_codigo_devolucion()

        # Insertar cabecera t_devolucion
        sql_ins_dev = f"""
            INSERT INTO {schema}.t_devolucion (
                id_venta, id_usuario, id_empresa, id_sucursal, codigo_devolucion,
                tipo_devolucion, motivo, observaciones_resolucion,
                monto_reembolso, estado, id_usuario_revisor, fecha_resolucion,
                metodo_reembolso, referencia_reembolso, fecha_reembolso, fecha_devolucion
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s,
                {"CURRENT_TIMESTAMP" if registrar_reembolso_inmediato else "NULL"}, CURRENT_TIMESTAMP
            ) RETURNING id_devolucion, fecha_devolucion;
        """
        params_ins_dev = (
            id_venta, id_usuario_cajero, id_empresa, id_sucursal, codigo_dev,
            'PRESENCIAL_MOSTRADOR', motivo, observaciones,
            monto_total_reembolso, estado_final, id_usuario_cajero,
            metodo_reembolso if registrar_reembolso_inmediato else None,
            referencia_reembolso if registrar_reembolso_inmediato else None
        )
        row_dev = db.execute_query(sql_ins_dev, params_ins_dev, fetchone=True)
        id_devolucion, fecha_dev = row_dev

        # Insertar detalles y ajustar stock si REVENDIBLE
        sql_ins_det = f"""
            INSERT INTO {schema}.t_detalle_devolucion (
                id_devolucion, id_detalle_venta, cantidad, condicion,
                precio_unitario, descuento_unitario, monto_reembolso, estado_item
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, 'RECIBIDO'
            );
        """

        for d in detalles_a_procesar:
            db.execute_query(sql_ins_det, (
                id_devolucion, d["id_detalle_venta"], d["cantidad"], d["condicion"],
                d["precio_unitario"], d["descuento_unitario"], d["monto_reembolso"]
            ))

            # Reincorporación a inventario únicamente si es REVENDIBLE
            if d["condicion"] == "REVENDIBLE":
                _reincorporar_stock_inventario(
                    db=db,
                    schema=schema,
                    id_sucursal=id_sucursal,
                    id_variante=d["id_variante"],
                    cantidad=d["cantidad"],
                    id_usuario=id_usuario_cajero,
                    motivo_log=f"Devolución presencial {codigo_dev}"
                )

        db.commit()

        return {
            "success": True,
            "id_devolucion": id_devolucion,
            "codigo_devolucion": codigo_dev,
            "estado": estado_final,
            "monto_reembolso": float(monto_total_reembolso),
            "id_empresa": v_emp,
            "id_sucursal": id_sucursal,
            "recepcion": items_recibidos,
            "fecha_devolucion": fecha_dev.isoformat() if hasattr(fecha_dev, 'isoformat') else str(fecha_dev)
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close_connection()

def _reincorporar_stock_inventario(
    db: PostgreSQL,
    schema: str,
    id_sucursal: int,
    id_variante: int,
    cantidad: int,
    id_usuario: int,
    motivo_log: str
) -> None:
    """
    Función interna que actualiza t_inventario y t_movimiento_inventario bajo la misma transacción.
    """
    lock_position(db,schema,id_sucursal,id_variante,allow_missing=True)
    # 1. Obtener o crear inventario para la variante en la sucursal
    sql_inv = f"""
        SELECT id_inventario, stock_actual, stock_disponible
        FROM {schema}.t_inventario
        WHERE id_sucursal = %s AND id_variante = %s
        FOR UPDATE;
    """
    inv_row = db.execute_query(sql_inv, (id_sucursal, id_variante), fetchone=True)
    if not inv_row:
        # Crear registro de inventario base si no existía en esta sucursal
        sql_crear_inv = f"""
            INSERT INTO {schema}.t_inventario (
                id_sucursal, id_variante, stock_actual, stock_reservado, stock_disponible, estado
            ) VALUES (
                %s, %s, %s, 0, %s, true
            ) RETURNING id_inventario;
        """
        nuevo_inv = db.execute_query(sql_crear_inv, (id_sucursal, id_variante, cantidad, cantidad), fetchone=True)
        id_inv = nuevo_inv[0]
        stock_ant = 0
        stock_nuevo = cantidad
    else:
        id_inv, stock_act, stock_disp = inv_row
        stock_ant = stock_act
        stock_nuevo = stock_act + cantidad
        stock_disp_nuevo = stock_disp + cantidad

        sql_upd_inv = f"""
            UPDATE {schema}.t_inventario
            SET stock_actual = %s,
                stock_disponible = %s,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id_inventario = %s;
        """
        db.execute_query(sql_upd_inv, (stock_nuevo, stock_disp_nuevo, id_inv))

    # 2. Registrar movimiento de inventario para trazabilidad completa
    sql_mov = f"""
        INSERT INTO {schema}.t_movimiento_inventario (
            id_inventario, id_usuario, tipo_movimiento, cantidad,
            stock_anterior, stock_nuevo, motivo, fecha_movimiento
        ) VALUES (
            %s, %s, 'ENTRADA', %s, %s, %s, %s, CURRENT_TIMESTAMP
        );
    """
    db.execute_query(sql_mov, (id_inv, id_usuario, cantidad, stock_ant, stock_nuevo, motivo_log))

    lock_position(db,schema,id_sucursal,id_variante)

def listar_devoluciones_cliente(
    id_usuario: int,
    id_empresa: Optional[int] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Lista las solicitudes de devolución del cliente autenticado con paginación.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        _require_structure(db,schema)

        condiciones = ["d.id_usuario = %s"]
        params: List[Any] = [id_usuario]

        if id_empresa and id_empresa > 0:
            condiciones.append("d.id_empresa = %s")
            params.append(id_empresa)

        where_cl = " AND ".join(condiciones)

        sql_total = f"SELECT COUNT(*) FROM {schema}.t_devolucion d WHERE {where_cl};"
        total = db.execute_query(sql_total, tuple(params), fetchone=True)[0]

        sql_data = f"""
            SELECT 
                d.id_devolucion,
                d.codigo_devolucion,
                d.id_venta,
                v.numero_venta,
                d.tipo_devolucion,
                d.motivo,
                d.descripcion_cliente,
                d.monto_reembolso,
                d.estado,
                d.fecha_devolucion,
                d.fecha_resolucion,
                d.observaciones_resolucion,
                s.nombre AS nombre_sucursal,
                (
                    SELECT COUNT(*) 
                    FROM {schema}.t_detalle_devolucion dd 
                    WHERE dd.id_devolucion = d.id_devolucion
                ) AS total_prendas
            FROM {schema}.t_devolucion d
            LEFT JOIN {schema}.t_venta v ON v.id_venta = d.id_venta
            LEFT JOIN {schema}.t_sucursal s ON s.id_sucursal = d.id_sucursal
            WHERE {where_cl}
            ORDER BY d.fecha_devolucion DESC
            LIMIT %s OFFSET %s;
        """
        params_data = tuple(params + [limit, offset])
        rows = db.execute_query(sql_data, params_data, fetchall=True) or []

        resultado = []
        for r in rows:
            resultado.append({
                "id_devolucion": r[0],
                "codigo_devolucion": r[1] or f"DEV-{r[0]}",
                "id_venta": r[2],
                "numero_venta": r[3],
                "tipo_devolucion": r[4],
                "motivo": r[5],
                "descripcion_cliente": r[6],
                "monto_reembolso": float(r[7] or 0),
                "estado": r[8],
                "fecha_devolucion": r[9].isoformat() if hasattr(r[9], 'isoformat') else str(r[9]),
                "fecha_resolucion": r[10].isoformat() if r[10] and hasattr(r[10], 'isoformat') else str(r[10]) if r[10] else None,
                "observaciones_resolucion": r[11],
                "nombre_sucursal": r[12],
                "total_prendas": int(r[13] or 0)
            })

        return {
            "total": total,
            "data": resultado
        }
    finally:
        db.close_connection()

def listar_devoluciones_personal(
    id_empresa: int,
    sucursales_autorizadas: Optional[List[int]] = None,
    estado: Optional[str] = None,
    id_sucursal: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    busqueda: Optional[str] = None,
    limit: int = 15,
    offset: int = 0
) -> Dict[str, Any]:
    """
    CU24W: Lista devoluciones para personal administrativo filtrando por tenant y sucursales.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        _require_structure(db,schema)

        condiciones = ["d.id_empresa = %s"]
        params: List[Any] = [id_empresa]

        # Restricción estricta de sucursales para cajero / encargado
        if sucursales_autorizadas is not None:
            if not sucursales_autorizadas:
                return {"total": 0, "data": []}
            condiciones.append("d.id_sucursal = ANY(%s)")
            params.append(sucursales_autorizadas)

        if id_sucursal and id_sucursal > 0:
            condiciones.append("d.id_sucursal = %s")
            params.append(id_sucursal)

        if estado and estado.strip() and estado.strip().upper() != 'TODOS':
            condiciones.append("d.estado = %s")
            params.append(estado.strip().upper())

        if fecha_inicio and fecha_inicio.strip():
            condiciones.append("d.fecha_devolucion >= %s")
            params.append(fecha_inicio.strip())

        if fecha_fin and fecha_fin.strip():
            condiciones.append("d.fecha_devolucion <= %s")
            params.append(fecha_fin.strip() + " 23:59:59")

        if busqueda and busqueda.strip():
            b = f"%{busqueda.strip()}%"
            condiciones.append("(d.codigo_devolucion ILIKE %s OR v.numero_venta ILIKE %s OR u.nombre ILIKE %s OR u.apellido ILIKE %s OR u.correo ILIKE %s)")
            params.extend([b, b, b, b, b])

        where_cl = " AND ".join(condiciones)

        sql_tot = f"""
            SELECT COUNT(*) 
            FROM {schema}.t_devolucion d
            LEFT JOIN {schema}.t_venta v ON v.id_venta = d.id_venta
            LEFT JOIN {schema}.t_usuario u ON u.id_usuario = d.id_usuario
            WHERE {where_cl};
        """
        total = db.execute_query(sql_tot, tuple(params), fetchone=True)[0]

        sql_data = f"""
            SELECT 
                d.id_devolucion,
                d.codigo_devolucion,
                d.id_venta,
                v.numero_venta,
                d.tipo_devolucion,
                d.motivo,
                d.monto_reembolso,
                d.estado,
                d.fecha_devolucion,
                d.fecha_resolucion,
                d.id_sucursal,
                s.nombre AS nombre_sucursal,
                u.nombre AS cliente_nombre,
                u.apellido AS cliente_apellido,
                u.correo AS cliente_correo,
                rev.nombre AS revisor_nombre,
                rev.apellido AS revisor_apellido,
                (
                    SELECT COUNT(*) 
                    FROM {schema}.t_detalle_devolucion dd 
                    WHERE dd.id_devolucion = d.id_devolucion
                ) AS total_prendas
            FROM {schema}.t_devolucion d
            LEFT JOIN {schema}.t_venta v ON v.id_venta = d.id_venta
            LEFT JOIN {schema}.t_sucursal s ON s.id_sucursal = d.id_sucursal
            LEFT JOIN {schema}.t_usuario u ON u.id_usuario = d.id_usuario
            LEFT JOIN {schema}.t_usuario rev ON rev.id_usuario = d.id_usuario_revisor
            WHERE {where_cl}
            ORDER BY d.fecha_devolucion DESC
            LIMIT %s OFFSET %s;
        """
        params_data = tuple(params + [limit, offset])
        rows = db.execute_query(sql_data, params_data, fetchall=True) or []

        resultado = []
        for r in rows:
            cliente_nom = f"{r[12] or ''} {r[13] or ''}".strip() or "Cliente Mostrador"
            revisor_nom = f"{r[15] or ''} {r[16] or ''}".strip() if r[15] else None

            resultado.append({
                "id_devolucion": r[0],
                "codigo_devolucion": r[1] or f"DEV-{r[0]}",
                "id_venta": r[2],
                "numero_venta": r[3],
                "tipo_devolucion": r[4],
                "motivo": r[5],
                "monto_reembolso": float(r[6] or 0),
                "estado": r[7],
                "fecha_devolucion": r[8].isoformat() if hasattr(r[8], 'isoformat') else str(r[8]),
                "fecha_resolucion": r[9].isoformat() if r[9] and hasattr(r[9], 'isoformat') else str(r[9]) if r[9] else None,
                "id_sucursal": r[10],
                "nombre_sucursal": r[11],
                "cliente_nombre": cliente_nom,
                "cliente_correo": r[14],
                "revisor_nombre": revisor_nom,
                "total_prendas": int(r[17] or 0)
            })

        return {
            "total": total,
            "data": resultado
        }
    finally:
        db.close_connection()

def obtener_detalle_devolucion(
    id_devolucion: int,
    id_usuario: int,
    id_empresa: Optional[int] = None,
    es_personal: bool = False,
    sucursales_autorizadas: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Retorna el detalle completo de una devolución (cabecera, venta, prendas, resolución y reembolso).
    Verifica pertenencia y aislamiento multitenant.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        _require_structure(db,schema)

        sql_head = f"""
            SELECT 
                d.id_devolucion,
                d.codigo_devolucion,
                d.id_venta,
                v.numero_venta,
                v.total AS total_venta,
                v.fecha_venta,
                v.tipo_venta,
                d.id_empresa,
                d.id_sucursal,
                s.nombre AS nombre_sucursal,
                d.id_usuario,
                u.nombre AS cliente_nombre,
                u.apellido AS cliente_apellido,
                u.correo AS cliente_correo,
                d.tipo_devolucion,
                d.motivo,
                d.descripcion_cliente,
                d.evidencia_url,
                d.monto_reembolso,
                d.estado,
                d.id_usuario_revisor,
                rev.nombre AS revisor_nombre,
                rev.apellido AS revisor_apellido,
                d.fecha_resolucion,
                d.observaciones_resolucion,
                d.metodo_reembolso,
                d.referencia_reembolso,
                d.fecha_reembolso,
                d.fecha_devolucion
            FROM {schema}.t_devolucion d
            LEFT JOIN {schema}.t_venta v ON v.id_venta = d.id_venta
            LEFT JOIN {schema}.t_sucursal s ON s.id_sucursal = d.id_sucursal
            LEFT JOIN {schema}.t_usuario u ON u.id_usuario = d.id_usuario
            LEFT JOIN {schema}.t_usuario rev ON rev.id_usuario = d.id_usuario_revisor
            WHERE d.id_devolucion = %s
            LIMIT 1;
        """
        row = db.execute_query(sql_head, (id_devolucion,), fetchone=True)
        if not row:
            raise HTTPException(status_code=404, detail="Devolución no encontrada.")

        # Validar permisos
        v_emp = row[7]
        v_suc = row[8]
        v_uid = row[10]

        if id_empresa and v_emp != id_empresa:
            raise HTTPException(status_code=403, detail="No tiene autorización sobre devoluciones de otra empresa.")

        if not es_personal:
            if v_uid != id_usuario:
                raise HTTPException(status_code=403, detail="No tiene autorización para consultar devoluciones ajenas.")
        else:
            if sucursales_autorizadas is not None and v_suc not in sucursales_autorizadas:
                raise HTTPException(status_code=403, detail="No tiene autorización sobre la sucursal de esta devolución.")

        # Obtener prendas de la devolución
        sql_items = f"""
            SELECT 
                dd.id_detalle_devolucion,
                dd.id_detalle_venta,
                dd.cantidad,
                COALESCE(dd.condicion, 'REVENDIBLE') AS condicion,
                dd.precio_unitario,
                dd.descuento_unitario,
                dd.monto_reembolso,
                COALESCE(dd.estado_item, 'SOLICITADO') AS estado_item,
                p.nombre AS producto_nombre,
                v.sku,
                t.nombre AS talla_nombre,
                col.nombre AS color_nombre,
                (
                    SELECT img.imagen_url 
                    FROM {schema}.t_producto_imagen img 
                    WHERE img.id_producto = p.id_producto 
                    ORDER BY img.es_principal DESC, img.orden ASC, img.id_imagen ASC 
                    LIMIT 1
                ) AS imagen_url
            FROM {schema}.t_detalle_devolucion dd
            JOIN {schema}.t_detalle_venta dv ON dv.id_detalle_venta = dd.id_detalle_venta
            JOIN {schema}.t_producto_talla_color v ON v.id_variante = dv.id_variante
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla
            JOIN {schema}.t_color col ON col.id_color = v.id_color
            WHERE dd.id_devolucion = %s
            ORDER BY dd.id_detalle_devolucion ASC;
        """
        rows_it = db.execute_query(sql_items, (id_devolucion,), fetchall=True) or []
        items = []
        for it in rows_it:
            items.append({
                "id_detalle_devolucion": it[0],
                "id_detalle_venta": it[1],
                "cantidad": it[2],
                "condicion": it[3],
                "precio_unitario": float(it[4] or 0),
                "descuento_unitario": float(it[5] or 0),
                "monto_reembolso": float(it[6] or 0),
                "estado_item": it[7],
                "producto_nombre": it[8],
                "sku": it[9],
                "talla": it[10],
                "color": it[11],
                "imagen_url": it[12]
            })

        cliente_nom = f"{row[11] or ''} {row[12] or ''}".strip() or "Cliente"
        revisor_nom = f"{row[21] or ''} {row[22] or ''}".strip() if row[21] else None

        return {
            "id_devolucion": row[0],
            "codigo_devolucion": row[1] or f"DEV-{row[0]}",
            "id_venta": row[2],
            "numero_venta": row[3],
            "total_venta": float(row[4] or 0),
            "fecha_venta": row[5].isoformat() if hasattr(row[5], 'isoformat') else str(row[5]),
            "tipo_venta": row[6],
            "id_empresa": row[7],
            "id_sucursal": row[8],
            "nombre_sucursal": row[9],
            "id_usuario_cliente": row[10],
            "cliente_nombre": cliente_nom,
            "cliente_correo": row[13],
            "tipo_devolucion": row[14],
            "motivo": row[15],
            "descripcion_cliente": row[16],
            "evidencia_url": row[17],
            "monto_reembolso": float(row[18] or 0),
            "estado": row[19],
            "id_usuario_revisor": row[20],
            "revisor_nombre": revisor_nom,
            "fecha_resolucion": row[23].isoformat() if row[23] and hasattr(row[23], 'isoformat') else str(row[23]) if row[23] else None,
            "observaciones_resolucion": row[24],
            "metodo_reembolso": row[25],
            "referencia_reembolso": row[26],
            "fecha_reembolso": row[27].isoformat() if row[27] and hasattr(row[27], 'isoformat') else str(row[27]) if row[27] else None,
            "fecha_devolucion": row[28].isoformat() if hasattr(row[28], 'isoformat') else str(row[28]),
            "items": items
        }
    finally:
        db.close_connection()

@atomic
def resolver_solicitud_devolucion(
    id_devolucion: int,
    id_usuario_revisor: int,
    id_empresa: int,
    nuevo_estado: str,
    observaciones: str
) -> Dict[str, Any]:
    """
    CU24W: Aprueba o rechaza una solicitud de devolución.
    Transiciones válidas:
      - SOLICITADA -> EN_REVISION, APROBADA, RECHAZADA
      - EN_REVISION -> APROBADA, RECHAZADA
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        _require_structure(db,schema)

        sql_dev = f"""
            SELECT id_devolucion, id_empresa, estado
            FROM {schema}.t_devolucion
            WHERE id_devolucion = %s
            FOR UPDATE;
        """
        row = db.execute_query(sql_dev, (id_devolucion,), fetchone=True)
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail="Devolución no encontrada.")

        v_id, v_emp, v_est_act = row
        if v_emp != id_empresa:
            db.rollback()
            raise HTTPException(status_code=403, detail="No tiene autorización sobre la empresa de esta devolución.")

        estado_act = (v_est_act or "").strip().upper()
        estado_dest = (nuevo_estado or "").strip().upper()

        transiciones_validas = {
            "SOLICITADA": ["EN_REVISION", "APROBADA", "RECHAZADA"],
            "EN_REVISION": ["APROBADA", "RECHAZADA"]
        }

        if estado_dest not in transiciones_validas.get(estado_act, []):
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Transición inválida: no se puede pasar de '{estado_act}' a '{estado_dest}'."
            )

        # Si es aprobada, pasa a PENDIENTE_RECEPCION
        estado_asignar = "PENDIENTE_RECEPCION" if estado_dest == "APROBADA" else estado_dest

        sql_upd = f"""
            UPDATE {schema}.t_devolucion
            SET estado = %s,
                id_usuario_revisor = %s,
                observaciones_resolucion = %s,
                fecha_resolucion = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id_devolucion = %s;
        """
        db.execute_query(sql_upd, (estado_asignar, id_usuario_revisor, observaciones, id_devolucion))
        db.commit()

        return {
            "success": True,
            "id_devolucion": id_devolucion,
            "estado_anterior": estado_act,
            "nuevo_estado": estado_asignar,
            "observaciones": observaciones
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close_connection()

@atomic
def registrar_recepcion_prendas(
    id_devolucion: int,
    id_usuario_receptor: int,
    id_empresa: int,
    id_sucursal_recepcion: int,
    observaciones: Optional[str],
    items_inspeccionados: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    CU24W: Registra la recepción física de las prendas inspeccionadas.
    Ajusta el inventario vendible solo para unidades marcadas como REVENDIBLE.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        _require_structure(db,schema)

        sql_dev = f"""
            SELECT id_devolucion, id_empresa, id_sucursal, codigo_devolucion, estado
            FROM {schema}.t_devolucion
            WHERE id_devolucion = %s
            FOR UPDATE;
        """
        row = db.execute_query(sql_dev, (id_devolucion,), fetchone=True)
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail="Devolución no encontrada.")

        d_id, d_emp, d_suc_orig, d_cod, d_estado = row
        if d_emp != id_empresa:
            db.rollback()
            raise HTTPException(status_code=403, detail="No tiene permisos sobre la empresa de esta devolución.")

        estado_act = (d_estado or "").strip().upper()
        sucursal_destino = id_sucursal_recepcion or d_suc_orig
        _validate_branch(db,schema,sucursal_destino,d_emp)

        # Obtener detalles de la devolución con sus variantes
        sql_det = f"""
            SELECT dd.id_detalle_devolucion, dd.id_detalle_venta, dd.cantidad, dv.id_variante,dd.condicion,dd.estado_item,dv.id_venta
            FROM {schema}.t_detalle_devolucion dd
            JOIN {schema}.t_detalle_venta dv ON dv.id_detalle_venta = dd.id_detalle_venta
            WHERE dd.id_devolucion = %s
            FOR UPDATE;
        """
        rows_det = db.execute_query(sql_det, (id_devolucion,), fetchall=True) or []
        mapa_det = {r[0]: r for r in rows_det}

        if not items_inspeccionados:
            db.rollback()
            raise HTTPException(status_code=400, detail="Debe detallar los artículos inspeccionados.")

        _unique_items(items_inspeccionados,'id_detalle_devolucion')
        if set(mapa_det) != {int(it['id_detalle_devolucion']) for it in items_inspeccionados}:
            raise HTTPException(409,'PARTIAL_RECEIPT_REQUIRES_MIGRATION: debe recibir todas las lineas completas.')
        sale = db.execute_query(f'SELECT id_venta FROM {schema}.t_devolucion WHERE id_devolucion=%s', (id_devolucion,), fetchone=True)[0]
        for it in items_inspeccionados:
            stored = mapa_det[int(it['id_detalle_devolucion'])]
            if stored[6] != sale:
                raise HTTPException(409,'RETURN_RECONCILIATION_REQUIRED: detalle de venta ajeno.')
            if int(it.get('cantidad_recibida',0)) != int(stored[2]):
                raise HTTPException(409,'PARTIAL_RECEIPT_REQUIRES_MIGRATION: cantidad parcial no persistible en 005.')
            if it.get('condicion','REVENDIBLE').upper() not in ('REVENDIBLE','DEFECTUOSO','NO_REVENDIBLE'):
                raise HTTPException(400,'Condicion invalida.')
        if estado_act in ('PENDIENTE_REEMBOLSO','RECIBIDA'):
            evidence = db.execute_query(f'''SELECT datos_nuevos FROM {schema}.t_bitacora WHERE entidad='t_devolucion' AND id_entidad=%s AND accion='RECEPCION_PRENDAS_DEVOLUCION' ORDER BY id_bitacora DESC LIMIT 1''', (str(id_devolucion),), fetchone=True)
            received = evidence[0] if evidence else {}
            def canonical(items):
                return sorted((int(i['id_detalle_devolucion']),int(i['cantidad_recibida']),i.get('condicion','REVENDIBLE').upper()) for i in items)
            if received.get('id_sucursal') == sucursal_destino and canonical(received.get('items_recibidos',[])) == canonical(items_inspeccionados):
                return dict(success=True,id_devolucion=id_devolucion,nuevo_estado=estado_act,idempotent_replay=True)
            raise HTTPException(409,'Recepcion ya registrada; concilie la evidencia existente.')
        if estado_act not in ('APROBADA', 'PENDIENTE_RECEPCION'):
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"No se pueden recibir prendas de una devolución en estado '{estado_act}' (debe estar APROBADA o PENDIENTE_RECEPCION)."
            )

        lock_items(db,schema,sucursal_destino,[dict(id_variante=r[3],cantidad=r[2]) for r in rows_det],id_empresa,allow_missing=True)

        for item in items_inspeccionados:
            id_det_dev = item.get("id_detalle_devolucion")
            cant_rec = int(item.get("cantidad_recibida", 0))
            condicion = (item.get("condicion") or "REVENDIBLE").strip().upper()

            if id_det_dev not in mapa_det:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"Detalle {id_det_dev} no pertenece a esta devolución.")

            det_info = mapa_det[id_det_dev]
            cant_solicitada = int(det_info[2])
            id_variante = det_info[3]

            if cant_rec <= 0 or cant_rec > cant_solicitada:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Cantidad recibida ({cant_rec}) inválida para ítem {id_det_dev} (solicitadas: {cant_solicitada})."
                )

            # Actualizar detalle de devolución
            sql_upd_det = f"""
                UPDATE {schema}.t_detalle_devolucion
                SET condicion = %s,
                    estado_item = 'RECIBIDO'
                WHERE id_detalle_devolucion = %s;
            """
            db.execute_query(sql_upd_det, (condicion, id_det_dev))

            # Reincorporación a inventario únicamente si es REVENDIBLE
            if condicion == "REVENDIBLE":
                _reincorporar_stock_inventario(
                    db=db,
                    schema=schema,
                    id_sucursal=sucursal_destino,
                    id_variante=id_variante,
                    cantidad=cant_rec,
                    id_usuario=id_usuario_receptor,
                    motivo_log=f"Recepción devolución {d_cod}"
                )

        # Actualizar estado de la devolución
        sql_upd_dev = f"""
            UPDATE {schema}.t_devolucion
            SET estado = 'PENDIENTE_REEMBOLSO',
                observaciones_resolucion = COALESCE(observaciones_resolucion, '') || ' | ' || %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id_devolucion = %s;
        """
        db.execute_query(sql_upd_dev, (observaciones or "Prendas recibidas e inspeccionadas.", id_devolucion))
        db.commit()

        return {
            "success": True,
            "id_devolucion": id_devolucion,
            "nuevo_estado": "PENDIENTE_REEMBOLSO",
            "items_recibidos": items_inspeccionados,
            "id_usuario_receptor": id_usuario_receptor,
            "id_sucursal": sucursal_destino,
            "mensaje": "Prendas recibidas y stock actualizado para artículos revendibles."
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close_connection()

@atomic
def registrar_reembolso_financiero(
    id_devolucion: int,
    id_usuario_responsable: int,
    id_empresa: int,
    metodo_reembolso: str,
    referencia_reembolso: str,
    observaciones: Optional[str]
) -> Dict[str, Any]:
    """
    CU24W: Registra formalmente el reembolso monetario al cliente.
    Actualiza la devolución a estado 'COMPLETADA'.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        _require_structure(db,schema)

        sql_dev = f"""
            SELECT id_devolucion, id_empresa, monto_reembolso, estado, codigo_devolucion
            FROM {schema}.t_devolucion
            WHERE id_devolucion = %s
            FOR UPDATE;
        """
        row = db.execute_query(sql_dev, (id_devolucion,), fetchone=True)
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail="Devolución no encontrada.")

        d_id, d_emp, d_monto, d_estado, d_cod = row
        if d_emp != id_empresa:
            db.rollback()
            raise HTTPException(status_code=403, detail="No tiene permisos sobre la empresa de esta devolución.")

        estado_act = (d_estado or "").strip().upper()
        if estado_act not in ('PENDIENTE_REEMBOLSO', 'RECIBIDA'):
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"La devolución debe encontrarse en estado 'PENDIENTE_REEMBOLSO' o 'RECIBIDA' (estado actual: '{estado_act}')."
            )

        if not metodo_reembolso or not referencia_reembolso:
            db.rollback()
            raise HTTPException(status_code=400, detail="Debe proporcionar el método de pago y número de comprobante/referencia del reembolso.")

        raise HTTPException(409,'REFUND_EVIDENCE_REQUIRED: falta registro financiero verificable; no se liquido ni cambio el estado.')
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close_connection()
