#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Diagrama de Secuencia UML para:
CU05 W/M: Buscar y filtrar productos

Reglas aplicadas:
1. Documenta estrictamente las FUNCIONES que se invocan entre capas (no código SQL ni implementación interna).
2. Estructura estándar:
   Actor (CLIENTE) -> IU_Catalogo -> catalogo_routes -> catalogo_services -> catalogo_repos -> T_BITACORA
3. Visualización limpia y sin solapamientos, idéntica al estilo de cátedra (media_1788651647326.png):
   - Marco exterior con pestaña de título en la esquina superior izquierda.
   - Pestañas y cajas 'alt' (alternativas) y 'opt' (opcional).
   - Barras de activación sobre líneas de vida punteadas.
   - Flechas sincrónicas (rellenas) y retornos (línea discontinua con flecha abierta).
"""

import os
import cairosvg

def escape_xml(s):
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))

def generate_cu05_sequence_svg():
    width = 1320
    height = 860

    # Coordenadas X con separación holgada para firmas de funciones
    x_actor = 90
    x_iu = 290
    x_controller = 530
    x_service = 780
    x_repo = 1040
    x_bitacora = 1240

    y_header_box = 85
    h_header_box = 36
    w_box = 140
    y_line_start = y_header_box + h_header_box
    y_line_end = 820

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
  <path d="M 15 15 L 340 15 L 355 35 L 355 45 L 15 45 Z" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
  <text x="30" y="34" font-size="12.5" font-weight="bold" fill="#000000">CU05 W/M: Buscar y filtrar productos</text>

  <!-- ==================== PARTICIPANTES ==================== -->

  <!-- Actor: CLIENTE -->
  <g transform="translate({x_actor}, 55)">
    <circle cx="0" cy="18" r="9" fill="#ffffff" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="27" x2="0" y2="48" stroke="#000000" stroke-width="1.5"/>
    <line x1="-15" y1="35" x2="15" y2="35" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="48" x2="-12" y2="65" stroke="#000000" stroke-width="1.5"/>
    <line x1="0" y1="48" x2="12" y2="65" stroke="#000000" stroke-width="1.5"/>
    <text x="0" y="78" font-size="11.5" font-weight="bold" text-anchor="middle" fill="#000000">CLIENTE</text>
  </g>

  <!-- IU_Catalogo -->
  <g>
    <rect x="{x_iu - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_iu}" y="{y_header_box + 22}" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">IU_Catalogo</text>
  </g>

  <!-- catalogo_routes -->
  <g>
    <rect x="{x_controller - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_controller}" y="{y_header_box + 22}" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">catalogo_routes</text>
  </g>

  <!-- catalogo_services -->
  <g>
    <rect x="{x_service - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_service}" y="{y_header_box + 22}" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">catalogo_services</text>
  </g>

  <!-- catalogo_repos -->
  <g>
    <rect x="{x_repo - w_box/2}" y="{y_header_box}" width="{w_box}" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_repo}" y="{y_header_box + 22}" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">catalogo_repos</text>
  </g>

  <!-- T_BITACORA -->
  <g>
    <rect x="{x_bitacora - 55}" y="{y_header_box}" width="110" height="{h_header_box}" fill="#ffffff" stroke="#000000" stroke-width="1.4"/>
    <text x="{x_bitacora}" y="{y_header_box + 22}" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">T_BITACORA</text>
  </g>

  <!-- ==================== LÍNEAS DE VIDA (PUNTEADAS) ==================== -->
  <line x1="{x_actor}" y1="138" x2="{x_actor}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_iu}" y1="{y_line_start}" x2="{x_iu}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_controller}" y1="{y_line_start}" x2="{x_controller}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_service}" y1="{y_line_start}" x2="{x_service}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_repo}" y1="{y_line_start}" x2="{x_repo}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>
  <line x1="{x_bitacora}" y1="{y_line_start}" x2="{x_bitacora}" y2="{y_line_end}" stroke="#000000" stroke-width="1" stroke-dasharray="5,5"/>

  <!-- ==================== BARRAS DE ACTIVACIÓN ==================== -->
  <!-- IU_Catalogo: activo durante todo el ciclo -->
  <rect x="{x_iu - 6}" y="160" width="12" height="615" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  
  <!-- catalogo_routes: activo durante consulta y luego durante opt -->
  <rect x="{x_controller - 6}" y="195" width="12" height="325" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_controller - 6}" y="590" width="12" height="155" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- catalogo_services: activo durante lógica de negocio -->
  <rect x="{x_service - 6}" y="225" width="12" height="270" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_service - 6}" y="620" width="12" height="105" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- catalogo_repos: consultas repositorio -->
  <rect x="{x_repo - 6}" y="295" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_repo - 6}" y="435" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <rect x="{x_repo - 6}" y="650" width="12" height="40" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- T_BITACORA: registro auditoría -->
  <rect x="{x_bitacora - 6}" y="355" width="12" height="30" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>

  <!-- ==================== MENSAJES INICIALES ==================== -->
  <!-- 1: CLIENTE -> IU_Catalogo -->
  <line x1="{x_actor}" y1="165" x2="{x_iu - 6}" y2="165" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_actor + x_iu)/2}" y="157" font-size="11" text-anchor="middle" fill="#000000">1: SeleccionarFiltros(filtros)</text>

  <!-- 2: IU_Catalogo -> catalogo_routes -->
  <line x1="{x_iu + 6}" y1="200" x2="{x_controller - 6}" y2="200" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_iu + x_controller)/2}" y="192" font-size="11" text-anchor="middle" fill="#000000">2: GET /api/catalogo/productos</text>

  <!-- 3: catalogo_routes -> catalogo_services -->
  <line x1="{x_controller + 6}" y1="230" x2="{x_service - 6}" y2="230" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_controller + x_service)/2}" y="222" font-size="11" text-anchor="middle" fill="#000000">3: filtrar_catalogo(criterios)</text>

  <!-- ==================== FRAGMENTO ALT: RESULTADOS ==================== -->
  <rect x="40" y="260" width="{width - 70}" height="280" fill="none" stroke="#000000" stroke-width="1.3"/>
  <!-- Pestaña alt -->
  <path d="M 40 260 L 95 260 L 105 277 L 105 285 L 40 285 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="70" y="277" font-size="11.5" font-weight="bold" text-anchor="middle" fill="#000000">alt</text>
  
  <!-- Guarda 1: PRODUCTOS ENCONTRADOS -->
  <text x="118" y="278" font-size="11" font-weight="bold" fill="#000000">[PRODUCTOS ENCONTRADOS]</text>

  <!-- 4: catalogo_services -> catalogo_repos -->
  <line x1="{x_service + 6}" y1="300" x2="{x_repo - 6}" y2="300" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_service + x_repo)/2}" y="292" font-size="10.5" text-anchor="middle" fill="#000000">4: listar_catalogo_publico(id_empresa, filtros)</text>

  <!-- 5: catalogo_repos -> catalogo_services (return) -->
  <line x1="{x_repo - 6}" y1="330" x2="{x_service + 6}" y2="330" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_service + x_repo)/2}" y="322" font-size="10.5" text-anchor="middle" fill="#000000">5: return lista_productos</text>

  <!-- 6: catalogo_services -> T_BITACORA -->
  <line x1="{x_service + 6}" y1="360" x2="{x_bitacora - 6}" y2="360" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_service + x_repo)/2}" y="352" font-size="10.5" text-anchor="middle" fill="#000000">6: registrar_bitacora(ACCION, filtros)</text>

  <!-- 7: catalogo_services -> catalogo_routes (return) -->
  <line x1="{x_service - 6}" y1="390" x2="{x_controller + 6}" y2="390" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_controller + x_service)/2}" y="382" font-size="10.5" text-anchor="middle" fill="#000000">7: respuesta_exitosa(productos)</text>

  <!-- 8: catalogo_routes -> IU_Catalogo -->
  <line x1="{x_controller - 6}" y1="410" x2="{x_iu + 6}" y2="410" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_iu + x_controller)/2}" y="402" font-size="10.5" text-anchor="middle" fill="#000000">8: RenderizarCatalogo(productos)</text>

  <!-- Línea divisoria alt -->
  <line x1="40" y1="425" x2="{width - 30}" y2="425" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4"/>
  
  <!-- Guarda 2: SIN RESULTADOS -->
  <text x="55" y="442" font-size="11" font-weight="bold" fill="#000000">[SIN RESULTADOS]</text>

  <!-- 9: catalogo_repos -> catalogo_services (return vacio) -->
  <line x1="{x_repo - 6}" y1="455" x2="{x_service + 6}" y2="455" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_service + x_repo)/2}" y="447" font-size="10.5" text-anchor="middle" fill="#000000">9: return lista_vacia</text>

  <!-- 10: catalogo_services -> catalogo_routes -->
  <line x1="{x_service - 6}" y1="485" x2="{x_controller + 6}" y2="485" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_controller + x_service)/2}" y="477" font-size="10.5" text-anchor="middle" fill="#000000">10: respuesta_vacia()</text>

  <!-- 11: catalogo_routes -> IU_Catalogo -->
  <line x1="{x_controller - 6}" y1="515" x2="{x_iu + 6}" y2="515" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_iu + x_controller)/2}" y="507" font-size="10.5" text-anchor="middle" fill="#000000">11: MostrarAlerta("Sin coincidencias")</text>

  <!-- ==================== FRAGMENTO OPT: CONSULTAR FILTROS DISPONIBLES ==================== -->
  <rect x="40" y="555" width="{width - 70}" height="205" fill="none" stroke="#000000" stroke-width="1.3"/>
  <!-- Pestaña opt -->
  <path d="M 40 555 L 95 555 L 105 572 L 105 580 L 40 580 Z" fill="#ffffff" stroke="#000000" stroke-width="1.3"/>
  <text x="70" y="572" font-size="11.5" font-weight="bold" text-anchor="middle" fill="#000000">opt</text>
  
  <!-- Guarda opt -->
  <text x="118" y="573" font-size="11" font-weight="bold" fill="#000000">[CARGAR METADATOS DE FILTROS]</text>

  <!-- 12: IU_Catalogo -> catalogo_routes -->
  <line x1="{x_iu + 6}" y1="595" x2="{x_controller - 6}" y2="595" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_iu + x_controller)/2}" y="587" font-size="10.5" text-anchor="middle" fill="#000000">12: GET /api/catalogo/filtros</text>

  <!-- 13: catalogo_routes -> catalogo_services -->
  <line x1="{x_controller + 6}" y1="625" x2="{x_service - 6}" y2="625" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_controller + x_service)/2}" y="617" font-size="10.5" text-anchor="middle" fill="#000000">13: obtener_filtros_disponibles(id_empresa)</text>

  <!-- 14: catalogo_services -> catalogo_repos -->
  <line x1="{x_service + 6}" y1="655" x2="{x_repo - 6}" y2="655" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow_sync)"/>
  <text x="{(x_service + x_repo)/2}" y="647" font-size="10.5" text-anchor="middle" fill="#000000">14: obtener_filtros_disponibles(id_empresa)</text>

  <!-- 15: catalogo_repos -> catalogo_services (return) -->
  <line x1="{x_repo - 6}" y1="685" x2="{x_service + 6}" y2="685" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_service + x_repo)/2}" y="677" font-size="10.5" text-anchor="middle" fill="#000000">15: return filtros</text>

  <!-- 16: catalogo_services -> catalogo_routes -->
  <line x1="{x_service - 6}" y1="710" x2="{x_controller + 6}" y2="710" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_controller + x_service)/2}" y="702" font-size="10.5" text-anchor="middle" fill="#000000">16: respuesta_filtros(filtros)</text>

  <!-- 17: catalogo_routes -> IU_Catalogo -->
  <line x1="{x_controller - 6}" y1="735" x2="{x_iu + 6}" y2="735" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_iu + x_controller)/2}" y="727" font-size="10.5" text-anchor="middle" fill="#000000">17: CargarSelectores(filtros)</text>

  <!-- Mensaje final a CLIENTE -->
  <line x1="{x_iu - 6}" y1="760" x2="{x_actor}" y2="760" stroke="#000000" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arrow_return)"/>
  <text x="{(x_actor + x_iu)/2}" y="752" font-size="11" text-anchor="middle" fill="#000000">18: MostrarCatalogo()</text>

</svg>
''')

    return "".join(svg)

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    svg_path = os.path.join(out_dir, "CU05_WM_Buscar_Filtrar_Productos_Secuencia.svg")
    png_path = os.path.join(out_dir, "CU05_WM_Buscar_Filtrar_Productos_Secuencia.png")

    svg_content = generate_cu05_sequence_svg()
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"✅ SVG generado en: {svg_path}")
    cairosvg.svg2png(bytestring=svg_content.encode("utf-8"), write_to=png_path, scale=2.0)
    print(f"✅ PNG (2x) generado en: {png_path}")

if __name__ == "__main__":
    main()
