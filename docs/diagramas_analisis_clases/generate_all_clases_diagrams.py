#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de los 17 Diagramas de Análisis de Clases (SI2 - UAGRM)
Abarca los 25 Casos de Uso del sistema:
- 8 Casos de Uso Unificados Web / Móvil (CU05, CU06, CU07, CU08, CU09, CU10, CU11, CU26_M15)
- 9 Casos de Uso Específicos Web (CU_W20, CU_W21, CU_W22, CU_W23, CU_W24, CU_W25, CU_W27, CU_W28, CU_W29)

Cumple estrictamente las directivas de la cátedra:
1. Form (Boundary) ── Controller ── Service ── Repository ── Entities
2. Nombres de tablas de la BASE DE DATOS y TODOS sus atributos en estricto orden y MAYÚSCULAS.
3. Cajas UML de 3 compartimentos (Encabezado, Atributos, Métodos) perfectamente dimensionadas.
4. Enlaces ortogonales con multiplicidades claras (1, 1..*, 0..*).
5. Genera SVG vectorial y PNG de alta resolución (2x) vía CairoSVG.
"""

import os
import sys
import cairosvg

def escape_xml(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def render_class_box(cls):
    """Renderiza caja UML con 3 compartimentos."""
    x = cls["x"]
    y = cls["y"]
    w = cls["width"]
    header_lines = cls.get("header", [])
    attrs = cls.get("attributes", [])
    methods = cls.get("methods", [])

    line_h = 16
    pad_y = 8
    
    h_header = max(34, len(header_lines) * line_h + pad_y * 2)
    h_attrs = max(24, len(attrs) * line_h + pad_y * 1.5) if attrs else 22
    h_methods = max(24, len(methods) * line_h + pad_y * 1.5) if methods else 22
    total_h = int(h_header + h_attrs + h_methods)

    parts = []
    parts.append(f'  <!-- Clase: {" / ".join(header_lines)} -->\n')
    parts.append(f'  <g id="class_{cls["id"]}">\n')
    parts.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{total_h}" fill="#ffffff" stroke="#111827" stroke-width="1.6"/>\n')

    y_div1 = y + h_header
    parts.append(f'    <line x1="{x}" y1="{y_div1}" x2="{x + w}" y2="{y_div1}" stroke="#111827" stroke-width="1.4"/>\n')

    y_div2 = y_div1 + h_attrs
    parts.append(f'    <line x1="{x}" y1="{y_div2}" x2="{x + w}" y2="{y_div2}" stroke="#111827" stroke-width="1.4"/>\n')

    # Header
    if len(header_lines) == 1:
        parts.append(f'    <text x="{x + w/2}" y="{y + 22}" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#111827">{escape_xml(header_lines[0])}</text>\n')
    else:
        parts.append(f'    <text x="{x + w/2}" y="{y + 17}" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#475569">{escape_xml(header_lines[0])}</text>\n')
        parts.append(f'    <text x="{x + w/2}" y="{y + 34}" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#111827">{escape_xml(header_lines[1])}</text>\n')

    # Attributes
    y_attr_text = y_div1 + 16
    for idx, attr in enumerate(attrs):
        parts.append(f'    <text x="{x + 10}" y="{y_attr_text + idx * line_h}" font-size="11" fill="#111827" font-family="monospace, sans-serif">{escape_xml(attr)}</text>\n')

    # Methods
    y_method_text = y_div2 + 16
    for idx, mth in enumerate(methods):
        parts.append(f'    <text x="{x + 10}" y="{y_method_text + idx * line_h}" font-size="11" fill="#111827" font-family="monospace, sans-serif">{escape_xml(mth)}</text>\n')

    parts.append('  </g>\n')
    return "".join(parts), total_h

def render_diagram_svg(diag):
    width = diag.get("width", 1880)
    height = diag.get("height", 850)

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <!-- Encabezado del Diagrama -->
  <text x="35" y="34" font-size="16" font-weight="bold" fill="#0f172a">{escape_xml(diag["title"])}</text>
  <text x="35" y="54" font-size="12" font-weight="500" fill="#475569">{escape_xml(diag["subtitle"])}</text>
  <text x="35" y="72" font-size="11.5" font-weight="600" fill="#2563eb">Actor(es): {escape_xml(diag["actors"])}</text>
  <line x1="35" y1="82" x2="{width - 35}" y2="82" stroke="#cbd5e1" stroke-width="1.2"/>

  <!-- Leyenda de Roles Arquitectónicos -->
  <g transform="translate({width - 490}, 24)">
    <rect x="0" y="0" width="455" height="48" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <text x="12" y="19" font-size="11" font-weight="bold" fill="#334155">Capas del Análisis de Clases:</text>
    <text x="12" y="36" font-size="10.5" fill="#64748b">Boundary (Form) -&gt; Controller -&gt; Service -&gt; Repository -&gt; Entities (BD)</text>
  </g>
''')

    for cls in diag["classes"]:
        cls_svg, _ = render_class_box(cls)
        svg_parts.append(cls_svg)

    svg_parts.append('\n  <!-- Asociaciones y Multiplicidades -->\n  <g id="associations">\n')
    for conn in diag.get("connections", []):
        pts = conn["points"]
        pts_str = " ".join([f"{p[0]},{p[1]}" for p in pts])
        svg_parts.append(f'    <polyline points="{pts_str}" fill="none" stroke="#111827" stroke-width="1.6" stroke-linejoin="round"/>\n')

        if "mult_from" in conn and conn["mult_from"]:
            mx, my = conn["mult_from"]["pos"]
            txt = conn["mult_from"]["text"]
            svg_parts.append(f'    <text x="{mx}" y="{my}" font-size="11" font-weight="bold" fill="#111827">{escape_xml(txt)}</text>\n')

        if "mult_to" in conn and conn["mult_to"]:
            mx, my = conn["mult_to"]["pos"]
            txt = conn["mult_to"]["text"]
            svg_parts.append(f'    <text x="{mx}" y="{my}" font-size="11" font-weight="bold" fill="#111827">{escape_xml(txt)}</text>\n')

    svg_parts.append('  </g>\n')
    svg_parts.append('</svg>\n')
    return "".join(svg_parts)


# ==============================================================================
# DEFINICIÓN DE LOS 17 DIAGRAMAS DE ANÁLISIS DE CLASES
# ==============================================================================
ALL_DIAGRAMS = [
    # --------------------------------------------------------------------------
    # 1. CU05 W/M: Buscar y filtrar productos
    # --------------------------------------------------------------------------
    {
        "id": "CU05_WM",
        "file_name": "CU05_WM_Buscar_Filtrar_Productos_Clases",
        "title": "CU05 W/M: Buscar y filtrar productos — Diagrama de Análisis de Clases",
        "subtitle": "Unificación Web (CU/W05) y Móvil (CU/M05) | Arquitectura: Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cliente (Web y Móvil), Administrador, Administrador de tienda, Encargado de sucursal, Cajero",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 270, "width": 235,
                "header": ["Form", "Buscar_Filtrar_Productos"],
                "attributes": ["+ texto_busqueda", "+ id_categoria_sel", "+ genero_sel", "+ rango_precio_min", "+ rango_precio_max", "+ id_talla_sel", "+ id_color_sel", "+ id_sucursal_sel"],
                "methods": ["+ ingresar_termino()", "+ seleccionar_categoria()", "+ filtrar_por_precio()", "+ filtrar_por_talla_color()", "+ filtrar_por_sucursal()", "+ mostrar_grilla_catalogo()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Catalogo_Controller"],
                "attributes": [],
                "methods": ["+ get_catalogo_filtrado(filtros)", "+ get_detalle_producto(id)", "+ get_stock_sucursales(id_var)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Catalogo_Service"],
                "attributes": [],
                "methods": ["+ listar_catalogo_filtrado(filtros)", "+ validar_filtros_busqueda(filtros)", "+ obtener_variantes_con_stock(id)", "+ verificar_stock_sucursal(id_suc)"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Catalogo_Repository"],
                "attributes": [],
                "methods": ["+ query_productos_filtrados(criterios)", "+ find_variantes_by_producto(id_prod)", "+ find_stock_por_sucursal(id_var, id_suc)", "+ find_categorias_activas()"]
            },
            {
                "id": "producto", "x": 1175, "y": 290, "width": 195,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ ID_CATEGORIA", "+ ID_EMPRESA", "+ NOMBRE", "+ DESCRIPCION", "+ GENERO", "+ PRECIO_BASE", "+ IMAGEN_URL", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "categoria", "x": 1175, "y": 80, "width": 195,
                "header": ["T_CATEGORIA"],
                "attributes": ["+ ID_CATEGORIA", "+ NOMBRE", "+ DESCRIPCION", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "variante", "x": 1415, "y": 305, "width": 210,
                "header": ["T_PRODUCTO_VARIANTE"],
                "attributes": ["+ ID_VARIANTE", "+ ID_PRODUCTO", "+ ID_TALLA", "+ ID_COLOR", "+ PRECIO_ADICIONAL", "+ SKU_VARIANTE", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "talla", "x": 1675, "y": 110, "width": 160,
                "header": ["T_TALLA"],
                "attributes": ["+ ID_TALLA", "+ NOMBRE", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "color", "x": 1675, "y": 280, "width": 160,
                "header": ["T_COLOR"],
                "attributes": ["+ ID_COLOR", "+ NOMBRE", "+ CODIGO_HEX"],
                "methods": []
            },
            {
                "id": "inventario", "x": 1415, "y": 570, "width": 210,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_VARIANTE", "+ ID_SUCURSAL", "+ STOCK_ACTUAL", "+ STOCK_RESERVADO", "+ STOCK_DISPONIBLE"],
                "methods": []
            },
            {
                "id": "sucursal", "x": 1675, "y": 570, "width": 165,
                "header": ["T_SUCURSAL"],
                "attributes": ["+ ID_SUCURSAL", "+ ID_EMPRESA", "+ ID_CIUDAD", "+ NOMBRE", "+ DIRECCION", "+ ESTADO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1272, 290), (1272, 220)], "mult_from": {"text": "0..*", "pos": (1280, 275)}, "mult_to": {"text": "1", "pos": (1280, 235)}},
            {"points": [(1370, 400), (1415, 400)], "mult_from": {"text": "1", "pos": (1376, 390)}, "mult_to": {"text": "1..*", "pos": (1390, 390)}},
            {"points": [(1625, 345), (1650, 345), (1650, 170), (1675, 170)], "mult_from": {"text": "0..*", "pos": (1628, 335)}, "mult_to": {"text": "1", "pos": (1655, 160)}},
            {"points": [(1625, 385), (1650, 385), (1650, 340), (1675, 340)], "mult_from": {"text": "0..*", "pos": (1628, 375)}, "mult_to": {"text": "1", "pos": (1655, 330)}},
            {"points": [(1520, 498), (1520, 570)], "mult_from": {"text": "1", "pos": (1530, 518)}, "mult_to": {"text": "0..*", "pos": (1530, 555)}},
            {"points": [(1625, 655), (1675, 655)], "mult_from": {"text": "0..*", "pos": (1632, 645)}, "mult_to": {"text": "1", "pos": (1658, 645)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 2. CU06 W/M: Consultar detalle de producto
    # --------------------------------------------------------------------------
    {
        "id": "CU06_WM",
        "file_name": "CU06_WM_Consultar_Detalle_Producto_Clases",
        "title": "CU06 W/M: Consultar detalle de producto — Diagrama de Análisis de Clases",
        "subtitle": "Unificación Web (CU/W06) y Móvil (CU/M06) | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cliente (Web y Móvil), Administrador, Administrador de tienda, Encargado de sucursal, Cajero",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 290, "width": 235,
                "header": ["Form", "Detalle_Producto"],
                "attributes": ["+ id_producto_sel", "+ id_variante_sel", "+ talla_seleccionada", "+ color_seleccionado", "+ cantidad_deseada"],
                "methods": ["+ cargar_detalle_producto()", "+ seleccionar_talla()", "+ seleccionar_color()", "+ ver_galeria_imagenes()", "+ consultar_guia_tallas()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Producto_Detalle_Controller"],
                "attributes": [],
                "methods": ["+ get_producto_por_id(id)", "+ get_imagenes_producto(id)", "+ get_variantes_disponibles(id)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Producto_Detalle_Service"],
                "attributes": [],
                "methods": ["+ obtener_ficha_tecnica(id)", "+ consolidar_tallas_colores(id)", "+ verificar_stock_variante(id_var)"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Producto_Detalle_Repository"],
                "attributes": [],
                "methods": ["+ find_by_id(id)", "+ find_imagenes_by_producto(id)", "+ find_variantes_by_producto(id)"]
            },
            {
                "id": "producto", "x": 1175, "y": 290, "width": 195,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ ID_CATEGORIA", "+ ID_EMPRESA", "+ NOMBRE", "+ DESCRIPCION", "+ GENERO", "+ PRECIO_BASE", "+ IMAGEN_URL", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "imagen", "x": 1175, "y": 80, "width": 195,
                "header": ["T_IMAGEN_PRODUCTO"],
                "attributes": ["+ ID_IMAGEN", "+ ID_PRODUCTO", "+ URL_IMAGEN", "+ ORDEN", "+ ES_PORTADA"],
                "methods": []
            },
            {
                "id": "categoria", "x": 1175, "y": 570, "width": 195,
                "header": ["T_CATEGORIA"],
                "attributes": ["+ ID_CATEGORIA", "+ NOMBRE", "+ DESCRIPCION", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "variante", "x": 1420, "y": 305, "width": 210,
                "header": ["T_PRODUCTO_VARIANTE"],
                "attributes": ["+ ID_VARIANTE", "+ ID_PRODUCTO", "+ ID_TALLA", "+ ID_COLOR", "+ PRECIO_ADICIONAL", "+ SKU_VARIANTE", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "talla", "x": 1680, "y": 190, "width": 160,
                "header": ["T_TALLA"],
                "attributes": ["+ ID_TALLA", "+ NOMBRE", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "color", "x": 1680, "y": 420, "width": 160,
                "header": ["T_COLOR"],
                "attributes": ["+ ID_COLOR", "+ NOMBRE", "+ CODIGO_HEX"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1272, 290), (1272, 220)], "mult_from": {"text": "1", "pos": (1280, 275)}, "mult_to": {"text": "0..*", "pos": (1280, 235)}},
            {"points": [(1272, 500), (1272, 570)], "mult_from": {"text": "0..*", "pos": (1280, 520)}, "mult_to": {"text": "1", "pos": (1280, 555)}},
            {"points": [(1370, 400), (1420, 400)], "mult_from": {"text": "1", "pos": (1376, 390)}, "mult_to": {"text": "1..*", "pos": (1395, 390)}},
            {"points": [(1630, 360), (1655, 360), (1655, 250), (1680, 250)], "mult_from": {"text": "0..*", "pos": (1632, 350)}, "mult_to": {"text": "1", "pos": (1660, 240)}},
            {"points": [(1630, 420), (1655, 420), (1655, 480), (1680, 480)], "mult_from": {"text": "0..*", "pos": (1632, 410)}, "mult_to": {"text": "1", "pos": (1660, 470)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 3. CU07 W/M: Consultar disponibilidad por sucursal
    # --------------------------------------------------------------------------
    {
        "id": "CU07_WM",
        "file_name": "CU07_WM_Consultar_Disponibilidad_Sucursal_Clases",
        "title": "CU07 W/M: Consultar disponibilidad por sucursal — Diagrama de Análisis de Clases",
        "subtitle": "Unificación Web (CU/W07) y Móvil (CU/M07) | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cliente (Web y Móvil), Administrador, Administrador de tienda, Encargado de sucursal, Cajero",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 290, "width": 235,
                "header": ["Form", "Disponibilidad_Sucursal"],
                "attributes": ["+ id_variante_sel", "+ id_ciudad_sel", "+ lat_usuario", "+ lng_usuario"],
                "methods": ["+ seleccionar_variante()", "+ filtrar_por_ciudad()", "+ calcular_tienda_cercana()", "+ mostrar_stock_tiendas()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Disponibilidad_Controller"],
                "attributes": [],
                "methods": ["+ get_disponibilidad_variante(id_var)", "+ get_stock_por_sucursal(id_var, id_suc)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Disponibilidad_Service"],
                "attributes": [],
                "methods": ["+ consultar_stock_sucursales(id_var)", "+ filtrar_sucursales_con_existencias(lista)"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Disponibilidad_Repository"],
                "attributes": [],
                "methods": ["+ find_stock_en_sucursales(id_var)", "+ find_sucursales_activas_con_ciudad()"]
            },
            {
                "id": "inventario", "x": 1175, "y": 310, "width": 210,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_VARIANTE", "+ ID_SUCURSAL", "+ STOCK_ACTUAL", "+ STOCK_RESERVADO", "+ STOCK_DISPONIBLE"],
                "methods": []
            },
            {
                "id": "variante", "x": 1175, "y": 90, "width": 210,
                "header": ["T_PRODUCTO_VARIANTE"],
                "attributes": ["+ ID_VARIANTE", "+ ID_PRODUCTO", "+ SKU_VARIANTE", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "sucursal", "x": 1445, "y": 300, "width": 195,
                "header": ["T_SUCURSAL"],
                "attributes": ["+ ID_SUCURSAL", "+ ID_EMPRESA", "+ ID_CIUDAD", "+ NOMBRE", "+ DIRECCION", "+ TELEFONO", "+ LATITUD", "+ LONGITUD", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "ciudad", "x": 1695, "y": 330, "width": 150,
                "header": ["T_CIUDAD"],
                "attributes": ["+ ID_CIUDAD", "+ NOMBRE", "+ DEPARTAMENTO", "+ ESTADO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1280, 310), (1280, 215)], "mult_from": {"text": "0..*", "pos": (1290, 290)}, "mult_to": {"text": "1", "pos": (1290, 235)}},
            {"points": [(1385, 410), (1445, 410)], "mult_from": {"text": "0..*", "pos": (1395, 400)}, "mult_to": {"text": "1", "pos": (1425, 400)}},
            {"points": [(1640, 410), (1695, 410)], "mult_from": {"text": "0..*", "pos": (1648, 400)}, "mult_to": {"text": "1", "pos": (1675, 400)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 4. CU08 W/M: Gestionar carrito de compras
    # --------------------------------------------------------------------------
    {
        "id": "CU08_WM",
        "file_name": "CU08_WM_Gestionar_Carrito_Compras_Clases",
        "title": "CU08 W/M: Gestionar carrito de compras — Diagrama de Análisis de Clases",
        "subtitle": "Unificación Web (CU/W08) y Móvil (CU/M08) | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cliente (Web y Móvil)",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Carrito_Compras"],
                "attributes": ["+ id_carrito", "+ id_variante_agregar", "+ cantidad_ajustar", "+ codigo_cupon"],
                "methods": ["+ agregar_item()", "+ modificar_cantidad()", "+ eliminar_item()", "+ vaciar_carrito()", "+ aplicar_descuento()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 330, "width": 235,
                "header": ["Carrito_Controller"],
                "attributes": [],
                "methods": ["+ post_item_carrito(item)", "+ put_cantidad_item(id, cant)", "+ delete_item(id)", "+ get_carrito(id_cli)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Carrito_Service"],
                "attributes": [],
                "methods": ["+ validar_stock_prenda(id, cant)", "+ sincronizar_carrito_sesion(cli)", "+ calcular_totales_carrito(cart)"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Carrito_Repository"],
                "attributes": [],
                "methods": ["+ save_or_update_carrito(cart)", "+ find_detalle_carrito(id_cart)", "+ update_item_cantidad(id, cant)", "+ remove_item(id)"]
            },
            {
                "id": "carrito", "x": 1175, "y": 315, "width": 195,
                "header": ["T_CARRITO"],
                "attributes": ["+ ID_CARRITO", "+ ID_CLIENTE", "+ FECHA_CREACION", "+ ESTADO", "+ TOTAL_ESTIMADO"],
                "methods": []
            },
            {
                "id": "det_carrito", "x": 1420, "y": 305, "width": 210,
                "header": ["T_DETALLE_CARRITO"],
                "attributes": ["+ ID_DETALLE_CARRITO", "+ ID_CARRITO", "+ ID_VARIANTE", "+ CANTIDAD", "+ PRECIO_UNITARIO", "+ SUBTOTAL"],
                "methods": []
            },
            {
                "id": "variante", "x": 1675, "y": 180, "width": 170,
                "header": ["T_PRODUCTO_VARIANTE"],
                "attributes": ["+ ID_VARIANTE", "+ ID_PRODUCTO", "+ SKU_VARIANTE", "+ PRECIO_ADICIONAL"],
                "methods": []
            },
            {
                "id": "inventario", "x": 1675, "y": 440, "width": 170,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_VARIANTE", "+ ID_SUCURSAL", "+ STOCK_DISPONIBLE"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1370, 400), (1420, 400)], "mult_from": {"text": "1", "pos": (1378, 390)}, "mult_to": {"text": "0..*", "pos": (1395, 390)}},
            {"points": [(1630, 360), (1655, 360), (1655, 250), (1675, 250)], "mult_from": {"text": "0..*", "pos": (1632, 350)}, "mult_to": {"text": "1", "pos": (1655, 240)}},
            {"points": [(1630, 420), (1655, 420), (1655, 500), (1675, 500)], "mult_from": {"text": "0..*", "pos": (1632, 410)}, "mult_to": {"text": "1", "pos": (1655, 490)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 5. CU09 W/M: Realizar compra
    # --------------------------------------------------------------------------
    {
        "id": "CU09_WM",
        "file_name": "CU09_WM_Realizar_Compra_Clases",
        "title": "CU09 W/M: Realizar compra — Diagrama de Análisis de Clases",
        "subtitle": "Unificación Web (CU/W09) y Móvil (CU/M09) | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cliente (Web y Móvil), Sistema de pagos",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Checkout_Compra"],
                "attributes": ["+ tipo_entrega", "+ direccion_envio", "+ id_sucursal_recojo", "+ metodo_pago", "+ datos_facturacion"],
                "methods": ["+ seleccionar_metodo_envio()", "+ ingresar_datos_facturacion()", "+ confirmar_orden_compra()", "+ procesar_pago()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Checkout_Controller"],
                "attributes": [],
                "methods": ["+ post_crear_pedido(payload)", "+ post_confirmar_pago(payload)", "+ get_resumen_pedido(id_ped)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Checkout_Service"],
                "attributes": [],
                "methods": ["+ validar_pedido_y_stock(cart)", "+ crear_orden_compra()", "+ bloquear_stock_pedido()", "+ vincular_pago_exitoso()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Checkout_Repository"],
                "attributes": [],
                "methods": ["+ insert_pedido(ped)", "+ insert_detalle_pedido(det)", "+ update_stock_reservado(var, cant)", "+ insert_pago(pago)"]
            },
            {
                "id": "pedido", "x": 1175, "y": 290, "width": 200,
                "header": ["T_PEDIDO"],
                "attributes": ["+ ID_PEDIDO", "+ ID_CLIENTE", "+ ID_EMPRESA", "+ NUMERO_PEDIDO", "+ TOTAL", "+ ESTADO_PEDIDO", "+ TIPO_ENTREGA", "+ FECHA_REGISTRO"],
                "methods": []
            },
            {
                "id": "det_pedido", "x": 1425, "y": 290, "width": 200,
                "header": ["T_DETALLE_PEDIDO"],
                "attributes": ["+ ID_DETALLE_PEDIDO", "+ ID_PEDIDO", "+ ID_VARIANTE", "+ CANTIDAD", "+ PRECIO_UNITARIO", "+ SUBTOTAL"],
                "methods": []
            },
            {
                "id": "pago", "x": 1175, "y": 570, "width": 200,
                "header": ["T_PAGO"],
                "attributes": ["+ ID_PAGO", "+ ID_PEDIDO", "+ METODO_PAGO", "+ MONTO", "+ CODIGO_TRANSACCION", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "inventario", "x": 1675, "y": 290, "width": 170,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_VARIANTE", "+ ID_SUCURSAL", "+ STOCK_ACTUAL", "+ STOCK_RESERVADO"],
                "methods": []
            },
            {
                "id": "bitacora", "x": 1425, "y": 570, "width": 200,
                "header": ["T_BITACORA"],
                "attributes": ["+ ID_BITACORA", "+ ID_USUARIO", "+ ACCION", "+ TABLA_AFECTADA", "+ FECHA"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1375, 390), (1425, 390)], "mult_from": {"text": "1", "pos": (1382, 380)}, "mult_to": {"text": "1..*", "pos": (1405, 380)}},
            {"points": [(1275, 480), (1275, 570)], "mult_from": {"text": "1", "pos": (1285, 500)}, "mult_to": {"text": "1", "pos": (1285, 555)}},
            {"points": [(1625, 390), (1675, 390)], "mult_from": {"text": "1", "pos": (1632, 380)}, "mult_to": {"text": "0..*", "pos": (1655, 380)}},
            {"points": [(1375, 640), (1425, 640)], "mult_from": {"text": "1", "pos": (1382, 630)}, "mult_to": {"text": "1", "pos": (1405, 630)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 6. CU10 W/M: Gestionar reservas
    # --------------------------------------------------------------------------
    {
        "id": "CU10_WM",
        "file_name": "CU10_WM_Gestionar_Reservas_Clases",
        "title": "CU10 W/M: Gestionar reservas — Diagrama de Análisis de Clases",
        "subtitle": "Unificación Web (CU/W10) y Móvil (CU/M10) | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cliente (Web y Móvil)",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Reservas_Prendas"],
                "attributes": ["+ id_variante_sel", "+ id_sucursal_retiro", "+ cantidad_apartar", "+ horas_vigencia"],
                "methods": ["+ seleccionar_tienda_retiro()", "+ apartar_prenda()", "+ ver_codigo_qr_reserva()", "+ cancelar_reserva()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Reserva_Controller"],
                "attributes": [],
                "methods": ["+ post_crear_reserva(data)", "+ get_mis_reservas(id_cli)", "+ put_cancelar_reserva(id_res)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Reserva_Service"],
                "attributes": [],
                "methods": ["+ verificar_stock_disponible_tienda()", "+ registrar_reserva_temporal()", "+ apartar_stock_inventario()", "+ generar_ticket_qr()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Reserva_Repository"],
                "attributes": [],
                "methods": ["+ insert_reserva(res)", "+ insert_detalle_reserva(det)", "+ update_increment_stock_reservado(var, suc, cant)"]
            },
            {
                "id": "reserva", "x": 1175, "y": 290, "width": 200,
                "header": ["T_RESERVA"],
                "attributes": ["+ ID_RESERVA", "+ ID_CLIENTE", "+ ID_SUCURSAL", "+ CODIGO_RESERVA_QR", "+ ESTADO", "+ FECHA_RESERVA", "+ FECHA_EXPIRACION"],
                "methods": []
            },
            {
                "id": "det_reserva", "x": 1425, "y": 290, "width": 200,
                "header": ["T_DETALLE_RESERVA"],
                "attributes": ["+ ID_DETALLE_RESERVA", "+ ID_RESERVA", "+ ID_VARIANTE", "+ CANTIDAD", "+ PRECIO_CONGELADO"],
                "methods": []
            },
            {
                "id": "inventario", "x": 1675, "y": 290, "width": 170,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_VARIANTE", "+ ID_SUCURSAL", "+ STOCK_ACTUAL", "+ STOCK_RESERVADO"],
                "methods": []
            },
            {
                "id": "sucursal", "x": 1175, "y": 570, "width": 200,
                "header": ["T_SUCURSAL"],
                "attributes": ["+ ID_SUCURSAL", "+ NOMBRE", "+ DIRECCION", "+ TELEFONO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1375, 380), (1425, 380)], "mult_from": {"text": "1", "pos": (1382, 370)}, "mult_to": {"text": "1..*", "pos": (1405, 370)}},
            {"points": [(1625, 380), (1675, 380)], "mult_from": {"text": "1", "pos": (1632, 370)}, "mult_to": {"text": "0..*", "pos": (1655, 370)}},
            {"points": [(1275, 470), (1275, 570)], "mult_from": {"text": "0..*", "pos": (1285, 490)}, "mult_to": {"text": "1", "pos": (1285, 555)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 7. CU11 W/M: Consultar pedidos e historial de compras
    # --------------------------------------------------------------------------
    {
        "id": "CU11_WM",
        "file_name": "CU11_WM_Consultar_Pedidos_Historial_Clases",
        "title": "CU11 W/M: Consultar pedidos e historial de compras — Diagrama de Análisis de Clases",
        "subtitle": "Unificación Web (CU/W11) y Móvil (CU/M11) | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cliente (Web y Móvil)",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Historial_Pedidos"],
                "attributes": ["+ filtro_estado_pedido", "+ rango_fechas", "+ id_pedido_sel"],
                "methods": ["+ listar_pedidos_cliente()", "+ filtrar_por_fecha()", "+ ver_tracking_envio()", "+ descargar_comprobante_digital()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Historial_Pedidos_Controller"],
                "attributes": [],
                "methods": ["+ get_pedidos_usuario(id_usr)", "+ get_detalle_orden(id_ped)", "+ get_tracking_pedido(id_ped)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Historial_Pedidos_Service"],
                "attributes": [],
                "methods": ["+ obtener_historial_compras(cli)", "+ armar_timeline_tracking(ped)", "+ emitir_recibo_resumen(ped)"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Historial_Pedidos_Repository"],
                "attributes": [],
                "methods": ["+ find_pedidos_by_cliente(cli)", "+ find_detalles_con_prendas(ped)", "+ find_pagos_by_pedido(ped)"]
            },
            {
                "id": "pedido", "x": 1175, "y": 290, "width": 195,
                "header": ["T_PEDIDO"],
                "attributes": ["+ ID_PEDIDO", "+ ID_CLIENTE", "+ NUMERO_PEDIDO", "+ TOTAL", "+ ESTADO_PEDIDO", "+ FECHA_REGISTRO"],
                "methods": []
            },
            {
                "id": "det_pedido", "x": 1420, "y": 290, "width": 210,
                "header": ["T_DETALLE_PEDIDO"],
                "attributes": ["+ ID_DETALLE_PEDIDO", "+ ID_PEDIDO", "+ ID_VARIANTE", "+ CANTIDAD", "+ PRECIO_UNITARIO", "+ SUBTOTAL"],
                "methods": []
            },
            {
                "id": "producto", "x": 1675, "y": 290, "width": 170,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ NOMBRE", "+ IMAGEN_URL"],
                "methods": []
            },
            {
                "id": "pago", "x": 1175, "y": 570, "width": 195,
                "header": ["T_PAGO"],
                "attributes": ["+ ID_PAGO", "+ ID_PEDIDO", "+ METODO_PAGO", "+ MONTO", "+ ESTADO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1370, 390), (1420, 390)], "mult_from": {"text": "1", "pos": (1378, 380)}, "mult_to": {"text": "1..*", "pos": (1400, 380)}},
            {"points": [(1630, 390), (1675, 390)], "mult_from": {"text": "0..*", "pos": (1638, 380)}, "mult_to": {"text": "1", "pos": (1658, 380)}},
            {"points": [(1272, 450), (1272, 570)], "mult_from": {"text": "1", "pos": (1282, 475)}, "mult_to": {"text": "1", "pos": (1282, 555)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 8. CU26/M15 W/M: Mostrar ubicaciones de sucursales
    # --------------------------------------------------------------------------
    {
        "id": "CU26_M15_WM",
        "file_name": "CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Clases",
        "title": "CU26/M15 W/M: Mostrar ubicaciones de sucursales — Diagrama de Análisis de Clases",
        "subtitle": "Unificación Web (CU/W26) y Móvil (CU/M15) | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cliente (Web y Móvil)",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 290, "width": 235,
                "header": ["Form", "Mapa_Sucursales"],
                "attributes": ["+ id_ciudad_filtro", "+ coords_origen", "+ sucursal_seleccionada"],
                "methods": ["+ cargar_mapa_interactivo()", "+ filtrar_por_departamento()", "+ ver_horarios_contacto()", "+ trazar_ruta_como_llegar()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Sucursales_Controller"],
                "attributes": [],
                "methods": ["+ get_sucursales_activas()", "+ get_sucursales_por_ciudad(id)", "+ get_info_tienda(id_suc)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Sucursales_Service"],
                "attributes": [],
                "methods": ["+ listar_tiendas_geolocalizadas()", "+ calcular_distancia_tiendas(lat, lng)", "+ consolidar_horarios_contacto()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Sucursales_Repository"],
                "attributes": [],
                "methods": ["+ find_sucursales_with_ciudad()", "+ find_ciudades_con_tiendas()"]
            },
            {
                "id": "sucursal", "x": 1175, "y": 300, "width": 205,
                "header": ["T_SUCURSAL"],
                "attributes": ["+ ID_SUCURSAL", "+ ID_EMPRESA", "+ ID_CIUDAD", "+ NOMBRE", "+ DIRECCION", "+ TELEFONO", "+ LATITUD", "+ LONGITUD", "+ HORARIO_APERTURA", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "ciudad", "x": 1445, "y": 310, "width": 180,
                "header": ["T_CIUDAD"],
                "attributes": ["+ ID_CIUDAD", "+ NOMBRE", "+ DEPARTAMENTO", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "empresa", "x": 1675, "y": 310, "width": 170,
                "header": ["T_EMPRESA"],
                "attributes": ["+ ID_EMPRESA", "+ NOMBRE_EMPRESA", "+ NIT", "+ ESTADO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1380, 410), (1445, 410)], "mult_from": {"text": "0..*", "pos": (1390, 400)}, "mult_to": {"text": "1", "pos": (1425, 400)}},
            {"points": [(1625, 410), (1675, 410)], "mult_from": {"text": "0..*", "pos": (1632, 400)}, "mult_to": {"text": "1", "pos": (1655, 400)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 9. CU_W20: Gestionar temporadas y colecciones (Web)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W20",
        "file_name": "CU_W20_Gestionar_Temporadas_Colecciones_Clases",
        "title": "CU/W20: Gestionar temporadas y colecciones — Diagrama de Análisis de Clases",
        "subtitle": "Módulo Web | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Administrador, Administrador de tienda",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Temporadas_Colecciones"],
                "attributes": ["+ nombre_temporada", "+ fecha_inicio", "+ fecha_fin", "+ nombre_coleccion", "+ prendas_asignadas"],
                "methods": ["+ crear_temporada()", "+ editar_vigencia()", "+ crear_coleccion_moda()", "+ asociar_prendas_catalogo()", "+ dar_baja_temporada()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Temporadas_Controller"],
                "attributes": [],
                "methods": ["+ post_temporada(data)", "+ put_temporada(id, data)", "+ post_coleccion(data)", "+ put_coleccion_prendas(id, pr)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Temporadas_Service"],
                "attributes": [],
                "methods": ["+ validar_rango_fechas()", "+ registrar_temporada_activa()", "+ asignar_prendas_coleccion()", "+ auditar_cambio_coleccion()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Temporadas_Repository"],
                "attributes": [],
                "methods": ["+ insert_temporada(t)", "+ update_temporada(t)", "+ insert_coleccion(c)", "+ link_prendas_coleccion(c, p)", "+ log_bitacora(b)"]
            },
            {
                "id": "temporada", "x": 1175, "y": 290, "width": 195,
                "header": ["T_TEMPORADA"],
                "attributes": ["+ ID_TEMPORADA", "+ NOMBRE", "+ DESCRIPCION", "+ FECHA_INICIO", "+ FECHA_FIN", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "coleccion", "x": 1420, "y": 290, "width": 195,
                "header": ["T_COLECCION"],
                "attributes": ["+ ID_COLECCION", "+ ID_TEMPORADA", "+ NOMBRE", "+ DESCRIPCION", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "producto", "x": 1675, "y": 290, "width": 170,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ NOMBRE", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "bitacora", "x": 1175, "y": 570, "width": 195,
                "header": ["T_BITACORA"],
                "attributes": ["+ ID_BITACORA", "+ ID_USUARIO", "+ ACCION", "+ TABLA_AFECTADA", "+ FECHA"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1370, 390), (1420, 390)], "mult_from": {"text": "1", "pos": (1378, 380)}, "mult_to": {"text": "0..*", "pos": (1395, 380)}},
            {"points": [(1615, 390), (1675, 390)], "mult_from": {"text": "0..*", "pos": (1622, 380)}, "mult_to": {"text": "0..*", "pos": (1650, 380)}},
            {"points": [(1272, 450), (1272, 570)], "mult_from": {"text": "1", "pos": (1282, 475)}, "mult_to": {"text": "1", "pos": (1282, 555)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 10. CU_W21: Gestionar proveedores (Web)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W21",
        "file_name": "CU_W21_Gestionar_Proveedores_Clases",
        "title": "CU/W21: Gestionar proveedores — Diagrama de Análisis de Clases",
        "subtitle": "Módulo Web | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Administrador, Administrador de tienda",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Gestion_Proveedores"],
                "attributes": ["+ razon_social", "+ nit", "+ telefono", "+ email", "+ direccion", "+ rubro_textil"],
                "methods": ["+ registrar_proveedor()", "+ actualizar_datos()", "+ consultar_catalogo_taller()", "+ cambiar_estado_proveedor()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Proveedores_Controller"],
                "attributes": [],
                "methods": ["+ post_proveedor(payload)", "+ put_proveedor(id, payload)", "+ get_proveedores()", "+ delete_proveedor(id)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Proveedores_Service"],
                "attributes": [],
                "methods": ["+ validar_nit_unico_tenant()", "+ verificar_proveedor_activo()", "+ auditar_registro_proveedor()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Proveedores_Repository"],
                "attributes": [],
                "methods": ["+ insert_proveedor(p)", "+ update_proveedor(p)", "+ find_by_nit(nit)", "+ log_bitacora(b)"]
            },
            {
                "id": "proveedor", "x": 1175, "y": 290, "width": 210,
                "header": ["T_PROVEEDOR"],
                "attributes": ["+ ID_PROVEEDOR", "+ ID_EMPRESA", "+ NOMBRE_RAZON_SOCIAL", "+ NIT", "+ TELEFONO", "+ EMAIL", "+ DIRECCION", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "prod_prov", "x": 1435, "y": 290, "width": 200,
                "header": ["T_PRODUCTO_PROVEEDOR"],
                "attributes": ["+ ID_PROVEEDOR", "+ ID_PRODUCTO", "+ CODIGO_REFERENCIA", "+ PRECIO_COMPRA", "+ FECHA_ASIGNACION"],
                "methods": []
            },
            {
                "id": "producto", "x": 1685, "y": 310, "width": 160,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ NOMBRE", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "bitacora", "x": 1175, "y": 570, "width": 210,
                "header": ["T_BITACORA"],
                "attributes": ["+ ID_BITACORA", "+ ID_USUARIO", "+ ACCION", "+ TABLA_AFECTADA", "+ FECHA"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1385, 390), (1435, 390)], "mult_from": {"text": "1", "pos": (1392, 380)}, "mult_to": {"text": "0..*", "pos": (1412, 380)}},
            {"points": [(1635, 390), (1685, 390)], "mult_from": {"text": "0..*", "pos": (1642, 380)}, "mult_to": {"text": "1", "pos": (1665, 380)}},
            {"points": [(1280, 490), (1280, 570)], "mult_from": {"text": "1", "pos": (1290, 510)}, "mult_to": {"text": "1", "pos": (1290, 555)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 11. CU_W22: Gestionar inventario (Web)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W22",
        "file_name": "CU_W22_Gestionar_Inventario_Clases",
        "title": "CU/W22: Gestionar inventario — Diagrama de Análisis de Clases",
        "subtitle": "Módulo Web | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Administrador, Administrador de tienda, Encargado de sucursal",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Gestion_Inventario"],
                "attributes": ["+ id_sucursal", "+ id_variante", "+ tipo_movimiento", "+ cantidad", "+ motivo_ajuste"],
                "methods": ["+ registrar_entrada_stock()", "+ registrar_salida_stock()", "+ registrar_ajuste_fisico()", "+ consultar_kardex_movimientos()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Inventario_Controller"],
                "attributes": [],
                "methods": ["+ post_movimiento_inventario(p)", "+ get_stock_variante(var, suc)", "+ get_kardex_sucursal(id_suc)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Inventario_Service"],
                "attributes": [],
                "methods": ["+ validar_tipo_movimiento()", "+ procesar_movimiento_stock_db()", "+ verificar_regla_stock_reservado()", "+ registrar_auditoria_inventario()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Inventario_Repository"],
                "attributes": [],
                "methods": ["+ call_fn_movimiento_inventario()", "+ insert_movimiento(mov)", "+ select_stock_for_update()", "+ insert_bitacora(b)"]
            },
            {
                "id": "inventario", "x": 1175, "y": 290, "width": 210,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_VARIANTE", "+ ID_SUCURSAL", "+ STOCK_ACTUAL", "+ STOCK_RESERVADO", "+ STOCK_DISPONIBLE"],
                "methods": []
            },
            {
                "id": "movimiento", "x": 1435, "y": 290, "width": 210,
                "header": ["T_MOVIMIENTO_INVENTARIO"],
                "attributes": ["+ ID_MOVIMIENTO", "+ ID_INVENTARIO", "+ TIPO_MOVIMIENTO", "+ CANTIDAD", "+ MOTIVO", "+ FECHA_MOVIMIENTO"],
                "methods": []
            },
            {
                "id": "variante", "x": 1695, "y": 290, "width": 150,
                "header": ["T_PRODUCTO_VARIANTE"],
                "attributes": ["+ ID_VARIANTE", "+ SKU_VARIANTE"],
                "methods": []
            },
            {
                "id": "sucursal", "x": 1175, "y": 570, "width": 210,
                "header": ["T_SUCURSAL"],
                "attributes": ["+ ID_SUCURSAL", "+ NOMBRE", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "bitacora", "x": 1435, "y": 570, "width": 210,
                "header": ["T_BITACORA"],
                "attributes": ["+ ID_BITACORA", "+ ID_USUARIO", "+ ACCION", "+ TABLA_AFECTADA", "+ FECHA"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1385, 390), (1435, 390)], "mult_from": {"text": "1", "pos": (1392, 380)}, "mult_to": {"text": "0..*", "pos": (1412, 380)}},
            {"points": [(1645, 390), (1695, 390)], "mult_from": {"text": "0..*", "pos": (1652, 380)}, "mult_to": {"text": "1", "pos": (1675, 380)}},
            {"points": [(1280, 470), (1280, 570)], "mult_from": {"text": "0..*", "pos": (1290, 490)}, "mult_to": {"text": "1", "pos": (1290, 555)}},
            {"points": [(1385, 640), (1435, 640)], "mult_from": {"text": "1", "pos": (1392, 630)}, "mult_to": {"text": "1", "pos": (1412, 630)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 12. CU_W23: Gestionar disponibilidad de prendas (Web)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W23",
        "file_name": "CU_W23_Gestionar_Disponibilidad_Prendas_Clases",
        "title": "CU/W23: Gestionar disponibilidad de prendas — Diagrama de Análisis de Clases",
        "subtitle": "Módulo Web | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Administrador, Administrador de tienda, Encargado de sucursal",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Disponibilidad_Prendas"],
                "attributes": ["+ id_variante", "+ flag_visible_web", "+ flag_disponible_tienda", "+ umbral_stock_alerta"],
                "methods": ["+ conmutar_visibilidad_web()", "+ conmutar_disponibilidad_tienda()", "+ configurar_stock_minimo()", "+ guardar_cambios_disponibilidad()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Disponibilidad_Prendas_Controller"],
                "attributes": [],
                "methods": ["+ put_visibilidad_prenda(id, p)", "+ get_alertas_bajo_stock(id_suc)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Disponibilidad_Prendas_Service"],
                "attributes": [],
                "methods": ["+ validar_umbral_minimo()", "+ evaluar_estado_publicacion()", "+ actualizar_banderas_disponibilidad()", "+ auditar_cambio_visibilidad()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Disponibilidad_Prendas_Repository"],
                "attributes": [],
                "methods": ["+ update_variante_flags(id, flags)", "+ update_inventario_umbral(id, umbral)", "+ insert_bitacora(b)"]
            },
            {
                "id": "variante", "x": 1175, "y": 290, "width": 210,
                "header": ["T_PRODUCTO_VARIANTE"],
                "attributes": ["+ ID_VARIANTE", "+ ID_PRODUCTO", "+ SKU_VARIANTE", "+ ES_VISIBLE_WEB", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "inventario", "x": 1435, "y": 290, "width": 210,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_VARIANTE", "+ ID_SUCURSAL", "+ STOCK_ACTUAL", "+ STOCK_DISPONIBLE", "+ UMBRAL_MINIMO"],
                "methods": []
            },
            {
                "id": "producto", "x": 1695, "y": 290, "width": 150,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ NOMBRE", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "bitacora", "x": 1175, "y": 570, "width": 210,
                "header": ["T_BITACORA"],
                "attributes": ["+ ID_BITACORA", "+ ID_USUARIO", "+ ACCION", "+ TABLA_AFECTADA", "+ FECHA"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1385, 390), (1435, 390)], "mult_from": {"text": "1", "pos": (1392, 380)}, "mult_to": {"text": "0..*", "pos": (1412, 380)}},
            {"points": [(1645, 390), (1695, 390)], "mult_from": {"text": "0..*", "pos": (1652, 380)}, "mult_to": {"text": "1", "pos": (1675, 380)}},
            {"points": [(1280, 450), (1280, 570)], "mult_from": {"text": "1", "pos": (1290, 475)}, "mult_to": {"text": "1", "pos": (1290, 555)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 13. CU_W24: Registrar venta presencial (Web)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W24",
        "file_name": "CU_W24_Registrar_Venta_Presencial_Clases",
        "title": "CU/W24: Registrar venta presencial — Diagrama de Análisis de Clases",
        "subtitle": "Módulo Web | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cajero",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "POS_Venta_Presencial"],
                "attributes": ["+ scan_codigo_barras_sku", "+ id_cliente_pos", "+ lineas_venta", "+ subtotal", "+ descuento", "+ total"],
                "methods": ["+ escanear_prenda()", "+ modificar_cantidad_linea()", "+ asignar_cliente()", "+ calcular_totales_pos()", "+ proceder_a_cobro()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["POS_Venta_Controller"],
                "attributes": [],
                "methods": ["+ post_registrar_venta(p)", "+ get_buscar_cliente_pos(doc)", "+ get_info_sku(sku)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["POS_Venta_Service"],
                "attributes": [],
                "methods": ["+ validar_caja_abierta_cajero()", "+ verificar_stock_disponible_tienda()", "+ generar_venta_pos()", "+ rebajar_stock_inmediato()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["POS_Venta_Repository"],
                "attributes": [],
                "methods": ["+ insert_venta(venta)", "+ insert_detalle_venta(det)", "+ update_stock_salida_venta(var, suc, cant)", "+ insert_movimiento(mov)"]
            },
            {
                "id": "venta", "x": 1175, "y": 290, "width": 200,
                "header": ["T_VENTA"],
                "attributes": ["+ ID_VENTA", "+ ID_EMPRESA", "+ ID_SUCURSAL", "+ ID_EMPLEADO", "+ NUMERO_VENTA", "+ FECHA_VENTA", "+ TOTAL_VENTA", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "det_venta", "x": 1425, "y": 290, "width": 200,
                "header": ["T_DETALLE_VENTA"],
                "attributes": ["+ ID_DETALLE_VENTA", "+ ID_VENTA", "+ ID_VARIANTE", "+ CANTIDAD", "+ PRECIO_UNITARIO", "+ SUBTOTAL"],
                "methods": []
            },
            {
                "id": "inventario", "x": 1675, "y": 290, "width": 170,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_VARIANTE", "+ ID_SUCURSAL", "+ STOCK_ACTUAL", "+ STOCK_DISPONIBLE"],
                "methods": []
            },
            {
                "id": "caja", "x": 1175, "y": 570, "width": 200,
                "header": ["T_CAJA"],
                "attributes": ["+ ID_CAJA", "+ ID_SUCURSAL", "+ ID_CAJERO", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "movimiento", "x": 1425, "y": 570, "width": 200,
                "header": ["T_MOVIMIENTO_INVENTARIO"],
                "attributes": ["+ ID_MOVIMIENTO", "+ ID_INVENTARIO", "+ TIPO_MOVIMIENTO", "+ CANTIDAD", "+ MOTIVO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1375, 390), (1425, 390)], "mult_from": {"text": "1", "pos": (1382, 380)}, "mult_to": {"text": "1..*", "pos": (1405, 380)}},
            {"points": [(1625, 390), (1675, 390)], "mult_from": {"text": "1", "pos": (1632, 380)}, "mult_to": {"text": "0..*", "pos": (1655, 380)}},
            {"points": [(1275, 480), (1275, 570)], "mult_from": {"text": "0..*", "pos": (1285, 500)}, "mult_to": {"text": "1", "pos": (1285, 555)}},
            {"points": [(1525, 460), (1525, 570)], "mult_from": {"text": "1", "pos": (1535, 480)}, "mult_to": {"text": "1", "pos": (1535, 555)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 14. CU_W25: Atender reservas (Web)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W25",
        "file_name": "CU_W25_Atender_Reservas_Clases",
        "title": "CU/W25: Atender reservas — Diagrama de Análisis de Clases",
        "subtitle": "Módulo Web | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Encargado de sucursal, Cajero",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Atender_Reservas"],
                "attributes": ["+ codigo_reserva_ingresado", "+ scan_qr", "+ estado_reserva_encontrada", "+ prendas_reservadas"],
                "methods": ["+ buscar_reserva_por_codigo()", "+ escanear_codigo_qr()", "+ verificar_vigencia_apartado()", "+ convertir_reserva_a_venta()", "+ liberar_reserva_vencida()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Atencion_Reservas_Controller"],
                "attributes": [],
                "methods": ["+ get_buscar_reserva(cod)", "+ post_despachar_reserva_pos(id)", "+ put_liberar_reserva(id)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Atencion_Reservas_Service"],
                "attributes": [],
                "methods": ["+ validar_estado_reserva()", "+ transformar_reserva_en_venta()", "+ liberar_stock_reservado_a_disponible()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Atencion_Reservas_Repository"],
                "attributes": [],
                "methods": ["+ find_reserva_by_codigo(cod)", "+ update_estado_reserva(id, est)", "+ create_venta_from_reserva(id)", "+ update_stock_liberar(var, cant)"]
            },
            {
                "id": "reserva", "x": 1175, "y": 290, "width": 200,
                "header": ["T_RESERVA"],
                "attributes": ["+ ID_RESERVA", "+ ID_CLIENTE", "+ ID_SUCURSAL", "+ CODIGO_RESERVA_QR", "+ ESTADO", "+ FECHA_EXPIRACION"],
                "methods": []
            },
            {
                "id": "det_reserva", "x": 1425, "y": 290, "width": 200,
                "header": ["T_DETALLE_RESERVA"],
                "attributes": ["+ ID_DETALLE_RESERVA", "+ ID_RESERVA", "+ ID_VARIANTE", "+ CANTIDAD", "+ PRECIO_CONGELADO"],
                "methods": []
            },
            {
                "id": "venta", "x": 1175, "y": 570, "width": 200,
                "header": ["T_VENTA"],
                "attributes": ["+ ID_VENTA", "+ ID_SUCURSAL", "+ TOTAL_VENTA", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "inventario", "x": 1675, "y": 290, "width": 170,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_VARIANTE", "+ ID_SUCURSAL", "+ STOCK_ACTUAL", "+ STOCK_RESERVADO", "+ STOCK_DISPONIBLE"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1375, 380), (1425, 380)], "mult_from": {"text": "1", "pos": (1382, 370)}, "mult_to": {"text": "1..*", "pos": (1405, 370)}},
            {"points": [(1625, 380), (1675, 380)], "mult_from": {"text": "1", "pos": (1632, 370)}, "mult_to": {"text": "0..*", "pos": (1655, 370)}},
            {"points": [(1275, 450), (1275, 570)], "mult_from": {"text": "1", "pos": (1285, 475)}, "mult_to": {"text": "0..1", "pos": (1285, 555)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 15. CU_W27: Procesar pago electrónico (Web)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W27",
        "file_name": "CU_W27_Procesar_Pago_Electronico_Clases",
        "title": "CU/W27: Procesar pago electrónico — Diagrama de Análisis de Clases",
        "subtitle": "Módulo Web | Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cliente, Sistema de pagos",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Pago_Electronico"],
                "attributes": ["+ id_pedido", "+ pasarela_seleccionada", "+ token_tarjeta", "+ codigo_qr_bancario", "+ monto_a_pagar"],
                "methods": ["+ seleccionar_tarjeta_o_qr()", "+ enviar_datos_pasarela()", "+ verificar_codigo_autorizacion()", "+ confirmar_pago_aprobado()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Pago_Electronico_Controller"],
                "attributes": [],
                "methods": ["+ post_procesar_pago_web(p)", "+ post_webhook_pasarela(p)", "+ get_estado_pago(id_pago)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Pago_Electronico_Service"],
                "attributes": [],
                "methods": ["+ invocar_pasarela_externa()", "+ registrar_transaccion_pago()", "+ actualizar_estado_pedido_pagado()", "+ auditar_pago_exitoso()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Pago_Electronico_Repository"],
                "attributes": [],
                "methods": ["+ insert_pago(pago)", "+ update_estado_pedido(id, est)", "+ insert_bitacora(b)"]
            },
            {
                "id": "pago", "x": 1175, "y": 290, "width": 200,
                "header": ["T_PAGO"],
                "attributes": ["+ ID_PAGO", "+ ID_PEDIDO", "+ METODO_PAGO", "+ MONTO", "+ CODIGO_TRANSACCION", "+ ESTADO", "+ FECHA_PAGO"],
                "methods": []
            },
            {
                "id": "pedido", "x": 1425, "y": 290, "width": 200,
                "header": ["T_PEDIDO"],
                "attributes": ["+ ID_PEDIDO", "+ ID_CLIENTE", "+ TOTAL", "+ ESTADO_PEDIDO", "+ FECHA_REGISTRO"],
                "methods": []
            },
            {
                "id": "metodo", "x": 1675, "y": 310, "width": 170,
                "header": ["T_METODO_PAGO"],
                "attributes": ["+ ID_METODO", "+ NOMBRE", "+ TIPO", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "bitacora", "x": 1175, "y": 570, "width": 200,
                "header": ["T_BITACORA"],
                "attributes": ["+ ID_BITACORA", "+ ID_USUARIO", "+ ACCION", "+ TABLA_AFECTADA", "+ FECHA"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1375, 390), (1425, 390)], "mult_from": {"text": "1", "pos": (1382, 380)}, "mult_to": {"text": "1", "pos": (1405, 380)}},
            {"points": [(1625, 390), (1675, 390)], "mult_from": {"text": "0..*", "pos": (1632, 380)}, "mult_to": {"text": "1", "pos": (1655, 380)}},
            {"points": [(1275, 470), (1275, 570)], "mult_from": {"text": "1", "pos": (1285, 490)}, "mult_to": {"text": "1", "pos": (1285, 555)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 16. CU_W28: Procesar pago en caja (Web)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W28",
        "file_name": "CU_W28_Procesar_Pago_Caja_Clases",
        "title": "CU/W28: Procesar pago en caja — Diagrama de Análisis de Clases",
        "subtitle": "Módulo Web (Control de Efectivo por Denominaciones) | Form -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cajero",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Cobro_Caja"],
                "attributes": ["+ id_venta", "+ monto_total_venta", "+ desglose_billetes_recibidos", "+ total_recibido", "+ cambio_a_entregar"],
                "methods": ["+ ingresar_denominaciones_recibidas()", "+ calcular_cambio_optimo()", "+ confirmar_pago_efectivo()", "+ abrir_gaveta_caja()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Caja_Pago_Controller"],
                "attributes": [],
                "methods": ["+ post_procesar_cobro_caja(p)", "+ get_resumen_arqueo_caja(id_caja)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Caja_Pago_Service"],
                "attributes": [],
                "methods": ["+ validar_sesion_caja_abierta()", "+ registrar_pago_con_denominaciones()", "+ registrar_entradas_salidas_efectivo()", "+ marcar_venta_como_pagada()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Caja_Pago_Repository"],
                "attributes": [],
                "methods": ["+ insert_pago(pago)", "+ insert_denominaciones_detalle(d)", "+ update_estado_venta(id, est)", "+ update_saldo_caja(caja, e, s)"]
            },
            {
                "id": "pago", "x": 1175, "y": 290, "width": 200,
                "header": ["T_PAGO"],
                "attributes": ["+ ID_PAGO", "+ ID_VENTA", "+ METODO_PAGO", "+ MONTO", "+ FECHA_PAGO", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "pago_denom", "x": 1425, "y": 290, "width": 210,
                "header": ["T_PAGO_DENOMINACION"],
                "attributes": ["+ ID_PAGO_DENOMINACION", "+ ID_PAGO", "+ DENOMINACION", "+ CANTIDAD", "+ SUBTOTAL", "+ TIPO"],
                "methods": []
            },
            {
                "id": "venta", "x": 1685, "y": 300, "width": 160,
                "header": ["T_VENTA"],
                "attributes": ["+ ID_VENTA", "+ ID_SUCURSAL", "+ TOTAL_VENTA", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "caja", "x": 1175, "y": 570, "width": 200,
                "header": ["T_CAJA"],
                "attributes": ["+ ID_CAJA", "+ ID_SUCURSAL", "+ ID_CAJERO", "+ MONTO_INICIAL", "+ MONTO_ACTUAL_EFECTIVO", "+ ESTADO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1375, 380), (1425, 380)], "mult_from": {"text": "1", "pos": (1382, 370)}, "mult_to": {"text": "1..*", "pos": (1405, 370)}},
            {"points": [(1635, 380), (1685, 380)], "mult_from": {"text": "1", "pos": (1642, 370)}, "mult_to": {"text": "1", "pos": (1665, 370)}},
            {"points": [(1275, 450), (1275, 570)], "mult_from": {"text": "0..*", "pos": (1285, 475)}, "mult_to": {"text": "1", "pos": (1285, 555)}}
        ]
    },

    # --------------------------------------------------------------------------
    # 17. CU_W29: Emitir comprobante de venta (Web)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W29",
        "file_name": "CU_W29_Emitir_Comprobante_Venta_Clases",
        "title": "CU/W29: Emitir comprobante de venta — Diagrama de Análisis de Clases",
        "subtitle": "Módulo Web (Factura / Recibo) | Form -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cajero",
        "width": 1880,
        "height": 850,
        "classes": [
            {
                "id": "form", "x": 35, "y": 280, "width": 235,
                "header": ["Form", "Emision_Comprobante"],
                "attributes": ["+ id_venta", "+ tipo_comprobante", "+ nit_razon_social", "+ email_digital"],
                "methods": ["+ seleccionar_tipo_factura_recibo()", "+ ingresar_datos_tributarios()", "+ generar_codigo_control_qr()", "+ mandar_impresion_termica()"]
            },
            {
                "id": "ctrl", "x": 310, "y": 340, "width": 235,
                "header": ["Comprobante_Controller"],
                "attributes": [],
                "methods": ["+ post_emitir_comprobante(p)", "+ get_comprobante_por_venta(id_v)", "+ get_reimprimir_ticket(id_c)"]
            },
            {
                "id": "srv", "x": 585, "y": 330, "width": 255,
                "header": ["Comprobante_Service"],
                "attributes": [],
                "methods": ["+ validar_dosificacion_tributaria()", "+ generar_codigo_control_y_qr()", "+ registrar_comprobante_fiscal()", "+ auditar_emision_fiscal()"]
            },
            {
                "id": "repo", "x": 880, "y": 330, "width": 255,
                "header": ["Comprobante_Repository"],
                "attributes": [],
                "methods": ["+ insert_comprobante(comp)", "+ update_venta_comprobante(id_v, id_c)", "+ insert_bitacora(b)"]
            },
            {
                "id": "comprobante", "x": 1175, "y": 290, "width": 210,
                "header": ["T_COMPROBANTE"],
                "attributes": ["+ ID_COMPROBANTE", "+ ID_VENTA", "+ TIPO_COMPROBANTE", "+ NUMERO_COMPROBANTE", "+ CODIGO_CONTROL", "+ QR_IMPRESION", "+ FECHA_EMISION", "+ TOTAL"],
                "methods": []
            },
            {
                "id": "venta", "x": 1435, "y": 290, "width": 190,
                "header": ["T_VENTA"],
                "attributes": ["+ ID_VENTA", "+ ID_SUCURSAL", "+ TOTAL_VENTA", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "empresa", "x": 1675, "y": 310, "width": 170,
                "header": ["T_EMPRESA"],
                "attributes": ["+ ID_EMPRESA", "+ NOMBRE_EMPRESA", "+ NIT", "+ LEYENDA_FACTURA"],
                "methods": []
            },
            {
                "id": "bitacora", "x": 1175, "y": 570, "width": 210,
                "header": ["T_BITACORA"],
                "attributes": ["+ ID_BITACORA", "+ ID_USUARIO", "+ ACCION", "+ TABLA_AFECTADA", "+ FECHA"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(270, 410), (310, 410)]},
            {"points": [(545, 410), (585, 410)]},
            {"points": [(840, 410), (880, 410)]},
            {"points": [(1135, 410), (1175, 410)]},
            {"points": [(1385, 380), (1435, 380)], "mult_from": {"text": "1", "pos": (1392, 370)}, "mult_to": {"text": "1", "pos": (1412, 370)}},
            {"points": [(1625, 380), (1675, 380)], "mult_from": {"text": "0..*", "pos": (1632, 370)}, "mult_to": {"text": "1", "pos": (1655, 370)}},
            {"points": [(1280, 490), (1280, 570)], "mult_from": {"text": "1", "pos": (1290, 510)}, "mult_to": {"text": "1", "pos": (1290, 555)}}
        ]
    }
]

def main():
    out_dir = "docs/diagramas_analisis_clases"
    os.makedirs(out_dir, exist_ok=True)
    total = len(ALL_DIAGRAMS)
    print(f"🚀 Iniciando generación de los {total} Diagramas de Análisis de Clases (SI2 - UAGRM)...")

    for idx, diag in enumerate(ALL_DIAGRAMS, 1):
        svg_content = render_diagram_svg(diag)
        base_name = diag["file_name"]
        svg_path = os.path.join(out_dir, f"{base_name}.svg")
        png_path = os.path.join(out_dir, f"{base_name}.png")

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2.0)
        print(f" [{idx:02d}/{total:02d}] ✅ Generado: {base_name}.svg y {base_name}.png")

    print(f"\n🎉 ¡Todos los {total} diagramas de clases generados y exportados exitosamente en {out_dir}!")

if __name__ == "__main__":
    main()
