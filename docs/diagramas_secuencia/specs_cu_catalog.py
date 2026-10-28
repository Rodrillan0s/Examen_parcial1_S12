#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Especificaciones de Diagramas de Secuencia UML 2.5+ (ICONIX):
- CU15: Gestionar empresas SaaS (P1 - Refactorización)
- CU16: Gestionar sucursales y ciudades (P1)
- CU17: Gestionar productos (P1)
- CU18: Gestionar categorías (P1)
- CU19: Gestionar tallas y colores (P1)
- CU20: Gestionar temporadas y colecciones (P1)
- CU21: Gestionar proveedores (P1)
"""

from specs_cu_auth import get_common_sequence_styles

# ==============================================================================
# CU15: Gestionar empresas SaaS (P1 — Refactorización)
# ==============================================================================
def build_cu15_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu15", "value": "<b>sd</b> CU15 — Gestionar empresas SaaS (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu15_ll_superadmin", "value": "<b>Superadmin</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu15_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_EmpresasSaaS</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu15_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:saas_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu15_ll_services", "value": "&laquo;control&raquo;<br/><b>:saas_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu15_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:tenant_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu15_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu15_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu15_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu15_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu15_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu15_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 370, "w": 12, "h": 30},
        {"id": "cu15_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 480, "w": 12, "h": 30},
        {"id": "cu15_act_repos_3", "value": "", "style": s["activation"], "x": 1154, "y": 660, "w": 12, "h": 30},
        {"id": "cu15_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 780, "w": 12, "h": 30},

        # alt por tipo de operación
        {"id": "cu15_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 435, "w": 1430, "h": 580},
        {"id": "cu15_lbl_alt1", "value": "[nit_unico == true &amp;&amp; datos_validos] (Curso Básico: Registro o Edición Exitosa)", "style": s["guard_label"], "x": 115, "y": 440, "w": 520, "h": 20},

        # opt inicialización de tenant
        {"id": "cu15_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 550, "w": 570, "h": 75},
        {"id": "cu15_lbl_opt", "value": "[es_nueva_empresa == true] (Configurar Esquema Tenant)", "style": s["guard_label"], "x": 720, "y": 555, "w": 350, "h": 20},

        {"id": "cu15_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu15_lbl_alt2", "value": "[else: nit_duplicado || intento_borrado_fisico] (Curso Alterno: Rechazo 409 / Baja Lógica)", "style": s["guard_label"], "x": 55, "y": 898, "w": 620, "h": 20}
    ]

    edges = [
        {"id": "e_cu15_01", "source": "cu15_ll_superadmin", "target": "cu15_ll_iu", "value": "1: ingresar_datos_empresa(nit, razon_social, direccion)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_02", "source": "cu15_ll_iu", "target": "cu15_ll_routes", "value": "2: POST /api/empresas(dto_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_03", "source": "cu15_ll_routes", "target": "cu15_ll_services", "value": "3: guardar_empresa_saas(dto_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_04", "source": "cu15_ll_services", "target": "cu15_ll_services", "value": "4: validar_alcance_plataforma(token)", "style": s["self_call"], "exitX": 0.5, "exitY": round((310 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((335 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_05", "source": "cu15_ll_services", "target": "cu15_ll_repos", "value": "5: verificar_unicidad_nit(nit)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((370 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((370 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_06", "source": "cu15_ll_repos", "target": "cu15_ll_services", "value": "6: return bool_nit_disponible", "style": s["return"], "exitX": 0.5, "exitY": round((400 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((400 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu15_07", "source": "cu15_ll_services", "target": "cu15_ll_repos", "value": "7: guardar_empresa_tenant(datos, activo=true)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((480 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_08", "source": "cu15_ll_repos", "target": "cu15_ll_services", "value": "8: return id_empresa_creada", "style": s["return"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},

        # opt
        {"id": "e_cu15_09", "source": "cu15_ll_services", "target": "cu15_ll_repos", "value": "9: inicializar_configuracion_tenant(id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((575 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((575 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_10", "source": "cu15_ll_repos", "target": "cu15_ll_services", "value": "10: return bool_init_ok", "style": s["return"], "exitX": 0.5, "exitY": round((600 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((600 - y_start_box) / h_box, 5)},

        {"id": "e_cu15_11", "source": "cu15_ll_services", "target": "cu15_ll_repos", "value": "11: preservar_integridad_sucursales(id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((660 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((660 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_12", "source": "cu15_ll_repos", "target": "cu15_ll_services", "value": "12: return bool_integridad_ok", "style": s["return"], "exitX": 0.5, "exitY": round((690 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((690 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_13", "source": "cu15_ll_services", "target": "cu15_ll_bitacora", "value": "13: registrar_bitacora(GESTION_EMPRESA_SAAS, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((780 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((780 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_14", "source": "cu15_ll_services", "target": "cu15_ll_routes", "value": "14: return empresa_guardada(id_empresa, nit)", "style": s["return"], "exitX": 0.5, "exitY": round((810 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((810 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_15", "source": "cu15_ll_routes", "target": "cu15_ll_iu", "value": "15: HTTP 201 Created (empresa_persistida)", "style": s["return"], "exitX": 0.5, "exitY": round((835 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((835 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_16", "source": "cu15_ll_iu", "target": "cu15_ll_superadmin", "value": "16: actualizar_catalogo_empresas()", "style": s["return"], "exitX": 0.5, "exitY": round((860 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((860 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu15_17", "source": "cu15_ll_services", "target": "cu15_ll_routes", "value": "17: throw ConflictException(\"NIT_DUPLICADO\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_18", "source": "cu15_ll_routes", "target": "cu15_ll_iu", "value": "18: HTTP 409 Conflict (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu15_19", "source": "cu15_ll_iu", "target": "cu15_ll_superadmin", "value": "19: mostrar_error_nit_duplicado()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu15_sec", "name": "CU15 - Gestionar empresas SaaS (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU16: Gestionar sucursales y ciudades
# ==============================================================================
def build_cu16_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu16", "value": "<b>sd</b> CU16 — Gestionar sucursales y ciudades (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu16_ll_admin", "value": "<b>Administrador</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu16_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Sucursales</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu16_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:sucursales_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu16_ll_services", "value": "&laquo;control&raquo;<br/><b>:sucursales_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu16_ll_saas", "value": "&laquo;control&raquo;<br/><b>:saas_services</b>", "style": s["lifeline_box"], "x": 880, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu16_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:sucursal_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu16_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu16_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu16_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu16_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu16_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu16_act_saas_1", "value": "", "style": s["activation"], "x": 936, "y": 315, "w": 12, "h": 30},
        {"id": "cu16_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 380, "w": 12, "h": 30},
        {"id": "cu16_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 510, "w": 12, "h": 30},
        {"id": "cu16_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 780, "w": 12, "h": 30},

        # alt validación límite de sucursales plan
        {"id": "cu16_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 445, "w": 1430, "h": 570},
        {"id": "cu16_lbl_alt1", "value": "[sucursales_activas < max_sucursales_plan &amp;&amp; codigo_unico] (Curso Básico: Sucursal Creada)", "style": s["guard_label"], "x": 115, "y": 450, "w": 620, "h": 20},

        # opt cambio de estado operativo
        {"id": "cu16_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 620, "w": 570, "h": 75},
        {"id": "cu16_lbl_opt", "value": "[desactivar_sucursal == true] (activo = false)", "style": s["guard_label"], "x": 720, "y": 625, "w": 320, "h": 20},

        {"id": "cu16_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu16_lbl_alt2", "value": "[else: sucursales_activas >= max_sucursales_plan || codigo_duplicado] (Curso Alterno: Error 409)", "style": s["guard_label"], "x": 55, "y": 898, "w": 650, "h": 20}
    ]

    edges = [
        {"id": "e_cu16_01", "source": "cu16_ll_admin", "target": "cu16_ll_iu", "value": "1: ingresar_datos_sucursal(codigo, nombre, ciudad_id)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_02", "source": "cu16_ll_iu", "target": "cu16_ll_routes", "value": "2: POST /api/sucursales(dto_sucursal)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_03", "source": "cu16_ll_routes", "target": "cu16_ll_services", "value": "3: crear_sucursal(id_empresa, dto_sucursal)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_04", "source": "cu16_ll_services", "target": "cu16_ll_saas", "value": "4: consultar_limite_plan(id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((315 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((315 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_05", "source": "cu16_ll_saas", "target": "cu16_ll_services", "value": "5: return max_sucursales_plan", "style": s["return"], "exitX": 0.5, "exitY": round((345 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((345 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_06", "source": "cu16_ll_services", "target": "cu16_ll_repos", "value": "6: contar_sucursales_activas(id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((380 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((380 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_07", "source": "cu16_ll_repos", "target": "cu16_ll_services", "value": "7: return conteo_activas", "style": s["return"], "exitX": 0.5, "exitY": round((410 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((410 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu16_08", "source": "cu16_ll_services", "target": "cu16_ll_repos", "value": "8: insertar_sucursal(codigo, nombre, ciudad_id, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_09", "source": "cu16_ll_repos", "target": "cu16_ll_services", "value": "9: return id_sucursal_creada", "style": s["return"], "exitX": 0.5, "exitY": round((540 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((540 - y_start_box) / h_box, 5)},

        # opt
        {"id": "e_cu16_10", "source": "cu16_ll_services", "target": "cu16_ll_repos", "value": "10: actualizar_estado_operativo(id_sucursal, false)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((645 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((645 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_11", "source": "cu16_ll_repos", "target": "cu16_ll_services", "value": "11: return bool_estado_ok", "style": s["return"], "exitX": 0.5, "exitY": round((670 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((670 - y_start_box) / h_box, 5)},

        {"id": "e_cu16_12", "source": "cu16_ll_services", "target": "cu16_ll_bitacora", "value": "12: registrar_bitacora(GESTION_SUCURSAL, id_sucursal)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((780 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((780 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_13", "source": "cu16_ll_services", "target": "cu16_ll_routes", "value": "13: return sucursal_creada(id_sucursal, codigo)", "style": s["return"], "exitX": 0.5, "exitY": round((810 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((810 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_14", "source": "cu16_ll_routes", "target": "cu16_ll_iu", "value": "14: HTTP 201 Created (sucursal_guardada)", "style": s["return"], "exitX": 0.5, "exitY": round((835 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((835 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_15", "source": "cu16_ll_iu", "target": "cu16_ll_admin", "value": "15: actualizar_lista_sucursales()", "style": s["return"], "exitX": 0.5, "exitY": round((860 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((860 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu16_16", "source": "cu16_ll_services", "target": "cu16_ll_routes", "value": "16: throw ConflictException(\"LIMITE_SUCURSALES_PLAN_EXCEDIDO\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_17", "source": "cu16_ll_routes", "target": "cu16_ll_iu", "value": "17: HTTP 409 Conflict (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu16_18", "source": "cu16_ll_iu", "target": "cu16_ll_admin", "value": "18: mostrar_error_limite_plan_alcanzado()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu16_sec", "name": "CU16 - Gestionar sucursales y ciudades (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU17: Gestionar productos
# ==============================================================================
def build_cu17_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu17", "value": "<b>sd</b> CU17 — Gestionar productos (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu17_ll_encargado", "value": "<b>Encargado Catálogo</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu17_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Productos</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu17_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:productos_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu17_ll_services", "value": "&laquo;control&raquo;<br/><b>:productos_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu17_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:producto_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu17_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu17_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu17_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu17_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu17_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu17_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 370, "w": 12, "h": 30},
        {"id": "cu17_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 480, "w": 12, "h": 30},
        {"id": "cu17_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 780, "w": 12, "h": 30},

        # alt validación precio y SKU
        {"id": "cu17_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 435, "w": 1430, "h": 580},
        {"id": "cu17_lbl_alt1", "value": "[precio > 0 &amp;&amp; sku_unico == true] (Curso Básico: Prenda Guardada)", "style": s["guard_label"], "x": 115, "y": 440, "w": 480, "h": 20},

        # opt vinculación con temporada
        {"id": "cu17_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 550, "w": 570, "h": 75},
        {"id": "cu17_lbl_opt", "value": "[id_temporada != null] (Asociar Colección Estacional)", "style": s["guard_label"], "x": 720, "y": 555, "w": 350, "h": 20},

        {"id": "cu17_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu17_lbl_alt2", "value": "[else: precio <= 0 || sku_duplicado] (Curso Alterno: Error 422/409)", "style": s["guard_label"], "x": 55, "y": 898, "w": 520, "h": 20}
    ]

    edges = [
        {"id": "e_cu17_01", "source": "cu17_ll_encargado", "target": "cu17_ll_iu", "value": "1: ingresar_datos_producto(sku, nombre, precio, categoria_id)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_02", "source": "cu17_ll_iu", "target": "cu17_ll_routes", "value": "2: POST /api/productos(dto_producto)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_03", "source": "cu17_ll_routes", "target": "cu17_ll_services", "value": "3: guardar_producto(id_empresa, dto_producto)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_04", "source": "cu17_ll_services", "target": "cu17_ll_services", "value": "4: validar_precio_y_formato(precio, sku)", "style": s["self_call"], "exitX": 0.5, "exitY": round((310 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((335 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_05", "source": "cu17_ll_services", "target": "cu17_ll_repos", "value": "5: buscar_producto_por_sku(sku, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((370 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((370 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_06", "source": "cu17_ll_repos", "target": "cu17_ll_services", "value": "6: return producto_existente", "style": s["return"], "exitX": 0.5, "exitY": round((400 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((400 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu17_07", "source": "cu17_ll_services", "target": "cu17_ll_repos", "value": "7: insertar_producto(datos, categoria_id, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((480 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_08", "source": "cu17_ll_repos", "target": "cu17_ll_services", "value": "8: return id_producto_creado", "style": s["return"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},

        # opt
        {"id": "e_cu17_09", "source": "cu17_ll_services", "target": "cu17_ll_repos", "value": "9: vincular_temporada_producto(id_producto, id_temporada)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((575 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((575 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_10", "source": "cu17_ll_repos", "target": "cu17_ll_services", "value": "10: return bool_temporada_ok", "style": s["return"], "exitX": 0.5, "exitY": round((600 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((600 - y_start_box) / h_box, 5)},

        {"id": "e_cu17_11", "source": "cu17_ll_services", "target": "cu17_ll_bitacora", "value": "11: registrar_bitacora(GESTION_PRODUCTO, id_producto)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((780 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((780 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_12", "source": "cu17_ll_services", "target": "cu17_ll_routes", "value": "12: return producto_guardado(id_producto, sku)", "style": s["return"], "exitX": 0.5, "exitY": round((810 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((810 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_13", "source": "cu17_ll_routes", "target": "cu17_ll_iu", "value": "13: HTTP 201 Created (producto)", "style": s["return"], "exitX": 0.5, "exitY": round((835 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((835 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_14", "source": "cu17_ll_iu", "target": "cu17_ll_encargado", "value": "14: actualizar_catalogo_visible()", "style": s["return"], "exitX": 0.5, "exitY": round((860 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((860 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu17_15", "source": "cu17_ll_services", "target": "cu17_ll_routes", "value": "15: throw ConflictException(\"SKU_YA_REGISTRADO\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_16", "source": "cu17_ll_routes", "target": "cu17_ll_iu", "value": "16: HTTP 409 Conflict (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu17_17", "source": "cu17_ll_iu", "target": "cu17_ll_encargado", "value": "17: mostrar_error_sku_duplicado()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu17_sec", "name": "CU17 - Gestionar productos (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU18: Gestionar categorías
# ==============================================================================
def build_cu18_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu18", "value": "<b>sd</b> CU18 — Gestionar categorías (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu18_ll_encargado", "value": "<b>Encargado Catálogo</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu18_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Categorias</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu18_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:categorias_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu18_ll_services", "value": "&laquo;control&raquo;<br/><b>:categorias_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu18_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:categoria_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu18_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu18_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu18_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu18_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu18_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu18_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 370, "w": 12, "h": 30},
        {"id": "cu18_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 480, "w": 12, "h": 30},
        {"id": "cu18_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 780, "w": 12, "h": 30},

        {"id": "cu18_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 435, "w": 1430, "h": 580},
        {"id": "cu18_lbl_alt1", "value": "[nombre_categoria_unico == true &amp;&amp; datos_validos] (Curso Básico: Categoría Guardada)", "style": s["guard_label"], "x": 115, "y": 440, "w": 550, "h": 20},

        # opt validar categoría padre
        {"id": "cu18_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 550, "w": 570, "h": 75},
        {"id": "cu18_lbl_opt", "value": "[id_padre != null] (Vincular Categoría Jerárquica)", "style": s["guard_label"], "x": 720, "y": 555, "w": 350, "h": 20},

        {"id": "cu18_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu18_lbl_alt2", "value": "[else: nombre_duplicado || productos_activos_asociados] (Curso Alterno: Error 409)", "style": s["guard_label"], "x": 55, "y": 898, "w": 580, "h": 20}
    ]

    edges = [
        {"id": "e_cu18_01", "source": "cu18_ll_encargado", "target": "cu18_ll_iu", "value": "1: ingresar_datos_categoria(nombre, descripcion, id_padre)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_02", "source": "cu18_ll_iu", "target": "cu18_ll_routes", "value": "2: POST /api/categorias(dto_categoria)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_03", "source": "cu18_ll_routes", "target": "cu18_ll_services", "value": "3: guardar_categoria(id_empresa, dto_categoria)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_04", "source": "cu18_ll_services", "target": "cu18_ll_repos", "value": "4: verificar_nombre_categoria_unico(nombre, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((370 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((370 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_05", "source": "cu18_ll_repos", "target": "cu18_ll_services", "value": "5: return bool_nombre_disponible", "style": s["return"], "exitX": 0.5, "exitY": round((400 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((400 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu18_06", "source": "cu18_ll_services", "target": "cu18_ll_repos", "value": "6: insertar_categoria(nombre, descripcion, id_padre, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((480 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_07", "source": "cu18_ll_repos", "target": "cu18_ll_services", "value": "7: return id_categoria_creada", "style": s["return"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},

        # opt
        {"id": "e_cu18_08", "source": "cu18_ll_services", "target": "cu18_ll_repos", "value": "8: vincular_jerarquia_padre(id_categoria, id_padre)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((575 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((575 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_09", "source": "cu18_ll_repos", "target": "cu18_ll_services", "value": "9: return bool_padre_ok", "style": s["return"], "exitX": 0.5, "exitY": round((600 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((600 - y_start_box) / h_box, 5)},

        {"id": "e_cu18_10", "source": "cu18_ll_services", "target": "cu18_ll_bitacora", "value": "10: registrar_bitacora(GESTION_CATEGORIA, id_categoria)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((780 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((780 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_11", "source": "cu18_ll_services", "target": "cu18_ll_routes", "value": "11: return categoria_guardada(id_categoria, nombre)", "style": s["return"], "exitX": 0.5, "exitY": round((810 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((810 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_12", "source": "cu18_ll_routes", "target": "cu18_ll_iu", "value": "12: HTTP 201 Created (categoria)", "style": s["return"], "exitX": 0.5, "exitY": round((835 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((835 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_13", "source": "cu18_ll_iu", "target": "cu18_ll_encargado", "value": "13: actualizar_arbol_categorias()", "style": s["return"], "exitX": 0.5, "exitY": round((860 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((860 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu18_14", "source": "cu18_ll_services", "target": "cu18_ll_routes", "value": "14: throw ConflictException(\"NOMBRE_CATEGORIA_DUPLICADO\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_15", "source": "cu18_ll_routes", "target": "cu18_ll_iu", "value": "15: HTTP 409 Conflict (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu18_16", "source": "cu18_ll_iu", "target": "cu18_ll_encargado", "value": "16: mostrar_error_nombre_duplicado()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu18_sec", "name": "CU18 - Gestionar categorías (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU19: Gestionar tallas y colores
# ==============================================================================
def build_cu19_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu19", "value": "<b>sd</b> CU19 — Gestionar tallas y colores (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu19_ll_encargado", "value": "<b>Encargado Inventario</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu19_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Variantes</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu19_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:variantes_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu19_ll_services", "value": "&laquo;control&raquo;<br/><b>:variantes_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu19_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:variante_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu19_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu19_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu19_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu19_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu19_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu19_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 370, "w": 12, "h": 30},
        {"id": "cu19_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 480, "w": 12, "h": 30},
        {"id": "cu19_act_repos_3", "value": "", "style": s["activation"], "x": 1154, "y": 660, "w": 12, "h": 30},
        {"id": "cu19_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 780, "w": 12, "h": 30},

        # loop sucursales para inventario inicial
        {"id": "cu19_frag_loop", "value": "<b>loop</b>", "style": s["frame_operator"], "x": 650, "y": 630, "w": 570, "h": 75},
        {"id": "cu19_lbl_loop", "value": "[para cada sucursal con stock inicial]", "style": s["guard_label"], "x": 720, "y": 635, "w": 280, "h": 20},

        {"id": "cu19_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 435, "w": 1430, "h": 580},
        {"id": "cu19_lbl_alt1", "value": "[combinacion_nueva == true &amp;&amp; stock >= 0] (Curso Básico: Variante Creada)", "style": s["guard_label"], "x": 115, "y": 440, "w": 500, "h": 20},

        {"id": "cu19_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu19_lbl_alt2", "value": "[else: combinacion_ya_existe || stock < 0] (Curso Alterno: Error 409/422)", "style": s["guard_label"], "x": 55, "y": 898, "w": 520, "h": 20}
    ]

    edges = [
        {"id": "e_cu19_01", "source": "cu19_ll_encargado", "target": "cu19_ll_iu", "value": "1: seleccionar_variante(id_producto, talla_id, color_id, stock)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_02", "source": "cu19_ll_iu", "target": "cu19_ll_routes", "value": "2: POST /api/productos/{id}/variantes(dto_variante)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_03", "source": "cu19_ll_routes", "target": "cu19_ll_services", "value": "3: agregar_variante_producto(id_producto, dto_variante)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_04", "source": "cu19_ll_services", "target": "cu19_ll_repos", "value": "4: verificar_combinacion_existente(id_producto, talla, color)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((370 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((370 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_05", "source": "cu19_ll_repos", "target": "cu19_ll_services", "value": "5: return bool_combinacion_existe", "style": s["return"], "exitX": 0.5, "exitY": round((400 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((400 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu19_06", "source": "cu19_ll_services", "target": "cu19_ll_repos", "value": "6: insertar_producto_talla_color(id_producto, talla, color)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((480 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_07", "source": "cu19_ll_repos", "target": "cu19_ll_services", "value": "7: return id_ptc_creada", "style": s["return"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},

        # loop
        {"id": "e_cu19_08", "source": "cu19_ll_services", "target": "cu19_ll_repos", "value": "8: inicializar_inventario_sucursal(id_ptc, id_sucursal, stock)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((660 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((660 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_09", "source": "cu19_ll_repos", "target": "cu19_ll_services", "value": "9: return bool_stock_ok", "style": s["return"], "exitX": 0.5, "exitY": round((685 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((685 - y_start_box) / h_box, 5)},

        {"id": "e_cu19_10", "source": "cu19_ll_services", "target": "cu19_ll_bitacora", "value": "10: registrar_bitacora(CREAR_VARIANTE, id_ptc)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((780 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((780 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_11", "source": "cu19_ll_services", "target": "cu19_ll_routes", "value": "11: return variante_creada(id_ptc, stock)", "style": s["return"], "exitX": 0.5, "exitY": round((810 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((810 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_12", "source": "cu19_ll_routes", "target": "cu19_ll_iu", "value": "12: HTTP 201 Created (variante)", "style": s["return"], "exitX": 0.5, "exitY": round((835 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((835 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_13", "source": "cu19_ll_iu", "target": "cu19_ll_encargado", "value": "13: actualizar_matriz_variantes()", "style": s["return"], "exitX": 0.5, "exitY": round((860 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((860 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu19_14", "source": "cu19_ll_services", "target": "cu19_ll_routes", "value": "14: throw ConflictException(\"COMBINACION_TALLA_COLOR_DUPLICADA\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_15", "source": "cu19_ll_routes", "target": "cu19_ll_iu", "value": "15: HTTP 409 Conflict (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu19_16", "source": "cu19_ll_iu", "target": "cu19_ll_encargado", "value": "16: mostrar_error_combinacion_duplicada()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu19_sec", "name": "CU19 - Gestionar tallas y colores (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU20: Gestionar temporadas y colecciones
# ==============================================================================
def build_cu20_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu20", "value": "<b>sd</b> CU20 — Gestionar temporadas y colecciones (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu20_ll_encargado", "value": "<b>Encargado Catálogo</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu20_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Colecciones</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu20_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:colecciones_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu20_ll_services", "value": "&laquo;control&raquo;<br/><b>:colecciones_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu20_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:coleccion_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu20_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu20_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu20_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu20_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu20_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu20_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 370, "w": 12, "h": 30},
        {"id": "cu20_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 480, "w": 12, "h": 30},
        {"id": "cu20_act_repos_3", "value": "", "style": s["activation"], "x": 1154, "y": 660, "w": 12, "h": 30},
        {"id": "cu20_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 780, "w": 12, "h": 30},

        # loop vinculación productos
        {"id": "cu20_frag_loop", "value": "<b>loop</b>", "style": s["frame_operator"], "x": 650, "y": 630, "w": 570, "h": 75},
        {"id": "cu20_lbl_loop", "value": "[para cada producto de la colección]", "style": s["guard_label"], "x": 720, "y": 635, "w": 280, "h": 20},

        {"id": "cu20_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 435, "w": 1430, "h": 580},
        {"id": "cu20_lbl_alt1", "value": "[fecha_fin > fecha_inicio &amp;&amp; nombre_unico] (Curso Básico: Campaña Registrada)", "style": s["guard_label"], "x": 115, "y": 440, "w": 530, "h": 20},

        {"id": "cu20_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu20_lbl_alt2", "value": "[else: fecha_fin <= fecha_inicio || nombre_duplicado] (Curso Alterno: Error)", "style": s["guard_label"], "x": 55, "y": 898, "w": 540, "h": 20}
    ]

    edges = [
        {"id": "e_cu20_01", "source": "cu20_ll_encargado", "target": "cu20_ll_iu", "value": "1: ingresar_datos_coleccion(nombre, inicio, fin, ids_productos)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_02", "source": "cu20_ll_iu", "target": "cu20_ll_routes", "value": "2: POST /api/colecciones(dto_coleccion)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_03", "source": "cu20_ll_routes", "target": "cu20_ll_services", "value": "3: guardar_temporada_coleccion(id_empresa, dto)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_04", "source": "cu20_ll_services", "target": "cu20_ll_repos", "value": "4: verificar_nombre_coleccion_unico(nombre, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((370 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((370 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_05", "source": "cu20_ll_repos", "target": "cu20_ll_services", "value": "5: return bool_nombre_disponible", "style": s["return"], "exitX": 0.5, "exitY": round((400 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((400 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu20_06", "source": "cu20_ll_services", "target": "cu20_ll_repos", "value": "6: insertar_coleccion(nombre, inicio, fin, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((480 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_07", "source": "cu20_ll_repos", "target": "cu20_ll_services", "value": "7: return id_coleccion_creada", "style": s["return"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},

        # loop
        {"id": "e_cu20_08", "source": "cu20_ll_services", "target": "cu20_ll_repos", "value": "8: vincular_producto_coleccion(id_coleccion, id_prod)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((660 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((660 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_09", "source": "cu20_ll_repos", "target": "cu20_ll_services", "value": "9: return bool_vinculo_ok", "style": s["return"], "exitX": 0.5, "exitY": round((685 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((685 - y_start_box) / h_box, 5)},

        {"id": "e_cu20_10", "source": "cu20_ll_services", "target": "cu20_ll_bitacora", "value": "10: registrar_bitacora(CREAR_COLECCION, id_coleccion)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((780 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((780 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_11", "source": "cu20_ll_services", "target": "cu20_ll_routes", "value": "11: return coleccion_guardada(id_coleccion, nombre)", "style": s["return"], "exitX": 0.5, "exitY": round((810 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((810 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_12", "source": "cu20_ll_routes", "target": "cu20_ll_iu", "value": "12: HTTP 201 Created (coleccion)", "style": s["return"], "exitX": 0.5, "exitY": round((835 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((835 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_13", "source": "cu20_ll_iu", "target": "cu20_ll_encargado", "value": "13: actualizar_lista_colecciones()", "style": s["return"], "exitX": 0.5, "exitY": round((860 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((860 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu20_14", "source": "cu20_ll_services", "target": "cu20_ll_routes", "value": "14: throw BadRequestException(\"FECHA_FIN_DEBE_SER_POSTERIOR\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_15", "source": "cu20_ll_routes", "target": "cu20_ll_iu", "value": "15: HTTP 400 Bad Request (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu20_16", "source": "cu20_ll_iu", "target": "cu20_ll_encargado", "value": "16: mostrar_error_fechas_incoherentes()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu20_sec", "name": "CU20 - Gestionar temporadas y colecciones (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU21: Gestionar proveedores
# ==============================================================================
def build_cu21_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu21", "value": "<b>sd</b> CU21 — Gestionar proveedores (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu21_ll_encargado", "value": "<b>Encargado Compras</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu21_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Proveedores</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu21_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:proveedores_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu21_ll_services", "value": "&laquo;control&raquo;<br/><b>:proveedores_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu21_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:proveedor_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu21_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu21_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu21_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu21_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu21_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu21_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 370, "w": 12, "h": 30},
        {"id": "cu21_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 480, "w": 12, "h": 30},
        {"id": "cu21_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 780, "w": 12, "h": 30},

        {"id": "cu21_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 435, "w": 1430, "h": 580},
        {"id": "cu21_lbl_alt1", "value": "[nit_proveedor_unico == true &amp;&amp; datos_validos] (Curso Básico: Proveedor Guardado)", "style": s["guard_label"], "x": 115, "y": 440, "w": 550, "h": 20},

        # opt verificación ordenes pendientes en caso de desactivar
        {"id": "cu21_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 550, "w": 570, "h": 75},
        {"id": "cu21_lbl_opt", "value": "[solicita_desactivar == true] (Verificar Órdenes Abiertas)", "style": s["guard_label"], "x": 720, "y": 555, "w": 360, "h": 20},

        {"id": "cu21_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu21_lbl_alt2", "value": "[else: nit_duplicado || ordenes_compra_activas] (Curso Alterno: Rechazo 409)", "style": s["guard_label"], "x": 55, "y": 898, "w": 550, "h": 20}
    ]

    edges = [
        {"id": "e_cu21_01", "source": "cu21_ll_encargado", "target": "cu21_ll_iu", "value": "1: ingresar_datos_proveedor(nit, razon_social, telefono, contacto)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_02", "source": "cu21_ll_iu", "target": "cu21_ll_routes", "value": "2: POST /api/proveedores(dto_proveedor)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_03", "source": "cu21_ll_routes", "target": "cu21_ll_services", "value": "3: registrar_proveedor(id_empresa, dto_proveedor)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_04", "source": "cu21_ll_services", "target": "cu21_ll_repos", "value": "4: verificar_nit_proveedor_unico(nit, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((370 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((370 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_05", "source": "cu21_ll_repos", "target": "cu21_ll_services", "value": "5: return bool_nit_disponible", "style": s["return"], "exitX": 0.5, "exitY": round((400 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((400 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu21_06", "source": "cu21_ll_services", "target": "cu21_ll_repos", "value": "6: insertar_proveedor(datos_proveedor, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((480 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_07", "source": "cu21_ll_repos", "target": "cu21_ll_services", "value": "7: return id_proveedor_creado", "style": s["return"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},

        # opt
        {"id": "e_cu21_08", "source": "cu21_ll_services", "target": "cu21_ll_repos", "value": "8: contar_ordenes_compra_activas(id_proveedor)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((575 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((575 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_09", "source": "cu21_ll_repos", "target": "cu21_ll_services", "value": "9: return conteo_ordenes_activas", "style": s["return"], "exitX": 0.5, "exitY": round((600 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((600 - y_start_box) / h_box, 5)},

        {"id": "e_cu21_10", "source": "cu21_ll_services", "target": "cu21_ll_bitacora", "value": "10: registrar_bitacora(REGISTRAR_PROVEEDOR, id_proveedor)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((780 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((780 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_11", "source": "cu21_ll_services", "target": "cu21_ll_routes", "value": "11: return proveedor_guardado(id_proveedor, nit)", "style": s["return"], "exitX": 0.5, "exitY": round((810 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((810 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_12", "source": "cu21_ll_routes", "target": "cu21_ll_iu", "value": "12: HTTP 201 Created (proveedor)", "style": s["return"], "exitX": 0.5, "exitY": round((835 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((835 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_13", "source": "cu21_ll_iu", "target": "cu21_ll_encargado", "value": "13: actualizar_directorio_proveedores()", "style": s["return"], "exitX": 0.5, "exitY": round((860 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((860 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu21_14", "source": "cu21_ll_services", "target": "cu21_ll_routes", "value": "14: throw ConflictException(\"NIT_PROVEEDOR_DUPLICADO\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_15", "source": "cu21_ll_routes", "target": "cu21_ll_iu", "value": "15: HTTP 409 Conflict (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu21_16", "source": "cu21_ll_iu", "target": "cu21_ll_encargado", "value": "16: mostrar_error_nit_duplicado()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu21_sec", "name": "CU21 - Gestionar proveedores (Secuencia)", "nodes": nodes, "edges": edges}
