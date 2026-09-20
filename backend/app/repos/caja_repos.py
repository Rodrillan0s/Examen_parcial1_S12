import logging
from typing import Dict, Any, List, Optional
from app.classes.postgres import PostgreSQL
from app.config import Config

logger = logging.getLogger(__name__)

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

def obtener_denominaciones_activas() -> List[Dict[str, Any]]:
    """
    Retorna la lista de billetes y monedas configuradas activas,
    ordenadas según su denominación.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        q = f"""
            SELECT id_denominacion, valor, moneda, tipo, orden
            FROM {schema}.t_denominacion
            WHERE activo = TRUE
            ORDER BY orden ASC, valor DESC;
        """
        rows = db.execute_query(q, fetchall=True) or []
        resultado = []
        for r in rows:
            resultado.append({
                "id_denominacion": r[0],
                "valor": float(r[1]),
                "moneda": r[2],
                "tipo": r[3],
                "orden": r[4]
            })
        return resultado
    finally:
        db.close_connection()

def obtener_sesion_activa_usuario(id_usuario: int, id_sucursal: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Obtiene la sesión de caja actualmente ABIERTA para el usuario/cajero y sucursal.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        sucursal_clause = "AND s.id_sucursal = %s" if id_sucursal else ""
        params = [id_usuario]
        if id_sucursal:
            params.append(id_sucursal)

        q = f"""
            SELECT 
                s.id_sesion_caja,
                s.id_caja,
                s.id_usuario,
                s.id_sucursal,
                s.id_empresa,
                s.fecha_apertura,
                s.monto_inicial,
                s.estado,
                s.observacion_apertura,
                c.codigo_caja,
                c.nombre AS nombre_caja,
                suc.nombre AS nombre_sucursal,
                emp.nombre_empresa,
                u.nombre AS nombre_cajero,
                u.apellido AS apellido_cajero
            FROM {schema}.t_caja_sesion s
            JOIN {schema}.t_caja c ON c.id_caja = s.id_caja
            JOIN {schema}.t_sucursal suc ON suc.id_sucursal = s.id_sucursal
            LEFT JOIN {schema}.empresa emp ON emp.id_empresa = s.id_empresa
            JOIN {schema}.t_usuario u ON u.id_usuario = s.id_usuario
            WHERE s.id_usuario = %s AND s.estado = 'ABIERTA' {sucursal_clause}
            ORDER BY s.id_sesion_caja DESC
            LIMIT 1;
        """
        row = db.execute_query(q, tuple(params), fetchone=True)
        if not row:
            return None

        return {
            "id_sesion_caja": row[0],
            "id_caja": row[1],
            "id_usuario": row[2],
            "id_sucursal": row[3],
            "id_empresa": row[4],
            "fecha_apertura": row[5].isoformat() if row[5] else None,
            "monto_inicial": float(row[6]),
            "estado": row[7],
            "observacion_apertura": row[8],
            "codigo_caja": row[9],
            "nombre_caja": row[10],
            "nombre_sucursal": row[11],
            "nombre_empresa": row[12] or "Aurora Store",
            "cajero_nombre_completo": f"{row[13]} {row[14]}".strip()
        }
    finally:
        db.close_connection()

def obtener_caja_disponible_sucursal(id_sucursal: int, id_empresa: int) -> Dict[str, Any]:
    """
    Retorna la caja principal de la sucursal o crea una si no existe.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        q = f"""
            SELECT id_caja, codigo_caja, nombre, estado
            FROM {schema}.t_caja
            WHERE id_sucursal = %s AND estado = 'ACTIVA'
            ORDER BY id_caja ASC
            LIMIT 1;
        """
        row = db.execute_query(q, (id_sucursal,), fetchone=True)
        if row:
            return {
                "id_caja": row[0],
                "codigo_caja": row[1],
                "nombre": row[2],
                "estado": row[3]
            }

        # Si no existe, crear Caja 01
        q_suc = f"SELECT nombre FROM {schema}.t_sucursal WHERE id_sucursal = %s;"
        nom_suc_row = db.execute_query(q_suc, (id_sucursal,), fetchone=True)
        nombre_suc = nom_suc_row[0] if nom_suc_row else f"Sucursal {id_sucursal}"

        q_insert = f"""
            INSERT INTO {schema}.t_caja (id_sucursal, id_empresa, codigo_caja, nombre, estado)
            VALUES (%s, %s, %s, %s, 'ACTIVA')
            RETURNING id_caja, codigo_caja, nombre, estado;
        """
        cod = f"CAJA-SUC-{id_sucursal}-01"
        nom = f"Caja 01 - {nombre_suc}"
        new_row = db.execute_query(q_insert, (id_sucursal, id_empresa, cod, nom), fetchone=True, commit=True)
        return {
            "id_caja": new_row[0],
            "codigo_caja": new_row[1],
            "nombre": new_row[2],
            "estado": new_row[3]
        }
    finally:
        db.close_connection()

