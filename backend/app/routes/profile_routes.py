from fastapi import APIRouter,Body,HTTPException,Depends
from app.services import profile_services
from app.utils.security import verificar_token

router=APIRouter(tags=['Perfil'])

@router.get('/')
def get_profile(token_data:dict = Depends(verificar_token)):
    try:
        nro_usuario=token_data.get('nro_usuario')
        return profile_services.obtener_perfil_usuario(nro_usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error interno en : {err}")
    

@router.put('/')
def update_profile(token_data:dict=Depends(verificar_token),data:dict=Body(...)):
    try:
        nro_usuario=token_data.get('nro_usuario')

        return profile_services.actualizar_perfil_usuario(nro_usuario,data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error interno en : {err}")