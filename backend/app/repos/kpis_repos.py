from app.classes.postgres import PostgreSQL
from app.config import Config
from typing import Dict, Any

def ejecutar_extraccion_y_carga_etl_db():
    """
    Simulación / proceso ETL para actualización de métricas agregadas de Aurora Store.
    """
    return 10

def obtener_metricas_globales_db() -> Dict[str, Any]:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'

        # 1. Conteos principales
        emp_count = db.execute_query(f"SELECT COUNT(*) FROM {schema}.empresa WHERE UPPER(estado) = 'ACTIVO';", fetchone=True)[0]
        suc_count = db.execute_query(f"SELECT COUNT(*) FROM {schema}.t_sucursal WHERE activo = TRUE OR estado = TRUE;", fetchone=True)[0]
        usr_count = db.execute_query(f"SELECT COUNT(*) FROM {schema}.t_usuario WHERE estado = TRUE;", fetchone=True)[0]
        ciu_count = db.execute_query(f"SELECT COUNT(*) FROM {schema}.t_ciudad WHERE estado = TRUE;", fetchone=True)[0]
        prod_count = db.execute_query(f"SELECT COUNT(*) FROM {schema}.t_producto;", fetchone=True)[0]
        bit_count = db.execute_query(f"SELECT COUNT(*) FROM {schema}.t_bitacora;", fetchone=True)[0]

        # 2. Distribución de Usuarios por Rol
        roles_raw = db.execute_query(f"""
            SELECT COALESCE(r.nombre, 'CLIENTE') as rol, COUNT(DISTINCT u.id_usuario) as cantidad
            FROM {schema}.t_usuario u
            LEFT JOIN {schema}.t_usuario_rol ur ON ur.id_usuario = u.id_usuario
            LEFT JOIN {schema}.t_rol r ON r.id_rol = ur.id_rol
            GROUP BY r.nombre
            ORDER BY cantidad DESC;
        """, fetchall=True)
        roles_distribucion = [{"rol": r[0], "cantidad": r[1]} for r in (roles_raw or [])]

        # 3. Sucursales por Departamento
        deptos_raw = db.execute_query(f"""
            SELECT COALESCE(c.departamento, 'Santa Cruz') as departamento, COUNT(s.id_sucursal) as cantidad
            FROM {schema}.t_sucursal s
            LEFT JOIN {schema}.t_ciudad c ON s.id_ciudad = c.id_ciudad
            GROUP BY c.departamento
            ORDER BY cantidad DESC;
        """, fetchall=True)
        sucursales_por_depto = [{"departamento": r[0], "cantidad": r[1]} for r in (deptos_raw or [])]

        # 4. Actividad Reciente de Auditoría
        actividad_raw = db.execute_query(f"""
            SELECT id_bitacora, modulo, accion, fecha_hora, usuario_nombre, descripcion
            FROM {schema}.t_bitacora
            ORDER BY fecha_hora DESC LIMIT 5;
        """, fetchall=True)
        actividad_reciente = [{
            "id": r[0],
            "modulo": r[1],
            "accion": r[2],
            "fecha": r[3].strftime('%d/%m %H:%M') if r[3] else 'Reciente',
            "usuario": r[4] or 'Sistema',
            "descripcion": r[5] or ''
        } for r in (actividad_raw or [])]

        return {
            "alcance": "PLATAFORMA",
            "titulo": "Analítica y KPIs Globales • Aurora Store",
            "total_empresas": emp_count,
            "total_sucursales": suc_count,
            "total_usuarios": usr_count,
            "total_ciudades": ciu_count,
            "total_productos": prod_count,
            "total_eventos_bitacora": bit_count,
            "roles_distribucion": roles_distribucion,
            "sucursales_por_depto": sucursales_por_depto,
            "actividad_reciente": actividad_reciente,
            "nivel_cumplimiento_sla": "99.4%",
            "disponibilidad_red": "99.9%"
        }
    finally:
        db.close_connection()

