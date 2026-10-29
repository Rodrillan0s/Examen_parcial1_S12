import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.security import verificar_token, tiene_permiso
from app.modules.pos.repos import pos_repos
from app.modules.pos.repos import caja_repos
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pos", tags=["W24 - Punto de Venta (POS)"])

# --- DTOs ---

class ItemVentaPosDTO(BaseModel):
    id_variante: int = Field(..., gt=0, description="ID de la variante (talla/color)")
    cantidad: int = Field(..., gt=0, description="Cantidad a vender")

class CrearVentaPosDTO(BaseModel):
    id_cliente: Optional[int] = Field(
        None,
        description="Cliente opcional o null para venta sin cliente"
    )
    id_sucursal: Optional[int] = Field(
        None,
        gt=0,
        description="Sucursal de la venta"
    )
    id_empresa: Optional[int] = Field(
        None,
        gt=0,
        description="Empresa de la venta"
    )
    id_reserva: Optional[int] = Field(
        None,
        gt=0,
        description="Reserva asociada a la venta, si corresponde"
    )
    descuento: float = Field(
        0.00,
        ge=0.0,
        description="Descuento en Bs (requiere permiso pos.descuento)"
    )
    observacion: Optional[str] = Field(
        None,
        max_length=300
    )
    observaciones: Optional[str] = Field(
        None,
        max_length=300
    )
    items: List[ItemVentaPosDTO] = Field(
        ...,
        min_items=1,
        description="Prendas seleccionadas"
    )

def _verificar_acceso_pos(token_data: dict) -> None:
    """
    Verifica que el usuario tenga rol de Cajero, Administrador o Encargado de Sucursal,
    o posea el permiso pos.vender.
    """
    if tiene_permiso(token_data, "pos.vender") or tiene_permiso(token_data, "caja.ver"):
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acceso restringido. No tienes permisos para operar el Punto de Venta (POS)."
    )


def _verificar_permiso_descuento(token_data: dict) -> None:
    """
    Verifica que el usuario tenga autorización RBAC para aplicar descuentos en ventas.
    """
    if tiene_permiso(token_data, "pos.descuento"):
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para aplicar descuentos manuales en la venta. Requiere autorización de encargado."
    )


def _obtener_empresa_contexto(token_data: dict, id_empresa_solicitada: Optional[int] = None) -> int:
    from app.core.tenant_guard import resolver_tenant_operacion
    return resolver_tenant_operacion(token_data, id_empresa_solicitada)


def _obtener_sucursal_contexto(token_data: dict, id_sucursal_solicitada: Optional[int] = None, id_empresa: Optional[int] = None) -> int:
    from app.core.tenant_guard import obtener_sucursales_autorizadas
    from app.modules.inventario.repos.sucursales_repos import obtener_sucursal_por_id, obtener_sucursales_por_empresa
    permitidas = obtener_sucursales_autorizadas(token_data)
    if id_sucursal_solicitada:
        suc = obtener_sucursal_por_id(id_sucursal_solicitada)
        if not suc or suc['id_empresa'] != id_empresa or not suc['activo']:
            raise HTTPException(403, detail='Sucursal ajena o inactiva.')
        if permitidas is not None and id_sucursal_solicitada not in permitidas:
            raise HTTPException(403, detail='Sucursal fuera de su alcance.')
        return id_sucursal_solicitada
    candidatas = obtener_sucursales_por_empresa(id_empresa)
    candidatas = [s for s in candidatas if s['activo'] and (permitidas is None or s['id_sucursal'] in permitidas)]
    if not candidatas:
        raise HTTPException(403, detail='No tiene sucursales activas autorizadas.')
    return candidatas[0]['id_sucursal']


# --- ENDPOINTS ---

