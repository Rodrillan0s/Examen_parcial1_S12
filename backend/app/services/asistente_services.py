import json
import logging
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import psycopg2
from app.config import Config

logger = logging.getLogger(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        connect_timeout=10
    )


# =====================================================================
# HERRAMIENTAS DISPONIBLES (OPENAI / DEEPSEEK FUNCTION CALLING SPEC)
# =====================================================================

CLIENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_prendas_catalogo",
            "description": "Busca prendas y artículos en el catálogo de Aurora Store por término, categoría, género (Damas, Caballeros, Unisex) o precio máximo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "termino": {"type": "string", "description": "Término de búsqueda (ej. 'vestido', 'camisa', 'pantalón slim', 'seda')"},
                    "categoria": {"type": "string", "description": "Nombre de la categoría (ej. 'Vestidos', 'Camisas', 'Pantalones')"},
                    "genero": {"type": "string", "enum": ["Damas", "Caballeros", "Unisex", "Niños"], "description": "Género o sección"},
                    "precio_max": {"type": "number", "description": "Precio máximo en Bolivianos (Bs.)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_detalle_prenda",
            "description": "Obtiene la información detallada de una prenda: precio, tallas disponibles, colores y existencias en tiendas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_producto": {"type": "integer", "description": "ID numérico del producto si se conoce"},
                    "nombre_prenda": {"type": "string", "description": "Nombre aproximado o código de la prenda"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_sucursales_tiendas",
            "description": "Lista las sucursales y tiendas físicas activas de Aurora Store con sus direcciones y teléfonos.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_mis_pedidos",
            "description": "Consulta el historial de pedidos y compras realizados por el cliente autenticado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limite": {"type": "integer", "description": "Cantidad de pedidos a consultar (por defecto 5)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_mis_reservas",
            "description": "Consulta las reservas activas de prendas del cliente autenticado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limite": {"type": "integer", "description": "Cantidad de reservas a consultar (por defecto 5)"}
                }
            }
        }
    }
]

ADMIN_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_ventas_empresa",
            "description": "Consulta las ventas, facturación total, ticket promedio y cantidad de transacciones de la empresa en un periodo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "periodo": {
                        "type": "string", 
                        "enum": ["hoy", "ayer", "esta_semana", "este_mes", "ultimos_30_dias"],
                        "description": "Periodo temporal a consultar"
                    },
                    "sucursal": {"type": "string", "description": "Nombre o fragmento de la sucursal (opcional)"}
                },
                "required": ["periodo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_inventario_alertas",
            "description": "Consulta el estado del inventario físico, prendas agotadas o con stock bajo respecto al mínimo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filtro": {
                        "type": "string", 
                        "enum": ["agotados", "bajo_stock", "todos"],
                        "description": "Condición del stock a filtrar"
                    },
                    "sucursal": {"type": "string", "description": "Nombre o fragmento de la sucursal (opcional)"}
                },
                "required": ["filtro"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_ventas_pendientes",
            "description": "Consulta las ventas y pedidos pendientes de pago, con clientes deudores, total por cobrar y días de antigüedad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sucursal": {"type": "string", "description": "Nombre de la sucursal (opcional)"},
                    "canal": {"type": "string", "enum": ["todos", "pos", "online"], "description": "Canal de venta"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_reservas_prendas_empresa",
            "description": "Consulta prendas apartadas/reservadas en tiendas físicas, fechas de visita y vigencia para cobranza o liberación de stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sucursal": {"type": "string", "description": "Nombre de la sucursal (opcional)"},
                    "vigencia": {"type": "string", "enum": ["vigente", "vencida", "todas"], "description": "Estado de vigencia"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_auditoria_pos_errores",
            "description": "Auditoría de ventas en mostrador/caja POS para encontrar errores, ventas sin pago registrado o descuadres de cajeros.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sucursal": {"type": "string", "description": "Nombre de la sucursal (opcional)"},
                    "solo_alertas": {"type": "boolean", "description": "Si es True, devuelve solo ventas con advertencias o no cobradas"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_indicadores_kpi_generales",
            "description": "Obtiene los principales indicadores de rendimiento (KPIs) del negocio: ingresos totales, margen, productos activos y pedidos.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generar_reporte_directo",
            "description": "Genera o resume un reporte formal de ventas, inventario, pagos o caja.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_reporte": {
                        "type": "string",
                        "enum": ["ventas", "inventario", "pagos", "caja"],
                        "description": "Tipo de reporte solicitado"
                    },
                    "periodo": {"type": "string", "description": "Periodo o rango de fechas"}
                },
                "required": ["tipo_reporte"]
            }
        }
    }
]


