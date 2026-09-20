from typing import Optional, List, Dict, Any
from app.classes.postgres import PostgreSQL
from app.config import Config

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

# ==============================================================================
# TENANTS PÚBLICOS
# ==============================================================================

def obtener_tenants_publicos() -> List[Dict[str, Any]]:
    """
    Retorna la lista de tiendas / empresas activas disponibles para consulta pública.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        query = f"""
            SELECT 
                id_empresa, 
                nombre_empresa, 
                razon_social, 
                logo, 
                ciudad, 
                correo, 
                telefono, 
                direccion_fiscal
            FROM {schema}.empresa
            WHERE estado = 'ACTIVO'
            ORDER BY id_empresa ASC;
        """
        filas = db.execute_query(query, fetchall=True) or []
        resultado = []
        for r in filas:
            resultado.append({
                "id_empresa": r[0],
                "nombre_empresa": r[1],
                "razon_social": r[2],
                "logo": r[3],
                "ciudad": r[4],
                "correo": r[5],
                "telefono": r[6],
                "direccion_fiscal": r[7]
            })
        return resultado
    finally:
        db.close_connection()

def obtener_info_tenant(id_empresa: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos públicos de un Tenant específico.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        query = f"""
            SELECT 
                id_empresa, 
                nombre_empresa, 
                razon_social, 
                logo, 
                ciudad, 
                correo, 
                telefono, 
                direccion_fiscal
            FROM {schema}.empresa
            WHERE id_empresa = %s AND estado = 'ACTIVO'
            LIMIT 1;
        """
        r = db.execute_query(query, (id_empresa,), fetchone=True)
        if not r:
            return None
        return {
            "id_empresa": r[0],
            "nombre_empresa": r[1],
            "razon_social": r[2],
            "logo": r[3],
            "ciudad": r[4],
            "correo": r[5],
            "telefono": r[6],
            "direccion_fiscal": r[7]
        }
    finally:
        db.close_connection()

# ==============================================================================
# FILTROS DINÁMICOS DISPONIBLES
# ==============================================================================

def obtener_filtros_disponibles(id_empresa: int) -> Dict[str, Any]:
    """
    Retorna dinámicamente las categorías, tallas, colores, temporadas y colecciones
    activas asociadas a productos activos del Tenant actual.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        # 1. Categorías con productos activos
        q_cats = f"""
            SELECT DISTINCT 
                c.id_categoria, 
                c.nombre, 
                c.imagen_url,
                COUNT(p.id_producto) AS total_prendas
            FROM {schema}.t_categoria c
            JOIN {schema}.t_producto p ON p.id_categoria = c.id_categoria
            WHERE p.id_empresa = %s AND p.activo = TRUE AND c.activo = TRUE
            GROUP BY c.id_categoria, c.nombre, c.imagen_url
            ORDER BY c.nombre ASC;
        """
        cats_res = db.execute_query(q_cats, (id_empresa,), fetchall=True) or []
        categorias = [
            {
                "id_categoria": r[0],
                "nombre": r[1],
                "imagen_url": r[2],
                "total_prendas": r[3]
            }
            for r in cats_res
        ]

        # 2. Tallas activas con variantes disponibles
        q_tallas = f"""
            SELECT DISTINCT 
                t.id_talla, 
                t.nombre
            FROM {schema}.t_talla t
            JOIN {schema}.t_producto_talla_color v ON v.id_talla = t.id_talla
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            WHERE p.id_empresa = %s AND p.activo = TRUE AND v.activo = TRUE AND t.activo = TRUE
            ORDER BY t.id_talla ASC;
        """
        tallas_res = db.execute_query(q_tallas, (id_empresa,), fetchall=True) or []
        tallas = [{"id_talla": r[0], "nombre": r[1]} for r in tallas_res]

        # 3. Colores activos con variantes disponibles
        q_colores = f"""
            SELECT DISTINCT 
                col.id_color, 
                col.nombre, 
                col.codigo_hex
            FROM {schema}.t_color col
            JOIN {schema}.t_producto_talla_color v ON v.id_color = col.id_color
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            WHERE p.id_empresa = %s AND p.activo = TRUE AND v.activo = TRUE AND col.activo = TRUE
            ORDER BY col.nombre ASC;
        """
        colores_res = db.execute_query(q_colores, (id_empresa,), fetchall=True) or []
        colores = [{"id_color": r[0], "nombre": r[1], "codigo_hex": r[2]} for r in colores_res]

        # 4. Temporadas activas
        q_temps = f"""
            SELECT DISTINCT TRIM(p.temporada)
            FROM {schema}.t_producto p
            WHERE p.id_empresa = %s AND p.activo = TRUE AND p.temporada IS NOT NULL AND TRIM(p.temporada) <> ''
            ORDER BY 1 ASC;
        """
        temps_res = db.execute_query(q_temps, (id_empresa,), fetchall=True) or []
        temporadas = [r[0] for r in temps_res if r[0]]

        # 5. Colecciones activas
        q_cols = f"""
            SELECT DISTINCT TRIM(p.coleccion)
            FROM {schema}.t_producto p
            WHERE p.id_empresa = %s AND p.activo = TRUE AND p.coleccion IS NOT NULL AND TRIM(p.coleccion) <> ''
            ORDER BY 1 ASC;
        """
        cols_res = db.execute_query(q_cols, (id_empresa,), fetchall=True) or []
        colecciones = [r[0] for r in cols_res if r[0]]

        # 6. Rango de precios activos del Tenant
        q_prices = f"""
            SELECT 
                COALESCE(MIN(p.precio), 0) AS min_precio,
                COALESCE(MAX(p.precio), 0) AS max_precio
            FROM {schema}.t_producto p
            WHERE p.id_empresa = %s AND p.activo = TRUE;
        """
        p_res = db.execute_query(q_prices, (id_empresa,), fetchone=True)
        precio_min_posible = float(p_res[0]) if p_res and p_res[0] is not None else 0.0
        precio_max_posible = float(p_res[1]) if p_res and p_res[1] is not None else 0.0

        return {
            "categorias": categorias,
            "tallas": tallas,
            "colores": colores,
            "temporadas": temporadas,
            "colecciones": colecciones,
            "precio_min": precio_min_posible,
            "precio_max": precio_max_posible
        }
    finally:
        db.close_connection()

