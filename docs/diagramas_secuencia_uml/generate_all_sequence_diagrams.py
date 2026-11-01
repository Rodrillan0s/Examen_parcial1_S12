#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro Completo de los 9 Diagramas de Secuencia UML 2.5+ (BCE):
CU01W a CU09W.
Cumple estrictamente con:
- Mensajes directos sin codigos HTTP (sin 'error 400' ni status codes).
- Estilo visual limpio y profesional fiel al patron de UML 2.5+ BCE (Actor -> Interfaz -> Control -> Entidades).
- Tablas reales del backend representadas individualmente con operaciones SQL explicitas.
- Halo blanco protector en textos para legibilidad absoluta sobre lineas de vida.
- Generacion dual automatica: SVG editable + PNG de alta resolucion (retina 2x).
"""

import os
import resvg_py

OUTPUT_DIR = os.path.join("docs", "diagramas_secuencia_uml")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# Helpers de Renderizado SVG
# ------------------------------------------------------------------------------
def get_header(width, height, title):
    tab_w = max(420, min(width - 80, len(title) * 9 + 40))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow-sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000" />
    </marker>
    <marker id="arrow-return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <polyline points="0,1 10,5 0,9" fill="none" stroke="#000000" stroke-width="1.6" />
    </marker>
    <marker id="arrow-error" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <polyline points="0,1 10,5 0,9" fill="none" stroke="#b91c1c" stroke-width="1.6" />
    </marker>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="1" dy="1.5" stdDeviation="1.5" flood-color="#000000" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Marco exterior UML 2.5 -->
  <rect x="20" y="20" width="{width - 40}" height="{height - 40}" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
  <!-- Pestana de titulo UML con esquina achaflanada -->
  <path d="M 20 20 L {tab_w} 20 L {tab_w + 18} 38 L {tab_w + 18} 56 L 20 56 Z" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
  <text x="35" y="42" font-size="13.5" font-weight="bold" fill="#0f172a">{title}</text>
"""

def draw_actor(x, l1, l2, y_end):
    sub = f"<text x='0' y='114' text-anchor='middle' font-size='11' font-weight='bold' fill='#0f172a' paint-order='stroke fill' stroke='#ffffff' stroke-width='4px'>{l2}</text>" if l2 else ""
    return f"""
  <!-- Actor -->
  <g transform="translate({x}, 65)">
    <circle cx="0" cy="14" r="12" fill="#ffffff" stroke="#000000" stroke-width="1.8" />
    <line x1="0" y1="26" x2="0" y2="52" stroke="#000000" stroke-width="1.8" />
    <line x1="-22" y1="36" x2="22" y2="36" stroke="#000000" stroke-width="1.8" />
    <line x1="0" y1="52" x2="-18" y2="78" stroke="#000000" stroke-width="1.8" />
    <line x1="0" y1="52" x2="18" y2="78" stroke="#000000" stroke-width="1.8" />
    <text x="0" y="98" text-anchor='middle' font-size='11' font-weight='bold' fill='#0f172a' paint-order='stroke fill' stroke='#ffffff' stroke-width='4px'>{l1}</text>
    {sub}
  </g>
  <line x1="{x}" y1="195" x2="{x}" y2="{y_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x - 4},{y_end - 2} {x},{y_end + 8} {x + 4},{y_end - 2}" fill="#000000" />
"""

def draw_box(x, w, stereotype, name, y_end):
    return f"""
  <!-- Participante: {name} -->
  <g filter="url(#shadow)">
    <rect x="{x - w//2}" y="135" width="{w}" height="56" rx="2" fill="#ffffff" stroke="#000000" stroke-width="1.5" />
    <text x="{x}" y="157" text-anchor="middle" font-size="11" fill="#475569">&#171;{stereotype}&#187;</text>
    <text x="{x}" y="176" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">{name}</text>
  </g>
  <line x1="{x}" y1="191" x2="{x}" y2="{y_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x - 4},{y_end - 2} {x},{y_end + 8} {x + 4},{y_end - 2}" fill="#000000" />
"""

def draw_act(x, y, h):
    return f'  <rect x="{x - 6}" y="{y}" width="12" height="{h}" fill="#f8fafc" stroke="#334155" stroke-width="1.2" />\n'

def draw_sync(x1, x2, y, msg, color="#0f172a"):
    mx = (x1 + x2) / 2
    return f"""  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#000000" stroke-width="1.5" marker-end="url(#arrow-sync)" />
  <text x="{mx}" y="{y - 8}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{color}" paint-order="stroke fill" stroke="#ffffff" stroke-width="4.5px" stroke-linecap="round" stroke-linejoin="round">{msg}</text>
"""

def draw_ret(x1, x2, y, msg, color="#334155", italic=True):
    mx = (x1 + x2) / 2
    st = ' font-style="italic"' if italic else ' font-weight="600"'
    return f"""  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#000000" stroke-width="1.4" stroke-dasharray="6,4" marker-end="url(#arrow-return)" />
  <text x="{mx}" y="{y - 8}" text-anchor="middle" font-size="10.5"{st} fill="{color}" paint-order="stroke fill" stroke="#ffffff" stroke-width="4.5px" stroke-linecap="round" stroke-linejoin="round">{msg}</text>
"""

def draw_err(x1, x2, y, msg):
    mx = (x1 + x2) / 2
    return f"""  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#b91c1c" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-error)" />
  <text x="{mx}" y="{y - 8}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#b91c1c" paint-order="stroke fill" stroke="#ffffff" stroke-width="4.5px" stroke-linecap="round" stroke-linejoin="round">{msg}</text>
"""

