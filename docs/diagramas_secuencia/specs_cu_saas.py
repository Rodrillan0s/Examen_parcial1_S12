#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Especificaciones de Diagramas de Secuencia UML 2.5+ (ICONIX):
- CU34: Gestionar planes de suscripción (P2 — Nuevo)
- CU35: Gestionar suscripciones empresariales (P2 — Nuevo)
- CU36: Consultar plan y límites de suscripción (P2 — Nuevo)
- CU41: Gestionar respaldos y restauraciones (P2 — Nuevo)
- CU43: Gestionar asignaciones de empleados a sucursales (P2 — Nuevo)
"""

from specs_cu_auth import get_common_sequence_styles

# ==============================================================================
# CU34: Gestionar planes de suscripción (P2 — Nuevo)
# ==============================================================================
def build_cu34_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu34", "value": "<b>sd</b> CU34 — Gestionar planes de suscripción (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu34_ll_superadmin", "value": "<b>Superadmin</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu34_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_PlanesSaaS</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu34_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:saas_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu34_ll_services", "value": "&laquo;control&raquo;<br/><b>:saas_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu34_ll_plan_repo", "value": "&laquo;entity&raquo;<br/><b>:plan_repos</b>", "style": s["lifeline_box"], "x": 880, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu34_ll_susc_repo", "value": "&laquo;entity&raquo;<br/><b>:suscripcion_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu34_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu34_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu34_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 160, "w": 12, "h": 150},
        {"id": "cu34_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 380, "w": 12, "h": 490},
        {"id": "cu34_act_routes_3", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu34_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 180, "w": 12, "h": 110},
        {"id": "cu34_act_services_2", "value": "", "style": s["activation"], "x": 716, "y": 410, "w": 12, "h": 440},
        {"id": "cu34_act_plan_1", "value": "", "style": s["activation"], "x": 934, "y": 215, "w": 12, "h": 30},
        {"id": "cu34_act_plan_2", "value": "", "style": s["activation"], "x": 934, "y": 510, "w": 12, "h": 30},
        {"id": "cu34_act_susc_1", "value": "", "style": s["activation"], "x": 1154, "y": 640, "w": 12, "h": 30},
        {"id": "cu34_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 760, "w": 12, "h": 30},

        # alt validación código inmutable y capacidad
        {"id": "cu34_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 465, "w": 1430, "h": 550},
        {"id": "cu34_lbl_alt1", "value": "[codigo in ['BASICO', 'PROFESIONAL'] &amp;&amp; limites_inmutables] (Curso Básico: Catálogo Actualizado)", "style": s["guard_label"], "x": 115, "y": 470, "w": 650, "h": 20},

        # opt preservación de suscripciones existentes
        {"id": "cu34_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 605, "w": 570, "h": 75},
        {"id": "cu34_lbl_opt", "value": "[suscripciones_asignadas > 0] (Preservar Contratos Vigentes)", "style": s["guard_label"], "x": 720, "y": 610, "w": 380, "h": 20},

        {"id": "cu34_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu34_lbl_alt2", "value": "[else: codigo_arbitrario || alteracion_limites] (Curso Alterno: Rechazo 422 / 403)", "style": s["guard_label"], "x": 55, "y": 898, "w": 620, "h": 20}
    ]

    edges = [
        {"id": "e_cu34_01", "source": "cu34_ll_superadmin", "target": "cu34_ll_iu", "value": "1: acceder_catalogo_planes()", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_02", "source": "cu34_ll_iu", "target": "cu34_ll_routes", "value": "2: GET /api/saas/planes()", "style": s["sync_call"], "exitX": 0.5, "exitY": round((160 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((160 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_03", "source": "cu34_ll_routes", "target": "cu34_ll_services", "value": "3: listar_planes_disponibles()", "style": s["sync_call"], "exitX": 0.5, "exitY": round((180 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((180 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_04", "source": "cu34_ll_services", "target": "cu34_ll_plan_repo", "value": "4: buscar_todos_planes()", "style": s["sync_call"], "exitX": 0.5, "exitY": round((215 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((215 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_05", "source": "cu34_ll_plan_repo", "target": "cu34_ll_services", "value": "5: return lista_planes [BASICO, PROFESIONAL]", "style": s["return"], "exitX": 0.5, "exitY": round((245 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((245 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_06", "source": "cu34_ll_services", "target": "cu34_ll_routes", "value": "6: return dto_planes", "style": s["return"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_07", "source": "cu34_ll_routes", "target": "cu34_ll_iu", "value": "7: renderizar_grilla_planes(dto_planes)", "style": s["return"], "exitX": 0.5, "exitY": round((295 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((295 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_08", "source": "cu34_ll_iu", "target": "cu34_ll_superadmin", "value": "8: mostrar_planes_y_capacidades()", "style": s["return"], "exitX": 0.5, "exitY": round((325 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((325 - y_start_actor) / h_actor, 5)},

        # Operación de edición
        {"id": "e_cu34_09", "source": "cu34_ll_superadmin", "target": "cu34_ll_iu", "value": "9: editar_disponibilidad_plan(codigo, descripcion, activo)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((355 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((355 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_10", "source": "cu34_ll_iu", "target": "cu34_ll_routes", "value": "10: PUT /api/saas/planes/{codigo}(dto_plan)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((380 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((380 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_11", "source": "cu34_ll_routes", "target": "cu34_ll_services", "value": "11: actualizar_plan(codigo, dto_plan)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((410 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((410 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_12", "source": "cu34_ll_services", "target": "cu34_ll_services", "value": "12: validar_codigo_fijo_y_limites(codigo, dto_plan)", "style": s["self_call"], "exitX": 0.5, "exitY": round((435 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((455 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu34_13", "source": "cu34_ll_services", "target": "cu34_ll_plan_repo", "value": "13: actualizar_estado_plan(codigo, descripcion, activo)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_14", "source": "cu34_ll_plan_repo", "target": "cu34_ll_services", "value": "14: return plan_actualizado", "style": s["return"], "exitX": 0.5, "exitY": round((540 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((540 - y_start_box) / h_box, 5)},

        {"id": "e_cu34_15", "source": "cu34_ll_services", "target": "cu34_ll_susc_repo", "value": "15: verificar_contratos_vigentes(codigo)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((640 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((640 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_16", "source": "cu34_ll_susc_repo", "target": "cu34_ll_services", "value": "16: return contratos_preservados", "style": s["return"], "exitX": 0.5, "exitY": round((670 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((670 - y_start_box) / h_box, 5)},

        {"id": "e_cu34_17", "source": "cu34_ll_services", "target": "cu34_ll_bitacora", "value": "17: registrar_bitacora(ACTUALIZAR_PLAN_SAAS, codigo)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((760 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((760 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_18", "source": "cu34_ll_services", "target": "cu34_ll_routes", "value": "18: return dto_plan_actualizado", "style": s["return"], "exitX": 0.5, "exitY": round((800 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((800 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_19", "source": "cu34_ll_routes", "target": "cu34_ll_iu", "value": "19: HTTP 200 OK (plan_actualizado)", "style": s["return"], "exitX": 0.5, "exitY": round((825 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((825 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_20", "source": "cu34_ll_iu", "target": "cu34_ll_superadmin", "value": "20: mostrar_confirmacion_plan_actualizado()", "style": s["return"], "exitX": 0.5, "exitY": round((855 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((855 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu34_21", "source": "cu34_ll_services", "target": "cu34_ll_routes", "value": "21: throw UnprocessableException(\"CODIGO_O_CAPACIDAD_INVALIDA\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_22", "source": "cu34_ll_routes", "target": "cu34_ll_iu", "value": "22: HTTP 422 Unprocessable (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu34_23", "source": "cu34_ll_iu", "target": "cu34_ll_superadmin", "value": "23: mostrar_alerta_rechazo_codigo()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu34_sec", "name": "CU34 - Gestionar planes de suscripción (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU35: Gestionar suscripciones empresariales (P2 — Nuevo)
# ==============================================================================
def build_cu35_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu35", "value": "<b>sd</b> CU35 — Gestionar suscripciones empresariales (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu35_ll_superadmin", "value": "<b>Superadmin</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu35_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Suscripciones</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu35_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:saas_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu35_ll_services", "value": "&laquo;control&raquo;<br/><b>:saas_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu35_ll_plan_repo", "value": "&laquo;entity&raquo;<br/><b>:plan_repos</b>", "style": s["lifeline_box"], "x": 880, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu35_ll_suc_repo", "value": "&laquo;entity&raquo;<br/><b>:sucursal_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu35_ll_susc_repo", "value": "&laquo;entity&raquo;<br/><b>:suscripcion_repos</b>", "style": s["lifeline_box"], "x": 1290, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu35_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1430, "y": y_start_box, "w": 100, "h": h_box},

        {"id": "cu35_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu35_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu35_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu35_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu35_act_plan_1", "value": "", "style": s["activation"], "x": 934, "y": 320, "w": 12, "h": 30},
        {"id": "cu35_act_suc_1", "value": "", "style": s["activation"], "x": 1154, "y": 380, "w": 12, "h": 30},
        {"id": "cu35_act_susc_1", "value": "", "style": s["activation"], "x": 1344, "y": 510, "w": 12, "h": 30},
        {"id": "cu35_act_bitacora", "value": "", "style": s["activation"], "x": 1474, "y": 760, "w": 12, "h": 30},

        # alt validación capacidad y solapamiento
        {"id": "cu35_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 445, "w": 1490, "h": 570},
        {"id": "cu35_lbl_alt1", "value": "[sucursales_activas <= max_sucursales &amp;&amp; no_solapamiento] (Curso Básico: Periodo Registrado)", "style": s["guard_label"], "x": 115, "y": 450, "w": 650, "h": 20},

        # opt cancelación previa
        {"id": "cu35_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 620, "w": 720, "h": 75},
        {"id": "cu35_lbl_opt", "value": "[es_cancelacion == true] (Actualizar estado a CANCELADA sin borrado físico)", "style": s["guard_label"], "x": 720, "y": 625, "w": 450, "h": 20},

        {"id": "cu35_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1490, "h": 1},
        {"id": "cu35_lbl_alt2", "value": "[else: sucursales_activas > max_sucursales || solapamiento] (Curso Alterno: Rechazo 409 Conflict)", "style": s["guard_label"], "x": 55, "y": 898, "w": 680, "h": 20}
    ]

    edges = [
        {"id": "e_cu35_01", "source": "cu35_ll_superadmin", "target": "cu35_ll_iu", "value": "1: seleccionar_empresa_y_plan(id_empresa, codigo_plan, fecha_ini, fecha_fin, motivo)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_02", "source": "cu35_ll_iu", "target": "cu35_ll_routes", "value": "2: POST /api/saas/suscripciones(dto_suscripcion)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_03", "source": "cu35_ll_routes", "target": "cu35_ll_services", "value": "3: crear_suscripcion(dto_suscripcion)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_04", "source": "cu35_ll_services", "target": "cu35_ll_services", "value": "4: validar_fechas(fecha_ini, fecha_fin)", "style": s["self_call"], "exitX": 0.5, "exitY": round((290 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((310 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_05", "source": "cu35_ll_services", "target": "cu35_ll_plan_repo", "value": "5: obtener_limites_plan(codigo_plan)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((320 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((320 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_06", "source": "cu35_ll_plan_repo", "target": "cu35_ll_services", "value": "6: return plan_info(max_sucursales)", "style": s["return"], "exitX": 0.5, "exitY": round((350 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((350 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_07", "source": "cu35_ll_services", "target": "cu35_ll_suc_repo", "value": "7: contar_sucursales_activas(id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((380 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((380 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_08", "source": "cu35_ll_suc_repo", "target": "cu35_ll_services", "value": "8: return total_sucursales_activas", "style": s["return"], "exitX": 0.5, "exitY": round((410 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((410 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu35_09", "source": "cu35_ll_services", "target": "cu35_ll_susc_repo", "value": "9: insertar_periodo_suscripcion(dto_suscripcion)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_10", "source": "cu35_ll_susc_repo", "target": "cu35_ll_services", "value": "10: return id_suscripcion_creada", "style": s["return"], "exitX": 0.5, "exitY": round((540 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((540 - y_start_box) / h_box, 5)},

        {"id": "e_cu35_11", "source": "cu35_ll_services", "target": "cu35_ll_susc_repo", "value": "11: actualizar_estado(id_suscripcion, CANCELADA)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((650 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((650 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_12", "source": "cu35_ll_susc_repo", "target": "cu35_ll_services", "value": "12: return bool_cancel_ok", "style": s["return"], "exitX": 0.5, "exitY": round((675 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((675 - y_start_box) / h_box, 5)},

        {"id": "e_cu35_13", "source": "cu35_ll_services", "target": "cu35_ll_bitacora", "value": "13: registrar_bitacora(GESTION_SUSCRIPCION, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((760 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((760 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_14", "source": "cu35_ll_services", "target": "cu35_ll_routes", "value": "14: return dto_suscripcion_creada", "style": s["return"], "exitX": 0.5, "exitY": round((800 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((800 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_15", "source": "cu35_ll_routes", "target": "cu35_ll_iu", "value": "15: HTTP 201 Created (suscripcion_confirmada)", "style": s["return"], "exitX": 0.5, "exitY": round((825 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((825 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_16", "source": "cu35_ll_iu", "target": "cu35_ll_superadmin", "value": "16: mostrar_confirmacion_periodo()", "style": s["return"], "exitX": 0.5, "exitY": round((855 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((855 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu35_17", "source": "cu35_ll_services", "target": "cu35_ll_routes", "value": "17: throw ConflictException(\"CAPACIDAD_EXCEDIDA_O_SOLAPAMIENTO\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_18", "source": "cu35_ll_routes", "target": "cu35_ll_iu", "value": "18: HTTP 409 Conflict (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu35_19", "source": "cu35_ll_iu", "target": "cu35_ll_superadmin", "value": "19: mostrar_alerta_error_capacidad()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu35_sec", "name": "CU35 - Gestionar suscripciones empresariales (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU36: Consultar plan y límites de suscripción (P2 — Nuevo)
# ==============================================================================
def build_cu36_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu36", "value": "<b>sd</b> CU36 — Consultar plan y límites de suscripción (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu36_ll_admin", "value": "<b>Admin Tienda</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu36_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_MiPlan</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu36_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:saas_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu36_ll_services", "value": "&laquo;control&raquo;<br/><b>:saas_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu36_ll_susc_repo", "value": "&laquo;entity&raquo;<br/><b>:suscripcion_repos</b>", "style": s["lifeline_box"], "x": 880, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu36_ll_plan_repo", "value": "&laquo;entity&raquo;<br/><b>:plan_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu36_ll_suc_repo", "value": "&laquo;entity&raquo;<br/><b>:sucursal_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu36_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu36_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu36_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu36_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu36_act_susc_1", "value": "", "style": s["activation"], "x": 934, "y": 360, "w": 12, "h": 30},
        {"id": "cu36_act_plan_1", "value": "", "style": s["activation"], "x": 1154, "y": 510, "w": 12, "h": 30},
        {"id": "cu36_act_suc_1", "value": "", "style": s["activation"], "x": 1364, "y": 620, "w": 12, "h": 30},

        # alt validación vigencia de suscripción
        {"id": "cu36_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 445, "w": 1430, "h": 570},
        {"id": "cu36_lbl_alt1", "value": "[suscripcion_vigente != null &amp;&amp; empresa_activa == true] (Curso Básico: Consulta Exitosa)", "style": s["guard_label"], "x": 115, "y": 450, "w": 650, "h": 20},

        # opt capacidad de reportes
        {"id": "cu36_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 700, "w": 570, "h": 75},
        {"id": "cu36_lbl_opt", "value": "[plan_codigo == 'PROFESIONAL'] (Habilitar reportes generativos)", "style": s["guard_label"], "x": 720, "y": 705, "w": 400, "h": 20},

        {"id": "cu36_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu36_lbl_alt2", "value": "[else: sin_suscripcion || vencida || empresa_inactiva] (Curso Alterno: Alerta y Bloqueo)", "style": s["guard_label"], "x": 55, "y": 898, "w": 650, "h": 20}
    ]

    edges = [
        {"id": "e_cu36_01", "source": "cu36_ll_admin", "target": "cu36_ll_iu", "value": "1: solicitar_consulta_mi_plan()", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_02", "source": "cu36_ll_iu", "target": "cu36_ll_routes", "value": "2: GET /api/saas/mi-plan()", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_03", "source": "cu36_ll_routes", "target": "cu36_ll_services", "value": "3: consultar_plan_y_limites(token_jwt)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_04", "source": "cu36_ll_services", "target": "cu36_ll_services", "value": "4: extraer_id_empresa(token_jwt)", "style": s["self_call"], "exitX": 0.5, "exitY": round((305 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((330 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_05", "source": "cu36_ll_services", "target": "cu36_ll_susc_repo", "value": "5: buscar_suscripcion_vigente(id_empresa, fecha_actual)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((360 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((360 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_06", "source": "cu36_ll_susc_repo", "target": "cu36_ll_services", "value": "6: return suscripcion_info(id_plan, fecha_fin, estado)", "style": s["return"], "exitX": 0.5, "exitY": round((390 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((390 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu36_07", "source": "cu36_ll_services", "target": "cu36_ll_plan_repo", "value": "7: buscar_por_id(id_plan)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_08", "source": "cu36_ll_plan_repo", "target": "cu36_ll_services", "value": "8: return plan_info(codigo, max_sucursales, reportes_ia)", "style": s["return"], "exitX": 0.5, "exitY": round((540 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((540 - y_start_box) / h_box, 5)},

        {"id": "e_cu36_09", "source": "cu36_ll_services", "target": "cu36_ll_suc_repo", "value": "9: contar_sucursales_activas(id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((620 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((620 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_10", "source": "cu36_ll_suc_repo", "target": "cu36_ll_services", "value": "10: return total_sucursales_activas", "style": s["return"], "exitX": 0.5, "exitY": round((650 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((650 - y_start_box) / h_box, 5)},

        {"id": "e_cu36_11", "source": "cu36_ll_services", "target": "cu36_ll_services", "value": "11: calcular_disponibilidad(max_sucursales, total_activas)", "style": s["self_call"], "exitX": 0.5, "exitY": round((715 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((735 - y_start_box) / h_box, 5)},

        {"id": "e_cu36_12", "source": "cu36_ll_services", "target": "cu36_ll_routes", "value": "12: return dto_metricas_plan", "style": s["return"], "exitX": 0.5, "exitY": round((800 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((800 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_13", "source": "cu36_ll_routes", "target": "cu36_ll_iu", "value": "13: HTTP 200 OK (metricas_y_limites)", "style": s["return"], "exitX": 0.5, "exitY": round((825 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((825 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_14", "source": "cu36_ll_iu", "target": "cu36_ll_admin", "value": "14: mostrar_panel_estado_suscripcion()", "style": s["return"], "exitX": 0.5, "exitY": round((855 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((855 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu36_15", "source": "cu36_ll_services", "target": "cu36_ll_routes", "value": "15: return dto_alerta(SIN_SUSCRIPCION_O_VENCIDA)", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_16", "source": "cu36_ll_routes", "target": "cu36_ll_iu", "value": "16: HTTP 200 OK / 403 (estado_inactivo)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu36_17", "source": "cu36_ll_iu", "target": "cu36_ll_admin", "value": "17: mostrar_alerta_suscripcion_vencida()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu36_sec", "name": "CU36 - Consultar plan y límites de suscripción (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU41: Gestionar respaldos y restauraciones (P2 — Nuevo)
# ==============================================================================
def build_cu41_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu41", "value": "<b>sd</b> CU41 — Gestionar respaldos y restauraciones (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu41_ll_superadmin", "value": "<b>Superadmin</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu41_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Respaldos</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu41_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:backup_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu41_ll_services", "value": "&laquo;control&raquo;<br/><b>:backup_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu41_ll_security", "value": "&laquo;control&raquo;<br/><b>:security_service</b>", "style": s["lifeline_box"], "x": 880, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu41_ll_resp_repo", "value": "&laquo;entity&raquo;<br/><b>:respaldo_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu41_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu41_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu41_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu41_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu41_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu41_act_sec_1", "value": "", "style": s["activation"], "x": 936, "y": 320, "w": 12, "h": 30},
        {"id": "cu41_act_resp_1", "value": "", "style": s["activation"], "x": 1154, "y": 620, "w": 12, "h": 30},
        {"id": "cu41_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 760, "w": 12, "h": 30},

        # alt validación motor de volcado y checksum
        {"id": "cu41_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 445, "w": 1430, "h": 570},
        {"id": "cu41_lbl_alt1", "value": "[espacio_suficiente == true &amp;&amp; dump_exitoso] (Curso Básico: Respaldo Generado)", "style": s["guard_label"], "x": 115, "y": 450, "w": 650, "h": 20},

        # opt cálculo de checksum
        {"id": "cu41_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 530, "w": 570, "h": 75},
        {"id": "cu41_lbl_opt", "value": "[calcular_hash == true] (SHA-256 integridad de esquema)", "style": s["guard_label"], "x": 720, "y": 535, "w": 380, "h": 20},

        {"id": "cu41_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu41_lbl_alt2", "value": "[else: fallo_pg_dump || checksum_invalido] (Curso Alterno: Error Motor 500)", "style": s["guard_label"], "x": 55, "y": 898, "w": 620, "h": 20}
    ]

    edges = [
        {"id": "e_cu41_01", "source": "cu41_ll_superadmin", "target": "cu41_ll_iu", "value": "1: solicitar_respaldo(tipo='COMPLETO', motivo)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_02", "source": "cu41_ll_iu", "target": "cu41_ll_routes", "value": "2: POST /api/admin/respaldos(dto_respaldo)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_03", "source": "cu41_ll_routes", "target": "cu41_ll_services", "value": "3: ejecutar_respaldo(dto_respaldo)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_04", "source": "cu41_ll_services", "target": "cu41_ll_security", "value": "4: validar_privilegios_superadmin(token)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((320 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((320 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_05", "source": "cu41_ll_security", "target": "cu41_ll_services", "value": "5: return bool_autorizado", "style": s["return"], "exitX": 0.5, "exitY": round((350 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((350 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu41_06", "source": "cu41_ll_services", "target": "cu41_ll_services", "value": "6: ejecutar_pg_dump(esquemas_db)", "style": s["self_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((500 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_07", "source": "cu41_ll_services", "target": "cu41_ll_services", "value": "7: calcular_checksum_sha256(archivo_dump)", "style": s["self_call"], "exitX": 0.5, "exitY": round((555 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((575 - y_start_box) / h_box, 5)},

        {"id": "e_cu41_08", "source": "cu41_ll_services", "target": "cu41_ll_resp_repo", "value": "8: guardar_metadatos_respaldo(nombre, checksum, tamanio)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((620 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((620 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_09", "source": "cu41_ll_resp_repo", "target": "cu41_ll_services", "value": "9: return id_respaldo_registrado", "style": s["return"], "exitX": 0.5, "exitY": round((650 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((650 - y_start_box) / h_box, 5)},

        {"id": "e_cu41_10", "source": "cu41_ll_services", "target": "cu41_ll_bitacora", "value": "10: registrar_evento_critico(RESPALDO_SISTEMA, id_respaldo)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((760 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((760 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_11", "source": "cu41_ll_services", "target": "cu41_ll_routes", "value": "11: return dto_respaldo_creado", "style": s["return"], "exitX": 0.5, "exitY": round((800 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((800 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_12", "source": "cu41_ll_routes", "target": "cu41_ll_iu", "value": "12: HTTP 201 Created (checksum_validado)", "style": s["return"], "exitX": 0.5, "exitY": round((825 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((825 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_13", "source": "cu41_ll_iu", "target": "cu41_ll_superadmin", "value": "13: mostrar_confirmacion_respaldo()", "style": s["return"], "exitX": 0.5, "exitY": round((855 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((855 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu41_14", "source": "cu41_ll_services", "target": "cu41_ll_routes", "value": "14: throw BackupException(\"FALLA_MOTOR_O_CHECKSUM\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_15", "source": "cu41_ll_routes", "target": "cu41_ll_iu", "value": "15: HTTP 500 Internal Error (detalle_fallo)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu41_16", "source": "cu41_ll_iu", "target": "cu41_ll_superadmin", "value": "16: mostrar_alerta_error_motor()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu41_sec", "name": "CU41 - Gestionar respaldos y restauraciones (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU43: Gestionar asignaciones de empleados a sucursales (P2 — Nuevo)
# ==============================================================================
def build_cu43_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu43", "value": "<b>sd</b> CU43 — Gestionar asignaciones de empleados a sucursales (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu43_ll_admin", "value": "<b>Admin Empresa</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu43_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Asignaciones</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu43_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:rbac_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu43_ll_services", "value": "&laquo;control&raquo;<br/><b>:asignaciones_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu43_ll_suc_repo", "value": "&laquo;entity&raquo;<br/><b>:sucursal_repos</b>", "style": s["lifeline_box"], "x": 880, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu43_ll_usrsuc_repo", "value": "&laquo;entity&raquo;<br/><b>:usuario_sucursal_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu43_ll_emp_repo", "value": "&laquo;entity&raquo;<br/><b>:empleado_repos</b>", "style": s["lifeline_box"], "x": 1290, "y": y_start_box, "w": 110, "h": h_box},
        {"id": "cu43_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1430, "y": y_start_box, "w": 100, "h": h_box},

        {"id": "cu43_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu43_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu43_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu43_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu43_act_suc_1", "value": "", "style": s["activation"], "x": 934, "y": 380, "w": 12, "h": 30},
        {"id": "cu43_act_usrsuc_1", "value": "", "style": s["activation"], "x": 1154, "y": 550, "w": 12, "h": 30},
        {"id": "cu43_act_emp_1", "value": "", "style": s["activation"], "x": 1344, "y": 660, "w": 12, "h": 30},
        {"id": "cu43_act_bitacora", "value": "", "style": s["activation"], "x": 1474, "y": 760, "w": 12, "h": 30},

        # loop validación de cada sucursal de la empresa
        {"id": "cu43_frag_loop", "value": "<b>loop</b>", "style": s["frame_operator"], "x": 650, "y": 340, "w": 350, "h": 85},
        {"id": "cu43_lbl_loop", "value": "[por cada id_sucursal en lista_sucursales]", "style": s["guard_label"], "x": 720, "y": 345, "w": 260, "h": 20},

        # alt validación pertenencia y estado activo
        {"id": "cu43_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 455, "w": 1490, "h": 560},
        {"id": "cu43_lbl_alt1", "value": "[todas_pertenecen_empresa &amp;&amp; activas] (Curso Básico: Reemplazo Atómico)", "style": s["guard_label"], "x": 115, "y": 460, "w": 650, "h": 20},

        # opt revocación total
        {"id": "cu43_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 490, "w": 570, "h": 50},
        {"id": "cu43_lbl_opt", "value": "[lista_sucursales.length == 0] (Revocación Total: borrado de asignaciones)", "style": s["guard_label"], "x": 720, "y": 493, "w": 450, "h": 20},

        {"id": "cu43_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1490, "h": 1},
        {"id": "cu43_lbl_alt2", "value": "[else: sucursal_ajena || inactiva] (Curso Alterno: Rechazo 403 Forbidden)", "style": s["guard_label"], "x": 55, "y": 898, "w": 650, "h": 20}
    ]

    edges = [
        {"id": "e_cu43_01", "source": "cu43_ll_admin", "target": "cu43_ll_iu", "value": "1: asignar_sucursales_empleado(id_empleado, [id_sucursal_1, id_sucursal_2])", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu43_02", "source": "cu43_ll_iu", "target": "cu43_ll_routes", "value": "2: PUT /api/empleados/{id}/sucursales(lista_ids)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu43_03", "source": "cu43_ll_routes", "target": "cu43_ll_services", "value": "3: actualizar_asignaciones_sucursal(id_empresa, id_empleado, lista_ids)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},

        # Loop calls
        {"id": "e_cu43_04", "source": "cu43_ll_services", "target": "cu43_ll_suc_repo", "value": "4: validar_pertenencia_empresa(id_sucursal, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((380 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((380 - y_start_box) / h_box, 5)},
        {"id": "e_cu43_05", "source": "cu43_ll_suc_repo", "target": "cu43_ll_services", "value": "5: return bool_valida", "style": s["return"], "exitX": 0.5, "exitY": round((405 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((405 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu43_06", "source": "cu43_ll_services", "target": "cu43_ll_usrsuc_repo", "value": "6: reemplazar_asignaciones_atomicamente(id_usuario, lista_ids)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((550 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((550 - y_start_box) / h_box, 5)},
        {"id": "e_cu43_07", "source": "cu43_ll_usrsuc_repo", "target": "cu43_ll_services", "value": "7: return asignaciones_actualizadas", "style": s["return"], "exitX": 0.5, "exitY": round((580 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((580 - y_start_box) / h_box, 5)},

        {"id": "e_cu43_08", "source": "cu43_ll_services", "target": "cu43_ll_emp_repo", "value": "8: verificar_integridad_empleado(id_empleado)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((660 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((660 - y_start_box) / h_box, 5)},
        {"id": "e_cu43_09", "source": "cu43_ll_emp_repo", "target": "cu43_ll_services", "value": "9: return datos_laborales_intactos", "style": s["return"], "exitX": 0.5, "exitY": round((690 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((690 - y_start_box) / h_box, 5)},

        {"id": "e_cu43_10", "source": "cu43_ll_services", "target": "cu43_ll_bitacora", "value": "10: registrar_bitacora(ASIGNACION_SUCURSALES, id_empleado)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((760 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((760 - y_start_box) / h_box, 5)},
        {"id": "e_cu43_11", "source": "cu43_ll_services", "target": "cu43_ll_routes", "value": "11: return dto_asignaciones", "style": s["return"], "exitX": 0.5, "exitY": round((800 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((800 - y_start_box) / h_box, 5)},
        {"id": "e_cu43_12", "source": "cu43_ll_routes", "target": "cu43_ll_iu", "value": "12: HTTP 200 OK (asignaciones_guardadas)", "style": s["return"], "exitX": 0.5, "exitY": round((825 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((825 - y_start_box) / h_box, 5)},
        {"id": "e_cu43_13", "source": "cu43_ll_iu", "target": "cu43_ll_admin", "value": "13: mostrar_confirmacion_asignaciones()", "style": s["return"], "exitX": 0.5, "exitY": round((855 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((855 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu43_14", "source": "cu43_ll_services", "target": "cu43_ll_routes", "value": "14: throw ForbiddenException(\"SUCURSAL_AJENA_O_INACTIVA\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu43_15", "source": "cu43_ll_routes", "target": "cu43_ll_iu", "value": "15: HTTP 403 Forbidden (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu43_16", "source": "cu43_ll_iu", "target": "cu43_ll_admin", "value": "16: mostrar_alerta_sucursal_invalida()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu43_sec", "name": "CU43 - Gestionar asignaciones de empleados a sucursales (Secuencia)", "nodes": nodes, "edges": edges}
