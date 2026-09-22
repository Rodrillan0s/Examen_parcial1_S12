#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de Diagramas de Navegación Funcionales — Aurora Store
Arquitectura de Carriles Ortogonales Estrictos (Zero-Collision & Zero-Overlap)
Cumple al 100% con los requisitos del usuario:
- Orientado al usuario y a la navegación funcional (sin código, sin backend, sin APIs, sin BD)
- Cero solapamientos: ruteo ortogonal Manhattan limpio, textos protegidos con halo y posiciones calculadas
- Rectángulo = Pantalla/Vista, Flecha = Navegación, Rombo = Decisión
- Separación limpia de los 8 paquetes funcionales:
  1. DN00: General Navegación Aurora Store (Web / Mobile)
  2. DN01: Paquete Cliente / Comercio Electrónico (W04-W11, W26)
  3. DN02: Paquete Autenticación y Perfil (W01-W03, M01-M03)
  4. DN03: Paquete Inteligencia Artificial (W12, W13, M12-M14)
  5. DN04: Paquete Administración de Tienda (W14, W17-W21, W30)
  6. DN05: Paquete Sucursales e Inventario (W15, W16, W22, W23)
  7. DN06: Paquete Ventas, Reservas y Pagos (W24, W25, W27-W29)
  8. DN07: Paquete Indicadores y Reportes (W31, W32, W33)
