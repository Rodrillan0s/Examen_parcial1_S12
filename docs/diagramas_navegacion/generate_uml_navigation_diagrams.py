#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Diagramas de Navegación UML Estándar (Ingeniería de Software)
Aura Store - Sistema E-Commerce & Retail Multi-Tenant
Genera:
- DN00: Mapa Maestro de Navegación del Sistema Aura
- DN01: Subsistema Navegación Cliente (Web E-Commerce & App Móvil)
- DN02: Subsistema Navegación Operativa de Sucursal (POS, Caja y Despacho)
- DN03: Subsistema Navegación Administrativa & Business Intelligence
"""

import os
import re
import resvg_py

OUT_DIR = r"d:\Locked Files --EY\Projectos\Examen_parcial1_S12\docs\diagramas_navegacion"
BRAIN_DIR = r"C:\Users\eddym\.gemini\antigravity-ide\brain\bce20c4d-ff88-4ad8-93ad-540bb85f5c37"


# -------------------------------------------------------------
# MOTOR DE RENDERIZADO Y MODELADO GEOMÉTRICO UML
# -------------------------------------------------------------

class UmlBox:
    """Representa una pantalla, modal o vista UML con cálculo dimensional exacto."""
    def __init__(self, id_name, x, y, w, stereotype, title, items=None, min_h=None):
        self.id = id_name
        self.x = x
        self.y = y
        self.w = w
        self.stereotype = stereotype
        self.title = title
        self.items = items or []
        
        self.h_header = 32 if stereotype else 26
        num_items = len(self.items)
        calc_h = self.h_header + 16 + num_items * 15 + 8
        self.h = max(min_h if min_h else 0, calc_h)

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
        lines.append(f'<rect x="{self.x}" y="{self.y}" width="{self.w}" height="{self.h}" rx="6" ry="6" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>')
        lines.append(f'<line x1="{self.x}" y1="{self.y + self.h_header}" x2="{self.x + self.w}" y2="{self.y + self.h_header}" stroke="#000000" stroke-width="1.1"/>')
        
        if self.stereotype:
            lines.append(f'<text x="{self.x + self.w/2}" y="{self.y + 13}" font-size="9" font-style="italic" fill="#222222" text-anchor="middle">«{self.stereotype}»</text>')
            lines.append(f'<text x="{self.x + self.w/2}" y="{self.y + 26}" font-size="11" font-weight="bold" fill="#000000" text-anchor="middle">{self.title}</text>')
        else:
            lines.append(f'<text x="{self.x + self.w/2}" y="{self.y + 17}" font-size="11" font-weight="bold" fill="#000000" text-anchor="middle">{self.title}</text>')
            
        y_item = self.y + self.h_header + 16
        for it in self.items:
            escaped = it.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            lines.append(f'<text x="{self.x + 10}" y="{y_item}" font-size="9.5" fill="#222222">{escaped}</text>')
            y_item += 15
            
        return "\n  ".join(lines)


class UmlSubsystem:
    """Caja de subsistema/módulo de navegación UML compuesto."""
    def __init__(self, id_name, x, y, w, h, code, title, cu_list=None):
        self.id = id_name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.code = code
        self.title = title
        self.cu_list = cu_list or []

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
        lines.append(f'<rect x="{self.x}" y="{self.y}" width="{self.w}" height="{self.h}" rx="5" ry="5" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>')
        lines.append(f'<g transform="translate({self.x + self.w - 26}, {self.y + 7})">'
                     f'<rect x="0" y="0" width="18" height="13" fill="#ffffff" stroke="#000000" stroke-width="1"/>'
                     f'<line x1="0" y1="4.5" x2="18" y2="4.5" stroke="#000000" stroke-width="0.8"/>'
                     f'<circle cx="5" cy="8.5" r="1.5" fill="#000000"/><circle cx="13" cy="8.5" r="1.5" fill="#000000"/>'
                     f'</g>')
        lines.append(f'<text x="{self.x + 12}" y="{self.y + 16}" font-size="9" font-style="italic" fill="#333333">«subsystem navigation»</text>')
        lines.append(f'<text x="{self.x + 12}" y="{self.y + 32}" font-size="12" font-weight="bold" fill="#000000">{self.code}: {self.title}</text>')
        lines.append(f'<line x1="{self.x}" y1="{self.y + 40}" x2="{self.x + self.w}" y2="{self.y + 40}" stroke="#000000" stroke-width="1"/>')
        
        y_t = self.y + 57
        for cu in self.cu_list:
            lines.append(f'<text x="{self.x + 12}" y="{y_t}" font-size="9.5" fill="#222222">• {cu}</text>')
            y_t += 15
        return "\n  ".join(lines)


def uml_decision_diamond(cx, cy, size=26, label=""):
    """Rombo de decisión UML estándar (pseudoestado de elección)."""
    s = size / 2
    points = f"{cx},{cy-s} {cx+s},{cy} {cx},{cy+s} {cx-s},{cy}"
    res = f'<polygon points="{points}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>'
    if label:
        res += f'\n  {uml_label(cx, cy - s - 8, label, font_size=9.5, font_weight="bold", anchor="middle")}'
    return res


def uml_label(x, y, text, font_size=9, font_weight="normal", anchor="middle"):
    """Genera texto con halo blanco perimétrico (técnica CAD) para 0 colisiones de líneas."""
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    halo = f'<text x="{x}" y="{y}" font-size="{font_size}" font-weight="{font_weight}" fill="none" stroke="#ffffff" stroke-width="5" stroke-linejoin="round" stroke-linecap="round" text-anchor="{anchor}">{escaped}</text>'
    front = f'<text x="{x}" y="{y}" font-size="{font_size}" font-weight="{font_weight}" fill="#000000" text-anchor="{anchor}">{escaped}</text>'
    return f"{halo}\n  {front}"


def uml_header_frame(width, height, title_code, title_name):
    """Genera marco UML estándar con pestaña proporcionada y sin invasión."""
    title_full = f"stm [{title_code}] {title_name}"
    tab_w = max(420, min(560, len(title_full) * 8 + 40))
    lines = []
    lines.append(f'<rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>')
    lines.append(f'<path d="M 15 15 L {tab_w} 15 L {tab_w + 14} 32 L {tab_w + 14} 42 L 15 42 Z" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>')
    lines.append(f'<text x="25" y="31" font-size="11.5" font-weight="bold" fill="#000000">{title_full}</text>')
    return "\n  ".join(lines)


# =============================================================
# 1. DN00: MAPA GENERAL DE NAVEGACIÓN (MAESTRO / HUB)
# =============================================================
def generate_dn00_svg():
    width = 1460
    height = 920

    portal = UmlBox("portal", 130, 105, 210, "screen", "Portal_Inicio_Screen", [
        "do / verificar_sesion_activa()",
        "[sin_sesion] -> Redirigir a Login",
        "[sesion_activa] -> Restaurar token"
    ])

    login = UmlBox("login", 460, 95, 250, "screen", "Login_Autenticacion_Screen", [
        "entry / limpiar_formulario()",
        "[click_iniciar] / enviar_credenciales()",
        "[click_crear_cuenta] -> Registro",
        "[click_olvido_pass] -> Recuperar",
        "[modo_invitado] -> Explorar Catálogo"
    ])

    registro = UmlBox("registro", 830, 85, 220, "screen", "Registro_Cliente_Screen", [
        "[click_registrarse] / validar_datos()",
        "[cuenta_creada] -> Redirigir a Login"
    ])

    recuperar = UmlBox("recuperar", 830, 175, 220, "modal", "Recuperar_Password_Modal", [
        "[ingresar_email] / enviar_token()",
        "[cerrar] -> volver a Login"
    ])

    sub_cliente = UmlSubsystem("sub_cli", 65, 390, 390, 250, "DN01", "Subsistema Cliente: E-Commerce & Móvil", [
        "Catálogo, Filtros y Búsqueda (CU05)",
        "Recomendaciones de Productos (CU/W12, CU/M12)",
        "Asistente Inteligente Chat (CU/W13, CU/M13)",
        "Detalle de Prenda y Variantes (CU06)",
        "Vestidor Virtual RA (CU/M14)",
        "Disponibilidad en Sucursales y Mapa (CU07, CU26)",
        "Carrito de Compras y Reservas (CU08, CU10)",
        "Checkout y Pago Digital QR/Tarjeta (CU09, CU_W27)",
        "Historial de Pedidos (CU11)"
    ])

    sub_pos = UmlSubsystem("sub_pos", 525, 390, 390, 250, "DN02", "Subsistema Operativo: Sucursal & POS", [
        "Apertura de Caja y Turno Operativo",
        "Terminal Punto de Venta POS (CU_W24)",
        "Atención y Despacho de Reservas (CU_W25)",
        "Módulo de Cobro en Caja Efectivo/QR (CU_W28)",
        "Emisión Factura / Recibo Fiscal (CU_W29)",
        "Gestión de Inventario de Sucursal (CU_W22)",
        "Cierre de Caja y Arqueo Diario"
    ])

    sub_admin = UmlSubsystem("sub_admin", 985, 390, 410, 250, "DN03", "Subsistema Backoffice: Administración & BI", [
        "Dashboard Ejecutivo de KPIs y Analítica (CU_W32)",
        "Gestión de Promociones y Descuentos (CU_W30)",
        "Consulta de Ventas, Reservas e Inventario (CU_W31)",
        "Generación de Reportes Bajo Demanda (CU_W33)",
        "Temporadas, Colecciones y Proveedores (CU_W20, W21)",
        "Gestión de Disponibilidad de Prendas (CU_W23)",
        "Auditoría y Bitácora del Sistema"
    ])

    sesion_cerrada = UmlBox("sesion_cerrada", 600, 755, 240, "", "Sesion_Cerrada", [
        "do / purgar_tokens_locales()",
        "do / redirigir_login()"
    ])

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#000000"/>
    </marker>
  </defs>

  <!-- Marco Exterior -->
  {uml_header_frame(width, height, "General", "DN00: Mapa Maestro de Navegación del Sistema Aura")}

  <!-- Estado Inicial -->
  <circle cx="60" cy="150" r="9" fill="#000000"/>
  <text x="60" y="175" font-size="9.5" font-weight="bold" text-anchor="middle">Inicio</text>
  <line x1="69" y1="150" x2="{portal.left()[0]}" y2="150" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(99, 142, "[iniciar app]", font_size=8.5, anchor="middle")}

  <!-- Pantallas Superiores -->
  {portal.render()}
  {login.render()}
  {registro.render()}
  {recuperar.render()}

  <!-- Transición Portal -> Login -->
  <line x1="{portal.right()[0]}" y1="{portal.right()[1]}" x2="{login.left()[0]}" y2="{portal.right()[1]}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(400, portal.right()[1] - 8, "[sin sesion activa]", font_size=8.5, anchor="middle")}

  <!-- Login <-> Registro -->
  <line x1="{login.right()[0]}" y1="115" x2="{registro.left()[0]}" y2="115" stroke="#000000" stroke-width="1.2" marker-end="url(#arrow)"/>
  {uml_label(770, 107, "[nuevo cliente]", font_size=8.5, anchor="middle")}

  <line x1="{registro.left()[0]}" y1="135" x2="{login.right()[0]}" y2="135" stroke="#000000" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
  {uml_label(770, 147, "[cuenta creada]", font_size=8.5, anchor="middle")}

  <!-- Login <-> Recuperar Password -->
  <line x1="{login.right()[0]}" y1="195" x2="{recuperar.left()[0]}" y2="195" stroke="#000000" stroke-width="1.2" marker-end="url(#arrow)"/>
  {uml_label(770, 187, "[olvidó pass]", font_size=8.5, anchor="middle")}

  <line x1="{recuperar.left()[0]}" y1="215" x2="{login.right()[0]}" y2="215" stroke="#000000" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
  {uml_label(770, 227, "[cerrar / volver]", font_size=8.5, anchor="middle")}

  <!-- Login -> Rombo de Decisión de Roles -->
  <line x1="585" y1="{login.bottom()[1]}" x2="585" y2="285" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(595, 260, "[autenticacion_exitosa / decodificar_JWT(rol)]", font_size=9, font_weight="bold", anchor="start")}

  <!-- Rombo de Decisión -->
  {uml_decision_diamond(585, 305, size=28, label="")}

  <!-- 3 Ramas de Roles hacia los Subsistemas -->
  <!-- 1. Rol CLIENTE (Izquierda) -->
  <path d="M 571 305 L 260 305 L 260 390" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(400, 297, "[rol == 'CLIENTE' || modo_invitado]", font_size=9.5, font_weight="bold", anchor="middle")}

  <!-- 2. Rol CAJERO / OPERADOR (Centro) -->
  <line x1="585" y1="319" x2="585" y2="390" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(595, 355, "[rol == 'CAJERO' || 'OPERADOR_TIENDA']", font_size=9.5, font_weight="bold", anchor="start")}

  <!-- 3. Rol ADMIN / GERENTE (Derecha) -->
  <path d="M 599 305 L 1190 305 L 1190 390" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(890, 297, "[rol == 'ADMINISTRADOR' || 'GERENTE']", font_size=9.5, font_weight="bold", anchor="middle")}

  <!-- Subsistemas -->
  {sub_cliente.render()}
  {sub_pos.render()}
  {sub_admin.render()}

  <!-- Colector de Cierre de Sesión (Logout Bus) -->
  <path d="M 260 {sub_cliente.bottom()[1]} L 260 690 L 720 690" fill="none" stroke="#000000" stroke-width="1.2" stroke-dasharray="5,4"/>
  <path d="M 720 {sub_pos.bottom()[1]} L 720 690" fill="none" stroke="#000000" stroke-width="1.2" stroke-dasharray="5,4"/>
  <path d="M 1190 {sub_admin.bottom()[1]} L 1190 690 L 720 690" fill="none" stroke="#000000" stroke-width="1.2" stroke-dasharray="5,4"/>

  <!-- Bajada desde el Bus a Sesion_Cerrada -->
  <line x1="720" y1="690" x2="720" y2="755" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(730, 722, "[click_cerrar_sesion || token_expirado] / destruir_credenciales()", font_size=9, font_weight="bold", anchor="start")}

  <!-- Pantalla Sesión Cerrada -->
  {sesion_cerrada.render()}

  <!-- Retorno Periférico al Login por el canal despejado x=40 e y=68 (sin tocar el tab) -->
  <path d="M {sesion_cerrada.left()[0]} {sesion_cerrada.left()[1]} L 40 {sesion_cerrada.left()[1]} L 40 68 L 585 68 L 585 {login.top()[1]}" fill="none" stroke="#000000" stroke-width="1.3" stroke-dasharray="6,4" marker-end="url(#arrow)"/>
  {uml_label(300, 60, "[redirigir_a_login_screen]", font_size=9, font_weight="bold", anchor="middle")}

  <!-- Estado Final de Sesión -->
  <line x1="{sesion_cerrada.right()[0]}" y1="{sesion_cerrada.right()[1]}" x2="920" y2="{sesion_cerrada.right()[1]}" stroke="#000000" stroke-width="1.2" marker-end="url(#arrow)"/>
  {uml_label(880, sesion_cerrada.right()[1] - 8, "[cerrar app]", font_size=8.5, anchor="middle")}

  <circle cx="940" cy="{sesion_cerrada.right()[1]}" r="11" stroke="#000000" stroke-width="1.4" fill="#ffffff"/>
  <circle cx="940" cy="{sesion_cerrada.right()[1]}" r="6" fill="#000000"/>
  <text x="940" y="{sesion_cerrada.right()[1] + 24}" font-size="9" text-anchor="middle">Fin Sesión</text>

</svg>''')
    return "".join(svg)


# =============================================================
# 2. DN01: NAVEGACIÓN CLIENTE (E-COMMERCE & APP MÓVIL)
# =============================================================
def generate_dn01_svg():
    width = 1540
    height = 1050

    # Columna 1 (x=110, w=240)
    catalogo = UmlBox("catalogo", 110, 105, 240, "screen", "Catalogo_Home_Screen", [
        "«CU05: Buscar y filtrar productos»",
        "entry / cargar_catalogo_reciente()",
        "[click_categoria] / filtrar_prendas()",
        "[click_prenda] -> Detalle Prenda",
        "[abrir_chat] -> Asistente Inteligente"
    ])

    asistente = UmlBox("asistente", 110, 310, 240, "drawer/view", "Asistente_Chat_Drawer", [
        "«CU/W13, CU/M13: Asistente IA»",
        "entry / inicializar_sesion_deepseek()",
        "[enviar_pregunta] / consultar_ia_y_bd()",
        "[click_card_producto] -> Detalle Prenda",
        "[cerrar_chat] -> Volver a Catalogo"
    ])

    # Columna 2 (x=470, w=250)
    recom = UmlBox("recom", 470, 105, 250, "screen", "Recomendaciones_Screen", [
        "«CU/W12, CU/M12: Recomendaciones»",
        "entry / consultar_preferencias_historial()",
        "do / renderizar_carrusel_para_ti()",
        "[click_item_recomendado] -> Detalle Prenda"
    ])

    carrito = UmlBox("carrito", 470, 485, 250, "drawer/screen", "Carrito_Compras_Screen", [
        "«CU08: Gestionar carrito de compras»",
        "entry / recalcular_subtotal_y_descuentos()",
        "[modificar_cantidad] / actualizar_linea()",
        "[eliminar_prenda] / remover_linea()",
        "[proceder_checkout] -> Checkout Envío"
    ])

    checkout = UmlBox("checkout", 470, 665, 250, "screen", "Checkout_Envio_Screen", [
        "«CU09: Realizar compra»",
        "entry / seleccionar_direccion_entrega()",
        "[seleccionar_retiro_sucursal] / elegir_tienda",
        "[seleccionar_courier] / calcular_tarifa()",
        "[continuar_pago] -> Pasarela de Pago"
    ])

    pasarela = UmlBox("pasarela", 470, 845, 250, "screen/payment", "Pasarela_Pago_Screen", [
        "«CU_W27: Procesar pago electrónico»",
        "entry / generar_intencion_pago()",
        "[pago_qr] / generar_qr_simple_dinamico()",
        "[pago_tarjeta] / tokenizar_tarjeta()",
        "[webhook_pago_aprobado] -> Confirmación",
        "[pago_rechazado] -> reintentar_pago"
    ])

    # Columna 3 (x=840, w=260)
    ficha = UmlBox("ficha", 840, 105, 260, "screen", "Ficha_Detalle_Prenda_Screen", [
        "«CU06: Consultar detalle producto»",
        "entry / cargar_variantes(tallas, colores)",
        "[click_vestidor_ra] -> Vestidor Virtual",
        "[click_disponibilidad] -> Mapa Tiendas",
        "[click_agregar_carrito] -> Carrito",
        "[click_reservar] -> Formulario Reserva"
    ])

    sucursales = UmlBox("sucursales", 840, 310, 260, "modal/map", "Disponibilidad_Sucursal_Modal", [
        "«CU07, CU26: Sucursales y Stock»",
        "entry / geolocalizar_y_listar_tiendas()",
        "do / mostrar_unidades_por_sucursal()",
        "[seleccionar_tienda_reserva] -> Reservar",
        "[cerrar] -> volver a Detalle"
    ])

    confirmacion = UmlBox("confirmacion", 840, 845, 260, "screen", "Confirmacion_Pedido_Screen", [
        "«CU09: Confirmación Pedido»",
        "entry / mostrar_nro_pedido_y_qr()",
        "[descargar_recibo] / pdf_comprobante()",
        "[ir_a_pedidos] -> Mis Pedidos",
        "[volver_inicio] -> Catalogo Home"
    ])

    # Columna 4 (x=1220, w=240)
    vestidor = UmlBox("vestidor", 1220, 105, 240, "screen/camera", "Vestidor_Virtual_RA_Screen", [
        "«CU/M14: Utilizar vestidor virtual»",
        "entry / activar_camara_frontal()",
        "do / tracker_corporal_y_mesh_3d()",
        "[cambiar_talla_color] / recalcular()",
        "[capturar_foto] / compartir_guardar()",
        "[volver_ficha] -> Detalle Prenda"
    ])

    reserva = UmlBox("reserva", 1220, 310, 240, "modal", "Formulario_Reserva_Modal", [
        "«CU10: Gestionar reservas»",
        "entry / verificar_stock_sucursal()",
        "[confirmar_reserva] / generar_qr_reserva()",
        "[reserva_creada] -> Mis Reservas"
    ])

    mis_reservas = UmlBox("mis_reservas", 1220, 485, 240, "screen", "Mis_Reservas_Screen", [
        "«CU10: Mis Reservas»",
        "entry / listar_reservas_vigentes()",
        "[mostrar_codigo_qr] / retiro_en_sucursal",
        "[cancelar_reserva] / liberar_stock()"
    ])

    mis_pedidos = UmlBox("mis_pedidos", 1220, 845, 240, "screen", "Mis_Pedidos_Screen", [
        "«CU11: Consultar pedidos e historial»",
        "entry / listar_pedidos_cliente()",
        "[click_pedido] / ver_detalle_seguimiento()",
        "[estado_despachado] / ver_tracking_courier()",
        "[repetir_compra] -> Carrito"
    ])

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#000000"/>
    </marker>
  </defs>

  <!-- Marco Exterior -->
  {uml_header_frame(width, height, "Subsistema Cliente", "DN01: Navegación E-Commerce Web y App Móvil")}

  <!-- Punto de Entrada desde DN00 -->
  <circle cx="50" cy="155" r="9" fill="#000000"/>
  <text x="50" y="180" font-size="9.5" font-weight="bold" text-anchor="middle">Inicio</text>
  <line x1="59" y1="155" x2="{catalogo.left()[0]}" y2="155" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(85, 147, "[login_ok / invitado]", font_size=8.5, anchor="middle")}

  <!-- RENDER DE PANTALLAS -->
  {catalogo.render()}
  {recom.render()}
  {ficha.render()}
  {vestidor.render()}
  {asistente.render()}
  {sucursales.render()}
  {reserva.render()}
  {carrito.render()}
  {mis_reservas.render()}
  {checkout.render()}
  {pasarela.render()}
  {confirmacion.render()}
  {mis_pedidos.render()}

  <!-- ENLACES FILA 1 -->
  <!-- Catálogo <-> Recomendaciones -->
  <line x1="{catalogo.right()[0]}" y1="135" x2="{recom.left()[0]}" y2="135" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(410, 127, "[recomendaciones]", font_size=8.5, anchor="middle")}

  <line x1="{recom.left()[0]}" y1="165" x2="{catalogo.right()[0]}" y2="165" stroke="#000000" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
  {uml_label(410, 177, "[volver]", font_size=8.5, anchor="middle")}

  <!-- Recomendaciones -> Ficha Detalle -->
  <line x1="{recom.right()[0]}" y1="150" x2="{ficha.left()[0]}" y2="150" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(780, 142, "[ver_detalle]", font_size=8.5, anchor="middle")}

  <!-- Catálogo directo a Ficha (Canal superior despejado y=68) -->
  <path d="M 230 {catalogo.top()[1]} L 230 68 L 970 68 L 970 {ficha.top()[1]}" fill="none" stroke="#000000" stroke-width="1.2" marker-end="url(#arrow)"/>
  {uml_label(600, 60, "[explorar_prenda]", font_size=8.5, anchor="middle")}

  <!-- Ficha <-> Vestidor Virtual RA -->
  <line x1="{ficha.right()[0]}" y1="135" x2="{vestidor.left()[0]}" y2="135" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(1160, 127, "[abrir_vestidor_ra]", font_size=8.5, anchor="middle")}

  <line x1="{vestidor.left()[0]}" y1="165" x2="{ficha.right()[0]}" y2="165" stroke="#000000" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
  {uml_label(1160, 177, "[volver]", font_size=8.5, anchor="middle")}

  <!-- FILA 1 A FILA 2 -->
  <!-- Catálogo <-> Asistente Chat (vertical totalmente libre) -->
  <line x1="170" y1="{catalogo.bottom()[1]}" x2="170" y2="{asistente.top()[1]}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(165, 270, "[abrir_chat]", font_size=8.5, anchor="end")}

  <line x1="280" y1="{asistente.top()[1]}" x2="280" y2="{catalogo.bottom()[1]}" stroke="#000000" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
  {uml_label(285, 270, "[cerrar]", font_size=8.5, anchor="start")}

  <!-- Asistente Chat -> Ficha (Canal y=265 despejado) -->
  <path d="M {asistente.right()[0]} 360 L 410 360 L 410 265 L 870 265 L 870 {ficha.bottom()[1]}" fill="none" stroke="#000000" stroke-width="1.2" marker-end="url(#arrow)"/>
  {uml_label(600, 257, "[click_producto_en_chat]", font_size=8.5, anchor="middle")}

  <!-- Ficha <-> Disponibilidad en Sucursales -->
  <line x1="970" y1="{ficha.bottom()[1]}" x2="970" y2="{sucursales.top()[1]}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(978, 282, "[ver_stock]", font_size=8.5, anchor="start")}

  <path d="M 930 {sucursales.top()[1]} L 930 {ficha.bottom()[1]}" fill="none" stroke="#000000" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
  {uml_label(922, 282, "[cerrar]", font_size=8.5, anchor="end")}

  <!-- Disponibilidad -> Formulario Reserva -->
  <line x1="{sucursales.right()[0]}" y1="350" x2="{reserva.left()[0]}" y2="350" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(1160, 342, "[reservar]", font_size=8.5, anchor="middle")}

  <!-- Formulario Reserva -> Mis Reservas -->
  <line x1="{reserva.bottom()[0]}" y1="{reserva.bottom()[1]}" x2="{mis_reservas.top()[0]}" y2="{mis_reservas.top()[1]}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(reserva.bottom()[0] + 8, 450, "[reserva_confirmada]", font_size=8.5, anchor="start")}

  <!-- Ficha -> Carrito (Canal central despejado x=780, etiqueta a la izquierda en espacio vacío) -->
  <path d="M {ficha.left()[0]} 200 L 780 200 L 780 520 L {carrito.right()[0]} 520" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(770, 410, "[agregar_al_carrito]", font_size=9, font_weight="bold", anchor="end")}

  <!-- Carrito -> Checkout Envío -->
  <line x1="{carrito.bottom()[0]}" y1="{carrito.bottom()[1]}" x2="{checkout.top()[0]}" y2="{checkout.top()[1]}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(carrito.bottom()[0] + 8, 638, "[proceder_al_checkout]", font_size=9, font_weight="bold", anchor="start")}

  <!-- Checkout -> Pasarela Pago -->
  <line x1="{checkout.bottom()[0]}" y1="{checkout.bottom()[1]}" x2="{pasarela.top()[0]}" y2="{pasarela.top()[1]}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(checkout.bottom()[0] + 8, 818, "[continuar_al_pago]", font_size=9, font_weight="bold", anchor="start")}

  <!-- Pasarela -> Confirmación Pedido -->
  <line x1="{pasarela.right()[0]}" y1="900" x2="{confirmacion.left()[0]}" y2="900" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(780, 892, "[pago_aprobado]", font_size=8.5, anchor="middle")}

  <!-- Confirmación -> Mis Pedidos -->
  <line x1="{confirmacion.right()[0]}" y1="900" x2="{mis_pedidos.left()[0]}" y2="900" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(1160, 892, "[ver_pedidos]", font_size=8.5, anchor="middle")}

  <!-- RETORNO PERIFÉRICO AL CATÁLOGO (Canal exterior inferior y=1015 y lateral x=45, 100% libre) -->
  <path d="M {confirmacion.bottom()[0]} {confirmacion.bottom()[1]} L {confirmacion.bottom()[0]} 1015 L 45 1015 L 45 155 L {catalogo.left()[0]} 155" fill="none" stroke="#000000" stroke-width="1.3" stroke-dasharray="6,4" marker-end="url(#arrow)"/>
  {uml_label(600, 1007, "[volver_al_inicio / seguir_comprando]", font_size=9, font_weight="bold", anchor="middle")}

</svg>''')
    return "".join(svg)


# =============================================================
# 3. DN02: NAVEGACIÓN OPERATIVA DE SUCURSAL (POS & CAJA)
# =============================================================
def generate_dn02_svg():
    width = 1480
    height = 940

    # Columna 1 (x=110, w=240)
    apertura = UmlBox("apertura", 110, 105, 240, "modal", "Apertura_Caja_Modal", [
        "entry / verificar_caja_previa()",
        "[ingresar_monto_apertura] / validar()",
        "[confirmar_apertura] -> Terminal POS",
        "[cancelar] -> Logout"
    ])

    cierre = UmlBox("cierre", 110, 620, 240, "modal", "Cierre_Caja_Arqueo_Modal", [
        "entry / consolidar_ventas_del_turno()",
        "[contar_efectivo_en_gaveta] / ingresar()",
        "do / conciliar_con_cobros_qr_tarjeta()",
        "[diferencia_detectada] / alertar()",
        "[confirmar_cierre] / emitir_reporte_z()",
        "[fin_turno] -> Cerrar Sesión"
    ])

    # Columna 2 (x=470, w=320)
    pos = UmlBox("pos", 470, 105, 320, "screen/pos", "Terminal_Venta_POS_Screen", [
        "«CU_W24: Registrar venta presencial»",
        "entry / inicializar_sesion_caja_turno()",
        "[escanear_codigo_barras] / buscar_prenda()",
        "[buscar_manual_catalogo] / seleccionar()",
        "[click_despachar_reserva] -> Reservas",
        "[click_cobrar] -> Módulo de Cobro",
        "[click_inventario] -> Stock Sucursal",
        "[click_cerrar_turno] -> Arqueo Caja"
    ])

    cobro = UmlBox("cobro", 470, 380, 320, "modal/payment", "Modulo_Cobro_Caja_Modal", [
        "«CU_W28: Procesar pago en caja»",
        "entry / calcular_total_venta(descuentos, promos)",
        "[cobro_efectivo] / calcular_cambio_vuelto()",
        "[cobro_qr_pos] / generar_qr_terminal_pantalla()",
        "[cobro_pos_tarjeta] / confirmar_voucher()",
        "[confirmar_pago] -> Emisión Comprobante",
        "[cancelar_cobro] -> volver a POS"
    ])

    comprobante = UmlBox("comprobante", 470, 630, 320, "screen", "Emision_Comprobante_Screen", [
        "«CU_W29: Emitir comprobante de venta»",
        "entry / generar_factura_o_recibo_fiscal()",
        "do / insertar_t_venta_y_t_detalle_venta()",
        "do / generar_qr_tributario_facturacion()",
        "[imprimir_ticket] / enviar_a_termica()",
        "[enviar_whatsapp_email] / notificar_cliente()",
        "[nueva_venta] -> Terminal POS"
    ])

    # Columna 3 (x=940, w=280)
    despacho = UmlBox("despacho", 940, 105, 280, "modal", "Despacho_Reservas_Modal", [
        "«CU_W25: Atender reservas»",
        "entry / lector_qr_reserva()",
        "[ingresar_dni_codigo] / buscar_reserva()",
        "[reserva_encontrada] / mostrar_prendas()",
        "[cargar_a_caja_pos] -> Venta POS",
        "[cerrar] -> volver a POS"
    ])

    inventario = UmlBox("inventario", 940, 380, 280, "screen", "Gestion_Inventario_Screen", [
        "«CU_W22: Gestionar inventario sucursal»",
        "entry / listar_stock_tienda_por_prenda()",
        "[consultar_kardex] / movimientos()",
        "[recepcionar_traspaso] / confirmar_ingreso()",
        "[registrar_merma_ajuste] / guardar_bitacora()",
        "[volver_a_pos] -> Terminal POS"
    ])

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#000000"/>
    </marker>
  </defs>

  <!-- Marco Exterior -->
  {uml_header_frame(width, height, "Subsistema POS", "DN02: Navegación Operativa de Sucursal, POS y Caja")}

  <!-- Entrada Inicial -->
  <circle cx="50" cy="155" r="9" fill="#000000"/>
  <text x="50" y="180" font-size="9.5" font-weight="bold" text-anchor="middle">Inicio</text>
  <line x1="59" y1="155" x2="{apertura.left()[0]}" y2="155" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(85, 147, "[rol_cajero]", font_size=8.5, anchor="middle")}

  <!-- RENDER DE PANTALLAS -->
  {apertura.render()}
  {pos.render()}
  {despacho.render()}
  {inventario.render()}
  {cobro.render()}
  {comprobante.render()}
  {cierre.render()}

  <!-- Apertura -> POS -->
  <line x1="{apertura.right()[0]}" y1="155" x2="{pos.left()[0]}" y2="155" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(410, 147, "[caja_abierta_ok]", font_size=8.5, anchor="middle")}

  <!-- POS <-> Despacho de Reservas -->
  <line x1="{pos.right()[0]}" y1="140" x2="{despacho.left()[0]}" y2="140" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(865, 132, "[atender_reserva]", font_size=8.5, anchor="middle")}

  <line x1="{despacho.left()[0]}" y1="175" x2="{pos.right()[0]}" y2="175" stroke="#000000" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
  {uml_label(865, 187, "[prenda_cargada_al_pos]", font_size=8.5, anchor="middle")}

  <!-- POS <-> Gestion de Inventario (Ruta lateral amplia de 150px) -->
  <!-- Ida: sale de POS a y=230, baja por x=880 hacia inventario -->
  <path d="M {pos.right()[0]} 230 L 880 230 L 880 420 L {inventario.left()[0]} 420" fill="none" stroke="#000000" stroke-width="1.2" marker-end="url(#arrow)"/>
  {uml_label(835, 222, "[consultar_stock]", font_size=8.5, anchor="middle")}

  <!-- Retorno: sale de inventario a y=460, sube por x=830 hacia POS -->
  <path d="M {inventario.left()[0]} 460 L 830 460 L 830 255 L {pos.right()[0]} 255" fill="none" stroke="#000000" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
  {uml_label(885, 472, "[volver]", font_size=8.5, anchor="middle")}

  <!-- POS -> Modulo de Cobro (Vertical limpio) -->
  <line x1="630" y1="{pos.bottom()[1]}" x2="630" y2="{cobro.top()[1]}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(640, (pos.bottom()[1] + cobro.top()[1]) / 2, "[proceder_al_cobro]", font_size=9.5, font_weight="bold", anchor="start")}

  <!-- Cobro -> Emision de Comprobante -->
  <line x1="630" y1="{cobro.bottom()[1]}" x2="630" y2="{comprobante.top()[1]}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(640, (cobro.bottom()[1] + comprobante.top()[1]) / 2, "[pago_asentado_exitoso]", font_size=9.5, font_weight="bold", anchor="start")}

  <!-- Emision Comprobante -> Retorno a POS para Nueva Venta (Canal despejado x=400) -->
  <path d="M {comprobante.left()[0]} 680 L 400 680 L 400 190 L {pos.left()[0]} 190" fill="none" stroke="#000000" stroke-width="1.2" stroke-dasharray="5,4" marker-end="url(#arrow)"/>
  {uml_label(390, 440, "[nueva_venta]", font_size=9, font_weight="bold", anchor="end")}

  <!-- POS -> Cierre de Caja y Arqueo (Canal vertical x=230) -->
  <path d="M {pos.left()[0]} 220 L 230 220 L 230 {cierre.top()[1]}" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(238, 380, "[click_cerrar_turno]", font_size=9, font_weight="bold", anchor="start")}

  <!-- Salida / Fin de Turno POS -->
  <line x1="{cierre.bottom()[0]}" y1="{cierre.bottom()[1]}" x2="{cierre.bottom()[0]}" y2="830" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(cierre.bottom()[0] + 8, 795, "[turno_cerrado_ok]", font_size=8.5, anchor="start")}

  <circle cx="{cierre.bottom()[0]}" cy="845" r="11" stroke="#000000" stroke-width="1.4" fill="#ffffff"/>
  <circle cx="{cierre.bottom()[0]}" cy="845" r="6" fill="#000000"/>
  <text x="{cierre.bottom()[0]}" y="870" font-size="9" text-anchor="middle">Fin Turno POS</text>

</svg>''')
    return "".join(svg)


# =============================================================
# 4. DN03: NAVEGACIÓN ADMINISTRATIVA & BI (BACKOFFICE)
# =============================================================
def generate_dn03_svg():
    width = 1540
    height = 940

    # Columna 1 (x=110, w=330)
    dashboard = UmlBox("dashboard", 110, 105, 330, "screen/dashboard", "Dashboard_KPIs_BI_Screen", [
        "«CU_W32: Visualizar indicadores empresariales»",
        "entry / cargar_metricas_globales_y_pos()",
        "do / renderizar_graficos_ventas_y_tickets()",
        "[filtrar_periodo] / actualizar_kpis()",
        "[sidebar_promociones] -> Gestionar Promociones",
        "[sidebar_consultas] -> Consultas Ventas e Inv.",
        "[sidebar_reportes] -> Generar Reportes",
        "[sidebar_catalogo] -> Catálogo y Colecciones"
    ])

    catalogo_admin = UmlBox("catalogo_admin", 110, 520, 330, "screen", "Gestion_Catalogo_Prendas_Screen", [
        "«CU_W20, CU_W23: Catálogo y Temporadas»",
        "entry / listar_prendas_y_colecciones()",
        "[crear_temporada] / definir_fechas()",
        "[crear_prenda] / registrar_variantes_talla_color()",
        "[habilitar_vestidor_ra] / subir_textura_3d()",
        "[actualizar_precios] / guardar()"
    ])

    # Columna 2 (x=600, w=320)
    promociones = UmlBox("promociones", 600, 105, 320, "screen", "Gestion_Promociones_Screen", [
        "«CU_W30: Gestionar promociones»",
        "entry / listar_promociones_activas()",
        "[click_crear_promo] / abrir_formulario()",
        "[validar_vigencia] / verificar_solapamiento()",
        "[asociar_prendas] / vincular_a_promocion()",
        "[guardar_promocion] / registrar_bitacora()",
        "[desactivar_promo] / cambiar_estado()"
    ])

    consultas = UmlBox("consultas", 600, 330, 320, "screen", "Consulta_Ventas_Inventario_Screen", [
        "«CU_W31: Consultar ventas, reservas, inv.»",
        "entry / consolidar_datos_multisucursal()",
        "[filtrar_por_sucursal] / listar_prendas()",
        "[ver_alertas_stock_minimo] / resaltar()",
        "[inspeccionar_reservas] / ver_estados()",
        "[exportar_vista] -> Generar Reportes"
    ])

    proveedores = UmlBox("proveedores", 600, 520, 320, "screen", "Proveedores_Sucursales_Screen", [
        "«CU_W21: Gestionar proveedores»",
        "entry / listar_proveedores_y_tiendas()",
        "[alta_proveedor] / registrar_datos_contacto()",
        "[vincular_suministro] / asociar_prendas()",
        "[gestionar_sucursal] / configurar_horarios()",
        "[guardar] / registrar_bitacora()"
    ])

    # Columna 3 (x=1060, w=330)
    reportes = UmlBox("reportes", 1060, 330, 330, "screen/job", "Generar_Reportes_Screen", [
        "«CU_W33: Generar reportes bajo demanda»",
        "entry / seleccionar_plantilla_reporte()",
        "[configurar_filtros_fechas_sucursal] / validar()",
        "[ejecutar_generacion_pdf] / compilar()",
        "[ejecutar_export_excel] / generar_xlsx()",
        "[descargar_archivo] / registrar_en_bitacora()",
        "[volver_dashboard] -> Dashboard"
    ])

    auditoria = UmlBox("auditoria", 1060, 520, 330, "screen/audit", "Auditoria_Bitacora_Screen", [
        "«Bitácora de Eventos de Seguridad»",
        "entry / consultar_t_bitacora()",
        "[filtrar_por_usuario_accion_fecha] / buscar()",
        "[ver_detalle_evento] / ver_ip_y_payload()",
        "[exportar_logs] / generar_archivo_auditoria()"
    ])

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#000000"/>
    </marker>
  </defs>

  <!-- Marco Exterior -->
  {uml_header_frame(width, height, "Subsistema Backoffice", "DN03: Navegación Panel Administrativo y BI")}

  <!-- Entrada Inicial -->
  <circle cx="50" cy="155" r="9" fill="#000000"/>
  <text x="50" y="180" font-size="9.5" font-weight="bold" text-anchor="middle">Inicio</text>
  <line x1="59" y1="155" x2="{dashboard.left()[0]}" y2="155" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(85, 147, "[rol_admin]", font_size=8.5, anchor="middle")}

  <!-- RENDER DE PANTALLAS -->
  {dashboard.render()}
  {catalogo_admin.render()}
  {promociones.render()}
  {consultas.render()}
  {proveedores.render()}
  {reportes.render()}
  {auditoria.render()}

  <!-- Dashboard -> Promociones -->
  <line x1="{dashboard.right()[0]}" y1="150" x2="{promociones.left()[0]}" y2="150" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(520, 142, "[promociones]", font_size=8.5, anchor="middle")}

  <!-- Dashboard -> Consultas Globales (Canal inter-columnas x=520, entra a consultas en y=380 limpio) -->
  <path d="M {dashboard.right()[0]} 210 L 520 210 L 520 380 L {consultas.left()[0]} 380" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(560, 372, "[consultas]", font_size=8.5, anchor="middle")}

  <!-- Dashboard -> Catálogo Prendas (Vertical limpio) -->
  <line x1="{dashboard.bottom()[0]}" y1="{dashboard.bottom()[1]}" x2="{catalogo_admin.top()[0]}" y2="{catalogo_admin.top()[1]}" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(dashboard.bottom()[0] + 8, 410, "[catalogo_prendas]", font_size=9, font_weight="bold", anchor="start")}

  <!-- Dashboard -> Reportes Bajo Demanda (Canal superior despejado y=68) -->
  <path d="M 370 {dashboard.top()[1]} L 370 68 L 1225 68 L 1225 {reportes.top()[1]}" fill="none" stroke="#000000" stroke-width="1.2" marker-end="url(#arrow)"/>
  {uml_label(800, 60, "[reportes_demanda]", font_size=8.5, anchor="middle")}

  <!-- Consultas -> Generar Reportes -->
  <line x1="{consultas.right()[0]}" y1="410" x2="{reportes.left()[0]}" y2="410" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(990, 402, "[exportar_reporte]", font_size=8.5, anchor="middle")}

  <!-- Catálogo -> Proveedores y Sucursales -->
  <line x1="{catalogo_admin.right()[0]}" y1="580" x2="{proveedores.left()[0]}" y2="580" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(520, 572, "[proveedores]", font_size=8.5, anchor="middle")}

  <!-- Proveedores -> Auditoría y Bitácora -->
  <line x1="{proveedores.right()[0]}" y1="580" x2="{auditoria.left()[0]}" y2="580" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(990, 572, "[auditoria]", font_size=8.5, anchor="middle")}

  <!-- RETORNO GENERAL AL DASHBOARD (Canal perimétrico exterior por y=880 y x=45, completamente libre) -->
  <path d="M {auditoria.right()[0]} 600 L 1460 600 L 1460 880 L 45 880 L 45 195 L {dashboard.left()[0]} 195" fill="none" stroke="#000000" stroke-width="1.3" stroke-dasharray="6,4" marker-end="url(#arrow)"/>
  {uml_label(750, 872, "[volver_dashboard / navegar_sidebar]", font_size=9, font_weight="bold", anchor="middle")}

  <!-- Salida / Logout Administrador -->
  <line x1="200" y1="{catalogo_admin.bottom()[1]}" x2="200" y2="780" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow)"/>
  {uml_label(208, 740, "[logout_admin]", font_size=8.5, anchor="start")}

  <circle cx="200" cy="795" r="11" stroke="#000000" stroke-width="1.4" fill="#ffffff"/>
  <circle cx="200" cy="795" r="6" fill="#000000"/>
  <text x="200" y="820" font-size="9" text-anchor="middle">Fin Admin</text>

</svg>''')
    return "".join(svg)


# =============================================================
# MAIN DE EJECUCIÓN
# =============================================================
def main():
    print("Iniciando regeneración final de Diagramas de Navegación UML Estándar...")
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(BRAIN_DIR, exist_ok=True)
    
    diagrams = [
        ("DN00_Mapa_General_Navegacion_Sistema_Aura", generate_dn00_svg()),
        ("DN01_Navegacion_Cliente_Ecommerce_Checkout", generate_dn01_svg()),
        ("DN02_Navegacion_Operativa_Sucursal_POS_Caja", generate_dn02_svg()),
        ("DN03_Navegacion_Administracion_Catalogo_Auditoria", generate_dn03_svg()),
    ]
    
    for idx, (name, raw_svg) in enumerate(diagrams):
        svg_content = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', '&amp;', raw_svg)
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
            
        print(f" [{idx+1}/{len(diagrams)}] Generado: {name} (SVG y PNG 2x)")

    print("\nTodos los Diagramas de Navegación UML generados y sincronizados exitosamente.")

if __name__ == "__main__":
    main()
