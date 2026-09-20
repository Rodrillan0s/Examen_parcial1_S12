#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de los 17 Diagramas de Estado UML 2.5 (SI2 - UAGRM)
Iteración Actual: E-Commerce Multi-Tenant para Venta de Ropa Aura

Criterios de Cátedra:
- NO usar plantilla repetitiva; cada Caso de Uso posee una topología y ciclo de vida propio:
  * Consultas: lineales, con bucles de selección interactiva o bifurcaciones de resultado (SIN bitácora).
  * Transacciones: con validaciones de negocio, ramas de error/reintento, bifurcaciones de tipo de pago/ajuste,
    actualizaciones de kardex y registro formal en bitácora de auditoría.
- Notación formal UAGRM (ejemplo docente CU23):
  * Título limpio centrado
  * Círculo negro sólido para Estado Inicial
  * Cajas redondeadas suaves (#f4f4f4 con borde #777777)
  * Transiciones claras con eventos, guardas y acciones
  * Diana concéntrica para Estado Final
"""

import os
import sys
import xml.sax.saxutils
import cairosvg

def escape_xml(text):
    return xml.sax.saxutils.escape(str(text))

# ------------------------------------------------------------------------------
# Helpers de Dibujo SVG
# ------------------------------------------------------------------------------

def svg_header(w, h, title):
    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n')
    parts.append('  <defs>\n')
    parts.append('    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">\n')
    parts.append('      <path d="M 0 1 L 7 4 L 0 7 Z" fill="#222222"/>\n')
    parts.append('    </marker>\n')
    parts.append('  </defs>\n\n')
    parts.append(f'  <rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>\n')
    parts.append(f'  <text x="{w/2}" y="46" font-family="Arial, Helvetica, sans-serif" font-size="20" font-weight="normal" fill="#000000" text-anchor="middle">{escape_xml(title)}</text>\n\n')
    return parts

def draw_initial(cx, y):
    return f'  <!-- Estado Inicial -->\n  <circle cx="{cx}" cy="{y}" r="11" fill="#222222"/>\n\n'

def draw_final(cx, y):
    return (f'  <!-- Estado Final -->\n'
            f'  <circle cx="{cx}" cy="{y}" r="14" fill="none" stroke="#222222" stroke-width="1.4"/>\n'
            f'  <circle cx="{cx}" cy="{y}" r="8.5" fill="#222222"/>\n\n')

def draw_state(sid, name, cx, y, bw=185, bh=38):
    return (f'  <!-- Estado: {name} -->\n'
            f'  <g id="{sid}">\n'
            f'    <rect x="{cx - bw/2}" y="{y}" width="{bw}" height="{bh}" rx="9" ry="9" fill="#f4f4f4" stroke="#777777" stroke-width="0.9"/>\n'
            f'    <text x="{cx}" y="{y + bh/2 + 4.5}" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#111111" text-anchor="middle">{escape_xml(name)}</text>\n'
            f'  </g>\n')

def draw_down_arrow(cx, y1, y2, label="", label_x_offset=10):
    res = []
    res.append(f'  <line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2}" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')
    if label:
        mid_y = (y1 + y2) / 2 + 4
        res.append(f'  <text x="{cx + label_x_offset}" y="{mid_y}" font-family="Arial, Helvetica, sans-serif" font-size="10.5" fill="#222222">{escape_xml(label)}</text>\n')
    return "".join(res)

def draw_diag_arrow(x1, y1, x2, y2, label="", label_x=None, label_y=None, text_anchor="start"):
    res = []
    res.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')
    if label:
        lx = label_x if label_x is not None else (x1 + x2) / 2 + 8
        ly = label_y if label_y is not None else (y1 + y2) / 2
        res.append(f'  <text x="{lx}" y="{ly}" font-family="Arial, Helvetica, sans-serif" font-size="10.5" fill="#222222" text-anchor="{text_anchor}">{escape_xml(label)}</text>\n')
    return "".join(res)

def draw_curve_arrow(x1, y1, cx_ctrl, cy_ctrl, x2, y2, label="", label_x=None, label_y=None):
    res = []
    res.append(f'  <path d="M {x1} {y1} Q {cx_ctrl} {cy_ctrl} {x2} {y2}" fill="none" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')
    if label and label_x is not None and label_y is not None:
        res.append(f'  <text x="{label_x}" y="{label_y}" font-family="Arial, Helvetica, sans-serif" font-size="10.5" fill="#222222">{escape_xml(label)}</text>\n')
    return "".join(res)

def draw_loop_arrow(cx, y, bw, bh, label="", side="right"):
    res = []
    if side == "right":
        x_start = cx + bw/2
        y_start = y + bh*0.3
        x_end = cx + bw/2
        y_end = y + bh*0.75
        ctrl_x = x_start + 45
        res.append(f'  <path d="M {x_start} {y_start} C {ctrl_x} {y_start - 20} {ctrl_x} {y_end + 20} {x_end} {y_end}" fill="none" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')
        if label:
            res.append(f'  <text x="{ctrl_x + 6}" y="{y + bh/2 + 3}" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#222222">{escape_xml(label)}</text>\n')
    else:
        x_start = cx - bw/2
        y_start = y + bh*0.3
        x_end = cx - bw/2
        y_end = y + bh*0.75
        ctrl_x = x_start - 45
        res.append(f'  <path d="M {x_start} {y_start} C {ctrl_x} {y_start - 20} {ctrl_x} {y_end + 20} {x_end} {y_end}" fill="none" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')
        if label:
            res.append(f'  <text x="{ctrl_x - 10}" y="{y + bh/2 + 3}" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#222222" text-anchor="end">{escape_xml(label)}</text>\n')
    return "".join(res)


# ==============================================================================
# CONSTRUCCIÓN ESPECÍFICA DE CADA DIAGRAMA DE ESTADO (TOPOLOGÍA PERSONALIZADA)
# ==============================================================================

def make_cu05():
    w, h, cx = 740, 720, 370
    p = svg_header(w, h, "CU05 W/M: Buscar y filtrar productos")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 160, "abrir_catalogo()"))
    p.append(draw_state("s1", "CatalogoAbierto", cx, 160, 180, 38))
    p.append(draw_down_arrow(cx, 198, 255, "seleccionar_filtros(categoria, precio)"))
    p.append(draw_state("s2", "FiltrandoProductos", cx, 255, 180, 38))
    p.append(draw_down_arrow(cx, 293, 350, "listar_catalogo_publico(filtros)"))
    p.append(draw_state("s3", "ProcesandoConsulta", cx, 350, 195, 38))
    
    # Bifurcación 2 vías
    left_x, right_x, b_y = 200, 540, 475
    p.append(draw_state("s4_err", "SinCoincidencias", left_x, b_y, 175, 38))
    p.append(draw_state("s4_ok", "ProductosMostrados", right_x, b_y, 185, 38))
    p.append(draw_curve_arrow(cx - 50, 388, left_x + 30, 420, left_x, b_y, "[Sin coincidencias]", left_x - 85, 435))
    p.append(draw_diag_arrow(cx + 35, 388, right_x - 30, b_y, "[Productos encontrados] / renderizar_grid()", cx + 110, 425))
    
    p.append(draw_final(cx, 630))
    p.append(draw_diag_arrow(left_x + 25, b_y + 38, cx - 14, 622))
    p.append(draw_diag_arrow(right_x - 25, b_y + 38, cx + 14, 622))
    p.append('</svg>\n')
    return "".join(p)


def make_cu06():
    # Topología: Lineal con Bucle interactivo de cambio de talla/color
    w, h, cx = 700, 680, 350
    p = svg_header(w, h, "CU06 W/M: Consultar detalle de producto")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 160, "seleccionar_prenda(id_producto)"))
    p.append(draw_state("s1", "FichaPrendaAbierta", cx, 160, 190, 38))
    p.append(draw_down_arrow(cx, 198, 255, "obtener_detalle_producto()"))
    p.append(draw_state("s2", "VariantesDisponibles", cx, 255, 190, 38))
    # Bucle interactivo
    p.append(draw_loop_arrow(cx, 255, 190, 38, "cambiar_talla_o_color()", side="right"))
    p.append(draw_down_arrow(cx, 293, 365, "cargar_galeria_imagenes()"))
    p.append(draw_state("s3", "GaleriaRenderizada", cx, 365, 190, 38))
    p.append(draw_down_arrow(cx, 403, 475, "visualizar_especificaciones()"))
    p.append(draw_state("s4", "DetallePrendaVisualizado", cx, 475, 205, 38))
    p.append(draw_down_arrow(cx, 513, 585, "cerrar_o_continuar()"))
    p.append(draw_final(cx, 600))
    p.append('</svg>\n')
    return "".join(p)


def make_cu07():
    # Topología: 3-Way Branch (Tienda actual / Otras tiendas / Agotado global)
    w, h, cx = 780, 680, 390
    p = svg_header(w, h, "CU07 W/M: Consultar disponibilidad por sucursal")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "consultar_stock_sucursales(id_variante)"))
    p.append(draw_state("s1", "VerificandoKardexSucursales", cx, 155, 230, 38))
    p.append(draw_down_arrow(cx, 193, 250, "evaluar_disponibilidad_red()"))
    p.append(draw_state("s2", "AnalizandoStockGlobal", cx, 250, 210, 38))
    
    # 3 Ramas: Izquierda (Agotado), Centro (Tienda actual), Derecha (Otras sucursales)
    y3 = 390
    x_left, x_center, x_right = 160, 390, 620
    p.append(draw_state("s3_agotado", "AgotadoEnRed", x_left, y3, 160, 38))
    p.append(draw_state("s3_local", "DisponibleEnTienda", x_center, y3, 175, 38))
    p.append(draw_state("s3_otras", "DisponibleEnOtras", x_right, y3, 170, 38))

    p.append(draw_diag_arrow(cx - 50, 288, x_left + 40, y3, "[Stock = 0]", x_left - 30, 335))
    p.append(draw_down_arrow(cx, 288, y3, "[Hay stock local]", label_x_offset=-105))
    p.append(draw_diag_arrow(cx + 50, 288, x_right - 40, y3, "[Solo otras tiendas] / ver_mapa()", cx + 80, 335))

    p.append(draw_final(cx, 590))
    p.append(draw_diag_arrow(x_left + 20, y3 + 38, cx - 18, 580))
    p.append(draw_down_arrow(cx, y3 + 38, 576))
    p.append(draw_diag_arrow(x_right - 20, y3 + 38, cx + 18, 580))
    p.append('</svg>\n')
    return "".join(p)


def make_cu08():
    # Topología: Bucle de cantidad con ramas de Remover Item y Pasar a Checkout
    w, h, cx = 740, 720, 370
    p = svg_header(w, h, "CU08 W/M: Gestionar carrito de compras")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "agregar_item(id_variante, cant)"))
    p.append(draw_state("s1", "VerificandoStockPrenda", cx, 155, 205, 38))
    p.append(draw_down_arrow(cx, 193, 255, "[Stock ok] / persistir_item()"))
    p.append(draw_state("s2", "ItemEnCarrito", cx, 255, 185, 38))
    
    # Bucle de incremento/decremento
    p.append(draw_loop_arrow(cx, 255, 185, 38, "modificar_cantidad(+/-)", side="right"))
    
    # Bifurcación: Izquierda (Eliminar de carrito) vs Derecha (Avanzar a Checkout)
    left_x, right_x, b_y = 210, 530, 410
    p.append(draw_state("s3_del", "ItemRemovido", left_x, b_y, 160, 38))
    p.append(draw_state("s3_ready", "CarritoConfirmado", right_x, b_y, 180, 38))
    
    p.append(draw_diag_arrow(cx - 40, 293, left_x + 30, b_y, "eliminar_item()", left_x - 30, 350))
    p.append(draw_diag_arrow(cx + 40, 293, right_x - 30, b_y, "confirmar_carrito()", cx + 85, 335))

    # Estado final
    p.append(draw_final(cx, 590))
    p.append(draw_diag_arrow(left_x + 20, b_y + 38, cx - 14, 580))
    p.append(draw_diag_arrow(right_x - 20, b_y + 38, cx + 14, 580))
    p.append('</svg>\n')
    return "".join(p)


def make_cu09():
    # Topología: Pipeline Transaccional Multi-Paso con Auditoría en Bitácora
    w, h, cx = 700, 780, 350
    p = svg_header(w, h, "CU09 W/M: Realizar compra")
    p.append(draw_initial(cx, 90))
    p.append(draw_down_arrow(cx, 101, 150, "iniciar_checkout()"))
    p.append(draw_state("s1", "ConfigurandoEntrega", cx, 150, 195, 38))
    p.append(draw_down_arrow(cx, 188, 240, "seleccionar_metodo_pago()"))
    p.append(draw_state("s2", "MetodoPagoConfigurado", cx, 240, 205, 38))
    p.append(draw_down_arrow(cx, 278, 330, "confirmar_orden()"))
    p.append(draw_state("s3", "IniciandoTransaccionPedido", cx, 330, 220, 38))
    p.append(draw_down_arrow(cx, 368, 420, "bloquear_stock_kardex()"))
    p.append(draw_state("s4", "StockApartadoTemporal", cx, 420, 200, 38))
    p.append(draw_down_arrow(cx, 458, 510, "registrar_bitacora(\"COMPRA\")"))
    p.append(draw_state("s5", "BitacoraCompraAsentada", cx, 510, 210, 38))
    p.append(draw_down_arrow(cx, 548, 600, "generar_numero_pedido()"))
    p.append(draw_state("s6", "PedidoRegistradoExitoso", cx, 600, 215, 38))
    p.append(draw_down_arrow(cx, 638, 690, "mostrar_confirmacion()"))
    p.append(draw_final(cx, 705))
    p.append('</svg>\n')
    return "".join(p)


def make_cu10():
    # Topología: Verificación de Stock con caducidad 48h y Bitácora
    w, h, cx = 760, 700, 380
    p = svg_header(w, h, "CU10 W/M: Gestionar reservas")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "solicitar_reserva(id_var, id_suc)"))
    p.append(draw_state("s1", "VerificandoStockSucursal", cx, 155, 210, 38))
    
    # Bifurcación: Rechazo vs Éxito
    left_x, right_x, b_y = 190, 530, 265
    p.append(draw_state("s2_err", "ReservaRechazada", left_x, b_y, 175, 38))
    p.append(draw_state("s2_ok", "ApartandoStockSucursal", right_x, b_y, 195, 38))
    p.append(draw_diag_arrow(cx - 50, 193, left_x + 30, b_y, "[Sin stock disponible]", left_x - 70, 225))
    p.append(draw_diag_arrow(cx + 50, 193, right_x - 30, b_y, "[Stock disponible]", cx + 60, 225))

    # Rama de éxito continúa con Bitácora y Estado 48h
    p.append(draw_down_arrow(right_x, b_y + 38, 365, "registrar_bitacora(\"RESERVA\")"))
    p.append(draw_state("s3", "BitacoraReservaAsentada", right_x, 365, 205, 38))
    p.append(draw_down_arrow(right_x, 403, 470, "generar_codigo_qr_48h()"))
    p.append(draw_state("s4", "ReservaActivaVencimiento48h", right_x, 470, 225, 38))

    # Convergencia
    p.append(draw_final(cx, 610))
    p.append(draw_diag_arrow(left_x, b_y + 38, cx - 18, 600))
    p.append(draw_diag_arrow(right_x - 40, 508, cx + 18, 600))
    p.append('</svg>\n')
    return "".join(p)


def make_cu11():
    # Topología: Drill-down de Historial con Filtro por Estado (Sin bitácora)
    w, h, cx = 720, 680, 360
    p = svg_header(w, h, "CU11 W/M: Consultar pedidos e historial")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "abrir_historial_pedidos()"))
    p.append(draw_state("s1", "ListadoPedidosCargado", cx, 155, 200, 38))
    # Bucle de filtrado
    p.append(draw_loop_arrow(cx, 155, 200, 38, "filtrar_por_estado(entregado/camino)", side="right"))
    p.append(draw_down_arrow(cx, 193, 280, "seleccionar_pedido(id_pedido)"))
    p.append(draw_state("s2", "DetallePedidoExpandido", cx, 280, 210, 38))
    p.append(draw_down_arrow(cx, 318, 405, "consultar_tracking_envio()"))
    p.append(draw_state("s3", "TimelineTrackingVisible", cx, 405, 210, 38))
    p.append(draw_down_arrow(cx, 443, 530, "cerrar_detalle()"))
    p.append(draw_final(cx, 595))
    p.append('</svg>\n')
    return "".join(p)


def make_cu26_m15():
    # Topología: Mapa interactivo con selección de pines y trazado de ruta
    w, h, cx = 740, 700, 370
    p = svg_header(w, h, "CU26/M15 W/M: Mostrar ubicaciones de sucursales")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "abrir_mapa_tiendas()"))
    p.append(draw_state("s1", "GeolocalizandoUsuario", cx, 155, 195, 38))
    p.append(draw_down_arrow(cx, 193, 260, "cargar_sucursales_cercanas()"))
    p.append(draw_state("s2", "PinesRenderizadosEnMapa", cx, 260, 215, 38))
    # Bucle interactivo de tocar pines
    p.append(draw_loop_arrow(cx, 260, 215, 38, "click_marcador_tienda()", side="right"))
    p.append(draw_down_arrow(cx, 298, 385, "seleccionar_tienda_destino()"))
    p.append(draw_state("s3", "InfoSucursalYHorariosVisible", cx, 385, 235, 38))
    p.append(draw_down_arrow(cx, 423, 510, "trazar_ruta_gps()"))
    p.append(draw_state("s4", "RutaNavegacionActiva", cx, 510, 195, 38))
    p.append(draw_down_arrow(cx, 548, 615, "finalizar_consulta()"))
    p.append(draw_final(cx, 630))
    p.append('</svg>\n')
    return "".join(p)


def make_cu_w20():
    # Topología: Validación de Rango de Fechas con Bucle de Corrección y Bitácora Admin
    w, h, cx = 760, 720, 380
    p = svg_header(w, h, "CU_W20: Gestionar temporadas y colecciones")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "abrir_formulario_coleccion()"))
    p.append(draw_state("s1", "CapturandoDatosColeccion", cx, 155, 220, 38))
    p.append(draw_down_arrow(cx, 193, 265, "validar_fechas_vigencia()"))
    p.append(draw_state("s2", "ValidandoPeriodo", cx, 265, 185, 38))
    
    # Bifurcación: Error fechas vs Fechas válidas
    left_x, right_x, b_y = 190, 530, 380
    p.append(draw_state("s3_err", "ErrorRangoFechas", left_x, b_y, 175, 38))
    p.append(draw_state("s3_ok", "ColeccionPersistida", right_x, b_y, 185, 38))

    p.append(draw_diag_arrow(cx - 40, 303, left_x + 30, b_y, "[Fechas inconsistentes]", left_x - 70, 340))
    p.append(draw_diag_arrow(cx + 40, 303, right_x - 30, b_y, "[Periodo coherente]", cx + 60, 340))

    # Bucle de reintento desde ErrorRangoFechas hacia CapturandoDatosColeccion
    p.append(draw_curve_arrow(left_x, b_y, left_x - 80, 200, cx - 110, 174, "corregir_fechas()", left_x - 120, 230))

    # Rama derecha continúa con Bitácora
    p.append(draw_down_arrow(right_x, b_y + 38, 485, "registrar_bitacora(\"COLECCION\")"))
    p.append(draw_state("s4", "BitacoraColeccionRegistrada", right_x, 485, 215, 38))

    p.append(draw_final(cx, 630))
    p.append(draw_diag_arrow(right_x - 20, 523, cx + 18, 620))
    p.append('</svg>\n')
    return "".join(p)


def make_cu_w21():
    # Topología: Validación de NIT Duplicado con Reintento y Bitácora
    w, h, cx = 760, 720, 380
    p = svg_header(w, h, "CU_W21: Gestionar proveedores")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "ingresar_datos_proveedor(nit, razon)"))
    p.append(draw_state("s1", "FormularioProveedorActivo", cx, 155, 215, 38))
    p.append(draw_down_arrow(cx, 193, 265, "verificar_nit_existente(nit)"))
    p.append(draw_state("s2", "VerificandoUnicidadNIT", cx, 265, 195, 38))

    # Bifurcación
    left_x, right_x, b_y = 190, 530, 380
    p.append(draw_state("s3_err", "DuplicidadNITDetectada", left_x, b_y, 185, 38))
    p.append(draw_state("s3_ok", "ProveedorGuardado", right_x, b_y, 180, 38))

    p.append(draw_diag_arrow(cx - 40, 303, left_x + 30, b_y, "[NIT ya registrado]", left_x - 70, 340))
    p.append(draw_diag_arrow(cx + 40, 303, right_x - 30, b_y, "[NIT disponible]", cx + 60, 340))

    # Bucle de corrección
    p.append(draw_curve_arrow(left_x, b_y, left_x - 80, 200, cx - 108, 174, "cambiar_nit()", left_x - 110, 230))

    p.append(draw_down_arrow(right_x, b_y + 38, 485, "registrar_bitacora(\"PROVEEDOR\")"))
    p.append(draw_state("s4", "BitacoraProveedorRegistrada", right_x, 485, 215, 38))

    p.append(draw_final(cx, 630))
    p.append(draw_diag_arrow(right_x - 20, 523, cx + 18, 620))
    p.append('</svg>\n')
    return "".join(p)


def make_cu_w22():
    # Topología: 3 Tipos de Movimiento Kardex (Ingreso / Merma / Transferencia) que convergen a Bitácora
    w, h, cx = 820, 720, 410
    p = svg_header(w, h, "CU_W22: Gestionar inventario")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "abrir_modulo_kardex()"))
    p.append(draw_state("s1", "SeleccionandoTipoMovimiento", cx, 155, 235, 38))
    
    # 3 Ramas de Movimiento:
    x_ing, x_mer, x_tra = 170, 410, 650
    y_mov = 280
    p.append(draw_state("s2_ing", "IngresoPorCompra", x_ing, y_mov, 170, 38))
    p.append(draw_state("s2_mer", "BajaPorMerma", x_mer, y_mov, 160, 38))
    p.append(draw_state("s2_tra", "TransferenciaTiendas", x_tra, y_mov, 180, 38))

    p.append(draw_diag_arrow(cx - 60, 193, x_ing + 40, y_mov, "[Tipo Entrada]", x_ing - 20, 235))
    p.append(draw_down_arrow(cx, 193, y_mov, "[Tipo Salida]"))
    p.append(draw_diag_arrow(cx + 60, 193, x_tra - 40, y_mov, "[Tipo Traspaso]", cx + 115, 230))

    # Convergencia a Actualización Kardex
    y_kdx = 410
    p.append(draw_state("s3", "SaldoKardexActualizado", cx, y_kdx, 205, 38))
    p.append(draw_diag_arrow(x_ing + 20, y_mov + 38, cx - 40, y_kdx))
    p.append(draw_down_arrow(cx, y_mov + 38, y_kdx))
    p.append(draw_diag_arrow(x_tra - 20, y_mov + 38, cx + 40, y_kdx))

    # Bitácora
    p.append(draw_down_arrow(cx, y_kdx + 38, 520, "registrar_bitacora(\"KARDEX\")"))
    p.append(draw_state("s4", "BitacoraInventarioAsentada", cx, 520, 215, 38))
    p.append(draw_down_arrow(cx, 558, 630))
    p.append(draw_final(cx, 645))
    p.append('</svg>\n')
    return "".join(p)


def make_cu_w23():
    # Topología: Toggle de Reglas de Disponibilidad con Auditoría
    w, h, cx = 720, 680, 360
    p = svg_header(w, h, "CU_W23: Gestionar disponibilidad de prendas")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "cargar_matriz_disponibilidad()"))
    p.append(draw_state("s1", "MatrizDisponibilidadCargada", cx, 155, 230, 38))
    # Bucle toggle
    p.append(draw_loop_arrow(cx, 155, 230, 38, "toggle_visibilidad_sucursal()", side="right"))
    p.append(draw_down_arrow(cx, 193, 275, "aplicar_regla_comercial()"))
    p.append(draw_state("s2", "VerificandoPoliticaCatalogo", cx, 275, 220, 38))
    p.append(draw_down_arrow(cx, 313, 395, "persistir_disponibilidad_db()"))
    p.append(draw_state("s3", "ReglaDisponibilidadPersistida", cx, 395, 235, 38))
    p.append(draw_down_arrow(cx, 433, 515, "registrar_bitacora(\"DISPONIBILIDAD\")"))
    p.append(draw_state("s4", "BitacoraReglaAsentada", cx, 515, 215, 38))
    p.append(draw_down_arrow(cx, 553, 620))
    p.append(draw_final(cx, 635))
    p.append('</svg>\n')
    return "".join(p)


def make_cu_w24():
    # Topología: Bucle de Escaneo de Códigos de Barra, Descuento, Cierre POS y Bitácora
    w, h, cx = 740, 740, 370
    p = svg_header(w, h, "CU_W24: Registrar venta presencial POS")
    p.append(draw_initial(cx, 90))
    p.append(draw_down_arrow(cx, 101, 150, "abrir_terminal_pos()"))
    p.append(draw_state("s1", "TerminalPOSListo", cx, 150, 185, 38))
    p.append(draw_down_arrow(cx, 188, 250, "iniciar_escaneo()"))
    p.append(draw_state("s2", "EscaneandoPrendas", cx, 250, 195, 38))
    # Bucle de escaneo de artículos
    p.append(draw_loop_arrow(cx, 250, 195, 38, "escanear_codigo_barra() / sumar_item()", side="right"))
    p.append(draw_down_arrow(cx, 288, 370, "confirmar_total_articulos()"))
    p.append(draw_state("s3", "VentaAsentadaEnCaja", cx, 370, 205, 38))
    p.append(draw_down_arrow(cx, 408, 480, "descontar_stock_inmediato()"))
    p.append(draw_state("s4", "StockFisicoDescontado", cx, 480, 210, 38))
    p.append(draw_down_arrow(cx, 518, 590, "registrar_bitacora(\"VENTA_POS\")"))
    p.append(draw_state("s5", "BitacoraVentaPOSRegistrada", cx, 590, 225, 38))
    p.append(draw_down_arrow(cx, 628, 685, "emitir_ticket_caja()"))
    p.append(draw_final(cx, 700))
    p.append('</svg>\n')
    return "".join(p)


def make_cu_w25():
    # Topología: Validación de Reserva en Tienda (Vencida > 48h / Ya entregada / Válida para entrega)
    w, h, cx = 780, 700, 390
    p = svg_header(w, h, "CU_W25: Atender reservas en sucursal")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "escanear_o_buscar_codigo_reserva()"))
    p.append(draw_state("s1", "ConsultandoEstadoReserva", cx, 155, 225, 38))

    # 3 Ramas
    x_venc, x_inval, x_ok = 160, 390, 620
    y_eval = 280
    p.append(draw_state("s2_venc", "ReservaCaducada48h", x_venc, y_eval, 180, 38))
    p.append(draw_state("s2_inval", "ReservaInvalida", x_inval, y_eval, 160, 38))
    p.append(draw_state("s2_ok", "PrendaListaParaEntrega", x_ok, y_eval, 200, 38))

    p.append(draw_diag_arrow(cx - 60, 193, x_venc + 40, y_eval, "[Vencida > 48h] / liberar_stock()", x_venc - 40, 235))
    p.append(draw_down_arrow(cx, 193, y_eval, "[Ya entregada]"))
    p.append(draw_diag_arrow(cx + 60, 193, x_ok - 40, y_eval, "[Vigente y confirmada]", cx + 70, 235))

    # Rama derecha continúa con entrega y bitácora
    p.append(draw_down_arrow(x_ok, y_eval + 38, 410, "confirmar_entrega_al_cliente()"))
    p.append(draw_state("s3", "PrendaEntregadaFisicamente", x_ok, 410, 220, 38))
    p.append(draw_down_arrow(x_ok, 448, 520, "registrar_bitacora(\"ENTREGA\")"))
    p.append(draw_state("s4", "BitacoraEntregaAsentada", x_ok, 520, 210, 38))

    p.append(draw_final(cx, 630))
    p.append(draw_diag_arrow(x_venc + 20, y_eval + 38, cx - 20, 620))
    p.append(draw_down_arrow(cx, y_eval + 38, 616))
    p.append(draw_diag_arrow(x_ok - 30, 558, cx + 20, 620))
    p.append('</svg>\n')
    return "".join(p)


def make_cu_w27():
    # Topología: Pasarela Electrónica con Desafío 3D-Secure, Rechazo y Aprobación
    w, h, cx = 780, 720, 390
    p = svg_header(w, h, "CU_W27: Procesar pago electrónico")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "iniciar_pago_tarjeta(datos_cifrados)"))
    p.append(draw_state("s1", "ConectandoPasarelaStripe", cx, 155, 225, 38))

    # 3 Ramas de Pasarela:
    x_rech, x_3ds, x_apr = 160, 390, 620
    y_gate = 280
    p.append(draw_state("s2_rech", "PagoRechazadoBanco", x_rech, y_gate, 185, 38))
    p.append(draw_state("s2_3ds", "Desafio3DSecure", x_3ds, y_gate, 175, 38))
    p.append(draw_state("s2_apr", "TransaccionAprobada", x_apr, y_gate, 185, 38))

    p.append(draw_diag_arrow(cx - 60, 193, x_rech + 40, y_gate, "[Fondos insuficientes]", x_rech - 40, 235))
    p.append(draw_down_arrow(cx, 193, y_gate, "[Requiere OTP / 3DS]"))
    p.append(draw_diag_arrow(cx + 60, 193, x_apr - 40, y_gate, "[Cobro exitoso]", cx + 70, 235))

    # Bucle de verificación de 3DS hacia Aprobada
    p.append(draw_diag_arrow(x_3ds + 40, y_gate + 38, x_apr - 40, 420, "validar_otp_bancario()", x_3ds + 60, 360))

    # Rama aprobada continúa con Bitácora
    p.append(draw_down_arrow(x_apr, y_gate + 38, 420))
    p.append(draw_state("s3", "TokenTransaccionGenerado", x_apr, 420, 215, 38))
    p.append(draw_down_arrow(x_apr, 458, 530, "registrar_bitacora(\"PAGO_STRIPE\")"))
    p.append(draw_state("s4", "BitacoraPagoAsentada", x_apr, 530, 205, 38))

    p.append(draw_final(cx, 640))
    p.append(draw_diag_arrow(x_rech + 20, y_gate + 38, cx - 20, 630))
    p.append(draw_diag_arrow(x_apr - 30, 568, cx + 20, 630))
    p.append('</svg>\n')
    return "".join(p)


def make_cu_w28():
    # Topología: Pago en Caja con Reintento por Monto Insuficiente, Apertura Gaveta y Cambio
    w, h, cx = 760, 720, 380
    p = svg_header(w, h, "CU_W28: Procesar pago en caja")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "ingresar_efectivo_recibido(monto)"))
    p.append(draw_state("s1", "CalculandoCambioEfectivo", cx, 155, 225, 38))

    # Bifurcación
    left_x, right_x, b_y = 190, 530, 275
    p.append(draw_state("s2_err", "MontoInsuficiente", left_x, b_y, 175, 38))
    p.append(draw_state("s2_ok", "GavetaDineroAbierta", right_x, b_y, 195, 38))

    p.append(draw_diag_arrow(cx - 40, 193, left_x + 30, b_y, "[Monto menor al total]", left_x - 70, 230))
    p.append(draw_diag_arrow(cx + 40, 193, right_x - 30, b_y, "[Monto suficiente]", cx + 60, 230))

    # Bucle de reintento si monto insuficiente
    p.append(draw_curve_arrow(left_x, b_y, left_x - 80, 200, cx - 110, 174, "solicitar_monto_restante()", left_x - 130, 220))

    # Rama derecha continúa con arqueo y bitácora
    p.append(draw_down_arrow(right_x, b_y + 38, 385, "asentar_pago_en_caja()"))
    p.append(draw_state("s3", "MovimientoCajaRegistrado", right_x, 385, 215, 38))
    p.append(draw_down_arrow(right_x, 423, 500, "registrar_bitacora(\"COBRO_CAJA\")"))
    p.append(draw_state("s4", "BitacoraCajaAsentada", right_x, 500, 205, 38))
    p.append(draw_down_arrow(right_x, 538, 605, "entregar_cambio_al_cliente()"))

    p.append(draw_final(cx, 650))
    p.append(draw_diag_arrow(right_x - 20, 620, cx + 18, 642))
    p.append('</svg>\n')
    return "".join(p)


def make_cu_w29():
    # Topología: Bifurcación Factura Fiscal (con validación NIT/CUF) vs Recibo de Venta
    w, h, cx = 800, 720, 400
    p = svg_header(w, h, "CU_W29: Emitir comprobante de venta")
    p.append(draw_initial(cx, 95))
    p.append(draw_down_arrow(cx, 106, 155, "solicitar_comprobante(tipo)"))
    p.append(draw_state("s1", "EligiendoTipoComprobante", cx, 155, 225, 38))

    # 2 Ramas: Factura con NIT vs Recibo de Venta
    x_fac, x_rec = 230, 570
    y_tipo = 280
    p.append(draw_state("s2_fac", "FacturaFiscalValidandoNIT", x_fac, y_tipo, 215, 38))
    p.append(draw_state("s2_rec", "ReciboCorrelativoInterno", x_rec, y_tipo, 205, 38))

    p.append(draw_diag_arrow(cx - 50, 193, x_fac + 40, y_tipo, "[Es Factura con NIT]", x_fac - 50, 235))
    p.append(draw_diag_arrow(cx + 50, 193, x_rec - 40, y_tipo, "[Es Recibo Simple]", cx + 60, 235))

    # Rama factura firma CUF
    p.append(draw_down_arrow(x_fac, y_tipo + 38, 395, "firmar_digitalmente_cuf()"))
    p.append(draw_state("s3_fac", "FacturaSelladaDigitalmente", x_fac, 395, 225, 38))

    # Convergencia a Impresión Térmica y Bitácora
    y_imp = 500
    p.append(draw_state("s4", "ImprimiendoTicketFiscal", cx, y_imp, 205, 38))
    p.append(draw_diag_arrow(x_fac + 20, 433, cx - 40, y_imp, "enviar_a_impresora()", x_fac + 40, 470))
    p.append(draw_diag_arrow(x_rec - 20, y_tipo + 38, cx + 40, y_imp, "enviar_a_impresora()", cx + 70, 460))

    p.append(draw_down_arrow(cx, y_imp + 38, 595, "registrar_bitacora(\"COMPROBANTE\")"))
    p.append(draw_state("s5", "BitacoraFiscalAsentada", cx, 595, 215, 38))
    p.append(draw_down_arrow(cx, 633, 675))
    p.append(draw_final(cx, 690))
    p.append('</svg>\n')
    return "".join(p)


# ==============================================================================
# EJECUCIÓN MAESTRA Y GENERACIÓN VECTORIAL / RASTER
# ==============================================================================

CASOS_DE_USO = [
    ("CU05_WM", "CU05_WM_Buscar_Filtrar_Productos_Estado", make_cu05),
    ("CU06_WM", "CU06_WM_Consultar_Detalle_Producto_Estado", make_cu06),
    ("CU07_WM", "CU07_WM_Consultar_Disponibilidad_Sucursal_Estado", make_cu07),
    ("CU08_WM", "CU08_WM_Gestionar_Carrito_Compras_Estado", make_cu08),
    ("CU09_WM", "CU09_WM_Realizar_Compra_Estado", make_cu09),
    ("CU10_WM", "CU10_WM_Gestionar_Reservas_Estado", make_cu10),
    ("CU11_WM", "CU11_WM_Consultar_Pedidos_Historial_Estado", make_cu11),
    ("CU26_M15_WM", "CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Estado", make_cu26_m15),
    ("CU_W20", "CU_W20_Gestionar_Temporadas_Colecciones_Estado", make_cu_w20),
    ("CU_W21", "CU_W21_Gestionar_Proveedores_Estado", make_cu_w21),
    ("CU_W22", "CU_W22_Gestionar_Inventario_Estado", make_cu_w22),
    ("CU_W23", "CU_W23_Gestionar_Disponibilidad_Prendas_Estado", make_cu_w23),
    ("CU_W24", "CU_W24_Registrar_Venta_Presencial_Estado", make_cu_w24),
    ("CU_W25", "CU_W25_Atender_Reservas_Estado", make_cu_w25),
    ("CU_W27", "CU_W27_Procesar_Pago_Electronico_Estado", make_cu_w27),
    ("CU_W28", "CU_W28_Procesar_Pago_Caja_Estado", make_cu_w28),
    ("CU_W29", "CU_W29_Emitir_Comprobante_Venta_Estado", make_cu_w29),
]

def main():
    out_dir = "/home/eddy/Escritorio/PROYECTOS/EP1-SI2/Examen_parcial1_S12/docs/diagramas_estado"
    os.makedirs(out_dir, exist_ok=True)

    print(f"=== INICIANDO GENERACIÓN DE {len(CASOS_DE_USO)} DIAGRAMAS DE ESTADO UML 2.5 ===")
    for idx, (cid, fname, gen_func) in enumerate(CASOS_DE_USO, 1):
        svg_content = gen_func()
        svg_path = os.path.join(out_dir, f"{fname}.svg")
        png_path = os.path.join(out_dir, f"{fname}.png")

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        cairosvg.svg2png(bytestring=svg_content.encode("utf-8"), write_to=png_path, scale=2.0)
        print(f"[{idx:02d}/17 OK] SVG & PNG (2x): {fname}")

    print("\n¡Todos los 17 Diagramas de Estado generados exitosamente con topologías diferenciadas!")

if __name__ == "__main__":
    main()
