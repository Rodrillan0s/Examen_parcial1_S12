"""
Migración para crear las tablas comercio.t_pedido y comercio.t_detalle_pedido
con soporte multi-tenant e índices de consulta.
"""
from app.classes.postgres import PostgreSQL
from app.config import Config

def migrar_tablas_pedidos():
    schema = Config.SCHEMA or 'comercio'
    db = PostgreSQL()
    db.create_connection()
    try:
        print(f"Iniciando migración de pedidos en esquema: {schema}")

        # 1. Crear tabla t_pedido
        q_pedido = f"""
        CREATE TABLE IF NOT EXISTS {schema}.t_pedido (
            id_pedido SERIAL PRIMARY KEY,
            codigo_pedido VARCHAR(50) UNIQUE NOT NULL,
            id_cliente INT NOT NULL REFERENCES {schema}.t_cliente(id_cliente),
            id_empresa INT NOT NULL REFERENCES {schema}.empresa(id_empresa),
            id_sucursal INT NOT NULL REFERENCES {schema}.t_sucursal(id_sucursal),
            id_carrito_origen INT REFERENCES {schema}.t_carrito(id_carrito),
            fecha_pedido TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE_PAGO',
            estado_pago VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
            modalidad_compra VARCHAR(30) NOT NULL DEFAULT 'RETIRO_SUCURSAL',
            nombre_contacto VARCHAR(150),
            telefono_contacto VARCHAR(50),
            correo_contacto VARCHAR(150),
            direccion_entrega TEXT,
            ciudad_entrega VARCHAR(100),
            notas_entrega TEXT,
            subtotal NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
            costo_envio NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
            descuento NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
            total NUMERIC(12, 2) NOT NULL DEFAULT 0.00
        );
        """
        db.execute_query(q_pedido, commit=True)
        print("Tabla comercio.t_pedido creada/verificada.")

        # 2. Crear tabla t_detalle_pedido
        q_detalle = f"""
        CREATE TABLE IF NOT EXISTS {schema}.t_detalle_pedido (
            id_detalle_pedido SERIAL PRIMARY KEY,
            id_pedido INT NOT NULL REFERENCES {schema}.t_pedido(id_pedido) ON DELETE CASCADE,
            id_variante INT NOT NULL REFERENCES {schema}.t_producto_talla_color(id_variante),
            cantidad INT NOT NULL CHECK (cantidad > 0),
            precio_unitario NUMERIC(12, 2) NOT NULL,
            subtotal NUMERIC(12, 2) NOT NULL
        );
        """
        db.execute_query(q_detalle, commit=True)
        print("Tabla comercio.t_detalle_pedido creada/verificada.")

        # 3. Crear índices
        q_idx1 = f"CREATE INDEX IF NOT EXISTS idx_pedido_cliente_empresa_estado ON {schema}.t_pedido(id_cliente, id_empresa, estado);"
        q_idx2 = f"CREATE INDEX IF NOT EXISTS idx_pedido_codigo ON {schema}.t_pedido(codigo_pedido);"
        q_idx3 = f"CREATE INDEX IF NOT EXISTS idx_detalle_pedido_pedido ON {schema}.t_detalle_pedido(id_pedido);"
        db.execute_query(q_idx1, commit=True)
        db.execute_query(q_idx2, commit=True)
        db.execute_query(q_idx3, commit=True)
        print("Índices de comercio.t_pedido y t_detalle_pedido creados exitosamente.")

        # Verificar columnas
        cols_pedido = db.execute_query(f"SELECT column_name FROM information_schema.columns WHERE table_schema='{schema}' AND table_name='t_pedido';", fetchall=True)
        print("Columnas en t_pedido:", [c[0] for c in cols_pedido])

        cols_detalle = db.execute_query(f"SELECT column_name FROM information_schema.columns WHERE table_schema='{schema}' AND table_name='t_detalle_pedido';", fetchall=True)
        print("Columnas en t_detalle_pedido:", [c[0] for c in cols_detalle])

    finally:
        db.close_connection(commit=True)

if __name__ == '__main__':
    migrar_tablas_pedidos()
