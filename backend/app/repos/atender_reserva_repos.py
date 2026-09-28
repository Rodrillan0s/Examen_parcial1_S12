from app.classes.postgres import PostgreSQL
from app.config import Config


def _get_schema():
    return Config.SCHEMA or "comercio"


def listar_reservas_para_atender(
    id_empresa: int,
    id_sucursal: int
):
    db = PostgreSQL()
    db.create_connection()

    schema = _get_schema()

    try:
        query = f"""
            SELECT
                r.id_reserva,
                r.codigo_reserva,
                r.id_cliente,
                r.id_sucursal,
                r.fecha_reserva,
                r.fecha_hora_visita,
                r.estado,
                r.observaciones,
                r.id_venta,

                u.nombre AS cliente_nombre,
                u.apellido AS cliente_apellido,
                c.ci AS cliente_ci,

                s.nombre AS sucursal_nombre,

                v.estado AS venta_estado,
                v.numero_venta,
                v.total AS venta_total

            FROM {schema}.t_reserva r

            LEFT JOIN {schema}.t_cliente c
                ON c.id_cliente = r.id_cliente

            LEFT JOIN {schema}.t_usuario u
                ON u.id_usuario = c.id_usuario

            INNER JOIN {schema}.t_sucursal s
                ON s.id_sucursal = r.id_sucursal

            LEFT JOIN {schema}.t_venta v
                ON v.id_venta = r.id_venta

            WHERE r.id_sucursal = %s
              AND s.id_empresa = %s
              AND r.estado IN ('PENDIENTE', 'CONFIRMADA')

            ORDER BY
                r.fecha_hora_visita ASC NULLS LAST,
                r.id_reserva ASC
        """

        reservas = db.execute_query(
            query,
            (id_sucursal, id_empresa),
            fetchall=True
        )

        resultado = []

        for reserva in reservas:
            venta_pagada = False

            if reserva[8]:
                venta_pagada = reserva[13] in (
                    "PAGADO",
                    "COMPLETADA"
                )

            query_detalles = f"""
                SELECT
                    dr.id_detalle_reserva,
                    dr.id_variante,
                    dr.cantidad,
                    dr.estado_prenda,

                    p.id_producto,
                    p.codigo_producto,
                    p.nombre AS producto_nombre,

                    ptc.sku,

                    t.nombre AS talla,
                    co.nombre AS color,
                    co.codigo_hex,

                    COALESCE(
                        (
                            SELECT pi.imagen_url
                            FROM {schema}.t_producto_imagen pi
                            WHERE pi.id_producto = p.id_producto
                              AND pi.es_principal = TRUE
                            ORDER BY pi.id_imagen
                            LIMIT 1
                        ),
                        (
                            SELECT pi.imagen_url
                            FROM {schema}.t_producto_imagen pi
                            WHERE pi.id_producto = p.id_producto
                            ORDER BY pi.id_imagen
                            LIMIT 1
                        ),
                        p.imagen_url
                    ) AS imagen_url

                FROM {schema}.t_detalle_reserva dr

                INNER JOIN {schema}.t_producto_talla_color ptc
                    ON ptc.id_variante = dr.id_variante

                INNER JOIN {schema}.t_producto p
                    ON p.id_producto = ptc.id_producto

                LEFT JOIN {schema}.t_talla t
                    ON t.id_talla = ptc.id_talla

                LEFT JOIN {schema}.t_color co
                    ON co.id_color = ptc.id_color

                WHERE dr.id_reserva = %s

                ORDER BY dr.id_detalle_reserva
            """

            detalles = db.execute_query(
                query_detalles,
                (reserva[0],),
                fetchall=True
            )

            prendas = []

            for item in detalles:
                prendas.append({
                    "id_detalle_reserva": item[0],
                    "id_variante": item[1],
                    "cantidad": item[2],
                    "estado_prenda": item[3],
                    "id_producto": item[4],
                    "codigo_producto": item[5],
                    "nombre": item[6],
                    "sku": item[7],
                    "talla": item[8],
                    "color": item[9],
                    "codigo_hex": item[10],
                    "imagen_url": item[11]
                })

            resultado.append({
                "id_reserva": reserva[0],
                "codigo_reserva": reserva[1],
                "id_cliente": reserva[2],
                "id_sucursal": reserva[3],
                "fecha_reserva": reserva[4],
                "fecha_hora_visita": reserva[5],
                "estado": reserva[6],
                "observaciones": reserva[7],
                "id_venta": reserva[8],

                "sucursal": reserva[12],

                "cliente": {
                    "id_cliente": reserva[2],
                    "nombre": reserva[9],
                    "apellido": reserva[10],
                    "ci": reserva[11]
                },

                "venta": {
                    "id_venta": reserva[8],
                    "numero_venta": reserva[14],
                    "estado": reserva[13],
                    "total": float(reserva[15] or 0),
                    "pagada": venta_pagada
                },

                "venta_pagada": venta_pagada,
                "puede_atender": True,
                "prendas": prendas
            })

        return {
            "success": True,
            "message": "Reservas obtenidas correctamente.",
            "data": resultado
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error al listar las reservas: {str(e)}",
            "data": []
        }

    finally:
        db.close_connection()


