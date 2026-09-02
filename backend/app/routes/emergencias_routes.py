from fastapi import APIRouter, Body, HTTPException, Depends, BackgroundTasks
from app.services import emergencias_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Emergencias"])

ROLES_ADMIN_CLIENTE = ['ADMINISTRADOR', 'CLIENTE']
ROLES_ACTUALIZAR = ROLES_ADMIN_CLIENTE + ['MECANICO']

#NORMALIZAR ROL
def normalizar_rol(rol_usuario: str):
    return rol_usuario.strip().upper() if rol_usuario else ""

#RUTA GET TODAS
@router.get('/')
def get_todas_las_emergencias(token_data: dict = Depends(verificar_token)):
    if normalizar_rol(token_data.get('nombre_rol')) not in ('ADMINISTRADOR','GERENTE TALLER'):
        raise HTTPException(status_code=403, detail="Solo administradores y gerentes.")
    return emergencias_services.listar_todas_las_emergencias()

#RUTA GET MIS EMERGENCIAS
@router.get('/mis-emergencias')
def get_mis_emergencias(token_data: dict = Depends(verificar_token)):
    return emergencias_services.listar_mis_emergencias(token_data.get('nro_usuario'))

#RUTA GET MI TALLER
@router.get('/mi-taller')
def get_emergencias_mi_taller(token_data: dict = Depends(verificar_token)):
    return emergencias_services.listar_emergencias_mi_taller(token_data.get('nro_usuario'))

#RUTA GET EVIDENCIAS DE UNA EMERGENCIA
@router.get('/{nro_emergencia}/evidencias')
def get_evidencias_emergencia(nro_emergencia: int, token_data: dict = Depends(verificar_token)):
    try:
        return emergencias_services.obtener_evidencias_emergencia(nro_emergencia, token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#RUTA POST CREAR
@router.post('/')
def create_emergencia(
    data: dict = Body(...), 
    token_data: dict = Depends(verificar_token),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        return emergencias_services.registrar_emergencia(data, token_data, background_tasks)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#RUTA PUT ACTUALIZAR
@router.put('/{nro_emergencia}')
def update_emergencia(nro_emergencia: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    try:
        return emergencias_services.actualizar_emergencia(nro_emergencia, data, token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#RUTA DELETE BORRAR
@router.delete('/{nro_emergencia}')
def delete_emergencia(nro_emergencia: int, token_data: dict = Depends(verificar_token)):
    try:
        return emergencias_services.borrar_emergencia(nro_emergencia, token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))