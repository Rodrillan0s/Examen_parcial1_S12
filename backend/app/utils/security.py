import re
import random
import jwt
from datetime import datetime, timedelta, timezone
from app.config import Config
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from werkzeug.security import generate_password_hash, check_password_hash

bearer_scheme = HTTPBearer()

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
def create_access_token(nro_usuario, username, id_rol, id_empresa, nombre, apellido, roles=None, permisos=None, sucursales=None, nombre_empresa=None, minutes=120):
    payload = {
        'nro_usuario': nro_usuario,
        'username': username,
        'id_rol': id_rol,
        'id_empresa': id_empresa,
        'nombre_empresa': nombre_empresa,
        'nombre': nombre,
        'apellido': apellido,
        'roles': roles or [],
        'permisos': permisos or [],
        'sucursales': sucursales or [],
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
    return resultado.get('payload')

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