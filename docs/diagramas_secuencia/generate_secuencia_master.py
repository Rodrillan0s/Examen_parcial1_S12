#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de Diagramas de Secuencia UML 2.5+ según la metodología ICONIX (Doug Rosenberg)
para el sistema AuroraStore en formato multi-diagrama nativo Draw.io (.drawio / .xml).

Colección completa de 16 Casos de Uso:
1.  CU01: Registrar usuario (P1)
2.  CU02: Iniciar sesión (P1)
3.  CU03: Gestionar perfil (P1)
4.  CU14: Gestionar usuarios y roles (P1)
5.  CU15: Gestionar empresas SaaS (P1 — Refactorización)
6.  CU16: Gestionar sucursales y ciudades (P1)
7.  CU17: Gestionar productos (P1)
8.  CU18: Gestionar categorías (P1)
9.  CU19: Gestionar tallas y colores (P1)
10. CU20: Gestionar temporadas y colecciones (P1)
11. CU21: Gestionar proveedores (P1)
12. CU34: Gestionar planes de suscripción (P2 — Nuevo)
13. CU35: Gestionar suscripciones empresariales (P2 — Nuevo)
14. CU36: Consultar plan y límites de suscripción (P2 — Nuevo)
15. CU41: Gestionar respaldos y restauraciones (P2 — Nuevo)
16. CU43: Gestionar asignaciones de empleados a sucursales (P2 — Nuevo)

Características de conformidad:
- Estereotipos ICONIX: Boundary, Control, Entity asociados a software real.
- Mensajes estrictamente funcionales con parámetros tipados.
- Fragmentos combinados UML 2.5+: loop, alt, opt con divisores y guardas.
- Especificaciones de ejecución (barras de activación) verticales ajustadas a duración.
"""

import os
import html
import xml.etree.ElementTree as ET

# Importar especificaciones modulares
from specs_cu_auth import (
    build_cu01_spec,
    build_cu02_spec,
    build_cu03_spec,
    build_cu14_spec
)
from specs_cu_catalog import (
    build_cu15_spec,
    build_cu16_spec,
    build_cu17_spec,
    build_cu18_spec,
    build_cu19_spec,
    build_cu20_spec,
    build_cu21_spec
)
from specs_cu_saas import (
    build_cu34_spec,
    build_cu35_spec,
    build_cu36_spec,
    build_cu41_spec,
    build_cu43_spec
)

def render_sequence_xml(diag_spec):
    parts = []
    parts.append(f'  <diagram id="{diag_spec["id"]}" name="{diag_spec["name"]}">')
    parts.append('    <mxGraphModel dx="1800" dy="1200" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1550" pageHeight="1120" background="#ffffff" math="0" shadow="0">')
    parts.append('      <root>')
    parts.append('        <mxCell id="0" />')
    parts.append('        <mxCell id="1" parent="0" />')

    # Nodos (Marcos, Líneas de vida, Activaciones, Fragmentos UML)
    for n in diag_spec["nodes"]:
        val_esc = html.escape(n["value"])
        style_esc = html.escape(n["style"])
        parts.append(
            f'        <mxCell id="{n["id"]}" value="{val_esc}" style="{style_esc}" vertex="1" parent="1">'
        )
        parts.append(
            f'          <mxGeometry x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" as="geometry" />'
        )
        parts.append('        </mxCell>')

    # Mensajes / Conexiones (Llamadas sincrónicas, asincrónicas, retornos y errores)
    for e in diag_spec["edges"]:
        val_esc = html.escape(e["value"])
        style_with_points = (
            f'{e["style"]}exitX={e["exitX"]};exitY={e["exitY"]};entryX={e["entryX"]};entryY={e["entryY"]};'
        )
        style_esc = html.escape(style_with_points)
        parts.append(
            f'        <mxCell id="{e["id"]}" value="{val_esc}" style="{style_esc}" edge="1" parent="1" source="{e["source"]}" target="{e["target"]}">'
        )
        parts.append('          <mxGeometry relative="1" as="geometry" />')
        parts.append('        </mxCell>')

    parts.append('      </root>')
    parts.append('    </mxGraphModel>')
    parts.append('  </diagram>')
    return "\n".join(parts)

def generate_all_sequence_diagrams():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    drawio_path = os.path.join(out_dir, "diagramas_secuencia.drawio")
    xml_path = os.path.join(out_dir, "diagramas_secuencia.xml")

    builders = [
        ("CU01", build_cu01_spec),
        ("CU02", build_cu02_spec),
        ("CU03", build_cu03_spec),
        ("CU14", build_cu14_spec),
        ("CU15", build_cu15_spec),
        ("CU16", build_cu16_spec),
        ("CU17", build_cu17_spec),
        ("CU18", build_cu18_spec),
        ("CU19", build_cu19_spec),
        ("CU20", build_cu20_spec),
        ("CU21", build_cu21_spec),
        ("CU34", build_cu34_spec),
        ("CU35", build_cu35_spec),
        ("CU36", build_cu36_spec),
        ("CU41", build_cu41_spec),
        ("CU43", build_cu43_spec),
    ]

    print(f"Iniciando compilación de {len(builders)} diagramas de secuencia UML 2.5+ / ICONIX...")

    xml_lines = []
    xml_lines.append('<mxfile host="app.diagrams.net" modified="2026-10-25T03:00:00.000Z" agent="Antigravity" version="24.0.0" type="device">')

    total_nodes = 0
    total_edges = 0

    for code, builder in builders:
        spec = builder()
        nodes_count = len(spec["nodes"])
        edges_count = len(spec["edges"])
        total_nodes += nodes_count
        total_edges += edges_count
        print(f"  -> [{code}] {spec['name']} ({nodes_count} elementos, {edges_count} mensajes)")
        xml_lines.append(render_sequence_xml(spec))

    xml_lines.append('</mxfile>')

    full_xml = "\n".join(xml_lines)

    # Validación formal XML mediante parser nativo de Python
    try:
        root = ET.fromstring(full_xml)
        diag_count = len(root.findall("diagram"))
        print(f"\n[OK] Validación XML exitosa: {diag_count} pestañas válidas, {total_nodes} elementos gráficos y {total_edges} mensajes.")
    except ET.ParseError as err:
        print(f"\n[ERROR FATAL] Error de sintaxis XML: {err}")
        raise

    with open(drawio_path, "w", encoding="utf-8") as f:
        f.write(full_xml)
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(full_xml)

    file_size_kb = os.path.getsize(drawio_path) / 1024
    print(f"\nArchivos generados exitosamente ({file_size_kb:.2f} KB):")
    print(f"  - {drawio_path}")
    print(f"  - {xml_path}")

if __name__ == "__main__":
    generate_all_sequence_diagrams()
