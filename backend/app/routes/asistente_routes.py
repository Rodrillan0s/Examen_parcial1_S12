from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.utils.security import verificar_token_opcional
from app.services import asistente_services

router = APIRouter(prefix="/api/asistente", tags=["Asistente Inteligente Aurora (W13)"])

class ChatMessage(BaseModel):
    role: str = Field(..., description="Rol del emisor: 'user' o 'assistant'")
    content: str = Field(..., description="Texto del mensaje")

class ChatRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=2000, description="Mensaje o comando del usuario")
    historial: Optional[List[ChatMessage]] = Field(default=[], description="Historial reciente de la sesión")

@router.post("/chat", summary="Conversar con el Asistente Inteligente Aurora (DeepSeek + RBAC Tools)")
def chat_asistente(
    request: ChatRequest,
    token_data: Optional[dict] = Depends(verificar_token_opcional)
):
    """
    Recibe la solicitud conversacional o comando por voz del usuario.
    DeepSeek interpreta la intención, ejecuta herramientas parametrizadas en la BD
    según el rol y permisos de JWT (o visitante anónimo), y devuelve una respuesta enriquecida.
    """
    try:
        historial_dicts = [h.model_dump() for h in (request.historial or [])]
        resultado = asistente_services.procesar_mensaje_chat(
            mensaje=request.mensaje,
            historial=historial_dicts,
            token_data=token_data
        )

        return {
            "success": True,
            "respuesta": resultado.get("respuesta", ""),
            "tipo": resultado.get("tipo", "texto"),
            "datos": resultado.get("datos")
        }
    except Exception as e:
        return {
            "success": False,
            "respuesta": "El asistente no está disponible temporalmente. Las demás funciones de Aurora Store continúan funcionando normalmente.",
            "tipo": "texto",
            "datos": None,
            "error": str(e)
        }
