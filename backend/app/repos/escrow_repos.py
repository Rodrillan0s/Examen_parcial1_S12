from app.classes.postgres import PostgreSQL
from app.config import Config


def crear_retencion_fondos_db(monto: float, nro_emergencia: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.fondo_custodia
            (monto_retenido, nro_emergencia, estado_custodia)
            VALUES (%s, %s, 'RETENIDO')
            RETURNING id_custodia;
        """
        resultado = db.execute_query(
            query,
            (monto, nro_emergencia),
            fetchone=True,
            commit=True
        )
        return resultado[0] if resultado else None
    finally:
        db.close_connection()


def obtener_fondos_usuario_db(nro_usuario: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT
                f.id_custodia,
                f.monto_retenido,
                f.estado_custodia,
                f.fecha_retencion,
                e.nro_emergencia,
                e.tipo_emergencia,
                p.nombre_completo,
                v.placa,
                v.marca_modelo
            FROM {Config.SCHEMA}.fondo_custodia f
            INNER JOIN {Config.SCHEMA}.emergencia e
                ON e.nro_emergencia = f.nro_emergencia
            INNER JOIN {Config.SCHEMA}.usuario u
                ON u.nro_usuario = e.nro_usuario
            INNER JOIN {Config.SCHEMA}.persona p
                ON p.ci = u.ci
            LEFT JOIN {Config.SCHEMA}.vehiculo v
                ON v.nro_vehiculo = e.nro_vehiculo
            WHERE e.nro_usuario = %s
            ORDER BY f.fecha_retencion DESC;
        """

        resultados = db.execute_query(query, (nro_usuario,), fetchall=True)

        fondos = []
        total_retenido = 0

        if resultados:
            for r in resultados:
                monto = float(r[1] or 0)

                if r[2] == 'RETENIDO':
                    total_retenido += monto

                fondos.append({
                    "id_custodia": r[0],
                    "monto_retenido": monto,
                    "estado_custodia": r[2],
                    "fecha_retencion": r[3].isoformat() if r[3] else None,
                    "nro_emergencia": r[4],
                    "tipo_emergencia": r[5],
                    "nombre_usuario": r[6],
                    "vehiculo_placa": r[7],
                    "vehiculo_marca": r[8]
                })

        return {
            "total_retenido": total_retenido,
            "fondos": fondos
        }
    finally:
        db.close_connection()


def obtener_resumen_fondos_por_usuario_db():
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT
                u.nro_usuario,
                p.nombre_completo,
                p.telefono,
                COALESCE(SUM(
                    CASE
                        WHEN f.estado_custodia = 'RETENIDO'
                        THEN f.monto_retenido
                        ELSE 0
                    END
                ), 0) AS total_retenido,
                COUNT(f.id_custodia) AS cantidad_retenciones
            FROM {Config.SCHEMA}.fondo_custodia f
            INNER JOIN {Config.SCHEMA}.emergencia e
                ON e.nro_emergencia = f.nro_emergencia
            INNER JOIN {Config.SCHEMA}.usuario u
                ON u.nro_usuario = e.nro_usuario
            INNER JOIN {Config.SCHEMA}.persona p
                ON p.ci = u.ci
            GROUP BY u.nro_usuario, p.nombre_completo, p.telefono
            ORDER BY total_retenido DESC;
        """

        resultados = db.execute_query(query, fetchall=True)

        data = []
        if resultados:
            for r in resultados:
                data.append({
                    "nro_usuario": r[0],
                    "nombre_completo": r[1],
                    "telefono": r[2],
                    "total_retenido": float(r[3] or 0),
                    "cantidad_retenciones": r[4]
                })

        return data
    finally:
        db.close_connection()