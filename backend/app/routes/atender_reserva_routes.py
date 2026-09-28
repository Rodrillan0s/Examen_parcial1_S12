from fastapi import APIRouter, Depends, Query
from app.utils.security import verificar_token

from app.services.atender_reserva_services import (
    listar_reservas_atender,
    obtener_reserva_atender,
    ejecutar_atencion_reserva
)


router = APIRouter(
    prefix="/api/atender-reserva",
    tags=["Atender Reserva"]
)


@router.get("")
def listar_reservas_para_atencion(
    id_sucursal: int = Query(...),
    payload: dict = Depends(verificar_token)
):
    id_empresa = payload.get("id_empresa")

    if not id_empresa:
        return {
            "success": False,
            "message": "No se encontró la empresa del usuario."
        }

    return listar_reservas_atender(
        id_empresa=id_empresa,
        id_sucursal=id_sucursal
    )


@router.get("/{id_reserva}")
def obtener_reserva_para_atencion(
    id_reserva: int,
    id_sucursal: int = Query(...),
    payload: dict = Depends(verificar_token)
):
    id_empresa = payload.get("id_empresa")

    if not id_empresa:
        return {
            "success": False,
            "message": "No se encontró la empresa del usuario."
        }

    return obtener_reserva_atender(
        id_reserva=id_reserva,
        id_empresa=id_empresa,
        id_sucursal=id_sucursal
    )


@router.post("/{id_reserva}")
def atender_reserva_endpoint(
    id_reserva: int,
    id_sucursal: int = Query(...),
    payload: dict = Depends(verificar_token)
):
    id_empresa = payload.get("id_empresa")

    if not id_empresa:
        return {
            "success": False,
            "message": "No se encontró la empresa del usuario."
        }

    return ejecutar_atencion_reserva(
        id_reserva=id_reserva,
        id_empresa=id_empresa,
        id_sucursal=id_sucursal
    )