import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.utils.security import verificar_token, tiene_permiso
from app.repos import caja_repos

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/caja", tags=["W24 - Control de Caja y Arqueo"])

# --- DTOs ---

class ConteoDenominacionItemDTO(BaseModel):
    id_denominacion: int = Field(..., gt=0)
    cantidad: int = Field(..., ge=0)

class AbrirCajaDTO(BaseModel):
    id_caja: Optional[int] = Field(None, gt=0, description="ID de la caja física opcional")
    id_sucursal: Optional[int] = Field(None, gt=0, description="Sucursal donde opera el cajero")
    id_empresa: Optional[int] = Field(None, gt=0, description="Empresa de la caja")
    conteo: Optional[List[ConteoDenominacionItemDTO]] = Field(None, description="Conteo físico de billetes y monedas")
    conteo_items: Optional[List[ConteoDenominacionItemDTO]] = Field(None, description="Alias conteo_items")
    observacion: Optional[str] = Field(None, max_length=300)
    observaciones: Optional[str] = Field(None, max_length=300)

class CerrarCajaDTO(BaseModel):
    id_sesion_caja: Optional[int] = Field(None, gt=0)
    conteo: Optional[List[ConteoDenominacionItemDTO]] = Field(None, description="Conteo de efectivo para el arqueo")
    conteo_items: Optional[List[ConteoDenominacionItemDTO]] = Field(None, description="Alias conteo_items")
    observacion: Optional[str] = Field(None, max_length=300)
    observaciones: Optional[str] = Field(None, max_length=300)


def _verificar_permiso_cajero(token_data: dict) -> None:
    """
    Verifica que el usuario tenga rol de Cajero, Administrador o Encargado de Sucursal,
    o posea el permiso explícito caja.ver / caja.abrir.
    """
    if any(tiene_permiso(token_data, codigo) for codigo in ("caja.ver", "caja.abrir", "pos.vender")):
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acceso restringido. No tienes permisos para operar la caja registradora."
    )


def _obtener_empresa_efectiva(token_data: dict, id_empresa_solicitada: Optional[int] = None) -> int:
    alcance = token_data.get("alcance")
    id_empresa_jwt = token_data.get("id_empresa")
    if alcance != "PLATAFORMA" and id_empresa_jwt:
        return id_empresa_jwt
    if id_empresa_solicitada and id_empresa_solicitada > 0:
        return id_empresa_solicitada
    if id_empresa_jwt:
        return id_empresa_jwt
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El usuario no tiene una empresa autorizada.")


def _obtener_sucursal_efectiva(token_data: dict, id_sucursal_solicitada: Optional[int] = None, id_empresa: Optional[int] = None) -> int:
    """
    Determina la sucursal autorizada sin confiar en valores arbitrarios.
    """
    sucursales_usuario = token_data.get("sucursales", [])
    id_rol = token_data.get("id_rol")
    roles = [str(r).upper() for r in token_data.get("roles", [])]
    alcance = token_data.get("alcance")
    es_global = (id_rol == 1 or "ADMINISTRADOR" in roles or "SUPERADMIN" in roles or alcance == "PLATAFORMA")
    es_tienda = (alcance == "EMPRESA")

    if id_sucursal_solicitada:
        if es_global:
            return id_sucursal_solicitada
        if es_tienda and id_empresa:
            from app.classes.postgres import PostgreSQL
            from app.config import Config
            db = PostgreSQL()
            db.create_connection()
            try:
                schema = Config.SCHEMA or 'comercio'
                valida = db.execute_query(
                    f"SELECT 1 FROM {schema}.t_sucursal WHERE id_sucursal = %s AND id_empresa = %s AND activo = TRUE;",
                    (id_sucursal_solicitada, id_empresa),
                    fetchone=True
                )
                if valida:
                    return id_sucursal_solicitada
            finally:
                db.close_connection()
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes autorización sobre esta sucursal.")
        if id_sucursal_solicitada in sucursales_usuario:
            return id_sucursal_solicitada
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás autorizado para operar en la sucursal especificada."
        )

    if sucursales_usuario:
        return sucursales_usuario[0]

    if es_global or es_tienda:
        if id_empresa:
            from app.classes.postgres import PostgreSQL
            from app.config import Config
            db = PostgreSQL()
            db.create_connection()
            try:
                schema = Config.SCHEMA or 'comercio'
                row = db.execute_query(
                    f"SELECT id_sucursal FROM {schema}.t_sucursal WHERE id_empresa = %s AND activo = TRUE ORDER BY id_sucursal LIMIT 1;",
                    (id_empresa,),
                    fetchone=True
                )
                if row:
                    return row[0]
            finally:
                db.close_connection()
        return 1

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="El usuario no tiene una sucursal asignada para operar."
    )


# --- ENDPOINTS ---

