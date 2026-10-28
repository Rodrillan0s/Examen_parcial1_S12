#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo base de renderizado para Diagramas de Análisis de Clases UML (ICONIX VOPC).
Genera archivos SVG vectoriales de alta precisión y PNG (2x) mediante resvg_py.
"""

import os
import resvg_py

def escape_xml(text):
    if text is None:
        return ""
    return (str(text).replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
                     .replace('"', "&quot;")
                     .replace("'", "&apos;"))

def calculate_class_dimensions(cls):
    """Calcula alturas exactas para los 3 compartimentos de la clase UML."""
    header_lines = cls.get("header", [])
    attrs = cls.get("attributes", [])
    methods = cls.get("methods", [])

    line_h = 16
    pad_y = 8

    h_header = max(34, len(header_lines) * line_h + pad_y * 2)
    h_attrs = max(24, len(attrs) * line_h + pad_y * 1.5) if attrs else 22
    h_methods = max(24, len(methods) * line_h + pad_y * 1.5) if methods else 22

    total_h = int(h_header + h_attrs + h_methods)
    return h_header, h_attrs, h_methods, total_h

def render_class_box(cls):
    """
    Renderiza una caja de clase UML con 3 compartimentos:
    1. Header (Nombre / Estereotipo, centrado)
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

    h_header, h_attrs, h_methods, total_h = calculate_class_dimensions(cls)

    parts = []
    parts.append(f'  <!-- Clase: {" / ".join(header_lines)} -->\n')
    parts.append(f'  <g id="class_{cls["id"]}">\n')
    
    # Rectángulo contenedor exterior
    parts.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{total_h}" fill="#ffffff" stroke="#000000" stroke-width="1.6"/>\n')

    # Divisor 1: Header -> Atributos
    y_div1 = y + h_header
    parts.append(f'    <line x1="{x}" y1="{y_div1}" x2="{x + w}" y2="{y_div1}" stroke="#000000" stroke-width="1.2"/>\n')

    # Divisor 2: Atributos -> Métodos
    y_div2 = y_div1 + h_attrs
    parts.append(f'    <line x1="{x}" y1="{y_div2}" x2="{x + w}" y2="{y_div2}" stroke="#000000" stroke-width="1.2"/>\n')

    # Texto Header (Centrado)
    if len(header_lines) == 1:
        parts.append(f'    <text x="{x + w/2}" y="{y + h_header/2 + 5}" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#000000" font-family="Arial, Helvetica, sans-serif">{escape_xml(header_lines[0])}</text>\n')
    elif len(header_lines) == 2:
        parts.append(f'    <text x="{x + w/2}" y="{y + 17}" text-anchor="middle" font-size="11" font-weight="bold" fill="#334155" font-family="Arial, Helvetica, sans-serif">{escape_xml(header_lines[0])}</text>\n')
        parts.append(f'    <text x="{x + w/2}" y="{y + 34}" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#000000" font-family="Arial, Helvetica, sans-serif">{escape_xml(header_lines[1])}</text>\n')
    else:
        for idx, line in enumerate(header_lines):
            parts.append(f'    <text x="{x + w/2}" y="{y + 16 + idx * 16}" text-anchor="middle" font-size="12" font-weight="bold" fill="#000000" font-family="Arial, Helvetica, sans-serif">{escape_xml(line)}</text>\n')

    # Texto Atributos (Alineado izquierda, margen 10px)
    y_attr_text = y_div1 + 16
    for idx, attr in enumerate(attrs):
        parts.append(f'    <text x="{x + 10}" y="{y_attr_text + idx * line_h}" font-size="11" fill="#000000" font-family="monospace, Courier New, sans-serif">{escape_xml(attr)}</text>\n')

    # Texto Métodos (Alineado izquierda, margen 10px)
    y_method_text = y_div2 + 16
    for idx, mth in enumerate(methods):
        parts.append(f'    <text x="{x + 10}" y="{y_method_text + idx * line_h}" font-size="11" fill="#000000" font-family="monospace, Courier New, sans-serif">{escape_xml(mth)}</text>\n')

    parts.append('  </g>\n')
    return "".join(parts), total_h

