from app.classes.postgres import PostgreSQL
from app.config import Config

def migrar_carrito():
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        # 1. Agregar columna id_empresa si no existe
        q1 = f"""
            ALTER TABLE {schema}.t_carrito 
            ADD COLUMN IF NOT EXISTS id_empresa integer REFERENCES {schema}.empresa(id_empresa);
        """
        db.execute_query(q1)

        # 2. Crear índice para búsqueda ágil de carrito por cliente y empresa
        q2 = f"""
            CREATE INDEX IF NOT EXISTS idx_carrito_cliente_empresa_estado 
            ON {schema}.t_carrito (id_cliente, id_empresa, estado);
        """
        db.execute_query(q2)

        # 3. Crear índice para detalle carrito
        q3 = f"""
            CREATE INDEX IF NOT EXISTS idx_detalle_carrito_carrito_variante 
            ON {schema}.t_detalle_carrito (id_carrito, id_variante);
        """
        db.execute_query(q3)

        print("✅ Migración de t_carrito completada exitosamente.")
    finally:
        db.close_connection()

if __name__ == "__main__":
    migrar_carrito()
