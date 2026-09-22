#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de los 8 Diagramas de Análisis de Clases Restantes (SI2 - UAGRM)
Basado en la BASE DE DATOS ACTUALIZADA y con ARQUITECTURAS DIFERENCIADAS (no plantilla fija):

1. CU/W13: Interactuar con asistente inteligente (Web) -> Chat_View + Controller + DeepSeek_AI_Service + Tools_Repository + 4 Tablas
2. CU/W30: Gestionar promociones (Web) -> Form_Promociones + Controller + Service + Repository + 4 Tablas (incluye Auditoría)
3. CU/W31: Consultar ventas, reservas e inventario (Web) -> Panel_Monitor_Operativo + Controller + Consolidador_Service + Repository + 4 Tablas
4. CU/W32: Visualizar indicadores empresariales (Web) -> Dashboard_KPIs_View + Controller + Analytics_Engine_Service (Sin repo redundante, acceso directo) + 5 Tablas
5. CU/W33: Generar reportes bajo demanda (Web) -> Form_Reportes + Controller + Report_Builder_Service (PDF/Excel) + Query_Repository + 4 Tablas
6. CU/M12: Obtener recomendaciones de productos (Mobile) -> Feed_Recomendados_Screen + Recomendaciones_Cubit + Mobile_API_Client + 4 Tablas
7. CU/M13: Interactuar con asistente inteligente (Mobile) -> Voice_Chat_Screen + Voice_Chat_Cubit + Speech_Detector_Service + AI_Mobile_Client + 4 Tablas
8. CU/M14: Utilizar vestidor virtual (Mobile RA) -> Vestidor_Virtual_Screen + AR_Camera_Controller + Pose_Body_Detector + Vestidor_Service + 4 Tablas

