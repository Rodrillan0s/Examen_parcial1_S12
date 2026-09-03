from fastapi import APIRouter, Body, HTTPException, Depends, Request
from app.services import tenant_services
from app.utils.security import require_permission

router = APIRouter(tags=["Empresas (Tenants)"])

@router.get('/', dependencies=[Depends(require_permission('sucursales.ver'))])
def get_empresas():
    try:
        return tenant_services.listar_empresas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/')
def create_empresa(request: Request, data: dict = Body(...), payload: dict = Depends(require_permission('sucursales.asignar'))):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    
    try:
        return tenant_services.registrar_empresa(data, payload, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.put('/{id_empresa}')
def update_empresa(id_empresa: int, request: Request, data: dict = Body(...), payload: dict = Depends(require_permission('sucursales.asignar'))):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
        
    try:
        return tenant_services.actualizar_empresa(id_empresa, data, payload, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.delete('/{id_empresa}')
def delete_empresa(id_empresa: int, request: Request, payload: dict = Depends(require_permission('sucursales.asignar'))):
    try:
        return tenant_services.borrar_empresa(id_empresa, payload, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")