def draw_self(x, y, dy, msg):
    return f"""  <path d="M {x + 6} {y} L {x + 32} {y} L {x + 32} {y + dy} L {x + 6} {y + dy}" fill="none" stroke="#000000" stroke-width="1.4" marker-end="url(#arrow-sync)" />
  <text x="{x + 38}" y="{y + dy/2 + 4}" font-size="10.5" font-weight="600" fill="#0f172a" paint-order="stroke fill" stroke="#ffffff" stroke-width="4px">{msg}</text>
"""

def draw_alt(x, y, w, h, guard_err, divider_y, guard_ok):
    return f"""  <!-- Fragmento alt -->
  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#334155" stroke-width="1.3" />
  <path d="M {x} {y} L {x + 80} {y} L {x + 92} {y + 13} L {x + 92} {y + 24} L {x} {y + 24} Z" fill="#f8fafc" stroke="#334155" stroke-width="1.3" />
  <text x="{x + 10}" y="{y + 17}" font-size="11" font-weight="bold" fill="#1e293b">alt</text>
  <text x="{x + 102}" y="{y + 17}" font-size="11" font-weight="bold" fill="#b91c1c">{guard_err}</text>

  <!-- Divisor alt else -->
  <line x1="{x}" y1="{divider_y}" x2="{x + w}" y2="{divider_y}" stroke="#334155" stroke-width="1.3" stroke-dasharray="7,4" />
  <text x="{x + 12}" y="{divider_y - 8}" font-size="10" font-weight="bold" fill="#475569">[else]</text>
  <text x="{x + 55}" y="{divider_y + 18}" font-size="11" font-weight="bold" fill="#15803d">{guard_ok}</text>
"""

def draw_opt_loop(x, y, w, h, guard, op_type="opt"):
    tab_w = max(50, len(op_type) * 9 + 14)
    return f"""  <!-- Fragmento {op_type} -->
  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#475569" stroke-width="1.2" stroke-dasharray="5,3" />
  <path d="M {x} {y} L {x + tab_w} {y} L {x + tab_w + 10} {y + 12} L {x + tab_w + 10} {y + 22} L {x} {y + 22} Z" fill="#f1f5f9" stroke="#475569" stroke-width="1.2" />
  <text x="{x + 8}" y="{y + 16}" font-size="10.5" font-weight="bold" fill="#1e293b">{op_type}</text>
  <text x="{x + tab_w + 16}" y="{y + 16}" font-size="10.5" font-weight="600" fill="#334155">{guard}</text>
"""

def render_dual(name, svg_content):
    svg_path = os.path.join(OUTPUT_DIR, f"{name}.svg")
    png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    # Render PNG 2x retina
    png_bytes = resvg_py.svg_to_bytes(svg_content, zoom=2.0)
    with open(png_path, "wb") as f:
        f.write(png_bytes)
    print(f" [OK] {name}: SVG={os.path.getsize(svg_path)}b, PNG={len(png_bytes)}b")


# ==============================================================================
# CU01W: Gestionar usuarios y roles
# ==============================================================================
def gen_cu01w():
    w, h = 1960, 1140
    y_end = 1085
    xa = 110
    xi = 290
    xc = 500
    xr = 730
    xu = 960
    xur = 1190
    xup = 1430
    xus = 1680
    xb = 1880
    
    s = get_header(w, h, "sd [CU01W] Gestionar usuarios y roles (UML 2.5+ / BCE)")
    s += draw_actor(xa, "Administrador /", "Administrador de Tienda", y_end)
    s += draw_box(xi, 130, "boundary", "IU_Usuario", y_end)
    s += draw_box(xc, 150, "control", "UsuarioControl", y_end)
    s += draw_box(xr, 120, "entity", ":t_rol", y_end)
    s += draw_box(xu, 120, "entity", ":t_usuario", y_end)
    s += draw_box(xur, 130, "entity", ":t_usuario_rol", y_end)
    s += draw_box(xup, 150, "entity", ":t_usuario_permiso", y_end)
    s += draw_box(xus, 150, "entity", ":t_usuario_sucursal", y_end)
    s += draw_box(xb, 120, "entity", ":t_bitacora", y_end)
    
    # Activaciones
    s += draw_act(xi, 222, 825)
    s += draw_act(xc, 254, 735)
    s += draw_act(xr, 318, 38)
    s += draw_act(xu, 378, 38)
    s += draw_act(xu, 608, 38)
    s += draw_act(xur, 668, 38)
    s += draw_act(xup, 750, 32)
    s += draw_act(xus, 834, 32)
    s += draw_act(xb, 892, 38)
    
    # Flujo de mensajes
    s += draw_sync(xa, xi - 6, 228, "1: solicitar_registro(datos_usuario)")
    s += draw_sync(xi + 6, xc - 6, 260, "2: registrar_usuario(datos_usuario)")
    s += draw_self(xc, 276, 20, "3: validar_campos_requeridos(datos)")
    s += draw_sync(xc + 6, xr - 6, 322, "4: SELECT nivel, permisos FROM t_rol WHERE id_rol = :id_rol")
    s += draw_ret(xr - 6, xc + 6, 352, "5: return datos_rol (nivel, permisos)")
    s += draw_sync(xc + 6, xu - 6, 382, "6: SELECT id_usuario FROM t_usuario WHERE username = :username")
    s += draw_ret(xu - 6, xc + 6, 412, "7: return usuario_existente")
    
    s += draw_alt(35, 432, w - 70, 625,
                  "[usuario_existente != null || jerarquia_invalida] (Curso Alterno: Rechazo por Duplicidad o Jerarquia)",
                  535,
                  "[else: usuario_existente == null &amp;&amp; jerarquia_valida] (Curso Basico: Creacion y Persistencia)")
    
    s += draw_err(xc - 6, xi + 6, 476, "8.1: (Error, \"Nombre de usuario ya existente\")")
    s += draw_err(xi - 6, xa, 506, "8.2: Mostrar error: \"Nombre de usuario ya existente\"")
    
    s += draw_self(xc, 568, 20, "9: hashear_password(password)")
    s += draw_sync(xc + 6, xu - 6, 612, "10: INSERT INTO t_usuario(username, correo, password_hash, id_empresa, estado)")
    s += draw_ret(xu - 6, xc + 6, 642, "11: return id_usuario")
    s += draw_sync(xc + 6, xur - 6, 672, "12: INSERT INTO t_usuario_rol(id_usuario, id_rol)")
    s += draw_ret(xur - 6, xc + 6, 702, "13: return confirmacion_rol")
    
    # loop permisos opcionales
    s += draw_opt_loop(470, 722, xup - 450, 70, "[para cada id_permiso: permisos directos != null]", "loop")
    s += draw_sync(xc + 6, xup - 6, 762, "14: INSERT INTO t_usuario_permiso(id_usuario, id_permiso, activo)")
    s += draw_ret(xup - 6, xc + 6, 778, "15: return confirmacion_permiso")
    
    # loop sucursales asignadas
    s += draw_opt_loop(470, 804, xus - 450, 70, "[para cada id_sucursal: sucursales asignadas != null]", "loop")
    s += draw_sync(xc + 6, xus - 6, 844, "16: INSERT INTO t_usuario_sucursal(id_usuario, id_sucursal)")
    s += draw_ret(xus - 6, xc + 6, 860, "17: return confirmacion_sucursal")
    
    s += draw_sync(xc + 6, xb - 6, 896, "18: INSERT INTO t_bitacora(id_usuario, id_empresa, modulo='USUARIOS', accion='USUARIO_CREADO', ...)")
    s += draw_ret(xb - 6, xc + 6, 924, "19: return confirmacion_log")
    s += draw_ret(xc - 6, xi + 6, 970, "20: confirmar_registro(id_usuario)", color="#15803d", italic=False)
    s += draw_ret(xi - 6, xa, 1010, "21: actualizar_usuarios()", italic=False)
    
    s += "</svg>"
    render_dual("CU01W_Gestionar_Usuarios_Roles_Secuencia", s)


