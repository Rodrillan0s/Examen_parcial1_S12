from fastapi import APIRouter, Body, HTTPException, Depends
from app.services import tenant_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Empresas (Tenants)"])

@router.get('/')
def get_empresas(token_data: dict = Depends(verificar_token)):
    try:
        return tenant_services.listar_empresas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/')
def create_empresa(data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    
    try:
        return tenant_services.registrar_empresa(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.put('/{id_empresa}')
def update_empresa(id_empresa: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
        
    try:
        return tenant_services.actualizar_empresa(id_empresa, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.delete('/{id_empresa}')
def delete_empresa(id_empresa: int, token_data: dict = Depends(verificar_token)):
    try:
        return tenant_services.borrar_empresa(id_empresa)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")