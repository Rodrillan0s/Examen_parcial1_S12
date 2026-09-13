import os
import psycopg2
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, '.env'))
load_dotenv(os.path.join(os.path.dirname(base_dir), '.env'))
load_dotenv()

PERMISOS_CATEGORIAS = [
    ("categorias.ver", "Ver categorías", "Consultar catálogo de categorías de prendas", "categorias"),
    ("categorias.crear", "Crear categoría", "Registrar nuevas categorías de prendas", "categorias"),
    ("categorias.editar", "Editar categoría", "Modificar datos y fotos de categorías", "categorias"),
    ("categorias.desactivar", "Activar/Desactivar categoría", "Activar o desactivar categorías de ropa", "categorias"),
]

CATEGORIAS_BASE = [
    {
        "nombre": "Sastrería & Sacos",
        "descripcion": "Blazers estructurados, trajes formales y cortes de sastrería italiana.",
        "padre": None,
        "subcategorias": ["Blazers Formales", "Chalecos Clásicos", "Pantalones de Vestir"]
    },
    {
        "nombre": "Alta Costura & Gala",
        "descripcion": "Vestidos de noche, textiles premium, bordados finos y piezas exclusivas.",
        "padre": None,
        "subcategorias": ["Vestidos de Noche", "Piezas de Pasarela", "Accesorios de Gala"]
    },
    {
        "nombre": "Esenciales & Casual Chic",
        "descripcion": "Prendas de lujo cotidiano en algodones pima, lino y sedas naturales.",
        "padre": None,
        "subcategorias": ["Camisas de Lino", "Tops de Seda", "Denim Premium"]
    },
    {
        "nombre": "Calzado & Marroquinería",
        "descripcion": "Zapatos artesanales de piel genuina, bolsos y marroquinería fina.",
        "padre": None,
        "subcategorias": ["Zapatos de Piel", "Bolsos de Cuero", "Cinturones Artesanales"]
    }
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
        print("1. Creando o adaptando tabla comercio.t_categoria...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comercio.t_categoria (
                id_categoria SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                estado BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Añadir columnas faltantes
        cur.execute("""
            ALTER TABLE comercio.t_categoria
            ADD COLUMN IF NOT EXISTS id_padre INTEGER REFERENCES comercio.t_categoria(id_categoria) ON DELETE SET NULL;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_categoria
            ADD COLUMN IF NOT EXISTS id_empresa INTEGER REFERENCES comercio.empresa(id_empresa) ON DELETE CASCADE;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_categoria
            ADD COLUMN IF NOT EXISTS imagen_url VARCHAR(500);
        """)
        cur.execute("""
            ALTER TABLE comercio.t_categoria
            ADD COLUMN IF NOT EXISTS imagen_public_id VARCHAR(255);
        """)
        cur.execute("""
            ALTER TABLE comercio.t_categoria
            ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_categoria
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """)

        print("2. Creando índice único por Tenant y nombre...")
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_categoria_nombre_tenant
            ON comercio.t_categoria (LOWER(TRIM(nombre)), COALESCE(id_empresa, 0));
        """)

        print("3. Registrando permisos de categorías en comercio.t_permiso...")
        for cod, nom, desc, mod in PERMISOS_CATEGORIAS:
            cur.execute("""
                SELECT id_permiso FROM comercio.t_permiso WHERE codigo = %s;
            """, (cod,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO comercio.t_permiso (codigo, nombre, descripcion, modulo, activo)
                    VALUES (%s, %s, %s, %s, TRUE);
                """, (cod, nom, desc, mod))

        print("4. Asignando permisos a roles administrativos (ADMINISTRADOR y ADMINISTRADOR_TIENDA)...")
        # Rol 1: ADMINISTRADOR, Rol 3: ADMINISTRADOR_TIENDA, Rol 4: ENCARGADO
        for r_id in [1, 3, 4]:
            cur.execute("""
                INSERT INTO comercio.t_rol_permiso (id_rol, id_permiso)
                SELECT %s, p.id_permiso
                FROM comercio.t_permiso p
                WHERE p.modulo = 'categorias'
                AND NOT EXISTS (
                    SELECT 1 FROM comercio.t_rol_permiso rp
                    WHERE rp.id_rol = %s AND rp.id_permiso = p.id_permiso
                );
            """, (r_id, r_id))

        print("5. Obteniendo id_empresa por defecto (Tenant matriz)...")
        cur.execute("SELECT id_empresa FROM comercio.empresa ORDER BY id_empresa ASC LIMIT 1;")
        row_emp = cur.fetchone()
        default_empresa_id = row_emp[0] if row_emp else 1

        print("6. Verificando categorías existentes...")
        cur.execute("SELECT COUNT(*) FROM comercio.t_categoria;")
        count_cat = cur.fetchone()[0]

        if count_cat == 0:
            print(f"Sembrando categorías base de moda para el Tenant {default_empresa_id}...")
            for cat in CATEGORIAS_BASE:
                cur.execute("""
                    INSERT INTO comercio.t_categoria (nombre, descripcion, id_padre, id_empresa, estado, activo)
                    VALUES (%s, %s, NULL, %s, TRUE, TRUE)
                    RETURNING id_categoria;
                """, (cat["nombre"], cat["descripcion"], default_empresa_id))
                padre_id = cur.fetchone()[0]

                for sub in cat["subcategorias"]:
                    cur.execute("""
                        INSERT INTO comercio.t_categoria (nombre, descripcion, id_padre, id_empresa, estado, activo)
                        VALUES (%s, %s, %s, %s, TRUE, TRUE)
                        ON CONFLICT (LOWER(TRIM(nombre)), COALESCE(id_empresa, 0)) DO NOTHING;
                    """, (sub, f"Subcategoría de {cat['nombre']}", padre_id, default_empresa_id))
            print("Categorías sembradas exitosamente.")
        else:
            print(f"La tabla ya contiene {count_cat} categorías.")

        print("Migración de Categorías concluida satisfactoriamente.")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrar()
