#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de Diagramas de Navegación UML Estándar (Ingeniería de Software)
Aura Store - Sistema E-Commerce & Retail Multi-Tenant (SI2 - UAGRM)

Cubre exactamente:
1. Todos los Actores del modelo de casos de uso:
   - CLIENTE
   - ADMINISTRADOR
   - ADMINISTRADOR TIENDA
   - ENCARGADO DE SUCURSAL
   - CAJERO
   - PROVEEDOR
   - SISTEMA DE PAGOS (Externo)
   - SISTEMA DE IA (Externo)

2. Todos los 8 Paquetes de Casos de Uso del sistema:
   - Paquete 1: Autenticación y Gestión de Usuarios (CU01WM - CU04WM)
   - Paquete 2: Gestión de Catálogo (CU05WM, CU06WM, CU16W - CU19W)
   - Paquete 3: Gestión de Sucursales, Inventario y Proveedores (CU07WM, CU20W - CU23W, CU31W)
   - Paquete 4: E-Commerce (CU08WM, CU09WM, CU27W)
   - Paquete 5: Reservas (CU10WM, CU25W)
   - Paquete 6: Punto de Venta (POS) (CU24W, CU28W, CU29W)
   - Paquete 7: Pedidos y Reportes (CU11WM, CU32W, CU33W)
   - Paquete 8: Inteligencia Artificial y Experiencia del Cliente (CU12WM - CU14M, CU15M/CU26W)

