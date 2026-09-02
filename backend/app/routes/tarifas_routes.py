from fastapi import APIRouter, Body, HTTPException, Depends
from app.services import tarifas_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Conceptos de Tarifas"])

def normalizar_rol(rol_usuario: str):
    return rol_usuario.strip().upper() if rol_usuario else ""

def validar_permiso_admin(token_data: dict):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    if rol != 'ADMINISTRADOR':
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Solo los administradores globales del sistema pueden gestionar las tarifas."
        )

@router.get('/')
def get_tarifas(token_data: dict = Depends(verificar_token)):
    validar_permiso_admin(token_data)
    try:
        return tarifas_services.listar_tarifas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/')
def create_tarifa(data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_permiso_admin(token_data)
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    try:
        return tarifas_services.registrar_tarifa(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.put('/{id_concepto}')
def update_tarifa(id_concepto: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_permiso_admin(token_data)
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    try:
        return tarifas_services.modificar_tarifa(id_concepto, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.delete('/{id_concepto}')
def delete_tarifa(id_concepto: int, token_data: dict = Depends(verificar_token)):
    validar_permiso_admin(token_data)
    try:
        return tarifas_services.borrar_tarifa(id_concepto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")