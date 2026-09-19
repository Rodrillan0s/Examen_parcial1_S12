#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de los 17 Diagramas de Tiempo UML 2.5 (SI2 - UAGRM)
Iteración Actual: E-Commerce Multi-Tenant

Abarca los 25 Casos de Uso del sistema:
- 8 Casos de Uso Unificados Web / Móvil:
  1. CU05_WM: Buscar y filtrar productos
  2. CU06_WM: Consultar detalle de producto
  3. CU07_WM: Consultar disponibilidad por sucursal
  4. CU08_WM: Gestionar carrito de compras
  5. CU09_WM: Realizar compra
  6. CU10_WM: Gestionar reservas
  7. CU11_WM: Consultar pedidos e historial
  8. CU26_M15_WM: Mostrar ubicaciones de sucursales
- 9 Casos de Uso Específicos Web:
  9.  CU_W20: Gestionar temporadas y colecciones
  10. CU_W21: Gestionar proveedores
  11. CU_W22: Gestionar inventario
  12. CU_W23: Gestionar disponibilidad de prendas
  13. CU_W24: Registrar venta presencial POS
  14. CU_W25: Atender reservas en sucursal
  15. CU_W27: Procesar pago electrónico
  16. CU_W28: Procesar pago en caja
  17. CU_W29: Emitir comprobante de venta

Directiva de cátedra aplicada:
- En consultas / búsquedas / filtros del cliente NO existe bitácora.
- En transacciones y mutaciones de estado se realizan las validaciones y persistencia correspondiente.
- Nombres de funciones reales (Controller -> Service -> Repository).
- Estilo UML 2.5 formal con pestaña "sd [Título]", niveles de estado, formas de onda ortogonales,
  estímulos con flechas sincrónicas/retorno y marcas de tiempo discretas t0..tn.
