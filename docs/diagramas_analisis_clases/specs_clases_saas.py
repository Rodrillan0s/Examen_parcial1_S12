#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Especificaciones de Diagramas de Análisis de Clases (UML / ICONIX VOPC) para el módulo SaaS y Operaciones Críticas:
- CU34: Gestionar planes de suscripción (P2 — Nuevo)
- CU35: Gestionar suscripciones empresariales (P2 — Nuevo)
- CU36: Consultar plan y límites de suscripción (P2 — Nuevo)
- CU41: Gestionar respaldos y restauraciones (P2 — Nuevo)
- CU43: Gestionar asignaciones de empleados a sucursales (P2 — Nuevo)
"""

# ==============================================================================
# CU34: Gestionar planes de suscripción (P2 — Nuevo)
# ==============================================================================
def get_cu34_clases():
    return {
        "id": "CU34_W",
        "file_name": "CU34_W_Gestionar_Planes_Suscripcion_Clases",
        "title": "CU34 W: Gestionar planes de suscripción — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Catálogo Inmutable de Planes SaaS | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Superadministrador de Plataforma",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_planes",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Planes_SaaS"],
                "attributes": [
                    "+ codigo_plan: string",
                    "+ nombre_plan: string",
                    "+ max_sucursales: int",
                    "+ reportes_generativos: boolean",
                    "+ activo: boolean"
                ],
                "methods": [
                    "+ consultar_catalogo_planes()",
                    "+ editar_disponibilidad_plan()",
                    "+ guardar_cambios_plan()",
                    "+ mostrar_alerta_codigo_arbitrario()"
                ]
            },
            {
                "id": "ctrl_planes",
                "x": 370, "y": 350, "width": 340,
                "header": ["Control", "Planes_SaaS"],
                "attributes": [
                    "- rbac_guard: PlatformScopeGuard"
                ],
                "methods": [
                    "+ listar_planes_disponibles()",
                    "+ validar_alcance_plataforma(token)",
                    "+ validar_codigo_fijo_y_limites(cod, dto)",
                    "+ actualizar_estado_plan(cod, act, desc)",
                    "+ verificar_contratos_vigentes(cod)"
                ]
            },
            {
                "id": "ent_plan",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_PLAN"],
                "attributes": [
                    "+ CODIGO: string [PK] (BASICO/PROF)",
                    "+ NOMBRE: string",
                    "+ MAX_SUCURSALES: int (2 o 10)",
                    "+ REPORTES_GENERATIVOS: boolean",
                    "+ ACTIVO: boolean = true"
                ],
                "methods": [
                    "+ buscar_todos()",
                    "+ buscar_por_codigo(codigo)",
                    "+ actualizar_estado(codigo, activo)"
                ]
            },
            {
                "id": "ent_suscripcion",
                "x": 1100, "y": 350, "width": 270,
                "header": ["T_SUSCRIPCION"],
                "attributes": [
                    "+ ID_SUSCRIPCION: bigint [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ CODIGO_PLAN: string [FK]",
                    "+ ESTADO: string",
                    "+ INICIO: timestamptz",
                    "+ FIN: timestamptz"
                ],
                "methods": [
                    "+ contar_vigentes_por_plan(codigo)"
                ]
            },
            {
                "id": "ent_empresa",
                "x": 1100, "y": 115, "width": 270,
                "header": ["EMPRESA"],
                "attributes": [
                    "+ ID_EMPRESA: int [PK]",
                    "+ NOMBRE_EMPRESA: string",
                    "+ ESTADO: string"
                ],
                "methods": []
            },
            {
                "id": "ent_bitacora",
                "x": 770, "y": 700, "width": 270,
                "header": ["T_BITACORA"],
                "attributes": [
                    "+ ID_BITACORA: bigint [PK]",
                    "+ FECHA_HORA: timestamp",
                    "+ ID_USUARIO: int [FK]",
                    "+ MODULO: string = 'SAAS_PLANES'",
                    "+ ACCION: string = 'ACTUALIZAR_PLAN'",
                    "+ RESULTADO: string"
                ],
                "methods": [
                    "+ registrar_evento(accion, codigo)"
                ]
            }
        ],
        "connections": [
            {"from": "form_planes", "to": "ctrl_planes", "label": "solicita"},
            {"from": "ctrl_planes", "to": "ent_plan", "label": "persiste"},
            {"from": "ent_plan", "to": "ent_suscripcion", "from_side": "right", "to_side": "left", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_suscripcion", "to": "ent_empresa", "from_side": "top", "to_side": "bottom", "mult_from": "0..*", "mult_to": "1"},
            {"from": "ent_plan", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU35: Gestionar suscripciones empresariales (P2 — Nuevo)
# ==============================================================================
def get_cu35_clases():
    return {
        "id": "CU35_W",
        "file_name": "CU35_W_Gestionar_Suscripciones_Empresariales_Clases",
        "title": "CU35 W: Gestionar suscripciones empresariales — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Asignación Administrativa y Control de Vigencia | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Superadministrador de Plataforma",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_suscripcion",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Suscripcion_Empresarial"],
                "attributes": [
                    "+ id_empresa: int",
                    "+ codigo_plan: string",
                    "+ fecha_inicio: date",
                    "+ fecha_fin: date",
                    "+ motivo: string",
                    "+ estado: string"
                ],
                "methods": [
                    "+ seleccionar_empresa()",
                    "+ solicitar_asignacion_plan()",
                    "+ confirmar_periodo()",
                    "+ cancelar_suscripcion()",
                    "+ mostrar_error_capacidad()"
                ]
            },
            {
                "id": "ctrl_suscripcion",
                "x": 370, "y": 350, "width": 340,
                "header": ["Control", "Suscripciones"],
                "attributes": [
                    "- validator: SubscriptionValidator"
                ],
                "methods": [
                    "+ crear_suscripcion(dto)",
                    "+ validar_rango_fechas(ini, fin)",
                    "+ obtener_limites_plan(codigo)",
                    "+ contar_sucursales_activas(id_empresa)",
                    "+ insertar_periodo_suscripcion(dto)",
                    "+ cancelar_suscripcion_logica(id)"
                ]
            },
            {
                "id": "ent_suscripcion",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_SUSCRIPCION"],
                "attributes": [
                    "+ ID_SUSCRIPCION: bigint [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ CODIGO_PLAN: string [FK]",
                    "+ INICIO: timestamptz",
                    "+ FIN: timestamptz",
                    "+ ESTADO: string = 'ACTIVA'",
                    "+ MOTIVO: text",
                    "+ CREADO_POR: int [FK]",
                    "+ CREADO_EN: timestamptz"
                ],
                "methods": [
                    "+ insertar_periodo(datos)",
                    "+ actualizar_estado(id, estado)",
                    "+ buscar_por_empresa(id_emp)"
                ]
            },
            {
                "id": "ent_plan",
                "x": 770, "y": 115, "width": 270,
                "header": ["T_PLAN"],
                "attributes": [
                    "+ CODIGO: string [PK]",
                    "+ NOMBRE: string",
                    "+ MAX_SUCURSALES: int",
                    "+ ACTIVO: boolean"
                ],
                "methods": [
                    "+ obtener_limites(codigo)"
                ]
            },
            {
                "id": "ent_empresa",
                "x": 1100, "y": 350, "width": 270,
                "header": ["EMPRESA"],
                "attributes": [
                    "+ ID_EMPRESA: int [PK]",
                    "+ NOMBRE_EMPRESA: string",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ existe_empresa(id)"
                ]
            },
            {
                "id": "ent_sucursal",
                "x": 1100, "y": 115, "width": 270,
                "header": ["T_SUCURSAL"],
                "attributes": [
                    "+ ID_SUCURSAL: int [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ NOMBRE: string",
                    "+ ACTIVO: boolean"
                ],
                "methods": [
                    "+ contar_activas(id_empresa)"
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
                    "+ ID_EMPRESA: int [FK]",
                    "+ MODULO: string = 'SUSCRIPCION'",
                    "+ ACCION: string = 'ASIGNAR_PLAN'"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_emp)"
                ]
            }
        ],
        "connections": [
            {"from": "form_suscripcion", "to": "ctrl_suscripcion", "label": "solicita"},
            {"from": "ctrl_suscripcion", "to": "ent_suscripcion", "label": "persiste"},
            {"from": "ent_plan", "to": "ent_suscripcion", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_empresa", "to": "ent_suscripcion", "from_side": "left", "to_side": "right", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_empresa", "to": "ent_sucursal", "from_side": "top", "to_side": "bottom", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_suscripcion", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU36: Consultar plan y límites de suscripción (P2 — Nuevo)
# ==============================================================================
def get_cu36_clases():
    return {
        "id": "CU36_W",
        "file_name": "CU36_W_Consultar_Plan_Limites_Suscripcion_Clases",
        "title": "CU36 W: Consultar plan y límites de suscripción — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Supervisión de Cuotas Operativas y Métricas | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Administrador de Tienda",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_mi_plan",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Mi_Plan_Limites"],
                "attributes": [
                    "+ id_empresa: int",
                    "+ plan_nombre: string",
                    "+ max_sucursales: int",
                    "+ sucursales_en_uso: int",
                    "+ sucursales_disponibles: int",
                    "+ reportes_ia_habilitados: boolean"
                ],
                "methods": [
                    "+ solicitar_consulta_mi_plan()",
                    "+ desplegar_indicadores_uso()",
                    "+ mostrar_alerta_vencimiento()"
                ]
            },
            {
                "id": "ctrl_consulta_plan",
                "x": 370, "y": 350, "width": 340,
                "header": ["Control", "Consulta_Plan"],
                "attributes": [
                    "- jwt_decoder: JwtSecurityContext"
                ],
                "methods": [
                    "+ consultar_plan_y_limites(token)",
                    "+ extraer_id_empresa(token)",
                    "+ buscar_suscripcion_vigente(id, fecha)",
                    "+ contar_sucursales_activas(id)",
                    "+ calcular_disponibilidad(max, act)"
                ]
            },
            {
                "id": "ent_suscripcion",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_SUSCRIPCION"],
                "attributes": [
                    "+ ID_SUSCRIPCION: bigint [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ CODIGO_PLAN: string [FK]",
                    "+ INICIO: timestamptz",
                    "+ FIN: timestamptz",
                    "+ ESTADO: string = 'ACTIVA'"
                ],
                "methods": [
                    "+ buscar_vigente(id_emp, fecha)"
                ]
            },
            {
                "id": "ent_plan",
                "x": 770, "y": 115, "width": 270,
                "header": ["T_PLAN"],
                "attributes": [
                    "+ CODIGO: string [PK]",
                    "+ NOMBRE: string",
                    "+ MAX_SUCURSALES: int",
                    "+ REPORTES_GENERATIVOS: boolean",
                    "+ ACTIVO: boolean"
                ],
                "methods": [
                    "+ buscar_por_codigo(codigo)"
                ]
            },
            {
                "id": "ent_empresa",
                "x": 1100, "y": 350, "width": 270,
                "header": ["EMPRESA"],
                "attributes": [
                    "+ ID_EMPRESA: int [PK]",
                    "+ NOMBRE_EMPRESA: string",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ verificar_activa(id)"
                ]
            },
            {
                "id": "ent_sucursal",
                "x": 1100, "y": 115, "width": 270,
                "header": ["T_SUCURSAL"],
                "attributes": [
                    "+ ID_SUCURSAL: int [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ ACTIVO: boolean"
                ],
                "methods": [
                    "+ contar_activas(id_emp)"
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
                    "+ MODULO: string = 'SAAS'",
                    "+ ACCION: string = 'CONSULTA_PLAN'"
                ],
                "methods": []
            }
        ],
        "connections": [
            {"from": "form_mi_plan", "to": "ctrl_consulta_plan", "label": "solicita"},
            {"from": "ctrl_consulta_plan", "to": "ent_suscripcion", "label": "consulta"},
            {"from": "ent_plan", "to": "ent_suscripcion", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_suscripcion", "to": "ent_empresa", "from_side": "right", "to_side": "left", "mult_from": "0..*", "mult_to": "1"},
            {"from": "ent_empresa", "to": "ent_sucursal", "from_side": "top", "to_side": "bottom", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_suscripcion", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU41: Gestionar respaldos y restauraciones (P2 — Nuevo)
# ==============================================================================
def get_cu41_clases():
    return {
        "id": "CU41_W",
        "file_name": "CU41_W_Gestionar_Respaldos_Restauraciones_Clases",
        "title": "CU41 W: Gestionar respaldos y restauraciones — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Infraestructura Crítica y Recuperación de Datos | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Superadministrador del Sistema",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_respaldos",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Respaldos_Restauracion"],
                "attributes": [
                    "+ id_respaldo: int",
                    "+ nombre_archivo: string",
                    "+ tipo_respaldo: string",
                    "+ checksum_sha256: string",
                    "+ tamanio_bytes: bigint",
                    "+ motivo: string"
                ],
                "methods": [
                    "+ solicitar_respaldo()",
                    "+ solicitar_restauracion()",
                    "+ confirmar_doble_factor()",
                    "+ mostrar_confirmacion()",
                    "+ mostrar_error_motor()"
                ]
            },
            {
                "id": "ctrl_respaldos",
                "x": 370, "y": 350, "width": 340,
                "header": ["Control", "Respaldos"],
                "attributes": [
                    "- security: SuperadminSecurityService"
                ],
                "methods": [
                    "+ ejecutar_respaldo(dto)",
                    "+ validar_privilegios_superadmin(token)",
                    "+ ejecutar_pg_dump(esquemas_db)",
                    "+ calcular_checksum_sha256(archivo)",
                    "+ guardar_metadatos_respaldo(datos)",
                    "+ ejecutar_pg_restore(id_respaldo)"
                ]
            },
            {
                "id": "ent_respaldo",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_RESPALDO_SISTEMA"],
                "attributes": [
                    "+ ID_RESPALDO: int [PK]",
                    "+ NOMBRE_ARCHIVO: string",
                    "+ TIPO_RESPALDO: string",
                    "+ CHECKSUM_SHA256: string",
                    "+ TAMANIO_BYTES: bigint",
                    "+ MOTIVO: text",
                    "+ CREADO_POR: int [FK]",
                    "+ FECHA_CREACION: timestamp"
                ],
                "methods": [
                    "+ insertar(datos)",
                    "+ buscar_por_id(id)",
                    "+ listar_historial()"
                ]
            },
            {
                "id": "ent_seguridad",
                "x": 770, "y": 115, "width": 270,
                "header": ["T_SEGURIDAD_USUARIO"],
                "attributes": [
                    "+ ID_SEGURIDAD: int [PK]",
                    "+ ID_USUARIO: int [FK/UQ]",
                    "+ CODIGO_VERIFICACION: string"
                ],
                "methods": [
                    "+ validar_mfa(id_usr, codigo)"
                ]
            },
            {
                "id": "ent_usuario",
                "x": 1100, "y": 350, "width": 270,
                "header": ["T_USUARIO"],
                "attributes": [
                    "+ ID_USUARIO: int [PK]",
                    "+ USERNAME: string",
                    "+ ID_ROL: int [FK]"
                ],
                "methods": []
            },
            {
                "id": "ent_bitacora",
                "x": 770, "y": 700, "width": 270,
                "header": ["T_BITACORA"],
                "attributes": [
                    "+ ID_BITACORA: bigint [PK]",
                    "+ FECHA_HORA: timestamp",
                    "+ ID_USUARIO: int [FK]",
                    "+ MODULO: string = 'BACKUP'",
                    "+ ACCION: string = 'RESPALDO_SISTEMA'",
                    "+ RESULTADO: string"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_resp)"
                ]
            }
        ],
        "connections": [
            {"from": "form_respaldos", "to": "ctrl_respaldos", "label": "solicita"},
            {"from": "ctrl_respaldos", "to": "ent_respaldo", "label": "ejecuta"},
            {"from": "ent_seguridad", "to": "ent_respaldo", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "1"},
            {"from": "ent_respaldo", "to": "ent_usuario", "from_side": "right", "to_side": "left", "mult_from": "0..*", "mult_to": "1"},
            {"from": "ent_respaldo", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU43: Gestionar asignaciones de empleados a sucursales (P2 — Nuevo)
# ==============================================================================
def get_cu43_clases():
    return {
        "id": "CU43_W",
        "file_name": "CU43_W_Gestionar_Asignaciones_Empleados_Sucursales_Clases",
        "title": "CU43 W: Gestionar asignaciones de empleados a sucursales — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Asignación Multitenant Atómica y Alcance RBAC | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Administrador de Empresa",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_asignaciones",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Asignacion_Sucursales"],
                "attributes": [
                    "+ id_empleado: int",
                    "+ id_usuario: int",
                    "+ lista_sucursales: int[]",
                    "+ motivo_cambio: string"
                ],
                "methods": [
                    "+ abrir_modulo_asignaciones()",
                    "+ marcar_sucursales_permitidas()",
                    "+ guardar_asignaciones()",
                    "+ revocar_todos_accesos()",
                    "+ mostrar_error_sucursal_ajena()"
                ]
            },
            {
                "id": "ctrl_asignaciones",
                "x": 370, "y": 350, "width": 340,
                "header": ["Control", "Asignaciones"],
                "attributes": [
                    "- rbac_manager: AccessManagerService"
                ],
                "methods": [
                    "+ consultar_asignaciones(id_empleado)",
                    "+ actualizar_asignaciones(id_emp, id_u, ids)",
                    "+ validar_pertenencia_empresa(id_suc, id_emp)",
                    "+ reemplazar_atomicamente(id_u, ids)",
                    "+ verificar_integridad_laboral(id_emp)"
                ]
            },
            {
                "id": "ent_usrsuc",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_USUARIO_SUCURSAL"],
                "attributes": [
                    "+ ID_USUARIO: int [PK/FK]",
                    "+ ID_SUCURSAL: int [PK/FK]",
                    "+ CREATED_AT: timestamp"
                ],
                "methods": [
                    "+ buscar_por_usuario(id_u)",
                    "+ eliminar_por_usuario(id_u)",
                    "+ insertar_lote(id_u, lista_suc)"
                ]
            },
            {
                "id": "ent_empleado",
                "x": 770, "y": 115, "width": 270,
                "header": ["T_EMPLEADO / T_USUARIO"],
                "attributes": [
                    "+ ID_USUARIO: int [PK]",
                    "+ USERNAME: string",
                    "+ NOMBRE: string",
                    "+ APELLIDO: string",
                    "+ ID_EMPRESA: int [FK]",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ buscar_empleado(id_u)"
                ]
            },
            {
                "id": "ent_sucursal",
                "x": 1100, "y": 350, "width": 270,
                "header": ["T_SUCURSAL"],
                "attributes": [
                    "+ ID_SUCURSAL: int [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ NOMBRE: string",
                    "+ ACTIVO: boolean = true"
                ],
                "methods": [
                    "+ pertenece_a_empresa(id_suc, id_emp)"
                ]
            },
            {
                "id": "ent_empresa",
                "x": 1100, "y": 115, "width": 270,
                "header": ["EMPRESA"],
                "attributes": [
                    "+ ID_EMPRESA: int [PK]",
                    "+ NOMBRE_EMPRESA: string"
                ],
                "methods": []
            },
            {
                "id": "ent_bitacora",
                "x": 770, "y": 700, "width": 270,
                "header": ["T_BITACORA"],
                "attributes": [
                    "+ ID_BITACORA: bigint [PK]",
                    "+ FECHA_HORA: timestamp",
                    "+ ID_USUARIO: int [FK]",
                    "+ MODULO: string = 'RBAC'",
                    "+ ACCION: string = 'ASIGN_SUCURSAL'",
                    "+ DESCRIPCION: text"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_u)"
                ]
            }
        ],
        "connections": [
            {"from": "form_asignaciones", "to": "ctrl_asignaciones", "label": "solicita"},
            {"from": "ctrl_asignaciones", "to": "ent_usrsuc", "label": "actualiza"},
            {"from": "ent_empleado", "to": "ent_usrsuc", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_usrsuc", "to": "ent_sucursal", "from_side": "right", "to_side": "left", "mult_from": "0..*", "mult_to": "1"},
            {"from": "ent_empresa", "to": "ent_sucursal", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_usrsuc", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }
