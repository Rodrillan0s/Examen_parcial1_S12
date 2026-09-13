import json
import logging
from typing import Dict, Any, Optional
from app.classes.postgres import PostgreSQL
from app.config import Config

logger = logging.getLogger(__name__)

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

def obtener_metodo_pago_id(tipo: str) -> int:
    """
    Retorna el ID de t_metodo_pago según su tipo ('TARJETA', 'PAYPAL', 'EFECTIVO').
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        row = db.execute_query(
            f"SELECT id_metodo_pago FROM {schema}.t_metodo_pago WHERE UPPER(tipo) = UPPER(%s) AND estado = TRUE LIMIT 1;",
            (tipo,),
            fetchone=True
        )
        if row:
            return row[0]
        return -99
    finally:
        db.close_connection()

def validar_pedido_para_pago(id_pedido: int, id_usuario: int, id_empresa: Optional[int] = None) -> Dict[str, Any]:
    """
    Valida que el pedido exista, pertenezca al usuario/cliente y tenant, y se encuentre en estado PENDIENTE_PAGO.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        q = f"""
            SELECT 
                p.id_pedido,
                p.codigo_pedido,
                p.id_cliente,
                p.id_empresa,
                p.id_sucursal,
                p.estado,
                p.estado_pago,
                p.subtotal,
                p.costo_envio,
                p.descuento,
                p.total,
                p.correo_contacto,
                p.nombre_contacto,
                p.id_venta,
                s.nombre AS sucursal_nombre,
                emp.nombre_empresa
            FROM {schema}.t_pedido p
            JOIN {schema}.t_sucursal s ON s.id_sucursal = p.id_sucursal
            LEFT JOIN {schema}.empresa emp ON emp.id_empresa = p.id_empresa
            JOIN {schema}.t_cliente c ON c.id_cliente = p.id_cliente
            WHERE p.id_pedido = %s AND c.id_usuario = %s
            LIMIT 1;
        """
        row = db.execute_query(q, (id_pedido, id_usuario), fetchone=True)
        if not row:
            raise ValueError("Pedido no encontrado o no pertenece a tu cuenta.")

        if id_empresa and row[3] != id_empresa:
            raise ValueError("El pedido no pertenece a la tienda (Tenant) activa.")

        estado_pago = row[6]
        if estado_pago == 'PAGADO' or row[13] is not None:
            raise ValueError(f"El pedido {row[1]} ya se encuentra pagado.")

        if row[5] in ('CANCELADO', 'ANULADO'):
            raise ValueError(f"El pedido {row[1]} fue cancelado y no admite pagos.")

        # Obtener detalle de prendas
        q_items = f"""
            SELECT 
                dp.id_variante,
                dp.cantidad,
                dp.precio_unitario,
                dp.subtotal,
                p.nombre AS producto_nombre,
                v.sku,
                t.nombre AS talla_nombre,
                col.nombre AS color_nombre
            FROM {schema}.t_detalle_pedido dp
            JOIN {schema}.t_producto_talla_color v ON v.id_variante = dp.id_variante
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla
            JOIN {schema}.t_color col ON col.id_color = v.id_color
            WHERE dp.id_pedido = %s
            ORDER BY dp.id_detalle_pedido ASC;
        """
        items_raw = db.execute_query(q_items, (id_pedido,), fetchall=True) or []
        items = []
        for it in items_raw:
            items.append({
                "id_variante": it[0],
                "cantidad": it[1],
                "precio_unitario": float(it[2]),
                "subtotal": float(it[3]),
                "producto_nombre": it[4],
                "sku": it[5],
                "talla": it[6],
                "color": it[7]
            })

        return {
            "id_pedido": row[0],
            "codigo_pedido": row[1],
            "id_cliente": row[2],
            "id_empresa": row[3],
            "id_sucursal": row[4],
            "estado": row[5],
            "estado_pago": row[6],
            "subtotal": float(row[7]),
            "costo_envio": float(row[8]),
            "descuento": float(row[9]),
            "total": float(row[10]),
            "correo_contacto": row[11] or "",
            "nombre_contacto": row[12] or "Cliente",
            "id_venta": row[13],
            "sucursal_nombre": row[14],
            "nombre_empresa": row[15] or "AURA Atelier",
            "items": items
        }
    finally:
        db.close_connection()

def ejecutar_confirmacion_pago(
    id_pedido: int,
    tipo_metodo: str,
    codigo_transaccion: str,
    monto: float,
    id_usuario: int,
    nit_ci: Optional[str] = None,
    razon_social: Optional[str] = None,
    tipo_documento: Optional[str] = None
) -> Dict[str, Any]:
    """
    Invoca atómicamente la función PostgreSQL fn_confirmar_pago_pedido.
    Garantiza aislamiento transaccional y prevención de sobreventas con FOR UPDATE.
    """
    id_metodo_pago = obtener_metodo_pago_id(tipo_metodo)

    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        q = f"""
            SELECT {schema}.fn_confirmar_pago_pedido(
                %s, %s, %s, %s, %s, %s, %s, %s
            );
        """
        params = (
            id_pedido,
            id_metodo_pago,
            codigo_transaccion,
            monto,
            id_usuario,
            nit_ci,
            razon_social,
            tipo_documento
        )

        res = db.execute_query(q, params, fetchone=True, commit=True)
        if not res or not res[0]:
            raise ValueError("No se recibió respuesta de la función transaccional de pagos.")

        data = res[0]
        if isinstance(data, str):
            data = json.loads(data)

        if not data.get("success"):
            error_code = data.get("error", "ERROR_PAGO")
            msg = data.get("message", "Error al confirmar el pago en la base de datos.")
            raise ValueError(f"[{error_code}] {msg}")

        return data
    finally:
        db.close_connection()

def obtener_venta_por_pedido(id_pedido: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene la venta asociada a un pedido.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        row = db.execute_query(
            f"SELECT id_venta FROM {schema}.t_pedido WHERE id_pedido = %s LIMIT 1;",
            (id_pedido,),
            fetchone=True
        )
        if not row or not row[0]:
            return None
        return {"id_venta": row[0]}
    finally:
        db.close_connection()
