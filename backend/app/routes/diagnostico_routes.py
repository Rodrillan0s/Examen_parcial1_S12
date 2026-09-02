from fastapi import APIRouter, Depends, HTTPException
from app.services import diagnostico_services
from app.utils.security import verificar_token

router = APIRouter(prefix="/api/diagnostico", tags=["IA y Pre-Diagnósticos"])

@router.get('/{nro_emergencia}')
def predecir_diagnostico_evidencia(nro_emergencia: int, token_data: dict = Depends(verificar_token)):
    """
    Analiza la evidencia de una emergencia con Inteligencia Artificial
    para devolver un posible diagnóstico mecánico.
    """
    try:
        return diagnostico_services.generar_diagnostico_ia(nro_emergencia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del Servidor: {str(e)}")