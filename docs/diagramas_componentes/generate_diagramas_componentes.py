#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de Diagramas de Componentes de Subsistemas UML 2.5
Sistema E-Commerce Multi-Tenant para Venta de Ropa Aura (SI2 - UAGRM)

Produce:
- DC00: Diagrama General de Componentes y Subsistemas (idéntico al formato docente)
- DC01: Subsistema de Autenticación y Gestión de Usuarios
- DC02: Subsistema de Gestión de Catálogo
- DC03: Subsistema de Sucursales, Inventario y Proveedores
- DC04: Subsistema de Gestión de E-Commerce
- DC05: Subsistema de Reservas
- DC06: Subsistema de Punto de Venta (POS)
"""

import os
import sys
import xml.sax.saxutils
import cairosvg

def escape_xml(text):
    return xml.sax.saxutils.escape(str(text))

# ------------------------------------------------------------------------------
# Primitivas Gráficas UML (Estándar Docente)
# ------------------------------------------------------------------------------

def svg_header(w, h, title=""):
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n',
        '  <defs>\n',
        '    <marker id="open-arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">\n',
        '      <path d="M 0 1 L 7 4.5 L 0 8" fill="none" stroke="#000000" stroke-width="1.2"/>\n',
        '    </marker>\n',
        '    <marker id="solid-arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">\n',
        '      <path d="M 0 1 L 7 4 L 0 7 Z" fill="#000000"/>\n',
        '    </marker>\n',
        '  </defs>\n\n',
        f'  <rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>\n\n'
    ]
    if title:
        parts.append(f'  <!-- Título Superior -->\n')
        parts.append(f'  <text x="{w/2}" y="32" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="bold" fill="#000000" text-anchor="middle">{escape_xml(title)}</text>\n\n')
    return parts

def draw_folder(x, y, title_lines, w=145, h=68, is_implemented=True):
    # Pestaña superior izquierda de la carpeta UML
    tab_w = 48
    tab_h = 13
    res = [
        f'  <!-- Carpeta Subsistema: {" ".join(title_lines)} -->\n',
        f'  <g>\n',
        f'    <path d="M {x} {y + tab_h} L {x} {y} L {x + tab_w - 8} {y} L {x + tab_w} {y + tab_h} Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>\n',
        f'    <rect x="{x}" y="{y + tab_h}" width="{w}" height="{h - tab_h}" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>\n'
    ]
    total = len(title_lines)
    mid_y = y + tab_h + (h - tab_h)/2
    start_y = mid_y - (total - 1) * 6.5
    for i, line in enumerate(title_lines):
        ly = start_y + i * 13 + 3.5
        res.append(f'    <text x="{x + w/2}" y="{ly}" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="bold" fill="#000000" text-anchor="middle">{escape_xml(line)}</text>\n')
    res.append(f'  </g>\n')
    return "".join(res)

def draw_component(x, y, stereotype, name, w=140, h=48, fill="#ffffff"):
    # Caja principal con icono de componente UML en esquina superior derecha
    x_ic = x + w - 24
    y_ic = y + 8
    res = [
        f'  <!-- Componente: {name} -->\n',
        f'  <g>\n',
        f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#000000" stroke-width="1.2"/>\n',
        f'    <!-- Icono Componente UML -->\n',
        f'    <rect x="{x_ic}" y="{y_ic}" width="16" height="19" fill="#ffffff" stroke="#000000" stroke-width="1.0"/>\n',
        f'    <rect x="{x_ic - 4}" y="{y_ic + 3}" width="8" height="4" fill="#ffffff" stroke="#000000" stroke-width="1.0"/>\n',
        f'    <rect x="{x_ic - 4}" y="{y_ic + 11}" width="8" height="4" fill="#ffffff" stroke="#000000" stroke-width="1.0"/>\n'
    ]
    # Texto centrado horizontalmente respecto al espacio útil
    text_cx = x + (w - 20) / 2
    if stereotype:
        res.append(f'    <text x="{text_cx}" y="{y + 19}" font-family="Arial, Helvetica, sans-serif" font-size="9.5" fill="#000000" text-anchor="middle">&lt;&lt;{escape_xml(stereotype)}&gt;&gt;</text>\n')
        res.append(f'    <text x="{text_cx}" y="{y + 35}" font-family="Arial, Helvetica, sans-serif" font-size="10.5" font-weight="bold" fill="#000000" text-anchor="middle">{escape_xml(name)}</text>\n')
    else:
        res.append(f'    <text x="{text_cx}" y="{y + h/2 + 4}" font-family="Arial, Helvetica, sans-serif" font-size="10.5" font-weight="bold" fill="#000000" text-anchor="middle">{escape_xml(name)}</text>\n')
    res.append(f'  </g>\n')
    return "".join(res)

def draw_dashed_arrow(x1, y1, x2, y2, label=""):
    res = [f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000000" stroke-width="1.1" stroke-dasharray="4,3" marker-end="url(#open-arrow)"/>\n']
    if label:
        res.append(f'  <text x="{(x1+x2)/2}" y="{(y1+y2)/2 - 4}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#000000" text-anchor="middle">{escape_xml(label)}</text>\n')
    return "".join(res)

def draw_solid_arrow(x1, y1, x2, y2, label=""):
    res = [f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000000" stroke-width="1.1" marker-end="url(#solid-arrow)"/>\n']
    if label:
        res.append(f'  <text x="{(x1+x2)/2}" y="{(y1+y2)/2 - 4}" font-family="Arial, Helvetica, sans-serif" font-size="8.5" fill="#000000" text-anchor="middle">{escape_xml(label)}</text>\n')
    return "".join(res)

# ==============================================================================
# DC00: DIAGRAMA GENERAL DE COMPONENTES Y SUBSISTEMAS
# Idéntico al formato enviado por el docente
# ==============================================================================
def make_dc00_general():
    w, h = 980, 720
    p = svg_header(w, h, "Diagrama General de Componentes y Subsistemas - Sistema Aura")

    # Marco Exterior Principal (Cuadro que delimita los subsistemas ya implementados)
    box_x, box_y, box_w, box_h = 140, 50, 825, 650
    p.append(f'  <!-- Cuadro de Subsistemas Implementados -->\n')
    p.append(f'  <rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" fill="none" stroke="#000000" stroke-width="1.2"/>\n\n')

    # 1. SUBSISTEMAS FUERA DEL CUADRO (Izquierda, No implementados / Futuros)
    p.append(draw_folder(12, 100, ["GESTIÓN DE PEDIDOS", "Y REPORTES"], 118, 68))
    p.append(draw_folder(12, 210, ["INTELIGENCIA", "ARTIFICIAL Y", "EXPERIENCIA DEL", "CLIENTE"], 118, 76))

    # 2. SUBSISTEMAS DENTRO DEL CUADRO (Implementados en la iteración)
    subsistemas = [
        (170, 75, ["AUTENTICACIÓN Y", "GESTIÓN DE", "USUARIOS"]),
        (170, 175, ["GESTIÓN DE", "CATÁLOGO"]),
        (170, 275, ["GESTIÓN", "SUCURSALES,", "INVENTARIO Y", "PROVEEDORES"]),
        (170, 385, ["GESTIÓN DE", "E-COMMERCE"]),
        (170, 495, ["RESERVAS"]),
        (170, 600, ["GESTIÓN DE", "PUNTO DE VENTA (POS)"])
    ]
    for sx, sy, lines in subsistemas:
        p.append(draw_folder(sx, sy, lines, 140, 66))

    # 3. COMPONENTE CENTRAL: run.py
    run_x, run_y = 390, 275
    p.append(draw_component(run_x, run_y, "source", "run.py", 115, 52))

    # Flechas discontinuas desde cada subsistema implementado hacia run.py
    for sx, sy, _ in subsistemas:
        mid_sy = sy + 38
        if sy < 275:
            # Viene de arriba a la derecha
            p.append(f'  <path d="M {sx + 140} {mid_sy} L 370 {mid_sy} L 370 300 L {run_x} 300" fill="none" stroke="#000000" stroke-width="1.1" stroke-dasharray="4,3" marker-end="url(#open-arrow)"/>\n')
        elif sy > 340:
            # Viene de abajo a la derecha
            p.append(f'  <path d="M {sx + 140} {mid_sy} L 370 {mid_sy} L 370 305 L {run_x} 305" fill="none" stroke="#000000" stroke-width="1.1" stroke-dasharray="4,3" marker-end="url(#open-arrow)"/>\n')
        else:
            # Nivel central directo
            p.append(draw_dashed_arrow(sx + 140, mid_sy, run_x, mid_sy))

    # 4. COLUMNA 1 DE LIBRERÍAS (Centro-Derecha, x=600)
    col1_x = 590
    libs_col1 = [
        (col1_x, 70, "library", "FastAPI"),
        (col1_x, 140, "library", "psycopg2"),
        (col1_x, 210, "library", "python-dotenv"),
        (col1_x, 290, "library", "Gunicorn"),
        (col1_x, 370, "library", "Angular"),
        (col1_x, 455, "library", "TailwindCSS"),
    ]
    for lx, ly, st, name in libs_col1:
        p.append(draw_component(lx, ly, st, name, 130, 46))
        # Flecha desde run.py a cada librería de col1
        p.append(f'  <path d="M {run_x + 115} {run_y + 26} L 545 {run_y + 26} L 545 {ly + 23} L {lx} {ly + 23}" fill="none" stroke="#000000" stroke-width="1.1" stroke-dasharray="4,3" marker-end="url(#open-arrow)"/>\n')

    # 5. COLUMNA 2 DE LIBRERÍAS Y APIS (Derecha, x=775)
    col2_x = 775
    libs_col2 = [
        (col2_x, 70, "library", "PyJWT"),
        (col2_x, 140, "library", "ReportLab"),
        (col2_x, 210, "library", "CloudinarySDK"),
        (col2_x, 290, "library", "Requests"),
        (col2_x, 370, "API", "PayPal API"),
        (col2_x, 455, "API", "Cloudinary"),
    ]
    for lx, ly, st, name in libs_col2:
        p.append(draw_component(lx, ly, st, name, 130, 46))
        # Flecha desde run.py hacia col2
        if name != "Cloudinary":  # Cloudinary recibe flecha sólida de CloudinarySDK
            p.append(f'  <path d="M {run_x + 115} {run_y + 26} L 545 {run_y + 26} L 545 60 L 740 60 L 740 {ly + 23} L {lx} {ly + 23}" fill="none" stroke="#000000" stroke-width="1.1" stroke-dasharray="4,3" marker-end="url(#open-arrow)"/>\n')

    # Flecha sólida de CloudinarySDK a Cloudinary API (como en el diagrama del docente)
    p.append(f'  <path d="M {col2_x + 130} 233 L 940 233 L 940 478 L {col2_x + 130} 478" fill="none" stroke="#000000" stroke-width="1.2" marker-end="url(#solid-arrow)"/>\n')

    # 6. CUADRO DE BASE DE DATOS (Abajo Centro-Derecha)
    db_box_x, db_box_y, db_box_w, db_box_h = 500, 535, 235, 145
    p.append(f'  <!-- Cuadro BASE DE DATOS -->\n')
    p.append(f'  <rect x="{db_box_x}" y="{db_box_y}" width="{db_box_w}" height="{db_box_h}" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>\n')
    p.append(f'  <rect x="{db_box_x}" y="{db_box_y - 18}" width="95" height="18" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>\n')
    p.append(f'  <text x="{db_box_x + 47}" y="{db_box_y - 5}" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="bold" fill="#000000" text-anchor="middle">BASE DE DATOS</text>\n')
    p.append(f'  <text x="{db_box_x + db_box_w/2}" y="{db_box_y + 16}" font-family="Arial, Helvetica, sans-serif" font-size="9.5" fill="#000000" text-anchor="middle">SGBD</text>\n')

    # Componentes dentro de la Base de Datos
    p.append(draw_component(db_box_x + 15, db_box_y + 26, "cloud service", "Oracle Cloud / VPS", 145, 42))
    p.append(draw_component(db_box_x + 65, db_box_y + 88, "database PostgreSQL", "comercio", 155, 42))

    # Flecha interna de cloud service a database postgreSQL
    p.append(f'  <path d="M {db_box_x + 85} {db_box_y + 68} L {db_box_x + 85} {db_box_y + 80} L {db_box_x + 140} {db_box_y + 80} L {db_box_x + 140} {db_box_y + 88}" fill="none" stroke="#000000" stroke-width="1.1" stroke-dasharray="3,2" marker-end="url(#open-arrow)"/>\n')

    # Flecha desde run.py a la Base de Datos (entra por x=615 evitando la pestaña del título)
    p.append(f'  <path d="M {run_x + 55} {run_y + 52} L {run_x + 55} 510 L 615 510 L 615 {db_box_y - 1}" fill="none" stroke="#000000" stroke-width="1.1" stroke-dasharray="4,3" marker-end="url(#open-arrow)"/>\n')

    p.append('</svg>\n')
    return "".join(p)


# ==============================================================================
# DC01..DC06: DIAGRAMAS DE COMPONENTES INTERNOS POR SUBSISTEMA
# Muestran la estructura interna de cada subsistema implementado
# ==============================================================================

def make_subsystem_diagram(title, sub_folder_name, components_ui, components_route, components_service, components_repo, tables_db, libs_used):
    w, h = 980, 640
    p = svg_header(w, h, title)

    # Marco de la Carpeta del Subsistema (Grande)
    fx, fy, fw, fh = 40, 55, 900, 560
    tab_w = 285
    p.append(f'  <!-- Contenedor del Subsistema como Paquete -->\n')
    p.append(f'  <path d="M {fx} {fy + 18} L {fx} {fy} L {fx + tab_w - 15} {fy} L {fx + tab_w} {fy + 18} Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>\n')
    p.append(f'  <rect x="{fx}" y="{fy + 18}" width="{fw}" height="{fh - 18}" fill="#fcfcfc" stroke="#000000" stroke-width="1.3"/>\n')
    p.append(f'  <text x="{fx + tab_w/2 - 5}" y="{fy + 13}" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="bold" fill="#000000" text-anchor="middle">{escape_xml(sub_folder_name)}</text>\n\n')

    # 4 Columnas Arquitectónicas Clásicas (Frontend -> Routes -> Services -> Repos)
    c_ui_x = 70
    c_rt_x = 290
    c_sv_x = 510
    c_rp_x = 730

    # Títulos de Capa
    p.append(f'  <text x="{c_ui_x + 85}" y="95" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="bold" fill="#334155" text-anchor="middle">Capa Presentación (UI Angular)</text>\n')
    p.append(f'  <text x="{c_rt_x + 85}" y="95" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="bold" fill="#334155" text-anchor="middle">Controlador / Rutas API</text>\n')
    p.append(f'  <text x="{c_sv_x + 85}" y="95" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="bold" fill="#334155" text-anchor="middle">Lógica de Negocio (Service)</text>\n')
    p.append(f'  <text x="{c_rp_x + 85}" y="95" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="bold" fill="#334155" text-anchor="middle">Acceso a Datos (Repository)</text>\n')

    # Renderizar UI
    y_start = 120
    spacing = 65
    for i, name in enumerate(components_ui):
        cy = y_start + i * spacing
        p.append(draw_component(c_ui_x, cy, "UI Component", name, 175, 46))
        # Flecha a route
        p.append(draw_dashed_arrow(c_ui_x + 175, cy + 23, c_rt_x, cy + 23))

    # Renderizar Routes
    for i, name in enumerate(components_route):
        cy = y_start + i * spacing
        p.append(draw_component(c_rt_x, cy, "router", name, 175, 46))
        # Flecha a service
        p.append(draw_dashed_arrow(c_rt_x + 175, cy + 23, c_sv_x, cy + 23))

    # Renderizar Services
    for i, name in enumerate(components_service):
        cy = y_start + i * spacing
        p.append(draw_component(c_sv_x, cy, "service", name, 175, 46))
        # Flecha a repository
        p.append(draw_dashed_arrow(c_sv_x + 175, cy + 23, c_rp_x, cy + 23))

    # Renderizar Repositories
    for i, name in enumerate(components_repo):
        cy = y_start + i * spacing
        p.append(draw_component(c_rp_x, cy, "repository", name, 175, 46))

    # Sector Inferior: Persistencia Relacional y Librerías del Subsistema
    y_bottom = 440
    # Cuadro de BD / Tablas
    db_w = 480
    p.append(f'  <!-- Cuadro de Tablas en BD -->\n')
    p.append(f'  <rect x="70" y="{y_bottom}" width="{db_w}" height="145" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>\n')
    p.append(f'  <rect x="70" y="{y_bottom - 18}" width="210" height="18" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>\n')
    p.append(f'  <text x="175" y="{y_bottom - 5}" font-family="Arial, Helvetica, sans-serif" font-size="8.8" font-weight="bold" fill="#000000" text-anchor="middle">ESQUEMA POSTGRESQL: COMERCIO</text>\n')

    # Componentes de tablas
    t_x1, t_x2 = 85, 315
    for i, tname in enumerate(tables_db):
        tx = t_x1 if i % 2 == 0 else t_x2
        ty = y_bottom + 15 + (i // 2) * 44
        p.append(draw_component(tx, ty, "database table", tname, 215, 38))

    # Flecha desde repos hacia el cuadro de BD
    p.append(f'  <path d="M {c_rp_x + 85} {y_start + len(components_repo)*spacing - 15} L {c_rp_x + 85} 410 L 310 410 L 310 {y_bottom - 1}" fill="none" stroke="#000000" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#open-arrow)"/>\n')

    # Cuadro de Librerías y APIs del Subsistema
    lib_box_x = 580
    lib_box_w = 330
    p.append(f'  <!-- Cuadro de Librerías y Dependencias -->\n')
    p.append(f'  <rect x="{lib_box_x}" y="{y_bottom}" width="{lib_box_w}" height="145" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>\n')
    p.append(f'  <rect x="{lib_box_x}" y="{y_bottom - 18}" width="150" height="18" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>\n')
    p.append(f'  <text x="{lib_box_x + 75}" y="{y_bottom - 5}" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="bold" fill="#000000" text-anchor="middle">DEPENDENCIAS &amp; APIS</text>\n')

    for i, (st, name) in enumerate(libs_used):
        lx = lib_box_x + 15 + (i % 2) * 150
        ly = y_bottom + 15 + (i // 2) * 44
        p.append(draw_component(lx, ly, st, name, 140, 38))

    p.append('</svg>\n')
    return "".join(p)


def make_dc01():
    return make_subsystem_diagram(
        title="Diagrama de Componentes: Subsistema Autenticación y Gestión de Usuarios",
        sub_folder_name="AUTENTICACIÓN Y GESTIÓN DE USUARIOS",
        components_ui=["login.component", "lista-usuarios.component", "perfil.component", "roles-rbac.component"],
        components_route=["auth_routes.py", "users_routes.py", "profile_routes.py", "rbac_routes.py"],
        components_service=["auth_services.py", "users_services.py", "profile_services.py", "rbac_services.py"],
        components_repo=["auth_repos.py", "users_repos.py", "profile_repos.py", "rbac_repos.py"],
        tables_db=["comercio.t_usuario", "comercio.t_rol", "comercio.t_permiso", "comercio.t_rol_permiso", "comercio.t_sesion", "comercio.t_empresa"],
        libs_used=[("library", "PyJWT"), ("library", "werkzeug"), ("library", "email-validator"), ("library", "FastAPI")]
    )

def make_dc02():
    return make_subsystem_diagram(
        title="Diagrama de Componentes: Subsistema de Gestión de Catálogo",
        sub_folder_name="GESTIÓN DE CATÁLOGO",
        components_ui=["productos.component", "tallas-colores.component", "categorias.component", "media-upload.component"],
        components_route=["productos_routes.py", "tallas_colores_routes.py", "categorias_routes.py", "media_routes.py"],
        components_service=["productos_services.py", "tallas_colores_services.py", "categorias_services.py", "media_services.py"],
        components_repo=["productos_repos.py", "tallas_colores_repos.py", "categorias_repos.py", "media_repos.py"],
        tables_db=["comercio.t_producto", "comercio.t_variante", "comercio.t_categoria", "comercio.t_talla", "comercio.t_color", "comercio.t_producto_imagen"],
        libs_used=[("library", "CloudinarySDK"), ("API", "Cloudinary CDN"), ("library", "python-multipart"), ("library", "psycopg2")]
    )

def make_dc03():
    return make_subsystem_diagram(
        title="Diagrama de Componentes: Subsistema Sucursales, Inventario y Proveedores",
        sub_folder_name="GESTIÓN SUCURSALES, INVENTARIO Y PROVEEDORES",
        components_ui=["lista-sucursales.component", "lista-inventario.component", "empresas.component", "proveedores.component"],
        components_route=["sucursales_routes.py", "inventario_routes.py", "tenant_routes.py", "ciudades_routes.py"],
        components_service=["sucursales_services.py", "inventario_services.py", "tenant_services.py", "ciudades_services.py"],
        components_repo=["sucursales_repos.py", "inventario_repos.py", "tenant_repos.py", "ciudades_repos.py"],
        tables_db=["comercio.t_sucursal", "comercio.t_inventario", "comercio.t_kardex_movimiento", "comercio.t_empresa", "comercio.t_proveedor", "comercio.t_ciudad"],
        libs_used=[("library", "Leaflet JS"), ("API", "OpenStreetMap"), ("library", "pandas"), ("library", "psycopg2")]
    )

def make_dc04():
    return make_subsystem_diagram(
        title="Diagrama de Componentes: Subsistema de Gestión de E-Commerce",
        sub_folder_name="GESTIÓN DE E-COMMERCE",
        components_ui=["catalogo.component", "carrito-drawer.component", "checkout.component", "pago.component"],
        components_route=["catalogo_routes.py", "carrito_routes.py", "pedido_routes.py", "pago_routes.py"],
        components_service=["catalogo_services.py", "carrito_services.py", "pedido_services.py", "pago_services.py"],
        components_repo=["catalogo_repos.py", "carrito_repos.py", "pedido_repos.py", "pago_repos.py"],
        tables_db=["comercio.t_carrito", "comercio.t_carrito_item", "comercio.t_venta", "comercio.t_detalle_venta", "comercio.t_pago", "comercio.t_metodo_pago"],
        libs_used=[("API", "PayPal Sandbox"), ("library", "Requests"), ("library", "Angular SSR"), ("library", "TailwindCSS")]
    )

def make_dc05():
    return make_subsystem_diagram(
        title="Diagrama de Componentes: Subsistema de Reservas",
        sub_folder_name="RESERVAS",
        components_ui=["mis-reservas.component", "atencion-reservas.component", "stock-sucursales.modal", "confirmacion-reserva.component"],
        components_route=["reserva_routes.py", "sucursales_routes.py", "catalogo_routes.py", "bitacora_routes.py"],
        components_service=["reserva_services.py", "sucursales_services.py", "catalogo_services.py", "bitacora_services.py"],
        components_repo=["reserva_repos.py", "sucursales_repos.py", "catalogo_repos.py", "bitacora_repos.py"],
        tables_db=["comercio.t_reserva", "comercio.t_reserva_detalle", "comercio.t_inventario", "comercio.t_sucursal", "comercio.t_usuario", "comercio.t_bitacora"],
        libs_used=[("library", "FastAPI"), ("library", "psycopg2"), ("library", "RxJS"), ("library", "python-dotenv")]
    )

def make_dc06():
    return make_subsystem_diagram(
        title="Diagrama de Componentes: Subsistema de Punto de Venta (POS)",
        sub_folder_name="GESTIÓN DE PUNTO DE VENTA (POS)",
        components_ui=["caja-pos.component", "caja-pago.component", "caja-comprobante.component", "sesion-caja.component"],
        components_route=["pos_routes.py", "caja_pago_routes.py", "comprobante_routes.py", "caja_routes.py"],
        components_service=["pos_services.py", "caja_pago_services.py", "comprobante_service.py", "caja_services.py"],
        components_repo=["pos_repos.py", "caja_pago_repos.py", "comprobante_repos.py", "caja_repos.py"],
        tables_db=["comercio.t_caja_sesion", "comercio.t_venta", "comercio.t_detalle_venta", "comercio.t_pago", "comercio.t_comprobante", "comercio.t_kardex_movimiento"],
        libs_used=[("library", "ReportLab PDF"), ("library", "python-multipart"), ("library", "FastAPI"), ("library", "TailwindCSS")]
    )


# ==============================================================================
# Ejecución Principal y Renderizado 2x
# ==============================================================================
def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)

    diagrams = [
        ("DC00_Diagrama_General_Componentes_Subsistemas", make_dc00_general()),
        ("DC01_Subsistema_Autenticacion_Usuarios", make_dc01()),
        ("DC02_Subsistema_Gestion_Catalogo", make_dc02()),
        ("DC03_Subsistema_Sucursales_Inventario_Proveedores", make_dc03()),
        ("DC04_Subsistema_Gestion_Ecommerce", make_dc04()),
        ("DC05_Subsistema_Reservas", make_dc05()),
        ("DC06_Subsistema_Punto_De_Venta_POS", make_dc06()),
    ]

    print("=== GENERANDO DIAGRAMAS DE COMPONENTES DE SUBSISTEMAS UML 2.5 ===")
    for name, svg_content in diagrams:
        svg_path = os.path.join(out_dir, f"{name}.svg")
        png_path = os.path.join(out_dir, f"{name}.png")

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2.0)
        print(f"[OK] {name} -> SVG & PNG (2x)")

    print("\n¡Todos los Diagramas de Componentes generados exitosamente!")

if __name__ == "__main__":
    main()