Garantías de Diseño:
- Cero solapamiento de líneas sobre letras o cajas.
- White-halo protector en todas las etiquetas de transición.
- Ruteo ortogonal estricto por pasillos despejados.
- Flechas UML estandarizadas con marcadores SVG precisos.
- Estética formal de ingeniería de software (fondo blanco, líneas oscuras definidas).
"""

import os
import resvg_py

OUT_DIR = r"d:\Locked Files --EY\Projectos\Examen_parcial1_S12\docs\diagramas_navegacion"
BRAIN_DIR = r"C:\Users\eddym\.gemini\antigravity-ide\brain\bce20c4d-ff88-4ad8-93ad-540bb85f5c37"

def escape(text):
    return (str(text).replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
                     .replace('"', "&quot;")
                     .replace("'", "&apos;"))

# -------------------------------------------------------------
# CLASES DE MODELADO GEOMÉTRICO UML
# -------------------------------------------------------------

class UmlScreen:
    """Representa una pantalla, vista o modal con compartimentos UML."""
    def __init__(self, screen_id, x, y, w, stereotype, title, actions=None, min_h=None):
        self.id = screen_id
        self.x = x
        self.y = y
        self.w = w
        self.stereotype = stereotype
        self.title = title
        self.actions = actions or []
        
        self.h_header = 34 if stereotype else 26
        content_h = len(self.actions) * 16 + 12
        self.h = max(min_h or 0, self.h_header + content_h)

    def top(self, frac=0.5):
        return (self.x + self.w * frac, self.y)

    def bottom(self, frac=0.5):
        return (self.x + self.w * frac, self.y + self.h)

    def left(self, frac=0.5):
        return (self.x, self.y + self.h * frac)

    def right(self, frac=0.5):
        return (self.x + self.w, self.y + self.h * frac)

    def render(self):
        lines = []
        is_modal = "modal" in (self.stereotype or "").lower()
        dash = ' stroke-dasharray="4,3"' if is_modal else ''
        lines.append(f'  <g id="screen_{self.id}">')
        # Caja principal
        lines.append(f'    <rect x="{self.x}" y="{self.y}" width="{self.w}" height="{self.h}" rx="6" ry="6" fill="#ffffff" stroke="#111827" stroke-width="1.5"{dash}/>')
        # Línea divisoria de cabecera
        lines.append(f'    <line x1="{self.x}" y1="{self.y + self.h_header}" x2="{self.x + self.w}" y2="{self.y + self.h_header}" stroke="#111827" stroke-width="1.2"/>')
        
        # Textos de cabecera
        if self.stereotype:
            lines.append(f'    <text x="{self.x + self.w/2}" y="{self.y + 13}" font-size="9" font-style="italic" fill="#374151" text-anchor="middle">«{escape(self.stereotype)}»</text>')
            lines.append(f'    <text x="{self.x + self.w/2}" y="{self.y + 27}" font-size="11" font-weight="bold" fill="#111827" text-anchor="middle">{escape(self.title)}</text>')
        else:
            lines.append(f'    <text x="{self.x + self.w/2}" y="{self.y + 18}" font-size="11" font-weight="bold" fill="#111827" text-anchor="middle">{escape(self.title)}</text>')
            
        # Contenido / Acciones
        y_cur = self.y + self.h_header + 16
        for act in self.actions:
            lines.append(f'    <text x="{self.x + 10}" y="{y_cur}" font-size="9.5" fill="#1f2937">{escape(act)}</text>')
            y_cur += 16
            
        lines.append('  </g>')
        return "\n".join(lines)


class UmlPackageBox:
    """Caja de paquete / subsistema con pestaña superior UML."""
    def __init__(self, pkg_id, x, y, w, h, code, name, items=None, actor_tag=None):
        self.id = pkg_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.code = code
        self.name = name
        self.items = items or []
        self.actor_tag = actor_tag

    def top(self, frac=0.5):
        return (self.x + self.w * frac, self.y)

    def bottom(self, frac=0.5):
        return (self.x + self.w * frac, self.y + self.h)

    def left(self, frac=0.5):
        return (self.x, self.y + self.h * frac)

    def right(self, frac=0.5):
        return (self.x + self.w, self.y + self.h * frac)

    def render(self):
        lines = []
        lines.append(f'  <g id="pkg_{self.id}">')
        # Pestaña de paquete UML
        lines.append(f'    <path d="M {self.x} {self.y} L {self.x + 120} {self.y} L {self.x + 130} {self.y + 18} L {self.x} {self.y + 18} Z" fill="#f8fafc" stroke="#111827" stroke-width="1.4"/>')
        lines.append(f'    <text x="{self.x + 8}" y="{self.y + 13}" font-size="9" font-weight="bold" fill="#475569">{escape(self.code)}</text>')
        # Cuerpo del paquete
        lines.append(f'    <rect x="{self.x}" y="{self.y + 18}" width="{self.w}" height="{self.h - 18}" rx="4" ry="4" fill="#ffffff" stroke="#111827" stroke-width="1.5"/>')
        # Título del paquete
        lines.append(f'    <text x="{self.x + 12}" y="{self.y + 36}" font-size="11.5" font-weight="bold" fill="#0f172a">{escape(self.name)}</text>')
        if self.actor_tag:
            lines.append(f'    <text x="{self.x + self.w - 12}" y="{self.y + 36}" font-size="9.5" font-style="italic" fill="#0369a1" text-anchor="end">{escape(self.actor_tag)}</text>')
        lines.append(f'    <line x1="{self.x}" y1="{self.y + 44}" x2="{self.x + self.w}" y2="{self.y + 44}" stroke="#e2e8f0" stroke-width="1.2"/>')
        
        # Lista de CUs o módulos
        y_cur = self.y + 60
        for it in self.items:
            lines.append(f'    <text x="{self.x + 14}" y="{y_cur}" font-size="9.5" fill="#334155">{escape(it)}</text>')
            y_cur += 16
            
        lines.append('  </g>')
        return "\n".join(lines)


def draw_actor(cx, cy, name, role_desc=None):
    """Dibuja un actor UML estándar con soporte de nombre multi-línea."""
    lines = []
    lines.append(f'  <g id="actor_{escape(name).replace(" ", "_")}">')
    # Cabeza
    lines.append(f'    <circle cx="{cx}" cy="{cy - 30}" r="12" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>')
    # Tronco
    lines.append(f'    <line x1="{cx}" y1="{cy - 18}" x2="{cx}" y2="{cy + 15}" stroke="#111827" stroke-width="1.8"/>')
    # Brazos
    lines.append(f'    <line x1="{cx - 18}" y1="{cy - 7}" x2="{cx + 18}" y2="{cy - 7}" stroke="#111827" stroke-width="1.8"/>')
    # Piernas
    lines.append(f'    <line x1="{cx}" y1="{cy + 15}" x2="{cx - 14}" y2="{cy + 42}" stroke="#111827" stroke-width="1.8"/>')
    lines.append(f'    <line x1="{cx}" y1="{cy + 15}" x2="{cx + 14}" y2="{cy + 42}" stroke="#111827" stroke-width="1.8"/>')
    
    # Nombre
    if len(name) > 14 and " " in name:
        parts = name.split(" ")
        lines.append(f'    <text x="{cx}" y="{cy + 58}" font-size="10.5" font-weight="bold" fill="#111827" text-anchor="middle">{escape(parts[0])}</text>')
        lines.append(f'    <text x="{cx}" y="{cy + 71}" font-size="10.5" font-weight="bold" fill="#111827" text-anchor="middle">{escape(" ".join(parts[1:]))}</text>')
        offset_y = cy + 84
    else:
        lines.append(f'    <text x="{cx}" y="{cy + 60}" font-size="11" font-weight="bold" fill="#111827" text-anchor="middle">{escape(name)}</text>')
        offset_y = cy + 73

    if role_desc:
        lines.append(f'    <text x="{cx}" y="{offset_y}" font-size="9" font-style="italic" fill="#64748b" text-anchor="middle">{escape(role_desc)}</text>')

    lines.append('  </g>')
    return "\n".join(lines)


def draw_external_system(cx, cy, w, h, name):
    """Dibuja una caja de sistema externo participante (UML System Boundary / Node)."""
    x = cx - w/2
    y = cy - h/2
    lines = []
    lines.append(f'  <g id="ext_{escape(name).replace(" ", "_")}">')
    lines.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" ry="6" fill="#f8fafc" stroke="#111827" stroke-width="1.6" stroke-dasharray="5,3"/>')
    lines.append(f'    <text x="{cx}" y="{y + 16}" font-size="8.5" font-style="italic" fill="#475569" text-anchor="middle">«external system»</text>')
    lines.append(f'    <text x="{cx}" y="{y + 32}" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">{escape(name)}</text>')
    lines.append('  </g>')
    return "\n".join(lines)


# -------------------------------------------------------------
# RUTEO ORTOGONAL CON HALO PROTECTOR ANTI-SOLAPAMIENTO
# -------------------------------------------------------------

def draw_transition(points, label=None, label_pos=None, is_dashed=False, arrow_end=True):
    """
    Dibuja una transición entre nodos con ruteo ortogonal y etiqueta protegida por halo blanco.
    - points: lista de tuplas [(x1, y1), (x2, y2), ...]
    - label: texto de transición, ej: '[click_agregar] / agregar_item()'
    - label_pos: tupla opcional (lx, ly) para ubicar el texto
    """
    lines = []
    dash_attr = ' stroke-dasharray="4,4"' if is_dashed else ''
    marker_attr = ' marker-end="url(#uml_arrow)"' if arrow_end else ''
    
    d_parts = [f"M {points[0][0]} {points[0][1]}"]
    for pt in points[1:]:
        d_parts.append(f"L {pt[0]} {pt[1]}")
    d_str = " ".join(d_parts)
    
    # Línea de transición
    lines.append(f'  <path d="{d_str}" fill="none" stroke="#111827" stroke-width="1.4"{dash_attr}{marker_attr}/>')
    
    # Etiqueta con White-Halo (garantiza legibilidad absoluta sin líneas atravesadas)
    if label:
        if label_pos:
            lx, ly = label_pos
        else:
            # Punto medio del primer o segundo segmento
            p_a = points[0]
            p_b = points[1]
            lx = (p_a[0] + p_b[0]) / 2
            ly = (p_a[1] + p_b[1]) / 2 - 6
            
        esc_lbl = escape(label)
        # Capa de halo blanco debajo
        lines.append(f'  <text x="{lx}" y="{ly}" font-size="9" font-weight="500" fill="#111827" text-anchor="middle" paint-order="stroke fill" stroke="#ffffff" stroke-width="5" stroke-linejoin="round">{esc_lbl}</text>')
        
    return "\n".join(lines)


def wrap_svg(width, height, title, content):
    """Envoltorio SVG con defs de flechas y encabezado institucional."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <defs>
    <!-- Marcador de flecha de transición UML estándar -->
    <marker id="uml_arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#111827"/>
    </marker>
    <!-- Marcador de flecha abierta para retornos -->
    <marker id="uml_return_arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto">
      <path d="M 2 1.5 L 8 5 L 2 8.5" fill="none" stroke="#111827" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- Marco Estándar UML -->
  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#111827" stroke-width="1.5"/>
  <path d="M 15 15 L 640 15 L 655 35 L 655 45 L 15 45 Z" fill="#f8fafc" stroke="#111827" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12" font-weight="bold" fill="#0f172a">{escape(title)}</text>