@router.get('/productos', summary="W24: Catálogo de productos optimizado para POS")
def catalogo_pos(
    q: Optional[str] = Query(None, description="Buscador por nombre, código, SKU o código de barras"),
    id_categoria: Optional[int] = Query(None, description="Filtro por categoría"),
    solo_con_stock: bool = Query(False, description="Mostrar solo productos con stock disponible"),
    id_sucursal: Optional[int] = Query(None, description="Sucursal de consulta"),
    id_empresa: Optional[int] = Query(None, description="Empresa de consulta (Multi-Tenant)"),
    token_data: dict = Depends(verificar_token)
):
    _verificar_acceso_pos(token_data)
    try:
        id_emp = _obtener_empresa_contexto(token_data, id_empresa)
        id_suc = _obtener_sucursal_contexto(token_data, id_sucursal, id_emp)

        productos = pos_repos.buscar_productos_pos(
            id_sucursal=id_suc,
            id_empresa=id_emp,
            q=q,
            id_categoria=id_categoria,
            solo_con_stock=solo_con_stock
        )
        return {
            "success": True,
            "productos": productos,
            "data": productos,
            "id_sucursal": id_suc,
            "id_empresa": id_emp
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CATALOGO POS ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/productos/{id_producto}/variantes', summary="W24: Obtener variantes y stock en sucursal")
def variantes_producto_pos(
    id_producto: int,
    id_sucursal: Optional[int] = Query(None, description="Sucursal activa"),
    id_empresa: Optional[int] = Query(None, description="Empresa activa"),
    token_data: dict = Depends(verificar_token)
):
    _verificar_acceso_pos(token_data)
    try:
        id_emp = _obtener_empresa_contexto(token_data, id_empresa)
        id_suc = _obtener_sucursal_contexto(token_data, id_sucursal, id_emp)
        variantes = pos_repos.obtener_variantes_producto_pos(id_producto, id_suc)
        return {
            "success": True,
            "variantes": variantes,
            "data": variantes
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VARIANTES POS ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/clientes/buscar', summary="W24: Búsqueda rápida de clientes para venta presencial")
def buscar_clientes(
    q: str = Query(..., min_length=2, description="Término de búsqueda: CI, nombre, apellido o correo"),
    id_empresa: Optional[int] = Query(None, description="Empresa a consultar"),
    token_data: dict = Depends(verificar_token)
):
    _verificar_acceso_pos(token_data)
    try:
        id_emp = _obtener_empresa_contexto(token_data, id_empresa)
        clientes = pos_repos.buscar_clientes_pos(id_emp, q)
        return {
            "success": True,
            "clientes": clientes,
            "data": clientes
        }
    except Exception as e:
        logger.error(f"[BUSCAR CLIENTES ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/ventas', summary="W24: Registrar venta presencial en estado PENDIENTE_PAGO")
def registrar_venta_presencial(
    body: CrearVentaPosDTO,
    token_data: dict = Depends(verificar_token)
):
    _verificar_acceso_pos(token_data)
    try:
        id_usuario = token_data.get("nro_usuario") or token_data.get("id_usuario")
        id_emp = _obtener_empresa_contexto(token_data, body.id_empresa)
        id_suc = _obtener_sucursal_contexto(token_data, body.id_sucursal, id_emp)
        from app.modules.saas.services.saas_services import exigir_vigencia
        exigir_vigencia(id_emp)

        # 1. Validar que el cajero tenga una caja ABIERTA en esta sucursal (Regla RB03 y RB12)
        sesion_activa = caja_repos.obtener_sesion_activa_usuario(id_usuario, id_suc)
        if not sesion_activa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para realizar ventas primero debe abrir la caja."
            )

        id_sesion_caja = sesion_activa["id_sesion_caja"]

        # 2. Validar descuento con RBAC si se especificó monto > 0 (Regla RB08 y Sección 13)
        if body.descuento and body.descuento > 0:
            _verificar_permiso_descuento(token_data)

        # 3. Registrar venta de forma atómica en PostgreSQL con bloqueo FOR UPDATE en inventario
        items_dict = [it.dict() for it in body.items]
        obs = body.observacion or body.observaciones
        resultado = pos_repos.ejecutar_registro_venta_pos(
    id_sesion_caja=id_sesion_caja,
    id_usuario=id_usuario,
    id_sucursal=id_suc,
    id_empresa=id_emp,
    id_cliente=body.id_cliente,
    items=items_dict,
    descuento=body.descuento,
    observacion=obs,
    id_reserva=body.id_reserva
)

        return {
            "success": True,
            "message": "Venta registrada exitosamente. Pendiente de pago (W28).",
            "venta": resultado,
            "data": resultado
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[REGISTRAR VENTA POS ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/ventas', summary="W24: Historial de ventas del turno actual de la caja")
def historial_ventas_pos(
    id_sesion_caja: Optional[int] = Query(None, description="ID de sesión de caja"),
    token_data: dict = Depends(verificar_token)
):
    _verificar_acceso_pos(token_data)
    try:
        id_usuario = token_data.get("nro_usuario") or token_data.get("id_usuario")
        if not id_sesion_caja:
            sesion = caja_repos.obtener_sesion_activa_usuario(id_usuario)
            if not sesion:
                return {"success": True, "ventas": [], "data": []}
            id_sesion_caja = sesion["id_sesion_caja"]

        ventas = pos_repos.obtener_historial_ventas_sesion(id_sesion_caja)
        return {
            "success": True,
            "ventas": ventas,
            "data": ventas
        }
    except Exception as e:
        logger.error(f"[HISTORIAL VENTAS ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/ventas/{id_venta}', summary="W24: Consultar detalle de venta presencial")
def detalle_venta_pos(
    id_venta: int,
    token_data: dict = Depends(verificar_token)
):
    _verificar_acceso_pos(token_data)
    try:
        detalle = pos_repos.obtener_detalle_venta_pos(id_venta)
        if not detalle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada.")
        return {
            "success": True,
            "data": detalle
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DETALLE VENTA ERROR] {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