# =====================================================================
# EJECUCIÓN PARAMETRIZADA DE HERRAMIENTAS (POSTGRESQL MULTI-TENANT)
# =====================================================================

def _ejecutar_buscar_prendas(args: dict, id_empresa: int) -> dict:
    termino = args.get("termino", "").strip()
    categoria = args.get("categoria", "").strip()
    genero = args.get("genero", "").strip()
    precio_max = args.get("precio_max")

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT DISTINCT
                p.id_producto,
                p.nombre,
                p.codigo_producto,
                COALESCE(p.precio, 0) as precio,
                COALESCE(c.nombre, 'Moda') as categoria,
                COALESCE(p.genero, 'Unisex') as genero,
                p.imagen_url,
                p.descripcion,
                COALESCE(SUM(inv.stock_disponible), 0) as stock_total
            FROM comercio.t_producto p
            LEFT JOIN comercio.t_categoria c ON p.id_categoria = c.id_categoria
            LEFT JOIN comercio.t_producto_talla_color ptc ON p.id_producto = ptc.id_producto
            LEFT JOIN comercio.t_inventario inv ON ptc.id_variante = inv.id_variante
            WHERE p.id_empresa = %s AND p.activo = true
        """
        params = [id_empresa]

        if termino:
            sql += " AND (p.nombre ILIKE %s OR p.descripcion ILIKE %s OR p.codigo_producto ILIKE %s)"
            t_pattern = f"%{termino}%"
            params.extend([t_pattern, t_pattern, t_pattern])

        if categoria:
            sql += " AND c.nombre ILIKE %s"
            params.append(f"%{categoria}%")

        if genero:
            sql += " AND p.genero ILIKE %s"
            params.append(f"%{genero}%")

        if precio_max:
            sql += " AND p.precio <= %s"
            params.append(float(precio_max))

        sql += """
            GROUP BY p.id_producto, p.nombre, p.codigo_producto, p.precio, c.nombre, p.genero, p.imagen_url, p.descripcion
            ORDER BY p.id_producto DESC
            LIMIT 8
        """

        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

        productos = []
        for r in rows:
            cur.execute("""
                SELECT DISTINCT t.nombre as talla, col.nombre as color
                FROM comercio.t_producto_talla_color ptc
                LEFT JOIN comercio.t_talla t ON ptc.id_talla = t.id_talla
                LEFT JOIN comercio.t_color col ON ptc.id_color = col.id_color
                WHERE ptc.id_producto = %s
            """, (r[0],))
            vars_data = cur.fetchall()
            tallas = sorted(list({v[0] for v in vars_data if v[0]}))
            colores = sorted(list({v[1] for v in vars_data if v[1]}))

            productos.append({
                "id_producto": r[0],
                "nombre": r[1],
                "codigo": r[2],
                "precio": float(r[3]),
                "categoria": r[4],
                "genero": r[5],
                "imagen_url": r[6] or "assets/images/default-fashion.jpg",
                "descripcion": r[7] or "",
                "stock_disponible": int(r[8]),
                "tallas": tallas,
                "colores": colores
            })

        return {
            "total_encontrados": len(productos),
            "productos": productos
        }
    finally:
        conn.close()


def _ejecutar_detalle_prenda(args: dict, id_empresa: int) -> dict:
    id_producto = args.get("id_producto")
    nombre = args.get("nombre_prenda", "").strip()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if id_producto:
            cur.execute("""
                SELECT p.id_producto, p.nombre, p.codigo_producto, p.precio, COALESCE(c.nombre, 'Moda'), p.imagen_url, p.descripcion
                FROM comercio.t_producto p
                LEFT JOIN comercio.t_categoria c ON p.id_categoria = c.id_categoria
                WHERE p.id_producto = %s AND p.id_empresa = %s
            """, (id_producto, id_empresa))
        else:
            cur.execute("""
                SELECT p.id_producto, p.nombre, p.codigo_producto, p.precio, COALESCE(c.nombre, 'Moda'), p.imagen_url, p.descripcion
                FROM comercio.t_producto p
                LEFT JOIN comercio.t_categoria c ON p.id_categoria = c.id_categoria
                WHERE (p.nombre ILIKE %s OR p.codigo_producto ILIKE %s) AND p.id_empresa = %s
                LIMIT 1
            """, (f"%{nombre}%", f"%{nombre}%", id_empresa))

        prod = cur.fetchone()
        if not prod:
            return {"error": "Prenda no encontrada en la tienda."}

        pid = prod[0]
        cur.execute("""
            SELECT s.nombre as sucursal, t.nombre as talla, col.nombre as color, 
                   COALESCE(inv.stock_disponible, 0) as disponible
            FROM comercio.t_producto_talla_color ptc
            JOIN comercio.t_inventario inv ON ptc.id_variante = inv.id_variante
            JOIN comercio.t_sucursal s ON inv.id_sucursal = s.id_sucursal
            LEFT JOIN comercio.t_talla t ON ptc.id_talla = t.id_talla
            LEFT JOIN comercio.t_color col ON ptc.id_color = col.id_color
            WHERE ptc.id_producto = %s AND s.id_empresa = %s
            ORDER BY s.nombre, t.nombre
        """, (pid, id_empresa))

        variantes = []
        for v in cur.fetchall():
            variantes.append({
                "sucursal": v[0],
                "talla": v[1],
                "color": v[2],
                "stock_disponible": int(v[3])
            })

        return {
            "id_producto": prod[0],
            "nombre": prod[1],
            "codigo": prod[2],
            "precio": float(prod[3]),
            "categoria": prod[4],
            "imagen_url": prod[5] or "assets/images/default-fashion.jpg",
            "descripcion": prod[6] or "",
            "variantes_stock": variantes
        }
    finally:
        conn.close()


def _ejecutar_consultar_sucursales(id_empresa: int) -> dict:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id_sucursal, s.nombre, COALESCE(s.direccion, 'Centro Comercial'), 
                   COALESCE(c.nombre, 'Santa Cruz'), COALESCE(s.telefono, 'S/N')
            FROM comercio.t_sucursal s
            LEFT JOIN comercio.t_ciudad c ON s.id_ciudad = c.id_ciudad
            WHERE s.id_empresa = %s AND s.activo = true
            ORDER BY s.nombre
        """, (id_empresa,))
        rows = cur.fetchall()
        sucursales = [{
            "id_sucursal": r[0],
            "nombre": r[1],
            "direccion": r[2],
            "ciudad": r[3],
            "telefono": r[4]
        } for r in rows]
        return {"sucursales": sucursales}
    finally:
        conn.close()


