from app.classes.postgres import PostgreSQL
from app.config import Config

# Inicializa el esquema comercio y las tablas de seguridad sobre las tablas existentes t_usuario y t_rol.
def inicializar_tablas_seguridad():
    db = PostgreSQL()
    try:
        db.create_connection()
        if not db.conn:
            return

        schema = Config.SCHEMA or 'comercio'

        # 1. Asegurar columnas en t_rol y sembrar roles requeridos
        db.execute_query(f"ALTER TABLE {schema}.t_rol ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;", commit=True)
        
        roles_default = [
            (1, 'ADMINISTRADOR', 'Administrador General'),
            (2, 'CLIENTE', 'Cliente Comprador'),
            (3, 'ADMINISTRADOR_TIENDA', 'Administrador de Tienda'),
            (4, 'ENCARGADO_SUCURSAL', 'Encargado de Sucursal'),
            (5, 'CAJERO', 'Cajero'),
            (6, 'PROVEEDOR', 'Proveedor')
        ]
        for r_id, r_nombre, r_desc in roles_default:
            res = db.execute_query(f"SELECT id_rol FROM {schema}.t_rol WHERE id_rol = %s OR LOWER(nombre) = LOWER(%s);", (r_id, r_nombre), fetchone=True)
            if not res:
                db.execute_query(f"INSERT INTO {schema}.t_rol (id_rol, nombre, descripcion) VALUES (%s, %s, %s);", (r_id, r_nombre, r_desc), commit=True)
            else:
                db.execute_query(f"UPDATE {schema}.t_rol SET nombre = %s, descripcion = %s WHERE id_rol = %s;", (r_nombre, r_desc, res[0]), commit=True)

        # 2. Tabla t_seguridad_usuario vinculada a t_usuario(id_usuario)
        query_seguridad = f"""
        CREATE TABLE IF NOT EXISTS {schema}.t_seguridad_usuario (
            id_seguridad SERIAL PRIMARY KEY,
            id_usuario INT UNIQUE NOT NULL REFERENCES {schema}.t_usuario(id_usuario) ON DELETE CASCADE,
            intentos_fallidos INT DEFAULT 0 NOT NULL,
            bloqueado_hasta TIMESTAMP,
            codigo_recuperacion VARCHAR(10),
            codigo_recuperacion_expira TIMESTAMP,
            codigo_verificacion_dispositivo VARCHAR(10),
            codigo_dispositivo_expira TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        db.execute_query(query_seguridad, commit=True)

        # 3. Tabla t_dispositivo_usuario vinculada a t_usuario(id_usuario)
        query_dispositivos = f"""
        CREATE TABLE IF NOT EXISTS {schema}.t_dispositivo_usuario (
            id_dispositivo SERIAL PRIMARY KEY,
            id_usuario INT NOT NULL REFERENCES {schema}.t_usuario(id_usuario) ON DELETE CASCADE,
            device_fingerprint VARCHAR(255) NOT NULL,
            nombre_dispositivo VARCHAR(150),
            ip_address VARCHAR(45),
            verificado BOOLEAN DEFAULT TRUE NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultima_conexion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uq_t_usuario_dispositivo UNIQUE (id_usuario, device_fingerprint)
        );
        """
        db.execute_query(query_dispositivos, commit=True)

        # 4. Tabla notificacion para notificaciones y alertas
        query_notificacion = f"""
        CREATE TABLE IF NOT EXISTS {schema}.notificacion (
            id_notificacion SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            cuerpo TEXT NOT NULL,
            tipo_referencia VARCHAR(100) DEFAULT 'SISTEMA',
            nro_usuario INT NOT NULL REFERENCES {schema}.t_usuario(id_usuario) ON DELETE CASCADE,
            leido BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nro_emergencia INT
        );
        """
        db.execute_query(query_notificacion, commit=True)
    except Exception as e:
        raise e
    finally:
        db.close_connection()
