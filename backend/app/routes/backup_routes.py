import io
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.services import backup_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Backups"])

@router.get('/manual')
def manual_backup(token_data: dict = Depends(verificar_token)):

    #VALIDACION DE ROL, SOLO EL ADMIN PUEDE SACAR BACKUP DE LA DB
    rol_usuario = token_data.get('nombre_rol')
    if rol_usuario != 'ADMINISTRADOR':
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado. Solo los administradores pueden generar backups."
        )

    try:
        #EJECUTAR EL SERVICIO
        res = backup_services.generar_backup_bd_memoria()
        
        
        buffer_memoria = io.BytesIO(res['file_bytes'])
        
        #RETORNAR ARCHIVO .SQL
        return StreamingResponse(
            buffer_memoria, 
            media_type="application/sql",
            headers={"Content-Disposition": f"attachment; filename={res['file_name']}"}
        )
        
    except RuntimeError as e:
        print(f"ERROR REAL DEL SERVICIO DE BACKUP: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f'ERROR INESPERADO: {e}')
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")