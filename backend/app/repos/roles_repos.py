from app.classes.postgres import PostgreSQL
from app.config import Config

# --- LEER ROLES ---
def obtener_todos_los_roles():
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT nro_rol, nombre_rol, descripcion, fecha_registro 
            FROM {Config.SCHEMA}.rol 
            ORDER BY nro_rol ASC;
        """
        resultados = db.execute_query(query, fetchall=True)
        
        roles = []
        if resultados:
            for r in resultados:
                roles.append({
                    "nro_rol": r[0],
                    "nombre_rol": r[1],
                    "descripcion": r[2],
                    # Convertimos la fecha a string para que el JSON no tenga problemas
                    "fecha_registro": r[3].strftime("%Y-%m-%d %H:%M:%S") if r[3] else None
                })
        return roles
    finally:
        db.close_connection()

# --- CREAR ROL ---
def crear_rol_db(nombre_rol, descripcion):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.rol (nombre_rol, descripcion) 
            VALUES (%s, %s) 
            RETURNING nro_rol;
        """
        resultado = db.execute_query(query, (nombre_rol, descripcion), fetchone=True, commit=True)
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

# --- ACTUALIZAR ROL ---
def actualizar_rol_db(nro_rol, nombre_rol, descripcion):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.rol 
            SET nombre_rol = %s, descripcion = %s 
            WHERE nro_rol = %s;
        """
        filas_afectadas = db.execute_query(query, (nombre_rol, descripcion, nro_rol), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()

# --- ELIMINAR ROL (Borrado Físico) ---
def eliminar_rol_db(nro_rol: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"DELETE FROM {Config.SCHEMA}.rol WHERE nro_rol = %s;"
        filas_afectadas = db.execute_query(query, (nro_rol,), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()