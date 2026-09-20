import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.utils.security import verificar_token
from app.reports.engine.catalog import CATALOGO_REPORTES
from app.reports.parser.command_parser import interpretar_comando_reporte
from app.reports.engine.report_engine import (
    ejecutar_reporte_dinamico,
    generar_pdf_reporte_dinamico,
    _resolver_contexto_tenant
)

router = APIRouter(prefix="/api/motor-reportes", tags=["Motor de Reportes Dinámico"])


class ParseCommandIn(BaseModel):
    command: Optional[str] = Field(None, description="Comando en lenguaje natural")
    comando: Optional[str] = Field(None, description="Alias en español para el comando")
    contexto: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexto opcional")

    def texto_comando(self) -> str:
        return (self.command or self.comando or "").strip()


class ReporteEjecucionIn(BaseModel):
    tipo_reporte: str = Field(..., description="Código canónico del reporte (ej. ventas, inventario, etc.)")
    filtros: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Diccionario de filtros normalizados")
    groupBy: Optional[str] = Field(None, description="Campo para agrupación SQL")
    orderBy: Optional[str] = Field(None, description="Columna para ordenamiento")
    orderDirection: Optional[str] = Field("DESC", description="ASC o DESC")


@router.get("/catalogo")
def obtener_catalogo_reportes(token_data: dict = Depends(verificar_token)):
    """
    Retorna la lista de reportes disponibles en el motor, sus vistas,
    filtros permitidos, agrupaciones y metadatos de columnas.
    """
    try:
        return {
            "success": True,
            "total": len(CATALOGO_REPORTES),
            "catalogo": list(CATALOGO_REPORTES.values())
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo catálogo de reportes: {str(e)}"
        )


@router.post("/parse-command")
def parsear_comando_reporte(
    payload: ParseCommandIn,
    token_data: dict = Depends(verificar_token)
):
    """
    Interpreta un comando de voz o texto determinísticamente.
    Retorna un ReportRequest canónico y si existen ambigüedades.
    """
    try:
        txt = payload.texto_comando()
        if not txt:
            raise ValueError("Debe ingresar o dictar un comando de texto.")

        id_empresa, _ = _resolver_contexto_tenant(token_data)
        resultado = interpretar_comando_reporte(txt, id_empresa=id_empresa)
        return {
            "success": True,
            **resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interpretando comando: {str(e)}"
        )


@router.post("/ejecutar")
def ejecutar_reporte(
    payload: ReporteEjecucionIn,
    token_data: dict = Depends(verificar_token)
):
    """
    Ejecuta una consulta SQL parametrizada a través del motor de reportes dinámico.
    Garantiza aislamiento multi-tenant estricto según la empresa del usuario.
    """
    try:
        req_dict = payload.model_dump()
        datos = ejecutar_reporte_dinamico(req_dict, token_data)
        return {
            "success": True,
            "data": datos
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ejecutando reporte dinámico: {str(e)}"
        )


@router.post("/exportar/pdf")
def exportar_reporte_pdf(
    payload: ReporteEjecucionIn,
    token_data: dict = Depends(verificar_token)
):
    """
    Genera y descarga en streaming un PDF profesional del reporte especificado.
    """
    try:
        req_dict = payload.model_dump()
        datos = ejecutar_reporte_dinamico(req_dict, token_data)
        
        pdf_buffer = generar_pdf_reporte_dinamico(datos, token_data)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        tipo = payload.tipo_reporte
        filename = f"reporte_{tipo}_{timestamp}.pdf"

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando PDF del reporte: {str(e)}"
        )
