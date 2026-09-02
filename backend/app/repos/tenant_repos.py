from app.classes.postgres import PostgreSQL
from app.config import Config

# --- LEER EMPRESAS ---
def obtener_todas_las_empresas():
    db = PostgreSQL()
    db.create_connection()
    try:
        # Se quitó el filtro WHERE estado = 'ACTIVO' para mostrar todo
        query = f"""
            SELECT id_empresa, nombre_empresa, nit, estado 
            FROM {Config.SCHEMA}.empresa 
            ORDER BY id_empresa ASC;
        """
        resultados = db.execute_query(query, fetchall=True)
        
        empresas = []
        if resultados:
            for r in resultados:
                empresas.append({
                    "id_empresa": r[0],
                    "nombre_empresa": r[1],
                    "nit": r[2],
                    "estado": r[3]
                })
        return empresas
    finally:
        db.close_connection()

# --- CREAR EMPRESA ---
def crear_empresa_db(nombre_empresa, nit):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.empresa (nombre_empresa, nit, estado) 
            VALUES (%s, %s, 'ACTIVO') 
            RETURNING id_empresa;
        """
        resultado = db.execute_query(query, (nombre_empresa, nit), fetchone=True, commit=True)
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

# --- ACTUALIZAR EMPRESA ---
def actualizar_empresa_db(id_empresa, nombre_empresa, nit, estado):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.empresa 
            SET nombre_empresa = %s, nit = %s, estado = %s 
            WHERE id_empresa = %s;
        """
        # Guardamos cuántas filas se actualizaron realmente
        filas_afectadas = db.execute_query(query, (nombre_empresa, nit, estado, id_empresa), commit=True)
        return filas_afectadas > 0 # Retorna True si afectó al menos 1 fila, False si es 0
    finally:
        db.close_connection()

# --- ELIMINAR EMPRESA (Borrado Físico Completo) ---
def eliminar_empresa_db(id_empresa: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"DELETE FROM {Config.SCHEMA}.empresa WHERE id_empresa = %s;"
        # Guardamos cuántas filas se borraron realmente
        filas_afectadas = db.execute_query(query, (id_empresa,), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()