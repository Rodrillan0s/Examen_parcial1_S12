#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de los Diagramas de Navegación Web UML / SI2
Sistema E-Commerce Multi-Tenant para Venta de Ropa Aura (SI2 - UAGRM)

Se generan 4 diagramas modulares para evitar diagramas excesivamente largos o ilegibles:
- DN00: Mapa General de Navegación del Sistema (Hub / Macro-Enrutador)
- DN01: Navegación de la Tienda E-Commerce, Catálogo y Checkout de Cliente
- DN02: Navegación Operativa de Sucursal, Punto de Venta (POS), Cobro y Facturación
- DN03: Navegación del Panel Administrativo, Catálogo Central, Red de Tiendas y Auditoría

Todos los diagramas parten de la misma raíz:
  <SISTEMA E-COMMERCE AURA> -> [Portal Web / Inicio de Sesión]
agrupando las pantallas que se relacionan directamente para mantener la cohesión.
"""

import os
import sys
import xml.sax.saxutils
import cairosvg

def escape_xml(text):
    return xml.sax.saxutils.escape(str(text))

# ------------------------------------------------------------------------------
# Helpers SVG de Dibujo
# ------------------------------------------------------------------------------

def svg_header(w, h, title, subtitle=""):
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n',
        '  <defs>\n',
        '    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">\n',
        '      <path d="M 0 1 L 7 4 L 0 7 Z" fill="#334155"/>\n',
        '    </marker>\n',
        '    <marker id="arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">\n',
        '      <path d="M 0 1 L 7 4 L 0 7 Z" fill="#0284c7"/>\n',
        '    </marker>\n',
        '    <marker id="arrow-green" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">\n',
        '      <path d="M 0 1 L 7 4 L 0 7 Z" fill="#16a34a"/>\n',
        '    </marker>\n',
        '    <marker id="arrow-orange" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">\n',
        '      <path d="M 0 1 L 7 4 L 0 7 Z" fill="#ea580c"/>\n',
        '    </marker>\n',
        '    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">\n',
        '      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-color="#000000" flood-opacity="0.07"/>\n',
        '    </filter>\n',
        '  </defs>\n\n',
        f'  <!-- Fondo Blanco con Rejilla Sutil -->\n',
        f'  <rect x="0" y="0" width="{w}" height="{h}" fill="#fcfdfd"/>\n',
    ]
    for gx in range(0, w, 40):
        parts.append(f'  <line x1="{gx}" y1="0" x2="{gx}" y2="{h}" stroke="#f1f5f9" stroke-width="0.8"/>\n')
    for gy in range(0, h, 40):
        parts.append(f'  <line x1="0" y1="{gy}" x2="{w}" y2="{gy}" stroke="#f1f5f9" stroke-width="0.8"/>\n')

    parts.append(f'  <rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="#cbd5e1" stroke-width="1.5"/>\n\n')
    parts.append(f'  <text x="{w/2}" y="36" font-family="Arial, Helvetica, sans-serif" font-size="20" font-weight="bold" fill="#0f172a" text-anchor="middle">{escape_xml(title)}</text>\n')
    if subtitle:
        parts.append(f'  <text x="{w/2}" y="55" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#64748b" text-anchor="middle">{escape_xml(subtitle)}</text>\n\n')
    return parts

def draw_system_root(cx, y, name="<SISTEMA E-COMMERCE AURA>", w=250, h=34):
    return (
        f'  <!-- Raíz del Sistema -->\n'
        f'  <g filter="url(#shadow)">\n'
        f'    <rect x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="17" ry="17" fill="#dcfce7" stroke="#16a34a" stroke-width="1.6"/>\n'
        f'    <text x="{cx}" y="{y + h/2 + 4.5}" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="bold" fill="#14532d" text-anchor="middle">{escape_xml(name)}</text>\n'
        f'  </g>\n'
    )

def draw_menu_hub(cx, y, title, subtitle="", w=250, h=44, bg="#ffffff", stroke="#475569"):
    res = [
        f'  <!-- Hub / Pantalla Intermedia -->\n',
        f'  <g filter="url(#shadow)">\n',
        f'    <rect x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="6" ry="6" fill="{bg}" stroke="{stroke}" stroke-width="1.4"/>\n'
    ]
    if subtitle:
        res.append(f'    <text x="{cx}" y="{y + 17}" font-family="Arial, Helvetica, sans-serif" font-size="11.5" font-weight="bold" fill="#0f172a" text-anchor="middle">{escape_xml(title)}</text>\n')
        res.append(f'    <text x="{cx}" y="{y + 32}" font-family="Arial, Helvetica, sans-serif" font-size="9.5" fill="#64748b" text-anchor="middle">{escape_xml(subtitle)}</text>\n')
    else:
        res.append(f'    <text x="{cx}" y="{y + h/2 + 4}" font-family="Arial, Helvetica, sans-serif" font-size="11.5" font-weight="bold" fill="#0f172a" text-anchor="middle">{escape_xml(title)}</text>\n')
    res.append(f'  </g>\n')
    return "".join(res)

def draw_module_diamond(cx, cy, label_lines, color="#0284c7", size=48):
    p_top = f"{cx},{cy - size}"
    p_right = f"{cx + size*1.45},{cy}"
    p_bottom = f"{cx},{cy + size}"
    p_left = f"{cx - size*1.45},{cy}"
    points = f"{p_top} {p_right} {p_bottom} {p_left}"
    
    res = [
        f'  <!-- Módulo Rombo -->\n',
        f'  <g filter="url(#shadow)">\n',
        f'    <polygon points="{points}" fill="{color}" stroke="#ffffff" stroke-width="1.8"/>\n'
    ]
    total_lines = len(label_lines)
    start_y = cy - (total_lines - 1) * 6
    for i, line in enumerate(label_lines):
        ly = start_y + i * 13 + 4
        res.append(f'    <text x="{cx}" y="{ly}" font-family="Arial, Helvetica, sans-serif" font-size="9.5" font-weight="bold" fill="#ffffff" text-anchor="middle">{escape_xml(line)}</text>\n')
    res.append(f'  </g>\n')
    return "".join(res)

def draw_page_box(cx, y, name, w=185, h=34):
    return (
        f'  <!-- Página UI -->\n'
        f'  <g filter="url(#shadow)">\n'
        f'    <rect x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="5" ry="5" fill="#ffffff" stroke="#64748b" stroke-width="1.1"/>\n'
        f'    <text x="{cx}" y="{y + h/2 + 3.5}" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="500" fill="#1e293b" text-anchor="middle">Página: {escape_xml(name)}</text>\n'
        f'  </g>\n'
    )

def draw_drawer_box(cx, y, name, w=185, h=34):
    return (
        f'  <!-- Drawer / Modal UI -->\n'
        f'  <g filter="url(#shadow)">\n'
        f'    <rect x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="5" ry="5" fill="#fffbeb" stroke="#d97706" stroke-width="1.2" stroke-dasharray="4,2"/>\n'
        f'    <text x="{cx}" y="{y + h/2 + 3.5}" font-family="Arial, Helvetica, sans-serif" font-size="9.5" font-weight="600" fill="#92400e" text-anchor="middle">Modal/Drawer: {escape_xml(name)}</text>\n'
        f'  </g>\n'
    )

def draw_cu_box(cx, y, cu_code, cu_title, w=185, h=34, fill="#dbeafe", stroke="#3b82f6", text_color="#1e40af"):
    return (
        f'  <!-- Caso de Uso -->\n'
        f'  <g filter="url(#shadow)">\n'
        f'    <rect x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="6" ry="6" fill="{fill}" stroke="{stroke}" stroke-width="1.1"/>\n'
        f'    <text x="{cx}" y="{y + 13}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" font-weight="bold" fill="{text_color}" text-anchor="middle">«CU» {escape_xml(cu_code)}</text>\n'
        f'    <text x="{cx}" y="{y + 26}" font-family="Arial, Helvetica, sans-serif" font-size="9" fill="{text_color}" text-anchor="middle">{escape_xml(cu_title)}</text>\n'
        f'  </g>\n'
    )

def draw_link_box(cx, y, title, dest_text, w=195, h=38, bg="#eff6ff", stroke="#3b82f6", color="#1d4ed8"):
    return (
        f'  <!-- Enlace a Sub-Diagrama -->\n'
        f'  <g filter="url(#shadow)">\n'
        f'    <rect x="{cx - w/2}" y="{y}" width="{w}" height="{h}" rx="6" ry="6" fill="{bg}" stroke="{stroke}" stroke-width="1.3" stroke-dasharray="4,2"/>\n'
        f'    <text x="{cx}" y="{y + 15}" font-family="Arial, Helvetica, sans-serif" font-size="9.5" font-weight="bold" fill="{color}" text-anchor="middle">{escape_xml(title)}</text>\n'
        f'    <text x="{cx}" y="{y + 29}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="{color}" text-anchor="middle">{escape_xml(dest_text)}</text>\n'
        f'  </g>\n'
    )

def draw_v_arrow(cx, y1, y2, label="", dashed=False, marker="url(#arrow)"):
    dash = ' stroke-dasharray="4,3"' if dashed else ''
    res = [f'  <line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2}" stroke="#334155" stroke-width="1.2"{dash} marker-end="{marker}"/>\n']
    if label:
        mid_y = (y1 + y2) / 2 + 3
        res.append(f'  <text x="{cx + 6}" y="{mid_y}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#334155">{escape_xml(label)}</text>\n')
    return "".join(res)

def draw_line(x1, y1, x2, y2, label="", label_x=None, label_y=None, dashed=False, marker="url(#arrow)", text_anchor="start"):
    dash = ' stroke-dasharray="4,3"' if dashed else ''
    res = [f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#334155" stroke-width="1.2"{dash} marker-end="{marker}"/>\n']
    if label:
        lx = label_x if label_x is not None else (x1 + x2) / 2 + 5
        ly = label_y if label_y is not None else (y1 + y2) / 2 - 4
        res.append(f'  <text x="{lx}" y="{ly}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#334155" text-anchor="{text_anchor}">{escape_xml(label)}</text>\n')
    return "".join(res)

def draw_ortho_step(x1, y1, x2, y2, label="", label_x=None, label_y=None, dashed=False, marker="url(#arrow)"):
    dash = ' stroke-dasharray="4,3"' if dashed else ''
    y_mid = (y1 + y2) / 2
    path_d = f"M {x1} {y1} L {x1} {y_mid} L {x2} {y_mid} L {x2} {y2}"
    res = [f'  <path d="{path_d}" fill="none" stroke="#334155" stroke-width="1.2"{dash} marker-end="{marker}"/>\n']
    if label:
        lx = label_x if label_x is not None else (x1 + x2) / 2
        ly = label_y if label_y is not None else y_mid - 4
        res.append(f'  <text x="{lx}" y="{ly}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#334155" text-anchor="middle">{escape_xml(label)}</text>\n')
    return "".join(res)

# ==============================================================================
# 1. DN00: Mapa General de Navegación del Sistema (Hub / Macro-Enrutador)
# ==============================================================================
def make_dn00_mapa_general():
    w, h, cx = 1140, 680, 570
    p = svg_header(w, h, "Diagrama de Navegación Maestro: Sistema E-Commerce Aura",
                   "Estructura Global y Distribución de Subsistemas (Partiendo del Portal Web y Autenticación Común)")
    
    # Raíz común
    p.append(draw_system_root(cx, 75, "<SISTEMA E-COMMERCE AURA>", 270, 36))
    p.append(draw_v_arrow(cx, 111, 140))

    # Entrada principal
    p.append(draw_menu_hub(cx, 140, "Portal Web & Autenticación", "Punto de Acceso Unificado (Explorar / Login)", 270, 42))
    p.append(draw_v_arrow(cx, 182, 215))

    # Enrutador Central
    p.append(draw_menu_hub(cx, 215, "Enrutador Central de Navegación (Angular Router)", "Distribución por Rol y Contexto Operativo", 310, 42, bg="#f8fafc", stroke="#2563eb"))
    
    # 3 Subsistemas
    x1, x2, x3 = 235, 570, 905
    y_rombo = 340
    
    # Conexiones desde el enrutador
    p.append(draw_ortho_step(cx - 100, 257, x1, y_rombo - 48, "Rol: Cliente Retail"))
    p.append(draw_v_arrow(x2, 257, y_rombo - 48, "Rol: Cajero / Sucursal"))
    p.append(draw_ortho_step(cx + 100, 257, x3, y_rombo - 48, "Rol: Admin / Tienda"))

    # Rombos de Módulos
    p.append(draw_module_diamond(x1, y_rombo, ["Módulo:", "Tienda Retail y", "Checkout Cliente"], color="#0284c7", size=48))
    p.append(draw_module_diamond(x2, y_rombo, ["Módulo:", "Operaciones Sucursal", "y Caja POS"], color="#ea580c", size=48))
    p.append(draw_module_diamond(x3, y_rombo, ["Módulo:", "Panel Administrativo", "y Catálogo Central"], color="#7c3aed", size=48))

    # Resumen de Pantallas bajo cada subsistema
    y_p = 425
    p.append(draw_v_arrow(x1, y_rombo + 48, y_p))
    p.append(draw_v_arrow(x2, y_rombo + 48, y_p))
    p.append(draw_v_arrow(x3, y_rombo + 48, y_p))

    p.append(draw_menu_hub(x1, y_p, "Área de Compras y Autoservicio", "Catálogo, Carrito, Checkout, Pagos y Pedidos", 260, 48))
    p.append(draw_menu_hub(x2, y_p, "Área Operativa de Mostrador", "Terminal POS, Cobro en Caja, Factura e Inventario", 260, 48))
    p.append(draw_menu_hub(x3, y_p, "Área de Configuración y Control", "KPIs, Prendas, Colecciones, Proveedores y Bitácora", 260, 48))

    # Casos de uso cubiertos
    y_cu = 505
    p.append(draw_v_arrow(x1, y_p + 48, y_cu))
    p.append(draw_v_arrow(x2, y_p + 48, y_cu))
    p.append(draw_v_arrow(x3, y_p + 48, y_cu))

    p.append(draw_cu_box(x1, y_cu, "CU05..CU11, CU26, CU_W27", "8 Casos de Uso de Cliente", 240, 36))
    p.append(draw_cu_box(x2, y_cu, "CU_W22, CU_W24, CU_W25, W28, W29", "5 Casos de Uso de Sucursal / POS", 240, 36, fill="#ffedd5", stroke="#f97316", text_color="#c2410c"))
    p.append(draw_cu_box(x3, y_cu, "CU_W20, CU_W21, CU_W23, Dashboard", "4 Casos de Uso Administrativos", 240, 36, fill="#f3e8ff", stroke="#a855f7", text_color="#6b21a8"))

    # Enlaces a sub-diagramas
    y_link = 575
    p.append(draw_v_arrow(x1, y_cu + 36, y_link))
    p.append(draw_v_arrow(x2, y_cu + 36, y_link))
    p.append(draw_v_arrow(x3, y_cu + 36, y_link))

    p.append(draw_link_box(x1, y_link, "DETALLE EN DIAGRAMA DN-01", "Navegación Cliente & Checkout", 240, 38))
    p.append(draw_link_box(x2, y_link, "DETALLE EN DIAGRAMA DN-02", "Operaciones Sucursal & POS", 240, 38, bg="#fff7ed", stroke="#ea580c", color="#c2410c"))
    p.append(draw_link_box(x3, y_link, "DETALLE EN DIAGRAMA DN-03", "Administración & Catálogo", 240, 38, bg="#faf5ff", stroke="#9333ea", color="#7e22ce"))

    p.append('</svg>\n')
    return "".join(p)


# ==============================================================================
# 2. DN01: Navegación de la Tienda E-Commerce, Catálogo y Checkout de Cliente
# ==============================================================================
def make_dn01_cliente():
    w, h, cx = 1200, 820, 600
    p = svg_header(w, h, "Diagrama de Navegación 01: Tienda E-Commerce, Catálogo y Checkout de Cliente",
                   "Flujo Integral de Navegación de Cliente: Exploración, Selección de Prendas, Carrito, Pasarela y Seguimiento")
    
    # Raíz común
    p.append(draw_system_root(cx, 75, "<SISTEMA E-COMMERCE AURA>", 270, 34))
    p.append(draw_v_arrow(cx, 109, 135))

    # Punto de Entrada: Explorar / Landing
    p.append(draw_page_box(cx, 135, "Explorar y Colecciones (Landing /)", 250, 36))
    p.append(draw_v_arrow(cx, 171, 195))
    p.append(draw_cu_box(cx, 195, "CU26/M15", "Mostrar Ubicaciones de Sucursales", 230, 34))

    # 3 Columnas:
    # Col 1: Catálogo y Ficha de Prenda (Azul)
    # Col 2: Carrito y Checkout Transaccional (Verde)
    # Col 3: Área Personal y Autoservicio (Naranja)
    c1, c2, c3 = 240, 600, 960
    y_rombo = 295

    # Flechas desde Explorar / Landing
    p.append(draw_ortho_step(cx - 110, 153, c1, y_rombo - 46, "Click Catálogo"))
    p.append(draw_v_arrow(c2, 229, y_rombo - 46, "Acción de Compra"))
    p.append(draw_ortho_step(cx + 110, 153, c3, y_rombo - 46, "Click Mi Cuenta"))

    # Rombos
    p.append(draw_module_diamond(c1, y_rombo, ["Módulo:", "Catálogo y Ficha", "de Prenda"], color="#0284c7", size=46))
    p.append(draw_module_diamond(c2, y_rombo, ["Módulo:", "Carrito y Checkout", "Transaccional"], color="#16a34a", size=46))
    p.append(draw_module_diamond(c3, y_rombo, ["Módulo:", "Área Personal y", "Autoservicio"], color="#ea580c", size=46))

    # --- COLUMNA 1: Catálogo & Prenda ---
    p.append(draw_v_arrow(c1, y_rombo + 46, 370))
    p.append(draw_page_box(c1, 370, "Catálogo General (/catalogo)", 200, 34))
    p.append(draw_v_arrow(c1, 404, 425))
    p.append(draw_cu_box(c1, 425, "CU05 W/M", "Buscar y Filtrar Productos", 195, 34))

    p.append(draw_v_arrow(c1, 459, 485, "[Click en Prenda]"))
    p.append(draw_page_box(c1, 485, "Detalle Prenda (/catalogo/:id)", 200, 34))
    p.append(draw_v_arrow(c1, 519, 540))
    p.append(draw_cu_box(c1, 540, "CU06 W/M", "Consultar Detalle de Producto", 195, 34))

    p.append(draw_v_arrow(c1, 574, 605, "[Consultar Stock]"))
    p.append(draw_drawer_box(c1, 605, "Disponibilidad en Tiendas", 200, 34))
    p.append(draw_v_arrow(c1, 639, 660))
    p.append(draw_cu_box(c1, 660, "CU07 W/M", "Consultar Disponibilidad Sucursal", 200, 34))

    # --- COLUMNA 2: Carrito y Checkout ---
    # Conexión limpia desde Detalle Prenda al Carrito
    p.append(draw_line(c1 + 100, 502, c2 - 105, 387, "[Agregar al Carrito]", label_x=370, label_y=435))

    p.append(draw_v_arrow(c2, y_rombo + 46, 370))
    p.append(draw_drawer_box(c2, 370, "Carrito de Compras (Drawer)", 210, 34))
    p.append(draw_v_arrow(c2, 404, 425))
    p.append(draw_cu_box(c2, 425, "CU08 W/M", "Gestionar Carrito de Compras", 205, 34, fill="#dcfce7", stroke="#16a34a", text_color="#14532d"))

    p.append(draw_v_arrow(c2, 459, 485, "[Ir al Checkout]"))
    p.append(draw_page_box(c2, 485, "Checkout (/checkout)", 200, 34))
    p.append(draw_v_arrow(c2, 519, 540))
    p.append(draw_cu_box(c2, 540, "CU09 W/M", "Realizar Compra", 195, 34, fill="#dcfce7", stroke="#16a34a", text_color="#14532d"))

    p.append(draw_v_arrow(c2, 574, 605, "[Pago Digital]"))
    p.append(draw_page_box(c2, 605, "Pasarela de Pago (/pago/:id)", 200, 34))
    p.append(draw_v_arrow(c2, 639, 660))
    p.append(draw_cu_box(c2, 660, "CU_W27", "Procesar Pago Electrónico", 195, 34, fill="#dcfce7", stroke="#16a34a", text_color="#14532d"))

    p.append(draw_v_arrow(c2, 694, 720, "[Pago Aprobado]"))
    p.append(draw_page_box(c2, 720, "Pedido Confirmado (/pedido-confirmado/:id)", 235, 34))

    # --- COLUMNA 3: Área Personal y Autoservicio ---
    p.append(draw_v_arrow(c3, y_rombo + 46, 370))
    p.append(draw_page_box(c3, 370, "Mi Perfil (/perfil)", 195, 34))

    p.append(draw_v_arrow(c3, 404, 460, "[Historial de Compras]"))
    p.append(draw_page_box(c3, 460, "Mis Pedidos (/mis-pedidos)", 195, 34))
    p.append(draw_v_arrow(c3, 494, 515))
    p.append(draw_cu_box(c3, 515, "CU11 W/M", "Consultar Pedidos e Historial", 195, 34, fill="#ffedd5", stroke="#ea580c", text_color="#c2410c"))

    p.append(draw_v_arrow(c3, 549, 605, "[Mis Reservas Activas]"))
    p.append(draw_page_box(c3, 605, "Mis Reservas (/mis-reservas)", 195, 34))
    p.append(draw_v_arrow(c3, 639, 660))
    p.append(draw_cu_box(c3, 660, "CU10 W/M", "Gestionar Reservas (48 Horas)", 195, 34, fill="#ffedd5", stroke="#ea580c", text_color="#c2410c"))

    # CONEXIONES TRANSVERSALES LIMPIAS (Sin cruces molestos):
    # 1. Pedido Confirmado -> Mis Pedidos (sube por el pasillo entre c2 y c3)
    p_track = "M 718 737 L 800 737 L 800 477 L 862 477"
    p.append(f'  <path d="{p_track}" fill="none" stroke="#334155" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>\n')
    p.append('  <text x="810" y="600" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#334155">[Ver Seguimiento]</text>\n')

    # 2. Disponibilidad en Tiendas -> Mis Reservas (baja por el piso exterior sin tocar nada)
    p_reserva = "M 240 694 L 240 770 L 960 770 L 960 694"
    p.append(f'  <path d="{p_reserva}" fill="none" stroke="#ea580c" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow-orange)"/>\n')
    p.append('  <text x="600" y="785" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#ea580c" text-anchor="middle">[Confirmar Reserva de Prenda (48 Horas Retención Activa)]</text>\n')

    p.append('</svg>\n')
    return "".join(p)


# ==============================================================================
# 3. DN02: Navegación Operativa de Sucursal, Punto de Venta (POS), Cobro y Facturación
# ==============================================================================
def make_dn02_operativo_sucursal():
    w, h, cx = 1160, 780, 580
    p = svg_header(w, h, "Diagrama de Navegación 02: Operaciones de Sucursal, Caja POS y Facturación",
                   "Flujo Integral de Mostrador: Venta Presencial POS, Procesamiento de Pago en Caja, Emisión Fiscal e Inventario")
    
    # Raíz común
    p.append(draw_system_root(cx, 75, "<SISTEMA E-COMMERCE AURA>", 270, 34))
    p.append(draw_v_arrow(cx, 109, 135))

    # Login cajero
    p.append(draw_menu_hub(cx, 135, "Pantalla de Inicio de Sesión (/login)", "Autenticación de Cajero o Encargado de Sucursal", 270, 40))
    p.append(draw_v_arrow(cx, 175, 205))

    # Hub Sucursal
    p.append(draw_menu_hub(cx, 205, "Panel Operativo de Sucursal (/admin)", "Layout de Tienda Física y Selección de Caja", 270, 40, bg="#fff7ed", stroke="#ea580c"))

    # DISTRIBUCIÓN LIMPIA:
    # Nivel 1: Flujo POS Mostrador (3 Columnas Superiores: POS -> Pago -> Factura)
    c1, c2, c3 = 230, 580, 930
    y_rombo = 295

    # Conexiones a Módulos POS
    p.append(draw_ortho_step(cx - 100, 245, c1, y_rombo - 46, "Abrir POS"))
    p.append(draw_v_arrow(c2, 245, y_rombo - 46, "Pase a Caja"))
    p.append(draw_ortho_step(cx + 100, 245, c3, y_rombo - 46, "Despacho"))

    # Rombos
    p.append(draw_module_diamond(c1, y_rombo, ["Módulo:", "Punto de Venta", "Presencial (POS)"], color="#dc2626", size=46))
    p.append(draw_module_diamond(c2, y_rombo, ["Módulo:", "Cobro y Arqueo", "de Caja"], color="#16a34a", size=46))
    p.append(draw_module_diamond(c3, y_rombo, ["Módulo:", "Facturación y", "Comprobantes"], color="#0284c7", size=46))

    # --- PASO 1: POS ---
    p.append(draw_v_arrow(c1, y_rombo + 46, 370))
    p.append(draw_page_box(c1, 370, "Terminal POS (/admin/caja)", 195, 34))
    p.append(draw_v_arrow(c1, 404, 425))
    p.append(draw_cu_box(c1, 425, "CU_W24", "Registrar Venta Presencial POS", 195, 34, fill="#fee2e2", stroke="#ef4444", text_color="#991b1b"))

    # Transición POS -> Pago en Caja
    p.append(draw_line(c1 + 98, 387, c2 - 105, 387, "[Venta Asentada: id_venta]", label_x=(c1 + 98 + c2 - 105)/2, label_y=373, text_anchor="middle"))

    # --- PASO 2: Pago en Caja ---
    p.append(draw_v_arrow(c2, y_rombo + 46, 370))
    p.append(draw_page_box(c2, 370, "Pago Caja (/admin/caja/pago/:id)", 210, 34))
    p.append(draw_v_arrow(c2, 404, 425))
    p.append(draw_cu_box(c2, 425, "CU_W28", "Procesar Pago en Caja (Efectivo/QR)", 210, 34, fill="#dcfce7", stroke="#16a34a", text_color="#14532d"))

    # Transición Pago en Caja -> Emisión Comprobante
    p.append(draw_line(c2 + 105, 387, c3 - 112, 387, "[Pago APROBADO]", label_x=(c2 + 105 + c3 - 112)/2, label_y=373, text_anchor="middle"))

    # --- PASO 3: Emisión Comprobante ---
    p.append(draw_v_arrow(c3, y_rombo + 46, 370))
    p.append(draw_page_box(c3, 370, "Comprobante (/admin/caja/comprobante/:id)", 225, 34))
    p.append(draw_v_arrow(c3, 404, 425))
    p.append(draw_cu_box(c3, 425, "CU_W29", "Emitir Comprobante de Venta", 210, 34, fill="#dbeafe", stroke="#0284c7", text_color="#1e40af"))

    # SECTOR INFERIOR: Operaciones de Tienda y Kardex Físico (Enrutado Perimetral Limpio)
    y_inf_rombo = 545
    cx_reserva, cx_kardex = 380, 780

    # Rombos Inferiores
    p.append(draw_module_diamond(cx_reserva, y_inf_rombo, ["Módulo:", "Atención de Reservas", "en Mostrador"], color="#ea580c", size=44))
    p.append(draw_module_diamond(cx_kardex, y_inf_rombo, ["Módulo:", "Kardex y Control", "de Inventario"], color="#7c3aed", size=44))

    # Conexiones desde Panel Operativo rodeando por fuera (sin cruzar cajas superiores)
    # Ruta izquierda a Reservas
    p_res = f"M {cx - 135} 225 L 80 225 L 80 545 L {cx_reserva - 64} 545"
    p.append(f'  <path d="{p_res}" fill="none" stroke="#ea580c" stroke-width="1.2" marker-end="url(#arrow-orange)"/>\n')
    p.append('  <text x="88" y="470" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#ea580c">Atención Reservas</text>\n')

    # Ruta derecha a Kardex
    p_kdx = f"M {cx + 135} 225 L 1080 225 L 1080 545 L {cx_kardex + 64} 545"
    p.append(f'  <path d="{p_kdx}" fill="none" stroke="#7c3aed" stroke-width="1.2" marker-end="url(#arrow)"/>\n')
    p.append('  <text x="1000" y="470" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#7c3aed">Control Kardex</text>\n')

    # Pantalla Reservas
    p.append(draw_v_arrow(cx_reserva, y_inf_rombo + 44, 620))
    p.append(draw_page_box(cx_reserva, 620, "Entrega Reservas (/admin/reservas)", 210, 34))
    p.append(draw_v_arrow(cx_reserva, 654, 675))
    p.append(draw_cu_box(cx_reserva, 675, "CU_W25", "Atender Reservas en Sucursal", 205, 34, fill="#ffedd5", stroke="#ea580c", text_color="#c2410c"))

    # Pantalla Inventario
    p.append(draw_v_arrow(cx_kardex, y_inf_rombo + 44, 620))
    p.append(draw_page_box(cx_kardex, 620, "Inventario Sucursal (/admin/inventario)", 225, 34))
    p.append(draw_v_arrow(cx_kardex, 654, 675))
    p.append(draw_cu_box(cx_kardex, 675, "CU_W22", "Gestionar Inventario de Sucursal", 210, 34, fill="#f3e8ff", stroke="#7c3aed", text_color="#6b21a8"))

    # Conexiones de Negocio Inter-pantallas:
    # 1. Al entregar reserva se procede al cobro en caja
    p.append(draw_line(cx_reserva + 105, 637, c2 - 50, 459, "[Cobrar Prenda Reservada]", label_x=475, label_y=545, dashed=True))
    
    # 2. Al emitir comprobante se asienta salida en Kardex
    p.append(draw_line(c3 - 30, 459, cx_kardex + 100, 620, "[Descuento Kardex Venta]", label_x=860, label_y=530, text_anchor="middle", dashed=True))

    p.append('</svg>\n')
    return "".join(p)


# ==============================================================================
# 4. DN03: Navegación del Panel Administrativo, Catálogo Central y Auditoría
# ==============================================================================
def make_dn03_administracion():
    w, h, cx = 1200, 800, 600
    p = svg_header(w, h, "Diagrama de Navegación 03: Panel Administrativo, Catálogo Central y Auditoría",
                   "Gestión Estratégica: KPIs, Colecciones, Proveedores, Disponibilidad de Prendas, RBAC y Bitácora")
    
    # Raíz común
    p.append(draw_system_root(cx, 75, "<SISTEMA E-COMMERCE AURA>", 270, 34))
    p.append(draw_v_arrow(cx, 109, 135))

    # Login Admin
    p.append(draw_menu_hub(cx, 135, "Pantalla de Inicio de Sesión (/login)", "Autenticación de Administrador de Tienda / Superadmin", 280, 40))
    p.append(draw_v_arrow(cx, 175, 205))

    # Dashboard Principal
    p.append(draw_page_box(cx, 205, "Dashboard Principal KPIs (/admin/kpis)", 260, 36))
    p.append(draw_v_arrow(cx, 241, 260))
    p.append(draw_cu_box(cx, 260, "CU36", "Visualizar Dashboard de Indicadores y KPIs", 250, 34))

    # 4 Módulos en Columnas Paralelas
    c1, c2, c3, c4 = 175, 455, 745, 1025
    y_rombo = 375

    # Ramas desde el Dashboard (bajan a y=322 para dar respiro al texto)
    y_split = 322
    p.append(f'  <line x1="{c1}" y1="{y_split}" x2="{c4}" y2="{y_split}" stroke="#334155" stroke-width="1.2"/>\n')
    p.append(f'  <line x1="{cx}" y1="294" x2="{cx}" y2="{y_split}" stroke="#334155" stroke-width="1.2"/>\n')

    p.append(f'  <line x1="{c1}" y1="{y_split}" x2="{c1}" y2="{y_rombo - 44}" stroke="#334155" stroke-width="1.2" marker-end="url(#arrow)"/>\n')
    p.append(f'  <line x1="{c2}" y1="{y_split}" x2="{c2}" y2="{y_rombo - 44}" stroke="#334155" stroke-width="1.2" marker-end="url(#arrow)"/>\n')
    p.append(f'  <line x1="{c3}" y1="{y_split}" x2="{c3}" y2="{y_rombo - 44}" stroke="#334155" stroke-width="1.2" marker-end="url(#arrow)"/>\n')
    p.append(f'  <line x1="{c4}" y1="{y_split}" x2="{c4}" y2="{y_rombo - 44}" stroke="#334155" stroke-width="1.2" marker-end="url(#arrow)"/>\n')

    p.append(f'  <text x="{c1}" y="{y_split - 5}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#334155" text-anchor="middle">Catálogo</text>\n')
    p.append(f'  <text x="{c2}" y="{y_split - 5}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#334155" text-anchor="middle">Red Tiendas</text>\n')
    p.append(f'  <text x="{c3}" y="{y_split - 5}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#334155" text-anchor="middle">Seguridad</text>\n')
    p.append(f'  <text x="{c4}" y="{y_split - 5}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#334155" text-anchor="middle">Auditoría / BI</text>\n')

    # Rombos
    p.append(draw_module_diamond(c1, y_rombo, ["Módulo:", "Catálogo y", "Colecciones"], color="#0284c7", size=44))
    p.append(draw_module_diamond(c2, y_rombo, ["Módulo:", "Proveedores y", "Sucursales"], color="#ea580c", size=44))
    p.append(draw_module_diamond(c3, y_rombo, ["Módulo:", "Seguridad y", "Roles RBAC"], color="#16a34a", size=44))
    p.append(draw_module_diamond(c4, y_rombo, ["Módulo:", "Auditoría, BI", "y Sistema"], color="#7c3aed", size=44))

    # --- COLUMNA 1: Catálogo y Colecciones ---
    p.append(draw_v_arrow(c1, y_rombo + 44, 445))
    p.append(draw_page_box(c1, 445, "Productos (/admin/productos)", 195, 32))
    p.append(draw_v_arrow(c1, 477, 495))
    p.append(draw_cu_box(c1, 495, "CU_W23", "Gestionar Disponibilidad Prendas", 195, 34, fill="#dbeafe", stroke="#0284c7", text_color="#1e40af"))

    p.append(draw_v_arrow(c1, 529, 555))
    p.append(draw_page_box(c1, 555, "Temporadas (/admin/temporadas)", 195, 32))
    p.append(draw_v_arrow(c1, 587, 605))
    p.append(draw_cu_box(c1, 605, "CU_W20", "Gestionar Temporadas y Colecciones", 195, 34, fill="#dbeafe", stroke="#0284c7", text_color="#1e40af"))

    p.append(draw_v_arrow(c1, 639, 665))
    p.append(draw_page_box(c1, 665, "Categorías (/admin/categorias)", 195, 32))
    p.append(draw_v_arrow(c1, 697, 720))
    p.append(draw_page_box(c1, 720, "Tallas & Colores (/admin/tallas-colores)", 205, 32))

    # --- COLUMNA 2: Proveedores y Red de Tiendas ---
    p.append(draw_v_arrow(c2, y_rombo + 44, 445))
    p.append(draw_page_box(c2, 445, "Proveedores (/admin/proveedores)", 195, 32))
    p.append(draw_v_arrow(c2, 477, 495))
    p.append(draw_cu_box(c2, 495, "CU_W21", "Gestionar Proveedores", 195, 34, fill="#ffedd5", stroke="#ea580c", text_color="#c2410c"))

    p.append(draw_v_arrow(c2, 529, 565))
    p.append(draw_page_box(c2, 565, "Empresas (/admin/empresas)", 195, 32))
    p.append(draw_v_arrow(c2, 597, 625))
    p.append(draw_page_box(c2, 625, "Sucursales (/admin/sucursales)", 195, 32))

    # --- COLUMNA 3: Seguridad y Roles RBAC ---
    p.append(draw_v_arrow(c3, y_rombo + 44, 445))
    p.append(draw_page_box(c3, 445, "Usuarios (/admin/usuarios)", 195, 32))
    p.append(draw_v_arrow(c3, 477, 495))
    p.append(draw_cu_box(c3, 495, "CU01/CU02", "Gestión de Usuarios y Roles", 195, 34, fill="#dcfce7", stroke="#16a34a", text_color="#14532d"))

    p.append(draw_v_arrow(c3, 529, 565))
    p.append(draw_page_box(c3, 565, "Mi Perfil (/perfil)", 195, 32))

    # --- COLUMNA 4: Auditoría, BI y Sistema ---
    p.append(draw_v_arrow(c4, y_rombo + 44, 445))
    p.append(draw_page_box(c4, 445, "Bitácora (/admin/bitacora)", 195, 32))
    p.append(draw_v_arrow(c4, 477, 495))
    p.append(draw_cu_box(c4, 495, "AUDITORÍA", "Bitácora Transaccional y Eventos", 195, 34, fill="#f3e8ff", stroke="#7c3aed", text_color="#6b21a8"))

    p.append(draw_v_arrow(c4, 529, 555))
    p.append(draw_page_box(c4, 555, "BI Dashboard (/admin/bi_dashboard)", 195, 32))

    p.append(draw_v_arrow(c4, 587, 615))
    p.append(draw_page_box(c4, 615, "Respaldo BD (/admin/backup)", 195, 32))

    p.append(draw_v_arrow(c4, 647, 675))
    p.append(draw_page_box(c4, 675, "Triaje IA (/admin/triaje-chat)", 195, 32))

    p.append('</svg>\n')
    return "".join(p)


# ==============================================================================
# Ejecución Principal y Exportación PNG (2x)
# ==============================================================================
def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)

    diagrams = [
        ("DN00_Mapa_General_Navegacion_Sistema_Aura", make_dn00_mapa_general()),
        ("DN01_Navegacion_Cliente_Ecommerce_Checkout", make_dn01_cliente()),
        ("DN02_Navegacion_Operativa_Sucursal_POS_Caja", make_dn02_operativo_sucursal()),
        ("DN03_Navegacion_Administracion_Catalogo_Auditoria", make_dn03_administracion()),
    ]

    print("=== GENERANDO 4 DIAGRAMAS DE NAVEGACIÓN WEB PULIDOS (UAGRM - SI2) ===")
    for name, svg_content in diagrams:
        svg_path = os.path.join(out_dir, f"{name}.svg")
        png_path = os.path.join(out_dir, f"{name}.png")

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2.0)
        print(f"[OK] {name} -> SVG & PNG (2x)")

    print("\n¡Todos los Diagramas de Navegación generados exitosamente!")

if __name__ == "__main__":
    main()
