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

        # 4. Tabla t_notificacion para notificaciones y alertas
        query_notificacion = f"""
        CREATE TABLE IF NOT EXISTS {schema}.t_notificacion (
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

        # 5. Función PostgreSQL fn_reservar_stock para control de concurrencia en reservas
        query_fn_reserva = f"""
        CREATE OR REPLACE FUNCTION {schema}.fn_reservar_stock(
            p_id_sucursal INT,
            p_id_variante INT,
            p_cantidad INT,
            p_id_usuario INT
        )
        RETURNS JSON AS $$
        DECLARE
            v_id_inventario INT;
            v_stock_actual INT;
            v_stock_reservado INT;
            v_stock_disponible INT;
            v_nuevo_reservado INT;
            v_nuevo_disponible INT;
        BEGIN
            IF p_cantidad <= 0 THEN
                RETURN json_build_object(
                    'success', false,
                    'error', 'CANTIDAD_INVALIDA',
                    'message', 'La cantidad a reservar debe ser mayor a 0.'
                );
            END IF;

            SELECT id_inventario, stock_actual, stock_reservado, stock_disponible
            INTO v_id_inventario, v_stock_actual, v_stock_reservado, v_stock_disponible
            FROM {schema}.t_inventario
            WHERE id_sucursal = p_id_sucursal AND id_variante = p_id_variante
            FOR UPDATE;

            IF v_id_inventario IS NULL THEN
                RETURN json_build_object(
                    'success', false,
                    'error', 'INVENTARIO_NO_ENCONTRADO',
                    'message', 'No existe inventario para la variante en la sucursal seleccionada.'
                );
            END IF;

            IF v_stock_disponible < p_cantidad THEN
                RETURN json_build_object(
                    'success', false,
                    'error', 'STOCK_INSUFICIENTE',
                    'message', 'Stock disponible insuficiente para cubrir la reserva.',
                    'stock_disponible', v_stock_disponible,
                    'cantidad_solicitada', p_cantidad
                );
            END IF;

            v_nuevo_reservado := v_stock_reservado + p_cantidad;
            v_nuevo_disponible := v_stock_disponible - p_cantidad;

            UPDATE {schema}.t_inventario
            SET stock_reservado = v_nuevo_reservado,
                stock_disponible = v_nuevo_disponible,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id_inventario = v_id_inventario;

            INSERT INTO {schema}.t_movimiento_inventario (
                id_inventario,
                id_usuario,
                tipo_movimiento,
                cantidad,
                stock_anterior,
                stock_nuevo,
                motivo,
                fecha_movimiento
            ) VALUES (
                v_id_inventario,
                p_id_usuario,
                'RESERVA',
                p_cantidad,
                v_stock_disponible,
                v_nuevo_disponible,
                'Reserva de prenda en sucursal',
                CURRENT_TIMESTAMP
            );

            RETURN json_build_object(
                'success', true,
                'id_inventario', v_id_inventario,
                'stock_anterior', v_stock_disponible,
                'stock_disponible', v_nuevo_disponible,
                'stock_reservado', v_nuevo_reservado
            );
        END;
        $$ LANGUAGE plpgsql;
        """
        db.execute_query(query_fn_reserva, commit=True)
    except Exception as e:
        raise e
    finally:
        db.close_connection()

