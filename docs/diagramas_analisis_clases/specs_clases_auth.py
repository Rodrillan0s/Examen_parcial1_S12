#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Especificaciones de Diagramas de Análisis de Clases (UML / ICONIX VOPC) para el módulo de Autenticación y Usuarios:
- CU01: Registrar usuario (P1)
- CU02: Iniciar sesión (P1)
- CU03: Gestionar perfil (P1)
- CU14: Gestionar usuarios y roles (P1)
"""

# ==============================================================================
# CU01: Registrar usuario (P1)
# ==============================================================================
def get_cu01_clases():
    return {
        "id": "CU01_WM",
        "file_name": "CU01_WM_Registrar_Usuario_Clases",
        "title": "CU01 W/M: Registrar usuario — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Unificación Web (CU01W) y Móvil (CU01M) | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Usuario No Autenticado (Cliente Web / Móvil)",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_registro",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Registro_Usuario"],
                "attributes": [
                    "+ username: string",
                    "+ email: string",
                    "+ password: string",
                    "+ nombre: string",
                    "+ apellido: string",
                    "+ telefono: string"
                ],
                "methods": [
                    "+ ingresar_datos()",
                    "+ solicitar_registro()",
                    "+ renderizar_formulario()",
                    "+ mostrar_confirmacion()",
                    "+ mostrar_error_validacion()"
                ]
            },
            {
                "id": "ctrl_registro",
                "x": 380, "y": 350, "width": 330,
                "header": ["Control", "Registro"],
                "attributes": [
                    "- validador: ValidatorService",
                    "- hasher: Argon2Hasher"
                ],
                "methods": [
                    "+ registrar_usuario(dto_registro)",
                    "+ validar_formato_email(email)",
                    "+ verificar_unicidad_email(email)",
                    "+ validar_politica_password(pass)",
                    "+ hashear_password(pass)",
                    "+ asignar_rol_por_defecto(id_usr)",
                    "+ crear_perfil_persona(id_usr, datos)"
                ]
            },
            {
                "id": "ent_usuario",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_USUARIO"],
                "attributes": [
                    "+ ID_USUARIO: int [PK]",
                    "+ USERNAME: string",
                    "+ CORREO: string [UQ]",
                    "+ PASSWORD_HASH: string",
                    "+ ID_ROL: int [FK]",
                    "+ ID_PERSONA: int [FK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ ESTADO: string = 'ACTIVO'",
                    "+ CREATED_AT: timestamp"
                ],
                "methods": [
                    "+ buscar_por_email(correo)",
                    "+ insertar_usuario(datos)",
                    "+ actualizar_estado(id, estado)"
                ]
            },
            {
                "id": "ent_persona",
                "x": 1100, "y": 350, "width": 280,
                "header": ["T_PERSONA"],
                "attributes": [
                    "+ ID_PERSONA: int [PK]",
                    "+ NOMBRE: string",
                    "+ APELLIDO: string",
                    "+ TELEFONO: string",
                    "+ CREATED_AT: timestamp"
                ],
                "methods": [
                    "+ insertar_persona(datos)",
                    "+ buscar_por_id(id)"
                ]
            },
            {
                "id": "ent_rol",
                "x": 770, "y": 115, "width": 270,
                "header": ["T_ROL"],
                "attributes": [
                    "+ ID_ROL: int [PK]",
                    "+ NOMBRE_ROL: string",
                    "+ DESCRIPCION: string"
                ],
                "methods": [
                    "+ buscar_por_nombre(nom)"
                ]
            },
            {
                "id": "ent_bitacora",
                "x": 770, "y": 710, "width": 270,
                "header": ["T_BITACORA"],
                "attributes": [
                    "+ ID_BITACORA: bigint [PK]",
                    "+ FECHA_HORA: timestamp",
                    "+ ID_USUARIO: int [FK]",
                    "+ MODULO: string = 'AUTH'",
                    "+ ACCION: string = 'REGISTRO'",
                    "+ IP_ORIGEN: string",
                    "+ RESULTADO: string = 'EXITO'"
                ],
                "methods": [
                    "+ registrar_evento(accion, resultado)"
                ]
            }
        ],
        "connections": [
            {"from": "form_registro", "to": "ctrl_registro", "label": "solicita"},
            {"from": "ctrl_registro", "to": "ent_usuario", "label": "persiste"},
            {"from": "ent_usuario", "to": "ent_persona", "from_side": "right", "to_side": "left", "mult_from": "1", "mult_to": "1"},
            {"from": "ent_rol", "to": "ent_usuario", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_usuario", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU02: Iniciar sesión (P1)
# ==============================================================================
def get_cu02_clases():
    return {
        "id": "CU02_WM",
        "file_name": "CU02_WM_Iniciar_Sesion_Clases",
        "title": "CU02 W/M: Iniciar sesión — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Unificación Web (CU02W) y Móvil (CU02M) | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Usuario (Cliente, Personal, Administrador)",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_login",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Login_Autenticacion"],
                "attributes": [
                    "+ correo: string",
                    "+ password: string",
                    "+ huella_dispositivo: string"
                ],
                "methods": [
                    "+ capturar_credenciales()",
                    "+ solicitar_login()",
                    "+ renderizar_dashboard()",
                    "+ mostrar_error_credenciales()",
                    "+ mostrar_alerta_bloqueo()"
                ]
            },
            {
                "id": "ctrl_login",
                "x": 380, "y": 350, "width": 330,
                "header": ["Control", "Autenticacion"],
                "attributes": [
                    "- max_intentos: int = 5",
                    "- minutos_bloqueo: int = 15"
                ],
                "methods": [
                    "+ autenticar_usuario(correo, pass)",
                    "+ verificar_intentos_bloqueo(id_usr)",
                    "+ verificar_password_hash(pass, hash)",
                    "+ registrar_intento_fallido(id_usr)",
                    "+ resetear_intentos(id_usr)",
                    "+ verificar_hardware_confiable(id, fprint)",
                    "+ generar_token_jwt(id_usr, rol)"
                ]
            },
            {
                "id": "ent_usuario",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_USUARIO"],
                "attributes": [
                    "+ ID_USUARIO: int [PK]",
                    "+ USERNAME: string",
                    "+ CORREO: string [UQ]",
                    "+ PASSWORD_HASH: string",
                    "+ ID_EMPRESA: int [FK]",
                    "+ ID_ROL: int [FK]",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ buscar_por_email(correo)",
                    "+ actualizar_ultimo_acceso(id)"
                ]
            },
            {
                "id": "ent_seguridad",
                "x": 770, "y": 115, "width": 270,
                "header": ["T_SEGURIDAD_USUARIO"],
                "attributes": [
                    "+ ID_SEGURIDAD: int [PK]",
                    "+ ID_USUARIO: int [FK/UQ]",
                    "+ INTENTOS_FALLIDOS: int = 0",
                    "+ BLOQUEADO_HASTA: timestamp",
                    "+ FECHA_ACTUALIZACION: timestamp"
                ],
                "methods": [
                    "+ incrementar_intentos(id_usr)",
                    "+ bloquear_cuenta(id_usr, min)",
                    "+ resetear_contador(id_usr)"
                ]
            },
            {
                "id": "ent_dispositivo",
                "x": 1100, "y": 350, "width": 280,
                "header": ["T_DISPOSITIVO_USUARIO"],
                "attributes": [
                    "+ ID_DISPOSITIVO: int [PK]",
                    "+ ID_USUARIO: int [FK]",
                    "+ DEVICE_FINGERPRINT: string",
                    "+ VERIFICADO: boolean",
                    "+ ULTIMA_CONEXION: timestamp"
                ],
                "methods": [
                    "+ es_reconocido(id_usr, fprint)",
                    "+ registrar_dispositivo(id, fprint)"
                ]
            },
            {
                "id": "ent_bitacora",
                "x": 770, "y": 700, "width": 270,
                "header": ["T_BITACORA"],
                "attributes": [
                    "+ ID_BITACORA: bigint [PK]",
                    "+ FECHA_HORA: timestamp",
                    "+ ID_USUARIO: int [FK]",
                    "+ MODULO: string = 'AUTH'",
                    "+ ACCION: string = 'LOGIN'",
                    "+ RESULTADO: string"
                ],
                "methods": [
                    "+ registrar_evento(accion, resultado)"
                ]
            }
        ],
        "connections": [
            {"from": "form_login", "to": "ctrl_login", "label": "envía"},
            {"from": "ctrl_login", "to": "ent_usuario", "label": "consulta"},
            {"from": "ent_usuario", "to": "ent_seguridad", "from_side": "top", "to_side": "bottom", "mult_from": "1", "mult_to": "1"},
            {"from": "ent_usuario", "to": "ent_dispositivo", "from_side": "right", "to_side": "left", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_usuario", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU03: Gestionar perfil (P1)
# ==============================================================================
def get_cu03_clases():
    return {
        "id": "CU03_WM",
        "file_name": "CU03_WM_Gestionar_Perfil_Clases",
        "title": "CU03 W/M: Gestionar perfil — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Unificación Web (CU03W) y Móvil (CU03M) | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Usuario Autenticado",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_perfil",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Gestion_Perfil"],
                "attributes": [
                    "+ nombre: string",
                    "+ apellido: string",
                    "+ telefono: string",
                    "+ password_actual: string",
                    "+ password_nueva: string"
                ],
                "methods": [
                    "+ cargar_datos_perfil()",
                    "+ ingresar_modificaciones()",
                    "+ guardar_perfil()",
                    "+ mostrar_confirmacion()",
                    "+ mostrar_error_password()"
                ]
            },
            {
                "id": "ctrl_perfil",
                "x": 380, "y": 350, "width": 330,
                "header": ["Control", "Perfil"],
                "attributes": [
                    "- politica_pass: PasswordPolicy"
                ],
                "methods": [
                    "+ consultar_perfil(id_usuario)",
                    "+ actualizar_datos_personales(id, datos)",
                    "+ cambiar_password(id, actual, nueva)",
                    "+ revocar_sesiones_activas(id_usuario)"
                ]
            },
            {
                "id": "ent_usuario",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_USUARIO"],
                "attributes": [
                    "+ ID_USUARIO: int [PK]",
                    "+ USERNAME: string",
                    "+ CORREO: string [UQ]",
                    "+ PASSWORD_HASH: string",
                    "+ NOMBRE: string",
                    "+ APELLIDO: string",
                    "+ TELEFONO: string",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ buscar_por_id(id)",
                    "+ actualizar_datos(id, datos)",
                    "+ actualizar_password(id, nuevo_hash)"
                ]
            },
            {
                "id": "ent_seguridad",
                "x": 770, "y": 115, "width": 270,
                "header": ["T_SEGURIDAD_USUARIO"],
                "attributes": [
                    "+ ID_SEGURIDAD: int [PK]",
                    "+ ID_USUARIO: int [FK/UQ]",
                    "+ CODIGO_RECUPERACION: string",
                    "+ FECHA_ACTUALIZACION: timestamp"
                ],
                "methods": [
                    "+ registrar_cambio_credenciales(id)"
                ]
            },
            {
                "id": "ent_bitacora",
                "x": 770, "y": 700, "width": 270,
                "header": ["T_BITACORA"],
                "attributes": [
                    "+ ID_BITACORA: bigint [PK]",
                    "+ FECHA_HORA: timestamp",
                    "+ ID_USUARIO: int [FK]",
                    "+ MODULO: string = 'PERFIL'",
                    "+ ACCION: string = 'ACTUALIZAR'",
                    "+ RESULTADO: string = 'EXITO'"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_u)"
                ]
            }
        ],
        "connections": [
            {"from": "form_perfil", "to": "ctrl_perfil", "label": "solicita"},
            {"from": "ctrl_perfil", "to": "ent_usuario", "label": "actualiza"},
            {"from": "ent_usuario", "to": "ent_seguridad", "from_side": "top", "to_side": "bottom", "mult_from": "1", "mult_to": "1"},
            {"from": "ent_usuario", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU14: Gestionar usuarios y roles (P1)
# ==============================================================================
def get_cu14_clases():
    return {
        "id": "CU14_W",
        "file_name": "CU14_W_Gestionar_Usuarios_Roles_Clases",
        "title": "CU14 W: Gestionar usuarios y roles — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Estructura idéntica al modelo de referencia | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Administrador de Empresa / Superadmin",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_rol",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Asignar_Rol/Modificar_Rol"],
                "attributes": [
                    "+ id_rol",
                    "+ id_permiso",
                    "+ id_usuario"
                ],
                "methods": [
                    "+ crear_rol_db()"
                ]
            },
            {
                "id": "ctrl_registro",
                "x": 380, "y": 350, "width": 330,
                "header": ["Registro"],
                "attributes": [],
                "methods": [
                    "- obtener_Todos_los_roles()",
                    "- actualizar_rol_db()",
                    "- eliminar_rol_db()"
                ]
            },
            {
                "id": "ent_rol",
                "x": 770, "y": 350, "width": 270,
                "header": ["ROL"],
                "attributes": [
                    "+ id_rol",
                    "+ nombre_rol"
                ],
                "methods": []
            },
            {
                "id": "ent_permisos",
                "x": 770, "y": 115, "width": 270,
                "header": ["Permisos"],
                "attributes": [
                    "+ id_permiso",
                    "+ nombre_permiso",
                    "+ id_modulo"
                ],
                "methods": []
            },
            {
                "id": "ent_modulos",
                "x": 1100, "y": 115, "width": 280,
                "header": ["Modulos"],
                "attributes": [
                    "+ id_modulo",
                    "+ nombre_modulo"
                ],
                "methods": []
            },
            {
                "id": "ent_usuario",
                "x": 770, "y": 700, "width": 270,
                "header": ["USUARIO"],
                "attributes": [
                    "+ id_usuario",
                    "+ correo",
                    "+ username",
                    "+ contraseña",
                    "+ id_rol",
                    "+ id_persona",
                    "+ id_empresa"
                ],
                "methods": []
            },
            {
                "id": "ent_bitacora",
                "x": 1100, "y": 700, "width": 280,
                "header": ["T_BITACORA"],
                "attributes": [
                    "+ id_bitacora",
                    "+ fecha_hora",
                    "+ id_usuario",
                    "+ modulo = 'ROLES'",
                    "+ accion"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_rol)"
                ]
            }
        ],
        "connections": [
            {"from": "form_rol", "to": "ctrl_registro"},
            {"from": "ctrl_registro", "to": "ent_rol"},
            {"from": "ent_permisos", "to": "ent_modulos", "from_side": "right", "to_side": "left", "mult_from": "1", "mult_to": "1"},
            {"from": "ent_permisos", "to": "ent_rol", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "1..*"},
            {"from": "ent_rol", "to": "ent_usuario", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "1..*"},
            {"from": "ent_rol", "to": "ent_bitacora", "from_side": "right", "to_side": "left", "mult_from": "1", "mult_to": "0..*"}
        ]
    }
