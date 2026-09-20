from typing import Dict, Any, Tuple, List, Optional
from app.config import Config

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

def construir_consulta_reporte(
    definicion: Dict[str, Any],
    request: Dict[str, Any],
    id_empresa: int,
    sucursales_permitidas: Optional[List[int]] = None
) -> Tuple[str, Tuple, List[Dict[str, Any]]]:
    """
    Construye una consulta SQL estrictamente parametrizada (%s) sobre las vistas.
    Garantiza el aislamiento multi-tenant forzando 'id_empresa = %s'
    y nunca concatena texto ingresado por el usuario en la sentencia SQL.
    """
    schema = _get_schema()
    vista = f"{schema}.{definicion['vista']}"
    filtros = request.get("filtros") or {}
    group_by = request.get("groupBy")
    order_by = request.get("orderBy")
    order_dir = "DESC" if str(request.get("orderDirection", "DESC")).upper() == "DESC" else "ASC"

    where_clauses = ["id_empresa = %s"]
    params = [id_empresa]

    # Restricción de sucursal por usuario de Nivel 4/5 (Encargado/Cajero)
    if sucursales_permitidas and len(sucursales_permitidas) > 0:
        placeholders = ', '.join(['%s'] * len(sucursales_permitidas))
        where_clauses.append(f"id_sucursal IN ({placeholders})")
        params.extend(sucursales_permitidas)

    # 1. Filtros de Fecha (Inclusivos)
    if filtros.get("fechaDesde"):
        where_clauses.append("fecha >= %s")
        params.append(filtros["fechaDesde"])
        
    if filtros.get("fechaHasta"):
        where_clauses.append("fecha <= %s")
        params.append(filtros["fechaHasta"])

    # 2. Filtros de Entidades
    if filtros.get("sucursalId"):
        where_clauses.append("id_sucursal = %s")
        params.append(filtros["sucursalId"])

    if filtros.get("categoriaId") and "categoriaId" in definicion["filtros_permitidos"]:
        where_clauses.append("id_categoria = %s")
        params.append(filtros["categoriaId"])

    if filtros.get("productoId") and "productoId" in definicion["filtros_permitidos"]:
        where_clauses.append("id_producto = %s")
        params.append(filtros["productoId"])

    if filtros.get("metodoPagoId") and "metodoPagoId" in definicion["filtros_permitidos"]:
        where_clauses.append("id_metodo_pago = %s")
        params.append(filtros["metodoPagoId"])

    if filtros.get("clienteId") and "clienteId" in definicion["filtros_permitidos"]:
        where_clauses.append("id_cliente = %s")
        params.append(filtros["clienteId"])

    if filtros.get("estado") and str(filtros.get("estado")).upper() != "TODOS":
        where_clauses.append("UPPER(estado) = %s")
        params.append(str(filtros["estado"]).upper())

    if filtros.get("estadoStock") and filtros.get("estadoStock") != "todos":
        where_clauses.append("LOWER(estado_stock) = %s")
        params.append(str(filtros["estadoStock"]).lower())

    where_sql = " AND ".join(where_clauses)

    # =========================================================================
    # RAMA A: CONSULTA CON AGRUPACIÓN (GROUP BY)
    # =========================================================================
    if group_by and group_by in definicion.get("agrupaciones_permitidas", []):
        columna_grupo = group_by
        
        # Adaptaciones de nombres de columna en vista
        if columna_grupo == "dia":
            col_expr = "fecha"
            col_alias = "dia"
        else:
            col_expr = columna_grupo
            col_alias = columna_grupo

        campo_monto = definicion.get("campo_monto", "total")
        
        sql = f"""
            SELECT 
                {col_expr} AS {col_alias},
                COUNT(*) AS cantidad_registros,
                COALESCE(SUM({campo_monto}), 0) AS total_monto,
                COALESCE(AVG({campo_monto}), 0) AS promedio_monto
            FROM {vista}
            WHERE {where_sql}
            GROUP BY {col_expr}
            ORDER BY total_monto {order_dir};
        """
        
        columnas_meta = [
            {"campo": col_alias, "titulo": col_alias.replace('_', ' ').capitalize(), "tipo": "string"},
            {"campo": "cantidad_registros", "titulo": "Registros / Transacciones", "tipo": "number"},
            {"campo": "total_monto", "titulo": "Monto Total (Bs.)", "tipo": "currency"},
            {"campo": "promedio_monto", "titulo": "Promedio (Bs.)", "tipo": "currency"}
        ]
        return sql, tuple(params), columnas_meta

    # =========================================================================
    # RAMA B: CONSULTA DE DETALLE ESTÁNDAR
    # =========================================================================
    columnas_meta = definicion["columnas"]
    campos_sql = [c["campo"] for c in columnas_meta]
    select_sql = ", ".join(campos_sql)

    # Ordenamiento seguro verificado contra campos permitidos
    campo_orden = order_by if (order_by and any(c["campo"] == order_by for c in columnas_meta)) else campos_sql[0]
    
    # Si el reporte tiene columna 'fecha' o 'total', preferirlas para orden lógico
    if not order_by:
        if "fecha" in campos_sql:
            campo_orden = "fecha"
            order_dir = "DESC"
        elif "total" in campos_sql:
            campo_orden = "total"
            order_dir = "DESC"
        elif "stock_disponible" in campos_sql:
            campo_orden = "stock_disponible"
            order_dir = "ASC"

    sql = f"""
        SELECT {select_sql}
        FROM {vista}
        WHERE {where_sql}
        ORDER BY {campo_orden} {order_dir}
        LIMIT 500;
    """

    return sql, tuple(params), columnas_meta