# ==============================================================================
# CONSULTA PÚBLICA DE PRODUCTOS (CATÁLOGO)
# ==============================================================================

def listar_catalogo_publico(
    id_empresa: int,
    busqueda: Optional[str] = None,
    id_categoria: Optional[int] = None,
    id_talla: Optional[int] = None,
    id_color: Optional[int] = None,
    temporada: Optional[str] = None,
    coleccion: Optional[str] = None,
    precio_min: Optional[float] = None,
    precio_max: Optional[float] = None,
    orden: Optional[str] = "destacados",
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Consulta productos activos del Tenant con filtros combinados y ordenamiento.
    Retorna total y lista formateada con variantes resumidas y fotos.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        condiciones = ["p.id_empresa = %s", "p.activo = TRUE"]
        params: List[Any] = [id_empresa]

        # Filtro de categoría activa
        if id_categoria:
            condiciones.append("p.id_categoria = %s")
            condiciones.append("c.activo = TRUE")
            params.append(id_categoria)

        # Filtro de búsqueda textual (nombre, descripción, marca, código)
        if busqueda and busqueda.strip():
            term = f"%{busqueda.strip()}%"
            condiciones.append("(p.nombre ILIKE %s OR p.descripcion ILIKE %s OR p.marca ILIKE %s OR p.codigo_producto ILIKE %s)")
            params.extend([term, term, term, term])

        # Filtro por talla (prenda debe tener variante activa con esta talla)
        if id_talla:
            condiciones.append(f"""
                EXISTS (
                    SELECT 1 FROM {schema}.t_producto_talla_color v
                    JOIN {schema}.t_talla t ON t.id_talla = v.id_talla
                    WHERE v.id_producto = p.id_producto AND v.id_talla = %s AND v.activo = TRUE AND t.activo = TRUE
                )
            """)
            params.append(id_talla)

        # Filtro por color (prenda debe tener variante activa con este color)
        if id_color:
            condiciones.append(f"""
                EXISTS (
                    SELECT 1 FROM {schema}.t_producto_talla_color v
                    JOIN {schema}.t_color col ON col.id_color = v.id_color
                    WHERE v.id_producto = p.id_producto AND v.id_color = %s AND v.activo = TRUE AND col.activo = TRUE
                )
            """)
            params.append(id_color)

        # Filtro por temporada
        if temporada and temporada.strip() and temporada.lower() != 'todas':
            condiciones.append("p.temporada ILIKE %s")
            params.append(f"%{temporada.strip()}%")

        # Filtro por colección
        if coleccion and coleccion.strip() and coleccion.lower() != 'todas':
            condiciones.append("p.coleccion ILIKE %s")
            params.append(f"%{coleccion.strip()}%")

        # Filtro por rango de precio
        if precio_min is not None and precio_min >= 0:
            condiciones.append("p.precio >= %s")
            params.append(precio_min)

        if precio_max is not None and precio_max >= 0:
            condiciones.append("p.precio <= %s")
            params.append(precio_max)

        where_sql = f"WHERE {' AND '.join(condiciones)}"

        # 1. Total de registros para paginación
        count_query = f"""
            SELECT COUNT(p.id_producto)
            FROM {schema}.t_producto p
            LEFT JOIN {schema}.t_categoria c ON c.id_categoria = p.id_categoria
            {where_sql};
        """
        total_res = db.execute_query(count_query, tuple(params), fetchone=True)
        total = total_res[0] if total_res else 0

        # 2. Cláusula de ordenamiento
        order_clause = "p.id_producto DESC"
        if orden == "precio_asc":
            order_clause = "p.precio ASC, p.id_producto DESC"
        elif orden == "precio_desc":
            order_clause = "p.precio DESC, p.id_producto DESC"
        elif orden == "nombre_asc":
            order_clause = "p.nombre ASC, p.id_producto DESC"
        elif orden == "nombre_desc":
            order_clause = "p.nombre DESC, p.id_producto DESC"
        elif orden == "recientes":
            order_clause = "p.fecha_registro DESC NULLS LAST, p.id_producto DESC"
        else: # "destacados"
            order_clause = "p.fecha_registro DESC NULLS LAST, p.id_producto DESC"

        # 3. Consulta principal de productos
        query = f"""
            SELECT 
                p.id_producto,
                p.id_empresa,
                p.id_categoria,
                c.nombre AS categoria_nombre,
                p.codigo_producto,
                p.nombre,
                p.descripcion,
                p.marca,
                p.genero,
                p.precio,
                p.temporada,
                p.coleccion,
                p.fecha_registro,
                (
                    SELECT img.imagen_url
                    FROM {schema}.t_producto_imagen img
                    WHERE img.id_producto = p.id_producto
                    ORDER BY img.es_principal DESC, img.orden ASC, img.id_imagen ASC
                    LIMIT 1
                ) AS imagen_portada,
                (
                    SELECT COUNT(img.id_imagen)
                    FROM {schema}.t_producto_imagen img
                    WHERE img.id_producto = p.id_producto
                ) AS total_imagenes,
                (
                    SELECT COUNT(v.id_variante)
                    FROM {schema}.t_producto_talla_color v
                    WHERE v.id_producto = p.id_producto AND v.activo = TRUE
                ) AS total_variantes
            FROM {schema}.t_producto p
            LEFT JOIN {schema}.t_categoria c ON c.id_categoria = p.id_categoria
            {where_sql}
            ORDER BY {order_clause}
            LIMIT %s OFFSET %s;
        """
        exec_params = params + [limit, offset]
        filas = db.execute_query(query, tuple(exec_params), fetchall=True) or []

        productos = []
        ids_productos = [r[0] for r in filas]

        # 4. Cargar variantes resumidas (tallas y colores disponibles) para las tarjetas
        variantes_por_prod: Dict[int, Dict[str, Any]] = {pid: {"tallas": [], "colores": []} for pid in ids_productos}
        if ids_productos:
            q_var_summary = f"""
                SELECT DISTINCT 
                    v.id_producto,
                    t.id_talla,
                    t.nombre AS talla_nombre,
                    col.id_color,
                    col.nombre AS color_nombre,
                    col.codigo_hex
                FROM {schema}.t_producto_talla_color v
                JOIN {schema}.t_talla t ON t.id_talla = v.id_talla AND t.activo = TRUE
                JOIN {schema}.t_color col ON col.id_color = v.id_color AND col.activo = TRUE
                WHERE v.id_producto = ANY(%s) AND v.activo = TRUE
                ORDER BY t.id_talla ASC, col.nombre ASC;
            """
            v_rows = db.execute_query(q_var_summary, (ids_productos,), fetchall=True) or []
            for vr in v_rows:
                pid, tid, tnom, cid, cnom, chex = vr
                v_dict = variantes_por_prod[pid]
                if not any(t["id_talla"] == tid for t in v_dict["tallas"]):
                    v_dict["tallas"].append({"id_talla": tid, "nombre": tnom})
                if not any(c["id_color"] == cid for c in v_dict["colores"]):
                    v_dict["colores"].append({"id_color": cid, "nombre": cnom, "codigo_hex": chex})

        for r in filas:
            pid = r[0]
            prod_vars = variantes_por_prod.get(pid, {"tallas": [], "colores": []})
            productos.append({
                "id_producto": pid,
                "id_empresa": r[1],
                "id_categoria": r[2],
                "categoria_nombre": r[3] or "Sin Categoría",
                "codigo_producto": r[4],
                "nombre": r[5],
                "descripcion": r[6] or "",
                "marca": r[7] or "Aurora Atelier",
                "genero": r[8] or "Unisex",
                "precio": float(r[9]) if r[9] is not None else 0.0,
                "temporada": r[10] or "Atemporal",
                "coleccion": r[11] or "Esenciales",
                "fecha_registro": r[12].strftime("%Y-%m-%d %H:%M") if r[12] else None,
                "imagen_principal": r[13],
                "total_imagenes": r[14],
                "total_variantes": r[15],
                "tallas_disponibles": prod_vars["tallas"],
                "colores_disponibles": prod_vars["colores"]
            })

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "productos": productos
        }
    finally:
        db.close_connection()