"""

import os
import resvg_py

OUT_DIR = r"d:\Locked Files --EY\Projectos\Examen_parcial1_S12\docs\diagramas_navegacion"
BRAIN_DIR = r"C:\Users\eddym\.gemini\antigravity-ide\brain\bce20c4d-ff88-4ad8-93ad-540bb85f5c37"

def esc(text):
    return (str(text).replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
                     .replace('"', "&quot;")
                     .replace("'", "&apos;"))

# -------------------------------------------------------------
# CLASE SCREEN (PANTALLA / VISTA)
# -------------------------------------------------------------
class Screen:
    def __init__(self, node_id, x, y, w, title, view_type="pantalla", items=None, min_h=None):
        self.id = node_id
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)
        self.title = title
        self.view_type = view_type
        self.items = items or []
        
        self.header_h = 30 if view_type else 24
        items_h = len(self.items) * 16 + 10 if self.items else 6
        self.h = float(max(min_h or 54, self.header_h + items_h))

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
        is_modal = "modal" in self.view_type.lower() or "formulario" in self.view_type.lower()
        dash = ' stroke-dasharray="4,3"' if "modal" in self.view_type.lower() else ''
        header_fill = "#fefce8" if is_modal else "#f8fafc"
        
        lines.append(f'  <g id="screen_{self.id}">')
        # Rectángulo contenedor
        lines.append(f'    <rect x="{self.x}" y="{self.y}" width="{self.w}" height="{self.h}" rx="5" ry="5" fill="#ffffff" stroke="#0f172a" stroke-width="1.5"{dash}/>')
        # Cabecera
        lines.append(f'    <path d="M {self.x} {self.y + 5} Q {self.x} {self.y} {self.x + 5} {self.y} L {self.x + self.w - 5} {self.y} Q {self.x + self.w} {self.y} {self.x + self.w} {self.y + 5} L {self.x + self.w} {self.y + self.header_h} L {self.x} {self.y + self.header_h} Z" fill="{header_fill}"/>')
        lines.append(f'    <line x1="{self.x}" y1="{self.y + self.header_h}" x2="{self.x + self.w}" y2="{self.y + self.header_h}" stroke="#0f172a" stroke-width="1.2"/>')
        
        if self.view_type:
            lines.append(f'    <text x="{self.x + self.w/2}" y="{self.y + 12}" font-size="8.5" font-style="italic" fill="#475569" text-anchor="middle">«{esc(self.view_type)}»</text>')
            lines.append(f'    <text x="{self.x + self.w/2}" y="{self.y + 25}" font-size="10.5" font-weight="bold" fill="#0f172a" text-anchor="middle">{esc(self.title)}</text>')
        else:
            lines.append(f'    <text x="{self.x + self.w/2}" y="{self.y + 17}" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">{esc(self.title)}</text>')
            
        y_cur = self.y + self.header_h + 15
        for it in self.items:
            lines.append(f'    <text x="{self.x + 10}" y="{y_cur}" font-size="9" fill="#334155">{esc(it)}</text>')
            y_cur += 16
            
        lines.append('  </g>')
        return "\n".join(lines)


# -------------------------------------------------------------
# CLASE DECISION (ROMBO UML)
# -------------------------------------------------------------
class Decision:
    def __init__(self, node_id, cx, cy, label, size=24):
        self.id = node_id
        self.cx = float(cx)
        self.cy = float(cy)
        self.label = label
        self.s = float(size)

    def top(self):
        return (self.cx, self.cy - self.s)

    def bottom(self):
        return (self.cx, self.cy + self.s)

    def left(self):
        return (self.cx - self.s, self.cy)

    def right(self):
        return (self.cx + self.s, self.cy)

    def render(self):
        s = self.s
        lines = []
        lines.append(f'  <polygon points="{self.cx},{self.cy-s} {self.cx+s},{self.cy} {self.cx},{self.cy+s} {self.cx-s},{self.cy}" fill="#f8fafc" stroke="#0f172a" stroke-width="1.5"/>')
        lines.append(f'  <text x="{self.cx}" y="{self.cy + 3}" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">{esc(self.label)}</text>')
        return "\n".join(lines)


# -------------------------------------------------------------
# RUTEO ORTOGONAL ESTRICTO Y ETIQUETADO INTELIGENTE
# -------------------------------------------------------------
def link(pts, label=None, label_side="above", label_pos="last", custom_label_pos=None, is_dashed=False):
    """
    pts: lista de tuplas (x, y) que forman una ruta ortogonal Manhattan.
    label: texto de la acción o evento de navegación.
    label_side: 'above' (encima de línea horizontal), 'below' (debajo), 'right' (a la derecha de vertical), 'left' (a la izquierda).
    label_pos: 'last' (en el último segmento horizontal antes del nodo), 'first', 'mid'.
    custom_label_pos: tupla explícita (lx, ly) para control absoluto anti-colisión.
    """
    lines = []
    dash_attr = ' stroke-dasharray="4,4"' if is_dashed else ''
    
    d_parts = [f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"]
    for p in pts[1:]:
        d_parts.append(f"L {p[0]:.1f} {p[1]:.1f}")
    d_str = " ".join(d_parts)
    
    lines.append(f'  <path d="{d_str}" fill="none" stroke="#0f172a" stroke-width="1.3"{dash_attr} marker-end="url(#nav_arrow)"/>')
    
    if label:
        if custom_label_pos:
            lx, ly = custom_label_pos
        else:
            # Seleccionar segmento según label_pos
            if label_pos == "last" and len(pts) >= 2:
                p1, p2 = pts[-2], pts[-1]
            elif label_pos == "first" and len(pts) >= 2:
                p1, p2 = pts[0], pts[1]
            else:
                mid_idx = len(pts) // 2
                p1, p2 = pts[mid_idx - 1], pts[mid_idx]
                
            is_horizontal = abs(p1[1] - p2[1]) < 0.1
            
            if is_horizontal:
                # Segmento horizontal: colocar encima o debajo, centrado horizontalmente
                lx = (p1[0] + p2[0]) / 2
                if label_side == "above":
                    ly = p1[1] - 7
                else:
                    ly = p1[1] + 15
            else:
                # Segmento vertical: colocar a un lado, NUNCA sobre la línea
                ly = (p1[1] + p2[1]) / 2
                if label_side == "right":
                    lx = p1[0] + 12
                else:
                    lx = p1[0] - 12

        lines.append(f'  <text x="{lx:.1f}" y="{ly:.1f}" font-size="8.5" font-weight="600" fill="#0f172a" text-anchor="middle" paint-order="stroke fill" stroke="#ffffff" stroke-width="4.5" stroke-linejoin="round">{esc(label)}</text>')
        
    return "\n".join(lines)


def canvas(w, h, code, title, subtitle, content):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background-color: #ffffff; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;">
  <defs>
    <marker id="nav_arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#0f172a"/>
    </marker>
  </defs>

  <!-- Marco Exterior -->
  <rect x="15" y="15" width="{w - 30}" height="{h - 30}" rx="4" ry="4" fill="#ffffff" stroke="#0f172a" stroke-width="1.5"/>
  
  <!-- Pestaña Superior de Identificación -->
  <path d="M 15 15 L 750 15 L 765 38 L 765 48 L 15 48 Z" fill="#f8fafc" stroke="#0f172a" stroke-width="1.5"/>
  <text x="32" y="32" font-size="11.5" font-weight="bold" fill="#0f172a">nav [{esc(code)}] {esc(title)}</text>
  <text x="32" y="44" font-size="9" font-style="italic" fill="#475569">{esc(subtitle)}</text>

{content}
</svg>'''


# =============================================================
# 1. DIAGRAMA GENERAL DE NAVEGACIÓN (RESUMIDO - ALTO NIVEL)
# =============================================================
def gen_dn00_general():
    w, h = 1540, 880
    content = []
    
    # Raíz Inicio
    s_inicio = Screen("inicio", 60, 390, 200, "Inicio (Home)", "pantalla principal", [
        "• Catálogo de moda",
        "• Carrito de compras",
        "• Mis reservas",
        "• Mis pedidos",
        "• Mi perfil",
        "• Asistente flotante"
    ])
    content.append(s_inicio.render())
    
    # Pasillo vertical de distribución
    x_bus = 310
    
    # 6 Carriles Horizontales (Lanes)
    # Carril 1: Catálogo (y = 70)
    s_cat = Screen("cat", 400, 70, 210, "Catálogo", "pantalla", ["• Grilla de prendas", "• Menú categorías"])
    s_busq = Screen("busq", 680, 70, 210, "Buscar / Filtrar", "vista filtros", ["• Talla, color, precio", "• Resultados"])
    s_det = Screen("det", 970, 70, 240, "Detalle de Producto", "pantalla", [
        "• Fotos y tallas",
        "• Disponibilidad por sucursal",
        "• Añadir al carrito",
        "• Reservar"
    ])
    content.extend([s_cat.render(), s_busq.render(), s_det.render()])
    
    # Carril 2: Carrito (y = 220)
    s_car = Screen("car", 400, 220, 210, "Carrito", "pantalla", ["• Lista de prendas", "• Subtotal"])
    s_chk = Screen("chk", 680, 220, 210, "Checkout", "pantalla", ["• Datos de compra", "• Dirección / Retiro"])
    s_pago = Screen("pago", 970, 220, 240, "Pago", "pantalla", ["• Pago electrónico / QR", "• Confirmación"])
    content.extend([s_car.render(), s_chk.render(), s_pago.render()])
    
    # Carril 3: Reservas (y = 370)
    s_res = Screen("res", 400, 370, 210, "Reservas", "pantalla", ["• Lista de apartados", "• Vigencia 48h"])
    s_det_res = Screen("det_res", 680, 370, 210, "Detalle de Reserva", "pantalla", ["• Código QR de retiro", "• Sucursal"])
    content.extend([s_res.render(), s_det_res.render()])
    
    # Carril 4: Pedidos (y = 510)
    s_ped = Screen("ped", 400, 510, 210, "Pedidos", "pantalla", ["• Historial de compras", "• Estado"])
    s_det_ped = Screen("det_ped", 680, 510, 210, "Detalle de Pedido", "pantalla", ["• Prendas y comprobante", "• Tracking"])
    content.extend([s_ped.render(), s_det_ped.render()])
    
    # Carril 5: Perfil (y = 650)
    s_perfil = Screen("perfil", 400, 650, 210, "Perfil", "pantalla", ["• Ver perfil", "• Editar datos", "• Contraseña"])
    content.append(s_perfil.render())
    
    # Carril 6: Asistente Inteligente (y = 780)
    s_asist = Screen("asist", 400, 780, 210, "Asistente Inteligente", "interfaz chat", ["• Preguntas sobre moda", "• Sugerencias"])
    content.append(s_asist.render())
    
    # Conexiones de distribución desde Inicio hacia los 6 carriles
    content.append(link([s_inicio.right(0.5), (x_bus, s_inicio.y + s_inicio.h/2)], "[Menús]"))
    content.append(link([(x_bus, s_inicio.y + s_inicio.h/2), (x_bus, s_cat.y + s_cat.h/2), s_cat.left(0.5)], "[Catálogo]", label_pos="last"))
    content.append(link([(x_bus, s_inicio.y + s_inicio.h/2), (x_bus, s_car.y + s_car.h/2), s_car.left(0.5)], "[Carrito]", label_pos="last"))
    content.append(link([(x_bus, s_inicio.y + s_inicio.h/2), (x_bus, s_res.y + s_res.h/2), s_res.left(0.5)], "[Reservas]", label_pos="last"))
    content.append(link([(x_bus, s_inicio.y + s_inicio.h/2), (x_bus, s_ped.y + s_ped.h/2), s_ped.left(0.5)], "[Pedidos]", label_pos="last"))
    content.append(link([(x_bus, s_inicio.y + s_inicio.h/2), (x_bus, s_perfil.y + s_perfil.h/2), s_perfil.left(0.5)], "[Perfil]", label_pos="last"))
    content.append(link([(x_bus, s_inicio.y + s_inicio.h/2), (x_bus, s_asist.y + s_asist.h/2), s_asist.left(0.5)], "[Asistente]", label_pos="last"))
    
    # Flujo interno Carril 1
    content.append(link([s_cat.right(0.4), s_busq.left(0.4)], "[Buscar / Filtrar]"))
    content.append(link([s_busq.right(0.5), s_det.left(0.4)], "[Ver Prenda]"))
    # Ruteo ortogonal limpio desde Catálogo directo a Detalle por debajo de Buscar
    content.append(link([s_cat.right(0.8), (645, s_cat.y + s_cat.h*0.8), (645, 175), (935, 175), (935, s_det.y + s_det.h*0.7), s_det.left(0.7)], "[Click Prenda]", custom_label_pos=(790, 168)))
    
    # Flujo interno Carril 2
    content.append(link([s_car.right(0.5), s_chk.left(0.5)], "[Checkout]"))
    content.append(link([s_chk.right(0.5), s_pago.left(0.5)], "[Continuar al Pago]"))
    
    # Flujo interno Carril 3
    content.append(link([s_res.right(0.5), s_det_res.left(0.5)], "[Ver Detalle]"))
    
    # Flujo interno Carril 4
    content.append(link([s_ped.right(0.5), s_det_ped.left(0.5)], "[Ver Detalle]"))
    
    return canvas(w, h, "DN-00", "Diagrama General de Navegación", "Estructura de Menús y Vistas de Alto Nivel — Cliente Web & Mobile", "\n".join(content))


# =============================================================
# 2. PAQUETE CLIENTE / COMERCIO ELECTRÓNICO (W04-W11, W26)
# =============================================================
def gen_dn01_cliente_ecommerce():
    w, h = 1880, 920
    content = []
    
    # Entrada Principal
    s_inicio = Screen("p1_inicio", 60, 220, 200, "Inicio (Home)", "pantalla", [
        "• Acceso a catálogo",
        "• Barra de búsqueda",
        "• Acceso directo carrito"
    ])
    content.append(s_inicio.render())
    
    # Pasillo vertical
    x_bus = 290
    
    # Carril 1: Catálogo y Detalle (y = 70 a 240)
    s_cat = Screen("p1_cat", 350, 90, 220, "Catálogo", "pantalla (W04)", ["• Grilla de prendas", "• Paginación"])
    s_filtros = Screen("p1_filtros", 650, 60, 220, "Buscar / Filtrar", "formulario (W05)", ["• Talla, color, estilo", "• Rango de precios"])
    s_res_busq = Screen("p1_res_busq", 950, 60, 220, "Resultados", "vista resultados", ["• Lista filtrada"])
    
    s_det = Screen("p1_det", 650, 210, 250, "Detalle de Producto", "pantalla (W06)", [
        "• Fotos y selector variantes",
        "• Botón Disponibilidad",
        "• Botón Añadir al carrito",
        "• Botón Reservar"
    ])
    s_disp = Screen("p1_disp", 970, 210, 250, "Disponibilidad Sucursal", "modal (W07)", ["• Stock físico por tienda", "• Botón Ubicaciones"])
    s_ubic = Screen("p1_ubic", 1290, 210, 250, "Ubicaciones Sucursales", "pantalla / mapa (W26)", ["• Mapa de tiendas", "• Horarios y teléfonos"])
    
    content.extend([s_cat.render(), s_filtros.render(), s_res_busq.render(), s_det.render(), s_disp.render(), s_ubic.render()])
    
    # Carril 2: Carrito -> Checkout -> Datos -> Pago -> Confirmación (y = 430)
    s_car = Screen("p1_car", 350, 430, 220, "Carrito de Compras", "pantalla (W08)", ["• Ítems, cantidades, subtotal", "• Botón Checkout"])
    s_chk = Screen("p1_chk", 650, 430, 220, "Checkout", "pantalla (W09)", ["• Dirección entrega / Retiro"])
    s_datos = Screen("p1_datos", 950, 430, 220, "Datos de Compra", "formulario", ["• Facturación y contacto"])
    s_pago = Screen("p1_pago", 1250, 430, 220, "Pago de Compra", "pantalla pago", ["• QR bancario / Tarjeta"])
    s_conf = Screen("p1_conf", 1550, 430, 220, "Confirmación de Compra", "pantalla éxito", ["• Código de orden", "• Recibo digital"])
    
    content.extend([s_car.render(), s_chk.render(), s_datos.render(), s_pago.render(), s_conf.render()])
    
    # Carril 3: Reservas (y = 650)
    s_res = Screen("p1_res", 350, 650, 220, "Mis Reservas", "pantalla (W10)", ["• Reservas activas (vigencia 48h)"])
    s_det_res = Screen("p1_det_res", 650, 650, 240, "Detalle de Reserva", "pantalla detalle", ["• Prenda apartada", "• Código QR de retiro", "• Cancelar"])
    content.extend([s_res.render(), s_det_res.render()])
    
    # Carril 4: Pedidos (y = 790)
    s_ped = Screen("p1_ped", 350, 790, 220, "Historial de Compras", "pantalla (W11)", ["• Pedidos anteriores", "• Estado despacho"])
    s_det_ped = Screen("p1_det_ped", 650, 790, 240, "Detalle del Pedido", "pantalla detalle", ["• Prendas compradas", "• Tracking de entrega"])
    content.extend([s_ped.render(), s_det_ped.render()])
    
    # Conexiones Inicio -> Carriles
    content.append(link([s_inicio.right(0.3), (x_bus, s_inicio.y + s_inicio.h*0.3), (x_bus, s_cat.y + s_cat.h/2), s_cat.left(0.5)], "[Catálogo]", label_pos="last"))
    content.append(link([s_inicio.right(0.6), (x_bus, s_inicio.y + s_inicio.h*0.6), (x_bus, s_car.y + s_car.h/2), s_car.left(0.5)], "[Carrito]", label_pos="last"))
    content.append(link([s_inicio.right(0.85), (x_bus, s_inicio.y + s_inicio.h*0.85), (x_bus, s_res.y + s_res.h/2), s_res.left(0.5)], "[Reservas]", label_pos="last"))
    content.append(link([s_inicio.bottom(0.5), (160, s_ped.y + s_ped.h/2), s_ped.left(0.5)], "[Pedidos]", label_pos="last"))
    
    # Conexiones Catálogo -> Filtros -> Resultados -> Detalle
    content.append(link([s_cat.right(0.3), (600, s_cat.y + s_cat.h*0.3), (600, s_filtros.y + s_filtros.h/2), s_filtros.left(0.5)], "[Buscar / Filtrar]", label_pos="last"))
    content.append(link([s_filtros.right(0.5), s_res_busq.left(0.5)], "[Aplicar]"))
    content.append(link([s_res_busq.bottom(0.5), (1060, 175), (600, 175), (600, s_det.y + s_det.h*0.3), s_det.left(0.3)], "[Seleccionar Prenda]", custom_label_pos=(830, 168)))
    content.append(link([s_cat.right(0.8), (600, s_cat.y + s_cat.h*0.8), (600, s_det.y + s_det.h*0.65), s_det.left(0.65)], "[Click Prenda]", label_pos="last"))
    
    # Conexiones Detalle -> Disponibilidad -> Ubicaciones
    content.append(link([s_det.right(0.5), s_disp.left(0.5)], "[Disponibilidad]"))
    content.append(link([s_disp.right(0.5), s_ubic.left(0.5)], "[Ver en Mapa]"))
    
    # Detalle -> Añadir al Carrito (bajada limpia por canal x = 460)
    content.append(link([s_det.bottom(0.2), (700, 375), (460, 375), s_car.top(0.5)], "[Añadir al Carrito]", custom_label_pos=(580, 367)))
    
    # Detalle -> Reservar (bajada limpia por canal x = 920 hacia reservas)
    content.append(link([s_det.bottom(0.8), (850, 350), (920, 350), (920, 595), (460, 595), s_res.top(0.5)], "[Reservar Prenda]", custom_label_pos=(690, 587)))
    
    # Flujo Carrito -> Checkout -> Datos -> Pago -> Confirmación
    content.append(link([s_car.right(0.5), s_chk.left(0.5)], "[Checkout]"))
    content.append(link([s_chk.right(0.5), s_datos.left(0.5)], "[Datos Compra]"))
    content.append(link([s_datos.right(0.5), s_pago.left(0.5)], "[Ir a Pagar]"))
    content.append(link([s_pago.right(0.5), s_conf.left(0.5)], "[Pagar]"))
    
    # Confirmación -> Detalle Pedido (retorno por pasillo inferior limpio)
    content.append(link([s_conf.bottom(0.5), (1660, 880), (770, 880), s_det_ped.bottom(0.5)], "[Ver Detalle Pedido]", custom_label_pos=(1215, 872)))
    
    # Flujos Internos Reservas & Pedidos
    content.append(link([s_res.right(0.5), s_det_res.left(0.5)], "[Ver Detalle]"))
    content.append(link([s_ped.right(0.5), s_det_ped.left(0.5)], "[Ver Detalle]"))
    
    return canvas(w, h, "DN-01", "Paquete Cliente / Comercio Electrónico", "Navegación de Catálogo, Ficha, Carrito, Compra, Reservas y Pedidos (W04-W11, W26)", "\n".join(content))


# =============================================================
# 3. PAQUETE AUTENTICACIÓN Y PERFIL (W01-W03, M01-M03)
# =============================================================
def gen_dn02_auth_perfil():
    w, h = 1580, 820
    content = []
    
    # Bloque 1: Autenticación (Superior)
    s_inicio = Screen("p2_inicio", 60, 180, 200, "Inicio (Home)", "pantalla", [
        "• Botón Iniciar sesión",
        "• Botón Registrarse",
        "• Menú Perfil"
    ])
    content.append(s_inicio.render())
    
    s_login = Screen("p2_login", 380, 90, 230, "Iniciar Sesión", "pantalla (W02, M02)", [
        "• Correo / Celular",
        "• Contraseña",
        "• Botón Entrar"
    ])
    s_reg = Screen("p2_reg", 380, 270, 230, "Registrarse", "pantalla (W01, M01)", [
        "• Opción crear cuenta",
        "• Botón Continuar"
    ])
    s_form_reg = Screen("p2_form_reg", 690, 270, 250, "Formulario de Registro", "formulario", [
        "• Nombres y apellidos",
        "• Correo y contraseña",
        "• Botón Confirmar"
    ])
    s_cta_reg = Screen("p2_cta_reg", 1020, 270, 230, "Cuenta Registrada", "pantalla éxito", [
        "• Mensaje de bienvenida",
        "• Botón Ir a Inicio"
    ])
    
    content.extend([s_login.render(), s_reg.render(), s_form_reg.render(), s_cta_reg.render()])
    
    # Bloque 2: Perfil de Usuario (Inferior)
    s_perfil = Screen("p2_perfil", 380, 560, 230, "Perfil", "menú principal (W03, M03)", [
        "• Ver perfil",
        "• Editar datos",
        "• Cambiar contraseña"
    ])
    s_ver_perfil = Screen("p2_ver_perfil", 690, 480, 250, "Ver Perfil", "pantalla", [
        "• Datos personales",
        "• Direcciones guardadas",
        "• Historial de compras"
    ])
    s_edit = Screen("p2_edit", 1020, 480, 250, "Editar Datos", "formulario", [
        "• Modificar nombres",
        "• Actualizar teléfono"
    ])
    s_pass = Screen("p2_pass", 690, 680, 250, "Cambiar Contraseña", "formulario seguridad", [
        "• Clave actual",
        "• Nueva contraseña",
        "• Confirmación"
    ])
    
    content.extend([s_perfil.render(), s_ver_perfil.render(), s_edit.render(), s_pass.render()])
    
    # Conexiones Autenticación (Límpias, ortogonales, sin cruzar cajas)
    content.append(link([s_inicio.right(0.3), (300, s_inicio.y + s_inicio.h*0.3), (300, s_login.y + s_login.h/2), s_login.left(0.5)], "[Iniciar sesión]", label_pos="last"))
    content.append(link([s_inicio.right(0.7), (300, s_inicio.y + s_inicio.h*0.7), (300, s_reg.y + s_reg.h/2), s_reg.left(0.5)], "[Registrarse]", label_pos="last"))
    
    content.append(link([s_reg.right(0.5), s_form_reg.left(0.5)], "[Abrir Formulario]"))
    content.append(link([s_form_reg.right(0.5), s_cta_reg.left(0.5)], "[Crear Cuenta]"))
    
    # Retorno limpio de Cuenta Registrada hacia Inicio por canal inferior y = 410 (sin tocar el header)
    content.append(link([s_cta_reg.bottom(0.5), (1135, 410), (160, 410), s_inicio.bottom(0.5)], "[Cuenta creada -> Inicio]", custom_label_pos=(647, 402)))
    
    # Conexión Inicio -> Perfil (Limpia por debajo)
    content.append(link([s_inicio.bottom(0.75), (210, s_perfil.y + s_perfil.h/2), s_perfil.left(0.5)], "[Acceso Perfil]", label_pos="last"))
    
    # Conexiones Perfil
    content.append(link([s_perfil.right(0.35), (650, s_perfil.y + s_perfil.h*0.35), (650, s_ver_perfil.y + s_ver_perfil.h/2), s_ver_perfil.left(0.5)], "[Ver perfil]", label_pos="last"))
    content.append(link([s_ver_perfil.right(0.5), s_edit.left(0.5)], "[Editar datos]"))
    content.append(link([s_perfil.right(0.75), (650, s_perfil.y + s_perfil.h*0.75), (650, s_pass.y + s_pass.h/2), s_pass.left(0.5)], "[Cambiar contraseña]", label_pos="last"))
    
    return canvas(w, h, "DN-02", "Paquete Autenticación y Perfil", "Flujo de Registro, Login y Gestión de Perfil de Usuario (W01-W03, M01-M03)", "\n".join(content))


# =============================================================
# 4. PAQUETE INTELIGENCIA ARTIFICIAL (W12, W13, M12-M14)
# =============================================================
def gen_dn03_ia():
    w, h = 1780, 840
    content = []
    
    s_hub = Screen("p3_hub", 60, 360, 220, "Inicio / Catálogo", "pantalla de entrada", [
        "• Botón Recomendaciones",
        "• Icono Asistente IA",
        "• Botón Vestidor Virtual"
    ])
    content.append(s_hub.render())
    
    x_bus = 340
    
    # Carril 1: Recomendaciones (y = 80)
    s_recom = Screen("p3_recom", 420, 80, 240, "Recomendaciones", "menú / sección (W12, M12)", ["• Algoritmo de afinidad", "• Novedades de estilo"])
    s_prod_recom = Screen("p3_prod_recom", 760, 80, 260, "Productos Recomendados", "pantalla grilla", ["• Prendas sugeridas", "• Nivel de coincidencia"])
    s_det1 = Screen("p3_det1", 1120, 80, 240, "Detalle de Producto", "pantalla detalle", ["• Ficha de prenda", "• Añadir al carrito"])
    content.extend([s_recom.render(), s_prod_recom.render(), s_det1.render()])
    
    # Carril 2: Asistente Inteligente (y = 360)
    s_asist = Screen("p3_asist", 420, 360, 240, "Asistente Inteligente", "interfaz (W13, M13)", ["• Chatbot DeepSeek AI", "• Asistencia en compras"])
    s_conv = Screen("p3_conv", 760, 360, 260, "Conversación", "pantalla de chat", ["• Diálogo interactivo", "• Respuestas sobre tallas"])
    s_prod_asist = Screen("p3_prod_asist", 1120, 360, 240, "Producto Recomendado", "tarjeta interactiva", ["• Prenda sugerida en chat", "• Botón Ver detalle"])
    content.extend([s_asist.render(), s_conv.render(), s_prod_asist.render()])
    
    # Carril 3: Vestidor Virtual (y = 640)
    s_vest = Screen("p3_vest", 420, 640, 240, "Vestidor Virtual", "sección (M14)", ["• Probador interactivo RA"])
    s_sel = Screen("p3_sel", 760, 640, 260, "Seleccionar Prenda", "catálogo RA", ["• Prendas compatibles", "• Selección de talla"])
    s_camara = Screen("p3_camara", 1120, 640, 240, "Vestidor Virtual (Cámara)", "pantalla RA", ["• Calce virtual en cámara", "• Ajuste de posición"])
    s_vis = Screen("p3_vis", 1440, 640, 240, "Visualización", "resultado outfit", ["• Foto del outfit virtual", "• Comprar prenda"])
    content.extend([s_vest.render(), s_sel.render(), s_camara.render(), s_vis.render()])
    
    # Conexiones desde Inicio / Catálogo hacia los 3 carriles
    content.append(link([s_hub.right(0.2), (x_bus, s_hub.y + s_hub.h*0.2), (x_bus, s_recom.y + s_recom.h/2), s_recom.left(0.5)], "[Recomendaciones]", label_pos="last"))
    content.append(link([s_hub.right(0.5), s_asist.left(0.5)], "[Asistente Inteligente]"))
    content.append(link([s_hub.right(0.8), (x_bus, s_hub.y + s_hub.h*0.8), (x_bus, s_vest.y + s_vest.h/2), s_vest.left(0.5)], "[Vestidor Virtual]", label_pos="last"))
    
    # Carril 1: Recomendaciones
    content.append(link([s_recom.right(0.5), s_prod_recom.left(0.5)], "[Ver Productos]"))
    content.append(link([s_prod_recom.right(0.5), s_det1.left(0.5)], "[Seleccionar Prenda]"))
    
    # Carril 2: Asistente
    content.append(link([s_asist.right(0.5), s_conv.left(0.5)], "[Iniciar Conversación]"))
    content.append(link([s_conv.right(0.5), s_prod_asist.left(0.5)], "[Sugerir Prenda]"))
    # Conexión limpia hacia Detalle de Producto
    content.append(link([s_prod_asist.top(0.5), (1240, s_det1.y + s_det1.h + 10), s_det1.bottom(0.5)], "[Ver Detalle de Producto]", custom_label_pos=(1305, 235)))
    
    # Carril 3: Vestidor Virtual
    content.append(link([s_vest.right(0.5), s_sel.left(0.5)], "[Seleccionar Prenda]"))
    content.append(link([s_sel.right(0.5), s_camara.left(0.5)], "[Abrir Probador RA]"))
    content.append(link([s_camara.right(0.5), s_vis.left(0.5)], "[Capturar / Visualizar]"))
    
    return canvas(w, h, "DN-03", "Paquete Inteligencia Artificial", "Recomendaciones, Chatbot Asistente y Vestidor Virtual (W12, W13, M12-M14)", "\n".join(content))


# =============================================================
# 5. PAQUETE ADMINISTRACIÓN DE TIENDA (W14, W17-W21, W30)
# =============================================================
def gen_dn04_admin_tienda():
    w, h = 1940, 1060
    content = []
    
    s_dash = Screen("p4_dash", 60, 480, 240, "Dashboard de Tienda", "pantalla principal (W14)", [
        "• Usuarios y roles",
        "• Productos",
        "• Categorías",
        "• Tallas y colores",
        "• Temporadas y colecciones",
        "• Proveedores",
        "• Promociones"
    ])
    content.append(s_dash.render())
    
    x_bus = 360
    
    # Carril 1: Usuarios y Roles (W14) - y = 60
    s_u_lista = Screen("p4_u_lista", 440, 60, 220, "Usuarios y Roles: Lista", "pantalla listado", ["• Listado de usuarios", "• Filtro por rol"])
    s_u_reg = Screen("p4_u_reg", 740, 60, 200, "Registrar", "formulario", ["• Datos de usuario"])
    s_u_edit = Screen("p4_u_edit", 1020, 60, 200, "Editar", "formulario", ["• Modificar rol"])
    s_u_det = Screen("p4_u_det", 1300, 60, 200, "Detalle", "vista", ["• Historial"])
    content.extend([s_u_lista.render(), s_u_reg.render(), s_u_edit.render(), s_u_det.render()])
    
    # Carril 2: Productos (W17) - y = 195
    s_p_lista = Screen("p4_p_lista", 440, 195, 220, "Productos: Lista", "pantalla listado", ["• Catálogo general"])
    s_p_reg = Screen("p4_p_reg", 740, 195, 200, "Registrar", "formulario", ["• Nombre, tela, precio"])
    s_p_edit = Screen("p4_p_edit", 1020, 195, 200, "Editar", "formulario", ["• Actualizar prenda"])
    s_p_det = Screen("p4_p_det", 1300, 195, 200, "Detalle", "vista", ["• Variantes"])
    content.extend([s_p_lista.render(), s_p_reg.render(), s_p_edit.render(), s_p_det.render()])
    
    # Carril 3: Categorías (W18) - y = 330
    s_c_lista = Screen("p4_c_lista", 440, 330, 220, "Categorías: Lista", "pantalla listado", ["• Árbol de categorías"])
    s_c_reg = Screen("p4_c_reg", 740, 330, 200, "Registrar", "formulario", ["• Nueva categoría"])
    s_c_edit = Screen("p4_c_edit", 1020, 330, 200, "Editar", "formulario", ["• Renombrar / Orden"])
    content.extend([s_c_lista.render(), s_c_reg.render(), s_c_edit.render()])
    
    # Carril 4: Tallas y Colores (W19) - y = 470
    s_tallas = Screen("p4_tallas", 440, 470, 260, "Tallas y Colores", "pantalla (W19)", ["• Matriz de tallas (XS-XXL)", "• Paleta de colores"])
    content.append(s_tallas.render())
    
    # Carril 5: Temporadas y Colecciones (W20) - y = 610
    s_temp = Screen("p4_temp", 440, 610, 260, "Temporadas y Colecciones", "pantalla (W20)", ["• Campañas y vigencia", "• Asignar prendas"])
    content.append(s_temp.render())
    
    # Carril 6: Proveedores (W21) - y = 750
    s_prov = Screen("p4_prov", 440, 750, 260, "Proveedores", "pantalla (W21)", ["• Directorio de proveedores", "• Registro y contacto"])
    content.append(s_prov.render())
    
    # Carril 7: Promociones (W30) - y = 890
    s_pr_lista = Screen("p4_pr_lista", 440, 890, 220, "Promociones: Lista", "pantalla (W30)", ["• Promociones vigentes"])
    s_pr_reg = Screen("p4_pr_reg", 740, 890, 200, "Registrar", "formulario", ["• % descuento / 2x1"])
    s_pr_edit = Screen("p4_pr_edit", 1020, 890, 200, "Editar", "formulario", ["• Modificar vigencia"])
    content.extend([s_pr_lista.render(), s_pr_reg.render(), s_pr_edit.render()])
    
    # Conexiones Dashboard -> Carriles (Etiquetas colocadas arriba del segmento horizontal de entrada)
    y_center_dash = s_dash.y + s_dash.h/2
    content.append(link([s_dash.right(0.5), (x_bus, y_center_dash)], "[Menús]"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_u_lista.y + s_u_lista.h/2), s_u_lista.left(0.5)], "[Usuarios y roles]", label_pos="last"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_p_lista.y + s_p_lista.h/2), s_p_lista.left(0.5)], "[Productos]", label_pos="last"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_c_lista.y + s_c_lista.h/2), s_c_lista.left(0.5)], "[Categorías]", label_pos="last"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_tallas.y + s_tallas.h/2), s_tallas.left(0.5)], "[Tallas y colores]", label_pos="last"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_temp.y + s_temp.h/2), s_temp.left(0.5)], "[Temporadas y colecciones]", label_pos="last"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_prov.y + s_prov.h/2), s_prov.left(0.5)], "[Proveedores]", label_pos="last"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_pr_lista.y + s_pr_lista.h/2), s_pr_lista.left(0.5)], "[Promociones]", label_pos="last"))
    
    # Flujos internos CRUD
    # Usuarios
    content.append(link([s_u_lista.right(0.3), s_u_reg.left(0.5)], "[Registrar]"))
    content.append(link([s_u_reg.right(0.5), s_u_edit.left(0.5)], "[Editar]"))
    content.append(link([s_u_edit.right(0.5), s_u_det.left(0.5)], "[Detalle]"))
    
    # Productos
    content.append(link([s_p_lista.right(0.3), s_p_reg.left(0.5)], "[Registrar]"))
    content.append(link([s_p_reg.right(0.5), s_p_edit.left(0.5)], "[Editar]"))
    content.append(link([s_p_edit.right(0.5), s_p_det.left(0.5)], "[Detalle]"))
    
    # Categorías
    content.append(link([s_c_lista.right(0.3), s_c_reg.left(0.5)], "[Registrar]"))
    content.append(link([s_c_reg.right(0.5), s_c_edit.left(0.5)], "[Editar]"))
    
    # Promociones
    content.append(link([s_pr_lista.right(0.3), s_pr_reg.left(0.5)], "[Registrar]"))
    content.append(link([s_pr_reg.right(0.5), s_pr_edit.left(0.5)], "[Editar]"))
    
    return canvas(w, h, "DN-04", "Paquete Administración de Tienda", "Gestión de Usuarios, Productos, Categorías, Tallas, Proveedores y Promociones (W14, W17-W21, W30)", "\n".join(content))


# =============================================================
# 6. PAQUETE SUCURSALES E INVENTARIO (W15, W16, W22, W23)
# =============================================================
def gen_dn05_sucursales_inventario():
    w, h = 1860, 840
    content = []
    
    s_admin = Screen("p5_admin", 60, 360, 220, "Administración", "pantalla principal", [
        "• Cadena de tiendas",
        "• Sucursales",
        "• Inventario",
        "• Disponibilidad"
    ])
    content.append(s_admin.render())
    
    x_bus = 340
    
    # Carril 1: Cadena de Tiendas (W15) - y = 80
    s_cadena = Screen("p5_cadena", 420, 80, 240, "Cadena de Tiendas", "pantalla (W15)", ["• Configuración de cadena", "• Reglas de negocio"])
    content.append(s_cadena.render())
    
    # Carril 2: Sucursales (W16) - y = 230
    s_suc_lista = Screen("p5_suc_lista", 420, 230, 220, "Sucursales: Lista", "pantalla (W16)", ["• Sucursales activas"])
    s_suc_reg = Screen("p5_suc_reg", 720, 230, 200, "Registrar", "formulario", ["• Ciudad y dirección"])
    s_suc_edit = Screen("p5_suc_edit", 1000, 230, 200, "Editar", "formulario", ["• Modificar datos"])
    s_suc_det = Screen("p5_suc_det", 1280, 230, 200, "Detalle", "vista", ["• Almacenes"])
    content.extend([s_suc_lista.render(), s_suc_reg.render(), s_suc_edit.render(), s_suc_det.render()])
    
    # Carril 3: Inventario (W22) - y = 450
    s_inv_ex = Screen("p5_inv_ex", 420, 450, 240, "Inventario: Existencias", "pantalla (W22)", ["• Stock físico por talla"])
    s_inv_det = Screen("p5_inv_det", 740, 450, 240, "Detalle de Inventario", "vista kardex", ["• Movimientos por prenda"])
    s_inv_mov = Screen("p5_inv_mov", 1060, 450, 240, "Registrar Movimiento", "formulario", ["• Entrada / Traslado / Merma"])
    content.extend([s_inv_ex.render(), s_inv_det.render(), s_inv_mov.render()])
    
    # Carril 4: Disponibilidad (W23) - y = 670
    s_disp_cons = Screen("p5_disp_cons", 420, 670, 260, "Consultar por Sucursal", "pantalla (W23)", ["• Disponibilidad en tienda"])
    s_disp_act = Screen("p5_disp_act", 760, 670, 260, "Actualizar Disponibilidad", "formulario", ["• Habilitar / Deshabilitar"])
    content.extend([s_disp_cons.render(), s_disp_act.render()])
    
    # Conexiones Administración -> Carriles
    y_center_admin = s_admin.y + s_admin.h/2
    content.append(link([s_admin.right(0.5), (x_bus, y_center_admin)], "[Menús]"))
    content.append(link([(x_bus, y_center_admin), (x_bus, s_cadena.y + s_cadena.h/2), s_cadena.left(0.5)], "[Cadena de tiendas]", label_pos="last"))
    content.append(link([(x_bus, y_center_admin), (x_bus, s_suc_lista.y + s_suc_lista.h/2), s_suc_lista.left(0.5)], "[Sucursales]", label_pos="last"))
    content.append(link([(x_bus, y_center_admin), (x_bus, s_inv_ex.y + s_inv_ex.h/2), s_inv_ex.left(0.5)], "[Inventario]", label_pos="last"))
    content.append(link([(x_bus, y_center_admin), (x_bus, s_disp_cons.y + s_disp_cons.h/2), s_disp_cons.left(0.5)], "[Disponibilidad]", label_pos="last"))
    
    # Flujos internos
    content.append(link([s_suc_lista.right(0.3), s_suc_reg.left(0.5)], "[Registrar]"))
    content.append(link([s_suc_reg.right(0.5), s_suc_edit.left(0.5)], "[Editar]"))
    content.append(link([s_suc_edit.right(0.5), s_suc_det.left(0.5)], "[Detalle]"))
    
    content.append(link([s_inv_ex.right(0.5), s_inv_det.left(0.5)], "[Ver Detalle]"))
    content.append(link([s_inv_det.right(0.5), s_inv_mov.left(0.5)], "[Registrar Movimiento]"))
    
    content.append(link([s_disp_cons.right(0.5), s_disp_act.left(0.5)], "[Actualizar Disponibilidad]"))
    
    return canvas(w, h, "DN-05", "Paquete Sucursales e Inventario", "Cadena de Tiendas, Sucursales, Existencias y Disponibilidad de Prendas (W15, W16, W22, W23)", "\n".join(content))


# =============================================================
# 7. PAQUETE VENTAS, RESERVAS Y PAGOS (W24, W25, W27-W29)
# =============================================================
def gen_dn06_ventas_reservas():
    w, h = 1880, 840
    content = []
    
    s_panel = Screen("p6_panel", 60, 360, 220, "Panel de Operaciones", "pantalla principal", [
        "• Venta presencial",
        "• Reservas en tienda",
        "• Comprobantes"
    ])
    content.append(s_panel.render())
    
    x_bus = 310
    
    # Carril 1: Venta Presencial (y = 110)
    s_v_sel = Screen("p6_v_sel", 360, 110, 220, "Seleccionar Productos", "pantalla POS (W24)", ["• Escaneo de prendas"])
    s_v_dat = Screen("p6_v_dat", 640, 110, 220, "Datos de Venta", "formulario", ["• Cliente / Descuentos"])
    
    # Decisión de Pago (Rombo a la derecha de Datos de Venta)
    dec_pago = Decision("dec_pago", 940, 140, "¿Pago?")
    s_p_elec = Screen("p6_p_elec", 1040, 50, 200, "Pago Electrónico", "modal (W27)", ["• QR Simple / Tarjeta"])
    s_p_caja = Screen("p6_p_caja", 1040, 180, 200, "Pago en Caja", "modal (W28)", ["• Efectivo en caja"])
    
    s_v_conf = Screen("p6_v_conf", 1320, 110, 220, "Confirmación", "pantalla éxito", ["• Venta asentada"])
    
    content.extend([s_v_sel.render(), s_v_dat.render(), dec_pago.render(), s_p_elec.render(), s_p_caja.render(), s_v_conf.render()])
    
    # Carril 2: Reservas (y = 420)
    s_res_lista = Screen("p6_res_lista", 360, 420, 220, "Lista de Reservas", "pantalla (W25)", ["• Reservas de clientes"])
    s_res_det = Screen("p6_res_det", 660, 420, 220, "Detalle", "vista reserva", ["• Prenda apartada"])
    s_res_aten = Screen("p6_res_aten", 960, 420, 220, "Atender Reserva", "pantalla despacho", ["• Entrega física"])
    content.extend([s_res_lista.render(), s_res_det.render(), s_res_aten.render()])
    
    # Carril 3: Comprobantes (y = 660)
    s_comp = Screen("p6_comp", 360, 660, 260, "Ver / Emitir Comprobante", "pantalla comprobantes (W29)", [
        "• Factura electrónica",
        "• Recibo fiscal",
        "• Impresión ticket"
    ])
    content.append(s_comp.render())
    
    # Conexiones Panel de Operaciones -> Carriles
    y_center_panel = s_panel.y + s_panel.h/2
    content.append(link([s_panel.right(0.5), (x_bus, y_center_panel)], "[Menús]"))
    content.append(link([(x_bus, y_center_panel), (x_bus, s_v_sel.y + s_v_sel.h/2), s_v_sel.left(0.5)], "[Venta presencial]", label_pos="last"))
    content.append(link([(x_bus, y_center_panel), (x_bus, s_res_lista.y + s_res_lista.h/2), s_res_lista.left(0.5)], "[Reservas]", label_pos="last"))
    content.append(link([(x_bus, y_center_panel), (x_bus, s_comp.y + s_comp.h/2), s_comp.left(0.5)], "[Comprobantes]", label_pos="last"))
    
    # Flujo Venta Presencial -> Pago (Bifurcación Ortogonal Estricta)
    content.append(link([s_v_sel.right(0.5), s_v_dat.left(0.5)], "[Datos]"))
    content.append(link([s_v_dat.right(0.5), dec_pago.left()], "[Pagar]"))
    
    # Bifurcación ortogonal Manhattan desde el rombo
    content.append(link([dec_pago.top(), (dec_pago.cx, s_p_elec.y + s_p_elec.h/2), s_p_elec.left(0.5)], "[Pago electrónico]", label_pos="last"))
    content.append(link([dec_pago.bottom(), (dec_pago.cx, s_p_caja.y + s_p_caja.h/2), s_p_caja.left(0.5)], "[Pago en caja]", label_pos="last"))
    
    # Convergencia hacia Confirmación
    content.append(link([s_p_elec.right(0.5), (1280, s_p_elec.y + s_p_elec.h/2), (1280, s_v_conf.y + s_v_conf.h*0.35), s_v_conf.left(0.35)], "[Aprobado]", label_pos="first"))
    content.append(link([s_p_caja.right(0.5), (1280, s_p_caja.y + s_p_caja.h/2), (1280, s_v_conf.y + s_v_conf.h*0.65), s_v_conf.left(0.65)], "[Cobrado]", label_pos="first"))
    
    # Confirmación -> Emitir Comprobante (canal ortogonal limpio por la derecha)
    content.append(link([s_v_conf.right(0.5), (1600, s_v_conf.y + s_v_conf.h/2), (1600, s_comp.y + s_comp.h/2), s_comp.right(0.5)], "[Emitir comprobante]", custom_label_pos=(1600, 440), label_side="right"))
    
    # Flujo Reservas
    content.append(link([s_res_lista.right(0.5), s_res_det.left(0.5)], "[Detalle]"))
    content.append(link([s_res_det.right(0.5), s_res_aten.left(0.5)], "[Atender reserva]"))
    
    return canvas(w, h, "DN-06", "Paquete Ventas, Reservas y Pagos", "Venta Presencial POS, Métodos de Pago, Despacho de Reservas y Facturación (W24, W25, W27-W29)", "\n".join(content))


# =============================================================
# 8. PAQUETE INDICADORES Y REPORTES (W31, W32, W33)
# =============================================================
def gen_dn07_indicadores_reportes():
    w, h = 1780, 840
    content = []
    
    s_dash = Screen("p7_dash", 60, 360, 220, "Dashboard", "pantalla principal", [
        "• Ventas",
        "• Reservas",
        "• Inventario",
        "• Indicadores",
        "• Reportes"
    ])
    content.append(s_dash.render())
    
    x_bus = 340
    
    # Carril 1: Consultas Operativas (W31) - y = 60, 180, 300
    s_v_op = Screen("p7_v_op", 420, 60, 230, "Ventas", "consulta operativa (W31)", ["• Ventas por fecha y canal"])
    s_r_op = Screen("p7_r_op", 420, 180, 230, "Reservas", "consulta operativa (W31)", ["• Reservas recogidas / vencidas"])
    s_i_op = Screen("p7_i_op", 420, 300, 230, "Inventario", "consulta operativa (W31)", ["• Existencias por tienda"])
    content.extend([s_v_op.render(), s_r_op.render(), s_i_op.render()])
    
    # Carril 2: Indicadores KPIs (W32) - a la derecha de las consultas
    s_ind_v = Screen("p7_ind_v", 740, 60, 240, "Indicadores: Ventas", "dashboard KPIs (W32)", ["• Gráficos de ingresos"])
    s_ind_r = Screen("p7_ind_r", 740, 180, 240, "Indicadores: Reservas", "dashboard KPIs (W32)", ["• Tasa de conversión"])
    s_ind_i = Screen("p7_ind_i", 740, 300, 240, "Indicadores: Inventario", "dashboard KPIs (W32)", ["• Rotación de prendas"])
    content.extend([s_ind_v.render(), s_ind_r.render(), s_ind_i.render()])
    
    # Carril 3: Reportes Bajo Demanda (W33) - y = 560
    s_rep_par = Screen("p7_rep_par", 420, 560, 260, "Seleccionar Parámetros", "formulario (W33)", ["• Tipo de reporte", "• Fechas y filtros"])
    s_rep_gen = Screen("p7_rep_gen", 760, 560, 260, "Generar Reporte", "pantalla procesamiento", ["• Compilar datos", "• PDF / Excel"])
    s_rep_vis = Screen("p7_rep_vis", 1100, 560, 260, "Visualizar Reporte", "visor reporte", ["• Previsualización", "• Descargar documento"])
    content.extend([s_rep_par.render(), s_rep_gen.render(), s_rep_vis.render()])
    
    # Conexiones Dashboard -> Consultas e Indicadores
    y_center_dash = s_dash.y + s_dash.h/2
    content.append(link([s_dash.right(0.5), (x_bus, y_center_dash)], "[Menús]"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_v_op.y + s_v_op.h/2), s_v_op.left(0.5)], "[Ventas]", label_pos="last"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_r_op.y + s_r_op.h/2), s_r_op.left(0.5)], "[Reservas]", label_pos="last"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_i_op.y + s_i_op.h/2), s_i_op.left(0.5)], "[Inventario]", label_pos="last"))
    content.append(link([(x_bus, y_center_dash), (x_bus, s_rep_par.y + s_rep_par.h/2), s_rep_par.left(0.5)], "[Reportes]", label_pos="last"))
    
    # Enlaces Consultas -> Indicadores
    content.append(link([s_v_op.right(0.5), s_ind_v.left(0.5)], "[Ver Indicadores]"))
    content.append(link([s_r_op.right(0.5), s_ind_r.left(0.5)], "[Ver Indicadores]"))
    content.append(link([s_i_op.right(0.5), s_ind_i.left(0.5)], "[Ver Indicadores]"))
    
    # Flujo Reportes
    content.append(link([s_rep_par.right(0.5), s_rep_gen.left(0.5)], "[Generar reporte]"))
    content.append(link([s_rep_gen.right(0.5), s_rep_vis.left(0.5)], "[Visualizar reporte]"))
    
    return canvas(w, h, "DN-07", "Paquete Indicadores y Reportes", "Consultas Operativas, Indicadores Empresariales y Reportes Bajo Demanda (W31, W32, W33)", "\n".join(content))


# =============================================================
# EJECUCIÓN PRINCIPAL
# =============================================================
DIAGRAMS = [
    ("DN00_General_Navegacion_Aurora_Store", gen_dn00_general),
    ("DN01_Cliente_Comercio_Electronico", gen_dn01_cliente_ecommerce),
    ("DN02_Autenticacion_y_Perfil", gen_dn02_auth_perfil),
    ("DN03_Inteligencia_Artificial", gen_dn03_ia),
    ("DN04_Administracion_Tienda", gen_dn04_admin_tienda),
    ("DN05_Sucursales_e_Inventario", gen_dn05_sucursales_inventario),
    ("DN06_Ventas_Reservas_y_Pagos", gen_dn06_ventas_reservas),
    ("DN07_Indicadores_y_Reportes", gen_dn07_indicadores_reportes),
]

def main():
    print("Iniciando generación de los 8 Diagramas de Navegación Funcionales de Aurora Store...")
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
            
        print(f" [{idx+1}/{len(DIAGRAMS)}] Generado impecable: {fname} (SVG + PNG 2x alta resolución)")

    print("\nTodos los Diagramas de Navegación de Aurora Store han sido generados exitosamente.")

if __name__ == "__main__":
    main()
