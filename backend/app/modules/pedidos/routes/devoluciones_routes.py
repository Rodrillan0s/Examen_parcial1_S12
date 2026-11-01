"""
AuroraStore Iteración 3 — Rutas API de Devoluciones (CU24W / CU25W)
Rutas protegidas con RBAC granular, aislamiento multitenant y validación Pydantic.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from app.core.security import verificar_token, require_permission
from app.modules.pedidos.services import devoluciones_services

router = APIRouter(prefix="/api/devoluciones", tags=["Devoluciones"])

# ==============================================================================
# DTOs
# ==============================================================================

class ItemDevolucionSolicitudDTO(BaseModel):
    id_detalle_venta: int = Field(..., gt=0, description="ID del ítem en la venta original")
    cantidad: int = Field(..., gt=0, description="Cantidad a devolver")

class SolicitarDevolucionClienteDTO(BaseModel):
    id_venta: int = Field(..., gt=0, description="ID de la venta")
    id_empresa: Optional[int] = Field(None, description="ID del Tenant")
    motivo: str = Field(..., min_length=3, max_length=150, description="Motivo de la devolución")
    descripcion: Optional[str] = Field(None, max_length=1000, description="Explicación detallada del cliente")
    evidencia_url: Optional[str] = Field(None, description="URL de foto o evidencia adjunta")
    items: List[ItemDevolucionSolicitudDTO] = Field(..., min_length=1, description="Prendas seleccionadas")

class ItemDevolucionPresencialDTO(BaseModel):
    id_detalle_venta: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    condicion: str = Field("REVENDIBLE", description="REVENDIBLE o DEFECTUOSO / NO_REVENDIBLE")

class RegistrarDevolucionPresencialDTO(BaseModel):
    id_venta: int = Field(..., gt=0)
    id_sucursal: Optional[int] = Field(None, description="Sucursal física donde se recibe la prenda")
    id_empresa: Optional[int] = Field(None, description="ID del Tenant")
    motivo: str = Field(..., min_length=3, max_length=150)
    observaciones: Optional[str] = Field(None, max_length=1000)
    items: List[ItemDevolucionPresencialDTO] = Field(..., min_length=1)
    registrar_reembolso_inmediato: bool = Field(False)
    metodo_reembolso: Optional[str] = Field(None, description="EFECTIVO, etc.")
    referencia_reembolso: Optional[str] = Field(None, max_length=150)

class DictaminarSolicitudDTO(BaseModel):
    accion: str = Field(..., description="APROBAR, RECHAZAR o EN_REVISION")
    observaciones: str = Field(..., min_length=3, max_length=1000, description="Justificación técnica del dictamen")
    id_empresa: Optional[int] = Field(None)

class ItemInspeccionRecepcionDTO(BaseModel):
    id_detalle_devolucion: int = Field(..., gt=0)
    cantidad_recibida: int = Field(..., gt=0)
    condicion: str = Field("REVENDIBLE", description="REVENDIBLE o DEFECTUOSO")

class RegistrarRecepcionPrendasDTO(BaseModel):
    id_sucursal: Optional[int] = Field(None)
    id_empresa: Optional[int] = Field(None)
    observaciones: Optional[str] = Field(None, max_length=1000)
    items: List[ItemInspeccionRecepcionDTO] = Field(..., min_length=1)

class LiquidarReembolsoDTO(BaseModel):
    metodo_reembolso: str = Field(..., min_length=2, max_length=50, description="EFECTIVO, TRANSFERENCIA, TARJETA_PASARELA")
    referencia_reembolso: str = Field(..., min_length=2, max_length=150, description="Número de comprobante o autorización bancaria")
    observaciones: Optional[str] = Field(None, max_length=500)
    id_empresa: Optional[int] = Field(None)

# ==============================================================================
# Rutas para CLIENTE (CU25W)
# ==============================================================================

@router.get('/ventas/{id_venta}/elegibilidad', summary="Consultar saldo elegible de una venta para devolución")
def consultar_elegibilidad_venta(
    id_venta: int,
    id_empresa: Optional[int] = Query(None, description="ID del Tenant"),
    token_data: dict = Depends(verificar_token)
):
    try:
        return devoluciones_services.consultar_elegibilidad_venta(
            id_venta=id_venta,
            token_data=token_data,
            id_empresa_solicitado=id_empresa
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar elegibilidad de la venta: {str(e)}"
        )

@router.post('/solicitudes', status_code=status.HTTP_201_CREATED, summary="CU25W: Solicitar devolución online (Cliente)")
def solicitar_devolucion(
    body: SolicitarDevolucionClienteDTO,
    token_data: dict = Depends(verificar_token)
):
    try:
        return devoluciones_services.solicitar_devolucion_cliente(
            datos=body.model_dump(),
            token_data=token_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la solicitud de devolución: {str(e)}"
        )

@router.get('/mis-solicitudes', summary="CU25W: Listar mis devoluciones solicitadas")
def listar_mis_devoluciones(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    id_empresa: Optional[int] = Query(None),
    token_data: dict = Depends(verificar_token)
):
    try:
        offset = (page - 1) * limit
        res = devoluciones_services.listar_mis_devoluciones(
            token_data=token_data,
            limit=limit,
            offset=offset,
            id_empresa_solicitado=id_empresa
        )
        total = res.get("total", 0)
        total_paginas = (total + limit - 1) // limit if total > 0 else 1
        return {
            "success": True,
            "data": res.get("data", []),
            "total": total,
            "page": page,
            "limit": limit,
            "total_paginas": total_paginas
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar mis devoluciones: {str(e)}"
        )

@router.get('/mis-solicitudes/{id_devolucion}', summary="CU25W: Ver detalle de mi solicitud de devolución")
def ver_mi_devolucion(
    id_devolucion: int,
    id_empresa: Optional[int] = Query(None),
    token_data: dict = Depends(verificar_token)
):
    try:
        return devoluciones_services.consultar_detalle_devolucion(
            id_devolucion=id_devolucion,
            token_data=token_data,
            id_empresa_solicitado=id_empresa
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el detalle de la devolución: {str(e)}"
        )

# ==============================================================================
# Rutas para PERSONAL AUTORIZADO (CU24W)
# ==============================================================================

@router.get('', summary="CU24W: Bandeja administrativa de devoluciones")
def listar_devoluciones_personal(
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100),
    estado: Optional[str] = Query(None),
    id_sucursal: Optional[int] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    busqueda: Optional[str] = Query(None),
    id_empresa: Optional[int] = Query(None),
    token_data: dict = Depends(require_permission('devoluciones.ver'))
):
    try:
        offset = (page - 1) * limit
        res = devoluciones_services.listar_bandeja_personal(
            token_data=token_data,
            estado=estado,
            id_sucursal=id_sucursal,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            busqueda=busqueda,
            limit=limit,
            offset=offset,
            id_empresa_solicitado=id_empresa
        )
        total = res.get("total", 0)
        total_paginas = (total + limit - 1) // limit if total > 0 else 1
        return {
            "success": True,
            "data": res.get("data", []),
            "total": total,
            "page": page,
            "limit": limit,
            "total_paginas": total_paginas
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar la bandeja de devoluciones: {str(e)}"
        )

@router.get('/{id_devolucion}', summary="CU24W: Ver detalle administrativo de una devolución")
def ver_detalle_devolucion_personal(
    id_devolucion: int,
    id_empresa: Optional[int] = Query(None),
    token_data: dict = Depends(require_permission('devoluciones.ver'))
):
    try:
        return devoluciones_services.consultar_detalle_devolucion(
            id_devolucion=id_devolucion,
            token_data=token_data,
            id_empresa_solicitado=id_empresa
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener detalle de la devolución: {str(e)}"
        )

@router.post('/presencial', status_code=status.HTTP_201_CREATED, summary="CU24W: Registrar devolución presencial directa en mostrador")
def registrar_presencial(
    body: RegistrarDevolucionPresencialDTO,
    token_data: dict = Depends(require_permission('devoluciones.crear_presencial'))
):
    try:
        return devoluciones_services.registrar_devolucion_presencial_mostrador(
            datos=body.model_dump(),
            token_data=token_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar la devolución presencial: {str(e)}"
        )

@router.post('/{id_devolucion}/revisar', summary="CU24W: Dictaminar solicitud (Aprobar / Rechazar)")
def resolver_solicitud(
    id_devolucion: int,
    body: DictaminarSolicitudDTO,
    token_data: dict = Depends(require_permission('devoluciones.aprobar_rechazar'))
):
    try:
        return devoluciones_services.resolver_solicitud(
            id_devolucion=id_devolucion,
            datos=body.model_dump(),
            token_data=token_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al dictaminar la solicitud de devolución: {str(e)}"
        )

@router.post('/{id_devolucion}/recepcion', summary="CU24W: Registrar recepción física e inspección de prendas")
def registrar_recepcion(
    id_devolucion: int,
    body: RegistrarRecepcionPrendasDTO,
    token_data: dict = Depends(require_permission('devoluciones.recibir'))
):
    try:
        return devoluciones_services.registrar_recepcion(
            id_devolucion=id_devolucion,
            datos=body.model_dump(),
            token_data=token_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar la recepción de prendas: {str(e)}"
        )

@router.post('/{id_devolucion}/reembolso', summary="CU24W: Registrar liquidación de reembolso financiero")
def liquidar_reembolso(
    id_devolucion: int,
    body: LiquidarReembolsoDTO,
    token_data: dict = Depends(require_permission('devoluciones.reembolsar'))
):
    try:
        return devoluciones_services.liquidar_reembolso(
            id_devolucion=id_devolucion,
            datos=body.model_dump(),
            token_data=token_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al liquidar el reembolso: {str(e)}"
        )

