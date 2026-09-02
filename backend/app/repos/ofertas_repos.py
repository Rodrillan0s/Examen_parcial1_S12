from app.classes.postgres import PostgreSQL
from app.config import Config

#CREAR OFERTA
def crear_oferta_db(precio_estimado, tiempo_estimado_minutos, nro_emergencia, nro_taller):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.oferta_emergencia 
            (precio_estimado, tiempo_estimado_minutos, estado_oferta, fecha_oferta, nro_emergencia, nro_taller) 
            VALUES (%s, %s, 'PENDIENTE', CURRENT_TIMESTAMP, %s, %s) 
            RETURNING id_oferta;
        """
        resultado = db.execute_query(
            query,
            (precio_estimado, tiempo_estimado_minutos, nro_emergencia, nro_taller),
            fetchone=True,
            commit=True
        )
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

#OBTENER OFERTA POR ID
def obtener_oferta_por_id_db(id_oferta: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"SELECT * FROM {Config.SCHEMA}.oferta_emergencia WHERE id_oferta = %s;"
        resultado = db.execute_query(query, (id_oferta,), fetchone=True)
        if resultado:
            return {
                "id_oferta": resultado[0],
                "precio_estimado": float(resultado[1]),
                "tiempo_estimado_minutos": resultado[2],
                "estado_oferta": resultado[3],
                "nro_emergencia": resultado[5],
                "nro_taller": resultado[6]
            }
        return None
    finally:
        db.close_connection()

#ACTUALIZAR ESTADO DE OFERTA
def actualizar_estado_oferta_db(id_oferta: int, estado: str):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"UPDATE {Config.SCHEMA}.oferta_emergencia SET estado_oferta = %s WHERE id_oferta = %s;"
        filas = db.execute_query(query, (estado, id_oferta), commit=True)
        return filas > 0
    finally:
        db.close_connection()

#RECHAZAR OTRAS OFERTAS AUTOMATICAMENTE (CU28)
def rechazar_otras_ofertas_db(nro_emergencia: int, id_oferta_aceptada: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.oferta_emergencia 
            SET estado_oferta = 'RECHAZADA' 
            WHERE nro_emergencia = %s AND id_oferta != %s AND estado_oferta = 'PENDIENTE';
        """
        db.execute_query(query, (nro_emergencia, id_oferta_aceptada), commit=True)
    finally:
        db.close_connection()

#VINCULAR TALLER A EMERGENCIA AL ACEPTAR OFERTA
def asignar_taller_emergencia_db(nro_emergencia: int, nro_taller: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"UPDATE {Config.SCHEMA}.emergencia SET estado = 'ACEPTADO', nro_taller = %s WHERE nro_emergencia = %s;"
        db.execute_query(query, (nro_taller, nro_emergencia), commit=True)
    finally:
        db.close_connection()

#LEER OFERTAS POR EMERGENCIA (CON NOMBRE DE TALLER PARA EL CLIENTE)
def obtener_ofertas_por_emergencia_db(nro_emergencia: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT o.id_oferta, o.precio_estimado, o.tiempo_estimado_minutos, o.estado_oferta, o.fecha_oferta, 
                   o.nro_emergencia, o.nro_taller, t.nombre_taller
            FROM {Config.SCHEMA}.oferta_emergencia o
            INNER JOIN {Config.SCHEMA}.taller t ON o.nro_taller = t.nro_taller
            WHERE o.nro_emergencia = %s
            ORDER BY o.precio_estimado ASC;
        """
        resultados = db.execute_query(query, (nro_emergencia,), fetchall=True)
        ofertas = []
        if resultados:
            for r in resultados:
                ofertas.append({
                    "id_oferta": r[0],
                    "precio_estimado": float(r[1]),
                    "tiempo_estimado_minutos": r[2],
                    "estado_oferta": r[3],
                    "fecha_oferta": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None,
                    "nro_emergencia": r[5],
                    "nro_taller": r[6],
                    "nombre_taller": r[7]
                })
        return ofertas
    finally:
        db.close_connection()

#LEER OFERTAS EMITIDAS POR MI TALLER
def obtener_ofertas_por_taller_db(nro_taller: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT id_oferta, precio_estimado, tiempo_estimado_minutos, estado_oferta, fecha_oferta, nro_emergencia 
            FROM {Config.SCHEMA}.oferta_emergencia
            WHERE nro_taller = %s
            ORDER BY fecha_oferta DESC;
        """
        resultados = db.execute_query(query, (nro_taller,), fetchall=True)
        ofertas = []
        if resultados:
            for r in resultados:
                ofertas.append({
                    "id_oferta": r[0],
                    "precio_estimado": float(r[1]),
                    "tiempo_estimado_minutos": r[2],
                    "estado_oferta": r[3],
                    "fecha_oferta": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None,
                    "nro_emergencia": r[5]
                })
        return ofertas
    finally:
        db.close_connection()