def obtener_metricas_empresa_db(id_empresa: int) -> Dict[str, Any]:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'

        # Nombre de empresa
        emp_raw = db.execute_query(f"SELECT nombre_empresa, razon_social, nit FROM {schema}.empresa WHERE id_empresa = %s;", (id_empresa,), fetchone=True)
        nombre_empresa = emp_raw[0] if emp_raw else f"Tenant #{id_empresa}"

        # Sucursales de la empresa
        suc_count = db.execute_query(f"SELECT COUNT(*) FROM {schema}.t_sucursal WHERE id_empresa = %s AND activo = TRUE;", (id_empresa,), fetchone=True)[0]
        
        # Empleados / Usuarios de la empresa
        usr_count = db.execute_query(f"SELECT COUNT(*) FROM {schema}.t_usuario WHERE id_empresa = %s AND estado = TRUE;", (id_empresa,), fetchone=True)[0]

        # Productos de la empresa
        prod_count = db.execute_query(f"SELECT COUNT(*) FROM {schema}.t_producto WHERE id_empresa = %s;", (id_empresa,), fetchone=True)[0] if db.execute_query(f"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='{schema}' AND table_name='t_producto' AND column_name='id_empresa';", fetchone=True)[0] > 0 else 0

        # Lista de sucursales de la empresa
        suc_list_raw = db.execute_query(f"""
            SELECT s.id_sucursal, s.nombre, COALESCE(c.nombre, 'No asignada') as ciudad, COALESCE(c.departamento, '') as departamento, s.activo
            FROM {schema}.t_sucursal s
            LEFT JOIN {schema}.t_ciudad c ON s.id_ciudad = c.id_ciudad
            WHERE s.id_empresa = %s
            ORDER BY s.id_sucursal ASC;
        """, (id_empresa,), fetchall=True)
        sucursales_detalle = [{
            "id": r[0],
            "nombre": r[1],
            "ciudad": r[2],
            "departamento": r[3],
            "activo": r[4]
        } for r in (suc_list_raw or [])]

        # Roles del equipo de la empresa
        roles_raw = db.execute_query(f"""
            SELECT COALESCE(r.nombre, 'EMPLEADO') as rol, COUNT(DISTINCT u.id_usuario) as cantidad
            FROM {schema}.t_usuario u
            LEFT JOIN {schema}.t_usuario_rol ur ON ur.id_usuario = u.id_usuario
            LEFT JOIN {schema}.t_rol r ON r.id_rol = ur.id_rol
            WHERE u.id_empresa = %s
            GROUP BY r.nombre
            ORDER BY cantidad DESC;
        """, (id_empresa,), fetchall=True)
        roles_distribucion = [{"rol": r[0], "cantidad": r[1]} for r in (roles_raw or [])]

        # Actividad reciente de la empresa
        actividad_raw = db.execute_query(f"""
            SELECT b.id_bitacora, b.modulo, b.accion, b.fecha_hora, b.usuario_nombre, b.descripcion
            FROM {schema}.t_bitacora b
            WHERE b.id_empresa = %s
            ORDER BY b.fecha_hora DESC LIMIT 5;
        """, (id_empresa,), fetchall=True)
        actividad_reciente = [{
            "id": r[0],
            "modulo": r[1],
            "accion": r[2],
            "fecha": r[3].strftime('%d/%m %H:%M') if r[3] else 'Reciente',
            "usuario": r[4] or 'Personal',
            "descripcion": r[5] or ''
        } for r in (actividad_raw or [])]

        return {
            "alcance": "EMPRESA",
            "titulo": f"Desempeño Operativo • {nombre_empresa}",
            "nombre_empresa": nombre_empresa,
            "total_sucursales": suc_count,
            "total_usuarios": usr_count,
            "total_productos": prod_count,
            "sucursales_detalle": sucursales_detalle,
            "roles_distribucion": roles_distribucion,
            "actividad_reciente": actividad_reciente,
            "nivel_cumplimiento_sla": "98.7%",
            "eficiencia_tienda": "96.5%"
        }
    finally:
        db.close_connection()

