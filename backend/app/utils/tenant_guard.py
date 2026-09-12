from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from app.classes.postgres import PostgreSQL
from app.config import Config

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

# --- IDENTIFICACIÓN DE ALCANCE Y ROLES ---

def obtener_alcance_usuario(payload: dict) -> str:
    """
    Determina el alcance de seguridad del usuario autenticado:
    - 'PLATAFORMA': Administrador global / Superadmin sin empresa fija.
    - 'EMPRESA': Administrador de tienda o usuario acotado a un Tenant específico.
    - 'SUCURSAL': Encargado o cajero acotado a sucursal(es).
    """
    id_rol = payload.get('id_rol')
    roles = [str(r).upper() for r in payload.get('roles', [])]
    nombre_rol = str(payload.get('nombre_rol', '')).upper()
    id_empresa = payload.get('id_empresa')

    if (id_rol == 1 or 'ADMINISTRADOR' in roles or nombre_rol == 'ADMINISTRADOR' or 'SUPERADMIN' in roles) and not id_empresa:
        return 'PLATAFORMA'
    
    if id_rol == 3 or 'ADMINISTRADOR_TIENDA' in roles or nombre_rol == 'ADMINISTRADOR_TIENDA':
        return 'EMPRESA'

    if id_empresa:
        return 'EMPRESA'

    return 'PLATAFORMA' if (id_rol == 1 or 'ADMINISTRADOR' in roles) else 'EMPRESA'

def es_administrador_global(payload: dict) -> bool:
    """Retorna True solo si el usuario tiene alcance global/multitenant."""
    return obtener_alcance_usuario(payload) == 'PLATAFORMA'

def es_administrador_tienda(payload: dict) -> bool:
    """Retorna True si el usuario es Administrador de Tienda (acotado a su empresa)."""
    id_rol = payload.get('id_rol')
    roles = [str(r).upper() for r in payload.get('roles', [])]
    nombre_rol = str(payload.get('nombre_rol', '')).upper()
    return id_rol == 3 or 'ADMINISTRADOR_TIENDA' in roles or nombre_rol == 'ADMINISTRADOR_TIENDA'

# --- RESOLUCIÓN Y VALIDACIÓN DE TENANT EFECTIVO ---

def resolver_tenant_operacion(
    payload: dict,
    id_empresa_solicitado: Optional[int] = None,
    permitir_global: bool = False
) -> Optional[int]:
    """
    Determina el ID de empresa obligatorio para una operación:
    - Para ADMINISTRADOR_TIENDA (o usuarios con empresa):
      FUERZA estrictamente su propio id_empresa. Si envió un id_empresa diferente en el cuerpo o query,
      lo rechaza con 403 Forbidden. Nunca permite operar sin tenant.
    - Para ADMINISTRADOR global:
      Permite indicar explícitamente el tenant deseado (validando que exista en la BD).
      Si no se envía tenant y 'permitir_global' es False (e.g. crear productos, sucursales, etc.),
      exige seleccionar un tenant con 400 Bad Request.
    """
    es_global = es_administrador_global(payload)
    id_empresa_sesion = payload.get('id_empresa')

    if not es_global:
        # Monotenant estricto
        if not id_empresa_sesion:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: El usuario no tiene asignado un Tenant (empresa) válido."
            )
        id_empresa_sesion = int(id_empresa_sesion)
        if id_empresa_solicitado is not None and int(id_empresa_solicitado) != id_empresa_sesion:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Violación de Tenant: No tiene autorización para consultar o gestionar recursos de otra empresa (Solicitado: #{id_empresa_solicitado}, Autorizado: #{id_empresa_sesion})."
            )
        return id_empresa_sesion

    # Es ADMINISTRADOR Global / Multi-tenant
    if id_empresa_solicitado is not None and int(id_empresa_solicitado) > 0:
        empresa_id = int(id_empresa_solicitado)
        # Validar existencia de la empresa en la BD
        db = PostgreSQL()
        db.create_connection()
        try:
            schema = _get_schema()
            row = db.execute_query(
                f"SELECT id_empresa, estado FROM {schema}.empresa WHERE id_empresa = %s;",
                (empresa_id,),
                fetchone=True
            )
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El Tenant seleccionado con ID #{empresa_id} no existe en el sistema."
                )
            if row[1] != 'ACTIVO':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El Tenant #{empresa_id} se encuentra inactivo."
                )
            return empresa_id
        finally:
            db.close_connection()

    if not permitir_global:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Como Administrador Global, debe seleccionar o identificar explícitamente el Tenant correspondiente para esta operación."
        )

    return None