def verificar_caja_ocupada(id_caja: int) -> Optional[int]:
    """
    Verifica si una caja física ya tiene una sesión abierta activa.
    Retorna el id_sesion_caja si está ocupada, o None si está libre.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        q = f"""
            SELECT id_sesion_caja FROM {schema}.t_caja_sesion
            WHERE id_caja = %s AND estado = 'ABIERTA'
            LIMIT 1;
        """
        row = db.execute_query(q, (id_caja,), fetchone=True)
        return row[0] if row else None
    finally:
        db.close_connection()

def abrir_caja_sesion(
    id_usuario: int,
    id_sucursal: int,
    id_empresa: int,
    id_caja: int,
    conteo_items: List[Dict[str, Any]],
    observacion: Optional[str] = None
) -> Dict[str, Any]:
    """
    Abre una nueva sesión de caja mediante conteo físico de billetes y monedas.
    Recalcula estrictamente el fondo inicial en el servidor.
    """
    # 1. Obtener denominaciones activas para validar y multiplicar
    denominaciones = {d["id_denominacion"]: d for d in obtener_denominaciones_activas()}

    total_recalculado = 0.00
    detalles_para_insertar = []

    for item in conteo_items:
        id_denom = item.get("id_denominacion")
        cant = item.get("cantidad", 0)

        if cant is None or cant < 0:
            raise ValueError("Las cantidades de denominaciones no pueden ser negativas.")

        if id_denom not in denominaciones:
            raise ValueError(f"Denominación con ID {id_denom} no es válida o se encuentra inactiva.")

        if cant > 0:
            val = denominaciones[id_denom]["valor"]
            subtot = round(val * cant, 2)
            total_recalculado += subtot
            detalles_para_insertar.append((id_denom, val, cant, subtot))

    total_recalculado = round(total_recalculado, 2)

    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        # Verificar que el usuario no tenga OTRA caja abierta
        q_check_user = f"""
            SELECT id_sesion_caja FROM {schema}.t_caja_sesion
            WHERE id_usuario = %s AND estado = 'ABIERTA'
            LIMIT 1;
        """
        user_open = db.execute_query(q_check_user, (id_usuario,), fetchone=True)
        if user_open:
            raise ValueError("El usuario ya tiene una sesión de caja abierta activa.")

        # Verificar que la caja física no esté abierta por otro usuario
        q_check_caja = f"""
            SELECT id_sesion_caja FROM {schema}.t_caja_sesion
            WHERE id_caja = %s AND estado = 'ABIERTA'
            LIMIT 1;
        """
        caja_open = db.execute_query(q_check_caja, (id_caja,), fetchone=True)
        if caja_open:
            raise ValueError("La caja seleccionada ya se encuentra abierta por otro turno.")

        # Insertar cabecera de sesión
        q_sesion = f"""
            INSERT INTO {schema}.t_caja_sesion (
                id_caja, id_usuario, id_sucursal, id_empresa,
                monto_inicial, estado, observacion_apertura
            ) VALUES (
                %s, %s, %s, %s, %s, 'ABIERTA', %s
            ) RETURNING id_sesion_caja, fecha_apertura;
        """
        res_sesion = db.execute_query(
            q_sesion,
            (id_caja, id_usuario, id_sucursal, id_empresa, total_recalculado, observacion),
            fetchone=True
        )
        id_sesion = res_sesion[0]
        fecha_apertura = res_sesion[1]

        # Insertar detalle de conteo histórico de apertura
        for id_denom, val, cant, subtot in detalles_para_insertar:
            q_conteo = f"""
                INSERT INTO {schema}.t_caja_conteo (
                    id_sesion_caja, tipo_conteo, id_denominacion,
                    valor_denominacion, cantidad, subtotal
                ) VALUES (
                    %s, 'APERTURA', %s, %s, %s, %s
                );
            """
            db.execute_query(q_conteo, (id_sesion, id_denom, val, cant, subtot))

        db.conn.commit()

        # Retornar sesión completa
        return {
            "id_sesion_caja": id_sesion,
            "id_caja": id_caja,
            "id_usuario": id_usuario,
            "id_sucursal": id_sucursal,
            "id_empresa": id_empresa,
            "fecha_apertura": fecha_apertura.isoformat() if fecha_apertura else None,
            "monto_inicial": total_recalculado,
            "estado": "ABIERTA",
            "observacion_apertura": observacion,
            "conteo_items": [
                {"id_denominacion": d[0], "valor": d[1], "cantidad": d[2], "subtotal": d[3]}
                for d in detalles_para_insertar
            ]
        }
    except Exception as e:
        db.conn.rollback()
        raise e
    finally:
        db.close_connection()

def calcular_resumen_caja(id_sesion_caja: int) -> Dict[str, Any]:
    """
    Calcula el resumen financiero de la sesión de caja:
    - Fondo inicial
    - Ventas en efectivo, tarjeta, otros métodos
    - Efectivo esperado = fondo_inicial + ventas_efectivo - salidas
    - Cantidad total de ventas realizadas
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        # Obtener sesión
        q_sesion = f"""
            SELECT id_sesion_caja, id_caja, id_usuario, id_sucursal, id_empresa,
                   monto_inicial, fecha_apertura, fecha_cierre, estado, diferencia,
                   efectivo_esperado, efectivo_contado
            FROM {schema}.t_caja_sesion
            WHERE id_sesion_caja = %s;
        """
        s_row = db.execute_query(q_sesion, (id_sesion_caja,), fetchone=True)
        if not s_row:
            raise ValueError(f"Sesión de caja {id_sesion_caja} no encontrada.")

        monto_inicial = float(s_row[5])
        estado_sesion = s_row[8]

        # Total ventas de la sesión
        q_ventas = f"""
            SELECT 
                COUNT(id_venta) AS cant_ventas,
                COALESCE(SUM(total), 0.00) AS total_ventas,
                COUNT(CASE WHEN estado = 'PAGADO' OR estado = 'COMPLETADA' THEN 1 END) AS cant_pagadas,
                COUNT(CASE WHEN estado = 'PENDIENTE_PAGO' THEN 1 END) AS cant_pendientes
            FROM {schema}.t_venta
            WHERE id_sesion_caja = %s;
        """
        v_row = db.execute_query(q_ventas, (id_sesion_caja,), fetchone=True)
        cant_ventas = v_row[0] if v_row else 0
        total_ventas = float(v_row[1]) if v_row else 0.00
        cant_pagadas = v_row[2] if v_row else 0
        cant_pendientes = v_row[3] if v_row else 0

        # Pagos clasificados por método de pago para ventas de esta sesión
        q_pagos = f"""
            SELECT 
                COALESCE(UPPER(mp.tipo), 'OTRO') AS tipo_metodo,
                COALESCE(SUM(p.monto), 0.00) AS monto_acumulado
            FROM {schema}.t_pago p
            JOIN {schema}.t_venta v ON v.id_venta = p.id_venta
            LEFT JOIN {schema}.t_metodo_pago mp ON mp.id_metodo_pago = p.id_metodo_pago
            WHERE v.id_sesion_caja = %s AND p.estado = 'APROBADO'
            GROUP BY COALESCE(UPPER(mp.tipo), 'OTRO');
        """
        p_rows = db.execute_query(q_pagos, (id_sesion_caja,), fetchall=True) or []
        desglose_pagos = {}
        ventas_efectivo = 0.00
        ventas_tarjeta = 0.00
        ventas_qr = 0.00

        for pr in p_rows:
            tipo = pr[0]
            monto = float(pr[1])
            desglose_pagos[tipo] = monto
            if tipo == 'EFECTIVO':
                ventas_efectivo += monto
            elif 'TARJETA' in tipo:
                ventas_tarjeta += monto
            elif 'QR' in tipo or 'PAYPAL' in tipo:
                ventas_qr += monto

        efectivo_esperado = round(monto_inicial + ventas_efectivo, 2)

        # Cálculo de Efectivo Esperado por Denominación
        # 1. Denominaciones activas
        q_denoms = f"""
            SELECT id_denominacion, valor, moneda, tipo, orden
            FROM {schema}.t_denominacion
            WHERE activo = TRUE
            ORDER BY orden ASC, valor DESC;
        """
        denom_rows = db.execute_query(q_denoms, fetchall=True) or []

        # 2. Conteo de Apertura por denominación
        q_apertura = f"""
            SELECT id_denominacion, COALESCE(SUM(cantidad), 0)
            FROM {schema}.t_caja_conteo
            WHERE id_sesion_caja = %s AND tipo_conteo = 'APERTURA'
            GROUP BY id_denominacion;
        """
        apertura_rows = db.execute_query(q_apertura, (id_sesion_caja,), fetchall=True) or []
        apertura_map = {r[0]: int(r[1]) for r in apertura_rows}

        # 3. Billetes/monedas recibidos en pagos de efectivo (ENTRADA_EFECTIVO)
        q_recibido = f"""
            SELECT id_denominacion, COALESCE(SUM(cantidad), 0)
            FROM {schema}.t_pago_denominacion
            WHERE id_sesion_caja = %s AND tipo_movimiento = 'ENTRADA_EFECTIVO'
            GROUP BY id_denominacion;
        """
        recibido_rows = db.execute_query(q_recibido, (id_sesion_caja,), fetchall=True) or []
        recibido_map = {r[0]: int(r[1]) for r in recibido_rows}

        # 4. Billetes/monedas entregados como cambio (SALIDA_CAMBIO)
        q_cambio = f"""
            SELECT id_denominacion, COALESCE(SUM(cantidad), 0)
            FROM {schema}.t_pago_denominacion
            WHERE id_sesion_caja = %s AND tipo_movimiento = 'SALIDA_CAMBIO'
            GROUP BY id_denominacion;
        """
        cambio_rows = db.execute_query(q_cambio, (id_sesion_caja,), fetchall=True) or []
        cambio_map = {r[0]: int(r[1]) for r in cambio_rows}

        # 5. Si ya está cerrada, obtener el conteo de cierre registrado
        conteo_cierre_map = {}
        if estado_sesion == 'CERRADA':
            q_cierre = f"""
                SELECT id_denominacion, COALESCE(SUM(cantidad), 0)
                FROM {schema}.t_caja_conteo
                WHERE id_sesion_caja = %s AND tipo_conteo = 'CIERRE'
                GROUP BY id_denominacion;
            """
            cierre_rows = db.execute_query(q_cierre, (id_sesion_caja,), fetchall=True) or []
            conteo_cierre_map = {r[0]: int(r[1]) for r in cierre_rows}

        denominaciones_esperadas = []
        for dr in denom_rows:
            id_d = dr[0]
            val_d = float(dr[1])
            cant_ap = apertura_map.get(id_d, 0)
            cant_rec = recibido_map.get(id_d, 0)
            cant_cam = cambio_map.get(id_d, 0)
            cant_esp = cant_ap + cant_rec - cant_cam
            subt_esp = round(cant_esp * val_d, 2)
            
            item_denom = {
                "id_denominacion": id_d,
                "valor": val_d,
                "moneda": dr[2],
                "tipo": dr[3],
                "orden": dr[4],
                "cantidad_apertura": cant_ap,
                "cantidad_recibida": cant_rec,
                "cantidad_cambio": cant_cam,
                "cantidad_esperada": cant_esp,
                "subtotal_esperado": subt_esp
            }
            if estado_sesion == 'CERRADA':
                item_denom["cantidad_contada"] = conteo_cierre_map.get(id_d, 0)
                item_denom["subtotal_contado"] = round(item_denom["cantidad_contada"] * val_d, 2)
                item_denom["diferencia_unidades"] = item_denom["cantidad_contada"] - cant_esp

            denominaciones_esperadas.append(item_denom)

        return {
            "id_sesion_caja": id_sesion_caja,
            "estado": estado_sesion,
            "fecha_apertura": s_row[6].isoformat() if s_row[6] else None,
            "fecha_cierre": s_row[7].isoformat() if s_row[7] else None,
            "monto_inicial": monto_inicial,
            "ventas_efectivo": round(ventas_efectivo, 2),
            "ventas_tarjeta": round(ventas_tarjeta, 2),
            "ventas_electronicas": round(ventas_qr, 2),
            "desglose_pagos": desglose_pagos,
            "efectivo_esperado": efectivo_esperado,
            "efectivo_contado": float(s_row[11]) if s_row[11] is not None else None,
            "diferencia": float(s_row[9]) if s_row[9] is not None else None,
            "total_ventas": round(total_ventas, 2),
            "cant_ventas": cant_ventas,
            "cant_pagadas": cant_pagadas,
            "cant_pendientes": cant_pendientes,
            "denominaciones_esperadas": denominaciones_esperadas
        }
    finally:
        db.close_connection()

