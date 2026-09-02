from app.classes.postgres import PostgreSQL
from app.config import Config

#LEER TODAS LAS EMERGENCIAS (PARA ADMINISTRADOR)
def obtener_todas_las_emergencias():
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT a.nro_emergencia, a.tipo_emergencia, a.latitud, a.longitud, 
            a.fecha_inicio, a.fecha_fin, a.estado, a.prioridad, 
            a.nro_usuario, a.nro_taller, a.id_empresa, b.nombre_usuario,
            a.nro_vehiculo, v.placa, v.marca_modelo, v.año
            FROM {Config.SCHEMA}.emergencia a
            INNER JOIN {Config.SCHEMA}.usuario b ON a.nro_usuario = b.nro_usuario 
            LEFT JOIN {Config.SCHEMA}.vehiculo v ON a.nro_vehiculo = v.nro_vehiculo
            ORDER BY a.fecha_inicio DESC;
        """
        resultados = db.execute_query(query, fetchall=True)

        emergencias = []
        if resultados:
            for r in resultados:
                emergencias.append({
                    "nro_emergencia": r[0],
                    "tipo_emergencia": r[1],
                    "latitud": float(r[2]) if r[2] is not None else None,
                    "longitud": float(r[3]) if r[3] is not None else None,
                    "fecha_inicio": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None,
                    "fecha_fin": r[5].strftime("%Y-%m-%d %H:%M:%S") if r[5] else None,
                    "estado": r[6],
                    "prioridad": r[7],
                    "nro_usuario": r[8],
                    "nro_taller": r[9],
                    "id_empresa": r[10],
                    "nombre_usuario": r[11],
                    "nro_vehiculo": r[12],
                    "vehiculo_placa": r[13],
                    "vehiculo_marca": r[14],
                    "vehiculo_año": r[15]
                })
        return emergencias
    finally:
        db.close_connection()

#LEER EMERGENCIAS POR USUARIO (PARA EL CLIENTE)
def obtener_emergencias_por_usuario(nro_usuario: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT e.nro_emergencia, e.tipo_emergencia, e.latitud, e.longitud, 
                   e.fecha_inicio, e.fecha_fin, e.estado, e.prioridad, 
                   e.nro_taller, e.id_empresa, e.nro_vehiculo,
                   v.placa, v.marca_modelo, v.año
            FROM {Config.SCHEMA}.emergencia e
            LEFT JOIN {Config.SCHEMA}.vehiculo v ON e.nro_vehiculo = v.nro_vehiculo
            WHERE e.nro_usuario = %s
            ORDER BY e.fecha_inicio DESC;
        """
        resultados = db.execute_query(query, (nro_usuario,), fetchall=True)

        emergencias = []
        if resultados:
            for r in resultados:
                emergencias.append({
                    "nro_emergencia": r[0],
                    "tipo_emergencia": r[1],
                    "latitud": float(r[2]) if r[2] is not None else None,
                    "longitud": float(r[3]) if r[3] is not None else None,
                    "fecha_inicio": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None,
                    "fecha_fin": r[5].strftime("%Y-%m-%d %H:%M:%S") if r[5] else None,
                    "estado": r[6],
                    "prioridad": r[7],
                    "nro_usuario": nro_usuario,
                    "nro_taller": r[8],
                    "id_empresa": r[9],
                    "nro_vehiculo": r[10],
                    "vehiculo_placa": r[11],
                    "vehiculo_marca": r[12],
                    "vehiculo_año": r[13]
                })
        return emergencias
    finally:
        db.close_connection()

