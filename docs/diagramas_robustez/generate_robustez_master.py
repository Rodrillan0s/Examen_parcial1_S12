#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro Unificado de Diagramas de Robustez (ICONIX / UML 2.5) en formato Draw.io (.drawio / .xml)
Estilo riguroso Doug Rosenberg (ICONIX Process):
- Panel izquierdo con especificación textual formal (BASIC COURSE y ALTERNATE COURSES).
- Grafo con artefactos nativos UML 2.5 (Actor, Boundary, Control, Entity).
- Cursos alternativos y pantallas de excepción resaltadas en ROJO (#ea4335, stroke #b91c1c).
- Distribución espacial con amplias distancias (sin solapamiento de cajas, etiquetas ni líneas).
- Archivo UNIFICADO multitab: un solo archivo .drawio con pestañas para los 16 Casos de Uso del sistema AuroraStore.
"""

import os
import html
import xml.etree.ElementTree as ET

def get_common_styles():
    style_note = (
        "shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;size=22;fillColor=#ffffff;"
        "strokeColor=#1e293b;strokeWidth=1.6;fontFamily=Arial;fontSize=11.5;fontColor=#0f172a;"
        "align=left;verticalAlign=top;spacingLeft=14;spacingRight=14;spacingTop=16;lineHeight=1.4;"
    )
    style_actor = (
        "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
        "outlineConnect=0;fillColor=#ffffff;strokeColor=#1e293b;strokeWidth=1.8;"
        "fontFamily=Arial;fontSize=11.5;fontStyle=1;fontColor=#0f172a;"
    )
    style_boundary = (
        "shape=umlBoundary;whiteSpace=wrap;html=1;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;fillColor=#ffffff;strokeColor=#1e293b;strokeWidth=1.8;"
        "fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#0f172a;"
    )
    style_control = (
        "shape=umlControl;whiteSpace=wrap;html=1;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;fillColor=#ffffff;strokeColor=#1e293b;strokeWidth=1.8;"
        "fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#0f172a;"
    )
    style_entity = (
        "shape=umlEntity;whiteSpace=wrap;html=1;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;fillColor=#ffffff;strokeColor=#1e293b;strokeWidth=1.8;"
        "fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#0f172a;"
    )

    # Estilos de cursos alternativos (ROJO ICONIX según el estándar docente)
    style_boundary_alt = (
        "shape=umlBoundary;whiteSpace=wrap;html=1;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;fillColor=#ea4335;strokeColor=#b91c1c;strokeWidth=2;"
        "fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#991b1b;"
    )
    style_control_alt = (
        "shape=umlControl;whiteSpace=wrap;html=1;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;fillColor=#ea4335;strokeColor=#b91c1c;strokeWidth=2;"
        "fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#991b1b;"
    )

    # Estilos de líneas
    style_edge = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
        "strokeColor=#334155;strokeWidth=1.5;endArrow=classic;endFill=1;endSize=6;fontFamily=Arial;"
        "fontSize=10;fontColor=#1e293b;labelBackgroundColor=#ffffff;labelBorderColor=#cbd5e1;"
    )
    style_edge_alt = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
        "dashed=1;strokeColor=#dc2626;strokeWidth=1.6;endArrow=classic;endFill=1;endSize=6;fontFamily=Arial;"
        "fontSize=10;fontColor=#991b1b;labelBackgroundColor=#ffffff;labelBorderColor=#fca5a5;"
    )

    return {
        "note": style_note,
        "actor": style_actor,
        "boundary": style_boundary,
        "control": style_control,
        "entity": style_entity,
        "boundary_alt": style_boundary_alt,
        "control_alt": style_control_alt,
        "edge": style_edge,
        "edge_alt": style_edge_alt
    }

# ==============================================================================
# 1. CU01W / CU01M: Registrar usuario (P1)
# ==============================================================================
def build_cu01_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Cliente accede a la página de registro del portal web o aplicación móvil.<br/><br/>"
        "2. El sistema despliega el formulario de registro solicitando datos personales (nombre, apellido, teléfono), "
        "correo electrónico, contraseña, confirmación de contraseña y aceptación de términos.<br/><br/>"
        "3. El Cliente ingresa sus datos y presiona el botón 'Registrarse'.<br/><br/>"
        "4. El sistema valida que los campos requeridos no estén vacíos y que las contraseñas coincidan con las políticas de seguridad.<br/><br/>"
        "5. El sistema consulta la base de datos para verificar que el correo electrónico o nombre de usuario no existan previamente.<br/><br/>"
        "6. El sistema genera el hash seguro de contraseña (Bcrypt), crea la cuenta en t_usuario con rol CLIENTE, "
        "registra el dispositivo inicial y emite el token JWT de sesión.<br/><br/>"
        "7. El sistema registra el evento de auditoría en t_bitacora y redirige al Cliente a la página de bienvenida con la sesión activa.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Datos inválidos o contraseñas no coinciden:</b><br/>"
        "El sistema despliega la página/alerta de error de validación detallando los campos a corregir.<br/><br/>"
        "• <b>Correo o usuario ya registrado:</b><br/>"
        "El sistema detecta duplicidad en t_usuario y despliega la página de cuenta existente ofreciendo iniciar sesión o recuperar contraseña."
    )

    nodes = [
        {"id": "cu01_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu01_act_cliente", "value": "Cliente", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu01_bnd_registro", "value": "Página de Registro", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu01_ctrl_validar", "value": "Validar datos", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu01_ctrl_verificar", "value": "Verificar disponibilidad", "style": s["control"], "x": 1140, "y": 145, "w": 75, "h": 75},
        {"id": "cu01_ent_usuario", "value": "t_usuario", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu01_ctrl_crear", "value": "Crear cuenta de cliente", "style": s["control"], "x": 1020, "y": 370, "w": 75, "h": 75},
        {"id": "cu01_ent_rol", "value": "t_usuario_rol / t_rol", "style": s["entity"], "x": 1440, "y": 320, "w": 80, "h": 75},
        {"id": "cu01_ent_dispositivo", "value": "t_dispositivo_usuario", "style": s["entity"], "x": 1440, "y": 430, "w": 80, "h": 75},
        {"id": "cu01_ctrl_bitacora", "value": "Registrar auditoría", "style": s["control"], "x": 1020, "y": 550, "w": 75, "h": 75},
        {"id": "cu01_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu01_ctrl_token", "value": "Generar token acceso", "style": s["control"], "x": 760, "y": 370, "w": 75, "h": 75},
        {"id": "cu01_bnd_bienvenida", "value": "Página de Bienvenida", "style": s["boundary"], "x": 520, "y": 370, "w": 80, "h": 75},
        {"id": "cu01_ctrl_err_val", "value": "Mostrar error validación", "style": s["control_alt"], "x": 760, "y": 740, "w": 75, "h": 75},
        {"id": "cu01_bnd_err_val", "value": "Página Error Validación", "style": s["boundary_alt"], "x": 520, "y": 740, "w": 80, "h": 75},
        {"id": "cu01_ctrl_err_dup", "value": "Mostrar cuenta existente", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu01_bnd_err_dup", "value": "Página Cuenta Existente", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu01_01", "source": "cu01_act_cliente", "target": "cu01_bnd_registro", "value": "ingresar datos y enviar", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu01_02", "source": "cu01_bnd_registro", "target": "cu01_ctrl_validar", "value": "solicitar registro", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu01_03", "source": "cu01_ctrl_validar", "target": "cu01_ctrl_verificar", "value": "datos sintácticamente válidos", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu01_04", "source": "cu01_ctrl_verificar", "target": "cu01_ent_usuario", "value": "consultar email y username", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu01_05", "source": "cu01_ctrl_verificar", "target": "cu01_ctrl_crear", "value": "disponibilidad confirmada", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu01_06", "source": "cu01_ctrl_crear", "target": "cu01_ent_usuario", "value": "insertar registro con Bcrypt", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.8},
        {"id": "e_cu01_07", "source": "cu01_ctrl_crear", "target": "cu01_ent_rol", "value": "asignar rol CLIENTE", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu01_08", "source": "cu01_ctrl_crear", "target": "cu01_ent_dispositivo", "value": "registrar huella dispositivo", "style": s["edge"], "exitX": 1.0, "exitY": 0.7, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu01_09", "source": "cu01_ctrl_crear", "target": "cu01_ctrl_bitacora", "value": "usuario creado con éxito", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu01_10", "source": "cu01_ctrl_bitacora", "target": "cu01_ent_bitacora", "value": "guardar log auditoría", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu01_11", "source": "cu01_ctrl_crear", "target": "cu01_ctrl_token", "value": "solicitar credenciales activas", "style": s["edge"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu01_12", "source": "cu01_ctrl_token", "target": "cu01_bnd_bienvenida", "value": "redirigir con sesión activa", "style": s["edge"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu01_13", "source": "cu01_bnd_bienvenida", "target": "cu01_act_cliente", "value": "mostrar confirmación", "style": s["edge"], "exitX": 0.5, "exitY": 0.0, "entryX": 0.8, "entryY": 1.0},
        {"id": "e_cu01_14", "source": "cu01_ctrl_validar", "target": "cu01_ctrl_err_val", "value": "campos vacíos o contraseñas no coinciden", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu01_15", "source": "cu01_ctrl_err_val", "target": "cu01_bnd_err_val", "value": "mostrar errores detectados", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu01_16", "source": "cu01_bnd_err_val", "target": "cu01_act_cliente", "value": "solicitar corrección", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 0.5, "entryY": 1.0},
        {"id": "e_cu01_17", "source": "cu01_ctrl_verificar", "target": "cu01_ctrl_err_dup", "value": "email o username ya existen", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu01_18", "source": "cu01_ctrl_err_dup", "target": "cu01_bnd_err_dup", "value": "presentar aviso de cuenta existente", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu01_19", "source": "cu01_bnd_err_dup", "target": "cu01_act_cliente", "value": "ofrecer inicio sesión o recuperación", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 0.3, "entryY": 1.0}
    ]

    return {"id": "diag_cu01", "name": "CU01 - Registrar usuario", "nodes": nodes, "edges": edges}

# ==============================================================================
# 2. CU02W / CU02M: Iniciar sesión (P1)
# ==============================================================================
def build_cu02_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Usuario accede a la pantalla de inicio de sesión del sistema.<br/><br/>"
        "2. El sistema despliega el formulario solicitando correo/nombre de usuario y contraseña.<br/><br/>"
        "3. El Usuario ingresa sus credenciales y presiona 'Ingresar'.<br/><br/>"
        "4. El sistema valida el formato de entrada y busca la cuenta en la tabla t_usuario.<br/><br/>"
        "5. El sistema consulta t_seguridad_usuario para verificar que la cuenta no se encuentre bloqueada por intentos fallidos.<br/><br/>"
        "6. El sistema compara el hash seguro Bcrypt de la contraseña ingresada con el almacenado.<br/><br/>"
        "7. El sistema verifica el dispositivo en t_dispositivo_usuario y restablece el contador de intentos fallidos a 0.<br/><br/>"
        "8. El sistema consulta t_usuario_rol, t_rol, t_permiso y t_usuario_sucursal para cargar el contexto de seguridad RBAC.<br/><br/>"
        "9. El sistema genera el token JWT con los claims de sesión, registra auditoría en t_bitacora y redirige a la Página Principal.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Credenciales incorrectas o cuenta bloqueada:</b><br/>"
        "El sistema incrementa los intentos fallidos en t_seguridad_usuario; al 3er fallo bloquea la cuenta por 15 min y muestra la Página de Error / Bloqueo.<br/><br/>"
        "• <b>Dispositivo no reconocido / MFA:</b><br/>"
        "El sistema detecta una nueva huella digital de dispositivo y despliega la Página de Verificación de Dispositivo solicitando el código OTP."
    )

    nodes = [
        {"id": "cu02_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu02_act_usuario", "value": "Usuario", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu02_bnd_login", "value": "Página Inicio de Sesión", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu02_ctrl_validar", "value": "Validar credenciales", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu02_ctrl_buscar", "value": "Buscar usuario y bloqueo", "style": s["control"], "x": 1140, "y": 145, "w": 75, "h": 75},
        {"id": "cu02_ent_usuario", "value": "t_usuario", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu02_ent_seguridad", "value": "t_seguridad_usuario", "style": s["entity"], "x": 1440, "y": 255, "w": 80, "h": 75},
        {"id": "cu02_ctrl_bcrypt", "value": "Verificar hash contraseña", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu02_ctrl_rbac", "value": "Cargar contexto RBAC y sucursales", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu02_ent_rol", "value": "t_usuario_rol / t_rol", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu02_ent_sucursal", "value": "t_usuario_sucursal / t_sucursal", "style": s["entity"], "x": 1440, "y": 475, "w": 80, "h": 75},
        {"id": "cu02_ctrl_token", "value": "Generar JWT y auditoría", "style": s["control"], "x": 620, "y": 370, "w": 75, "h": 75},
        {"id": "cu02_bnd_menu", "value": "Página Menú Principal", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu02_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 585, "w": 80, "h": 75},
        {"id": "cu02_ctrl_fallo", "value": "Gestionar fallo / bloqueo", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu02_bnd_error", "value": "Página Error / Bloqueo", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75},
        {"id": "cu02_ctrl_dispositivo", "value": "Verificar dispositivo nuevo", "style": s["control_alt"], "x": 620, "y": 740, "w": 75, "h": 75},
        {"id": "cu02_bnd_mfa", "value": "Página Verificación Dispositivo", "style": s["boundary_alt"], "x": 420, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu02_01", "source": "cu02_act_usuario", "target": "cu02_bnd_login", "value": "ingresar credenciales", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu02_02", "source": "cu02_bnd_login", "target": "cu02_ctrl_validar", "value": "solicitar autenticación", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu02_03", "source": "cu02_ctrl_validar", "target": "cu02_ctrl_buscar", "value": "formato correcto", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu02_04", "source": "cu02_ctrl_buscar", "target": "cu02_ent_usuario", "value": "obtener usuario y hash", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu02_05", "source": "cu02_ctrl_buscar", "target": "cu02_ent_seguridad", "value": "consultar intentos y estado bloqueo", "style": s["edge"], "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu02_06", "source": "cu02_ctrl_buscar", "target": "cu02_ctrl_bcrypt", "value": "cuenta activa y sin bloqueo", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu02_07", "source": "cu02_ctrl_bcrypt", "target": "cu02_ent_seguridad", "value": "restablecer intentos fallidos a 0", "style": s["edge"], "exitX": 1.0, "exitY": 0.2, "entryX": 0.0, "entryY": 0.8},
        {"id": "e_cu02_08", "source": "cu02_ctrl_bcrypt", "target": "cu02_ctrl_rbac", "value": "contraseña válida", "style": s["edge"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu02_09", "source": "cu02_ctrl_rbac", "target": "cu02_ent_rol", "value": "obtener roles y permisos", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu02_10", "source": "cu02_ctrl_rbac", "target": "cu02_ent_sucursal", "value": "obtener sucursales autorizadas", "style": s["edge"], "exitX": 1.0, "exitY": 0.7, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu02_11", "source": "cu02_ctrl_rbac", "target": "cu02_ctrl_token", "value": "contexto cargado", "style": s["edge"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu02_12", "source": "cu02_ctrl_token", "target": "cu02_ent_bitacora", "value": "registrar login exitoso", "style": s["edge"], "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu02_13", "source": "cu02_ctrl_token", "target": "cu02_bnd_menu", "value": "emitir JWT y redirigir", "style": s["edge"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu02_14", "source": "cu02_bnd_menu", "target": "cu02_act_usuario", "value": "mostrar menú del rol", "style": s["edge"], "exitX": 0.5, "exitY": 0.0, "entryX": 0.5, "entryY": 1.0},
        {"id": "e_cu02_15", "source": "cu02_ctrl_buscar", "target": "cu02_ctrl_fallo", "value": "usuario no existe o bloqueado", "style": s["edge_alt"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.7, "entryY": 0.0},
        {"id": "e_cu02_16", "source": "cu02_ctrl_bcrypt", "target": "cu02_ctrl_fallo", "value": "contraseña incorrecta", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu02_17", "source": "cu02_ctrl_fallo", "target": "cu02_ent_seguridad", "value": "incrementar intentos / bloquear", "style": s["edge_alt"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.2, "entryY": 1.0},
        {"id": "e_cu02_18", "source": "cu02_ctrl_fallo", "target": "cu02_bnd_error", "value": "mostrar alerta credenciales / bloqueo", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu02_19", "source": "cu02_ctrl_rbac", "target": "cu02_ctrl_dispositivo", "value": "huella digital no reconocida", "style": s["edge_alt"], "exitX": 0.2, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu02_20", "source": "cu02_ctrl_dispositivo", "target": "cu02_bnd_mfa", "value": "solicitar código OTP", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu02", "name": "CU02 - Iniciar sesión", "nodes": nodes, "edges": edges}

# ==============================================================================
# 3. CU03W / CU03M: Gestionar perfil (P1)
# ==============================================================================
def build_cu03_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Usuario autenticado accede a la opción 'Mi Perfil' desde el menú principal.<br/><br/>"
        "2. El sistema consulta t_usuario y t_cliente/t_empleado para recuperar datos personales (nombre, correo, teléfono, dirección).<br/><br/>"
        "3. El sistema despliega la Página Mi Perfil con la información actual y habilita la edición.<br/><br/>"
        "4. El Usuario modifica sus datos de contacto o solicita cambio de contraseña en el Formulario Edición Perfil.<br/><br/>"
        "5. El sistema valida el formato de teléfono, dirección y datos requeridos.<br/><br/>"
        "6. En caso de cambio de contraseña, el sistema verifica la contraseña actual contra t_usuario y genera el nuevo hash Bcrypt.<br/><br/>"
        "7. El sistema actualiza t_usuario, registra auditoría en t_bitacora y muestra la Página Confirmación Actualización.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Datos o formato de contacto inválidos:</b><br/>"
        "El sistema rechaza la edición y muestra la Página Error Validación Perfil.<br/><br/>"
        "• <b>Contraseña actual incorrecta:</b><br/>"
        "El sistema detecta discrepancia en el hash de la contraseña actual y despliega la Página Error Contraseña Actual."
    )

    nodes = [
        {"id": "cu03_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu03_act_usuario", "value": "Usuario Autenticado", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu03_bnd_perfil", "value": "Página Mi Perfil", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu03_ctrl_cargar", "value": "Cargar datos de perfil", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu03_ent_usuario", "value": "t_usuario", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu03_bnd_form", "value": "Formulario Edición Perfil", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu03_ctrl_validar", "value": "Validar datos y formato", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu03_ctrl_actualizar", "value": "Actualizar perfil y password", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu03_ent_seguridad", "value": "t_seguridad_usuario", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu03_ctrl_bitacora", "value": "Registrar auditoría perfil", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu03_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu03_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu03_ctrl_err_val", "value": "Mostrar error validación", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu03_bnd_err_val", "value": "Página Error Validación", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu03_ctrl_err_pwd", "value": "Mostrar error password", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu03_bnd_err_pwd", "value": "Página Error Password", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu03_01", "source": "cu03_act_usuario", "target": "cu03_bnd_perfil", "value": "solicitar ver perfil", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu03_02", "source": "cu03_bnd_perfil", "target": "cu03_ctrl_cargar", "value": "obtener datos personales", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu03_03", "source": "cu03_ctrl_cargar", "target": "cu03_ent_usuario", "value": "consultar registro usuario", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu03_04", "source": "cu03_ctrl_cargar", "target": "cu03_bnd_perfil", "value": "devolver datos actuales", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.8},
        {"id": "e_cu03_05", "source": "cu03_act_usuario", "target": "cu03_bnd_form", "value": "ingresar datos modificados", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu03_06", "source": "cu03_bnd_form", "target": "cu03_ctrl_validar", "value": "enviar actualización", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu03_07", "source": "cu03_ctrl_validar", "target": "cu03_ctrl_actualizar", "value": "datos validados", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu03_08", "source": "cu03_ctrl_actualizar", "target": "cu03_ent_usuario", "value": "actualizar campos y hash Bcrypt", "style": s["edge"], "exitX": 1.0, "exitY": 0.2, "entryX": 0.0, "entryY": 0.8},
        {"id": "e_cu03_09", "source": "cu03_ctrl_actualizar", "target": "cu03_ent_seguridad", "value": "actualizar timestamp password", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu03_10", "source": "cu03_ctrl_actualizar", "target": "cu03_ctrl_bitacora", "value": "cambios persistidos", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu03_11", "source": "cu03_ctrl_bitacora", "target": "cu03_ent_bitacora", "value": "registrar log auditoría", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu03_12", "source": "cu03_ctrl_actualizar", "target": "cu03_bnd_confirm", "value": "confirmar actualización", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu03_13", "source": "cu03_ctrl_validar", "target": "cu03_ctrl_err_val", "value": "teléfono o campos inválidos", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu03_14", "source": "cu03_ctrl_err_val", "target": "cu03_bnd_err_val", "value": "mostrar mensaje error", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu03_15", "source": "cu03_ctrl_actualizar", "target": "cu03_ctrl_err_pwd", "value": "password actual no coincide", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu03_16", "source": "cu03_ctrl_err_pwd", "target": "cu03_bnd_err_pwd", "value": "mostrar alerta password inválida", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu03", "name": "CU03 - Gestionar perfil", "nodes": nodes, "edges": edges}

# ==============================================================================
# 4. CU14W: Gestionar usuarios y roles (P1)
# ==============================================================================
def build_cu14_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Administrador accede al módulo 'Gestión de Usuarios y Roles'.<br/><br/>"
        "2. El sistema consulta t_usuario, t_rol y filtra por el ámbito de empresa del Administrador.<br/><br/>"
        "3. El sistema despliega la lista de usuarios y roles activos.<br/><br/>"
        "4. El Administrador pulsa 'Nuevo Usuario' o 'Editar Usuario' e ingresa credenciales, rol y sucursales asignadas.<br/><br/>"
        "5. El sistema valida unicidad de correo/username y que no se trasladen usuarios entre distintas empresas.<br/><br/>"
        "6. El sistema guarda transaccionalmente el usuario en t_usuario y asigna el rol en t_usuario_rol.<br/><br/>"
        "7. El Administrador puede además desactivar un usuario (activo = false) revocando sus sesiones activas.<br/><br/>"
        "8. El sistema registra auditoría en t_bitacora y actualiza la lista visible.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Usuario o correo ya registrado / Formato inválido:</b><br/>"
        "El sistema rechaza la operación y muestra la Página Error Validación / Duplicado.<br/><br/>"
        "• <b>Intento de modificar roles protegidos o empresa ajena:</b><br/>"
        "El sistema deniega el acceso con 403 Forbidden y muestra la Página Error Permiso Denegado."
    )

    nodes = [
        {"id": "cu14_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu14_act_admin", "value": "Administrador", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu14_bnd_gestion", "value": "Página Gestión Usuarios", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu14_ctrl_listar", "value": "Listar usuarios y roles", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu14_ent_usuario", "value": "t_usuario", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu14_ent_rol", "value": "t_rol / t_usuario_rol", "style": s["entity"], "x": 1440, "y": 255, "w": 80, "h": 75},
        {"id": "cu14_bnd_form", "value": "Formulario Usuario y Rol", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu14_ctrl_validar", "value": "Validar datos y ámbito empresa", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu14_ctrl_persistir", "value": "Persistir usuario y rol", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu14_ent_empresa", "value": "empresa", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu14_ctrl_bitacora", "value": "Registrar auditoría RBAC", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu14_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu14_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu14_ctrl_err_dup", "value": "Mostrar error duplicado", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu14_bnd_err_dup", "value": "Página Error Validación", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu14_ctrl_err_perm", "value": "Mostrar error permisos", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu14_bnd_err_perm", "value": "Página Error Ámbito", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu14_01", "source": "cu14_act_admin", "target": "cu14_bnd_gestion", "value": "abrir módulo usuarios", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu14_02", "source": "cu14_bnd_gestion", "target": "cu14_ctrl_listar", "value": "solicitar lista de personal", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu14_03", "source": "cu14_ctrl_listar", "target": "cu14_ent_usuario", "value": "filtrar usuarios por empresa", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu14_04", "source": "cu14_ctrl_listar", "target": "cu14_ent_rol", "value": "cargar roles disponibles", "style": s["edge"], "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu14_05", "source": "cu14_act_admin", "target": "cu14_bnd_form", "value": "ingresar datos y rol asignado", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu14_06", "source": "cu14_bnd_form", "target": "cu14_ctrl_validar", "value": "solicitar persistencia", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu14_07", "source": "cu14_ctrl_validar", "target": "cu14_ent_empresa", "value": "verificar pertenencia a empresa", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu14_08", "source": "cu14_ctrl_validar", "target": "cu14_ctrl_persistir", "value": "validación exitosa", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu14_09", "source": "cu14_ctrl_persistir", "target": "cu14_ent_usuario", "value": "guardar usuario con Bcrypt", "style": s["edge"], "exitX": 1.0, "exitY": 0.2, "entryX": 0.0, "entryY": 0.8},
        {"id": "e_cu14_10", "source": "cu14_ctrl_persistir", "target": "cu14_ent_rol", "value": "asociar rol en t_usuario_rol", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.8},
        {"id": "e_cu14_11", "source": "cu14_ctrl_persistir", "target": "cu14_ctrl_bitacora", "value": "operación completada", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu14_12", "source": "cu14_ctrl_bitacora", "target": "cu14_ent_bitacora", "value": "registrar log auditoría", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu14_13", "source": "cu14_ctrl_persistir", "target": "cu14_bnd_confirm", "value": "confirmar guardado / actualización", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu14_14", "source": "cu14_ctrl_validar", "target": "cu14_ctrl_err_dup", "value": "email duplicado o campos vacíos", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu14_15", "source": "cu14_ctrl_err_dup", "target": "cu14_bnd_err_dup", "value": "mostrar alerta validación", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu14_16", "source": "cu14_ctrl_validar", "target": "cu14_ctrl_err_perm", "value": "empresa ajena o rol de plataforma", "style": s["edge_alt"], "exitX": 0.8, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu14_17", "source": "cu14_ctrl_err_perm", "target": "cu14_bnd_err_perm", "value": "mostrar acceso denegado (403)", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu14", "name": "CU14 - Gestionar usuarios y roles", "nodes": nodes, "edges": edges}

# ==============================================================================
# 5. CU15W: Gestionar empresas SaaS (P1 — Refactorización)
# ==============================================================================
def build_cu15_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Administrador de Plataforma (Superadmin) accede al módulo 'Gestión de Empresas SaaS'.<br/><br/>"
        "2. El sistema consulta la tabla empresa y despliega la lista de tiendas tenant con su estado comercial.<br/><br/>"
        "3. El Superadmin presiona 'Registrar Empresa' o 'Editar Empresa' e ingresa nombre, NIT, dirección y teléfono.<br/><br/>"
        "4. El sistema valida los datos requeridos y verifica unicidad de NIT en la tabla empresa.<br/><br/>"
        "5. El sistema guarda la empresa activa configurando el tenant en la base de datos.<br/><br/>"
        "6. Ante una solicitud de eliminación, el sistema ejecuta una **baja lógica** (activo = false) preservando integridad referencial.<br/><br/>"
        "7. El sistema registra auditoría SaaS en t_bitacora y actualiza el catálogo visible.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>NIT o nombre de empresa duplicado:</b><br/>"
        "El sistema detiene el registro y muestra la Página Error NIT Duplicado.<br/><br/>"
        "• <b>Intento de borrado físico destructivo:</b><br/>"
        "El sistema intercepta la petición, rechaza la eliminación en cascada y muestra la Página Rechazo Supresión Física."
    )

    nodes = [
        {"id": "cu15_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu15_act_superadmin", "value": "Superadmin", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu15_bnd_empresas", "value": "Página Empresas SaaS", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu15_ctrl_listar", "value": "Listar empresas registradas", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu15_ent_empresa", "value": "empresa", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu15_bnd_form", "value": "Formulario Empresa", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu15_ctrl_validar", "value": "Validar datos y NIT", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu15_ctrl_persistir", "value": "Crear / Desactivar empresa", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu15_ent_sucursal", "value": "t_sucursal", "style": s["entity"], "x": 1440, "y": 270, "w": 80, "h": 75},
        {"id": "cu15_ent_suscripcion", "value": "t_suscripcion", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu15_ctrl_bitacora", "value": "Registrar auditoría SaaS", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu15_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu15_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu15_ctrl_err_nit", "value": "Mostrar error NIT duplicado", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu15_bnd_err_nit", "value": "Página Error NIT", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu15_ctrl_err_del", "value": "Rechazar borrado físico", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu15_bnd_err_del", "value": "Página Rechazo Supresión", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu15_01", "source": "cu15_act_superadmin", "target": "cu15_bnd_empresas", "value": "solicitar gestión empresas", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu15_02", "source": "cu15_bnd_empresas", "target": "cu15_ctrl_listar", "value": "consultar empresas", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu15_03", "source": "cu15_ctrl_listar", "target": "cu15_ent_empresa", "value": "obtener registros tenant", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu15_04", "source": "cu15_act_superadmin", "target": "cu15_bnd_form", "value": "ingresar datos comerciales", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu15_05", "source": "cu15_bnd_form", "target": "cu15_ctrl_validar", "value": "solicitar guardado", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu15_06", "source": "cu15_ctrl_validar", "target": "cu15_ent_empresa", "value": "verificar NIT no existente", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.7},
        {"id": "e_cu15_07", "source": "cu15_ctrl_validar", "target": "cu15_ctrl_persistir", "value": "validación exitosa", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu15_08", "source": "cu15_ctrl_persistir", "target": "cu15_ent_empresa", "value": "guardar o baja lógica (activo=false)", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu15_09", "source": "cu15_ctrl_persistir", "target": "cu15_ent_sucursal", "value": "preservar integridad sucursales", "style": s["edge"], "exitX": 1.0, "exitY": 0.2, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu15_10", "source": "cu15_ctrl_persistir", "target": "cu15_ent_suscripcion", "value": "consultar suscripciones asociadas", "style": s["edge"], "exitX": 1.0, "exitY": 0.7, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu15_11", "source": "cu15_ctrl_persistir", "target": "cu15_ctrl_bitacora", "value": "auditar cambio tenant", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu15_12", "source": "cu15_ctrl_bitacora", "target": "cu15_ent_bitacora", "value": "guardar evento auditoría", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu15_13", "source": "cu15_ctrl_persistir", "target": "cu15_bnd_confirm", "value": "notificar empresa guardada / desactivada", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu15_14", "source": "cu15_ctrl_validar", "target": "cu15_ctrl_err_nit", "value": "NIT duplicado o formato inválido", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu15_15", "source": "cu15_ctrl_err_nit", "target": "cu15_bnd_err_nit", "value": "mostrar error NIT", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu15_16", "source": "cu15_ctrl_persistir", "target": "cu15_ctrl_err_del", "value": "solicitud DELETE físico", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu15_17", "source": "cu15_ctrl_err_del", "target": "cu15_bnd_err_del", "value": "rechazar borrado en cascada", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu15", "name": "CU15 - Gestionar empresas SaaS", "nodes": nodes, "edges": edges}

# ==============================================================================
# 6. CU16W: Gestionar sucursales y ciudades (P1)
# ==============================================================================
def build_cu16_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Administrador de Empresa accede al módulo 'Sucursales y Ciudades'.<br/><br/>"
        "2. El sistema consulta t_sucursal y t_ciudad filtrando por la empresa activa.<br/><br/>"
        "3. El Administrador pulsa 'Nueva Sucursal' e ingresa nombre, código, dirección y selecciona la ciudad.<br/><br/>"
        "4. El sistema valida unicidad de código y verifica el límite de sucursales activas según el plan SaaS (Básico: 2, Profesional: 10).<br/><br/>"
        "5. El sistema persiste la sucursal vinculada a t_ciudad y a la empresa.<br/><br/>"
        "6. El Administrador puede además desactivar sucursales o modificar datos operativos.<br/><br/>"
        "7. El sistema registra auditoría en t_bitacora y actualiza la lista.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Límite de sucursales activas del plan excedido:</b><br/>"
        "El sistema rechaza la creación/reactivación con 409 Conflict y muestra la Página Error Límite Sucursales Plan.<br/><br/>"
        "• <b>Código de sucursal duplicado:</b><br/>"
        "El sistema muestra la Página Error Código Duplicado solicitando un código único."
    )

    nodes = [
        {"id": "cu16_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu16_act_admin", "value": "Administrador Empresa", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu16_bnd_sucursales", "value": "Página Sucursales y Ciudades", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu16_ctrl_listar", "value": "Listar sucursales y ciudades", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu16_ent_sucursal", "value": "t_sucursal", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu16_ent_ciudad", "value": "t_ciudad", "style": s["entity"], "x": 1440, "y": 255, "w": 80, "h": 75},
        {"id": "cu16_bnd_form", "value": "Formulario Sucursal", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu16_ctrl_verificar_cupo", "value": "Verificar límite de plan SaaS", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu16_ctrl_persistir", "value": "Persistir sucursal / ciudad", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu16_ent_suscripcion", "value": "t_suscripcion / t_plan", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu16_ctrl_bitacora", "value": "Registrar auditoría sucursales", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu16_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu16_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu16_ctrl_err_limite", "value": "Bloquear por límite plan", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu16_bnd_err_limite", "value": "Página Error Límite Plan", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu16_ctrl_err_dup", "value": "Mostrar código duplicado", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu16_bnd_err_dup", "value": "Página Error Código", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu16_01", "source": "cu16_act_admin", "target": "cu16_bnd_sucursales", "value": "abrir módulo sucursales", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu16_02", "source": "cu16_bnd_sucursales", "target": "cu16_ctrl_listar", "value": "solicitar sucursales", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu16_03", "source": "cu16_ctrl_listar", "target": "cu16_ent_sucursal", "value": "consultar sucursales empresa", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu16_04", "source": "cu16_ctrl_listar", "target": "cu16_ent_ciudad", "value": "consultar catálogo ciudades", "style": s["edge"], "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu16_05", "source": "cu16_act_admin", "target": "cu16_bnd_form", "value": "ingresar código, nombre y ciudad", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu16_06", "source": "cu16_bnd_form", "target": "cu16_ctrl_verificar_cupo", "value": "solicitar creación", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu16_07", "source": "cu16_ctrl_verificar_cupo", "target": "cu16_ent_suscripcion", "value": "consultar límite max_sucursales", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu16_08", "source": "cu16_ctrl_verificar_cupo", "target": "cu16_ctrl_persistir", "value": "cupo disponible", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu16_09", "source": "cu16_ctrl_persistir", "target": "cu16_ent_sucursal", "value": "insertar registro sucursal", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.8},
        {"id": "e_cu16_10", "source": "cu16_ctrl_persistir", "target": "cu16_ctrl_bitacora", "value": "sucursal persistida", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu16_11", "source": "cu16_ctrl_bitacora", "target": "cu16_ent_bitacora", "value": "guardar auditoría", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu16_12", "source": "cu16_ctrl_persistir", "target": "cu16_bnd_confirm", "value": "confirmar guardado", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu16_13", "source": "cu16_ctrl_verificar_cupo", "target": "cu16_ctrl_err_limite", "value": "sucursales activas >= límite plan", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu16_14", "source": "cu16_ctrl_err_limite", "target": "cu16_bnd_err_limite", "value": "mostrar error cupo excedido (409)", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu16_15", "source": "cu16_ctrl_persistir", "target": "cu16_ctrl_err_dup", "value": "código sucursal ya existe", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu16_16", "source": "cu16_ctrl_err_dup", "target": "cu16_bnd_err_dup", "value": "mostrar alerta código duplicado", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu16", "name": "CU16 - Gestionar sucursales y ciudades", "nodes": nodes, "edges": edges}

# ==============================================================================
# 7. CU17W: Gestionar productos (P1)
# ==============================================================================
def build_cu17_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Encargado de Catálogo accede al módulo 'Gestión de Productos'.<br/><br/>"
        "2. El sistema consulta t_producto y t_categoria de la empresa mostrando el inventario catalogado.<br/><br/>"
        "3. El usuario pulsa 'Nuevo Producto' e ingresa código SKU, nombre, descripción, precio y categoría.<br/><br/>"
        "4. El sistema valida que el precio sea mayor a cero y que el código SKU no esté duplicado.<br/><br/>"
        "5. El sistema persiste el registro en t_producto con estado activo.<br/><br/>"
        "6. El usuario puede modificar precios, descripciones o cambiar visibilidad comercial.<br/><br/>"
        "7. El sistema registra auditoría en t_bitacora y actualiza el catálogo.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Precio menor o igual a cero / Campos vacíos:</b><br/>"
        "El sistema rechaza el producto y muestra la Página Error Validación Precio.<br/><br/>"
        "• <b>Código de producto ya existente:</b><br/>"
        "El sistema detecta duplicidad en t_producto y muestra la Página Error Código Duplicado."
    )

    nodes = [
        {"id": "cu17_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu17_act_catalogo", "value": "Encargado Catálogo", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu17_bnd_productos", "value": "Página Productos", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu17_ctrl_listar", "value": "Listar productos de catálogo", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu17_ent_producto", "value": "t_producto", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu17_ent_categoria", "value": "t_categoria", "style": s["entity"], "x": 1440, "y": 255, "w": 80, "h": 75},
        {"id": "cu17_bnd_form", "value": "Formulario Producto", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu17_ctrl_validar", "value": "Validar precio y SKU", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu17_ctrl_persistir", "value": "Persistir producto", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu17_ent_marca", "value": "t_marca", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu17_ctrl_bitacora", "value": "Registrar auditoría catálogo", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu17_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu17_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu17_ctrl_err_val", "value": "Mostrar error precio", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu17_bnd_err_val", "value": "Página Error Precio", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu17_ctrl_err_dup", "value": "Mostrar error SKU duplicado", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu17_bnd_err_dup", "value": "Página Error SKU", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu17_01", "source": "cu17_act_catalogo", "target": "cu17_bnd_productos", "value": "abrir catálogo productos", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu17_02", "source": "cu17_bnd_productos", "target": "cu17_ctrl_listar", "value": "consultar catálogo", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu17_03", "source": "cu17_ctrl_listar", "target": "cu17_ent_producto", "value": "obtener prendas empresa", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu17_04", "source": "cu17_ctrl_listar", "target": "cu17_ent_categoria", "value": "asociar categorías", "style": s["edge"], "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu17_05", "source": "cu17_act_catalogo", "target": "cu17_bnd_form", "value": "ingresar datos de prenda", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu17_06", "source": "cu17_bnd_form", "target": "cu17_ctrl_validar", "value": "solicitar registro", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu17_07", "source": "cu17_ctrl_validar", "target": "cu17_ent_producto", "value": "comprobar SKU disponible", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.7},
        {"id": "e_cu17_08", "source": "cu17_ctrl_validar", "target": "cu17_ctrl_persistir", "value": "precio > 0 y SKU válido", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu17_09", "source": "cu17_ctrl_persistir", "target": "cu17_ent_producto", "value": "guardar producto en BD", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.9},
        {"id": "e_cu17_10", "source": "cu17_ctrl_persistir", "target": "cu17_ent_marca", "value": "asociar marca", "style": s["edge"], "exitX": 1.0, "exitY": 0.7, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu17_11", "source": "cu17_ctrl_persistir", "target": "cu17_ctrl_bitacora", "value": "producto guardado", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu17_12", "source": "cu17_ctrl_bitacora", "target": "cu17_ent_bitacora", "value": "auditar cambio", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu17_13", "source": "cu17_ctrl_persistir", "target": "cu17_bnd_confirm", "value": "confirmar guardado", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu17_14", "source": "cu17_ctrl_validar", "target": "cu17_ctrl_err_val", "value": "precio <= 0 o campo vacío", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu17_15", "source": "cu17_ctrl_err_val", "target": "cu17_bnd_err_val", "value": "mostrar error precio", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu17_16", "source": "cu17_ctrl_validar", "target": "cu17_ctrl_err_dup", "value": "SKU ya registrado", "style": s["edge_alt"], "exitX": 0.8, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu17_17", "source": "cu17_ctrl_err_dup", "target": "cu17_bnd_err_dup", "value": "mostrar alerta SKU duplicado", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu17", "name": "CU17 - Gestionar productos", "nodes": nodes, "edges": edges}

# ==============================================================================
# 8. CU18W: Gestionar categorías (P1)
# ==============================================================================
def build_cu18_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Encargado de Catálogo accede al módulo 'Gestión de Categorías'.<br/><br/>"
        "2. El sistema consulta t_categoria y despliega la estructura jerárquica de categorías de ropa.<br/><br/>"
        "3. El usuario pulsa 'Nueva Categoría' e ingresa nombre, descripción y categoría padre (opcional).<br/><br/>"
        "4. El sistema valida unicidad del nombre dentro de la empresa.<br/><br/>"
        "5. El sistema guarda la categoría en t_categoria.<br/><br/>"
        "6. En caso de solicitar eliminación, el sistema verifica que no existan prendas asociadas en t_producto.<br/><br/>"
        "7. El sistema registra auditoría en t_bitacora y actualiza el árbol de categorías.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Nombre de categoría duplicado:</b><br/>"
        "El sistema muestra la Página Error Nombre Categoría Duplicado.<br/><br/>"
        "• <b>Categoría con productos asociados:</b><br/>"
        "El sistema bloquea la eliminación y despliega la Página Error Dependencias Productos."
    )

    nodes = [
        {"id": "cu18_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu18_act_catalogo", "value": "Encargado Catálogo", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu18_bnd_categorias", "value": "Página Categorías", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu18_ctrl_listar", "value": "Listar árbol categorías", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu18_ent_categoria", "value": "t_categoria", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu18_bnd_form", "value": "Formulario Categoría", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu18_ctrl_validar", "value": "Validar nombre único", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu18_ctrl_persistir", "value": "Persistir categoría", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu18_ent_producto", "value": "t_producto", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu18_ctrl_bitacora", "value": "Registrar auditoría categorías", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu18_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu18_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu18_ctrl_err_dup", "value": "Mostrar error nombre", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu18_bnd_err_dup", "value": "Página Error Nombre", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu18_ctrl_err_dep", "value": "Bloquear por productos asociados", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu18_bnd_err_dep", "value": "Página Error Dependencias", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu18_01", "source": "cu18_act_catalogo", "target": "cu18_bnd_categorias", "value": "abrir módulo categorías", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu18_02", "source": "cu18_bnd_categorias", "target": "cu18_ctrl_listar", "value": "solicitar árbol", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu18_03", "source": "cu18_ctrl_listar", "target": "cu18_ent_categoria", "value": "obtener categorías empresa", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu18_04", "source": "cu18_act_catalogo", "target": "cu18_bnd_form", "value": "ingresar nombre y categoría padre", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu18_05", "source": "cu18_bnd_form", "target": "cu18_ctrl_validar", "value": "solicitar guardado", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu18_06", "source": "cu18_ctrl_validar", "target": "cu18_ent_categoria", "value": "comprobar nombre único", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.7},
        {"id": "e_cu18_07", "source": "cu18_ctrl_validar", "target": "cu18_ctrl_persistir", "value": "nombre válido", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu18_08", "source": "cu18_ctrl_persistir", "target": "cu18_ent_categoria", "value": "insertar / actualizar categoría", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.9},
        {"id": "e_cu18_09", "source": "cu18_ctrl_persistir", "target": "cu18_ent_producto", "value": "verificar ausencia de prendas para baja", "style": s["edge"], "exitX": 1.0, "exitY": 0.7, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu18_10", "source": "cu18_ctrl_persistir", "target": "cu18_ctrl_bitacora", "value": "categoría guardada", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu18_11", "source": "cu18_ctrl_bitacora", "target": "cu18_ent_bitacora", "value": "guardar auditoría", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu18_12", "source": "cu18_ctrl_persistir", "target": "cu18_bnd_confirm", "value": "confirmar cambios", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu18_13", "source": "cu18_ctrl_validar", "target": "cu18_ctrl_err_dup", "value": "nombre de categoría repetido", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu18_14", "source": "cu18_ctrl_err_dup", "target": "cu18_bnd_err_dup", "value": "mostrar error nombre duplicado", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu18_15", "source": "cu18_ctrl_persistir", "target": "cu18_ctrl_err_dep", "value": "existen productos activos asociados", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu18_16", "source": "cu18_ctrl_err_dep", "target": "cu18_bnd_err_dep", "value": "mostrar bloqueo por productos", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu18", "name": "CU18 - Gestionar categorías", "nodes": nodes, "edges": edges}

# ==============================================================================
# 9. CU19W: Gestionar tallas y colores (P1)
# ==============================================================================
def build_cu19_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Encargado de Inventario selecciona una prenda y accede a 'Variantes de Producto'.<br/><br/>"
        "2. El sistema consulta t_producto_talla_color, t_talla, t_color y t_inventario para mostrar las variantes existentes y su stock.<br/><br/>"
        "3. El usuario pulsa 'Agregar Variante', selecciona una talla, un color e ingresa la cantidad de stock inicial.<br/><br/>"
        "4. El sistema valida que la combinación de talla y color no esté ya asignada a la prenda.<br/><br/>"
        "5. El sistema persiste el registro en t_producto_talla_color e inicializa el registro en t_inventario para la sucursal.<br/><br/>"
        "6. El usuario puede actualizar las cantidades de stock o inactivar combinaciones agotadas.<br/><br/>"
        "7. El sistema registra auditoría en t_bitacora y actualiza la matriz de variantes.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Combinación talla-color ya existente:</b><br/>"
        "El sistema rechaza la variante y muestra la Página Error Variante Duplicada.<br/><br/>"
        "• <b>Stock negativo o formato inválido:</b><br/>"
        "El sistema muestra la Página Error Stock Inválido."
    )

    nodes = [
        {"id": "cu19_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu19_act_inventario", "value": "Encargado Inventario", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu19_bnd_variantes", "value": "Página Variantes Prendas", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu19_ctrl_listar", "value": "Listar variantes y stock", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu19_ent_ptc", "value": "t_producto_talla_color", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu19_ent_talla_color", "value": "t_talla / t_color", "style": s["entity"], "x": 1440, "y": 255, "w": 80, "h": 75},
        {"id": "cu19_bnd_form", "value": "Formulario Talla / Color", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu19_ctrl_validar", "value": "Validar combinación única", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu19_ctrl_persistir", "value": "Crear variante y stock", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu19_ent_inventario", "value": "t_inventario", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu19_ctrl_bitacora", "value": "Registrar auditoría inventario", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu19_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu19_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu19_ctrl_err_dup", "value": "Mostrar error variante dup", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu19_bnd_err_dup", "value": "Página Error Variante", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu19_ctrl_err_stock", "value": "Mostrar error stock negativo", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu19_bnd_err_stock", "value": "Página Error Stock", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu19_01", "source": "cu19_act_inventario", "target": "cu19_bnd_variantes", "value": "seleccionar prenda y ver variantes", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu19_02", "source": "cu19_bnd_variantes", "target": "cu19_ctrl_listar", "value": "solicitar matriz de variantes", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu19_03", "source": "cu19_ctrl_listar", "target": "cu19_ent_ptc", "value": "obtener combinaciones prenda", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu19_04", "source": "cu19_ctrl_listar", "target": "cu19_ent_talla_color", "value": "cargar catálogo tallas y colores", "style": s["edge"], "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu19_05", "source": "cu19_act_inventario", "target": "cu19_bnd_form", "value": "seleccionar talla, color y stock", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu19_06", "source": "cu19_bnd_form", "target": "cu19_ctrl_validar", "value": "solicitar adición de variante", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu19_07", "source": "cu19_ctrl_validar", "target": "cu19_ent_ptc", "value": "comprobar inexistencia previa", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.7},
        {"id": "e_cu19_08", "source": "cu19_ctrl_validar", "target": "cu19_ctrl_persistir", "value": "variante nueva y stock >= 0", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu19_09", "source": "cu19_ctrl_persistir", "target": "cu19_ent_ptc", "value": "insertar en t_producto_talla_color", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.9},
        {"id": "e_cu19_10", "source": "cu19_ctrl_persistir", "target": "cu19_ent_inventario", "value": "inicializar stock en sucursal", "style": s["edge"], "exitX": 1.0, "exitY": 0.7, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu19_11", "source": "cu19_ctrl_persistir", "target": "cu19_ctrl_bitacora", "value": "variante creada", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu19_12", "source": "cu19_ctrl_bitacora", "target": "cu19_ent_bitacora", "value": "guardar auditoría stock", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu19_13", "source": "cu19_ctrl_persistir", "target": "cu19_bnd_confirm", "value": "confirmar registro", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu19_14", "source": "cu19_ctrl_validar", "target": "cu19_ctrl_err_dup", "value": "combinación ya existe en la prenda", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu19_15", "source": "cu19_ctrl_err_dup", "target": "cu19_bnd_err_dup", "value": "mostrar alerta combinación duplicada", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu19_16", "source": "cu19_ctrl_validar", "target": "cu19_ctrl_err_stock", "value": "stock ingresado < 0", "style": s["edge_alt"], "exitX": 0.8, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu19_17", "source": "cu19_ctrl_err_stock", "target": "cu19_bnd_err_stock", "value": "mostrar alerta stock inválido", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu19", "name": "CU19 - Gestionar tallas y colores", "nodes": nodes, "edges": edges}

# ==============================================================================
# 10. CU20W: Gestionar temporadas y colecciones (P1)
# ==============================================================================
def build_cu20_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Encargado de Catálogo accede al módulo 'Temporadas y Colecciones'.<br/><br/>"
        "2. El sistema consulta t_temporada y t_coleccion mostrando las campañas comerciales activas.<br/><br/>"
        "3. El usuario pulsa 'Nueva Temporada/Colección' e introduce nombre, fecha de inicio y fecha de fin.<br/><br/>"
        "4. El sistema valida que la fecha de fin sea posterior a la de inicio y que el nombre sea único.<br/><br/>"
        "5. El sistema guarda la colección y permite asociar prendas de catálogo de t_producto.<br/><br/>"
        "6. El usuario puede modificar fechas de vigencia o estado promocional.<br/><br/>"
        "7. El sistema registra auditoría en t_bitacora y actualiza las colecciones visibles.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Fechas incoherentes (inicio > fin):</b><br/>"
        "El sistema rechaza la campaña y muestra la Página Error Rango de Fechas.<br/><br/>"
        "• <b>Colección con nombre duplicado:</b><br/>"
        "El sistema muestra la Página Error Colección Duplicada."
    )

    nodes = [
        {"id": "cu20_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu20_act_catalogo", "value": "Encargado Catálogo", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu20_bnd_colecciones", "value": "Página Temporadas y Colecciones", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu20_ctrl_listar", "value": "Listar campañas comerciales", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu20_ent_temporada", "value": "t_temporada", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu20_ent_coleccion", "value": "t_coleccion", "style": s["entity"], "x": 1440, "y": 255, "w": 80, "h": 75},
        {"id": "cu20_bnd_form", "value": "Formulario Colección", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu20_ctrl_validar", "value": "Validar fechas y nombre", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu20_ctrl_persistir", "value": "Persistir colección y prendas", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu20_ent_producto", "value": "t_producto", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu20_ctrl_bitacora", "value": "Registrar auditoría colecciones", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu20_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu20_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu20_ctrl_err_fechas", "value": "Mostrar error fechas", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu20_bnd_err_fechas", "value": "Página Error Fechas", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu20_ctrl_err_dup", "value": "Mostrar error duplicado", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu20_bnd_err_dup", "value": "Página Error Nombre", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu20_01", "source": "cu20_act_catalogo", "target": "cu20_bnd_colecciones", "value": "abrir módulo campañas", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu20_02", "source": "cu20_bnd_colecciones", "target": "cu20_ctrl_listar", "value": "solicitar colecciones", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu20_03", "source": "cu20_ctrl_listar", "target": "cu20_ent_temporada", "value": "consultar temporadas", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu20_04", "source": "cu20_ctrl_listar", "target": "cu20_ent_coleccion", "value": "consultar colecciones", "style": s["edge"], "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu20_05", "source": "cu20_act_catalogo", "target": "cu20_bnd_form", "value": "ingresar datos y vigencia", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu20_06", "source": "cu20_bnd_form", "target": "cu20_ctrl_validar", "value": "solicitar registro", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu20_07", "source": "cu20_ctrl_validar", "target": "cu20_ctrl_persistir", "value": "fechas consistentes e inicio < fin", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu20_08", "source": "cu20_ctrl_persistir", "target": "cu20_ent_coleccion", "value": "guardar en t_coleccion", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.9},
        {"id": "e_cu20_09", "source": "cu20_ctrl_persistir", "target": "cu20_ent_producto", "value": "vincular prendas seleccionadas", "style": s["edge"], "exitX": 1.0, "exitY": 0.7, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu20_10", "source": "cu20_ctrl_persistir", "target": "cu20_ctrl_bitacora", "value": "campaña registrada", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu20_11", "source": "cu20_ctrl_bitacora", "target": "cu20_ent_bitacora", "value": "guardar log auditoría", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu20_12", "source": "cu20_ctrl_persistir", "target": "cu20_bnd_confirm", "value": "confirmar guardado", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu20_13", "source": "cu20_ctrl_validar", "target": "cu20_ctrl_err_fechas", "value": "inicio >= fin", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu20_14", "source": "cu20_ctrl_err_fechas", "target": "cu20_bnd_err_fechas", "value": "mostrar error fechas incoherentes", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu20_15", "source": "cu20_ctrl_validar", "target": "cu20_ctrl_err_dup", "value": "nombre colección repetido", "style": s["edge_alt"], "exitX": 0.8, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu20_16", "source": "cu20_ctrl_err_dup", "target": "cu20_bnd_err_dup", "value": "mostrar alerta colección duplicada", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu20", "name": "CU20 - Gestionar temporadas y colecciones", "nodes": nodes, "edges": edges}

# ==============================================================================
# 11. CU21W: Gestionar proveedores (P1)
# ==============================================================================
def build_cu21_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Encargado de Compras accede al módulo 'Directorio de Proveedores'.<br/><br/>"
        "2. El sistema consulta t_proveedor y muestra la lista de proveedores activos de la empresa.<br/><br/>"
        "3. El usuario pulsa 'Registrar Proveedor' e ingresa razón social, NIT, teléfono, correo y dirección.<br/><br/>"
        "4. El sistema valida el formato de datos y comprueba que el NIT no esté duplicado.<br/><br/>"
        "5. El sistema persiste el nuevo proveedor en t_proveedor.<br/><br/>"
        "6. En caso de desactivación, el sistema comprueba que no existan órdenes de compra pendientes en t_orden_compra.<br/><br/>"
        "7. El sistema registra auditoría en t_bitacora y actualiza el directorio.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>NIT duplicado o teléfono inválido:</b><br/>"
        "El sistema muestra la Página Error NIT Duplicado.<br/><br/>"
        "• <b>Proveedor con órdenes de compra activas:</b><br/>"
        "El sistema bloquea la baja y despliega la Página Error Órdenes Pendientes."
    )

    nodes = [
        {"id": "cu21_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu21_act_compras", "value": "Encargado Compras", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu21_bnd_proveedores", "value": "Página Directorio Proveedores", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu21_ctrl_listar", "value": "Listar proveedores empresa", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu21_ent_proveedor", "value": "t_proveedor", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu21_bnd_form", "value": "Formulario Proveedor", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu21_ctrl_validar", "value": "Validar NIT y contacto", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu21_ctrl_persistir", "value": "Persistir proveedor", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu21_ent_orden", "value": "t_orden_compra", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu21_ctrl_bitacora", "value": "Registrar auditoría compras", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu21_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu21_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu21_ctrl_err_nit", "value": "Mostrar error NIT", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu21_bnd_err_nit", "value": "Página Error NIT", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu21_ctrl_err_orden", "value": "Bloquear por compras activas", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu21_bnd_err_orden", "value": "Página Error Compras Activas", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu21_01", "source": "cu21_act_compras", "target": "cu21_bnd_proveedores", "value": "abrir directorio proveedores", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu21_02", "source": "cu21_bnd_proveedores", "target": "cu21_ctrl_listar", "value": "solicitar directorio", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu21_03", "source": "cu21_ctrl_listar", "target": "cu21_ent_proveedor", "value": "consultar proveedores empresa", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu21_04", "source": "cu21_act_compras", "target": "cu21_bnd_form", "value": "ingresar razón social y NIT", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu21_05", "source": "cu21_bnd_form", "target": "cu21_ctrl_validar", "value": "solicitar registro", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu21_06", "source": "cu21_ctrl_validar", "target": "cu21_ent_proveedor", "value": "comprobar NIT no repetido", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.7},
        {"id": "e_cu21_07", "source": "cu21_ctrl_validar", "target": "cu21_ctrl_persistir", "value": "datos validados", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu21_08", "source": "cu21_ctrl_persistir", "target": "cu21_ent_proveedor", "value": "insertar / actualizar proveedor", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.9},
        {"id": "e_cu21_09", "source": "cu21_ctrl_persistir", "target": "cu21_ent_orden", "value": "verificar ausencia de órdenes abiertas", "style": s["edge"], "exitX": 1.0, "exitY": 0.7, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu21_10", "source": "cu21_ctrl_persistir", "target": "cu21_ctrl_bitacora", "value": "proveedor guardado", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu21_11", "source": "cu21_ctrl_bitacora", "target": "cu21_ent_bitacora", "value": "guardar auditoría", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu21_12", "source": "cu21_ctrl_persistir", "target": "cu21_bnd_confirm", "value": "confirmar guardado", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu21_13", "source": "cu21_ctrl_validar", "target": "cu21_ctrl_err_nit", "value": "NIT duplicado o formato inválido", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu21_14", "source": "cu21_ctrl_err_nit", "target": "cu21_bnd_err_nit", "value": "mostrar error NIT duplicado", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu21_15", "source": "cu21_ctrl_persistir", "target": "cu21_ctrl_err_orden", "value": "órdenes de compra activas existentes", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu21_16", "source": "cu21_ctrl_err_orden", "target": "cu21_bnd_err_orden", "value": "mostrar bloqueo por órdenes activas", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu21", "name": "CU21 - Gestionar proveedores", "nodes": nodes, "edges": edges}

# ==============================================================================
# 12. CU34W: Gestionar planes de suscripción (P2 — Nuevo)
# ==============================================================================
def build_cu34_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Administrador de Plataforma (Superadmin) accede al módulo 'Planes de Suscripción'.<br/><br/>"
        "2. El sistema valida el alcance PLATAFORMA y el permiso planes.ver.<br/><br/>"
        "3. El sistema consulta t_plan y despliega los planes: BASICO (2 sucursales) y PROFESIONAL (10 sucursales, reportes generativos).<br/><br/>"
        "4. El Superadmin selecciona un plan y actualiza su nombre descriptivo o disponibilidad para nuevas suscripciones.<br/><br/>"
        "5. El sistema verifica la inmutabilidad de los límites y códigos fijos del modelo de negocio.<br/><br/>"
        "6. El sistema persiste los cambios en t_plan sin alterar suscripciones ya asignadas.<br/><br/>"
        "7. El sistema registra auditoría en t_bitacora y actualiza el catálogo de planes.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Intento de crear códigos de plan arbitrarios o alterar capacidades:</b><br/>"
        "El sistema rechaza la solicitud y muestra la Página Rechazo Código Arbitrario.<br/><br/>"
        "• <b>Usuario sin alcance PLATAFORMA:</b><br/>"
        "El sistema deniega el acceso con 403 Forbidden y muestra la Página Error Permisos Plataforma."
    )

    nodes = [
        {"id": "cu34_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu34_act_superadmin", "value": "Superadmin", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu34_bnd_planes", "value": "Página Planes SaaS", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu34_ctrl_validar_perm", "value": "Validar alcance PLATAFORMA", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu34_ctrl_listar", "value": "Listar planes disponibles", "style": s["control"], "x": 1140, "y": 145, "w": 75, "h": 75},
        {"id": "cu34_ent_plan", "value": "t_plan", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu34_bnd_form", "value": "Formulario Configuración Plan", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu34_ctrl_verificar_codigo", "value": "Verificar códigos fijos (BASICO/PROF)", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu34_ctrl_persistir", "value": "Actualizar disponibilidad plan", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu34_ent_suscripcion", "value": "t_suscripcion", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu34_ctrl_bitacora", "value": "Registrar auditoría planes", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu34_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu34_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu34_ctrl_err_perm", "value": "Mostrar error alcance", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu34_bnd_err_perm", "value": "Página Error Permisos", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu34_ctrl_err_cod", "value": "Rechazar código arbitrario", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu34_bnd_err_cod", "value": "Página Rechazo Código", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu34_01", "source": "cu34_act_superadmin", "target": "cu34_bnd_planes", "value": "solicitar catálogo planes", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu34_02", "source": "cu34_bnd_planes", "target": "cu34_ctrl_validar_perm", "value": "verificar autorización", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu34_03", "source": "cu34_ctrl_validar_perm", "target": "cu34_ctrl_listar", "value": "autorizado PLATAFORMA", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu34_04", "source": "cu34_ctrl_listar", "target": "cu34_ent_plan", "value": "consultar planes t_plan", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu34_05", "source": "cu34_act_superadmin", "target": "cu34_bnd_form", "value": "modificar nombre o estado activo", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu34_06", "source": "cu34_bnd_form", "target": "cu34_ctrl_verificar_codigo", "value": "solicitar actualización", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu34_07", "source": "cu34_ctrl_verificar_codigo", "target": "cu34_ctrl_persistir", "value": "código BASICO o PROFESIONAL", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu34_08", "source": "cu34_ctrl_persistir", "target": "cu34_ent_plan", "value": "actualizar disponibilidad en t_plan", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.9},
        {"id": "e_cu34_09", "source": "cu34_ctrl_persistir", "target": "cu34_ent_suscripcion", "value": "preservar contratos existentes", "style": s["edge"], "exitX": 1.0, "exitY": 0.7, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu34_10", "source": "cu34_ctrl_persistir", "target": "cu34_ctrl_bitacora", "value": "plan actualizado", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu34_11", "source": "cu34_ctrl_bitacora", "target": "cu34_ent_bitacora", "value": "guardar auditoría SaaS", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu34_12", "source": "cu34_ctrl_persistir", "target": "cu34_bnd_confirm", "value": "confirmar cambios en plan", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu34_13", "source": "cu34_ctrl_validar_perm", "target": "cu34_ctrl_err_perm", "value": "alcance no es PLATAFORMA", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu34_14", "source": "cu34_ctrl_err_perm", "target": "cu34_bnd_err_perm", "value": "mostrar acceso denegado (403)", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu34_15", "source": "cu34_ctrl_verificar_codigo", "target": "cu34_ctrl_err_cod", "value": "código no reconocido o alteración de límites", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu34_16", "source": "cu34_ctrl_err_cod", "target": "cu34_bnd_err_cod", "value": "mostrar rechazo código arbitrario", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu34", "name": "CU34 - Gestionar planes de suscripción", "nodes": nodes, "edges": edges}

# ==============================================================================
# 13. CU35W: Gestionar suscripciones empresariales (P2 — Nuevo)
# ==============================================================================
def build_cu35_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Superadmin accede al módulo 'Suscripciones Empresariales' y selecciona una empresa.<br/><br/>"
        "2. El sistema consulta t_suscripcion y t_plan mostrando el historial de suscripciones.<br/><br/>"
        "3. El Superadmin pulsa 'Asignar / Renovar Suscripción', elige el plan, fechas [inicio, fin) y motivo administrativo.<br/><br/>"
        "4. El sistema valida que fin > inicio y que no existan periodos solapados activos.<br/><br/>"
        "5. El sistema cuenta las sucursales activas en t_sucursal y verifica que no superen el límite del nuevo plan.<br/><br/>"
        "6. El sistema crea el nuevo registro en t_suscripcion con estado VIGENTE.<br/><br/>"
        "7. En caso de requerir cancelación, actualiza el estado a CANCELADA sin borrar el registro.<br/><br/>"
        "8. El sistema registra auditoría en t_bitacora y actualiza el historial.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Capacidad de sucursales inferior al uso actual:</b><br/>"
        "El sistema rechaza la asignación con 409 Conflict y muestra la Página Error Capacidad Insuficiente.<br/><br/>"
        "• <b>Periodo solapado o fechas inválidas:</b><br/>"
        "El sistema rechaza la solicitud y muestra la Página Error Periodo Solapado."
    )

    nodes = [
        {"id": "cu35_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu35_act_superadmin", "value": "Superadmin", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu35_bnd_suscripciones", "value": "Página Suscripciones", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu35_ctrl_historial", "value": "Listar historial suscripciones", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu35_ent_suscripcion", "value": "t_suscripcion", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu35_ent_plan", "value": "t_plan", "style": s["entity"], "x": 1440, "y": 255, "w": 80, "h": 75},
        {"id": "cu35_bnd_form", "value": "Formulario Suscripción", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu35_ctrl_validar", "value": "Validar fechas y capacidad sucursales", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu35_ctrl_persistir", "value": "Registrar periodo o cancelar", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu35_ent_sucursal", "value": "t_sucursal", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu35_ctrl_bitacora", "value": "Registrar auditoría suscripción", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu35_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu35_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu35_ctrl_err_cap", "value": "Bloquear por capacidad insuficiente", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu35_bnd_err_cap", "value": "Página Error Capacidad", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu35_ctrl_err_solap", "value": "Mostrar error solapamiento", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu35_bnd_err_solap", "value": "Página Error Solapamiento", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu35_01", "source": "cu35_act_superadmin", "target": "cu35_bnd_suscripciones", "value": "seleccionar empresa cliente", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu35_02", "source": "cu35_bnd_suscripciones", "target": "cu35_ctrl_historial", "value": "solicitar historial", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu35_03", "source": "cu35_ctrl_historial", "target": "cu35_ent_suscripcion", "value": "consultar periodos históricos", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu35_04", "source": "cu35_ctrl_historial", "target": "cu35_ent_plan", "value": "obtener detalles plan", "style": s["edge"], "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu35_05", "source": "cu35_act_superadmin", "target": "cu35_bnd_form", "value": "ingresar plan, fechas y motivo", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu35_06", "source": "cu35_bnd_form", "target": "cu35_ctrl_validar", "value": "solicitar asignación/renovación", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu35_07", "source": "cu35_ctrl_validar", "target": "cu35_ent_sucursal", "value": "contar sucursales activas actuales", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.7},
        {"id": "e_cu35_08", "source": "cu35_ctrl_validar", "target": "cu35_ctrl_persistir", "value": "capacidad suficiente y fechas válidas", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu35_09", "source": "cu35_ctrl_persistir", "target": "cu35_ent_suscripcion", "value": "insertar nuevo periodo [inicio, fin)", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.9},
        {"id": "e_cu35_10", "source": "cu35_ctrl_persistir", "target": "cu35_ctrl_bitacora", "value": "suscripción registrada", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu35_11", "source": "cu35_ctrl_bitacora", "target": "cu35_ent_bitacora", "value": "guardar log auditoría", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu35_12", "source": "cu35_ctrl_persistir", "target": "cu35_bnd_confirm", "value": "confirmar periodo creado", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu35_13", "source": "cu35_ctrl_validar", "target": "cu35_ctrl_err_cap", "value": "sucursales activas > límite plan", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu35_14", "source": "cu35_ctrl_err_cap", "target": "cu35_bnd_err_cap", "value": "mostrar error capacidad insuficiente (409)", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu35_15", "source": "cu35_ctrl_validar", "target": "cu35_ctrl_err_solap", "value": "periodo solapado con otro activo", "style": s["edge_alt"], "exitX": 0.8, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu35_16", "source": "cu35_ctrl_err_solap", "target": "cu35_bnd_err_solap", "value": "mostrar error periodo solapado", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu35", "name": "CU35 - Gestionar suscripciones empresariales", "nodes": nodes, "edges": edges}

# ==============================================================================
# 14. CU36W: Consultar plan y límites de suscripción (P2 — Nuevo)
# ==============================================================================
def build_cu36_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Administrador de Tienda accede a la sección 'Mi Plan y Límites' desde el menú del sistema.<br/><br/>"
        "2. El sistema extrae el id_empresa desde el contexto seguro de sesión JWT.<br/><br/>"
        "3. El sistema consulta t_suscripcion para obtener el periodo vigente dentro del rango [inicio, fin).<br/><br/>"
        "4. El sistema consulta t_plan para obtener los límites de sucursales y la capacidad de reportes generativos.<br/><br/>"
        "5. El sistema cuenta las sucursales activas en t_sucursal y calcula las disponibles.<br/><br/>"
        "6. El sistema despliega la Página Estado de Suscripción con indicadores gráficos de uso y vigencia.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Sin suscripción vigente o periodo vencido:</b><br/>"
        "El sistema muestra la Página Sin Suscripción Vigente con estado SIN_SUSCRIPCION o VENCIDA.<br/><br/>"
        "• <b>Empresa desactivada o suspendida:</b><br/>"
        "El sistema muestra la Página Empresa Inactiva bloqueando operaciones de escritura."
    )

    nodes = [
        {"id": "cu36_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu36_act_admin", "value": "Administrador Tienda", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu36_bnd_consulta", "value": "Página Consulta Plan", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu36_ctrl_sesion", "value": "Obtener id_empresa de JWT", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu36_ctrl_vigencia", "value": "Consultar vigencia suscripción", "style": s["control"], "x": 1140, "y": 145, "w": 75, "h": 75},
        {"id": "cu36_ent_suscripcion", "value": "t_suscripcion", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu36_ctrl_metricas", "value": "Calcular métricas de uso", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu36_ent_plan", "value": "t_plan", "style": s["entity"], "x": 1440, "y": 270, "w": 80, "h": 75},
        {"id": "cu36_ent_sucursal", "value": "t_sucursal", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu36_ent_empresa", "value": "empresa", "style": s["entity"], "x": 1440, "y": 480, "w": 80, "h": 75},
        {"id": "cu36_bnd_estado", "value": "Página Estado y Límites", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu36_ctrl_err_vencida", "value": "Evaluar sin suscripción / vencida", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu36_bnd_err_vencida", "value": "Página Sin Suscripción", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu36_ctrl_err_inactiva", "value": "Evaluar empresa inactiva", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu36_bnd_err_inactiva", "value": "Página Empresa Inactiva", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu36_01", "source": "cu36_act_admin", "target": "cu36_bnd_consulta", "value": "abrir sección mi plan", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu36_02", "source": "cu36_bnd_consulta", "target": "cu36_ctrl_sesion", "value": "solicitar estado del plan", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu36_03", "source": "cu36_ctrl_sesion", "target": "cu36_ctrl_vigencia", "value": "empresa identificada", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu36_04", "source": "cu36_ctrl_vigencia", "target": "cu36_ent_suscripcion", "value": "buscar periodo [inicio, fin)", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu36_05", "source": "cu36_ctrl_vigencia", "target": "cu36_ctrl_metricas", "value": "suscripción VIGENTE encontrada", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu36_06", "source": "cu36_ctrl_metricas", "target": "cu36_ent_plan", "value": "obtener max_sucursales y reportes", "style": s["edge"], "exitX": 1.0, "exitY": 0.2, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu36_07", "source": "cu36_ctrl_metricas", "target": "cu36_ent_sucursal", "value": "contar sucursales activas", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu36_08", "source": "cu36_ctrl_metricas", "target": "cu36_bnd_estado", "value": "desplegar límites y uso", "style": s["edge"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu36_09", "source": "cu36_bnd_estado", "target": "cu36_act_admin", "value": "mostrar panel informativo", "style": s["edge"], "exitX": 0.0, "exitY": 0.5, "entryX": 0.8, "entryY": 1.0},
        {"id": "e_cu36_10", "source": "cu36_ctrl_vigencia", "target": "cu36_ctrl_err_vencida", "value": "periodo no encontrado o expirado", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu36_11", "source": "cu36_ctrl_err_vencida", "target": "cu36_bnd_err_vencida", "value": "mostrar alerta sin suscripción vigente", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu36_12", "source": "cu36_ctrl_sesion", "target": "cu36_ctrl_err_inactiva", "value": "empresa dada de baja", "style": s["edge_alt"], "exitX": 0.8, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu36_13", "source": "cu36_ctrl_err_inactiva", "target": "cu36_ent_empresa", "value": "verificar activo = false", "style": s["edge_alt"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu36_14", "source": "cu36_ctrl_err_inactiva", "target": "cu36_bnd_err_inactiva", "value": "mostrar alerta empresa suspendida", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu36", "name": "CU36 - Consultar plan y límites de suscripción", "nodes": nodes, "edges": edges}

# ==============================================================================
# 15. CU41W: Gestionar respaldos y restauraciones (P2 — Nuevo)
# ==============================================================================
def build_cu41_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Administrador del Sistema (Superadmin) accede al módulo de infraestructura 'Gestión de Respaldos'.<br/><br/>"
        "2. El sistema valida los privilegios de superusuario y consulta t_respaldo_sistema listando los snapshots disponibles.<br/><br/>"
        "3. El usuario pulsa 'Generar Respaldo Completo' e ingresa descripción y motivo.<br/><br/>"
        "4. El sistema ejecuta el volcado estructurado seguro (pg_dump), calcula el checksum SHA256 y cifra el archivo.<br/><br/>"
        "5. El sistema registra los metadatos en t_respaldo_sistema.<br/><br/>"
        "6. En caso de restauración, el usuario selecciona un volcado y confirma con doble factor de seguridad.<br/><br/>"
        "7. El sistema verifica la integridad del archivo y ejecuta la restauración de esquemas y datos.<br/><br/>"
        "8. El sistema registra auditoría crítica en t_bitacora y notifica el resultado.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Falla en el motor de volcado / Espacio insuficiente:</b><br/>"
        "El sistema detiene el proceso y muestra la Página Error Falla Motor Respaldo.<br/><br/>"
        "• <b>Checksum corrupto o versión de esquema incompatible:</b><br/>"
        "El sistema bloquea la restauración y muestra la Página Error Verificación Integridad."
    )

    nodes = [
        {"id": "cu41_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu41_act_superadmin", "value": "Superadmin", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu41_bnd_respaldos", "value": "Página Gestión Respaldos", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu41_ctrl_listar", "value": "Listar respaldos y verificar rol", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu41_ent_respaldo", "value": "t_respaldo_sistema", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu41_bnd_form", "value": "Modal Respaldo / Restauración", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu41_ctrl_dump", "value": "Ejecutar volcado y checksum SHA256", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu41_ctrl_restore", "value": "Ejecutar restauración segura", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu41_ent_seguridad", "value": "t_seguridad_usuario", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu41_ctrl_bitacora", "value": "Registrar auditoría crítica", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu41_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu41_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu41_ctrl_err_dump", "value": "Gestionar falla pg_dump", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu41_bnd_err_dump", "value": "Página Error Motor", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu41_ctrl_err_chk", "value": "Gestionar checksum inválido", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu41_bnd_err_chk", "value": "Página Error Integridad", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu41_01", "source": "cu41_act_superadmin", "target": "cu41_bnd_respaldos", "value": "abrir módulo respaldos", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu41_02", "source": "cu41_bnd_respaldos", "target": "cu41_ctrl_listar", "value": "solicitar historial dumps", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu41_03", "source": "cu41_ctrl_listar", "target": "cu41_ent_respaldo", "value": "obtener registros de respaldos", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu41_04", "source": "cu41_act_superadmin", "target": "cu41_bnd_form", "value": "solicitar creación o restauración", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu41_05", "source": "cu41_bnd_form", "target": "cu41_ctrl_dump", "value": "iniciar generación dump", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu41_06", "source": "cu41_ctrl_dump", "target": "cu41_ent_respaldo", "value": "guardar metadatos y checksum SHA256", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.8},
        {"id": "e_cu41_07", "source": "cu41_ctrl_dump", "target": "cu41_ctrl_restore", "value": "respaldo listo para restauración", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu41_08", "source": "cu41_ctrl_restore", "target": "cu41_ent_seguridad", "value": "verificar credencial superusuario", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu41_09", "source": "cu41_ctrl_restore", "target": "cu41_ctrl_bitacora", "value": "restauración exitosa", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu41_10", "source": "cu41_ctrl_bitacora", "target": "cu41_ent_bitacora", "value": "registrar evento crítico", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu41_11", "source": "cu41_ctrl_restore", "target": "cu41_bnd_confirm", "value": "confirmar operación", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu41_12", "source": "cu41_ctrl_dump", "target": "cu41_ctrl_err_dump", "value": "error en pg_dump o espacio agotado", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu41_13", "source": "cu41_ctrl_err_dump", "target": "cu41_bnd_err_dump", "value": "mostrar error motor respaldo", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu41_14", "source": "cu41_ctrl_restore", "target": "cu41_ctrl_err_chk", "value": "checksum SHA256 no coincide", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu41_15", "source": "cu41_ctrl_err_chk", "target": "cu41_bnd_err_chk", "value": "mostrar error archivo corrupto", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu41", "name": "CU41 - Gestionar respaldos y restauraciones", "nodes": nodes, "edges": edges}

# ==============================================================================
# 16. CU43W: Gestionar asignaciones de empleados a sucursales (P2 — Nuevo)
# ==============================================================================
def build_cu43_spec():
    s = get_common_styles()
    note_text = (
        "<b>BASIC COURSE (Curso Básico):</b><br/><br/>"
        "1. El Administrador de Empresa accede al módulo 'Asignación de Empleados a Sucursales'.<br/><br/>"
        "2. El sistema consulta t_empleado y t_usuario_sucursal de la empresa y muestra el personal con sus sucursales autorizadas.<br/><br/>"
        "3. El Administrador selecciona un empleado e ingresa la lista de IDs de sucursales permitidas [1, 2].<br/><br/>"
        "4. El sistema valida que todas las sucursales indicadas pertenezcan a la empresa y se encuentren activas.<br/><br/>"
        "5. El sistema ejecuta un reemplazo atómico en t_usuario_sucursal, preservando el dato laboral en t_empleado.<br/><br/>"
        "6. Si la lista enviada es vacía [], el sistema revoca todos los accesos a sucursales de ese usuario.<br/><br/>"
        "7. El sistema registra auditoría en t_bitacora (con el antes y después) y actualiza la vista.<br/><br/>"
        "<hr/>"
        "<b>ALTERNATE COURSES (Cursos Alternativos):</b><br/><br/>"
        "• <b>Sucursal perteneciente a otra empresa o sin jerarquía:</b><br/>"
        "El sistema rechaza la asignación con 403 Forbidden y muestra la Página Error Sucursal Ajena.<br/><br/>"
        "• <b>Sucursal inactiva o formato de lista inválido:</b><br/>"
        "El sistema rechaza la solicitud con 422/409 y muestra la Página Error Validación Sucursal."
    )

    nodes = [
        {"id": "cu43_note", "value": note_text, "style": s["note"], "x": 40, "y": 40, "w": 330, "h": 900},
        {"id": "cu43_act_admin", "value": "Administrador Empresa", "style": s["actor"], "x": 430, "y": 140, "w": 45, "h": 85},
        {"id": "cu43_bnd_asignaciones", "value": "Página Asignaciones", "style": s["boundary"], "x": 620, "y": 145, "w": 80, "h": 75},
        {"id": "cu43_ctrl_listar", "value": "Listar empleados y sucursales", "style": s["control"], "x": 880, "y": 145, "w": 75, "h": 75},
        {"id": "cu43_ent_empleado", "value": "t_empleado / t_usuario", "style": s["entity"], "x": 1440, "y": 145, "w": 80, "h": 75},
        {"id": "cu43_ent_sucursal", "value": "t_sucursal", "style": s["entity"], "x": 1440, "y": 255, "w": 80, "h": 75},
        {"id": "cu43_bnd_form", "value": "Formulario Asignación Sucursales", "style": s["boundary"], "x": 620, "y": 370, "w": 80, "h": 75},
        {"id": "cu43_ctrl_validar", "value": "Validar sucursales activas y empresa", "style": s["control"], "x": 880, "y": 370, "w": 75, "h": 75},
        {"id": "cu43_ctrl_persistir", "value": "Reemplazo atómico en t_usuario_sucursal", "style": s["control"], "x": 1140, "y": 370, "w": 75, "h": 75},
        {"id": "cu43_ent_usuario_sucursal", "value": "t_usuario_sucursal", "style": s["entity"], "x": 1440, "y": 370, "w": 80, "h": 75},
        {"id": "cu43_ctrl_bitacora", "value": "Registrar auditoría asignaciones", "style": s["control"], "x": 1140, "y": 550, "w": 75, "h": 75},
        {"id": "cu43_ent_bitacora", "value": "t_bitacora", "style": s["entity"], "x": 1440, "y": 550, "w": 80, "h": 75},
        {"id": "cu43_bnd_confirm", "value": "Página Confirmación", "style": s["boundary"], "x": 420, "y": 370, "w": 80, "h": 75},
        {"id": "cu43_ctrl_err_ajena", "value": "Rechazar sucursal ajena", "style": s["control_alt"], "x": 880, "y": 740, "w": 75, "h": 75},
        {"id": "cu43_bnd_err_ajena", "value": "Página Error Sucursal Ajena", "style": s["boundary_alt"], "x": 620, "y": 740, "w": 80, "h": 75},
        {"id": "cu43_ctrl_err_inactiva", "value": "Rechazar sucursal inactiva/formato", "style": s["control_alt"], "x": 1140, "y": 740, "w": 75, "h": 75},
        {"id": "cu43_bnd_err_inactiva", "value": "Página Error Validación", "style": s["boundary_alt"], "x": 920, "y": 740, "w": 80, "h": 75}
    ]

    edges = [
        {"id": "e_cu43_01", "source": "cu43_act_admin", "target": "cu43_bnd_asignaciones", "value": "abrir módulo asignaciones", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu43_02", "source": "cu43_bnd_asignaciones", "target": "cu43_ctrl_listar", "value": "solicitar lista de personal", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu43_03", "source": "cu43_ctrl_listar", "target": "cu43_ent_empleado", "value": "obtener empleados empresa", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu43_04", "source": "cu43_ctrl_listar", "target": "cu43_ent_sucursal", "value": "obtener sucursales empresa", "style": s["edge"], "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu43_05", "source": "cu43_act_admin", "target": "cu43_bnd_form", "value": "seleccionar empleado y lista sucursales", "style": s["edge"], "exitX": 0.7, "exitY": 1.0, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu43_06", "source": "cu43_bnd_form", "target": "cu43_ctrl_validar", "value": "solicitar asignación", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu43_07", "source": "cu43_ctrl_validar", "target": "cu43_ent_sucursal", "value": "verificar pertenencia a empresa y activo=true", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.7},
        {"id": "e_cu43_08", "source": "cu43_ctrl_validar", "target": "cu43_ctrl_persistir", "value": "todas las sucursales válidas", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu43_09", "source": "cu43_ctrl_persistir", "target": "cu43_ent_usuario_sucursal", "value": "reemplazo atómico de asignaciones", "style": s["edge"], "exitX": 1.0, "exitY": 0.3, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu43_10", "source": "cu43_ctrl_persistir", "target": "cu43_ent_empleado", "value": "preservar t_empleado.id_sucursal", "style": s["edge"], "exitX": 1.0, "exitY": 0.7, "entryX": 0.0, "entryY": 0.8},
        {"id": "e_cu43_11", "source": "cu43_ctrl_persistir", "target": "cu43_ctrl_bitacora", "value": "asignaciones actualizadas", "style": s["edge"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu43_12", "source": "cu43_ctrl_bitacora", "target": "cu43_ent_bitacora", "value": "guardar auditoría con antes/después", "style": s["edge"], "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5},
        {"id": "e_cu43_13", "source": "cu43_ctrl_persistir", "target": "cu43_bnd_confirm", "value": "confirmar asignación", "style": s["edge"], "exitX": 0.0, "exitY": 0.8, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu43_14", "source": "cu43_ctrl_validar", "target": "cu43_ctrl_err_ajena", "value": "sucursal de empresa ajena o actor sin permisos", "style": s["edge_alt"], "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu43_15", "source": "cu43_ctrl_err_ajena", "target": "cu43_bnd_err_ajena", "value": "mostrar error 403 Forbidden", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5},
        {"id": "e_cu43_16", "source": "cu43_ctrl_validar", "target": "cu43_ctrl_err_inactiva", "value": "sucursal inactiva o formato de lista inválido", "style": s["edge_alt"], "exitX": 0.8, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0},
        {"id": "e_cu43_17", "source": "cu43_ctrl_err_inactiva", "target": "cu43_bnd_err_inactiva", "value": "mostrar error validación 422", "style": s["edge_alt"], "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5}
    ]

    return {"id": "diag_cu43", "name": "CU43 - Gestionar asignaciones de empleados", "nodes": nodes, "edges": edges}

# ==============================================================================
# Generador del XML y Renderizador Maestro
# ==============================================================================
def render_diagram_xml(diag_spec):
    parts = []
    parts.append(f'  <diagram id="{diag_spec["id"]}" name="{diag_spec["name"]}">')
    parts.append('    <mxGraphModel dx="1800" dy="1100" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1850" pageHeight="1050" background="#ffffff" math="0" shadow="0">')
    parts.append('      <root>')
    parts.append('        <mxCell id="0" />')
    parts.append('        <mxCell id="1" parent="0" />')

    # Nodos
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

    # Conexiones (Edges)
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

def generate_unified_drawio():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    unified_drawio_path = os.path.join(output_dir, "diagramas_robustez.drawio")
    unified_xml_path = os.path.join(output_dir, "diagramas_robustez.xml")

    # Lista con los 16 constructores en orden estricto
    builders = [
        build_cu01_spec,
        build_cu02_spec,
        build_cu03_spec,
        build_cu14_spec,
        build_cu15_spec,
        build_cu16_spec,
        build_cu17_spec,
        build_cu18_spec,
        build_cu19_spec,
        build_cu20_spec,
        build_cu21_spec,
        build_cu34_spec,
        build_cu35_spec,
        build_cu36_spec,
        build_cu41_spec,
        build_cu43_spec
    ]

    xml_lines = []
    xml_lines.append('<mxfile host="app.diagrams.net" modified="2026-10-24T23:55:00.000Z" agent="Antigravity" version="24.0.0" type="device">')
    
    for builder in builders:
        diag = builder()
        print(f"Generando pestaña: {diag['name']} ({len(diag['nodes'])} nodos, {len(diag['edges'])} conexiones)...")
        xml_lines.append(render_diagram_xml(diag))
        
    xml_lines.append('</mxfile>')

    full_xml = "\n".join(xml_lines)

    # Validar sintaxis XML estricta
    try:
        ET.fromstring(full_xml)
        print("\n[OK] Validación XML exitosa: Estructura Draw.io multi-diagrama perfecta y bien formada.")
    except ET.ParseError as err:
        print(f"\n[ERROR] Error de sintaxis XML: {err}")
        raise

    with open(unified_drawio_path, "w", encoding="utf-8") as f:
        f.write(full_xml)
    with open(unified_xml_path, "w", encoding="utf-8") as f:
        f.write(full_xml)

    print(f"\nArchivo maestro multi-tab generado exitosamente con los 16 Casos de Uso:")
    print(f" - {unified_drawio_path}")
    print(f" - {unified_xml_path}")

if __name__ == "__main__":
    generate_unified_drawio()