def _ejecutar_consultar_mis_pedidos(id_usuario: int, limite: int = 5) -> dict:
    if not id_usuario:
        return {"error": "Debes iniciar sesión para consultar tus pedidos."}

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id_pedido, p.numero_pedido, p.fecha_pedido, p.total, p.estado
            FROM comercio.t_pedido p
            WHERE p.id_cliente = %s
            ORDER BY p.fecha_pedido DESC
            LIMIT %s
        """, (id_usuario, limite or 5))
        rows = cur.fetchall()
        pedidos = [{
            "id_pedido": r[0],
            "numero_pedido": r[1],
            "fecha": r[2].isoformat() if hasattr(r[2], 'isoformat') else str(r[2]),
            "total_bs": float(r[3]),
            "estado": r[4]
        } for r in rows]
        return {"pedidos": pedidos}
    finally:
        conn.close()


def _ejecutar_consultar_mis_reservas(id_usuario: int, limite: int = 5) -> dict:
    if not id_usuario:
        return {"error": "Debes iniciar sesión para consultar tus reservas."}

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT r.id_reserva, r.codigo_reserva, r.fecha_reserva, r.fecha_vencimiento, r.estado,
                   p.nombre as prenda, r.cantidad
            FROM comercio.t_reserva r
            LEFT JOIN comercio.t_producto_talla_color ptc ON r.id_variante = ptc.id_variante
            LEFT JOIN comercio.t_producto p ON ptc.id_producto = p.id_producto
            WHERE r.id_cliente = %s
            ORDER BY r.fecha_reserva DESC
            LIMIT %s
        """, (id_usuario, limite or 5))
        rows = cur.fetchall()
        reservas = [{
            "id_reserva": r[0],
            "codigo_reserva": r[1],
            "fecha_reserva": r[2].isoformat() if hasattr(r[2], 'isoformat') else str(r[2]),
            "fecha_vencimiento": r[3].isoformat() if hasattr(r[3], 'isoformat') else str(r[3]),
            "estado": r[4],
            "prenda": r[5] or "Prenda reservada",
            "cantidad": r[6]
        } for r in rows]
        return {"reservas": reservas}
    finally:
        conn.close()