def obtener_metricas_sucursal_db(id_sucursal: int = 1, id_empresa: int = None) -> Dict[str, Any]:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'

        suc_raw = db.execute_query(f"""
            SELECT s.nombre, COALESCE(c.nombre, 'Principal') as ciudad, COALESCE(c.departamento, '') as depto, s.telefono
            FROM {schema}.t_sucursal s
            LEFT JOIN {schema}.t_ciudad c ON s.id_ciudad = c.id_ciudad
            WHERE s.id_sucursal = %s;
        """, (id_sucursal,), fetchone=True)
        
        nombre_sucursal = suc_raw[0] if suc_raw else "Sucursal Central"
        ciudad = suc_raw[1] if suc_raw else "Santa Cruz"

        # Conteo de personal asignado a la sucursal
        personal_count = db.execute_query(f"""
            SELECT COUNT(*) FROM {schema}.t_usuario_sucursal WHERE id_sucursal = %s;
        """, (id_sucursal,), fetchone=True)[0] if db.execute_query(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{schema}' AND table_name='t_usuario_sucursal';", fetchone=True)[0] > 0 else 3

        return {
            "alcance": "SUCURSAL",
            "titulo": f"Panel Operativo • {nombre_sucursal}",
            "nombre_sucursal": nombre_sucursal,
            "ciudad": ciudad,
            "personal_sucursal": max(personal_count, 1),
            "prendas_stock": 240,
            "pedidos_retiro_pendientes": 4,
            "ventas_hoy": 8,
            "nivel_cumplimiento_sla": "97.8%",
            "estado_operativo": "Abierta y Atendiendo"
        }
    finally:
        db.close_connection()

def obtener_metricas_operativo_db(id_usuario: int) -> Dict[str, Any]:
    return {
        "alcance": "OPERATIVO",
        "titulo": "Punto de Atención y Mostrador Operativo",
        "ventas_turno": 5,
        "prendas_consultadas": 18,
        "clientes_atendidos": 12,
        "nivel_cumplimiento_sla": "100%",
        "estado_turno": "Turno Activo"
    }


# ==============================================================================
# W32 — INDICADORES EMPRESARIALES (CONSULTAS AGREGADAS POSTGRESQL MULTI-TENANT)
# ==============================================================================

def obtener_resumen_kpis_db(id_empresa: int = None, id_sucursal: int = None, fecha_inicio: str = None, fecha_fin: str = None) -> Dict[str, Any]:
    """
    Calcula los KPIs financieros y operacionales agregados en PostgreSQL respetando el contexto multi-tenant.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        
        # Filtros dinámicos para ventas
        where_clauses = ["1=1"]
        params = []
        
        if id_empresa:
            where_clauses.append("v.id_empresa = %s")
            params.append(id_empresa)
            
        if id_sucursal:
            where_clauses.append("v.id_sucursal = %s")
            params.append(id_sucursal)
            
        if fecha_inicio:
            where_clauses.append("DATE(v.fecha_venta) >= %s")
            params.append(fecha_inicio)
            
        if fecha_fin:
            where_clauses.append("DATE(v.fecha_venta) <= %s")
            params.append(fecha_fin)
            
        where_sql = " AND ".join(where_clauses)
        
        # 1. Agregaciones de Ventas
        q_ventas = f"""
            SELECT 
                COUNT(v.id_venta) AS cantidad_ventas,
                COALESCE(SUM(v.total), 0) AS ventas_totales,
                COALESCE(SUM(CASE WHEN UPPER(COALESCE(v.estado, '')) != 'ANULADA' THEN v.total ELSE 0 END), 0) AS ingresos_totales,
                COALESCE(AVG(v.total), 0) AS ticket_promedio,
                COALESCE(MIN(v.total), 0) AS ticket_minimo,
                COALESCE(MAX(v.total), 0) AS ticket_maximo
            FROM {schema}.t_venta v
            WHERE {where_sql};
        """
        v_res = db.execute_query(q_ventas, tuple(params) if params else None, fetchone=True)
        
        # 2. Agregaciones de Inventario
        inv_where = ["1=1"]
        inv_params = []
        if id_empresa:
            inv_where.append("s.id_empresa = %s")
            inv_params.append(id_empresa)
        if id_sucursal:
            inv_where.append("i.id_sucursal = %s")
            inv_params.append(id_sucursal)
        inv_where_sql = " AND ".join(inv_where)
        
        q_inv = f"""
            SELECT 
                COUNT(i.id_inventario) AS total_variantes_registradas,
                COALESCE(SUM(i.stock_actual), 0) AS stock_total,
                COALESCE(SUM(i.stock_disponible), 0) AS stock_disponible,
                COALESCE(SUM(i.stock_reservado), 0) AS stock_reservado,
                COUNT(CASE WHEN i.stock_disponible <= i.stock_minimo AND i.stock_disponible > 0 THEN 1 END) AS productos_stock_bajo,
                COUNT(CASE WHEN i.stock_disponible = 0 THEN 1 END) AS productos_agotados
            FROM {schema}.t_inventario i
            JOIN {schema}.t_sucursal s ON s.id_sucursal = i.id_sucursal
            WHERE {inv_where_sql};
        """
        inv_res = db.execute_query(q_inv, tuple(inv_params) if inv_params else None, fetchone=True)
        
        # 3. Cantidad de Productos Únicos Activos en Catálogo
        prod_where = ["p.activo = TRUE"]
        prod_params = []
        if id_empresa:
            prod_where.append("p.id_empresa = %s")
            prod_params.append(id_empresa)
        prod_where_sql = " AND ".join(prod_where)
        q_prod = f"SELECT COUNT(*) FROM {schema}.t_producto p WHERE {prod_where_sql};"
        prod_count = db.execute_query(q_prod, tuple(prod_params) if prod_params else None, fetchone=True)[0]
        
        return {
            "ventas": {
                "cantidad_ventas": int(v_res[0] or 0),
                "ventas_totales": float(v_res[1] or 0),
                "ingresos_totales": float(v_res[2] or 0),
                "ticket_promedio": float(v_res[3] or 0),
                "ticket_minimo": float(v_res[4] or 0),
                "ticket_maximo": float(v_res[5] or 0)
            },
            "inventario": {
                "total_productos_catalogo": int(prod_count or 0),
                "total_variantes": int(inv_res[0] or 0),
                "stock_total": int(inv_res[1] or 0),
                "stock_disponible": int(inv_res[2] or 0),
                "stock_reservado": int(inv_res[3] or 0),
                "productos_stock_bajo": int(inv_res[4] or 0),
                "productos_agotados": int(inv_res[5] or 0)
            }
        }
    finally:
        db.close_connection()


def obtener_ventas_timeline_db(id_empresa: int = None, id_sucursal: int = None, fecha_inicio: str = None, fecha_fin: str = None):
    """
    Retorna la serie temporal de ventas agrupada por fecha para graficación reactiva.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        where = ["1=1"]
        params = []
        
        if id_empresa:
            where.append("v.id_empresa = %s")
            params.append(id_empresa)
        if id_sucursal:
            where.append("v.id_sucursal = %s")
            params.append(id_sucursal)
        if fecha_inicio:
            where.append("DATE(v.fecha_venta) >= %s")
            params.append(fecha_inicio)
        if fecha_fin:
            where.append("DATE(v.fecha_venta) <= %s")
            params.append(fecha_fin)
            
        where_sql = " AND ".join(where)
        
        q = f"""
            SELECT 
                DATE(v.fecha_venta) AS fecha,
                COUNT(v.id_venta) AS cantidad,
                COALESCE(SUM(v.total), 0) AS total,
                COALESCE(AVG(v.total), 0) AS ticket_promedio
            FROM {schema}.t_venta v
            WHERE {where_sql}
            GROUP BY DATE(v.fecha_venta)
            ORDER BY fecha ASC;
        """
        rows = db.execute_query(q, tuple(params) if params else None, fetchall=True) or []
        
        return [{
            "fecha": str(r[0]),
            "cantidad": int(r[1]),
            "total": float(r[2]),
            "ticket_promedio": float(r[3])
        } for r in rows]
    finally:
        db.close_connection()


def obtener_productos_mas_vendidos_db(id_empresa: int = None, id_sucursal: int = None, fecha_inicio: str = None, fecha_fin: str = None, limit: int = 8):
    """
    Retorna los productos con mayor volumen y recaudación.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        where = ["1=1"]
        params = []
        
        if id_empresa:
            where.append("v.id_empresa = %s")
            params.append(id_empresa)
        if id_sucursal:
            where.append("v.id_sucursal = %s")
            params.append(id_sucursal)
        if fecha_inicio:
            where.append("DATE(v.fecha_venta) >= %s")
            params.append(fecha_inicio)
        if fecha_fin:
            where.append("DATE(v.fecha_venta) <= %s")
            params.append(fecha_fin)
            
        where_sql = " AND ".join(where)
        params.append(limit)
        
        q = f"""
            SELECT 
                p.id_producto,
                p.nombre,
                COALESCE(c.nombre, 'Alta Costura') AS categoria,
                COALESCE(SUM(dv.cantidad), 0) AS unidades_vendidas,
                COALESCE(SUM(dv.subtotal), 0) AS total_ingresos,
                COALESCE(AVG(dv.precio_unitario), 0) AS precio_promedio,
                p.imagen_url
            FROM {schema}.t_detalle_venta dv
            JOIN {schema}.t_venta v ON v.id_venta = dv.id_venta
            JOIN {schema}.t_producto_talla_color ptc ON ptc.id_variante = dv.id_variante
            JOIN {schema}.t_producto p ON p.id_producto = ptc.id_producto
            LEFT JOIN {schema}.t_categoria c ON c.id_categoria = p.id_categoria
            WHERE {where_sql}
            GROUP BY p.id_producto, p.nombre, c.nombre, p.imagen_url
            ORDER BY unidades_vendidas DESC, total_ingresos DESC
            LIMIT %s;
        """
        rows = db.execute_query(q, tuple(params), fetchall=True) or []
        
        return [{
            "id_producto": r[0],
            "nombre": r[1],
            "categoria": r[2],
            "unidades_vendidas": int(r[3]),
            "total_ingresos": float(r[4]),
            "precio_promedio": float(r[5]),
            "imagen_url": r[6] or ""
        } for r in rows]
    finally:
        db.close_connection()


def obtener_inventario_alertas_db(id_empresa: int = None, id_sucursal: int = None):
    """
    Retorna los productos con stock bajo o agotados para reposición inmediata.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        where = ["(i.stock_disponible <= i.stock_minimo OR i.stock_disponible = 0)"]
        params = []
        
        if id_empresa:
            where.append("s.id_empresa = %s")
            params.append(id_empresa)
        if id_sucursal:
            where.append("i.id_sucursal = %s")
            params.append(id_sucursal)
            
        where_sql = " AND ".join(where)
        
        q = f"""
            SELECT 
                p.id_producto,
                p.nombre AS producto_nombre,
                ptc.sku,
                COALESCE(t.nombre, '') AS talla,
                COALESCE(col.nombre, '') AS color,
                s.nombre AS sucursal_nombre,
                i.stock_actual,
                i.stock_disponible,
                i.stock_minimo,
                CASE 
                    WHEN i.stock_disponible = 0 THEN 'AGOTADO'
                    WHEN i.stock_disponible <= i.stock_minimo THEN 'BAJO_STOCK'
                    ELSE 'OPTIMO'
                END AS estado_alerta
            FROM {schema}.t_inventario i
            JOIN {schema}.t_producto_talla_color ptc ON ptc.id_variante = i.id_variante
            JOIN {schema}.t_producto p ON p.id_producto = ptc.id_producto
            JOIN {schema}.t_sucursal s ON s.id_sucursal = i.id_sucursal
            LEFT JOIN {schema}.t_talla t ON t.id_talla = ptc.id_talla
            LEFT JOIN {schema}.t_color col ON col.id_color = ptc.id_color
            WHERE {where_sql}
            ORDER BY i.stock_disponible ASC, p.nombre ASC;
        """
        rows = db.execute_query(q, tuple(params) if params else None, fetchall=True) or []
        
        return [{
            "id_producto": r[0],
            "producto_nombre": r[1],
            "sku": r[2],
            "talla": r[3],
            "color": r[4],
            "sucursal_nombre": r[5],
            "stock_actual": int(r[6]),
            "stock_disponible": int(r[7]),
            "stock_minimo": int(r[8]),
            "estado_alerta": r[9]
        } for r in rows]
    finally:
        db.close_connection()


def obtener_ventas_por_sucursal_db(id_empresa: int = None, fecha_inicio: str = None, fecha_fin: str = None):
    """
    Retorna métricas comparativas entre sucursales: ventas, ingresos y unidades vendidas.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        
        # Condiciones para ventas
        v_where = ["1=1"]
        params = []
        if id_empresa:
            v_where.append("v.id_empresa = %s")
            params.append(id_empresa)
        if fecha_inicio:
            v_where.append("DATE(v.fecha_venta) >= %s")
            params.append(fecha_inicio)
        if fecha_fin:
            v_where.append("DATE(v.fecha_venta) <= %s")
            params.append(fecha_fin)
            
        v_where_sql = " AND ".join(v_where)
        
        s_where = ["s.activo = TRUE"]
        s_params = []
        if id_empresa:
            s_where.append("s.id_empresa = %s")
            s_params.append(id_empresa)
        s_where_sql = " AND ".join(s_where)
        
        q = f"""
            SELECT 
                s.id_sucursal,
                s.nombre AS sucursal_nombre,
                COALESCE(c.nombre, 'No asignada') AS ciudad,
                COUNT(v.id_venta) AS cantidad_ventas,
                COALESCE(SUM(v.total), 0) AS total_ingresos,
                COALESCE(SUM(dv_agg.total_items), 0) AS total_unidades,
                COALESCE(AVG(v.total), 0) AS ticket_promedio
            FROM {schema}.t_sucursal s
            LEFT JOIN {schema}.t_ciudad c ON c.id_ciudad = s.id_ciudad
            LEFT JOIN {schema}.t_venta v ON v.id_sucursal = s.id_sucursal AND {v_where_sql}
            LEFT JOIN (
                SELECT id_venta, SUM(cantidad) AS total_items
                FROM {schema}.t_detalle_venta
                GROUP BY id_venta
            ) dv_agg ON dv_agg.id_venta = v.id_venta
            WHERE {s_where_sql}
            GROUP BY s.id_sucursal, s.nombre, c.nombre
            ORDER BY total_ingresos DESC;
        """
        # params order: v_where params then s_where params
        all_params = params + s_params
        rows = db.execute_query(q, tuple(all_params) if all_params else None, fetchall=True) or []
        
        return [{
            "id_sucursal": r[0],
            "nombre_sucursal": r[1],
            "ciudad": r[2],
            "cantidad_ventas": int(r[3]),
            "total_ingresos": float(r[4]),
            "total_unidades": int(r[5]),
            "ticket_promedio": float(r[6])
        } for r in rows]
    finally:
        db.close_connection()


def obtener_tenants_dashboard_db():
    """
    Retorna todas las empresas / tiendas activas con su resumen de sucursales,
    productos, inventario total disponible y ventas acumuladas para el panel administrativo.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            SELECT 
                e.id_empresa,
                e.nombre_empresa,
                COALESCE(e.razon_social, e.nombre_empresa) as razon_social,
                COALESCE(e.nit, '') as nit,
                COALESCE(e.ciudad, 'Santa Cruz') as ciudad,
                COALESCE(e.direccion_fiscal, '') as direccion,
                COALESCE(e.telefono, '') as telefono,
                COALESCE(e.correo, '') as correo,
                COALESCE(e.logo, '') as logo,
                COALESCE(e.estado, 'ACTIVO') as estado,
                (SELECT COUNT(*) FROM {schema}.t_sucursal s WHERE s.id_empresa = e.id_empresa AND (s.activo = TRUE OR s.estado = TRUE)) as total_sucursales,
                (SELECT COUNT(*) FROM {schema}.t_producto p WHERE p.id_empresa = e.id_empresa) as total_productos,
                (SELECT COALESCE(SUM(i.stock_disponible), 0) FROM {schema}.t_inventario i JOIN {schema}.t_sucursal s ON i.id_sucursal = s.id_sucursal WHERE s.id_empresa = e.id_empresa) as total_stock_disponible,
                (SELECT COUNT(*) FROM {schema}.t_venta v WHERE v.id_empresa = e.id_empresa) as total_ventas_cantidad,
                (SELECT COALESCE(SUM(v.total), 0) FROM {schema}.t_venta v WHERE v.id_empresa = e.id_empresa) as total_ingresos_historico
            FROM {schema}.empresa e
            WHERE UPPER(e.estado) = 'ACTIVO'
            ORDER BY e.id_empresa ASC;
        """
        rows = db.execute_query(query, fetchall=True) or []
        tenants = []
        for r in rows:
            id_emp = r[0]
            sucs_raw = db.execute_query(f"""
                SELECT s.id_sucursal, s.nombre, COALESCE(c.nombre, '') as ciudad, COALESCE(s.direccion, '') as direccion
                FROM {schema}.t_sucursal s
                LEFT JOIN {schema}.t_ciudad c ON s.id_ciudad = c.id_ciudad
                WHERE s.id_empresa = %s AND (s.activo = TRUE OR s.estado = TRUE)
                ORDER BY s.id_sucursal ASC;
            """, (id_emp,), fetchall=True) or []
            
            sucursales = [{
                "id": s[0],
                "nombre": s[1],
                "ciudad": s[2],
                "direccion": s[3]
            } for s in sucs_raw]

            tenants.append({
                "id_empresa": id_emp,
                "nombre_empresa": r[1],
                "razon_social": r[2],
                "nit": r[3],
                "ciudad": r[4],
                "direccion": r[5],
                "telefono": r[6],
                "correo": r[7],
                "logo": r[8],
                "estado": r[9],
                "total_sucursales": int(r[10]),
                "total_productos": int(r[11]),
                "total_stock_disponible": int(r[12]),
                "total_ventas_cantidad": int(r[13]),
                "total_ingresos_historico": float(r[14]),
                "sucursales": sucursales
            })
        return tenants
    finally:
        db.close_connection()