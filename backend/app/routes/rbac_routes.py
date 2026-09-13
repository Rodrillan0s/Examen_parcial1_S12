from fastapi import APIRouter, Body, Depends, HTTPException, Request
from app.utils.security import verificar_token, require_permission
from app.repos import rbac_repos
from app.services import rbac_services

router = APIRouter(tags=["Administración de RBAC (Roles y Permisos)"])

# --- CONSULTAR MIS PERMISOS Y ALCANCE (USUARIO ACTUAL) ---
@router.get('/mis-permisos')
def mis_permisos(payload: dict = Depends(verificar_token)):
    id_usuario = payload.get('nro_usuario') or payload.get('id_usuario')
    if not id_usuario:
        raise HTTPException(status_code=400, detail="Token no contiene identificador de usuario.")
    
    permisos = rbac_repos.obtener_permisos_efectivos_usuario(id_usuario)
    roles = rbac_repos.obtener_roles_usuario(id_usuario)
    sucursales = rbac_repos.obtener_sucursales_usuario(id_usuario)
    
    return {
        "success": True,
        "nro_usuario": id_usuario,
        "roles": roles,
        "permisos": permisos,
        "sucursales": sucursales
    }

# --- ROLES ---
@router.get('/roles', dependencies=[Depends(require_permission('roles.ver'))])
def listar_roles(solo_activos: bool = False):
    return {
        "success": True,
        "roles": rbac_repos.obtener_todos_los_roles(solo_activos=solo_activos)
    }

@router.get('/roles-delegables')
def listar_roles_delegables(payload: dict = Depends(verificar_token)):
    return {
        "success": True,
        "roles": rbac_services.obtener_roles_delegables(payload)
    }

@router.post('/roles', dependencies=[Depends(require_permission('roles.crear'))])
def crear_nuevo_rol(data: dict = Body(...)):
    nombre = (data.get('nombre') or '').strip().upper()
    descripcion = (data.get('descripcion') or '').strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="El nombre del rol es obligatorio.")
    try:
        id_rol = rbac_repos.crear_rol(nombre, descripcion)
        return {"success": True, "message": "Rol creado exitosamente.", "id_rol": id_rol}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo crear el rol: {str(e)}")

@router.put('/roles/{id_rol}', dependencies=[Depends(require_permission('roles.editar'))])
def actualizar_rol_existente(id_rol: int, data: dict = Body(...)):
    nombre = (data.get('nombre') or '').strip().upper()
    descripcion = (data.get('descripcion') or '').strip()
    activo = data.get('activo', True)
    if not nombre:
        raise HTTPException(status_code=400, detail="El nombre del rol es obligatorio.")
    
    exito = rbac_repos.actualizar_rol(id_rol, nombre, descripcion, activo)
    if not exito:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    return {"success": True, "message": "Rol actualizado exitosamente."}

@router.delete('/roles/{id_rol}', dependencies=[Depends(require_permission('roles.eliminar'))])
def desactivar_rol_existente(id_rol: int):
    exito = rbac_repos.desactivar_rol(id_rol)
    if not exito:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    return {"success": True, "message": "Rol desactivado exitosamente."}

# --- PERMISOS ---
@router.get('/permisos', dependencies=[Depends(require_permission('permisos.ver'))])
def listar_permisos():
    return {
        "success": True,
        "permisos": rbac_repos.obtener_todos_los_permisos()
    }

@router.get('/permisos-delegables')
def listar_permisos_delegables(payload: dict = Depends(verificar_token)):
    return {
        "success": True,
        "permisos": rbac_services.obtener_permisos_delegables(payload)
    }

@router.post('/permisos', dependencies=[Depends(require_permission('permisos.ver'))])
def crear_nuevo_permiso(data: dict = Body(...)):
    codigo = (data.get('codigo') or '').strip().lower()
    nombre = (data.get('nombre') or '').strip()
    descripcion = (data.get('descripcion') or '').strip()
    modulo = (data.get('modulo') or 'general').strip().lower()
    
    if not codigo or not nombre:
        raise HTTPException(status_code=400, detail="El código y el nombre del permiso son obligatorios.")
    try:
        id_permiso = rbac_repos.crear_permiso(codigo, nombre, descripcion, modulo)
        return {"success": True, "message": "Permiso creado exitosamente.", "id_permiso": id_permiso}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo crear el permiso: {str(e)}")

# --- ASIGNACIÓN DE PERMISOS A ROL ---
@router.get('/roles/{id_rol}/permisos', dependencies=[Depends(require_permission('permisos.ver'))])
def obtener_permisos_de_rol(id_rol: int):
    return {
        "success": True,
        "id_rol": id_rol,
        "permisos": rbac_repos.obtener_permisos_de_rol(id_rol)
    }

