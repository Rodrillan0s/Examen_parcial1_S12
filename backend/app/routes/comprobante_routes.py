import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel

from app.utils.security import verificar_token
from app.services import comprobante_service
from app.repos import pago_repos
from app.utils.email_service import enviar_correo_comprobante

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/comprobantes", tags=["W29 - Emisión de Comprobantes"])

class ReenviarCorreoDTO(BaseModel):
    correo_destino: Optional[str] = None

@router.get('/venta/{id_venta}/pdf', summary="W29: Descargar comprobante de venta o factura en PDF")
def descargar_pdf_venta(
    id_venta: int,
    token_data: dict = Depends(verificar_token)
):
    try:
        datos = comprobante_service.obtener_datos_venta_comprobante(id_venta)
        if not datos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comprobante no encontrado.")

        pdf_bytes = comprobante_service.generar_pdf_venta(id_venta)
        filename = f"{datos['tipo_documento']}_{datos['numero_venta']}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{filename}"',
                "X-Document-Type": datos["tipo_documento"],
                "X-Document-Number": datos["numero_venta"]
            }
        )
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al generar PDF: {str(e)}")

@router.get('/pedido/{id_pedido}/pdf', summary="W29: Descargar comprobante por ID de pedido")
def descargar_pdf_por_pedido(
    id_pedido: int,
    token_data: dict = Depends(verificar_token)
):
    try:
        id_usuario = token_data.get('nro_usuario') or token_data.get('id_usuario')
        venta_info = pago_repos.obtener_venta_por_pedido(id_pedido)
        if not venta_info or not venta_info.get("id_venta"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El pedido aún no cuenta con una venta confirmada ni comprobante emitido."
            )

        id_venta = venta_info["id_venta"]
        return descargar_pdf_venta(id_venta, token_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get('/reserva/{id_reserva}/pdf', summary="W29: Descargar comprobante de reserva en PDF")
def descargar_pdf_reserva(
    id_reserva: int,
    token_data: dict = Depends(verificar_token)
):
    try:
        pdf_bytes = comprobante_service.generar_pdf_reserva(id_reserva)
        filename = f"Comprobante_Reserva_{id_reserva}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{filename}"'
            }
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post('/venta/{id_venta}/reenviar-correo', summary="W29: Reintentar envío de comprobante al correo del cliente")
def reenviar_correo_venta(
    id_venta: int,
    body: Optional[ReenviarCorreoDTO] = None,
    token_data: dict = Depends(verificar_token)
):
    try:
        datos = comprobante_service.obtener_datos_venta_comprobante(id_venta)
        if not datos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada.")

        correo_dest = (body.correo_destino if body and body.correo_destino else None) or datos["cliente_correo"]
        if not correo_dest or '@' not in correo_dest:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El cliente no tiene un correo válido registrado.")

        pdf_bytes = comprobante_service.generar_pdf_venta(id_venta)
        filename = f"{datos['tipo_documento']}_{datos['numero_venta']}.pdf"

        enviado = enviar_correo_comprobante(
            destinatario_email=correo_dest,
            destinatario_nombre=datos["cliente_nombre"],
            tipo_documento=datos["tipo_documento"],
            numero_documento=datos["numero_venta"],
            total_bs=datos["total"],
            pdf_bytes=pdf_bytes,
            nombre_archivo=filename
        )

        if not enviado:
            return {
                "success": False,
                "message": "No se pudo entregar el correo en este momento, pero puedes descargar el PDF directamente.",
                "correo": correo_dest
            }

        return {
            "success": True,
            "message": f"Comprobante enviado exitosamente a {correo_dest}.",
            "correo": correo_dest
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