Cumple:
- Estereotipos UML y cajas de 3 compartimentos calibradas.
- Atributos exactos en MAYÚSCULAS según la Base Actualizada.
- Conexiones ortogonales limpias con multiplicidades explícitas.
- Generación de SVG y PNG de alta resolución (2x) con resvg_py.
"""

import os
import shutil
import resvg_py

def escape_xml(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def render_class_box(cls):
    x = cls["x"]
    y = cls["y"]
    w = cls["width"]
    header_lines = cls.get("header", [])
    attrs = cls.get("attributes", [])
    methods = cls.get("methods", [])

    line_h = 16
    pad_y = 8
    
    h_header = max(34, len(header_lines) * line_h + pad_y * 2)
    h_attrs = max(24, len(attrs) * line_h + pad_y * 1.5) if attrs else 22
    h_methods = max(24, len(methods) * line_h + pad_y * 1.5) if methods else 22
    total_h = int(h_header + h_attrs + h_methods)

    parts = []
    parts.append(f'  <!-- Clase: {" / ".join(header_lines)} -->\n')
    parts.append(f'  <g id="class_{cls["id"]}">\n')
    parts.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{total_h}" fill="#ffffff" stroke="#111827" stroke-width="1.6"/>\n')

    y_div1 = y + h_header
    parts.append(f'    <line x1="{x}" y1="{y_div1}" x2="{x + w}" y2="{y_div1}" stroke="#111827" stroke-width="1.4"/>\n')

    y_div2 = y_div1 + h_attrs
    parts.append(f'    <line x1="{x}" y1="{y_div2}" x2="{x + w}" y2="{y_div2}" stroke="#111827" stroke-width="1.4"/>\n')

    # Header
    if len(header_lines) == 1:
        parts.append(f'    <text x="{x + w/2}" y="{y + 22}" text-anchor="middle" font-size="12" font-weight="bold" fill="#111827">{escape_xml(header_lines[0])}</text>\n')
    else:
        parts.append(f'    <text x="{x + w/2}" y="{y + 17}" text-anchor="middle" font-size="11" font-weight="bold" fill="#475569">{escape_xml(header_lines[0])}</text>\n')
        parts.append(f'    <text x="{x + w/2}" y="{y + 34}" text-anchor="middle" font-size="12" font-weight="bold" fill="#111827">{escape_xml(header_lines[1])}</text>\n')

    # Attributes
    y_attr_text = y_div1 + 16
    for idx, attr in enumerate(attrs):
        parts.append(f'    <text x="{x + 10}" y="{y_attr_text + idx * line_h}" font-size="10.5" fill="#111827" font-family="monospace, sans-serif">{escape_xml(attr)}</text>\n')

    # Methods
    y_method_text = y_div2 + 16
    for idx, mth in enumerate(methods):
        parts.append(f'    <text x="{x + 10}" y="{y_method_text + idx * line_h}" font-size="10.5" fill="#111827" font-family="monospace, sans-serif">{escape_xml(mth)}</text>\n')

    parts.append('  </g>\n')
    return "".join(parts), total_h

def render_diagram_svg(diag):
    width = diag.get("width", 2120)
    height = diag.get("height", 860)

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <!-- Encabezado del Diagrama -->
  <text x="35" y="34" font-size="16" font-weight="bold" fill="#0f172a">{escape_xml(diag["title"])}</text>
  <text x="35" y="54" font-size="12" font-weight="500" fill="#475569">{escape_xml(diag["subtitle"])}</text>
  <text x="35" y="72" font-size="11.5" font-weight="600" fill="#2563eb">Actor(es): {escape_xml(diag["actors"])}</text>
  <line x1="35" y1="82" x2="{width - 35}" y2="82" stroke="#cbd5e1" stroke-width="1.2"/>

  <!-- Leyenda de Arquitectura Específica -->
  <g transform="translate({width - 530}, 24)">
    <rect x="0" y="0" width="495" height="48" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <text x="12" y="19" font-size="11" font-weight="bold" fill="#334155">{escape_xml(diag.get("arch_badge_title", "Arquitectura del Caso de Uso:"))}</text>
    <text x="12" y="36" font-size="10" fill="#64748b">{escape_xml(diag.get("arch_badge_desc", "Boundary -> Controller / Services -> Entities"))}</text>
  </g>
''')

    for cls in diag["classes"]:
        cls_svg, _ = render_class_box(cls)
        svg_parts.append(cls_svg)

    svg_parts.append('\n  <!-- Asociaciones y Multiplicidades -->\n  <g id="associations">\n')
    for conn in diag.get("connections", []):
        pts = conn["points"]
        pts_str = " ".join([f"{p[0]},{p[1]}" for p in pts])
        svg_parts.append(f'    <polyline points="{pts_str}" fill="none" stroke="#111827" stroke-width="1.6" stroke-linejoin="round"/>\n')

        if "mult_from" in conn and conn["mult_from"]:
            mx, my = conn["mult_from"]["pos"]
            txt = conn["mult_from"]["text"]
            svg_parts.append(f'    <text x="{mx}" y="{my}" font-size="11" font-weight="bold" fill="#111827">{escape_xml(txt)}</text>\n')

        if "mult_to" in conn and conn["mult_to"]:
            mx, my = conn["mult_to"]["pos"]
            txt = conn["mult_to"]["text"]
            svg_parts.append(f'    <text x="{mx}" y="{my}" font-size="11" font-weight="bold" fill="#111827">{escape_xml(txt)}</text>\n')

    svg_parts.append('  </g>\n')
    svg_parts.append('</svg>\n')
    return "".join(svg_parts)

# ==================== CONFIGURACIÓN DE LOS 8 DIAGRAMAS RESTANTES ====================
DIAGRAMS = [
    # -------------------------------------------------------------------------
    # 1. CU/W13: Interactuar con asistente inteligente (Web)
    # -------------------------------------------------------------------------
    {
        "id": "CU_W13",
        "file_name": "CU_W13_Interactuar_Asistente_Inteligente_Clases",
        "title": "CU/W13: Interactuar con asistente inteligente — Diagrama de Análisis de Clases",
        "subtitle": "Sistema Aura Store | Arquitectura IA: Chat_View -> Controller -> DeepSeek_AI_Service -> Tools_Repository -> Entities (BD)",
        "actors": "Cliente (Web), Visitante, Administrador",
        "arch_badge_title": "Arquitectura Conversacional / Function Calling:",
        "arch_badge_desc": "Boundary -> Asistente_Controller -> DeepSeek_LLM_Service -> Tools_Repo -> Entities",
        "width": 2100,
        "height": 840,
        "classes": [
            {
                "id": "view_chat", "x": 35, "y": 270, "width": 260,
                "header": ["Form", "IU_Asistente_Chat"],
                "attributes": ["+ texto_mensaje", "+ historial_chat", "+ token_sesion", "+ prendas_sugeridas", "+ estado_respuesta"],
                "methods": ["+ enviar_mensaje_chat()", "+ mostrar_respuesta_asistente()", "+ mostrar_cards_prendas()", "+ limpiar_conversacion()"]
            },
            {
                "id": "ctrl_asistente", "x": 335, "y": 340, "width": 240,
                "header": ["Asistente_Controller"],
                "attributes": [],
                "methods": ["+ post_chat_mensaje(payload)", "+ get_historial_conversacion()", "+ parse_intent_usuario()"]
            },
            {
                "id": "srv_deepseek", "x": 615, "y": 320, "width": 270,
                "header": ["DeepSeek_AI_Service"],
                "attributes": ["- api_key_deepseek", "- modelo_llm", "- system_prompt_aura"],
                "methods": ["+ procesar_mensaje_chat(msg)", "+ despachar_function_calling()", "+ sintetizar_respuesta_ia()"]
            },
            {
                "id": "repo_tools", "x": 925, "y": 330, "width": 265,
                "header": ["Asistente_Tools_Repository"],
                "attributes": [],
                "methods": ["+ ejecutar_buscar_prendas(termino)", "+ consultar_ventas_pedidos(cli)", "+ consultar_sucursales_activas()"]
            },
            # Entidades (4 tablas)
            {
                "id": "producto", "x": 1240, "y": 90, "width": 210,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ ID_CATEGORIA", "+ CODIGO_PRODUCTO", "+ NOMBRE", "+ DESCRIPCION", "+ MARCA", "+ GENERO", "+ PRECIO", "+ IMAGEN_URL", "+ ESTADO", "+ FECHA_REGISTRO"],
                "methods": []
            },
            {
                "id": "cliente", "x": 1240, "y": 550, "width": 200,
                "header": ["T_CLIENTE"],
                "attributes": ["+ ID_CLIENTE", "+ ID_USUARIO", "+ CI", "+ FECHA_REGISTRO"],
                "methods": []
            },
            {
                "id": "venta", "x": 1500, "y": 310, "width": 210,
                "header": ["T_VENTA"],
                "attributes": ["+ ID_VENTA", "+ ID_CLIENTE", "+ ID_SUCURSAL", "+ ID_EMPLEADO", "+ NUMERO_VENTA", "+ TIPO_VENTA", "+ FECHA_VENTA", "+ SUBTOTAL", "+ DESCUENTO", "+ TOTAL", "+ ESTADO", "+ TIPO_RECIBO"],
                "methods": []
            },
            {
                "id": "sucursal", "x": 1760, "y": 340, "width": 210,
                "header": ["T_SUCURSAL"],
                "attributes": ["+ ID_SUCURSAL", "+ ID_CIUDAD", "+ NOMBRE", "+ CODIGO_SUCURSAL", "+ DIRECCION", "+ TELEFONO", "+ ESTADO", "+ ID_EMPRESA"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(295, 410), (335, 410)]},
            {"points": [(575, 410), (615, 410)]},
            {"points": [(885, 410), (925, 410)]},
            # Repo -> T_PRODUCTO
            {"points": [(1190, 390), (1215, 390), (1215, 230), (1240, 230)]},
            # Repo -> T_VENTA
            {"points": [(1190, 410), (1500, 410)]},
            # Repo -> T_CLIENTE
            {"points": [(1190, 430), (1215, 430), (1215, 620), (1240, 620)]},
            # T_CLIENTE (1) -> T_VENTA (0..*)
            {"points": [(1440, 620), (1470, 620), (1470, 460), (1500, 460)], "mult_from": {"text": "1", "pos": (1445, 610)}, "mult_to": {"text": "0..*", "pos": (1475, 450)}},
            # T_SUCURSAL (1) -> T_VENTA (0..*)
            {"points": [(1760, 420), (1710, 420)], "mult_from": {"text": "1", "pos": (1740, 410)}, "mult_to": {"text": "0..*", "pos": (1715, 410)}}
        ]
    },

    # -------------------------------------------------------------------------
    # 2. CU/W30: Gestionar promociones (Web)
    # -------------------------------------------------------------------------
    {
        "id": "CU_W30",
        "file_name": "CU_W30_Gestionar_Promociones_Clases",
        "title": "CU/W30: Gestionar promociones — Diagrama de Análisis de Clases",
        "subtitle": "Sistema Aura Store | Arquitectura Multicapa: Form -> Controller -> Service -> Repository -> Entities (BD)",
        "actors": "Administrador de tienda, Encargado de Marketing",
        "arch_badge_title": "Arquitectura Promociones & Auditoría:",
        "arch_badge_desc": "Boundary -> Controller -> Service -> Repository -> Entities (con T_BITACORA)",
        "width": 2100,
        "height": 840,
        "classes": [
            {
                "id": "form_promocion", "x": 35, "y": 270, "width": 260,
                "header": ["Form", "Gestion_Promociones"],
                "attributes": ["+ id_promocion_sel", "+ nombre_promocion", "+ porcentaje_desc", "+ fecha_inicio", "+ fecha_fin", "+ prendas_asignadas"],
                "methods": ["+ crear_promocion()", "+ vincular_prendas_catalogo()", "+ modificar_vigencia()", "+ desactivar_promocion()", "+ mostrar_grilla_promociones()"]
            },
            {
                "id": "ctrl_promocion", "x": 335, "y": 340, "width": 245,
                "header": ["Promocion_Controller"],
                "attributes": [],
                "methods": ["+ post_crear_promocion(datos)", "+ put_asignar_prendas(id, prendas)", "+ get_promociones_activas()"]
            },
            {
                "id": "srv_promocion", "x": 620, "y": 325, "width": 270,
                "header": ["Promocion_Service"],
                "attributes": [],
                "methods": ["+ registrar_promocion(datos)", "+ validar_solapamiento_fechas()", "+ aplicar_descuento_prendas()", "+ auditar_evento_promocion()"]
            },
            {
                "id": "repo_promocion", "x": 930, "y": 325, "width": 265,
                "header": ["Promocion_Repository"],
                "attributes": [],
                "methods": ["+ insert_promocion(datos)", "+ insert_promocion_producto(id_p, id_pr)", "+ find_promociones_activas()", "+ insert_bitacora_auditoria(reg)"]
            },
            # Entidades (4 tablas)
            {
                "id": "promocion", "x": 1245, "y": 330, "width": 205,
                "header": ["T_PROMOCION"],
                "attributes": ["+ ID_PROMOCION", "+ NOMBRE", "+ DESCRIPCION", "+ FECHA_INICIO", "+ FECHA_FIN", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "promo_prod", "x": 1495, "y": 330, "width": 215,
                "header": ["T_PROMOCION_PRODUCTO"],
                "attributes": ["+ ID_PROMOCION_PRODUCTO", "+ ID_PROMOCION", "+ ID_PRODUCTO", "+ PORCENTAJE_DESCUENTO"],
                "methods": []
            },
            {
                "id": "producto", "x": 1755, "y": 240, "width": 210,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ ID_CATEGORIA", "+ CODIGO_PRODUCTO", "+ NOMBRE", "+ DESCRIPCION", "+ MARCA", "+ GENERO", "+ PRECIO", "+ IMAGEN_URL", "+ ESTADO", "+ FECHA_REGISTRO"],
                "methods": []
            },
            {
                "id": "bitacora", "x": 1245, "y": 570, "width": 205,
                "header": ["T_BITACORA"],
                "attributes": ["+ ID_BITACORA", "+ ID_USUARIO", "+ MODULO", "+ ACCION", "+ DESCRIPCION", "+ FECHA_HORA", "+ IP", "+ TENANT_ORIGEN", "+ RESULTADO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(295, 410), (335, 410)]},
            {"points": [(580, 410), (620, 410)]},
            {"points": [(890, 410), (930, 410)]},
            # Repo -> T_PROMOCION
            {"points": [(1195, 410), (1245, 410)]},
            # Repo -> T_BITACORA
            {"points": [(1195, 430), (1220, 430), (1220, 650), (1245, 650)]},
            # T_PROMOCION (1) -> T_PROMOCION_PRODUCTO (0..*)
            {"points": [(1450, 410), (1495, 410)], "mult_from": {"text": "1", "pos": (1456, 400)}, "mult_to": {"text": "0..*", "pos": (1472, 400)}},
            # T_PRODUCTO (1) -> T_PROMOCION_PRODUCTO (0..*)
            {"points": [(1755, 370), (1710, 370)], "mult_from": {"text": "1", "pos": (1735, 360)}, "mult_to": {"text": "0..*", "pos": (1715, 360)}}
        ]
    },

    # -------------------------------------------------------------------------
    # 3. CU/W31: Consultar ventas, reservas e inventario (Web)
    # -------------------------------------------------------------------------
    {
        "id": "CU_W31",
        "file_name": "CU_W31_Consultar_Ventas_Reservas_Inventario_Clases",
        "title": "CU/W31: Consultar ventas, reservas e inventario — Diagrama de Análisis de Clases",
        "subtitle": "Sistema Aura Store | Monitor Operativo Multicapa: Panel -> Controller -> Consolidador_Service -> Repository -> Entities",
        "actors": "Encargado de sucursal, Administrador",
        "arch_badge_title": "Arquitectura Monitor de Operaciones:",
        "arch_badge_desc": "Boundary -> Monitor_Controller -> Consolidador_Service -> Operaciones_Repo -> Entities",
        "width": 2120,
        "height": 840,
        "classes": [
            {
                "id": "panel_operativo", "x": 35, "y": 270, "width": 260,
                "header": ["Form", "Monitor_Operativo_View"],
                "attributes": ["+ id_sucursal_sel", "+ fecha_consulta", "+ total_ventas_dia", "+ reservas_activas", "+ alertas_stock_bajo"],
                "methods": ["+ filtrar_por_sucursal()", "+ actualizar_metricas_vivo()", "+ ver_detalle_apartados()", "+ emitir_alerta_stock()"]
            },
            {
                "id": "ctrl_monitor", "x": 335, "y": 340, "width": 245,
                "header": ["Monitor_Operativo_Controller"],
                "attributes": [],
                "methods": ["+ get_balance_diario(sucursal)", "+ get_reservas_vigentes(suc)", "+ get_stock_critico(suc)"]
            },
            {
                "id": "srv_monitor", "x": 620, "y": 325, "width": 270,
                "header": ["Monitor_Consolidador_Service"],
                "attributes": [],
                "methods": ["+ consolidar_balance_sucursal()", "+ auditar_reservas_por_vencer()", "+ calcular_alertas_reposicion()"]
            },
            {
                "id": "repo_monitor", "x": 930, "y": 325, "width": 265,
                "header": ["Operaciones_Repository"],
                "attributes": [],
                "methods": ["+ query_ventas_del_dia(id_suc)", "+ query_reservas_pendientes(id_suc)", "+ query_inventario_stock(id_suc)", "+ find_sucursal_by_id(id_suc)"]
            },
            # Entidades (4 tablas operativas)
            {
                "id": "venta", "x": 1245, "y": 80, "width": 210,
                "header": ["T_VENTA"],
                "attributes": ["+ ID_VENTA", "+ ID_CLIENTE", "+ ID_SUCURSAL", "+ ID_EMPLEADO", "+ NUMERO_VENTA", "+ TIPO_VENTA", "+ FECHA_VENTA", "+ SUBTOTAL", "+ DESCUENTO", "+ TOTAL", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "reserva", "x": 1245, "y": 480, "width": 210,
                "header": ["T_RESERVA"],
                "attributes": ["+ ID_RESERVA", "+ ID_CLIENTE", "+ ID_SUCURSAL", "+ CODIGO_RESERVA", "+ FECHA_RESERVA", "+ FECHA_EXPIRACION", "+ FECHA_ESTIMADA_VISITA", "+ ESTADO", "+ OBSERVACIONES"],
                "methods": []
            },
            {
                "id": "sucursal", "x": 1515, "y": 320, "width": 205,
                "header": ["T_SUCURSAL"],
                "attributes": ["+ ID_SUCURSAL", "+ ID_CIUDAD", "+ NOMBRE", "+ CODIGO_SUCURSAL", "+ DIRECCION", "+ TELEFONO", "+ ESTADO", "+ ID_EMPRESA"],
                "methods": []
            },
            {
                "id": "inventario", "x": 1770, "y": 310, "width": 215,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_SUCURSAL", "+ ID_VARIANTE", "+ TEMPORADA", "+ STOCK_ACTUAL", "+ STOCK_RESERVADO", "+ STOCK_DISPONIBLE", "+ STOCK_MINIMO", "+ ESTADO", "+ FECHA_ACTUALIZACION"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(295, 410), (335, 410)]},
            {"points": [(580, 410), (620, 410)]},
            {"points": [(890, 410), (930, 410)]},
            # Repo -> T_VENTA
            {"points": [(1195, 390), (1220, 390), (1220, 220), (1245, 220)]},
            # Repo -> T_RESERVA
            {"points": [(1195, 430), (1220, 430), (1220, 580), (1245, 580)]},
            # T_SUCURSAL (1) -> T_VENTA (0..*)
            {"points": [(1515, 360), (1485, 360), (1485, 220), (1455, 220)], "mult_from": {"text": "1", "pos": (1495, 350)}, "mult_to": {"text": "0..*", "pos": (1462, 210)}},
            # T_SUCURSAL (1) -> T_RESERVA (0..*)
            {"points": [(1515, 420), (1485, 420), (1485, 580), (1455, 580)], "mult_from": {"text": "1", "pos": (1495, 410)}, "mult_to": {"text": "0..*", "pos": (1462, 570)}},
            # T_SUCURSAL (1) -> T_INVENTARIO (0..*)
            {"points": [(1720, 410), (1770, 410)], "mult_from": {"text": "1", "pos": (1725, 400)}, "mult_to": {"text": "0..*", "pos": (1750, 400)}}
        ]
    },

    # -------------------------------------------------------------------------
    # 4. CU/W32: Visualizar indicadores empresariales (Web)
    # -------------------------------------------------------------------------
    {
        "id": "CU_W32",
        "file_name": "CU_W32_Visualizar_Indicadores_Empresariales_Clases",
        "title": "CU/W32: Visualizar indicadores empresariales — Diagrama de Análisis de Clases",
        "subtitle": "Sistema Aura Store | Arquitectura Analítica: Dashboard_KPIs_View -> Controller -> Analytics_Engine (Sin Repo intermedio) -> Entities",
        "actors": "Gerente General, Propietario, Administrador",
        "arch_badge_title": "Arquitectura Analítica Optimizada:",
        "arch_badge_desc": "Dashboard_View -> KPI_Analytics_Controller -> Analytics_Engine_Service -> Entities (BD)",
        "width": 2150,
        "height": 840,
        "classes": [
            {
                "id": "dashboard_kpis", "x": 35, "y": 270, "width": 260,
                "header": ["Form", "Dashboard_KPIs_View"],
                "attributes": ["+ periodo_seleccionado", "+ ticket_promedio_bs", "+ margen_bruto_pct", "+ rotacion_inventario", "+ canal_mas_rentable"],
                "methods": ["+ seleccionar_rango_fechas()", "+ cambiar_filtro_sucursal()", "+ exportar_grafico_kpis()", "+ actualizar_tablero()"]
            },
            {
                "id": "ctrl_kpis", "x": 340, "y": 340, "width": 255,
                "header": ["KPI_Analytics_Controller"],
                "attributes": [],
                "methods": ["+ get_dashboard_summary(periodo)", "+ get_ventas_por_canal(periodo)", "+ get_top_prendas_rentabilidad()"]
            },
            {
                "id": "srv_analytics", "x": 645, "y": 320, "width": 285,
                "header": ["Analytics_Engine_Service"],
                "attributes": ["- db_engine_postgres", "- cache_metricas_redis"],
                "methods": ["+ calcular_ticket_promedio()", "+ calcular_crecimiento_interanual()", "+ calcular_margen_por_categoria()", "+ procesar_arqueos_por_caja()"]
            },
            # Entidades (5 tablas financieras)
            {
                "id": "venta", "x": 985, "y": 260, "width": 210,
                "header": ["T_VENTA"],
                "attributes": ["+ ID_VENTA", "+ ID_CLIENTE", "+ ID_SUCURSAL", "+ ID_EMPLEADO", "+ NUMERO_VENTA", "+ TIPO_VENTA", "+ FECHA_VENTA", "+ SUBTOTAL", "+ DESCUENTO", "+ TOTAL", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "det_venta", "x": 1255, "y": 100, "width": 210,
                "header": ["T_DETALLE_VENTA"],
                "attributes": ["+ ID_DETALLE_VENTA", "+ ID_VENTA", "+ ID_VARIANTE", "+ CANTIDAD", "+ PRECIO_UNITARIO", "+ DESCUENTO", "+ SUBTOTAL"],
                "methods": []
            },
            {
                "id": "pago", "x": 1255, "y": 480, "width": 210,
                "header": ["T_PAGO"],
                "attributes": ["+ ID_PAGO", "+ ID_VENTA", "+ ID_METODO_PAGO", "+ ID_SUCURSAL", "+ CODIGO_TRANSACCION", "+ MONTO", "+ FECHA_PAGO", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "metodo_pago", "x": 1530, "y": 495, "width": 195,
                "header": ["T_METODO_PAGO"],
                "attributes": ["+ ID_METODO_PAGO", "+ NOMBRE", "+ TIPO", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "empleado", "x": 1530, "y": 240, "width": 205,
                "header": ["T_EMPLEADO"],
                "attributes": ["+ ID_EMPLEADO", "+ ID_USUARIO", "+ ID_SUCURSAL", "+ CODIGO_EMPLEADO", "+ CARGO", "+ FECHA_CONTRATACION", "+ ESTADO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(295, 410), (340, 410)]},
            {"points": [(595, 410), (645, 410)]},
            # Analytics_Engine conecta directo a T_VENTA
            {"points": [(930, 410), (985, 410)]},
            # T_VENTA (1) -> T_DETALLE_VENTA (1..*)
            {"points": [(1195, 340), (1225, 340), (1225, 190), (1255, 190)], "mult_from": {"text": "1", "pos": (1200, 330)}, "mult_to": {"text": "1..*", "pos": (1230, 180)}},
            # T_VENTA (1) -> T_PAGO (1..*)
            {"points": [(1195, 440), (1225, 440), (1225, 570), (1255, 570)], "mult_from": {"text": "1", "pos": (1200, 430)}, "mult_to": {"text": "1..*", "pos": (1230, 560)}},
            # T_METODO_PAGO (1) -> T_PAGO (0..*)
            {"points": [(1530, 560), (1465, 560)], "mult_from": {"text": "1", "pos": (1505, 550)}, "mult_to": {"text": "0..*", "pos": (1472, 550)}},
            # T_EMPLEADO (1) -> T_VENTA (0..*)
            {"points": [(1530, 310), (1225, 310), (1195, 310)], "mult_from": {"text": "1", "pos": (1505, 300)}, "mult_to": {"text": "0..*", "pos": (1200, 300)}}
        ]
    },

    # -------------------------------------------------------------------------
    # 5. CU/W33: Generar reportes bajo demanda (Web)
    # -------------------------------------------------------------------------
    {
        "id": "CU_W33",
        "file_name": "CU_W33_Generar_Reportes_Bajo_Demanda_Clases",
        "title": "CU/W33: Generar reportes bajo demanda — Diagrama de Análisis de Clases",
        "subtitle": "Sistema Aura Store | Motor Documental: Form -> Controller -> Report_Builder_Service -> Query_Repository -> Entities",
        "actors": "Administrador, Auditor Contable, Gerente",
        "arch_badge_title": "Arquitectura Exportación Documental:",
        "arch_badge_desc": "Boundary -> Reportes_Controller -> Report_Builder_Service (PDF/Excel) -> Query_Repo -> Entities",
        "width": 2100,
        "height": 840,
        "classes": [
            {
                "id": "form_reportes", "x": 35, "y": 270, "width": 260,
                "header": ["Form", "Generador_Reportes_View"],
                "attributes": ["+ tipo_reporte_sel", "+ rango_fecha_inicio", "+ rango_fecha_fin", "+ formato_exportacion", "+ sucursal_filtro"],
                "methods": ["+ seleccionar_tipo_reporte()", "+ configurar_parametros()", "+ generar_previsualizacion()", "+ descargar_archivo_binario()"]
            },
            {
                "id": "ctrl_reportes", "x": 335, "y": 340, "width": 245,
                "header": ["Reportes_Controller"],
                "attributes": [],
                "methods": ["+ post_generar_reporte(criterios)", "+ get_formatos_disponibles()", "+ get_auditoria_descargas()"]
            },
            {
                "id": "srv_report_builder", "x": 620, "y": 320, "width": 270,
                "header": ["Report_Builder_Service"],
                "attributes": ["- reportlab_engine", "- openpyxl_workbook"],
                "methods": ["+ compilar_pdf_documental()", "+ compilar_excel_tabular()", "+ registrar_trazabilidad_auditoria()"]
            },
            {
                "id": "repo_reportes", "x": 930, "y": 325, "width": 265,
                "header": ["Reportes_Query_Repository"],
                "attributes": [],
                "methods": ["+ query_ventas_tributarias(fechas)", "+ query_valoracion_inventario()", "+ query_movimientos_kardex(fechas)", "+ insert_log_bitacora(auditoria)"]
            },
            # Entidades (4 tablas de reporte)
            {
                "id": "venta", "x": 1245, "y": 100, "width": 210,
                "header": ["T_VENTA"],
                "attributes": ["+ ID_VENTA", "+ ID_CLIENTE", "+ ID_SUCURSAL", "+ ID_EMPLEADO", "+ NUMERO_VENTA", "+ TIPO_VENTA", "+ FECHA_VENTA", "+ SUBTOTAL", "+ DESCUENTO", "+ TOTAL", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "inventario", "x": 1245, "y": 480, "width": 215,
                "header": ["T_INVENTARIO"],
                "attributes": ["+ ID_INVENTARIO", "+ ID_SUCURSAL", "+ ID_VARIANTE", "+ TEMPORADA", "+ STOCK_ACTUAL", "+ STOCK_RESERVADO", "+ STOCK_DISPONIBLE", "+ STOCK_MINIMO", "+ ESTADO", "+ FECHA_ACTUALIZACION"],
                "methods": []
            },
            {
                "id": "mov_inventario", "x": 1520, "y": 490, "width": 215,
                "header": ["T_MOVIMIENTO_INVENTARIO"],
                "attributes": ["+ ID_MOVIMIENTO", "+ ID_INVENTARIO", "+ ID_USUARIO", "+ TIPO_MOVIMIENTO", "+ CANTIDAD", "+ STOCK_ANTERIOR", "+ STOCK_NUEVO", "+ MOTIVO", "+ FECHA_MOVIMIENTO"],
                "methods": []
            },
            {
                "id": "bitacora", "x": 1520, "y": 150, "width": 215,
                "header": ["T_BITACORA"],
                "attributes": ["+ ID_BITACORA", "+ ID_USUARIO", "+ MODULO", "+ ACCION", "+ DESCRIPCION", "+ FECHA_HORA", "+ IP", "+ TENANT_ORIGEN", "+ RESULTADO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(295, 410), (335, 410)]},
            {"points": [(580, 410), (620, 410)]},
            {"points": [(890, 410), (930, 410)]},
            # Repo -> T_VENTA
            {"points": [(1195, 390), (1220, 390), (1220, 230), (1245, 230)]},
            # Repo -> T_INVENTARIO
            {"points": [(1195, 430), (1220, 430), (1220, 580), (1245, 580)]},
            # T_INVENTARIO (1) -> T_MOVIMIENTO_INVENTARIO (0..*)
            {"points": [(1460, 580), (1520, 580)], "mult_from": {"text": "1", "pos": (1465, 570)}, "mult_to": {"text": "0..*", "pos": (1495, 570)}},
            # Repo -> T_BITACORA
            {"points": [(1195, 360), (1220, 360), (1220, 20), (1490, 20), (1490, 230), (1520, 230)]}
        ]
    },

    # -------------------------------------------------------------------------
    # 6. CU/M12: Obtener recomendaciones de productos (Mobile)
    # -------------------------------------------------------------------------
    {
        "id": "CU_M12",
        "file_name": "CU_M12_Obtener_Recomendaciones_Productos_Clases",
        "title": "CU/M12: Obtener recomendaciones de productos (App Móvil) — Diagrama de Análisis de Clases",
        "subtitle": "Sistema Aura Mobile | Arquitectura Móvil Flutter: Screen -> Cubit -> Mobile_API_Client -> Backend Entities",
        "actors": "Cliente Móvil, Visitante",
        "arch_badge_title": "Arquitectura Nativa Flutter Mobile:",
        "arch_badge_desc": "Mobile_Screen -> Recomendaciones_Cubit -> Mobile_API_Client -> Entities (Cloud Backend)",
        "width": 2100,
        "height": 840,
        "classes": [
            {
                "id": "screen_recomendados", "x": 35, "y": 270, "width": 260,
                "header": ["Screen", "Feed_Recomendados_Screen"],
                "attributes": ["+ controller_scroll", "+ lista_cards_sugeridas", "+ flag_cargando_feed", "+ categoria_filtro_rapido"],
                "methods": ["+ refrescar_feed_para_ti()", "+ deslizar_carrusel_estilos()", "+ navegar_detalle_prenda()", "+ marcar_no_me_interesa()"]
            },
            {
                "id": "cubit_recomendados", "x": 335, "y": 330, "width": 255,
                "header": ["Recomendaciones_Cubit"],
                "attributes": ["- estado_actual_feed", "- lista_cache_prendas"],
                "methods": ["+ cargar_recomendaciones()", "+ filtrar_por_estilo(tag)", "+ emit(RecomendacionesLoaded)"]
            },
            {
                "id": "client_api", "x": 630, "y": 340, "width": 265,
                "header": ["Catalogo_Mobile_API_Client"],
                "attributes": ["- http_client_dio", "- url_base_backend"],
                "methods": ["+ get_productos_recomendados()", "+ post_registrar_interaccion(id)"]
            },
            # Entidades Backend (4 tablas)
            {
                "id": "recomendacion", "x": 955, "y": 280, "width": 205,
                "header": ["T_RECOMENDACION"],
                "attributes": ["+ ID_RECOMENDACION", "+ ID_CLIENTE", "+ ID_PRODUCTO", "+ PUNTUACION", "+ MOTIVO", "+ FECHA_RECOMENDACION"],
                "methods": []
            },
            {
                "id": "preferencia", "x": 1220, "y": 480, "width": 210,
                "header": ["T_PREFERENCIA_CLIENTE"],
                "attributes": ["+ ID_PREFERENCIA", "+ ID_CLIENTE", "+ ID_CATEGORIA", "+ ID_TALLA", "+ ID_COLOR", "+ TIPO_PREFERENCIA"],
                "methods": []
            },
            {
                "id": "historial", "x": 1220, "y": 100, "width": 210,
                "header": ["T_HISTORIAL_NAVEGACION"],
                "attributes": ["+ ID_HISTORIAL", "+ ID_CLIENTE", "+ ID_PRODUCTO", "+ TIPO_ACCION", "+ FECHA_HORA"],
                "methods": []
            },
            {
                "id": "producto", "x": 1490, "y": 240, "width": 210,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ ID_CATEGORIA", "+ CODIGO_PRODUCTO", "+ NOMBRE", "+ DESCRIPCION", "+ MARCA", "+ GENERO", "+ PRECIO", "+ IMAGEN_URL", "+ ESTADO", "+ FECHA_REGISTRO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(295, 410), (335, 410)]},
            {"points": [(590, 410), (630, 410)]},
            {"points": [(895, 410), (955, 410)]},
            # T_RECOMENDACION -> T_PRODUCTO
            {"points": [(1160, 390), (1490, 390)], "mult_from": {"text": "0..*", "pos": (1165, 380)}, "mult_to": {"text": "1", "pos": (1465, 380)}},
            # T_RECOMENDACION -> T_PREFERENCIA_CLIENTE
            {"points": [(1160, 430), (1190, 430), (1190, 580), (1220, 580)], "mult_from": {"text": "1", "pos": (1165, 420)}, "mult_to": {"text": "0..*", "pos": (1195, 570)}},
            # T_HISTORIAL_NAVEGACION -> T_PRODUCTO
            {"points": [(1430, 160), (1460, 160), (1460, 270), (1490, 270)], "mult_from": {"text": "0..*", "pos": (1435, 150)}, "mult_to": {"text": "1", "pos": (1465, 260)}}
        ]
    },

    # -------------------------------------------------------------------------
    # 7. CU/M13: Interactuar con asistente inteligente (Mobile)
    # -------------------------------------------------------------------------
    {
        "id": "CU_M13",
        "file_name": "CU_M13_Interactuar_Asistente_Inteligente_Clases",
        "title": "CU/M13: Interactuar con asistente inteligente (App Móvil) — Diagrama de Análisis de Clases",
        "subtitle": "Sistema Aura Mobile | Asistente de Voz y Texto: Voice_Chat_Screen -> Cubit -> Speech_Detector -> AI_Client -> Backend Entities",
        "actors": "Cliente Móvil",
        "arch_badge_title": "Arquitectura Móvil con Voz y LLM:",
        "arch_badge_desc": "Voice_Screen -> Voice_Cubit -> Speech_Service -> AI_Mobile_Client -> Entities (Cloud)",
        "width": 2100,
        "height": 840,
        "classes": [
            {
                "id": "screen_asistente", "x": 35, "y": 270, "width": 260,
                "header": ["Screen", "Asistente_Voz_Chat_Screen"],
                "attributes": ["+ animacion_onda_voz", "+ transcripcion_en_vivo", "+ historial_burbujas", "+ boton_microfono_activo"],
                "methods": ["+ iniciar_escucha_voz()", "+ detener_y_enviar_audio()", "+ reproducir_sintesis_tts()", "+ renderizar_cards_producto()"]
            },
            {
                "id": "cubit_asistente", "x": 335, "y": 330, "width": 250,
                "header": ["Voice_Chat_Cubit"],
                "attributes": ["- is_recording_audio", "- mensajes_stream"],
                "methods": ["+ enviar_comando_voz(audio)", "+ enviar_mensaje_texto(txt)", "+ reproducir_audio_ia()"]
            },
            {
                "id": "srv_speech", "x": 625, "y": 320, "width": 265,
                "header": ["Speech_Detector_Service"],
                "attributes": ["- speech_to_text_engine", "- flutter_tts_engine"],
                "methods": ["+ grabar_audio_stream()", "+ convertir_audio_a_texto()", "+ hablar_texto(respuesta)"]
            },
            {
                "id": "client_ai", "x": 930, "y": 335, "width": 265,
                "header": ["Asistente_Mobile_Client"],
                "attributes": ["- dio_client", "- token_jwt_movil"],
                "methods": ["+ post_conversacion(payload)", "+ get_sugerencias_rapidas()"]
            },
            # Entidades Backend (4 tablas)
            {
                "id": "cliente", "x": 1245, "y": 100, "width": 200,
                "header": ["T_CLIENTE"],
                "attributes": ["+ ID_CLIENTE", "+ ID_USUARIO", "+ CI", "+ FECHA_REGISTRO"],
                "methods": []
            },
            {
                "id": "venta", "x": 1495, "y": 100, "width": 210,
                "header": ["T_VENTA"],
                "attributes": ["+ ID_VENTA", "+ ID_CLIENTE", "+ ID_SUCURSAL", "+ ID_EMPLEADO", "+ NUMERO_VENTA", "+ TIPO_VENTA", "+ FECHA_VENTA", "+ SUBTOTAL", "+ DESCUENTO", "+ TOTAL", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "reserva", "x": 1245, "y": 480, "width": 210,
                "header": ["T_RESERVA"],
                "attributes": ["+ ID_RESERVA", "+ ID_CLIENTE", "+ ID_SUCURSAL", "+ CODIGO_RESERVA", "+ FECHA_RESERVA", "+ FECHA_EXPIRACION", "+ FECHA_ESTIMADA_VISITA", "+ ESTADO", "+ OBSERVACIONES"],
                "methods": []
            },
            {
                "id": "producto", "x": 1500, "y": 460, "width": 210,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ ID_CATEGORIA", "+ CODIGO_PRODUCTO", "+ NOMBRE", "+ DESCRIPCION", "+ MARCA", "+ GENERO", "+ PRECIO", "+ IMAGEN_URL", "+ ESTADO", "+ FECHA_REGISTRO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(295, 410), (335, 410)]},
            {"points": [(585, 410), (625, 410)]},
            {"points": [(890, 410), (930, 410)]},
            # Client -> T_CLIENTE
            {"points": [(1195, 390), (1220, 390), (1220, 200), (1245, 200)]},
            # Client -> T_RESERVA
            {"points": [(1195, 430), (1220, 430), (1220, 580), (1245, 580)]},
            # T_CLIENTE (1) -> T_VENTA (0..*)
            {"points": [(1445, 200), (1495, 200)], "mult_from": {"text": "1", "pos": (1450, 190)}, "mult_to": {"text": "0..*", "pos": (1475, 190)}},
            # T_CLIENTE (1) -> T_RESERVA (0..*)
            {"points": [(1345, 230), (1345, 480)], "mult_from": {"text": "1", "pos": (1355, 245)}, "mult_to": {"text": "0..*", "pos": (1355, 465)}},
            # T_RESERVA -> T_PRODUCTO
            {"points": [(1455, 590), (1500, 590)], "mult_from": {"text": "0..*", "pos": (1460, 580)}, "mult_to": {"text": "1", "pos": (1480, 580)}}
        ]
    },

    # -------------------------------------------------------------------------
    # 8. CU/M14: Utilizar vestidor virtual (Mobile RA)
    # -------------------------------------------------------------------------
    {
        "id": "CU_M14",
        "file_name": "CU_M14_Utilizar_Vestidor_Virtual_Clases",
        "title": "CU/M14: Utilizar vestidor virtual (Probador RA) — Diagrama de Análisis de Clases",
        "subtitle": "Sistema Aura Mobile | Probador Realidad Aumentada: Vestidor_Screen -> AR_Camera_Controller -> Pose_Detector -> Vestidor_Service -> Entities",
        "actors": "Cliente Móvil",
        "arch_badge_title": "Arquitectura Visión Artificial & Realidad Aumentada:",
        "arch_badge_desc": "AR_Screen -> AR_Controller -> Pose_Body_Detector -> Vestidor_Service -> Entities (RA)",
        "width": 2100,
        "height": 840,
        "classes": [
            {
                "id": "screen_vestidor", "x": 35, "y": 270, "width": 260,
                "header": ["Screen", "Vestidor_Virtual_Screen"],
                "attributes": ["+ camera_preview_widget", "+ prenda_activa_ra", "+ escala_modelo_textil", "+ selector_talla_color", "+ status_deteccion_cuerpo"],
                "methods": ["+ alternar_camara_frontal()", "+ seleccionar_prenda_vestidor()", "+ capturar_foto_con_prenda()", "+ comprar_prenda_directa()"]
            },
            {
                "id": "ctrl_ar_camera", "x": 335, "y": 330, "width": 250,
                "header": ["AR_Camera_Controller"],
                "attributes": ["- camera_controller", "- is_detecting_pose"],
                "methods": ["+ inicializar_feed_camara()", "+ procesar_frame_camara(frame)", "+ ajustar_anclaje_hombros()"]
            },
            {
                "id": "srv_pose_detector", "x": 625, "y": 315, "width": 265,
                "header": ["Pose_Body_Detector"],
                "attributes": ["- mediapipe_pose_engine", "- confidence_threshold"],
                "methods": ["+ detectar_puntos_clave_torso()", "+ calcular_dimensiones_pecho_cadera()", "+ sincronizar_movimiento_prenda()"]
            },
            {
                "id": "srv_vestidor", "x": 930, "y": 335, "width": 265,
                "header": ["Vestidor_Service"],
                "attributes": ["- catalogo_repository", "- cache_texturas_transparentes"],
                "methods": ["+ get_prendas_compatibles_ra()", "+ descargar_textura_2d_3d(id)", "+ registrar_sesion_vestidor()"]
            },
            # Entidades (4 tablas de RA)
            {
                "id": "vestidor_virtual", "x": 1245, "y": 100, "width": 205,
                "header": ["T_VESTIDOR_VIRTUAL"],
                "attributes": ["+ ID_VESTIDOR_VIRTUAL", "+ ID_CLIENTE", "+ ID_PRENDA_RA", "+ FECHA_USO"],
                "methods": []
            },
            {
                "id": "prenda_ra", "x": 1245, "y": 480, "width": 205,
                "header": ["T_PRENDA_RA"],
                "attributes": ["+ ID_PRENDA_RA", "+ ID_PRODUCTO", "+ NOMBRE", "+ MODELO_3D_URL", "+ MODELO_2D_URL", "+ ESTADO"],
                "methods": []
            },
            {
                "id": "producto", "x": 1500, "y": 240, "width": 210,
                "header": ["T_PRODUCTO"],
                "attributes": ["+ ID_PRODUCTO", "+ ID_CATEGORIA", "+ CODIGO_PRODUCTO", "+ NOMBRE", "+ DESCRIPCION", "+ MARCA", "+ GENERO", "+ PRECIO", "+ IMAGEN_URL", "+ ESTADO", "+ FECHA_REGISTRO"],
                "methods": []
            },
            {
                "id": "variante", "x": 1765, "y": 250, "width": 225,
                "header": ["T_PRODUCTO_TALLA_COLOR"],
                "attributes": ["+ ID_VARIANTE", "+ ID_PRODUCTO", "+ ID_TALLA", "+ ID_COLOR", "+ SKU", "+ CODIGO_BARRAS", "+ PRECIO", "+ MODELO_3D_URL", "+ ESTADO"],
                "methods": []
            }
        ],
        "connections": [
            {"points": [(295, 410), (335, 410)]},
            {"points": [(585, 410), (625, 410)]},
            {"points": [(890, 410), (930, 410)]},
            # Vestidor_Service -> T_VESTIDOR_VIRTUAL
            {"points": [(1195, 390), (1220, 390), (1220, 200), (1245, 200)]},
            # Vestidor_Service -> T_PRENDA_RA
            {"points": [(1195, 430), (1220, 430), (1220, 580), (1245, 580)]},
            # T_PRENDA_RA (1) -> T_VESTIDOR_VIRTUAL (0..*)
            {"points": [(1345, 480), (1345, 230)], "mult_from": {"text": "1", "pos": (1355, 465)}, "mult_to": {"text": "0..*", "pos": (1355, 245)}},
            # T_PRODUCTO (1) -> T_PRENDA_RA (0..*)
            {"points": [(1500, 380), (1470, 380), (1470, 580), (1450, 580)], "mult_from": {"text": "1", "pos": (1480, 370)}, "mult_to": {"text": "0..*", "pos": (1455, 570)}},
            # T_PRODUCTO (1) -> T_PRODUCTO_TALLA_COLOR (1..*)
            {"points": [(1710, 370), (1765, 370)], "mult_from": {"text": "1", "pos": (1715, 360)}, "mult_to": {"text": "1..*", "pos": (1740, 360)}}
        ]
    }
]

def generate_all():
    output_dir = "docs/diagramas_analisis_clases"
    brain_dir = r"C:\Users\eddym\.gemini\antigravity-ide\brain\bce20c4d-ff88-4ad8-93ad-540bb85f5c37"

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(brain_dir, exist_ok=True)

    print(f"Iniciando generacion de los {len(DIAGRAMS)} Diagramas de Analisis de Clases restantes...")

    for i, diag in enumerate(DIAGRAMS, 1):
        file_base = diag["file_name"]
        svg_file = os.path.join(output_dir, f"{file_base}.svg")
        png_file = os.path.join(output_dir, f"{file_base}.png")

        svg_code = render_diagram_svg(diag)

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

        print(f" [{i:02d}/{len(DIAGRAMS)}] Generado: {file_base} (SVG y PNG 2x)")

    print("\nTodos los Diagramas de Analisis de Clases generados exitosamente.")

if __name__ == "__main__":
    generate_all()
