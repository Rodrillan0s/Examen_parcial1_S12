#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del Diagrama de Análisis de Clases para CU/W12: Obtener recomendaciones de productos
Basado en la BASE DE DATOS ACTUALIZADA enviada por el usuario (UAGRM - SI2).

Arquitectura y Directivas Cátedra:
1. Capas: Form (Boundary) -> Controller -> Service -> Repository -> Entities (BD en MAYÚSCULAS)
2. Cajas UML de 3 compartimentos (Header, Atributos, Métodos)
3. Atributos de las entidades de Base de Datos exactos y en estricto orden según el DER actualizado:
   - T_RECOMENDACION (ID_RECOMENDACION, ID_CLIENTE, ID_PRODUCTO, PUNTUACION, MOTIVO, FECHA_RECOMENDACION)
   - T_PREFERENCIA_CLIENTE (ID_PREFERENCIA, ID_CLIENTE, ID_CATEGORIA, ID_TALLA, ID_COLOR, TIPO_PREFERENCIA)
   - T_PRODUCTO (ID_PRODUCTO, ID_CATEGORIA, CODIGO_PRODUCTO, NOMBRE, DESCRIPCION, MARCA, GENERO, PRECIO, IMAGEN_URL, ESTADO, FECHA_REGISTRO)
   - T_PROMOCION_PRODUCTO (ID_PROMOCION_PRODUCTO, ID_PROMOCION, ID_PRODUCTO, PORCENTAJE_DESCUENTO)
   - T_PROMOCION (ID_PROMOCION, NOMBRE, DESCRIPCION, FECHA_INICIO, FECHA_FIN, ESTADO)
   - T_CLIENTE (ID_CLIENTE, ID_USUARIO, CI, FECHA_REGISTRO)
   - T_CATEGORIA (ID_CATEGORIA, NOMBRE, DESCRIPCION, ESTADO)
