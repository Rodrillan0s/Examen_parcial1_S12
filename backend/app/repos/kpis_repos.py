from app.classes.postgres import PostgreSQL
from app.config import Config

def ejecutar_extraccion_y_carga_etl_db():
    """
    Limpia la tabla analítica y carga todo el historial de emergencias 
    disponibles para asegurar la demo.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        # 1. Limpiamos la tabla de hechos antes de recargar para evitar duplicados
        db.execute_query(f"TRUNCATE TABLE {Config.SCHEMA}.fact_emergencia_analitica", commit=True)
        
        # 2. Insertamos todo el historial sin filtrar por fecha (PARA DEMOSTRACIÓN)
        query = f"""
            INSERT INTO {Config.SCHEMA}.fact_emergencia_analitica 
            (fecha_sk, rango_hora, zona_geografica, tipo_emergencia, promedio_respuesta_minutos, cantidad_emergencias, ingresos_generados)
            SELECT 
                DATE(e.fecha_inicio) as fecha_sk,
                CASE 
                    WHEN EXTRACT(HOUR FROM e.fecha_inicio) < 6 THEN 'Madrugada'
                    WHEN EXTRACT(HOUR FROM e.fecha_inicio) < 12 THEN 'Mañana'
                    WHEN EXTRACT(HOUR FROM e.fecha_inicio) < 18 THEN 'Tarde'
                    ELSE 'Noche'
                END as rango_hora,
                'Zona Urbana' as zona_geografica, 
                e.tipo_emergencia,
                COALESCE(AVG(EXTRACT(EPOCH FROM (e.fecha_fin - e.fecha_inicio))/60), 30) as promedio_respuesta_minutos,
                COUNT(e.nro_emergencia) as cantidad_emergencias,
                COALESCE(SUM(oe.precio_estimado), 0.00) as ingresos_generados
            FROM {Config.SCHEMA}.emergencia e
            LEFT JOIN {Config.SCHEMA}.oferta_emergencia oe 
                ON e.nro_emergencia = oe.nro_emergencia AND UPPER(oe.estado_oferta) = 'ACEPTADA'
            GROUP BY 1, 2, 3, 4;
        """
        # execute_query devuelve el número de filas afectadas
        filas = db.execute_query(query, commit=True)
        return filas
    finally:
        db.close_connection()


def obtener_metricas_dashboard_db():
    db = PostgreSQL()
    db.create_connection()
    try:
        # 1. Incidentes por tipo (GLOBAL)
        query_tipos = f"""
            SELECT tipo_emergencia, COUNT(*) 
            FROM {Config.SCHEMA}.emergencia 
            GROUP BY tipo_emergencia
            ORDER BY COUNT(*) DESC;
        """
        tipos_raw = db.execute_query(query_tipos, fetchall=True)
        incidentes_por_tipo = [{"tipo": r[0], "cantidad": r[1]} for r in (tipos_raw or [])]

        # 2. Casos Cancelados y Totales (GLOBAL)
        query_estados = f"""
            SELECT 
                COUNT(*) as total_casos,
                COUNT(CASE WHEN UPPER(estado) = 'CANCELADO' THEN 1 END) as cancelados,
                COUNT(CASE WHEN UPPER(estado) = 'RESUELTO' THEN 1 END) as resueltos
            FROM {Config.SCHEMA}.emergencia;
        """
        estados_raw = db.execute_query(query_estados, fetchone=True)
        total_casos = estados_raw[0] if estados_raw else 0
        cancelados = estados_raw[1] if estados_raw else 0

        # 3. Talleres más eficientes en toda la plataforma
        query_eficiencia = f"""
            SELECT t.nombre_taller, 
                   AVG(EXTRACT(EPOCH FROM (e.fecha_fin - e.fecha_inicio))/60) as avg_minutos
            FROM {Config.SCHEMA}.emergencia e
            JOIN {Config.SCHEMA}.taller t ON e.nro_taller = t.nro_taller
            WHERE UPPER(e.estado) = 'RESUELTO' AND e.fecha_fin IS NOT NULL
            GROUP BY t.nombre_taller
            ORDER BY avg_minutos ASC LIMIT 5;
        """
        eficiencia_raw = db.execute_query(query_eficiencia, fetchall=True)
        talleres_eficientes = [{"taller": r[0], "tiempo_promedio_min": round(float(r[1]), 2)} for r in (eficiencia_raw or [])]

        # 4. Tiempos Promedio Operativos y SLA a Nivel Sistema
        query_tiempos = f"""
            SELECT 
                AVG(EXTRACT(EPOCH FROM (oe.fecha_oferta - e.fecha_inicio))/60) as tiempo_asignacion,
                AVG(EXTRACT(EPOCH FROM (e.fecha_fin - oe.fecha_oferta))/60) * 0.4 as tiempo_llegada_estimado,
                COUNT(*) as total_con_oferta,
                COUNT(CASE WHEN (EXTRACT(EPOCH FROM (e.fecha_fin - oe.fecha_oferta))/60) <= oe.tiempo_estimado_minutos THEN 1 END) as sla_cumplido
            FROM {Config.SCHEMA}.emergencia e
            JOIN {Config.SCHEMA}.oferta_emergencia oe ON e.nro_emergencia = oe.nro_emergencia
            WHERE UPPER(oe.estado_oferta) = 'ACEPTADA';
        """
        tiempos_raw = db.execute_query(query_tiempos, fetchone=True)
        
        t_asignacion = round(float(tiempos_raw[0]), 2) if tiempos_raw and tiempos_raw[0] else 0.0
        t_llegada = round(float(tiempos_raw[1]), 2) if tiempos_raw and tiempos_raw[1] else 0.0
        total_ofertas = tiempos_raw[2] if tiempos_raw and tiempos_raw[2] else 0
        sla_cumplidos = tiempos_raw[3] if tiempos_raw and tiempos_raw[3] else 0
        
        porcentaje_sla = round((sla_cumplidos / total_ofertas) * 100, 2) if total_ofertas > 0 else 0.0

        # 5. Mapa de Zonas Global
        query_mapa = f"""
            SELECT latitud, longitud, tipo_emergencia 
            FROM {Config.SCHEMA}.emergencia 
            WHERE latitud IS NOT NULL AND longitud IS NOT NULL;
        """
        mapa_raw = db.execute_query(query_mapa, fetchall=True)
        zonas_incidentes = [{"lat": float(r[0]), "lng": float(r[1]), "tipo": r[2]} for r in (mapa_raw or [])]

        return {
            "incidentes_por_tipo": incidentes_por_tipo,
            "casos_cancelados": cancelados,
            "total_casos_historicos": total_casos,
            "talleres_eficientes": talleres_eficientes,
            "tiempos_operativos": {
                "promedio_asignacion_minutos": t_asignacion,
                "promedio_llegada_minutos": t_llegada,
            },
            "nivel_cumplimiento_sla": f"{porcentaje_sla}%",
            "mapa_calor": zonas_incidentes
        }
    finally:
        db.close_connection()