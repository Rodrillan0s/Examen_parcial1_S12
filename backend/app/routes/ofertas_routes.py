from fastapi import APIRouter, Body, HTTPException, Depends,BackgroundTasks
from app.services import ofertas_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Ofertas Comerciales"])

#RUTA GET OFERTAS POR EMERGENCIA (PARA EL CLIENTE O ADMIN)
@router.get('/emergencia/{nro_emergencia}')
def get_ofertas_por_emergencia(nro_emergencia: int, token_data: dict = Depends(verificar_token)):
    try:
        return ofertas_services.listar_ofertas_por_emergencia(nro_emergencia, token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#RUTA GET MIS OFERTAS (PARA EL TALLER/MECANICO)
@router.get('/mi-taller')
def get_mis_ofertas(token_data: dict = Depends(verificar_token)):
    try:
        return ofertas_services.listar_mis_ofertas_taller(token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#RUTA POST CREAR OFERTA
@router.post('/')
def create_oferta(
    data: dict = Body(...), 
    token_data: dict = Depends(verificar_token),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        return ofertas_services.emitir_oferta(data, token_data, background_tasks)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#RUTA PUT RESPONDER OFERTA
@router.put('/{id_oferta}/responder')
def update_respuesta_oferta(
    id_oferta: int, 
    data: dict = Body(...), 
    token_data: dict = Depends(verificar_token),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        return ofertas_services.responder_oferta(id_oferta, data, token_data, background_tasks)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))