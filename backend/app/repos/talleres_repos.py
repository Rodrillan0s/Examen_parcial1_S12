from app.classes.postgres import PostgreSQL
from app.config import Config

#OBTENER TALLERES
def obtener_todos_los_talleres(id_empresa_filtro=None):
    db = PostgreSQL()
    db.create_connection()
    try:
        # LÓGICA DEL FILTRO:
        if id_empresa_filtro:
            query = f"""
                SELECT nro_taller, nombre_taller, direccion_escrita, latitud, longitud, disponibilidad, fecha_registro, id_empresa
                FROM {Config.SCHEMA}.taller
                WHERE id_empresa = %s
                ORDER BY nro_taller ASC;
            """
            resultados = db.execute_query(query, (id_empresa_filtro,), fetchall=True)
        else:
            
            query = f"""
                SELECT nro_taller, nombre_taller, direccion_escrita, latitud, longitud, disponibilidad, fecha_registro, id_empresa
                FROM {Config.SCHEMA}.taller
                ORDER BY nro_taller ASC;
            """
            resultados = db.execute_query(query, fetchall=True)
        
        talleres = []
        if resultados:
            for r in resultados:
                talleres.append({
                    "nro_taller": r[0],
                    "nombre_taller": r[1],
                    "direccion_escrita": r[2],
                    "latitud": float(r[3]) if r[3] is not None else None,
                    "longitud": float(r[4]) if r[4] is not None else None,
                    "disponibilidad": r[5],
                    "fecha_registro": r[6].strftime("%Y-%m-%d %H:%M:%S") if r[6] else None,
                    "id_empresa": r[7]
                })
        return talleres
    finally:
        db.close_connection()

#CREAR NUEVO TALLER
def crear_taller_db(nombre_taller, direccion_escrita, latitud, longitud, id_empresa):
    db = PostgreSQL()
    db.create_connection()
    try:
        # La disponibilidad se pondrá en true automáticamente por tu DEFAULT en la BD
        query = f"""
            INSERT INTO {Config.SCHEMA}.taller (nombre_taller, direccion_escrita, latitud, longitud, id_empresa) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING nro_taller;
        """
        resultado = db.execute_query(query, (nombre_taller, direccion_escrita, latitud, longitud, id_empresa), fetchone=True, commit=True)
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

#ACTUALIZAR TALLER
def actualizar_taller_db(nro_taller, nombre_taller, direccion_escrita, latitud, longitud, disponibilidad, id_empresa):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.taller 
            SET nombre_taller = %s, direccion_escrita = %s, latitud = %s, longitud = %s, disponibilidad = %s, id_empresa = %s
            WHERE nro_taller = %s;
        """
        filas_afectadas = db.execute_query(query, (nombre_taller, direccion_escrita, latitud, longitud, disponibilidad, id_empresa, nro_taller), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()

#ELIMINAR TALLER
def eliminar_taller_db(nro_taller: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"DELETE FROM {Config.SCHEMA}.taller WHERE nro_taller = %s;"
        filas_afectadas = db.execute_query(query, (nro_taller,), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()


#SERVICIOS DEL TALLER
def obtener_servicios_taller(nro_taller: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT nro_servicio, nro_taller, nombre_servicio, descripcion, fecha_registro
            FROM {Config.SCHEMA}.servicio_taller
            WHERE nro_taller = %s
            ORDER BY nro_servicio ASC;
        """
        resultados = db.execute_query(query, (nro_taller,), fetchall=True)
        servicios = []
        if resultados:
            for r in resultados:
                servicios.append({
                    "nro_servicio": r[0],
                    "nro_taller": r[1],
                    "nombre_servicio": r[2],
                    "descripcion": r[3],
                    "fecha_registro": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None
                })
        return servicios
    finally:
        db.close_connection()

def crear_servicio_taller_db(nro_taller, nombre_servicio, descripcion):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.servicio_taller (nro_taller, nombre_servicio, descripcion)
            VALUES (%s, %s, %s)
            RETURNING nro_servicio;
        """
        resultado = db.execute_query(query, (nro_taller, nombre_servicio, descripcion), fetchone=True, commit=True)
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

def actualizar_servicio_taller_db(nro_servicio, nro_taller, nombre_servicio, descripcion):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.servicio_taller
            SET nombre_servicio = %s, descripcion = %s
            WHERE nro_servicio = %s AND nro_taller = %s;
        """
        filas_afectadas = db.execute_query(query, (nombre_servicio, descripcion, nro_servicio, nro_taller), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()

def eliminar_servicio_taller_db(nro_servicio: int, nro_taller: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"DELETE FROM {Config.SCHEMA}.servicio_taller WHERE nro_servicio = %s AND nro_taller = %s;"
        filas_afectadas = db.execute_query(query, (nro_servicio, nro_taller), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()


def obtener_id_empresa_de_taller(nro_taller: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"SELECT id_empresa FROM {Config.SCHEMA}.taller WHERE nro_taller = %s;"
        resultado = db.execute_query(query, (nro_taller,), fetchone=True)
        return resultado[0] if resultado else None
    finally:
        db.close_connection()