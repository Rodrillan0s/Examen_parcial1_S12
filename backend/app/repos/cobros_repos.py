from app.classes.postgres import PostgreSQL
from app.config import Config

def obtener_resumen_cobro_db(nro_emergencia: int, nro_usuario_cliente: int):
    """
    Trae la oferta aceptada y la orden de cobro vinculada a la emergencia de forma flexible.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        # 1. Traer la Oferta Aceptada (Usamos UPPER para evitar fallas de tipeo en el estado)
        query_oferta = f"""
            SELECT oe.id_oferta, oe.precio_estimado, oe.tiempo_estimado_minutos, t.nombre_taller
            FROM {Config.SCHEMA}.emergencia e
            JOIN {Config.SCHEMA}.oferta_emergencia oe ON e.nro_emergencia = oe.nro_emergencia
            JOIN {Config.SCHEMA}.taller t ON oe.nro_taller = t.nro_taller
            WHERE e.nro_emergencia = %s AND UPPER(oe.estado_oferta) = 'ACEPTADA';
        """
        oferta = db.execute_query(query_oferta, (nro_emergencia,), fetchone=True)
        if not oferta:
            print(f"⚠️ Resitorio: No se encontro oferta 'ACEPTADA' para la emergencia {nro_emergencia}")
            return None 

        # 2. Traer la Orden de Cobro
        query_orden = f"""
            SELECT id_orden, fecha_emision, monto_total, estado_cobro
            FROM {Config.SCHEMA}.orden_cobro
            WHERE nro_emergencia = %s;
        """
        orden = db.execute_query(query_orden, (nro_emergencia,), fetchone=True)
        
        # 3. Traer los Detalles de Cobro
        detalles_list = []
        if orden:
            query_detalles = f"""
                SELECT dc.cantidad, dc.subtotal, ct.nombre_concepto, ct.precio_base
                FROM {Config.SCHEMA}.detalle_cobro dc
                JOIN {Config.SCHEMA}.concepto_tarifa ct ON dc.id_concepto = ct.id_concepto
                WHERE dc.id_orden = %s;
            """
            detalles = db.execute_query(query_detalles, (orden[0],), fetchall=True)
            if detalles:
                for d in detalles:
                    detalles_list.append({
                        "cantidad": d[0],
                        "subtotal": float(d[1]),
                        "concepto": d[2],
                        "precio_unitario": float(d[3])
                    })

        return {
            "taller": oferta[3],
            "oferta": {
                "id_oferta": oferta[0],
                "precio_estimado": float(oferta[1]),
                "tiempo_estimado": oferta[2]
            },
            "orden": {
                "id_orden": orden[0] if orden else None,
                "fecha_emision": orden[1].strftime("%Y-%m-%d %H:%M") if orden else None,
                "monto_total": float(orden[2]) if orden else 0.0,
                "estado_cobro": orden[3] if orden else "NO_GENERADA",
                "detalles": detalles_list
            }
        }
    finally:
        db.close_connection()

def registrar_pago_db(id_orden: int, monto_pagado: float, metodo_pago: str):
    db = PostgreSQL()
    db.create_connection()
    try:
        # 1. Insertar en tabla PAGO
        query_pago = f"""
            INSERT INTO {Config.SCHEMA}.pago (monto_pagado, metodo_pago, id_orden)
            VALUES (%s, %s, %s) RETURNING id_pago;
        """
        db.execute_query(query_pago, (monto_pagado, metodo_pago, id_orden))

        # 2. Actualizar tabla ORDEN_COBRO
        query_update = f"""
            UPDATE {Config.SCHEMA}.orden_cobro
            SET estado_cobro = 'PAGADO'
            WHERE id_orden = %s;
        """
        db.execute_query(query_update, (id_orden,), commit=True)
        return True
    except Exception as e:
        print(f"❌ Error en BD al registrar pago: {e}")
        return False
    finally:
        db.close_connection()