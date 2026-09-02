from fastapi import APIRouter, Body, HTTPException, Depends
from app.services import roles_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Roles"])

@router.get('/')
def get_roles(token_data: dict = Depends(verificar_token)):
    try:
        return roles_services.listar_roles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/')
def create_rol(data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    
    try:
        return roles_services.registrar_rol(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.put('/{nro_rol}')
def update_rol(nro_rol: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
        
    try:
        return roles_services.actualizar_rol(nro_rol, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.delete('/{nro_rol}')
def delete_rol(nro_rol: int, token_data: dict = Depends(verificar_token)):
    try:
        return roles_services.borrar_rol(nro_rol)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        if "fk_usuario_rol" in error_msg:
            raise HTTPException(status_code=400, detail="No se puede eliminar este rol porque hay usuarios asignados a él.")
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {error_msg}")