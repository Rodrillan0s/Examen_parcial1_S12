from app.repos import kpis_repos
from app.services.rbac_services import obtener_nivel_actor

def procesar_etl_diario(token_data: dict):
    nivel = obtener_nivel_actor(token_data)
    if nivel > 2:
        raise ValueError("Operación crítica restringida. Solo el SuperAdministrador puede disparar el recálculo analítico.")
    
    filas = kpis_repos.ejecutar_extraccion_y_carga_etl_db()
    return {
        "success": True, 
        "message": f"Consolidación analítica de Aurora Store completada. Tablas actualizadas: {filas}"
    }

def generar_dashboard(token_data: dict):
    nivel = obtener_nivel_actor(token_data)
    id_empresa = token_data.get('id_empresa')
    id_sucursal = (token_data.get('sucursales') or [1])[0] if token_data.get('sucursales') else 1
    id_usuario = token_data.get('nro_usuario') or token_data.get('id_usuario') or 1

    # Nivel 6 o superior: CLIENTE / PROVEEDOR
    if nivel >= 6:
        raise ValueError("Acceso restringido: El panel analítico interno es exclusivo para el personal operativo y administrativo.")

    # Nivel 1 y 2: SUPERADMIN Y ADMIN PLATAFORMA
    if nivel <= 2:
        metricas = kpis_repos.obtener_metricas_globales_db()
        mensaje = "KPIs operacionales GLOBALES del ecosistema Aurora Store calculados exitosamente."

    # Nivel 3: ADMINISTRADOR DE TIENDA (TENANT)
    elif nivel == 3:
        if not id_empresa:
            metricas = kpis_repos.obtener_metricas_globales_db()
            mensaje = "KPIs de empresa calculados."
        else:
            metricas = kpis_repos.obtener_metricas_empresa_db(id_empresa)
            mensaje = f"KPIs operacionales de empresa calculados exitosamente."

    # Nivel 4: ENCARGADO DE SUCURSAL
    elif nivel == 4:
        metricas = kpis_repos.obtener_metricas_sucursal_db(id_sucursal, id_empresa)
        mensaje = "KPIs de sucursal calculados exitosamente."

    # Nivel 5: EMPLEADO / CAJERO
    else:
        metricas = kpis_repos.obtener_metricas_operativo_db(id_usuario)
        mensaje = "Métricas de turno operativo calculadas exitosamente."

    return {
        "success": True,
        "message": mensaje,
        "data": metricas
    }