@router.post('/roles/{id_rol}/permisos', dependencies=[Depends(require_permission('permisos.asignar'))])
def asignar_permisos_a_rol(id_rol: int, data: dict = Body(...)):
    ids_permisos = data.get('ids_permisos', [])
    if not isinstance(ids_permisos, list):
        raise HTTPException(status_code=400, detail="'ids_permisos' debe ser un arreglo numérico de IDs de permisos.")
    
    rbac_repos.asignar_permisos_a_rol(id_rol, ids_permisos)
    return {"success": True, "message": f"Permisos actualizados correctamente para el rol ID {id_rol}."}

# --- ASIGNACIÓN DE ROLES A USUARIO (CON VALIDACIÓN DE JERARQUÍA) ---
@router.get('/usuarios/{id_usuario}/roles')
def obtener_roles_de_usuario(id_usuario: int, payload: dict = Depends(require_permission('usuarios.ver'))):
    from app.repos import users_repos
    from app.utils.tenant_guard import validar_acceso_recurso_tenant
    user_db = users_repos.obtener_usuario_por_id(id_usuario)
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    validar_acceso_recurso_tenant(payload, user_db.get('id_empresa'), "usuario")

    return {
        "success": True,
        "id_usuario": id_usuario,
        "roles": rbac_repos.obtener_roles_usuario(id_usuario)
    }

@router.post('/usuarios/{id_usuario}/roles', dependencies=[Depends(require_permission('usuarios.editar'))])
def asignar_roles_a_usuario(id_usuario: int, data: dict = Body(...), payload: dict = Depends(verificar_token)):
    from app.repos import users_repos
    from app.utils.tenant_guard import validar_acceso_recurso_tenant
    user_db = users_repos.obtener_usuario_por_id(id_usuario)
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    validar_acceso_recurso_tenant(payload, user_db.get('id_empresa'), "usuario")

    ids_roles = data.get('ids_roles', [])
    if not isinstance(ids_roles, list):
        raise HTTPException(status_code=400, detail="'ids_roles' debe ser un arreglo numérico de IDs de roles.")
    
    try:
        # Validar jerarquía para cada rol que se pretende asignar
        for id_r in ids_roles:
            rbac_services.validar_asignacion_rol(payload, id_r)
        
        rbac_repos.asignar_roles_a_usuario(id_usuario, ids_roles)
        return {"success": True, "message": f"Roles asignados correctamente al usuario ID {id_usuario}."}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

# --- PERMISOS DIRECTOS DE USUARIO (HEREDADOS + DIRECTOS) ---
@router.get('/usuarios/{id_usuario}/permisos')
def consultar_permisos_usuario(id_usuario: int, payload: dict = Depends(require_permission('permisos.ver'))):
    try:
        return rbac_services.obtener_permisos_completos_usuario(id_usuario, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/usuarios/{id_usuario}/permisos')
def asignar_permisos_directos_usuario(
    id_usuario: int, 
    request: Request,
    data: dict = Body(...), 
    payload: dict = Depends(require_permission('permisos.asignar'))
):
    ids_permisos = data.get('ids_permisos', [])
    if not isinstance(ids_permisos, list):
        raise HTTPException(status_code=400, detail="'ids_permisos' debe ser una lista de enteros con IDs de permisos.")
    
    try:
        return rbac_services.asignar_permisos_directos(id_usuario, ids_permisos, payload, request)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# --- SUCURSALES Y ALCANCE ---
@router.get('/sucursales', dependencies=[Depends(require_permission('sucursales.ver'))])
def listar_sucursales():
    return {
        "success": True,
        "sucursales": rbac_repos.obtener_todas_las_sucursales()
    }

@router.get('/usuarios/{id_usuario}/sucursales', dependencies=[Depends(require_permission('sucursales.ver'))])
def obtener_sucursales_de_usuario(id_usuario: int):
    return {
        "success": True,
        "id_usuario": id_usuario,
        "sucursales": rbac_repos.obtener_sucursales_usuario(id_usuario)
    }

@router.post('/usuarios/{id_usuario}/sucursales', dependencies=[Depends(require_permission('sucursales.asignar'))])
def asignar_sucursales_a_usuario(id_usuario: int, data: dict = Body(...)):
    ids_sucursales = data.get('ids_sucursales', [])
    if not isinstance(ids_sucursales, list):
        raise HTTPException(status_code=400, detail="'ids_sucursales' debe ser un arreglo numérico de IDs de sucursales.")
    
    rbac_repos.asignar_sucursales_a_usuario(id_usuario, ids_sucursales)
    return {"success": True, "message": f"Sucursales asignadas correctamente al usuario ID {id_usuario}."}