def _ejecutar_consultar_ventas(args: dict, id_empresa: int) -> dict:
    periodo = args.get("periodo", "hoy")
    sucursal = args.get("sucursal", "").strip()

    hoy = date.today()
    if periodo == "ayer":
        fecha_ini = hoy - timedelta(days=1)
        fecha_fin = fecha_ini
    elif periodo == "esta_semana":
        fecha_ini = hoy - timedelta(days=hoy.weekday())
        fecha_fin = hoy
    elif periodo == "este_mes":
        fecha_ini = hoy.replace(day=1)
        fecha_fin = hoy
    elif periodo == "ultimos_30_dias":
        fecha_ini = hoy - timedelta(days=30)
        fecha_fin = hoy
    else:
        fecha_ini = hoy
        fecha_fin = hoy

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT 
                COUNT(id_venta) as total_ventas,
                COALESCE(SUM(total), 0) as facturacion_total,
                COALESCE(AVG(total), 0) as ticket_promedio
            FROM comercio.vw_ventas_reporte
            WHERE id_empresa = %s
              AND fecha >= %s AND fecha <= %s
        """
        params = [id_empresa, fecha_ini, fecha_fin]

        if sucursal:
            sql += " AND sucursal ILIKE %s"
            params.append(f"%{sucursal}%")

        cur.execute(sql, tuple(params))
        res = cur.fetchone()

        sql_top = """
            SELECT p.nombre as prenda, SUM(dv.cantidad) as total_prendas, SUM(dv.subtotal) as total_bs
            FROM comercio.t_detalle_venta dv
            JOIN comercio.vw_ventas_reporte v ON dv.id_venta = v.id_venta
            JOIN comercio.t_producto_talla_color ptc ON dv.id_variante = ptc.id_variante
            JOIN comercio.t_producto p ON ptc.id_producto = p.id_producto
            WHERE v.id_empresa = %s AND v.fecha >= %s AND v.fecha <= %s
            GROUP BY p.nombre
            ORDER BY total_prendas DESC
            LIMIT 3
        """
        cur.execute(sql_top, (id_empresa, fecha_ini, fecha_fin))
        top_items = [{
            "prenda": t[0],
            "unidades": int(t[1]),
            "subtotal": float(t[2])
        } for t in cur.fetchall()]

        return {
            "periodo": periodo,
            "rango_fechas": f"{fecha_ini} al {fecha_fin}",
            "total_ventas": int(res[0] or 0),
            "facturacion_total_bs": float(res[1] or 0.0),
            "ticket_promedio_bs": float(res[2] or 0.0),
            "top_prendas": top_items
        }
    finally:
        conn.close()


def _ejecutar_consultar_inventario_alertas(args: dict, id_empresa: int) -> dict:
    filtro = args.get("filtro", "agotados")
    sucursal = args.get("sucursal", "").strip()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT producto, sku, talla, color, sucursal, stock_actual, stock_disponible, stock_minimo
            FROM comercio.vw_inventario_reporte
            WHERE id_empresa = %s
        """
        params = [id_empresa]

        if filtro == "agotados":
            sql += " AND stock_disponible = 0"
        elif filtro == "bajo_stock":
            sql += " AND stock_disponible <= stock_minimo AND stock_disponible > 0"

        if sucursal:
            sql += " AND sucursal ILIKE %s"
            params.append(f"%{sucursal}%")

        sql += " ORDER BY stock_disponible ASC, producto ASC LIMIT 10"

        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

        items = [{
            "prenda": r[0],
            "sku": r[1],
            "talla": r[2],
            "color": r[3],
            "sucursal": r[4],
            "stock_fisico": int(r[5]),
            "stock_disponible": int(r[6]),
            "stock_minimo": int(r[7])
        } for r in rows]

        return {
            "filtro": filtro,
            "total_items": len(items),
            "items": items
        }
    finally:
        conn.close()