def cerrar_caja_sesion(
    id_sesion_caja: int,
    id_usuario: int,
    conteo_items: List[Dict[str, Any]],
    observacion: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cierra la sesión de caja mediante conteo por denominaciones.
    Compara efectivo contado vs esperado y registra el arqueo.
    """
    denominaciones = {d["id_denominacion"]: d for d in obtener_denominaciones_activas()}

    efectivo_contado = 0.00
    detalles_para_insertar = []

    for item in conteo_items:
        id_denom = item.get("id_denominacion")
        cant = item.get("cantidad", 0)

        if cant is None or cant < 0:
            raise ValueError("Las cantidades de denominaciones no pueden ser negativas.")

        if id_denom not in denominaciones:
            raise ValueError(f"Denominación con ID {id_denom} no es válida.")

        if cant > 0:
            val = denominaciones[id_denom]["valor"]
            subtot = round(val * cant, 2)
            efectivo_contado += subtot
            detalles_para_insertar.append((id_denom, val, cant, subtot))

    efectivo_contado = round(efectivo_contado, 2)

    # Calcular resumen actual
    resumen = calcular_resumen_caja(id_sesion_caja)
    if resumen["estado"] != "ABIERTA":
        raise ValueError("La sesión de caja ya se encuentra cerrada.")

    efectivo_esperado = resumen["efectivo_esperado"]
    diferencia = round(efectivo_contado - efectivo_esperado, 2)

    estado_diferencia = "CUADRA"
    if diferencia > 0:
        estado_diferencia = "SOBRANTE"
    elif diferencia < 0:
        estado_diferencia = "FALTANTE"

    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        # Actualizar sesión a CERRADA
        q_update = f"""
            UPDATE {schema}.t_caja_sesion
            SET fecha_cierre = CURRENT_TIMESTAMP,
                efectivo_esperado = %s,
                efectivo_contado = %s,
                diferencia = %s,
                estado = 'CERRADA',
                observacion_cierre = %s
            WHERE id_sesion_caja = %s AND estado = 'ABIERTA'
            RETURNING fecha_cierre;
        """
        res_close = db.execute_query(
            q_update,
            (efectivo_esperado, efectivo_contado, diferencia, observacion, id_sesion_caja),
            fetchone=True
        )
        if not res_close:
            raise ValueError("No se pudo cerrar la caja. Verifique que la sesión siga abierta.")

        fecha_cierre = res_close[0]

        # Insertar conteo histórico de cierre
        for id_denom, val, cant, subtot in detalles_para_insertar:
            q_conteo = f"""
                INSERT INTO {schema}.t_caja_conteo (
                    id_sesion_caja, tipo_conteo, id_denominacion,
                    valor_denominacion, cantidad, subtotal
                ) VALUES (
                    %s, 'CIERRE', %s, %s, %s, %s
                );
            """
            db.execute_query(q_conteo, (id_sesion_caja, id_denom, val, cant, subtot))

        db.conn.commit()

        return {
            "id_sesion_caja": id_sesion_caja,
            "estado": "CERRADA",
            "fecha_apertura": resumen["fecha_apertura"],
            "fecha_cierre": fecha_cierre.isoformat() if fecha_cierre else None,
            "monto_inicial": resumen["monto_inicial"],
            "ventas_efectivo": resumen["ventas_efectivo"],
            "ventas_tarjeta": resumen["ventas_tarjeta"],
            "efectivo_esperado": efectivo_esperado,
            "efectivo_contado": efectivo_contado,
            "diferencia": diferencia,
            "estado_diferencia": estado_diferencia,
            "observacion_cierre": observacion,
            "conteo_items": [
                {"id_denominacion": d[0], "valor": d[1], "cantidad": d[2], "subtotal": d[3]}
                for d in detalles_para_insertar
            ]
        }
    except Exception as e:
        db.conn.rollback()
        raise e
    finally:
        db.close_connection()
