#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Diagramas de Comunicación UML para el Sistema Aura Store (SI2)
Cumple con:
1. Icono UML Control estricto (flecha curva circular adherida a la circunferencia).
2. Icono UML Boundary (barra vertical + enlace horizontal + círculo).
3. Estereotipo UML Entity (círculo con línea plana de base '○_').
4. Entidades de base de datos reales y específicas del modelo.
5. Tipografía y espaciado calibrado para evitar solapamientos.
6. Exportación vectorial SVG y renderizado PNG de alta resolución (2x) con resvg_py.
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

def draw_ctrl(cx_val, cy, r, name):
    escaped_name = escape_xml(name)
    if len(name) > 12 and "_" in name:
        parts = name.split("_")
        line1 = "_".join(parts[:-1]) + "_"
        line2 = parts[-1]
        name_svg = f'<text x="{cx_val}" y="{cy - 4}" text-anchor="middle" font-size="11" font-weight="600">{escape_xml(line1)}</text><text x="{cx_val}" y="{cy + 10}" text-anchor="middle" font-size="11" font-weight="600">{escape_xml(line2)}</text>'
    else:
        name_svg = f'<text x="{cx_val}" y="{cy + 4}" text-anchor="middle" font-size="11.5" font-weight="600">{escaped_name}</text>'
    return f'''  <!-- Controller: {escaped_name} -->
  <g>
    <circle cx="{cx_val}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <!-- Flecha circular del estándar UML Robustness adherida a la circunferencia -->
    <path d="M {cx_val + 18} {cy - r + 4} A {r + 4} {r + 4} 0 0 0 {cx_val - 6} {cy - r - 1}" fill="none" stroke="#111827" stroke-width="1.8"/>
    <path d="M {cx_val + 6} {cy - r - 10} L {cx_val - 6} {cy - r - 1} L {cx_val + 4} {cy - r + 8}" fill="none" stroke="#111827" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    {name_svg}
  </g>\n'''

def draw_boundary(cx_val, cy, r, name):
    escaped_name = escape_xml(name)
    if "_" in name:
        parts = name.split("_")
        line1 = parts[0] + "_"
        line2 = "_".join(parts[1:])
        font_size = 9.5 if len(line2) > 12 else 11
        name_svg = f'<text x="{cx_val}" y="{cy - 4}" text-anchor="middle" font-size="{font_size}" font-weight="600">{escape_xml(line1)}</text><text x="{cx_val}" y="{cy + 10}" text-anchor="middle" font-size="{font_size}" font-weight="600">{escape_xml(line2)}</text>'
    else:
        font_size = 10 if len(name) > 12 else 11.5
        name_svg = f'<text x="{cx_val}" y="{cy + 4}" text-anchor="middle" font-size="{font_size}" font-weight="600">{escaped_name}</text>'
    return f'''  <!-- 2. Boundary -->
  <g id="boundary">
    <line x1="{cx_val - r - 14}" y1="{cy - 34}" x2="{cx_val - r - 14}" y2="{cy + 34}" stroke="#111827" stroke-width="2.2"/>
    <line x1="{cx_val - r - 14}" y1="{cy}" x2="{cx_val - r}" y2="{cy}" stroke="#111827" stroke-width="2.0"/>
    <circle cx="{cx_val}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    {name_svg}
  </g>\n'''

def format_entity_text(name, x, y):
    if len(name) > 13 and "_" in name:
        parts = name.split("_")
        mid = 2 if len(parts) >= 3 else 1
        line1 = "_".join(parts[:mid]) + "_"
        line2 = "_".join(parts[mid:])
        return f'<text x="{x}" y="{y - 4}" text-anchor="middle" font-size="10.5" font-weight="bold">{escape_xml(line1)}</text><text x="{x}" y="{y + 11}" text-anchor="middle" font-size="10.5" font-weight="bold">{escape_xml(line2)}</text>'
    else:
        return f'<text x="{x}" y="{y + 5}" text-anchor="middle" font-size="12" font-weight="bold">{escape_xml(name)}</text>'

