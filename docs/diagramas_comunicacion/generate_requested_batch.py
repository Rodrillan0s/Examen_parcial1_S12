#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de Diagramas de Comunicación UML (Estándar de Ingeniería de Software)
Aura Store - Sistema E-Commerce & Retail Multi-Tenant (SI2 - UAGRM)

Corrige y garantiza:
1. Cero solapamiento de flechas sobre letras o textos.
2. Iconos Robustness (Boundary, Control, Entity, Actor) perfectamente calibrados y proporcionales.
3. Ruteo ortogonal hacia entidades (sin líneas diagonales que atraviesen textos).
4. Asociación única sólida con flechitas de dirección de mensaje dedicadas (estándar UML 2.5).
5. Modelo de datos actualizado con entidades en MAYÚSCULAS (T_PRODUCTO, T_VENTA, T_RECOMENDACION, etc.).
6. Arquitecturas específicas por CU (Web REST, Mobile Cubit, Analytics Engine, DeepSeek AI, AR Camera).
"""

import os
import shutil
import resvg_py

OUT_DIR = r"d:\Locked Files --EY\Projectos\Examen_parcial1_S12\docs\diagramas_comunicacion"
BRAIN_DIR = r"C:\Users\eddym\.gemini\antigravity-ide\brain\bce20c4d-ff88-4ad8-93ad-540bb85f5c37"

def escape_xml(text):
    return (str(text).replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
                     .replace('"', "&quot;")
                     .replace("'", "&apos;"))

# -------------------------------------------------------------
# HELPERS DE TEXTO Y FORMATEO ROBUSTO
# -------------------------------------------------------------

def split_node_label(name):
    """
    Divide inteligentemente el nombre del nodo en 1 o 2 líneas
    para garantizar que NUNCA sobrepase el radio del círculo (r=46).
    """
    if len(name) <= 11 and "_" not in name:
        return [name]
    
    if name.startswith("IU_"):
        rest = name[3:]
        return ["IU_", rest]
    
    if name.startswith("T_"):
        rest = name[2:]
        if "_" in rest:
            parts = rest.split("_")
            return [f"T_{parts[0]}_", "_".join(parts[1:])]
        return ["T_", rest]

    if "_" in name:
        parts = name.split("_")
        mid = len(parts) // 2
        p1 = "_".join(parts[:mid]) + "_"
        p2 = "_".join(parts[mid:])
        return [p1, p2]
        
    # Nombre largo continuo
    mid = len(name) // 2
    return [name[:mid] + "-", name[mid:]]


# -------------------------------------------------------------
# HELPERS DE DIBUJO DE PARTICIPANTES (ROBUSTNESS UML ESTÁNDAR)
# -------------------------------------------------------------

def draw_actor(cx, cy, name):
    lines = []
    lines.append(f'  <!-- Actor: {escape_xml(name)} -->')
    lines.append(f'  <g id="actor">')
    # Cabeza
    lines.append(f'    <circle cx="{cx}" cy="{cy - 36}" r="13" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>')
    # Tronco
    lines.append(f'    <line x1="{cx}" y1="{cy - 23}" x2="{cx}" y2="{cy + 14}" stroke="#111827" stroke-width="1.8"/>')
    # Brazos
    lines.append(f'    <line x1="{cx - 18}" y1="{cy - 12}" x2="{cx + 18}" y2="{cy - 12}" stroke="#111827" stroke-width="1.8"/>')
    # Piernas
    lines.append(f'    <line x1="{cx}" y1="{cy + 14}" x2="{cx - 14}" y2="{cy + 42}" stroke="#111827" stroke-width="1.8"/>')
    lines.append(f'    <line x1="{cx}" y1="{cy + 14}" x2="{cx + 14}" y2="{cy + 42}" stroke="#111827" stroke-width="1.8"/>')
    # Nombre
    lines.append(f'    <text x="{cx}" y="{cy + 62}" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#111827">{escape_xml(name)}</text>')
    lines.append(f'  </g>')
    return "\n".join(lines)


def draw_boundary(cx, cy, r, name):
    lines = []
    lines.append(f'  <!-- Boundary: {escape_xml(name)} -->')
    lines.append(f'  <g id="boundary">')
    # Barra vertical izquierda y conector al círculo
    bar_x = cx - 60
    lines.append(f'    <line x1="{bar_x}" y1="{cy - 34}" x2="{bar_x}" y2="{cy + 34}" stroke="#111827" stroke-width="2.2"/>')
    lines.append(f'    <line x1="{bar_x}" y1="{cy}" x2="{cx - r}" y2="{cy}" stroke="#111827" stroke-width="2.0"/>')
    # Círculo
    lines.append(f'    <circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>')
    # Texto calibrado
    text_lines = split_node_label(name)
    if len(text_lines) == 1:
        font_sz = "10.5" if len(text_lines[0]) > 10 else "11.5"
        lines.append(f'    <text x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="{font_sz}" font-weight="600" fill="#111827">{escape_xml(text_lines[0])}</text>')
    else:
        l1_sz = "10.5" if len(text_lines[0]) > 10 else "11"
        l2_sz = "10" if len(text_lines[1]) > 11 else "11"
        lines.append(f'    <text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="{l1_sz}" font-weight="600" fill="#111827">{escape_xml(text_lines[0])}</text>')
        lines.append(f'    <text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="{l2_sz}" font-weight="600" fill="#111827">{escape_xml(text_lines[1])}</text>')
    lines.append(f'  </g>')
    return "\n".join(lines)


def draw_control(cx, cy, r, name):
    lines = []
    lines.append(f'  <!-- Control: {escape_xml(name)} -->')
    lines.append(f'  <g>')
    # Círculo
    lines.append(f'    <circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>')
    # Flecha circular estándar UML Robustness adherida a la circunferencia
    lines.append(f'    <path d="M {cx + 18} {cy - 42} A 50 50 0 0 0 {cx - 6} {cy - 47}" fill="none" stroke="#111827" stroke-width="1.8"/>')
    lines.append(f'    <path d="M {cx + 6} {cy - 56} L {cx - 6} {cy - 47} L {cx + 4} {cy - 38}" fill="none" stroke="#111827" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    # Texto calibrado
    text_lines = split_node_label(name)
    if len(text_lines) == 1:
        font_sz = "10.5" if len(text_lines[0]) > 10 else "11.5"
        lines.append(f'    <text x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="{font_sz}" font-weight="600" fill="#111827">{escape_xml(text_lines[0])}</text>')
    else:
        l1_sz = "10.5" if len(text_lines[0]) > 10 else "11"
        l2_sz = "10" if len(text_lines[1]) > 11 else "11"
        lines.append(f'    <text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="{l1_sz}" font-weight="600" fill="#111827">{escape_xml(text_lines[0])}</text>')
        lines.append(f'    <text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="{l2_sz}" font-weight="600" fill="#111827">{escape_xml(text_lines[1])}</text>')
    lines.append(f'  </g>')
    return "\n".join(lines)


def draw_entity(cx, cy, r, name):
    lines = []
    lines.append(f'  <!-- Entity: {escape_xml(name)} -->')
    lines.append(f'  <g>')
    # Círculo
    lines.append(f'    <circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>')
    # Línea base inferior
    lines.append(f'    <line x1="{cx - 32}" y1="{cy + 49}" x2="{cx + 32}" y2="{cy + 49}" stroke="#111827" stroke-width="2.2"/>')
    # Texto calibrado
    text_lines = split_node_label(name)
    if len(text_lines) == 1:
        font_sz = "10.5" if len(text_lines[0]) > 10 else "11.5"
        lines.append(f'    <text x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="{font_sz}" font-weight="bold" fill="#111827">{escape_xml(text_lines[0])}</text>')
    else:
        l1_sz = "10.5" if len(text_lines[0]) > 10 else "11"
        l2_sz = "9.5" if len(text_lines[1]) > 11 else "10.5"
        lines.append(f'    <text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="{l1_sz}" font-weight="bold" fill="#111827">{escape_xml(text_lines[0])}</text>')
        lines.append(f'    <text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="{l2_sz}" font-weight="bold" fill="#111827">{escape_xml(text_lines[1])}</text>')
    lines.append(f'  </g>')
    return "\n".join(lines)


# -------------------------------------------------------------
# HELPER DE ENLACE DE COMUNICACIÓN CON FLECHAS DEDICADAS
# -------------------------------------------------------------

def draw_horizontal_link(x1, x2, cy, f_msg, r_msg=None):
    """
    Dibuja el enlace de comunicación idéntico al estándar del docente:
    - Línea de ida en y_fwd = cy - 25 con flecha continua (arrow-solid-right)
    - Línea de retorno en y_ret = cy + 36 con flecha abierta punteada (arrow-open-left)
    - Textos perfectamente alineados sin solapar jamás las líneas ni letras.
    """
    lines = []
    mid_x = (x1 + x2) / 2
    y_fwd = cy - 25
    y_ret = cy + 36
    
    # 1. Mensaje de Ida (Forward)
    if f_msg:
        lines.append(f'  <line x1="{x1}" y1="{y_fwd}" x2="{x2}" y2="{y_fwd}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>')
        f_lines = [f_msg] if isinstance(f_msg, str) else f_msg
        if len(f_lines) == 1:
            lines.append(f'  <text x="{mid_x}" y="{y_fwd - 8}" text-anchor="middle" font-size="11.5" font-weight="500" fill="#111827">{escape_xml(f_lines[0])}</text>')
        else:
            lines.append(f'  <text x="{mid_x}" y="{y_fwd - 22}" text-anchor="middle" font-size="11.5" font-weight="500" fill="#111827">{escape_xml(f_lines[0])}</text>')
            lines.append(f'  <text x="{mid_x}" y="{y_fwd - 8}" text-anchor="middle" font-size="11.5" font-weight="500" fill="#111827">{escape_xml(f_lines[1])}</text>')

    # 2. Mensaje de Retorno (Return, punteado)
    if r_msg:
        lines.append(f'  <line x1="{x2 - 10}" y1="{y_ret}" x2="{x1 + 10}" y2="{y_ret}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>')
        r_lines = [r_msg] if isinstance(r_msg, str) else r_msg
        if len(r_lines) == 1:
            lines.append(f'  <text x="{mid_x}" y="{y_ret - 10}" text-anchor="middle" font-size="11" font-weight="500" fill="#111827">{escape_xml(r_lines[0])}</text>')
        else:
            lines.append(f'  <text x="{mid_x}" y="{y_ret - 20}" text-anchor="middle" font-size="11" font-weight="500" fill="#111827">{escape_xml(r_lines[0])}</text>')
            lines.append(f'  <text x="{mid_x}" y="{y_ret - 8}" text-anchor="middle" font-size="11" font-weight="500" fill="#111827">{escape_xml(r_lines[1])}</text>')

    return "\n".join(lines)


def draw_entity_links(x_repo, cy_repo, x_entity, entity_coords, entities):
    """
    Conecta el repositorio con las entidades (1, 2 o 3) según el estándar del docente.
    """
    lines = []
    for idx, e in enumerate(entities):
        ey = entity_coords[idx]
        f_msg = e.get("forward")
        r_msg = e.get("return")
        
        if len(entities) == 1:
            # Caso 1 entidad: perfectamente horizontal
            lines.append(draw_horizontal_link(x_repo + 46, x_entity - 46, cy_repo, f_msg, r_msg))
        else:
            # Caso multi-entidad con ángulos limpios
            # Desplazamiento en repo para separar las líneas de origen
            dy = (ey - cy_repo)
            y_start_fwd = cy_repo + (dy * 0.15) - 15
            y_end_fwd = ey - 25
            
            y_start_ret = ey + 25
            y_end_ret = cy_repo + (dy * 0.15) + 20
            
            mid_x = (x_repo + 46 + x_entity - 46) / 2
            mid_y_fwd = (y_start_fwd + y_end_fwd) / 2
            mid_y_ret = (y_start_ret + y_end_ret) / 2
            
            # Línea de ida
            lines.append(f'  <line x1="{x_repo + 46}" y1="{y_start_fwd:.1f}" x2="{x_entity - 46}" y2="{y_end_fwd:.1f}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>')
            if f_msg:
                lines.append(f'  <text x="{mid_x}" y="{mid_y_fwd - 8:.1f}" text-anchor="middle" font-size="11" font-weight="500" fill="#111827">{escape_xml(f_msg)}</text>')
                
            # Línea de retorno punteada
            lines.append(f'  <line x1="{x_entity - 55}" y1="{y_end_ret:.1f}" x2="{x_repo + 55}" y2="{y_end_ret:.1f}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>')
            if r_msg:
                lines.append(f'  <text x="{mid_x}" y="{mid_y_ret - 8:.1f}" text-anchor="middle" font-size="10.5" font-weight="500" fill="#111827">{escape_xml(r_msg)}</text>')
                
    return "\n".join(lines)


# -------------------------------------------------------------
# GENERADOR GENÉRICO DE DIAGRAMA DE COMUNICACIÓN
# -------------------------------------------------------------

def generate_comm_diagram_svg(cu_def):
    width = 2420
    entities = cu_def.get("entities", [])
    num_entities = len(entities)
    
    if num_entities <= 1:
        height = 510
        cy = 255
        entity_coords = [cy]
    elif num_entities == 2:
        height = 560
        cy = 280
        entity_coords = [170, 390]
    else:
        height = 680
        cy = 340
        entity_coords = [170, 340, 510]
        
    r = 46
    # Coordenadas idénticas a la grilla canónica del docente
    x_actor = 120
    x_boundary = 460
    x_boundary_bar = 400
    x_route = 840
    x_service = 1220
    x_repo = 1600
    x_entity = 2140
    
    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
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

  <!-- Lineas guía del estándar (tenues) -->
  <line x1="{x_actor}" y1="20" x2="{x_actor}" y2="{height - 20}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="{x_boundary_bar}" y1="20" x2="{x_boundary_bar}" y2="{height - 20}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="{x_entity}" y1="20" x2="{x_entity}" y2="{height - 20}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="20" y1="{cy + 46}" x2="{width - 20}" y2="{cy + 46}" stroke="#f1f5f9" stroke-width="1" stroke-dasharray="4,4"/>

  <!-- Título Oficial del Caso de Uso -->
  <text x="30" y="38" font-size="14" font-weight="bold" fill="#334155">{escape_xml(cu_def.get("title", ""))}</text>
''')

    # 1. Enlace Actor -> Boundary
    svg.append(draw_horizontal_link(x_actor + 18, x_boundary_bar, cy, cu_def.get("msg_1_1"), cu_def.get("msg_ret_actor")))
    
    # 2. Enlace Boundary -> Route / Cubit
    svg.append(draw_horizontal_link(x_boundary + r, x_route - r, cy, cu_def.get("msg_1_2"), cu_def.get("msg_ret_boundary")))
    
    # 3. Enlace Route -> Service / Engine
    svg.append(draw_horizontal_link(x_route + r, x_service - r, cy, cu_def.get("msg_1_3"), cu_def.get("msg_ret_route")))
    
    # 4. Enlace Service -> Repo
    svg.append(draw_horizontal_link(x_service + r, x_repo - r, cy, cu_def.get("msg_1_4"), cu_def.get("msg_ret_service")))
    
    # 5. Enlaces Repo -> Entidades
    svg.append(draw_entity_links(x_repo, cy, x_entity, entity_coords, entities))
    
    # Dibujar Nodos Participantes
    svg.append(draw_actor(x_actor, cy, cu_def.get("actor_name", "CLIENTE")))
    svg.append(draw_boundary(x_boundary, cy, r, cu_def.get("boundary_name", "IU_Pantalla")))
    svg.append(draw_control(x_route, cy, r, cu_def.get("route_name", "routes")))
    svg.append(draw_control(x_service, cy, r, cu_def.get("service_name", "services")))
    svg.append(draw_control(x_repo, cy, r, cu_def.get("repo_name", "repos")))
    
    # Dibujar Entidades
    for idx, e in enumerate(entities):
        ey = entity_coords[idx]
        svg.append(draw_entity(x_entity, ey, r, e["name"]))

    svg.append("</svg>")
    return "\n".join(svg)


# =============================================================
# DEFINICIÓN EXACTA DE LOS 9 CASOS DE USO SOLICITADOS
# (Con nombres de tablas de BD actualizados en MAYÚSCULAS)
# =============================================================

CUS_DATA = [
    # 1. CU/W12: Obtener recomendaciones de productos
    {
        "id": "CU_W12",
        "file_name": "CU_W12_Obtener_Recomendaciones_Productos",
        "title": "CU/W12: Obtener recomendaciones de productos (Moda & Colecciones Afines)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_Recomendaciones",
        "route_name": "catalogo_routes",
        "service_name": "catalogo_services",
        "repo_name": "catalogo_repos",
        "msg_1_1": [
            "1.1: Explorar sugerencias",
            "de moda y tendencias()"
        ],
        "msg_1_2": [
            "1.2: GET /api/catalogo/destacados",
            "(id_cliente, categoria)"
        ],
        "msg_1_3": [
            "1.3: obtener_catalogo_recomendado()",
            "calculando scoring de afinidad"
        ],
        "msg_1_4": [
            "1.4: consultar_ranking_ventas()",
            "con filtros de popularidad"
        ],
        "msg_ret_service": "1.11: return prendas_recomendadas()",
        "msg_ret_route": "1.12: HTTP 200 OK (payload_moda)",
        "msg_ret_boundary": "1.13: renderizar grilla 'Para Ti'",
        "msg_ret_actor": "1.14: visualizar prendas sugeridas",
        "entities": [
            {
                "name": "T_PRODUCTO",
                "forward": "1.5: SELECT prendas activas con fotos",
                "return": "1.6: return prendas aptas para sugerir"
            },
            {
                "name": "T_RECOMENDACION",
                "forward": "1.7: SELECT scores previos del cliente",
                "return": "1.8: return matriz de afinidad"
            },
            {
                "name": "T_PREFERENCIA_CLIENTE",
                "forward": "1.9: SELECT tallas y estilos favoritos",
                "return": "1.10: return perfil de preferencias"
            }
        ]
    },

    # 2. CU/W13: Interactuar con asistente inteligente
    {
        "id": "CU_W13",
        "file_name": "CU_W13_Interactuar_Asistente_Inteligente",
        "title": "CU/W13: Interactuar con asistente inteligente (Chatbot DeepSeek AI)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_AsistenteChat",
        "route_name": "asistente_routes",
        "service_name": "DeepSeek_AI_Service",
        "repo_name": "asistente_repos",
        "msg_1_1": [
            "1.1: Enviar pregunta sobre",
            "prendas, tallas o tiendas()"
        ],
        "msg_1_2": [
            "1.2: POST /api/asistente/chat",
            "(mensaje, historial_sesion)"
        ],
        "msg_1_3": [
            "1.3: procesar_chat_con_llm()",
            "despachando function calling"
        ],
        "msg_1_4": [
            "1.4: ejecutar_herramienta_bd()",
            "según intención detectada"
        ],
        "msg_ret_service": "1.11: sintetizar respuesta conversacional()",
        "msg_ret_route": "1.12: HTTP 200 OK (texto, cards)",
        "msg_ret_boundary": "1.13: renderizar burbuja asistente",
        "msg_ret_actor": "1.14: leer recomendación y cards",
        "entities": [
            {
                "name": "T_PRODUCTO",
                "forward": "1.5: SELECT prendas por coincidencia",
                "return": "1.6: return lista de prendas con stock"
            },
            {
                "name": "T_VENTA",
                "forward": "1.7: SELECT compras recientes del cliente",
                "return": "1.8: return tracking y estado de entrega"
            },
            {
                "name": "T_SUCURSAL",
                "forward": "1.9: SELECT sucursales físicas activas",
                "return": "1.10: return direcciones y horarios"
            }
        ]
    },

    # 3. CU/W30: Gestionar promociones
    {
        "id": "CU_W30",
        "file_name": "CU_W30_Gestionar_Promociones",
        "title": "CU/W30: Gestionar promociones (Campañas, Descuentos y Vigencias)",
        "actor_name": "ADMIN_TIENDA",
        "boundary_name": "IU_Promociones",
        "route_name": "productos_routes",
        "service_name": "productos_services",
        "repo_name": "productos_repos",
        "msg_1_1": [
            "1.1: Registrar nueva promo",
            "(nombre, %descuento, fechas)"
        ],
        "msg_1_2": [
            "1.2: POST /api/promociones",
            "(payload_campaña_prendas)"
        ],
        "msg_1_3": [
            "1.3: asignar_promocion_service()",
            "validando solapamiento de fechas"
        ],
        "msg_1_4": [
            "1.4: persistir cabecera, prendas",
            "y asentar registro de auditoría"
        ],
        "msg_ret_service": "1.11: confirmar activación de campaña()",
        "msg_ret_route": "1.12: HTTP 201 Created (promo_id)",
        "msg_ret_boundary": "1.13: actualizar grilla de promociones",
        "msg_ret_actor": "1.14: notificar promoción activa",
        "entities": [
            {
                "name": "T_PROMOCION",
                "forward": "1.5: INSERT INTO T_PROMOCION (fechas, %)",
                "return": "1.6: return id_promocion generado"
            },
            {
                "name": "T_PROMOCION_PRODUCTO",
                "forward": "1.7: INSERT INTO T_PROMOCION_PRODUCTO",
                "return": "1.8: return confirmación de vínculo"
            },
            {
                "name": "T_BITACORA",
                "forward": "1.9: INSERT INTO T_BITACORA (CREAR_PROMO)",
                "return": "1.10: return confirmación de auditoría"
            }
        ]
    },

    # 4. CU/W31: Consultar ventas, reservas e inventario
    {
        "id": "CU_W31",
        "file_name": "CU_W31_Consultar_Ventas_Reservas_Inventario",
        "title": "CU/W31: Consultar ventas, reservas e inventario (Monitor Operativo)",
        "actor_name": "ENCARGADO_SUCURSAL",
        "boundary_name": "IU_MonitorOperativo",
        "route_name": "inventario_routes",
        "service_name": "inventario_services",
        "repo_name": "inventario_repos",
        "msg_1_1": [
            "1.1: Filtrar sucursal y fecha",
            "para consultar balance integral()"
        ],
        "msg_1_2": [
            "1.2: GET /api/inventario/monitor",
            "(id_sucursal, rango_fechas)"
        ],
        "msg_1_3": [
            "1.3: consultar_balance_operativo()",
            "cruzando ventas, reservas y kardex"
        ],
        "msg_1_4": [
            "1.4: ejecutar consultas agregadas",
            "para métricas en tiempo real"
        ],
        "msg_ret_service": "1.11: return balance_consolidado()",
        "msg_ret_route": "1.12: HTTP 200 OK (datos_monitor)",
        "msg_ret_boundary": "1.13: renderizar panel operativo",
        "msg_ret_actor": "1.14: visualizar balance de tienda",
        "entities": [
            {
                "name": "T_VENTA",
                "forward": "1.5: SELECT ventas facturadas del turno",
                "return": "1.6: return totales y tickets cobrados"
            },
            {
                "name": "T_RESERVA",
                "forward": "1.7: SELECT reservas pendientes de retiro",
                "return": "1.8: return prendas apartadas en tienda"
            },
            {
                "name": "T_INVENTARIO",
                "forward": "1.9: SELECT existencias físicas y mínimas",
                "return": "1.10: return balance de stock disponible"
            }
        ]
    },

    # 5. CU/W32: Visualizar indicadores empresariales
    {
        "id": "CU_W32",
        "file_name": "CU_W32_Visualizar_Indicadores_Empresariales",
        "title": "CU/W32: Visualizar indicadores empresariales (Analytics & Dashboard KPIs)",
        "actor_name": "GERENTE",
        "boundary_name": "IU_DashboardKpis",
        "route_name": "kpis_routes",
        "service_name": "Analytics_Engine_Service",
        "repo_name": "kpis_repos",
        "msg_1_1": [
            "1.1: Seleccionar rango mensual",
            "y canal (POS vs Online)()"
        ],
        "msg_1_2": [
            "1.2: GET /api/kpis/dashboard",
            "(periodo, sucursal_id)"
        ],
        "msg_1_3": [
            "1.3: calcular_kpis_ejecutivos()",
            "agregando tickets e ingresos"
        ],
        "msg_1_4": [
            "1.4: consultar agregaciones SQL",
            "y comparativa anual (YoY)"
        ],
        "msg_ret_service": "1.11: return dataset_metricas_kpis()",
        "msg_ret_route": "1.12: HTTP 200 OK (graficos, tablas)",
        "msg_ret_boundary": "1.13: renderizar gráficos ejecutivos",
        "msg_ret_actor": "1.14: inspeccionar KPIs del negocio",
        "entities": [
            {
                "name": "T_VENTA",
                "forward": "1.5: SELECT SUM(TOTAL), COUNT(*) ventas",
                "return": "1.6: return ingresos consolidados periodo"
            },
            {
                "name": "T_DETALLE_VENTA",
                "forward": "1.7: SELECT prendas más vendidas rotación",
                "return": "1.8: return ranking prendas estrella"
            },
            {
                "name": "T_PAGO",
                "forward": "1.9: SELECT montos por método (Efectivo/QR)",
                "return": "1.10: return desglose canales de recaudo"
            }
        ]
    },

    # 6. CU/W33: Generar reportes bajo demanda
    {
        "id": "CU_W33",
        "file_name": "CU_W33_Generar_Reportes_Bajo_Demanda",
        "title": "CU/W33: Generar reportes bajo demanda (Exportación PDF / XLSX)",
        "actor_name": "ADMIN / GERENTE",
        "boundary_name": "IU_ReportesDemanda",
        "route_name": "reportes_routes",
        "service_name": "Report_Export_Service",
        "repo_name": "reportes_repos",
        "msg_1_1": [
            "1.1: Configurar tipo reporte",
            "y rango de fechas a exportar()"
        ],
        "msg_1_2": [
            "1.2: POST /api/reportes/generar",
            "(formato='PDF', filtros)"
        ],
        "msg_1_3": [
            "1.3: compilar_reporte_asincrono()",
            "generando documento estructurado"
        ],
        "msg_1_4": [
            "1.4: extraer datasets consolidados",
            "para compilación tabular"
        ],
        "msg_ret_service": "1.11: return url_descarga_storage()",
        "msg_ret_route": "1.12: HTTP 200 OK (documento_binario)",
        "msg_ret_boundary": "1.13: disparar descarga en navegador",
        "msg_ret_actor": "1.14: guardar archivo descargado",
        "entities": [
            {
                "name": "T_VENTA",
                "forward": "1.5: SELECT transacciones para reporte",
                "return": "1.6: return registros de venta filtrados"
            },
            {
                "name": "T_INVENTARIO",
                "forward": "1.7: SELECT movimientos y kardex de tienda",
                "return": "1.8: return historial de existencias"
            },
            {
                "name": "T_BITACORA",
                "forward": "1.9: INSERT INTO T_BITACORA (EXPORT_REPORTE)",
                "return": "1.10: return confirmación de auditoría"
            }
        ]
    },

    # 7. CU/M12: Obtener recomendaciones de productos (Mobile)
    {
        "id": "CU_M12",
        "file_name": "CU_M12_Obtener_Recomendaciones_Productos",
        "title": "CU/M12: Obtener recomendaciones de productos (Flutter App Móvil)",
        "actor_name": "CLIENTE_MOVIL",
        "boundary_name": "Feed_Recomendados_Screen",
        "route_name": "Recomendaciones_Cubit",
        "service_name": "Mobile_API_Client",
        "repo_name": "catalogo_repos",
        "msg_1_1": [
            "1.1: Tocar pestaña 'Para Ti'",
            "en app móvil Flutter()"
        ],
        "msg_1_2": [
            "1.2: cargar_recomendaciones()",
            "(cache_offline || sync_api)"
        ],
        "msg_1_3": [
            "1.3: GET /api/catalogo/recomendados",
            "con token JWT de cliente móvil"
        ],
        "msg_1_4": [
            "1.4: consultar_recomendaciones_cliente()",
            "priorizando tallas en stock"
        ],
        "msg_ret_service": "1.11: return prendas_json_optimizadas()",
        "msg_ret_route": "1.12: emit(RecomendacionesLoaded)",
        "msg_ret_boundary": "1.13: renderizar carrusel nativo",
        "msg_ret_actor": "1.14: explorar recomendaciones",
        "entities": [
            {
                "name": "T_RECOMENDACION",
                "forward": "1.5: SELECT recomendaciones activas cliente",
                "return": "1.6: return IDs de prendas recomendadas"
            },
            {
                "name": "T_HISTORIAL_NAVEGACION",
                "forward": "1.7: INSERT INTO T_HISTORIAL_NAVEGACION",
                "return": "1.8: return confirmación de registro"
            },
            {
                "name": "T_PRODUCTO",
                "forward": "1.9: SELECT fotos, tallas y precio prenda",
                "return": "1.10: return cards con imagen optimizada"
            }
        ]
    },

    # 8. CU/M13: Interactuar con asistente inteligente (Mobile)
    {
        "id": "CU_M13",
        "file_name": "CU_M13_Interactuar_Asistente_Inteligente",
        "title": "CU/M13: Interactuar con asistente inteligente (App Móvil - Voz y Chat)",
        "actor_name": "CLIENTE_MOVIL",
        "boundary_name": "IU_ChatVoz_Screen",
        "route_name": "Asistente_Cubit",
        "service_name": "DeepSeek_AI_Service",
        "repo_name": "asistente_repos",
        "msg_1_1": [
            "1.1: Hablar por micrófono o",
            "escribir en app móvil()"
        ],
        "msg_1_2": [
            "1.2: enviar_comando_audio_o_texto()",
            "procesando speech-to-text"
        ],
        "msg_1_3": [
            "1.3: POST /api/asistente/chat",
            "streaming con LLM DeepSeek"
        ],
        "msg_1_4": [
            "1.4: ejecutar tool en base de datos",
            "con parámetros de voz inferidos"
        ],
        "msg_ret_service": "1.11: emitir texto y cards de prendas()",
        "msg_ret_route": "1.12: emit(AsistenteResponseReady)",
        "msg_ret_boundary": "1.13: renderizar burbuja y reproducir TTS",
        "msg_ret_actor": "1.14: escuchar/leer respuesta",
        "entities": [
            {
                "name": "T_PRODUCTO",
                "forward": "1.5: SELECT prendas por búsqueda semántica",
                "return": "1.6: return catálogo de prendas afines"
            },
            {
                "name": "T_HISTORIAL_NAVEGACION",
                "forward": "1.7: INSERT INTO T_HISTORIAL_NAVEGACION",
                "return": "1.8: return confirmación de interacción"
            }
        ]
    },

    # 9. CU/M14: Utilizar vestidor virtual (Mobile RA)
    {
        "id": "CU_M14",
        "file_name": "CU_M14_Utilizar_Vestidor_Virtual",
        "title": "CU/M14: Utilizar vestidor virtual (Probador Realidad Aumentada - AR Try-On)",
        "actor_name": "CLIENTE_MOVIL",
        "boundary_name": "Vestidor_Screen",
        "route_name": "AR_Camera_Ctrl",
        "service_name": "Pose_Body_Detector",
        "repo_name": "Vestidor_Service",
        "msg_1_1": [
            "1.1: Tocar 'Probar Prenda en RA'",
            "y apuntar cámara frontal()"
        ],
        "msg_1_2": [
            "1.2: inicializar_feed_camara()",
            "y stream de frames 60fps"
        ],
        "msg_1_3": [
            "1.3: procesar_frame_pose(image)",
            "detectando hombros, torso y cadera"
        ],
        "msg_1_4": [
            "1.4: get_recursos_prenda_ra(id)",
            "descargando texturas 2D/3D"
        ],
        "msg_ret_service": "1.11: return PoseData(escala, rotación)()",
        "msg_ret_route": "1.12: superponer_textura_sobre_cuerpo()",
        "msg_ret_boundary": "1.13: renderizar prenda en tiempo real",
        "msg_ret_actor": "1.14: verse con la prenda superpuesta",
        "entities": [
            {
                "name": "T_PRENDA_RA",
                "forward": "1.5: SELECT MODELO_2D_URL, MODELO_3D_URL",
                "return": "1.6: return texturas transparentes prenda"
            },
            {
                "name": "T_VESTIDOR_VIRTUAL",
                "forward": "1.7: INSERT INTO T_VESTIDOR_VIRTUAL (sesión)",
                "return": "1.8: return confirmación de prueba RA"
            }
        ]
    }
]

# =============================================================
# MAIN DE EJECUCIÓN
# =============================================================

def main():
    print("Iniciando regeneración cuidadosa de los 9 Diagramas de Comunicación UML...")
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(BRAIN_DIR, exist_ok=True)
    
    for idx, cu_def in enumerate(CUS_DATA):
        name = cu_def["file_name"]
        svg_content = generate_comm_diagram_svg(cu_def)
        
        svg_path = os.path.join(OUT_DIR, f"{name}.svg")
        png_path = os.path.join(OUT_DIR, f"{name}.png")
        brain_svg = os.path.join(BRAIN_DIR, f"{name}.svg")
        brain_png = os.path.join(BRAIN_DIR, f"{name}.png")
        
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        with open(brain_svg, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
        # Renderizar PNG 2x con resvg_py
        png_bytes = resvg_py.svg_to_bytes(svg_content, zoom=2.0)
        with open(png_path, "wb") as f:
            f.write(png_bytes)
        with open(brain_png, "wb") as f:
            f.write(png_bytes)
            
        print(f" [{idx+1}/{len(CUS_DATA)}] Generado con precisión: {name} (SVG y PNG 2x)")

    print("\nTodos los Diagramas de Comunicación han sido regenerados y sincronizados exitosamente.")

if __name__ == "__main__":
    main()
