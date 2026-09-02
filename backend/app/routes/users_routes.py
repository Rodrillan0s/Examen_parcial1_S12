from fastapi import APIRouter, Body, HTTPException, Depends
from app.services import users_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Usuarios"])

@router.get('/')
def get_users(token_data: dict = Depends(verificar_token)):
    try:
        return users_services.listar_usuarios()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/')
def create_user(data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    
    try:
        return users_services.registrar_usuario(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        if "uk_nombre_usuario" in error_msg:
            raise HTTPException(status_code=400, detail="El nombre de usuario elegido ya está en uso. Por favor, elija otro.")
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {error_msg}")

@router.put('/{nro_usuario}')
def update_user(nro_usuario: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
        
    try:
        return users_services.actualizar_usuario(nro_usuario, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        if "uk_nombre_usuario" in error_msg:
            raise HTTPException(status_code=400, detail="El nombre de usuario elegido ya está en uso por otra persona.")
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {error_msg}")

@router.delete('/{nro_usuario}')
def delete_user(nro_usuario: int, token_data: dict = Depends(verificar_token)):
    try:
        return users_services.borrar_usuario(nro_usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")