def generate_communication_svg(config):
    entities = config.get("entities", [])
    num_entities = len(entities)
    
    if num_entities <= 1:
        height = 430
        cy = 215
    elif num_entities == 2:
        height = 510
        cy = 255
    else:
        height = 600
        cy = 300
        
    width = 2420
    r = 46

    x_nodes = [120, 460, 840, 1220, 1600]
    e_x = 2140

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif;">
  <defs>
    <!-- Flecha continua negra a la derecha -->
    <marker id="arrow-solid-right" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#111827"/>
    </marker>
    <!-- Flecha abierta punteada a la izquierda -->
    <marker id="arrow-open-left" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto">
      <path d="M 2 1.5 L 8 5 L 2 8.5" fill="none" stroke="#111827" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- Lineas guía -->
  <line x1="{x_nodes[0]}" y1="20" x2="{x_nodes[0]}" y2="{height-20}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="{x_nodes[1] - r - 14}" y1="20" x2="{x_nodes[1] - r - 14}" y2="{height-20}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="{e_x}" y1="20" x2="{e_x}" y2="{height-20}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="20" y1="{cy + 46}" x2="{width - 20}" y2="{cy + 46}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
''')

    # 1. Actor to Boundary
    f_msg1 = config.get("msg_1_1", ["1.1: Solicitar operación()"])
    r_msg1 = config.get("msg_ret_actor", "1.ret: notificar confirmación()")
    svg_parts.append(f'''  <!-- 1. Actor to Boundary -->
  <line x1="{x_nodes[0] + 18}" y1="{cy}" x2="{x_nodes[1] - r - 14}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[0] + 18 + x_nodes[1] - r - 14)/2}" y="{cy - 22}" text-anchor="middle" font-size="11.5" font-weight="500">{escape_xml(f_msg1[0])}</text>
  <text x="{(x_nodes[0] + 18 + x_nodes[1] - r - 14)/2}" y="{cy - 8}" text-anchor="middle" font-size="11.5" font-weight="500">{escape_xml(f_msg1[1] if len(f_msg1) > 1 else "")}</text>
  
  <line x1="{x_nodes[1] - r - 24}" y1="{cy + 36}" x2="{x_nodes[0] + 28}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[0] + 18 + x_nodes[1] - r - 14)/2}" y="{cy + 26}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(r_msg1)}</text>
''')

    # 2. Boundary to Route
    f_msg2 = config.get("msg_1_2", ["1.2: enviar datos con Bearer Token()"])
    r_msg2 = config.get("msg_ret_boundary", "1.ret: renderizar datos en pantalla()")
    svg_parts.append(f'''  <!-- 2. Boundary to Route -->
  <line x1="{x_nodes[1] + r}" y1="{cy}" x2="{x_nodes[2] - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[1] + r + x_nodes[2] - r)/2}" y="{cy - 22}" text-anchor="middle" font-size="11.5" font-weight="500">{escape_xml(f_msg2[0])}</text>
  <text x="{(x_nodes[1] + r + x_nodes[2] - r)/2}" y="{cy - 8}" text-anchor="middle" font-size="11.5" font-weight="500">{escape_xml(f_msg2[1] if len(f_msg2) > 1 else "")}</text>
  
  <line x1="{x_nodes[2] - r - 10}" y1="{cy + 36}" x2="{x_nodes[1] + r + 10}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[1] + r + x_nodes[2] - r)/2}" y="{cy + 26}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(r_msg2)}</text>
''')

    # 3. Route to Service
    f_msg3 = config.get("msg_1_3", ["1.3: procesar_peticion()"])
    r_msg3 = config.get("msg_ret_route", "1.ret: responder HTTP 200 OK()")
    svg_parts.append(f'''  <!-- 3. Route to Service -->
  <line x1="{x_nodes[2] + r}" y1="{cy}" x2="{x_nodes[3] - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[2] + r + x_nodes[3] - r)/2}" y="{cy - 22}" text-anchor="middle" font-size="11.5" font-weight="500">{escape_xml(f_msg3[0])}</text>
  <text x="{(x_nodes[2] + r + x_nodes[3] - r)/2}" y="{cy - 8}" text-anchor="middle" font-size="11.5" font-weight="500">{escape_xml(f_msg3[1] if len(f_msg3) > 1 else "")}</text>
  
  <line x1="{x_nodes[3] - r - 10}" y1="{cy + 36}" x2="{x_nodes[2] + r + 10}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[2] + r + x_nodes[3] - r)/2}" y="{cy + 26}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(r_msg3)}</text>