"""

import os
import sys
import xml.sax.saxutils
import cairosvg

def escape_xml(text):
    return xml.sax.saxutils.escape(str(text))

def render_timing_svg(diag):
    title = diag["title"]
    time_x = diag["time_x"]
    lifelines = diag["lifelines"]
    events = diag.get("events", [])

    w = diag.get("canvas_width", 1460)
    state_step_h = 24
    gap_between_lfs = 18

    # Calcular posiciones verticales de las líneas de vida
    y_current = 70
    lf_layout = []
    for lf_idx, lf in enumerate(lifelines):
        states = lf["states"]
        num_states = len(states)
        box_h = num_states * state_step_h + 16
        y_top = y_current
        
        state_y = {}
        for s_idx, st in enumerate(states):
            sy = y_top + 34 + s_idx * state_step_h
            state_y[s_idx] = sy
            
        lf_layout.append({
            "name": lf["name"],
            "y_top": y_top,
            "box_h": box_h,
            "states": states,
            "state_y": state_y,
            "wave": lf["wave"]
        })
        y_current += box_h + gap_between_lfs

    # Altura del canvas calculada dinámicamente
    y_bottom_grid = y_current + 10
    h = y_bottom_grid + 70

    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n')

    # Marcadores de flecha
    parts.append('  <defs>\n')
    parts.append('    <marker id="arrow_call" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">\n')
    parts.append('      <path d="M 0 1.5 L 7 4.5 L 0 7.5 Z" fill="#000000"/>\n')
    parts.append('    </marker>\n')
    parts.append('    <marker id="arrow_ret" markerWidth="9" markerHeight="9" refX="2" refY="4.5" orient="auto">\n')
    parts.append('      <path d="M 7 1.5 L 2 4.5 L 7 7.5" fill="none" stroke="#000000" stroke-width="1.3"/>\n')
    parts.append('    </marker>\n')
    parts.append('  </defs>\n\n')

    # Fondo blanco
    parts.append(f'  <rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>\n')

    # Marco Exterior UML 2.5 con pestaña superior izquierda
    tab_title = f"sd {title}"
    tab_w = len(tab_title) * 8.2 + 36
    if tab_w < 260:
        tab_w = 260
    tab_h = 28

    parts.append('  <!-- Marco Exterior UML 2.5 -->\n')
    parts.append(f'  <rect x="15" y="15" width="{w - 30}" height="{h - 30}" fill="none" stroke="#000000" stroke-width="1.3"/>\n')
    parts.append(f'  <path d="M 15 15 L {15 + tab_w} 15 L {15 + tab_w} {15 + tab_h - 8} L {15 + tab_w - 8} {15 + tab_h} L 15 {15 + tab_h} Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>\n')
    parts.append(f'  <text x="25" y="33" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="bold" fill="#000000">{escape_xml(tab_title)}</text>\n\n')

    # Líneas de tiempo verticales
    parts.append('  <!-- Marcas de Tiempo Verticales -->\n  <g id="time_grid">\n')
    for t_name, tx in time_x.items():
        parts.append(f'    <line x1="{tx}" y1="60" x2="{tx}" y2="{y_bottom_grid}" stroke="#dedede" stroke-width="1" stroke-dasharray="3,3"/>\n')
        parts.append(f'    <text x="{tx}" y="{y_bottom_grid + 20}" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="bold" fill="#333333" text-anchor="middle">{t_name}</text>\n')
    parts.append('  </g>\n\n')

    # Eje horizontal temporal
    parts.append(f'  <line x1="240" y1="{y_bottom_grid + 4}" x2="{w - 55}" y2="{y_bottom_grid + 4}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_call)"/>\n')
    parts.append(f'  <text x="{w - 48}" y="{y_bottom_grid + 8}" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="bold" fill="#000000">Tiempo (t)</text>\n\n')

    # Líneas de vida
    for lf in lf_layout:
        y_top = lf["y_top"]
        name = lf["name"]
        states = lf["states"]
        box_h = lf["box_h"]

        parts.append(f'  <!-- Línea de vida: {name} -->\n')
        parts.append(f'  <rect x="25" y="{y_top}" width="{w - 50}" height="{box_h}" fill="none" stroke="#cccccc" stroke-width="0.8"/>\n')
        parts.append(f'  <rect x="25" y="{y_top}" width="215" height="{box_h}" fill="#f8f9fa" stroke="#cccccc" stroke-width="0.8"/>\n')
        parts.append(f'  <text x="35" y="{y_top + 18}" font-family="Arial, Helvetica, sans-serif" font-size="11.5" font-weight="bold" fill="#000000">{escape_xml(name)}</text>\n')

        # Niveles de estado
        for s_idx, st in enumerate(states):
            sy = lf["state_y"][s_idx]
            parts.append(f'    <text x="230" y="{sy + 4}" font-family="Arial, Helvetica, sans-serif" font-size="9.5" fill="#444444" text-anchor="end">{escape_xml(st)}</text>\n')
            parts.append(f'    <line x1="240" y1="{sy}" x2="{w - 30}" y2="{sy}" stroke="#f0f0f0" stroke-width="0.8"/>\n')

        # Forma de onda
        wave = lf["wave"]
        path_segments = []
        prev_sy = None

        for seg_idx, (t_start, t_end, s_idx) in enumerate(wave):
            x_s = time_x[t_start]
            x_e = time_x[t_end]
            curr_sy = lf["state_y"][s_idx]

            if prev_sy is None:
                path_segments.append(f'M {x_s} {curr_sy} L {x_e} {curr_sy}')
            else:
                if prev_sy != curr_sy:
                    path_segments.append(f'L {x_s} {curr_sy} L {x_e} {curr_sy}')
                else:
                    path_segments.append(f'L {x_e} {curr_sy}')

            prev_sy = curr_sy

        waveform_d = " ".join(path_segments)
        parts.append(f'    <path d="{waveform_d}" fill="none" stroke="#004499" stroke-width="2.3" stroke-linejoin="round"/>\n\n')

    # Helper para buscar lifeline por nombre
    def get_lf(lf_ref):
        if isinstance(lf_ref, int):
            return lf_layout[lf_ref]
        for l in lf_layout:
            if l["name"] == lf_ref:
                return l
        raise ValueError(f"Lifeline not found: {lf_ref}")

    # Helper para resolver nivel Y de un estado
    def resolve_y(lf_ref, state_ref):
        l = get_lf(lf_ref)
        if isinstance(state_ref, int):
            return l["state_y"][state_ref]
        for s_idx, s_name in enumerate(l["states"]):
            if s_name == state_ref:
                return l["state_y"][s_idx]
        raise ValueError(f"State not found: {state_ref} in {l['name']}")

    # Mensajes entre líneas de vida
    parts.append('  <!-- Mensajes Inter-Línea de Vida (Estímulos de Transición) -->\n  <g id="messages">\n')
    for ev in events:
        ev_x = ev["x"] if isinstance(ev["x"], (int, float)) else time_x[ev["x"]]
        if "x_offset" in ev:
            ev_x += ev["x_offset"]

        y1 = resolve_y(ev["from_lf"], ev["from_state"])
        y2 = resolve_y(ev["to_lf"], ev["to_state"])
        lbl = ev["label"]
        mtype = ev.get("type", "call")

        if mtype == "call":
            marker = "url(#arrow_call)"
            stroke = "#000000"
            dash = ""
        else:
            marker = "url(#arrow_ret)"
            stroke = "#000000"
            dash = 'stroke-dasharray="3,3"'

        parts.append(f'    <line x1="{ev_x}" y1="{y1}" x2="{ev_x}" y2="{y2}" stroke="{stroke}" stroke-width="1.3" {dash} marker-end="{marker}"/>\n')
        mid_y = (y1 + y2) / 2
        lbl_w = len(lbl) * 6.4 + 10
        lbl_x = ev_x + 6
        if lbl_x + lbl_w > w - 35:
            lbl_x = ev_x - lbl_w - 6

        parts.append(f'    <rect x="{lbl_x}" y="{mid_y - 8}" width="{lbl_w}" height="16" fill="#ffffff" stroke="#cccccc" stroke-width="0.6" rx="3" opacity="0.95"/>\n')
        parts.append(f'    <text x="{lbl_x + 4}" y="{mid_y + 4}" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="bold" fill="#000000">{escape_xml(lbl)}</text>\n')

    parts.append('  </g>\n\n')

    # Leyenda
    parts.append('  <!-- Leyenda -->\n  <g id="legend">\n')
    parts.append(f'    <rect x="25" y="{y_bottom_grid + 5}" width="215" height="38" fill="#fafafa" stroke="#dddddd" stroke-width="0.8"/>\n')
    parts.append(f'    <line x1="32" y1="{y_bottom_grid + 17}" x2="58" y2="{y_bottom_grid + 17}" stroke="#004499" stroke-width="2.2"/>\n')
    parts.append(f'    <text x="66" y="{y_bottom_grid + 20}" font-family="Arial, Helvetica, sans-serif" font-size="9" fill="#333333">Forma de onda de estado</text>\n')
    parts.append(f'    <line x1="32" y1="{y_bottom_grid + 31}" x2="58" y2="{y_bottom_grid + 31}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_call)"/>\n')
    parts.append(f'    <text x="66" y="{y_bottom_grid + 34}" font-family="Arial, Helvetica, sans-serif" font-size="9" fill="#333333">Estímulo / Mensaje</text>\n')
    parts.append('  </g>\n\n')

    parts.append('</svg>\n')
    return "".join(parts)


# ==============================================================================
# DEFINICIÓN DE LOS 17 DIAGRAMAS DE TIEMPO UML 2.5
# ==============================================================================

DIAGRAMAS_TIEMPO = [
    # --------------------------------------------------------------------------
    # 01. CU05 W/M - Buscar y filtrar productos (Consulta pública, SIN bitácora)
    # --------------------------------------------------------------------------
    {
        "id": "CU05_WM",
        "file_name": "CU05_WM_Buscar_Filtrar_Productos_Tiempo.svg",
        "png_name": "CU05_WM_Buscar_Filtrar_Productos_Tiempo.png",
        "title": "CU05 W/M - Buscar y filtrar productos",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CLIENTE",
                "states": ["Navegando", "SeleccionandoFiltros", "EsperandoResultados", "VisualizandoCatalogo"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_Catalogo",
                "states": ["CatalogoVisible", "CapturandoEntrada", "EnviandoPeticion", "RenderizandoGrid"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t6", 2), ("t6", "t8", 3)]
            },
            {
                "name": "catalogo_routes",
                "states": ["EnEspera", "RecepcionandoParams", "FormateandoRespuesta"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "catalogo_services",
                "states": ["Ocioso", "ProcesandoFiltros", "RetornandoDTO"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "catalogo_repos",
                "states": ["EnEspera", "EjecutandoQuerySQL", "DatasetDisponible"],
                "wave": [("t0", "t4", 0), ("t4", "t5", 1), ("t5", "t6", 2), ("t6", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CLIENTE", "from_state": "SeleccionandoFiltros", "to_lf": "IU_Catalogo", "to_state": "CapturandoEntrada", "label": "1: SeleccionarFiltros(categoria, precio)", "type": "call"},
            {"x": "t2", "from_lf": "IU_Catalogo", "from_state": "EnviandoPeticion", "to_lf": "catalogo_routes", "to_state": "RecepcionandoParams", "label": "2: GET /api/catalogo/productos", "type": "call"},
            {"x": "t3", "from_lf": "catalogo_routes", "from_state": "RecepcionandoParams", "to_lf": "catalogo_services", "to_state": "ProcesandoFiltros", "label": "3: filtrar_catalogo(criterios)", "type": "call"},
            {"x": "t4", "from_lf": "catalogo_services", "from_state": "ProcesandoFiltros", "to_lf": "catalogo_repos", "to_state": "EjecutandoQuerySQL", "label": "4: listar_catalogo_publico(filtros)", "type": "call"},
            {"x": "t5", "from_lf": "catalogo_repos", "from_state": "DatasetDisponible", "to_lf": "catalogo_services", "to_state": "RetornandoDTO", "label": "5: return lista_productos", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "catalogo_services", "from_state": "RetornandoDTO", "to_lf": "catalogo_routes", "to_state": "FormateandoRespuesta", "label": "6: return respuesta_exitosa(productos)", "type": "ret"},
            {"x": "t6", "from_lf": "catalogo_routes", "from_state": "FormateandoRespuesta", "to_lf": "IU_Catalogo", "to_state": "RenderizandoGrid", "label": "7: RenderizarCatalogo(productos)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_Catalogo", "from_state": "RenderizandoGrid", "to_lf": "CLIENTE", "to_state": "VisualizandoCatalogo", "label": "8: MostrarGridProductos()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 02. CU06 W/M - Consultar detalle de producto (Consulta, SIN bitácora)
    # --------------------------------------------------------------------------
    {
        "id": "CU06_WM",
        "file_name": "CU06_WM_Consultar_Detalle_Producto_Tiempo.svg",
        "png_name": "CU06_WM_Consultar_Detalle_Producto_Tiempo.png",
        "title": "CU06 W/M - Consultar detalle de producto",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CLIENTE",
                "states": ["ExplorandoCatalogo", "SeleccionandoPrenda", "EsperandoFicha", "ViendoDetallePrenda"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_DetalleProducto",
                "states": ["VistaInactiva", "CargandoSkeleton", "RenderizandoVariantes", "FichaCompletaVisible"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "catalogo_routes",
                "states": ["EnEspera", "ValidandoIdProducto", "RetornandoPayloadJSON"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "productos_services",
                "states": ["Ocioso", "ConsolidandoVariantesImagenes", "EstructurandoDetalleDTO"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "catalogo_repos",
                "states": ["EnEspera", "ConsultandoProductoYVariantes", "DatasetRecuperado"],
                "wave": [("t0", "t4", 0), ("t4", "t5", 1), ("t5", "t6", 2), ("t6", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CLIENTE", "from_state": "SeleccionandoPrenda", "to_lf": "IU_DetalleProducto", "to_state": "CargandoSkeleton", "label": "1: SeleccionarPrenda(id_producto)", "type": "call"},
            {"x": "t2", "from_lf": "IU_DetalleProducto", "from_state": "CargandoSkeleton", "to_lf": "catalogo_routes", "to_state": "ValidandoIdProducto", "label": "2: GET /api/catalogo/productos/{id}", "type": "call"},
            {"x": "t3", "from_lf": "catalogo_routes", "from_state": "ValidandoIdProducto", "to_lf": "productos_services", "to_state": "ConsolidandoVariantesImagenes", "label": "3: obtener_detalle_producto(id_producto)", "type": "call"},
            {"x": "t4", "from_lf": "productos_services", "from_state": "ConsolidandoVariantesImagenes", "to_lf": "catalogo_repos", "to_state": "ConsultandoProductoYVariantes", "label": "4: obtener_producto_por_id(id_producto)", "type": "call"},
            {"x": "t5", "from_lf": "catalogo_repos", "from_state": "DatasetRecuperado", "to_lf": "productos_services", "to_state": "EstructurandoDetalleDTO", "label": "5: return producto_info, variantes, imagenes", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "productos_services", "from_state": "EstructurandoDetalleDTO", "to_lf": "catalogo_routes", "to_state": "RetornandoPayloadJSON", "label": "6: return detalle_dto", "type": "ret"},
            {"x": "t6", "from_lf": "catalogo_routes", "from_state": "RetornandoPayloadJSON", "to_lf": "IU_DetalleProducto", "to_state": "RenderizandoVariantes", "label": "7: RenderizarDetalle(tallas, colores, stock)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_DetalleProducto", "from_state": "RenderizandoVariantes", "to_lf": "CLIENTE", "to_state": "ViendoDetallePrenda", "label": "8: MostrarFichaTecnica()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 03. CU07 W/M - Consultar disponibilidad por sucursal (Consulta, SIN bitácora)
    # --------------------------------------------------------------------------
    {
        "id": "CU07_WM",
        "file_name": "CU07_WM_Consultar_Disponibilidad_Sucursal_Tiempo.svg",
        "png_name": "CU07_WM_Consultar_Disponibilidad_Sucursal_Tiempo.png",
        "title": "CU07 W/M - Consultar disponibilidad por sucursal",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CLIENTE",
                "states": ["ViendoProducto", "EligiendoTallaColor", "EsperandoStockSucursales", "VisualizandoMapaDisponibilidad"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_StockSucursal",
                "states": ["ModalCerrado", "MostrandoLoaderSucursales", "PintandoListaSucursales", "ModalActivo"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "catalogo_routes",
                "states": ["EnEspera", "VerificandoParametrosVariante", "RespondiendoArraySucursales"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "inventario_services",
                "states": ["Ocioso", "CalculandoStockPorTienda", "FormateandoDisponibilidad"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "inventario_repos",
                "states": ["EnEspera", "ConsultandoKardexYSucursales", "StockConsolidado"],
                "wave": [("t0", "t4", 0), ("t4", "t5", 1), ("t5", "t6", 2), ("t6", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CLIENTE", "from_state": "EligiendoTallaColor", "to_lf": "IU_StockSucursal", "to_state": "MostrandoLoaderSucursales", "label": "1: ConsultarStockSucursales(id_variante)", "type": "call"},
            {"x": "t2", "from_lf": "IU_StockSucursal", "from_state": "MostrandoLoaderSucursales", "to_lf": "catalogo_routes", "to_state": "VerificandoParametrosVariante", "label": "2: GET /api/catalogo/stock-sucursales", "type": "call"},
            {"x": "t3", "from_lf": "catalogo_routes", "from_state": "VerificandoParametrosVariante", "to_lf": "inventario_services", "to_state": "CalculandoStockPorTienda", "label": "3: consultar_stock_sucursales(id_variante)", "type": "call"},
            {"x": "t4", "from_lf": "inventario_services", "from_state": "CalculandoStockPorTienda", "to_lf": "inventario_repos", "to_state": "ConsultandoKardexYSucursales", "label": "4: obtener_stock_sucursales_producto(id_variante)", "type": "call"},
            {"x": "t5", "from_lf": "inventario_repos", "from_state": "StockConsolidado", "to_lf": "inventario_services", "to_state": "FormateandoDisponibilidad", "label": "5: return lista_sucursales_stock", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "inventario_services", "from_state": "FormateandoDisponibilidad", "to_lf": "catalogo_routes", "to_state": "RespondiendoArraySucursales", "label": "6: return datos_disponibilidad", "type": "ret"},
            {"x": "t6", "from_lf": "catalogo_routes", "from_state": "RespondiendoArraySucursales", "to_lf": "IU_StockSucursal", "to_state": "PintandoListaSucursales", "label": "7: RenderizarDisponibilidad(sucursales)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_StockSucursal", "from_state": "PintandoListaSucursales", "to_lf": "CLIENTE", "to_state": "VisualizandoMapaDisponibilidad", "label": "8: MostrarSucursalesConStock()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 04. CU08 W/M - Gestionar carrito de compras (Mutación de items del carrito)
    # --------------------------------------------------------------------------
    {
        "id": "CU08_WM",
        "file_name": "CU08_WM_Gestionar_Carrito_Compras_Tiempo.svg",
        "png_name": "CU08_WM_Gestionar_Carrito_Compras_Tiempo.png",
        "title": "CU08 W/M - Gestionar carrito de compras",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CLIENTE",
                "states": ["Navegando", "AgregandoPrenda", "EsperandoConfirmacion", "CarritoActualizado"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_Carrito",
                "states": ["DrawerCerrado", "AnimandoBotonAgregar", "ActualizandoBadgeContador", "DrawerAbiertoConTotales"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "carrito_routes",
                "states": ["EnEspera", "DecodificandoItemPayload", "RespondiendoEstadoCarrito"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "carrito_services",
                "states": ["Ocioso", "ValidandoStockMaximo", "PersistiendoItemEnCarrito"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "carrito_repos",
                "states": ["EnEspera", "VerificandoStockDisponible", "UpsertItemCarrito"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CLIENTE", "from_state": "AgregandoPrenda", "to_lf": "IU_Carrito", "to_state": "AnimandoBotonAgregar", "label": "1: AgregarItem(id_variante, cantidad)", "type": "call"},
            {"x": "t2", "from_lf": "IU_Carrito", "from_state": "AnimandoBotonAgregar", "to_lf": "carrito_routes", "to_state": "DecodificandoItemPayload", "label": "2: POST /api/carrito/items", "type": "call"},
            {"x": "t3", "from_lf": "carrito_routes", "from_state": "DecodificandoItemPayload", "to_lf": "carrito_services", "to_state": "ValidandoStockMaximo", "label": "3: agregar_item_carrito(id_cliente, payload)", "type": "call"},
            {"x": "t4", "from_lf": "carrito_services", "from_state": "ValidandoStockMaximo", "to_lf": "carrito_repos", "to_state": "VerificandoStockDisponible", "label": "4: verificar_stock_disponible(id_variante, cant)", "type": "call"},
            {"x": "t5", "from_lf": "carrito_repos", "from_state": "UpsertItemCarrito", "to_lf": "carrito_services", "to_state": "PersistiendoItemEnCarrito", "label": "5: return stock_ok, item_guardado", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "carrito_services", "from_state": "PersistiendoItemEnCarrito", "to_lf": "carrito_routes", "to_state": "RespondiendoEstadoCarrito", "label": "6: return carrito_actualizado", "type": "ret"},
            {"x": "t6", "from_lf": "carrito_routes", "from_state": "RespondiendoEstadoCarrito", "to_lf": "IU_Carrito", "to_state": "ActualizandoBadgeContador", "label": "7: ActualizarBadgeCarrito(totales)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_Carrito", "from_state": "ActualizandoBadgeContador", "to_lf": "CLIENTE", "to_state": "CarritoActualizado", "label": "8: NotificarPrendaAgregada()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 05. CU09 W/M - Realizar compra (Checkout y orden, Transaccional)
    # --------------------------------------------------------------------------
    {
        "id": "CU09_WM",
        "file_name": "CU09_WM_Realizar_Compra_Tiempo.svg",
        "png_name": "CU09_WM_Realizar_Compra_Tiempo.png",
        "title": "CU09 W/M - Realizar compra",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CLIENTE",
                "states": ["CompletandoCheckout", "ConfirmandoOrden", "EsperandoConfirmacionPedido", "OrdenConfirmada"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_Checkout",
                "states": ["FormularioCheckout", "BloqueandoBotonPagar", "ProcesandoOrdenLoader", "PantallaExitoOrden"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "pedidos_routes",
                "states": ["EnEspera", "ValidandoAuthYPayload", "EmitiendoRespuestaHTTP201"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "pedidos_services",
                "states": ["Ocioso", "IniciandoTxCheckout", "RegistrandoBitacoraCompra", "RetornandoOrdenCreada"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "pedidos_repos",
                "states": ["EnEspera", "CreandoPedidoYDetalles", "BloqueandoStockKardex"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CLIENTE", "from_state": "ConfirmandoOrden", "to_lf": "IU_Checkout", "to_state": "BloqueandoBotonPagar", "label": "1: ConfirmarCompra(tipo_entrega, metodo_pago)", "type": "call"},
            {"x": "t2", "from_lf": "IU_Checkout", "from_state": "BloqueandoBotonPagar", "to_lf": "pedidos_routes", "to_state": "ValidandoAuthYPayload", "label": "2: POST /api/pedidos/checkout", "type": "call"},
            {"x": "t3", "from_lf": "pedidos_routes", "from_state": "ValidandoAuthYPayload", "to_lf": "pedidos_services", "to_state": "IniciandoTxCheckout", "label": "3: procesar_checkout_pedido(id_cliente, payload)", "type": "call"},
            {"x": "t4", "from_lf": "pedidos_services", "from_state": "IniciandoTxCheckout", "to_lf": "pedidos_repos", "to_state": "CreandoPedidoYDetalles", "label": "4: crear_pedido_con_detalles(pedido_data)", "type": "call"},
            {"x": "t5", "from_lf": "pedidos_repos", "from_state": "BloqueandoStockKardex", "to_lf": "pedidos_services", "to_state": "RegistrandoBitacoraCompra", "label": "5: return id_pedido, numero_pedido", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "pedidos_services", "from_state": "RegistrandoBitacoraCompra", "to_lf": "pedidos_routes", "to_state": "EmitiendoRespuestaHTTP201", "label": "6: return confirmacion_pedido", "type": "ret"},
            {"x": "t6", "from_lf": "pedidos_routes", "from_state": "EmitiendoRespuestaHTTP201", "to_lf": "IU_Checkout", "to_state": "PantallaExitoOrden", "label": "7: RedirigirExito(numero_pedido)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_Checkout", "from_state": "PantallaExitoOrden", "to_lf": "CLIENTE", "to_state": "OrdenConfirmada", "label": "8: MostrarReciboPedido()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 06. CU10 W/M - Gestionar reservas (Apartado en sucursal, Transaccional)
    # --------------------------------------------------------------------------
    {
        "id": "CU10_WM",
        "file_name": "CU10_WM_Gestionar_Reservas_Tiempo.svg",
        "png_name": "CU10_WM_Gestionar_Reservas_Tiempo.png",
        "title": "CU10 W/M - Gestionar reservas",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CLIENTE",
                "states": ["SeleccionandoSucursal", "ConfirmandoReserva", "EsperandoCodigoReserva", "ReservaConfirmada"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_Reservas",
                "states": ["FormularioReserva", "EnviandoPeticionReserva", "GenerandoComprobanteQR", "ModalReservaVisible"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "reservas_routes",
                "states": ["EnEspera", "ValidandoDatosReserva", "RetornandoTicketReserva"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "reservas_services",
                "states": ["Ocioso", "CalculandoVencimiento48h", "ApartandoStockVariante", "RegistrandoBitacoraReserva"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "reservas_repos",
                "states": ["EnEspera", "VerificandoStockSucursal", "InsertandoReservaKardex"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CLIENTE", "from_state": "ConfirmandoReserva", "to_lf": "IU_Reservas", "to_state": "EnviandoPeticionReserva", "label": "1: SolicitarReserva(id_variante, id_sucursal)", "type": "call"},
            {"x": "t2", "from_lf": "IU_Reservas", "from_state": "EnviandoPeticionReserva", "to_lf": "reservas_routes", "to_state": "ValidandoDatosReserva", "label": "2: POST /api/reservas", "type": "call"},
            {"x": "t3", "from_lf": "reservas_routes", "from_state": "ValidandoDatosReserva", "to_lf": "reservas_services", "to_state": "CalculandoVencimiento48h", "label": "3: crear_reserva_sucursal(id_cliente, payload)", "type": "call"},
            {"x": "t4", "from_lf": "reservas_services", "from_state": "CalculandoVencimiento48h", "to_lf": "reservas_repos", "to_state": "VerificandoStockSucursal", "label": "4: verificar_stock_reservable(id_var, id_suc)", "type": "call"},
            {"x": "t5", "from_lf": "reservas_repos", "from_state": "InsertandoReservaKardex", "to_lf": "reservas_services", "to_state": "ApartandoStockVariante", "label": "5: return disponible_ok, id_reserva, codigo", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "reservas_services", "from_state": "ApartandoStockVariante", "to_lf": "reservas_routes", "to_state": "RetornandoTicketReserva", "label": "6: return datos_reserva", "type": "ret"},
            {"x": "t6", "from_lf": "reservas_routes", "from_state": "RetornandoTicketReserva", "to_lf": "IU_Reservas", "to_state": "GenerandoComprobanteQR", "label": "7: MostrarComprobanteReserva(codigo)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_Reservas", "from_state": "GenerandoComprobanteQR", "to_lf": "CLIENTE", "to_state": "ReservaConfirmada", "label": "8: NotificarReservaExitosa()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 07. CU11 W/M - Consultar pedidos e historial (Consulta, SIN bitácora)
    # --------------------------------------------------------------------------
    {
        "id": "CU11_WM",
        "file_name": "CU11_WM_Consultar_Pedidos_Historial_Tiempo.svg",
        "png_name": "CU11_WM_Consultar_Pedidos_Historial_Tiempo.png",
        "title": "CU11 W/M - Consultar pedidos e historial",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CLIENTE",
                "states": ["EnPerfil", "AccediendoHistorial", "EsperandoListadoPedidos", "ViendoTimelinePedidos"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_HistorialPedidos",
                "states": ["VistaInactiva", "CargandoTimelineLoader", "PaginandoResultados", "HistorialVisible"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "pedidos_routes",
                "states": ["EnEspera", "ExtrayendoTokenCliente", "RetornandoListaJSON"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "pedidos_services",
                "states": ["Ocioso", "MapeandoEstadosYTracking", "EstructurandoTimelineDTO"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "pedidos_repos",
                "states": ["EnEspera", "ConsultandoPedidosClienteDB", "PedidosRecuperados"],
                "wave": [("t0", "t4", 0), ("t4", "t5", 1), ("t5", "t6", 2), ("t6", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CLIENTE", "from_state": "AccediendoHistorial", "to_lf": "IU_HistorialPedidos", "to_state": "CargandoTimelineLoader", "label": "1: AbrirHistorialPedidos()", "type": "call"},
            {"x": "t2", "from_lf": "IU_HistorialPedidos", "from_state": "CargandoTimelineLoader", "to_lf": "pedidos_routes", "to_state": "ExtrayendoTokenCliente", "label": "2: GET /api/pedidos/mis-pedidos", "type": "call"},
            {"x": "t3", "from_lf": "pedidos_routes", "from_state": "ExtrayendoTokenCliente", "to_lf": "pedidos_services", "to_state": "MapeandoEstadosYTracking", "label": "3: listar_pedidos_cliente(id_cliente)", "type": "call"},
            {"x": "t4", "from_lf": "pedidos_services", "from_state": "MapeandoEstadosYTracking", "to_lf": "pedidos_repos", "to_state": "ConsultandoPedidosClienteDB", "label": "4: obtener_pedidos_por_cliente(id_cliente)", "type": "call"},
            {"x": "t5", "from_lf": "pedidos_repos", "from_state": "PedidosRecuperados", "to_lf": "pedidos_services", "to_state": "EstructurandoTimelineDTO", "label": "5: return lista_pedidos", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "pedidos_services", "from_state": "EstructurandoTimelineDTO", "to_lf": "pedidos_routes", "to_state": "RetornandoListaJSON", "label": "6: return pedidos_dto", "type": "ret"},
            {"x": "t6", "from_lf": "pedidos_routes", "from_state": "RetornandoListaJSON", "to_lf": "IU_HistorialPedidos", "to_state": "PaginandoResultados", "label": "7: RenderizarHistorial(pedidos)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_HistorialPedidos", "from_state": "PaginandoResultados", "to_lf": "CLIENTE", "to_state": "ViendoTimelinePedidos", "label": "8: MostrarListaPedidos()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 08. CU26_M15_WM - Mostrar ubicaciones de sucursales (Consulta, SIN bitácora)
    # --------------------------------------------------------------------------
    {
        "id": "CU26_M15_WM",
        "file_name": "CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Tiempo.svg",
        "png_name": "CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Tiempo.png",
        "title": "CU26/M15 W/M - Mostrar ubicaciones de sucursales",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CLIENTE",
                "states": ["Navegando", "AbriendoMapaTiendas", "EsperandoMarcadores", "ExplorandoSucursales"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_MapaTiendas",
                "states": ["MapaInactivo", "CargandoGeolocalizacion", "DibujandoPinsYMural", "MapaInteractivoListo"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "sucursales_routes",
                "states": ["EnEspera", "VerificandoTenantPublico", "EntregandoGeodatosJSON"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "sucursales_services",
                "states": ["Ocioso", "FiltrandoSucursalesActivas", "ConstruyendoGeoJSON"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "sucursales_repos",
                "states": ["EnEspera", "ConsultandoSucursalesYCiudades", "DatasetCoordenadasRecuperado"],
                "wave": [("t0", "t4", 0), ("t4", "t5", 1), ("t5", "t6", 2), ("t6", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CLIENTE", "from_state": "AbriendoMapaTiendas", "to_lf": "IU_MapaTiendas", "to_state": "CargandoGeolocalizacion", "label": "1: AbrirMapaTiendas()", "type": "call"},
            {"x": "t2", "from_lf": "IU_MapaTiendas", "from_state": "CargandoGeolocalizacion", "to_lf": "sucursales_routes", "to_state": "VerificandoTenantPublico", "label": "2: GET /api/sucursales/publicas", "type": "call"},
            {"x": "t3", "from_lf": "sucursales_routes", "from_state": "VerificandoTenantPublico", "to_lf": "sucursales_services", "to_state": "FiltrandoSucursalesActivas", "label": "3: listar_sucursales_activas(id_empresa)", "type": "call"},
            {"x": "t4", "from_lf": "sucursales_services", "from_state": "FiltrandoSucursalesActivas", "to_lf": "sucursales_repos", "to_state": "ConsultandoSucursalesYCiudades", "label": "4: obtener_sucursales_con_coordenadas(id_empresa)", "type": "call"},
            {"x": "t5", "from_lf": "sucursales_repos", "from_state": "DatasetCoordenadasRecuperado", "to_lf": "sucursales_services", "to_state": "ConstruyendoGeoJSON", "label": "5: return sucursales_list", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "sucursales_services", "from_state": "ConstruyendoGeoJSON", "to_lf": "sucursales_routes", "to_state": "EntregandoGeodatosJSON", "label": "6: return geo_sucursales", "type": "ret"},
            {"x": "t6", "from_lf": "sucursales_routes", "from_state": "EntregandoGeodatosJSON", "to_lf": "IU_MapaTiendas", "to_state": "DibujandoPinsYMural", "label": "7: RenderizarMarcadores(sucursales)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_MapaTiendas", "from_state": "DibujandoPinsYMural", "to_lf": "CLIENTE", "to_state": "ExplorandoSucursales", "label": "8: MostrarMapaConTiendas()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 09. CU_W20 - Gestionar temporadas y colecciones (Administración / Mutación)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W20",
        "file_name": "CU_W20_Gestionar_Temporadas_Colecciones_Tiempo.svg",
        "png_name": "CU_W20_Gestionar_Temporadas_Colecciones_Tiempo.png",
        "title": "CU_W20 - Gestionar temporadas y colecciones",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "ADMINISTRADOR",
                "states": ["EnPanelColecciones", "LlenandoFormularioColeccion", "EsperandoConfirmacion", "ColeccionRegistrada"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_Colecciones",
                "states": ["FormularioAbierto", "ValidandoCamposCliente", "EnviandoPeticionAdmin", "TablaColeccionesActualizada"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "colecciones_routes",
                "states": ["EnEspera", "VerificandoRolAdmin", "RetornandoResultadoExitoso"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "colecciones_services",
                "states": ["Ocioso", "ValidandoPeriodoVigencia", "RegistrandoBitacoraAdmin", "ColeccionCreada"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "colecciones_repos",
                "states": ["EnEspera", "InsertandoColeccionDB", "RegistroConfirmado"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "ADMINISTRADOR", "from_state": "LlenandoFormularioColeccion", "to_lf": "IU_Colecciones", "to_state": "ValidandoCamposCliente", "label": "1: GuardarColeccion(nombre, temporada, anio)", "type": "call"},
            {"x": "t2", "from_lf": "IU_Colecciones", "from_state": "ValidandoCamposCliente", "to_lf": "colecciones_routes", "to_state": "VerificandoRolAdmin", "label": "2: POST /api/colecciones", "type": "call"},
            {"x": "t3", "from_lf": "colecciones_routes", "from_state": "VerificandoRolAdmin", "to_lf": "colecciones_services", "to_state": "ValidandoPeriodoVigencia", "label": "3: registrar_coleccion(id_empresa, payload)", "type": "call"},
            {"x": "t4", "from_lf": "colecciones_services", "from_state": "ValidandoPeriodoVigencia", "to_lf": "colecciones_repos", "to_state": "InsertandoColeccionDB", "label": "4: insertar_coleccion_db(coleccion_data)", "type": "call"},
            {"x": "t5", "from_lf": "colecciones_repos", "from_state": "RegistroConfirmado", "to_lf": "colecciones_services", "to_state": "RegistrandoBitacoraAdmin", "label": "5: return id_coleccion", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "colecciones_services", "from_state": "RegistrandoBitacoraAdmin", "to_lf": "colecciones_routes", "to_state": "RetornandoResultadoExitoso", "label": "6: return exito(id_coleccion)", "type": "ret"},
            {"x": "t6", "from_lf": "colecciones_routes", "from_state": "RetornandoResultadoExitoso", "to_lf": "IU_Colecciones", "to_state": "TablaColeccionesActualizada", "label": "7: ActualizarTabla(colecciones)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_Colecciones", "from_state": "TablaColeccionesActualizada", "to_lf": "ADMINISTRADOR", "to_state": "ColeccionRegistrada", "label": "8: NotificarColeccionGuardada()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 10. CU_W21 - Gestionar proveedores (Administración / Mutación)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W21",
        "file_name": "CU_W21_Gestionar_Proveedores_Tiempo.svg",
        "png_name": "CU_W21_Gestionar_Proveedores_Tiempo.png",
        "title": "CU_W21 - Gestionar proveedores",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "ADMINISTRADOR",
                "states": ["EnModuloProveedores", "IngresandoDatosProveedor", "EsperandoRespuestaServidor", "ProveedorGuardado"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_Proveedores",
                "states": ["ListaProveedores", "MostrandoModalFormulario", "EnviandoPayloadProveedor", "AlertaExitoVisible"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "proveedores_routes",
                "states": ["EnEspera", "ValidandoEsquemaNIT", "EntregandoRespuestaHTTP201"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "proveedores_services",
                "states": ["Ocioso", "VerificandoDuplicidadNIT", "RegistrandoBitacoraProveedor", "ProveedorCreado"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "proveedores_repos",
                "states": ["EnEspera", "VerificandoNITExistente", "InsertandoProveedorDB"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "ADMINISTRADOR", "from_state": "IngresandoDatosProveedor", "to_lf": "IU_Proveedores", "to_state": "MostrandoModalFormulario", "label": "1: GuardarProveedor(razon_social, nit, telefono)", "type": "call"},
            {"x": "t2", "from_lf": "IU_Proveedores", "from_state": "MostrandoModalFormulario", "to_lf": "proveedores_routes", "to_state": "ValidandoEsquemaNIT", "label": "2: POST /api/proveedores", "type": "call"},
            {"x": "t3", "from_lf": "proveedores_routes", "from_state": "ValidandoEsquemaNIT", "to_lf": "proveedores_services", "to_state": "VerificandoDuplicidadNIT", "label": "3: crear_proveedor(id_empresa, payload)", "type": "call"},
            {"x": "t4", "from_lf": "proveedores_services", "from_state": "VerificandoDuplicidadNIT", "to_lf": "proveedores_repos", "to_state": "VerificandoNITExistente", "label": "4: verificar_nit_existente(nit, id_empresa)", "type": "call"},
            {"x": "t5", "from_lf": "proveedores_repos", "from_state": "InsertandoProveedorDB", "to_lf": "proveedores_services", "to_state": "RegistrandoBitacoraProveedor", "label": "5: return nit_libre, id_proveedor", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "proveedores_services", "from_state": "RegistrandoBitacoraProveedor", "to_lf": "proveedores_routes", "to_state": "EntregandoRespuestaHTTP201", "label": "6: return proveedor_dto", "type": "ret"},
            {"x": "t6", "from_lf": "proveedores_routes", "from_state": "EntregandoRespuestaHTTP201", "to_lf": "IU_Proveedores", "to_state": "AlertaExitoVisible", "label": "7: RefrescarListaProveedores()", "type": "ret"},
            {"x": "t7", "from_lf": "IU_Proveedores", "from_state": "AlertaExitoVisible", "to_lf": "ADMINISTRADOR", "to_state": "ProveedorGuardado", "label": "8: MostrarToastExito()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 11. CU_W22 - Gestionar inventario (Movimientos Kardex, Transaccional)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W22",
        "file_name": "CU_W22_Gestionar_Inventario_Tiempo.svg",
        "png_name": "CU_W22_Gestionar_Inventario_Tiempo.png",
        "title": "CU_W22 - Gestionar inventario",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "ENCARGADO SUCURSAL",
                "states": ["EnModuloKardex", "SeleccionandoTipoMovimiento", "EsperandoConfirmacionStock", "StockActualizado"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_Inventario",
                "states": ["TablaStockVisible", "ValidandoEntradaCantidad", "EnviandoAjusteInventario", "KardexActualizado"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "inventario_routes",
                "states": ["EnEspera", "VerificandoPermisoSucursal", "NotificandoExitoKardex"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "inventario_services",
                "states": ["Ocioso", "CalculandoSaldoKardex", "RegistrandoBitacoraKardex", "MovimientoCompletado"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "inventario_repos",
                "states": ["EnEspera", "ValidandoDisponibilidadPrevia", "ActualizandoStockYLog"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "ENCARGADO SUCURSAL", "from_state": "SeleccionandoTipoMovimiento", "to_lf": "IU_Inventario", "to_state": "ValidandoEntradaCantidad", "label": "1: RegistrarMovimiento(tipo, id_variante, cant, motivo)", "type": "call"},
            {"x": "t2", "from_lf": "IU_Inventario", "from_state": "ValidandoEntradaCantidad", "to_lf": "inventario_routes", "to_state": "VerificandoPermisoSucursal", "label": "2: POST /api/inventario/movimientos", "type": "call"},
            {"x": "t3", "from_lf": "inventario_routes", "from_state": "VerificandoPermisoSucursal", "to_lf": "inventario_services", "to_state": "CalculandoSaldoKardex", "label": "3: procesar_movimiento_stock(id_sucursal, payload)", "type": "call"},
            {"x": "t4", "from_lf": "inventario_services", "from_state": "CalculandoSaldoKardex", "to_lf": "inventario_repos", "to_state": "ValidandoDisponibilidadPrevia", "label": "4: validar_disponibilidad_stock(id_var, id_suc, tipo, cant)", "type": "call"},
            {"x": "t5", "from_lf": "inventario_repos", "from_state": "ActualizandoStockYLog", "to_lf": "inventario_services", "to_state": "RegistrandoBitacoraKardex", "label": "5: return stock_valido, nuevo_saldo", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "inventario_services", "from_state": "RegistrandoBitacoraKardex", "to_lf": "inventario_routes", "to_state": "NotificandoExitoKardex", "label": "6: return movimiento_exitoso", "type": "ret"},
            {"x": "t6", "from_lf": "inventario_routes", "from_state": "NotificandoExitoKardex", "to_lf": "IU_Inventario", "to_state": "KardexActualizado", "label": "7: RenderizarNuevoSaldo(stock)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_Inventario", "from_state": "KardexActualizado", "to_lf": "ENCARGADO SUCURSAL", "to_state": "StockActualizado", "label": "8: MostrarAlertaMovimientoOk()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 12. CU_W23 - Gestionar disponibilidad de prendas (Reglas de visibilidad, Mutación)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W23",
        "file_name": "CU_W23_Gestionar_Disponibilidad_Prendas_Tiempo.svg",
        "png_name": "CU_W23_Gestionar_Disponibilidad_Prendas_Tiempo.png",
        "title": "CU_W23 - Gestionar disponibilidad de prendas",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "ADMINISTRADOR",
                "states": ["RevisandoCatalogoAdmin", "AlternandoReglaVisibilidad", "EsperandoAplicacionRegla", "ReglaAplicada"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_Disponibilidad",
                "states": ["MatrizDisponibilidad", "ToggleReglaInteractivo", "EnviandoConfiguracion", "MatrizActualizada"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "disponibilidad_routes",
                "states": ["EnEspera", "VerificandoPayloadRegla", "ConfirmandoReglaGuardada"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "disponibilidad_services",
                "states": ["Ocioso", "ValidandoImpactoEnCatalogo", "RegistrandoBitacoraRegla", "ReglaConsistente"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "inventario_repos",
                "states": ["EnEspera", "ActualizandoDisponibilidadDB", "CommitReglaExitoso"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "ADMINISTRADOR", "from_state": "AlternandoReglaVisibilidad", "to_lf": "IU_Disponibilidad", "to_state": "ToggleReglaInteractivo", "label": "1: ModificarRegla(id_variante, id_sucursal, estado)", "type": "call"},
            {"x": "t2", "from_lf": "IU_Disponibilidad", "from_state": "ToggleReglaInteractivo", "to_lf": "disponibilidad_routes", "to_state": "VerificandoPayloadRegla", "label": "2: PUT /api/inventario/disponibilidad", "type": "call"},
            {"x": "t3", "from_lf": "disponibilidad_routes", "from_state": "VerificandoPayloadRegla", "to_lf": "disponibilidad_services", "to_state": "ValidandoImpactoEnCatalogo", "label": "3: modificar_estado_disponibilidad(payload)", "type": "call"},
            {"x": "t4", "from_lf": "disponibilidad_services", "from_state": "ValidandoImpactoEnCatalogo", "to_lf": "inventario_repos", "to_state": "ActualizandoDisponibilidadDB", "label": "4: actualizar_disponibilidad_db(id_var, id_suc, estado)", "type": "call"},
            {"x": "t5", "from_lf": "inventario_repos", "from_state": "CommitReglaExitoso", "to_lf": "disponibilidad_services", "to_state": "RegistrandoBitacoraRegla", "label": "5: return filas_afectadas", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "disponibilidad_services", "from_state": "RegistrandoBitacoraRegla", "to_lf": "disponibilidad_routes", "to_state": "ConfirmandoReglaGuardada", "label": "6: return estado_actualizado", "type": "ret"},
            {"x": "t6", "from_lf": "disponibilidad_routes", "from_state": "ConfirmandoReglaGuardada", "to_lf": "IU_Disponibilidad", "to_state": "MatrizActualizada", "label": "7: RefrescarToggle(estado)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_Disponibilidad", "from_state": "MatrizActualizada", "to_lf": "ADMINISTRADOR", "to_state": "ReglaAplicada", "label": "8: NotificarCambioVisibilidad()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 13. CU_W24 - Registrar venta presencial POS (Cajero, Transaccional)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W24",
        "file_name": "CU_W24_Registrar_Venta_Presencial_Tiempo.svg",
        "png_name": "CU_W24_Registrar_Venta_Presencial_Tiempo.png",
        "title": "CU_W24 - Registrar venta presencial POS",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CAJERO",
                "states": ["EscaneandoPrendas", "ConfirmandoTotalVenta", "EsperandoGeneracionTicket", "VentaPresencialConcluida"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_POS",
                "states": ["GridProductosPOS", "BloqueandoTerminalPOS", "GenerandoReciboVenta", "TerminalListaSiguienteCliente"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "pos_routes",
                "states": ["EnEspera", "ValidandoSesionCajaActiva", "EntregandoResumenVenta"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "pos_services",
                "states": ["Ocioso", "CalculandoDescuentosYTotales", "RegistrandoBitacoraPOS", "VentaRegistrada"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "pos_repos",
                "states": ["EnEspera", "DescontandoStockFisicoCaja", "CommitTransaccionVenta"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CAJERO", "from_state": "ConfirmandoTotalVenta", "to_lf": "IU_POS", "to_state": "BloqueandoTerminalPOS", "label": "1: ConfirmarVenta(items, cliente, total)", "type": "call"},
            {"x": "t2", "from_lf": "IU_POS", "from_state": "BloqueandoTerminalPOS", "to_lf": "pos_routes", "to_state": "ValidandoSesionCajaActiva", "label": "2: POST /api/pos/ventas", "type": "call"},
            {"x": "t3", "from_lf": "pos_routes", "from_state": "ValidandoSesionCajaActiva", "to_lf": "pos_services", "to_state": "CalculandoDescuentosYTotales", "label": "3: procesar_venta_presencial(id_sesion, payload)", "type": "call"},
            {"x": "t4", "from_lf": "pos_services", "from_state": "CalculandoDescuentosYTotales", "to_lf": "pos_repos", "to_state": "DescontandoStockFisicoCaja", "label": "4: verificar_stock_caja(items, id_sucursal)", "type": "call"},
            {"x": "t5", "from_lf": "pos_repos", "from_state": "CommitTransaccionVenta", "to_lf": "pos_services", "to_state": "RegistrandoBitacoraPOS", "label": "5: return stock_ok, id_venta", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "pos_services", "from_state": "RegistrandoBitacoraPOS", "to_lf": "pos_routes", "to_state": "EntregandoResumenVenta", "label": "6: return venta_registrada", "type": "ret"},
            {"x": "t6", "from_lf": "pos_routes", "from_state": "EntregandoResumenVenta", "to_lf": "IU_POS", "to_state": "GenerandoReciboVenta", "label": "7: ImprimirComprobante(id_venta)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_POS", "from_state": "GenerandoReciboVenta", "to_lf": "CAJERO", "to_state": "VentaPresencialConcluida", "label": "8: MostrarConfirmacionVenta()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 14. CU_W25 - Atender reservas en sucursal (Encargado/Cajero, Transaccional)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W25",
        "file_name": "CU_W25_Atender_Reservas_Tiempo.svg",
        "png_name": "CU_W25_Atender_Reservas_Tiempo.png",
        "title": "CU_W25 - Atender reservas en sucursal",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "ENCARGADO SUCURSAL",
                "states": ["AtendiendoCliente", "IngresandoCodigoReserva", "EsperandoValidacion", "PrendaEntregadaAlCliente"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_AtencionReservas",
                "states": ["BuscadorReserva", "MostrandoDetalleReserva", "EnviandoConfirmacionEntrega", "TicketEntregaImpreso"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "reservas_routes",
                "states": ["EnEspera", "VerificandoEstadoReserva", "ConfirmandoCambioEstado"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "reservas_services",
                "states": ["Ocioso", "VerificandoVigencia48h", "RegistrandoBitacoraEntrega", "ReservaFinalizada"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "reservas_repos",
                "states": ["EnEspera", "ConsultandoReservaDB", "ActualizandoEstadoEntregada"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "ENCARGADO SUCURSAL", "from_state": "IngresandoCodigoReserva", "to_lf": "IU_AtencionReservas", "to_state": "MostrandoDetalleReserva", "label": "1: BuscarReserva(codigo_reserva)", "type": "call"},
            {"x": "t2", "from_lf": "IU_AtencionReservas", "from_state": "MostrandoDetalleReserva", "to_lf": "reservas_routes", "to_state": "VerificandoEstadoReserva", "label": "2: GET /api/reservas/buscar?codigo={cod}", "type": "call"},
            {"x": "t3", "from_lf": "reservas_routes", "from_state": "VerificandoEstadoReserva", "to_lf": "reservas_services", "to_state": "VerificandoVigencia48h", "label": "3: consultar_reserva_por_codigo(codigo)", "type": "call"},
            {"x": "t4", "from_lf": "reservas_services", "from_state": "VerificandoVigencia48h", "to_lf": "reservas_repos", "to_state": "ConsultandoReservaDB", "label": "4: obtener_reserva_db(codigo)", "type": "call"},
            {"x": "t5", "from_lf": "reservas_repos", "from_state": "ActualizandoEstadoEntregada", "to_lf": "reservas_services", "to_state": "RegistrandoBitacoraEntrega", "label": "5: return datos_reserva, estado_valido", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "reservas_services", "from_state": "RegistrandoBitacoraEntrega", "to_lf": "reservas_routes", "to_state": "ConfirmandoCambioEstado", "label": "6: return reserva_entregada", "type": "ret"},
            {"x": "t6", "from_lf": "reservas_routes", "from_state": "ConfirmandoCambioEstado", "to_lf": "IU_AtencionReservas", "to_state": "TicketEntregaImpreso", "label": "7: RenderizarConfirmacionEntrega()", "type": "ret"},
            {"x": "t7", "from_lf": "IU_AtencionReservas", "from_state": "TicketEntregaImpreso", "to_lf": "ENCARGADO SUCURSAL", "to_state": "PrendaEntregadaAlCliente", "label": "8: NotificarEntregaCompletada()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 15. CU_W27 - Procesar pago electrónico (Pasarela Stripe/QR, Transaccional)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W27",
        "file_name": "CU_W27_Procesar_Pago_Electronico_Tiempo.svg",
        "png_name": "CU_W27_Procesar_Pago_Electronico_Tiempo.png",
        "title": "CU_W27 - Procesar pago electrónico",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CLIENTE",
                "states": ["EnPasarelaPago", "IngresandoDatosTarjeta", "EsperandoTokenBancario", "TransaccionAprobada"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_PasarelaPago",
                "states": ["FormularioTarjeta", "CifrandoCamposSensibles", "EsperandoWebhookPasarela", "PantallaAprobacionVisible"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "pago_routes",
                "states": ["EnEspera", "VerificandoMontoYPedido", "RetornandoResultadoPago"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "pasarela_services",
                "states": ["Ocioso", "ComunicandoConGatewayBancario", "RegistrandoBitacoraPago", "PagoConfirmado"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "pago_repos",
                "states": ["EnEspera", "RegistrandoIntentoPago", "ActualizandoEstadoTransaccion"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CLIENTE", "from_state": "IngresandoDatosTarjeta", "to_lf": "IU_PasarelaPago", "to_state": "CifrandoCamposSensibles", "label": "1: IniciarPago(id_pedido, metodo, datos_tarjeta)", "type": "call"},
            {"x": "t2", "from_lf": "IU_PasarelaPago", "from_state": "CifrandoCamposSensibles", "to_lf": "pago_routes", "to_state": "VerificandoMontoYPedido", "label": "2: POST /api/pagos/procesar-electronico", "type": "call"},
            {"x": "t3", "from_lf": "pago_routes", "from_state": "VerificandoMontoYPedido", "to_lf": "pasarela_services", "to_state": "ComunicandoConGatewayBancario", "label": "3: procesar_transaccion_pasarela(payload)", "type": "call"},
            {"x": "t4", "from_lf": "pasarela_services", "from_state": "ComunicandoConGatewayBancario", "to_lf": "pago_repos", "to_state": "RegistrandoIntentoPago", "label": "4: validar_y_registrar_intento_pago(id_pedido, monto)", "type": "call"},
            {"x": "t5", "from_lf": "pago_repos", "from_state": "ActualizandoEstadoTransaccion", "to_lf": "pasarela_services", "to_state": "RegistrandoBitacoraPago", "label": "5: return token_transaccion, auth_code", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "pasarela_services", "from_state": "RegistrandoBitacoraPago", "to_lf": "pago_routes", "to_state": "RetornandoResultadoPago", "label": "6: return resultado_pago_aprobado", "type": "ret"},
            {"x": "t6", "from_lf": "pago_routes", "from_state": "RetornandoResultadoPago", "to_lf": "IU_PasarelaPago", "to_state": "PantallaAprobacionVisible", "label": "7: RenderizarAprobacion(auth_code)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_PasarelaPago", "from_state": "PantallaAprobacionVisible", "to_lf": "CLIENTE", "to_state": "TransaccionAprobada", "label": "8: MostrarComprobanteDigital()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 16. CU_W28 - Procesar pago en caja (Cajero físico, Transaccional)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W28",
        "file_name": "CU_W28_Procesar_Pago_Caja_Tiempo.svg",
        "png_name": "CU_W28_Procesar_Pago_Caja_Tiempo.png",
        "title": "CU_W28 - Procesar pago en caja",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CAJERO",
                "states": ["RecibiendoDinero", "IngresandoMontoRecibido", "EntregandoCambio", "CobroCajaFinalizado"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_CajaCobro",
                "states": ["ModalCobro", "CalculandoCambioEfectivo", "AbriendoGavetaDinero", "ResumenCobroVisible"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "caja_routes",
                "states": ["EnEspera", "ValidandoCuadraturaCaja", "RespondiendoExitoCobro"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "caja_services",
                "states": ["Ocioso", "CalculandoArqueoSesion", "RegistrandoBitacoraCaja", "CobroAsentado"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "caja_pago_repos",
                "states": ["EnEspera", "VerificandoTotalVenta", "InsertandoMovimientoCajaDB"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CAJERO", "from_state": "IngresandoMontoRecibido", "to_lf": "IU_CajaCobro", "to_state": "CalculandoCambioEfectivo", "label": "1: RegistrarCobro(id_venta, monto_recibido, metodo)", "type": "call"},
            {"x": "t2", "from_lf": "IU_CajaCobro", "from_state": "CalculandoCambioEfectivo", "to_lf": "caja_routes", "to_state": "ValidandoCuadraturaCaja", "label": "2: POST /api/caja/pagos", "type": "call"},
            {"x": "t3", "from_lf": "caja_routes", "from_state": "ValidandoCuadraturaCaja", "to_lf": "caja_services", "to_state": "CalculandoArqueoSesion", "label": "3: registrar_pago_caja(id_sesion, payload)", "type": "call"},
            {"x": "t4", "from_lf": "caja_services", "from_state": "CalculandoArqueoSesion", "to_lf": "caja_pago_repos", "to_state": "VerificandoTotalVenta", "label": "4: calcular_cambio_efectivo(total, monto_recibido)", "type": "call"},
            {"x": "t5", "from_lf": "caja_pago_repos", "from_state": "InsertandoMovimientoCajaDB", "to_lf": "caja_services", "to_state": "RegistrandoBitacoraCaja", "label": "5: return cambio, id_pago_caja", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "caja_services", "from_state": "RegistrandoBitacoraCaja", "to_lf": "caja_routes", "to_state": "RespondiendoExitoCobro", "label": "6: return cobro_confirmado", "type": "ret"},
            {"x": "t6", "from_lf": "caja_routes", "from_state": "RespondiendoExitoCobro", "to_lf": "IU_CajaCobro", "to_state": "AbriendoGavetaDinero", "label": "7: AbrirCajonYMostrarCambio(cambio)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_CajaCobro", "from_state": "AbriendoGavetaDinero", "to_lf": "CAJERO", "to_state": "CobroCajaFinalizado", "label": "8: EntregarCambioACliente()", "type": "ret"}
        ]
    },

    # --------------------------------------------------------------------------
    # 17. CU_W29 - Emitir comprobante de venta (Facturación / Recibo, Transaccional)
    # --------------------------------------------------------------------------
    {
        "id": "CU_W29",
        "file_name": "CU_W29_Emitir_Comprobante_Venta_Tiempo.svg",
        "png_name": "CU_W29_Emitir_Comprobante_Venta_Tiempo.png",
        "title": "CU_W29 - Emitir comprobante de venta",
        "canvas_width": 1420,
        "time_x": {
            "t0": 260, "t1": 380, "t2": 510, "t3": 650, "t4": 800, "t5": 940, "t6": 1080, "t7": 1220, "t8": 1340
        },
        "lifelines": [
            {
                "name": "CAJERO",
                "states": ["VentaConcluida", "SolicitandoFactura", "EsperandoSelloDigital", "ComprobanteImpresoYEntregado"],
                "wave": [("t0", "t1", 0), ("t1", "t2", 1), ("t2", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "IU_Facturacion",
                "states": ["FormularioDatosFiscales", "ValidandoNITEnLinea", "EnviandoPeticionEmision", "ImprimiendoTicketFiscal"],
                "wave": [("t0", "t2", 0), ("t2", "t6", 1), ("t6", "t7", 2), ("t7", "t8", 3)]
            },
            {
                "name": "comprobante_routes",
                "states": ["EnEspera", "VerificandoParametrosFiscales", "RetornandoComprobanteFirmado"],
                "wave": [("t0", "t2", 0), ("t2", "t3", 1), ("t3", "t5", 0), ("t5", "t6", 2), ("t6", "t8", 0)]
            },
            {
                "name": "comprobante_services",
                "states": ["Ocioso", "GenerandoCodigoCUFDCUF", "RegistrandoBitacoraFiscal", "ComprobanteSellado"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            },
            {
                "name": "comprobante_repos",
                "states": ["EnEspera", "ValidandoDatosFacturacion", "PersistiendoComprobanteDB"],
                "wave": [("t0", "t3", 0), ("t3", "t4", 1), ("t4", "t5", 2), ("t5", "t8", 0)]
            }
        ],
        "events": [
            {"x": "t1", "from_lf": "CAJERO", "from_state": "SolicitandoFactura", "to_lf": "IU_Facturacion", "to_state": "ValidandoNITEnLinea", "label": "1: SolicitarComprobante(id_venta, tipo, datos_fiscales)", "type": "call"},
            {"x": "t2", "from_lf": "IU_Facturacion", "from_state": "ValidandoNITEnLinea", "to_lf": "comprobante_routes", "to_state": "VerificandoParametrosFiscales", "label": "2: POST /api/comprobantes/emitir", "type": "call"},
            {"x": "t3", "from_lf": "comprobante_routes", "from_state": "VerificandoParametrosFiscales", "to_lf": "comprobante_services", "to_state": "GenerandoCodigoCUFDCUF", "label": "3: emitir_comprobante_fiscal(payload)", "type": "call"},
            {"x": "t4", "from_lf": "comprobante_services", "from_state": "GenerandoCodigoCUFDCUF", "to_lf": "comprobante_repos", "to_state": "ValidandoDatosFacturacion", "label": "4: validar_datos_facturacion(nit, razon_social)", "type": "call"},
            {"x": "t5", "from_lf": "comprobante_repos", "from_state": "PersistiendoComprobanteDB", "to_lf": "comprobante_services", "to_state": "RegistrandoBitacoraFiscal", "label": "5: return datos_validos, numero_factura", "type": "ret"},
            {"x": "t5", "x_offset": 50, "from_lf": "comprobante_services", "from_state": "RegistrandoBitacoraFiscal", "to_lf": "comprobante_routes", "to_state": "RetornandoComprobanteFirmado", "label": "6: return comprobante_pdf_xml", "type": "ret"},
            {"x": "t6", "from_lf": "comprobante_routes", "from_state": "RetornandoComprobanteFirmado", "to_lf": "IU_Facturacion", "to_state": "ImprimiendoTicketFiscal", "label": "7: EnviarAImpresoraTermica(comprobante)", "type": "ret"},
            {"x": "t7", "from_lf": "IU_Facturacion", "from_state": "ImprimiendoTicketFiscal", "to_lf": "CAJERO", "to_state": "ComprobanteImpresoYEntregado", "label": "8: CortarYEntregarFactura()", "type": "ret"}
        ]
    }
]


def main():
    out_dir = "/home/eddy/Escritorio/PROYECTOS/EP1-SI2/Examen_parcial1_S12/docs/diagramas_tiempo"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"=== INICIANDO GENERACIÓN DE {len(DIAGRAMAS_TIEMPO)} DIAGRAMAS DE TIEMPO UML 2.5 ===")
    for idx, diag in enumerate(DIAGRAMAS_TIEMPO, 1):
        svg_content = render_timing_svg(diag)
        svg_path = os.path.join(out_dir, diag["file_name"])
        png_path = os.path.join(out_dir, diag["png_name"])

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        cairosvg.svg2png(bytestring=svg_content.encode("utf-8"), write_to=png_path, scale=2.0)
        print(f"[{idx:02d}/17 OK] SVG & PNG (2x): {diag['file_name']}")

    print("\n¡Todos los 17 Diagramas de Tiempo generados exitosamente!")

if __name__ == "__main__":
    main()
