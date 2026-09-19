from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repos import rbac_repos, users_repos
from app.services import bitacora_services

# Mapeo de Nivel de Autoridad por ID o Nombre de Rol
# Nivel 1: SUPERADMIN
# Nivel 2: ADMINISTRADOR
# Nivel 3: ADMINISTRADOR_TIENDA
# Nivel 4: ENCARGADO / ENCARGADO_SUCURSAL
# Nivel 5: EMPLEADO / CAJERO
# Nivel 6: CLIENTE
# Nivel 7: PROVEEDOR

JERARQUIA_ROLES = {
    1: 2,  # Rol ID 1: ADMINISTRADOR (es Nivel 1 si id_empresa is None, Nivel 2 en general)
    2: 6,  # CLIENTE
    3: 3,  # ADMINISTRADOR_TIENDA
    4: 4,  # ENCARGADO / ENCARGADO_SUCURSAL
    5: 5,  # EMPLEADO / CAJERO
    6: 7   # PROVEEDOR
}

def obtener_nivel_actor(actor_payload: dict) -> int:
    roles = [str(r).upper() for r in actor_payload.get('roles', [])]
    if actor_payload.get('rol'):
        roles.append(str(actor_payload.get('rol')).upper())
    id_rol = actor_payload.get('id_rol')
    id_empresa = actor_payload.get('id_empresa')

    if (id_rol == 1 or 'ADMINISTRADOR' in roles or 'SUPERADMIN' in roles) and (id_empresa is None or id_empresa == 0):
        return 1  # SUPERADMIN
    if id_rol == 1 or 'ADMINISTRADOR' in roles or 'SUPERADMIN' in roles:
        return 2  # ADMINISTRADOR
    if id_rol == 3 or 'ADMINISTRADOR_TIENDA' in roles:
        return 3  # ADMINISTRADOR_TIENDA
    if id_rol == 4 or 'ENCARGADO' in roles or 'ENCARGADO_SUCURSAL' in roles:
        return 4  # ENCARGADO
    if id_rol == 5 or 'EMPLEADO' in roles or 'CAJERO' in roles:
        return 5  # EMPLEADO
    if id_rol == 2 or 'CLIENTE' in roles:
        return 6  # CLIENTE
    return 7      # PROVEEDOR

def obtener_nivel_rol_destino(id_rol: int) -> int:
    return JERARQUIA_ROLES.get(id_rol, 6)

def validar_asignacion_rol(actor_payload: dict, id_rol_destino: int):
    nivel_actor = obtener_nivel_actor(actor_payload)
    nivel_destino = obtener_nivel_rol_destino(id_rol_destino)

    # Regla: Ningún usuario podrá asignar un rol superior a su propia autoridad
    if nivel_actor > nivel_destino:
        raise ValueError(
            f"Violación de jerarquía: Su nivel de autoridad ({nivel_actor}) "
            f"no le permite asignar un rol de nivel superior ({nivel_destino})."
        )

def validar_delegacion_permisos(actor_payload: dict, ids_permisos: List[int]):
    nivel_actor = obtener_nivel_actor(actor_payload)
    if nivel_actor == 1:
        # Superadmin puede delegar cualquier permiso activo
        return

    # Obtener los permisos efectivos del actor
    id_actor = actor_payload.get('nro_usuario') or actor_payload.get('id_usuario')
    if not id_actor:
        raise ValueError("Token de usuario no válido para verificar permisos de delegación.")

    permisos_actor = set(rbac_repos.obtener_permisos_efectivos_usuario(id_actor))

    # Obtener todos los permisos del sistema para mapear ID -> Código
    todos_permisos = {p['id_permiso']: p['codigo'] for p in rbac_repos.obtener_todos_los_permisos()}

    permisos_no_autorizados = []
    for id_p in ids_permisos:
        codigo = todos_permisos.get(id_p)
        if codigo and codigo not in permisos_actor:
            permisos_no_autorizados.append(codigo)

    if permisos_no_autorizados:
        raise ValueError(
            f"No tiene autorización para delegar los siguientes permisos: "
            f"{', '.join(permisos_no_autorizados)}. "
            f"Un administrador solo puede asignar permisos que tenga en su propio nivel de acceso."
        )