''')

    # 4. Service to Repo
    f_msg4 = config.get("msg_1_4", ["1.4: validar reglas y permisos()"])
    r_msg4 = config.get("msg_ret_service", "1.ret: retornar datos estructurados()")
    svg_parts.append(f'''  <!-- 4. Service to Repo -->
  <line x1="{x_nodes[3] + r}" y1="{cy}" x2="{x_nodes[4] - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[3] + r + x_nodes[4] - r)/2}" y="{cy - 22}" text-anchor="middle" font-size="11.5" font-weight="500">{escape_xml(f_msg4[0])}</text>
  <text x="{(x_nodes[3] + r + x_nodes[4] - r)/2}" y="{cy - 8}" text-anchor="middle" font-size="11.5" font-weight="500">{escape_xml(f_msg4[1] if len(f_msg4) > 1 else "")}</text>
  
  <line x1="{x_nodes[4] - r - 10}" y1="{cy + 36}" x2="{x_nodes[3] + r + 10}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[3] + r + x_nodes[4] - r)/2}" y="{cy + 26}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(r_msg4)}</text>
''')

    # ==================== ENTIDADES (1, 2 o 3) ====================
    if num_entities == 1:
        e = entities[0]
        ey = cy
        f_e = e.get("forward", "1.5: consultar datos()")
        r_e = e.get("return", "1.6: retornar registros()")
        text_svg = format_entity_text(e['name'], e_x, ey)
        svg_parts.append(f'''  <!-- Conexión Repo a Entidad Única -->
  <line x1="{x_nodes[4] + r}" y1="{cy}" x2="{e_x - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + r + e_x - r)/2}" y="{cy - 12}" text-anchor="middle" font-size="11.5" font-weight="500">{escape_xml(f_e)}</text>
  <line x1="{e_x - r - 10}" y1="{cy + 36}" x2="{x_nodes[4] + r + 10}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + r + e_x - r)/2}" y="{cy + 26}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(r_e)}</text>

  <!-- Entidad Única -->
  <g>
    <circle cx="{e_x}" cy="{ey}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{e_x - 32}" y1="{ey + r + 3}" x2="{e_x + 32}" y2="{ey + r + 3}" stroke="#111827" stroke-width="2.2"/>
    {text_svg}
  </g>
''')
    elif num_entities == 2:
        e1, e2 = entities[0], entities[1]
        e1_y = cy - 85
        e2_y = cy + 85
        t1_svg = format_entity_text(e1['name'], e_x, e1_y)
        t2_svg = format_entity_text(e2['name'], e_x, e2_y)
        
        svg_parts.append(f'''  <!-- Conexiones a 2 Entidades -->
  <!-- Entidad 1 -->
  <line x1="{x_nodes[4] + 32}" y1="{cy - 25}" x2="{e_x - r}" y2="{e1_y + 15}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + 32 + e_x - r)/2 + 15}" y="{(cy - 25 + e1_y + 15)/2 - 16}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(e1.get('forward', ''))}</text>
  <line x1="{e_x - r - 15}" y1="{e1_y + 36}" x2="{x_nodes[4] + 38}" y2="{cy - 6}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + 38 + e_x - r - 15)/2 + 15}" y="{(cy - 6 + e1_y + 36)/2 + 20}" text-anchor="middle" font-size="10.5" font-weight="500">{escape_xml(e1.get('return', ''))}</text>

  <!-- Entidad 2 -->
  <line x1="{x_nodes[4] + 32}" y1="{cy + 25}" x2="{e_x - r}" y2="{e2_y - 15}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + 32 + e_x - r)/2 + 15}" y="{(cy + 25 + e2_y - 15)/2 - 14}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(e2.get('forward', ''))}</text>
  <line x1="{e_x - r - 15}" y1="{e2_y + 15}" x2="{x_nodes[4] + 38}" y2="{cy + 45}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + 38 + e_x - r - 15)/2 + 15}" y="{(cy + 45 + e2_y + 15)/2 + 18}" text-anchor="middle" font-size="10.5" font-weight="500">{escape_xml(e2.get('return', ''))}</text>

  <!-- G Entidad 1 -->
  <g>
    <circle cx="{e_x}" cy="{e1_y}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{e_x - 32}" y1="{e1_y + r + 3}" x2="{e_x + 32}" y2="{e1_y + r + 3}" stroke="#111827" stroke-width="2.2"/>
    {t1_svg}
  </g>

  <!-- G Entidad 2 -->
  <g>
    <circle cx="{e_x}" cy="{e2_y}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{e_x - 32}" y1="{e2_y + r + 3}" x2="{e_x + 32}" y2="{e2_y + r + 3}" stroke="#111827" stroke-width="2.2"/>
    {t2_svg}
  </g>
