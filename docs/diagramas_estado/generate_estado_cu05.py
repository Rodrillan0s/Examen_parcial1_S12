#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del Diagrama de Estado UML 2.5 para CU05 W/M: Buscar y filtrar productos
Basado exactamente en el modelo de cátedra de SI2 - UAGRM (ejemplo docente CU23):
- Título limpio superior centrado: CU05 W/M: Buscar y filtrar productos
- Estados en cajas redondeadas simples (#f4f4f4 con borde #777777)
- Estado inicial (círculo sólido negro) y estado final (diana concéntrica)
- Transiciones limpias con eventos/guardas/acciones sin solapamiento de líneas
- Sin bitácora en consultas de búsqueda/filtros
"""

import os
import sys
import xml.sax.saxutils
import cairosvg

def escape_xml(text):
    return xml.sax.saxutils.escape(str(text))

def generate_estado_cu05():
    out_dir = "/home/eddy/Escritorio/PROYECTOS/EP1-SI2/Examen_parcial1_S12/docs/diagramas_estado"
    os.makedirs(out_dir, exist_ok=True)

    svg_file = os.path.join(out_dir, "CU05_WM_Buscar_Filtrar_Productos_Estado.svg")
    png_file = os.path.join(out_dir, "CU05_WM_Buscar_Filtrar_Productos_Estado.png")

    w = 760
    h = 740
    cx = 380

    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n')

    # Marcador de flecha idéntico al modelo del docente
    parts.append('  <defs>\n')
    parts.append('    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">\n')
    parts.append('      <path d="M 0 1 L 7 4 L 0 7 Z" fill="#222222"/>\n')
    parts.append('    </marker>\n')
    parts.append('  </defs>\n\n')

    # Fondo blanco
    parts.append(f'  <rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>\n')

    # Título superior
    title = "CU05 W/M: Buscar y filtrar productos"
    parts.append(f'  <text x="{cx}" y="50" font-family="Arial, Helvetica, sans-serif" font-size="22" font-weight="normal" fill="#000000" text-anchor="middle">{escape_xml(title)}</text>\n\n')

    # 1. Estado Inicial
    init_y = 100
    parts.append('  <!-- Estado Inicial -->\n')
    parts.append(f'  <circle cx="{cx}" cy="{init_y}" r="11" fill="#222222"/>\n\n')

    # Helper para dibujar cajas de estado
    def draw_state(state_id, name, x, y, bw=185, bh=38):
        res = []
        res.append(f'  <!-- Estado: {name} -->\n')
        res.append(f'  <g id="{state_id}">\n')
        res.append(f'    <rect x="{x - bw/2}" y="{y}" width="{bw}" height="{bh}" rx="9" ry="9" fill="#f4f4f4" stroke="#777777" stroke-width="0.9"/>\n')
        res.append(f'    <text x="{x}" y="{y + bh/2 + 4.5}" font-family="Arial, Helvetica, sans-serif" font-size="12.5" fill="#111111" text-anchor="middle">{escape_xml(name)}</text>\n')
        res.append('  </g>\n')
        return "".join(res)

    # 2. Estado: CatalogoAbierto
    s1_y = 175
    parts.append(draw_state("s1", "CatalogoAbierto", cx, s1_y, 185, 38))

    # Transición Inicial -> CatalogoAbierto
    parts.append(f'  <line x1="{cx}" y1="{init_y + 11}" x2="{cx}" y2="{s1_y}" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')
    parts.append(f'  <text x="{cx + 10}" y="142" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#222222">abrir_catalogo()</text>\n\n')

    # 3. Estado: FiltrandoProductos
    s2_y = 275
    parts.append(draw_state("s2", "FiltrandoProductos", cx, s2_y, 185, 38))

    # Transición CatalogoAbierto -> FiltrandoProductos
    parts.append(f'  <line x1="{cx}" y1="{s1_y + 38}" x2="{cx}" y2="{s2_y}" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')
    parts.append(f'  <text x="{cx + 10}" y="240" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#222222">seleccionar_filtros(categoria, precio)</text>\n\n')

    # 4. Estado: ProcesandoConsulta
    s3_y = 375
    parts.append(draw_state("s3", "ProcesandoConsulta", cx, s3_y, 195, 38))

    # Transición FiltrandoProductos -> ProcesandoConsulta
    parts.append(f'  <line x1="{cx}" y1="{s2_y + 38}" x2="{cx}" y2="{s3_y}" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')
    parts.append(f'  <text x="{cx + 10}" y="340" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#222222">listar_catalogo_publico(filtros)</text>\n\n')

    # 5. Bifurcación:
    # Izquierda: SinCoincidencias
    # Derecha: ProductosMostrados
    left_x = 210
    right_x = 550
    branch_y = 505

    parts.append(draw_state("s4_err", "SinCoincidencias", left_x, branch_y, 175, 38))
    parts.append(draw_state("s4_ok", "ProductosMostrados", right_x, branch_y, 185, 38))

    # Flecha izquierda: ProcesandoConsulta -> SinCoincidencias (curva hacia la izquierda)
    parts.append(f'  <path d="M {cx - 50} {s3_y + 38} Q {left_x + 30} {s3_y + 70} {left_x} {branch_y}" fill="none" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')
    parts.append(f'  <text x="{left_x - 85}" y="450" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#222222">[Sin coincidencias]</text>\n\n')

    # Flecha derecha: ProcesandoConsulta -> ProductosMostrados (línea diagonal como en el ejemplo del docente)
    parts.append(f'  <line x1="{cx + 35}" y1="{s3_y + 38}" x2="{right_x - 30}" y2="{branch_y}" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')
    # Texto colocado a la derecha de la diagonal
    parts.append(f'  <text x="{cx + 115}" y="445" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#222222">[Productos encontrados] / renderizar_grid()</text>\n\n')

    # 6. Estado Final
    final_x = cx
    final_y = 655
    parts.append('  <!-- Estado Final -->\n')
    parts.append(f'  <circle cx="{final_x}" cy="{final_y}" r="14" fill="none" stroke="#222222" stroke-width="1.4"/>\n')
    parts.append(f'  <circle cx="{final_x}" cy="{final_y}" r="8.5" fill="#222222"/>\n\n')

    # Flecha: SinCoincidencias -> Estado Final
    parts.append(f'  <line x1="{left_x + 25}" y1="{branch_y + 38}" x2="{final_x - 14}" y2="{final_y - 8}" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')

    # Flecha: ProductosMostrados -> Estado Final
    parts.append(f'  <line x1="{right_x - 25}" y1="{branch_y + 38}" x2="{final_x + 14}" y2="{final_y - 8}" stroke="#222222" stroke-width="1.1" marker-end="url(#arrow)"/>\n')

    parts.append('</svg>\n')

    content = "".join(parts)
    with open(svg_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f" -> SVG Generado: {svg_file}")

    cairosvg.svg2png(bytestring=content.encode("utf-8"), write_to=png_file, scale=2.0)
    print(f" -> PNG 2x Generado: {png_file}")

if __name__ == "__main__":
    generate_estado_cu05()
