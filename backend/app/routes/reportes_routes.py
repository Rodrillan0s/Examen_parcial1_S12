from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime

from app.services import reportes_services
from app.utils.security import verificar_token

router = APIRouter(prefix='/api/reportes', tags=["Reportes Bajo Demanda W33"])

@router.get('/ventas')
def reporte_ventas(
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicial YYYY-MM-DD"),
    fecha_fin: Optional[str] = Query(None, description="Fecha final YYYY-MM-DD"),
    id_sucursal: Optional[int] = Query(None, description="ID de sucursal específica"),
    estado: Optional[str] = Query(None, description="Estado de venta: COMPLETADA, PENDIENTE, ANULADA"),
    id_metodo_pago: Optional[int] = Query(None, description="Filtrar por método de pago"),
    id_empresa: Optional[int] = Query(None, description="Filtrar por empresa / tenant"),
    formato: str = Query('json', description="Formato de salida: 'json' o 'pdf'"),
    token_data: dict = Depends(verificar_token)
):
    """
    Genera el reporte de ventas bajo demanda con filtros dinámicos.
    Soporta visualización JSON para frontend y descarga directa en PDF con ReportLab.
    """
    try:
        if formato.lower() == 'pdf':
            pdf_buffer = reportes_services.generar_pdf_reporte_ventas(
                token_data, id_sucursal, fecha_inicio, fecha_fin, estado, id_metodo_pago
            )
            filename = f"reporte_ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return StreamingResponse(
                pdf_buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            return reportes_services.generar_reporte_ventas(
                token_data, id_sucursal, fecha_inicio, fecha_fin, estado, id_metodo_pago, id_empresa
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generando reporte de ventas: {str(e)}")


@router.get('/inventario')
def reporte_inventario(
    id_sucursal: Optional[int] = Query(None, description="ID de sucursal específica"),
    id_categoria: Optional[int] = Query(None, description="Filtrar por categoría"),
    estado_stock: Optional[str] = Query(None, description="Estado de existencias: 'todos', 'bajo', 'agotado', 'disponible'"),
    id_empresa: Optional[int] = Query(None, description="Filtrar por empresa / tenant"),
    formato: str = Query('json', description="Formato de salida: 'json' o 'pdf'"),
    token_data: dict = Depends(verificar_token)
):
    """
    Genera el reporte de inventario y existencias por almacén/sucursal.
    """
    try:
        if formato.lower() == 'pdf':
            pdf_buffer = reportes_services.generar_pdf_reporte_inventario(
                token_data, id_sucursal, id_categoria, estado_stock
            )
            filename = f"reporte_inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return StreamingResponse(
                pdf_buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            return reportes_services.generar_reporte_inventario(
                token_data, id_sucursal, id_categoria, estado_stock, id_empresa
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generando reporte de inventario: {str(e)}")


@router.get('/productos-vendidos')
def reporte_productos_vendidos(
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicial YYYY-MM-DD"),
    fecha_fin: Optional[str] = Query(None, description="Fecha final YYYY-MM-DD"),
    id_sucursal: Optional[int] = Query(None, description="ID de sucursal específica"),
    id_categoria: Optional[int] = Query(None, description="Filtrar por categoría"),
    id_empresa: Optional[int] = Query(None, description="Filtrar por empresa / tenant"),
    formato: str = Query('json', description="Formato de salida: 'json' o 'pdf'"),
    token_data: dict = Depends(verificar_token)
):
    """
    Genera el reporte de productos más vendidos, unidades y recaudación generada.
    """
    try:
        if formato.lower() == 'pdf':
            pdf_buffer = reportes_services.generar_pdf_reporte_productos_vendidos(
                token_data, id_sucursal, id_categoria, fecha_inicio, fecha_fin
            )
            filename = f"reporte_productos_vendidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return StreamingResponse(
                pdf_buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            return reportes_services.generar_reporte_productos_vendidos(
                token_data, id_sucursal, id_categoria, fecha_inicio, fecha_fin, id_empresa
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generando reporte de productos: {str(e)}")


@router.get('/sucursales')
def reporte_sucursales(
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicial YYYY-MM-DD"),
    fecha_fin: Optional[str] = Query(None, description="Fecha final YYYY-MM-DD"),
    id_empresa: Optional[int] = Query(None, description="Filtrar por empresa / tenant"),
    formato: str = Query('json', description="Formato de salida: 'json' o 'pdf'"),
    token_data: dict = Depends(verificar_token)
):
    """
    Genera el reporte comparativo entre sucursales de la empresa.
    """
    try:
        if formato.lower() == 'pdf':
            pdf_buffer = reportes_services.generar_pdf_reporte_sucursales(
                token_data, fecha_inicio, fecha_fin
            )
            filename = f"reporte_sucursales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return StreamingResponse(
                pdf_buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            return reportes_services.generar_reporte_sucursales(
                token_data, fecha_inicio, fecha_fin, id_empresa
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generando reporte de sucursales: {str(e)}")