''')
    else:
        # 3 Entidades
        e1, e2, e3 = entities[0], entities[1], entities[2]
        e1_y = cy - 150
        e2_y = cy
        e3_y = cy + 150
        t1_svg = format_entity_text(e1['name'], e_x, e1_y)
        t2_svg = format_entity_text(e2['name'], e_x, e2_y)
        t3_svg = format_entity_text(e3['name'], e_x, e3_y)
        
        svg_parts.append(f'''  <!-- Conexiones a 3 Entidades -->
  <!-- Entidad 1 (Arriba) -->
  <line x1="{x_nodes[4] + 32}" y1="{cy - 38}" x2="{e_x - r}" y2="{e1_y + 12}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + 32 + e_x - r)/2 + 20}" y="{(cy - 38 + e1_y + 12)/2 - 16}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(e1.get('forward', ''))}</text>
  <line x1="{e_x - r - 15}" y1="{e1_y + 36}" x2="{x_nodes[4] + 38}" y2="{cy - 12}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + 38 + e_x - r - 15)/2 + 20}" y="{(cy - 12 + e1_y + 36)/2 + 22}" text-anchor="middle" font-size="10.5" font-weight="500">{escape_xml(e1.get('return', ''))}</text>

  <!-- Entidad 2 (Centro) -->
  <line x1="{x_nodes[4] + r}" y1="{cy}" x2="{e_x - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + r + e_x - r)/2}" y="{cy - 12}" text-anchor="middle" font-size="11.5" font-weight="500">{escape_xml(e2.get('forward', ''))}</text>
  <line x1="{e_x - r - 10}" y1="{cy + 36}" x2="{x_nodes[4] + r + 10}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + r + e_x - r)/2}" y="{cy + 26}" text-anchor="middle" font-size="10.5" font-weight="500">{escape_xml(e2.get('return', ''))}</text>

  <!-- Entidad 3 (Abajo) -->
  <line x1="{x_nodes[4] + 32}" y1="{cy + 38}" x2="{e_x - r}" y2="{e3_y - 12}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + 32 + e_x - r)/2 + 20}" y="{(cy + 38 + e3_y - 12)/2 - 14}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(e3.get('forward', ''))}</text>
  <line x1="{e_x - r - 15}" y1="{e3_y + 14}" x2="{x_nodes[4] + 38}" y2="{cy + 64}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + 38 + e_x - r - 15)/2 + 20}" y="{(cy + 64 + e3_y + 14)/2 + 20}" text-anchor="middle" font-size="10.5" font-weight="500">{escape_xml(e3.get('return', ''))}</text>

  <!-- G Entidad 1 -->
  <g>
    <circle cx="{e_x}" cy="{e1_y}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{e_x - 32}" y1="{e1_y + r + 3}" x2="{e_x + 32}" y2="{e1_y + r + 3}" stroke="#111827" stroke-width="2.2"/>
    {t1_svg}
  </g>

  <!-- G Entidad 2 -->
  <g>
    <circle cx="{e_x}" cy="{e2_y}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{e_x - 32}" y1="{e2_y + r + 3}" x2="{e_x + 32}" y2="{e2_y + r + 3}" stroke="#111827" stroke-width="2.2"/>
    {t2_svg}
  </g>

  <!-- G Entidad 3 -->
  <g>
    <circle cx="{e_x}" cy="{e3_y}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{e_x - 32}" y1="{e3_y + r + 3}" x2="{e_x + 32}" y2="{e3_y + r + 3}" stroke="#111827" stroke-width="2.2"/>
    {t3_svg}
  </g>
''')

    # ==================== NODOS ====================
    # 1. Actor
    actor_label = config.get("actor_name", "USUARIO")
    svg_parts.append(f'''  <!-- 1. Actor -->
  <g id="actor">
    <circle cx="{x_nodes[0]}" cy="{cy - 36}" r="13" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{x_nodes[0]}" y1="{cy - 23}" x2="{x_nodes[0]}" y2="{cy + 14}" stroke="#111827" stroke-width="1.8"/>
    <line x1="{x_nodes[0] - 18}" y1="{cy - 12}" x2="{x_nodes[0] + 18}" y2="{cy - 12}" stroke="#111827" stroke-width="1.8"/>
    <line x1="{x_nodes[0]}" y1="{cy + 14}" x2="{x_nodes[0] - 14}" y2="{cy + 42}" stroke="#111827" stroke-width="1.8"/>
    <line x1="{x_nodes[0]}" y1="{cy + 14}" x2="{x_nodes[0] + 14}" y2="{cy + 42}" stroke="#111827" stroke-width="1.8"/>
    <text x="{x_nodes[0]}" y="{cy + 62}" text-anchor="middle" font-size="11.5" font-weight="bold">{escape_xml(actor_label)}</text>
  </g>
