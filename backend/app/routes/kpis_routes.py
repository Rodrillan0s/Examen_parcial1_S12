from fastapi import APIRouter, Depends, HTTPException, status
from app.services import kpis_services
from app.utils.security import verificar_token

router = APIRouter(prefix='/api/dashboard',tags=["Analítica y KPIs"])

@router.post('/etl/ejecutar')
def trigger_etl_process(token_data: dict = Depends(verificar_token)):
    """
    Puebla el Data Warehouse con los datos del día anterior.
    """
    try:
        return kpis_services.procesar_etl_diario(token_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get('/metricas')
def get_kpis_operacionales(token_data: dict = Depends(verificar_token)):
    """
    Retorna la analítica general o por sucursal dependiendo del rol del JWT.
    """
    try:
        return kpis_services.generar_dashboard(token_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al calcular métricas: {str(e)}")