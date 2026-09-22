#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de los 8 Diagramas de Secuencia UML Restantes (SI2 - UAGRM)
Basado en la BASE DE DATOS ACTUALIZADA y con FLUJOS Y OPERADORES DIFERENCIADOS:

1. CU/W13: Interactuar con asistente inteligente (Web) -> alt (Simple vs Tool Function Calling), opt (T_VENTA / T_SUCURSAL)
2. CU/W30: Gestionar promociones (Web) -> alt (Fechas Válidas vs Solapamiento), loop (Prendas vinculadas), opt (T_BITACORA)
3. CU/W31: Consultar ventas, reservas e inventario (Web) -> loop (Sucursales), opt (Alertas Stock en T_INVENTARIO), alt (Con Actividad vs Sin Actividad)
4. CU/W32: Visualizar indicadores empresariales (Web) -> loop (Cálculo Diario/Mensual), alt (Canal POS vs Online), opt (Comparativa Anual)
5. CU/W33: Generar reportes bajo demanda (Web) -> alt (PDF ReportLab vs Excel OpenPyXL), opt (Kardex Movimientos), opt (T_BITACORA)
6. CU/M12: Obtener recomendaciones de productos (Mobile) -> alt (Cache Local vs Backend Sync), loop (Cards Nativas), opt (T_HISTORIAL_NAVEGACION)
7. CU/M13: Interactuar con asistente inteligente (Mobile) -> alt (Audio Voz STT vs Texto), alt (Tracking Pedido vs Consulta Reserva), opt (TTS Audio)
8. CU/M14: Utilizar vestidor virtual (Mobile RA) -> loop (Frames Cámara 60FPS), alt (Cuerpo Detectado vs Fuera de Encuadre), opt (Textura Cloudinary), opt (T_VESTIDOR_VIRTUAL)

Genera SVG y renderiza PNG 2x con resvg_py.
"""

import os
import shutil
import resvg_py

def escape_xml(s):
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))

# ==================== GENERADOR CU/W13 ====================
def generate_cu_w13_svg():
    width = 1420
    height = 920
    x_actor = 80
    x_iu = 250
    x_ctrl = 460
    x_ai = 680
    x_repo = 910
    x_prod = 1080
    x_venta = 1220
    x_suc = 1350

    y_header = 85
    h_box = 36
    w_box = 120
    y_line_start = y_header + h_box
    y_line_end = 880

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow_sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/>
    </marker>
    <marker id="arrow_return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9" fill="none" stroke="#000000" stroke-width="1.4"/>
    </marker>
  </defs>

  <!-- Marco Exterior -->
  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <path d="M 15 15 L 470 15 L 485 35 L 485 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12.5" font-weight="bold" fill="#000000">CU/W13: Interactuar con asistente inteligente (DeepSeek AI)</text>

  <!-- Participantes -->
  <g transform="translate({x_actor}, 55)">
    <circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/>
    <line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/>
    <text x="0" y="78" font-size="11" font-weight="bold" text-anchor="middle">CLIENTE</text>
  </g>

  <g><rect x="{x_iu - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_iu}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">IU_AsistenteChat</text></g>
  <g><rect x="{x_ctrl - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_ctrl}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">asistente_routes</text></g>
  <g><rect x="{x_ai - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_ai}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">DeepSeek_AI_Service</text></g>
  <g><rect x="{x_repo - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_repo}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">asistente_repos</text></g>
  <g><rect x="{x_prod - 55}" y="{y_header}" width="110" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_prod}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">T_PRODUCTO</text></g>
  <g><rect x="{x_venta - 50}" y="{y_header}" width="100" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_venta}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_VENTA</text></g>
  <g><rect x="{x_suc - 50}" y="{y_header}" width="100" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_suc}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_SUCURSAL</text></g>

  <!-- Líneas de vida -->
  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_iu}" y1="{y_line_start}" x2="{x_iu}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_ctrl}" y1="{y_line_start}" x2="{x_ctrl}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_ai}" y1="{y_line_start}" x2="{x_ai}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_repo}" y1="{y_line_start}" x2="{x_repo}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_prod}" y1="{y_line_start}" x2="{x_prod}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_venta}" y1="{y_line_start}" x2="{x_venta}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_suc}" y1="{y_line_start}" x2="{x_suc}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <!-- Barras activación -->
  <rect x="{x_iu - 6}" y="155" width="12" height="695" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_ctrl - 6}" y="185" width="12" height="635" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_ai - 6}" y="215" width="12" height="575" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_repo - 6}" y="365" width="12" height="345" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_prod - 6}" y="390" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_venta - 6}" y="525" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_suc - 6}" y="650" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- 1: Enviar mensaje -->
  <line x1="{x_actor}" y1="160" x2="{x_iu - 6}" y2="160" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_actor + x_iu)/2}" y="152" font-size="10.5" text-anchor="middle">1: EnviarMensaje("¿Tienen blusas de seda en stock?")</text>

  <!-- 2: POST /chat -->
  <line x1="{x_iu + 6}" y1="190" x2="{x_ctrl - 6}" y2="190" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="182" font-size="10.5" text-anchor="middle">2: POST /api/asistente/chat</text>

  <!-- 3: Procesar con DeepSeek -->
  <line x1="{x_ctrl + 6}" y1="220" x2="{x_ai - 6}" y2="220" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_ctrl + x_ai)/2}" y="212" font-size="10.5" text-anchor="middle">3: procesar_mensaje_chat(msg, historial)</text>

  <!-- Fragmento ALT: Charla simple vs Function Calling BD -->
  <rect x="35" y="240" width="{width - 60}" height="495" fill="none" stroke="#000000" stroke-width="1.3"/>
  <path d="M 35 240 L 90 240 L 100 257 L 100 265 L 35 265 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="65" y="257" font-size="11" font-weight="bold" text-anchor="middle">alt</text>
  <text x="110" y="258" font-size="10.5" font-weight="bold">[RESPUESTA CONVERSACIONAL SIMPLE SIN TOOLS]</text>

  <path d="M {x_ai + 6} 270 L {x_ai + 45} 270 L {x_ai + 45} 295 L {x_ai + 8} 295" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{x_ai + 52}" y="285" font-size="10" text-anchor="start">4: generar_respuesta_texto_directa()</text>

  <!-- Línea divisoria alt -->
  <line x1="35" y1="315" x2="{width - 25}" y2="315" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>
  <text x="50" y="332" font-size="10.5" font-weight="bold">[FUNCTION CALLING REQUERIDO: CONSULTAS EN BASE DE DATOS]</text>

  <!-- 5: Despachar Tool -->
  <line x1="{x_ai + 6}" y1="355" x2="{x_repo - 6}" y2="355" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_ai + x_repo)/2}" y="347" font-size="10" text-anchor="middle">5: ejecutar_herramienta('buscar_prendas_catalogo', params)</text>

  <!-- 6: Query T_PRODUCTO -->
  <line x1="{x_repo + 6}" y1="390" x2="{x_prod - 6}" y2="390" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_prod)/2}" y="382" font-size="9.5" text-anchor="middle">6: SELECT * FROM T_PRODUCTO</text>

  <line x1="{x_prod - 6}" y1="415" x2="{x_repo + 6}" y2="415" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_repo + x_prod)/2}" y="407" font-size="9" text-anchor="middle">7: return prendas_encontradas</text>

  <!-- OPT: Consultar compras si el cliente pide su pedido -->
  <rect x="50" y="445" width="{width - 90}" height="120" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 445 L 95 445 L 105 460 L 105 467 L 50 467 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="460" font-size="10" font-weight="bold" text-anchor="middle">opt</text>
  <text x="115" y="461" font-size="10" font-weight="bold">[SI PREGUNTA POR ESTADO DE COMPRA / TRACKING]</text>

  <line x1="{x_repo + 6}" y1="490" x2="{x_venta - 6}" y2="490" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_venta)/2}" y="482" font-size="9.5" text-anchor="middle">8: SELECT * FROM T_VENTA WHERE ID_CLIENTE = ?</text>

  <line x1="{x_venta - 6}" y1="520" x2="{x_repo + 6}" y2="520" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_repo + x_venta)/2}" y="512" font-size="9.5" text-anchor="middle">9: return estado_compras_recientes</text>

  <!-- OPT: Consultar tiendas físicas -->
  <rect x="50" y="580" width="{width - 90}" height="115" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 580 L 95 580 L 105 595 L 105 602 L 50 602 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="595" font-size="10" font-weight="bold" text-anchor="middle">opt</text>
  <text x="115" y="596" font-size="10" font-weight="bold">[SI CONSULTA TIENDAS FÍSICAS O DIRECCIONES]</text>

  <line x1="{x_repo + 6}" y1="625" x2="{x_suc - 6}" y2="625" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_suc)/2}" y="617" font-size="9.5" text-anchor="middle">10: SELECT * FROM T_SUCURSAL WHERE ESTADO = 'ACTIVO'</text>

  <line x1="{x_suc - 6}" y1="655" x2="{x_repo + 6}" y2="655" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_repo + x_suc)/2}" y="647" font-size="9.5" text-anchor="middle">11: return lista_sucursales_horarios</text>

  <!-- Retorno Tools a DeepSeek -->
  <line x1="{x_repo - 6}" y1="715" x2="{x_ai + 6}" y2="715" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_ai + x_repo)/2}" y="707" font-size="10" text-anchor="middle">12: return resultado_datos_herramienta</text>

  <!-- Retornos finales -->
  <line x1="{x_ai - 6}" y1="760" x2="{x_ctrl + 6}" y2="760" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_ctrl + x_ai)/2}" y="752" font-size="10" text-anchor="middle">13: return respuesta_sintetizada_ia(texto, datos_cards)</text>

  <line x1="{x_ctrl - 6}" y1="795" x2="{x_iu + 6}" y2="795" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="787" font-size="10" text-anchor="middle">14: HTTP 200 OK (payload_chat_cards)</text>

  <line x1="{x_iu - 6}" y1="835" x2="{x_actor}" y2="835" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_actor + x_iu)/2}" y="827" font-size="10" text-anchor="middle">15: DesplegarBurbujaAsistente(texto, cards_prendas)</text>

</svg>
''')
    return "".join(svg)

# ==================== GENERADOR CU/W30 ====================
def generate_cu_w30_svg():
    width = 1380
    height = 920
    x_actor = 80
    x_iu = 260
    x_ctrl = 480
    x_srv = 720
    x_repo = 960
    x_prom = 1140
    x_bit = 1300

    y_header = 85
    h_box = 36
    y_line_start = y_header + h_box
    y_line_end = 880

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow_sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/></marker>
    <marker id="arrow_return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 1 L 10 5 L 0 9" fill="none" stroke="#000000" stroke-width="1.4"/></marker>
  </defs>

  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <path d="M 15 15 L 430 15 L 445 35 L 445 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12.5" font-weight="bold">CU/W30: Gestionar promociones</text>

  <g transform="translate({x_actor}, 55)"><circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/><line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/><text x="0" y="78" font-size="10.5" font-weight="bold" text-anchor="middle">ADMIN_TIENDA</text></g>

  <g><rect x="{x_iu - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_iu}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">IU_Promociones</text></g>
  <g><rect x="{x_ctrl - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_ctrl}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">productos_routes</text></g>
  <g><rect x="{x_srv - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_srv}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">productos_services</text></g>
  <g><rect x="{x_repo - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_repo}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">productos_repos</text></g>
  <g><rect x="{x_prom - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_prom}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">T_PROMOCION</text></g>
  <g><rect x="{x_bit - 55}" y="{y_header}" width="110" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_bit}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_BITACORA</text></g>

  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_iu}" y1="{y_line_start}" x2="{x_iu}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_ctrl}" y1="{y_line_start}" x2="{x_ctrl}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_srv}" y1="{y_line_start}" x2="{x_srv}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_repo}" y1="{y_line_start}" x2="{x_repo}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_prom}" y1="{y_line_start}" x2="{x_prom}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_bit}" y1="{y_line_start}" x2="{x_bit}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <rect x="{x_iu - 6}" y="155" width="12" height="695" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_ctrl - 6}" y="185" width="12" height="635" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_srv - 6}" y="215" width="12" height="575" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_repo - 6}" y="360" width="12" height="340" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_prom - 6}" y="390" width="12" height="150" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_bit - 6}" y="650" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- 1: Crear promocion -->
  <line x1="{x_actor}" y1="160" x2="{x_iu - 6}" y2="160" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_actor + x_iu)/2}" y="152" font-size="10.5" text-anchor="middle">1: GuardarPromocion(nombre, %descuento, fechas, prendas)</text>

  <!-- 2: POST /promocion -->
  <line x1="{x_iu + 6}" y1="190" x2="{x_ctrl - 6}" y2="190" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="182" font-size="10.5" text-anchor="middle">2: POST /api/productos/promocion</text>

  <!-- 3: Validar reglas -->
  <line x1="{x_ctrl + 6}" y1="220" x2="{x_srv - 6}" y2="220" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_ctrl + x_srv)/2}" y="212" font-size="10.5" text-anchor="middle">3: asignar_promocion_producto_service(datos)</text>

  <!-- Fragmento ALT: Fechas válidas vs Solapamiento -->
  <rect x="35" y="240" width="{width - 60}" height="490" fill="none" stroke="#000000" stroke-width="1.3"/>
  <path d="M 35 240 L 90 240 L 100 257 L 100 265 L 35 265 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="65" y="257" font-size="11" font-weight="bold" text-anchor="middle">alt</text>
  <text x="110" y="258" font-size="10.5" font-weight="bold">[FECHAS VÁLIDAS Y SIN SOLAPAMIENTO DE CAMPAÑA]</text>

  <line x1="{x_srv + 6}" y1="280" x2="{x_repo - 6}" y2="280" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_srv + x_repo)/2}" y="272" font-size="10" text-anchor="middle">4: validar_no_solapamiento_vigencia(fechas)</text>

  <line x1="{x_repo - 6}" y1="305" x2="{x_srv + 6}" y2="305" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_srv + x_repo)/2}" y="297" font-size="10" text-anchor="middle">5: return ok_sin_conflicto</text>

  <!-- 6: Insert T_PROMOCION -->
  <line x1="{x_srv + 6}" y1="335" x2="{x_repo - 6}" y2="335" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_srv + x_repo)/2}" y="327" font-size="10" text-anchor="middle">6: registrar_promocion(cabecera_promo)</text>

  <line x1="{x_repo + 6}" y1="365" x2="{x_prom - 6}" y2="365" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_prom)/2}" y="357" font-size="9.5" text-anchor="middle">7: INSERT INTO T_PROMOCION</text>

  <line x1="{x_prom - 6}" y1="395" x2="{x_repo + 6}" y2="395" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_repo + x_prom)/2}" y="387" font-size="9.5" text-anchor="middle">8: return id_promocion_generado</text>

  <!-- LOOP: Vincular cada prenda -->
  <rect x="50" y="420" width="{width - 90}" height="100" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 420 L 95 420 L 105 435 L 105 442 L 50 442 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="435" font-size="10" font-weight="bold" text-anchor="middle">loop</text>
  <text x="115" y="436" font-size="10" font-weight="bold">[POR CADA PRENDA SELECCIONADA PARA LA PROMOCIÓN]</text>

  <line x1="{x_repo + 6}" y1="465" x2="{x_prom - 6}" y2="465" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_prom)/2}" y="457" font-size="9.5" text-anchor="middle">9: INSERT INTO T_PROMOCION_PRODUCTO (id_promo, id_producto, %)</text>

  <line x1="{x_prom - 6}" y1="495" x2="{x_repo + 6}" y2="495" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_repo + x_prom)/2}" y="487" font-size="9.5" text-anchor="middle">10: return confirmacion_vinculacion</text>

  <!-- OPT: Auditoría en Bitácora -->
  <rect x="50" y="535" width="{width - 90}" height="70" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 535 L 95 535 L 105 550 L 105 557 L 50 557 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="550" font-size="10" font-weight="bold" text-anchor="middle">opt</text>
  <text x="115" y="551" font-size="10" font-weight="bold">[AUDITAR REGISTRO DE PROMOCIÓN]</text>

  <line x1="{x_repo + 6}" y1="575" x2="{x_bit - 6}" y2="575" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_bit)/2}" y="567" font-size="9.5" text-anchor="middle">11: INSERT INTO T_BITACORA ('CREAR_PROMOCION', user_id)</text>

  <!-- Rama 2 ALT: Solapamiento -->
  <line x1="35" y1="620" x2="{width - 25}" y2="620" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>
  <text x="50" y="637" font-size="10.5" font-weight="bold">[ERROR: SOLAPAMIENTO DE FECHAS O RANGO INVÁLIDO]</text>

  <line x1="{x_srv - 6}" y1="665" x2="{x_ctrl + 6}" y2="665" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_ctrl + x_srv)/2}" y="657" font-size="10" text-anchor="middle">12: return Error('Conflicto con promoción vigente en las mismas fechas')</text>

  <line x1="{x_ctrl - 6}" y1="695" x2="{x_iu + 6}" y2="695" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="687" font-size="10" text-anchor="middle">13: HTTP 400 Bad Request</text>

  <!-- Retorno exitoso final -->
  <line x1="{x_srv - 6}" y1="760" x2="{x_ctrl + 6}" y2="760" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_ctrl + x_srv)/2}" y="752" font-size="10" text-anchor="middle">14: respuesta_exitosa(promocion_guardada)</text>

  <line x1="{x_ctrl - 6}" y1="795" x2="{x_iu + 6}" y2="795" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="787" font-size="10" text-anchor="middle">15: HTTP 201 Created (datos_promocion)</text>

  <line x1="{x_iu - 6}" y1="835" x2="{x_actor}" y2="835" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_actor + x_iu)/2}" y="827" font-size="10" text-anchor="middle">16: NotificarPromocionActiva(mensaje_exito)</text>

</svg>
''')
    return "".join(svg)

# ==================== GENERADOR CU/W31 ====================
def generate_cu_w31_svg():
    width = 1400
    height = 920
    x_actor = 80
    x_iu = 260
    x_ctrl = 480
    x_srv = 720
    x_repo = 940
    x_venta = 1100
    x_res = 1240
    x_inv = 1360

    y_header = 85
    h_box = 36
    y_line_start = y_header + h_box
    y_line_end = 880

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow_sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/></marker>
    <marker id="arrow_return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 1 L 10 5 L 0 9" fill="none" stroke="#000000" stroke-width="1.4"/></marker>
  </defs>

  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <path d="M 15 15 L 490 15 L 505 35 L 505 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12" font-weight="bold">CU/W31: Consultar ventas, reservas e inventario</text>

  <g transform="translate({x_actor}, 55)"><circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/><line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/><text x="0" y="78" font-size="10.5" font-weight="bold" text-anchor="middle">ENCARGADO</text></g>

  <g><rect x="{x_iu - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_iu}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">IU_MonitorOperativo</text></g>
  <g><rect x="{x_ctrl - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_ctrl}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">inventario_routes</text></g>
  <g><rect x="{x_srv - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_srv}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">Consolidador_Service</text></g>
  <g><rect x="{x_repo - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_repo}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">inventario_repos</text></g>
  <g><rect x="{x_venta - 45}" y="{y_header}" width="90" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_venta}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_VENTA</text></g>
  <g><rect x="{x_res - 50}" y="{y_header}" width="100" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_res}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_RESERVA</text></g>
  <g><rect x="{x_inv - 55}" y="{y_header}" width="110" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_inv}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">T_INVENTARIO</text></g>

  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_iu}" y1="{y_line_start}" x2="{x_iu}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_ctrl}" y1="{y_line_start}" x2="{x_ctrl}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_srv}" y1="{y_line_start}" x2="{x_srv}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_repo}" y1="{y_line_start}" x2="{x_repo}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_venta}" y1="{y_line_start}" x2="{x_venta}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_res}" y1="{y_line_start}" x2="{x_res}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_inv}" y1="{y_line_start}" x2="{x_inv}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <rect x="{x_iu - 6}" y="155" width="12" height="695" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_ctrl - 6}" y="185" width="12" height="635" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_srv - 6}" y="215" width="12" height="575" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_repo - 6}" y="325" width="12" height="375" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_venta - 6}" y="340" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_res - 6}" y="420" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_inv - 6}" y="505" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- 1: Solicitar panel -->
  <line x1="{x_actor}" y1="160" x2="{x_iu - 6}" y2="160" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_actor + x_iu)/2}" y="152" font-size="10.5" text-anchor="middle">1: ConsultarBalanceOperativo(id_sucursal, fecha)</text>

  <!-- 2: GET /monitor -->
  <line x1="{x_iu + 6}" y1="190" x2="{x_ctrl - 6}" y2="190" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="182" font-size="10.5" text-anchor="middle">2: GET /api/inventario/monitor-operativo?sucursal=1</text>

  <!-- 3: Invocación servicio -->
  <line x1="{x_ctrl + 6}" y1="220" x2="{x_srv - 6}" y2="220" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_ctrl + x_srv)/2}" y="212" font-size="10.5" text-anchor="middle">3: consolidar_operaciones_sucursal(sucursal, fecha)</text>

  <!-- LOOP: Recorrer Sucursales -->
  <rect x="35" y="240" width="{width - 60}" height="495" fill="none" stroke="#000000" stroke-width="1.3"/>
  <path d="M 35 240 L 90 240 L 100 257 L 100 265 L 35 265 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="65" y="257" font-size="11" font-weight="bold" text-anchor="middle">loop</text>
  <text x="110" y="258" font-size="10.5" font-weight="bold">[POR CADA SUCURSAL VINCULADA AL ENCARGADO / ADMIN]</text>

  <line x1="{x_srv + 6}" y1="285" x2="{x_repo - 6}" y2="285" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_srv + x_repo)/2}" y="277" font-size="10" text-anchor="middle">4: query_balance_completo(id_sucursal)</text>

  <!-- Consulta 1: T_VENTA -->
  <line x1="{x_repo + 6}" y1="325" x2="{x_venta - 6}" y2="325" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_venta)/2}" y="317" font-size="9.5" text-anchor="middle">5: SELECT SUM(TOTAL) FROM T_VENTA</text>

  <line x1="{x_venta - 6}" y1="355" x2="{x_repo + 6}" y2="355" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_repo + x_venta)/2}" y="347" font-size="9" text-anchor="middle">6: return total_ventas_dia</text>

  <!-- Consulta 2: T_RESERVA -->
  <line x1="{x_repo + 6}" y1="405" x2="{x_res - 6}" y2="405" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_res)/2}" y="397" font-size="9.5" text-anchor="middle">7: SELECT * FROM T_RESERVA WHERE ESTADO = 'PENDIENTE'</text>

  <line x1="{x_res - 6}" y1="435" x2="{x_repo + 6}" y2="435" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_repo + x_res)/2}" y="427" font-size="9" text-anchor="middle">8: return apartados_por_vencer</text>

  <!-- Consulta 3: T_INVENTARIO -->
  <line x1="{x_repo + 6}" y1="485" x2="{x_inv - 6}" y2="485" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_inv)/2}" y="477" font-size="9.5" text-anchor="middle">9: SELECT STOCK_DISPONIBLE, STOCK_MINIMO FROM T_INVENTARIO</text>

  <line x1="{x_inv - 6}" y1="515" x2="{x_repo + 6}" y2="515" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_repo + x_inv)/2}" y="507" font-size="9" text-anchor="middle">10: return existencias_fisicas</text>

  <!-- OPT: Alerta de stock crítico -->
  <rect x="50" y="550" width="{width - 90}" height="75" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 550 L 95 550 L 105 565 L 105 572 L 50 572 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="565" font-size="10" font-weight="bold" text-anchor="middle">opt</text>
  <text x="115" y="566" font-size="10" font-weight="bold">[STOCK_DISPONIBLE &lt;= STOCK_MINIMO: GENERAR ALERTA]</text>

  <path d="M {x_srv + 6} 585 L {x_srv + 45} 585 L {x_srv + 45} 605 L {x_srv + 8} 605" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{x_srv + 52}" y="598" font-size="9.5" text-anchor="start">11: flag_alerta_reposicion = true</text>

  <line x1="{x_repo - 6}" y1="675" x2="{x_srv + 6}" y2="675" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_srv + x_repo)/2}" y="667" font-size="10" text-anchor="middle">12: return dataset_operativo_sucursal</text>

  <!-- Retornos finales -->
  <line x1="{x_srv - 6}" y1="760" x2="{x_ctrl + 6}" y2="760" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_ctrl + x_srv)/2}" y="752" font-size="10" text-anchor="middle">13: consolidar_kpis_en_vivo(metricas)</text>

  <line x1="{x_ctrl - 6}" y1="795" x2="{x_iu + 6}" y2="795" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="787" font-size="10" text-anchor="middle">14: HTTP 200 OK (balance_consolidado)</text>

  <line x1="{x_iu - 6}" y1="835" x2="{x_actor}" y2="835" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_actor + x_iu)/2}" y="827" font-size="10" text-anchor="middle">15: RenderizarMonitorOperativo(tablas, semaforos_stock)</text>

</svg>
''')
    return "".join(svg)

# ==================== GENERADOR CU/W32 ====================
def generate_cu_w32_svg():
    width = 1380
    height = 920
    x_actor = 80
    x_iu = 260
    x_ctrl = 480
    x_srv = 740
    x_venta = 1000
    x_det = 1180
    x_pago = 1320

    y_header = 85
    h_box = 36
    y_line_start = y_header + h_box
    y_line_end = 880

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow_sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/></marker>
    <marker id="arrow_return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 1 L 10 5 L 0 9" fill="none" stroke="#000000" stroke-width="1.4"/></marker>
  </defs>

  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <path d="M 15 15 L 480 15 L 495 35 L 495 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12" font-weight="bold">CU/W32: Visualizar indicadores empresariales (Analytics)</text>

  <g transform="translate({x_actor}, 55)"><circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/><line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/><text x="0" y="78" font-size="11" font-weight="bold" text-anchor="middle">GERENTE</text></g>

  <g><rect x="{x_iu - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_iu}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">Dashboard_KPIs_View</text></g>
  <g><rect x="{x_ctrl - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_ctrl}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">KPI_Controller</text></g>
  <g><rect x="{x_srv - 75}" y="{y_header}" width="150" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_srv}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">Analytics_Engine_Service</text></g>
  <g><rect x="{x_venta - 50}" y="{y_header}" width="100" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_venta}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_VENTA</text></g>
  <g><rect x="{x_det - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_det}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">T_DETALLE_VENTA</text></g>
  <g><rect x="{x_pago - 45}" y="{y_header}" width="90" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_pago}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_PAGO</text></g>

  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_iu}" y1="{y_line_start}" x2="{x_iu}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_ctrl}" y1="{y_line_start}" x2="{x_ctrl}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_srv}" y1="{y_line_start}" x2="{x_srv}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_venta}" y1="{y_line_start}" x2="{x_venta}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_det}" y1="{y_line_start}" x2="{x_det}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_pago}" y1="{y_line_start}" x2="{x_pago}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <rect x="{x_iu - 6}" y="155" width="12" height="695" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_ctrl - 6}" y="185" width="12" height="635" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_srv - 6}" y="215" width="12" height="575" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_venta - 6}" y="325" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_det - 6}" y="420" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_pago - 6}" y="525" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- 1: Consultar KPIs -->
  <line x1="{x_actor}" y1="160" x2="{x_iu - 6}" y2="160" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_actor + x_iu)/2}" y="152" font-size="10.5" text-anchor="middle">1: SeleccionarPeriodoAnalitico('ESTE_MES')</text>

  <!-- 2: GET /kpis -->
  <line x1="{x_iu + 6}" y1="190" x2="{x_ctrl - 6}" y2="190" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="182" font-size="10.5" text-anchor="middle">2: GET /api/kpis/dashboard-ejecutivo?periodo=mensual</text>

  <!-- 3: Invocación Analytics Engine (Directo) -->
  <line x1="{x_ctrl + 6}" y1="220" x2="{x_srv - 6}" y2="220" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_ctrl + x_srv)/2}" y="212" font-size="10" text-anchor="middle">3: calcular_kpis_empresariales(periodo, canal)</text>

  <!-- LOOP: Procesar agregaciones analíticas -->
  <rect x="35" y="240" width="{width - 60}" height="495" fill="none" stroke="#000000" stroke-width="1.3"/>
  <path d="M 35 240 L 90 240 L 100 257 L 100 265 L 35 265 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="65" y="257" font-size="11" font-weight="bold" text-anchor="middle">loop</text>
  <text x="110" y="258" font-size="10.5" font-weight="bold">[POR CADA SERIE TEMPORAL (DÍA / SEMANA / MES)]</text>

  <path d="M {x_srv + 6} 270 L {x_srv + 45} 270 L {x_srv + 45} 295 L {x_srv + 8} 295" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{x_srv + 52}" y="285" font-size="10" text-anchor="start">4: calcular_ticket_promedio_y_crecimiento()</text>

  <!-- Agregación en T_VENTA -->
  <line x1="{x_srv + 6}" y1="325" x2="{x_venta - 6}" y2="325" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_srv + x_venta)/2}" y="317" font-size="9.5" text-anchor="middle">5: SELECT COUNT(*), AVG(TOTAL), SUM(TOTAL) FROM T_VENTA</text>

  <line x1="{x_venta - 6}" y1="355" x2="{x_srv + 6}" y2="355" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_srv + x_venta)/2}" y="347" font-size="9.5" text-anchor="middle">6: return metricas_ingresos_globales</text>

  <!-- ALT: Canal POS vs Canal Online -->
  <rect x="50" y="380" width="{width - 90}" height="195" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 380 L 95 380 L 105 395 L 105 402 L 50 402 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="395" font-size="10" font-weight="bold" text-anchor="middle">alt</text>
  <text x="115" y="396" font-size="10" font-weight="bold">[CANAL TIENDAS FÍSICAS POS]</text>

  <line x1="{x_srv + 6}" y1="420" x2="{x_det - 6}" y2="420" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_srv + x_det)/2}" y="412" font-size="9" text-anchor="middle">7: SELECT TOP prendas_mas_vendidas FROM T_DETALLE_VENTA</text>

  <line x1="{x_det - 6}" y1="450" x2="{x_srv + 6}" y2="450" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_srv + x_det)/2}" y="442" font-size="9" text-anchor="middle">8: return ranking_rotacion_pos</text>

  <line x1="50" y1="480" x2="{width - 40}" y2="480" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>
  <text x="65" y="497" font-size="10" font-weight="bold">[CANAL COMERCIO ELECTRÓNICO / MÓVIL]</text>

  <line x1="{x_srv + 6}" y1="525" x2="{x_pago - 6}" y2="525" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_srv + x_pago)/2}" y="517" font-size="9" text-anchor="middle">9: SELECT MONTO, ESTADO FROM T_PAGO WHERE METODO_PAGO = 'ONLINE'</text>

  <line x1="{x_pago - 6}" y1="555" x2="{x_srv + 6}" y2="555" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_srv + x_pago)/2}" y="547" font-size="9" text-anchor="middle">10: return metricas_pagos_digitales</text>

  <!-- OPT: Comparativa Interanual -->
  <rect x="50" y="590" width="{width - 90}" height="75" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 590 L 95 590 L 105 605 L 105 612 L 50 612 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="605" font-size="10" font-weight="bold" text-anchor="middle">opt</text>
  <text x="115" y="606" font-size="10" font-weight="bold">[COMPARATIVA CON MISMO PERIODO AÑO ANTERIOR]</text>

  <path d="M {x_srv + 6} 625 L {x_srv + 45} 625 L {x_srv + 45} 645 L {x_srv + 8} 645" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{x_srv + 52}" y="638" font-size="9.5" text-anchor="start">11: tasa_crecimiento = ((actual - anterior)/anterior)*100</text>

  <!-- Retornos -->
  <line x1="{x_srv - 6}" y1="760" x2="{x_ctrl + 6}" y2="760" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_ctrl + x_srv)/2}" y="752" font-size="10" text-anchor="middle">12: return dataset_kpis_ejecutivo</text>

  <line x1="{x_ctrl - 6}" y1="795" x2="{x_iu + 6}" y2="795" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="787" font-size="10" text-anchor="middle">13: HTTP 200 OK (graficos, tablas_kpis)</text>

  <line x1="{x_iu - 6}" y1="835" x2="{x_actor}" y2="835" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_actor + x_iu)/2}" y="827" font-size="10" text-anchor="middle">14: RenderizarTablerosEjecutivos(graficos_tendencias)</text>

</svg>
''')
    return "".join(svg)

# ==================== GENERADOR CU/W33 ====================
def generate_cu_w33_svg():
    width = 1380
    height = 920
    x_actor = 80
    x_iu = 260
    x_ctrl = 480
    x_srv = 720
    x_repo = 940
    x_inv = 1120
    x_bit = 1290

    y_header = 85
    h_box = 36
    y_line_start = y_header + h_box
    y_line_end = 880

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow_sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/></marker>
    <marker id="arrow_return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 1 L 10 5 L 0 9" fill="none" stroke="#000000" stroke-width="1.4"/></marker>
  </defs>

  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <path d="M 15 15 L 450 15 L 465 35 L 465 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12" font-weight="bold">CU/W33: Generar reportes bajo demanda</text>

  <g transform="translate({x_actor}, 55)"><circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/><line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/><text x="0" y="78" font-size="10.5" font-weight="bold" text-anchor="middle">ADMINISTRADOR</text></g>

  <g><rect x="{x_iu - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_iu}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">IU_ReportesDemanda</text></g>
  <g><rect x="{x_ctrl - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_ctrl}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">reportes_routes</text></g>
  <g><rect x="{x_srv - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_srv}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">Report_Builder_Service</text></g>
  <g><rect x="{x_repo - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_repo}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">reportes_repos</text></g>
  <g><rect x="{x_inv - 55}" y="{y_header}" width="110" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_inv}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">T_INVENTARIO</text></g>
  <g><rect x="{x_bit - 55}" y="{y_header}" width="110" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_bit}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_BITACORA</text></g>

  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_iu}" y1="{y_line_start}" x2="{x_iu}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_ctrl}" y1="{y_line_start}" x2="{x_ctrl}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_srv}" y1="{y_line_start}" x2="{x_srv}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_repo}" y1="{y_line_start}" x2="{x_repo}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_inv}" y1="{y_line_start}" x2="{x_inv}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_bit}" y1="{y_line_start}" x2="{x_bit}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <rect x="{x_iu - 6}" y="155" width="12" height="695" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_ctrl - 6}" y="185" width="12" height="635" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_srv - 6}" y="215" width="12" height="575" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_repo - 6}" y="325" width="12" height="340" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_inv - 6}" y="350" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_bit - 6}" y="575" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- 1: Solicitar reporte -->
  <line x1="{x_actor}" y1="160" x2="{x_iu - 6}" y2="160" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_actor + x_iu)/2}" y="152" font-size="10.5" text-anchor="middle">1: ConfigurarParametros(tipo='STOCK', fechas, formato='PDF')</text>

  <!-- 2: POST /reportes/generar -->
  <line x1="{x_iu + 6}" y1="190" x2="{x_ctrl - 6}" y2="190" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="182" font-size="10.5" text-anchor="middle">2: POST /api/reportes/generar</text>

  <!-- 3: Invocación builder -->
  <line x1="{x_ctrl + 6}" y1="220" x2="{x_srv - 6}" y2="220" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_ctrl + x_srv)/2}" y="212" font-size="10.5" text-anchor="middle">3: compilar_reporte_documental(criterios)</text>

  <!-- Fragmento ALT: PDF vs EXCEL -->
  <rect x="35" y="240" width="{width - 60}" height="490" fill="none" stroke="#000000" stroke-width="1.3"/>
  <path d="M 35 240 L 90 240 L 100 257 L 100 265 L 35 265 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="65" y="257" font-size="11" font-weight="bold" text-anchor="middle">alt</text>
  <text x="110" y="258" font-size="10.5" font-weight="bold">[FORMATO SELECCIONADO = PDF (REPORTLAB)]</text>

  <line x1="{x_srv + 6}" y1="285" x2="{x_repo - 6}" y2="285" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_srv + x_repo)/2}" y="277" font-size="10" text-anchor="middle">4: extraer_datos_reporte_stock(sucursal)</text>

  <line x1="{x_repo + 6}" y1="350" x2="{x_inv - 6}" y2="350" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_inv)/2}" y="342" font-size="9.5" text-anchor="middle">5: SELECT * FROM T_INVENTARIO WHERE STOCK_ACTUAL &gt; 0</text>

  <line x1="{x_inv - 6}" y1="380" x2="{x_repo + 6}" y2="380" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_repo + x_inv)/2}" y="372" font-size="9.5" text-anchor="middle">6: return tuplas_inventario_valorizado</text>

  <line x1="{x_repo - 6}" y1="410" x2="{x_srv + 6}" y2="410" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_srv + x_repo)/2}" y="402" font-size="10" text-anchor="middle">7: return dataset_tabular</text>

  <path d="M {x_srv + 6} 435 L {x_srv + 45} 435 L {x_srv + 45} 455 L {x_srv + 8} 455" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{x_srv + 52}" y="448" font-size="10" text-anchor="start">8: renderizar_plantilla_pdf(ReportLab_Canvas)</text>

  <line x1="35" y1="480" x2="{width - 25}" y2="480" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>
  <text x="50" y="497" font-size="10.5" font-weight="bold">[FORMATO SELECCIONADO = EXCEL (OPENPYXL)]</text>

  <path d="M {x_srv + 6} 520 L {x_srv + 45} 520 L {x_srv + 45} 540 L {x_srv + 8} 540" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{x_srv + 52}" y="533" font-size="10" text-anchor="start">9: generar_hoja_calculo_xlsx(OpenPyXL_Workbook)</text>

  <!-- OPT: Auditoría en T_BITACORA -->
  <rect x="50" y="560" width="{width - 90}" height="70" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 560 L 95 560 L 105 575 L 105 582 L 50 582 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="575" font-size="10" font-weight="bold" text-anchor="middle">opt</text>
  <text x="115" y="576" font-size="10" font-weight="bold">[TRAZABILIDAD DE EXPORTACIÓN EN T_BITACORA]</text>

  <line x1="{x_srv + 6}" y1="600" x2="{x_bit - 6}" y2="600" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_srv + x_bit)/2}" y="592" font-size="9.5" text-anchor="middle">10: INSERT INTO T_BITACORA ('EXPORTAR_REPORTE', formato, user_id)</text>

  <!-- Retornos finales -->
  <line x1="{x_srv - 6}" y1="760" x2="{x_ctrl + 6}" y2="760" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_ctrl + x_srv)/2}" y="752" font-size="10" text-anchor="middle">11: return archivo_binario(bytes)</text>

  <line x1="{x_ctrl - 6}" y1="795" x2="{x_iu + 6}" y2="795" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_iu + x_ctrl)/2}" y="787" font-size="10" text-anchor="middle">12: HTTP 200 OK (Content-Type: application/pdf o xlsx)</text>

  <line x1="{x_iu - 6}" y1="835" x2="{x_actor}" y2="835" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_actor + x_iu)/2}" y="827" font-size="10" text-anchor="middle">13: DescargarDocumentoOficial(archivo_generado)</text>

</svg>
''')
    return "".join(svg)

# ==================== GENERADOR CU/M12 ====================
def generate_cu_m12_svg():
    width = 1380
    height = 920
    x_actor = 80
    x_screen = 270
    x_cubit = 500
    x_api = 740
    x_recom = 990
    x_hist = 1170
    x_prod = 1310

    y_header = 85
    h_box = 36
    y_line_start = y_header + h_box
    y_line_end = 880

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow_sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/></marker>
    <marker id="arrow_return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 1 L 10 5 L 0 9" fill="none" stroke="#000000" stroke-width="1.4"/></marker>
  </defs>

  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <path d="M 15 15 L 480 15 L 495 35 L 495 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12" font-weight="bold">CU/M12: Obtener recomendaciones de productos (Mobile)</text>

  <g transform="translate({x_actor}, 55)"><circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/><line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/><text x="0" y="78" font-size="10.5" font-weight="bold" text-anchor="middle">CLIENTE_MOVIL</text></g>

  <g><rect x="{x_screen - 70}" y="{y_header}" width="140" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_screen}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">Feed_Recomendados_Screen</text></g>
  <g><rect x="{x_cubit - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_cubit}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">Recomendaciones_Cubit</text></g>
  <g><rect x="{x_api - 70}" y="{y_header}" width="140" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_api}" y="{y_header + 22}" font-size="10" font-weight="bold" text-anchor="middle">Mobile_API_Client</text></g>
  <g><rect x="{x_recom - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_recom}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">T_RECOMENDACION</text></g>
  <g><rect x="{x_hist - 75}" y="{y_header}" width="150" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_hist}" y="{y_header + 22}" font-size="9.5" font-weight="bold" text-anchor="middle">T_HISTORIAL_NAVEGACION</text></g>
  <g><rect x="{x_prod - 50}" y="{y_header}" width="100" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_prod}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">T_PRODUCTO</text></g>

  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_screen}" y1="{y_line_start}" x2="{x_screen}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_cubit}" y1="{y_line_start}" x2="{x_cubit}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_api}" y1="{y_line_start}" x2="{x_api}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_recom}" y1="{y_line_start}" x2="{x_recom}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_hist}" y1="{y_line_start}" x2="{x_hist}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_prod}" y1="{y_line_start}" x2="{x_prod}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <rect x="{x_screen - 6}" y="155" width="12" height="695" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_cubit - 6}" y="185" width="12" height="635" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_api - 6}" y="215" width="12" height="575" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_recom - 6}" y="360" width="12" height="50" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_hist - 6}" y="575" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_prod - 6}" y="440" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- 1: Abrir app móvil -->
  <line x1="{x_actor}" y1="160" x2="{x_screen - 6}" y2="160" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_actor + x_screen)/2}" y="152" font-size="10.5" text-anchor="middle">1: TocarPestañaParaTi()</text>

  <!-- 2: Cargar Cubit -->
  <line x1="{x_screen + 6}" y1="190" x2="{x_cubit - 6}" y2="190" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_screen + x_cubit)/2}" y="182" font-size="10.5" text-anchor="middle">2: cargar_recomendaciones()</text>

  <!-- ALT: Cache Local vs Sync Backend -->
  <rect x="35" y="220" width="{width - 60}" height="510" fill="none" stroke="#000000" stroke-width="1.3"/>
  <path d="M 35 220 L 90 220 L 100 237 L 100 245 L 35 245 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="65" y="237" font-size="11" font-weight="bold" text-anchor="middle">alt</text>
  <text x="110" y="238" font-size="10.5" font-weight="bold">[CACHE LOCAL VÁLIDA EN DISPOSITIVO]</text>

  <path d="M {x_cubit + 6} 265 L {x_cubit + 45} 265 L {x_cubit + 45} 285 L {x_cubit + 8} 285" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{x_cubit + 52}" y="278" font-size="10" text-anchor="start">3: recuperar_cache_local_hive()</text>

  <line x1="35" y1="310" x2="{width - 25}" y2="310" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>
  <text x="50" y="327" font-size="10.5" font-weight="bold">[FEED DESACTUALIZADO O SIN CONEXIÓN PREVIA: SYNC REST]</text>

  <line x1="{x_cubit + 6}" y1="340" x2="{x_api - 6}" y2="340" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_cubit + x_api)/2}" y="332" font-size="10" text-anchor="middle">4: get_productos_recomendados(id_cliente)</text>

  <line x1="{x_api + 6}" y1="370" x2="{x_recom - 6}" y2="370" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_api + x_recom)/2}" y="362" font-size="9.5" text-anchor="middle">5: SELECT * FROM T_RECOMENDACION WHERE ID_CLIENTE = ?</text>

  <line x1="{x_recom - 6}" y1="400" x2="{x_api + 6}" y2="400" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_api + x_recom)/2}" y="392" font-size="9.5" text-anchor="middle">6: return id_productos_recomendados</text>

  <line x1="{x_api + 6}" y1="440" x2="{x_prod - 6}" y2="440" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_api + x_prod)/2}" y="432" font-size="9.5" text-anchor="middle">7: SELECT NOMBRE, PRECIO, IMAGEN_URL FROM T_PRODUCTO</text>

  <line x1="{x_prod - 6}" y1="470" x2="{x_api + 6}" y2="470" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_api + x_prod)/2}" y="462" font-size="9.5" text-anchor="middle">8: return datos_prendas_sugeridas</text>

  <!-- OPT: Registro en historial navegación -->
  <rect x="50" y="520" width="{width - 90}" height="80" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 520 L 95 520 L 105 535 L 105 542 L 50 542 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="535" font-size="10" font-weight="bold" text-anchor="middle">opt</text>
  <text x="115" y="536" font-size="10" font-weight="bold">[REGISTRAR VISITA EN HISTORIAL DE NAVEGACIÓN]</text>

  <line x1="{x_api + 6}" y1="565" x2="{x_hist - 6}" y2="565" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_api + x_hist)/2}" y="557" font-size="9.5" text-anchor="middle">9: INSERT INTO T_HISTORIAL_NAVEGACION (ID_CLIENTE, ID_PRODUCTO, 'VISTA_FEED')</text>

  <line x1="{x_api - 6}" y1="640" x2="{x_cubit + 6}" y2="640" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_cubit + x_api)/2}" y="632" font-size="10" text-anchor="middle">10: return prendas_recomendadas_json</text>

  <!-- LOOP: Construir Cards Móviles -->
  <path d="M {x_cubit + 6} 675 L {x_cubit + 45} 675 L {x_cubit + 45} 695 L {x_cubit + 8} 695" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{x_cubit + 52}" y="688" font-size="9.5" text-anchor="start">11: emit(RecomendacionesLoaded(cards_optimizadas))</text>

  <line x1="{x_cubit - 6}" y1="760" x2="{x_screen + 6}" y2="760" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_screen + x_cubit)/2}" y="752" font-size="10" text-anchor="middle">12: actualizar_estado_feed()</text>

  <line x1="{x_screen - 6}" y1="835" x2="{x_actor}" y2="835" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_actor + x_screen)/2}" y="827" font-size="10" text-anchor="middle">13: RenderizarCarruselNativo('Descubre tu Estilo')</text>

</svg>
''')
    return "".join(svg)

# ==================== GENERADOR CU/M13 ====================
def generate_cu_m13_svg():
    width = 1400
    height = 920
    x_actor = 80
    x_screen = 260
    x_cubit = 470
    x_speech = 680
    x_ai = 900
    x_cli = 1070
    x_ped = 1220
    x_res = 1350

    y_header = 85
    h_box = 36
    y_line_start = y_header + h_box
    y_line_end = 880

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow_sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/></marker>
    <marker id="arrow_return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 1 L 10 5 L 0 9" fill="none" stroke="#000000" stroke-width="1.4"/></marker>
  </defs>

  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <path d="M 15 15 L 480 15 L 495 35 L 495 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12" font-weight="bold">CU/M13: Interactuar con asistente inteligente (Mobile Voz/Chat)</text>

  <g transform="translate({x_actor}, 55)"><circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/><line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/><text x="0" y="78" font-size="10.5" font-weight="bold" text-anchor="middle">CLIENTE_MOVIL</text></g>

  <g><rect x="{x_screen - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_screen}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">Voice_Chat_Screen</text></g>
  <g><rect x="{x_cubit - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_cubit}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">Voice_Chat_Cubit</text></g>
  <g><rect x="{x_speech - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_speech}" y="{y_header + 22}" font-size="10" font-weight="bold" text-anchor="middle">Speech_Detector</text></g>
  <g><rect x="{x_ai - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_ai}" y="{y_header + 22}" font-size="10" font-weight="bold" text-anchor="middle">AI_Mobile_Client</text></g>
  <g><rect x="{x_cli - 45}" y="{y_header}" width="90" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_cli}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_CLIENTE</text></g>
  <g><rect x="{x_ped - 45}" y="{y_header}" width="90" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_ped}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_VENTA</text></g>
  <g><rect x="{x_res - 50}" y="{y_header}" width="100" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_res}" y="{y_header + 22}" font-size="11" font-weight="bold" text-anchor="middle">T_RESERVA</text></g>

  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_screen}" y1="{y_line_start}" x2="{x_screen}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_cubit}" y1="{y_line_start}" x2="{x_cubit}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_speech}" y1="{y_line_start}" x2="{x_speech}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_ai}" y1="{y_line_start}" x2="{x_ai}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_cli}" y1="{y_line_start}" x2="{x_cli}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_ped}" y1="{y_line_start}" x2="{x_ped}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_res}" y1="{y_line_start}" x2="{x_res}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <rect x="{x_screen - 6}" y="155" width="12" height="695" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_cubit - 6}" y="185" width="12" height="635" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_speech - 6}" y="235" width="12" height="90" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_ai - 6}" y="360" width="12" height="340" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_ped - 6}" y="465" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_res - 6}" y="575" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- 1: Interacción móvil -->
  <line x1="{x_actor}" y1="160" x2="{x_screen - 6}" y2="160" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_actor + x_screen)/2}" y="152" font-size="10.5" text-anchor="middle">1: TocarMicrofono('¿Dónde está mi pedido?')</text>

  <!-- ALT: Voz STT vs Texto Teclado -->
  <rect x="35" y="180" width="{width - 60}" height="170" fill="none" stroke="#000000" stroke-width="1.3"/>
  <path d="M 35 180 L 90 180 L 100 197 L 100 205 L 35 205 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="65" y="197" font-size="11" font-weight="bold" text-anchor="middle">alt</text>
  <text x="110" y="198" font-size="10.5" font-weight="bold">[ENTRADA POR VOZ EN TIEMPO REAL]</text>

  <line x1="{x_screen + 6}" y1="225" x2="{x_cubit - 6}" y2="225" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_screen + x_cubit)/2}" y="217" font-size="10" text-anchor="middle">2: escuchar_audio_stream()</text>

  <line x1="{x_cubit + 6}" y1="250" x2="{x_speech - 6}" y2="250" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_cubit + x_speech)/2}" y="242" font-size="9.5" text-anchor="middle">3: convertir_audio_a_texto(buffer)</text>

  <line x1="{x_speech - 6}" y1="280" x2="{x_cubit + 6}" y2="280" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_cubit + x_speech)/2}" y="272" font-size="9.5" text-anchor="middle">4: return texto_transcrito</text>

  <line x1="35" y1="305" x2="{width - 25}" y2="305" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>
  <text x="50" y="322" font-size="10" font-weight="bold">[ENTRADA POR TECLADO EN PANTALLA]</text>
  <text x="{(x_screen + x_cubit)/2}" y="337" font-size="9.5" text-anchor="middle">5: enviar_texto_directo(mensaje_str)</text>

  <!-- Enviar a AI Client -->
  <line x1="{x_cubit + 6}" y1="375" x2="{x_ai - 6}" y2="375" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_cubit + x_ai)/2}" y="367" font-size="10" text-anchor="middle">6: post_mensaje_ia(texto, token_jwt)</text>

  <!-- ALT: Intención Pedido vs Intención Reserva -->
  <rect x="50" y="405" width="{width - 90}" height="250" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 405 L 95 405 L 105 420 L 105 427 L 50 427 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="420" font-size="10" font-weight="bold" text-anchor="middle">alt</text>
  <text x="115" y="421" font-size="10" font-weight="bold">[INTENCIÓN: CONSULTAR ESTADO DE COMPRA / TRACKING]</text>

  <line x1="{x_ai + 6}" y1="455" x2="{x_ped - 6}" y2="455" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_ai + x_ped)/2}" y="447" font-size="9" text-anchor="middle">7: SELECT NUMERO_VENTA, ESTADO, TOTAL FROM T_VENTA</text>

  <line x1="{x_ped - 6}" y1="485" x2="{x_ai + 6}" y2="485" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_ai + x_ped)/2}" y="477" font-size="9" text-anchor="middle">8: return tracking_pedido_activo</text>

  <line x1="50" y1="520" x2="{width - 40}" y2="520" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>
  <text x="65" y="537" font-size="10" font-weight="bold">[INTENCIÓN: CONSULTAR CÓDIGO QR DE RESERVA EN TIENDA]</text>

  <line x1="{x_ai + 6}" y1="565" x2="{x_res - 6}" y2="565" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_ai + x_res)/2}" y="557" font-size="9" text-anchor="middle">9: SELECT CODIGO_RESERVA, FECHA_EXPIRACION FROM T_RESERVA</text>

  <line x1="{x_res - 6}" y1="595" x2="{x_ai + 6}" y2="595" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_ai + x_res)/2}" y="587" font-size="9" text-anchor="middle">10: return ticket_qr_reserva</text>

  <!-- Retorno AI Client -->
  <line x1="{x_ai - 6}" y1="685" x2="{x_cubit + 6}" y2="685" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_cubit + x_ai)/2}" y="677" font-size="10" text-anchor="middle">11: return respuesta_enriquecida_movil</text>

  <!-- OPT: Síntesis de voz TTS -->
  <rect x="50" y="715" width="{width - 90}" height="55" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 715 L 95 715 L 105 730 L 105 737 L 50 737 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="730" font-size="10" font-weight="bold" text-anchor="middle">opt</text>
  <text x="115" y="731" font-size="10" font-weight="bold">[REPRODUCCIÓN DE VOZ SINTETIZADA TTS]</text>

  <line x1="{x_cubit + 6}" y1="745" x2="{x_speech - 6}" y2="745" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_cubit + x_speech)/2}" y="738" font-size="9.5" text-anchor="middle">12: hablar_texto(respuesta_ia)</text>

  <!-- Retorno pantalla -->
  <line x1="{x_cubit - 6}" y1="790" x2="{x_screen + 6}" y2="790" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_screen + x_cubit)/2}" y="782" font-size="10" text-anchor="middle">13: emit(VoiceChatResponseLoaded(burbuja, action_card))</text>

  <line x1="{x_screen - 6}" y1="835" x2="{x_actor}" y2="835" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_actor + x_screen)/2}" y="827" font-size="10" text-anchor="middle">14: MostrarRespuestaEnPantalla(texto, audio, card)</text>

</svg>
''')
    return "".join(svg)

# ==================== GENERADOR CU/M14 ====================
def generate_cu_m14_svg():
    width = 1280
    height = 920
    x_actor = 70
    x_screen = 220
    x_ctrl = 410
    x_pose = 620
    x_srv = 830
    x_prenda_ra = 1020
    x_vestidor = 1180

    y_header = 85
    h_box = 36
    y_line_start = y_header + h_box
    y_line_end = 880

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <defs>
    <marker id="arrow_sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/></marker>
    <marker id="arrow_return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 1 L 10 5 L 0 9" fill="none" stroke="#000000" stroke-width="1.4"/></marker>
  </defs>

  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <path d="M 15 15 L 490 15 L 505 35 L 505 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12" font-weight="bold">CU/M14: Utilizar vestidor virtual (Realidad Aumentada)</text>

  <g transform="translate({x_actor}, 55)"><circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/><line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/><line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/><text x="0" y="78" font-size="10.5" font-weight="bold" text-anchor="middle">CLIENTE_MOVIL</text></g>

  <g><rect x="{x_screen - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_screen}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">Vestidor_Screen</text></g>
  <g><rect x="{x_ctrl - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_ctrl}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">AR_Camera_Ctrl</text></g>
  <g><rect x="{x_pose - 65}" y="{y_header}" width="130" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_pose}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">Pose_Body_Detector</text></g>
  <g><rect x="{x_srv - 60}" y="{y_header}" width="120" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_srv}" y="{y_header + 22}" font-size="10.5" font-weight="bold" text-anchor="middle">Vestidor_Service</text></g>
  <g><rect x="{x_prenda_ra - 55}" y="{y_header}" width="110" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_prenda_ra}" y="{y_header + 22}" font-size="10" font-weight="bold" text-anchor="middle">T_PRENDA_RA</text></g>
  <g><rect x="{x_vestidor - 55}" y="{y_header}" width="110" height="{h_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/><text x="{x_vestidor}" y="{y_header + 22}" font-size="9.5" font-weight="bold" text-anchor="middle">T_VESTIDOR_VIRTUAL</text></g>

  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_screen}" y1="{y_line_start}" x2="{x_screen}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_ctrl}" y1="{y_line_start}" x2="{x_ctrl}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_pose}" y1="{y_line_start}" x2="{x_pose}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_srv}" y1="{y_line_start}" x2="{x_srv}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_prenda_ra}" y1="{y_line_start}" x2="{x_prenda_ra}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_vestidor}" y1="{y_line_start}" x2="{x_vestidor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <rect x="{x_screen - 6}" y="155" width="12" height="695" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_ctrl - 6}" y="185" width="12" height="635" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_pose - 6}" y="235" width="12" height="320" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_srv - 6}" y="575" width="12" height="180" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_prenda_ra - 6}" y="605" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_vestidor - 6}" y="680" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- 1: Iniciar vestidor -->
  <line x1="{x_actor}" y1="160" x2="{x_screen - 6}" y2="160" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_actor + x_screen)/2}" y="152" font-size="10.5" text-anchor="middle">1: Tocar'Probar en Vestidor Virtual'</text>

  <!-- 2: Inicializar Cámara -->
  <line x1="{x_screen + 6}" y1="190" x2="{x_ctrl - 6}" y2="190" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_screen + x_ctrl)/2}" y="182" font-size="10.5" text-anchor="middle">2: inicializar_camara_frontal()</text>

  <!-- LOOP: 60 FPS Camera Frames -->
  <rect x="35" y="215" width="{width - 60}" height="325" fill="none" stroke="#000000" stroke-width="1.3"/>
  <path d="M 35 215 L 90 215 L 100 232 L 100 240 L 35 240 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="65" y="232" font-size="11" font-weight="bold" text-anchor="middle">loop</text>
  <text x="110" y="233" font-size="10.5" font-weight="bold">[POR CADA FRAME DEL FEED DE CÁMARA]</text>

  <line x1="{x_ctrl + 6}" y1="260" x2="{x_pose - 6}" y2="260" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_ctrl + x_pose)/2}" y="252" font-size="10" text-anchor="middle">3: procesar_frame(CameraImage)</text>

  <!-- ALT: Cuerpo detectado vs Fuera de encuadre -->
  <rect x="50" y="285" width="{width - 90}" height="235" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 285 L 95 285 L 105 300 L 105 307 L 50 307 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="300" font-size="10" font-weight="bold" text-anchor="middle">alt</text>
  <text x="115" y="301" font-size="10" font-weight="bold">[CUERPO Y PUNTOS CLAVE DE TORSO DETECTADOS (ANCHORS OK)]</text>

  <path d="M {x_pose + 6} 330 L {x_pose + 45} 330 L {x_pose + 45} 350 L {x_pose + 8} 350" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{x_pose + 52}" y="343" font-size="9.5" text-anchor="start">4: calcular_escala_y_posicion(hombros, cadera)</text>

  <line x1="{x_pose - 6}" y1="375" x2="{x_ctrl + 6}" y2="375" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_ctrl + x_pose)/2}" y="367" font-size="9.5" text-anchor="middle">5: return PoseData(escala, rotacion, traslacion)</text>

  <line x1="{x_ctrl - 6}" y1="405" x2="{x_screen + 6}" y2="405" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_screen + x_ctrl)/2}" y="397" font-size="9.5" text-anchor="middle">6: superponer_prenda_sobre_frame(PoseData)</text>

  <line x1="50" y1="435" x2="{width - 40}" y2="435" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>
  <text x="65" y="452" font-size="10" font-weight="bold">[CUERPO NO DETECTADO O ILUMINACIÓN INSUFICIENTE]</text>

  <line x1="{x_pose - 6}" y1="480" x2="{x_screen + 6}" y2="480" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_screen + x_pose)/2}" y="472" font-size="9.5" text-anchor="middle">7: MostrarGuiaVisual('Ubícate frente a la cámara')</text>

  <!-- Descargar recurso textil -->
  <line x1="{x_screen + 6}" y1="565" x2="{x_srv - 6}" y2="565" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_screen + x_srv)/2}" y="557" font-size="10" text-anchor="middle">8: get_recursos_prenda_ra(id_producto)</text>

  <line x1="{x_srv + 6}" y1="605" x2="{x_prenda_ra - 6}" y2="605" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_srv + x_prenda_ra)/2}" y="597" font-size="9.5" text-anchor="middle">9: SELECT MODELO_2D_URL, MODELO_3D_URL FROM T_PRENDA_RA</text>

  <line x1="{x_prenda_ra - 6}" y1="635" x2="{x_srv + 6}" y2="635" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_srv + x_prenda_ra)/2}" y="627" font-size="9.5" text-anchor="middle">10: return url_textura_transparente</text>

  <!-- OPT: Guardar sesion de uso en T_VESTIDOR_VIRTUAL -->
  <rect x="50" y="660" width="{width - 90}" height="70" fill="none" stroke="#000000" stroke-width="1.2"/>
  <path d="M 50 660 L 95 660 L 105 675 L 105 682 L 50 682 Z" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="75" y="675" font-size="10" font-weight="bold" text-anchor="middle">opt</text>
  <text x="115" y="676" font-size="10" font-weight="bold">[REGISTRAR USO DEL VESTIDOR VIRTUAL]</text>

  <line x1="{x_srv + 6}" y1="700" x2="{x_vestidor - 6}" y2="700" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_srv + x_vestidor)/2}" y="692" font-size="9.5" text-anchor="middle">11: INSERT INTO T_VESTIDOR_VIRTUAL (ID_CLIENTE, ID_PRENDA_RA, NOW())</text>

  <!-- Retorno final -->
  <line x1="{x_srv - 6}" y1="760" x2="{x_screen + 6}" y2="760" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_screen + x_srv)/2}" y="752" font-size="10" text-anchor="middle">12: return textura_optimizada_ra</text>

  <line x1="{x_screen - 6}" y1="835" x2="{x_actor}" y2="835" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_actor + x_screen)/2}" y="827" font-size="10" text-anchor="middle">13: VisualizarPrendaSuperpuestaEnCuerpo(feed_en_vivo)</text>

</svg>
''')
    return "".join(svg)

# ==================== FUNCIÓN PRINCIPAL DE EJECUCIÓN ====================
DIAGRAMS_CONFIG = [
    {"name": "CU_W13_Interactuar_Asistente_Inteligente_Secuencia", "gen": generate_cu_w13_svg},
    {"name": "CU_W30_Gestionar_Promociones_Secuencia", "gen": generate_cu_w30_svg},
    {"name": "CU_W31_Consultar_Ventas_Reservas_Inventario_Secuencia", "gen": generate_cu_w31_svg},
    {"name": "CU_W32_Visualizar_Indicadores_Empresariales_Secuencia", "gen": generate_cu_w32_svg},
    {"name": "CU_W33_Generar_Reportes_Bajo_Demanda_Secuencia", "gen": generate_cu_w33_svg},
    {"name": "CU_M12_Obtener_Recomendaciones_Productos_Secuencia", "gen": generate_cu_m12_svg},
    {"name": "CU_M13_Interactuar_Asistente_Inteligente_Secuencia", "gen": generate_cu_m13_svg},
    {"name": "CU_M14_Utilizar_Vestidor_Virtual_Secuencia", "gen": generate_cu_m14_svg},
]

def main():
    out_dir = "docs/diagramas_secuencia"
    brain_dir = r"C:\Users\eddym\.gemini\antigravity-ide\brain\bce20c4d-ff88-4ad8-93ad-540bb85f5c37"

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(brain_dir, exist_ok=True)

    print(f"Iniciando generacion de los {len(DIAGRAMS_CONFIG)} Diagramas de Secuencia restantes...")

    for i, item in enumerate(DIAGRAMS_CONFIG, 1):
        file_base = item["name"]
        svg_file = os.path.join(out_dir, f"{file_base}.svg")
        png_file = os.path.join(out_dir, f"{file_base}.png")

        svg_code = item["gen"]()

        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg_code)

        # Renderizar PNG 2x con resvg_py
        png_data = resvg_py.svg_to_bytes(svg_code)
        with open(png_file, "wb") as f:
            f.write(png_data)

        # Copiar al brain
        brain_png = os.path.join(brain_dir, os.path.basename(png_file))
        brain_svg = os.path.join(brain_dir, os.path.basename(svg_file))
        shutil.copy(png_file, brain_png)
        shutil.copy(svg_file, brain_svg)

        print(f" [{i:02d}/{len(DIAGRAMS_CONFIG)}] Generado: {file_base} (SVG y PNG 2x)")

    print("\nTodos los Diagramas de Secuencia restantes generados exitosamente.")

if __name__ == "__main__":
    main()
