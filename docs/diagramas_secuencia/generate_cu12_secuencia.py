#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del Diagrama de Secuencia UML para:
CU/W12: Obtener recomendaciones de productos (Moda & Colecciones Afines)
Basado en la BASE DE DATOS ACTUALIZADA (T_RECOMENDACION, T_BITACORA).

Aplica operadores combinados estándar UML:
- loop: Iteración sobre catálogo para cálculo de scoring de afinidad y tendencias.
- alt: Alternativa entre cliente con recomendaciones personalizadas vs visitante con tendencias más vendidas.
- opt: Enriquecimiento opcional con promociones vigentes y registro en T_BITACORA.
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

def generate_cu12_sequence_svg():
    width = 1380
    height = 920

    # Coordenadas X de los participantes
    x_actor = 80
    x_iu = 260
    x_controller = 480
    x_service = 720
    x_repo = 960
    x_recom = 1160
    x_bitacora = 1310

    y_header_box = 85
    h_header_box = 36
    w_box = 130
    y_line_start = y_header_box + h_header_box
    y_line_end = 880

    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
  <defs>
    <!-- Marcador de flecha sincrónica (cerrada y rellena) -->
    <marker id="arrow_sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/>
    </marker>
    <!-- Marcador de retorno / asincrónico (flecha abierta) -->
    <marker id="arrow_return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9" fill="none" stroke="#000000" stroke-width="1.4"/>
    </marker>
  </defs>

  <!-- Marco Exterior -->
  <rect x="15" y="15" width="{width - 30}" height="{height - 30}" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  
  <!-- Pestaña de Título estilo UML -->
  <path d="M 15 15 L 450 15 L 465 35 L 465 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12.5" font-weight="bold" fill="#000000">CU/W12: Obtener recomendaciones de productos</text>

  <!-- ==================== PARTICIPANTES ==================== -->

  <!-- Actor: CLIENTE -->
  <g transform="translate({x_actor}, 55)">
    <circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/>
    <line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/>
    <text x="0" y="78" font-size="11" font-weight="bold" text-anchor="middle" fill="#000000">CLIENTE</text>
  </g>

  <!-- IU_Recomendaciones -->
  <g>
    <rect x="{x_iu - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_iu}" y="{y_header_box + 22}" font-size="11" font-weight="bold" text-anchor="middle" fill="#000000">IU_Recomendaciones</text>
  </g>

  <!-- catalogo_routes -->
  <g>
    <rect x="{x_controller - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_controller}" y="{y_header_box + 22}" font-size="11.5" font-weight="bold" text-anchor="middle" fill="#000000">catalogo_routes</text>
  </g>

  <!-- catalogo_services -->
  <g>
    <rect x="{x_service - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_service}" y="{y_header_box + 22}" font-size="11.5" font-weight="bold" text-anchor="middle" fill="#000000">catalogo_services</text>
  </g>

  <!-- catalogo_repos -->
  <g>
    <rect x="{x_repo - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_repo}" y="{y_header_box + 22}" font-size="11.5" font-weight="bold" text-anchor="middle" fill="#000000">catalogo_repos</text>
  </g>

  <!-- T_RECOMENDACION (Entity BD Actualizada) -->
  <g>
    <rect x="{x_recom - 65}" y="{y_header_box}" width="130" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_recom}" y="{y_header_box + 22}" font-size="11" font-weight="bold" text-anchor="middle" fill="#000000">T_RECOMENDACION</text>
  </g>

  <!-- T_BITACORA (Entity BD Actualizada) -->
  <g>
    <rect x="{x_bitacora - 50}" y="{y_header_box}" width="100" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_bitacora}" y="{y_header_box + 22}" font-size="11" font-weight="bold" text-anchor="middle" fill="#000000">T_BITACORA</text>
  </g>

  <!-- ==================== LÍNEAS DE VIDA (PUNTEADAS) ==================== -->
  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_iu}" y1="{y_line_start}" x2="{x_iu}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_controller}" y1="{y_line_start}" x2="{x_controller}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_service}" y1="{y_line_start}" x2="{x_service}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_repo}" y1="{y_line_start}" x2="{x_repo}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_recom}" y1="{y_line_start}" x2="{x_recom}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_bitacora}" y1="{y_line_start}" x2="{x_bitacora}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <!-- ==================== BARRAS DE ACTIVACIÓN ==================== -->
  <!-- IU_Recomendaciones -->
  <rect x="{x_iu - 6}" y="155" width="12" height="695" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  
  <!-- catalogo_routes -->
  <rect x="{x_controller - 6}" y="185" width="12" height="635" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- catalogo_services -->
  <rect x="{x_service - 6}" y="215" width="12" height="575" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- catalogo_repos -->
  <rect x="{x_repo - 6}" y="355" width="12" height="85" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_repo - 6}" y="485" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_repo - 6}" y="595" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- T_RECOMENDACION -->
  <rect x="{x_recom - 6}" y="385" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- T_BITACORA -->
  <rect x="{x_bitacora - 6}" y="700" width="12" height="35" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- ==================== MENSAJES INICIALES ==================== -->
  <!-- 1: CLIENTE -> IU_Recomendaciones -->
  <line x1="{x_actor}" y1="160" x2="{x_iu - 6}" y2="160" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_actor + x_iu)/2}" y="152" font-size="10.5" text-anchor="middle" fill="#000000">1: AbrirSeccionParaTi(filtros_estilo)</text>

  <!-- 2: IU_Recomendaciones -> catalogo_routes -->
  <line x1="{x_iu + 6}" y1="190" x2="{x_controller - 6}" y2="190" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_iu + x_controller)/2}" y="182" font-size="10.5" text-anchor="middle" fill="#000000">2: GET /api/catalogo/productos?orden=destacados</text>

  <!-- 3: catalogo_routes -> catalogo_services -->
  <line x1="{x_controller + 6}" y1="220" x2="{x_service - 6}" y2="220" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_controller + x_service)/2}" y="212" font-size="10.5" text-anchor="middle" fill="#000000">3: obtener_catalogo_recomendado(id_empresa, filtros)</text>

  <!-- ==================== FRAGMENTO LOOP: SCORING DE AFINIDAD ==================== -->
  <rect x="40" y="240" width="{width - 70}" height="70" fill="none" stroke="#000000" stroke-width="1.3"/>
  <!-- Pestaña loop -->
  <path d="M 40 240 L 95 240 L 105 257 L 105 265 L 40 265 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="70" y="257" font-size="11" font-weight="bold" text-anchor="middle" fill="#000000">loop</text>
  <text x="115" y="257" font-size="10.5" font-weight="bold" fill="#000000">[POR CADA PRENDA CANDIDATA]</text>

  <!-- 4: Auto-llamada catalogo_services -->
  <path d="M {x_service + 6} 270 L {x_service + 45} 270 L {x_service + 45} 295 L {x_service + 8} 295" fill="none" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{x_service + 52}" y="285" font-size="10" text-anchor="start" fill="#000000">4: calcular_scoring_afinidad(prenda, tendencias)</text>

  <!-- ==================== FRAGMENTO ALT: PERSONALIZADO VS TENDENCIAS ==================== -->
  <rect x="40" y="325" width="{width - 70}" height="225" fill="none" stroke="#000000" stroke-width="1.3"/>
  <!-- Pestaña alt -->
  <path d="M 40 325 L 95 325 L 105 342 L 105 350 L 40 350 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="70" y="342" font-size="11" font-weight="bold" text-anchor="middle" fill="#000000">alt</text>
  
  <!-- Guarda 1: CLIENTE CON RECOMENDACIONES PREVIAS -->
  <text x="115" y="343" font-size="10.5" font-weight="bold" fill="#000000">[CLIENTE IDENTIFICADO CON PERFIL Y PREFERENCIAS]</text>

  <!-- 5: catalogo_services -> catalogo_repos -->
  <line x1="{x_service + 6}" y1="365" x2="{x_repo - 6}" y2="365" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_service + x_repo)/2}" y="357" font-size="10" text-anchor="middle" fill="#000000">5: find_recomendaciones_cliente(id_cliente)</text>

  <!-- 6: catalogo_repos -> T_RECOMENDACION -->
  <line x1="{x_repo + 6}" y1="395" x2="{x_recom - 6}" y2="395" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_repo + x_recom)/2}" y="387" font-size="10" text-anchor="middle" fill="#000000">6: SELECT * FROM T_RECOMENDACION</text>

  <!-- 7: T_RECOMENDACION -> catalogo_repos (return) -->
  <line x1="{x_recom - 6}" y1="415" x2="{x_repo + 6}" y2="415" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_repo + x_recom)/2}" y="407" font-size="9.5" text-anchor="middle" fill="#000000">7: return tuplas_recomendaciones</text>

  <!-- 8: catalogo_repos -> catalogo_services (return) -->
  <line x1="{x_repo - 6}" y1="435" x2="{x_service + 6}" y2="435" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_service + x_repo)/2}" y="427" font-size="10" text-anchor="middle" fill="#000000">8: return lista_recomendaciones_personalizadas</text>

  <!-- Línea divisoria alt -->
  <line x1="40" y1="455" x2="{width - 30}" y2="455" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>
  
  <!-- Guarda 2: VISITANTE NUEVO O SIN HISTORIAL -->
  <text x="55" y="472" font-size="10.5" font-weight="bold" fill="#000000">[VISITANTE NUEVO / RECOMENDACIÓN POR POPULARIDAD GLOBAL]</text>

  <!-- 9: catalogo_services -> catalogo_repos -->
  <line x1="{x_service + 6}" y1="495" x2="{x_repo - 6}" y2="495" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_service + x_repo)/2}" y="487" font-size="10" text-anchor="middle" fill="#000000">9: find_prendas_populares_tendencia(id_empresa)</text>

  <!-- 10: catalogo_repos -> catalogo_services (return) -->
  <line x1="{x_repo - 6}" y1="520" x2="{x_service + 6}" y2="520" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_service + x_repo)/2}" y="512" font-size="10" text-anchor="middle" fill="#000000">10: return lista_prendas_destacadas</text>

  <!-- ==================== FRAGMENTO OPT: VINCULAR PROMOCIONES VIGENTES ==================== -->
  <rect x="40" y="565" width="{width - 70}" height="95" fill="none" stroke="#000000" stroke-width="1.3"/>
  <!-- Pestaña opt -->
  <path d="M 40 565 L 95 565 L 105 582 L 105 590 L 40 590 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="70" y="582" font-size="11" font-weight="bold" text-anchor="middle" fill="#000000">opt</text>
  <text x="115" y="583" font-size="10.5" font-weight="bold" fill="#000000">[VINCULAR OFERTAS Y DESCUENTOS DE T_PROMOCION_PRODUCTO]</text>

  <!-- 11: catalogo_services -> catalogo_repos -->
  <line x1="{x_service + 6}" y1="605" x2="{x_repo - 6}" y2="605" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_service + x_repo)/2}" y="597" font-size="10" text-anchor="middle" fill="#000000">11: asociar_descuentos_vigentes(prendas_ids)</text>

  <!-- 12: catalogo_repos -> catalogo_services (return) -->
  <line x1="{x_repo - 6}" y1="630" x2="{x_service + 6}" y2="630" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_service + x_repo)/2}" y="622" font-size="10" text-anchor="middle" fill="#000000">12: return prendas_con_descuento_aplicado</text>

  <!-- ==================== FRAGMENTO OPT: REGISTRAR AUDITORÍA ==================== -->
  <rect x="40" y="675" width="{width - 70}" height="75" fill="none" stroke="#000000" stroke-width="1.3"/>
  <!-- Pestaña opt -->
  <path d="M 40 675 L 95 675 L 105 692 L 105 700 L 40 700 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="70" y="692" font-size="11" font-weight="bold" text-anchor="middle" fill="#000000">opt</text>
  <text x="115" y="693" font-size="10.5" font-weight="bold" fill="#000000">[TRAZABILIDAD EN T_BITACORA]</text>

  <!-- 13: catalogo_services -> T_BITACORA -->
  <line x1="{x_service + 6}" y1="710" x2="{x_bitacora - 6}" y2="710" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_service + x_bitacora)/2}" y="702" font-size="10" text-anchor="middle" fill="#000000">13: registrar_evento_bitacora('RECOMENDACIONES_VISTAS', id_cliente)</text>

  <!-- ==================== RETORNOS FINALES ==================== -->
  <!-- 14: catalogo_services -> catalogo_routes (return) -->
  <line x1="{x_service - 6}" y1="770" x2="{x_controller + 6}" y2="770" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_controller + x_service)/2}" y="762" font-size="10.5" text-anchor="middle" fill="#000000">14: respuesta_exitosa(catalogo_recomendado)</text>

  <!-- 15: catalogo_routes -> IU_Recomendaciones (return HTTP 200) -->
  <line x1="{x_controller - 6}" y1="800" x2="{x_iu + 6}" y2="800" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_iu + x_controller)/2}" y="792" font-size="10.5" text-anchor="middle" fill="#000000">15: HTTP 200 OK (payload_recomendaciones)</text>

  <!-- 16: IU_Recomendaciones -> CLIENTE (Renderizado final) -->
  <line x1="{x_iu - 6}" y1="835" x2="{x_actor}" y2="835" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_actor + x_iu)/2}" y="827" font-size="10" text-anchor="middle" fill="#000000">16: MostrarPrendasRecomendadas()</text>

