from app.classes.postgres import PostgreSQL
from app.config import Config

# --- LEER TODOS LOS VEHÍCULOS (Para el Administrador) ---
def obtener_todos_los_vehiculos():
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT nro_vehiculo, placa, marca_modelo, "año", vehiculo.fecha_registro, vehiculo.nro_usuario, usuario.nombre_usuario
            FROM {Config.SCHEMA}.vehiculo
            INNER JOIN {Config.SCHEMA}.usuario ON vehiculo.nro_usuario = usuario.nro_usuario
            ORDER BY nro_vehiculo ASC;
        """
        resultados = db.execute_query(query, fetchall=True)
        
        vehiculos = []
        if resultados:
            for r in resultados:
                vehiculos.append({
                    "nro_vehiculo": r[0],
                    "placa": r[1],
                    "marca_modelo": r[2],
                    "anio": r[3],
                    "fecha_registro": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None,
                    "nro_usuario": r[5],
                    "nombre_usuario": r[6]
                })
        return vehiculos
    finally:
        db.close_connection()

# --- LEER VEHÍCULOS POR USUARIO (Para la App Móvil / Cliente) ---
def obtener_vehiculos_por_usuario(nro_usuario: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT nro_vehiculo, placa, marca_modelo, "año", fecha_registro 
            FROM {Config.SCHEMA}.vehiculo
            WHERE nro_usuario = %s
            ORDER BY nro_vehiculo ASC;
        """
        resultados = db.execute_query(query, (nro_usuario,), fetchall=True)
        
        vehiculos = []
        if resultados:
            for r in resultados:
                vehiculos.append({
                    "nro_vehiculo": r[0],
                    "placa": r[1],
                    "marca_modelo": r[2],
                    "anio": r[3],
                    "fecha_registro": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None,
                    "nro_usuario": nro_usuario
                })
        return vehiculos
    finally:
        db.close_connection()

# --- CREAR VEHÍCULO ---
def crear_vehiculo_db(placa, marca_modelo, anio, nro_usuario):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.vehiculo (placa, marca_modelo, "año", nro_usuario) 
            VALUES (%s, %s, %s, %s) 
            RETURNING nro_vehiculo;
        """
        resultado = db.execute_query(query, (placa, marca_modelo, anio, nro_usuario), fetchone=True, commit=True)
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

# --- ACTUALIZAR VEHÍCULO ---
def actualizar_vehiculo_db(nro_vehiculo, placa, marca_modelo, anio):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.vehiculo 
            SET placa = %s, marca_modelo = %s, "año" = %s 
            WHERE nro_vehiculo = %s;
        """
        filas_afectadas = db.execute_query(query, (placa, marca_modelo, anio, nro_vehiculo), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()

# --- ELIMINAR VEHÍCULO ---
def eliminar_vehiculo_db(nro_vehiculo: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"DELETE FROM {Config.SCHEMA}.vehiculo WHERE nro_vehiculo = %s;"
        filas_afectadas = db.execute_query(query, (nro_vehiculo,), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()

# --- VALIDAR PLACA EXISTENTE ---
def verificar_placa_db(placa: str, nro_vehiculo_excluir: int = None):
    db = PostgreSQL()
    db.create_connection()
    try:
        if nro_vehiculo_excluir:
            # En el UPDATE: Verificamos si la placa existe, pero ignoramos el vehículo actual
            query = f"SELECT nro_vehiculo FROM {Config.SCHEMA}.vehiculo WHERE placa = %s AND nro_vehiculo != %s;"
            resultado = db.execute_query(query, (placa, nro_vehiculo_excluir), fetchone=True)
        else:
            # En el CREATE: Verificamos si la placa existe en cualquier registro
            query = f"SELECT nro_vehiculo FROM {Config.SCHEMA}.vehiculo WHERE placa = %s;"
            resultado = db.execute_query(query, (placa,), fetchone=True)
            
        return resultado is not None # Retorna True si la placa ya existe
    finally:
        db.close_connection()