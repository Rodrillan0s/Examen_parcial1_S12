#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Especificaciones de Diagramas de Análisis de Clases (UML / ICONIX VOPC) para el módulo de Catálogo y Sucursales:
- CU15: Gestionar empresas SaaS (P1 — Refactorización)
- CU16: Gestionar sucursales y ciudades (P1)
- CU17: Gestionar productos (P1)
- CU18: Gestionar categorías (P1)
- CU19: Gestionar tallas y colores (P1)
- CU20: Gestionar temporadas y colecciones (P1)
- CU21: Gestionar proveedores (P1)
"""

# ==============================================================================
# CU15: Gestionar empresas SaaS (P1 — Refactorización)
# ==============================================================================
def get_cu15_clases():
    return {
        "id": "CU15_W",
        "file_name": "CU15_W_Gestionar_Empresas_SaaS_Clases",
        "title": "CU15 W: Gestionar empresas SaaS — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Administración de Empresas y Tenancy | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Superadministrador de Plataforma",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_empresas",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Empresas_SaaS"],
                "attributes": [
                    "+ id_empresa: int",
                    "+ nit: string",
                    "+ razon_social: string",
                    "+ direccion: string",
                    "+ estado: string"
                ],
                "methods": [
                    "+ solicitar_creacion_empresa()",
                    "+ editar_empresa()",
                    "+ desactivar_empresa_logica()",
                    "+ mostrar_error_nit_duplicado()"
                ]
            },
            {
                "id": "ctrl_empresas",
                "x": 380, "y": 350, "width": 330,
                "header": ["Control", "Empresas_SaaS"],
                "attributes": [
                    "- scope_validator: PlatformScopeGuard"
                ],
                "methods": [
                    "+ guardar_empresa_saas(dto_empresa)",
                    "+ validar_alcance_plataforma(token)",
                    "+ buscar_por_nit(nit)",
                    "+ inicializar_esquema_tenant(id_emp)",
                    "+ desactivar_empresa_baja_logica(id)",
                    "+ verificar_integridad_sucursales(id)"
                ]
            },
            {
                "id": "ent_empresa",
                "x": 770, "y": 350, "width": 270,
                "header": ["EMPRESA"],
                "attributes": [
                    "+ ID_EMPRESA: int [PK]",
                    "+ NOMBRE_EMPRESA: string",
                    "+ NIT: string [UQ]",
                    "+ ESTADO: string = 'ACTIVO'",
                    "+ CREATED_AT: timestamp"
                ],
                "methods": [
                    "+ buscar_por_nit(nit)",
                    "+ insertar(datos)",
                    "+ baja_logica(id_empresa)"
                ]
            },
            {
                "id": "ent_sucursal",
                "x": 1100, "y": 350, "width": 280,
                "header": ["T_SUCURSAL"],
                "attributes": [
                    "+ ID_SUCURSAL: int [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ NOMBRE: string",
                    "+ DIRECCION: string",
                    "+ ACTIVO: boolean = true"
                ],
                "methods": [
                    "+ contar_por_empresa(id_empresa)",
                    "+ desactivar_todas(id_empresa)"
                ]
            },
            {
                "id": "ent_suscripcion",
                "x": 770, "y": 115, "width": 270,
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
                    "+ buscar_activa(id_empresa)"
                ]
            },
            {
                "id": "ent_plan",
                "x": 1100, "y": 115, "width": 280,
                "header": ["T_PLAN"],
                "attributes": [
                    "+ CODIGO: string [PK]",
                    "+ NOMBRE: string",
                    "+ MAX_SUCURSALES: int",
                    "+ REPORTES_GENERATIVOS: boolean",
                    "+ ACTIVO: boolean"
                ],
                "methods": [
                    "+ obtener_limites(codigo)"
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
                    "+ MODULO: string = 'SAAS'",
                    "+ ACCION: string = 'GESTION_EMPRESA'",
                    "+ RESULTADO: string"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_emp)"
                ]
            }
        ],
        "connections": [
            {"from": "form_empresas", "to": "ctrl_empresas", "label": "solicita"},
            {"from": "ctrl_empresas", "to": "ent_empresa", "label": "persiste"},
            {"from": "ent_empresa", "to": "ent_sucursal", "from_side": "right", "to_side": "left", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_empresa", "to": "ent_suscripcion", "from_side": "top", "to_side": "bottom", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_suscripcion", "to": "ent_plan", "from_side": "right", "to_side": "left", "mult_from": "0..*", "mult_to": "1"},
            {"from": "ent_empresa", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU16: Gestionar sucursales y ciudades (P1)
# ==============================================================================
def get_cu16_clases():
    return {
        "id": "CU16_W",
        "file_name": "CU16_W_Gestionar_Sucursales_Ciudades_Clases",
        "title": "CU16 W: Gestionar sucursales y ciudades — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Límites por Plan de Suscripción | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Administrador de Empresa",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_sucursales",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Sucursales"],
                "attributes": [
                    "+ id_sucursal: int",
                    "+ codigo_sucursal: string",
                    "+ nombre: string",
                    "+ direccion: string",
                    "+ id_ciudad: int",
                    "+ activo: boolean"
                ],
                "methods": [
                    "+ ingresar_datos_sucursal()",
                    "+ guardar_sucursal()",
                    "+ alternar_estado_activo()",
                    "+ mostrar_alerta_limite_plan()"
                ]
            },
            {
                "id": "ctrl_sucursales",
                "x": 380, "y": 350, "width": 330,
                "header": ["Control", "Sucursales"],
                "attributes": [
                    "- saas_service: SaasPlanService"
                ],
                "methods": [
                    "+ crear_sucursal(id_empresa, dto)",
                    "+ consultar_limite_plan(id_empresa)",
                    "+ contar_sucursales_activas(id_emp)",
                    "+ insertar_sucursal(datos)",
                    "+ actualizar_estado_sucursal(id, act)"
                ]
            },
            {
                "id": "ent_sucursal",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_SUCURSAL"],
                "attributes": [
                    "+ ID_SUCURSAL: int [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ NOMBRE: string",
                    "+ DIRECCION: string",
                    "+ ACTIVO: boolean = true",
                    "+ CREATED_AT: timestamp"
                ],
                "methods": [
                    "+ insertar(datos)",
                    "+ contar_activas(id_empresa)",
                    "+ actualizar_estado(id, activo)"
                ]
            },
            {
                "id": "ent_empresa",
                "x": 770, "y": 115, "width": 270,
                "header": ["EMPRESA"],
                "attributes": [
                    "+ ID_EMPRESA: int [PK]",
                    "+ NOMBRE_EMPRESA: string",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ buscar_por_id(id)"
                ]
            },
            {
                "id": "ent_plan",
                "x": 1100, "y": 115, "width": 280,
                "header": ["T_PLAN"],
                "attributes": [
                    "+ CODIGO: string [PK]",
                    "+ NOMBRE: string",
                    "+ MAX_SUCURSALES: int (2 o 10)",
                    "+ ACTIVO: boolean"
                ],
                "methods": [
                    "+ obtener_max_sucursales(codigo)"
                ]
            },
            {
                "id": "ent_suscripcion",
                "x": 1100, "y": 350, "width": 280,
                "header": ["T_SUSCRIPCION"],
                "attributes": [
                    "+ ID_SUSCRIPCION: bigint [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ CODIGO_PLAN: string [FK]",
                    "+ ESTADO: string = 'ACTIVA'"
                ],
                "methods": [
                    "+ buscar_vigente(id_empresa)"
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
                    "+ ID_SUCURSAL: int [FK]",
                    "+ MODULO: string = 'SUCURSAL'",
                    "+ ACCION: string = 'CREAR_SUCURSAL'"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_suc)"
                ]
            }
        ],
        "connections": [
            {"from": "form_sucursales", "to": "ctrl_sucursales", "label": "solicita"},
            {"from": "ctrl_sucursales", "to": "ent_sucursal", "label": "persiste"},
            {"from": "ent_empresa", "to": "ent_sucursal", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_empresa", "to": "ent_plan", "from_side": "right", "to_side": "left", "mult_from": "1", "mult_to": "1"},
            {"from": "ent_plan", "to": "ent_suscripcion", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_sucursal", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU17: Gestionar productos (P1)
# ==============================================================================
def get_cu17_clases():
    return {
        "id": "CU17_W",
        "file_name": "CU17_W_Gestionar_Productos_Clases",
        "title": "CU17 W: Gestionar productos — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Catálogo Maestro de Prendas | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Administrador de Tienda / Encargado de Sucursal",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_productos",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Productos"],
                "attributes": [
                    "+ id_producto: int",
                    "+ codigo_sku: string",
                    "+ nombre: string",
                    "+ descripcion: string",
                    "+ precio_base: decimal",
                    "+ id_categoria: int",
                    "+ id_proveedor: int"
                ],
                "methods": [
                    "+ ingresar_datos_producto()",
                    "+ guardar_producto()",
                    "+ asociar_categoria()",
                    "+ asociar_proveedor()",
                    "+ mostrar_error_sku_duplicado()"
                ]
            },
            {
                "id": "ctrl_productos",
                "x": 380, "y": 350, "width": 330,
                "header": ["Control", "Productos"],
                "attributes": [
                    "- catalog_service: ProductCatalogService"
                ],
                "methods": [
                    "+ crear_producto(id_empresa, dto)",
                    "+ validar_sku_unico(id_empresa, sku)",
                    "+ verificar_precio_positivo(precio)",
                    "+ insertar_producto(datos)",
                    "+ actualizar_producto(id, datos)",
                    "+ dar_de_baja_producto(id)"
                ]
            },
            {
                "id": "ent_producto",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_PRODUCTO"],
                "attributes": [
                    "+ ID_PRODUCTO: int [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ ID_CATEGORIA: int [FK]",
                    "+ ID_PROVEEDOR: int [FK]",
                    "+ NOMBRE: string",
                    "+ DESCRIPCION: string",
                    "+ PRECIO_BASE: decimal",
                    "+ ESTADO: string = 'ACTIVO'"
                ],
                "methods": [
                    "+ buscar_por_sku(id_emp, sku)",
                    "+ insertar(datos)",
                    "+ actualizar(id, datos)"
                ]
            },
            {
                "id": "ent_categoria",
                "x": 770, "y": 115, "width": 270,
                "header": ["T_CATEGORIA"],
                "attributes": [
                    "+ ID_CATEGORIA: int [PK]",
                    "+ NOMBRE: string",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ existe_categoria(id)"
                ]
            },
            {
                "id": "ent_proveedor",
                "x": 1100, "y": 350, "width": 280,
                "header": ["T_PROVEEDOR"],
                "attributes": [
                    "+ ID_PROVEEDOR: int [PK]",
                    "+ RAZON_SOCIAL: string",
                    "+ NIT_RUC: string",
                    "+ ACTIVO: boolean"
                ],
                "methods": [
                    "+ existe_proveedor(id)"
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
                    "+ MODULO: string = 'PRODUCTO'",
                    "+ ACCION: string = 'REG_PRODUCTO'"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_prod)"
                ]
            }
        ],
        "connections": [
            {"from": "form_productos", "to": "ctrl_productos", "label": "solicita"},
            {"from": "ctrl_productos", "to": "ent_producto", "label": "persiste"},
            {"from": "ent_categoria", "to": "ent_producto", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_producto", "to": "ent_proveedor", "from_side": "right", "to_side": "left", "mult_from": "0..*", "mult_to": "0..1"},
            {"from": "ent_producto", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU18: Gestionar categorías (P1)
# ==============================================================================
def get_cu18_clases():
    return {
        "id": "CU18_W",
        "file_name": "CU18_W_Gestionar_Categorias_Clases",
        "title": "CU18 W: Gestionar categorías — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Estructura Jerárquica de Categorías | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Administrador de Tienda",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_categorias",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Categorias"],
                "attributes": [
                    "+ id_categoria: int",
                    "+ nombre: string",
                    "+ descripcion: string",
                    "+ id_categoria_padre: int",
                    "+ estado: string"
                ],
                "methods": [
                    "+ capturar_categoria()",
                    "+ guardar_categoria()",
                    "+ asignar_jerarquia()",
                    "+ eliminar_categoria()",
                    "+ mostrar_error_asociaciones()"
                ]
            },
            {
                "id": "ctrl_categorias",
                "x": 380, "y": 350, "width": 330,
                "header": ["Control", "Categorias"],
                "attributes": [
                    "- category_service: CategoryService"
                ],
                "methods": [
                    "+ crear_categoria(dto_categoria)",
                    "+ validar_nombre_categoria(nombre)",
                    "+ verificar_no_circular(id, id_padre)",
                    "+ verificar_productos_asociados(id)",
                    "+ insertar_categoria(datos)",
                    "+ actualizar_categoria(id, datos)"
                ]
            },
            {
                "id": "ent_categoria",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_CATEGORIA"],
                "attributes": [
                    "+ ID_CATEGORIA: int [PK]",
                    "+ ID_CATEGORIA_PADRE: int [FK]",
                    "+ NOMBRE: string [UQ]",
                    "+ DESCRIPCION: string",
                    "+ ESTADO: string = 'ACTIVO'"
                ],
                "methods": [
                    "+ buscar_por_nombre(nombre)",
                    "+ insertar(datos)",
                    "+ eliminar(id)"
                ]
            },
            {
                "id": "ent_producto",
                "x": 1100, "y": 350, "width": 280,
                "header": ["T_PRODUCTO"],
                "attributes": [
                    "+ ID_PRODUCTO: int [PK]",
                    "+ ID_CATEGORIA: int [FK]",
                    "+ NOMBRE: string",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ contar_por_categoria(id_cat)"
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
                    "+ MODULO: string = 'CATEGORIA'",
                    "+ ACCION: string = 'GEST_CATEGORIA'"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_cat)"
                ]
            }
        ],
        "connections": [
            {"from": "form_categorias", "to": "ctrl_categorias", "label": "solicita"},
            {"from": "ctrl_categorias", "to": "ent_categoria", "label": "persiste"},
            {"points": [(950, 350), (950, 280), (860, 280), (860, 350)], "mult_from": {"text": "0..1", "pos": (955, 305)}, "mult_to": {"text": "0..*", "pos": (830, 305)}},
            {"from": "ent_categoria", "to": "ent_producto", "from_side": "right", "to_side": "left", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_categoria", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU19: Gestionar tallas y colores (P1)
# ==============================================================================
def get_cu19_clases():
    return {
        "id": "CU19_W",
        "file_name": "CU19_W_Gestionar_Tallas_Colores_Clases",
        "title": "CU19 W: Gestionar tallas y colores — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Variantes de Prendas | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Administrador de Tienda",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_variantes",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Tallas_Colores"],
                "attributes": [
                    "+ id_talla: int",
                    "+ nombre_talla: string",
                    "+ id_color: int",
                    "+ nombre_color: string",
                    "+ codigo_hex: string"
                ],
                "methods": [
                    "+ capturar_talla()",
                    "+ capturar_color()",
                    "+ guardar_variante()",
                    "+ asociar_a_producto()",
                    "+ mostrar_alerta_duplicado()"
                ]
            },
            {
                "id": "ctrl_variantes",
                "x": 380, "y": 350, "width": 330,
                "header": ["Control", "Variantes"],
                "attributes": [
                    "- variant_service: VariantService"
                ],
                "methods": [
                    "+ registrar_talla(nombre)",
                    "+ registrar_color(nombre, hex)",
                    "+ crear_variante_producto(id_p, id_t, id_c)",
                    "+ validar_unicidad_variante(id_p, id_t, id_c)"
                ]
            },
            {
                "id": "ent_variante",
                "x": 770, "y": 350, "width": 285,
                "header": ["T_PRODUCTO_VARIANTE"],
                "attributes": [
                    "+ ID_VARIANTE: int [PK]",
                    "+ ID_PRODUCTO: int [FK]",
                    "+ ID_TALLA: int [FK]",
                    "+ ID_COLOR: int [FK]",
                    "+ PRECIO_ADICIONAL: decimal",
                    "+ SKU_VARIANTE: string",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ insertar_variante(datos)",
                    "+ verificar_duplicado(id_p, id_t, id_c)"
                ]
            },
            {
                "id": "ent_talla",
                "x": 770, "y": 115, "width": 270,
                "header": ["T_TALLA"],
                "attributes": [
                    "+ ID_TALLA: int [PK]",
                    "+ NOMBRE: string [UQ]",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ buscar_por_nombre(nom)"
                ]
            },
            {
                "id": "ent_color",
                "x": 1100, "y": 115, "width": 280,
                "header": ["T_COLOR"],
                "attributes": [
                    "+ ID_COLOR: int [PK]",
                    "+ NOMBRE: string",
                    "+ CODIGO_HEX: string"
                ],
                "methods": [
                    "+ buscar_por_nombre(nom)"
                ]
            },
            {
                "id": "ent_producto",
                "x": 1100, "y": 350, "width": 280,
                "header": ["T_PRODUCTO"],
                "attributes": [
                    "+ ID_PRODUCTO: int [PK]",
                    "+ NOMBRE: string",
                    "+ PRECIO_BASE: decimal"
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
                    "+ MODULO: string = 'VARIANTES'",
                    "+ ACCION: string = 'CREAR_VARIANTE'"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_var)"
                ]
            }
        ],
        "connections": [
            {"from": "form_variantes", "to": "ctrl_variantes", "label": "solicita"},
            {"from": "ctrl_variantes", "to": "ent_variante", "label": "persiste"},
            {"from": "ent_talla", "to": "ent_variante", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_color", "to": "ent_variante", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_producto", "to": "ent_variante", "from_side": "left", "to_side": "right", "mult_from": "1", "mult_to": "1..*"},
            {"from": "ent_variante", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU20: Gestionar temporadas y colecciones (P1)
# ==============================================================================
def get_cu20_clases():
    return {
        "id": "CU20_W",
        "file_name": "CU20_W_Gestionar_Temporadas_Colecciones_Clases",
        "title": "CU20 W: Gestionar temporadas y colecciones — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Periodos Comerciales y Agrupaciones | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Administrador de Tienda",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_temporadas",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Temporadas_Colecciones"],
                "attributes": [
                    "+ id_temporada: int",
                    "+ nombre_temporada: string",
                    "+ fecha_inicio: date",
                    "+ fecha_fin: date",
                    "+ id_coleccion: int",
                    "+ nombre_coleccion: string"
                ],
                "methods": [
                    "+ ingresar_datos_temporada()",
                    "+ ingresar_datos_coleccion()",
                    "+ guardar_temporada()",
                    "+ guardar_coleccion()",
                    "+ mostrar_error_fechas()"
                ]
            },
            {
                "id": "ctrl_temporadas",
                "x": 380, "y": 350, "width": 330,
                "header": ["Control", "Temporadas_Colecciones"],
                "attributes": [
                    "- season_service: SeasonService"
                ],
                "methods": [
                    "+ crear_temporada(nombre, ini, fin)",
                    "+ validar_rango_fechas(ini, fin)",
                    "+ crear_coleccion(id_temp, nom, desc)",
                    "+ vincular_productos(id_col, lista_p)"
                ]
            },
            {
                "id": "ent_temporada",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_TEMPORADA"],
                "attributes": [
                    "+ ID_TEMPORADA: int [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ NOMBRE: string",
                    "+ FECHA_INICIO: date",
                    "+ FECHA_FIN: date",
                    "+ ACTIVO: boolean = true"
                ],
                "methods": [
                    "+ insertar(datos)",
                    "+ validar_rango(ini, fin)"
                ]
            },
            {
                "id": "ent_coleccion",
                "x": 1100, "y": 350, "width": 280,
                "header": ["T_COLECCION"],
                "attributes": [
                    "+ ID_COLECCION: int [PK]",
                    "+ ID_TEMPORADA: int [FK]",
                    "+ NOMBRE: string",
                    "+ DESCRIPCION: string",
                    "+ ESTADO: string = 'ACTIVO'"
                ],
                "methods": [
                    "+ insertar(datos)",
                    "+ asociar_temporada(id_temp)"
                ]
            },
            {
                "id": "ent_producto",
                "x": 1100, "y": 115, "width": 280,
                "header": ["T_PRODUCTO"],
                "attributes": [
                    "+ ID_PRODUCTO: int [PK]",
                    "+ NOMBRE: string",
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
                    "+ MODULO: string = 'TEMPORADA'",
                    "+ ACCION: string = 'CREAR_TEMPORADA'"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_temp)"
                ]
            }
        ],
        "connections": [
            {"from": "form_temporadas", "to": "ctrl_temporadas", "label": "solicita"},
            {"from": "ctrl_temporadas", "to": "ent_temporada", "label": "persiste"},
            {"from": "ent_temporada", "to": "ent_coleccion", "from_side": "right", "to_side": "left", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_coleccion", "to": "ent_producto", "from_side": "top", "to_side": "bottom", "mult_from": "0..1", "mult_to": "0..*"},
            {"from": "ent_temporada", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }

# ==============================================================================
# CU21: Gestionar proveedores (P1)
# ==============================================================================
def get_cu21_clases():
    return {
        "id": "CU21_W",
        "file_name": "CU21_W_Gestionar_Proveedores_Clases",
        "title": "CU21 W: Gestionar proveedores — Diagrama de Análisis de Clases (UML / ICONIX)",
        "subtitle": "Cadena de Suministro y Proveedores | Estereotipos: Boundary (Form) ── Control ── Entity",
        "actors": "Administrador de Tienda",
        "width": 1440,
        "height": 980,
        "classes": [
            {
                "id": "form_proveedores",
                "x": 50, "y": 350, "width": 270,
                "header": ["Form", "Proveedores"],
                "attributes": [
                    "+ id_proveedor: int",
                    "+ nit_ruc: string",
                    "+ razon_social: string",
                    "+ contacto: string",
                    "+ telefono: string",
                    "+ direccion: string",
                    "+ activo: boolean"
                ],
                "methods": [
                    "+ capturar_proveedor()",
                    "+ guardar_proveedor()",
                    "+ alternar_estado_activo()",
                    "+ mostrar_error_nit_duplicado()"
                ]
            },
            {
                "id": "ctrl_proveedores",
                "x": 380, "y": 350, "width": 330,
                "header": ["Control", "Proveedores"],
                "attributes": [
                    "- supplier_service: SupplierService"
                ],
                "methods": [
                    "+ crear_proveedor(id_empresa, dto)",
                    "+ validar_formato_nit(nit)",
                    "+ verificar_unicidad_nit(id_emp, nit)",
                    "+ insertar_proveedor(datos)",
                    "+ actualizar_proveedor(id, datos)"
                ]
            },
            {
                "id": "ent_proveedor",
                "x": 770, "y": 350, "width": 270,
                "header": ["T_PROVEEDOR"],
                "attributes": [
                    "+ ID_PROVEEDOR: int [PK]",
                    "+ ID_EMPRESA: int [FK]",
                    "+ RAZON_SOCIAL: string",
                    "+ NIT_RUC: string [UQ]",
                    "+ CONTACTO: string",
                    "+ TELEFONO: string",
                    "+ DIRECCION: string",
                    "+ ACTIVO: boolean = true"
                ],
                "methods": [
                    "+ buscar_por_nit(id_emp, nit)",
                    "+ insertar(datos)",
                    "+ actualizar(id, datos)"
                ]
            },
            {
                "id": "ent_producto",
                "x": 1100, "y": 350, "width": 280,
                "header": ["T_PRODUCTO"],
                "attributes": [
                    "+ ID_PRODUCTO: int [PK]",
                    "+ ID_PROVEEDOR: int [FK]",
                    "+ NOMBRE: string",
                    "+ ESTADO: string"
                ],
                "methods": [
                    "+ contar_por_proveedor(id_prov)"
                ]
            },
            {
                "id": "ent_empresa",
                "x": 770, "y": 115, "width": 270,
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
                "id": "ent_bitacora",
                "x": 770, "y": 700, "width": 270,
                "header": ["T_BITACORA"],
                "attributes": [
                    "+ ID_BITACORA: bigint [PK]",
                    "+ FECHA_HORA: timestamp",
                    "+ ID_USUARIO: int [FK]",
                    "+ MODULO: string = 'PROVEEDORES'",
                    "+ ACCION: string = 'CREAR_PROVEEDOR'"
                ],
                "methods": [
                    "+ registrar_evento(accion, id_prov)"
                ]
            }
        ],
        "connections": [
            {"from": "form_proveedores", "to": "ctrl_proveedores", "label": "solicita"},
            {"from": "ctrl_proveedores", "to": "ent_proveedor", "label": "persiste"},
            {"from": "ent_empresa", "to": "ent_proveedor", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"},
            {"from": "ent_proveedor", "to": "ent_producto", "from_side": "right", "to_side": "left", "mult_from": "0..1", "mult_to": "0..*"},
            {"from": "ent_proveedor", "to": "ent_bitacora", "from_side": "bottom", "to_side": "top", "mult_from": "1", "mult_to": "0..*"}
        ]
    }