#LEER EMERGENCIAS DEL TALLER DEL MECANICO
def obtener_emergencias_por_taller_del_mecanico(nro_usuario: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT 
                e.nro_emergencia, e.tipo_emergencia, e.latitud, e.longitud,
                e.fecha_inicio, e.fecha_fin, e.estado, e.prioridad,
                e.nro_usuario, e.nro_taller, e.id_empresa, t.nombre_taller,
                p.nombre_completo, p.telefono, e.nro_vehiculo,
                v.placa, v.marca_modelo, v.año
            FROM {Config.SCHEMA}.usuario um
            INNER JOIN {Config.SCHEMA}.taller t ON um.nro_taller = t.nro_taller
            INNER JOIN {Config.SCHEMA}.emergencia e ON e.nro_taller = t.nro_taller
            INNER JOIN {Config.SCHEMA}.usuario uc ON e.nro_usuario = uc.nro_usuario
            INNER JOIN {Config.SCHEMA}.persona p ON uc.ci = p.ci
            LEFT JOIN {Config.SCHEMA}.vehiculo v ON e.nro_vehiculo = v.nro_vehiculo
            WHERE um.nro_usuario = %s
              AND um.nro_taller IS NOT NULL
              AND um.id_empresa IS NOT NULL
              AND t.id_empresa = um.id_empresa
            ORDER BY e.fecha_inicio DESC;
        """
        resultados = db.execute_query(query, (nro_usuario,), fetchall=True)

        emergencias = []
        if resultados:
            for r in resultados:
                emergencias.append({
                    "nro_emergencia": r[0],
                    "tipo_emergencia": r[1],
                    "latitud": float(r[2]) if r[2] is not None else None,
                    "longitud": float(r[3]) if r[3] is not None else None,
                    "fecha_inicio": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None,
                    "fecha_fin": r[5].strftime("%Y-%m-%d %H:%M:%S") if r[5] else None,
                    "estado": r[6],
                    "prioridad": r[7],
                    "nro_usuario": r[8],
                    "nro_taller": r[9],
                    "id_empresa": r[10],
                    "nombre_taller": r[11],
                    "cliente": r[12],
                    "telefono_cliente": r[13],
                    "nro_vehiculo": r[14],
                    "vehiculo_placa": r[15],
                    "vehiculo_marca": r[16],
                    "vehiculo_año": r[17]
                })

        return emergencias
    finally:
        db.close_connection()

#CREAR EMERGENCIA
def crear_emergencia_db(tipo_emergencia, latitud, longitud, estado, prioridad, nro_usuario, nro_vehiculo=None):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.emergencia 
            (tipo_emergencia, latitud, longitud, fecha_inicio, estado, prioridad, nro_usuario, nro_vehiculo) 
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s) 
            RETURNING nro_emergencia;
        """
        resultado = db.execute_query(
            query,
            (tipo_emergencia, latitud, longitud, estado, prioridad, nro_usuario, nro_vehiculo),
            fetchone=True,
            commit=True
        )
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

#ACTUALIZAR EMERGENCIA
def actualizar_emergencia_db(nro_emergencia, tipo_emergencia, latitud, longitud, estado, prioridad, nro_taller, id_empresa, nro_vehiculo=None):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.emergencia 
            SET tipo_emergencia = %s, latitud = %s, longitud = %s, 
                estado = %s, prioridad = %s, nro_taller = %s, id_empresa = %s, nro_vehiculo = %s
            WHERE nro_emergencia = %s;
        """
        filas_afectadas = db.execute_query(
            query,
            (tipo_emergencia, latitud, longitud, estado, prioridad, nro_taller, id_empresa, nro_vehiculo, nro_emergencia),
            commit=True
        )
        return filas_afectadas > 0
    finally:
        db.close_connection()

#ELIMINAR EMERGENCIA (BORRADO FISICO)
def eliminar_emergencia_db(nro_emergencia: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"DELETE FROM {Config.SCHEMA}.emergencia WHERE nro_emergencia = %s;"
        filas_afectadas = db.execute_query(query, (nro_emergencia,), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()

#OBTENER EMERGENCIA POR ID
def obtener_emergencia_por_id(nro_emergencia: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"SELECT * FROM {Config.SCHEMA}.emergencia WHERE nro_emergencia = %s;"
        resultado = db.execute_query(query, (nro_emergencia,), fetchone=True)
        if resultado:
            return {
                "nro_emergencia": resultado[0],
                "estado": resultado[6], 
                "nro_usuario": resultado[8],
                "nro_taller": resultado[9],
                "nro_vehiculo": resultado[12] if len(resultado) > 12 else None
            }
        return None
    finally:
        db.close_connection()

#ACTUALIZAR ESTADO DE EMERGENCIA
def actualizar_estado_emergencia_db(nro_emergencia: int, nuevo_estado: str):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"UPDATE {Config.SCHEMA}.emergencia SET estado = %s WHERE nro_emergencia = %s;"
        filas_afectadas = db.execute_query(query, (nuevo_estado, nro_emergencia), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()

#AGREGAR EVIDENCIA EN BASE64
def agregar_evidencia_db(nro_emergencia: int, tipo_archivo: str, base64_data: str):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"INSERT INTO {Config.SCHEMA}.evidencia (nro_emergencia, tipo_archivo, url_archivo) VALUES (%s, %s, %s);"
        db.execute_query(query, (nro_emergencia, tipo_archivo, base64_data), commit=True)
    finally:
        db.close_connection()

#ELIMINAR EVIDENCIA
def eliminar_evidencia_db(nro_evidencia: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"DELETE FROM {Config.SCHEMA}.evidencia WHERE nro_evidencia = %s;"
        db.execute_query(query, (nro_evidencia,), commit=True)
    finally:
        db.close_connection()

#OBTENER EVIDENCIAS POR EMERGENCIA
def obtener_evidencias_db(nro_emergencia: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT nro_evidencia, tipo_archivo, url_archivo, 
                   transcripcion_archivo, diagnostico_archivo, fecha_carga
            FROM {Config.SCHEMA}.evidencia
            WHERE nro_emergencia = %s
            ORDER BY fecha_carga ASC;
        """
        resultados = db.execute_query(query, (nro_emergencia,), fetchall=True)
        
        evidencias = []
        if resultados:
            for r in resultados:
                evidencias.append({
                    "nro_evidencia": r[0],
                    "tipo_archivo": r[1],
                    "base64": r[2], 
                    "transcripcion_archivo": r[3],
                    "diagnostico_archivo": r[4],
                    "fecha_carga": r[5].strftime("%Y-%m-%d %H:%M:%S") if r[5] else None
                })
        return evidencias
    finally:
        db.close_connection()