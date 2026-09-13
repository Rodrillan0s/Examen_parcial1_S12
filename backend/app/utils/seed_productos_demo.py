import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.classes.postgres import PostgreSQL
from app.config import Config
from app.repos import productos_repos

def seed_prendas():
    print("Iniciando seed de prendas de alta costura para Tenant 1...")
    db = PostgreSQL()
    db.create_connection()
    schema = Config.SCHEMA or 'comercio'

    try:
        # Verificar si ya existen productos
        conteo = db.execute_query(f"SELECT COUNT(*) FROM {schema}.t_producto WHERE id_empresa = 1;", fetchone=True)[0]
        if conteo > 0:
            print(f"Ya existen {conteo} productos en el Tenant 1. No se requiere seed.")
            return

        # Categorías activas
        cats = db.execute_query(f"SELECT id_categoria, nombre FROM {schema}.t_categoria WHERE id_empresa = 1 AND activo = TRUE;", fetchall=True)
        cat_map = {c[1].lower(): c[0] for c in cats}
        primer_cat_id = cats[0][0] if cats else 1

        # Tallas activas
        tallas = db.execute_query(f"SELECT id_talla, nombre FROM {schema}.t_talla WHERE id_empresa = 1 AND activo = TRUE;", fetchall=True)
        talla_map = {t[1].upper(): t[0] for t in tallas}

        # Colores activos
        colores = db.execute_query(f"SELECT id_color, nombre FROM {schema}.t_color WHERE id_empresa = 1 AND activo = TRUE;", fetchall=True)
        color_map = {c[1].lower(): c[0] for c in colores}

        prendas = [
            {
                "nombre": "Vestido Sirena de Terciopelo y Encaje",
                "cat": cat_map.get("vestidos de noche", primer_cat_id),
                "precio": 1850.00,
                "codigo": "AUR-01-VES-01",
                "temporada": "Invierno 2026",
                "coleccion": "Cápsula Alta Costura",
                "descripcion": "Vestido de gala corte sirena confeccionado en terciopelo de seda y encaje chantilly artesanal.",
                "tallas": [talla_map.get("S", 2), talla_map.get("M", 3), talla_map.get("L", 4)],
                "colores": [color_map.get("negro azabache", 1), color_map.get("borgoña imperial", 7), color_map.get("azul medianoche", 8)],
                "foto": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=800&q=80"
            },
            {
                "nombre": "Traje Sastre Dos Piezas Lana de Alpaca",
                "cat": cat_map.get("blazers formales", primer_cat_id),
                "precio": 2100.00,
                "codigo": "AUR-01-BLZ-01",
                "temporada": "Otoño 2026",
                "coleccion": "Sastrería Clásica Femenina",
                "descripcion": "Blazer cruzado con hombreras arquitectónicas y pantalón recto de tiro alto confeccionados en 100% alpaca boliviana.",
                "tallas": [talla_map.get("XS", 1), talla_map.get("S", 2), talla_map.get("M", 3), talla_map.get("L", 4)],
                "colores": [color_map.get("negro azabache", 1), color_map.get("beige arena", 4), color_map.get("cacao profundo", 14)],
                "foto": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80"
            },
            {
                "nombre": "Blusa Camisera de Seda Natural Marfil",
                "cat": cat_map.get("tops de seda", primer_cat_id),
                "precio": 680.00,
                "codigo": "AUR-01-TOP-01",
                "temporada": "Permanente",
                "coleccion": "Esenciales de Lujo",
                "descripcion": "Camisa fluida con botones de nácar genuino y puños sastre, caída inmaculada en crepé de seda pura.",
                "tallas": [talla_map.get("S", 2), talla_map.get("M", 3), talla_map.get("L", 4)],
                "colores": [color_map.get("blanco seda", 2), color_map.get("marfil nupcial", 3), color_map.get("rosa empolvado", 5)],
                "foto": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80"
            },
            {
                "nombre": "Abrigo Midi de Cachemira Cruzado",
                "cat": primer_cat_id,
                "precio": 2450.00,
                "codigo": "AUR-01-ABR-01",
                "temporada": "Invierno 2026",
                "coleccion": "Línea Exterior",
                "descripcion": "Abrigo estructurado con cinturón lazo de paño doble faz en lana de cachemira con forro de cupro.",
                "tallas": [talla_map.get("S", 2), talla_map.get("M", 3), talla_map.get("L", 4)],
                "colores": [color_map.get("beige arena", 4), color_map.get("negro azabache", 1), color_map.get("oro champaña", 6)],
                "foto": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80"
            }
        ]

        for p in prendas:
            t_ids = [t for t in p["tallas"] if t]
            c_ids = [c for c in p["colores"] if c]
            id_p = productos_repos.crear_producto(
                id_empresa=1,
                id_categoria=p["cat"],
                nombre=p["nombre"],
                precio=p["precio"],
                descripcion=p["descripcion"],
                codigo_producto=p["codigo"],
                temporada=p["temporada"],
                coleccion=p["coleccion"],
                marca="Aurora Atelier",
                genero="Femenino",
                activo=True
            )
            # Variantes
            if t_ids and c_ids:
                productos_repos.sincronizar_variantes_producto(id_p, t_ids, c_ids, p["precio"])
            # Foto
            productos_repos.agregar_imagen_producto(
                id_producto=id_p,
                imagen_url=p["foto"],
                public_id=f"seed_{id_p}",
                es_principal=True
            )
            print(f"✔ Prenda '{p['nombre']}' creada con {len(t_ids) * len(c_ids)} variantes.")

        print("Seed completado exitosamente.")
    finally:
        db.close_connection()

if __name__ == '__main__':
    seed_prendas()
