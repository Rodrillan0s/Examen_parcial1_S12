#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de Diagramas de Estructura de Casos de Uso (SI2 - UAGRM)
Sistema Web de Comercio Electrónico Multi-Tenant Aura

Sigue la plantilla y simbología oficial de la cátedra SI2:
- Árbol jerárquico de Sistema -> Portal/Login -> Módulos/Subsistemas (Rombos de colores) -> Páginas -> «CU» Casos de Uso
- Integra los 29 Casos de Uso del sistema estructurados en los 6 Subsistemas Implementados.
- Genera también el Diagrama de Paquetes de Casos de Uso UML con Actores y Dependencias.
"""

import os
import sys
import xml.sax.saxutils
import cairosvg

def escape_xml(text):
    return xml.sax.saxutils.escape(str(text))

def svg_header(w, h, title, subtitle=""):
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n',
        '  <defs>\n',
        '    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">\n',
        '      <path d="M 0 1 L 7 4 L 0 7 Z" fill="#334155"/>\n',
        '    </marker>\n',
        '    <marker id="arrow-dashed" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">\n',
        '      <path d="M 0 1 L 7 4 L 0 7 Z" fill="#64748b"/>\n',
        '    </marker>\n',
        '    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">\n',
        '      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-color="#000000" flood-opacity="0.08"/>\n',
        '    </filter>\n',
        '  </defs>\n\n',
        f'  <!-- Fondo Blanco con Rejilla de Cuadrícula Sutil -->\n',
        f'  <rect x="0" y="0" width="{w}" height="{h}" fill="#fcfdfd"/>\n',
    ]
    for gx in range(0, w, 40):
        parts.append(f'  <line x1="{gx}" y1="0" x2="{gx}" y2="{h}" stroke="#f1f5f9" stroke-width="0.8"/>\n')
    for gy in range(0, h, 40):
        parts.append(f'  <line x1="0" y1="{gy}" x2="{w}" y2="{gy}" stroke="#f1f5f9" stroke-width="0.8"/>\n')

    parts.append(f'  <rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="#cbd5e1" stroke-width="1.5"/>\n\n')
    parts.append(f'  <text x="{w/2}" y="36" font-family="Arial, Helvetica, sans-serif" font-size="22" font-weight="bold" fill="#0f172a" text-anchor="middle">{escape_xml(title)}</text>\n')
    if subtitle:
        parts.append(f'  <text x="{w/2}" y="56" font-family="Arial, Helvetica, sans-serif" font-size="12.5" fill="#64748b" text-anchor="middle">{escape_xml(subtitle)}</text>\n\n')
    return parts

# ------------------------------------------------------------------------------
# Primitivas Gráficas Estilo SI2
# ------------------------------------------------------------------------------

def draw_system_root(cx, y, name="<SISTEMA E-COMMERCE AURA>", w=280, h=36):
    return (
        f'  <!-- Raíz del Sistema -->\n'
        f'  <g filter="url(#shadow)">\n'
        f'    <rect x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="18" ry="18" fill="#dcfce7" stroke="#16a34a" stroke-width="1.8"/>\n'
        f'    <text x="{cx}" y="{y + h/2 + 4.5}" font-family="Arial, Helvetica, sans-serif" font-size="12.5" font-weight="bold" fill="#14532d" text-anchor="middle">{escape_xml(name)}</text>\n'
        f'  </g>\n'
    )

def draw_screen_box(cx, y, title, subtitle="", w=240, h=44, bg="#ffffff", border="#475569", text_color="#0f172a"):
    res = [
        f'  <g filter="url(#shadow)">\n',
        f'    <rect x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="6" ry="6" fill="{bg}" stroke="{border}" stroke-width="1.4"/>\n'
    ]
    if subtitle:
        res.append(f'    <text x="{cx}" y="{y + 17}" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="bold" fill="{text_color}" text-anchor="middle">{escape_xml(title)}</text>\n')
        res.append(f'    <text x="{cx}" y="{y + 32}" font-family="Arial, Helvetica, sans-serif" font-size="9" fill="#64748b" text-anchor="middle">{escape_xml(subtitle)}</text>\n')
    else:
        res.append(f'    <text x="{cx}" y="{y + h/2 + 4}" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="bold" fill="{text_color}" text-anchor="middle">{escape_xml(title)}</text>\n')
    res.append('  </g>\n')
    return "".join(res)

def draw_diamond_module(cx, cy, lines, fill_color, size=62):
    # Dibuja un rombo centrado en (cx, cy) con ancho suficiente para el texto
    rx = size * 1.55
    ry = size * 0.95
    pts = f"{cx},{cy - ry} {cx + rx},{cy} {cx},{cy + ry} {cx - rx},{cy}"
    res = [
        f'  <!-- Módulo Rombo -->\n',
        f'  <g filter="url(#shadow)">\n',
        f'    <polygon points="{pts}" fill="{fill_color}" stroke="#ffffff" stroke-width="1.5"/>\n'
    ]
    total_lines = len(lines)
    start_y = cy - (total_lines - 1) * 6.5
    for i, line in enumerate(lines):
        ly = start_y + i * 13
        res.append(f'    <text x="{cx}" y="{ly + 4}" font-family="Arial, Helvetica, sans-serif" font-size="9.5" font-weight="bold" fill="#ffffff" text-anchor="middle">{escape_xml(line)}</text>\n')
    res.append('  </g>\n')
    return "".join(res)

def draw_page_box(cx, y, name, w=160, h=32):
    return (
        f'  <g filter="url(#shadow)">\n'
        f'    <rect x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="4" ry="4" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2"/>\n'
        f'    <text x="{cx}" y="{y + h/2 + 4}" font-family="Arial, Helvetica, sans-serif" font-size="9.2" font-weight="600" fill="#1e293b" text-anchor="middle">Página: {escape_xml(name)}</text>\n'
        f'  </g>\n'
    )

def draw_cu_box(cx, y, cu_code, cu_name, w=160, h=36, fill="#e0f2fe", border="#0284c7", text_color="#0369a1"):
    return (
        f'  <g filter="url(#shadow)">\n'
        f'    <rect x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="7" ry="7" fill="{fill}" stroke="{border}" stroke-width="1.3"/>\n'
        f'    <text x="{cx}" y="{y + 14}" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="bold" fill="{text_color}" text-anchor="middle">«CU» {escape_xml(cu_code)}</text>\n'
        f'    <text x="{cx}" y="{y + 27}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" font-weight="500" fill="#0f172a" text-anchor="middle">{escape_xml(cu_name)}</text>\n'
        f'  </g>\n'
    )

def draw_arrow(x1, y1, x2, y2, label=""):
    res = [f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#334155" stroke-width="1.3" marker-end="url(#arrow)"/>\n']
    if label:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2 - 4
        res.append(f'  <text x="{mx}" y="{my}" font-family="Arial, Helvetica, sans-serif" font-size="8" fill="#475569" text-anchor="middle">{escape_xml(label)}</text>\n')
    return "".join(res)

def draw_path_arrow(d, label="", lx=0, ly=0):
    res = [f'  <path d="{d}" fill="none" stroke="#334155" stroke-width="1.3" marker-end="url(#arrow)"/>\n']
    if label and lx and ly:
        res.append(f'  <text x="{lx}" y="{ly}" font-family="Arial, Helvetica, sans-serif" font-size="8" fill="#475569" text-anchor="middle">{escape_xml(label)}</text>\n')
    return "".join(res)


# ==============================================================================
# DE00: DIAGRAMA MAESTRO DE ESTRUCTURA DE CASOS DE USO (ÁRBOL GLOBAL COMPLETO)
# ==============================================================================

def make_de00_master():
    w, h = 2750, 1180
    p = svg_header(w, h, 
                   "Diagrama de Estructura de Casos de Uso del Sistema - Plataforma Aura", 
                   "Jerarquía Arquitectónica de Navegación, Módulos Funcionales y Cobertura de Casos de Uso (SI2 - UAGRM)")

    mid_x = w / 2

    # 1. NODO RAÍZ: <SISTEMA E-COMMERCE AURA>
    p.append(draw_system_root(mid_x, 80, "<SISTEMA E-COMMERCE AURA>", 320, 38))

    # 2. PANTALLA DE ENTRADA: Pantalla de Inicio de Sesión / Portal
    p.append(draw_arrow(mid_x, 118, mid_x, 145))
    p.append(draw_screen_box(mid_x, 145, "Pantalla de Inicio de Sesión / Portal Web", "Autenticación Unificada y Acceso Público", 310, 44))

    # 3. PANEL DE CONTROL GENERAL
    p.append(draw_arrow(mid_x, 189, mid_x, 215))
    p.append(draw_screen_box(mid_x, 215, "Panel de Control General (Selección de Módulo)", "Distribución de Flujos Operativos y Vistas por Rol", 340, 44, bg="#1e293b", border="#0f172a", text_color="#f8fafc"))

    # Coordenadas X de los 6 Subsistemas Implementados con suficiente separación
    cols_x = [260, 740, 1220, 1690, 2070, 2440]
    sub_y = 345

    # Flechas distribuidoras desde el Panel de Control a cada módulo
    for cx in cols_x:
        p.append(draw_path_arrow(f"M {mid_x} 259 L {mid_x} 275 L {cx} 275 L {cx} {sub_y - 60}"))

    # ==========================================================================
    # SUBSISTEMA 1: Seguridad, Usuarios y Roles (Verde Esmeralda)
    # ==========================================================================
    c1 = cols_x[0]
    p.append(draw_diamond_module(c1, sub_y, ["Módulo:", "Seguridad y", "Usuarios"], "#10b981", 54))

    c1_l = c1 - 105
    c1_r = c1 + 105

    # 1.1 Registro & Login
    p.append(draw_path_arrow(f"M {c1 - 55} {sub_y + 35} L {c1 - 55} 435 L {c1_l} 435 L {c1_l} 440"))
    p.append(draw_page_box(c1_l, 440, "Registro de Clientes", 155, 30))
    p.append(draw_arrow(c1_l, 470, c1_l, 490))
    p.append(draw_cu_box(c1_l, 490, "CU01", "Registrar Usuario", 155, 34))

    p.append(draw_path_arrow(f"M {c1 + 55} {sub_y + 35} L {c1 + 55} 435 L {c1_r} 435 L {c1_r} 440"))
    p.append(draw_page_box(c1_r, 440, "Acceso al Sistema", 155, 30))
    p.append(draw_arrow(c1_r, 470, c1_r, 490))
    p.append(draw_cu_box(c1_r, 490, "CU02", "Iniciar Sesión", 155, 34))

    # 1.2 Perfil de Usuario
    p.append(draw_arrow(c1_l, 524, c1_l, 550))
    p.append(draw_page_box(c1_l, 550, "Mi Perfil Personal", 155, 30))
    p.append(draw_arrow(c1_l, 580, c1_l, 600))
    p.append(draw_cu_box(c1_l, 600, "CU03", "Gestionar Perfil", 155, 34))

    # 1.3 Administración de Usuarios y Roles (RBAC)
    p.append(draw_arrow(c1_r, 524, c1_r, 550))
    p.append(draw_page_box(c1_r, 550, "Panel Usuarios & Roles", 155, 30))
    p.append(draw_arrow(c1_r, 580, c1_r, 600))
    p.append(draw_cu_box(c1_r, 600, "CU14", "Gestionar Usuarios y Roles", 155, 34))

    # 1.4 Bitácora de Auditoría
    p.append(draw_arrow(c1_r, 634, c1_r, 660))
    p.append(draw_page_box(c1_r, 660, "Registro de Bitácora", 155, 30))
    p.append(draw_arrow(c1_r, 690, c1_r, 710))
    p.append(draw_cu_box(c1_r, 710, "CU-AUD", "Auditoría del Sistema", 155, 34, fill="#fef08a", border="#ca8a04", text_color="#854d0e"))


    # ==========================================================================
    # SUBSISTEMA 2: Gestión de Catálogo y Colecciones (Azul Océano)
    # ==========================================================================
    c2 = cols_x[1]
    p.append(draw_diamond_module(c2, sub_y, ["Módulo:", "Gestión de", "Catálogo"], "#0284c7", 54))

    c2_l = c2 - 105
    c2_r = c2 + 105

    # 2.1 Exploración de Catálogo y Filtros
    p.append(draw_path_arrow(f"M {c2 - 55} {sub_y + 35} L {c2 - 55} 435 L {c2_l} 435 L {c2_l} 440"))
    p.append(draw_page_box(c2_l, 440, "Catálogo de Moda", 155, 30))
    p.append(draw_arrow(c2_l, 470, c2_l, 490))
    p.append(draw_cu_box(c2_l, 490, "CU04/CU05", "Buscar y Filtrar Prendas", 155, 34))

    p.append(draw_arrow(c2_l, 524, c2_l, 550))
    p.append(draw_page_box(c2_l, 550, "Ficha de Prenda", 155, 30))
    p.append(draw_arrow(c2_l, 580, c2_l, 600))
    p.append(draw_cu_box(c2_l, 600, "CU06", "Detalle de Producto", 155, 34))

    # 2.2 Gestión Administrativa de Productos y Categorías
    p.append(draw_path_arrow(f"M {c2 + 55} {sub_y + 35} L {c2 + 55} 435 L {c2_r} 435 L {c2_r} 440"))
    p.append(draw_page_box(c2_r, 440, "Gestión de Prendas", 155, 30))
    p.append(draw_arrow(c2_r, 470, c2_r, 490))
    p.append(draw_cu_box(c2_r, 490, "CU17", "Gestionar Productos", 155, 34))

    p.append(draw_arrow(c2_r, 524, c2_r, 550))
    p.append(draw_page_box(c2_r, 550, "Gestión Categorías", 155, 30))
    p.append(draw_arrow(c2_r, 580, c2_r, 600))
    p.append(draw_cu_box(c2_r, 600, "CU18", "Gestionar Categorías", 155, 34))

    # 2.3 Variantes (Tallas/Colores) y Colecciones
    p.append(draw_arrow(c2_r, 634, c2_r, 660))
    p.append(draw_page_box(c2_r, 660, "Tallas y Colores", 155, 30))
    p.append(draw_arrow(c2_r, 690, c2_r, 710))
    p.append(draw_cu_box(c2_r, 710, "CU19", "Gestionar Variantes", 155, 34))

    p.append(draw_arrow(c2_r, 744, c2_r, 770))
    p.append(draw_page_box(c2_r, 770, "Colecciones Moda", 155, 30))
    p.append(draw_arrow(c2_r, 800, c2_r, 820))
    p.append(draw_cu_box(c2_r, 820, "CU20", "Gestionar Colecciones", 155, 34))


    # ==========================================================================
    # SUBSISTEMA 3: Sucursales, Inventario y Proveedores (Índigo Púrpura)
    # ==========================================================================
    c3 = cols_x[2]
    p.append(draw_diamond_module(c3, sub_y, ["Módulo: Sucursales,", "Inventario y", "Proveedores"], "#6366f1", 54))

    c3_l = c3 - 105
    c3_r = c3 + 105

    # 3.1 Tiendas y Sucursales
    p.append(draw_path_arrow(f"M {c3 - 55} {sub_y + 35} L {c3 - 55} 435 L {c3_l} 435 L {c3_l} 440"))
    p.append(draw_page_box(c3_l, 440, "Cadena de Tiendas", 155, 30))
    p.append(draw_arrow(c3_l, 470, c3_l, 490))
    p.append(draw_cu_box(c3_l, 490, "CU15", "Gestionar Tiendas", 155, 34))

    p.append(draw_arrow(c3_l, 524, c3_l, 550))
    p.append(draw_page_box(c3_l, 550, "Sucursales & Ciudades", 155, 30))
    p.append(draw_arrow(c3_l, 580, c3_l, 600))
    p.append(draw_cu_box(c3_l, 600, "CU16", "Gestionar Sucursales", 155, 34))

    p.append(draw_arrow(c3_l, 634, c3_l, 660))
    p.append(draw_page_box(c3_l, 660, "Mapa de Sucursales", 155, 30))
    p.append(draw_arrow(c3_l, 690, c3_l, 710))
    p.append(draw_cu_box(c3_l, 710, "CU26", "Mostrar Ubicaciones", 155, 34))

    # 3.2 Proveedores e Inventario Kardex
    p.append(draw_path_arrow(f"M {c3 + 55} {sub_y + 35} L {c3 + 55} 435 L {c3_r} 435 L {c3_r} 440"))
    p.append(draw_page_box(c3_r, 440, "Proveedores", 155, 30))
    p.append(draw_arrow(c3_r, 470, c3_r, 490))
    p.append(draw_cu_box(c3_r, 490, "CU21", "Gestionar Proveedores", 155, 34))

    p.append(draw_arrow(c3_r, 524, c3_r, 550))
    p.append(draw_page_box(c3_r, 550, "Kardex Inventario", 155, 30))
    p.append(draw_arrow(c3_r, 580, c3_r, 600))
    p.append(draw_cu_box(c3_r, 600, "CU22", "Gestionar Inventario", 155, 34))

    p.append(draw_arrow(c3_r, 634, c3_r, 660))
    p.append(draw_page_box(c3_r, 660, "Disponibilidad Prendas", 155, 30))
    p.append(draw_arrow(c3_r, 690, c3_r, 710))
    p.append(draw_cu_box(c3_r, 710, "CU23", "Disponibilidad Stock", 155, 34))

    p.append(draw_arrow(c3_r, 744, c3_r, 770))
    p.append(draw_page_box(c3_r, 770, "Stock por Sucursal", 155, 30))
    p.append(draw_arrow(c3_r, 800, c3_r, 820))
    p.append(draw_cu_box(c3_r, 820, "CU07", "Stock Sucursal Físico", 155, 34))


    # ==========================================================================
    # SUBSISTEMA 4: Gestión de E-Commerce (Verde Esmeralda)
    # ==========================================================================
    c4 = cols_x[3]
    p.append(draw_diamond_module(c4, sub_y, ["Módulo:", "Gestión de", "E-Commerce"], "#059669", 54))

    # Flujo secuencial natural de compra
    p.append(draw_arrow(c4, sub_y + 52, c4, 440))
    p.append(draw_page_box(c4, 440, "Carrito de Compras", 175, 30))
    p.append(draw_arrow(c4, 470, c4, 490))
    p.append(draw_cu_box(c4, 490, "CU08", "Gestionar Carrito Compras", 175, 34))

    p.append(draw_arrow(c4, 524, c4, 550, label="[Checkout]"))
    p.append(draw_page_box(c4, 550, "Pantalla de Checkout", 175, 30))
    p.append(draw_arrow(c4, 580, c4, 600))
    p.append(draw_cu_box(c4, 600, "CU09", "Realizar Compra", 175, 34))

    p.append(draw_arrow(c4, 634, c4, 660, label="[Pagar]"))
    p.append(draw_page_box(c4, 660, "Pasarela Digital PayPal", 175, 30))
    p.append(draw_arrow(c4, 690, c4, 710))
    p.append(draw_cu_box(c4, 710, "CU27", "Procesar Pago Electrónico", 175, 34))

    p.append(draw_arrow(c4, 744, c4, 770, label="[Confirmado]"))
    p.append(draw_page_box(c4, 770, "Historial de Pedidos", 175, 30))
    p.append(draw_arrow(c4, 800, c4, 820))
    p.append(draw_cu_box(c4, 820, "CU11", "Consultar Pedidos & Compras", 175, 34))


    # ==========================================================================
    # SUBSISTEMA 5: Reservas (Naranja Atardecer)
    # ==========================================================================
    c5 = cols_x[4]
    p.append(draw_diamond_module(c5, sub_y, ["Módulo:", "Gestión de", "Reservas"], "#ea580c", 54))

    p.append(draw_arrow(c5, sub_y + 52, c5, 440))
    p.append(draw_page_box(c5, 440, "Apartado en Sucursal", 175, 30))
    p.append(draw_arrow(c5, 470, c5, 490))
    p.append(draw_cu_box(c5, 490, "CU10", "Gestionar Reservas (Cliente)", 175, 34))

    p.append(draw_arrow(c5, 524, c5, 550, label="[En Sucursal]"))
    p.append(draw_page_box(c5, 550, "Mostrador de Reservas", 175, 30))
    p.append(draw_arrow(c5, 580, c5, 600))
    p.append(draw_cu_box(c5, 600, "CU25", "Atender y Despachar Reservas", 175, 34))


    # ==========================================================================
    # SUBSISTEMA 6: Punto de Venta (POS) (Rojo Carmesí)
    # ==========================================================================
    c6 = cols_x[5]
    p.append(draw_diamond_module(c6, sub_y, ["Módulo: Punto", "de Venta", "(POS)"], "#e11d48", 54))

    # Flujo secuencial de mostrador
    p.append(draw_arrow(c6, sub_y + 52, c6, 440))
    p.append(draw_page_box(c6, 440, "Terminal Táctil POS", 175, 30))
    p.append(draw_arrow(c6, 470, c6, 490))
    p.append(draw_cu_box(c6, 490, "CU24", "Registrar Venta Presencial", 175, 34))

    p.append(draw_arrow(c6, 524, c6, 550, label="[Cobrar]"))
    p.append(draw_page_box(c6, 550, "Caja de Cobro (Efectivo/QR)", 175, 30))
    p.append(draw_arrow(c6, 580, c6, 600))
    p.append(draw_cu_box(c6, 600, "CU28", "Procesar Pago en Caja", 175, 34))

    p.append(draw_arrow(c6, 634, c6, 660, label="[Emitir]"))
    p.append(draw_page_box(c6, 660, "Comprobante Fiscal / Recibo", 175, 30))
    p.append(draw_arrow(c6, 690, c6, 710))
    p.append(draw_cu_box(c6, 710, "CU29", "Emitir Comprobante de Venta", 175, 34, fill="#bbf7d0", border="#16a34a", text_color="#15803d"))


    # ==========================================================================
    # SUBSISTEMAS NO IMPLEMENTADOS / PROYECTADOS (Extremo inferior derecho / izquierdo)
    # ==========================================================================
    p.append(f'  <!-- Cuadro Informativo de Subsistemas Futuros -->\n')
    p.append(f'  <g filter="url(#shadow)">\n')
    p.append(f'    <rect x="50" y="930" width="460" height="180" rx="8" ry="8" fill="#f8fafc" stroke="#94a3b8" stroke-dasharray="5,4" stroke-width="1.3"/>\n')
    p.append(f'    <text x="280" y="955" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="bold" fill="#475569" text-anchor="middle">SUBSISTEMAS PROYECTADOS / NO IMPLEMENTADOS</text>\n')
    
    # Diamond 1
    p.append(draw_diamond_module(160, 1025, ["Gestión de", "Pedidos y", "Reportes"], "#64748b", 42))
    p.append(draw_cu_box(160, 1070, "CU-REP", "Reportes y Estadísticas BI", 160, 28, fill="#f1f5f9", border="#94a3b8", text_color="#64748b"))

    # Diamond 2
    p.append(draw_diamond_module(380, 1025, ["Inteligencia", "Artificial y", "Recomend."], "#64748b", 42))
    p.append(draw_cu_box(380, 1070, "CU-IA", "Recomendación Estilo / Tallas", 165, 28, fill="#f1f5f9", border="#94a3b8", text_color="#64748b"))
    p.append(f'  </g>\n')

    # Leyenda Estándar
    p.append(f'  <!-- Leyenda Gráfica -->\n')
    p.append(f'  <g filter="url(#shadow)">\n')
    p.append(f'    <rect x="1950" y="930" width="700" height="180" rx="8" ry="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>\n')
    p.append(f'    <text x="2300" y="955" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">CONVENCIONES GRÁFICAS (PLANTILLA SI2 - UAGRM)</text>\n')
    
    # Muestra 1: Rombo
    p.append(draw_diamond_module(2030, 1025, ["Módulo"], "#0284c7", 26))
    p.append(f'    <text x="2080" y="1030" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#334155">Módulo Funcional del Subsistema</text>\n')

    # Muestra 2: Página
    p.append(draw_page_box(2330, 1010, "Nombre Pantalla", 130, 26))
    p.append(f'    <text x="2410" y="1027" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#334155">Pantalla / Vista de Usuario</text>\n')

    # Muestra 3: CU
    p.append(draw_cu_box(2050, 1070, "CUxx", "Caso de Uso Asignado", 140, 26))
    p.append(f'    <text x="2135" y="1087" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#334155">Caso de Uso (CU) Ejecutado</text>\n')

    p.append(f'  </g>\n')

    p.append('</svg>\n')
    return "".join(p)


# ==============================================================================
# DIAGRAMAS MODULARES DE ESTRUCTURA POR SUBSISTEMA (DE01 a DE06)
# ==============================================================================

def make_de_subsystem(title, mod_name, mod_color, flows):
    w, h = 1200, 840
    p = svg_header(w, h, title, "Estructura de Páginas de Navegación y Casos de Uso del Subsistema (SI2)")

    mid_x = w / 2

    # Raíz del flujo
    p.append(draw_system_root(mid_x, 80, "<SISTEMA E-COMMERCE AURA>", 280, 36))
    p.append(draw_arrow(mid_x, 116, mid_x, 140))
    p.append(draw_screen_box(mid_x, 140, "Portal Web / Panel Principal", "Menú de Acceso al Subsistema", 260, 38))
    p.append(draw_arrow(mid_x, 178, mid_x, 210))

    # Módulo
    p.append(draw_diamond_module(mid_x, 260, [f"Módulo:", mod_name], mod_color, 54))

    # Ramas del subsistema
    num_flows = len(flows)
    step = w / (num_flows + 1)
    for i, flow in enumerate(flows):
        fx = step * (i + 1)
        p.append(draw_path_arrow(f"M {mid_x} 310 L {mid_x} 330 L {fx} 330 L {fx} 360"))
        
        curr_y = 360
        for j, node in enumerate(flow):
            ntype = node.get("type", "page")
            if ntype == "page":
                p.append(draw_page_box(fx, curr_y, node["name"], 220, 34))
                curr_y += 34
            elif ntype == "cu":
                p.append(draw_cu_box(fx, curr_y, node["code"], node["name"], 220, 40, 
                                     fill=node.get("fill", "#e0f2fe"), 
                                     border=node.get("border", "#0284c7"), 
                                     text_color=node.get("text_color", "#0369a1")))
                curr_y += 40
            
            # Flecha al siguiente si no es el último
            if j < len(flow) - 1:
                label = node.get("transition", "")
                p.append(draw_arrow(fx, curr_y, fx, curr_y + 30, label=label))
                curr_y += 30

    p.append('</svg>\n')
    return "".join(p)


def make_de01():
    return make_de_subsystem(
        title="Estructura de CU: Subsistema Autenticación y Gestión de Usuarios",
        mod_name="Seguridad y Usuarios",
        mod_color="#10b981",
        flows=[
            [
                {"type": "page", "name": "Registro de Nuevos Clientes", "transition": "[Submit Form]"},
                {"type": "cu", "code": "CU01", "name": "Registrar Usuario"},
                {"type": "page", "name": "Mi Perfil de Usuario", "transition": "[Guardar Cambios]"},
                {"type": "cu", "code": "CU03", "name": "Gestionar Perfil"}
            ],
            [
                {"type": "page", "name": "Inicio de Sesión (Login)", "transition": "[Credenciales Válidas]"},
                {"type": "cu", "code": "CU02", "name": "Iniciar Sesión"},
                {"type": "page", "name": "Gestión de Personal & Roles", "transition": "[Asignar Permisos]"},
                {"type": "cu", "code": "CU14", "name": "Gestionar Usuarios y Roles"},
                {"type": "page", "name": "Visor de Auditoría", "transition": "[Consultar Logs]"},
                {"type": "cu", "code": "CU-AUD", "name": "Auditoría en Bitácora", "fill": "#fef08a", "border": "#ca8a04", "text_color": "#854d0e"}
            ]
        ]
    )

def make_de02():
    return make_de_subsystem(
        title="Estructura de CU: Subsistema Gestión de Catálogo y Colecciones",
        mod_name="Catálogo de Moda",
        mod_color="#0284c7",
        flows=[
            [
                {"type": "page", "name": "Catálogo Público de Prendas", "transition": "[Filtrar por Categoría/Precio]"},
                {"type": "cu", "code": "CU04/CU05", "name": "Buscar y Filtrar Productos"},
                {"type": "page", "name": "Ficha Técnica de Prenda", "transition": "[Seleccionar Talla y Color]"},
                {"type": "cu", "code": "CU06", "name": "Consultar Detalle de Producto"}
            ],
            [
                {"type": "page", "name": "Catálogo Maestro de Prendas", "transition": "[Crear/Editar Prenda]"},
                {"type": "cu", "code": "CU17", "name": "Gestionar Productos"},
                {"type": "page", "name": "Árbol de Categorías de Ropa", "transition": "[Guardar Categoría]"},
                {"type": "cu", "code": "CU18", "name": "Gestionar Categorías"}
            ],
            [
                {"type": "page", "name": "Matriz de Tallas y Colores", "transition": "[Configurar Variantes]"},
                {"type": "cu", "code": "CU19", "name": "Gestionar Tallas y Colores"},
                {"type": "page", "name": "Lanzamiento de Temporadas", "transition": "[Asignar Colección]"},
                {"type": "cu", "code": "CU20", "name": "Gestionar Temporadas y Colecciones"}
            ]
        ]
    )

def make_de03():
    return make_de_subsystem(
        title="Estructura de CU: Subsistema Sucursales, Inventario y Proveedores",
        mod_name="Sucursales e Inventario",
        mod_color="#6366f1",
        flows=[
            [
                {"type": "page", "name": "Red de Tiendas (Tenants)", "transition": "[Registrar Empresa]"},
                {"type": "cu", "code": "CU15", "name": "Gestionar Cadena de Tiendas"},
                {"type": "page", "name": "Sucursales Físicas por Ciudad", "transition": "[Nueva Sucursal]"},
                {"type": "cu", "code": "CU16", "name": "Gestionar Sucursales y Ciudades"},
                {"type": "page", "name": "Geolocalización y Mapa Leaflet", "transition": "[Ver en Mapa]"},
                {"type": "cu", "code": "CU26", "name": "Mostrar Ubicaciones de Sucursales"}
            ],
            [
                {"type": "page", "name": "Directorio de Proveedores", "transition": "[Registrar Proveedor]"},
                {"type": "cu", "code": "CU21", "name": "Gestionar Proveedores"},
                {"type": "page", "name": "Kardex de Inventario Central", "transition": "[Entrada/Salida Stock]"},
                {"type": "cu", "code": "CU22", "name": "Gestionar Inventario Multialmacén"},
                {"type": "page", "name": "Matriz de Disponibilidad", "transition": "[Verificar Stock]"},
                {"type": "cu", "code": "CU23", "name": "Gestionar Disponibilidad de Prendas"},
                {"type": "page", "name": "Consulta de Existencia Local", "transition": "[Stock Sucursal]"},
                {"type": "cu", "code": "CU07", "name": "Consultar Disponibilidad por Sucursal"}
            ]
        ]
    )

def make_de04():
    return make_de_subsystem(
        title="Estructura de CU: Subsistema Gestión de E-Commerce",
        mod_name="E-Commerce y Pagos",
        mod_color="#059669",
        flows=[
            [
                {"type": "page", "name": "Drawer / Vista de Carrito", "transition": "[Modificar Cantidad / Ítem]"},
                {"type": "cu", "code": "CU08", "name": "Gestionar Carrito de Compras"},
                {"type": "page", "name": "Pasarela de Checkout Final", "transition": "[Confirmar Datos Entrega]"},
                {"type": "cu", "code": "CU09", "name": "Realizar Compra Online"},
                {"type": "page", "name": "Pasarela Digital PayPal API", "transition": "[Aprobación de Pago]"},
                {"type": "cu", "code": "CU27", "name": "Procesar Pago Electrónico"},
                {"type": "page", "name": "Historial y Tracking de Pedidos", "transition": "[Ver Detalle Pedido]"},
                {"type": "cu", "code": "CU11", "name": "Consultar Pedidos e Historial"}
            ]
        ]
    )

def make_de05():
    return make_de_subsystem(
        title="Estructura de CU: Subsistema de Reservas",
        mod_name="Gestión de Reservas",
        mod_color="#ea580c",
        flows=[
            [
                {"type": "page", "name": "Modal de Apartado en Tienda", "transition": "[Confirmar Reserva 48h]"},
                {"type": "cu", "code": "CU10", "name": "Gestionar Reservas (Cliente)"},
                {"type": "page", "name": "Panel de Mostrador de Sucursal", "transition": "[Cliente Acude a Tienda]"},
                {"type": "cu", "code": "CU25", "name": "Atender y Despachar Reservas"}
            ]
        ]
    )

def make_de06():
    return make_de_subsystem(
        title="Estructura de CU: Subsistema Punto de Venta (POS) y Facturación",
        mod_name="Punto de Venta (POS)",
        mod_color="#e11d48",
        flows=[
            [
                {"type": "page", "name": "Terminal Táctil / Escáner POS", "transition": "[Asentar Venta en Mostrador]"},
                {"type": "cu", "code": "CU24", "name": "Registrar Venta Presencial"},
                {"type": "page", "name": "Caja de Cobro Multimoneda", "transition": "[Recibir Efectivo / QR]"},
                {"type": "cu", "code": "CU28", "name": "Procesar Pago en Caja"},
                {"type": "page", "name": "Emisión Fiscal (PDF / Térmico)", "transition": "[Imprimir / Enviar Correo]"},
                {"type": "cu", "code": "CU29", "name": "Emitir Comprobante de Venta", "fill": "#bbf7d0", "border": "#16a34a", "text_color": "#15803d"}
            ]
        ]
    )


# ==============================================================================
# DE_PAQUETES: DIAGRAMA UML FORMAL DE PAQUETES DE CASOS DE USO
# ==============================================================================

def make_de_paquetes_uml():
    w, h = 1450, 940
    p = svg_header(w, h, 
                   "Diagrama de Paquetes de Casos de Uso UML 2.5 - Sistema Aura", 
                   "Agrupación Modular de Casos de Uso por Subsistemas con Actores del Negocio")

    # Función para dibujar paquete UML (carpeta) con pestaña ancha proporcional
    def draw_uml_package(x, y, pw, ph, name, cus, tab_w=280):
        res = [
            f'  <!-- Paquete: {name} -->\n',
            f'  <g filter="url(#shadow)">\n',
            f'    <path d="M {x} {y + 20} L {x} {y} L {x + tab_w - 15} {y} L {x + tab_w} {y + 20} Z" fill="#f8fafc" stroke="#334155" stroke-width="1.3"/>\n',
            f'    <rect x="{x}" y="{y + 20}" width="{pw}" height="{ph - 20}" fill="#ffffff" stroke="#334155" stroke-width="1.3"/>\n',
            f'    <text x="{x + tab_w/2 - 5}" y="{y + 14}" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="bold" fill="#0f172a" text-anchor="middle">{escape_xml(name)}</text>\n'
        ]
        # Dibujar óvalos de casos de uso dentro del paquete
        for i, (code, cname) in enumerate(cus):
            col = i % 2
            row = i // 2
            ow = 230
            ox = x + 25 + col * (ow + 25)
            oy = y + 42 + row * 54
            res.append(f'    <ellipse cx="{ox + ow/2}" cy="{oy + 18}" rx="{ow/2}" ry="18" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.2"/>\n')
            res.append(f'    <text x="{ox + ow/2}" y="{oy + 15}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" font-weight="bold" fill="#0369a1" text-anchor="middle">«CU» {escape_xml(code)}</text>\n')
            res.append(f'    <text x="{ox + ow/2}" y="{oy + 27}" font-family="Arial, Helvetica, sans-serif" font-size="8" fill="#0f172a" text-anchor="middle">{escape_xml(cname)}</text>\n')
        res.append('  </g>\n')
        return "".join(res)

    def draw_actor(x, y, name):
        return (
            f'  <g id="actor_{name}">\n'
            f'    <circle cx="{x}" cy="{y - 28}" r="11" fill="#ffffff" stroke="#0f172a" stroke-width="1.6"/>\n'
            f'    <line x1="{x}" y1="{y - 17}" x2="{x}" y2="{y + 10}" stroke="#0f172a" stroke-width="1.6"/>\n'
            f'    <line x1="{x - 16}" y1="{y - 8}" x2="{x + 16}" y2="{y - 8}" stroke="#0f172a" stroke-width="1.6"/>\n'
            f'    <line x1="{x}" y1="{y + 10}" x2="{x - 12}" y2="{y + 34}" stroke="#0f172a" stroke-width="1.6"/>\n'
            f'    <line x1="{x}" y1="{y + 10}" x2="{x + 12}" y2="{y + 34}" stroke="#0f172a" stroke-width="1.6"/>\n'
            f'    <text x="{x}" y="{y + 49}" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="bold" fill="#0f172a" text-anchor="middle">{escape_xml(name)}</text>\n'
            f'  </g>\n'
        )

    # Actores a la izquierda
    p.append(draw_actor(70, 160, "CLIENTE"))
    p.append(draw_actor(70, 360, "USUARIO"))
    p.append(draw_actor(70, 560, "CAJERO"))
    p.append(draw_actor(70, 760, "ADMINISTRADOR"))

    # Paquetes de Subsistemas
    # Fila 1
    p.append(draw_uml_package(200, 90, 560, 240, "AUTENTICACIÓN Y GESTIÓN DE USUARIOS", [
        ("CU01", "Registrar Usuario"),
        ("CU02", "Iniciar Sesión"),
        ("CU03", "Gestionar Perfil"),
        ("CU14", "Gestionar Usuarios y Roles"),
        ("CU-AUD", "Auditoría en Bitácora"),
    ], tab_w=280))

    p.append(draw_uml_package(820, 90, 560, 240, "GESTIÓN DE CATÁLOGO", [
        ("CU04/CU05", "Buscar y Filtrar Productos"),
        ("CU06", "Consultar Detalle de Producto"),
        ("CU17", "Gestionar Productos"),
        ("CU18", "Gestionar Categorías"),
        ("CU19", "Gestionar Tallas y Colores"),
        ("CU20", "Gestionar Colecciones"),
    ], tab_w=190))

    # Fila 2
    p.append(draw_uml_package(200, 370, 560, 250, "SUCURSALES, INVENTARIO Y PROVEEDORES", [
        ("CU15", "Gestionar Cadena de Tiendas"),
        ("CU16", "Gestionar Sucursales y Ciudades"),
        ("CU26", "Mostrar Ubicaciones Sucursales"),
        ("CU21", "Gestionar Proveedores"),
        ("CU22", "Gestionar Inventario"),
        ("CU23", "Disponibilidad Prendas"),
        ("CU07", "Stock por Sucursal"),
    ], tab_w=285))

    p.append(draw_uml_package(820, 370, 560, 250, "GESTIÓN DE E-COMMERCE", [
        ("CU08", "Gestionar Carrito de Compras"),
        ("CU09", "Realizar Compra Online"),
        ("CU27", "Procesar Pago Electrónico"),
        ("CU11", "Consultar Pedidos e Historial"),
    ], tab_w=200))

    # Fila 3
    p.append(draw_uml_package(200, 650, 560, 220, "RESERVAS", [
        ("CU10", "Gestionar Reservas (Cliente)"),
        ("CU25", "Atender Reservas (Encargado)"),
    ], tab_w=140))

    p.append(draw_uml_package(820, 650, 560, 220, "GESTIÓN DE PUNTO DE VENTA (POS)", [
        ("CU24", "Registrar Venta Presencial"),
        ("CU28", "Procesar Pago en Caja"),
        ("CU29", "Emitir Comprobante de Venta"),
    ], tab_w=240))

    # Líneas de asociación entre Actores y Paquetes (ortogonales y limpias)
    p.append(f'  <path d="M 100 160 L 150 160 L 150 200 L 200 200" fill="none" stroke="#475569" stroke-width="1.2"/>\n')
    p.append(f'  <path d="M 100 160 L 150 160 L 150 50 L 780 50 L 780 180 L 820 180" fill="none" stroke="#475569" stroke-width="1.2" stroke-dasharray="4,3"/>\n')
    p.append(f'  <path d="M 100 360 L 170 360 L 170 230 L 200 230" fill="none" stroke="#475569" stroke-width="1.2"/>\n')
    p.append(f'  <path d="M 100 560 L 170 560 L 170 760 L 820 760" fill="none" stroke="#475569" stroke-width="1.2"/>\n')
    p.append(f'  <path d="M 100 760 L 150 760 L 150 500 L 200 500" fill="none" stroke="#475569" stroke-width="1.2"/>\n')

    p.append('</svg>\n')
    return "".join(p)


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    out_dir = "docs/diagramas_estructura_cu"
    os.makedirs(out_dir, exist_ok=True)

    diagrams = [
        ("DE_CU00_Estructura_Casos_De_Uso_General_Sistema_Aura", make_de00_master),
        ("DE_CU01_Estructura_Usuarios_Autenticacion", make_de01),
        ("DE_CU02_Estructura_Catalogo_Colecciones", make_de02),
        ("DE_CU03_Estructura_Sucursales_Inventario", make_de03),
        ("DE_CU04_Estructura_Ecommerce_Compras_Pagos", make_de04),
        ("DE_CU05_Estructura_Reservas", make_de05),
        ("DE_CU06_Estructura_Punto_De_Venta_POS", make_de06),
        ("DE_CU_Paquetes_UML", make_de_paquetes_uml),
    ]

    print("=== GENERANDO DIAGRAMAS DE ESTRUCTURA DE CASOS DE USO (SI2) ===")
    for filename, func in diagrams:
        svg_content = func()
        svg_path = os.path.join(out_dir, f"{filename}.svg")
        png_path = os.path.join(out_dir, f"{filename}.png")

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        cairosvg.svg2png(bytestring=svg_content.encode("utf-8"), write_to=png_path, scale=2.0)
        print(f"[OK] {filename} -> SVG & PNG (2x)")

    print("\n¡Todos los Diagramas de Estructura de CU generados exitosamente!")

if __name__ == "__main__":
    main()
