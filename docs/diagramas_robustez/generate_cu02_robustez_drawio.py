#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del Diagrama de Robustez (Análisis ICONIX / UML 2.5) en formato XML para draw.io
Caso de Uso: CU02W / CU02M - Iniciar sesión
Sistema: AuroraStore (Aura Atelier) - Multi-tenant SaaS
Materia: Sistemas de Información II (UAGRM)
"""

import os
import html
import xml.etree.ElementTree as ET

def create_cu02_drawio():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    drawio_path = os.path.join(output_dir, "CU02_WM_Iniciar_Sesion_Robustez.drawio")
    xml_path = os.path.join(output_dir, "CU02_WM_Iniciar_Sesion_Robustez.xml")

    # Estilos de draw.io para ICONIX / UML 2.5
    style_actor = (
        "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
        "outlineConnect=0;fillColor=#f8fafc;strokeColor=#1e293b;strokeWidth=2;"
        "fontFamily=Arial;fontSize=12;fontStyle=1;fontColor=#0f172a;"
    )
    style_boundary = (
        "shape=umlBoundary;whiteSpace=wrap;html=1;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;fillColor=#eff6ff;strokeColor=#2563eb;strokeWidth=2.2;"
        "fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#1e3a8a;"
    )
    style_control = (
        "shape=umlControl;whiteSpace=wrap;html=1;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;fillColor=#fef3c7;strokeColor=#d97706;strokeWidth=2.2;"
        "fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#78350f;"
    )
    style_entity = (
        "shape=umlEntity;whiteSpace=wrap;html=1;verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;fillColor=#ecfdf5;strokeColor=#059669;strokeWidth=2.2;"
        "fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#064e3b;"
    )
    style_edge = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
        "strokeColor=#334155;strokeWidth=1.6;endArrow=classic;endFill=1;fontFamily=Arial;"
        "fontSize=10;fontColor=#1e293b;labelBackgroundColor=#ffffff;labelBorderColor=#cbd5e1;"
    )
    style_edge_alt = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
        "dashed=1;strokeColor=#dc2626;strokeWidth=1.6;endArrow=classic;endFill=1;fontFamily=Arial;"
        "fontSize=10;fontColor=#991b1b;labelBackgroundColor=#ffffff;labelBorderColor=#fca5a5;"
    )

    # Definición de Nodos (ID, Value, Style, X, Y, W, H)
    nodes = [
        # Encabezado
        {
            "id": "header_title",
            "value": (
                "<b>AURORASTORE — DIAGRAMA DE ROBUSTEZ (ANÁLISIS ICONIX / UML 2.5)</b><br/>"
                "<span style='font-size: 13px; color: #475569; font-weight: normal;'>"
                "<b>CU02W / CU02M: Iniciar sesión</b> | "
                "Flujo Principal, Control de Intentos Fallidos (3 intentos / 15 min), Verificación de Dispositivos, "
                "Generación de JWT y Resolución de Contexto RBAC Multi-tenant</span>"
            ),
            "style": (
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8fafc;strokeColor=#cbd5e1;strokeWidth=1.5;"
                "fontFamily=Arial;fontSize=15;fontColor=#0f172a;align=left;spacingLeft=20;"
            ),
            "x": 40, "y": 20, "w": 1620, "h": 60
        },

        # 1. ACTOR
        {
            "id": "act_usuario",
            "value": "<b>Usuario</b><br/>(Cliente / Personal / Admin)",
            "style": style_actor,
            "x": 80, "y": 420, "w": 50, "h": 90
        },

        # 2. BOUNDARIES (Fronteras / Interfaces)
        {
            "id": "bnd_login",
            "value": "<b>IU_IniciarSesion</b><br/>(Formulario Web / Pantalla Móvil)",
            "style": style_boundary,
            "x": 270, "y": 425, "w": 95, "h": 80
        },
        {
            "id": "bnd_menu",
            "value": "<b>IU_MenuPrincipal</b><br/>(Dashboard Admin / Catálogo Público)",
            "style": style_boundary,
            "x": 270, "y": 170, "w": 95, "h": 80
        },
        {
            "id": "bnd_error",
            "value": "<b>IU_MensajeAlerta</b><br/>(Credenciales Inválidas / Cuenta Bloqueada)",
            "style": style_boundary,
            "x": 270, "y": 660, "w": 95, "h": 80
        },
        {
            "id": "bnd_mfa",
            "value": "<b>IU_VerificarDispositivo</b><br/>(Formulario Código OTP de Seguridad)",
            "style": style_boundary,
            "x": 270, "y": 880, "w": 95, "h": 80
        },

        # 3. CONTROLLERS (Lógica / Verbos de Control)
        {
            "id": "ctrl_login",
            "value": "<b>ctrl_AutenticarUsuario</b><br/>(Valida campos y orquesta autenticación)",
            "style": style_control,
            "x": 550, "y": 425, "w": 85, "h": 80
        },
        {
            "id": "ctrl_bloqueo",
            "value": "<b>ctrl_GestionarIntentosBloqueo</b><br/>(Incrementa intentos o bloquea 15 min)",
            "style": style_control,
            "x": 550, "y": 660, "w": 85, "h": 80
        },
        {
            "id": "ctrl_dispositivo",
            "value": "<b>ctrl_VerificarDispositivo</b><br/>(Comprueba huella digital y genera OTP)",
            "style": style_control,
            "x": 550, "y": 880, "w": 85, "h": 80
        },
        {
            "id": "ctrl_token",
            "value": "<b>ctrl_GenerarTokenSesion</b><br/>(Construye y firma JWT con claims RBAC)",
            "style": style_control,
            "x": 550, "y": 170, "w": 85, "h": 80
        },
        {
            "id": "ctrl_rbac",
            "value": "<b>ctrl_CargarContextoRBAC</b><br/>(Carga roles, permisos y sucursales)",
            "style": style_control,
            "x": 860, "y": 260, "w": 85, "h": 80
        },
        {
            "id": "ctrl_bitacora",
            "value": "<b>ctrl_RegistrarAuditoria</b><br/>(Inserta evento LOGIN en auditoría)",
            "style": style_control,
            "x": 860, "y": 540, "w": 85, "h": 80
        },

        # 4. ENTITIES (Entidades del Modelo de Datos Real)
        {
            "id": "ent_usuario",
            "value": (
                "<b>t_usuario</b><br/>"
                "<span style='font-size:9.5px;'>"
                "nro_usuario, correo, password_hash,<br/>"
                "estado, intentos_fallidos, bloqueado_hasta</span>"
            ),
            "style": style_entity,
            "x": 1200, "y": 425, "w": 85, "h": 80
        },
        {
            "id": "ent_roles",
            "value": (
                "<b>t_usuario_rol / t_rol</b><br/>"
                "<span style='font-size:9.5px;'>id_rol, nombre_rol, alcance</span>"
            ),
            "style": style_entity,
            "x": 1200, "y": 150, "w": 85, "h": 80
        },
        {
            "id": "ent_permisos",
            "value": (
                "<b>t_rol_permiso / t_permiso</b><br/>"
                "<span style='font-size:9.5px;'>codigo, modulo, accion</span>"
            ),
            "style": style_entity,
            "x": 1200, "y": 260, "w": 85, "h": 80
        },
        {
            "id": "ent_sucursales",
            "value": (
                "<b>t_usuario_sucursal / t_sucursal</b><br/>"
                "<span style='font-size:9.5px;'>id_sucursal, nombre, id_empresa</span>"
            ),
            "style": style_entity,
            "x": 1450, "y": 260, "w": 85, "h": 80
        },
        {
            "id": "ent_bitacora",
            "value": (
                "<b>t_bitacora</b><br/>"
                "<span style='font-size:9.5px;'>modulo, accion, nivel, resultado, ip, detalle</span>"
            ),
            "style": style_entity,
            "x": 1200, "y": 540, "w": 85, "h": 80
        },
        {
            "id": "ent_dispositivo",
            "value": (
                "<b>t_dispositivo_usuario</b><br/>"
                "<span style='font-size:9.5px;'>id_usuario, fingerprint, confirmado</span>"
            ),
            "style": style_entity,
            "x": 1200, "y": 880, "w": 85, "h": 80
        },

        # Panel Metodológico ICONIX (Reglas y Leyenda)
        {
            "id": "panel_legend",
            "value": (
                "<b>ESTÁNDAR METODOLÓGICO ICONIX (UML 2.5) — REGLAS ESTRICTAS DE ROBUSTEZ:</b><br/>"
                "• <b>1. Actores:</b> Solo pueden comunicarse directamente con objetos <b>Boundary</b> (Interfaz). Nunca con Control ni Entity.<br/>"
                "• <b>2. Boundary (Frontera):</b> Recibe eventos de la UI y delega exclusivamente a <b>Control</b>. <i>(Prohibido Boundary ➔ Entity)</i>.<br/>"
                "• <b>3. Control (Lógica):</b> Orquesta transacciones, reglas de negocio y delega a otros <b>Control</b>, <b>Entity</b> o responde a <b>Boundary</b>.<br/>"
                "• <b>4. Entity (Datos):</b> Representa el estado persistente (tablas de BD PostgreSQL). Solo es accedido y manipulado por <b>Control</b>."
            ),
            "style": (
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#f1f5f9;strokeColor=#94a3b8;strokeWidth=1.5;"
                "fontFamily=Arial;fontSize=10.5;fontColor=#334155;align=left;spacingLeft=15;verticalAlign=middle;"
            ),
            "x": 40, "y": 1020, "w": 1620, "h": 85
        }
    ]

    # Definición de Conexiones (Edges)
    # id, source, target, value, style, exitX, exitY, entryX, entryY
    edges = [
        # 1. Usuario -> IU_IniciarSesion
        {
            "id": "e01_usuario_login",
            "source": "act_usuario",
            "target": "bnd_login",
            "value": "1: Ingresar credenciales y enviar formulario",
            "style": style_edge,
            "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5
        },
        # 2. IU_IniciarSesion -> ctrl_AutenticarUsuario
        {
            "id": "e02_login_ctrl",
            "source": "bnd_login",
            "target": "ctrl_login",
            "value": "2: Solicitar login(login_identifier, password)",
            "style": style_edge,
            "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5
        },
        # 3. ctrl_AutenticarUsuario -> t_usuario (consulta)
        {
            "id": "e03_ctrl_usuario",
            "source": "ctrl_login",
            "target": "ent_usuario",
            "value": "3: Consultar credenciales por correo o username",
            "style": style_edge,
            "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5
        },

        # Flujo Alternativo: Password Incorrecto / Bloqueo
        # 4. ctrl_AutenticarUsuario -> ctrl_GestionarIntentosBloqueo
        {
            "id": "e04_ctrl_bloqueo",
            "source": "ctrl_login",
            "target": "ctrl_bloqueo",
            "value": "[Credencial incorrecta o cuenta inactiva]",
            "style": style_edge_alt,
            "exitX": 0.5, "exitY": 1.0, "entryX": 0.5, "entryY": 0.0
        },
        # 4a. ctrl_GestionarIntentosBloqueo -> t_usuario (actualizar intentos o bloqueo)
        {
            "id": "e05_bloqueo_ent",
            "source": "ctrl_bloqueo",
            "target": "ent_usuario",
            "value": "4a: Actualizar intentos_fallidos / fijar bloqueado_hasta (15 min)",
            "style": style_edge_alt,
            "exitX": 1.0, "exitY": 0.5, "entryX": 0.2, "entryY": 1.0
        },
        # 4b. ctrl_GestionarIntentosBloqueo -> ctrl_RegistrarAuditoria
        {
            "id": "e06_bloqueo_auditoria",
            "source": "ctrl_bloqueo",
            "target": "ctrl_bitacora",
            "value": "4b: Registrar LOGIN_FALLIDO o CUENTA_BLOQUEADA",
            "style": style_edge_alt,
            "exitX": 0.8, "exitY": 0.0, "entryX": 0.2, "entryY": 1.0
        },
        # 4c. ctrl_GestionarIntentosBloqueo -> IU_MensajeAlerta
        {
            "id": "e07_bloqueo_error",
            "source": "ctrl_bloqueo",
            "target": "bnd_error",
            "value": "4c: Notificar intentos restantes o tiempo de bloqueo",
            "style": style_edge_alt,
            "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5
        },
        # 4d. IU_MensajeAlerta -> Usuario
        {
            "id": "e08_error_usuario",
            "source": "bnd_error",
            "target": "act_usuario",
            "value": "4d: Visualizar alerta de error",
            "style": style_edge_alt,
            "exitX": 0.0, "exitY": 0.5, "entryX": 0.8, "entryY": 1.0
        },

        # Flujo Dispositivo Nuevo / MFA
        # 5. ctrl_AutenticarUsuario -> ctrl_VerificarDispositivo
        {
            "id": "e09_ctrl_dispositivo",
            "source": "ctrl_login",
            "target": "ctrl_dispositivo",
            "value": "[Contraseña correcta] Verificar huella de dispositivo",
            "style": style_edge,
            "exitX": 0.3, "exitY": 1.0, "entryX": 0.3, "entryY": 0.0
        },
        # 5a. ctrl_VerificarDispositivo -> t_dispositivo_usuario
        {
            "id": "e10_dispositivo_ent",
            "source": "ctrl_dispositivo",
            "target": "ent_dispositivo",
            "value": "5a: Consultar huella digital (device_fingerprint)",
            "style": style_edge,
            "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5
        },
        # 5b. ctrl_VerificarDispositivo -> IU_VerificarDispositivo
        {
            "id": "e11_dispositivo_mfa",
            "source": "ctrl_dispositivo",
            "target": "bnd_mfa",
            "value": "[Dispositivo desconocido] Generar código y solicitar OTP",
            "style": style_edge,
            "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5
        },
        # 5c. IU_VerificarDispositivo -> Usuario
        {
            "id": "e12_mfa_usuario",
            "source": "bnd_mfa",
            "target": "act_usuario",
            "value": "5c: Solicitar ingreso de código de verificación",
            "style": style_edge,
            "exitX": 0.0, "exitY": 0.5, "entryX": 0.2, "entryY": 1.0
        },

        # Flujo Principal: Éxito y Contexto RBAC
        # 6. ctrl_AutenticarUsuario -> ctrl_CargarContextoRBAC
        {
            "id": "e13_ctrl_rbac",
            "source": "ctrl_login",
            "target": "ctrl_rbac",
            "value": "6: [Autenticado] Cargar privilegios y contexto",
            "style": style_edge,
            "exitX": 1.0, "exitY": 0.2, "entryX": 0.0, "entryY": 0.8
        },
        # 6a. ctrl_CargarContextoRBAC -> t_usuario_rol
        {
            "id": "e14_rbac_roles",
            "source": "ctrl_rbac",
            "target": "ent_roles",
            "value": "6a: Consultar roles del usuario",
            "style": style_edge,
            "exitX": 1.0, "exitY": 0.2, "entryX": 0.0, "entryY": 0.5
        },
        # 6b. ctrl_CargarContextoRBAC -> t_rol_permiso
        {
            "id": "e15_rbac_permisos",
            "source": "ctrl_rbac",
            "target": "ent_permisos",
            "value": "6b: Consultar permisos efectivos",
            "style": style_edge,
            "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5
        },
        # 6c. ctrl_CargarContextoRBAC -> t_usuario_sucursal
        {
            "id": "e16_rbac_sucursales",
            "source": "ctrl_rbac",
            "target": "ent_sucursales",
            "value": "6c: Consultar sucursales asignadas",
            "style": style_edge,
            "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.5
        },

        # 7. ctrl_CargarContextoRBAC -> ctrl_GenerarTokenSesion
        {
            "id": "e17_rbac_token",
            "source": "ctrl_rbac",
            "target": "ctrl_token",
            "value": "7: Entregar roles, permisos, tenant y alcance",
            "style": style_edge,
            "exitX": 0.0, "exitY": 0.2, "entryX": 1.0, "entryY": 0.8
        },
        # 8. ctrl_GenerarTokenSesion -> IU_MenuPrincipal
        {
            "id": "e18_token_menu",
            "source": "ctrl_token",
            "target": "bnd_menu",
            "value": "8: Retornar token JWT y autorizar redirección",
            "style": style_edge,
            "exitX": 0.0, "exitY": 0.5, "entryX": 1.0, "entryY": 0.5
        },
        # 9. IU_MenuPrincipal -> Usuario
        {
            "id": "e19_menu_usuario",
            "source": "bnd_menu",
            "target": "act_usuario",
            "value": "9: Presentar vista inicial según rol (Admin/POS/Tienda)",
            "style": style_edge,
            "exitX": 0.0, "exitY": 0.5, "entryX": 0.5, "entryY": 0.0
        },

        # 10. ctrl_AutenticarUsuario -> ctrl_RegistrarAuditoria (Éxito)
        {
            "id": "e20_login_bitacora",
            "source": "ctrl_login",
            "target": "ctrl_bitacora",
            "value": "10: Registrar LOGIN_EXITOSO",
            "style": style_edge,
            "exitX": 1.0, "exitY": 0.8, "entryX": 0.0, "entryY": 0.2
        },
        # 10a. ctrl_RegistrarAuditoria -> t_bitacora
        {
            "id": "e21_bitacora_ent",
            "source": "ctrl_bitacora",
            "target": "ent_bitacora",
            "value": "10a: Insertar registro de auditoría",
            "style": style_edge,
            "exitX": 1.0, "exitY": 0.5, "entryX": 0.0, "entryY": 0.5
        }
    ]

    # Construcción XML de draw.io
    xml_parts = []
    xml_parts.append('<mxfile host="app.diagrams.net" modified="2026-10-24T22:35:00.000Z" agent="Antigravity" version="24.0.0" type="device">')
    xml_parts.append('  <diagram id="diagram_cu02_robustez" name="CU02 - Iniciar sesión (Robustez ICONIX)">')
    xml_parts.append('    <mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1700" pageHeight="1150" background="#ffffff" math="0" shadow="0">')
    xml_parts.append('      <root>')
    xml_parts.append('        <mxCell id="0" />')
    xml_parts.append('        <mxCell id="1" parent="0" />')

    # Agregar Nodos
    for n in nodes:
        val_esc = html.escape(n["value"])
        style_esc = html.escape(n["style"])
        xml_parts.append(
            f'        <mxCell id="{n["id"]}" value="{val_esc}" style="{style_esc}" vertex="1" parent="1">'
        )
        xml_parts.append(
            f'          <mxGeometry x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" as="geometry" />'
        )
        xml_parts.append('        </mxCell>')

    # Agregar Conexiones (Edges)
    for e in edges:
        val_esc = html.escape(e["value"])
        style_with_points = (
            f'{e["style"]}exitX={e["exitX"]};exitY={e["exitY"]};entryX={e["entryX"]};entryY={e["entryY"]};'
        )
        style_esc = html.escape(style_with_points)
        xml_parts.append(
            f'        <mxCell id="{e["id"]}" value="{val_esc}" style="{style_esc}" edge="1" parent="1" source="{e["source"]}" target="{e["target"]}">'
        )
        xml_parts.append('          <mxGeometry relative="1" as="geometry" />')
        xml_parts.append('        </mxCell>')

    xml_parts.append('      </root>')
    xml_parts.append('    </mxGraphModel>')
    xml_parts.append('  </diagram>')
    xml_parts.append('</mxfile>')

    full_xml = "\n".join(xml_parts)

    # Validar que sea un XML perfectamente válido
    try:
        ET.fromstring(full_xml)
        print("Validación XML exitosa: El contenido cumple estrictamente la sintaxis XML de draw.io.")
    except ET.ParseError as err:
        print(f"Error de sintaxis XML: {err}")
        raise

    # Guardar ambos archivos (.drawio y .xml)
    with open(drawio_path, "w", encoding="utf-8") as f:
        f.write(full_xml)
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(full_xml)

    print(f"Diagrama de robustez guardado en:")
    print(f" - {drawio_path}")
    print(f" - {xml_path}")

if __name__ == "__main__":
    create_cu02_drawio()
