import json
import logging
from typing import Dict, Any, List, Optional
from app.classes.postgres import PostgreSQL
from app.config import Config

logger = logging.getLogger(__name__)

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

def buscar_productos_pos(
    id_sucursal: int,
    id_empresa: int,
    q: Optional[str] = None,
    id_categoria: Optional[int] = None,
    solo_con_stock: bool = False
) -> List[Dict[str, Any]]:
    """
    Retorna el catálogo optimizado para el POS de la sucursal activa.
    Incluye variantes, tallas, colores y stock disponible en tiempo real.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        filtros = [
            "p.id_empresa = %s",
            "p.activo = TRUE",
            "v.activo = TRUE",
            "inv.id_sucursal = %s"
        ]
        params: List[Any] = [id_empresa, id_sucursal]

        if id_categoria and id_categoria > 0:
            filtros.append("p.id_categoria = %s")
            params.append(id_categoria)

        if solo_con_stock:
            filtros.append("inv.stock_disponible > 0")

        if q and q.strip():
            filtro_q = q.strip()
            filtros.append("""(
                p.nombre ILIKE %s OR 
                p.codigo_producto ILIKE %s OR 
                v.sku ILIKE %s OR 
                v.codigo_barras ILIKE %s
            )""")
            term = f"%{filtro_q}%"
            params.extend([term, term, term, term])

        where_str = " AND ".join(filtros)

        sql = f"""
            SELECT 
                p.id_producto,
                p.nombre AS producto_nombre,
                p.codigo_producto,
                p.precio AS precio_base,
                p.imagen_url,
                p.id_categoria,
                c.nombre AS categoria_nombre,
                v.id_variante,
                v.sku,
                v.codigo_barras,
                COALESCE(v.precio, p.precio) AS precio_variante,
                t.nombre AS talla_nombre,
                col.nombre AS color_nombre,
                col.codigo_hex,
                inv.stock_disponible,
                inv.stock_actual
            FROM {schema}.t_producto p
            JOIN {schema}.t_categoria c ON c.id_categoria = p.id_categoria
            JOIN {schema}.t_producto_talla_color v ON v.id_producto = p.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla
            JOIN {schema}.t_color col ON col.id_color = v.id_color
            JOIN {schema}.t_inventario inv ON inv.id_variante = v.id_variante
            WHERE {where_str}
            ORDER BY p.nombre ASC, t.nombre ASC;
        """

        rows = db.execute_query(sql, tuple(params), fetchall=True) or []

        # Agrupar variantes dentro de cada producto
        productos_map: Dict[int, Dict[str, Any]] = {}

        for r in rows:
            id_prod = r[0]
            if id_prod not in productos_map:
                productos_map[id_prod] = {
                    "id_producto": id_prod,
                    "nombre": r[1],
                    "codigo_producto": r[2],
                    "precio_base": float(r[3]),
                    "imagen_url": r[4],
                    "id_categoria": r[5],
                    "categoria_nombre": r[6],
                    "stock_total_sucursal": 0,
                    "variantes": []
                }

            stock_disp = r[14] or 0
            productos_map[id_prod]["stock_total_sucursal"] += stock_disp
            productos_map[id_prod]["variantes"].append({
                "id_variante": r[7],
                "sku": r[8],
                "codigo_barras": r[9],
                "precio": float(r[10]),
                "talla": r[11],
                "color": r[12],
                "codigo_hex": r[13],
                "stock_disponible": stock_disp,
                "stock_actual": r[15] or 0
            })

        return list(productos_map.values())
    finally:
        db.close_connection()

def obtener_variantes_producto_pos(id_producto: int, id_sucursal: int) -> List[Dict[str, Any]]:
    """
    Retorna las variantes activas de un producto específico con su stock en la sucursal.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        sql = f"""
            SELECT 
                v.id_variante,
                v.sku,
                v.codigo_barras,
                COALESCE(v.precio, p.precio) AS precio,
                t.nombre AS talla_nombre,
                col.nombre AS color_nombre,
                col.codigo_hex,
                COALESCE(inv.stock_disponible, 0) AS stock_disponible,
                COALESCE(inv.stock_actual, 0) AS stock_actual
            FROM {schema}.t_producto_talla_color v
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla
            JOIN {schema}.t_color col ON col.id_color = v.id_color
            LEFT JOIN {schema}.t_inventario inv ON inv.id_variante = v.id_variante AND inv.id_sucursal = %s
            WHERE v.id_producto = %s AND v.activo = TRUE AND p.activo = TRUE
            ORDER BY t.nombre ASC, col.nombre ASC;
        """
        rows = db.execute_query(sql, (id_sucursal, id_producto), fetchall=True) or []
        resultado = []
        for r in rows:
            resultado.append({
                "id_variante": r[0],
                "sku": r[1],
                "codigo_barras": r[2],
                "precio": float(r[3]),
                "talla": r[4],
                "color": r[5],
                "codigo_hex": r[6],
                "stock_disponible": r[7],
                "stock_actual": r[8]
            })
        return resultado
    finally:
        db.close_connection()

