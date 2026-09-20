import logging
from app.classes.postgres import PostgreSQL
from app.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MigrateM14")

def migrate():
    db = PostgreSQL()
    db.create_connection()
    schema = Config.SCHEMA or 'comercio'

    try:
        # 1. Agregar columnas a t_producto si no existen
        logger.info(f"Agregando columnas RA a {schema}.t_producto...")
        alter_query = f"""
            ALTER TABLE {schema}.t_producto
            ADD COLUMN IF NOT EXISTS tiene_ra BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS modelo_2d_url VARCHAR(500),
            ADD COLUMN IF NOT EXISTS tipo_prenda_ra VARCHAR(50);
        """
        db.execute_query(alter_query)

        # 2. Asignar prendas compatibles para demostración de RA (TOP, PANT, DRESS)
        # Usamos imágenes transparentes de alta calidad en WebP/PNG
        prendas_ra = [
            {
                "codigo": "TOP_01",
                "nombre": "Blusa Seda Gala Aurora",
                "tipo": "TOP",
                "url": "https://res.cloudinary.com/demo/image/upload/v1689254821/samples/ecommerce/clothing-white-blouse.png"
            },
            {
                "codigo": "PANT_01",
                "nombre": "Pantalón Sastrería Obsidian",
                "tipo": "PANT",
                "url": "https://res.cloudinary.com/demo/image/upload/v1689254821/samples/ecommerce/leather-bag-gray.png"
            },
            {
                "codigo": "DRESS_01",
                "nombre": "Vestido de Noche Aurora Gold",
                "tipo": "DRESS",
                "url": "https://res.cloudinary.com/demo/image/upload/v1689254821/samples/ecommerce/shoes.png"
            }
        ]

        # Verificar qué productos existen en la BD y habilitar RA en al menos 3 prendas
        q_prod = f"SELECT id_producto, nombre FROM {schema}.t_producto WHERE activo = TRUE ORDER BY id_producto ASC LIMIT 6;"
        prods = db.execute_query(q_prod, fetchall=True) or []

        if prods:
            logger.info(f"Encontrados {len(prods)} productos. Actualizando atributos RA...")
            # Habilitar TOP en el primero
            db.execute_query(
                f"""UPDATE {schema}.t_producto 
                    SET tiene_ra = TRUE, 
                        tipo_prenda_ra = 'TOP', 
                        modelo_2d_url = 'https://assets.stickpng.com/images/580b57fbd9996e24bc43bf55.png'
                    WHERE id_producto = %s;""",
                (prods[0][0],)
            )
            logger.info(f"-> Producto {prods[0][0]} ({prods[0][1]}): Habilitado como TOP")

            if len(prods) > 1:
                # Habilitar DRESS en el segundo
                db.execute_query(
                    f"""UPDATE {schema}.t_producto 
                        SET tiene_ra = TRUE, 
                            tipo_prenda_ra = 'DRESS', 
                            modelo_2d_url = 'https://assets.stickpng.com/images/580b57fbd9996e24bc43bf42.png'
                        WHERE id_producto = %s;""",
                    (prods[1][0],)
                )
                logger.info(f"-> Producto {prods[1][0]} ({prods[1][1]}): Habilitado como DRESS")

            if len(prods) > 2:
                # Habilitar PANT en el tercero
                db.execute_query(
                    f"""UPDATE {schema}.t_producto 
                        SET tiene_ra = TRUE, 
                            tipo_prenda_ra = 'PANT', 
                            modelo_2d_url = 'https://assets.stickpng.com/images/580b57fbd9996e24bc43bf44.png'
                        WHERE id_producto = %s;""",
                    (prods[2][0],)
                )
                logger.info(f"-> Producto {prods[2][0]} ({prods[2][1]}): Habilitado como PANT")

        if db.conn:
            db.conn.commit()
        logger.info("Migración M14 completada exitosamente.")
    except Exception as e:
        logger.error(f"Error en migración M14: {e}")
        if db.conn:
            db.conn.rollback()
        raise
    finally:
        db.close_connection()

if __name__ == "__main__":
    migrate()
