#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de los 17 Diagramas de Secuencia UML (SI2 - UAGRM)
Abarca los 25 Casos de Uso del sistema:
- 8 Casos de Uso Unificados Web / Móvil (CU05, CU06, CU07, CU08, CU09, CU10, CU11, CU26_M15)
- 9 Casos de Uso Específicos Web (CU_W20, CU_W21, CU_W22, CU_W23, CU_W24, CU_W25, CU_W27, CU_W28, CU_W29)

Directivas del usuario aplicadas:
1. Documenta estrictamente las FUNCIONES reales que se invocan en el backend (Controller -> Service -> Repository -> Bitácora).
2. Mensajes limpios y concisos (sin query params técnicos extensos ni cadenas técnicas HTTP 200/400).
3. Estilo UML oficial idéntico al diagrama de cátedra (media_1788651647326.png):
   - Marco exterior con pestaña de título en esquina superior izquierda.
   - Pestañas 'alt' y 'opt' con sus correspondientes guardas.
   - Barras de activación vertical alineadas a las llamadas y retornos.
   - Flechas sincrónicas (cerradas y rellenas) y retornos (línea discontinua con flecha abierta).
   - Generación vectorial SVG y exportación a PNG de alta resolución (2x) mediante CairoSVG.
"""

import os
import sys
import cairosvg

def escape_xml(s):
    return (str(s).replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;")
                  .replace('"', "&quot;")
                  .replace("'", "&apos;"))

def render_sequence_svg(data):
    width = data.get("width", 1320)
    height = data.get("height", 860)

    x_actor = data.get("x_actor", 90)
    x_iu = data.get("x_iu", 290)
    x_controller = data.get("x_controller", 530)
    x_service = data.get("x_service", 780)
    x_repo = data.get("x_repo", 1040)
    x_bitacora = data.get("x_bitacora", 1240)

    actor_name = data.get("actor_name", "CLIENTE")
    iu_name = data.get("iu_name", "IU_Boundary")
    controller_name = data.get("controller_name", "Controller")
    service_name = data.get("service_name", "Service")
    repo_name = data.get("repo_name", "Repository")
    bitacora_name = data.get("bitacora_name", "T_BITACORA")

    title = data.get("title", "Diagrama de Secuencia")

    y_header_box = 85
    h_header_box = 36
    w_box = 145
    y_line_start = y_header_box + h_header_box
    y_line_end = height - 40

    coords_map = {
        "ACTOR": x_actor,
        "IU": x_iu,
        "CONTROLLER": x_controller,
        "SERVICE": x_service,
        "REPO": x_repo,
        "BITACORA": x_bitacora
    }

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <defs>
    <!-- Flecha sincrónica (cerrada y rellena) -->
    <marker id="arrow_sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/>
    </marker>
    <!-- Flecha de retorno / asincrónico (abierta) -->
    <marker id="arrow_return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9" fill="none" stroke="#000000" stroke-width="1.4"/>
    </marker>
  </defs>

  <!-- Marco Exterior -->
  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  
  <!-- Pestaña de Título UML -->
  <path d="M 15 15 L 420 15 L 435 35 L 435 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12.5" font-weight="bold" fill="#000000">{escape_xml(title)}</text>

  <!-- ==================== PARTICIPANTES ==================== -->

  <!-- Actor -->
  <g transform="translate({x_actor}, 55)">
    <circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/>
    <line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/>
    <text x="0" y="78" font-size="11" font-weight="bold" text-anchor="middle" fill="#000000">{escape_xml(actor_name)}</text>
  </g>

  <!-- IU -->
  <g>
    <rect x="{x_iu - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_iu}" y="{y_header_box + 22}" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">{escape_xml(iu_name)}</text>
  </g>

  <!-- Controller -->
  <g>
    <rect x="{x_controller - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_controller}" y="{y_header_box + 22}" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">{escape_xml(controller_name)}</text>
  </g>

  <!-- Service -->
  <g>
    <rect x="{x_service - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_service}" y="{y_header_box + 22}" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">{escape_xml(service_name)}</text>
  </g>

  <!-- Repo -->
  <g>
    <rect x="{x_repo - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_repo}" y="{y_header_box + 22}" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">{escape_xml(repo_name)}</text>
  </g>

  <!-- T_BITACORA -->
  <g>
    <rect x="{x_bitacora - 55}" y="{y_header_box}" width="110" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_bitacora}" y="{y_header_box + 22}" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">{escape_xml(bitacora_name)}</text>
  </g>

  <!-- ==================== LÍNEAS DE VIDA (PUNTEADAS) ==================== -->
  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_iu}" y1="{y_line_start}" x2="{x_iu}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_controller}" y1="{y_line_start}" x2="{x_controller}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_service}" y1="{y_line_start}" x2="{x_service}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_repo}" y1="{y_line_start}" x2="{x_repo}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_bitacora}" y1="{y_line_start}" x2="{x_bitacora}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <!-- ==================== BARRAS DE ACTIVACIÓN ==================== -->
''')

    for bar in data.get("activations", []):
        x_target = coords_map.get(bar["target"], x_iu)
        y = bar["y"]
        h = bar["h"]
        svg.append(f'  <rect x="{x_target - 6}" y="{y}" width="12" height="{h}" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>\n')

    # Fragmentos (alt / opt)
    for frag in data.get("fragments", []):
        fx = frag.get("x", 40)
        fy = frag.get("y", 260)
        fw = frag.get("w", width - 70)
        fh = frag.get("h", 280)
        ftype = frag.get("type", "alt")
        fguard = frag.get("guard", "")

        svg.append(f'\n  <!-- Fragmento {ftype}: {escape_xml(fguard)} -->\n')
        svg.append(f'  <rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="none" stroke="#000000" stroke-width="1.3"/>\n')
        svg.append(f'  <path d="M {fx} {fy} L {fx + 55} {fy} L {fx + 65} {fy + 17} L {fx + 65} {fy + 25} L {fx} {fy + 25} Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>\n')
        svg.append(f'  <text x="{fx + 30}" y="{fy + 17}" font-size="11.5" font-weight="bold" text-anchor="middle" fill="#000000">{ftype}</text>\n')
        if fguard:
            svg.append(f'  <text x="{fx + 78}" y="{fy + 18}" font-size="11" font-weight="bold" fill="#000000">{escape_xml(fguard)}</text>\n')

        # Si tiene divisor alt
        if "divider_y" in frag:
            dy = frag["divider_y"]
            svg.append(f'  <line x1="{fx}" y1="{dy}" x2="{fx + fw}" y2="{dy}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>\n')
            if "guard2" in frag:
                svg.append(f'  <text x="{fx + 15}" y="{dy + 17}" font-size="11" font-weight="bold" fill="#000000">{escape_xml(frag["guard2"])}</text>\n')

    svg.append('\n  <!-- ==================== MENSAJES ==================== -->\n')
    for msg in data.get("messages", []):
        src = coords_map[msg["from"]]
        dst = coords_map[msg["to"]]
        y = msg["y"]
        text = msg["text"]
        is_return = msg.get("return", False)

        # Determinar dirección y puntos
        if src < dst:
            x1 = src + 6 if msg["from"] != "ACTOR" else src
            x2 = dst - 6
        else:
            x1 = src - 6
            x2 = dst + 6 if msg["to"] != "ACTOR" else dst

        marker = "url(#arrow_return)" if is_return else "url(#arrow_sync)"
        dash = ' stroke-dasharray="4,3"' if is_return else ''

        # Posición del texto: centrado entre las dos entidades, a menos que cruce otra
        if "tx" in msg:
            tx = msg["tx"]
        else:
            tx = (x1 + x2) / 2

        svg.append(f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#000000" stroke-width="1.3"{dash} marker-end="{marker}"/>\n')
        svg.append(f'  <text x="{tx}" y="{y - 7}" font-size="10.5" text-anchor="middle" fill="#000000">{escape_xml(text)}</text>\n')

    svg.append('\n</svg>\n')
    return "".join(svg)

# ==============================================================================
# DEFINICIÓN DE LOS 17 DIAGRAMAS DE SECUENCIA
# ==============================================================================

DIAGRAMAS = [
    # 01. CU05 W/M
    {
        "filename": "CU05_WM_Buscar_Filtrar_Productos_Secuencia",
        "title": "CU05 W/M: Buscar y filtrar productos",
        "actor_name": "CLIENTE",
        "iu_name": "IU_Catalogo",
        "controller_name": "catalogo_routes",
        "service_name": "catalogo_services",
        "repo_name": "catalogo_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 295, "h": 40},
            {"target": "REPO", "y": 445, "h": 40},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 355, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[PRODUCTOS ENCONTRADOS]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[SIN RESULTADOS]"
            },
            {
                "type": "opt", "guard": "[CARGAR METADATOS DE FILTROS]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: SeleccionarFiltros(filtros)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: GET /api/catalogo/productos"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: filtrar_catalogo(criterios)"},
            {"from": "SERVICE", "to": "REPO", "y": 300, "text": "4: listar_catalogo_publico(id_empresa, filtros)"},
            {"from": "REPO", "to": "SERVICE", "y": 330, "text": "5: return lista_productos", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 360, "text": "6: registrar_bitacora(ACCION, filtros)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 390, "text": "7: respuesta_exitosa(productos)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 410, "text": "8: RenderizarCatalogo(productos)", "return": True},
            {"from": "REPO", "to": "SERVICE", "y": 455, "text": "9: return lista_vacia", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 485, "text": "10: respuesta_vacia()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 515, "text": "11: MostrarAlerta(\"Sin coincidencias\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "12: GET /api/catalogo/filtros"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "13: obtener_filtros_disponibles(id_empresa)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "14: obtener_filtros_disponibles(id_empresa)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "15: return filtros", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "16: respuesta_filtros(filtros)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "17: CargarSelectores(filtros)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "18: MostrarCatalogo()", "return": True}
        ]
    },

    # 02. CU06 W/M
    {
        "filename": "CU06_WM_Consultar_Detalle_Producto_Secuencia",
        "title": "CU06 W/M: Consultar detalle de producto",
        "actor_name": "CLIENTE",
        "iu_name": "IU_DetalleProducto",
        "controller_name": "catalogo_routes",
        "service_name": "productos_services",
        "repo_name": "catalogo_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 290, "h": 65},
            {"target": "REPO", "y": 445, "h": 40},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 375, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[PRODUCTO ACTIVO Y EXISTENTE]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[PRODUCTO INEXISTENTE O INACTIVO]"
            },
            {
                "type": "opt", "guard": "[CONSULTAR GUÍA DE TALLAS DE PRENDA]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: SeleccionarPrenda(id_producto)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: GET /api/catalogo/productos/{id}"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: obtener_detalle_producto(id_producto)"},
            {"from": "SERVICE", "to": "REPO", "y": 295, "text": "4: obtener_producto_por_id(id_producto)"},
            {"from": "REPO", "to": "SERVICE", "y": 320, "text": "5: return producto_info", "return": True},
            {"from": "SERVICE", "to": "REPO", "y": 345, "text": "6: obtener_variantes_e_imagenes(id_producto)"},
            {"from": "REPO", "to": "SERVICE", "y": 365, "text": "7: return variantes, imagenes", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 385, "text": "8: registrar_bitacora(CONSULTA_DETALLE, id_producto)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 405, "text": "9: respuesta_exitosa(detalle_completo)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 420, "text": "10: RenderizarDetallePrenda(detalle)", "return": True},
            {"from": "REPO", "to": "SERVICE", "y": 455, "text": "11: return None", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 485, "text": "12: respuesta_no_encontrado()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 515, "text": "13: MostrarAlerta(\"Prenda no disponible\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "14: GET /api/catalogo/tallas/guia"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "15: obtener_guia_tallas()"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "16: get_medidas_guia_tallas()"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "17: return tabla_medidas", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "18: respuesta_guia(tabla_medidas)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "19: MostrarModalTallas(tabla_medidas)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "20: PresentarFichaProducto()", "return": True}
        ]
    },

    # 03. CU07 W/M
    {
        "filename": "CU07_WM_Consultar_Disponibilidad_Sucursal_Secuencia",
        "title": "CU07 W/M: Consultar disponibilidad por sucursal",
        "actor_name": "CLIENTE",
        "iu_name": "IU_Disponibilidad",
        "controller_name": "catalogo_routes",
        "service_name": "inventario_services",
        "repo_name": "inventario_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 295, "h": 40},
            {"target": "REPO", "y": 445, "h": 40},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 355, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[EXISTENCIAS EN SUCURSALES]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[SIN EXISTENCIAS EN TIENDAS]"
            },
            {
                "type": "opt", "guard": "[VER UBICACIÓN EN MAPA DE LA SUCURSAL]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: ConsultarStockSucursales(id_variante)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: GET /api/catalogo/stock-sucursales"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: consultar_stock_sucursales(id_variante)"},
            {"from": "SERVICE", "to": "REPO", "y": 300, "text": "4: obtener_stock_sucursales_producto(id_variante)"},
            {"from": "REPO", "to": "SERVICE", "y": 330, "text": "5: return lista_sucursales_stock", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 360, "text": "6: registrar_bitacora(CONSULTA_STOCK, id_variante)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 390, "text": "7: respuesta_exitosa(sucursales_stock)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 410, "text": "8: MostrarSucursalesConStock(sucursales_stock)", "return": True},
            {"from": "REPO", "to": "SERVICE", "y": 455, "text": "9: return stock_vacio", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 485, "text": "10: respuesta_sin_stock()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 515, "text": "11: MostrarAlerta(\"Sin existencias en tiendas\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "12: GET /api/sucursales/{id}/coordenadas"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "13: obtener_geolocalizacion_sucursal(id_sucursal)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "14: get_coordenadas_sucursal(id_sucursal)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "15: return coordenadas_gps", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "16: respuesta_gps(coordenadas_gps)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "17: AbrirPinEnMapa(coordenadas_gps)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "18: MostrarDisponibilidadTiendas()", "return": True}
        ]
    },

    # 04. CU08 W/M
    {
        "filename": "CU08_WM_Gestionar_Carrito_Compras_Secuencia",
        "title": "CU08 W/M: Gestionar carrito de compras",
        "actor_name": "CLIENTE",
        "iu_name": "IU_Carrito",
        "controller_name": "carrito_routes",
        "service_name": "carrito_services",
        "repo_name": "carrito_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 290, "h": 65},
            {"target": "REPO", "y": 450, "h": 35},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 375, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[STOCK DISPONIBLE EN ALMACÉN]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[STOCK INSUFICIENTE]"
            },
            {
                "type": "opt", "guard": "[MODIFICAR CANTIDAD O ELIMINAR PRENDA]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: AgregarItem(id_variante, cantidad)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: POST /api/carrito/items"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: agregar_item_carrito(id_cliente, payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 295, "text": "4: verificar_stock_disponible(id_variante, cant)"},
            {"from": "REPO", "to": "SERVICE", "y": 320, "text": "5: return stock_ok", "return": True},
            {"from": "SERVICE", "to": "REPO", "y": 345, "text": "6: insertar_o_actualizar_item(id_carrito, id_var, cant)"},
            {"from": "REPO", "to": "SERVICE", "y": 365, "text": "7: return item_guardado", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 385, "text": "8: registrar_bitacora(AGREGAR_CARRITO, id_item)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 405, "text": "9: respuesta_exitosa(\"Item agregado\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 420, "text": "10: ActualizarBadgeCarrito(total_items)", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "11: respuesta_error(\"Stock insuficiente\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "12: MostrarAlerta(\"Stock insuficiente en bodega\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "13: DELETE /api/carrito/items/{id}"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "14: eliminar_item_carrito(id_item)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "15: delete_item_db(id_item)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "16: return confirmacion", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "17: respuesta_eliminacion(totales)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "18: RecalcularTotalesCarrito(totales)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "19: MostrarCarritoActualizado()", "return": True}
        ]
    },

    # 05. CU09 W/M
    {
        "filename": "CU09_WM_Realizar_Compra_Secuencia",
        "title": "CU09 W/M: Realizar compra",
        "actor_name": "CLIENTE",
        "iu_name": "IU_Checkout",
        "controller_name": "pedidos_routes",
        "service_name": "pedidos_services",
        "repo_name": "pedidos_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 290, "h": 70},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 380, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[PAGO AUTORIZADO Y STOCK RESERVADO]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[TRANSACCIÓN RECHAZADA O FALLA]"
            },
            {
                "type": "opt", "guard": "[DESCARGAR COMPROBANTE DIGITAL EN PDF]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: ConfirmarCompra(tipo_entrega, metodo_pago)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: POST /api/pedidos/checkout"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: procesar_checkout_pedido(id_cliente, payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 295, "text": "4: crear_pedido_con_detalles(pedido_data)"},
            {"from": "REPO", "to": "SERVICE", "y": 320, "text": "5: return id_pedido, numero_pedido", "return": True},
            {"from": "SERVICE", "to": "REPO", "y": 345, "text": "6: descontar_stock_inventario(items)"},
            {"from": "REPO", "to": "SERVICE", "y": 365, "text": "7: return stock_actualizado", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 385, "text": "8: registrar_bitacora(CREAR_PEDIDO, id_pedido)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 405, "text": "9: respuesta_exitosa(numero_pedido)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 420, "text": "10: MostrarConfirmacionOrden(numero_pedido)", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "11: respuesta_error(\"Pago rechazado\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "12: MostrarAlerta(\"Error en el pago, intente nuevamente\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "13: GET /api/pedidos/{id}/comprobante"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "14: generar_comprobante_digital(id_pedido)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "15: get_datos_comprobante(id_pedido)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "16: return pdf_bytes", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "17: respuesta_descarga(pdf_url)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "18: DescargarComprobante(pdf_url)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "19: FinalizarFlujoCompra()", "return": True}
        ]
    },

    # 06. CU10 W/M
    {
        "filename": "CU10_WM_Gestionar_Reservas_Secuencia",
        "title": "CU10 W/M: Gestionar reservas",
        "actor_name": "CLIENTE",
        "iu_name": "IU_Reservas",
        "controller_name": "reservas_routes",
        "service_name": "reservas_services",
        "repo_name": "reservas_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 290, "h": 65},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 375, "h": 30},
            {"target": "BITACORA", "y": 680, "h": 25}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[CUPO Y PRENDA DISPONIBLE PARA RESERVA]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[SIN DISPONIBILIDAD EN SUCURSAL]"
            },
            {
                "type": "opt", "guard": "[CANCELAR RESERVA ACTIVA DEL CLIENTE]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: SolicitarReserva(id_variante, id_sucursal)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: POST /api/reservas"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: crear_reserva_sucursal(id_cliente, payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 295, "text": "4: verificar_stock_reservable(id_var, id_suc)"},
            {"from": "REPO", "to": "SERVICE", "y": 320, "text": "5: return disponible_ok", "return": True},
            {"from": "SERVICE", "to": "REPO", "y": 345, "text": "6: registrar_reserva_y_bloqueo(reserva_data)"},
            {"from": "REPO", "to": "SERVICE", "y": 365, "text": "7: return codigo_reserva, fecha_limite", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 385, "text": "8: registrar_bitacora(CREAR_RESERVA, id_reserva)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 405, "text": "9: respuesta_exitosa(codigo_reserva)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 420, "text": "10: MostrarComprobanteReserva(codigo)", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "11: respuesta_error(\"Sin stock reservable\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "12: MostrarAlerta(\"No hay prendas disponibles para reserva\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "13: PUT /api/reservas/{id}/cancelar"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "14: cancelar_reserva_cliente(id_reserva)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "15: liberar_stock_reserva_db(id_reserva)"},
            {"from": "REPO", "to": "SERVICE", "y": 680, "text": "16: return cancelacion_ok", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 695, "text": "17: registrar_bitacora(CANCELAR_RESERVA, id)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 715, "text": "18: respuesta_cancelacion()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "19: ActualizarEstadoReserva(\"CANCELADA\")", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "20: ConfirmarCancelacion()", "return": True}
        ]
    },

    # 07. CU11 W/M
    {
        "filename": "CU11_WM_Consultar_Pedidos_Historial_Secuencia",
        "title": "CU11 W/M: Consultar pedidos e historial de compras",
        "actor_name": "CLIENTE",
        "iu_name": "IU_HistorialPedidos",
        "controller_name": "pedidos_routes",
        "service_name": "pedidos_services",
        "repo_name": "pedidos_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 295, "h": 40},
            {"target": "REPO", "y": 445, "h": 40},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 355, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[HISTORIAL CON REGISTROS]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[SIN PEDIDOS REGISTRADOS]"
            },
            {
                "type": "opt", "guard": "[VER DETALLE Y SEGUIMIENTO DE ORDEN]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: AbrirHistorialPedidos()"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: GET /api/pedidos/mis-pedidos"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: listar_pedidos_cliente(id_cliente)"},
            {"from": "SERVICE", "to": "REPO", "y": 300, "text": "4: obtener_pedidos_por_cliente(id_cliente)"},
            {"from": "REPO", "to": "SERVICE", "y": 330, "text": "5: return lista_pedidos", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 360, "text": "6: registrar_bitacora(CONSULTA_HISTORIAL, id_cli)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 390, "text": "7: respuesta_exitosa(lista_pedidos)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 410, "text": "8: RenderizarTablaPedidos(lista_pedidos)", "return": True},
            {"from": "REPO", "to": "SERVICE", "y": 455, "text": "9: return [] (vacio)", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 485, "text": "10: respuesta_vacia()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 515, "text": "11: MostrarMensaje(\"No tienes pedidos registrados\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "12: GET /api/pedidos/{id}"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "13: obtener_detalle_completo_pedido(id_pedido)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "14: get_detalle_pedido_items(id_pedido)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "15: return items, estado, pago", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "16: respuesta_detalle(info_pedido)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "17: MostrarModalDetalle(info_pedido)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "18: VisualizarHistorialCompleto()", "return": True}
        ]
    },

    # 08. CU26 / M15
    {
        "filename": "CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Secuencia",
        "title": "CU26 / M15 W/M: Mostrar ubicaciones de sucursales",
        "actor_name": "CLIENTE",
        "iu_name": "IU_MapaTiendas",
        "controller_name": "sucursales_routes",
        "service_name": "sucursales_services",
        "repo_name": "sucursales_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 295, "h": 40},
            {"target": "REPO", "y": 445, "h": 40},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 355, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[SUCURSALES ACTIVAS ENCONTRADAS]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[SIN TIENDAS FÍSICAS]"
            },
            {
                "type": "opt", "guard": "[CONSULTAR HORARIO Y TELÉFONO DE TIENDA]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: AbrirMapaTiendas()"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: GET /api/sucursales/publicas"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: listar_sucursales_activas(id_empresa)"},
            {"from": "SERVICE", "to": "REPO", "y": 300, "text": "4: obtener_sucursales_con_coordenadas(id_empresa)"},
            {"from": "REPO", "to": "SERVICE", "y": 330, "text": "5: return sucursales_list", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 360, "text": "6: registrar_bitacora(CONSULTA_MAPA, id_empresa)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 390, "text": "7: respuesta_exitosa(sucursales_list)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 410, "text": "8: CargarPinesEnMapa(sucursales_list)", "return": True},
            {"from": "REPO", "to": "SERVICE", "y": 455, "text": "9: return []", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 485, "text": "10: respuesta_vacia()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 515, "text": "11: MostrarMensaje(\"No hay sucursales registradas\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "12: GET /api/sucursales/{id}/horarios"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "13: obtener_horarios_atencion(id_sucursal)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "14: get_horarios_sucursal(id_sucursal)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "15: return horarios, telefono", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "16: respuesta_horarios(info_tienda)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "17: MostrarFichaTienda(info_tienda)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "18: ExplorarUbicaciones()", "return": True}
        ]
    },

    # 09. CU_W20
    {
        "filename": "CU_W20_Gestionar_Temporadas_Colecciones_Secuencia",
        "title": "CU/W20: Gestionar temporadas y colecciones",
        "actor_name": "ADMINISTRADOR",
        "iu_name": "IU_Colecciones",
        "controller_name": "colecciones_routes",
        "service_name": "colecciones_services",
        "repo_name": "colecciones_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 295, "h": 40},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 355, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[COLECCIÓN VÁLIDA Y NO DUPLICADA]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[NOMBRE DE COLECCIÓN YA EXISTENTE]"
            },
            {
                "type": "opt", "guard": "[ASOCIAR PRENDAS A LA NUEVA COLECCIÓN]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: GuardarColeccion(nombre, temporada, anio)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: POST /api/colecciones"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: registrar_coleccion(id_empresa, payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 300, "text": "4: insertar_coleccion_db(coleccion_data)"},
            {"from": "REPO", "to": "SERVICE", "y": 330, "text": "5: return id_coleccion", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 360, "text": "6: registrar_bitacora(CREAR_COLECCION, id)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 390, "text": "7: respuesta_exitosa(\"Colección registrada\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 410, "text": "8: ActualizarGrillaColecciones()", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "9: respuesta_error(\"Nombre de colección duplicado\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "10: MostrarAlerta(\"La colección ya existe en la empresa\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "11: PUT /api/colecciones/{id}/productos"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "12: asociar_productos_coleccion(id, productos_ids)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "13: update_productos_coleccion_db(id, ids)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "14: return asociacion_ok", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "15: respuesta_asociacion()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "16: NotificarAsociacionPrendas()", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "17: ConfirmarGestionColeccion()", "return": True}
        ]
    },

    # 10. CU_W21
    {
        "filename": "CU_W21_Gestionar_Proveedores_Secuencia",
        "title": "CU/W21: Gestionar proveedores",
        "actor_name": "ADMINISTRADOR",
        "iu_name": "IU_Proveedores",
        "controller_name": "proveedores_routes",
        "service_name": "proveedores_services",
        "repo_name": "proveedores_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 290, "h": 65},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 375, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[PROVEEDOR VÁLIDO CON NIT ÚNICO]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[NIT YA REGISTRADO EN EL SISTEMA]"
            },
            {
                "type": "opt", "guard": "[CONSULTAR ÓRDENES DE COMPRA AL PROVEEDOR]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: GuardarProveedor(razon_social, nit, telefono)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: POST /api/proveedores"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: crear_proveedor(id_empresa, payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 295, "text": "4: verificar_nit_existente(nit, id_empresa)"},
            {"from": "REPO", "to": "SERVICE", "y": 320, "text": "5: return nit_libre", "return": True},
            {"from": "SERVICE", "to": "REPO", "y": 345, "text": "6: insertar_proveedor_db(proveedor_data)"},
            {"from": "REPO", "to": "SERVICE", "y": 365, "text": "7: return id_proveedor", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 385, "text": "8: registrar_bitacora(CREAR_PROVEEDOR, id)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 405, "text": "9: respuesta_exitosa(\"Proveedor guardado\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 420, "text": "10: ActualizarListaProveedores()", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "11: respuesta_error(\"NIT ya registrado\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "12: MostrarAlerta(\"El NIT ingresado ya existe\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "13: GET /api/proveedores/{id}/ordenes"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "14: obtener_ordenes_proveedor(id_proveedor)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "15: get_ordenes_compra_prov(id_proveedor)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "16: return ordenes_list", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "17: respuesta_ordenes(ordenes_list)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "18: MostrarHistorialOrdenes(ordenes_list)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "19: ConfirmarProveedorRegistrado()", "return": True}
        ]
    },

    # 11. CU_W22
    {
        "filename": "CU_W22_Gestionar_Inventario_Secuencia",
        "title": "CU/W22: Gestionar inventario",
        "actor_name": "ENCARGADO SUCURSAL",
        "iu_name": "IU_Inventario",
        "controller_name": "inventario_routes",
        "service_name": "inventario_services",
        "repo_name": "inventario_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 290, "h": 65},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 375, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[MOVIMIENTO DE INVENTARIO VÁLIDO]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[STOCK INSUFICIENTE PARA SALIDA]"
            },
            {
                "type": "opt", "guard": "[CONSULTAR MOVIMIENTOS KARDEX DE LA VARIANTE]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: RegistrarMovimiento(tipo, id_variante, cant, motivo)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: POST /api/inventario/movimientos"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: procesar_movimiento_stock(id_sucursal, payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 295, "text": "4: validar_disponibilidad_stock(id_var, id_suc, tipo, cant)"},
            {"from": "REPO", "to": "SERVICE", "y": 320, "text": "5: return stock_valido", "return": True},
            {"from": "SERVICE", "to": "REPO", "y": 345, "text": "6: ejecutar_movimiento_inventario(mov_data)"},
            {"from": "REPO", "to": "SERVICE", "y": 365, "text": "7: return nuevo_stock, id_movimiento", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 385, "text": "8: registrar_bitacora(MOVIMIENTO_INVENTARIO, id)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 405, "text": "9: respuesta_exitosa(\"Stock actualizado\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 420, "text": "10: ActualizarTablaKardex()", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "11: respuesta_error(\"Stock insuficiente\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "12: MostrarAlerta(\"No hay stock suficiente para la salida\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "13: GET /api/inventario/kardex?id_variante={id}"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "14: consultar_kardex_variante(id_variante, id_sucursal)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "15: get_kardex_movimientos(id_variante, id_sucursal)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "16: return movimientos_kardex", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "17: respuesta_kardex(movimientos_kardex)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "18: RenderizarKardex(movimientos_kardex)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "19: ConfirmarOperacionInventario()", "return": True}
        ]
    },

    # 12. CU_W23
    {
        "filename": "CU_W23_Gestionar_Disponibilidad_Prendas_Secuencia",
        "title": "CU/W23: Gestionar disponibilidad de prendas",
        "actor_name": "ADMINISTRADOR",
        "iu_name": "IU_Disponibilidad",
        "controller_name": "disponibilidad_routes",
        "service_name": "disponibilidad_services",
        "repo_name": "inventario_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 295, "h": 40},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 355, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[ESTADO DE DISPONIBILIDAD ACTUALIZADO]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[REGISTRO O SUCURSAL NO ENCONTRADA]"
            },
            {
                "type": "opt", "guard": "[MONITOREO DE ALERTAS DE STOCK MÍNIMO]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: ModificarRegla(id_variante, id_sucursal, estado)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: PUT /api/inventario/disponibilidad"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: modificar_estado_disponibilidad(payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 300, "text": "4: actualizar_disponibilidad_db(id_var, id_suc, estado)"},
            {"from": "REPO", "to": "SERVICE", "y": 330, "text": "5: return filas_afectadas", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 360, "text": "6: registrar_bitacora(DISPONIBILIDAD, id_var)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 390, "text": "7: respuesta_exitosa(\"Disponibilidad guardada\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 410, "text": "8: RefrescarMatrizDisponibilidad()", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "9: respuesta_error(\"Registro no encontrado\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "10: MostrarAlerta(\"Error al actualizar disponibilidad\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "11: GET /api/inventario/alertas-stock-minimo"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "12: obtener_alertas_quiebre_stock(id_empresa)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "13: get_prendas_bajo_stock(id_empresa)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "14: return alertas_stock", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "15: respuesta_alertas(alertas_stock)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "16: MostrarInsigniasAlerta(alertas_stock)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "17: CerrarPanelDisponibilidad()", "return": True}
        ]
    },

    # 13. CU_W24
    {
        "filename": "CU_W24_Registrar_Venta_Presencial_Secuencia",
        "title": "CU/W24: Registrar venta presencial",
        "actor_name": "CAJERO",
        "iu_name": "IU_POSVenta",
        "controller_name": "pos_routes",
        "service_name": "pos_services",
        "repo_name": "pos_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 290, "h": 70},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 380, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[VENTA REGISTRADA CON ÉXITO]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[STOCK INSUFICIENTE EN CAJA]"
            },
            {
                "type": "opt", "guard": "[IMPRIMIR TICKET DE VENTA FISCAL / POS]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: ConfirmarVenta(items, cliente, total)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: POST /api/pos/ventas"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: procesar_venta_presencial(id_sesion, payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 295, "text": "4: verificar_stock_caja(items, id_sucursal)"},
            {"from": "REPO", "to": "SERVICE", "y": 320, "text": "5: return stock_ok", "return": True},
            {"from": "SERVICE", "to": "REPO", "y": 345, "text": "6: insertar_venta_y_detalles(venta_data)"},
            {"from": "REPO", "to": "SERVICE", "y": 365, "text": "7: return id_venta, nro_ticket", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 385, "text": "8: registrar_bitacora(VENTA_POS, id_venta)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 405, "text": "9: respuesta_exitosa(nro_ticket)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 420, "text": "10: MostrarCobroExitoso(nro_ticket)", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "11: respuesta_error(\"Sin stock en tienda\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "12: MostrarAlerta(\"Stock insuficiente para completar venta\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "13: GET /api/pos/ventas/{id}/ticket"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "14: generar_ticket_venta_pos(id_venta)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "15: get_datos_ticket_venta(id_venta)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "16: return ticket_texto_plano", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "17: respuesta_impresion(ticket_data)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "18: EnviarComandoImpresora(ticket_data)", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "19: PrepararNuevaVenta()", "return": True}
        ]
    },

    # 14. CU_W25
    {
        "filename": "CU_W25_Atender_Reservas_Secuencia",
        "title": "CU/W25: Atender reservas",
        "actor_name": "ENCARGADO SUCURSAL",
        "iu_name": "IU_AtencionReservas",
        "controller_name": "reservas_routes",
        "service_name": "reservas_services",
        "repo_name": "reservas_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 295, "h": 40},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 680, "h": 25}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[RESERVA ENCONTRADA Y VIGENTE]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[RESERVA EXPIRADA O CÓDIGO NO VÁLIDO]"
            },
            {
                "type": "opt", "guard": "[CONFIRMAR ENTREGA Y CONVERSIÓN A VENTA]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: BuscarReserva(codigo_reserva)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: GET /api/reservas/buscar?codigo={cod}"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: consultar_reserva_por_codigo(codigo)"},
            {"from": "SERVICE", "to": "REPO", "y": 300, "text": "4: obtener_reserva_db(codigo)"},
            {"from": "REPO", "to": "SERVICE", "y": 330, "text": "5: return datos_reserva", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 370, "text": "6: respuesta_exitosa(datos_reserva)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 400, "text": "7: MostrarDetalleParaEntrega(datos_reserva)", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "8: respuesta_error(\"Reserva no encontrada o expirada\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "9: MostrarAlerta(\"El código no tiene reserva activa\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "10: POST /api/reservas/{id}/entregar"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "11: completar_entrega_reserva(id_reserva)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "12: convertir_reserva_en_venta(id_reserva)"},
            {"from": "REPO", "to": "SERVICE", "y": 680, "text": "13: return entrega_exitosa", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 695, "text": "14: registrar_bitacora(ENTREGA_RESERVA, id)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 715, "text": "15: respuesta_entrega()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "16: MostrarMensaje(\"Reserva entregada y liquidada\")", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "17: FinalizarAtencionReserva()", "return": True}
        ]
    },

    # 15. CU_W27
    {
        "filename": "CU_W27_Procesar_Pago_Electronico_Secuencia",
        "title": "CU/W27: Procesar pago electrónico",
        "actor_name": "CLIENTE",
        "iu_name": "IU_PasarelaPago",
        "controller_name": "pago_routes",
        "service_name": "pasarela_services",
        "repo_name": "pago_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 290, "h": 70},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 380, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[TRANSACCIÓN APROBADA POR PASARELA]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[TRANSACCIÓN RECHAZADA O FONDOS INSUFICIENTES]"
            },
            {
                "type": "opt", "guard": "[CONFIRMACIÓN ASINCRÓNICA VÍA WEBHOOK]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: IniciarPago(id_pedido, metodo, datos_tarjeta)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: POST /api/pagos/procesar-electronico"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: procesar_transaccion_pasarela(payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 295, "text": "4: validar_y_registrar_intento_pago(id_pedido, monto)"},
            {"from": "REPO", "to": "SERVICE", "y": 320, "text": "5: return token_transaccion", "return": True},
            {"from": "SERVICE", "to": "REPO", "y": 345, "text": "6: registrar_pago_aprobado_db(id_pedido, cod_aprob)"},
            {"from": "REPO", "to": "SERVICE", "y": 365, "text": "7: return id_pago", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 385, "text": "8: registrar_bitacora(PAGO_APROBADO, id_pago)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 405, "text": "9: respuesta_exitosa(cod_aprobacion)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 420, "text": "10: MostrarComprobanteTransaccion(cod_aprob)", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "11: respuesta_error(\"Pago rechazado por el banco\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "12: MostrarAlerta(\"Transacción rechazada por el emisor\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "13: POST /api/pagos/webhook-callback"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "14: verificar_firma_webhook(payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "15: sincronizar_estado_pago_db(id_pedido)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "16: return estado_sincronizado", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "17: respuesta_webhook_ack()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "18: ActualizarEstadoPagoEnPantalla()", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "19: FinalizarPagoElectronico()", "return": True}
        ]
    },

    # 16. CU_W28
    {
        "filename": "CU_W28_Procesar_Pago_Caja_Secuencia",
        "title": "CU/W28: Procesar pago en caja",
        "actor_name": "CAJERO",
        "iu_name": "IU_CobroCaja",
        "controller_name": "caja_routes",
        "service_name": "caja_services",
        "repo_name": "caja_pago_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 290, "h": 70},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 380, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[MONTO SUFICIENTE Y CAMBIO CALCULADO]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[MONTO RECIBIDO MENOR AL TOTAL]"
            },
            {
                "type": "opt", "guard": "[REGISTRO DE ARQUEO O DENOMINACIONES DE CAJA]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: RegistrarCobro(id_venta, monto_recibido, metodo)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: POST /api/caja/pagos"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: registrar_pago_caja(id_sesion, payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 295, "text": "4: calcular_cambio_efectivo(total, monto_recibido)"},
            {"from": "REPO", "to": "SERVICE", "y": 320, "text": "5: return cambio", "return": True},
            {"from": "SERVICE", "to": "REPO", "y": 345, "text": "6: insertar_pago_caja_db(id_venta, monto, cambio)"},
            {"from": "REPO", "to": "SERVICE", "y": 365, "text": "7: return id_pago", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 385, "text": "8: registrar_bitacora(COBRO_CAJA, id_pago)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 405, "text": "9: respuesta_exitosa(cambio, id_pago)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 420, "text": "10: MostrarCambioAlCajero(cambio)", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "11: respuesta_error(\"Monto insuficiente\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "12: MostrarAlerta(\"Monto recibido menor al importe de venta\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "13: POST /api/caja/arqueo"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "14: registrar_arqueo_caja(id_sesion, denominaciones)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "15: guardar_arqueo_denominaciones_db(id_sesion, data)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "16: return arqueo_guardado", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "17: respuesta_arqueo()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "18: ImprimirResumenCierreCaja()", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "19: FinalizarCobroCaja()", "return": True}
        ]
    },

    # 17. CU_W29
    {
        "filename": "CU_W29_Emitir_Comprobante_Venta_Secuencia",
        "title": "CU/W29: Emitir comprobante de venta",
        "actor_name": "CAJERO",
        "iu_name": "IU_Comprobante",
        "controller_name": "comprobante_routes",
        "service_name": "comprobante_services",
        "repo_name": "comprobante_repos",
        "bitacora_name": "T_BITACORA",
        "activations": [
            {"target": "IU", "y": 160, "h": 615},
            {"target": "CONTROLLER", "y": 195, "h": 325},
            {"target": "CONTROLLER", "y": 590, "h": 155},
            {"target": "SERVICE", "y": 225, "h": 270},
            {"target": "SERVICE", "y": 620, "h": 105},
            {"target": "REPO", "y": 290, "h": 70},
            {"target": "REPO", "y": 650, "h": 40},
            {"target": "BITACORA", "y": 380, "h": 30}
        ],
        "fragments": [
            {
                "type": "alt", "guard": "[DATOS FISCALES VÁLIDOS Y CUFD GENERADO]",
                "x": 40, "y": 260, "w": 1250, "h": 280,
                "divider_y": 425, "guard2": "[ERROR EN VALIDACIÓN FISCAL O TRIBUTARIA]"
            },
            {
                "type": "opt", "guard": "[ENVIAR COMPROBANTE POR CORREO ELECTRÓNICO]",
                "x": 40, "y": 555, "w": 1250, "h": 205
            }
        ],
        "messages": [
            {"from": "ACTOR", "to": "IU", "y": 165, "text": "1: SolicitarComprobante(id_venta, tipo, datos_fiscales)"},
            {"from": "IU", "to": "CONTROLLER", "y": 200, "text": "2: POST /api/comprobantes/emitir"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 230, "text": "3: emitir_comprobante_fiscal(payload)"},
            {"from": "SERVICE", "to": "REPO", "y": 295, "text": "4: validar_datos_facturacion(nit, razon_social)"},
            {"from": "REPO", "to": "SERVICE", "y": 320, "text": "5: return datos_validos", "return": True},
            {"from": "SERVICE", "to": "REPO", "y": 345, "text": "6: insertar_comprobante_db(id_venta, tipo, nro, cufd)"},
            {"from": "REPO", "to": "SERVICE", "y": 365, "text": "7: return id_comprobante, nro_autorizado", "return": True},
            {"from": "SERVICE", "to": "BITACORA", "y": 385, "text": "8: registrar_bitacora(EMITIR_COMPROBANTE, id)", "tx": 910},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 405, "text": "9: respuesta_exitosa(nro_autorizado)", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 420, "text": "10: VistaPreviaComprobante(pdf_url)", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 465, "text": "11: respuesta_error(\"Falla de validación fiscal\")", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 500, "text": "12: MostrarAlerta(\"No se pudo autorizar el comprobante\")", "return": True},
            {"from": "IU", "to": "CONTROLLER", "y": 595, "text": "13: POST /api/comprobantes/{id}/enviar-correo"},
            {"from": "CONTROLLER", "to": "SERVICE", "y": 625, "text": "14: enviar_email_comprobante(id, email_cliente)"},
            {"from": "SERVICE", "to": "REPO", "y": 655, "text": "15: get_pdf_comprobante_stream(id)"},
            {"from": "REPO", "to": "SERVICE", "y": 685, "text": "16: return stream_ok", "return": True},
            {"from": "SERVICE", "to": "CONTROLLER", "y": 710, "text": "17: respuesta_envio_email()", "return": True},
            {"from": "CONTROLLER", "to": "IU", "y": 735, "text": "18: NotificarEnvioExitoso()", "return": True},
            {"from": "IU", "to": "ACTOR", "y": 760, "text": "19: FinalizarEmisionComprobante()", "return": True}
        ]
    }
]

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"🚀 Iniciando generación de los {len(DIAGRAMAS)} Diagramas de Secuencia UML...")

    for idx, diag in enumerate(DIAGRAMAS, 1):
        fname = diag["filename"]
        svg_path = os.path.join(out_dir, f"{fname}.svg")
        png_path = os.path.join(out_dir, f"{fname}.png")

        svg_content = render_sequence_svg(diag)
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        cairosvg.svg2png(bytestring=svg_content.encode("utf-8"), write_to=png_path, scale=2.0)
        print(f" [{idx:02d}/{len(DIAGRAMAS)}] ✅ Generado: {fname}.svg y {fname}.png")

    print(f"\n🎉 ¡Todos los {len(DIAGRAMAS)} diagramas de secuencia generados y exportados exitosamente en {out_dir}!")

if __name__ == "__main__":
    main()
