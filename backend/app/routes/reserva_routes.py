from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from app.utils.security import verificar_token
from app.repos import reserva_repos, catalogo_repos
from app.classes.postgres import PostgreSQL
from app.config import Config

router = APIRouter(prefix="/api/reservas", tags=["Reservas y Citas en Sucursal"])

class ItemReservaDTO(BaseModel):
    id_variante: int = Field(..., gt=0, description="ID de la variante (talla + color)")
    cantidad: int = Field(1, gt=0, description="Cantidad de prendas a apartar")

class CrearReservaDTO(BaseModel):
    id_sucursal: int = Field(..., gt=0, description="ID de la sucursal física seleccionada")
    fecha_hora_visita: str = Field(..., min_length=10, description="Fecha y hora de visita programada (YYYY-MM-DD HH:MM)")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones o notas para el asesor de tienda")
    items: List[ItemReservaDTO] = Field(..., min_length=1, description="Listado de prendas y variantes a reservar")
    id_empresa: Optional[int] = Field(None, description="Parámetro opcional; el backend valida y resuelve el Tenant real")

class CancelarReservaDTO(BaseModel):
    motivo: Optional[str] = Field("Cancelación solicitada por el cliente.", max_length=300, description="Motivo de la cancelación")

def _resolver_empresa_de_sucursal(id_sucursal: int) -> Optional[int]:
    """Obtiene el ID de la empresa dueña de la sucursal física."""
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        cur = db.conn.cursor()
        cur.execute(f"SELECT id_empresa FROM {schema}.t_sucursal WHERE id_sucursal = %s;", (id_sucursal,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        db.close_connection()

def _resolver_id_empresa_segura(token_data: dict, id_empresa_param: Optional[int] = None, id_sucursal: Optional[int] = None) -> int:
    """
    Resuelve y valida el Tenant sin confiar ciegamente en id_empresa enviado por el frontend.
    1. Si se proporciona id_sucursal, la empresa se determina directamente de la sucursal en BD.
    2. Si no hay sucursal, se valida id_empresa_param o el token claim.
    3. Fallback para clientes globales al tenant público activo.
    """
    sucursal_empresa = _resolver_empresa_de_sucursal(id_sucursal) if id_sucursal else None
    if sucursal_empresa:
        return sucursal_empresa

    token_empresa = token_data.get('id_empresa')
    if token_empresa is not None:
        try:
            token_empresa = int(token_empresa)
        except (ValueError, TypeError):
            token_empresa = None

    if id_empresa_param:
        try:
            return int(id_empresa_param)
        except (ValueError, TypeError):
            pass

    if token_empresa:
        return token_empresa

    tenants = catalogo_repos.obtener_tenants_publicos()
    if tenants:
        return tenants[0]["id_empresa"]

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No se pudo determinar la tienda (Tenant) para esta operación."
    )

@router.post('', status_code=status.HTTP_201_CREATED, summary="Crear una reserva de prendas para visita en sucursal")
@router.post('/', status_code=status.HTTP_201_CREATED, summary="Crear una reserva de prendas para visita en sucursal")
def crear_reserva(
    body: CrearReservaDTO,
    token_data: dict = Depends(verificar_token)
):
    try:
        id_usuario = token_data.get('nro_usuario') or token_data.get('id_usuario')
        if not id_usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión no válida o usuario no identificado.")

        empresa_id = _resolver_id_empresa_segura(token_data, body.id_empresa, body.id_sucursal)

        datos = body.model_dump()
        reserva = reserva_repos.crear_reserva(
            id_usuario=id_usuario,
            id_empresa=empresa_id,
            datos=datos
        )

        return {
            "success": True,
            "message": f"Reserva {reserva['codigo_reserva']} generada exitosamente. Tu prenda ha sido apartada.",
            "data": reserva
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al generar la reserva: {str(e)}"
        )

@router.get('/mis-reservas', summary="Listar las reservas del cliente autenticado")
def obtener_mis_reservas(
    id_empresa: Optional[int] = Query(None, description="Opcional: ID de la empresa"),
    token_data: dict = Depends(verificar_token)
):
    try:
        id_usuario = token_data.get('nro_usuario') or token_data.get('id_usuario')
        if not id_usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado.")

        reservas = reserva_repos.obtener_mis_reservas(id_usuario, id_empresa)

        return {
            "success": True,
            "data": reservas
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tus reservas: {str(e)}"
        )

@router.get('/{id_reserva}', summary="Consultar detalle de una reserva específica")
def consultar_detalle_reserva(
    id_reserva: int,
    id_empresa: Optional[int] = Query(None, description="Opcional: ID de la empresa"),
    token_data: dict = Depends(verificar_token)
):
    try:
        id_usuario = token_data.get('nro_usuario') or token_data.get('id_usuario')
        rol = (token_data.get('nombre_rol') or '').upper()
        es_admin = rol in ('ADMINISTRADOR', 'ADMINISTRADOR_TIENDA', 'ENCARGADO_SUCURSAL')

        empresa_id = _resolver_id_empresa_segura(token_data, id_empresa)
        reserva = reserva_repos.obtener_detalle_reserva(id_reserva, id_usuario, empresa_id, es_admin)

        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La reserva solicitada no existe, no pertenece a tu cuenta o corresponde a otra tienda."
            )

        return {
            "success": True,
            "data": reserva
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar el detalle de la reserva: {str(e)}"
        )

@router.post('/{id_reserva}/cancelar', summary="Cancelar una reserva activa y liberar su inventario")
def cancelar_reserva(
    id_reserva: int,
    body: Optional[CancelarReservaDTO] = None,
    id_empresa: Optional[int] = Query(None, description="Opcional: ID de la empresa"),
    token_data: dict = Depends(verificar_token)
):
    try:
        id_usuario = token_data.get('nro_usuario') or token_data.get('id_usuario')
        rol = (token_data.get('nombre_rol') or '').upper()
        es_admin = rol in ('ADMINISTRADOR', 'ADMINISTRADOR_TIENDA', 'ENCARGADO_SUCURSAL')

        empresa_id = _resolver_id_empresa_segura(token_data, id_empresa)
        motivo = body.motivo if body and body.motivo else "Cancelación solicitada por el cliente."

        resultado = reserva_repos.cancelar_reserva(
            id_reserva=id_reserva,
            id_usuario=id_usuario,
            id_empresa=empresa_id,
            motivo=motivo,
            es_admin=es_admin
        )

        return {
            "success": True,
            "data": resultado
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar la reserva: {str(e)}"
        )
