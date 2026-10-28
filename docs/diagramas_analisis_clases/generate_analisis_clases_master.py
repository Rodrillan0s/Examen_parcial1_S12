#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de los 16 Diagramas de Análisis de Clases (UML / ICONIX VOPC)
para el sistema AuroraStore en formato vectorial SVG y PNG de alta resolución (2x).

Colección completa de 16 Casos de Uso:
1.  CU01 W/M: Registrar usuario (P1)
2.  CU02 W/M: Iniciar sesión (P1)
3.  CU03 W/M: Gestionar perfil (P1)
4.  CU14 W: Gestionar usuarios y roles (P1)
5.  CU15 W: Gestionar empresas SaaS (P1 — Refactorización)
6.  CU16 W: Gestionar sucursales y ciudades (P1)
7.  CU17 W: Gestionar productos (P1)
8.  CU18 W: Gestionar categorías (P1)
9.  CU19 W: Gestionar tallas y colores (P1)
10. CU20 W: Gestionar temporadas y colecciones (P1)
11. CU21 W: Gestionar proveedores (P1)
12. CU34 W: Gestionar planes de suscripción (P2 — Nuevo)
13. CU35 W: Gestionar suscripciones empresariales (P2 — Nuevo)
14. CU36 W: Consultar plan y límites de suscripción (P2 — Nuevo)
15. CU41 W: Gestionar respaldos y restauraciones (P2 — Nuevo)
16. CU43 W: Gestionar asignaciones de empleados a sucursales (P2 — Nuevo)

Características:
- Cajas UML de 3 compartimentos calibradas según el ejemplo de gráficos provisto por el usuario.
- Mismas entidades utilizadas en el Análisis de Robustez.
- Mismas funciones e invocaciones modeladas en los Diagramas de Secuencia.
- Enlaces ortogonales con multiplicidades explícitas (1, 1..*, 0..*, etc.).
- Exportación directa a SVG y PNG (2x) mediante resvg_py.
"""

import os
import shutil
import resvg_py

from render_clases_base import render_diagram_svg

from specs_clases_auth import (
    get_cu01_clases,
    get_cu02_clases,
    get_cu03_clases,
    get_cu14_clases
)

from specs_clases_catalog import (
    get_cu15_clases,
    get_cu16_clases,
    get_cu17_clases,
    get_cu18_clases,
    get_cu19_clases,
    get_cu20_clases,
    get_cu21_clases
)

from specs_clases_saas import (
    get_cu34_clases,
    get_cu35_clases,
    get_cu36_clases,
    get_cu41_clases,
    get_cu43_clases
)

ALL_DIAGRAM_BUILDERS = [
    ("CU01", get_cu01_clases),
    ("CU02", get_cu02_clases),
    ("CU03", get_cu03_clases),
    ("CU14", get_cu14_clases),
    ("CU15", get_cu15_clases),
    ("CU16", get_cu16_clases),
    ("CU17", get_cu17_clases),
    ("CU18", get_cu18_clases),
    ("CU19", get_cu19_clases),
    ("CU20", get_cu20_clases),
    ("CU21", get_cu21_clases),
    ("CU34", get_cu34_clases),
    ("CU35", get_cu35_clases),
    ("CU36", get_cu36_clases),
    ("CU41", get_cu41_clases),
    ("CU43", get_cu43_clases),
]

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    brain_dir = r"C:\Users\eddym\.gemini\antigravity-ide\brain\bce20c4d-ff88-4ad8-93ad-540bb85f5c37"
    
    os.makedirs(base_dir, exist_ok=True)
    if os.path.exists(brain_dir):
        os.makedirs(brain_dir, exist_ok=True)

    total = len(ALL_DIAGRAM_BUILDERS)
    print(f"Iniciando generacion de los {total} Diagramas de Analisis de Clases (UML / ICONIX VOPC)...")

    generated_files = []

    for idx, (code, builder) in enumerate(ALL_DIAGRAM_BUILDERS, 1):
        diag = builder()
        file_base = diag["file_name"]
        svg_file = os.path.join(base_dir, f"{file_base}.svg")
        png_file = os.path.join(base_dir, f"{file_base}.png")

        # 1. Renderizar SVG
        svg_code = render_diagram_svg(diag)
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg_code)

        # 2. Renderizar PNG 2x con resvg_py
        png_data = resvg_py.svg_to_bytes(svg_code)
        with open(png_file, "wb") as f:
            f.write(png_data)

        # 3. Copiar a la carpeta de artefactos si existe
        if os.path.exists(brain_dir):
            shutil.copy(png_file, os.path.join(brain_dir, f"{file_base}.png"))
            shutil.copy(svg_file, os.path.join(brain_dir, f"{file_base}.svg"))

        classes_count = len(diag["classes"])
        conns_count = len(diag.get("connections", []))
        print(f" [{idx:02d}/{total:02d}] Generado: {file_base} ({classes_count} clases, {conns_count} asociaciones) -> SVG y PNG 2x")
        generated_files.append((code, diag["title"], f"{file_base}.svg", f"{file_base}.png", classes_count, conns_count))

    print(f"\nExito: {total} Diagramas de Analisis de Clases generados y exportados correctamente en {base_dir}")

if __name__ == "__main__":
    main()