def buscar_clientes_pos(id_empresa: int, query: str) -> List[Dict[str, Any]]:
    """
    Búsqueda rápida de clientes para el POS por CI, nombre, apellido o correo.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        term = f"%{query.strip()}%"
        sql = f"""
            SELECT 
                c.id_cliente,
                c.ci,
                u.nombre,
                u.apellido,
                u.correo,
                u.telefono
            FROM {schema}.t_cliente c
            JOIN {schema}.t_usuario u ON u.id_usuario = c.id_usuario
            WHERE (
                c.ci ILIKE %s OR 
                u.nombre ILIKE %s OR 
                u.apellido ILIKE %s OR 
                u.correo ILIKE %s
            )
            ORDER BY u.nombre ASC
            LIMIT 15;
        """
        rows = db.execute_query(sql, (term, term, term, term), fetchall=True) or []
        resultado = []
        for r in rows:
            resultado.append({
                "id_cliente": r[0],
                "ci": r[1] or "",
                "nombre": r[2],
                "apellido": r[3] or "",
                "nombre_completo": f"{r[2]} {r[3] or ''}".strip(),
                "correo": r[4] or "",
                "telefono": r[5] or ""
            })
        return resultado
    finally:
        db.close_connection()

def ejecutar_registro_venta_pos(
    id_sesion_caja: int,
    id_usuario: int,
    id_sucursal: int,
    id_empresa: int,
    id_cliente: Optional[int],
    items: List[Dict[str, Any]],
    descuento: float = 0.0,
    observacion: Optional[str] = None
) -> Dict[str, Any]:
    """
    Invoca la función transaccional fn_registrar_venta_pos en PostgreSQL.
    Asegura stock con FOR UPDATE, crea t_venta en PENDIENTE_PAGO y t_detalle_venta.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        items_json = json.dumps(items)

        sql = f"""
            SELECT {schema}.fn_registrar_venta_pos(
                %s, %s, %s, %s, %s, %s::json, %s, %s
            );
        """
        params = (
            id_sesion_caja,
            id_usuario,
            id_sucursal,
            id_empresa,
            id_cliente,
            items_json,
            descuento,
            observacion
        )

        res = db.execute_query(sql, params, fetchone=True, commit=True)
        if not res or not res[0]:
            raise ValueError("No se recibió respuesta de la función transaccional del POS.")

        data = res[0]
        if isinstance(data, str):
            data = json.loads(data)

        if not data.get("success"):
            err_code = data.get("error", "ERROR_VENTA_POS")
            msg = data.get("message", "Error al procesar la venta en el POS.")
            raise ValueError(f"[{err_code}] {msg}")

        return data
    finally:
        db.close_connection()