# ==============================================================================
# CU02W: Gestionar empresas SaaS
# ==============================================================================
def gen_cu02w():
    w, h = 1860, 960
    y_end = 905
    xa = 130
    xi = 380
    xc = 680
    xe = 990
    xp = 1260
    xs = 1510
    xb = 1730
    
    s = get_header(w, h, "sd [CU02W] Gestionar empresas SaaS (UML 2.5+ / BCE)")
    s += draw_actor(xa, "Administrador", "(SuperAdmin)", y_end)
    s += draw_box(xi, 130, "boundary", "IU_Empresa", y_end)
    s += draw_box(xc, 150, "control", "EmpresaControl", y_end)
    s += draw_box(xe, 120, "entity", ":empresa", y_end)
    s += draw_box(xp, 120, "entity", ":t_plan", y_end)
    s += draw_box(xs, 130, "entity", ":t_suscripcion", y_end)
    s += draw_box(xb, 120, "entity", ":t_bitacora", y_end)
    
    s += draw_act(xi, 222, 650)
    s += draw_act(xc, 254, 595)
    s += draw_act(xe, 318, 38)
    s += draw_act(xe, 508, 38)
    s += draw_act(xp, 572, 38)
    s += draw_act(xs, 638, 38)
    s += draw_act(xb, 702, 38)
    
    s += draw_sync(xa, xi - 6, 228, "1: solicitar_registro_tenant(datos_empresa)")
    s += draw_sync(xi + 6, xc - 6, 260, "2: registrar_tenant(datos_empresa)")
    s += draw_self(xc, 276, 20, "3: validar_datos_fiscales(datos)")
    s += draw_sync(xc + 6, xe - 6, 322, "4: SELECT 1 FROM empresa WHERE LOWER(nit) = LOWER(:nit)")
    s += draw_ret(xe - 6, xc + 6, 352, "5: return nit_existente")
    
    s += draw_alt(35, 375, w - 70, 480,
                  "[nit_existente == true] (Curso Alterno: Rechazo por NIT Duplicado)",
                  475,
                  "[else: nit_valido &amp;&amp; no_duplicado] (Curso Basico: Creacion de Tenant y Plan Inicial)")
    
    s += draw_err(xc - 6, xi + 6, 415, "6.1: (Error, \"NIT fiscal ya registrado\")")
    s += draw_err(xi - 6, xa, 445, "6.2: Mostrar error: \"Empresa ya registrada con ese NIT\"")
    
    s += draw_sync(xc + 6, xe - 6, 512, "7: INSERT INTO empresa(nombre_empresa, razon_social, nit, correo, estado='ACTIVO')")
    s += draw_ret(xe - 6, xc + 6, 542, "8: return id_empresa")
    s += draw_sync(xc + 6, xp - 6, 576, "9: SELECT codigo, max_sucursales FROM t_plan WHERE codigo = 'BASICO' AND activo = true")
    s += draw_ret(xp - 6, xc + 6, 606, "10: return plan_base")
    s += draw_sync(xc + 6, xs - 6, 642, "11: INSERT INTO t_suscripcion(id_empresa, codigo_plan, estado='ACTIVA', inicio, fin, motivo)")
    s += draw_ret(xs - 6, xc + 6, 672, "12: return id_suscripcion")
    s += draw_sync(xc + 6, xb - 6, 706, "13: INSERT INTO t_bitacora(id_usuario, id_empresa, modulo='EMPRESAS', accion='REGISTRAR_TENANT', ...)")
    s += draw_ret(xb - 6, xc + 6, 736, "14: return confirmacion_log")
    s += draw_ret(xc - 6, xi + 6, 790, "15: confirmar_registro(id_empresa)", color="#15803d", italic=False)
    s += draw_ret(xi - 6, xa, 825, "16: actualizar_empresas()", italic=False)
    
    s += "</svg>"
    render_dual("CU02W_Gestionar_Empresas_SaaS_Secuencia", s)


