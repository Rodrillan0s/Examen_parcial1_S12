from app.classes.postgres import PostgreSQL
from app.config import Config

def get_contexto_emergencia(nro_emergencia: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        # ── 1. Datos de la emergencia y el vehículo ───────────────────
        emergencia_query = f"""
            SELECT 
                e.tipo_emergencia, 
                e.prioridad, 
                e.estado,
                v.marca_modelo, 
                v.año, 
                v.placa
            FROM {Config.SCHEMA}.emergencia e
            JOIN {Config.SCHEMA}.vehiculo v ON e.nro_usuario = v.nro_usuario
            WHERE e.nro_emergencia = %s
            LIMIT 1;
        """
        em_row = db.execute_query(emergencia_query, (nro_emergencia,), fetchone=True)

        if not em_row:
            return None

        emergencia_data = {
            "tipo_emergencia": em_row[0],
            "prioridad_actual": em_row[1],
            "estado": em_row[2],
            "marca_modelo": em_row[3],
            "año_vehiculo": em_row[4],
            "placa": em_row[5]
        }

        # ── 2. Evidencias (Dejamos pasar el Base64 original de la columna url_archivo) ──────
        evidencia_query = f"""
            SELECT tipo_archivo, transcripcion_archivo, url_archivo
            FROM {Config.SCHEMA}.evidencia
            WHERE nro_emergencia = %s;
        """
        evidencias_rows = db.execute_query(evidencia_query, (nro_emergencia,), fetchall=True)

        evidencias = []
        if evidencias_rows:
            for r in evidencias_rows:
                tipo = r[0] if r[0] else "ARCHIVO"
                transcripcion = r[1]
                url = r[2] if r[2] else ""

                # Si el url_archivo empieza con data:image, significa que es la imagen en Base64 pura
                if url.startswith("data:image"):
                    contenido = url
                elif transcripcion and str(transcripcion).strip().lower() != 'none':
                    contenido = str(transcripcion).strip()
                else:
                    contenido = "Evidencia multimedia sin transcripción."

                evidencias.append({
                    "tipo_archivo": tipo,
                    "descripcion": contenido
                })
        else:
            # Fallback en caso de que no existan filas en la tabla evidencia
            evidencias.append({
                "tipo_archivo": "SINTOMA_BASE",
                "descripcion": f"El cliente reporta un incidente crítico de tipo: {emergencia_data['tipo_emergencia']}"
            })

        return {
            "emergencia": emergencia_data,
            "evidencias": evidencias
        }
    finally:
        db.close_connection()