def resolve_connection(conn, class_map):
    """
    Resuelve puntos ortogonales y posiciones de multiplicidad
    conectando exactamente al perímetro exterior de las clases.
    """
    if "points" in conn:
        return conn["points"], conn.get("mult_from"), conn.get("mult_to"), conn.get("label")

    from_id = conn["from"]
    to_id = conn["to"]
    c1 = class_map[from_id]
    c2 = class_map[to_id]

    from_side = conn.get("from_side")
    to_side = conn.get("to_side")

    # Detección inteligente de lados si no están especificados
    if not from_side or not to_side:
        if c2["x"] >= c1["x"] + c1["w"] - 20:
            from_side = "right"
            to_side = "left"
        elif c2["y"] >= c1["y"] + c1["h"] - 20:
            from_side = "bottom"
            to_side = "top"
        elif c2["y"] + c2["h"] <= c1["y"] + 20:
            from_side = "top"
            to_side = "bottom"
        else:
            from_side = "left"
            to_side = "right"

    # Coordenadas según el lado
    if from_side == "right":
        p1 = (c1["x"] + c1["w"], c1["y"] + c1["h"] / 2)
    elif from_side == "left":
        p1 = (c1["x"], c1["y"] + c1["h"] / 2)
    elif from_side == "bottom":
        p1 = (c1["x"] + c1["w"] / 2, c1["y"] + c1["h"])
    elif from_side == "top":
        p1 = (c1["x"] + c1["w"] / 2, c1["y"])

    if to_side == "right":
        p2 = (c2["x"] + c2["w"], c2["y"] + c2["h"] / 2)
    elif to_side == "left":
        p2 = (c2["x"], c2["y"] + c2["h"] / 2)
    elif to_side == "bottom":
        p2 = (c2["x"] + c2["w"] / 2, c2["y"] + c2["h"])
    elif to_side == "top":
        p2 = (c2["x"] + c2["w"] / 2, c2["y"])

    pts = []
    # Routing ortogonal
    if from_side in ["right", "left"] and to_side in ["left", "right"]:
        if abs(p1[1] - p2[1]) > 5:
            mid_x = round((p1[0] + p2[0]) / 2)
            pts = [p1, (mid_x, p1[1]), (mid_x, p2[1]), p2]
        else:
            pts = [p1, p2]
    elif from_side in ["bottom", "top"] and to_side in ["top", "bottom"]:
        if abs(p1[0] - p2[0]) > 5:
            mid_y = round((p1[1] + p2[1]) / 2)
            pts = [p1, (p1[0], mid_y), (p2[0], mid_y), p2]
        else:
            pts = [p1, p2]
    else:
        # Lados mixtos (ej. right a top, etc.)
        if from_side == "right":
            pts = [p1, (p2[0], p1[1]), p2]
        elif from_side == "bottom":
            pts = [p1, (p1[0], p2[1]), p2]
        else:
            pts = [p1, p2]

    # Posicionamiento de multiplicidades
    mult_from = None
    if "mult_from" in conn and conn["mult_from"]:
        text = conn["mult_from"]
        if from_side == "right":
            pos = (p1[0] + 8, p1[1] - 6)
        elif from_side == "left":
            pos = (p1[0] - 25, p1[1] - 6)
        elif from_side == "bottom":
            pos = (p1[0] + 8, p1[1] + 16)
        else: # top
            pos = (p1[0] + 8, p1[1] - 8)
        mult_from = {"text": text, "pos": pos}

    mult_to = None
    if "mult_to" in conn and conn["mult_to"]:
        text = conn["mult_to"]
        if to_side == "left":
            pos = (p2[0] - 25, p2[1] - 6)
        elif to_side == "right":
            pos = (p2[0] + 8, p2[1] - 6)
        elif to_side == "top":
            pos = (p2[0] + 8, p2[1] - 8)
        else: # bottom
            pos = (p2[0] + 8, p2[1] + 16)
        mult_to = {"text": text, "pos": pos}

    label = None
    if "label" in conn and conn["label"]:
        text = conn["label"]
        mid_pt = pts[len(pts) // 2]
        pos = (mid_pt[0] - 15, mid_pt[1] - 6)
        label = {"text": text, "pos": pos}

    return pts, mult_from, mult_to, label

def render_diagram_svg(diag):
    width = diag.get("width", 1400)
    height = diag.get("height", 880)

    # 1. Mapear dimensiones de cada clase
    class_map = {}
    for cls in diag["classes"]:
        _, _, _, th = calculate_class_dimensions(cls)
        class_map[cls["id"]] = {
            "x": cls["x"],
            "y": cls["y"],
            "w": cls["width"],
            "h": th
        }

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <!-- Encabezado del Diagrama -->
  <text x="35" y="34" font-size="16" font-weight="bold" fill="#0f172a">{escape_xml(diag["title"])}</text>
  <text x="35" y="54" font-size="12" font-weight="500" fill="#475569">{escape_xml(diag["subtitle"])}</text>
  <text x="35" y="72" font-size="11.5" font-weight="bold" fill="#1e293b">Actor(es): <tspan font-weight="normal" fill="#334155">{escape_xml(diag["actors"])}</tspan></text>
  <line x1="35" y1="82" x2="{width - 35}" y2="82" stroke="#94a3b8" stroke-width="1.2"/>

  <!-- Leyenda de Estructura ICONIX -->
  <g transform="translate({width - 430}, 24)">
    <rect x="0" y="0" width="395" height="48" rx="4" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="12" y="19" font-size="11" font-weight="bold" fill="#1e293b">Estructura del Análisis de Clases (ICONIX):</text>
    <text x="12" y="36" font-size="10.5" fill="#475569">Boundary (Form) ── Control (Lógica) ── Entity (Persistencia)</text>
  </g>
''')

    # Renderizar Cajas de Clases
    for cls in diag["classes"]:
        cls_svg, _ = render_class_box(cls)
        svg_parts.append(cls_svg)

    # Renderizar Conexiones y Multiplicidades
    svg_parts.append('\n  <!-- Asociaciones y Multiplicidades -->\n  <g id="associations">\n')
    for conn in diag.get("connections", []):
        pts, mult_from, mult_to, label = resolve_connection(conn, class_map)
        pts_str = " ".join([f"{p[0]},{p[1]}" for p in pts])
        stroke_color = conn.get("color", "#000000")
        stroke_width = conn.get("width", 1.4)
        dash_style = f' stroke-dasharray="{conn["dashed"]}"' if "dashed" in conn else ""
        svg_parts.append(f'    <polyline points="{pts_str}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_width}" stroke-linejoin="round"{dash_style}/>\n')

        # Multiplicidad Origen
        if mult_from:
            mx, my = mult_from["pos"]
            txt = mult_from["text"]
            svg_parts.append(f'    <text x="{mx}" y="{my}" font-size="11" font-weight="bold" fill="#000000">{escape_xml(txt)}</text>\n')

        # Multiplicidad Destino
        if mult_to:
            mx, my = mult_to["pos"]
            txt = mult_to["text"]
            svg_parts.append(f'    <text x="{mx}" y="{my}" font-size="11" font-weight="bold" fill="#000000">{escape_xml(txt)}</text>\n')

        # Etiqueta opcional en la línea de conexión
        if label:
            lx, ly = label["pos"]
            txt = label["text"]
            svg_parts.append(f'    <text x="{lx}" y="{ly}" font-size="10" font-style="italic" fill="#334155">{escape_xml(txt)}</text>\n')

    svg_parts.append('  </g>\n')
    svg_parts.append('</svg>\n')
    return "".join(svg_parts)