def _ejecutar_consultar_indicadores_kpi(id_empresa: int) -> dict:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        hoy = date.today()
        ini_mes = hoy.replace(day=1)
        cur.execute("""
            SELECT COUNT(id_venta), COALESCE(SUM(total), 0), COALESCE(AVG(total), 0)
            FROM comercio.vw_ventas_reporte
            WHERE id_empresa = %s AND fecha >= %s
        """, (id_empresa, ini_mes))
        v = cur.fetchone()

        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE stock_disponible = 0) as sin_stock,
                COUNT(*) FILTER (WHERE stock_disponible <= stock_minimo AND stock_disponible > 0) as bajo_stock,
                COALESCE(SUM(stock_actual), 0) as stock_total
            FROM comercio.vw_inventario_reporte
            WHERE id_empresa = %s
        """, (id_empresa,))
        inv = cur.fetchone()

        return {
            "mes": hoy.strftime("%B %Y"),
            "ventas_mes_count": int(v[0] or 0),
            "ingresos_mes_bs": float(v[1] or 0.0),
            "ticket_promedio_bs": float(v[2] or 0.0),
            "prendas_agotadas": int(inv[0] or 0),
            "prendas_bajo_stock": int(inv[1] or 0),
            "stock_fisico_total": int(inv[2] or 0)
        }
    finally:
        conn.close()


def _ejecutar_consultar_ventas_pendientes(args: dict, id_empresa: int) -> dict:
    sucursal = args.get("sucursal", "").strip()
    canal = args.get("canal", "todos").lower()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT numero_documento, cliente, telefono, sucursal, canal, total, dias_pendiente, estado_pago
            FROM comercio.vw_ventas_pendientes_reporte
            WHERE id_empresa = %s
        """
        params = [id_empresa]

        if sucursal:
            sql += " AND sucursal ILIKE %s"
            params.append(f"%{sucursal}%")

        if canal == "pos":
            sql += " AND canal ILIKE '%POS%'"
        elif canal == "online":
            sql += " AND canal ILIKE '%ONLINE%'"

        sql += " ORDER BY dias_pendiente DESC, total DESC LIMIT 10"

        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

        items = [{
            "numero_pedido": r[0],
            "cliente": r[1],
            "telefono": r[2],
            "sucursal": r[3],
            "canal": r[4],
            "total_bs": float(r[5] or 0),
            "dias_pendiente": int(r[6] or 0),
            "estado": r[7]
        } for r in rows]

        cur.execute("""
            SELECT COUNT(*), COALESCE(SUM(total), 0)
            FROM comercio.vw_ventas_pendientes_reporte
            WHERE id_empresa = %s
        """, (id_empresa,))
        totales = cur.fetchone()

        return {
            "total_pendientes_count": int(totales[0] or 0),
            "total_por_cobrar_bs": float(totales[1] or 0),
            "items": items
        }
    finally:
        conn.close()


