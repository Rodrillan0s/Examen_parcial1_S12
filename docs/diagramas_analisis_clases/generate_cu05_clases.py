#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del Diagrama de Análisis de Clases para CU05 W/M: Buscar y filtrar productos
Modelo completo según la arquitectura multicapa y el estándar del docente:
- Boundary (Formulario / Interfaz de Usuario)
- Controller (Controlador / Rutas API)
- Service (Servicio de Reglas de Negocio)
- Repository (Repositorio de Acceso a Datos)
- Entities (Tablas de la Base de Datos y Atributos estrictamente en MAYÚSCULAS)
- Asociaciones y multiplicidades ortogonales limpias
"""

import os
import cairosvg

def escape_xml(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def render_class_box(cls):
    """
    Renderiza una caja de clase UML con 3 compartimentos:
    1. Encabezado (Nombre de la clase, centrado, negrita)
    2. Atributos (Alineados a la izquierda)
    3. Métodos (Alineados a la izquierda)
    """
    x = cls["x"]
    y = cls["y"]
    w = cls["width"]
    header_lines = cls.get("header", [])
    attrs = cls.get("attributes", [])
    methods = cls.get("methods", [])

    line_h = 16
    pad_y = 8
    
    # 1. Altura Header
    h_header = max(34, len(header_lines) * line_h + pad_y * 2)
    
    # 2. Altura Atributos
    h_attrs = max(24, len(attrs) * line_h + pad_y * 1.5) if attrs else 22
    
    # 3. Altura Métodos
    h_methods = max(24, len(methods) * line_h + pad_y * 1.5) if methods else 22

    total_h = int(h_header + h_attrs + h_methods)

    parts = []
    parts.append(f'  <!-- Clase: {" / ".join(header_lines)} -->\n')
    parts.append(f'  <g id="class_{cls["id"]}">\n')
    # Rectángulo principal
    parts.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{total_h}" fill="#ffffff" stroke="#111827" stroke-width="1.6"/>\n')

    # Divisor 1: Header -> Atributos
    y_div1 = y + h_header
    parts.append(f'    <line x1="{x}" y1="{y_div1}" x2="{x + w}" y2="{y_div1}" stroke="#111827" stroke-width="1.4"/>\n')

    # Divisor 2: Atributos -> Métodos
    y_div2 = y_div1 + h_attrs
    parts.append(f'    <line x1="{x}" y1="{y_div2}" x2="{x + w}" y2="{y_div2}" stroke="#111827" stroke-width="1.4"/>\n')

    # Texto Header (Centrado)
    if len(header_lines) == 1:
        parts.append(f'    <text x="{x + w/2}" y="{y + 22}" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#111827">{escape_xml(header_lines[0])}</text>\n')
    else:
        parts.append(f'    <text x="{x + w/2}" y="{y + 17}" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#475569">{escape_xml(header_lines[0])}</text>\n')
        parts.append(f'    <text x="{x + w/2}" y="{y + 34}" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#111827">{escape_xml(header_lines[1])}</text>\n')

    # Texto Atributos (Alineado izquierda, margen 10px)
    y_attr_text = y_div1 + 16
    for idx, attr in enumerate(attrs):
        parts.append(f'    <text x="{x + 10}" y="{y_attr_text + idx * line_h}" font-size="11" fill="#111827" font-family="monospace, sans-serif">{escape_xml(attr)}</text>\n')

    # Texto Métodos (Alineado izquierda, margen 10px)
    y_method_text = y_div2 + 16
    for idx, mth in enumerate(methods):
        parts.append(f'    <text x="{x + 10}" y="{y_method_text + idx * line_h}" font-size="11" fill="#111827" font-family="monospace, sans-serif">{escape_xml(mth)}</text>\n')

    parts.append('  </g>\n')
    return "".join(parts), total_h

def generate_cu05_diagram():
    diag = {
        "title": "CU05 W/M: Buscar y filtrar productos — Diagrama de Análisis de Clases",
        "subtitle": "Unificación Web (CU/W05) y Móvil (CU/M05) | Arquitectura: Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)",
        "actors": "Cliente (Web y Móvil), Administrador, Administrador de tienda, Encargado de sucursal, Cajero",
        "width": 1880,
        "height": 850,
        "classes": [
            # 1. Boundary: Form Buscar_Filtrar_Productos
            {
                "id": "form_catalogo",
                "x": 35,
                "y": 270,
                "width": 235,
                "header": ["Form", "Buscar_Filtrar_Productos"],
                "attributes": [
                    "+ texto_busqueda",
                    "+ id_categoria_sel",
                    "+ genero_sel",
                    "+ rango_precio_min",
                    "+ rango_precio_max",
                    "+ id_talla_sel",
                    "+ id_color_sel",
                    "+ id_sucursal_sel"
                ],
                "methods": [
                    "+ ingresar_termino()",
                    "+ seleccionar_categoria()",
                    "+ filtrar_por_precio()",
                    "+ filtrar_por_talla_color()",
                    "+ filtrar_por_sucursal()",
                    "+ mostrar_grilla_catalogo()"
                ]
            },
            # 2. Controller: Catalogo_Controller
            {
                "id": "catalogo_controller",
                "x": 310,
                "y": 340,
                "width": 235,
                "header": ["Catalogo_Controller"],
                "attributes": [],
                "methods": [
                    "+ get_catalogo_filtrado(filtros)",
                    "+ get_detalle_producto(id)",
                    "+ get_stock_sucursales(id_var)"
                ]
            },
            # 3. Service: Catalogo_Service
            {
                "id": "catalogo_service",
                "x": 585,
                "y": 330,
                "width": 255,
                "header": ["Catalogo_Service"],
                "attributes": [],
                "methods": [
                    "+ listar_catalogo_filtrado(filtros)",
                    "+ validar_filtros_busqueda(filtros)",
                    "+ obtener_variantes_con_stock(id)",
                    "+ verificar_stock_sucursal(id_suc)"
                ]
            },
            # 4. Repository: Catalogo_Repository
            {
                "id": "catalogo_repository",
                "x": 880,
                "y": 330,
                "width": 255,
                "header": ["Catalogo_Repository"],
                "attributes": [],
                "methods": [
                    "+ query_productos_filtrados(criterios)",
                    "+ find_variantes_by_producto(id_prod)",
                    "+ find_stock_por_sucursal(id_var, id_suc)",
                    "+ find_categorias_activas()"
                ]
            },
            # 5. Entity: T_PRODUCTO (MAYÚSCULAS)
            {
                "id": "producto",
                "x": 1175,
                "y": 290,
                "width": 195,
                "header": ["T_PRODUCTO"],
                "attributes": [
                    "+ ID_PRODUCTO",
                    "+ ID_CATEGORIA",
                    "+ ID_EMPRESA",
                    "+ NOMBRE",
                    "+ DESCRIPCION",
                    "+ GENERO",
                    "+ PRECIO_BASE",
                    "+ IMAGEN_URL",
                    "+ ESTADO"
                ],
                "methods": []
            },
            # 6. Entity: T_CATEGORIA (MAYÚSCULAS)
            {
                "id": "categoria",
                "x": 1175,
                "y": 80,
                "width": 195,
                "header": ["T_CATEGORIA"],
                "attributes": [
                    "+ ID_CATEGORIA",
                    "+ NOMBRE",
                    "+ DESCRIPCION",
                    "+ ESTADO"
                ],
                "methods": []
            },
            # 7. Entity: T_PRODUCTO_VARIANTE (MAYÚSCULAS)
            {
                "id": "variante",
                "x": 1415,
                "y": 305,
                "width": 210,
                "header": ["T_PRODUCTO_VARIANTE"],
                "attributes": [
                    "+ ID_VARIANTE",
                    "+ ID_PRODUCTO",
                    "+ ID_TALLA",
                    "+ ID_COLOR",
                    "+ PRECIO_ADICIONAL",
                    "+ SKU_VARIANTE",
                    "+ ESTADO"
                ],
                "methods": []
            },
            # 8. Entity: T_TALLA (MAYÚSCULAS)
            {
                "id": "talla",
                "x": 1675,
                "y": 110,
                "width": 160,
                "header": ["T_TALLA"],
                "attributes": [
                    "+ ID_TALLA",
                    "+ NOMBRE",
                    "+ ESTADO"
                ],
                "methods": []
            },
            # 9. Entity: T_COLOR (MAYÚSCULAS)
            {
                "id": "color",
                "x": 1675,
                "y": 280,
                "width": 160,
                "header": ["T_COLOR"],
                "attributes": [
                    "+ ID_COLOR",
                    "+ NOMBRE",
                    "+ CODIGO_HEX"
                ],
                "methods": []
            },
            # 10. Entity: T_INVENTARIO (MAYÚSCULAS)
            {
                "id": "inventario",
                "x": 1415,
                "y": 570,
                "width": 210,
                "header": ["T_INVENTARIO"],
                "attributes": [
                    "+ ID_INVENTARIO",
                    "+ ID_VARIANTE",
                    "+ ID_SUCURSAL",
                    "+ STOCK_ACTUAL",
                    "+ STOCK_RESERVADO",
                    "+ STOCK_DISPONIBLE"
                ],
                "methods": []
            },
            # 11. Entity: T_SUCURSAL (MAYÚSCULAS)
            {
                "id": "sucursal",
                "x": 1675,
                "y": 570,
                "width": 165,
                "header": ["T_SUCURSAL"],
                "attributes": [
                    "+ ID_SUCURSAL",
                    "+ ID_EMPRESA",
                    "+ ID_CIUDAD",
                    "+ NOMBRE",
                    "+ DIRECCION",
                    "+ ESTADO"
                ],
                "methods": []
            }
        ],
        "connections": [
            # Form -> Controller (Horizontal directo)
            {"points": [(270, 410), (310, 410)]},

            # Controller -> Service (Horizontal directo)
            {"points": [(545, 410), (585, 410)]},

            # Service -> Repository (Horizontal directo)
            {"points": [(840, 410), (880, 410)]},

            # Repository -> T_PRODUCTO (Horizontal directo)
            {"points": [(1135, 410), (1175, 410)]},

            # T_PRODUCTO -> T_CATEGORIA (Vertical)
            {
                "points": [(1272, 290), (1272, 220)],
                "mult_from": {"text": "0..*", "pos": (1280, 275)},
                "mult_to": {"text": "1", "pos": (1280, 235)}
            },

            # T_PRODUCTO -> T_PRODUCTO_VARIANTE (Horizontal)
            {
                "points": [(1370, 400), (1415, 400)],
                "mult_from": {"text": "1", "pos": (1376, 390)},
                "mult_to": {"text": "1..*", "pos": (1390, 390)}
            },

            # T_PRODUCTO_VARIANTE -> T_TALLA (Ortogonal arriba derecha)
            {
                "points": [(1625, 345), (1650, 345), (1650, 170), (1675, 170)],
                "mult_from": {"text": "0..*", "pos": (1628, 335)},
                "mult_to": {"text": "1", "pos": (1655, 160)}
            },

            # T_PRODUCTO_VARIANTE -> T_COLOR (Ortogonal medio derecha)
            {
                "points": [(1625, 385), (1650, 385), (1650, 340), (1675, 340)],
                "mult_from": {"text": "0..*", "pos": (1628, 375)},
                "mult_to": {"text": "1", "pos": (1655, 330)}
            },

            # T_PRODUCTO_VARIANTE -> T_INVENTARIO (Vertical abajo)
            {
                "points": [(1520, 498), (1520, 570)],
                "mult_from": {"text": "1", "pos": (1530, 518)},
                "mult_to": {"text": "0..*", "pos": (1530, 555)}
            },

            # T_INVENTARIO -> T_SUCURSAL (Horizontal derecha)
            {
                "points": [(1625, 655), (1675, 655)],
                "mult_from": {"text": "0..*", "pos": (1632, 645)},
                "mult_to": {"text": "1", "pos": (1658, 645)}
            }
        ]
    }

    width = diag["width"]
    height = diag["height"]

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

    # 1. Renderizar Clases
    for cls in diag["classes"]:
        cls_svg, act_h = render_class_box(cls)
        svg_parts.append(cls_svg)

    # 2. Renderizar Asociaciones
    svg_parts.append('\n  <!-- Asociaciones y Multiplicidades -->\n  <g id="associations">\n')
    for conn in diag.get("connections", []):
        pts = conn["points"]
        pts_str = " ".join([f"{p[0]},{p[1]}" for p in pts])
        svg_parts.append(f'    <polyline points="{pts_str}" fill="none" stroke="#111827" stroke-width="1.6" stroke-linejoin="round"/>\n')

        # Multiplicidad origen
        if "mult_from" in conn and conn["mult_from"]:
            mx, my = conn["mult_from"]["pos"]
            txt = conn["mult_from"]["text"]
            svg_parts.append(f'    <text x="{mx}" y="{my}" font-size="11" font-weight="bold" fill="#111827">{escape_xml(txt)}</text>\n')

        # Multiplicidad destino
        if "mult_to" in conn and conn["mult_to"]:
            mx, my = conn["mult_to"]["pos"]
            txt = conn["mult_to"]["text"]
            svg_parts.append(f'    <text x="{mx}" y="{my}" font-size="11" font-weight="bold" fill="#111827">{escape_xml(txt)}</text>\n')

    svg_parts.append('  </g>\n')
    svg_parts.append('</svg>\n')

    svg_content = "".join(svg_parts)
    
    out_dir = "docs/diagramas_analisis_clases"
    os.makedirs(out_dir, exist_ok=True)
    
    svg_path = os.path.join(out_dir, "CU05_WM_Buscar_Filtrar_Productos_Clases.svg")
    png_path = os.path.join(out_dir, "CU05_WM_Buscar_Filtrar_Productos_Clases.png")

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"✅ SVG guardado: {svg_path}")

    cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2.0)
    print(f"✅ PNG guardado (2x): {png_path}")

if __name__ == "__main__":
    generate_cu05_diagram()