# ==============================================================================
# DETALLE PÚBLICO DE PRODUCTO CON VARIANTES Y STOCK POR SUCURSAL
# ==============================================================================

def obtener_detalle_producto_publico(id_producto: int, id_empresa: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Obtiene el detalle completo de un producto activo, su galería de fotos,
    sus variantes activas de talla/color y la disponibilidad por sucursal vigente.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        # 1. Consulta datos de la prenda
        cond_empresa = "AND p.id_empresa = %s" if id_empresa else ""
        params_base: List[Any] = [id_producto]
        if id_empresa:
            params_base.append(id_empresa)

        q_prod = f"""
            SELECT 
                p.id_producto,
                p.id_empresa,
                e.nombre_empresa,
                p.id_categoria,
                c.nombre AS categoria_nombre,
                p.codigo_producto,
                p.nombre,
                p.descripcion,
                p.marca,
                p.genero,
                p.precio,
                p.temporada,
                p.coleccion,
                p.fecha_registro,
                p.updated_at,
                COALESCE(p.tiene_ra, FALSE) AS tiene_ra,
                p.modelo_2d_url,
                p.tipo_prenda_ra
            FROM {schema}.t_producto p
            LEFT JOIN {schema}.empresa e ON e.id_empresa = p.id_empresa
            LEFT JOIN {schema}.t_categoria c ON c.id_categoria = p.id_categoria
            WHERE p.id_producto = %s AND p.activo = TRUE {cond_empresa}
            LIMIT 1;
        """
        p_row = db.execute_query(q_prod, tuple(params_base), fetchone=True)
        if not p_row:
            return None

        id_empresa_prod = p_row[1]

        # 2. Galería de imágenes completa
        q_imgs = f"""
            SELECT 
                id_imagen, 
                imagen_url, 
                public_id, 
                es_principal, 
                orden
            FROM {schema}.t_producto_imagen
            WHERE id_producto = %s
            ORDER BY es_principal DESC, orden ASC, id_imagen ASC;
        """
        imgs_res = db.execute_query(q_imgs, (id_producto,), fetchall=True) or []
        imagenes = [
            {
                "id_imagen": r[0],
                "imagen_url": r[1],
                "public_id": r[2],
                "es_principal": r[3],
                "orden": r[4]
            }
            for r in imgs_res
        ]

        # 3. Variantes activas de talla y color
        q_vars = f"""
            SELECT 
                v.id_variante,
                v.id_talla,
                t.nombre AS talla_nombre,
                v.id_color,
                col.nombre AS color_nombre,
                col.codigo_hex,
                v.sku,
                v.precio,
                v.modelo_ra_url
            FROM {schema}.t_producto_talla_color v
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla AND t.activo = TRUE
            JOIN {schema}.t_color col ON col.id_color = v.id_color AND col.activo = TRUE
            WHERE v.id_producto = %s AND v.activo = TRUE
            ORDER BY t.id_talla ASC, col.nombre ASC;
        """
        vars_res = db.execute_query(q_vars, (id_producto,), fetchall=True) or []
        variantes = []
        ids_variantes = []
        tiene_modelo_ra = False

        for vr in vars_res:
            ids_variantes.append(vr[0])
            if vr[8]:
                tiene_modelo_ra = True
            variantes.append({
                "id_variante": vr[0],
                "id_talla": vr[1],
                "talla_nombre": vr[2],
                "id_color": vr[3],
                "color_nombre": vr[4],
                "codigo_hex": vr[5],
                "sku": vr[6],
                "precio": float(vr[7]) if vr[7] is not None else float(p_row[10] or 0.0),
                "modelo_ra_url": vr[8]
            })

        # 4. Revisar si tiene modelo 3D en t_prenda_ra
        q_ra = f"""
            SELECT modelo_3d_url, modelo_ar_url 
            FROM {schema}.t_prenda_ra 
            WHERE id_producto = %s AND estado = TRUE 
            LIMIT 1;
        """
        ra_res = db.execute_query(q_ra, (id_producto,), fetchone=True)
        modelo_3d_global = ra_res[0] if ra_res else None
        modelo_ar_global = ra_res[1] if ra_res else None
        if modelo_3d_global or modelo_ar_global:
            tiene_modelo_ra = True

        # 5. Disponibilidad por Sucursal en tiempo real desde t_inventario
        # Consultar todas las sucursales activas del Tenant
        q_sucs = f"""
            SELECT 
                s.id_sucursal,
                s.nombre,
                s.codigo_sucursal,
                s.direccion,
                s.telefono,
                s.correo,
                s.horario_apertura,
                s.horario_cierre,
                ci.nombre AS ciudad_nombre
            FROM {schema}.t_sucursal s
            LEFT JOIN {schema}.t_ciudad ci ON ci.id_ciudad = s.id_ciudad
            WHERE s.id_empresa = %s AND s.activo = TRUE
            ORDER BY s.nombre ASC;
        """
        sucs_res = db.execute_query(q_sucs, (id_empresa_prod,), fetchall=True) or []

        # Consultar stock por sucursal y variante
        stock_map: Dict[int, Dict[int, int]] = {} # id_sucursal -> { id_variante: stock_disponible }
        if ids_variantes and sucs_res:
            q_inv = f"""
                SELECT 
                    inv.id_sucursal,
                    inv.id_variante,
                    GREATEST(0, COALESCE(inv.stock_disponible, 0)) AS stock_disponible
                FROM {schema}.t_inventario inv
                WHERE inv.id_variante = ANY(%s) AND inv.estado = TRUE;
            """
            inv_res = db.execute_query(q_inv, (ids_variantes,), fetchall=True) or []
            for ir in inv_res:
                suc_id, var_id, stk = ir
                if suc_id not in stock_map:
                    stock_map[suc_id] = {}
                stock_map[suc_id][var_id] = int(stk)

        sucursales_stock = []
        stock_total_general = 0

        for s in sucs_res:
            suc_id = s[0]
            var_stock_dict = stock_map.get(suc_id, {})
            # Total de unidades de esta prenda en la sucursal sumando todas sus variantes
            total_suc = sum(var_stock_dict.get(vid, 0) for vid in ids_variantes)
            stock_total_general += total_suc

            sucursales_stock.append({
                "id_sucursal": suc_id,
                "nombre": s[1],
                "codigo_sucursal": s[2],
                "direccion": s[3] or "Dirección no especificada",
                "telefono": s[4] or "",
                "horario": f"{s[6] or '09:00'} - {s[7] or '20:00'}",
                "ciudad": s[8] or "",
                "stock_total_sucursal": total_suc,
                "disponible": total_suc > 0,
                "stock_por_variante": var_stock_dict
            })

        # Listas agrupadas de tallas y colores para navegación ágil
        tallas_unicas = []
        colores_unicos = []
        for v in variantes:
            if not any(t["id_talla"] == v["id_talla"] for t in tallas_unicas):
                tallas_unicas.append({"id_talla": v["id_talla"], "nombre": v["talla_nombre"]})
            if not any(c["id_color"] == v["id_color"] for c in colores_unicos):
                colores_unicos.append({
                    "id_color": v["id_color"], 
                    "nombre": v["color_nombre"], 
                    "codigo_hex": v["codigo_hex"]
                })

        return {
            "id_producto": p_row[0],
            "id_empresa": id_empresa_prod,
            "empresa_nombre": p_row[2],
            "id_categoria": p_row[3],
            "categoria_nombre": p_row[4] or "Colección General",
            "codigo_producto": p_row[5],
            "nombre": p_row[6],
            "descripcion": p_row[7] or "",
            "marca": p_row[8] or "Aurora Atelier",
            "genero": p_row[9] or "Unisex",
            "precio": float(p_row[10]) if p_row[10] is not None else 0.0,
            "temporada": p_row[11] or "Atemporal",
            "coleccion": p_row[12] or "Esenciales",
            "fecha_registro": p_row[13].strftime("%Y-%m-%d %H:%M") if p_row[13] else None,
            "imagenes": imagenes,
            "imagen_principal": imagenes[0]["imagen_url"] if imagenes else None,
            "variantes": variantes,
            "tallas": tallas_unicas,
            "colores": colores_unicos,
            "sucursales_stock": sucursales_stock,
            "stock_total_general": stock_total_general,
            "hay_stock_disponible": stock_total_general > 0,
            # M14: Vestidor Virtual en Realidad Aumentada
            "tiene_ra": bool(p_row[15]),
            "modelo_2d_url": p_row[16],
            "tipo_prenda_ra": p_row[17] or "TOP",
            "permite_reserva": True,
            "permite_compra": True,
            "permite_vestidor_ra": bool(p_row[15]) or tiene_modelo_ra,
            "recursos_ra": {
                "modelo_2d_url": p_row[16],
                "tipo_prenda_ra": p_row[17] or "TOP",
                "modelo_3d_url": modelo_3d_global,
                "modelo_ar_url": modelo_ar_global
            }
        }
    finally:
        db.close_connection()

# ==============================================================================
# M14 - VESTIDOR VIRTUAL REALIDAD AUMENTADA
# ==============================================================================

ORDEN_TALLAS = {'XXS': 0, 'XS': 1, 'S': 2, 'M': 3, 'L': 4, 'XL': 5, 'XXL': 6, '2XL': 6, '3XL': 7}

def _ordenar_tallas(tallas: Optional[List[str]]) -> List[str]:
    if not tallas:
        return ['S', 'M', 'L']
    def key_fn(t):
        t_str = str(t).strip().upper()
        if t_str in ORDEN_TALLAS:
            return (0, ORDEN_TALLAS[t_str], t_str)
        if t_str.isdigit():
            return (1, int(t_str), t_str)
        return (2, 0, t_str)
    return sorted(list(set(str(t).strip() for t in tallas if t)), key=key_fn)

def obtener_prendas_vestidor_ra(id_empresa: Optional[int] = None, tipo_prenda: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retorna la lista de prendas activas compatibles con el Vestidor Virtual (M14),
    incluyendo las tallas disponibles según inventario / variantes activas.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        conds = ["p.activo = TRUE", "p.tiene_ra = TRUE"]
        params: List[Any] = []

        if id_empresa:
            conds.append("p.id_empresa = %s")
            params.append(id_empresa)

        if tipo_prenda and tipo_prenda.upper() != 'TODAS':
            conds.append("UPPER(p.tipo_prenda_ra) = %s")
            params.append(tipo_prenda.upper())

        where_clause = " AND ".join(conds)
        q = f"""
            SELECT 
                p.id_producto,
                p.nombre,
                p.precio,
                p.modelo_2d_url,
                p.tipo_prenda_ra,
                img.imagen_url AS imagen_preview,
                COALESCE(
                    (
                        SELECT array_agg(DISTINCT t.nombre)
                        FROM {schema}.t_producto_talla_color ptc
                        JOIN {schema}.t_talla t ON ptc.id_talla = t.id_talla
                        WHERE ptc.id_producto = p.id_producto AND ptc.activo = TRUE
                    ),
                    ARRAY['S', 'M', 'L']::varchar[]
                ) AS tallas_disponibles
            FROM {schema}.t_producto p
            LEFT JOIN LATERAL (
                SELECT imagen_url 
                FROM {schema}.t_producto_imagen 
                WHERE id_producto = p.id_producto 
                ORDER BY es_principal DESC, orden ASC, id_imagen ASC 
                LIMIT 1
            ) img ON TRUE
            WHERE {where_clause}
            ORDER BY p.id_producto ASC;
        """
        rows = db.execute_query(q, tuple(params) if params else None, fetchall=True) or []
        resultado = []
        for r in rows:
            resultado.append({
                "id_producto": r[0],
                "nombre": r[1],
                "precio": float(r[2]) if r[2] is not None else 0.0,
                "modelo_2d_url": r[3] or r[5],
                "tipo_prenda_ra": r[4] or "TOP",
                "imagen_preview": r[5] or r[3],
                "tallas_disponibles": _ordenar_tallas(r[6])
            })
        return resultado
    finally:
        db.close_connection()

def obtener_config_vestidor_producto(id_producto: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene la configuración de vestidor virtual para una prenda específica,
    incluyendo sus tallas disponibles.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        q = f"""
            SELECT 
                p.id_producto,
                p.nombre,
                p.precio,
                COALESCE(p.tiene_ra, FALSE) AS tiene_ra,
                p.modelo_2d_url,
                p.tipo_prenda_ra,
                COALESCE(
                    (
                        SELECT array_agg(DISTINCT t.nombre)
                        FROM {schema}.t_producto_talla_color ptc
                        JOIN {schema}.t_talla t ON ptc.id_talla = t.id_talla
                        WHERE ptc.id_producto = p.id_producto AND ptc.activo = TRUE
                    ),
                    ARRAY['S', 'M', 'L']::varchar[]
                ) AS tallas_disponibles
            FROM {schema}.t_producto p
            WHERE p.id_producto = %s AND p.activo = TRUE
            LIMIT 1;
        """
        r = db.execute_query(q, (id_producto,), fetchone=True)
        if not r:
            return None
        return {
            "id_producto": r[0],
            "nombre": r[1],
            "precio": float(r[2]) if r[2] is not None else 0.0,
            "tiene_ra": bool(r[3]),
            "modelo_2d_url": r[4],
            "tipo_prenda_ra": r[5] or "TOP",
            "tallas_disponibles": _ordenar_tallas(r[6])
        }
    finally:
        db.close_connection()

# ==============================================================================
# DISPONIBILIDAD DE VARIANTE POR SUCURSAL EN TIEMPO REAL
# ==============================================================================

def obtener_disponibilidad_variante_sucursales(id_variante: int, id_empresa: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Consulta en tiempo real la disponibilidad y existencias de una variante específica
    en todas las sucursales activas del Tenant al que pertenece.
    Garantiza aislamiento estricto por empresa y evita cantidades negativas.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        # 1. Obtener datos de la variante y su producto/empresa
        q_var = f"""
            SELECT 
                v.id_variante,
                v.id_producto,
                p.nombre AS producto_nombre,
                p.id_empresa,
                e.nombre_empresa,
                t.id_talla,
                t.nombre AS talla_nombre,
                col.id_color,
                col.nombre AS color_nombre,
                col.codigo_hex,
                v.sku,
                COALESCE(v.precio, p.precio) AS precio,
                p.activo AS producto_activo,
                v.activo AS variante_activa
            FROM {schema}.t_producto_talla_color v
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            JOIN {schema}.empresa e ON e.id_empresa = p.id_empresa
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla AND t.activo = TRUE
            JOIN {schema}.t_color col ON col.id_color = v.id_color AND col.activo = TRUE
            WHERE v.id_variante = %s
            LIMIT 1;
        """
        var_row = db.execute_query(q_var, (id_variante,), fetchone=True)
        if not var_row:
            return None

        tenant_id = var_row[3]
        if id_empresa and tenant_id != id_empresa:
            return None  # Aislamiento multi-tenant

        if not var_row[12] or not var_row[13]:
            return None

        # 2. Consultar sucursales activas del Tenant con inventario vigente
        q_sucs = f"""
            SELECT 
                s.id_sucursal,
                s.nombre,
                s.codigo_sucursal,
                s.direccion,
                s.telefono,
                s.correo,
                s.horario_apertura,
                s.horario_cierre,
                ci.nombre AS ciudad_nombre,
                GREATEST(0, COALESCE(inv.stock_disponible, 0)) AS stock_disponible
            FROM {schema}.t_sucursal s
            LEFT JOIN {schema}.t_ciudad ci ON ci.id_ciudad = s.id_ciudad
            LEFT JOIN {schema}.t_inventario inv ON inv.id_sucursal = s.id_sucursal 
                 AND inv.id_variante = %s 
                 AND inv.estado = TRUE
            WHERE s.id_empresa = %s AND s.activo = TRUE
            ORDER BY s.nombre ASC;
        """
        filas_sucs = db.execute_query(q_sucs, (id_variante, tenant_id), fetchall=True) or []

        sucursales = []
        stock_total = 0
        for s in filas_sucs:
            stock = int(s[9])
            stock_total += stock
            sucursales.append({
                "id_sucursal": s[0],
                "nombre": s[1],
                "codigo_sucursal": s[2],
                "direccion": s[3] or "Dirección no especificada",
                "telefono": s[4] or "",
                "correo": s[5] or "",
                "horario": f"{s[6] or '09:00'} - {s[7] or '20:00'}",
                "ciudad": s[8] or "",
                "stock_disponible": stock,
                "disponible": stock > 0,
                "permite_reserva": True,
                "permite_compra": stock > 0
            })

        return {
            "variante": {
                "id_variante": var_row[0],
                "id_producto": var_row[1],
                "producto_nombre": var_row[2],
                "id_empresa": tenant_id,
                "empresa_nombre": var_row[4],
                "id_talla": var_row[5],
                "talla_nombre": var_row[6],
                "id_color": var_row[7],
                "color_nombre": var_row[8],
                "codigo_hex": var_row[9],
                "sku": var_row[10],
                "precio": float(var_row[11]) if var_row[11] is not None else 0.0
            },
            "stock_total": stock_total,
            "hay_disponibilidad": stock_total > 0,
            "sucursales": sucursales
        }
    finally:
        db.close_connection()