# ==============================================================================
# CU03W: Gestionar sucursales y ciudades
# ==============================================================================
def gen_cu03w():
    w, h = 1980, 1060
    y_end = 1005
    xa = 130
    xi = 370
    xc = 640
    xs = 920
    xp = 1170
    xsc = 1420
    xcd = 1660
    xb = 1880
    
    s = get_header(w, h, "sd [CU03W] Gestionar sucursales y ciudades (UML 2.5+ / BCE)")
    s += draw_actor(xa, "Administrador /", "Administrador de Tienda", y_end)
    s += draw_box(xi, 140, "boundary", "IU_SucursalCiudad", y_end)
    s += draw_box(xc, 150, "control", "SucursalControl", y_end)
    s += draw_box(xs, 130, "entity", ":t_suscripcion", y_end)
    s += draw_box(xp, 120, "entity", ":t_plan", y_end)
    s += draw_box(xsc, 130, "entity", ":t_sucursal", y_end)
    s += draw_box(xcd, 120, "entity", ":t_ciudad", y_end)
    s += draw_box(xb, 120, "entity", ":t_bitacora", y_end)
    
    s += draw_act(xi, 222, 750)
    s += draw_act(xc, 254, 695)
    s += draw_act(xs, 318, 38)
    s += draw_act(xp, 378, 38)
    s += draw_act(xsc, 438, 38)
    s += draw_act(xcd, 650, 35)
    s += draw_act(xsc, 730, 38)
    s += draw_act(xb, 796, 38)
    
    s += draw_sync(xa, xi - 6, 228, "1: solicitar_registro_sucursal(datos_sucursal)")
    s += draw_sync(xi + 6, xc - 6, 260, "2: registrar_sucursal(datos_sucursal)")
    s += draw_self(xc, 276, 20, "3: resolver_tenant_operacion(payload, id_empresa)")
    s += draw_sync(xc + 6, xs - 6, 322, "4: SELECT codigo_plan FROM t_suscripcion WHERE id_empresa = :id AND estado='ACTIVA'")
    s += draw_ret(xs - 6, xc + 6, 352, "5: return codigo_plan")
    s += draw_sync(xc + 6, xp - 6, 382, "6: SELECT max_sucursales FROM t_plan WHERE codigo = :codigo")
    s += draw_ret(xp - 6, xc + 6, 412, "7: return max_sucursales")
    s += draw_sync(xc + 6, xsc - 6, 442, "8: SELECT COUNT(*) FROM t_sucursal WHERE id_empresa = :id AND activo = true")
    s += draw_ret(xsc - 6, xc + 6, 472, "9: return conteo_sucursales_activas")
    
    s += draw_alt(35, 495, w - 70, 480,
                  "[conteo_sucursales_activas &gt;= max_sucursales] (Curso Alterno: Limite de Plan Excedido)",
                  595,
                  "[else: conteo_sucursales_activas &lt; max_sucursales] (Curso Basico: Registro Permitido)")
    
    s += draw_err(xc - 6, xi + 6, 535, "10.1: (Error, \"Limite de sucursales alcanzado para el plan\")")
    s += draw_err(xi - 6, xa, 565, "10.2: Mostrar error: \"Limite de sucursales alcanzado (actualice su plan)\"")
    
    # opt ciudad nueva
    s += draw_opt_loop(470, 620, xcd - 450, 75, "[si ciudad no registrada previamente]", "opt")
    s += draw_sync(xc + 6, xcd - 6, 656, "11: INSERT INTO t_ciudad(nombre, codigo_pais) RETURNING id_ciudad")
    s += draw_ret(xcd - 6, xc + 6, 676, "12: return id_ciudad_nueva")
    
    s += draw_sync(xc + 6, xsc - 6, 735, "13: INSERT INTO t_sucursal(nombre_sucursal, direccion, telefono, id_ciudad, id_empresa, activo)")
    s += draw_ret(xsc - 6, xc + 6, 765, "14: return id_sucursal")
    s += draw_sync(xc + 6, xb - 6, 800, "15: INSERT INTO t_bitacora(id_usuario, id_empresa, modulo='SUCURSALES', accion='CREAR_SUCURSAL', ...)")
    s += draw_ret(xb - 6, xc + 6, 830, "16: return confirmacion_log")
    s += draw_ret(xc - 6, xi + 6, 880, "17: confirmar_registro(id_sucursal)", color="#15803d", italic=False)
    s += draw_ret(xi - 6, xa, 915, "18: actualizar_sucursales()", italic=False)
    
    s += "</svg>"
    render_dual("CU03W_Gestionar_Sucursales_Ciudades_Secuencia", s)