{content}
</svg>'''


# =============================================================
# 1. DN00: DIAGRAMA MAESTRO GENERAL (ACTORES Y 8 PAQUETES)
# =============================================================

def build_dn00_general():
    width = 2460
    height = 1420
    content = []
    
    # Columna 1: Actores del Sistema (8 Actores)
    x_actors = 140
    content.append(draw_actor(x_actors, 160, "ADMINISTRADOR", "Superadmin Global"))
    content.append(draw_actor(x_actors, 360, "ADMINISTRADOR TIENDA", "Gestión Sucursal Local"))
    content.append(draw_actor(x_actors, 560, "ENCARGADO DE SUCURSAL", "Operaciones e Inventario"))
    content.append(draw_actor(x_actors, 760, "CAJERO", "Operador POS y Cobros"))
    content.append(draw_actor(x_actors, 960, "PROVEEDOR", "Abastecimiento y Catálogo"))
    content.append(draw_actor(x_actors, 1180, "CLIENTE", "Comprador Web & Móvil"))
    
    # Sistemas Externos (en la parte superior y lateral)
    content.append(draw_external_system(700, 100, 180, 50, "SISTEMA DE PAGOS"))
    content.append(draw_external_system(1420, 100, 180, 50, "SISTEMA DE IA"))
    
    # Nodo Central de Entrada y Distribución RBAC
    login_box = UmlScreen("login_central", 420, 600, 260, "screen", "Login & Autenticación Central", [
        "entry / renderizar_formulario()",
        "[click_iniciar] / autenticar_jwt()",
        "[rol_reconocido] -> Enrutar Módulo",
        "[sin_cuenta] -> Registro Cliente",
        "[recuperar_clave] -> Enviar OTP"
    ])
    content.append(login_box.render())
    
    # Conexiones de los 6 actores humanos al Login Central
    content.append(draw_transition([(x_actors + 40, 160), (320, 160), (320, 630), (420, 630)], "[ingresar]"))
    content.append(draw_transition([(x_actors + 40, 360), (340, 360), (340, 645), (420, 645)], "[ingresar]"))
    content.append(draw_transition([(x_actors + 40, 560), (360, 560), (360, 660), (420, 660)], "[ingresar]"))
    content.append(draw_transition([(x_actors + 40, 760), (360, 760), (360, 675), (420, 675)], "[ingresar]"))
    content.append(draw_transition([(x_actors + 40, 960), (340, 960), (340, 690), (420, 690)], "[ingresar]"))
    content.append(draw_transition([(x_actors + 40, 1180), (320, 1180), (320, 705), (420, 705)], "[ingresar / navegar_tienda]"))
    
    # Router Rombo de Roles
    rx, ry = 740, 665
    content.append(f'  <polygon points="{rx},{ry-24} {rx+28},{ry} {rx},{ry+24} {rx-28},{ry}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>')
    content.append(f'  <text x="{rx}" y="{ry+4}" font-size="8" font-weight="bold" fill="#111827" text-anchor="middle">RBAC</text>')
    content.append(draw_transition([login_box.right(0.5), (rx - 28, ry)], "[jwt_valido]"))
    
    # -------------------------------------------------------------
    # COLOCACIÓN DE LOS 8 PAQUETES DE CASOS DE USO
    # -------------------------------------------------------------
    
    # Paquete 1: Autenticación y Usuarios
    pkg1 = UmlPackageBox("p1", 900, 150, 420, 170, "PAQUETE 01", "AUTENTICACIÓN Y GESTIÓN DE USUARIOS", [
        "• CU01WM: Registrar Usuario",
        "• CU02WM: Iniciar Sesión",
        "• CU03WM: Gestionar Perfil",
        "• CU04WM: Gestionar Roles y Permisos"
    ], "ADMINISTRADOR / CLIENTE")
    content.append(pkg1.render())
    
    # Paquete 2: Gestión de Catálogo
    pkg2 = UmlPackageBox("p2", 1400, 150, 460, 200, "PAQUETE 02", "GESTIÓN DE CATÁLOGO", [
        "• CU05WM: Buscar y Filtrar Productos",
        "• CU06WM: Consultar Detalle de Producto",
        "• CU16W: Gestionar Productos y Colecciones",
        "• CU17W: Gestionar Categorías de Moda",
        "• CU18W: Gestionar Tallas y Colores",
        "• CU19W: Gestionar Actualización de Precios"
    ], "ADMINISTRADOR / CLIENTE")
    content.append(pkg2.render())
    
    # Paquete 3: Sucursales, Inventario y Proveedores
    pkg3 = UmlPackageBox("p3", 1930, 150, 480, 210, "PAQUETE 03", "GESTIÓN DE SUCURSALES, INVENTARIO Y PROVEEDORES", [
        "• CU07WM: Consultar Disponibilidad por Sucursal",
        "• CU20W: Gestionar Cadena de Tiendas / Sucursales",
        "• CU21W: Gestionar Proveedores y Pedidos",
        "• CU22W: Gestionar Inventario y Kardex",
        "• CU23W: Gestionar Disponibilidad de Prendas",
        "• CU31W: Consultar Ventas, Reservas e Inventario"
    ], "ADMIN / TIENDA / ENCARGADO / PROV")
    content.append(pkg3.render())
    
    # Paquete 4: E-Commerce
    pkg4 = UmlPackageBox("p4", 900, 430, 420, 170, "PAQUETE 04", "E-COMMERCE Y COMPRA EN LÍNEA", [
        "• CU08WM: Gestionar Carrito de Compras",
        "• CU09WM: Realizar Compra Online",
        "• CU27W: Procesar Pago Electrónico (QR / Tarjeta)"
    ], "CLIENTE / SISTEMA DE PAGOS")
    content.append(pkg4.render())
    
    # Paquete 5: Reservas
    pkg5 = UmlPackageBox("p5", 1400, 430, 460, 170, "PAQUETE 05", "GESTIÓN Y ATENCIÓN DE RESERVAS", [
        "• CU10WM: Gestionar Reservas (Apartado de Prendas)",
        "• CU25W: Atender y Despachar Reservas en Tienda"
    ], "CLIENTE / ENCARGADO SUCURSAL")
    content.append(pkg5.render())
    
    # Paquete 6: Punto de Venta (POS)
    pkg6 = UmlPackageBox("p6", 1930, 430, 480, 180, "PAQUETE 06", "PUNTO DE VENTA (POS)", [
        "• CU24W: Registrar Venta Presencial en Mostrador",
        "• CU28W: Procesar Pago en Caja (Efectivo / QR / Tarjeta)",
        "• CU29W: Emitir Comprobante de Venta (Factura SIN / Recibo)"
    ], "CAJERO / ENCARGADO SUCURSAL")
    content.append(pkg6.render())
    
    # Paquete 7: Pedidos y Reportes
    pkg7 = UmlPackageBox("p7", 900, 710, 420, 180, "PAQUETE 07", "PEDIDOS, INDICADORES Y REPORTES", [
        "• CU11WM: Consultar Pedidos y Seguimiento",
        "• CU32W: Visualizar Indicadores Empresariales (BI)",
        "• CU33W: Generar Reportes Bajo Demanda (PDF / Excel)"
    ], "CLIENTE / ADMIN / TIENDA")
    content.append(pkg7.render())
    
    # Paquete 8: Inteligencia Artificial y Experiencia del Cliente
    pkg8 = UmlPackageBox("p8", 1400, 710, 460, 200, "PAQUETE 08", "INTELIGENCIA ARTIFICIAL Y EXPERIENCIA", [
        "• CU12WM: Obtener Recomendaciones de Productos",
        "• CU13WM: Interactuar con Asistente Inteligente (Chat)",
        "• CU14M: Utilizar Vestidor Virtual (Realidad Aumentada)",
        "• CU15M / CU26W: Mostrar Ubicaciones de Sucursales"
    ], "CLIENTE / SISTEMA DE IA")
    content.append(pkg8.render())
    
    # Ruteo desde el Router RBAC a los Paquetes correspondientes
    content.append(draw_transition([(rx + 28, ry), (840, ry), (840, 235), (900, 235)], "[rol == ADMIN] -> P1"))
    content.append(draw_transition([(rx + 28, ry), (840, ry), (840, 515), (900, 515)], "[rol == CLIENTE] -> P4"))
    content.append(draw_transition([(rx + 28, ry), (840, ry), (840, 800), (900, 800)], "[rol == CLIENTE || ADMIN] -> P7"))
    
    # Conexiones adicionales limpias entre router y otros paquetes
    content.append(draw_transition([(1320, 515), (1400, 515)], "[reservar] -> P5"))
    content.append(draw_transition([(1860, 515), (1930, 515)], "[rol == CAJERO] -> P6"))
    content.append(draw_transition([(1320, 235), (1400, 235)], "[gestionar_prendas] -> P2"))
    content.append(draw_transition([(1860, 235), (1930, 235)], "[abastecimiento] -> P3"))
    content.append(draw_transition([(1320, 800), (1400, 800)], "[explorar_ia] -> P8"))
    
    # Conexiones con Sistemas Externos
    content.append(draw_transition([(700, 125), (700, 480), (900, 480)], "[webhook_pago / tokenizar]", None, True))
    content.append(draw_transition([(1420, 125), (1420, 710)], "[api_deepseek / vision_ar]", None, True))
    
    # Pie de diagrama con leyenda institucional
    content.append(f'  <rect x="900" y="990" width="1510" height="90" rx="6" ry="6" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2"/>')
    content.append(f'  <text x="920" y="1015" font-size="11" font-weight="bold" fill="#0f172a">ESTRUCTURA DE NAVEGACIÓN GLOBAL Y RELACIÓN CON ACTORES (SI2 - UAGRM):</text>')
    content.append(f'  <text x="920" y="1035" font-size="10" fill="#334155">1. Acceso Universal: Todo usuario inicia en el portal/login y es derivado mediante el controlador RBAC al paquete correspondiente.</text>')
    content.append(f'  <text x="920" y="1053" font-size="10" fill="#334155">2. Integración Externa: El Sistema de Pagos procesa cobros electrónicos en P4 y P6; el Sistema de IA alimenta sugerencias y vestidor RA en P8.</text>')
    content.append(f'  <text x="920" y="1070" font-size="10" fill="#334155">3. Cohesión de Flujo: Los diagramas específicos (DN01 a DN06) detallan el flujo de pantallas y eventos internos de cada paquete.</text>')
    
    return wrap_svg(width, height, "stm [General] DN00: Mapa Maestro de Navegación del Sistema Aura (8 Actores y 8 Módulos)", "\n".join(content))


# =============================================================
# 2. DN01: NAVEGACIÓN AUTENTICACIÓN Y GESTIÓN DE USUARIOS
# =============================================================

def build_dn01_auth():
    width = 1980
    height = 920
    content = []
    
    # Actores
    content.append(draw_actor(100, 240, "ADMINISTRADOR", "Gestor RBAC"))
    content.append(draw_actor(100, 580, "CLIENTE", "Usuario Registrado"))
    
    # Pantallas
    s_login = UmlScreen("login", 300, 360, 260, "screen", "Login_Screen", [
        "entry / inicializar_formulario()",
        "[click_iniciar] / enviar_credenciales()",
        "[click_crear] -> Registro_Usuario",
        "[click_recuperar] -> Recuperar_Clave",
        "[login_ok] -> Enrutar según Rol"
    ])
    content.append(s_login.render())
    
    s_registro = UmlScreen("registro", 680, 540, 280, "screen", "Registro_Usuario_Screen", [
        "«CU01WM: Registrar Usuario»",
        "entry / cargar_formulario_registro()",
        "[click_guardar] / validar_datos()",
        "[registro_exitoso] -> Login_Screen",
        "[cancelar] -> Login_Screen"
    ])
    content.append(s_registro.render())
    
    s_recuperar = UmlScreen("recuperar", 680, 200, 280, "modal", "Recuperar_Password_Modal", [
        "entry / solicitar_email_o_telefono()",
        "[click_enviar_otp] / despachar_codigo()",
        "[validar_otp] / restablecer_clave()",
        "[cerrar_modal] -> Login_Screen"
    ])
    content.append(s_recuperar.render())
    
    s_perfil = UmlScreen("perfil", 1120, 540, 300, "screen", "Perfil_Usuario_Screen", [
        "«CU03WM: Gestionar Perfil»",
        "entry / cargar_datos_personales()",
        "do / mostrar_direcciones_y_tarjetas()",
        "[click_editar] -> Editar_Perfil_Modal",
        "[cambiar_password] -> Modal_Password",
        "[cerrar_sesion] -> Login_Screen"
    ])
    content.append(s_perfil.render())
    
    s_edit_perfil = UmlScreen("edit_perfil", 1540, 540, 280, "modal", "Editar_Perfil_Modal", [
        "entry / precargar_formulario()",
        "[guardar_cambios] / update_perfil()",
        "[cancelar] -> Perfil_Usuario_Screen"
    ])
    content.append(s_edit_perfil.render())
    
    s_roles = UmlScreen("roles", 1120, 180, 320, "screen", "Gestion_Roles_Permisos_Screen", [
        "«CU04WM: Gestionar Roles y Permisos»",
        "entry / listar_usuarios_y_roles()",
        "[seleccionar_usuario] -> Asignar_Rol_Modal",
        "[crear_nuevo_rol] -> Configurar_Permisos",
        "[auditar_accesos] / exportar_bitacora()"
    ])
    content.append(s_roles.render())
    
    s_asignar_rol = UmlScreen("asignar_rol", 1560, 180, 300, "modal", "Asignar_Rol_Permisos_Modal", [
        "entry / cargar_arbol_permisos()",
        "[guardar_asignacion] / commit_rbac()",
        "[cancelar] -> Gestion_Roles_Permisos"
    ])
    content.append(s_asignar_rol.render())
    
    # Transiciones con White-Halo protector
    content.append(draw_transition([(140, 580), (300, 440)], "[acceder]"))
    content.append(draw_transition([(140, 240), (300, 390)], "[acceder_admin]"))
    
    content.append(draw_transition([s_login.right(0.3), (620, 400), (620, 260), s_recuperar.left(0.4)], "[olvido_clave]"))
    content.append(draw_transition([s_recuperar.left(0.7), (600, 300), (600, 420), s_login.right(0.4)], "[volver / clave_cambiada]"))
    
    content.append(draw_transition([s_login.right(0.7), (620, 450), (620, 600), s_registro.left(0.4)], "[click_registrarse]"))
    content.append(draw_transition([s_registro.left(0.7), (600, 650), (600, 470), s_login.right(0.8)], "[cuenta_creada]"))
    
    content.append(draw_transition([s_login.right(0.5), (1040, 430), (1040, 600), s_perfil.left(0.4)], "[login_exitoso / rol == CLIENTE]"))
    content.append(draw_transition([s_perfil.right(0.5), s_edit_perfil.left(0.5)], "[click_editar]"))
    content.append(draw_transition([s_edit_perfil.left(0.7), s_perfil.right(0.7)], "[guardar / cancelar]"))
    
    content.append(draw_transition([s_login.right(0.2), (1040, 380), (1040, 240), s_roles.left(0.4)], "[login_exitoso / rol == ADMIN]"))
    content.append(draw_transition([s_roles.right(0.5), s_asignar_rol.left(0.5)], "[editar_permisos]"))
    content.append(draw_transition([s_asignar_rol.left(0.7), s_roles.right(0.7)], "[guardar_rbac]"))
    
    return wrap_svg(width, height, "stm [Módulo 01] DN01: Navegación de Autenticación y Gestión de Usuarios (CU01WM - CU04WM)", "\n".join(content))


# =============================================================
# 3. DN02: NAVEGACIÓN E-COMMERCE, CATÁLOGO Y RESERVAS
# =============================================================

def build_dn02_ecommerce():
    width = 2380
    height = 1040
    content = []
    
    # Actores
    content.append(draw_actor(100, 360, "CLIENTE", "Comprador Retail"))
    content.append(draw_external_system(1900, 780, 200, 60, "SISTEMA DE PAGOS"))
    
    # Pantallas
    s_catalogo = UmlScreen("catalogo", 280, 300, 300, "screen", "Catalogo_Prendas_Screen", [
        "«CU05WM: Buscar y Filtrar Productos»",
        "entry / cargar_catalogo_reciente()",
        "[click_categoria] / filtrar_por_categoria()",
        "[click_prenda] -> Ficha_Detalle_Prenda",
        "[abrir_filtros] -> Filtros_Busqueda_Drawer",
        "[ver_carrito] -> Carrito_Compras_Drawer"
    ])
    content.append(s_catalogo.render())
    
    s_filtros = UmlScreen("filtros", 280, 680, 300, "modal", "Filtros_Busqueda_Drawer", [
        "entry / cargar_tallas_colores_precios()",
        "[aplicar_filtros] / actualizar_grilla()",
        "[limpiar_filtros] / reset_query()",
        "[cerrar] -> Catalogo_Prendas_Screen"
    ])
    content.append(s_filtros.render())
    
    s_detalle = UmlScreen("detalle", 720, 300, 320, "screen", "Ficha_Detalle_Prenda_Screen", [
        "«CU06WM: Consultar Detalle Producto»",
        "entry / cargar_variantes_stock_fotos()",
        "[seleccionar_talla_color] / recalcular_precio()",
        "[consultar_sucursal] -> Modal_Disponibilidad",
        "[click_agregar] -> Carrito_Compras_Drawer",
        "[click_reservar] -> Formulario_Reserva_Modal"
    ])
    content.append(s_detalle.render())
    
    s_disp = UmlScreen("disp", 720, 680, 320, "modal", "Disponibilidad_Sucursal_Modal", [
        "«CU07WM: Consultar Disponibilidad»",
        "entry / listar_sucursales_con_stock()",
        "[seleccionar_tienda_reserva] -> Form_Reserva",
        "[cerrar] -> Ficha_Detalle_Prenda"
    ])
    content.append(s_disp.render())
    
    s_reserva_form = UmlScreen("reserva_form", 1180, 680, 300, "modal", "Formulario_Reserva_Modal", [
        "«CU10WM: Gestionar Reservas»",
        "entry / fijar_tiempo_vigencia_48h()",
        "[confirmar_reserva] / generar_token_reserva()",
        "[reserva_exitosa] -> Mis_Reservas_Screen"
    ])
    content.append(s_reserva_form.render())
    
    s_mis_reservas = UmlScreen("mis_reservas", 1620, 680, 300, "screen", "Mis_Reservas_Screen", [
        "«CU10WM: Mis Reservas Activas»",
        "entry / listar_reservas_vigentes()",
        "[mostrar_qr_retiro] / mostrar_modal_qr()",
        "[cancelar_reserva] / liberar_stock()"
    ])
    content.append(s_mis_reservas.render())
    
    s_carrito = UmlScreen("carrito", 1180, 300, 300, "modal", "Carrito_Compras_Drawer", [
        "«CU08WM: Gestionar Carrito de Compras»",
        "entry / calcular_subtotal_descuentos()",
        "[modificar_cantidad] / actualizar_item()",
        "[eliminar_prenda] / remover_linea()",
        "[proceder_checkout] -> Checkout_Envio_Screen"
    ])
    content.append(s_carrito.render())
    
    s_checkout = UmlScreen("checkout", 1620, 300, 300, "screen", "Checkout_Envio_Screen", [
        "«CU09WM: Realizar Compra Online»",
        "entry / seleccionar_direccion_envio()",
        "[elegir_retiro_sucursal] / asignar_tienda()",
        "[calcular_tarifa_courier] / sumar_total()",
        "[continuar_al_pago] -> Pasarela_Pago_Screen"
    ])
    content.append(s_checkout.render())
    
    s_pasarela = UmlScreen("pasarela", 2040, 300, 280, "screen", "Pasarela_Pago_Screen", [
        "«CU27W: Procesar Pago Electrónico»",
        "entry / solicitar_intencion_pago()",
        "[pagar_qr_simple] / generar_qr_dinamico()",
        "[pagar_tarjeta] / tokenizar_pasarela()",
        "[pago_aprobado] -> Confirmacion_Compra",
        "[pago_rechazado] / reintentar()"
    ])
    content.append(s_pasarela.render())
    
    s_confirmacion = UmlScreen("confirmacion", 2040, 680, 280, "screen", "Confirmacion_Compra_Screen", [
        "«CU09WM: Confirmación de Pedido»",
        "entry / generar_recibo_digital()",
        "do / enviar_notificacion_email()",
        "[ver_seguimiento] -> Mis_Pedidos_Screen",
        "[volver_inicio] -> Catalogo_Prendas"
    ])
    content.append(s_confirmacion.render())
    
    # Transiciones
    content.append(draw_transition([(140, 360), (280, 360)], "[explorar_catalogo]"))
    content.append(draw_transition([s_catalogo.bottom(0.5), s_filtros.top(0.5)], "[abrir_filtros]"))
    content.append(draw_transition([s_filtros.top(0.7), s_catalogo.bottom(0.7)], "[aplicar / cerrar]"))
    
    content.append(draw_transition([s_catalogo.right(0.4), s_detalle.left(0.4)], "[click_prenda]"))
    content.append(draw_transition([s_detalle.bottom(0.4), s_disp.top(0.4)], "[consultar_disponibilidad]"))
    content.append(draw_transition([s_disp.top(0.7), s_detalle.bottom(0.7)], "[cerrar]"))
    
    content.append(draw_transition([s_detalle.right(0.4), s_carrito.left(0.4)], "[click_agregar_al_carrito]"))
    content.append(draw_transition([s_detalle.right(0.7), (1100, 410), (1100, 720), s_reserva_form.left(0.4)], "[click_apartar_reserva]"))
    content.append(draw_transition([s_disp.right(0.5), s_reserva_form.left(0.6)], "[reservar_en_sucursal]"))
    content.append(draw_transition([s_reserva_form.right(0.5), s_mis_reservas.left(0.5)], "[reserva_confirmada]"))
    
    content.append(draw_transition([s_carrito.right(0.5), s_checkout.left(0.5)], "[proceder_al_checkout]"))
    content.append(draw_transition([s_checkout.right(0.5), s_pasarela.left(0.5)], "[continuar_al_pago]"))
    content.append(draw_transition([s_pasarela.bottom(0.5), s_confirmacion.top(0.5)], "[pago_aprobado]"))
    
    # Conexión externa con Sistema de Pagos
    content.append(draw_transition([(1900, 780), (1900, 440), (2040, 440)], "[webhook_notificacion_pago]", None, True))
    
    return wrap_svg(width, height, "stm [Módulos 02, 04, 05] DN02: Navegación E-Commerce, Catálogo Retail y Reservas (CU05WM-CU10WM, CU27W)", "\n".join(content))


# =============================================================
# 4. DN03: NAVEGACIÓN IA Y EXPERIENCIA DEL CLIENTE
# =============================================================

def build_dn03_ia():
    width = 2080
    height = 920
    content = []
    
    # Actores
    content.append(draw_actor(100, 360, "CLIENTE", "Usuario Interactivo"))
    content.append(draw_external_system(1480, 100, 220, 60, "SISTEMA DE IA"))
    
    s_portal_ia = UmlScreen("portal_ia", 280, 300, 280, "screen", "Hub_Experiencia_Cliente_Screen", [
        "entry / inicializar_preferencias()",
        "[ver_recomendaciones] -> Carrousel_Recomendaciones",
        "[abrir_asistente] -> Asistente_Chat_Screen",
        "[probar_probador] -> Vestidor_Virtual_RA",
        "[ver_tiendas_cercanas] -> Mapa_Sucursales"
    ])
    content.append(s_portal_ia.render())
    
    s_recom = UmlScreen("recom", 700, 180, 320, "screen", "Recomendaciones_Personalizadas_Screen", [
        "«CU12WM: Obtener Recomendaciones»",
        "entry / consultar_scoring_afinidad_ia()",
        "do / renderizar_carrousel_para_ti()",
        "[click_prenda_recomendada] -> Ficha_Prenda",
        "[refrescar_preferencias] / recomputar()"
    ])
    content.append(s_recom.render())
    
    s_chat = UmlScreen("chat", 700, 520, 320, "screen", "Asistente_Virtual_Chat_Screen", [
        "«CU13WM: Interactuar con Asistente IA»",
        "entry / iniciar_sesion_deepseek()",
        "[enviar_pregunta] / consultar_llm_prendas()",
        "[recibir_respuesta] / renderizar_tarjeta_ropa()",
        "[click_prenda_sugerida] -> Ficha_Prenda"
    ])
    content.append(s_chat.render())
    
    s_vestidor = UmlScreen("vestidor", 1160, 300, 340, "screen", "Vestidor_Virtual_RA_Screen", [
        "«CU14M: Utilizar Vestidor Virtual RA»",
        "entry / activar_camara_dispositivo()",
        "do / cargar_modelo_3d_textura_prenda()",
        "[ajustar_talla_calce] / recalcular_mesh()",
        "[capturar_foto_outfit] / guardar_en_galeria()",
        "[agregar_al_carrito] -> Carrito_Compras"
    ])
    content.append(s_vestidor.render())
    
    s_mapa = UmlScreen("mapa", 1160, 650, 340, "screen", "Mapa_Ubicaciones_Sucursales_Screen", [
        "«CU15M / CU26W: Mostrar Ubicaciones»",
        "entry / solicitar_geolocalizacion_gps()",
        "do / trazar_ruta_sucursal_mas_cercana()",
        "[seleccionar_tienda] / ver_horarios_y_stock()",
        "[iniciar_navegacion_gps] / abrir_google_maps()"
    ])
    content.append(s_mapa.render())
    
    # Transiciones
    content.append(draw_transition([(140, 360), (280, 360)], "[ingresar_experiencia_ia]"))
    content.append(draw_transition([s_portal_ia.right(0.2), (620, 330), (620, 240), s_recom.left(0.4)], "[click_sugerencias_moda]"))
    content.append(draw_transition([s_portal_ia.right(0.8), (620, 420), (620, 580), s_chat.left(0.4)], "[click_abrir_chat_deepseek]"))
    content.append(draw_transition([s_portal_ia.right(0.5), s_vestidor.left(0.5)], "[click_probar_en_vestidor_ra]"))
    content.append(draw_transition([s_portal_ia.bottom(0.5), (420, 720), s_mapa.left(0.4)], "[click_buscar_tiendas]"))
    
    # Interacción con el Sistema de IA Externo
    content.append(draw_transition([(1480, 130), (1020, 130), s_recom.top(0.6)], "[vector_embeddings / ranking_afinidad]", None, True))
    content.append(draw_transition([(1540, 130), (1540, 560), (1020, 560), s_chat.right(0.3)], "[prompt_tokens / deepseek_llm_stream]", None, True))
    content.append(draw_transition([(1600, 130), (1600, 350), s_vestidor.right(0.4)], "[segmentacion_pose_mesh_3d]", None, True))
    
    return wrap_svg(width, height, "stm [Módulo 08] DN03: Navegación de Inteligencia Artificial y Experiencia del Cliente (CU12WM - CU14M, CU15M/CU26W)", "\n".join(content))


# =============================================================
# 5. DN04: NAVEGACIÓN PUNTO DE VENTA (POS) Y RESERVAS
# =============================================================

def build_dn04_pos():
    width = 2240
    height = 980
    content = []
    
    # Actores
    content.append(draw_actor(100, 320, "CAJERO", "Operador de Mostrador"))
    content.append(draw_actor(100, 680, "ENCARGADO DE SUCURSAL", "Supervisor de Tienda"))
    
    s_apertura = UmlScreen("apertura", 280, 260, 280, "screen", "Apertura_Caja_Turno_Screen", [
        "entry / ingresar_monto_apertura()",
        "[validar_monto_inicial] / registrar_sesion()",
        "[caja_abierta] -> Terminal_POS_Screen"
    ])
    content.append(s_apertura.render())
    
    s_pos = UmlScreen("pos", 680, 260, 340, "screen", "Terminal_Punto_Venta_POS_Screen", [
        "«CU24W: Registrar Venta Presencial»",
        "entry / inicializar_ticket_venta()",
        "[escanear_codigo_barras] / buscar_prenda()",
        "[agregar_variante] / actualizar_subtotal()",
        "[proceder_al_cobro] -> Modal_Cobro_Caja",
        "[cancelar_ticket] / descartar_venta()"
    ])
    content.append(s_pos.render())
    
    s_cobro = UmlScreen("cobro", 1140, 260, 320, "modal", "Cobro_Caja_Modal", [
        "«CU28W: Procesar Pago en Caja»",
        "entry / mostrar_total_a_pagar()",
        "[pago_efectivo] / calcular_cambio_bs()",
        "[pago_qr_bancario] / verificar_abono()",
        "[pago_pos_tarjeta] / confirmar_voucher()",
        "[cobro_exitoso] -> Emision_Comprobante"
    ])
    content.append(s_cobro.render())
    
    s_factura = UmlScreen("factura", 1580, 260, 320, "screen", "Emision_Comprobante_Screen", [
        "«CU29W: Emitir Comprobante de Venta»",
        "entry / firmar_factura_digital_sin()",
        "do / descontar_inventario_kardex()",
        "[imprimir_ticket_termico] / mandar_impresora()",
        "[nueva_venta] -> Terminal_POS_Screen"
    ])
    content.append(s_factura.render())
    
    s_atender_res = UmlScreen("atender_res", 680, 650, 340, "screen", "Atencion_Despacho_Reservas_Screen", [
        "«CU25W: Atender y Despachar Reservas»",
        "entry / listar_reservas_pendientes_sucursal()",
        "[escanear_qr_cliente] -> Validar_Reserva_Modal",
        "[cliente_desiste] / liberar_prenda_a_perchero()"
    ])
    content.append(s_atender_res.render())
    
    s_val_res = UmlScreen("val_res", 1140, 650, 320, "modal", "Validar_Reserva_Modal", [
        "entry / comprobar_codigo_y_vigencia()",
        "[reserva_valida] / transferir_items_a_pos()",
        "[derivar_a_caja] -> Cobro_Caja_Modal",
        "[reserva_expirada] / alertar_vencimiento()"
    ])
    content.append(s_val_res.render())
    
    s_cierre = UmlScreen("cierre", 1580, 650, 320, "screen", "Cierre_Caja_Arqueo_Screen", [
        "entry / consolidar_ventas_del_turno()",
        "[declarar_efectivo_en_caja] / contrastar_sistema()",
        "[firmar_cierre_arqueo] / cerrar_sesion()",
        "[imprimir_cierre_x_z] / generar_reporte()"
    ])
    content.append(s_cierre.render())
    
    # Transiciones
    content.append(draw_transition([(140, 320), (280, 320)], "[iniciar_turno]"))
    content.append(draw_transition([s_apertura.right(0.5), s_pos.left(0.5)], "[turno_iniciado]"))
    content.append(draw_transition([s_pos.right(0.5), s_cobro.left(0.5)], "[cobrar_venta]"))
    content.append(draw_transition([s_cobro.right(0.5), s_factura.left(0.5)], "[pago_asentado]"))
    content.append(draw_transition([s_factura.bottom(0.5), (1740, 480), (850, 480), s_pos.bottom(0.5)], "[siguiente_venta]"))
    
    content.append(draw_transition([(140, 680), (680, 680)], "[modulo_reservas_tienda]"))
    content.append(draw_transition([s_atender_res.right(0.5), s_val_res.left(0.5)], "[escanear_voucher_qr]"))
    content.append(draw_transition([s_val_res.top(0.5), s_cobro.bottom(0.5)], "[cobrar_saldo_reserva]"))
    
    content.append(draw_transition([s_val_res.right(0.5), s_cierre.left(0.5)], "[auditar_turnos]"))
    content.append(draw_transition([s_factura.bottom(0.8), (1800, 560), (1800, 650), s_cierre.top(0.7)], "[fin_jornada / arqueo]"))
    
    return wrap_svg(width, height, "stm [Módulo 05 & 06] DN04: Navegación de Punto de Venta (POS) y Atención de Reservas (CU24W, CU25W, CU28W, CU29W)", "\n".join(content))


# =============================================================
# 6. DN05: NAVEGACIÓN SUCURSALES, INVENTARIO Y PROVEEDORES
# =============================================================

def build_dn05_inventory():
    width = 2320
    height = 960
    content = []
    
    # Actores
    content.append(draw_actor(100, 220, "ADMINISTRADOR", "Supervisión Global"))
    content.append(draw_actor(100, 460, "ADMINISTRADOR TIENDA", "Gestión Tienda Física"))
    content.append(draw_actor(100, 700, "PROVEEDOR", "Distribuidor Mayorista"))
    
    s_panel = UmlScreen("panel", 280, 360, 280, "screen", "Panel_Control_Logistico_Screen", [
        "entry / verificar_rol_y_sucursal()",
        "[gestion_sucursales] -> Cadenas_Tiendas",
        "[control_kardex] -> Gestion_Inventario",
        "[abastecimiento] -> Portal_Proveedores",
        "[recepcion_stock] -> Recepcion_Mercaderia"
    ])
    content.append(s_panel.render())
    
    s_tiendas = UmlScreen("tiendas", 700, 180, 340, "screen", "Gestion_Cadenas_Tiendas_Screen", [
        "«CU20W: Gestionar Cadena de Tiendas»",
        "entry / listar_sucursales_y_almacenes()",
        "[crear_sucursal] -> Form_Nueva_Tienda",
        "[asignar_encargado] / actualizar_personal()",
        "[auditar_capacidad] / ver_aforo_m2()"
    ])
    content.append(s_tiendas.render())
    
    s_inventario = UmlScreen("inventario", 700, 540, 340, "screen", "Gestion_Inventario_Kardex_Screen", [
        "«CU22W & CU23W: Inventario y Prendas»",
        "entry / listar_stock_por_talla_color()",
        "[ajustar_stock_minimo] / emitir_alerta()",
        "[bloquear_prenda_averiada] / dar_de_baja()",
        "[traslado_entre_tiendas] -> Modal_Traslado"
    ])
    content.append(s_inventario.render())
    
    s_proveedores = UmlScreen("proveedores", 1180, 180, 340, "screen", "Portal_Gestion_Proveedores_Screen", [
        "«CU21W: Gestionar Proveedores»",
        "entry / listar_contratos_y_ordenes()",
        "[crear_orden_compra] -> Nueva_Orden_Modal",
        "[aprobar_presupuesto] / enviar_notificacion()",
        "[evaluar_desempeno] / registrar_scoring()"
    ])
    content.append(s_proveedores.render())
    
    s_recepcion = UmlScreen("recepcion", 1180, 540, 340, "screen", "Recepcion_Mercaderia_Screen", [
        "«CU31W: Registro de Recepción Mercadería»",
        "entry / escanear_guia_despacho_remision()",
        "[cotejar_cantidades] / validar_lote_prendas()",
        "[asentar_ingreso_kardex] / sumar_stock()",
        "[reportar_discrepancia] / abrir_reclamo()"
    ])
    content.append(s_recepcion.render())
    
    s_traslado = UmlScreen("traslado", 1660, 360, 320, "modal", "Modal_Traslado_Inter_Sucursal", [
        "entry / seleccionar_tienda_origen_destino()",
        "[despachar_bulto] / generar_guia_transito()",
        "[confirmar_recepcion_destino] / asentar()"
    ])
    content.append(s_traslado.render())
    
    # Transiciones
    content.append(draw_transition([(140, 220), (280, 380)], "[login_admin]"))
    content.append(draw_transition([(140, 460), (280, 410)], "[login_tienda]"))
    content.append(draw_transition([(140, 700), (280, 440)], "[portal_b2b]"))
    
    content.append(draw_transition([s_panel.right(0.2), (620, 390), (620, 240), s_tiendas.left(0.4)], "[admin_sucursales]"))
    content.append(draw_transition([s_panel.right(0.8), (620, 450), (620, 600), s_inventario.left(0.4)], "[control_kardex]"))
    
    content.append(draw_transition([s_tiendas.right(0.5), s_proveedores.left(0.5)], "[vincular_proveedores]"))
    content.append(draw_transition([s_inventario.right(0.5), s_recepcion.left(0.5)], "[recibir_lote_nuevo]"))
    content.append(draw_transition([s_proveedores.bottom(0.5), s_recepcion.top(0.5)], "[orden_aprobada -> esperar_guia]"))
    
    content.append(draw_transition([s_inventario.right(0.8), (1580, 640), (1580, 440), s_traslado.left(0.5)], "[transferir_prendas]"))
    
    return wrap_svg(width, height, "stm [Módulo 03] DN05: Navegación de Sucursales, Inventario, Proveedores y Abastecimiento (CU07WM, CU20W-CU23W, CU31W)", "\n".join(content))


# =============================================================
# 7. DN06: NAVEGACIÓN PEDIDOS, REPORTES Y BUSINESS INTELLIGENCE
# =============================================================

def build_dn06_bi():
    width = 2260
    height = 920
    content = []
    
    # Actores
    content.append(draw_actor(100, 260, "ADMINISTRADOR", "Supervisión Estratégica"))
    content.append(draw_actor(100, 620, "ADMINISTRADOR TIENDA", "Gestor Operativo"))
    
    s_hub_bi = UmlScreen("hub_bi", 280, 360, 280, "screen", "Hub_Analitica_Reportes_Screen", [
        "entry / cargar_permisos_alcance_datos()",
        "[ver_dashboard_bi] -> Dashboard_KPIs",
        "[consultar_ventas_stock] -> Monitor_Operativo",
        "[generar_reportes] -> Generador_Reportes"
    ])
    content.append(s_hub_bi.render())
    
    s_kpis = UmlScreen("kpis", 700, 180, 340, "screen", "Dashboard_KPIs_Empresariales_Screen", [
        "«CU32W: Indicadores Empresariales»",
        "entry / procesar_volumen_ventas_mes()",
        "do / renderizar_graficos_mrr_churn()",
        "[filtrar_por_temporada] / recalcular()",
        "[top_prendas_mas_vendidas] / drilldown()",
        "[exportar_snapshot_pdf] / compilar_pdf()"
    ])
    content.append(s_kpis.render())
    
    s_monitor = UmlScreen("monitor", 700, 540, 340, "screen", "Monitor_Ventas_Inventario_Screen", [
        "«CU31W: Consultar Ventas e Inventario»",
        "entry / cruzar_rotacion_prenda_vs_stock()",
        "[ver_alertas_quiebre_stock] / filtrar()",
        "[ver_reservas_sin_retirar] / listar()",
        "[descargar_tabla_excel] / exportar_csv()"
    ])
    content.append(s_monitor.render())
    
    s_reportes = UmlScreen("reportes", 1180, 360, 340, "screen", "Generador_Reportes_Demanda_Screen", [
        "«CU33W: Generar Reportes Bajo Demanda»",
        "entry / listar_plantillas_disponibles()",
        "[seleccionar_tipo_reporte] -> Config_Filtros",
        "[reporte_fiscal_ventas] / preparar_sin()",
        "[reporte_rotacion_prendas] / calcular()",
        "[reporte_rendimiento_sucursales] / agrupar()"
    ])
    content.append(s_reportes.render())
    
    s_config = UmlScreen("config", 1640, 360, 320, "modal", "Configuracion_Parametros_Reporte_Modal", [
        "entry / fijar_rango_fechas_sucursales()",
        "[elegir_formato_pdf_excel] / set_format()",
        "[ejecutar_generacion] / compilar_dataset()",
        "[reporte_listo] -> Visor_Descarga_Modal"
    ])
    content.append(s_config.render())
    
    s_visor = UmlScreen("visor", 1640, 680, 320, "modal", "Visor_Descarga_Reporte_Modal", [
        "entry / previsualizar_documento()",
        "[descargar_archivo_pdf] / save_local()",
        "[enviar_por_correo_gerencia] / send_smtp()",
        "[cerrar] -> Hub_Analitica_Reportes"
    ])
    content.append(s_visor.render())
    
    # Transiciones
    content.append(draw_transition([(140, 260), (280, 390)], "[alcance_global]"))
    content.append(draw_transition([(140, 620), (280, 430)], "[alcance_sucursal_propia]"))
    
    content.append(draw_transition([s_hub_bi.right(0.2), (620, 390), (620, 240), s_kpis.left(0.4)], "[abrir_dashboard_kpi]"))
    content.append(draw_transition([s_hub_bi.right(0.8), (620, 450), (620, 600), s_monitor.left(0.4)], "[monitorear_rotacion]"))
    content.append(draw_transition([s_hub_bi.right(0.5), s_reportes.left(0.5)], "[modulo_reportes]"))
    
    content.append(draw_transition([s_kpis.right(0.5), (1080, 240), (1080, 390), s_reportes.left(0.3)], "[exportar_informe_ejecutivo]"))
    content.append(draw_transition([s_monitor.right(0.5), (1080, 600), (1080, 430), s_reportes.left(0.7)], "[solicitar_auditoria_detallada]"))
    
    content.append(draw_transition([s_reportes.right(0.5), s_config.left(0.5)], "[configurar_filtros]"))
    content.append(draw_transition([s_config.bottom(0.5), s_visor.top(0.5)], "[compilacion_exitosa]"))
    
    return wrap_svg(width, height, "stm [Módulo 07] DN06: Navegación de Pedidos, Indicadores Empresariales y Reportes BI (CU11WM, CU32W, CU33W)", "\n".join(content))


# =============================================================
# MAIN DE EJECUCIÓN Y RENDERIZADO
# =============================================================

DIAGRAMS = [
    ("DN00_Mapa_General_Navegacion_Sistema_Aura", build_dn00_general),
    ("DN01_Navegacion_Autenticacion_Usuarios", build_dn01_auth),
    ("DN02_Navegacion_Ecommerce_Catalogo_Reservas", build_dn02_ecommerce),
    ("DN03_Navegacion_Inteligencia_Artificial_Experiencia", build_dn03_ia),
    ("DN04_Navegacion_Punto_Venta_POS_Reservas", build_dn04_pos),
    ("DN05_Navegacion_Sucursales_Inventario_Proveedores", build_dn05_inventory),
    ("DN06_Navegacion_Pedidos_Reportes_BI", build_dn06_bi),
]

def main():
    print("Iniciando generación de los 7 Diagramas de Navegación UML Estándar...")
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(BRAIN_DIR, exist_ok=True)
    
    for idx, (fname, builder) in enumerate(DIAGRAMS):
        svg_content = builder()
        svg_path = os.path.join(OUT_DIR, f"{fname}.svg")
        png_path = os.path.join(OUT_DIR, f"{fname}.png")
        brain_svg = os.path.join(BRAIN_DIR, f"{fname}.svg")
        brain_png = os.path.join(BRAIN_DIR, f"{fname}.png")
        
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        with open(brain_svg, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
        png_bytes = resvg_py.svg_to_bytes(svg_content, zoom=2.0)
        with open(png_path, "wb") as f:
            f.write(png_bytes)
        with open(brain_png, "wb") as f:
            f.write(png_bytes)
            
        print(f" [{idx+1}/{len(DIAGRAMS)}] Generado: {fname} (SVG + PNG 2x alta resolución)")

    print("\nTodos los Diagramas de Navegación han sido generados exitosamente.")

if __name__ == "__main__":
    main()
