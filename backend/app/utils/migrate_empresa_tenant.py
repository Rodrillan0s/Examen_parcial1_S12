from app.classes.postgres import PostgreSQL
from app.config import Config

def migrar_empresa():
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        cur = db.conn.cursor()

        print(f"Iniciando migración de esquema para {schema}.empresa...")

        # 1. Agregar columnas si no existen
        columnas = [
            ("razon_social", "VARCHAR(255)"),
            ("correo", "VARCHAR(150)"),
            ("telefono", "VARCHAR(50)"),
            ("direccion_fiscal", "VARCHAR(255)"),
            ("ciudad", "VARCHAR(100)"),
            ("logo", "VARCHAR(500)"),
            ("updated_at", "TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP")
        ]

        for col_name, col_type in columnas:
            cur.execute(f"""
                ALTER TABLE {schema}.empresa 
                ADD COLUMN IF NOT EXISTS {col_name} {col_type};
            """)
            print(f"Columna verificada/agregada: {col_name} ({col_type})")

        # 2. Actualizar registro 1 existente con valores por defecto consistentes
        cur.execute(f"""
            UPDATE {schema}.empresa
            SET razon_social = COALESCE(razon_social, 'SHOPPING BOLIVIA S.R.L.'),
                correo = COALESCE(correo, 'contacto@shoppingbolivia.com.bo'),
                telefono = COALESCE(telefono, '+591 3 3445566'),
                direccion_fiscal = COALESCE(direccion_fiscal, 'Av. Cristo Redentor #2340'),
                ciudad = COALESCE(ciudad, 'Santa Cruz'),
                estado = 'ACTIVO'
            WHERE id_empresa = 1;
        """)

        # 3. Crear índice único en NIT para evitar duplicidad de empresas
        cur.execute(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_empresa_nit 
            ON {schema}.empresa(nit);
        """)
        print("Índice de unicidad uq_empresa_nit verificado/creado.")

        db.conn.commit()
        print("Migración de tabla empresa completada exitosamente.")
        cur.close()
    except Exception as e:
        if db.conn:
            db.conn.rollback()
        print(f"Error en la migración: {e}")
        raise e
    finally:
        db.close_connection()

if __name__ == '__main__':
    migrar_empresa()