# ==============================================================================
# CU04W: Gestionar productos
# ==============================================================================
def gen_cu04w():
    w, h = 1980, 1060
    y_end = 1005
    xa = 130
    xi = 380
    xc = 660
    xcat = 940
    xpr = 1200
    xvar = 1460
    ximg = 1690
    xb = 1890
    
    s = get_header(w, h, "sd [CU04W] Gestionar productos (UML 2.5+ / BCE)")
    s += draw_actor(xa, "Administrador de Empresa /", "Encargado de Sucursal", y_end)
    s += draw_box(xi, 130, "boundary", "IU_Producto", y_end)
    s += draw_box(xc, 150, "control", "ProductoControl", y_end)
    s += draw_box(xcat, 130, "entity", ":t_categoria", y_end)
    s += draw_box(xpr, 130, "entity", ":t_producto", y_end)
    s += draw_box(xvar, 150, "entity", ":t_variante_producto", y_end)
    s += draw_box(ximg, 140, "entity", ":t_imagen_producto", y_end)
    s += draw_box(xb, 120, "entity", ":t_bitacora", y_end)
    
    s += draw_act(xi, 222, 750)
    s += draw_act(xc, 254, 695)
    s += draw_act(xcat, 288, 38)
    s += draw_act(xpr, 348, 38)
    s += draw_act(xpr, 538, 38)
    s += draw_act(xvar, 630, 32)
    s += draw_act(ximg, 730, 32)
    s += draw_act(xb, 796, 38)
    
    s += draw_sync(xa, xi - 6, 228, "1: solicitar_creacion_producto(datos_producto)")
    s += draw_sync(xi + 6, xc - 6, 260, "2: crear_producto(datos_producto)")
    s += draw_sync(xc + 6, xcat - 6, 292, "3: SELECT activo, id_empresa FROM t_categoria WHERE id_categoria = :id")
    s += draw_ret(xcat - 6, xc + 6, 322, "4: return categoria_datos")
    s += draw_sync(xc + 6, xpr - 6, 352, "5: SELECT 1 FROM t_producto WHERE nombre = :nombre AND id_empresa = :id_empresa")
    s += draw_ret(xpr - 6, xc + 6, 382, "6: return nombre_duplicado")
    
    s += draw_alt(35, 405, w - 70, 565,
                  "[nombre_duplicado == true || !categoria_datos.activo] (Curso Alterno: Producto Duplicado o Categoria Invalida)",
                  505,
                  "[else: datos_validos &amp;&amp; nombre_unico] (Curso Basico: Insercion y Variantes)")
    
    s += draw_err(xc - 6, xi + 6, 445, "7.1: (Error, \"Nombre de producto ya existente o categoria invalida\")")
    s += draw_err(xi - 6, xa, 475, "7.2: Mostrar error: \"Nombre de producto ya existente o categoria inactiva\"")
    
    s += draw_sync(xc + 6, xpr - 6, 542, "8: INSERT INTO t_producto(nombre, precio, descripcion, id_categoria, id_empresa, activo, temporada)")
    s += draw_ret(xpr - 6, xc + 6, 572, "9: return id_producto")
    
    # loop variantes
    s += draw_opt_loop(470, 600, xvar - 450, 75, "[para cada variante: tallas y colores definidos]", "loop")
    s += draw_sync(xc + 6, xvar - 6, 636, "10: INSERT INTO t_variante_producto(id_producto, sku, talla, color, codigo_hex)")
    s += draw_ret(xvar - 6, xc + 6, 656, "11: return id_variante")
    
    # loop imagenes
    s += draw_opt_loop(470, 695, ximg - 450, 75, "[para cada imagen: archivos adjuntos != null]", "loop")
    s += draw_sync(xc + 6, ximg - 6, 735, "12: INSERT INTO t_imagen_producto(id_producto, url_imagen, orden, es_portada)")
    s += draw_ret(ximg - 6, xc + 6, 755, "13: return confirmacion_imagen")
    
    s += draw_sync(xc + 6, xb - 6, 800, "14: INSERT INTO t_bitacora(id_usuario, id_empresa, modulo='CATALOGO', accion='PRODUCTO_CREADO', ...)")
    s += draw_ret(xb - 6, xc + 6, 830, "15: return confirmacion_log")
    s += draw_ret(xc - 6, xi + 6, 885, "16: confirmar_creacion(id_producto)", color="#15803d", italic=False)
    s += draw_ret(xi - 6, xa, 920, "17: actualizar_catalogo()", italic=False)
    
    s += "</svg>"
    render_dual("CU04W_Gestionar_Productos_Secuencia", s)


# ==============================================================================
# CU05W: Gestionar planes de suscripcion
# ==============================================================================
def gen_cu05w():
    w, h = 1720, 880
    y_end = 825
    xa = 150
    xi = 450
    xc = 800
    xp = 1200
    xb = 1550
    
    s = get_header(w, h, "sd [CU05W] Gestionar planes de suscripcion (UML 2.5+ / BCE)")
    s += draw_actor(xa, "Administrador", "(SuperAdmin)", y_end)
    s += draw_box(xi, 130, "boundary", "IU_PlanesSaaS", y_end)
    s += draw_box(xc, 150, "control", "PlanSaaSControl", y_end)
    s += draw_box(xp, 120, "entity", ":t_plan", y_end)
    s += draw_box(xb, 120, "entity", ":t_bitacora", y_end)
    
    s += draw_act(xi, 222, 570)
    s += draw_act(xc, 254, 515)
    s += draw_act(xp, 318, 38)
    s += draw_act(xp, 510, 38)
    s += draw_act(xb, 576, 38)
    
    s += draw_sync(xa, xi - 6, 228, "1: solicitar_actualizacion_plan(codigo_plan, nombre, activo)")
    s += draw_sync(xi + 6, xc - 6, 260, "2: actualizar_plan(codigo_plan, datos)")
    s += draw_self(xc, 276, 20, "3: verificar_permiso_superadmin(payload)")
    s += draw_sync(xc + 6, xp - 6, 322, "4: SELECT codigo, max_sucursales, activo FROM t_plan WHERE codigo = :codigo")
    s += draw_ret(xp - 6, xc + 6, 352, "5: return plan_db")
    
    s += draw_alt(35, 375, w - 70, 410,
                  "[plan_db == null] (Curso Alterno: Plan No Encontrado)",
                  475,
                  "[else: plan_db != null] (Curso Basico: Actualizacion de Parametros del Plan)")
    
    s += draw_err(xc - 6, xi + 6, 415, "6.1: (Error, \"Plan de suscripcion no encontrado\")")
    s += draw_err(xi - 6, xa, 445, "6.2: Mostrar error: \"Plan de suscripcion inexistente en la plataforma\"")
    
    s += draw_sync(xc + 6, xp - 6, 515, "7: UPDATE t_plan SET nombre = :nombre, activo = :activo WHERE codigo = :codigo RETURNING codigo")
    s += draw_ret(xp - 6, xc + 6, 545, "8: return plan_actualizado")
    s += draw_sync(xc + 6, xb - 6, 580, "9: INSERT INTO t_bitacora(id_usuario, modulo='SAAS', accion='ACTUALIZAR_PLAN', entidad='t_plan', ...)")
    s += draw_ret(xb - 6, xc + 6, 610, "10: return confirmacion_log")
    s += draw_ret(xc - 6, xi + 6, 665, "11: confirmar_actualizacion(plan_actualizado)", color="#15803d", italic=False)
    s += draw_ret(xi - 6, xa, 700, "12: actualizar_planes()", italic=False)
    
    s += "</svg>"
    render_dual("CU05W_Gestionar_Planes_Suscripcion_Secuencia", s)


