from fastapi import APIRouter, Body, Depends, HTTPException
from app.services import escrow_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Dinero Retenido Simulado"])


@router.post('/retener')
def retener_dinero(
    data: dict = Body(...),
    token_data: dict = Depends(verificar_token)
):
    try:
        return escrow_services.retener_pago_simulado(data, token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/mis-fondos')
def mis_fondos(token_data: dict = Depends(verificar_token)):
    try:
        return escrow_services.obtener_mis_fondos(token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/resumen-usuarios')
def resumen_usuarios(token_data: dict = Depends(verificar_token)):
    try:
        return escrow_services.obtener_resumen_usuarios(token_data)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))