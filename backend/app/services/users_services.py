from app.repos import users_repos
from werkzeug.security import generate_password_hash
from fastapi import Request
from app.services import bitacora_services

def is_global_admin(payload: dict) -> bool:
    roles = payload.get('roles', [])
    id_rol = payload.get('id_rol')
    return 'ADMINISTRADOR' in roles or id_rol == 1

def listar_usuarios(payload: dict):
    if is_global_admin(payload):
        usuarios = users_repos.obtener_todos_los_usuarios()
    else:
        id_empresa = payload.get('id_empresa')
        usuarios = users_repos.obtener_usuarios_por_empresa(id_empresa)
        
    return {
        "success": True,
        "message": "Usuarios recuperados exitosamente",
        "data": usuarios
    }

def registrar_usuario(data: dict, payload: dict, request: Request = None):
    campos_requeridos = ['nombre_completo', 'nombre_usuario', 'password', 'id_empresa']
    for campo in campos_requeridos:
        if not data.get(campo):
            raise ValueError(f"El campo '{campo}' es obligatorio.")

    id_rol = data.get('nro_rol') or data.get('id_rol')
    if not id_rol:
        raise ValueError("El campo 'nro_rol' o 'id_rol' es obligatorio.")
        
    # Tenant Isolation Validation
    if not is_global_admin(payload):
        if int(data['id_empresa']) != int(payload.get('id_empresa')):
            raise ValueError("No tiene permisos para crear usuarios en otra empresa.")
        if int(id_rol) == 1:
            raise ValueError("No tiene permisos para asignar el rol de ADMINISTRADOR global.")

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
        'id_empresa': int(data['id_empresa']),
        'id_rol': int(id_rol)
    }

    nuevo_id = users_repos.crear_usuario_db(None, datos_usuario)
    
    # Quitar password del log
    datos_log = {k: v for k, v in datos_usuario.items() if k != 'password_hash'}

    bitacora_services.registrar_accion(
        modulo="USUARIOS", accion="USUARIO_CREADO", nivel="INFO", resultado="EXITO",
        payload_jwt=payload, entidad="Usuario", id_entidad=str(nuevo_id),
        descripcion=f"Usuario creado: {nombre_completo}",
        datos_nuevos=datos_log,
        request=request
    )

    return {
        "success": True,
        "message": "Usuario registrado exitosamente",
        "nro_usuario": nuevo_id
    }

def actualizar_usuario(id_usuario: int, data: dict, payload: dict, request: Request = None):
    nro_usuario = id_usuario
    if nro_usuario <= 0:
        raise ValueError("ID de usuario no válido.")
        
    campos_requeridos = ['nombre_completo', 'nombre_usuario', 'id_empresa']
    for campo in campos_requeridos:
        if not data.get(campo):
            raise ValueError(f"El campo '{campo}' es obligatorio.")

    id_rol = data.get('nro_rol') or data.get('id_rol')
    if not id_rol:
        raise ValueError("El campo 'nro_rol' o 'id_rol' es obligatorio.")
        
    # Tenant Isolation Validation
    if not is_global_admin(payload):
        user_db = users_repos.obtener_usuario_por_id(nro_usuario)
        if not user_db or int(user_db.get('id_empresa', 0)) != int(payload.get('id_empresa')):
            raise ValueError("No tiene permisos para editar a este usuario.")
        if int(data['id_empresa']) != int(payload.get('id_empresa')):
            raise ValueError("No puede mover un usuario a otra empresa.")
        if int(id_rol) == 1:
            raise ValueError("No tiene permisos para asignar el rol de ADMINISTRADOR global.")

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
        'id_empresa': int(data['id_empresa']),
        'id_rol': int(id_rol)
    }

    cambiar_password = False
    if data.get('password') and len(str(data.get('password')).strip()) > 0:
        cambiar_password = True
        datos_usuario['password_hash'] = generate_password_hash(data['password'])
        
    user_db_before = users_repos.obtener_usuario_por_id(nro_usuario)
    if not user_db_before:
        raise ValueError("Usuario no encontrado.")

    users_repos.actualizar_usuario_db(nro_usuario, data.get('ci'), None, datos_usuario, cambiar_password)
    
    # Audit log
    datos_log = {k: v for k, v in datos_usuario.items() if k != 'password_hash'}
    datos_anteriores = {k: v for k, v in user_db_before.items() if k != 'password_hash'}

    bitacora_services.registrar_accion(
        modulo="USUARIOS", accion="USUARIO_EDITADO", nivel="INFO", resultado="EXITO",
        payload_jwt=payload, entidad="Usuario", id_entidad=str(nro_usuario),
        descripcion=f"Usuario editado: {nombre_completo}",
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_log,
        request=request
    )

    return {
        "success": True,
        "message": "Usuario actualizado exitosamente"
    }

def eliminar_usuario(id_usuario: int, payload: dict, request: Request = None):
    nro_usuario = id_usuario
    if nro_usuario <= 0:
        raise ValueError("ID de usuario no válido.")
        
    if not is_global_admin(payload):
        user_db = users_repos.obtener_usuario_por_id(nro_usuario)
        if not user_db or int(user_db.get('id_empresa', 0)) != int(payload.get('id_empresa')):
            raise ValueError("No tiene permisos para eliminar a este usuario.")
        
    users_repos.eliminar_usuario_db(nro_usuario)
    
    bitacora_services.registrar_accion(
        modulo="USUARIOS", accion="USUARIO_ELIMINADO", nivel="WARNING", resultado="EXITO",
        payload_jwt=payload, entidad="Usuario", id_entidad=str(nro_usuario),
        descripcion=f"Usuario eliminado",
        datos_anteriores={"activo": True},
        datos_nuevos={"activo": False},
        request=request
    )
    
    return {
        "success": True,
        "message": "Usuario eliminado correctamente."
    }