# ==============================================================================
# CU06W: Gestionar suscripciones empresariales
# ==============================================================================
def gen_cu06w():
    w, h = 1980, 1060
    y_end = 1005
    xa = 130
    xi = 370
    xc = 640
    xe = 920
    xp = 1170
    xsc = 1420
    xs = 1670
    xb = 1890
    
    s = get_header(w, h, "sd [CU06W] Gestionar suscripciones empresariales (UML 2.5+ / BCE)")
    s += draw_actor(xa, "Administrador /", "Administrador de Tienda", y_end)
    s += draw_box(xi, 130, "boundary", "IU_Suscripciones", y_end)
    s += draw_box(xc, 150, "control", "SuscripcionControl", y_end)
    s += draw_box(xe, 120, "entity", ":empresa", y_end)
    s += draw_box(xp, 120, "entity", ":t_plan", y_end)
    s += draw_box(xsc, 130, "entity", ":t_sucursal", y_end)
    s += draw_box(xs, 130, "entity", ":t_suscripcion", y_end)
    s += draw_box(xb, 120, "entity", ":t_bitacora", y_end)
    
    s += draw_act(xi, 222, 750)
    s += draw_act(xc, 254, 695)
    s += draw_act(xe, 288, 38)
    s += draw_act(xp, 348, 38)
    s += draw_act(xsc, 408, 38)
    s += draw_act(xs, 468, 38)
    s += draw_act(xs, 658, 38)
    s += draw_act(xb, 728, 38)
    
    s += draw_sync(xa, xi - 6, 228, "1: solicitar_alta_suscripcion(id_empresa, codigo_plan, periodo, motivo)")
    s += draw_sync(xi + 6, xc - 6, 260, "2: crear_suscripcion(id_empresa, datos_suscripcion)")
    s += draw_sync(xc + 6, xe - 6, 292, "3: SELECT estado FROM empresa WHERE id_empresa = :id FOR UPDATE")
    s += draw_ret(xe - 6, xc + 6, 322, "4: return estado_empresa")
    s += draw_sync(xc + 6, xp - 6, 352, "5: SELECT max_sucursales, activo FROM t_plan WHERE codigo = :codigo FOR SHARE")
    s += draw_ret(xp - 6, xc + 6, 382, "6: return datos_plan")
    s += draw_sync(xc + 6, xsc - 6, 412, "7: SELECT COUNT(*) FROM t_sucursal WHERE id_empresa = :id AND activo = true")
    s += draw_ret(xsc - 6, xc + 6, 442, "8: return sucursales_activas")
    s += draw_sync(xc + 6, xs - 6, 472, "9: SELECT 1 FROM t_suscripcion WHERE id_empresa = :id AND estado='ACTIVA' AND inicio &lt; :fin AND fin &gt; :inicio")
    s += draw_ret(xs - 6, xc + 6, 502, "10: return periodo_solapado")
    
    s += draw_alt(35, 520, w - 70, 455,
                  "[estado_empresa != 'ACTIVO' || sucursales_activas &gt; max_sucursales || periodo_solapado] (Rechazo)",
                  620,
                  "[else: validaciones_conformes] (Curso Basico: Registro de Suscripcion)")
    
    s += draw_err(xc - 6, xi + 6, 560, "11.1: (Error, \"Periodo solapado o sucursales exceden limite del plan\")")
    s += draw_err(xi - 6, xa, 590, "11.2: Mostrar error: \"Suscripcion incompatible: sucursales exceden limite\"")
    
    s += draw_sync(xc + 6, xs - 6, 665, "12: INSERT INTO t_suscripcion(id_empresa, codigo_plan, estado='ACTIVA', inicio, fin, motivo)")
    s += draw_ret(xs - 6, xc + 6, 695, "13: return id_suscripcion")
    s += draw_sync(xc + 6, xb - 6, 730, "14: INSERT INTO t_bitacora(id_usuario, id_empresa, modulo='SAAS', accion='ALTA_SUSCRIPCION', ...)")
    s += draw_ret(xb - 6, xc + 6, 760, "15: return confirmacion_log")
    s += draw_ret(xc - 6, xi + 6, 815, "16: confirmar_suscripcion(id_suscripcion)", color="#15803d", italic=False)
    s += draw_ret(xi - 6, xa, 850, "17: actualizar_suscripciones()", italic=False)
    
    s += "</svg>"
    render_dual("CU06W_Gestionar_Suscripciones_Empresariales_Secuencia", s)