def obtener_historial_ventas_sesion(id_sesion_caja: int) -> List[Dict[str, Any]]:
    """
    Retorna el listado de ventas generadas durante la sesión de caja activa.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        sql = f"""
            SELECT 
                v.id_venta,
                v.numero_venta,
                v.fecha_venta,
                v.subtotal,
                v.descuento,
                v.total,
                v.estado,
                v.tipo_venta,
                v.observacion,
                c.id_cliente,
                c.ci AS cliente_ci,
                u.nombre AS cliente_nombre,
                u.apellido AS cliente_apellido,
                (
                    SELECT COUNT(*) 
                    FROM {schema}.t_detalle_venta dv 
                    WHERE dv.id_venta = v.id_venta
                ) AS cant_items
            FROM {schema}.t_venta v
            LEFT JOIN {schema}.t_cliente c ON c.id_cliente = v.id_cliente
            LEFT JOIN {schema}.t_usuario u ON u.id_usuario = c.id_usuario
            WHERE v.id_sesion_caja = %s
            ORDER BY v.id_venta DESC;
        """
        rows = db.execute_query(sql, (id_sesion_caja,), fetchall=True) or []
        resultado = []
        for r in rows:
            cliente_nombre = "Sin cliente"
            if r[9] or r[11]:
                cliente_nombre = f"{r[11]} {r[12] or ''}".strip()
                if r[10]:
                    cliente_nombre += f" (CI: {r[10]})"

            resultado.append({
                "id_venta": r[0],
                "numero_venta": r[1],
                "fecha_venta": r[2].isoformat() if r[2] else None,
                "subtotal": float(r[3]),
                "descuento": float(r[4]),
                "total": float(r[5]),
                "estado": r[6],
                "tipo_venta": r[7],
                "observacion": r[8],
                "id_cliente": r[9],
                "cliente_str": cliente_nombre,
                "cant_items": r[13]
            })
        return resultado
    finally:
        db.close_connection()

def obtener_detalle_venta_pos(id_venta: int) -> Optional[Dict[str, Any]]:
    """
    Retorna el detalle completo de una venta presencial con sus prendas y pagos.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        sql_head = f"""
            SELECT 
                v.id_venta,
                v.numero_venta,
                v.fecha_venta,
                v.subtotal,
                v.descuento,
                v.total,
                v.estado,
                v.tipo_venta,
                v.observacion,
                v.id_sesion_caja,
                c.id_cliente,
                c.ci,
                u.nombre,
                u.apellido,
                u.correo,
                suc.nombre AS nombre_sucursal
            FROM {schema}.t_venta v
            LEFT JOIN {schema}.t_cliente c ON c.id_cliente = v.id_cliente
            LEFT JOIN {schema}.t_usuario u ON u.id_usuario = c.id_usuario
            LEFT JOIN {schema}.t_sucursal suc ON suc.id_sucursal = v.id_sucursal
            WHERE v.id_venta = %s
            LIMIT 1;
        """
        head = db.execute_query(sql_head, (id_venta,), fetchone=True)
        if not head:
            return None

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
                col.nombre AS color_nombre
            FROM {schema}.t_detalle_venta dv
            JOIN {schema}.t_producto_talla_color v ON v.id_variante = dv.id_variante
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla
            JOIN {schema}.t_color col ON col.id_color = v.id_color
            WHERE dv.id_venta = %s
            ORDER BY dv.id_detalle_venta ASC;
        """
        items_rows = db.execute_query(sql_items, (id_venta,), fetchall=True) or []
        items = []
        for it in items_rows:
            items.append({
                "id_detalle_venta": it[0],
                "id_variante": it[1],
                "cantidad": it[2],
                "precio_unitario": float(it[3]),
                "descuento": float(it[4]),
                "subtotal": float(it[5]),
                "producto_nombre": it[6],
                "sku": it[7],
                "talla": it[8],
                "color": it[9]
            })

        cliente_str = "Sin cliente"
        if head[12]:
            cliente_str = f"{head[12]} {head[13] or ''}".strip()
            if head[11]:
                cliente_str += f" (CI: {head[11]})"

        return {
            "id_venta": head[0],
            "numero_venta": head[1],
            "fecha_venta": head[2].isoformat() if head[2] else None,
            "subtotal": float(head[3]),
            "descuento": float(head[4]),
            "total": float(head[5]),
            "estado": head[6],
            "tipo_venta": head[7],
            "observacion": head[8],
            "id_sesion_caja": head[9],
            "id_cliente": head[10],
            "cliente_str": cliente_str,
            "cliente_correo": head[14],
            "nombre_sucursal": head[15],
            "items": items
        }
    finally:
        db.close_connection()