</svg>
''')

    return "".join(svg)

def main():
    output_dir = "docs/diagramas_secuencia"
    brain_dir = r"C:\Users\eddym\.gemini\antigravity-ide\brain\bce20c4d-ff88-4ad8-93ad-540bb85f5c37"

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(brain_dir, exist_ok=True)

    file_base = "CU_W12_Obtener_Recomendaciones_Productos_Secuencia"
    svg_file = os.path.join(output_dir, f"{file_base}.svg")
    png_file = os.path.join(output_dir, f"{file_base}.png")

    svg_code = generate_cu12_sequence_svg()

    with open(svg_file, "w", encoding="utf-8") as f:
        f.write(svg_code)

    # Renderizar PNG 2x con resvg_py
    png_data = resvg_py.svg_to_bytes(svg_code)
    with open(png_file, "wb") as f:
        f.write(png_data)

    # Copiar al directorio de artefactos del brain
    brain_png = os.path.join(brain_dir, os.path.basename(png_file))
    brain_svg = os.path.join(brain_dir, os.path.basename(svg_file))
    shutil.copy(png_file, brain_png)
    shutil.copy(svg_file, brain_svg)

    print("[OK] Diagrama de Secuencia CU/W12 generado con éxito")
    print(f"SVG: {svg_file}")
    print(f"PNG: {png_file}")

if __name__ == "__main__":
    main()
