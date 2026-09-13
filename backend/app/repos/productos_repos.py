from typing import Optional, List, Dict, Any, Tuple
from app.classes.postgres import PostgreSQL
from app.config import Config

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

# ==============================================================================
# LECTURA DE PRODUCTOS
# ==============================================================================

def listar_productos(
    id_empresa: Optional[int] = None,
    solo_activos: bool = False,
    id_categoria: Optional[int] = None,
    busqueda: Optional[str] = None,
    limit: int = 200,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Lista productos con categoría, Tenant, portada principal y conteos de variantes/fotos.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        condiciones = []
        params: List[Any] = []

        if id_empresa:
            condiciones.append("p.id_empresa = %s")
            params.append(id_empresa)

        if solo_activos:
            condiciones.append("p.activo = TRUE")

        if id_categoria:
            condiciones.append("p.id_categoria = %s")
            params.append(id_categoria)

        if busqueda:
            term = f"%{busqueda.strip()}%"
            condiciones.append("(p.nombre ILIKE %s OR p.descripcion ILIKE %s OR p.codigo_producto ILIKE %s OR c.nombre ILIKE %s)")
            params.extend([term, term, term, term])

        where_clause = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

        query = f"""
            SELECT 
                p.id_producto,
                p.id_empresa,
                e.nombre_empresa AS empresa_nombre,
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
                p.activo,
                p.estado,
                p.fecha_registro,
                p.updated_at,
                COALESCE(
                    (SELECT img.imagen_url FROM {schema}.t_producto_imagen img 
                     WHERE img.id_producto = p.id_producto AND img.es_principal = TRUE 
                     ORDER BY img.id_imagen ASC LIMIT 1),
                    (SELECT img.imagen_url FROM {schema}.t_producto_imagen img 
                     WHERE img.id_producto = p.id_producto 
                     ORDER BY img.id_imagen ASC LIMIT 1),
                    p.imagen_url
                ) AS imagen_principal,
                (SELECT COUNT(*) FROM {schema}.t_producto_imagen img WHERE img.id_producto = p.id_producto) AS total_imagenes,
                (SELECT COUNT(*) FROM {schema}.t_producto_talla_color ptc WHERE ptc.id_producto = p.id_producto AND ptc.activo = TRUE) AS total_variantes
            FROM {schema}.t_producto p
            LEFT JOIN {schema}.t_categoria c ON p.id_categoria = c.id_categoria
            LEFT JOIN {schema}.empresa e ON p.id_empresa = e.id_empresa
            {where_clause}
            ORDER BY p.id_producto DESC
            LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])
        filas = db.execute_query(query, tuple(params), fetchall=True) or []

        resultado = []
        for r in filas:
            resultado.append({
                "id_producto": r[0],
                "id_empresa": r[1],
                "empresa_nombre": r[2] or "Sin Tenant",
                "id_categoria": r[3],
                "categoria_nombre": r[4] or "Sin Categoría",
                "codigo_producto": r[5] or f"PRD-{r[0]}",
                "nombre": r[6],
                "descripcion": r[7] or "",
                "marca": r[8] or "Aurora Atelier",
                "genero": r[9] or "Femenino",
                "precio": float(r[10]) if r[10] is not None else 0.0,
                "temporada": r[11] or "",
                "coleccion": r[12] or "",
                "activo": bool(r[13]),
                "estado": bool(r[14]),
                "fecha_registro": r[15].isoformat() if r[15] else None,
                "updated_at": r[16].isoformat() if r[16] else None,
                "imagen_principal": r[17] or "",
                "total_imagenes": int(r[18]),
                "total_variantes": int(r[19])
            })
        return resultado
    finally:
        db.close_connection()

def obtener_producto_por_id(id_producto: int, id_empresa: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Obtiene el detalle completo de un producto con su galería de imágenes y variantes (talla x color).
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        condiciones = ["p.id_producto = %s"]
        params: List[Any] = [id_producto]

        if id_empresa:
            condiciones.append("p.id_empresa = %s")
            params.append(id_empresa)

        query = f"""
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
                p.activo,
                p.estado,
                p.fecha_registro,
                p.updated_at,
                p.imagen_url
            FROM {schema}.t_producto p
            LEFT JOIN {schema}.t_categoria c ON p.id_categoria = c.id_categoria
            LEFT JOIN {schema}.empresa e ON p.id_empresa = e.id_empresa
            WHERE {' AND '.join(condiciones)};
        """
        r = db.execute_query(query, tuple(params), fetchone=True)
        if not r:
            return None

        # 1. Obtener galería de fotos
        query_imgs = f"""
            SELECT id_imagen, imagen_url, public_id, es_principal, orden, created_at
            FROM {schema}.t_producto_imagen
            WHERE id_producto = %s
            ORDER BY es_principal DESC, orden ASC, id_imagen ASC;
        """
        filas_imgs = db.execute_query(query_imgs, (id_producto,), fetchall=True) or []
        imagenes = []
        for img in filas_imgs:
            imagenes.append({
                "id_imagen": img[0],
                "imagen_url": img[1],
                "public_id": img[2],
                "es_principal": bool(img[3]),
                "orden": img[4],
                "created_at": img[5].isoformat() if img[5] else None
            })

        # 2. Obtener variantes (Tallas x Colores)
        query_vars = f"""
            SELECT 
                ptc.id_variante,
                ptc.id_talla,
                t.nombre AS talla_nombre,
                ptc.id_color,
                col.nombre AS color_nombre,
                col.codigo_hex,
                ptc.sku,
                ptc.precio,
                ptc.activo,
                ptc.estado,
                (SELECT COUNT(*) FROM {schema}.t_inventario inv 
                 WHERE inv.id_variante = ptc.id_variante AND (inv.stock_actual > 0 OR inv.stock_reservado > 0)) AS tiene_stock,
                (SELECT COUNT(*) FROM {schema}.t_movimiento_inventario mov 
                 JOIN {schema}.t_inventario inv2 ON mov.id_inventario = inv2.id_inventario 
                 WHERE inv2.id_variante = ptc.id_variante) AS total_movimientos
            FROM {schema}.t_producto_talla_color ptc
            JOIN {schema}.t_talla t ON ptc.id_talla = t.id_talla
            JOIN {schema}.t_color col ON ptc.id_color = col.id_color
            WHERE ptc.id_producto = %s
            ORDER BY t.id_talla ASC, col.nombre ASC;
        """
        filas_vars = db.execute_query(query_vars, (id_producto,), fetchall=True) or []
        variantes = []
        for v in filas_vars:
            variantes.append({
                "id_variante": v[0],
                "id_talla": v[1],
                "talla_nombre": v[2],
                "id_color": v[3],
                "color_nombre": v[4],
                "codigo_hex": v[5],
                "sku": v[6] or "",
                "precio": float(v[7]) if v[7] is not None else float(r[10] or 0.0),
                "activo": bool(v[8]),
                "estado": bool(v[9]),
                "tiene_stock": int(v[10]) > 0,
                "total_movimientos": int(v[11])
            })

        # Imagen de portada resuelta
        portada = next((img["imagen_url"] for img in imagenes if img["es_principal"]), None)
        if not portada and imagenes:
            portada = imagenes[0]["imagen_url"]
        if not portada:
            portada = r[17] or ""

        return {
            "id_producto": r[0],
            "id_empresa": r[1],
            "empresa_nombre": r[2] or "Sin Tenant",
            "id_categoria": r[3],
            "categoria_nombre": r[4] or "Sin Categoría",
            "codigo_producto": r[5] or f"PRD-{r[0]}",
            "nombre": r[6],
            "descripcion": r[7] or "",
            "marca": r[8] or "Aurora Atelier",
            "genero": r[9] or "Femenino",
            "precio": float(r[10]) if r[10] is not None else 0.0,
            "temporada": r[11] or "",
            "coleccion": r[12] or "",
            "activo": bool(r[13]),
            "estado": bool(r[14]),
            "fecha_registro": r[15].isoformat() if r[15] else None,
            "updated_at": r[16].isoformat() if r[16] else None,
            "imagen_principal": portada,
            "imagenes": imagenes,
            "variantes": variantes
        }
    finally:
        db.close_connection()

def verificar_nombre_duplicado(nombre: str, id_empresa: Optional[int], id_producto_actual: Optional[int] = None) -> bool:
    """
    Verifica si ya existe un producto con el mismo nombre dentro del Tenant.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        query = f"""
            SELECT COUNT(*) 
            FROM {schema}.t_producto 
            WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(%s)) 
              AND COALESCE(id_empresa, 0) = COALESCE(%s, 0)
        """
        params = [nombre, id_empresa]
        if id_producto_actual:
            query += " AND id_producto != %s"
            params.append(id_producto_actual)

        res = db.execute_query(query, tuple(params), fetchone=True)
        return (res[0] > 0) if res else False
    finally:
        db.close_connection()

# ==============================================================================
# ESCRITURA Y MUTACIONES
# ==============================================================================

def crear_producto(
    id_empresa: int,
    id_categoria: int,
    nombre: str,
    precio: float,
    descripcion: str = "",
    codigo_producto: Optional[str] = None,
    temporada: Optional[str] = None,
    coleccion: Optional[str] = None,
    marca: str = "Aurora Atelier",
    genero: str = "Femenino",
    activo: bool = True
) -> int:
    """
    Crea el producto base en t_producto y retorna su id_producto.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        query = f"""
            INSERT INTO {schema}.t_producto (
                id_empresa, id_categoria, nombre, descripcion, precio,
                codigo_producto, temporada, coleccion, marca, genero,
                activo, estado, fecha_registro, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id_producto;
        """
        params = (
            id_empresa, id_categoria, nombre.strip(), descripcion.strip(), precio,
            codigo_producto, temporada.strip() if temporada else None,
            coleccion.strip() if coleccion else None, marca, genero,
            activo, activo
        )
        res = db.execute_query(query, params, fetchone=True, commit=True)
        id_prod = res[0]

        # Si no se pasó código_producto, generamos uno limpio con el ID
        if not codigo_producto:
            codigo_gen = f"AUR-{id_empresa:02d}-{id_prod:04d}"
            db.execute_query(
                f"UPDATE {schema}.t_producto SET codigo_producto = %s WHERE id_producto = %s;",
                (codigo_gen, id_prod),
                commit=True
            )

        return id_prod
    finally:
        db.close_connection()

def actualizar_producto(
    id_producto: int,
    id_categoria: int,
    nombre: str,
    precio: float,
    descripcion: str = "",
    codigo_producto: Optional[str] = None,
    temporada: Optional[str] = None,
    coleccion: Optional[str] = None,
    marca: str = "Aurora Atelier",
    genero: str = "Femenino",
    activo: bool = True
) -> bool:
    """
    Actualiza la información general del producto.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        query = f"""
            UPDATE {schema}.t_producto 
            SET 
                id_categoria = %s,
                nombre = %s,
                descripcion = %s,
                precio = %s,
                codigo_producto = COALESCE(%s, codigo_producto),
                temporada = %s,
                coleccion = %s,
                marca = %s,
                genero = %s,
                activo = %s,
                estado = %s,
                updated_at = NOW()
            WHERE id_producto = %s;
        """
        params = (
            id_categoria, nombre.strip(), descripcion.strip(), precio,
            codigo_producto, temporada.strip() if temporada else None,
            coleccion.strip() if coleccion else None, marca, genero,
            activo, activo, id_producto
        )
        filas = db.execute_query(query, params, commit=True)
        return filas > 0
    finally:
        db.close_connection()

def cambiar_estado_producto(id_producto: int, activo: bool) -> bool:
    """
    Alterna el estado Activo / Inactivo del producto.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        query = f"""
            UPDATE {schema}.t_producto 
            SET activo = %s, estado = %s, updated_at = NOW() 
            WHERE id_producto = %s;
        """
        filas = db.execute_query(query, (activo, activo, id_producto), commit=True)
        return filas > 0
    finally:
        db.close_connection()

# ==============================================================================
# GESTIÓN DE VARIANTES (TALLA x COLOR)
# ==============================================================================

def sincronizar_variantes_producto(
    id_producto: int,
    tallas_ids: List[int],
    colores_ids: List[int],
    precio_base: float
) -> Dict[str, Any]:
    """
    Genera y sincroniza la matriz cartesiana (Tallas x Colores) para el producto.
    - Reactiva variantes existentes.
    - Inserta nuevas variantes.
    - Para variantes no seleccionadas:
        - Si tienen inventario/movimientos -> las desactiva (activo = FALSE) para conservar historial.
        - Si no tienen inventario -> las elimina físicamente.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        # Obtener datos del producto para SKU
        prod_row = db.execute_query(
            f"SELECT codigo_producto, id_empresa FROM {schema}.t_producto WHERE id_producto = %s;",
            (id_producto,),
            fetchone=True
        )
        codigo_prod = prod_row[0] if prod_row and prod_row[0] else f"PRD-{id_producto}"

        # 1. Combinaciones deseadas: set de tuplas (id_talla, id_color)
        combinaciones_deseadas = set()
        for t_id in tallas_ids:
            for c_id in colores_ids:
                combinaciones_deseadas.add((int(t_id), int(c_id)))

        # 2. Consultar variantes existentes en la BD
        query_existentes = f"""
            SELECT id_variante, id_talla, id_color, activo 
            FROM {schema}.t_producto_talla_color 
            WHERE id_producto = %s;
        """
        filas_existentes = db.execute_query(query_existentes, (id_producto,), fetchall=True) or []
        variantes_bd = {}
        for row in filas_existentes:
            # key: (id_talla, id_color) -> (id_variante, activo)
            variantes_bd[(row[1], row[2])] = {"id_variante": row[0], "activo": bool(row[3])}

        creadas = 0
        reactivadas = 0
        desactivadas = 0
        eliminadas = 0

        # 3. Procesar combinaciones deseadas
        for (t_id, c_id) in combinaciones_deseadas:
            if (t_id, c_id) in variantes_bd:
                # Ya existe: si estaba inactiva, la reactivamos
                info = variantes_bd[(t_id, c_id)]
                if not info["activo"]:
                    db.execute_query(
                        f"UPDATE {schema}.t_producto_talla_color SET activo = TRUE, estado = TRUE WHERE id_variante = %s;",
                        (info["id_variante"],),
                        commit=True
                    )
                    reactivadas += 1
            else:
                # No existe: obtener nombres para el SKU
                t_nombre = db.execute_query(f"SELECT nombre FROM {schema}.t_talla WHERE id_talla = %s;", (t_id,), fetchone=True)
                c_nombre = db.execute_query(f"SELECT nombre FROM {schema}.t_color WHERE id_color = %s;", (c_id,), fetchone=True)
                t_str = t_nombre[0].replace(" ", "").upper()[:4] if t_nombre else str(t_id)
                c_str = c_nombre[0].replace(" ", "").upper()[:4] if c_nombre else str(c_id)
                sku = f"{codigo_prod}-{t_str}-{c_str}"

                db.execute_query(f"""
                    INSERT INTO {schema}.t_producto_talla_color (
                        id_producto, id_talla, id_color, sku, precio, activo, estado, created_at
                    ) VALUES (%s, %s, %s, %s, %s, TRUE, TRUE, NOW())
                    ON CONFLICT (id_producto, id_talla, id_color) DO UPDATE 
                    SET activo = TRUE, estado = TRUE;
                """, (id_producto, t_id, c_id, sku, precio_base), commit=True)
                creadas += 1

        # 4. Procesar variantes que estaban antes pero ya NO están en las seleccionadas
        for (t_id, c_id), info in variantes_bd.items():
            if (t_id, c_id) not in combinaciones_deseadas and info["activo"]:
                id_var = info["id_variante"]
                # Verificar si tiene stock o movimientos de inventario
                stock_row = db.execute_query(f"""
                    SELECT 
                        COALESCE(SUM(stock_actual), 0),
                        COALESCE(SUM(stock_reservado), 0)
                    FROM {schema}.t_inventario 
                    WHERE id_variante = %s;
                """, (id_var,), fetchone=True)
                stock_total = (stock_row[0] + stock_row[1]) if stock_row else 0

                mov_count = db.execute_query(f"""
                    SELECT COUNT(*) 
                    FROM {schema}.t_movimiento_inventario mov
                    JOIN {schema}.t_inventario inv ON mov.id_inventario = inv.id_inventario
                    WHERE inv.id_variante = %s;
                """, (id_var,), fetchone=True)[0]

                if stock_total > 0 or mov_count > 0:
                    # Protección de catálogo: Solo desactivar para preservar historial
                    db.execute_query(
                        f"UPDATE {schema}.t_producto_talla_color SET activo = FALSE, estado = FALSE WHERE id_variante = %s;",
                        (id_var,),
                        commit=True
                    )
                    desactivadas += 1
                else:
                    # Sin movimientos: eliminación limpia
                    db.execute_query(
                        f"DELETE FROM {schema}.t_producto_talla_color WHERE id_variante = %s;",
                        (id_var,),
                        commit=True
                    )
                    eliminadas += 1

        return {
            "total_combinaciones": len(combinaciones_deseadas),
            "creadas": creadas,
            "reactivadas": reactivadas,
            "desactivadas": desactivadas,
            "eliminadas": eliminadas
        }
    finally:
        db.close_connection()

# ==============================================================================
# GESTIÓN DE IMÁGENES MULTIMEDIA (CLOUDINARY)
# ==============================================================================

def agregar_imagen_producto(
    id_producto: int,
    imagen_url: str,
    public_id: str,
    es_principal: bool = False
) -> int:
    """
    Agrega una imagen a t_producto_imagen y sincroniza la portada en t_producto.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        # Si es la primera imagen o es_principal es True, asegurar bandera
        conteo_imgs = db.execute_query(
            f"SELECT COUNT(*) FROM {schema}.t_producto_imagen WHERE id_producto = %s;",
            (id_producto,),
            fetchone=True
        )[0]
        if conteo_imgs == 0:
            es_principal = True

        if es_principal:
            # Desmarcar anteriores
            db.execute_query(
                f"UPDATE {schema}.t_producto_imagen SET es_principal = FALSE WHERE id_producto = %s;",
                (id_producto,),
                commit=True
            )

        query = f"""
            INSERT INTO {schema}.t_producto_imagen (
                id_producto, imagen_url, public_id, es_principal, orden, created_at
            ) VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id_imagen;
        """
        res = db.execute_query(query, (id_producto, imagen_url, public_id, es_principal, conteo_imgs), fetchone=True, commit=True)
        id_img = res[0]

        if es_principal:
            db.execute_query(
                f"UPDATE {schema}.t_producto SET imagen_url = %s, updated_at = NOW() WHERE id_producto = %s;",
                (imagen_url, id_producto),
                commit=True
            )

        return id_img
    finally:
        db.close_connection()

def marcar_imagen_principal(id_imagen: int, id_producto: int) -> bool:
    """
    Establece una imagen como la principal de la prenda.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        # Verificar que la imagen pertenezca al producto
        img_row = db.execute_query(
            f"SELECT imagen_url FROM {schema}.t_producto_imagen WHERE id_imagen = %s AND id_producto = %s;",
            (id_imagen, id_producto),
            fetchone=True
        )
        if not img_row:
            return False

        url = img_row[0]
        db.execute_query(
            f"UPDATE {schema}.t_producto_imagen SET es_principal = FALSE WHERE id_producto = %s;",
            (id_producto,),
            commit=True
        )
        db.execute_query(
            f"UPDATE {schema}.t_producto_imagen SET es_principal = TRUE WHERE id_imagen = %s;",
            (id_imagen,),
            commit=True
        )
        db.execute_query(
            f"UPDATE {schema}.t_producto SET imagen_url = %s, updated_at = NOW() WHERE id_producto = %s;",
            (url, id_producto),
            commit=True
        )
        return True
    finally:
        db.close_connection()

def eliminar_imagen_producto(id_imagen: int, id_producto: int) -> Optional[str]:
    """
    Elimina la imagen de la BD y retorna su public_id para borrarla en Cloudinary.
    Si era la principal, promueve otra imagen automáticamente.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        img_row = db.execute_query(
            f"SELECT public_id, es_principal FROM {schema}.t_producto_imagen WHERE id_imagen = %s AND id_producto = %s;",
            (id_imagen, id_producto),
            fetchone=True
        )
        if not img_row:
            return None

        public_id, era_principal = img_row[0], bool(img_row[1])

        db.execute_query(
            f"DELETE FROM {schema}.t_producto_imagen WHERE id_imagen = %s;",
            (id_imagen,),
            commit=True
        )

        # Si era principal, promover la siguiente disponible
        if era_principal:
            siguiente = db.execute_query(
                f"SELECT id_imagen, imagen_url FROM {schema}.t_producto_imagen WHERE id_producto = %s ORDER BY id_imagen ASC LIMIT 1;",
                (id_producto,),
                fetchone=True
            )
            if siguiente:
                db.execute_query(
                    f"UPDATE {schema}.t_producto_imagen SET es_principal = TRUE WHERE id_imagen = %s;",
                    (siguiente[0],),
                    commit=True
                )
                db.execute_query(
                    f"UPDATE {schema}.t_producto SET imagen_url = %s, updated_at = NOW() WHERE id_producto = %s;",
                    (siguiente[1], id_producto),
                    commit=True
                )
            else:
                db.execute_query(
                    f"UPDATE {schema}.t_producto SET imagen_url = NULL, updated_at = NOW() WHERE id_producto = %s;",
                    (id_producto,),
                    commit=True
                )

        return public_id
    finally:
        db.close_connection()

# ==============================================================================
# ELIMINACIÓN INTELIGENTE DE PRODUCTO
# ==============================================================================

def eliminar_producto_seguro(id_producto: int) -> Tuple[str, List[str]]:
    """
    Evalúa si el producto tiene historial o dependencias:
    - Si tiene movimientos de inventario, stock > 0 o ventas -> Desactiva suavemente ('DESACTIVADO', []).
    - Si no tiene historial -> Borra físicamente ('ELIMINADO', [public_ids de fotos para Cloudinary]).
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        # 1. Comprobar stock o movimientos en sus variantes
        check_inventario = db.execute_query(f"""
            SELECT 
                COALESCE(SUM(inv.stock_actual), 0),
                COALESCE(SUM(inv.stock_reservado), 0)
            FROM {schema}.t_inventario inv
            JOIN {schema}.t_producto_talla_color ptc ON inv.id_variante = ptc.id_variante
            WHERE ptc.id_producto = %s;
        """, (id_producto,), fetchone=True)
        stock_total = (check_inventario[0] + check_inventario[1]) if check_inventario else 0

        check_movs = db.execute_query(f"""
            SELECT COUNT(*) 
            FROM {schema}.t_movimiento_inventario mov
            JOIN {schema}.t_inventario inv ON mov.id_inventario = inv.id_inventario
            JOIN {schema}.t_producto_talla_color ptc ON inv.id_variante = ptc.id_variante
            WHERE ptc.id_producto = %s;
        """, (id_producto,), fetchone=True)[0]

        # 2. Comprobar detalles de venta
        check_ventas = 0
        ventas_table_exists = db.execute_query(f"""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = '{schema}' AND table_name = 't_detalle_venta';
        """, fetchone=True)[0]
        if ventas_table_exists > 0:
            check_ventas = db.execute_query(f"""
                SELECT COUNT(*) FROM {schema}.t_detalle_venta dv
                JOIN {schema}.t_producto_talla_color ptc ON dv.id_variante = ptc.id_variante
                WHERE ptc.id_producto = %s;
            """, (id_producto,), fetchone=True)[0]

        if stock_total > 0 or check_movs > 0 or check_ventas > 0:
            # Desactivación preventiva
            db.execute_query(
                f"UPDATE {schema}.t_producto SET activo = FALSE, estado = FALSE, updated_at = NOW() WHERE id_producto = %s;",
                (id_producto,),
                commit=True
            )
            db.execute_query(
                f"UPDATE {schema}.t_producto_talla_color SET activo = FALSE, estado = FALSE WHERE id_producto = %s;",
                (id_producto,),
                commit=True
            )
            return ("DESACTIVADO", [])

        # 3. No tiene historial: recolectar public_ids de fotos para Cloudinary
        filas_imgs = db.execute_query(
            f"SELECT public_id FROM {schema}.t_producto_imagen WHERE id_producto = %s;",
            (id_producto,),
            fetchall=True
        ) or []
        public_ids = [r[0] for r in filas_imgs if r[0]]

        # Borrar registros en cascada
        db.execute_query(f"DELETE FROM {schema}.t_producto_imagen WHERE id_producto = %s;", (id_producto,), commit=True)
        db.execute_query(f"DELETE FROM {schema}.t_producto_talla_color WHERE id_producto = %s;", (id_producto,), commit=True)
        db.execute_query(f"DELETE FROM {schema}.t_producto WHERE id_producto = %s;", (id_producto,), commit=True)

        return ("ELIMINADO", public_ids)
    finally:
        db.close_connection()
