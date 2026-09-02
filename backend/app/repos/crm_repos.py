from app.classes.postgres import PostgreSQL
from app.config import Config


def crear_plan_mantenimiento_db(tipo_servicio: str, kilometraje_esperado: int, fecha_estimada: str, nro_vehiculo: int, id_empresa: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.plan_mantenimiento
            (tipo_servicio, kilometraje_esperado, fecha_estimada, estado_plan, nro_vehiculo, id_empresa)
            VALUES (%s, %s, %s, 'PENDIENTE', %s, %s)
            RETURNING id_plan;
        """
        resultado = db.execute_query(
            query,
            (tipo_servicio, kilometraje_esperado, fecha_estimada, nro_vehiculo, id_empresa),
            fetchone=True,
            commit=True
        )
        return resultado[0] if resultado else None
    finally:
        db.close_connection()


def obtener_planes_vencidos_pendientes_db():
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT p.id_plan, p.tipo_servicio, p.nro_vehiculo, v.nro_usuario
            FROM {Config.SCHEMA}.plan_mantenimiento p
            INNER JOIN {Config.SCHEMA}.vehiculo v ON p.nro_vehiculo = v.nro_vehiculo
            WHERE p.estado_plan = 'PENDIENTE'
            AND p.fecha_estimada <= CURRENT_DATE;
        """
        resultados = db.execute_query(query, fetchall=True)

        planes = []
        if resultados:
            for r in resultados:
                planes.append({
                    "id_plan": r[0],
                    "tipo_servicio": r[1],
                    "nro_vehiculo": r[2],
                    "nro_usuario": r[3]
                })

        return planes
    finally:
        db.close_connection()


def actualizar_estado_plan_db(id_plan: int, nuevo_estado: str):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.plan_mantenimiento
            SET estado_plan = %s
            WHERE id_plan = %s;
        """
        db.execute_query(query, (nuevo_estado, id_plan), commit=True)
    finally:
        db.close_connection()


def obtener_clientes_crm_db():
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT
                u.nro_usuario,
                p.nombre_completo,
                p.telefono,
                p.correo,
                u.nombre_usuario
            FROM {Config.SCHEMA}.usuario u
            INNER JOIN {Config.SCHEMA}.persona p ON p.ci = u.ci
            INNER JOIN {Config.SCHEMA}.rol r ON r.nro_rol = u.nro_rol
            WHERE UPPER(r.nombre_rol) = 'CLIENTE'
            ORDER BY p.nombre_completo ASC;
        """
        resultados = db.execute_query(query, fetchall=True)

        clientes = []
        if resultados:
            for r in resultados:
                clientes.append({
                    "nro_usuario": r[0],
                    "nombre": r[1],
                    "apellido": "",
                    "telefono": r[2],
                    "correo": r[3],
                    "username": r[4]
                })

        return clientes
    finally:
        db.close_connection()