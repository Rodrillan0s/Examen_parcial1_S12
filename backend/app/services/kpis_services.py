from app.repos import kpis_repos

def procesar_etl_diario(token_data: dict):
    if token_data.get('nombre_rol', '').upper() != 'ADMINISTRADOR':
        raise ValueError("Operación crítica. Solo el administrador puede disparar el ETL.")
    
    filas = kpis_repos.ejecutar_extraccion_y_carga_etl_db()
    return {
        "success": True, 
        "message": f"Proceso ETL completado exitosamente. Bloques analíticos generados: {filas}"
    }

def generar_dashboard(token_data: dict):
    rol = token_data.get('nombre_rol', '').upper()
    id_empresa = token_data.get('id_empresa')

    if rol == 'ADMINISTRADOR':
        # El administrador ve la métrica global (pasamos None para no filtrar)
        metricas = kpis_repos.obtener_metricas_dashboard_db()
        mensaje = "KPIs operacionales GLOBALES calculados exitosamente."
    
    elif rol == 'GERENTE TALLER':
        # El gerente solo ve la información de su tenant/empresa
        if not id_empresa:
            raise ValueError("Configuración de cuenta errónea. No perteneces a una empresa.")
        metricas = kpis_repos.obtener_metricas_dashboard_db()
        mensaje = "KPIs operacionales DE SUCURSAL calculados exitosamente."
    
    else:
        raise ValueError("No tienes permisos suficientes para acceder a la analítica.")

    return {
        "success": True,
        "message": mensaje,
        "data": metricas
    }