# ==============================================================================
# CU07W: Consultar plan y limites de suscripcion
# ==============================================================================
def gen_cu07w():
    w, h = 1920, 960
    y_end = 905
    xa = 140
    xi = 410
    xc = 720
    xe = 1010
    xs = 1270
    xp = 1530
    xsc = 1770
    
    s = get_header(w, h, "sd [CU07W] Consultar plan y limites de suscripcion (UML 2.5+ / BCE)")
    s += draw_actor(xa, "Administrador", "", y_end)
    s += draw_box(xi, 130, "boundary", "IU_MiPlan", y_end)
    s += draw_box(xc, 160, "control", "ConsultaPlanControl", y_end)
    s += draw_box(xe, 120, "entity", ":empresa", y_end)
    s += draw_box(xs, 130, "entity", ":t_suscripcion", y_end)
    s += draw_box(xp, 120, "entity", ":t_plan", y_end)
    s += draw_box(xsc, 130, "entity", ":t_sucursal", y_end)
    
    s += draw_act(xi, 222, 650)
    s += draw_act(xc, 254, 595)
    s += draw_act(xe, 318, 38)
    s += draw_act(xs, 382, 38)
    s += draw_act(xp, 578, 38)
    s += draw_act(xsc, 642, 38)
    
    s += draw_sync(xa, xi - 6, 228, "1: solicitar_consulta_plan(id_empresa)")
    s += draw_sync(xi + 6, xc - 6, 260, "2: consultar_plan_empresa(id_empresa)")
    s += draw_self(xc, 276, 20, "3: validar_acceso_recurso_tenant(payload, id_empresa)")
    s += draw_sync(xc + 6, xe - 6, 322, "4: SELECT estado, nombre_empresa FROM empresa WHERE id_empresa = :id")
    s += draw_ret(xe - 6, xc + 6, 352, "5: return datos_empresa")
    s += draw_sync(xc + 6, xs - 6, 386, "6: SELECT id_suscripcion, codigo_plan, inicio, fin FROM t_suscripcion WHERE id_empresa = :id AND estado='ACTIVA' AND NOW() BETWEEN inicio AND fin")
    s += draw_ret(xs - 6, xc + 6, 416, "7: return suscripcion_activa")
    
    s += draw_alt(35, 440, w - 70, 435,
                  "[suscripcion_activa == null] (Curso Alterno: Sin Suscripcion Vigente)",
                  540,
                  "[else: suscripcion_activa != null] (Curso Basico: Consulta y Calculo de Limites)")
    
    s += draw_err(xc - 6, xi + 6, 480, "8.1: (Alerta, \"Sin suscripcion activa o vigente\")")
    s += draw_err(xi - 6, xa, 510, "8.2: Mostrar alerta: \"Empresa sin suscripcion vigente\"")
    
    s += draw_sync(xc + 6, xp - 6, 582, "9: SELECT nombre, max_sucursales, reportes_generativos FROM t_plan WHERE codigo = :codigo_plan")
    s += draw_ret(xp - 6, xc + 6, 612, "10: return limites_plan")
    s += draw_sync(xc + 6, xsc - 6, 646, "11: SELECT COUNT(*) FROM t_sucursal WHERE id_empresa = :id AND activo = true")
    s += draw_ret(xsc - 6, xc + 6, 676, "12: return conteo_sucursales_activas")
    s += draw_self(xc, 706, 20, "13: calcular_margen_y_dias_restantes(suscripcion, limites, conteo)")
    s += draw_ret(xc - 6, xi + 6, 755, "14: entregar_resumen_plan(limites, conteo, dias_restantes)", color="#15803d", italic=False)
    s += draw_ret(xi - 6, xa, 790, "15: mostrar_tablero_plan_y_limites()", italic=False)
    
    s += "</svg>"
    render_dual("CU07W_Consultar_Plan_Limites_Suscripcion_Secuencia", s)


# ==============================================================================
# CU08W: Gestionar respaldos y restauraciones
# ==============================================================================
def gen_cu08w():
    w, h = 1860, 940
    y_end = 885
    xa = 130
    xi = 390
    xc = 700
    xu = 1000
    xr = 1250
    xpg = 1500
    xb = 1730
    
    s = get_header(w, h, "sd [CU08W] Gestionar respaldos y restauraciones (UML 2.5+ / BCE)")
    s += draw_actor(xa, "Administrador", "(SuperAdmin)", y_end)
    s += draw_box(xi, 130, "boundary", "IU_Respaldos", y_end)
    s += draw_box(xc, 150, "control", "BackupControl", y_end)
    s += draw_box(xu, 120, "entity", ":t_usuario", y_end)
    s += draw_box(xr, 120, "entity", ":t_rol", y_end)
    s += draw_box(xpg, 130, "entity", ":PostgreSQL_DB", y_end)
    s += draw_box(xb, 120, "entity", ":t_bitacora", y_end)
    
    s += draw_act(xi, 222, 630)
    s += draw_act(xc, 254, 575)
    s += draw_act(xu, 288, 38)
    s += draw_act(xr, 350, 38)
    s += draw_act(xpg, 580, 40)
    s += draw_act(xb, 655, 38)
    
    s += draw_sync(xa, xi - 6, 228, "1: solicitar_generacion_backup(tipo='FULL_SQL')")
    s += draw_sync(xi + 6, xc - 6, 260, "2: generar_backup(tipo)")
    s += draw_sync(xc + 6, xu - 6, 292, "3: SELECT id_rol FROM t_usuario WHERE id_usuario = :id_usuario")
    s += draw_ret(xu - 6, xc + 6, 322, "4: return id_rol")
    s += draw_sync(xc + 6, xr - 6, 354, "5: SELECT nombre_rol FROM t_rol WHERE id_rol = :id_rol")
    s += draw_ret(xr - 6, xc + 6, 384, "6: return nombre_rol")
    
    s += draw_alt(35, 405, w - 70, 445,
                  "[nombre_rol != 'ADMINISTRADOR'] (Curso Alterno: Acceso Denegado)",
                  505,
                  "[else: rol == 'ADMINISTRADOR'] (Curso Basico: Dump de Base de Datos y Descarga)")
    
    s += draw_err(xc - 6, xi + 6, 445, "7.1: (Error, \"Acceso denegado: permisos insuficientes\")")
    s += draw_err(xi - 6, xa, 475, "7.2: Mostrar error: \"Permisos insuficientes para generar respaldos\"")
    
    s += draw_self(xc, 540, 20, "8: preparar_comando_pg_dump(schema='comercio', host, db)")
    s += draw_sync(xc + 6, xpg - 6, 585, "9: SELECT pg_dump(schema='comercio', formato='sql')")
    s += draw_ret(xpg - 6, xc + 6, 615, "10: return dump_sql_bytes")
    s += draw_sync(xc + 6, xb - 6, 660, "11: INSERT INTO t_bitacora(id_usuario, modulo='ADMIN', accion='BACKUP_GENERADO', ...)")
    s += draw_ret(xb - 6, xc + 6, 690, "12: return confirmacion_log")
    s += draw_ret(xc - 6, xi + 6, 740, "13: entregar_archivo_sql(dump_sql_bytes, \"backup.sql\")", color="#15803d", italic=False)
    s += draw_ret(xi - 6, xa, 775, "14: descargar_archivo_backup()", italic=False)
    
    s += "</svg>"
    render_dual("CU08W_Gestionar_Respaldos_Restauraciones_Secuencia", s)