4. Enlaces ortogonales con multiplicidades formales (1, 1..*, 0..*).
5. Renderizado en SVG vectorial y PNG de alta resolución (2x) con resvg_py.
"""

import os
import shutil
import resvg_py

def escape_xml(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def render_class_box(cls):
    """Renderiza una caja de clase UML con 3 compartimentos."""
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
        parts.append(f'    <text x="{x + w/2}" y="{y + 22}" text-anchor="middle" font-size="12" font-weight="bold" fill="#111827">{escape_xml(header_lines[0])}</text>\n')
    else:
        parts.append(f'    <text x="{x + w/2}" y="{y + 17}" text-anchor="middle" font-size="11" font-weight="bold" fill="#475569">{escape_xml(header_lines[0])}</text>\n')
        parts.append(f'    <text x="{x + w/2}" y="{y + 34}" text-anchor="middle" font-size="12" font-weight="bold" fill="#111827">{escape_xml(header_lines[1])}</text>\n')

    # Attributes
    y_attr_text = y_div1 + 16
    for idx, attr in enumerate(attrs):
        parts.append(f'    <text x="{x + 10}" y="{y_attr_text + idx * line_h}" font-size="10.5" fill="#111827" font-family="monospace, sans-serif">{escape_xml(attr)}</text>\n')

    # Methods
    y_method_text = y_div2 + 16
    for idx, mth in enumerate(methods):
        parts.append(f'    <text x="{x + 10}" y="{y_method_text + idx * line_h}" font-size="10.5" fill="#111827" font-family="monospace, sans-serif">{escape_xml(mth)}</text>\n')

    parts.append('  </g>\n')
    return "".join(parts), total_h

def render_diagram_svg(diag):
    width = diag.get("width", 2120)
    height = diag.get("height", 860)

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <!-- Encabezado del Diagrama -->
  <text x="35" y="34" font-size="16" font-weight="bold" fill="#0f172a">{escape_xml(diag["title"])}</text>
  <text x="35" y="54" font-size="12" font-weight="500" fill="#475569">{escape_xml(diag["subtitle"])}</text>
  <text x="35" y="72" font-size="11.5" font-weight="600" fill="#2563eb">Actor(es): {escape_xml(diag["actors"])}</text>
  <line x1="35" y1="82" x2="{width - 35}" y2="82" stroke="#cbd5e1" stroke-width="1.2"/>

  <!-- Leyenda de Roles Arquitectónicos -->
  <g transform="translate({width - 510}, 24)">
    <rect x="0" y="0" width="475" height="48" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <text x="12" y="19" font-size="11" font-weight="bold" fill="#334155">Capas del Análisis de Clases:</text>
    <text x="12" y="36" font-size="10.5" fill="#64748b">Boundary (Form) -&gt; Controller -&gt; Service -&gt; Repository -&gt; Entities (BD Actualizada)</text>
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

# ==================== CONFIGURACIÓN DE CU/W12 ====================
CU12_DIAGRAM_CONFIG = {
    "title": "CU/W12: Obtener recomendaciones de productos — Diagrama de Análisis de Clases",
    "subtitle": "Sistema Aura Store | Arquitectura Multicapa: Form -> Controller -> Service -> Repository -> Entities (BD Actualizada en MAYÚSCULAS)",
    "actors": "Cliente (Web y Móvil), Visitante, Administrador de tienda",
    "width": 2150,
    "height": 850,
    "classes": [
        # 1. Boundary: Form Obtener_Recomendaciones
        {
            "id": "form_recomendacion",
            "x": 35,
            "y": 270,
            "width": 260,
            "header": ["Form", "Obtener_Recomendaciones"],
            "attributes": [
                "+ id_cliente_activo",
                "+ id_categoria_interes",
                "+ estilo_preferido",
                "+ rango_precio_max",
                "+ lista_prendas_sugeridas",
                "+ prenda_seleccionada"
            ],
            "methods": [
                "+ abrir_seccion_para_ti()",
                "+ seleccionar_preferencia_estilo()",
                "+ filtrar_por_categoria()",
                "+ solicitar_nuevas_sugerencias()",
                "+ ver_detalle_prenda()"
            ]
        },
        # 2. Controller: Recomendacion_Controller
        {
            "id": "ctrl_recomendacion",
            "x": 335,
            "y": 340,
            "width": 255,
            "header": ["Recomendacion_Controller"],
            "attributes": [],
            "methods": [
                "+ get_recomendaciones(id_cliente)",
                "+ get_prendas_afines(id_cat)",
                "+ registrar_preferencia(id_cli, datos)"
            ]
        },
        # 3. Service: Recomendacion_Service
        {
            "id": "srv_recomendacion",
            "x": 630,
            "y": 325,
            "width": 275,
            "header": ["Recomendacion_Service"],
            "attributes": [],
            "methods": [
                "+ generar_recomendaciones_cliente()",
                "+ calcular_scoring_tendencias()",
                "+ asociar_descuentos_vigentes()",
                "+ validar_stock_disponible()"
            ]
        },
        # 4. Repository: Recomendacion_Repository
        {
            "id": "repo_recomendacion",
            "x": 945,
            "y": 325,
            "width": 275,
            "header": ["Recomendacion_Repository"],
            "attributes": [],
            "methods": [
                "+ find_recomendaciones_cliente(id_cli)",
                "+ find_preferencias_cliente(id_cli)",
                "+ query_prendas_destacadas(criterios)",
                "+ find_promociones_prendas(ids)",
                "+ save_recomendacion(datos)"
            ]
        },
        # ==================== ENTIDADES BASE ACTUALIZADA ====================
        # 5. Entity: T_CLIENTE
        {
            "id": "cliente",
            "x": 1260,
            "y": 90,
            "width": 195,
            "header": ["T_CLIENTE"],
            "attributes": [
                "+ ID_CLIENTE",
                "+ ID_USUARIO",
                "+ CI",
                "+ FECHA_REGISTRO"
            ],
            "methods": []
        },
        # 6. Entity: T_RECOMENDACION
        {
            "id": "recomendacion",
            "x": 1260,
            "y": 285,
            "width": 205,
            "header": ["T_RECOMENDACION"],
            "attributes": [
                "+ ID_RECOMENDACION",
                "+ ID_CLIENTE",
                "+ ID_PRODUCTO",
                "+ PUNTUACION",
                "+ MOTIVO",
                "+ FECHA_RECOMENDACION"
            ],
            "methods": []
        },
        # 7. Entity: T_PREFERENCIA_CLIENTE
        {
            "id": "preferencia",
            "x": 1260,
            "y": 550,
            "width": 205,
            "header": ["T_PREFERENCIA_CLIENTE"],
            "attributes": [
                "+ ID_PREFERENCIA",
                "+ ID_CLIENTE",
                "+ ID_CATEGORIA",
                "+ ID_TALLA",
                "+ ID_COLOR",
                "+ TIPO_PREFERENCIA"
            ],
            "methods": []
        },
        # 8. Entity: T_PRODUCTO
        {
            "id": "producto",
            "x": 1520,
            "y": 230,
            "width": 210,
            "header": ["T_PRODUCTO"],
            "attributes": [
                "+ ID_PRODUCTO",
                "+ ID_CATEGORIA",
                "+ CODIGO_PRODUCTO",
                "+ NOMBRE",
                "+ DESCRIPCION",
                "+ MARCA",
                "+ GENERO",
                "+ PRECIO",
                "+ IMAGEN_URL",
                "+ ESTADO",
                "+ FECHA_REGISTRO"
            ],
            "methods": []
        },
        # 9. Entity: T_CATEGORIA
        {
            "id": "categoria",
            "x": 1520,
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
        # 10. Entity: T_PROMOCION_PRODUCTO
        {
            "id": "promo_prod",
            "x": 1785,
            "y": 250,
            "width": 215,
            "header": ["T_PROMOCION_PRODUCTO"],
            "attributes": [
                "+ ID_PROMOCION_PRODUCTO",
                "+ ID_PROMOCION",
                "+ ID_PRODUCTO",
                "+ PORCENTAJE_DESCUENTO"
            ],
            "methods": []
        },
        # 11. Entity: T_PROMOCION
        {
            "id": "promocion",
            "x": 1785,
            "y": 480,
            "width": 215,
            "header": ["T_PROMOCION"],
            "attributes": [
                "+ ID_PROMOCION",
                "+ NOMBRE",
                "+ DESCRIPCION",
                "+ FECHA_INICIO",
                "+ FECHA_FIN",
                "+ ESTADO"
            ],
            "methods": []
        }
    ],
    "connections": [
        # Form -> Controller
        {"points": [(295, 410), (335, 410)]},
        # Controller -> Service
        {"points": [(590, 410), (630, 410)]},
        # Service -> Repository
        {"points": [(905, 410), (945, 410)]},
        # Repository -> T_RECOMENDACION
        {"points": [(1220, 410), (1260, 410)]},

        # T_CLIENTE (1) -> T_RECOMENDACION (0..*)
        {
            "points": [(1360, 220), (1360, 285)],
            "mult_from": {"text": "1", "pos": (1370, 235)},
            "mult_to": {"text": "0..*", "pos": (1370, 275)}
        },
        # T_RECOMENDACION (1) -> T_PREFERENCIA_CLIENTE (0..*) [por ID_CLIENTE compartido]
        {
            "points": [(1360, 475), (1360, 550)],
            "mult_from": {"text": "1", "pos": (1370, 490)},
            "mult_to": {"text": "0..*", "pos": (1370, 540)}
        },
        # T_RECOMENDACION (0..*) -> T_PRODUCTO (1)
        {
            "points": [(1465, 380), (1520, 380)],
            "mult_from": {"text": "0..*", "pos": (1472, 370)},
            "mult_to": {"text": "1", "pos": (1502, 370)}
        },
        # T_CATEGORIA (1) -> T_PRODUCTO (0..*)
        {
            "points": [(1617, 195), (1617, 230)],
            "mult_from": {"text": "1", "pos": (1625, 208)},
            "mult_to": {"text": "0..*", "pos": (1625, 225)}
        },
        # T_PRODUCTO (1) -> T_PROMOCION_PRODUCTO (0..*)
        {
            "points": [(1730, 335), (1785, 335)],
            "mult_from": {"text": "1", "pos": (1736, 325)},
            "mult_to": {"text": "0..*", "pos": (1760, 325)}
        },
        # T_PROMOCION (1) -> T_PROMOCION_PRODUCTO (0..*)
        {
            "points": [(1892, 480), (1892, 385)],
            "mult_from": {"text": "1", "pos": (1900, 465)},
            "mult_to": {"text": "0..*", "pos": (1900, 400)}
        },
        # T_CATEGORIA (1) -> T_PREFERENCIA_CLIENTE (0..*)
        {
            "points": [(1520, 140), (1490, 140), (1490, 640), (1465, 640)],
            "mult_from": {"text": "1", "pos": (1497, 132)},
            "mult_to": {"text": "0..*", "pos": (1472, 630)}
        }
    ]
}

def main():
    output_dir = "docs/diagramas_analisis_clases"
    brain_dir = r"C:\Users\eddym\.gemini\antigravity-ide\brain\bce20c4d-ff88-4ad8-93ad-540bb85f5c37"

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(brain_dir, exist_ok=True)

    file_base = "CU_W12_Obtener_Recomendaciones_Productos_Clases"
    svg_file = os.path.join(output_dir, f"{file_base}.svg")
    png_file = os.path.join(output_dir, f"{file_base}.png")

    svg_code = render_diagram_svg(CU12_DIAGRAM_CONFIG)

    with open(svg_file, "w", encoding="utf-8") as f:
        f.write(svg_code)

    # Renderizar PNG 2x con resvg_py
    png_data = resvg_py.svg_to_bytes(svg_code)
    with open(png_file, "wb") as f:
        f.write(png_data)

    # Copiar al directorio de artefactos del brain
    brain_png = os.path.join(brain_dir, os.path.basename(png_file))
    brain_svg = os.path.join(brain_dir, os.path.basename(svg_file))
    shutil.copy(png_file, brain_png)
    shutil.copy(svg_file, brain_svg)

    print("[OK] Diagrama de Analisis de Clases CU/W12 regenerado con exito")
    print(f"SVG: {svg_file}")
    print(f"PNG: {png_file}")

if __name__ == "__main__":
    main()
