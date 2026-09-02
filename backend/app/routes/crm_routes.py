from fastapi import APIRouter, Body, Depends, HTTPException
from app.services import crm_services
from app.utils.security import verificar_token


router = APIRouter(tags=["CRM Clientes"])


@router.post('/mantenimiento')
def create_plan_mantenimiento(
    data: dict = Body(...),
    token_data: dict = Depends(verificar_token)
):
    try:
        return crm_services.registrar_nuevo_plan(data, token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/mantenimiento/ejecutar-recordatorios')
async def trigger_recordatorios(token_data: dict = Depends(verificar_token)):
    if token_data.get('nombre_rol') != 'ADMINISTRADOR':
        raise HTTPException(status_code=403, detail="Acceso denegado.")

    try:
        return await crm_services.procesar_recordatorios_automaticos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/clientes')
def obtener_clientes_crm(token_data: dict = Depends(verificar_token)):
    try:
        return crm_services.listar_clientes_crm(token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/notificaciones/enviar')
async def enviar_notificacion_crm(
    data: dict = Body(...),
    token_data: dict = Depends(verificar_token)
):
    try:
        return await crm_services.enviar_notificacion_crm(data, token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))