# ==============================================================================
# CU09W: Gestionar asignaciones de empleados a sucursales
# ==============================================================================
def gen_cu09w():
    w, h = 1920, 980
    y_end = 925
    xa = 140
    xi = 410
    xc = 720
    xu = 1010
    xsc = 1270
    xus = 1530
    xb = 1780
    
    s = get_header(w, h, "sd [CU09W] Gestionar asignaciones de empleados a sucursales (UML 2.5+ / BCE)")
    s += draw_actor(xa, "Administrador de Tienda", "", y_end)
    s += draw_box(xi, 150, "boundary", "IU_AsignacionSucursales", y_end)
    s += draw_box(xc, 150, "control", "AsignacionControl", y_end)
    s += draw_box(xu, 120, "entity", ":t_usuario", y_end)
    s += draw_box(xsc, 130, "entity", ":t_sucursal", y_end)
    s += draw_box(xus, 150, "entity", ":t_usuario_sucursal", y_end)
    s += draw_box(xb, 120, "entity", ":t_bitacora", y_end)
    
    s += draw_act(xi, 222, 670)
    s += draw_act(xc, 254, 615)
    s += draw_act(xu, 288, 38)
    s += draw_act(xsc, 350, 38)
    s += draw_act(xus, 542, 38)
    s += draw_act(xus, 630, 35)
    s += draw_act(xb, 712, 38)
    
    s += draw_sync(xa, xi - 6, 228, "1: solicitar_asignacion_sucursales(id_empleado, ids_sucursales)")
    s += draw_sync(xi + 6, xc - 6, 260, "2: asignar_sucursales(id_empleado, ids_sucursales)")
    s += draw_sync(xc + 6, xu - 6, 292, "3: SELECT id_empresa, estado FROM t_usuario WHERE id_usuario = :id_empleado")
    s += draw_ret(xu - 6, xc + 6, 322, "4: return datos_empleado")
    s += draw_sync(xc + 6, xsc - 6, 354, "5: SELECT COUNT(*) FROM t_sucursal WHERE id_sucursal = ANY(:ids) AND id_empresa = :actor_empresa")
    s += draw_ret(xsc - 6, xc + 6, 384, "6: return sucursales_validas_count")
    
    s += draw_alt(35, 405, w - 70, 485,
                  "[sucursales_validas_count != length(ids_sucursales) || datos_empleado.id_empresa != actor.id_empresa] (Rechazo)",
                  505,
                  "[else: sucursales_validas] (Curso Basico: Reemplazo Transaccional de Asignaciones)")
    
    s += draw_err(xc - 6, xi + 6, 445, "7.1: (Error, \"Sucursales invalidas o ajenas a la empresa\")")
    s += draw_err(xi - 6, xa, 475, "7.2: Mostrar error: \"Sucursales seleccionadas no pertenecen a la empresa\"")
    
    s += draw_sync(xc + 6, xus - 6, 545, "8: DELETE FROM t_usuario_sucursal WHERE id_usuario = :id_empleado")
    s += draw_ret(xus - 6, xc + 6, 575, "9: return asignaciones_previas_eliminadas")
    
    # loop asignacion
    s += draw_opt_loop(470, 600, xus - 450, 75, "[para cada id_sucursal en ids_sucursales]", "loop")
    s += draw_sync(xc + 6, xus - 6, 635, "10: INSERT INTO t_usuario_sucursal(id_usuario, id_sucursal)")
    s += draw_ret(xus - 6, xc + 6, 655, "11: return confirmacion_insercion")
    
    s += draw_sync(xc + 6, xb - 6, 715, "12: INSERT INTO t_bitacora(id_usuario, id_empresa, modulo='USUARIOS', accion='ASIGNAR_SUCURSALES', ...)")
    s += draw_ret(xb - 6, xc + 6, 745, "13: return confirmacion_log")
    s += draw_ret(xc - 6, xi + 6, 795, "14: confirmar_asignacion(ids_sucursales)", color="#15803d", italic=False)
    s += draw_ret(xi - 6, xa, 830, "15: actualizar_asignaciones()", italic=False)
    
    s += "</svg>"
    render_dual("CU09W_Gestionar_Asignaciones_Empleados_Sucursales_Secuencia", s)


# ==============================================================================
# EJECUCION MAESTRA
# ==============================================================================
def main():
    print("=== GENERANDO SUITE COMPLETA DE 9 DIAGRAMAS DE SECUENCIA UML 2.5+ ===")
    gen_cu01w()
    gen_cu02w()
    gen_cu03w()
    gen_cu04w()
    gen_cu05w()
    gen_cu06w()
    gen_cu07w()
    gen_cu08w()
    gen_cu09w()
    print("=== TODOS LOS 9 DIAGRAMAS GENERADOS SATISFACTORIAMENTE ===")

if __name__ == "__main__":
    main()
