from fastapi import APIRouter, Body, Depends, HTTPException
from app.services import triaje_services
from app.utils.security import verificar_token

router = APIRouter(tags=["IA Chatbot"])

@router.post('/iniciar')
def start_chat(token_data: dict = Depends(verificar_token)):
    return triaje_services.iniciar_chat_triaje(token_data)

@router.post('/{id_conversacion}/mensaje')
def send_message(id_conversacion: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    mensaje = data.get('mensaje')
    if not mensaje:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")
    
    try:
        respuesta = triaje_services.interactuar_con_chatbot(id_conversacion, mensaje)
        return {"success": True, "data": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))