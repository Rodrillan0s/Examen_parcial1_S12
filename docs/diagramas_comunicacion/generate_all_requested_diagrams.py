#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro Completo de Diagramas de Comunicación UML / Robustez (SI2)
Genera los 25 Casos de Uso (17 Web + 8 Mobile) con:
1. Icono UML Control estricto (flecha circular en la circunferencia, sin pelo de Homero).
2. Estereotipo UML Entity (○_) para entidades de base de datos individuales y reales.
3. Inclusión de t_bitacora para auditoría en casos transaccionales.
4. Soporte multi-entidad (1, 2 o 3 entidades organizadas limpiamente).
5. Renderizado en SVG vectorial y PNG de alta resolución (2x).
"""

import os
import cairosvg
import shutil

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
    if len(name) > 13 and "_" in name:
        parts = name.split("_")
        line1 = parts[0] + "_"
        line2 = "_".join(parts[1:])
        name_svg = f'<text x="{cx_val}" y="{cy - 4}" text-anchor="middle" font-size="11" font-weight="600">{escape_xml(line1)}</text><text x="{cx_val}" y="{cy + 10}" text-anchor="middle" font-size="11" font-weight="600">{escape_xml(line2)}</text>'
    else:
        name_svg = f'<text x="{cx_val}" y="{cy + 4}" text-anchor="middle" font-size="11.5" font-weight="600">{escaped_name}</text>'
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
    
    # Altura y coordenadas según la cantidad de entidades
    if num_entities <= 1:
        height = 430
        cy = 215
    elif num_entities == 2:
        height = 510
        cy = 255
    else: # 3 o más
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
  <text x="{(x_nodes[4] + 32 + e_x - r)/2 + 15}" y="{(cy - 25 + e1_y + 15)/2 - 14}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(e1.get('forward', ''))}</text>
  <line x1="{e_x - r - 15}" y1="{e1_y + 36}" x2="{x_nodes[4] + 38}" y2="{cy - 6}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + 38 + e_x - r - 15)/2 + 15}" y="{(cy - 6 + e1_y + 36)/2 + 18}" text-anchor="middle" font-size="10.5" font-weight="500">{escape_xml(e1.get('return', ''))}</text>

  <!-- Entidad 2 -->
  <line x1="{x_nodes[4] + 32}" y1="{cy + 25}" x2="{e_x - r}" y2="{e2_y - 15}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + 32 + e_x - r)/2 + 15}" y="{(cy + 25 + e2_y - 15)/2 - 12}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(e2.get('forward', ''))}</text>
  <line x1="{e_x - r - 15}" y1="{e2_y + 15}" x2="{x_nodes[4] + 38}" y2="{cy + 45}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + 38 + e_x - r - 15)/2 + 15}" y="{(cy + 45 + e2_y + 15)/2 + 16}" text-anchor="middle" font-size="10.5" font-weight="500">{escape_xml(e2.get('return', ''))}</text>

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
  <text x="{(x_nodes[4] + 32 + e_x - r)/2 + 20}" y="{(cy - 38 + e1_y + 12)/2 - 14}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(e1.get('forward', ''))}</text>
  <line x1="{e_x - r - 15}" y1="{e1_y + 36}" x2="{x_nodes[4] + 38}" y2="{cy - 12}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + 38 + e_x - r - 15)/2 + 20}" y="{(cy - 12 + e1_y + 36)/2 + 18}" text-anchor="middle" font-size="10.5" font-weight="500">{escape_xml(e1.get('return', ''))}</text>

  <!-- Entidad 2 (Centro) -->
  <line x1="{x_nodes[4] + r}" y1="{cy}" x2="{e_x - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + r + e_x - r)/2}" y="{cy - 12}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(e2.get('forward', ''))}</text>
  <line x1="{e_x - r - 10}" y1="{cy + 36}" x2="{x_nodes[4] + r + 10}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + r + e_x - r)/2}" y="{cy + 26}" text-anchor="middle" font-size="10.5" font-weight="500">{escape_xml(e2.get('return', ''))}</text>

  <!-- Entidad 3 (Abajo) -->
  <line x1="{x_nodes[4] + 32}" y1="{cy + 38}" x2="{e_x - r}" y2="{e3_y - 12}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + 32 + e_x - r)/2 + 20}" y="{(cy + 38 + e3_y - 12)/2 - 12}" text-anchor="middle" font-size="11" font-weight="500">{escape_xml(e3.get('forward', ''))}</text>
  <line x1="{e_x - r - 15}" y1="{e3_y + 14}" x2="{x_nodes[4] + 38}" y2="{cy + 64}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + 38 + e_x - r - 15)/2 + 20}" y="{(cy + 64 + e3_y + 14)/2 + 18}" text-anchor="middle" font-size="10.5" font-weight="500">{escape_xml(e3.get('return', ''))}</text>

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

    # Controllers
    svg_parts.append(draw_ctrl(x_nodes[2], cy, r, config.get("route_name", "app_routes")))
    svg_parts.append(draw_ctrl(x_nodes[3], cy, r, config.get("service_name", "app_services")))
    svg_parts.append(draw_ctrl(x_nodes[4], cy, r, config.get("repo_name", "app_repos")))

    # Título superior
    title = config.get("title", "")
    svg_parts.append(f'  <text x="30" y="35" font-size="14" font-weight="bold" fill="#475569">{escape_xml(title)}</text>\n')
    svg_parts.append('</svg>\n')
    return "".join(svg_parts)

# ==================== CONFIGURACIÓN DE LOS 25 CASOS DE USO ====================
ALL_REQUESTED_CUS = [
    # ------------------- WEB -------------------
    # 1. W05: Buscar y filtrar productos
    {
        "id": "CU_W05",
        "file_name": "CU_W05_Buscar_Filtrar_Productos.svg",
        "title": "CU/W05: Buscar y filtrar productos",
        "actor_name": "CLIENTE / ADMIN / CAJERO",
        "boundary_name": "IU_CatalogoPrendas",
        "route_name": "catalogo_routes",
        "service_name": "catalogo_services",
        "repo_name": "catalogo_repos",
        "msg_1_1": ["1.1: Ingresar texto de búsqueda,", "categoría y filtros de moda()"],
        "msg_1_2": ["1.2: GET /api/catalogo con query params", "filtros (talla, color, rango_precio)()"],
        "msg_1_3": ["1.3: listar_catalogo_filtrado(filtros)", "aplicando aislamiento tenant"],
        "msg_1_4": ["1.4: construir query con JOINs de", "variantes, stock y atributos()"],
        "msg_ret_service": "1.9: retornar catálogo estructurado con stock disponible()",
        "msg_ret_route": "1.10: responder HTTP 200 con prendas y metadatos()",
        "msg_ret_boundary": "1.11: renderizar grilla dinámica de productos()",
        "msg_ret_actor": "1.12: visualizar catálogo filtrado()",
        "entities": [
            {"name": "t_producto", "forward": "1.5: SELECT prendas activas por tenant", "return": "1.6: devolver tuplas de productos"},
            {"name": "t_variante_producto", "forward": "1.7: SELECT variantes, tallas y colores", "return": "1.8: devolver atributos y precios"}
        ]
    },

    # 2. W06: Consultar detalle de producto
    {
        "id": "CU_W06",
        "file_name": "CU_W06_Consultar_Detalle_Producto.svg",
        "title": "CU/W06: Consultar detalle de producto",
        "actor_name": "CLIENTE / ADMIN / CAJERO",
        "boundary_name": "IU_DetalleProducto",
        "route_name": "catalogo_routes",
        "service_name": "catalogo_services",
        "repo_name": "catalogo_repos",
        "msg_1_1": ["1.1: Seleccionar tarjeta de prenda", "para ver especificaciones()"],
        "msg_1_2": ["1.2: GET /api/catalogo/producto/{slug_o_id}", "con token opcional()"],
        "msg_1_3": ["1.3: obtener_detalle_producto_completo()", "validando estado activo"],
        "msg_1_4": ["1.4: consultar producto con galería,", "variantes y guía de tallas()"],
        "msg_ret_service": "1.9: armar payload enriquecido con galería y variantes()",
        "msg_ret_route": "1.10: responder HTTP 200 con detalle de prenda()",
        "msg_ret_boundary": "1.11: presentar ficha técnica, fotos y selector de talla()",
        "msg_ret_actor": "1.12: visualizar detalle de prenda()",
        "entities": [
            {"name": "t_producto", "forward": "1.5: consultar producto y especificaciones", "return": "1.6: retornar datos base y descripción"},
            {"name": "t_foto_producto", "forward": "1.7: consultar galería multimedia Cloudinary", "return": "1.8: retornar URLs de imágenes HD"}
        ]
    },

    # 3. W07: Consultar disponibilidad por sucursal
    {
        "id": "CU_W07",
        "file_name": "CU_W07_Consultar_Disponibilidad_Sucursal.svg",
        "title": "CU/W07: Consultar disponibilidad por sucursal",
        "actor_name": "CLIENTE / ADMIN / ENCARGADO",
        "boundary_name": "IU_DisponibilidadSucursal",
        "route_name": "inventario_routes",
        "service_name": "inventario_services",
        "repo_name": "inventario_repos",
        "msg_1_1": ["1.1: Seleccionar variante y", "consultar tiendas físicas()"],
        "msg_1_2": ["1.2: GET /api/inventario/disponibilidad", "con id_variante e id_ciudad()"],
        "msg_1_3": ["1.3: consultar_stock_sucursales(variante)", "calculando stock disponible"],
        "msg_1_4": ["1.4: verificar existencia física", "menos reservas activas()"],
        "msg_ret_service": "1.9: consolidar mapa de disponibilidad por tienda()",
        "msg_ret_route": "1.10: responder HTTP 200 con sucursales y stock()",
        "msg_ret_boundary": "1.11: mostrar lista de tiendas con indicador de stock()",
        "msg_ret_actor": "1.12: visualizar tiendas con stock disponible()",
        "entities": [
            {"name": "t_inventario", "forward": "1.5: SELECT stock_actual, stock_reservado", "return": "1.6: retornar unidades físicas y reservadas"},
            {"name": "t_sucursal", "forward": "1.7: consultar datos de sucursal y dirección", "return": "1.8: retornar nombre, ciudad y coordenadas"}
        ]
    },

    # 4. W08: Gestionar carrito de compras
    {
        "id": "CU_W08",
        "file_name": "CU_W08_Gestionar_Carrito_Compras.svg",
        "title": "CU/W08: Gestionar carrito de compras",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_CarritoCompras",
        "route_name": "carrito_routes",
        "service_name": "carrito_services",
        "repo_name": "carrito_repos",
        "msg_1_1": ["1.1: Agregar prenda, modificar cantidad", "o eliminar ítem del carrito()"],
        "msg_1_2": ["1.2: POST/PUT/DELETE /api/carrito/items", "con id_variante y cantidad()"],
        "msg_1_3": ["1.3: gestionar_item_carrito(usuario, item)", "verificando disponibilidad"],
        "msg_1_4": ["1.4: comprobar que cantidad solicitada", "<= stock_disponible en tienda()"],
        "msg_ret_service": "1.9: recalcular subtotales, descuentos y total()",
        "msg_ret_route": "1.10: responder HTTP 200 con carrito actualizado()",
        "msg_ret_boundary": "1.11: actualizar drawer del carrito y badge()",
        "msg_ret_actor": "1.12: confirmar actualización de bolsa de compras()",
        "entities": [
            {"name": "t_carrito", "forward": "1.5: consultar o crear t_carrito activo", "return": "1.6: retornar ID de carrito de usuario"},
            {"name": "t_detalle_carrito", "forward": "1.7: INSERT / UPDATE / DELETE ítem", "return": "1.8: confirmar persistencia de líneas"}
        ]
    },

    # 5. W09: Realizar compra
    {
        "id": "CU_W09",
        "file_name": "CU_W09_Realizar_Compra.svg",
        "title": "CU/W09: Realizar compra (Checkout y Pedido)",
        "actor_name": "CLIENTE / SISTEMA_PAGOS",
        "boundary_name": "IU_CheckoutWeb",
        "route_name": "pedido_routes",
        "service_name": "pedido_services",
        "repo_name": "pedido_repos",
        "msg_1_1": ["1.1: Confirmar entrega (envío/retiro),", "datos de facturación y pagar()"],
        "msg_1_2": ["1.2: POST /api/pedidos/crear con", "items, método de pago y dirección()"],
        "msg_1_3": ["1.3: registrar_pedido_transaccional()", "con validación atómica de stock"],
        "msg_1_4": ["1.4: reservar/descontar stock de inventario", "y crear cabecera de pedido()"],
        "msg_ret_service": "1.11: confirmar creación de orden con código seguimiento()",
        "msg_ret_route": "1.12: responder HTTP 201 Created con orden confirmada()",
        "msg_ret_boundary": "1.13: mostrar pantalla de confirmación y comprobante()",
        "msg_ret_actor": "1.14: recibir confirmación de pedido y tracking()",
        "entities": [
            {"name": "t_pedido", "forward": "1.5: INSERT cabecera pedido (PENDIENTE/PAGADO)", "return": "1.6: retornar id_pedido y número orden"},
            {"name": "t_detalle_pedido", "forward": "1.7: INSERT líneas de ítems con precio unitario", "return": "1.8: confirmar persistencia de detalles"},
            {"name": "t_bitacora", "forward": "1.9: registrar evento 'COMPRA_WEB' en auditoría", "return": "1.10: confirmar trazabilidad"}
        ]
    },

    # 6. W10: Gestionar reservas
    {
        "id": "CU_W10",
        "file_name": "CU_W10_Gestionar_Reservas.svg",
        "title": "CU/W10: Gestionar reservas (Apartado en Tienda)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_ReservasWeb",
        "route_name": "reserva_routes",
        "service_name": "reserva_services",
        "repo_name": "reserva_repos",
        "msg_1_1": ["1.1: Seleccionar prenda para apartar", "en tienda física por 48 horas()"],
        "msg_1_2": ["1.2: POST /api/reservas con id_variante,", "sucursal y tiempo de expiración()"],
        "msg_1_3": ["1.3: registrar_reserva_prenda()", "validando límite de reservas por cliente"],
        "msg_1_4": ["1.4: bloquear unidades en t_inventario", "incrementando stock_reservado()"],
        "msg_ret_service": "1.11: retornar reserva confirmada con código QR retiro()",
        "msg_ret_route": "1.12: responder HTTP 201 con ticket de reserva()",
        "msg_ret_boundary": "1.13: renderizar comprobante de apartado y QR()",
        "msg_ret_actor": "1.14: confirmar reserva activa para retiro en tienda()",
        "entities": [
            {"name": "t_reserva", "forward": "1.5: INSERT en t_reserva (estado PENDIENTE)", "return": "1.6: retornar id_reserva y fecha_vencimiento"},
            {"name": "t_detalle_reserva", "forward": "1.7: INSERT prendas y variantes apartadas", "return": "1.8: confirmar persistencia de ítems"},
            {"name": "t_inventario", "forward": "1.9: UPDATE stock_reservado = stock_reservado + N", "return": "1.10: confirmar bloqueo de stock"}
        ]
    },

    # 7. W11: Consultar pedidos e historial de compras
    {
        "id": "CU_W11",
        "file_name": "CU_W11_Consultar_Pedidos_Historial.svg",
        "title": "CU/W11: Consultar pedidos e historial de compras",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_HistorialCompras",
        "route_name": "pedido_routes",
        "service_name": "pedido_services",
        "repo_name": "pedido_repos",
        "msg_1_1": ["1.1: Acceder a 'Mis Pedidos' y", "filtrar por fecha o estado()"],
        "msg_1_2": ["1.2: GET /api/pedidos/mis-pedidos", "con JWT autenticado()"],
        "msg_1_3": ["1.3: listar_pedidos_cliente(id_usuario)", "con estado de entrega y tracking"],
        "msg_1_4": ["1.4: consultar pedidos, líneas de compra", "y pagos asociados()"],
        "msg_ret_service": "1.9: armar listado con tracking y comprobantes()",
        "msg_ret_route": "1.10: responder HTTP 200 con historial de compras()",
        "msg_ret_boundary": "1.11: mostrar tarjetas de pedidos con timeline de estado()",
        "msg_ret_actor": "1.12: visualizar pedidos pasados y activos()",
        "entities": [
            {"name": "t_pedido", "forward": "1.5: SELECT pedidos por id_usuario", "return": "1.6: retornar cabeceras y totales"},
            {"name": "t_detalle_pedido", "forward": "1.7: SELECT prendas, tallas y fotos de la orden", "return": "1.8: retornar detalle de prendas compradas"}
        ]
    },

    # 8. W20: Gestionar temporadas y colecciones
    {
        "id": "CU_W20",
        "file_name": "CU_W20_Gestionar_Temporadas_Colecciones.svg",
        "title": "CU/W20: Gestionar temporadas y colecciones",
        "actor_name": "ADMINISTRADOR / ADMIN_TIENDA",
        "boundary_name": "IU_TemporadasColecciones",
        "route_name": "productos_routes",
        "service_name": "productos_services",
        "repo_name": "productos_repos",
        "msg_1_1": ["1.1: Crear/editar temporada (Primavera-Verano)", "o colección de moda (Cápsula Urbana)()"],
        "msg_1_2": ["1.3: POST/PUT /api/temporadas y /colecciones", "con vigencia, descripción y tenant()"],
        "msg_1_3": ["1.3: registrar_temporada_coleccion()", "validando fechas y catálogo de prendas"],
        "msg_1_4": ["1.4: persistir temporada/colección y", "asociar prendas del catálogo()"],
        "msg_ret_service": "1.11: retornar colección configurada y activa()",
        "msg_ret_route": "1.12: responder HTTP 201/200 con entidad guardada()",
        "msg_ret_boundary": "1.13: actualizar catálogo de colecciones y filtros()",
        "msg_ret_actor": "1.14: confirmar colección de moda disponible()",
        "entities": [
            {"name": "t_temporada", "forward": "1.5: INSERT / UPDATE en t_temporada", "return": "1.6: retornar id_temporada y vigencia"},
            {"name": "t_coleccion", "forward": "1.7: INSERT / UPDATE en t_coleccion", "return": "1.8: retornar id_coleccion asociada"},
            {"name": "t_bitacora", "forward": "1.9: auditar 'GESTION_COLECCION' en t_bitacora", "return": "1.10: confirmar trazabilidad"}
        ]
    },

    # 9. W21: Gestionar proveedores
    {
        "id": "CU_W21",
        "file_name": "CU_W21_Gestionar_Proveedores.svg",
        "title": "CU/W21: Gestionar proveedores (Talleres y Confección)",
        "actor_name": "ADMINISTRADOR / ADMIN_TIENDA",
        "boundary_name": "IU_Proveedores",
        "route_name": "productos_routes",
        "service_name": "productos_services",
        "repo_name": "productos_repos",
        "msg_1_1": ["1.1: Ingresar razón social, NIT, contacto", "y rubro de confección textil()"],
        "msg_1_2": ["1.2: POST /api/proveedores con datos", "fiscales y credenciales de contacto()"],
        "msg_1_3": ["1.3: registrar_proveedor_textil()", "validando unicidad de NIT por tenant"],
        "msg_1_4": ["1.4: persistir datos de proveedor y", "asociar a materias primas/prendas()"],
        "msg_ret_service": "1.9: retornar ficha de proveedor registrada()",
        "msg_ret_route": "1.10: responder HTTP 201 Created con ID de proveedor()",
        "msg_ret_boundary": "1.11: actualizar directorio de proveedores textiles()",
        "msg_ret_actor": "1.12: notificar proveedor registrado exitosamente()",
        "entities": [
            {"name": "t_proveedor", "forward": "1.5: INSERT / UPDATE en t_proveedor", "return": "1.6: retornar id_proveedor confirmado"},
            {"name": "t_bitacora", "forward": "1.7: registrar evento 'PROVEEDOR_CREADO' en auditoría", "return": "1.8: confirmar registro en bitácora"}
        ]
    },

    # 10. W22: Gestionar inventario (Ya validado con 3 entidades)
    {
        "id": "CU_W22",
        "file_name": "CU_W22_Gestionar_Inventario.svg",
        "title": "CU/W22: Gestionar inventario (Entradas, Salidas y Ajustes)",
        "actor_name": "ADMIN / ENCARGADO_SUCURSAL",
        "boundary_name": "IU_Inventario",
        "route_name": "inventario_routes",
        "service_name": "inventario_services",
        "repo_name": "inventario_repos",
        "msg_1_1": ["1.1: Consultar stock / registrar", "entrada, salida o ajuste()"],
        "msg_1_2": ["1.2: enviar tipo (ENTRADA/SALIDA/AJUSTE),", "sucursal, variante y cantidad()"],
        "msg_1_3": ["1.3: procesar_movimiento_inventario()", "con validación de permisos tenant"],
        "msg_1_4": ["1.4: validar stock disponible >= salida", "y ajuste >= stock_reservado()"],
        "msg_ret_service": "1.11: retornar balances de stock actualizados()",
        "msg_ret_route": "1.12: responder HTTP 200 OK con stock nuevo()",
        "msg_ret_boundary": "1.13: actualizar grilla de stock y alertas()",
        "msg_ret_actor": "1.14: notificar resultado de operación()",
        "entities": [
            {"name": "t_inventario", "forward": "1.5: fn_movimiento_inventario() FOR UPDATE (modificar stock)", "return": "1.6: confirmar stock nuevo (actual y disponible)"},
            {"name": "t_movimiento_inventario", "forward": "1.7: insertar en t_movimiento (ENTRADA / SALIDA / AJUSTE)", "return": "1.8: confirmar registro de movimiento histórico"},
            {"name": "t_bitacora", "forward": "1.9: registrar_evento_db() auditoría de inventario", "return": "1.10: confirmar persistencia en t_bitacora"}
        ]
    },

    # 11. W23: Gestionar disponibilidad de prendas
    {
        "id": "CU_W23",
        "file_name": "CU_W23_Gestionar_Disponibilidad_Prendas.svg",
        "title": "CU/W23: Gestionar disponibilidad de prendas",
        "actor_name": "ADMIN / ENCARGADO_SUCURSAL",
        "boundary_name": "IU_DisponibilidadPrendas",
        "route_name": "inventario_routes",
        "service_name": "inventario_services",
        "repo_name": "inventario_repos",
        "msg_1_1": ["1.1: Habilitar/deshabilitar disponibilidad", "de prenda para venta web o tienda()"],
        "msg_1_2": ["1.2: PUT /api/inventario/visibilidad con", "id_variante, estado y umbral mínimo()"],
        "msg_1_3": ["1.3: actualizar_estado_disponibilidad()", "evaluando reglas de umbral de stock"],
        "msg_1_4": ["1.4: modificar flags activo/visible y", "actualizar caché de catálogo público()"],
        "msg_ret_service": "1.11: confirmar nuevo estado de disponibilidad()",
        "msg_ret_route": "1.12: responder HTTP 200 con estado actualizado()",
        "msg_ret_boundary": "1.13: refrescar switches de visibilidad en grilla()",
        "msg_ret_actor": "1.14: confirmar disponibilidad actualizada()",
        "entities": [
            {"name": "t_inventario", "forward": "1.5: UPDATE estado_disponible en t_inventario", "return": "1.6: confirmar cambio en existencias"},
            {"name": "t_variante_producto", "forward": "1.7: UPDATE estado activo en variante de prenda", "return": "1.8: confirmar persistencia de estado"},
            {"name": "t_bitacora", "forward": "1.9: registrar 'CAMBIO_DISPONIBILIDAD' en auditoría", "return": "1.10: confirmar auditoría en t_bitacora"}
        ]
    },

    # 12. W24: Registrar venta presencial
    {
        "id": "CU_W24",
        "file_name": "CU_W24_Registrar_Venta_Presencial.svg",
        "title": "CU/W24: Registrar venta presencial (POS Caja)",
        "actor_name": "CAJERO",
        "boundary_name": "IU_POSCaja",
        "route_name": "pos_routes",
        "service_name": "pos_services",
        "repo_name": "pos_repos",
        "msg_1_1": ["1.1: Escanear código de barras de prendas,", "seleccionar cliente y crear venta()"],
        "msg_1_2": ["1.2: POST /api/pos/venta con id_sucursal,", "items (variante, qty, precio) y cliente()"],
        "msg_1_3": ["1.3: registrar_venta_presencial()", "verificando sesión de caja abierta activa"],
        "msg_1_4": ["1.4: descontar stock físico en sucursal", "y persistir venta con estado PENDIENTE_PAGO()"],
        "msg_ret_service": "1.11: retornar id_venta y resumen para cobro inmediato()",
        "msg_ret_route": "1.12: responder HTTP 201 con venta generada()",
        "msg_ret_boundary": "1.13: mostrar venta en panel de cobro inmediato()",
        "msg_ret_actor": "1.14: proceder al cobro de la venta (W28)()",
        "entities": [
            {"name": "t_venta", "forward": "1.5: INSERT cabecera de venta en t_venta", "return": "1.6: retornar id_venta generado"},
            {"name": "t_detalle_venta", "forward": "1.7: INSERT líneas de prendas y precios finales", "return": "1.8: confirmar líneas registradas"},
            {"name": "t_inventario", "forward": "1.9: UPDATE descontar stock_actual en sucursal", "return": "1.10: confirmar salida física de mercadería"}
        ]
    },

    # 13. W25: Atender reservas
    {
        "id": "CU_W25",
        "file_name": "CU_W25_Atender_Reservas.svg",
        "title": "CU/W25: Atender reservas (Entrega en Tienda Física)",
        "actor_name": "ENCARGADO_SUCURSAL / CAJERO",
        "boundary_name": "IU_AtencionReservas",
        "route_name": "reserva_routes",
        "service_name": "reserva_services",
        "repo_name": "reserva_repos",
        "msg_1_1": ["1.1: Escanear código QR o buscar reserva", "del cliente para concretar entrega()"],
        "msg_1_2": ["1.2: POST /api/reservas/{id}/atender", "validando vigencia de 48 horas()"],
        "msg_1_3": ["1.3: procesar_entrega_reserva()", "liberando stock reservado para venta"],
        "msg_1_4": ["1.4: transformar reserva en venta presencial", "o anular por expiración de plazo()"],
        "msg_ret_service": "1.11: retornar estado 'ATENDIDA' y generar venta POS()",
        "msg_ret_route": "1.12: responder HTTP 200 con venta lista para cobrar()",
        "msg_ret_boundary": "1.13: cargar ítems reservados directamente al POS()",
        "msg_ret_actor": "1.14: entregar prendas y cobrar al cliente()",
        "entities": [
            {"name": "t_reserva", "forward": "1.5: UPDATE estado = 'ATENDIDA' en t_reserva", "return": "1.6: confirmar reserva consumida"},
            {"name": "t_inventario", "forward": "1.7: descontar stock_reservado de la prenda", "return": "1.8: confirmar balance de reservas en tienda"},
            {"name": "t_bitacora", "forward": "1.9: auditar 'ENTREGA_RESERVA' en t_bitacora", "return": "1.10: confirmar trazabilidad"}
        ]
    },

    # 14. W26: Mostrar ubicaciones de sucursales
    {
        "id": "CU_W26",
        "file_name": "CU_W26_Mostrar_Ubicaciones_Sucursales.svg",
        "title": "CU/W26: Mostrar ubicaciones de sucursales (Mapa Interactivo)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_MapaTiendas",
        "route_name": "sucursales_routes",
        "service_name": "sucursales_services",
        "repo_name": "sucursales_repos",
        "msg_1_1": ["1.1: Abrir vista de tiendas físicas y", "filtrar por ciudad geográfica()"],
        "msg_1_2": ["1.2: GET /api/sucursales con coordenadas,", "horarios de atención y teléfonos()"],
        "msg_1_3": ["1.3: listar_sucursales_activas()", "agrupadas por departamento y ciudad"],
        "msg_1_4": ["1.4: consultar tiendas activas con", "latitud, longitud y ciudad asociada()"],
        "msg_ret_service": "1.9: estructurar lista con pines geoespaciales()",
        "msg_ret_route": "1.10: responder HTTP 200 con sucursales y ubicaciones()",
        "msg_ret_boundary": "1.11: renderizar mapa interactivo con pines y detalles()",
        "msg_ret_actor": "1.12: visualizar tiendas físicas y cómo llegar()",
        "entities": [
            {"name": "t_sucursal", "forward": "1.5: SELECT sucursales activas con lat/lng", "return": "1.6: retornar datos de tienda y horarios"},
            {"name": "t_ciudad", "forward": "1.7: SELECT ciudades (Santa Cruz, La Paz, Cbba)", "return": "1.8: retornar nombres de departamentos"}
        ]
    },

    # 15. W27: Procesar pago electrónico
    {
        "id": "CU_W27",
        "file_name": "CU_W27_Procesar_Pago_Electronico.svg",
        "title": "CU/W27: Procesar pago electrónico (Pasarela Web / QR)",
        "actor_name": "CLIENTE / PASARELA_PAGO",
        "boundary_name": "IU_PasarelaPago",
        "route_name": "pago_routes",
        "service_name": "pago_services",
        "repo_name": "pago_repos",
        "msg_1_1": ["1.1: Seleccionar pago por Tarjeta / QR,", "ingresar datos y autorizar cobro()"],
        "msg_1_2": ["1.2: POST /api/pagos/procesar con id_pedido,", "método (TARJETA/QR) y token pasarela()"],
        "msg_1_3": ["1.3: procesar_pago_electronico()", "conectando con pasarela bancaria externa"],
        "msg_1_4": ["1.4: registrar transacción en t_pago", "y cambiar estado de pedido a 'PAGADO'()"],
        "msg_ret_service": "1.11: confirmar pago exitoso con código autorización()",
        "msg_ret_route": "1.12: responder HTTP 200 OK con recibo digital()",
        "msg_ret_boundary": "1.13: mostrar pantalla de pago exitoso y comprobante()",
        "msg_ret_actor": "1.14: recibir notificación de cobro aprobado()",
        "entities": [
            {"name": "t_pago", "forward": "1.5: INSERT registro de pago en t_pago (APROBADO)", "return": "1.6: retornar id_pago y fecha transacción"},
            {"name": "t_pedido", "forward": "1.7: UPDATE estado = 'PAGADO' en t_pedido", "return": "1.8: confirmar pedido listo para despacho"},
            {"name": "t_bitacora", "forward": "1.9: registrar evento 'PAGO_ELECTRONICO_EXITOSO'", "return": "1.10: confirmar auditoría de pago"}
        ]
    },

    # 16. W28: Procesar pago en caja
    {
        "id": "CU_W28",
        "file_name": "CU_W28_Procesar_Pago_Caja.svg",
        "title": "CU/W28: Procesar pago en caja (Control de Efectivo por Denominaciones)",
        "actor_name": "CAJERO",
        "boundary_name": "IU_CobroCaja",
        "route_name": "caja_pago_routes",
        "service_name": "caja_pago_services",
        "repo_name": "caja_pago_repos",
        "msg_1_1": ["1.1: Registrar billetes/monedas recibidos,", "calcular cambio óptimo y confirmar cobro()"],
        "msg_1_2": ["1.2: POST /api/caja/pago con id_venta,", "desglose_recibido y desglose_cambio()"],
        "msg_1_3": ["1.3: ejecutar_pago_caja() asociando", "sesión de caja abierta del cajero"],
        "msg_1_4": ["1.4: registrar pago en t_pago y desglosar", "entradas y salidas de efectivo por billete()"],
        "msg_ret_service": "1.11: confirmar venta pagada con desglose de vuelto()",
        "msg_ret_route": "1.12: responder HTTP 200 con comprobante térmico()",
        "msg_ret_boundary": "1.13: renderizar ticket de venta y cambio a entregar()",
        "msg_ret_actor": "1.14: entregar cambio exacto y ticket al cliente()",
        "entities": [
            {"name": "t_pago", "forward": "1.5: INSERT en t_pago con id_venta y monto", "return": "1.6: retornar id_pago confirmado"},
            {"name": "t_pago_denominacion", "forward": "1.7: INSERT ENTRADA_EFECTIVO y SALIDA_CAMBIO", "return": "1.8: confirmar arqueo físico de caja"},
            {"name": "t_venta", "forward": "1.9: UPDATE estado = 'COMPLETADA' en t_venta", "return": "1.10: confirmar venta finalizada"}
        ]
    },

    # 17. W29: Emitir comprobante de venta
    {
        "id": "CU_W29",
        "file_name": "CU_W29_Emitir_Comprobante_Venta.svg",
        "title": "CU/W29: Emitir comprobante de venta (Factura / Recibo)",
        "actor_name": "CAJERO",
        "boundary_name": "IU_ComprobanteVenta",
        "route_name": "comprobante_routes",
        "service_name": "comprobante_services",
        "repo_name": "pos_repos",
        "msg_1_1": ["1.1: Solicitar emisión de comprobante térmico", "o factura electrónica()"],
        "msg_1_2": ["1.2: POST /api/comprobantes/emitir con", "id_venta, tipo (FACTURA/RECIBO) y NIT()"],
        "msg_1_3": ["1.3: generar_comprobante_fiscal()", "con código de control y QR tributario"],
        "msg_1_4": ["1.4: consultar ítems de venta, total", "y generar numeración correlativa()"],
        "msg_ret_service": "1.11: estructurar formato térmico ESC/POS y PDF()",
        "msg_ret_route": "1.12: responder HTTP 201 con datos de comprobante()",
        "msg_ret_boundary": "1.13: enviar orden a impresora térmica e imprimir()",
        "msg_ret_actor": "1.14: entregar comprobante impreso al cliente()",
        "entities": [
            {"name": "t_comprobante", "forward": "1.5: INSERT en t_comprobante con número correlativo", "return": "1.6: retornar id_comprobante generado"},
            {"name": "t_venta", "forward": "1.7: asociar id_comprobante a la venta", "return": "1.8: confirmar venta documentada fiscalmente"},
            {"name": "t_bitacora", "forward": "1.9: registrar emisión de comprobante en auditoría", "return": "1.10: confirmar registro en bitácora"}
        ]
    },

    # ------------------- MOBILE -------------------
    # 18. M05: Buscar y filtrar productos
    {
        "id": "CU_M05",
        "file_name": "CU_M05_Buscar_Filtrar_Productos.svg",
        "title": "CU/M05: Buscar y filtrar productos (App Móvil)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_MovilCatalogo",
        "route_name": "catalogo_routes",
        "service_name": "catalogo_services",
        "repo_name": "catalogo_repos",
        "msg_1_1": ["1.1: Tocar buscador, seleccionar categoría", "y deslizar filtros táctiles()"],
        "msg_1_2": ["1.2: GET /api/catalogo desde App Móvil", "con filtros (talla, color, colección)()"],
        "msg_1_3": ["1.3: listar_catalogo_filtrado(filtros)", "con paginación móvil optimizada"],
        "msg_1_4": ["1.4: consultar prendas activas con imágenes", "optimizadas para pantalla de smartphone()"],
        "msg_ret_service": "1.9: retornar lista móvil con miniaturas WebP()",
        "msg_ret_route": "1.10: responder JSON HTTP 200 con prendas()",
        "msg_ret_boundary": "1.11: renderizar grid táctil de productos()",
        "msg_ret_actor": "1.12: explorar catálogo fluido en el celular()",
        "entities": [
            {"name": "t_producto", "forward": "1.5: SELECT prendas activas en catálogo", "return": "1.6: retornar nombres, precios y slugs"},
            {"name": "t_variante_producto", "forward": "1.7: SELECT variantes de tallas y colores", "return": "1.8: retornar códigos HEX y stock"}
        ]
    },

    # 19. M06: Consultar detalle de producto
    {
        "id": "CU_M06",
        "file_name": "CU_M06_Consultar_Detalle_Producto.svg",
        "title": "CU/M06: Consultar detalle de producto (App Móvil)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_MovilDetalle",
        "route_name": "catalogo_routes",
        "service_name": "catalogo_services",
        "repo_name": "catalogo_repos",
        "msg_1_1": ["1.1: Tocar producto en la pantalla táctil", "para ver fotos y seleccionar talla()"],
        "msg_1_2": ["1.2: GET /api/catalogo/producto/{slug}", "solicitando carrusel de imágenes()"],
        "msg_1_3": ["1.3: obtener_detalle_producto()", "con variantes de tallas y colores disponibles"],
        "msg_1_4": ["1.4: consultar información técnica, material", "y galería de fotos HD()"],
        "msg_ret_service": "1.9: formatear respuesta para carrusel móvil()",
        "msg_ret_route": "1.10: responder HTTP 200 con galería y variantes()",
        "msg_ret_boundary": "1.11: renderizar carrusel gestual y botón de compra()",
        "msg_ret_actor": "1.12: interactuar con detalle de prenda en la app()",
        "entities": [
            {"name": "t_producto", "forward": "1.5: SELECT información de prenda y composición", "return": "1.6: retornar datos de prenda"},
            {"name": "t_foto_producto", "forward": "1.7: SELECT fotos de alta resolución en Cloudinary", "return": "1.8: retornar URLs de imágenes HD"}
        ]
    },

    # 20. M07: Consultar disponibilidad por sucursal
    {
        "id": "CU_M07",
        "file_name": "CU_M07_Consultar_Disponibilidad_Sucursal.svg",
        "title": "CU/M07: Consultar disponibilidad por sucursal (App Móvil)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_MovilDisponibilidad",
        "route_name": "inventario_routes",
        "service_name": "inventario_services",
        "repo_name": "inventario_repos",
        "msg_1_1": ["1.1: Tocar 'Disponibilidad en Tiendas'", "desde la pantalla del producto()"],
        "msg_1_2": ["1.2: GET /api/inventario/disponibilidad", "con GPS móvil de cercanía()"],
        "msg_1_3": ["1.3: consultar_stock_sucursales_movil()", "ordenando tiendas por distancia GPS"],
        "msg_1_4": ["1.4: verificar existencias físicas", "menos unidades reservadas()"],
        "msg_ret_service": "1.9: retornar lista de tiendas con distancia en km()",
        "msg_ret_route": "1.10: responder HTTP 200 con stock por tienda()",
        "msg_ret_boundary": "1.11: mostrar tarjetas de sucursales con badge de stock()",
        "msg_ret_actor": "1.12: ver tiendas cercanas con stock disponible()",
        "entities": [
            {"name": "t_inventario", "forward": "1.5: SELECT stock_actual y stock_reservado", "return": "1.6: retornar existencias disponibles"},
            {"name": "t_sucursal", "forward": "1.7: SELECT sucursales con lat/lng de cercanía", "return": "1.8: retornar sucursal más próxima"}
        ]
    },

    # 21. M08: Gestionar carrito de compras
    {
        "id": "CU_M08",
        "file_name": "CU_M08_Gestionar_Carrito_Compras.svg",
        "title": "CU/M08: Gestionar carrito de compras (App Móvil)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_MovilCarrito",
        "route_name": "carrito_routes",
        "service_name": "carrito_services",
        "repo_name": "carrito_repos",
        "msg_1_1": ["1.1: Tocar 'Añadir a la bolsa', cambiar", "cantidad o deslizar para eliminar()"],
        "msg_1_2": ["1.2: POST/PUT/DELETE /api/carrito/items", "con id_variante y token JWT()"],
        "msg_1_3": ["1.3: gestionar_bolsa_compras_movil()", "verificando límites de stock"],
        "msg_1_4": ["1.4: validar stock disponible antes de", "agregar ítem al carrito del cliente()"],
        "msg_ret_service": "1.9: calcular subtotal, impuestos y total de compra()",
        "msg_ret_route": "1.10: responder HTTP 200 con bolsa actualizada()",
        "msg_ret_boundary": "1.11: animar icono de bolsa y actualizar vista()",
        "msg_ret_actor": "1.12: confirmar prendas agregadas a la bolsa()",
        "entities": [
            {"name": "t_carrito", "forward": "1.5: consultar o crear t_carrito móvil activo", "return": "1.6: retornar ID de carrito de usuario"},
            {"name": "t_detalle_carrito", "forward": "1.7: INSERT / UPDATE / DELETE líneas de bolsa", "return": "1.8: confirmar persistencia de ítems"}
        ]
    },

    # 22. M09: Realizar compra
    {
        "id": "CU_M09",
        "file_name": "CU_M09_Realizar_Compra.svg",
        "title": "CU/M09: Realizar compra (Checkout Móvil y Pago)",
        "actor_name": "CLIENTE / SISTEMA_PAGOS",
        "boundary_name": "IU_MovilCheckout",
        "route_name": "pedido_routes",
        "service_name": "pedido_services",
        "repo_name": "pedido_repos",
        "msg_1_1": ["1.1: Tocar 'Comprar Ahora', elegir", "envío o retiro y autorizar pago()"],
        "msg_1_2": ["1.2: POST /api/pedidos/crear desde móvil", "con items, método pago y dirección()"],
        "msg_1_3": ["1.3: registrar_pedido_movil() con", "reserva y descuento atómico de stock"],
        "msg_1_4": ["1.4: crear orden de compra y generar", "transacción de pago electrónico()"],
        "msg_ret_service": "1.11: confirmar orden con tracking y recibo digital()",
        "msg_ret_route": "1.12: responder HTTP 201 con pedido confirmado()",
        "msg_ret_boundary": "1.13: mostrar animación de éxito y comprobante()",
        "msg_ret_actor": "1.14: recibir confirmación de compra en el móvil()",
        "entities": [
            {"name": "t_pedido", "forward": "1.5: INSERT orden de compra en t_pedido", "return": "1.6: retornar id_pedido y número de tracking"},
            {"name": "t_detalle_pedido", "forward": "1.7: INSERT líneas de prendas compradas", "return": "1.8: confirmar ítems de la orden"},
            {"name": "t_bitacora", "forward": "1.9: registrar evento 'COMPRA_MOVIL' en auditoría", "return": "1.10: confirmar registro en bitácora"}
        ]
    },

    # 23. M10: Gestionar reservas
    {
        "id": "CU_M10",
        "file_name": "CU_M10_Gestionar_Reservas.svg",
        "title": "CU/M10: Gestionar reservas (Apartado Móvil con QR)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_MovilReservas",
        "route_name": "reserva_routes",
        "service_name": "reserva_services",
        "repo_name": "reserva_repos",
        "msg_1_1": ["1.1: Tocar 'Apartar en Tienda', elegir", "sucursal física y confirmar()"],
        "msg_1_2": ["1.2: POST /api/reservas desde móvil", "con id_variante y sucursal destino()"],
        "msg_1_3": ["1.3: registrar_reserva_movil()", "bloqueando stock por 48 horas"],
        "msg_1_4": ["1.4: incrementar stock_reservado en tienda", "y generar ticket con código QR de retiro()"],
        "msg_ret_service": "1.11: retornar ticket de reserva con código QR()",
        "msg_ret_route": "1.12: responder HTTP 201 con reserva activa()",
        "msg_ret_boundary": "1.13: guardar ticket QR en 'Mis Reservas' del móvil()",
        "msg_ret_actor": "1.14: visualizar código QR para retirar en tienda()",
        "entities": [
            {"name": "t_reserva", "forward": "1.5: INSERT reserva con código QR único", "return": "1.6: retornar id_reserva y vencimiento"},
            {"name": "t_detalle_reserva", "forward": "1.7: INSERT prendas y tallas apartadas", "return": "1.8: confirmar prendas bloqueadas"},
            {"name": "t_inventario", "forward": "1.9: UPDATE stock_reservado = stock_reservado + N", "return": "1.10: confirmar bloqueo de stock en tienda"}
        ]
    },

    # 24. M11: Consultar pedidos e historial de compras
    {
        "id": "CU_M11",
        "file_name": "CU_M11_Consultar_Pedidos_Historial.svg",
        "title": "CU/M11: Consultar pedidos e historial de compras (App Móvil)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_MovilHistorial",
        "route_name": "pedido_routes",
        "service_name": "pedido_services",
        "repo_name": "pedido_repos",
        "msg_1_1": ["1.1: Tocar pestaña 'Historial' para ver", "compras anteriores y tracking en vivo()"],
        "msg_1_2": ["1.2: GET /api/pedidos/mis-pedidos", "con token de sesión móvil()"],
        "msg_1_3": ["1.3: listar_pedidos_movil(cliente)", "con estado de entrega en tiempo real"],
        "msg_1_4": ["1.4: consultar compras, ítems, totales", "y enlaces a comprobantes digitales()"],
        "msg_ret_service": "1.9: armar tarjetas móviles con estado y fotos()",
        "msg_ret_route": "1.10: responder HTTP 200 con historial de compras()",
        "msg_ret_boundary": "1.11: presentar tarjetas de pedidos con timeline visual()",
        "msg_ret_actor": "1.12: revisar compras realizadas y estado()",
        "entities": [
            {"name": "t_pedido", "forward": "1.5: SELECT pedidos del cliente ordenados por fecha", "return": "1.6: retornar cabeceras de compras"},
            {"name": "t_detalle_pedido", "forward": "1.7: SELECT ítems de cada orden con fotos miniatura", "return": "1.8: retornar prendas compradas"}
        ]
    },

    # 25. M15: Mostrar ubicaciones de sucursales
    {
        "id": "CU_M15",
        "file_name": "CU_M15_Mostrar_Ubicaciones_Sucursales.svg",
        "title": "CU/M15: Mostrar ubicaciones de sucursales (Geolocalización Móvil)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_MovilSucursales",
        "route_name": "sucursales_routes",
        "service_name": "sucursales_services",
        "repo_name": "sucursales_repos",
        "msg_1_1": ["1.1: Tocar 'Tiendas Cercanas' y", "conceder permiso de GPS al dispositivo()"],
        "msg_1_2": ["1.2: GET /api/sucursales con latitud/longitud", "del dispositivo del cliente()"],
        "msg_1_3": ["1.3: listar_sucursales_geolocalizadas()", "calculando ruta y distancia en km"],
        "msg_1_4": ["1.4: consultar tiendas activas con dirección,", "horarios de atención y teléfono()"],
        "msg_ret_service": "1.9: ordenar tiendas de más cercana a más lejana()",
        "msg_ret_route": "1.10: responder HTTP 200 con pines de tiendas()",
        "msg_ret_boundary": "1.11: mostrar mapa nativo con pines y botón 'Cómo llegar'()",
        "msg_ret_actor": "1.12: ver ruta GPS a la tienda más cercana()",
        "entities": [
            {"name": "t_sucursal", "forward": "1.5: SELECT sucursales con coordenadas GPS", "return": "1.6: retornar latitud, longitud y dirección"},
            {"name": "t_ciudad", "forward": "1.7: SELECT ciudades y departamentos", "return": "1.8: retornar nombres de ciudades"}
        ]
    }
]

def generate_all_diagrams():
    output_dir = "docs/diagramas_comunicacion"
    brain_dir = "/home/eddy/.gemini/antigravity-ide/brain/b5ff4fcb-4250-43ad-8cb8-b6447f7c448a"
    os.makedirs(output_dir, exist_ok=True)

    print(f"🚀 Iniciando generación de los {len(ALL_REQUESTED_CUS)} diagramas de comunicación UML...")

    for i, cu in enumerate(ALL_REQUESTED_CUS, 1):
        svg_code = generate_communication_svg(cu)
        svg_file = os.path.join(output_dir, cu["file_name"])
        png_file = os.path.join(output_dir, cu["file_name"].replace(".svg", ".png"))
        
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg_code)
            
        # Renderizar en alta resolución 2x con cairosvg
        cairosvg.svg2png(url=svg_file, write_to=png_file, scale=2.0)
        
        # Copiar también al brain/artifact dir
        artifact_png = os.path.join(brain_dir, os.path.basename(png_file))
        shutil.copy(png_file, artifact_png)
        
        print(f" [{i:02d}/25] ✅ Generado: {cu['file_name']} y {os.path.basename(png_file)}")

    print(f"\n🎉 ¡Todos los 25 diagramas generados y exportados exitosamente en {output_dir}!")

if __name__ == "__main__":
    generate_all_diagrams()
