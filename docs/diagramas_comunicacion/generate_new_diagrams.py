#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de Diagramas de Comunicación UML / Robustez (Iteraciones 2 y 3)
Específicamente adaptado al código fuente del sistema con:
1. Icono UML Control estricto (flecha curva adherida a la circunferencia).
2. Entidades de base de datos individuales y específicas con estereotipo UML (○_).
3. Inclusión de t_bitacora para auditoría y trazabilidad.
4. Flujo completo y detallado (Entradas, Salidas, Ajustes, Validaciones de reglas de negocio).
"""

import os
import cairosvg
import shutil

def escape_xml(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def draw_ctrl(cx_val, cy, r, name):
    escaped_name = escape_xml(name)
    return f'''  <!-- Controller: {escaped_name} -->
  <g>
    <circle cx="{cx_val}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <!-- Flecha circular del estándar UML Robustness adherida a la circunferencia -->
    <path d="M {cx_val + 18} {cy - r + 4} A {r + 4} {r + 4} 0 0 0 {cx_val - 6} {cy - r - 1}" fill="none" stroke="#111827" stroke-width="1.8"/>
    <path d="M {cx_val + 6} {cy - r - 10} L {cx_val - 6} {cy - r - 1} L {cx_val + 4} {cy - r + 8}" fill="none" stroke="#111827" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="{cx_val}" y="{cy + 5}" text-anchor="middle" font-size="12.5" font-weight="500">{escaped_name}</text>
  </g>\n'''

def generate_cu_w22(output_dir="docs/diagramas_comunicacion"):
    os.makedirs(output_dir, exist_ok=True)
    
    width = 2160
    height = 580
    cy = 290
    r = 46

    x_nodes = [110, 420, 740, 1060, 1380]
    
    # 3 entidades en columna x = 1860
    e_x = 1860
    e1_y = cy - 150   # t_inventario
    e2_y = cy         # t_movimiento_inventario
    e3_y = cy + 150   # t_bitacora

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif;">
  <defs>
    <!-- Flecha continua negra a la derecha -->
    <marker id="arrow-solid-right" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#111827"/>
    </marker>
    <!-- Flecha abierta punteada a la izquierda -->
    <marker id="arrow-open-left" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto">
      <path d="M 2 1.5 L 8 5 L 2 8.5" fill="none" stroke="#111827" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- Lineas guía -->
  <line x1="{x_nodes[0]}" y1="20" x2="{x_nodes[0]}" y2="{height-20}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="{x_nodes[1] - r - 14}" y1="20" x2="{x_nodes[1] - r - 14}" y2="{height-20}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="{e_x}" y1="20" x2="{e_x}" y2="{height-20}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="20" y1="{cy + 46}" x2="{width - 20}" y2="{cy + 46}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>

  <!-- 1. Actor to Boundary -->
  <line x1="{x_nodes[0] + 18}" y1="{cy}" x2="{x_nodes[1] - r - 14}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[0] + 18 + x_nodes[1] - r - 14)/2}" y="{cy - 22}" text-anchor="middle" font-size="11.5" font-weight="500">1.1: Consultar stock / registrar</text>
  <text x="{(x_nodes[0] + 18 + x_nodes[1] - r - 14)/2}" y="{cy - 8}" text-anchor="middle" font-size="11.5" font-weight="500">entrada, salida o ajuste()</text>
  
  <line x1="{x_nodes[1] - r - 24}" y1="{cy + 36}" x2="{x_nodes[0] + 28}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[0] + 18 + x_nodes[1] - r - 14)/2}" y="{cy + 26}" text-anchor="middle" font-size="11" font-weight="500">1.14: notificar resultado de operación()</text>

  <!-- 2. Boundary to Route -->
  <line x1="{x_nodes[1] + r}" y1="{cy}" x2="{x_nodes[2] - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[1] + r + x_nodes[2] - r)/2}" y="{cy - 22}" text-anchor="middle" font-size="11.5" font-weight="500">1.2: enviar tipo (ENTRADA/SALIDA/AJUSTE),</text>
  <text x="{(x_nodes[1] + r + x_nodes[2] - r)/2}" y="{cy - 8}" text-anchor="middle" font-size="11.5" font-weight="500">sucursal, variante y cantidad()</text>
  
  <line x1="{x_nodes[2] - r - 10}" y1="{cy + 36}" x2="{x_nodes[1] + r + 10}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[1] + r + x_nodes[2] - r)/2}" y="{cy + 26}" text-anchor="middle" font-size="11" font-weight="500">1.13: actualizar grilla de stock y alertas()</text>

  <!-- 3. Route to Service -->
  <line x1="{x_nodes[2] + r}" y1="{cy}" x2="{x_nodes[3] - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[2] + r + x_nodes[3] - r)/2}" y="{cy - 22}" text-anchor="middle" font-size="11.5" font-weight="500">1.3: procesar_movimiento_inventario()</text>
  <text x="{(x_nodes[2] + r + x_nodes[3] - r)/2}" y="{cy - 8}" text-anchor="middle" font-size="11.5" font-weight="500">con validación de permisos tenant</text>
  
  <line x1="{x_nodes[3] - r - 10}" y1="{cy + 36}" x2="{x_nodes[2] + r + 10}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[2] + r + x_nodes[3] - r)/2}" y="{cy + 26}" text-anchor="middle" font-size="11" font-weight="500">1.12: responder HTTP 200 OK con stock nuevo()</text>

  <!-- 4. Service to Repo -->
  <line x1="{x_nodes[3] + r}" y1="{cy}" x2="{x_nodes[4] - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[3] + r + x_nodes[4] - r)/2}" y="{cy - 22}" text-anchor="middle" font-size="11.5" font-weight="500">1.4: validar stock disponible &gt;= salida</text>
  <text x="{(x_nodes[3] + r + x_nodes[4] - r)/2}" y="{cy - 8}" text-anchor="middle" font-size="11.5" font-weight="500">y ajuste &gt;= stock_reservado()</text>
  
  <line x1="{x_nodes[4] - r - 10}" y1="{cy + 36}" x2="{x_nodes[3] + r + 10}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[3] + r + x_nodes[4] - r)/2}" y="{cy + 26}" text-anchor="middle" font-size="11" font-weight="500">1.11: retornar balances de stock actualizados()</text>

  <!-- ==================== CONEXIONES A LAS 3 ENTIDADES ==================== -->

  <!-- Branch 1: Repo to Entity 1 (t_inventario) [Arriba] -->
  <line x1="{x_nodes[4] + 32}" y1="{cy - 38}" x2="{e_x - r}" y2="{e1_y + 12}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + 32 + e_x - r)/2 + 20}" y="{(cy - 38 + e1_y + 12)/2 - 14}" text-anchor="middle" font-size="11" font-weight="500">1.5: fn_movimiento_inventario() FOR UPDATE (modificar stock)</text>
  
  <line x1="{e_x - r - 15}" y1="{e1_y + 36}" x2="{x_nodes[4] + 38}" y2="{cy - 12}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + 38 + e_x - r - 15)/2 + 20}" y="{(cy - 12 + e1_y + 36)/2 + 18}" text-anchor="middle" font-size="10.5" font-weight="500">1.6: confirmar stock nuevo (actual y disponible)</text>

  <!-- Branch 2: Repo to Entity 2 (t_movimiento_inventario) [Horizontal centro] -->
  <line x1="{x_nodes[4] + r}" y1="{cy}" x2="{e_x - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + r + e_x - r)/2}" y="{cy - 12}" text-anchor="middle" font-size="11" font-weight="500">1.7: insertar en t_movimiento (ENTRADA / SALIDA / AJUSTE)</text>
  
  <line x1="{e_x - r - 10}" y1="{cy + 36}" x2="{x_nodes[4] + r + 10}" y2="{cy + 36}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + r + e_x - r)/2}" y="{cy + 26}" text-anchor="middle" font-size="10.5" font-weight="500">1.8: confirmar registro de movimiento histórico</text>

  <!-- Branch 3: Repo to Entity 3 (t_bitacora) [Abajo] -->
  <line x1="{x_nodes[4] + 32}" y1="{cy + 38}" x2="{e_x - r}" y2="{e3_y - 12}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>
  <text x="{(x_nodes[4] + 32 + e_x - r)/2 + 20}" y="{(cy + 38 + e3_y - 12)/2 - 12}" text-anchor="middle" font-size="11" font-weight="500">1.9: registrar_evento_db() auditoría de inventario</text>
  
  <line x1="{e_x - r - 15}" y1="{e3_y + 14}" x2="{x_nodes[4] + 38}" y2="{cy + 64}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>
  <text x="{(x_nodes[4] + 38 + e_x - r - 15)/2 + 20}" y="{(cy + 64 + e3_y + 14)/2 + 18}" text-anchor="middle" font-size="10.5" font-weight="500">1.10: confirmar persistencia en t_bitacora</text>

  <!-- ==================== NODOS ==================== -->

  <!-- 1. Actor -->
  <g id="actor">
    <circle cx="{x_nodes[0]}" cy="{cy - 36}" r="13" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{x_nodes[0]}" y1="{cy - 23}" x2="{x_nodes[0]}" y2="{cy + 14}" stroke="#111827" stroke-width="1.8"/>
    <line x1="{x_nodes[0] - 18}" y1="{cy - 12}" x2="{x_nodes[0] + 18}" y2="{cy - 12}" stroke="#111827" stroke-width="1.8"/>
    <line x1="{x_nodes[0]}" y1="{cy + 14}" x2="{x_nodes[0] - 14}" y2="{cy + 42}" stroke="#111827" stroke-width="1.8"/>
    <line x1="{x_nodes[0]}" y1="{cy + 14}" x2="{x_nodes[0] + 14}" y2="{cy + 42}" stroke="#111827" stroke-width="1.8"/>
    <text x="{x_nodes[0]}" y="{cy + 62}" text-anchor="middle" font-size="12.5" font-weight="bold">ADMIN_TIENDA</text>
  </g>

  <!-- 2. Boundary -->
  <g id="boundary">
    <line x1="{x_nodes[1] - r - 14}" y1="{cy - 34}" x2="{x_nodes[1] - r - 14}" y2="{cy + 34}" stroke="#111827" stroke-width="2.2"/>
    <line x1="{x_nodes[1] - r - 14}" y1="{cy}" x2="{x_nodes[1] - r}" y2="{cy}" stroke="#111827" stroke-width="2.0"/>
    <circle cx="{x_nodes[1]}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <text x="{x_nodes[1]}" y="{cy + 5}" text-anchor="middle" font-size="13" font-weight="500">IU_Inventario</text>
  </g>
'''

    svg += draw_ctrl(x_nodes[2], cy, r, "inventario_routes")
    svg += draw_ctrl(x_nodes[3], cy, r, "inventario_services")
    svg += draw_ctrl(x_nodes[4], cy, r, "inventario_repos")

    # 3 ENTIDADES (Estereotipo UML Entity: círculo con barra horizontal plana inferior)
    # Entity 1: t_inventario (Arriba)
    svg += f'''  <!-- Entity 1: t_inventario -->
  <g id="entity1">
    <circle cx="{e_x}" cy="{e1_y}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{e_x - 32}" y1="{e1_y + r + 3}" x2="{e_x + 32}" y2="{e1_y + r + 3}" stroke="#111827" stroke-width="2.2"/>
    <text x="{e_x}" y="{e1_y + 5}" text-anchor="middle" font-size="12.5" font-weight="bold">t_inventario</text>
  </g>

  <!-- Entity 2: t_movimiento_inventario (Centro) -->
  <g id="entity2">
    <circle cx="{e_x}" cy="{e2_y}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{e_x - 32}" y1="{e2_y + r + 3}" x2="{e_x + 32}" y2="{e2_y + r + 3}" stroke="#111827" stroke-width="2.2"/>
    <text x="{e_x}" y="{e2_y - 4}" text-anchor="middle" font-size="11" font-weight="bold">t_movimiento_</text>
    <text x="{e_x}" y="{e2_y + 11}" text-anchor="middle" font-size="11" font-weight="bold">inventario</text>
  </g>

  <!-- Entity 3: t_bitacora (Abajo) -->
  <g id="entity3">
    <circle cx="{e_x}" cy="{e3_y}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <line x1="{e_x - 32}" y1="{e3_y + r + 3}" x2="{e_x + 32}" y2="{e3_y + r + 3}" stroke="#111827" stroke-width="2.2"/>
    <text x="{e_x}" y="{e3_y + 5}" text-anchor="middle" font-size="12.5" font-weight="bold">t_bitacora</text>
  </g>

  <text x="30" y="35" font-size="14" font-weight="bold" fill="#475569">CU/W22: Gestionar inventario (Entradas, Salidas, Ajustes y Auditoría)</text>
</svg>'''

    svg_file = os.path.join(output_dir, "CU_W22_Gestionar_Inventario.svg")
    png_file = os.path.join(output_dir, "CU_W22_Gestionar_Inventario.png")
    
    with open(svg_file, "w", encoding="utf-8") as f:
        f.write(svg)
    cairosvg.svg2png(url=svg_file, write_to=png_file, scale=2.0)
    
    # Copiar a artifacts para visualización
    shutil.copy(png_file, "/home/eddy/.gemini/antigravity-ide/brain/b5ff4fcb-4250-43ad-8cb8-b6447f7c448a/CU_W22_Gestionar_Inventario.png")
    print(f"✅ CU_W22 generado correctamente en {svg_file} y {png_file}")

if __name__ == "__main__":
    generate_cu_w22()
