from app.classes.postgres import PostgreSQL
from app.config import Config

def iniciar_conversacion_ia_db(nro_usuario: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"INSERT INTO {Config.SCHEMA}.conversacion_ia (nro_usuario) VALUES (%s) RETURNING id_conversacion;"
        resultado = db.execute_query(query, (nro_usuario,), fetchone=True, commit=True)
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

def escalar_conversacion_db(id_conversacion: int, resumen: str, nivel_riesgo: str):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.conversacion_ia 
            SET resumen_ia = %s, nivel_riesgo = %s, escalado_a_humano = TRUE, fecha_fin = CURRENT_TIMESTAMP
            WHERE id_conversacion = %s;
        """
        db.execute_query(query, (resumen, nivel_riesgo, id_conversacion), commit=True)
    finally:
        db.close_connection()