def _ejecutar_consultar_reservas_empresa(args: dict, id_empresa: int) -> dict:
    sucursal = args.get("sucursal", "").strip()
    vigencia = args.get("vigencia", "todas").lower()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT codigo_reserva, cliente, telefono, sucursal, prenda, talla, color, cantidad, subtotal_estimado, vigencia, fecha_vencimiento
            FROM comercio.vw_reservas_reporte
            WHERE id_empresa = %s
        """
        params = [id_empresa]

        if sucursal:
            sql += " AND sucursal ILIKE %s"
            params.append(f"%{sucursal}%")

        if vigencia == "vigente":
            sql += " AND vigencia = 'VIGENTE'"
        elif vigencia == "vencida":
            sql += " AND vigencia = 'VENCIDA'"

        sql += " ORDER BY fecha_vencimiento ASC LIMIT 10"

        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

        items = [{
            "codigo_reserva": r[0],
            "cliente": r[1],
            "telefono": r[2],
            "sucursal": r[3],
            "prenda": f"{r[4]} ({r[5]} - {r[6]})",
            "cantidad": int(r[7] or 1),
            "total_bs": float(r[8] or 0),
            "estado": r[9],
            "fecha_vencimiento": str(r[10])
        } for r in rows]

        cur.execute("""
            SELECT COUNT(*), COALESCE(SUM(subtotal_estimado), 0),
                   COUNT(*) FILTER (WHERE vigencia = 'VENCIDA')
            FROM comercio.vw_reservas_reporte
            WHERE id_empresa = %s
        """, (id_empresa,))
        res = cur.fetchone()

        return {
            "total_reservas": int(res[0] or 0),
            "monto_estimado_bs": float(res[1] or 0),
            "reservas_vencidas": int(res[2] or 0),
            "items": items
        }
    finally:
        conn.close()


def _ejecutar_consultar_auditoria_pos(args: dict, id_empresa: int) -> dict:
    sucursal = args.get("sucursal", "").strip()
    solo_alertas = args.get("solo_alertas", False)

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT numero_venta, fecha, hora, sucursal, caja, cajero, cliente, metodo_pago, total, estado_venta, alerta_auditoria
            FROM comercio.vw_pos_reporte
            WHERE id_empresa = %s
        """
        params = [id_empresa]

        if sucursal:
            sql += " AND sucursal ILIKE %s"
            params.append(f"%{sucursal}%")

        if solo_alertas:
            sql += " AND alerta_auditoria != '✓ COBRADO Y CUADRADO'"

        sql += " ORDER BY fecha DESC, hora DESC LIMIT 10"

        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

        items = [{
            "numero_pedido": r[0],
            "fecha": f"{r[1]} {r[2]}",
            "sucursal": r[3],
            "caja": r[4],
            "cajero": r[5],
            "cliente": r[6],
            "metodo_pago": r[7],
            "total_bs": float(r[8] or 0),
            "estado": r[9],
            "alerta": r[10]
        } for r in rows]

        cur.execute("""
            SELECT 
                COUNT(*),
                COALESCE(SUM(total), 0),
                COUNT(*) FILTER (WHERE alerta_auditoria != '✓ COBRADO Y CUADRADO'),
                COUNT(*) FILTER (WHERE estado_venta = 'PENDIENTE_PAGO')
            FROM comercio.vw_pos_reporte
            WHERE id_empresa = %s
        """, (id_empresa,))
        pos_stats = cur.fetchone()

        return {
            "total_ventas_pos": int(pos_stats[0] or 0),
            "monto_total_pos_bs": float(pos_stats[1] or 0),
            "ventas_con_alerta": int(pos_stats[2] or 0),
            "ventas_sin_cobro": int(pos_stats[3] or 0),
            "items": items
        }
    finally:
        conn.close()


# =====================================================================
# DESPACHADOR DE HERRAMIENTAS
# =====================================================================

