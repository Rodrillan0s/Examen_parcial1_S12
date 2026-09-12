import os
import psycopg2
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, '.env'))
load_dotenv(os.path.join(os.path.dirname(base_dir), '.env'))
load_dotenv()

PERMISOS_TALLAS_COLORES = [
    ("tallas.ver", "Ver catálogo de tallas", "Consultar tallas de prendas de vestir", "tallas"),
    ("tallas.crear", "Crear talla", "Registrar nuevas tallas de prendas", "tallas"),
    ("tallas.editar", "Editar talla", "Modificar nombres y descripciones de tallas", "tallas"),
    ("tallas.desactivar", "Activar/Desactivar talla", "Cambiar estado operativo de tallas", "tallas"),
    ("colores.ver", "Ver catálogo de colores", "Consultar gama cromática y códigos HEX", "colores"),
    ("colores.crear", "Crear color", "Registrar nuevos colores y tonalidades textiles", "colores"),
    ("colores.editar", "Editar color", "Modificar nombre y código HEX de colores", "colores"),
    ("colores.desactivar", "Activar/Desactivar color", "Cambiar estado operativo de colores", "colores"),
]

TALLAS_MUJER_BASE = [
    ("XS", "Extra Pequeña (Busto 80-84 cm, Cintura 60-64 cm)"),
    ("S", "Pequeña (Busto 84-88 cm, Cintura 64-68 cm)"),
    ("M", "Mediana (Busto 88-92 cm, Cintura 68-72 cm)"),
    ("L", "Grande (Busto 92-96 cm, Cintura 72-76 cm)"),
    ("XL", "Extra Grande (Busto 96-102 cm, Cintura 76-82 cm)"),
    ("XXL", "Doble Extra Grande (Busto 102-110 cm, Cintura 82-90 cm)"),
    ("34", "Talla Europea 34 / Cintura Femenina"),
    ("36", "Talla Europea 36 / Pantalones y Faldas"),
    ("38", "Talla Europea 38 / Estándar Femenino"),
    ("40", "Talla Europea 40 / Corte Clásico"),
    ("42", "Talla Europea 42 / Confort Femenino"),
    ("44", "Talla Europea 44 / Silueta Curvy"),
]

COLORES_MODA_BASE = [
    ("Negro Azabache", "#111111"),
    ("Blanco Seda", "#FDFBF7"),
    ("Marfil Perla", "#F5F2EB"),
    ("Rosa Empolvado", "#E8C5C8"),
    ("Champagne Oro", "#F7E7CE"),
    ("Borgoña Profundo", "#5B1425"),
    ("Rojo Rubí", "#9B111E"),
    ("Verde Esmeralda", "#097969"),
    ("Verde Salvia", "#9DC183"),
    ("Azul Noche", "#191970"),
    ("Azul Celeste Cielo", "#87CEEB"),
    ("Terracota Cálido", "#C04000"),
    ("Camel Clásico", "#C19A6B"),
    ("Gris Perla", "#D3D3D3"),
    ("Lila Lavanda", "#BDB0D0"),
]

def migrar():
    db_name = os.getenv("DB_NAME", "obras")
    db_user = os.getenv("DB_USER", "devpoppy")
    db_pass = os.getenv("DB_PASSWORD", "Ip12@10203040")
    db_host = os.getenv("DB_HOST", "147.15.29.190")
    db_port = os.getenv("DB_PORT", "5433")

    print(f"Conectando a {db_host}:{db_port}/{db_name} como {db_user}...")
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port
    )
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("1. Adaptando columnas y restricciones en comercio.t_talla...")
        cur.execute("""
            ALTER TABLE comercio.t_talla
            ADD COLUMN IF NOT EXISTS id_empresa INTEGER REFERENCES comercio.empresa(id_empresa) ON DELETE CASCADE;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_talla
            ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_talla
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_talla
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_talla_nombre_tenant
            ON comercio.t_talla (LOWER(TRIM(nombre)), COALESCE(id_empresa, 0));
        """)

        print("2. Adaptando columnas y restricciones en comercio.t_color...")
        cur.execute("""
            ALTER TABLE comercio.t_color
            ADD COLUMN IF NOT EXISTS id_empresa INTEGER REFERENCES comercio.empresa(id_empresa) ON DELETE CASCADE;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_color
            ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_color
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_color
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_color_nombre_tenant
            ON comercio.t_color (LOWER(TRIM(nombre)), COALESCE(id_empresa, 0));
        """)

        print("3. Registrando permisos de Tallas y Colores...")
        for cod, nom, desc, mod in PERMISOS_TALLAS_COLORES:
            cur.execute("SELECT id_permiso FROM comercio.t_permiso WHERE codigo = %s;", (cod,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO comercio.t_permiso (codigo, nombre, descripcion, modulo, activo)
                    VALUES (%s, %s, %s, %s, TRUE);
                """, (cod, nom, desc, mod))

        print("4. Mapeando permisos a roles administrativos (ADMINISTRADOR, ADMINISTRADOR_TIENDA, ENCARGADO)...")
        for r_id in [1, 3, 4]:
            cur.execute("""
                INSERT INTO comercio.t_rol_permiso (id_rol, id_permiso)
                SELECT %s, p.id_permiso
                FROM comercio.t_permiso p
                WHERE p.modulo IN ('tallas', 'colores')
                AND NOT EXISTS (
                    SELECT 1 FROM comercio.t_rol_permiso rp
                    WHERE rp.id_rol = %s AND rp.id_permiso = p.id_permiso
                );
            """, (r_id, r_id))

        print("5. Obteniendo id_empresa por defecto (Tenant matriz)...")
        cur.execute("SELECT id_empresa FROM comercio.empresa ORDER BY id_empresa ASC LIMIT 1;")
        row_emp = cur.fetchone()
        default_empresa_id = row_emp[0] if row_emp else 1

        print("6. Sembrando Tallas de prendas de mujer iniciales...")
        tallas_agregadas = 0
        for nombre, desc in TALLAS_MUJER_BASE:
            cur.execute("""
                INSERT INTO comercio.t_talla (nombre, descripcion, id_empresa, activo, estado)
                VALUES (%s, %s, %s, TRUE, TRUE)
                ON CONFLICT (LOWER(TRIM(nombre)), COALESCE(id_empresa, 0)) DO NOTHING;
            """, (nombre, desc, default_empresa_id))
            if cur.rowcount > 0:
                tallas_agregadas += 1
        print(f"   Tallas insertadas: {tallas_agregadas}")

        print("7. Sembrando Colores de moda femenina iniciales...")
        colores_agregados = 0
        for nombre, hex_code in COLORES_MODA_BASE:
            cur.execute("""
                INSERT INTO comercio.t_color (nombre, codigo_hex, id_empresa, activo, estado)
                VALUES (%s, %s, %s, TRUE, TRUE)
                ON CONFLICT (LOWER(TRIM(nombre)), COALESCE(id_empresa, 0)) DO NOTHING;
            """, (nombre, hex_code, default_empresa_id))
            if cur.rowcount > 0:
                colores_agregados += 1
        print(f"   Colores insertados: {colores_agregados}")

        print("Migración de Tallas y Colores finalizada exitosamente.")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrar()
