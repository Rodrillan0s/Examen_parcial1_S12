from fastapi import APIRouter, Body, HTTPException, Depends
from app.services import talleres_services
from app.repos import talleres_repos
from app.utils.security import verificar_token

router = APIRouter(tags=["Talleres"])

#LISTA DE ROLES AUTORIZADOS A ESTE MODULO
ROLES_PERMITIDOS = ['ADMINISTRADOR', 'GERENTE TALLER','CLIENTE']

def validar_rol_taller(rol_usuario: str):
    if rol_usuario not in ROLES_PERMITIDOS:
        raise HTTPException(status_code=403, detail="No tienes permisos para gestionar talleres.")

def validar_pertenencia_taller(nro_taller: int, token_data: dict):
    """
    Bloquea la petición si el gerente intenta tocar un taller de OTRA empresa.
    """
    rol = token_data.get('nombre_rol')
    
    if rol == 'ADMINISTRADOR':
        return True

    if rol == 'GERENTE TALLER':
        id_empresa_taller = talleres_repos.obtener_id_empresa_de_taller(nro_taller)
        
        if id_empresa_taller is None:
            raise HTTPException(status_code=404, detail="El taller no existe.")
            
        if id_empresa_taller != token_data.get('id_empresa'):
            raise HTTPException(
                status_code=403, 
                detail="Acceso denegado. Este taller pertenece a otra empresa."
            )
        return True

    raise HTTPException(status_code=403, detail="Rol no autorizado.")


#ENDPOINTS DE TALLER
@router.get('/')
def get_talleres(token_data: dict = Depends(verificar_token)):
    validar_rol_taller(token_data.get('nombre_rol'))
    try:
        # Si es gerente, pasamos su id_empresa como filtro al servicio
        filtro_empresa = token_data.get('id_empresa') if token_data.get('nombre_rol') == 'GERENTE TALLER' else None
        return talleres_services.listar_talleres(filtro_empresa)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/')
def create_taller(data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_rol_taller(token_data.get('nombre_rol'))
    
    if token_data.get('nombre_rol') == 'GERENTE TALLER':
        data['id_empresa'] = token_data.get('id_empresa')

    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    
    try:
        return talleres_services.registrar_taller(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/{nro_taller}')
def update_taller(nro_taller: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_pertenencia_taller(nro_taller, token_data)
    
    if token_data.get('nombre_rol') == 'GERENTE TALLER':
        data['id_empresa'] = token_data.get('id_empresa')

    try:
        return talleres_services.actualizar_taller(nro_taller, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete('/{nro_taller}')
def delete_taller(nro_taller: int, token_data: dict = Depends(verificar_token)):
    validar_pertenencia_taller(nro_taller, token_data) # <-- CANDADO AQUÍ
    try:
        return talleres_services.borrar_taller(nro_taller)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


#ENDPOINTS SERVICIOS DEL TRALLER

@router.get('/{nro_taller}/servicios')
def get_servicios_taller(nro_taller: int, token_data: dict = Depends(verificar_token)):
    validar_pertenencia_taller(nro_taller, token_data)
    try:
        return talleres_services.listar_servicios_taller(nro_taller)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/{nro_taller}/servicios')
def create_servicio_taller(nro_taller: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_pertenencia_taller(nro_taller, token_data)
    try:
        return talleres_services.registrar_servicio_taller(nro_taller, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/{nro_taller}/servicios/{nro_servicio}')
def update_servicio_taller(nro_taller: int, nro_servicio: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_pertenencia_taller(nro_taller, token_data) 
    try:
        return talleres_services.actualizar_servicio_taller(nro_servicio, nro_taller, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete('/{nro_taller}/servicios/{nro_servicio}')
def delete_servicio_taller(nro_taller: int, nro_servicio: int, token_data: dict = Depends(verificar_token)):
    validar_pertenencia_taller(nro_taller, token_data) 
    try:
        return talleres_services.borrar_servicio_taller(nro_servicio, nro_taller)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))