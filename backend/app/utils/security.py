from typing import Optional
import re
import random
import jwt
from datetime import datetime, timedelta, timezone
from app.config import Config
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from werkzeug.security import generate_password_hash, check_password_hash

bearer_scheme = HTTPBearer()
optional_bearer_scheme = HTTPBearer(auto_error=False)

# Valida que la contraseña tenga al menos 8 caracteres y 1 carácter especial.
def validar_password(password: str) -> bool:
    if not password or len(password) < 8:
        return False
    # Al menos un carácter especial
    pattern = r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]'
    return bool(re.search(pattern, password))

# Genera un hash seguro para la contraseña del usuario.
def hash_password(password: str) -> str:
    return generate_password_hash(password)

# Comprueba si una contraseña en texto plano coincide con su hash almacenado.
def verificar_password_hash(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)

# Genera un código numérico aleatorio de 6 dígitos para verificaciones o recuperación.
def generar_codigo_seguridad() -> str:
    return str(random.randint(100000, 999999))

# Genera el token JWT de acceso para la sesión del usuario con sus claims RBAC.
def create_access_token(nro_usuario, username, id_rol, id_empresa, nombre, apellido, roles=None, permisos=None, sucursales=None, nombre_empresa=None, nombre_rol=None, minutes=120):
    roles_list = roles or []
    roles_upper = [str(r).upper() for r in roles_list]
    es_global = (id_rol == 1 or 'ADMINISTRADOR' in roles_upper or 'SUPERADMIN' in roles_upper) and (id_empresa is None or id_empresa == 0)

    if es_global:
        alcance = 'PLATAFORMA'
    elif id_rol in (1, 3) or 'ADMINISTRADOR' in roles_upper or 'ADMINISTRADOR_TIENDA' in roles_upper:
        alcance = 'EMPRESA'
    elif id_rol in (4, 5) or any(r in ('CAJERO', 'EMPLEADO', 'ENCARGADO', 'ENCARGADO_SUCURSAL') for r in roles_upper):
        alcance = 'SUCURSAL'
    elif id_empresa and id_empresa > 0:
        alcance = 'SUCURSAL'
    else:
        alcance = 'PLATAFORMA'

    rol_final = nombre_rol or (roles_list[0] if roles_list else 'CLIENTE')

    payload = {
        'nro_usuario': nro_usuario,
        'id_usuario': nro_usuario,
        'username': username,
        'id_rol': id_rol,
        'nombre_rol': rol_final,
        'id_empresa': id_empresa,
        'nombre_empresa': nombre_empresa,
        'nombre': nombre,
        'apellido': apellido,
        'roles': roles_list,
        'permisos': permisos or [],
        'sucursales': sucursales or [],
        'alcance': alcance,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=minutes),
        'iat': datetime.now(timezone.utc)
    }
    secret_key = Config.TOKEN_KEY or Config.SECRET_KEY or 'secret_jwt_key'
    return jwt.encode(payload, secret_key, algorithm="HS256")

# Decodifica y valida la firma del token JWT recibido.
def decode_access_token(token: str):
    try:
        secret_key = Config.TOKEN_KEY or Config.SECRET_KEY or 'secret_jwt_key'
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return {
            'success': True,
            'message': 'TOKEN VALIDO',
            'payload': payload
        }
    except jwt.ExpiredSignatureError:
        return {
            'success': False,
            'message': 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.'
        }
    except jwt.InvalidTokenError:
        return {
            'success': False,
            'message': 'Token de acceso inválido o corrupto.'
        }

# Extrae y valida el token Bearer del header de la petición HTTP.
def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    resultado = decode_access_token(token)
    if not resultado.get('success'):
        raise HTTPException(status_code=401, detail=resultado.get('message'))
    payload = resultado.get('payload')
    
    # Garantizar consistencia de id_usuario y alcance
    if 'id_usuario' not in payload and 'nro_usuario' in payload:
        payload['id_usuario'] = payload['nro_usuario']
    if 'alcance' not in payload:
        roles_upper = [str(r).upper() for r in payload.get('roles', [])]
        id_rol = payload.get('id_rol')
        id_emp = payload.get('id_empresa')
        es_glob = (id_rol == 1 or 'ADMINISTRADOR' in roles_upper or 'SUPERADMIN' in roles_upper) and (id_emp is None or id_emp == 0)
        payload['alcance'] = 'PLATAFORMA' if es_glob else 'EMPRESA'
        
    return payload

# Extrae y valida el token Bearer opcionalmente (permite visitantes no autenticados)
def verificar_token_opcional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer_scheme)):
    if not credentials:
        return None
    resultado = decode_access_token(credentials.credentials)
    if not resultado.get('success'):
        return None
    payload = resultado.get('payload')
    if not payload:
        return None
    if 'id_usuario' not in payload and 'nro_usuario' in payload:
        payload['id_usuario'] = payload['nro_usuario']
    if 'alcance' not in payload:
        roles_upper = [str(r).upper() for r in payload.get('roles', [])]
        id_rol = payload.get('id_rol')
        id_emp = payload.get('id_empresa')
        es_glob = (id_rol == 1 or 'ADMINISTRADOR' in roles_upper or 'SUPERADMIN' in roles_upper) and (id_emp is None or id_emp == 0)
        payload['alcance'] = 'PLATAFORMA' if es_glob else 'EMPRESA'
    return payload

# Dependencia reutilizable FastAPI para autorizar según el permiso requerido (<recurso>.<accion>)
def require_permission(codigo_permiso: str):
    def dependency(payload: dict = Depends(verificar_token)):
        # 1. Intentar validar permiso mediante el JWT actual
        permisos_jwt = payload.get('permisos', [])
        if codigo_permiso in permisos_jwt:
            return payload

        # 2. Consulta de permisos efectivos en caliente en la BD (para evitar JWT desactualizados)
        from app.repos import rbac_repos
        id_usuario = payload.get('nro_usuario') or payload.get('id_usuario')
        if id_usuario:
            permisos_bd = rbac_repos.obtener_permisos_efectivos_usuario(id_usuario)
            if codigo_permiso in permisos_bd:
                return payload

        # 3. Si no posee el permiso -> 403 Forbidden
        raise HTTPException(
            status_code=403,
            detail=f"Acceso denegado. No posee el permiso requerido: '{codigo_permiso}'"
        )
    return dependency

# Valida acceso administrativo basándose exclusivamente en el permiso 'admin.acceder'
def verificar_token_admin(payload: dict = Depends(verificar_token)):
    permisos_jwt = payload.get('permisos', [])
    if 'admin.acceder' in permisos_jwt:
        return payload
        
    from app.repos import rbac_repos
    id_usuario = payload.get('nro_usuario') or payload.get('id_usuario')
    if id_usuario:
        permisos_bd = rbac_repos.obtener_permisos_efectivos_usuario(id_usuario)
        if 'admin.acceder' in permisos_bd:
            return payload
            
    raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere el permiso 'admin.acceder'.")