# --- VALIDACIÓN DE ACCESO A UN RECURSO ESPECÍFICO ---

def validar_acceso_recurso_tenant(
    payload: dict,
    id_empresa_recurso: Optional[int],
    nombre_recurso: str = "recurso"
):
    """
    Verifica que el recurso pertenezca al Tenant del usuario.
    Si el usuario es Administrador Global, se le permite el acceso.
    Si el usuario es Monotenant y el recurso es de otra empresa, lanza 403 Forbidden.
    """
    if es_administrador_global(payload):
        return  # Administrador global autorizado

    id_empresa_sesion = payload.get('id_empresa')
    if not id_empresa_sesion:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado: Usuario sin empresa asignada para acceder a este {nombre_recurso}."
        )

    if id_empresa_recurso is None or int(id_empresa_recurso) != int(id_empresa_sesion):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado: El {nombre_recurso} pertenece a otro Tenant o no tiene permisos para acceder a él."
        )

# --- VALIDACIÓN DE RELACIONES ENTRE ENTIDADES (NO MEZCLAR TENANTS) ---

def validar_relaciones_tenant(
    id_empresa: int,
    id_categoria: Optional[int] = None,
    tallas_ids: Optional[List[int]] = None,
    colores_ids: Optional[List[int]] = None,
    id_ciudad: Optional[int] = None
):
    """
    Garantiza que ninguna de las entidades foráneas vinculadas a una operación
    pertenezca a un Tenant diferente.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        # 1. Validar Categoría
        if id_categoria:
            row_cat = db.execute_query(
                f"SELECT id_empresa, activo, nombre FROM {schema}.t_categoria WHERE id_categoria = %s;",
                (id_categoria,),
                fetchone=True
            )
            if not row_cat:
                raise HTTPException(status_code=400, detail=f"La categoría #{id_categoria} no existe.")
            if row_cat[0] is not None and int(row_cat[0]) != int(id_empresa):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"La categoría '{row_cat[2]}' pertenece a otro Tenant y no puede asociarse a este recurso."
                )

        # 2. Validar Tallas
        if tallas_ids:
            for t_id in tallas_ids:
                row_t = db.execute_query(
                    f"SELECT id_empresa, activo, nombre FROM {schema}.t_talla WHERE id_talla = %s;",
                    (t_id,),
                    fetchone=True
                )
                if not row_t:
                    raise HTTPException(status_code=400, detail=f"La talla #{t_id} no existe.")
                if row_t[0] is not None and int(row_t[0]) != int(id_empresa):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"La talla '{row_t[2]}' pertenece a otro Tenant."
                    )

        # 3. Validar Colores
        if colores_ids:
            for c_id in colores_ids:
                row_c = db.execute_query(
                    f"SELECT id_empresa, activo, nombre FROM {schema}.t_color WHERE id_color = %s;",
                    (c_id,),
                    fetchone=True
                )
                if not row_c:
                    raise HTTPException(status_code=400, detail=f"El color #{c_id} no existe.")
                if row_c[0] is not None and int(row_c[0]) != int(id_empresa):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"El color '{row_c[2]}' pertenece a otro Tenant."
                    )

        # 4. Validar Ciudad (referencia geográfica)
        if id_ciudad:
            row_ciu = db.execute_query(
                f"SELECT activo, nombre FROM {schema}.t_ciudad WHERE id_ciudad = %s;",
                (id_ciudad,),
                fetchone=True
            )
            if not row_ciu:
                raise HTTPException(status_code=400, detail="La ciudad seleccionada no existe.")
            if not row_ciu[0]:
                raise HTTPException(status_code=400, detail=f"La ciudad '{row_ciu[1]}' se encuentra inactiva.")

    finally:
        db.close_connection()
