#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de Diagramas de Comunicación UML / Robustez (SI2)
Perfeccionado visualmente para coincidir 1:1 con el modelo del docente.
"""

import os

def escape_xml(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def generate_communication_svg(config):
    width = 1760
    height = 360
    cy = 185
    r = 44  # Radio aumentado para que el texto respire holgadamente dentro del círculo

    # Posiciones X de los 6 nodos espaciados a 300px de centro a centro
    # 0: Actor (95)
    # 1: Boundary (375)
    # 2: Route (675)
    # 3: Service (975)
    # 4: Repo (1275)
    # 5: Entity BD (1565)
    x_nodes = [95, 375, 675, 975, 1275, 1565]

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <defs>
    <!-- Marcador de flecha sólida negra hacia la derecha -->
    <marker id="arrow-solid-right" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#111827"/>
    </marker>
    <!-- Marcador de flecha punteada abierta apuntando a la izquierda al final de la línea -->
    <marker id="arrow-open-left" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto">
      <path d="M 2 1.5 L 8 5 L 2 8.5" fill="none" stroke="#111827" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- Líneas guía de cuadrícula (típicas de Enterprise Architect / StarUML) -->
  <line x1="{x_nodes[0]}" y1="15" x2="{x_nodes[0]}" y2="345" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="{x_nodes[1] - r - 14}" y1="15" x2="{x_nodes[1] - r - 14}" y2="345" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="{x_nodes[5] - 25}" y1="15" x2="{x_nodes[5] - 25}" y2="345" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="20" y1="{cy + 46}" x2="{width - 20}" y2="{cy + 46}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>

''')

    # Líneas principales de conexión (Solid con flecha al destino)
    actor_x_right = x_nodes[0] + 18
    boundary_bar_x = x_nodes[1] - r - 14

    # 1. Actor -> Boundary
    svg_parts.append(f'  <!-- Conexión 1: Actor a Boundary -->\n')
    svg_parts.append(f'  <line x1="{actor_x_right}" y1="{cy}" x2="{boundary_bar_x}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>\n')

    # 2. Boundary -> Route
    svg_parts.append(f'  <!-- Conexión 2: Boundary a Route -->\n')
    svg_parts.append(f'  <line x1="{x_nodes[1] + r}" y1="{cy}" x2="{x_nodes[2] - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>\n')

    # 3. Route -> Service
    svg_parts.append(f'  <!-- Conexión 3: Route a Service -->\n')
    svg_parts.append(f'  <line x1="{x_nodes[2] + r}" y1="{cy}" x2="{x_nodes[3] - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>\n')

    # 4. Service -> Repo
    svg_parts.append(f'  <!-- Conexión 4: Service a Repo -->\n')
    svg_parts.append(f'  <line x1="{x_nodes[3] + r}" y1="{cy}" x2="{x_nodes[4] - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>\n')

    # 5. Repo -> Entity
    svg_parts.append(f'  <!-- Conexión 5: Repo a Entity -->\n')
    svg_parts.append(f'  <line x1="{x_nodes[4] + r}" y1="{cy}" x2="{x_nodes[5] - r}" y2="{cy}" stroke="#111827" stroke-width="1.6" marker-end="url(#arrow-solid-right)"/>\n')

    # Textos de mensajes hacia adelante (Forward Messages) colocados SOBRE la línea
    forward_msgs = config.get("forward_messages", [])
    connection_centers = [
        (actor_x_right + boundary_bar_x) / 2,
        (x_nodes[1] + r + x_nodes[2] - r) / 2,
        (x_nodes[2] + r + x_nodes[3] - r) / 2,
        (x_nodes[3] + r + x_nodes[4] - r) / 2,
        (x_nodes[4] + r + x_nodes[5] - r) / 2,
    ]

    for idx, x_mid in enumerate(connection_centers):
        if idx < len(forward_msgs):
            msg = forward_msgs[idx]
            if isinstance(msg, list):
                if len(msg) == 2:
                    t1 = escape_xml(msg[0])
                    t2 = escape_xml(msg[1])
                    svg_parts.append(f'  <text x="{x_mid}" y="{cy - 24}" text-anchor="middle" font-size="12" font-weight="500" fill="#111827">{t1}</text>\n')
                    svg_parts.append(f'  <text x="{x_mid}" y="{cy - 9}" text-anchor="middle" font-size="12" font-weight="500" fill="#111827">{t2}</text>\n')
                elif len(msg) == 3:
                    t1 = escape_xml(msg[0])
                    t2 = escape_xml(msg[1])
                    t3 = escape_xml(msg[2])
                    svg_parts.append(f'  <text x="{x_mid}" y="{cy - 36}" text-anchor="middle" font-size="11.5" font-weight="500" fill="#111827">{t1}</text>\n')
                    svg_parts.append(f'  <text x="{x_mid}" y="{cy - 22}" text-anchor="middle" font-size="11.5" font-weight="500" fill="#111827">{t2}</text>\n')
                    svg_parts.append(f'  <text x="{x_mid}" y="{cy - 8}" text-anchor="middle" font-size="11.5" font-weight="500" fill="#111827">{t3}</text>\n')
            else:
                t = escape_xml(msg)
                svg_parts.append(f'  <text x="{x_mid}" y="{cy - 12}" text-anchor="middle" font-size="12.5" font-weight="500" fill="#111827">{t}</text>\n')

    # Flechas y textos de mensajes de retorno (Return Messages) colocados DEBAJO de la línea
    return_spans = [
        (x_nodes[5] - r - 10, x_nodes[4] + r + 10),  # BD -> Repo
        (x_nodes[4] - r - 10, x_nodes[3] + r + 10),  # Repo -> Service
        (x_nodes[3] - r - 10, x_nodes[2] + r + 10),  # Service -> Route
        (x_nodes[2] - r - 10, x_nodes[1] + r + 10),  # Route -> Boundary
        (boundary_bar_x - 10, actor_x_right + 10),   # Boundary -> Actor
    ]

    return_msgs = config.get("return_messages", [])
    y_return_arrow = cy + 40

    for ret_idx, (x_end, x_start) in enumerate(return_spans):
        if ret_idx < len(return_msgs):
            msg = return_msgs[ret_idx]
            x_mid = (x_start + x_end) / 2

            # Flecha punteada hacia la izquierda (de x_end a x_start)
            svg_parts.append(f'  <!-- Retorno {ret_idx+1} -->\n')
            svg_parts.append(f'  <line x1="{x_end}" y1="{y_return_arrow}" x2="{x_start}" y2="{y_return_arrow}" stroke="#111827" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-open-left)"/>\n')

            # Texto del mensaje de retorno situado justo encima de la flecha punteada
            if isinstance(msg, list):
                if len(msg) == 2:
                    t1 = escape_xml(msg[0])
                    t2 = escape_xml(msg[1])
                    svg_parts.append(f'  <text x="{x_mid}" y="{y_return_arrow - 20}" text-anchor="middle" font-size="11.5" font-weight="500" fill="#111827">{t1}</text>\n')
                    svg_parts.append(f'  <text x="{x_mid}" y="{y_return_arrow - 8}" text-anchor="middle" font-size="11.5" font-weight="500" fill="#111827">{t2}</text>\n')
            else:
                t = escape_xml(msg)
                svg_parts.append(f'  <text x="{x_mid}" y="{y_return_arrow - 8}" text-anchor="middle" font-size="12" font-weight="500" fill="#111827">{t}</text>\n')

    # ==================== DIBUJO DE NODOS ====================

    # 1. NODO: ACTOR
    ax = x_nodes[0]
    actor_label = escape_xml(config.get("actor_name", "USUARIO"))
    svg_parts.append(f'''  <!-- Nodo 1: Actor -->
  <g id="actor">
    <!-- Cabeza -->
    <circle cx="{ax}" cy="{cy - 36}" r="13" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <!-- Tronco -->
    <line x1="{ax}" y1="{cy - 23}" x2="{ax}" y2="{cy + 14}" stroke="#111827" stroke-width="1.8"/>
    <!-- Brazos -->
    <line x1="{ax - 20}" y1="{cy - 10}" x2="{ax + 20}" y2="{cy - 10}" stroke="#111827" stroke-width="1.8"/>
    <!-- Pierna izquierda -->
    <line x1="{ax}" y1="{cy + 14}" x2="{ax - 16}" y2="{cy + 46}" stroke="#111827" stroke-width="1.8"/>
    <!-- Pierna derecha -->
    <line x1="{ax}" y1="{cy + 14}" x2="{ax + 16}" y2="{cy + 46}" stroke="#111827" stroke-width="1.8"/>
    <!-- Etiqueta debajo de la línea base -->
    <text x="{ax}" y="{cy + 66}" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#111827" letter-spacing="0.5">{actor_label}</text>
  </g>
''')

    # 2. NODO: BOUNDARY (Frontera / IU)
    bx = x_nodes[1]
    boundary_label = config.get("boundary_name", "IU_Login")
    svg_parts.append(f'''  <!-- Nodo 2: Boundary (Frontera) -->
  <g id="boundary">
    <!-- Barra vertical izquierda -->
    <line x1="{bx - r - 14}" y1="{cy - 28}" x2="{bx - r - 14}" y2="{cy + 28}" stroke="#111827" stroke-width="2"/>
    <!-- Conector horizontal hacia el círculo -->
    <line x1="{bx - r - 14}" y1="{cy}" x2="{bx - r}" y2="{cy}" stroke="#111827" stroke-width="1.8"/>
    <!-- Círculo principal -->
    <circle cx="{bx}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
''')
    if "\n" in boundary_label:
        parts = boundary_label.split("\n")
        svg_parts.append(f'    <text x="{bx}" y="{cy - 4}" text-anchor="middle" font-size="11.5" font-weight="500" fill="#111827">{escape_xml(parts[0])}</text>\n')
        svg_parts.append(f'    <text x="{bx}" y="{cy + 12}" text-anchor="middle" font-size="11.5" font-weight="500" fill="#111827">{escape_xml(parts[1])}</text>\n')
    else:
        svg_parts.append(f'    <text x="{bx}" y="{cy + 4}" text-anchor="middle" font-size="12.5" font-weight="500" fill="#111827">{escape_xml(boundary_label)}</text>\n')
    svg_parts.append('  </g>\n')

    # Función para dibujar Controlador (Círculo + Flecha chevron en el tope)
    def draw_controller(cx_val, label_val, elem_id):
        # Flecha en el arco superior exactamente como en el modelo:
        # Un chevron '<' con el vértice sobre el perímetro y brazos abiertos
        tip_x = cx_val - 12
        tip_y = cy - r + 3
        return f'''  <!-- Nodo Controlador: {label_val} -->
  <g id="{elem_id}">
    <!-- Círculo principal -->
    <circle cx="{cx_val}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <!-- Chevron de control en el cuadrante superior -->
    <path d="M {tip_x + 18} {tip_y - 9} L {tip_x} {tip_y} L {tip_x + 16} {tip_y + 3}" fill="none" stroke="#111827" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    <!-- Nombre del controlador -->
    <text x="{cx_val}" y="{cy + 4}" text-anchor="middle" font-size="12" font-weight="500" fill="#111827">{escape_xml(label_val)}</text>
  </g>
'''

    # 3. NODO: ROUTE
    svg_parts.append(draw_controller(x_nodes[2], config.get("route_name", "auth_routes"), "route_ctrl"))

    # 4. NODO: SERVICE
    svg_parts.append(draw_controller(x_nodes[3], config.get("service_name", "auth_services"), "service_ctrl"))

    # 5. NODO: REPO
    svg_parts.append(draw_controller(x_nodes[4], config.get("repo_name", "auth_repos"), "repo_ctrl"))

    # 6. NODO: ENTITY (BD)
    ex = x_nodes[5]
    entity_label = escape_xml(config.get("entity_name", "BD"))
    svg_parts.append(f'''  <!-- Nodo 6: Entidad (BD) -->
  <g id="entity">
    <!-- Círculo principal -->
    <circle cx="{ex}" cy="{cy}" r="{r}" fill="#ffffff" stroke="#111827" stroke-width="1.8"/>
    <!-- Línea plana inferior tangencial (Estereotipo Entity) -->
    <line x1="{ex - 30}" y1="{cy + r + 3}" x2="{ex + 30}" y2="{cy + r + 3}" stroke="#111827" stroke-width="2.2"/>
    <!-- Texto BD -->
    <text x="{ex}" y="{cy + 5}" text-anchor="middle" font-size="14.5" font-weight="500" fill="#111827">{entity_label}</text>
  </g>
''')

    # Título superior del CU
    title = escape_xml(config.get("title", ""))
    if title:
        svg_parts.append(f'  <!-- Título del CU -->\n')
        svg_parts.append(f'  <text x="30" y="32" font-size="13.5" font-weight="bold" fill="#475569" letter-spacing="0.3">{title}</text>\n')

    svg_parts.append('</svg>\n')
    return "".join(svg_parts)

ALL_CUS = [
    # 1. CU01 W/M: Registrar usuario
    {
        "id": "CU01_WM",
        "file_name": "CU01_WM_Registrar_Usuario.svg",
        "title": "CU01 W/M: Registrar usuario (CU/W01 y CU/M01)",
        "actor_name": "USUARIO",
        "boundary_name": "IU_Registro",
        "route_name": "auth_routes",
        "service_name": "auth_services",
        "repo_name": "auth_repos",
        "entity_name": "BD",
        "forward_messages": [
            "1.1. Ingresar datos de registro()",
            "1.2: enviar datos de registro()",
            "1.3: registrar_cliente(datos)",
            "1.4: validar unicidad y hash clave()",
            [
                "1.5: verificar existencia correo/user()",
                "1.5.1: insertar en t_usuario y t_seguridad()"
            ]
        ],
        "return_messages": [
            "1.6: confirmar inserción exitosa",
            "1.7: retornar ID nuevo usuario()",
            "1.8: generar token JWT / confirmación()",
            "1.9: mostrar resultado exitoso()",
            "1.10: acceder al sistema()"
        ],
        "description": "Permite registrar un nuevo usuario cliente en la plataforma, tanto desde la tienda Web como desde la app móvil. Valida unicidad de correo y username, aplica hash SHA-256 a la contraseña y genera el registro de seguridad y dispositivo."
    },

    # 2. CU02 W/M: Iniciar sesión (Modelo exacto del docente)
    {
        "id": "CU02_WM",
        "file_name": "CU02_WM_Iniciar_Sesion.svg",
        "title": "CU02 W/M: Iniciar sesión (CU/W02 y CU/M02)",
        "actor_name": "USUARIO",
        "boundary_name": "IU_Login",
        "route_name": "auth_routes",
        "service_name": "auth_services",
        "repo_name": "auth_repos",
        "entity_name": "BD",
        "forward_messages": [
            "1.1. Ingresar credenciales()",
            "1.2: enviar credenciales()",
            "1.3: enviar credenciales()",
            "1.4: validar credenciales()",
            [
                "1.5: consultar datos de usuario()",
                "1.5.1: registrar Intento de Inicio de Sesión()"
            ]
        ],
        "return_messages": [
            "1.6: devolver verificación",
            "1.7: confirmar acceso válido/erróneo()",
            "1.8: devolver verificación",
            "1.9: mostrar resultado()",
            "1.10: acceder o denegar acceso()"
        ],
        "description": "Autenticación unificada de credenciales (correo/username y contraseña). Valida intentos fallidos, aplica bloqueo de 15 minutos al tercer fallo consecutivo y valida dispositivo mediante huella o código."
    },

    # 3. CU03 W/M: Gestionar perfil
    {
        "id": "CU03_WM",
        "file_name": "CU03_WM_Gestionar_Perfil.svg",
        "title": "CU03 W/M: Gestionar perfil (CU/W03 y CU/M03)",
        "actor_name": "USUARIO",
        "boundary_name": "IU_Perfil",
        "route_name": "profile_routes",
        "service_name": "profile_services",
        "repo_name": "profile_repos",
        "entity_name": "BD",
        "forward_messages": [
            "1.1. Solicitar o editar perfil()",
            "1.2: enviar datos con Bearer Token()",
            "1.3: actualizar_perfil_usuario(datos)",
            "1.4: validar sesión y consistencia()",
            [
                "1.5: consultar/actualizar t_usuario()",
                "1.5.1: registrar cambio en t_bitacora()"
            ]
        ],
        "return_messages": [
            "1.6: devolver confirmación de actualización",
            "1.7: retornar perfil actualizado()",
            "1.8: responder datos de perfil OK()",
            "1.9: presentar perfil actualizado()",
            "1.10: visualizar datos confirmados()"
        ],
        "description": "Permite al usuario autenticado visualizar y editar sus datos personales (nombre, apellido, teléfono, foto y dirección), validando la sesión JWT activa."
    },

    # 4. CU04 W/M: Consultar catálogo
    {
        "id": "CU04_WM",
        "file_name": "CU04_WM_Consultar_Catalogo.svg",
        "title": "CU04 W/M: Consultar catálogo (CU/W04 y CU/M04)",
        "actor_name": "CLIENTE",
        "boundary_name": "IU_Catalogo",
        "route_name": "catalogo_routes",
        "service_name": "catalogo_services",
        "repo_name": "catalogo_repos",
        "entity_name": "BD",
        "forward_messages": [
            "1.1. Seleccionar filtros y prendas()",
            "1.2: enviar criterios de búsqueda()",
            "1.3: listar_catalogo_filtrado(filtros)",
            "1.4: procesar filtros y verificar stock()",
            [
                "1.5: consultar prendas, variantes y stock()",
                "1.5.1: registrar métrica de búsqueda()"
            ]
        ],
        "return_messages": [
            "1.6: devolver registros de prendas y fotos",
            "1.7: retornar prendas estructuradas()",
            "1.8: devolver catálogo formateado()",
            "1.9: renderizar tarjetas de prendas()",
            "1.10: visualizar catálogo de productos()"
        ],
        "description": "Exploración pública de las colecciones de prendas con filtrado dinámico por categoría, sucursal física, tallas, paleta de color y ordenación por popularidad/precio."
    },

    # 5. CU/W14: Gestionar usuarios y roles
    {
        "id": "CU_W14",
        "file_name": "CU_W14_Gestionar_Usuarios_Roles.svg",
        "title": "CU/W14: Gestionar usuarios y roles",
        "actor_name": "ADMINISTRADOR",
        "boundary_name": "IU_UsuariosRoles",
        "route_name": "users_routes",
        "service_name": "users_services",
        "repo_name": "users_repos",
        "entity_name": "BD",
        "forward_messages": [
            "1.1. Crear/editar usuario y asignar rol()",
            "1.2: enviar formulario con token RBAC()",
            "1.3: registrar_usuario_con_rol(datos)",
            "1.4: validar permisos y consistencia()",
            [
                "1.5: persistir en t_usuario y t_rol()",
                "1.5.1: registrar auditoría en t_bitacora()"
            ]
        ],
        "return_messages": [
            "1.6: confirmar persistencia usuario y rol",
            "1.7: retornar estado de asignación()",
            "1.8: responder operación RBAC exitosa()",
            "1.9: actualizar grilla de usuarios y roles()",
            "1.10: notificar confirmación de usuario()"
        ],
        "description": "Panel administrativo para listar, crear, editar y desactivar usuarios del sistema, con asignación de roles jerárquicos (ADMINISTRADOR, TIENDA, SUCURSAL, CAJERO) y permisos granulares."
    },

    # 6. CU/W15: Gestionar cadena de tiendas
    {
        "id": "CU_W15",
        "file_name": "CU_W15_Gestionar_Cadena_Tiendas.svg",
        "title": "CU/W15: Gestionar cadena de tiendas",
        "actor_name": "ADMINISTRADOR",
        "boundary_name": "IU_CadenaTiendas",
        "route_name": "tenant_routes",
        "service_name": "tenant_services",
        "repo_name": "tenant_repos",
        "entity_name": "BD",
        "forward_messages": [
            "1.1. Ingresar razón social, NIT y datos()",
            "1.2: enviar datos de cadena de tiendas()",
            "1.3: registrar_empresa(datos, payload)",
            "1.4: verificar unicidad de NIT y estado()",
            [
                "1.5: insertar/actualizar en tabla empresa()",
                "1.5.1: registrar evento en t_bitacora()"
            ]
        ],
        "return_messages": [
            "1.6: devolver confirmación y ID de empresa",
            "1.7: retornar tenant configurado()",
            "1.8: responder creación de tienda exitosa()",
            "1.9: actualizar lista de cadenas de tiendas()",
            "1.10: confirmar guardado de tienda()"
        ],
        "description": "Mantenimiento del multi-tenancy para la cadena comercial: registro y configuración de las empresas/marcas de moda asociadas, su estado operativo y credenciales fiscales."
    },

    # 7. CU/W16: Gestionar sucursales y ciudades
    {
        "id": "CU_W16",
        "file_name": "CU_W16_Gestionar_Sucursales_Ciudades.svg",
        "title": "CU/W16: Gestionar sucursales y ciudades",
        "actor_name": "ADMINISTRADOR",
        "boundary_name": "IU_Sucursales",
        "route_name": "sucursales_routes",
        "service_name": "sucursales_services",
        "repo_name": "sucursales_repos",
        "entity_name": "BD",
        "forward_messages": [
            "1.1. Ingresar sucursal, ciudad y dirección()",
            "1.2: enviar formulario de sucursal()",
            "1.3: registrar_sucursal(datos, payload)",
            "1.4: validar pertenencia a empresa()",
            [
                "1.5: insertar en t_sucursal y asociar ciudad()",
                "1.5.1: auditar acción en t_bitacora()"
            ]
        ],
        "return_messages": [
            "1.6: confirmar inserción de sucursal",
            "1.7: retornar ID de nueva sucursal()",
            "1.8: responder operación de sucursal OK()",
            "1.9: recargar lista de sucursales()",
            "1.10: notificar sucursal guardada()"
        ],
        "description": "Gestión de las tiendas físicas por ciudad geográfica (Santa Cruz - Equipetrol, La Paz - Calacoto, Cochabamba), requeridas para la asignación de stock y retiro en tienda."
    },

    # 8. CU/W17: Gestionar productos
    {
        "id": "CU_W17",
        "file_name": "CU_W17_Gestionar_Productos.svg",
        "title": "CU/W17: Gestionar productos",
        "actor_name": "ADMIN_TIENDA",
        "boundary_name": "IU_Productos",
        "route_name": "productos_routes",
        "service_name": "productos_services",
        "repo_name": "productos_repos",
        "entity_name": "BD",
        "forward_messages": [
            "1.1. Ingresar SKU, nombre, precio y prenda()",
            "1.2: enviar formulario de producto()",
            "1.3: registrar_producto(datos, id_tienda)",
            "1.4: validar código SKU y categoría()",
            [
                "1.5: insertar prenda en t_producto()",
                "1.5.1: registrar auditoría en t_bitacora()"
            ]
        ],
        "return_messages": [
            "1.6: devolver confirmación y ID producto",
            "1.7: retornar producto registrado()",
            "1.8: devolver respuesta 201 Created()",
            "1.9: actualizar catálogo administrativo()",
            "1.10: notificar prenda registrada()"
        ],
        "description": "Mantenimiento del catálogo maestro de indumentaria textil: registro de prendas, descripción artesanal (ej. fibra de alpaca boliviana), precio base y asignación de categoría."
    },

    # 9. CU/W18: Gestionar categorías
    {
        "id": "CU_W18",
        "file_name": "CU_W18_Gestionar_Categorias.svg",
        "title": "CU/W18: Gestionar categorías",
        "actor_name": "ADMIN_TIENDA",
        "boundary_name": "IU_Categorias",
        "route_name": "categorias_routes",
        "service_name": "categorias_services",
        "repo_name": "categorias_repos",
        "entity_name": "BD",
        "forward_messages": [
            "1.1. Definir nombre y temporada categoría()",
            "1.2: enviar formulario de categoría()",
            "1.3: crear_categoria(datos)",
            "1.4: validar unicidad de nombre categoría()",
            [
                "1.5: insertar registro en t_categoria()",
                "1.5.1: registrar evento en t_bitacora()"
            ]
        ],
        "return_messages": [
            "1.6: confirmar guardado de categoría",
            "1.7: retornar ID de nueva categoría()",
            "1.8: responder confirmación 201 Created()",
            "1.9: recargar lista de categorías()",
            "1.10: notificar categoría guardada()"
        ],
        "description": "Definición y jerarquización de las líneas de moda (ej: Otoño 2026, Sastrería Urbana, Alta Costura, Esenciales, Accesorios) para agrupar las prendas del e-commerce."
    },

    # 10. CU/W19: Gestionar tallas y colores
    {
        "id": "CU_W19",
        "file_name": "CU_W19_Gestionar_Tallas_Colores.svg",
        "title": "CU/W19: Gestionar tallas y colores",
        "actor_name": "ADMIN_TIENDA",
        "boundary_name": "IU_TallasColores",
        "route_name": "variantes_routes",
        "service_name": "variantes_services",
        "repo_name": "variantes_repos",
        "entity_name": "BD",
        "forward_messages": [
            "1.1. Configurar tallas (S, M, L) y colores HEX()",
            "1.2: enviar matriz de atributos()",
            "1.3: registrar_variantes_atributos(datos)",
            "1.4: validar combinaciones y prenda()",
            [
                "1.5: insertar en t_talla, t_color y variantes()",
                "1.5.1: registrar auditoría en t_bitacora()"
            ]
        ],
        "return_messages": [
            "1.6: confirmar persistencia de variantes",
            "1.7: devolver resumen de variantes()",
            "1.8: responder operación completada()",
            "1.9: renderizar selector de variantes()",
            "1.10: notificar variantes guardadas()"
        ],
        "description": "Configuración de las dimensiones y paleta cromática por prenda: tallas textiles (XS, S, M, L, XL) y colores con código HEX (ej: Camel Atacama #c19a6b, Negro Azabache #18181b)."
    }
]

def generate_all():
    output_dir = "docs/diagramas_comunicacion"
    os.makedirs(output_dir, exist_ok=True)
    
    import cairosvg

    print(f"Generando {len(ALL_CUS)} diagramas de comunicación (SVG y PNG 2x)...")
    for cu in ALL_CUS:
        svg_code = generate_communication_svg(cu)
        svg_path = os.path.join(output_dir, cu["file_name"])
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_code)
        
        # Renderizar también PNG de alta resolución (2x)
        png_name = cu["file_name"].replace(".svg", ".png")
        png_path = os.path.join(output_dir, png_name)
        cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2.0)
        
        print(f" -> Generado: {cu['file_name']} y {png_name}")

    print("¡Todos los diagramas SVG y PNG generados con éxito!")

if __name__ == "__main__":
    generate_all()