''')

    # 2. Boundary
    svg_parts.append(draw_boundary(x_nodes[1], cy, r, config.get("boundary_name", "IU_Boundary")))

    # 3, 4, 5 Controllers
    svg_parts.append(draw_ctrl(x_nodes[2], cy, r, config.get("route_name", "app_routes")))
    svg_parts.append(draw_ctrl(x_nodes[3], cy, r, config.get("service_name", "app_services")))
    svg_parts.append(draw_ctrl(x_nodes[4], cy, r, config.get("repo_name", "app_repos")))

    # Título superior
    title = config.get("title", "")
    svg_parts.append(f'  <text x="30" y="35" font-size="14" font-weight="bold" fill="#475569">{escape_xml(title)}</text>\n')
    svg_parts.append('</svg>\n')
    return "".join(svg_parts)

# ==================== CONFIGURACIÓN DEL PRIMER CASO DE USO ====================
CU_W12_CONFIG = {
    "id": "CU_W12",
    "file_name": "CU_W12_Obtener_Recomendaciones_Productos.svg",
    "title": "CU/W12: Obtener recomendaciones de productos (Moda & Colecciones Afines)",
    "actor_name": "CLIENTE / VISITANTE",
    "boundary_name": "IU_Recomendaciones",
    "route_name": "catalogo_routes",
    "service_name": "catalogo_services",
    "repo_name": "catalogo_repos",
    "msg_1_1": [
        "1.1: Explorar prendas sugeridas, tendencias",
        "y colecciones recomendadas de moda()"
    ],
    "msg_1_2": [
        "1.2: GET /api/catalogo/productos?orden=destacados",
        "con id_empresa, temporada y categoria()"
    ],
    "msg_1_3": [
        "1.3: obtener_catalogo_recomendado()",
        "calculando scoring de popularidad y tendencias"
    ],
    "msg_1_4": [
        "1.4: procesar consulta con ranking de ventas,",
        "promociones vigentes y stock disponible()"
    ],
    "msg_ret_service": "1.11: retornar lista jerarquizada con prendas recomendadas()",
    "msg_ret_route": "1.12: responder HTTP 200 con sugerencias y afinidad de moda()",
    "msg_ret_boundary": "1.13: renderizar grilla 'Recomendados para Ti' con badges()",
    "msg_ret_actor": "1.14: visualizar prendas sugeridas según tendencias()",
    "entities": [
        {
            "name": "t_producto",
            "forward": "1.5: SELECT prendas activas con fotos y categorización",
            "return": "1.6: retornar prendas aptas para sugerencia"
        },
        {
            "name": "t_detalle_pedido",
            "forward": "1.7: SELECT prendas con mayor volumen de compra e historial",
            "return": "1.8: retornar rankings de ventas y co-ocurrencia"
        },
        {
            "name": "t_promocion_producto",
            "forward": "1.9: SELECT descuentos y ofertas activas asociadas a prendas",
            "return": "1.10: retornar precios rebajados y vigencia de promo"
        }
    ]
}

def main():
    output_dir = "docs/diagramas_comunicacion"
    brain_dir = r"C:\Users\eddym\.gemini\antigravity-ide\brain\bce20c4d-ff88-4ad8-93ad-540bb85f5c37"
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(brain_dir, exist_ok=True)

    svg_code = generate_communication_svg(CU_W12_CONFIG)
    svg_file = os.path.join(output_dir, CU_W12_CONFIG["file_name"])
    png_file = os.path.join(output_dir, CU_W12_CONFIG["file_name"].replace(".svg", ".png"))

    with open(svg_file, "w", encoding="utf-8") as f:
        f.write(svg_code)

    # Renderizar PNG en alta resolución (2x) con resvg_py
    png_data = resvg_py.svg_to_bytes(svg_code)
    with open(png_file, "wb") as f:
        f.write(png_data)

    # Copiar al directorio de artefactos
    brain_png = os.path.join(brain_dir, os.path.basename(png_file))
    brain_svg = os.path.join(brain_dir, os.path.basename(svg_file))
    shutil.copy(png_file, brain_png)
    shutil.copy(svg_file, brain_svg)

    print("[OK] CU/W12 generado con exito")
    print(f"SVG: {svg_file}")
    print(f"PNG: {png_file}")

if __name__ == "__main__":
    main()
