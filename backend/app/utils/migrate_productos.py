import sys
import os

# Asegurar que el path incluya backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.classes.postgres import PostgreSQL
from app.config import Config

def run_migration():
    print("Iniciando migración para Gestión de Productos...")
    db = PostgreSQL()
    db.create_connection()
    schema = Config.SCHEMA or 'comercio'

    try:
        # 1. Actualizar tabla t_producto
        print("1. Verificando y agregando columnas en t_producto...")
        db.execute_query(f"""
            ALTER TABLE {schema}.t_producto 
            ADD COLUMN IF NOT EXISTS id_empresa INTEGER REFERENCES {schema}.empresa(id_empresa) ON DELETE CASCADE;
        """, commit=True)

        db.execute_query(f"""
            ALTER TABLE {schema}.t_producto 
            ADD COLUMN IF NOT EXISTS temporada VARCHAR(100);
        """, commit=True)

        db.execute_query(f"""
            ALTER TABLE {schema}.t_producto 
            ADD COLUMN IF NOT EXISTS coleccion VARCHAR(100);
        """, commit=True)

        db.execute_query(f"""
            ALTER TABLE {schema}.t_producto 
            ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;
        """, commit=True)

        db.execute_query(f"""
            ALTER TABLE {schema}.t_producto 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """, commit=True)

        # Si fecha_registro no tiene default
        db.execute_query(f"""
            ALTER TABLE {schema}.t_producto 
            ALTER COLUMN fecha_registro SET DEFAULT CURRENT_TIMESTAMP;
        """, commit=True)

        # Crear índice único por nombre y tenant
        print("Creando índice de unicidad por nombre y Tenant en t_producto...")
        db.execute_query(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_producto_nombre_tenant 
            ON {schema}.t_producto (LOWER(TRIM(nombre)), COALESCE(id_empresa, 0));
        """, commit=True)

        # 2. Crear tabla t_producto_imagen si no existe
        print("2. Creando tabla t_producto_imagen...")
        db.execute_query(f"""
            CREATE TABLE IF NOT EXISTS {schema}.t_producto_imagen (
                id_imagen SERIAL PRIMARY KEY,
                id_producto INTEGER NOT NULL REFERENCES {schema}.t_producto(id_producto) ON DELETE CASCADE,
                imagen_url VARCHAR(500) NOT NULL,
                public_id VARCHAR(255) NOT NULL,
                es_principal BOOLEAN DEFAULT FALSE,
                orden INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """, commit=True)

        db.execute_query(f"""
            CREATE INDEX IF NOT EXISTS idx_producto_imagen_prod 
            ON {schema}.t_producto_imagen (id_producto);
        """, commit=True)

        # 3. Actualizar t_producto_talla_color (Variantes)
        print("3. Ajustando t_producto_talla_color...")
        db.execute_query(f"""
            ALTER TABLE {schema}.t_producto_talla_color 
            ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;
        """, commit=True)

        db.execute_query(f"""
            ALTER TABLE {schema}.t_producto_talla_color 
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """, commit=True)

        db.execute_query(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_variante_producto_talla_color 
            ON {schema}.t_producto_talla_color (id_producto, id_talla, id_color);
        """, commit=True)

        # 4. Verificar permisos para Productos
        print("4. Verificando y asignando permisos de Productos...")
        permisos = [
            ('productos.ver', 'Ver catálogo y lista de productos', 'PRODUCTOS'),
            ('productos.crear', 'Crear nuevo producto y variantes', 'PRODUCTOS'),
            ('productos.editar', 'Editar producto, variantes y fotos', 'PRODUCTOS'),
            ('productos.desactivar', 'Activar o desactivar productos', 'PRODUCTOS'),
            ('productos.eliminar', 'Eliminar producto o variantes', 'PRODUCTOS'),
            ('productos.cambiar_precio', 'Cambiar precio de venta de productos', 'PRODUCTOS')
        ]

        for codigo, nombre, modulo in permisos:
            db.execute_query(f"""
                INSERT INTO {schema}.t_permiso (codigo, nombre, modulo)
                VALUES (%s, %s, %s)
                ON CONFLICT (codigo) DO UPDATE 
                SET nombre = EXCLUDED.nombre, modulo = EXCLUDED.modulo;
            """, (codigo, nombre, modulo), commit=True)

        # Asignar permisos a roles: 1 (SuperAdmin), 3 (Admin), 4 (Admin Tienda), 5 (Encargado)
        roles = [1, 3, 4, 5]
        for r_id in roles:
            # Comprobar si el rol existe
            rol_existe = db.execute_query(f"SELECT COUNT(*) FROM {schema}.t_rol WHERE id_rol = %s;", (r_id,), fetchone=True)[0]
            if rol_existe > 0:
                for codigo, _, _ in permisos:
                    perm_id_row = db.execute_query(f"SELECT id_permiso FROM {schema}.t_permiso WHERE codigo = %s;", (codigo,), fetchone=True)
                    if perm_id_row:
                        p_id = perm_id_row[0]
                        db.execute_query(f"""
                            INSERT INTO {schema}.t_rol_permiso (id_rol, id_permiso)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING;
                        """, (r_id, p_id), commit=True)

        print("Migración de Productos completada con éxito.")
    except Exception as e:
        print(f"Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close_connection()

if __name__ == '__main__':
    run_migration()
