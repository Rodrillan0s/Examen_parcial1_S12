from fastapi import APIRouter, Depends, HTTPException, Body
from app.services import cobros_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Cobros y Pagos"])

@router.get('/emergencia/{nro_emergencia}')
def get_resumen_cobro(nro_emergencia: int, token_data: dict = Depends(verificar_token)):
    """
    Obtiene la cotización y los detalles de cobro para mostrar en la pantalla de "Pagar".
    """
    try:
        nro_usuario = token_data.get('nro_usuario')
        return cobros_services.obtener_detalles_para_pago(nro_emergencia, nro_usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/pagar')
def realizar_pago_mock(data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    """
    Simulador de pasarela de pago. Confirma el pago de una orden.
    """
    # Solo el cliente debería poder pagar
    if token_data.get('nombre_rol') != 'CLIENTE':
        raise HTTPException(status_code=403, detail="Solo los clientes pueden realizar pagos.")

    try:
        nro_usuario = token_data.get('nro_usuario')
        return cobros_services.procesar_pago_simulado(data, nro_usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))