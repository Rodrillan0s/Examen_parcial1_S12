#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Especificaciones de Diagramas de Secuencia UML 2.5+ (ICONIX):
- CU01: Registrar usuario (P1)
- CU02: Iniciar sesión (P1)
- CU03: Gestionar perfil (P1)
- CU14: Gestionar usuarios y roles (P1)
"""

def get_common_sequence_styles():
    style_frame_main = (
        "shape=umlFrame;whiteSpace=wrap;html=1;pointerEvents=0;recursiveResize=0;container=1;collapsible=0;"
        "width=340;height=32;fillColor=#ffffff;strokeColor=#1e293b;strokeWidth=1.6;fontFamily=Arial;"
        "fontSize=12;fontStyle=1;fontColor=#0f172a;align=left;spacingLeft=12;"
    )
    style_lifeline_actor = (
        "shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;dropTarget=0;"
        "collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;participant=umlActor;"
        "fillColor=#ffffff;strokeColor=#1e293b;strokeWidth=1.6;fontFamily=Arial;fontSize=11.5;fontStyle=1;"
        "fontColor=#0f172a;size=60;"
    )
    style_lifeline_box = (
        "shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;dropTarget=0;"
        "collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;"
        "fillColor=#ffffff;strokeColor=#1e293b;strokeWidth=1.6;fontFamily=Arial;fontSize=11;"
        "fontColor=#0f172a;size=45;"
    )
    style_activation = (
        "html=1;points=[];perimeter=orthogonalPerimeter;outlineConnect=0;rounded=0;"
        "fillColor=#f8fafc;strokeColor=#334155;strokeWidth=1.2;"
    )
    style_frame_operator = (
        "shape=umlFrame;whiteSpace=wrap;html=1;pointerEvents=0;recursiveResize=0;container=0;collapsible=0;"
        "width=65;height=24;fillColor=#f8fafc;strokeColor=#334155;strokeWidth=1.4;fontFamily=Arial;"
        "fontSize=11;fontStyle=1;fontColor=#1e293b;align=left;spacingLeft=8;opacity=85;"
    )
    style_guard_label = (
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
        "fontFamily=Arial;fontSize=10.5;fontStyle=1;fontColor=#334155;"
    )
    style_divider = (
        "strokeColor=#94a3b8;strokeWidth=1.3;dashed=1;html=1;endArrow=none;"
    )
    style_sync_call = (
        "html=1;verticalAlign=bottom;endArrow=block;endFill=1;strokeColor=#1e293b;strokeWidth=1.5;"
        "fontFamily=Arial;fontSize=10.5;fontStyle=0;fontColor=#0f172a;rounded=0;edgeStyle=orthogonalEdgeStyle;"
    )
    style_return = (
        "html=1;verticalAlign=bottom;endArrow=open;endSize=7;dashed=1;strokeColor=#475569;strokeWidth=1.3;"
        "fontFamily=Arial;fontSize=10;fontStyle=2;fontColor=#475569;rounded=0;edgeStyle=orthogonalEdgeStyle;"
    )
    style_return_error = (
        "html=1;verticalAlign=bottom;endArrow=open;endSize=7;dashed=1;strokeColor=#dc2626;strokeWidth=1.5;"
        "fontFamily=Arial;fontSize=10;fontStyle=2;fontColor=#991b1b;rounded=0;edgeStyle=orthogonalEdgeStyle;"
    )
    style_self_call = (
        "html=1;verticalAlign=bottom;endArrow=block;endFill=1;strokeColor=#1e293b;strokeWidth=1.4;"
        "fontFamily=Arial;fontSize=10.5;fontStyle=0;fontColor=#0f172a;rounded=0;edgeStyle=orthogonalEdgeStyle;curved=0;"
    )

    return {
        "frame_main": style_frame_main,
        "lifeline_actor": style_lifeline_actor,
        "lifeline_box": style_lifeline_box,
        "activation": style_activation,
        "frame_operator": style_frame_operator,
        "guard_label": style_guard_label,
        "divider": style_divider,
        "sync_call": style_sync_call,
        "return": style_return,
        "return_error": style_return_error,
        "self_call": style_self_call
    }

# ==============================================================================
# CU01: Registrar usuario
# ==============================================================================
def build_cu01_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu01", "value": "<b>sd</b> CU01 — Registrar usuario (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu01_ll_cliente", "value": "<b>Cliente</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu01_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Registro</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu01_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:auth_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu01_ll_services", "value": "&laquo;control&raquo;<br/><b>:auth_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu01_ll_security", "value": "&laquo;control&raquo;<br/><b>:security_service</b>", "style": s["lifeline_box"], "x": 880, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu01_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:usuario_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu01_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu01_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu01_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 260, "w": 12, "h": 625},
        {"id": "cu01_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 940, "w": 12, "h": 35},
        {"id": "cu01_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 295, "w": 12, "h": 560},
        {"id": "cu01_act_services_2", "value": "", "style": s["activation"], "x": 716, "y": 935, "w": 12, "h": 15},
        {"id": "cu01_act_security_1", "value": "", "style": s["activation"], "x": 936, "y": 330, "w": 12, "h": 30},
        {"id": "cu01_act_security_2", "value": "", "style": s["activation"], "x": 936, "y": 480, "w": 12, "h": 30},
        {"id": "cu01_act_security_3", "value": "", "style": s["activation"], "x": 936, "y": 760, "w": 12, "h": 30},
        {"id": "cu01_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 390, "w": 12, "h": 30},
        {"id": "cu01_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 540, "w": 12, "h": 30},
        {"id": "cu01_act_repos_3", "value": "", "style": s["activation"], "x": 1154, "y": 600, "w": 12, "h": 30},
        {"id": "cu01_act_repos_4", "value": "", "style": s["activation"], "x": 1154, "y": 688, "w": 12, "h": 30},
        {"id": "cu01_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 818, "w": 12, "h": 30},

        {"id": "cu01_frag_loop", "value": "<b>loop</b>", "style": s["frame_operator"], "x": 210, "y": 160, "w": 200, "h": 75},
        {"id": "cu01_lbl_loop", "value": "[para cada campo obligatorio]", "style": s["guard_label"], "x": 280, "y": 163, "w": 160, "h": 20},

        {"id": "cu01_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 445, "w": 1430, "h": 575},
        {"id": "cu01_lbl_alt_guard1", "value": "[usuario_existente == null &amp;&amp; bool_password_valido == true] (Curso Básico: Registro Exitoso)", "style": s["guard_label"], "x": 115, "y": 450, "w": 520, "h": 20},

        {"id": "cu01_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 655, "w": 570, "h": 85},
        {"id": "cu01_lbl_opt_guard", "value": "[huella_dispositivo != null] (Registro de Hardware Confiable)", "style": s["guard_label"], "x": 720, "y": 660, "w": 360, "h": 20},

        {"id": "cu01_alt_divider", "value": "", "style": s["divider"], "x": 45, "y": 915, "w": 1430, "h": 1},
        {"id": "cu01_lbl_alt_guard2", "value": "[else: usuario_existente != null || !bool_password_valido] (Curso Alterno: Rechazo por Duplicidad o Datos Inválidos)", "style": s["guard_label"], "x": 55, "y": 918, "w": 650, "h": 20}
    ]

    edges = [
        {"id": "e_cu01_01", "source": "cu01_ll_cliente", "target": "cu01_ll_iu", "value": "1: enviar_formulario(datos_cliente)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_02", "source": "cu01_ll_iu", "target": "cu01_ll_iu", "value": "2: validar_formato_campo(nombre, valor)", "style": s["self_call"], "exitX": 0.5, "exitY": round((195 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((218 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_03", "source": "cu01_ll_iu", "target": "cu01_ll_routes", "value": "3: POST /api/auth/registro(dto_registro)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((260 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((260 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_04", "source": "cu01_ll_routes", "target": "cu01_ll_services", "value": "4: registrar_cliente(dto_registro)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((295 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((295 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_05", "source": "cu01_ll_services", "target": "cu01_ll_security", "value": "5: validar_politica_password(password)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((330 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((330 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_06", "source": "cu01_ll_security", "target": "cu01_ll_services", "value": "6: return bool_password_valido", "style": s["return"], "exitX": 0.5, "exitY": round((358 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((358 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_07", "source": "cu01_ll_services", "target": "cu01_ll_repos", "value": "7: buscar_por_email(email)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((390 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((390 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_08", "source": "cu01_ll_repos", "target": "cu01_ll_services", "value": "8: return usuario_existente", "style": s["return"], "exitX": 0.5, "exitY": round((418 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((418 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu01_09", "source": "cu01_ll_services", "target": "cu01_ll_security", "value": "9: generar_hash_password(password)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((480 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_10", "source": "cu01_ll_security", "target": "cu01_ll_services", "value": "10: return password_hash", "style": s["return"], "exitX": 0.5, "exitY": round((508 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((508 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_11", "source": "cu01_ll_services", "target": "cu01_ll_repos", "value": "11: insertar_usuario(datos_usuario, password_hash)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((540 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((540 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_12", "source": "cu01_ll_repos", "target": "cu01_ll_services", "value": "12: return nuevo_usuario", "style": s["return"], "exitX": 0.5, "exitY": round((568 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((568 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_13", "source": "cu01_ll_services", "target": "cu01_ll_repos", "value": "13: asignar_rol(id_usuario, ROL_CLIENTE)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((600 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((600 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_14", "source": "cu01_ll_repos", "target": "cu01_ll_services", "value": "14: return bool_rol_asignado", "style": s["return"], "exitX": 0.5, "exitY": round((628 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((628 - y_start_box) / h_box, 5)},

        # opt
        {"id": "e_cu01_15", "source": "cu01_ll_services", "target": "cu01_ll_repos", "value": "15: registrar_dispositivo(id_usuario, huella_dispositivo)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((688 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((688 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_16", "source": "cu01_ll_repos", "target": "cu01_ll_services", "value": "16: return bool_dispositivo_ok", "style": s["return"], "exitX": 0.5, "exitY": round((716 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((716 - y_start_box) / h_box, 5)},

        {"id": "e_cu01_17", "source": "cu01_ll_services", "target": "cu01_ll_security", "value": "17: generar_token_jwt(id_usuario, ROL_CLIENTE)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((760 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((760 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_18", "source": "cu01_ll_security", "target": "cu01_ll_services", "value": "18: return jwt_token", "style": s["return"], "exitX": 0.5, "exitY": round((788 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((788 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_19", "source": "cu01_ll_services", "target": "cu01_ll_bitacora", "value": "19: registrar_bitacora(ACCION_REGISTRO, id_usuario)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((818 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((818 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_20", "source": "cu01_ll_services", "target": "cu01_ll_routes", "value": "20: return respuesta_exitosa(nuevo_usuario, jwt_token)", "style": s["return"], "exitX": 0.5, "exitY": round((845 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((845 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_21", "source": "cu01_ll_routes", "target": "cu01_ll_iu", "value": "21: HTTP 201 Created (jwt_token, usuario)", "style": s["return"], "exitX": 0.5, "exitY": round((870 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((870 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_22", "source": "cu01_ll_iu", "target": "cu01_ll_cliente", "value": "22: renderizar_bienvenida_sesion_activa()", "style": s["return"], "exitX": 0.5, "exitY": round((892 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((892 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu01_23", "source": "cu01_ll_services", "target": "cu01_ll_routes", "value": "23: throw ConflictException(\"EMAIL_DUPLICADO\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((940 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((940 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_24", "source": "cu01_ll_routes", "target": "cu01_ll_iu", "value": "24: HTTP 409 Conflict (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((965 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((965 - y_start_box) / h_box, 5)},
        {"id": "e_cu01_25", "source": "cu01_ll_iu", "target": "cu01_ll_cliente", "value": "25: mostrar_alerta_cuenta_existente()", "style": s["return_error"], "exitX": 0.5, "exitY": round((990 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((990 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu01_sec", "name": "CU01 - Registrar usuario (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU02: Iniciar sesión
# ==============================================================================
def build_cu02_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 980
    y_start_box = 75
    h_box = 965

    nodes = [
        {"id": "frame_main_cu02", "value": "<b>sd</b> CU02 — Iniciar sesión (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1050},
        {"id": "cu02_ll_usuario", "value": "<b>Usuario</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu02_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Login</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu02_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:auth_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu02_ll_services", "value": "&laquo;control&raquo;<br/><b>:auth_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu02_ll_security", "value": "&laquo;control&raquo;<br/><b>:security_service</b>", "style": s["lifeline_box"], "x": 880, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu02_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:usuario_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu02_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu02_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 880},
        {"id": "cu02_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 250, "w": 12, "h": 630},
        {"id": "cu02_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 940, "w": 12, "h": 40},
        {"id": "cu02_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 280, "w": 12, "h": 580},
        {"id": "cu02_act_services_2", "value": "", "style": s["activation"], "x": 716, "y": 930, "w": 12, "h": 20},
        {"id": "cu02_act_security_1", "value": "", "style": s["activation"], "x": 936, "y": 380, "w": 12, "h": 30},
        {"id": "cu02_act_security_2", "value": "", "style": s["activation"], "x": 936, "y": 750, "w": 12, "h": 30},
        {"id": "cu02_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 315, "w": 12, "h": 30},
        {"id": "cu02_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 480, "w": 12, "h": 30},
        {"id": "cu02_act_repos_3", "value": "", "style": s["activation"], "x": 1154, "y": 660, "w": 12, "h": 30},
        {"id": "cu02_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 800, "w": 12, "h": 30},

        # loop validación credenciales
        {"id": "cu02_frag_loop", "value": "<b>loop</b>", "style": s["frame_operator"], "x": 210, "y": 155, "w": 200, "h": 70},
        {"id": "cu02_lbl_loop", "value": "[para cada campo credencial]", "style": s["guard_label"], "x": 280, "y": 158, "w": 160, "h": 20},

        # alt principal de autenticación
        {"id": "cu02_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 435, "w": 1430, "h": 590},
        {"id": "cu02_lbl_alt1", "value": "[usuario != null &amp;&amp; password_valido == true &amp;&amp; !bloqueado] (Curso Básico: Login Exitoso)", "style": s["guard_label"], "x": 115, "y": 440, "w": 550, "h": 20},

        # opt verificación dispositivo
        {"id": "cu02_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 525, "w": 570, "h": 90},
        {"id": "cu02_lbl_opt", "value": "[dispositivo_no_reconocido == true] (Desafío MFA / OTP)", "style": s["guard_label"], "x": 720, "y": 530, "w": 380, "h": 20},

        {"id": "cu02_divider", "value": "", "style": s["divider"], "x": 45, "y": 910, "w": 1430, "h": 1},
        {"id": "cu02_lbl_alt2", "value": "[else: password_invalido || cuenta_bloqueada] (Curso Alterno: Fallo o Bloqueo 15 min)", "style": s["guard_label"], "x": 55, "y": 913, "w": 580, "h": 20}
    ]

    edges = [
        {"id": "e_cu02_01", "source": "cu02_ll_usuario", "target": "cu02_ll_iu", "value": "1: ingresar_credenciales(username, password)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_02", "source": "cu02_ll_iu", "target": "cu02_ll_iu", "value": "2: validar_formato_credenciales()", "style": s["self_call"], "exitX": 0.5, "exitY": round((185 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((208 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_03", "source": "cu02_ll_iu", "target": "cu02_ll_routes", "value": "3: POST /api/auth/login(credenciales)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((250 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((250 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_04", "source": "cu02_ll_routes", "target": "cu02_ll_services", "value": "4: autenticar_usuario(credenciales)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((280 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((280 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_05", "source": "cu02_ll_services", "target": "cu02_ll_repos", "value": "5: buscar_por_identificador(login_id)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((315 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((315 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_06", "source": "cu02_ll_repos", "target": "cu02_ll_services", "value": "6: return usuario_seguridad", "style": s["return"], "exitX": 0.5, "exitY": round((345 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((345 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_07", "source": "cu02_ll_services", "target": "cu02_ll_security", "value": "7: verificar_hash_password(password, hash)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((380 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((380 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_08", "source": "cu02_ll_security", "target": "cu02_ll_services", "value": "8: return bool_password_valido", "style": s["return"], "exitX": 0.5, "exitY": round((410 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((410 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu02_09", "source": "cu02_ll_services", "target": "cu02_ll_repos", "value": "9: restablecer_intentos_fallidos(id_usuario)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((480 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_10", "source": "cu02_ll_repos", "target": "cu02_ll_services", "value": "10: return bool_reset_ok", "style": s["return"], "exitX": 0.5, "exitY": round((505 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((505 - y_start_box) / h_box, 5)},

        # opt
        {"id": "e_cu02_11", "source": "cu02_ll_services", "target": "cu02_ll_security", "value": "11: generar_desafio_otp(id_usuario)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((555 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((555 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_12", "source": "cu02_ll_security", "target": "cu02_ll_services", "value": "12: return codigo_otp_generado", "style": s["return"], "exitX": 0.5, "exitY": round((585 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((585 - y_start_box) / h_box, 5)},

        {"id": "e_cu02_13", "source": "cu02_ll_services", "target": "cu02_ll_repos", "value": "13: cargar_contexto_rbac_y_sucursales(id_usuario)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((660 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((660 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_14", "source": "cu02_ll_repos", "target": "cu02_ll_services", "value": "14: return contexto_rbac (roles, permisos, sucursales)", "style": s["return"], "exitX": 0.5, "exitY": round((690 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((690 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_15", "source": "cu02_ll_services", "target": "cu02_ll_security", "value": "15: generar_token_jwt(id_usuario, contexto_rbac)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((750 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((750 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_16", "source": "cu02_ll_security", "target": "cu02_ll_services", "value": "16: return jwt_token", "style": s["return"], "exitX": 0.5, "exitY": round((775 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((775 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_17", "source": "cu02_ll_services", "target": "cu02_ll_bitacora", "value": "17: registrar_bitacora(LOGIN_EXITOSO, id_usuario)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((800 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((800 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_18", "source": "cu02_ll_services", "target": "cu02_ll_routes", "value": "18: return sesion_exitosa(jwt_token, contexto_rbac)", "style": s["return"], "exitX": 0.5, "exitY": round((830 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((830 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_19", "source": "cu02_ll_routes", "target": "cu02_ll_iu", "value": "19: HTTP 200 OK (jwt_token, contexto)", "style": s["return"], "exitX": 0.5, "exitY": round((855 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((855 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_20", "source": "cu02_ll_iu", "target": "cu02_ll_usuario", "value": "20: renderizar_menu_principal()", "style": s["return"], "exitX": 0.5, "exitY": round((880 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((880 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu02_21", "source": "cu02_ll_services", "target": "cu02_ll_routes", "value": "21: throw UnauthorizedException(\"CREDENCIALES_INVALIDAS\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((935 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((935 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_22", "source": "cu02_ll_routes", "target": "cu02_ll_iu", "value": "22: HTTP 401 Unauthorized (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((960 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((960 - y_start_box) / h_box, 5)},
        {"id": "e_cu02_23", "source": "cu02_ll_iu", "target": "cu02_ll_usuario", "value": "23: mostrar_alerta_error_credenciales()", "style": s["return_error"], "exitX": 0.5, "exitY": round((985 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((985 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu02_sec", "name": "CU02 - Iniciar sesión (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU03: Gestionar perfil
# ==============================================================================
def build_cu03_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 960
    y_start_box = 75
    h_box = 945

    nodes = [
        {"id": "frame_main_cu03", "value": "<b>sd</b> CU03 — Gestionar perfil (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1030},
        {"id": "cu03_ll_usuario", "value": "<b>Usuario</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu03_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_Perfil</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu03_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:perfil_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu03_ll_services", "value": "&laquo;control&raquo;<br/><b>:perfil_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu03_ll_security", "value": "&laquo;control&raquo;<br/><b>:security_service</b>", "style": s["lifeline_box"], "x": 880, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu03_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:usuario_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu03_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu03_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 130, "w": 12, "h": 870},
        {"id": "cu03_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 150, "w": 12, "h": 60},
        {"id": "cu03_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 320, "w": 12, "h": 570},
        {"id": "cu03_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 340, "w": 12, "h": 510},
        {"id": "cu03_act_security_1", "value": "", "style": s["activation"], "x": 936, "y": 480, "w": 12, "h": 30},
        {"id": "cu03_act_security_2", "value": "", "style": s["activation"], "x": 936, "y": 620, "w": 12, "h": 30},
        {"id": "cu03_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 170, "w": 12, "h": 30},
        {"id": "cu03_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 680, "w": 12, "h": 30},
        {"id": "cu03_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 790, "w": 12, "h": 30},

        # loop validación de contacto
        {"id": "cu03_frag_loop", "value": "<b>loop</b>", "style": s["frame_operator"], "x": 210, "y": 255, "w": 200, "h": 60},
        {"id": "cu03_lbl_loop", "value": "[para cada dato de contacto]", "style": s["guard_label"], "x": 280, "y": 258, "w": 160, "h": 20},

        # alt cambio password
        {"id": "cu03_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 440, "w": 1430, "h": 580},
        {"id": "cu03_lbl_alt1", "value": "[password_actual_valida == true &amp;&amp; datos_validos] (Curso Básico: Perfil Actualizado)", "style": s["guard_label"], "x": 115, "y": 445, "w": 520, "h": 20},

        # opt cambio de contraseña opcional
        {"id": "cu03_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 590, "w": 570, "h": 85},
        {"id": "cu03_lbl_opt", "value": "[solicita_nueva_password == true]", "style": s["guard_label"], "x": 720, "y": 595, "w": 250, "h": 20},

        {"id": "cu03_divider", "value": "", "style": s["divider"], "x": 45, "y": 890, "w": 1430, "h": 1},
        {"id": "cu03_lbl_alt2", "value": "[else: password_actual_invalida || formato_invalido] (Curso Alterno: Rechazo)", "style": s["guard_label"], "x": 55, "y": 893, "w": 550, "h": 20}
    ]

    edges = [
        {"id": "e_cu03_01", "source": "cu03_ll_usuario", "target": "cu03_ll_iu", "value": "1: solicitar_ver_perfil()", "style": s["sync_call"], "exitX": 0.5, "exitY": round((130 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((130 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_02", "source": "cu03_ll_iu", "target": "cu03_ll_routes", "value": "2: GET /api/perfil/mi-cuenta", "style": s["sync_call"], "exitX": 0.5, "exitY": round((150 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((150 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_03", "source": "cu03_ll_routes", "target": "cu03_ll_repos", "value": "3: obtener_perfil_usuario(id_usuario)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((170 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((170 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_04", "source": "cu03_ll_repos", "target": "cu03_ll_routes", "value": "4: return datos_perfil", "style": s["return"], "exitX": 0.5, "exitY": round((195 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((195 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_05", "source": "cu03_ll_routes", "target": "cu03_ll_iu", "value": "5: renderizar_formulario_perfil(datos)", "style": s["return"], "exitX": 0.5, "exitY": round((215 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((215 - y_start_box) / h_box, 5)},

        # loop
        {"id": "e_cu03_06", "source": "cu03_ll_iu", "target": "cu03_ll_iu", "value": "6: validar_formato_contacto(campo, valor)", "style": s["self_call"], "exitX": 0.5, "exitY": round((275 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((298 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_07", "source": "cu03_ll_iu", "target": "cu03_ll_routes", "value": "7: PUT /api/perfil/actualizar(dto_perfil)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((320 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((320 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_08", "source": "cu03_ll_routes", "target": "cu03_ll_services", "value": "8: actualizar_perfil(id_usuario, dto_perfil)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((345 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((345 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_09", "source": "cu03_ll_services", "target": "cu03_ll_security", "value": "9: verificar_password_actual(id_usuario, pwd_actual)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((480 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_010", "source": "cu03_ll_security", "target": "cu03_ll_services", "value": "10: return bool_pwd_valida", "style": s["return"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},

        # opt
        {"id": "e_cu03_011", "source": "cu03_ll_services", "target": "cu03_ll_security", "value": "11: generar_hash_password(nueva_password)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((620 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((620 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_012", "source": "cu03_ll_security", "target": "cu03_ll_services", "value": "12: return nuevo_hash", "style": s["return"], "exitX": 0.5, "exitY": round((650 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((650 - y_start_box) / h_box, 5)},

        {"id": "e_cu03_013", "source": "cu03_ll_services", "target": "cu03_ll_repos", "value": "13: actualizar_datos_usuario(id_usuario, telefono, dir, hash)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((680 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((680 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_014", "source": "cu03_ll_repos", "target": "cu03_ll_services", "value": "14: return bool_actualizado", "style": s["return"], "exitX": 0.5, "exitY": round((710 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((710 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_015", "source": "cu03_ll_services", "target": "cu03_ll_bitacora", "value": "15: registrar_bitacora(ACTUALIZAR_PERFIL, id_usuario)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((790 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((790 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_016", "source": "cu03_ll_services", "target": "cu03_ll_routes", "value": "16: return respuesta_perfil_actualizado()", "style": s["return"], "exitX": 0.5, "exitY": round((820 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((820 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_017", "source": "cu03_ll_routes", "target": "cu03_ll_iu", "value": "17: HTTP 200 OK (datos_actualizados)", "style": s["return"], "exitX": 0.5, "exitY": round((845 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((845 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_018", "source": "cu03_ll_iu", "target": "cu03_ll_usuario", "value": "18: mostrar_confirmacion_actualizacion()", "style": s["return"], "exitX": 0.5, "exitY": round((868 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((868 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu03_019", "source": "cu03_ll_services", "target": "cu03_ll_routes", "value": "19: throw BadRequestException(\"PASSWORD_ACTUAL_INCORRECTA\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((920 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((920 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_020", "source": "cu03_ll_routes", "target": "cu03_ll_iu", "value": "20: HTTP 400 Bad Request (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu03_021", "source": "cu03_ll_iu", "target": "cu03_ll_usuario", "value": "21: mostrar_alerta_password_incorrecta()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu03_sec", "name": "CU03 - Gestionar perfil (Secuencia)", "nodes": nodes, "edges": edges}

# ==============================================================================
# CU14: Gestionar usuarios y roles
# ==============================================================================
def build_cu14_spec():
    s = get_common_sequence_styles()
    y_start_actor = 60
    h_actor = 980
    y_start_box = 75
    h_box = 965

    nodes = [
        {"id": "frame_main_cu14", "value": "<b>sd</b> CU14 — Gestionar usuarios y roles (ICONIX / UML 2.5)", "style": s["frame_main"], "x": 25, "y": 20, "w": 1470, "h": 1050},
        {"id": "cu14_ll_admin", "value": "<b>Administrador</b>", "style": s["lifeline_actor"], "x": 60, "y": y_start_actor, "w": 60, "h": h_actor},
        {"id": "cu14_ll_iu", "value": "&laquo;boundary&raquo;<br/><b>:IU_UsuariosRoles</b>", "style": s["lifeline_box"], "x": 230, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu14_ll_routes", "value": "&laquo;boundary&raquo;<br/><b>:usuarios_routes</b>", "style": s["lifeline_box"], "x": 440, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu14_ll_services", "value": "&laquo;control&raquo;<br/><b>:usuarios_services</b>", "style": s["lifeline_box"], "x": 660, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu14_ll_security", "value": "&laquo;control&raquo;<br/><b>:security_service</b>", "style": s["lifeline_box"], "x": 880, "y": y_start_box, "w": 125, "h": h_box},
        {"id": "cu14_ll_repos", "value": "&laquo;entity&raquo;<br/><b>:usuario_repos</b>", "style": s["lifeline_box"], "x": 1100, "y": y_start_box, "w": 120, "h": h_box},
        {"id": "cu14_ll_bitacora", "value": "&laquo;entity&raquo;<br/><b>:bitacora_repos</b>", "style": s["lifeline_box"], "x": 1310, "y": y_start_box, "w": 120, "h": h_box},

        {"id": "cu14_act_iu", "value": "", "style": s["activation"], "x": 284, "y": 135, "w": 12, "h": 870},
        {"id": "cu14_act_routes_1", "value": "", "style": s["activation"], "x": 494, "y": 240, "w": 12, "h": 620},
        {"id": "cu14_act_routes_2", "value": "", "style": s["activation"], "x": 494, "y": 925, "w": 12, "h": 40},
        {"id": "cu14_act_services_1", "value": "", "style": s["activation"], "x": 716, "y": 270, "w": 12, "h": 570},
        {"id": "cu14_act_security_1", "value": "", "style": s["activation"], "x": 936, "y": 480, "w": 12, "h": 30},
        {"id": "cu14_act_repos_1", "value": "", "style": s["activation"], "x": 1154, "y": 370, "w": 12, "h": 30},
        {"id": "cu14_act_repos_2", "value": "", "style": s["activation"], "x": 1154, "y": 540, "w": 12, "h": 30},
        {"id": "cu14_act_repos_3", "value": "", "style": s["activation"], "x": 1154, "y": 600, "w": 12, "h": 30},
        {"id": "cu14_act_repos_4", "value": "", "style": s["activation"], "x": 1154, "y": 690, "w": 12, "h": 30},
        {"id": "cu14_act_bitacora", "value": "", "style": s["activation"], "x": 1364, "y": 790, "w": 12, "h": 30},

        # loop sucursales
        {"id": "cu14_frag_loop", "value": "<b>loop</b>", "style": s["frame_operator"], "x": 650, "y": 660, "w": 570, "h": 75},
        {"id": "cu14_lbl_loop", "value": "[para cada id_sucursal en lista_asignaciones]", "style": s["guard_label"], "x": 720, "y": 665, "w": 320, "h": 20},

        # alt validación y unicidad
        {"id": "cu14_frag_alt", "value": "<b>alt</b>", "style": s["frame_operator"], "x": 45, "y": 435, "w": 1430, "h": 585},
        {"id": "cu14_lbl_alt1", "value": "[email_unico == true &amp;&amp; misma_empresa == true] (Curso Básico: Usuario Guardado)", "style": s["guard_label"], "x": 115, "y": 440, "w": 520, "h": 20},

        # opt desactivar cuenta
        {"id": "cu14_frag_opt", "value": "<b>opt</b>", "style": s["frame_operator"], "x": 650, "y": 745, "w": 570, "h": 50},
        {"id": "cu14_lbl_opt", "value": "[solicita_desactivar == true] (activo = false)", "style": s["guard_label"], "x": 720, "y": 750, "w": 280, "h": 20},

        {"id": "cu14_divider", "value": "", "style": s["divider"], "x": 45, "y": 895, "w": 1430, "h": 1},
        {"id": "cu14_lbl_alt2", "value": "[else: email_duplicado || traslado_empresa_invalido] (Curso Alterno: Rechazo 409/403)", "style": s["guard_label"], "x": 55, "y": 898, "w": 600, "h": 20}
    ]

    edges = [
        {"id": "e_cu14_01", "source": "cu14_ll_admin", "target": "cu14_ll_iu", "value": "1: ingresar_datos_usuario(nombre, email, rol, sucursales)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((135 - y_start_actor) / h_actor, 5), "entryX": 0.5, "entryY": round((135 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_02", "source": "cu14_ll_iu", "target": "cu14_ll_routes", "value": "2: POST /api/usuarios(dto_usuario)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((240 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((240 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_03", "source": "cu14_ll_routes", "target": "cu14_ll_services", "value": "3: guardar_usuario_empresa(id_empresa, dto_usuario)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((270 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((270 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_04", "source": "cu14_ll_services", "target": "cu14_ll_services", "value": "4: validar_jerarquia_y_empresa(actor, id_empresa)", "style": s["self_call"], "exitX": 0.5, "exitY": round((310 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((335 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_05", "source": "cu14_ll_services", "target": "cu14_ll_repos", "value": "5: buscar_duplicado_email(email)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((370 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((370 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_06", "source": "cu14_ll_repos", "target": "cu14_ll_services", "value": "6: return usuario_existente", "style": s["return"], "exitX": 0.5, "exitY": round((400 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((400 - y_start_box) / h_box, 5)},

        # Básico
        {"id": "e_cu14_07", "source": "cu14_ll_services", "target": "cu14_ll_security", "value": "7: generar_hash_password(password)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((480 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((480 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_08", "source": "cu14_ll_security", "target": "cu14_ll_services", "value": "8: return password_hash", "style": s["return"], "exitX": 0.5, "exitY": round((510 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((510 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_09", "source": "cu14_ll_services", "target": "cu14_ll_repos", "value": "9: insertar_usuario_transaccional(datos, hash, id_empresa)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((540 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((540 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_10", "source": "cu14_ll_repos", "target": "cu14_ll_services", "value": "10: return id_usuario_creado", "style": s["return"], "exitX": 0.5, "exitY": round((570 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((570 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_11", "source": "cu14_ll_services", "target": "cu14_ll_repos", "value": "11: asignar_rol_usuario(id_usuario, id_rol)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((600 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((600 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_12", "source": "cu14_ll_repos", "target": "cu14_ll_services", "value": "12: return bool_rol_ok", "style": s["return"], "exitX": 0.5, "exitY": round((625 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((625 - y_start_box) / h_box, 5)},

        # loop
        {"id": "e_cu14_13", "source": "cu14_ll_services", "target": "cu14_ll_repos", "value": "13: vincular_sucursal_usuario(id_usuario, id_sucursal)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((690 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((690 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_14", "source": "cu14_ll_repos", "target": "cu14_ll_services", "value": "14: return bool_vinculo_ok", "style": s["return"], "exitX": 0.5, "exitY": round((715 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((715 - y_start_box) / h_box, 5)},

        {"id": "e_cu14_15", "source": "cu14_ll_services", "target": "cu14_ll_bitacora", "value": "15: registrar_bitacora(GESTION_USUARIO_ROL, id_usuario)", "style": s["sync_call"], "exitX": 0.5, "exitY": round((790 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((790 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_16", "source": "cu14_ll_services", "target": "cu14_ll_routes", "value": "16: return usuario_creado(id_usuario, email, rol)", "style": s["return"], "exitX": 0.5, "exitY": round((820 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((820 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_17", "source": "cu14_ll_routes", "target": "cu14_ll_iu", "value": "17: HTTP 201 Created (usuario_guardado)", "style": s["return"], "exitX": 0.5, "exitY": round((845 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((845 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_18", "source": "cu14_ll_iu", "target": "cu14_ll_admin", "value": "18: actualizar_tabla_usuarios()", "style": s["return"], "exitX": 0.5, "exitY": round((870 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((870 - y_start_actor) / h_actor, 5)},

        # Alterno
        {"id": "e_cu14_19", "source": "cu14_ll_services", "target": "cu14_ll_routes", "value": "19: throw ConflictException(\"USUARIO_DUPLICADO\")", "style": s["return_error"], "exitX": 0.5, "exitY": round((925 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((925 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_20", "source": "cu14_ll_routes", "target": "cu14_ll_iu", "value": "20: HTTP 409 Conflict (detalle_error)", "style": s["return_error"], "exitX": 0.5, "exitY": round((950 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((950 - y_start_box) / h_box, 5)},
        {"id": "e_cu14_21", "source": "cu14_ll_iu", "target": "cu14_ll_admin", "value": "21: mostrar_alerta_error_duplicado()", "style": s["return_error"], "exitX": 0.5, "exitY": round((975 - y_start_box) / h_box, 5), "entryX": 0.5, "entryY": round((975 - y_start_actor) / h_actor, 5)}
    ]

    return {"id": "diag_cu14_sec", "name": "CU14 - Gestionar usuarios y roles (Secuencia)", "nodes": nodes, "edges": edges}
