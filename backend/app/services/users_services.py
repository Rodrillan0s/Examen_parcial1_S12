from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from werkzeug.security import generate_password_hash
from app.repos import users_repos, rbac_repos
from app.services import bitacora_services, rbac_services
from app.utils.tenant_guard import (
    es_administrador_global,
    resolver_tenant_operacion,
    validar_acceso_recurso_tenant
)

def is_global_admin(payload: dict) -> bool:
    return es_administrador_global(payload)

def listar_usuarios(payload: dict, id_empresa_filtro: Optional[int] = None) -> Dict[str, Any]:
    empresa_efectiva = resolver_tenant_operacion(payload, id_empresa_filtro, permitir_global=True)
    
    if empresa_efectiva is not None:
        usuarios = users_repos.obtener_usuarios_por_empresa(empresa_efectiva)
    else:
        usuarios = users_repos.obtener_todos_los_usuarios()
        
    return {
        "success": True,
        "message": "Usuarios recuperados exitosamente",
        "data": usuarios
    }

def obtener_usuario_detalle(id_usuario: int, payload: dict) -> Dict[str, Any]:
    if id_usuario <= 0:
        raise HTTPException(status_code=400, detail="ID de usuario no válido.")

    user_db = users_repos.obtener_usuario_por_id(id_usuario)
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    validar_acceso_recurso_tenant(payload, user_db.get('id_empresa'), "usuario")

    return {
        "success": True,
        "data": user_db
    }

def registrar_usuario(data: dict, payload: dict, request: Optional[Request] = None) -> Dict[str, Any]:
    campos_requeridos = ['nombre_completo', 'nombre_usuario', 'password']
    for campo in campos_requeridos:
        if not data.get(campo) or not str(data[campo]).strip():
            raise HTTPException(status_code=400, detail=f"El campo '{campo}' es obligatorio.")

    id_rol = data.get('nro_rol') or data.get('id_rol')
    if not id_rol:
        raise HTTPException(status_code=400, detail="El campo 'id_rol' es obligatorio.")
    id_rol = int(id_rol)

    # 1. Validación de Jerarquía Estricta
    try:
        rbac_services.validar_asignacion_rol(payload, id_rol)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    # 2. Resolución de Tenant Efectivo
    id_empresa_solicitado = data.get('id_empresa')
    if id_empresa_solicitado in (0, '0', '', None):
        id_empresa_solicitado = None
    else:
        id_empresa_solicitado = int(id_empresa_solicitado)

    id_empresa = resolver_tenant_operacion(payload, id_empresa_solicitado, permitir_global=True)

    password_hash = generate_password_hash(data['password'])

    nombre_completo = str(data['nombre_completo']).strip()
    partes = nombre_completo.split(' ', 1)
    nombre = partes[0]
    apellido = partes[1] if len(partes) > 1 else ''

    datos_usuario = {
        'username': str(data.get('nombre_usuario') or data.get('username')).strip().lower(),
        'correo': data.get('correo'),
        'password_hash': password_hash,
        'nombre': nombre,
        'apellido': apellido,
        'telefono': data.get('telefono'),
        'id_empresa': id_empresa,
        'id_rol': id_rol
    }

    nuevo_id = users_repos.crear_usuario_db(None, datos_usuario)

    # 3. Asignación opcional de Permisos Directos iniciales
    ids_permisos = data.get('ids_permisos')
    if ids_permisos and isinstance(ids_permisos, list):
        rbac_services.validar_delegacion_permisos(payload, ids_permisos)
        rbac_repos.asignar_permisos_directos_a_usuario(nuevo_id, ids_permisos)

    # Auditoría
    datos_log = {k: v for k, v in datos_usuario.items() if k != 'password_hash'}
    try:
        bitacora_services.registrar_accion(
            modulo="USUARIOS", 
            accion="USUARIO_CREADO", 
            nivel="INFO", 
            resultado="EXITO",
            payload_jwt=payload, 
            entidad="Usuario", 
            id_entidad=str(nuevo_id),
            descripcion=f"Usuario creado: {nombre_completo} con rol #{id_rol}",
            datos_nuevos=datos_log,
            request=request
        )
    except Exception as e:
        print(f"[BITACORA] Error al registrar usuario: {e}")

    return {
        "success": True,
        "message": "Usuario registrado exitosamente",
        "nro_usuario": nuevo_id,
        "id_usuario": nuevo_id
    }

