from fastapi import Request
import uuid
import json
import logging
from app.repos import bitacora_repos
from datetime import datetime

logger = logging.getLogger(__name__)

# Keys to remove from payloads to avoid leaking sensitive data
SENSITIVE_KEYS = {'password', 'password_hash', 'token', 'access_token', 'refresh_token', 'secret', 'api_key', 'credentials'}

def sanitizar_dict(data: dict) -> dict:
    if not data or not isinstance(data, dict):
        return data
        
    sanitized = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_KEYS:
            continue
        if isinstance(v, dict):
            sanitized[k] = sanitizar_dict(v)
        elif isinstance(v, list):
            sanitized[k] = [sanitizar_dict(item) if isinstance(item, dict) else item for item in v]
        elif isinstance(v, datetime):
            sanitized[k] = v.isoformat()
        else:
            sanitized[k] = v
    return sanitized

def get_scope_level(payload: dict) -> str:
    roles = [r.upper() for r in payload.get('roles', [])]
    if 'ADMINISTRADOR' in roles or payload.get('id_rol') == 1:
        return 'PLATAFORMA'
    if 'ADMINISTRADOR_TIENDA' in roles:
        return 'EMPRESA'
    if 'ENCARGADO_SUCURSAL' in roles or 'CAJERO' in roles:
        return 'SUCURSAL'
    return 'PLATAFORMA' if not payload.get('id_empresa') else 'EMPRESA'

def registrar_accion(
    modulo: str,
    accion: str,
    nivel: str,
    resultado: str,
    payload_jwt: dict = None,
    entidad: str = None,
    id_entidad: str = None,
    descripcion: str = None,
    datos_anteriores: dict = None,
    datos_nuevos: dict = None,
    metadatos: dict = None,
    request: Request = None
):
    try:
        payload = payload_jwt or {}
        id_usuario = payload.get("id_usuario")
        usuario_nombre = payload.get("username")
        
        # Determine scopes from context if not available in payload
        # Generally we just take what's in the JWT for id_empresa, unless an explicit context was given.
        id_empresa = payload.get("id_empresa")
        id_sucursal = None # Sucursal can be determined if needed, JWT doesn't always have it depending on the system
        
        ip = None
        user_agent = None
        request_id = None
        
        if request:
            # Extract real IP and user agent
            # Handles X-Forwarded-For if behind a proxy
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                ip = forwarded.split(",")[0].strip()
            else:
                ip = request.client.host if request.client else None
                
            user_agent = request.headers.get("user-agent")
            
            # Simple unique ID for the request if not injected via middleware
            request_id = str(uuid.uuid4())
            
        sanitized_anteriores = sanitizar_dict(datos_anteriores)
        sanitized_nuevos = sanitizar_dict(datos_nuevos)
        sanitized_metadatos = sanitizar_dict(metadatos)

        bitacora_repos.registrar_evento_db(
            id_usuario=id_usuario,
            usuario_nombre=usuario_nombre,
            usuario_email=None,  # We may not have email in payload directly
            id_empresa=id_empresa,
            id_sucursal=id_sucursal,
            modulo=modulo,
            accion=accion,
            entidad=entidad,
            id_entidad=str(id_entidad) if id_entidad else None,
            descripcion=descripcion,
            resultado=resultado,
            nivel=nivel,
            ip=ip,
            user_agent=user_agent,
            datos_anteriores=sanitized_anteriores,
            datos_nuevos=sanitized_nuevos,
            metadatos=sanitized_metadatos,
            request_id=request_id
        )
    except Exception as e:
        logger.error(f"Error al registrar acción en bitácora: {e}")

def obtener_eventos(
    payload: dict,
    filtros: dict,
    page: int = 1,
    limit: int = 25
):
    # RBAC & Scope enforcement
    scope = get_scope_level(payload)
    
    id_empresa_filtro = None
    id_sucursal_filtro = None
    
    if scope == 'PLATAFORMA':
        # Admin can view all, or filter by requested empresa
        id_empresa_filtro = filtros.get('id_empresa')
        id_sucursal_filtro = filtros.get('id_sucursal')
    elif scope == 'EMPRESA':
        # Tienda Admin can only view their own empresa
        id_empresa_filtro = payload.get('id_empresa')
        id_sucursal_filtro = filtros.get('id_sucursal')
    elif scope == 'SUCURSAL':
        # Encargado can only view their own sucursal (assuming it's passed or known, but we don't have id_sucursal in token)
        # We would need to verify the user's sucursales, but for MVP we restrict to empresa and if they pass sucursal
        id_empresa_filtro = payload.get('id_empresa')
        # If the user is Encargado, ideally they only see their assigned branch.
        # But for now, since JWT doesn't store id_sucursal, we assume they can only see their empresa.
        # In a real scenario we'd query their assigned branch.
        
    offset = (page - 1) * limit
    
    res = bitacora_repos.obtener_eventos_db(
        id_empresa_filtro=id_empresa_filtro,
        id_sucursal_filtro=id_sucursal_filtro,
        filtros=filtros,
        limit=limit,
        offset=offset
    )
    
    total = res['total']
    pages = (total + limit - 1) // limit
    
    return {
        "success": True,
        "data": res['items'],
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages
    }

def obtener_detalle_evento(id_bitacora: int, payload: dict):
    evento = bitacora_repos.obtener_detalle_evento_db(id_bitacora)
    
    if not evento:
        raise ValueError("Evento no encontrado.")
        
    scope = get_scope_level(payload)
    if scope != 'PLATAFORMA':
        # User can only view events from their own empresa
        if evento['id_empresa'] and evento['id_empresa'] != payload.get('id_empresa'):
            raise ValueError("No tiene permisos para ver el detalle de este evento.")
            
    return {
        "success": True,
        "data": evento
    }
