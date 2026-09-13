from fastapi import APIRouter, Body, HTTPException, Depends, Request
from app.services import tenant_services
from app.utils.security import require_permission, verificar_token

router = APIRouter(tags=["Empresas (Tenants)"])

# Dependencia de seguridad estricta para SuperAdministrador de la plataforma
def require_superadmin(payload: dict = Depends(verificar_token)):
    id_rol = payload.get('id_rol')
    roles = [str(r).upper() for r in payload.get('roles', [])]
    nombre_rol = str(payload.get('nombre_rol', '')).upper()
    
    if id_rol == 1 or 'ADMINISTRADOR' in roles or nombre_rol == 'ADMINISTRADOR':
        return payload
        
    raise HTTPException(
        status_code=403,
        detail="Acceso denegado: El único autorizado para registrar o gestionar Tiendas/Empresas (Tenants) es el SuperAdministrador."
    )

@router.get('/')
def get_empresas(payload: dict = Depends(require_permission('sucursales.ver'))):
    try:
        return tenant_services.listar_empresas(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al listar empresas: {str(e)}")

@router.get('/{id_empresa}')
def get_empresa(id_empresa: int, payload: dict = Depends(require_permission('sucursales.ver'))):
    try:
        return tenant_services.obtener_empresa(id_empresa, payload)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al obtener empresa: {str(e)}")

@router.post('/', status_code=201)
def create_empresa(request: Request, data: dict = Body(...), payload: dict = Depends(require_superadmin)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    
    try:
        return tenant_services.registrar_empresa(data, payload, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al registrar Tenant: {str(e)}")

@router.put('/{id_empresa}')
def update_empresa(id_empresa: int, request: Request, data: dict = Body(...), payload: dict = Depends(require_superadmin)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
        
    try:
        return tenant_services.actualizar_empresa(id_empresa, data, payload, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al actualizar Tenant: {str(e)}")

@router.delete('/{id_empresa}')
def delete_empresa(id_empresa: int, request: Request, payload: dict = Depends(require_superadmin)):
    try:
        return tenant_services.borrar_empresa(id_empresa, payload, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al eliminar Tenant: {str(e)}")