def actualizar_usuario(id_usuario: int, data: dict, payload: dict, request: Optional[Request] = None) -> Dict[str, Any]:
    if id_usuario <= 0:
        raise ValueError("ID de usuario no válido.")
        
    campos_requeridos = ['nombre_completo', 'nombre_usuario']
    for campo in campos_requeridos:
        if not data.get(campo) or not str(data[campo]).strip():
            raise ValueError(f"El campo '{campo}' es obligatorio.")

    id_rol = data.get('nro_rol') or data.get('id_rol')
    if not id_rol:
        raise ValueError("El campo 'id_rol' es obligatorio.")
    id_rol = int(id_rol)

    # 1. Validación de Jerarquía Estricta
    rbac_services.validar_asignacion_rol(payload, id_rol)

    user_db_before = users_repos.obtener_usuario_por_id(id_usuario)
    if not user_db_before:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # 1. Validación de Jerarquía Estricta
    try:
        rbac_services.validar_asignacion_rol(payload, id_rol)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    nivel_actor = rbac_services.obtener_nivel_actor(payload)
    rol_actual_id = user_db_before.get('id_rol')
    if rol_actual_id:
        nivel_actual = rbac_services.obtener_nivel_rol_destino(rol_actual_id)
        if nivel_actor > nivel_actual:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Violación de jerarquía: No puede modificar a un usuario con mayor autoridad que la suya.")

    # 2. Validación Multi-Tenant
    validar_acceso_recurso_tenant(payload, user_db_before.get('id_empresa'), "usuario")

    id_empresa_solicitado = data.get('id_empresa')
    if id_empresa_solicitado in (0, '0', '', None):
        id_empresa_solicitado = None
    else:
        id_empresa_solicitado = int(id_empresa_solicitado)

    if not is_global_admin(payload):
        id_empresa = payload.get('id_empresa')
    else:
        id_empresa = id_empresa_solicitado

    nombre_completo = str(data['nombre_completo']).strip()
    partes = nombre_completo.split(' ', 1)
    nombre = partes[0]
    apellido = partes[1] if len(partes) > 1 else ''

    datos_usuario = {
        'username': str(data.get('nombre_usuario') or data.get('username')).strip().lower(),
        'correo': data.get('correo'),
        'nombre': nombre,
        'apellido': apellido,
        'telefono': data.get('telefono'),
        'id_empresa': id_empresa,
        'id_rol': id_rol,
        'estado': data.get('estado', user_db_before.get('estado'))
    }

    cambiar_password = False
    if data.get('password') and len(str(data.get('password')).strip()) > 0:
        cambiar_password = True
        datos_usuario['password_hash'] = generate_password_hash(data['password'])

    users_repos.actualizar_usuario_db(id_usuario, data.get('ci'), None, datos_usuario, cambiar_password)

    # 3. Asignación opcional de Permisos Directos si vienen en el payload
    if 'ids_permisos' in data and isinstance(data['ids_permisos'], list):
        rbac_services.validar_delegacion_permisos(payload, data['ids_permisos'])
        rbac_repos.asignar_permisos_directos_a_usuario(id_usuario, data['ids_permisos'])

    # Auditoría
    datos_log = {k: v for k, v in datos_usuario.items() if k != 'password_hash'}
    datos_anteriores = {k: v for k, v in user_db_before.items() if k != 'password_hash'}
    try:
        bitacora_services.registrar_accion(
            modulo="USUARIOS", 
            accion="USUARIO_EDITADO", 
            nivel="INFO", 
            resultado="EXITO",
            payload_jwt=payload, 
            entidad="Usuario", 
            id_entidad=str(id_usuario),
            descripcion=f"Usuario editado: {nombre_completo}",
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_log,
            request=request
        )
    except Exception as e:
        print(f"[BITACORA] Error al registrar edición de usuario: {e}")

    return {
        "success": True,
        "message": "Usuario actualizado exitosamente"
    }

