from app.classes.postgres import PostgreSQL
from app.config import Config

# --- LEER SUCURSALES POR EMPRESA ---
def obtener_sucursales_por_empresa(id_empresa: int = None):
    db = PostgreSQL()
    db.create_connection()
    try:
        if id_empresa:
            query = f"""
                SELECT id_sucursal, nombre, direccion, activo, id_empresa 
                FROM {Config.SCHEMA}.t_sucursal 
                WHERE id_empresa = %s
                ORDER BY id_sucursal ASC;
            """
            resultados = db.execute_query(query, (id_empresa,), fetchall=True)
        else:
            query = f"""
                SELECT id_sucursal, nombre, direccion, activo, id_empresa 
                FROM {Config.SCHEMA}.t_sucursal 
                ORDER BY id_sucursal ASC;
            """
            resultados = db.execute_query(query, fetchall=True)
            
        sucursales = []
        if resultados:
            for r in resultados:
                sucursales.append({
                    "id_sucursal": r[0],
                    "nombre": r[1],
                    "direccion": r[2],
                    "activo": r[3],
                    "id_empresa": r[4]
                })
        return sucursales
    finally:
        db.close_connection()

# --- CREAR SUCURSAL ---
def crear_sucursal_db(nombre: str, direccion: str, id_empresa: int, activo: bool = True):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.t_sucursal (nombre, direccion, id_empresa, activo) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id_sucursal;
        """
        resultado = db.execute_query(query, (nombre, direccion, id_empresa, activo), fetchone=True, commit=True)
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

# --- LEER SUCURSAL POR ID ---
def obtener_sucursal_por_id(id_sucursal: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT s.id_sucursal, s.nombre, s.direccion, s.activo, s.id_empresa 
            FROM {Config.SCHEMA}.t_sucursal s
            WHERE s.id_sucursal = %s;
        """
        r = db.execute_query(query, (id_sucursal,), fetchone=True)
        if r:
            return {
                "id_sucursal": r[0],
                "nombre": r[1],
                "direccion": r[2],
                "activo": r[3],
                "id_empresa": r[4]
            }
        return None
    finally:
        db.close_connection()

# --- ACTUALIZAR SUCURSAL ---
def actualizar_sucursal_db(id_sucursal: int, nombre: str, direccion: str, id_empresa: int, activo: bool):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.t_sucursal 
            SET nombre = %s, direccion = %s, id_empresa = %s, activo = %s
            WHERE id_sucursal = %s;
        """
        filas_afectadas = db.execute_query(query, (nombre, direccion, id_empresa, activo, id_sucursal), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()

# --- DESACTIVAR SUCURSAL ---
def desactivar_sucursal_db(id_sucursal: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"UPDATE {Config.SCHEMA}.t_sucursal SET activo = FALSE WHERE id_sucursal = %s;"
        filas_afectadas = db.execute_query(query, (id_sucursal,), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()
