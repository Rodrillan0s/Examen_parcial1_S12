from app.classes.postgres import PostgreSQL
from app.config import Config

def obtener_todas_las_tarifas():
    db = PostgreSQL()
    db.create_connection()
    try:
        # Consulta exacta adaptada a tu CREATE TABLE
        query = f"""
            SELECT id_concepto, nombre_concepto, precio_base, tipo
            FROM {Config.SCHEMA}.concepto_tarifa
            ORDER BY id_concepto ASC;
        """
        resultados = db.execute_query(query, fetchall=True)
        tarifas = []
        if resultados:
            for r in resultados:
                tarifas.append({
                    "id_concepto": r[0],
                    "descripcion": r[1],  # Traduce 'nombre_concepto' a 'descripcion' para tu servicio
                    "monto": float(r[2]) if r[2] is not None else 0.0,  # Traduce 'precio_base' a 'monto'
                    "tipo": r[3]
                })
        return tarifas
    finally:
        db.close_connection()

def crear_tarifa_db(descripcion: str, monto: float, tipo: str):
    db = PostgreSQL()
    db.create_connection()
    try:
        # Inserción con tus columnas reales
        query = f"""
            INSERT INTO {Config.SCHEMA}.concepto_tarifa (nombre_concepto, precio_base, tipo)
            VALUES (%s, %s, %s) RETURNING id_concepto;
        """
        resultado = db.execute_query(query, (descripcion, monto, tipo), fetchone=True, commit=True)
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

def actualizar_tarifa_db(id_concepto: int, descripcion: str, monto: float, tipo: str):
    db = PostgreSQL()
    db.create_connection()
    try:
        # Actualización usando tus columnas reales
        query = f"""
            UPDATE {Config.SCHEMA}.concepto_tarifa
            SET nombre_concepto = %s, precio_base = %s, tipo = %s
            WHERE id_concepto = %s;
        """
        filas_afectadas = db.execute_query(query, (descripcion, monto, tipo, id_concepto), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()

def eliminar_tarifa_db(id_concepto: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"DELETE FROM {Config.SCHEMA}.concepto_tarifa WHERE id_concepto = %s;"
        filas_afectadas = db.execute_query(query, (id_concepto,), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()