def obtener_reserva_para_atender(
    id_reserva: int,
    id_empresa: int,
    id_sucursal: int
):
    db = PostgreSQL()
    db.create_connection()

    schema = _get_schema()

    try:
        query_reserva = f"""
            SELECT
                r.id_reserva,
                r.codigo_reserva,
                r.id_cliente,
                r.id_sucursal,
                r.fecha_reserva,
                r.fecha_hora_visita,
                r.estado,
                r.observaciones,
                r.id_venta,

                u.nombre AS cliente_nombre,
                u.apellido AS cliente_apellido,
                c.ci AS cliente_ci,

                s.nombre AS sucursal_nombre,

                v.estado AS venta_estado,
                v.numero_venta,
                v.subtotal AS venta_subtotal,
                v.descuento AS venta_descuento,
                v.total AS venta_total

            FROM {schema}.t_reserva r

            LEFT JOIN {schema}.t_cliente c
                ON c.id_cliente = r.id_cliente

            LEFT JOIN {schema}.t_usuario u
                ON u.id_usuario = c.id_usuario

            INNER JOIN {schema}.t_sucursal s
                ON s.id_sucursal = r.id_sucursal

            LEFT JOIN {schema}.t_venta v
                ON v.id_venta = r.id_venta

            WHERE r.id_reserva = %s
              AND r.id_sucursal = %s
              AND s.id_empresa = %s
        """

        reserva = db.execute_query(
            query_reserva,
            (id_reserva, id_sucursal, id_empresa),
            fetchone=True
        )

        if not reserva:
            return {
                "success": False,
                "message": "La reserva no existe o no pertenece a esta sucursal."
            }

        query_detalles = f"""
            SELECT
                dr.id_detalle_reserva,
                dr.id_variante,
                dr.cantidad,
                dr.estado_prenda,

                p.id_producto,
                p.codigo_producto,
                p.nombre AS producto_nombre,
                p.precio AS precio_producto,

                ptc.sku,
                ptc.precio AS precio_variante,

                t.nombre AS talla,
                co.nombre AS color,
                co.codigo_hex,

                COALESCE(
                    (
                        SELECT pi.imagen_url
                        FROM {schema}.t_producto_imagen pi
                        WHERE pi.id_producto = p.id_producto
                          AND pi.es_principal = TRUE
                        ORDER BY pi.id_imagen
                        LIMIT 1
                    ),
                    (
                        SELECT pi.imagen_url
                        FROM {schema}.t_producto_imagen pi
                        WHERE pi.id_producto = p.id_producto
                        ORDER BY pi.id_imagen
                        LIMIT 1
                    ),
                    p.imagen_url
                ) AS imagen_url

            FROM {schema}.t_detalle_reserva dr

            INNER JOIN {schema}.t_producto_talla_color ptc
                ON ptc.id_variante = dr.id_variante

            INNER JOIN {schema}.t_producto p
                ON p.id_producto = ptc.id_producto

            LEFT JOIN {schema}.t_talla t
                ON t.id_talla = ptc.id_talla

            LEFT JOIN {schema}.t_color co
                ON co.id_color = ptc.id_color

            WHERE dr.id_reserva = %s

            ORDER BY dr.id_detalle_reserva
        """

        detalles = db.execute_query(
            query_detalles,
            (id_reserva,),
            fetchall=True
        )

        venta_pagada = False

        if reserva[8]:
            venta_pagada = reserva[13] in (
                "PAGADO",
                "COMPLETADA"
            )

        prendas = []

        for item in detalles:
            precio = (
                item[9]
                if item[9] is not None
                else item[7]
            )

            prendas.append({
                "id_detalle_reserva": item[0],
                "id_variante": item[1],
                "id_producto": item[4],
                "codigo_producto": item[5],
                "nombre": item[6],
                "sku": item[8],
                "talla": item[10],
                "color": item[11],
                "codigo_hex": item[12],
                "cantidad": item[2],
                "precio": float(precio or 0),
                "estado_prenda": item[3],
                "imagen_url": item[13]
            })

        return {
            "success": True,
            "data": {
                "reserva": {
                    "id_reserva": reserva[0],
                    "codigo_reserva": reserva[1],
                    "id_cliente": reserva[2],
                    "id_sucursal": reserva[3],
                    "sucursal": reserva[12],
                    "fecha_reserva": reserva[4],
                    "fecha_hora_visita": reserva[5],
                    "estado": reserva[6],
                    "observaciones": reserva[7],
                    "id_venta": reserva[8]
                },

                "cliente": {
                    "id_cliente": reserva[2],
                    "nombre": reserva[9],
                    "apellido": reserva[10],
                    "ci": reserva[11]
                },

                "venta": {
                    "id_venta": reserva[8],
                    "numero_venta": reserva[14],
                    "estado": reserva[13],
                    "subtotal": float(reserva[15] or 0),
                    "descuento": float(reserva[16] or 0),
                    "total": float(reserva[17] or 0),
                    "pagada": venta_pagada
                },

                "prendas": prendas,

                "puede_atender": (
                    reserva[6] not in
                    ("CANCELADA", "ATENDIDA", "VENCIDA")
                )
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error al obtener la reserva: {str(e)}"
        }

    finally:
        db.close_connection()


def atender_reserva_pagada(
    id_reserva: int,
    id_empresa: int,
    id_sucursal: int
):
    db = PostgreSQL()
    db.create_connection()

    schema = _get_schema()

    try:
        query = f"""
            SELECT
                r.id_reserva,
                r.estado,
                r.id_venta,
                v.estado AS venta_estado

            FROM {schema}.t_reserva r

            INNER JOIN {schema}.t_sucursal s
                ON s.id_sucursal = r.id_sucursal

            LEFT JOIN {schema}.t_venta v
                ON v.id_venta = r.id_venta

            WHERE r.id_reserva = %s
              AND r.id_sucursal = %s
              AND s.id_empresa = %s

            FOR UPDATE OF r
        """

        reserva = db.execute_query(
            query,
            (id_reserva, id_sucursal, id_empresa),
            fetchone=True
        )

        if not reserva:
            return {
                "success": False,
                "message": "La reserva no existe."
            }

        if reserva[1] == "ATENDIDA":
            return {
                "success": False,
                "message": "La reserva ya fue atendida."
            }

        if reserva[1] in ("CANCELADA", "VENCIDA"):
            return {
                "success": False,
                "message": "La reserva no puede ser atendida."
            }

        if not reserva[2]:
            return {
                "success": False,
                "message": "La reserva todavía no tiene una venta asociada."
            }

        if reserva[3] not in ("PAGADO", "COMPLETADA"):
            return {
                "success": False,
                "message": "La venta asociada todavía no está pagada."
            }

        db.execute_query(
            f"""
                UPDATE {schema}.t_reserva
                SET estado = 'ATENDIDA'
                WHERE id_reserva = %s
            """,
            (id_reserva,)
        )

        db.execute_query(
            f"""
                UPDATE {schema}.t_detalle_reserva
                SET estado_prenda = 'ATENDIDA'
                WHERE id_reserva = %s
            """,
            (id_reserva,)
        )

        db.close_connection(commit=True)

        return {
            "success": True,
            "message": "Reserva atendida correctamente.",
            "accion": "ENTREGADA",
            "data": {
                "id_reserva": id_reserva,
                "id_venta": reserva[2]
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error al atender la reserva: {str(e)}"
        }

    finally:
        if db.conn:
            db.close_connection()


def atender_reserva(
    id_reserva: int,
    id_empresa: int,
    id_sucursal: int
):
    reserva = obtener_reserva_para_atender(
        id_reserva,
        id_empresa,
        id_sucursal
    )

    if not reserva["success"]:
        return reserva

    data = reserva["data"]

    if not data["puede_atender"]:
        return {
            "success": False,
            "message": "La reserva no puede ser atendida."
        }

    venta = data["venta"]

    if venta["id_venta"] and venta["pagada"]:
        return atender_reserva_pagada(
            id_reserva,
            id_empresa,
            id_sucursal
        )

    return {
        "success": True,
        "message": "La reserva debe ser procesada mediante el POS.",
        "accion": "IR_A_POS",
        "data": {
            "id_reserva": data["reserva"]["id_reserva"],
            "codigo_reserva": data["reserva"]["codigo_reserva"],
            "id_sucursal": data["reserva"]["id_sucursal"],
            "id_cliente": data["cliente"]["id_cliente"],
            "cliente": data["cliente"],
            "items": [
                {
                    "id_variante": item["id_variante"],
                    "id_producto": item["id_producto"],
                    "nombre": item["nombre"],
                    "sku": item["sku"],
                    "talla": item["talla"],
                    "color": item["color"],
                    "cantidad": item["cantidad"],
                    "precio": item["precio"]
                }
                for item in data["prendas"]
                if item["estado_prenda"] == "RESERVADA"
            ]
        }
    }