def eliminar_usuario(id_usuario: int, payload: dict, request: Optional[Request] = None) -> Dict[str, Any]:
    if id_usuario <= 0:
        raise HTTPException(status_code=400, detail="ID de usuario no válido.")
        
    user_db = users_repos.obtener_usuario_por_id(id_usuario)
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    validar_acceso_recurso_tenant(payload, user_db.get('id_empresa'), "usuario")

    nivel_actor = rbac_services.obtener_nivel_actor(payload)
    rol_actual_id = user_db.get('id_rol')
    if rol_actual_id:
        nivel_actual = rbac_services.obtener_nivel_rol_destino(rol_actual_id)
        if nivel_actor > nivel_actual:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Violación de jerarquía: No puede desactivar a un usuario con mayor autoridad que la suya.")

    users_repos.eliminar_usuario_db(id_usuario)
    
    try:
        bitacora_services.registrar_accion(
            modulo="USUARIOS", 
            accion="USUARIO_DESACTIVADO", 
            nivel="WARNING", 
            resultado="EXITO",
            payload_jwt=payload, 
            entidad="Usuario", 
            id_entidad=str(id_usuario),
            descripcion=f"Usuario #{id_usuario} desactivado",
            datos_anteriores={"activo": True},
            datos_nuevos={"activo": False},
            request=request
        )
    except Exception as e:
        print(f"[BITACORA] Error al registrar desactivación de usuario: {e}")
    
    return {
        "success": True,
        "message": "Usuario desactivado correctamente."
    }

def cambiar_estado_usuario(id_usuario: int, data: dict, payload: dict, request: Optional[Request] = None) -> Dict[str, Any]:
    if id_usuario <= 0:
        raise HTTPException(status_code=400, detail="ID de usuario no válido.")

    user_db = users_repos.obtener_usuario_por_id(id_usuario)
    if not user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    validar_acceso_recurso_tenant(payload, user_db.get('id_empresa'), "usuario")

    nivel_actor = rbac_services.obtener_nivel_actor(payload)
    rol_actual_id = user_db.get('id_rol')
    if rol_actual_id:
        nivel_actual = rbac_services.obtener_nivel_rol_destino(rol_actual_id)
        if nivel_actor > nivel_actual:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Violación de jerarquía: No puede modificar el estado de un usuario con mayor autoridad que la suya.")

    nuevo_estado = bool(data.get('activo', data.get('estado', True)))
    exito = users_repos.cambiar_estado_usuario_db(id_usuario, nuevo_estado)
    if not exito:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el estado del usuario.")

    try:
        bitacora_services.registrar_accion(
            modulo="USUARIOS",
            accion="CAMBIAR_ESTADO_USUARIO",
            nivel="INFO",
            resultado="EXITO",
            payload_jwt=payload,
            entidad="Usuario",
            id_entidad=str(id_usuario),
            descripcion=f"Estado de usuario #{id_usuario} cambiado a {'ACTIVO' if nuevo_estado else 'INACTIVO'}",
            datos_anteriores={"estado": user_db.get('estado')},
            datos_nuevos={"estado": 'ACTIVO' if nuevo_estado else 'INACTIVO'},
            request=request
        )
    except Exception as e:
        print(f"[BITACORA] Error al registrar cambio de estado: {e}")

    return {
        "success": True,
        "message": f"Usuario {'activado' if nuevo_estado else 'desactivado'} correctamente."
    }