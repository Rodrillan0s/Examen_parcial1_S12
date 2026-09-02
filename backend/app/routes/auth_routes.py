from fastapi import APIRouter, Body, HTTPException
from app.services import auth_services

router = APIRouter(tags=["Autenticacion"])

@router.post('/login')
def login(data: dict = Body(...)):
    
    if not data:
        raise HTTPException(
            status_code=400, 
            detail='El cuerpo de la petición está vacío o no es un JSON válido.'
        )
    
    try:
        result = auth_services.loguear_usuario(data)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
@router.post('/register')
def register(data:dict=Body(...)):
    if not data:
        raise HTTPException(
            status_code=400,
            detail='El cuerpo de la peticion esta vacio o no es un JSON valido.'
        )
    
    try:
        result=auth_services.registrar_nuevo_usuario(data)

        return result
    
    except ValueError as e:
        raise HTTPException(status_code=401,detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')