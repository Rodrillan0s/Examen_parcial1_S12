import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from app.classes.postgres import PostgreSQL
from app.config import Config
from app.repos.carrito_repos import obtener_o_crear_cliente
from app.repos.bitacora_repos import registrar_evento_db

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

def _generar_codigo_reserva() -> str:
    prefijo = datetime.now().strftime("%Y%m%d")
    sufijo = uuid.uuid4().hex[:6].upper()
    return f"RES-{prefijo}-{sufijo}"

def crear_reserva(id_usuario: int, id_empresa: int, datos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea una reserva en una única transacción atómica:
    1. Invoca fn_reservar_stock para cada variante (bloqueo FOR UPDATE, validación y reserva).
    2. Si alguna variante falla (stock insuficiente, inactiva, etc.), realiza ROLLBACK total.
    3. Si todo es exitoso, crea t_reserva y t_detalle_reserva.
    4. Registra auditoría en t_bitacora.
    """
    id_sucursal = datos.get('id_sucursal')
    fecha_hora_visita = datos.get('fecha_hora_visita')
    observaciones = datos.get('observaciones') or ''
    items = datos.get('items') or []

    if not id_sucursal:
        raise ValueError("Debe seleccionar una sucursal para la reserva.")

    if not fecha_hora_visita:
        raise ValueError("Debe especificar una fecha y hora programada para la visita.")

    if not items or len(items) == 0:
        raise ValueError("La reserva debe contener al menos una prenda o variante.")

    # Validar formato y validez temporal de la fecha de visita
    try:
        if isinstance(fecha_hora_visita, str):
            fecha_hora_limpia = fecha_hora_visita.replace('T', ' ')
            if len(fecha_hora_limpia) == 16:
                fecha_hora_dt = datetime.strptime(fecha_hora_limpia, "%Y-%m-%d %H:%M")
            elif len(fecha_hora_limpia) >= 19:
                fecha_hora_dt = datetime.strptime(fecha_hora_limpia[:19], "%Y-%m-%d %H:%M:%S")
            else:
                fecha_hora_dt = datetime.fromisoformat(fecha_hora_visita)
        else:
            fecha_hora_dt = fecha_hora_visita
    except Exception:
        raise ValueError("El formato de fecha_hora_visita es inválido. Use formato YYYY-MM-DD HH:MM.")

    # Validar que no sea una fecha pasada (con margen de 24h para absorber diferencias de zona horaria)
    if fecha_hora_dt < datetime.now() - timedelta(hours=24):
        raise ValueError("La fecha y hora de visita no puede ser anterior a la fecha actual.")

    # Obtener el cliente asociado al usuario autenticado
    id_cliente = obtener_o_crear_cliente(id_usuario)

    schema = _get_schema()
    db = PostgreSQL()
    db.create_connection()

    try:
        cur = db.conn.cursor()

        # 1. Validar que la sucursal pertenezca a la empresa del Tenant y esté activa
        cur.execute(f"""
            SELECT nombre, activo 
            FROM {schema}.t_sucursal 
            WHERE id_sucursal = %s AND id_empresa = %s;
        """, (id_sucursal, id_empresa))
        suc_row = cur.fetchone()
        if not suc_row:
            raise ValueError("La sucursal seleccionada no pertenece a la tienda actual o no existe.")
        if not suc_row[1]:
            raise ValueError(f"La sucursal '{suc_row[0]}' se encuentra inactiva temporalmente.")

        sucursal_nombre = suc_row[0]

        # 2. Validar que cada variante pertenezca a un producto activo del Tenant
        for item in items:
            id_var = item.get('id_variante')
            cant = item.get('cantidad', 1)
            if not id_var or cant <= 0:
                raise ValueError("Cada detalle debe tener id_variante válido y cantidad mayor a 0.")

            cur.execute(f"""
                SELECT p.nombre, p.id_empresa, p.activo, ptc.activo
                FROM {schema}.t_producto_talla_color ptc
                JOIN {schema}.t_producto p ON p.id_producto = ptc.id_producto
                WHERE ptc.id_variante = %s;
            """, (id_var,))
            p_row = cur.fetchone()
            if not p_row:
                raise ValueError(f"La variante {id_var} no existe.")
            if p_row[1] != id_empresa:
                raise ValueError(f"La prenda '{p_row[0]}' no pertenece a la tienda actual.")
            if not p_row[2] or not p_row[3]:
                raise ValueError(f"La prenda o variante '{p_row[0]}' se encuentra inactiva para reservas.")

        # 3. Reservar stock ejecutando fn_reservar_stock para cada variante
        # Si alguna falla, se lanza excepción y se ejecutará el ROLLBACK completo
        detalles_procesados = []
        for item in items:
            id_var = item.get('id_variante')
            cant = int(item.get('cantidad', 1))

            cur.execute(f"""
                SELECT {schema}.fn_reservar_stock(%s, %s, %s, %s);
            """, (id_sucursal, id_var, cant, id_usuario))
            fn_res = cur.fetchone()[0]

            if isinstance(fn_res, str):
                fn_res = json.loads(fn_res)

            if not fn_res.get('success'):
                err_msg = fn_res.get('message') or "Error al reservar stock en inventario."
                raise ValueError(f"No fue posible apartar la variante {id_var}: {err_msg}")

            detalles_procesados.append({
                "id_variante": id_var,
                "cantidad": cant,
                "stock_info": fn_res
            })

        # 4. Crear cabecera de la reserva en t_reserva
        codigo_reserva = _generar_codigo_reserva()
        cur.execute(f"""
            INSERT INTO {schema}.t_reserva (
                id_cliente,
                id_sucursal,
                codigo_reserva,
                fecha_reserva,
                fecha_hora_visita,
                estado,
                observaciones
            ) VALUES (%s, %s, %s, NOW(), %s, 'PENDIENTE', %s)
            RETURNING id_reserva, fecha_reserva;
        """, (id_cliente, id_sucursal, codigo_reserva, fecha_hora_dt, observaciones))
        reserva_creada = cur.fetchone()
        id_reserva = reserva_creada[0]
        fecha_reserva_db = reserva_creada[1]

        # 5. Insertar registros en t_detalle_reserva
        detalles_guardados = []
        for det in detalles_procesados:
            cur.execute(f"""
                INSERT INTO {schema}.t_detalle_reserva (
                    id_reserva,
                    id_variante,
                    cantidad,
                    estado_prenda
                ) VALUES (%s, %s, %s, 'RESERVADA')
                RETURNING id_detalle_reserva;
            """, (id_reserva, det["id_variante"], det["cantidad"]))
            id_det = cur.fetchone()[0]
            detalles_guardados.append({
                "id_detalle_reserva": id_det,
                "id_variante": det["id_variante"],
                "cantidad": det["cantidad"],
                "estado_prenda": "RESERVADA"
            })

        # 6. Confirmar transacción completa
        db.conn.commit()

        # 7. Registrar evento de auditoría en t_bitacora
        try:
            registrar_evento_db(
                id_usuario=id_usuario,
                usuario_nombre=None,
                usuario_email=None,
                id_empresa=id_empresa,
                id_sucursal=id_sucursal,
                modulo="RESERVAS",
                accion="CREAR_RESERVA",
                entidad="t_reserva",
                id_entidad=str(id_reserva),
                descripcion=f"Reserva {codigo_reserva} creada con {len(detalles_guardados)} prenda(s) para visita el {fecha_hora_dt}.",
                resultado="EXITO",
                nivel="INFO",
                ip=None,
                user_agent=None,
                datos_anteriores=None,
                datos_nuevos={
                    "codigo_reserva": codigo_reserva,
                    "id_sucursal": id_sucursal,
                    "fecha_hora_visita": str(fecha_hora_dt),
                    "items": detalles_guardados
                },
                metadatos={"id_cliente": id_cliente},
                request_id=None
            )
        except Exception as bit_ex:
            print(f"[RESERVAS] Advertencia al registrar bitácora: {bit_ex}")

        return {
            "id_reserva": id_reserva,
            "codigo_reserva": codigo_reserva,
            "id_sucursal": id_sucursal,
            "sucursal_nombre": sucursal_nombre,
            "fecha_reserva": fecha_reserva_db.isoformat() if fecha_reserva_db else None,
            "fecha_hora_visita": fecha_hora_dt.isoformat() if isinstance(fecha_hora_dt, datetime) else str(fecha_hora_dt),
            "estado": "PENDIENTE",
            "observaciones": observaciones,
            "detalles": detalles_guardados
        }

    except Exception as e:
        if db.conn:
            db.conn.rollback()
        raise e
    finally:
        db.close_connection()

def obtener_mis_reservas(id_usuario: int, id_empresa: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retorna la lista de reservas asociadas al cliente autenticado.
    Si se indica id_empresa, filtra por ese Tenant específico; de lo contrario retorna todas las reservas del cliente.
    Incluye datos de sucursal y el desglose de prendas/variantes reservadas.
    """
    id_cliente = obtener_o_crear_cliente(id_usuario)
    schema = _get_schema()
    db = PostgreSQL()
    db.create_connection()

    try:
        cur = db.conn.cursor()
        empresa_filtro = "AND s.id_empresa = %s" if id_empresa else ""
        query = f"""
            SELECT 
                r.id_reserva,
                r.codigo_reserva,
                r.fecha_reserva,
                r.fecha_hora_visita,
                r.estado,
                r.observaciones,
                r.fecha_cancelacion,
                r.motivo_cancelacion,
                s.id_sucursal,
                s.nombre AS sucursal_nombre,
                s.direccion AS sucursal_direccion,
                s.telefono AS sucursal_telefono,
                ci.nombre AS ciudad_nombre
            FROM {schema}.t_reserva r
            JOIN {schema}.t_sucursal s ON s.id_sucursal = r.id_sucursal
            LEFT JOIN {schema}.t_ciudad ci ON ci.id_ciudad = s.id_ciudad
            WHERE r.id_cliente = %s {empresa_filtro}
            ORDER BY r.fecha_reserva DESC;
        """
        params = (id_cliente, id_empresa) if id_empresa else (id_cliente,)
        cur.execute(query, params)
        reservas_rows = cur.fetchall()

        if not reservas_rows:
            return []

        ids_reservas = [r[0] for r in reservas_rows]

        # Consultar detalles de todas las reservas del cliente
        det_query = f"""
            SELECT 
                dr.id_detalle_reserva,
                dr.id_reserva,
                dr.id_variante,
                dr.cantidad,
                dr.estado_prenda,
                p.id_producto,
                p.nombre AS producto_nombre,
                p.precio AS producto_precio,
                t.nombre AS talla_nombre,
                c.nombre AS color_nombre,
                c.codigo_hex,
                COALESCE(
                    (SELECT imagen_url FROM {schema}.t_producto_imagen WHERE id_producto = p.id_producto AND es_principal = TRUE LIMIT 1),
                    (SELECT imagen_url FROM {schema}.t_producto_imagen WHERE id_producto = p.id_producto ORDER BY orden ASC LIMIT 1)
                ) AS imagen_url
            FROM {schema}.t_detalle_reserva dr
            JOIN {schema}.t_producto_talla_color ptc ON ptc.id_variante = dr.id_variante
            JOIN {schema}.t_producto p ON p.id_producto = ptc.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = ptc.id_talla
            JOIN {schema}.t_color c ON c.id_color = ptc.id_color
            WHERE dr.id_reserva = ANY(%s)
            ORDER BY dr.id_detalle_reserva ASC;
        """
        cur.execute(det_query, (ids_reservas,))
        detalles_rows = cur.fetchall()

        # Agrupar detalles por id_reserva
        detalles_por_reserva: Dict[int, List[Dict[str, Any]]] = {r_id: [] for r_id in ids_reservas}
        for d in detalles_rows:
            r_id = d[1]
            detalles_por_reserva[r_id].append({
                "id_detalle_reserva": d[0],
                "id_variante": d[2],
                "cantidad": d[3],
                "estado_prenda": d[4],
                "id_producto": d[5],
                "producto_nombre": d[6],
                "precio": float(d[7]) if d[7] is not None else 0.0,
                "talla": d[8],
                "color": d[9],
                "codigo_hex": d[10],
                "imagen_url": d[11]
            })

        resultado = []
        for r in reservas_rows:
            r_id = r[0]
            resultado.append({
                "id_reserva": r_id,
                "codigo_reserva": r[1],
                "fecha_reserva": r[2].isoformat() if r[2] else None,
                "fecha_hora_visita": r[3].isoformat() if r[3] else None,
                "estado": r[4],
                "observaciones": r[5] or "",
                "fecha_cancelacion": r[6].isoformat() if r[6] else None,
                "motivo_cancelacion": r[7] or "",
                "sucursal": {
                    "id_sucursal": r[8],
                    "nombre": r[9],
                    "direccion": r[10] or "Sin dirección",
                    "telefono": r[11] or "",
                    "ciudad": r[12] or "Santa Cruz"
                },
                "items": detalles_por_reserva.get(r_id, []),
                "total_prendas": sum(item["cantidad"] for item in detalles_por_reserva.get(r_id, []))
            })

        return resultado

    finally:
        db.close_connection()

def obtener_detalle_reserva(id_reserva: int, id_usuario: int, id_empresa: int, es_admin: bool = False) -> Optional[Dict[str, Any]]:
    """
    Retorna la información completa de una reserva puntual.
    Si no es administrador, valida que pertenezca forzosamente al id_cliente del usuario autenticado.
    """
    id_cliente = obtener_o_crear_cliente(id_usuario)
    schema = _get_schema()
    db = PostgreSQL()
    db.create_connection()

    try:
        cur = db.conn.cursor()
        query = f"""
            SELECT 
                r.id_reserva,
                r.id_cliente,
                r.codigo_reserva,
                r.fecha_reserva,
                r.fecha_hora_visita,
                r.estado,
                r.observaciones,
                r.fecha_cancelacion,
                r.motivo_cancelacion,
                s.id_sucursal,
                s.id_empresa,
                s.nombre AS sucursal_nombre,
                s.direccion AS sucursal_direccion,
                s.telefono AS sucursal_telefono,
                ci.nombre AS ciudad_nombre,
                u.nombre AS cliente_nombre,
                u.apellido AS cliente_apellido,
                u.correo AS cliente_correo,
                u.telefono AS cliente_telefono
            FROM {schema}.t_reserva r
            JOIN {schema}.t_sucursal s ON s.id_sucursal = r.id_sucursal
            LEFT JOIN {schema}.t_ciudad ci ON ci.id_ciudad = s.id_ciudad
            JOIN {schema}.t_cliente cl ON cl.id_cliente = r.id_cliente
            JOIN {schema}.t_usuario u ON u.id_usuario = cl.id_usuario
            WHERE r.id_reserva = %s;
        """
        cur.execute(query, (id_reserva,))
        r = cur.fetchone()
        if not r:
            return None

        # Validación estricta de aislamiento multi-tenant
        if r[10] != id_empresa:
            return None

        # Validación de propiedad para clientes
        if not es_admin and r[1] != id_cliente:
            return None

        # Obtener los items
        det_query = f"""
            SELECT 
                dr.id_detalle_reserva,
                dr.id_variante,
                dr.cantidad,
                dr.estado_prenda,
                p.id_producto,
                p.nombre AS producto_nombre,
                p.precio AS producto_precio,
                t.nombre AS talla_nombre,
                c.nombre AS color_nombre,
                c.codigo_hex,
                COALESCE(
                    (SELECT imagen_url FROM {schema}.t_producto_imagen WHERE id_producto = p.id_producto AND es_principal = TRUE LIMIT 1),
                    (SELECT imagen_url FROM {schema}.t_producto_imagen WHERE id_producto = p.id_producto ORDER BY orden ASC LIMIT 1)
                ) AS imagen_url
            FROM {schema}.t_detalle_reserva dr
            JOIN {schema}.t_producto_talla_color ptc ON ptc.id_variante = dr.id_variante
            JOIN {schema}.t_producto p ON p.id_producto = ptc.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = ptc.id_talla
            JOIN {schema}.t_color c ON c.id_color = ptc.id_color
            WHERE dr.id_reserva = %s
            ORDER BY dr.id_detalle_reserva ASC;
        """
        cur.execute(det_query, (id_reserva,))
        items = []
        for d in cur.fetchall():
            items.append({
                "id_detalle_reserva": d[0],
                "id_variante": d[1],
                "cantidad": d[2],
                "estado_prenda": d[3],
                "id_producto": d[4],
                "producto_nombre": d[5],
                "precio": float(d[6]) if d[6] is not None else 0.0,
                "talla": d[7],
                "color": d[8],
                "codigo_hex": d[9],
                "imagen_url": d[10]
            })

        return {
            "id_reserva": r[0],
            "id_cliente": r[1],
            "codigo_reserva": r[2],
            "fecha_reserva": r[3].isoformat() if r[3] else None,
            "fecha_hora_visita": r[4].isoformat() if r[4] else None,
            "estado": r[5],
            "observaciones": r[6] or "",
            "fecha_cancelacion": r[7].isoformat() if r[7] else None,
            "motivo_cancelacion": r[8] or "",
            "sucursal": {
                "id_sucursal": r[9],
                "nombre": r[11],
                "direccion": r[12] or "Sin dirección",
                "telefono": r[13] or "",
                "ciudad": r[14] or "Santa Cruz"
            },
            "cliente": {
                "nombre": f"{r[15]} {r[16]}".strip(),
                "correo": r[17],
                "telefono": r[18] or ""
            },
            "items": items,
            "total_prendas": sum(item["cantidad"] for item in items)
        }

    finally:
        db.close_connection()

def cancelar_reserva(id_reserva: int, id_usuario: int, id_empresa: int, motivo: str, es_admin: bool = False) -> Dict[str, Any]:
    """
    Cancela una reserva activa de forma atómica:
    1. Bloquea la fila en t_reserva (FOR UPDATE) para evitar concurrencia y doble cancelación.
    2. Valida que el estado sea 'PENDIENTE' o 'CONFIRMADA'.
    3. Para cada variante en t_detalle_reserva:
       - Bloquea t_inventario (FOR UPDATE).
       - Reduce stock_reservado y restituye stock_disponible (stock_actual no cambia).
       - Registra movimiento 'LIBERACION_RESERVA' en t_movimiento_inventario.
    4. Actualiza t_reserva a 'CANCELADA' con fecha y motivo.
    5. Registra auditoría en t_bitacora.
    """
    if not motivo or not motivo.strip():
        motivo = "Cancelación solicitada por el cliente."

    id_cliente = obtener_o_crear_cliente(id_usuario)
    schema = _get_schema()
    db = PostgreSQL()
    db.create_connection()

    try:
        cur = db.conn.cursor()

        # 1. Bloquear y verificar la reserva
        cur.execute(f"""
            SELECT r.id_reserva, r.id_cliente, r.id_sucursal, r.codigo_reserva, r.estado, s.id_empresa
            FROM {schema}.t_reserva r
            JOIN {schema}.t_sucursal s ON s.id_sucursal = r.id_sucursal
            WHERE r.id_reserva = %s
            FOR UPDATE OF r;
        """, (id_reserva,))
        res_row = cur.fetchone()

        if not res_row:
            raise ValueError("La reserva solicitada no existe.")

        if res_row[5] != id_empresa:
            raise ValueError("La reserva no pertenece a la tienda actual.")

        if not es_admin and res_row[1] != id_cliente:
            raise ValueError("No tienes autorización para cancelar una reserva que no te pertenece.")

        estado_actual = res_row[4]
        id_sucursal = res_row[2]
        codigo_reserva = res_row[3]

        if estado_actual == 'CANCELADA':
            raise ValueError("La reserva ya fue cancelada previamente. No se puede liberar stock dos veces.")

        if estado_actual in ('ATENDIDA', 'VENCIDA'):
            raise ValueError(f"No se puede cancelar una reserva que ya se encuentra en estado '{estado_actual}'.")

        # 2. Obtener los detalles de la reserva a liberar
        cur.execute(f"""
            SELECT id_variante, cantidad
            FROM {schema}.t_detalle_reserva
            WHERE id_reserva = %s;
        """, (id_reserva,))
        detalles = cur.fetchall()

        # 3. Restituir inventario de forma atómica para cada variante
        for det in detalles:
            id_var = det[0]
            cant = det[1]

            # Bloquear fila de inventario
            cur.execute(f"""
                SELECT id_inventario, stock_reservado, stock_disponible
                FROM {schema}.t_inventario
                WHERE id_sucursal = %s AND id_variante = %s
                FOR UPDATE;
            """, (id_sucursal, id_var))
            inv_row = cur.fetchone()

            if inv_row:
                id_inv = inv_row[0]
                stock_res = inv_row[1]
                stock_disp = inv_row[2]

                nuevo_reservado = max(0, stock_res - cant)
                nuevo_disponible = stock_disp + cant

                cur.execute(f"""
                    UPDATE {schema}.t_inventario
                    SET stock_reservado = %s,
                        stock_disponible = %s,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id_inventario = %s;
                """, (nuevo_reservado, nuevo_disponible, id_inv))

                # Registrar movimiento de inventario
                cur.execute(f"""
                    INSERT INTO {schema}.t_movimiento_inventario (
                        id_inventario,
                        id_usuario,
                        tipo_movimiento,
                        cantidad,
                        stock_anterior,
                        stock_nuevo,
                        motivo,
                        fecha_movimiento
                    ) VALUES (%s, %s, 'LIBERACION_RESERVA', %s, %s, %s, %s, CURRENT_TIMESTAMP);
                """, (
                    id_inv,
                    id_usuario,
                    cant,
                    stock_disp,
                    nuevo_disponible,
                    f"Liberación por cancelación de reserva {codigo_reserva}: {motivo}"
                ))

        # 4. Actualizar estado de la reserva
        cur.execute(f"""
            UPDATE {schema}.t_reserva
            SET estado = 'CANCELADA',
                fecha_cancelacion = CURRENT_TIMESTAMP,
                motivo_cancelacion = %s
            WHERE id_reserva = %s;
        """, (motivo.strip(), id_reserva))

        # Actualizar estado de las prendas a 'CANCELADA'
        cur.execute(f"""
            UPDATE {schema}.t_detalle_reserva
            SET estado_prenda = 'CANCELADA'
            WHERE id_reserva = %s;
        """, (id_reserva,))

        # 5. Commit de la transacción
        db.conn.commit()

        # 6. Auditoría en bitácora
        try:
            registrar_evento_db(
                id_usuario=id_usuario,
                usuario_nombre=None,
                usuario_email=None,
                id_empresa=id_empresa,
                id_sucursal=id_sucursal,
                modulo="RESERVAS",
                accion="CANCELAR_RESERVA",
                entidad="t_reserva",
                id_entidad=str(id_reserva),
                descripcion=f"Reserva {codigo_reserva} cancelada. Motivo: {motivo}",
                resultado="EXITO",
                nivel="INFO",
                ip=None,
                user_agent=None,
                datos_anteriores={"estado": estado_actual},
                datos_nuevos={"estado": "CANCELADA", "motivo_cancelacion": motivo},
                metadatos={"id_cliente": id_cliente},
                request_id=None
            )
        except Exception as bit_ex:
            print(f"[RESERVAS] Error al registrar bitácora de cancelación: {bit_ex}")

        return {
            "id_reserva": id_reserva,
            "codigo_reserva": codigo_reserva,
            "estado": "CANCELADA",
            "motivo_cancelacion": motivo,
            "mensaje": "La reserva ha sido cancelada exitosamente y el inventario fue restituido."
        }

    except Exception as e:
        if db.conn:
            db.conn.rollback()
        raise e
    finally:
        db.close_connection()