@router.get('/denominaciones', summary="W24: Obtener catálogo de denominaciones monetarias")
def listar_denominaciones(token_data: dict = Depends(verificar_token)):
    _verificar_permiso_cajero(token_data)
    try:
        data = caja_repos.obtener_denominaciones_activas()
        return {
            "success": True,
            "denominaciones": data,
            "data": data
        }
    except Exception as e:
        logger.error(f"[DENOMINACIONES ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/estado', summary="W24: Consultar estado de la caja del cajero")
def obtener_estado_caja(
    id_sucursal: Optional[int] = Query(None, description="Sucursal a consultar"),
    id_empresa: Optional[int] = Query(None, description="Empresa a consultar"),
    token_data: dict = Depends(verificar_token)
):
    _verificar_permiso_cajero(token_data)
    try:
        id_usuario = token_data.get("nro_usuario") or token_data.get("id_usuario")
        id_emp = _obtener_empresa_efectiva(token_data, id_empresa)
        id_suc = _obtener_sucursal_efectiva(token_data, id_sucursal, id_emp)

        caja_asig = caja_repos.obtener_caja_disponible_sucursal(id_suc, id_emp)
        sesion_activa = caja_repos.obtener_sesion_activa_usuario(id_usuario, id_suc)

        if not sesion_activa:
            return {
                "success": True,
                "abierta": False,
                "tiene_sesion_activa": False,
                "caja_asignada": caja_asig,
                "sesion_activa": None,
                "id_sucursal": id_suc,
                "id_empresa": id_emp,
                "message": "No existe una caja abierta para tu usuario en esta sucursal.",
                "data": None
            }

        # Calcular resumen financiero en vivo de la sesión
        resumen = caja_repos.calcular_resumen_caja(sesion_activa["id_sesion_caja"])
        sesion_activa["resumen"] = resumen

        return {
            "success": True,
            "abierta": True,
            "tiene_sesion_activa": True,
            "caja_asignada": caja_asig,
            "sesion_activa": sesion_activa,
            "id_sucursal": id_suc,
            "id_empresa": id_emp,
            "message": "Caja abierta activa encontrada.",
            "data": sesion_activa
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ESTADO CAJA ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/abrir', summary="W24: Apertura de caja registradora mediante conteo físico")
def abrir_caja(
    body: AbrirCajaDTO,
    token_data: dict = Depends(verificar_token)
):
    _verificar_permiso_cajero(token_data)
    try:
        id_usuario = token_data.get("nro_usuario") or token_data.get("id_usuario")
        id_emp = _obtener_empresa_efectiva(token_data, body.id_empresa)
        id_suc = _obtener_sucursal_efectiva(token_data, body.id_sucursal, id_emp)

        # Si no se pasó id_caja, obtener o crear la caja por defecto de la sucursal
        id_caja = body.id_caja
        if not id_caja:
            caja_info = caja_repos.obtener_caja_disponible_sucursal(id_suc, id_emp)
            id_caja = caja_info["id_caja"]

        conteo_raw = body.conteo or body.conteo_items or []
        if not conteo_raw:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe ingresar el conteo físico de billetes y monedas.")

        conteo_dicts = [item.dict() for item in conteo_raw]
        obs = body.observacion or body.observaciones
        sesion = caja_repos.abrir_caja_sesion(
            id_usuario=id_usuario,
            id_sucursal=id_suc,
            id_empresa=id_emp,
            id_caja=id_caja,
            conteo_items=conteo_dicts,
            observacion=obs
        )

        return {
            "success": True,
            "message": f"Caja abierta exitosamente con un fondo inicial de Bs. {sesion['monto_inicial']:.2f}.",
            "sesion": sesion,
            "data": sesion
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ABRIR CAJA ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/resumen', summary="W24: Resumen financiero en vivo de la caja del turno")
def obtener_resumen_caja(
    id_sesion_caja: Optional[int] = Query(None, description="ID de sesión de caja opcional"),
    token_data: dict = Depends(verificar_token)
):
    _verificar_permiso_cajero(token_data)
    try:
        id_usuario = token_data.get("nro_usuario") or token_data.get("id_usuario")
        if not id_sesion_caja:
            sesion = caja_repos.obtener_sesion_activa_usuario(id_usuario)
            if not sesion:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tienes una sesión de caja abierta.")
            id_sesion_caja = sesion["id_sesion_caja"]

        resumen = caja_repos.calcular_resumen_caja(id_sesion_caja)
        return {
            "success": True,
            "resumen": resumen,
            "data": resumen
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[RESUMEN CAJA ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/cerrar', summary="W24: Cierre de caja registradora mediante conteo y arqueo")
def cerrar_caja(
    body: CerrarCajaDTO,
    token_data: dict = Depends(verificar_token)
):
    _verificar_permiso_cajero(token_data)
    try:
        id_usuario = token_data.get("nro_usuario") or token_data.get("id_usuario")
        id_sesion = body.id_sesion_caja
        if not id_sesion:
            sesion = caja_repos.obtener_sesion_activa_usuario(id_usuario)
            if not sesion:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tienes una sesión de caja abierta para cerrar.")
            id_sesion = sesion["id_sesion_caja"]

        conteo_raw = body.conteo or body.conteo_items or []
        if not conteo_raw:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe ingresar el conteo físico de billetes y monedas.")

        conteo_dicts = [item.dict() for item in conteo_raw]
        obs = body.observacion or body.observaciones
        cierre = caja_repos.cerrar_caja_sesion(
            id_sesion_caja=id_sesion,
            id_usuario=id_usuario,
            conteo_items=conteo_dicts,
            observacion=obs
        )

        dif = cierre["diferencia"]
        estado_dif = cierre["estado_diferencia"]
        mensaje = f"Caja cerrada exitosamente. Arqueo: {estado_dif} (Bs. {abs(dif):.2f})."

        return {
            "success": True,
            "message": mensaje,
            "cierre": cierre,
            "data": cierre
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CERRAR CAJA ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