def despachar_herramienta(tool_name: str, tool_args: dict, token_data: Optional[dict], id_empresa: int) -> tuple[dict, str]:
    id_usuario = token_data.get("id_usuario") if token_data else None

    if tool_name == "buscar_prendas_catalogo":
        res = _ejecutar_buscar_prendas(tool_args, id_empresa)
        return res, "productos"

    elif tool_name == "consultar_detalle_prenda":
        res = _ejecutar_detalle_prenda(tool_args, id_empresa)
        return res, "productos"

    elif tool_name == "consultar_sucursales_tiendas":
        res = _ejecutar_consultar_sucursales(id_empresa)
        return res, "tabla"

    elif tool_name == "consultar_mis_pedidos":
        res = _ejecutar_consultar_mis_pedidos(id_usuario, tool_args.get("limite", 5))
        return res, "tabla"

    elif tool_name == "consultar_mis_reservas":
        res = _ejecutar_consultar_mis_reservas(id_usuario, tool_args.get("limite", 5))
        return res, "tabla"

    elif tool_name == "consultar_ventas_empresa":
        res = _ejecutar_consultar_ventas(tool_args, id_empresa)
        return res, "indicadores"

    elif tool_name == "consultar_inventario_alertas":
        res = _ejecutar_consultar_inventario_alertas(tool_args, id_empresa)
        return res, "tabla"

    elif tool_name == "consultar_ventas_pendientes":
        res = _ejecutar_consultar_ventas_pendientes(tool_args, id_empresa)
        return res, "tabla"

    elif tool_name == "consultar_reservas_prendas_empresa":
        res = _ejecutar_consultar_reservas_empresa(tool_args, id_empresa)
        return res, "tabla"

    elif tool_name == "consultar_auditoria_pos_errores":
        res = _ejecutar_consultar_auditoria_pos(tool_args, id_empresa)
        return res, "tabla"

    elif tool_name == "consultar_indicadores_kpi_generales":
        res = _ejecutar_consultar_indicadores_kpi(id_empresa)
        return res, "indicadores"

    elif tool_name == "generar_reporte_directo":
        tipo = tool_args.get("tipo_reporte", "ventas")
        if tipo == "ventas":
            res = _ejecutar_consultar_ventas({"periodo": "este_mes"}, id_empresa)
        elif tipo == "inventario":
            res = _ejecutar_consultar_inventario_alertas({"filtro": "todos"}, id_empresa)
        elif tipo == "ventas_pendientes":
            res = _ejecutar_consultar_ventas_pendientes({}, id_empresa)
        elif tipo == "reservas":
            res = _ejecutar_consultar_reservas_empresa({}, id_empresa)
        elif tipo == "pos":
            res = _ejecutar_consultar_auditoria_pos({}, id_empresa)
        else:
            res = _ejecutar_consultar_indicadores_kpi(id_empresa)
        return res, "reporte"

    return {"error": f"Herramienta '{tool_name}' desconocida."}, "texto"


# =====================================================================
# SERVICIO PRINCIPAL DE CHAT CON DEEPSEEK
# =====================================================================