def obtener_permisos_completos_usuario(id_usuario: int, actor_payload: Optional[dict] = None) -> Dict[str, Any]:
    user_db = users_repos.obtener_usuario_por_id(id_usuario)
    if not user_db:
        raise ValueError("Usuario no encontrado.")

    if actor_payload:
        from app.utils.tenant_guard import validar_acceso_recurso_tenant
        validar_acceso_recurso_tenant(actor_payload, user_db.get('id_empresa'), "usuario")

    directos = rbac_repos.obtener_permisos_directos_usuario(id_usuario)
    heredados = rbac_repos.obtener_permisos_heredados_usuario(id_usuario)
    efectivos = rbac_repos.obtener_permisos_efectivos_usuario(id_usuario)

    return {
        "success": True,
        "id_usuario": id_usuario,
        "usuario": user_db.get("username") or user_db.get("nombre"),
        "permisos_directos": directos,
        "permisos_heredados": heredados,
        "permisos_efectivos": efectivos
    }

def asignar_permisos_directos(
    id_usuario: int, 
    ids_permisos: List[int], 
    actor_payload: dict, 
    request: Optional[Request] = None
) -> Dict[str, Any]:
    user_destino = users_repos.obtener_usuario_por_id(id_usuario)
    if not user_destino:
        raise ValueError("El usuario destino no existe.")

    # Aislamiento Multi-Tenant
    from app.utils.tenant_guard import validar_acceso_recurso_tenant
    validar_acceso_recurso_tenant(actor_payload, user_destino.get('id_empresa'), "usuario")

    # Validar delegación de permisos
    validar_delegacion_permisos(actor_payload, ids_permisos)

    # Asignar permisos directos en la BD
    rbac_repos.asignar_permisos_directos_a_usuario(id_usuario, ids_permisos)

    # Auditoría en t_bitacora
    try:
        todos = {p['id_permiso']: p['codigo'] for p in rbac_repos.obtener_todos_los_permisos()}
        codigos_asignados = [todos[i] for i in ids_permisos if i in todos]

        bitacora_services.registrar_accion(
            modulo="RBAC",
            accion="ASIGNAR_PERMISOS_DIRECTOS",
            nivel="INFO",
            resultado="EXITO",
            payload_jwt=actor_payload,
            entidad="Usuario",
            id_entidad=str(id_usuario),
            descripcion=f"Permisos directos asignados a usuario #{id_usuario}: {', '.join(codigos_asignados)}",
            datos_nuevos={"ids_permisos": ids_permisos, "codigos": codigos_asignados},
            request=request
        )
    except Exception as e:
        print(f"[BITACORA] Error al registrar auditoría de permisos: {e}")

    return {
        "success": True,
        "message": f"Permisos directos actualizados correctamente para el usuario #{id_usuario}.",
        "permisos_efectivos": rbac_repos.obtener_permisos_efectivos_usuario(id_usuario)
    }

def obtener_roles_delegables(actor_payload: dict) -> List[Dict[str, Any]]:
    nivel_actor = obtener_nivel_actor(actor_payload)
    todos_los_roles = rbac_repos.obtener_todos_los_roles(solo_activos=True)

    roles_permitidos = []
    for r in todos_los_roles:
        id_r = r['id_rol']
        nivel_r = obtener_nivel_rol_destino(id_r)
        # Solo roles con nivel >= nivel_actor (autoridad igual o inferior)
        if nivel_r >= nivel_actor:
            roles_permitidos.append({
                **r,
                "nivel_jerarquia": nivel_r
            })

    return roles_permitidos

def obtener_permisos_delegables(actor_payload: dict) -> List[Dict[str, Any]]:
    nivel_actor = obtener_nivel_actor(actor_payload)
    todos_permisos = rbac_repos.obtener_todos_los_permisos()

    if nivel_actor == 1:
        # Superadmin puede delegar todos
        return todos_permisos

    id_actor = actor_payload.get('nro_usuario') or actor_payload.get('id_usuario')
    permisos_actor = set(rbac_repos.obtener_permisos_efectivos_usuario(id_actor))

    # Filtrar solo los permisos que el actor posee
    return [p for p in todos_permisos if p['codigo'] in permisos_actor]