def procesar_mensaje_chat(mensaje: str, historial: Optional[List[dict]] = None, token_data: Optional[dict] = None) -> dict:
    if not mensaje or not mensaje.strip():
        return {
            "respuesta": "Por favor escribe tu consulta.",
            "tipo": "texto",
            "datos": None
        }

    id_empresa = (token_data.get("id_empresa") if token_data else None) or 1
    roles = [str(r).upper() for r in (token_data.get("roles", []) if token_data else [])]
    id_rol = token_data.get("id_rol") if token_data else 2
    es_admin = (id_rol == 1 or "ADMINISTRADOR" in roles or "ADMINISTRADOR_TIENDA" in roles or 
                "ENCARGADO" in roles or "EMPLEADO" in roles)

    herramientas = list(CLIENT_TOOLS)
    if es_admin:
        herramientas.extend(ADMIN_TOOLS)

    fecha_hoy = datetime.now().strftime("%d de %B de %Y")
    nombre_usuario = token_data.get("nombre") if token_data else "estimado cliente"
    empresa_nombre = token_data.get("nombre_empresa") if token_data else "Aurora Store"

    rol_desc = "un miembro del equipo administrativo" if es_admin else "un cliente exclusivo"
    system_prompt = f"""Eres 'Aurora Assistant', la asistente virtual inteligente y asesora de estilo de {empresa_nombre}.
Hoy es {fecha_hoy}. Estás atendiendo a {nombre_usuario}, quien es {rol_desc}.

Instrucciones de comportamiento:
1. Responde con un tono elegante, cordial, conciso y profesional propio del mundo de la moda y alta costura.
2. Si el usuario te saluda o hace preguntas generales, salúdalo con calidez y explícale brevemente en qué puedes asistirle.
3. UTILIZA SIEMPRE las herramientas disponibles para consultar datos reales (productos, ventas, inventarios, pedidos o tiendas). Nunca inventes información de catálogo ni cifras ficticias.
4. Si encuentras prendas en el catálogo, destaca brevemente sus cualidades (material, precio en Bs., tallas o colores disponibles).
5. Sé directo: evita textos kilométricos o redundantes."""

    messages = [{"role": "system", "content": system_prompt}]
    if historial and isinstance(historial, list):
        for h in historial[-6:]:
            if isinstance(h, dict) and "role" in h and "content" in h:
                if h["role"] in ["user", "assistant"]:
                    messages.append({"role": h["role"], "content": str(h["content"])})

    messages.append({"role": "user", "content": mensaje.strip()})

    api_key = Config.DEEPSEEK_API_KEY
    base_url = Config.DEEPSEEK_BASE_URL.rstrip("/")
    model = Config.DEEPSEEK_MODEL

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "tools": herramientas,
        "tool_choice": "auto",
        "temperature": 0.2,
        "max_tokens": 1000
    }

    try:
        response = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=25)
        if response.status_code != 200:
            logger.error(f"Error DeepSeek API status {response.status_code}: {response.text}")
            return {
                "respuesta": "No pude procesar la solicitud en este momento con el servidor de inteligencia artificial. Inténtalo nuevamente en unos instantes.",
                "tipo": "texto",
                "datos": None
            }

        res_json = response.json()
        choice = res_json["choices"][0]["message"]

        if choice.get("tool_calls"):
            tool_call = choice["tool_calls"][0]
            func_name = tool_call["function"]["name"]
            func_args_str = tool_call["function"].get("arguments", "{}")
            try:
                func_args = json.loads(func_args_str) if isinstance(func_args_str, str) else func_args_str
            except Exception:
                func_args = {}

            tool_result, tipo_sugerido = despachar_herramienta(func_name, func_args, token_data, id_empresa)

            messages.append(choice)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": func_name,
                "content": json.dumps(tool_result, ensure_ascii=False)
            })

            followup_payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 800
            }

            followup_resp = requests.post(f"{base_url}/chat/completions", headers=headers, json=followup_payload, timeout=20)
            if followup_resp.status_code == 200:
                followup_choice = followup_resp.json()["choices"][0]["message"]
                texto_respuesta = followup_choice.get("content", "")
            else:
                texto_respuesta = "Aquí tienes los datos solicitados."

            datos_salida = None
            if tipo_sugerido == "productos" and "productos" in tool_result:
                datos_salida = tool_result["productos"]
            elif tipo_sugerido == "productos" and "variantes_stock" in tool_result:
                datos_salida = [tool_result]
            elif tipo_sugerido == "tabla" and "items" in tool_result:
                datos_salida = tool_result["items"]
            elif tipo_sugerido == "tabla" and "sucursales" in tool_result:
                datos_salida = tool_result["sucursales"]
            elif tipo_sugerido == "tabla" and "pedidos" in tool_result:
                datos_salida = tool_result["pedidos"]
            elif tipo_sugerido == "tabla" and "reservas" in tool_result:
                datos_salida = tool_result["reservas"]
            elif tipo_sugerido == "indicadores":
                datos_salida = tool_result
            elif tipo_sugerido == "reporte":
                datos_salida = tool_result

            return {
                "respuesta": texto_respuesta,
                "tipo": tipo_sugerido if datos_salida else "texto",
                "datos": datos_salida
            }

        return {
            "respuesta": choice.get("content", "En qué puedo colaborarte hoy?"),
            "tipo": "texto",
            "datos": None
        }

    except requests.exceptions.Timeout:
        logger.warning("Timeout al conectar con DeepSeek API.")
        return {
            "respuesta": "La conexión con el asistente tardó más de lo esperado. Por favor realiza tu consulta nuevamente.",
            "tipo": "texto",
            "datos": None
        }
    except Exception as e:
        logger.error(f"Error procesando chat asistente: {e}", exc_info=True)
        return {
            "respuesta": "El asistente no está disponible temporalmente. Las demás funciones de Aurora Store continúan funcionando normalmente.",
            "tipo": "texto",
            "datos": None
        }
