import os
import psycopg2
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, '.env'))
load_dotenv(os.path.join(os.path.dirname(base_dir), '.env'))
load_dotenv()

CIUDADES_BOLIVIA = [
    # Santa Cruz
    ("Santa Cruz de la Sierra", "Santa Cruz"),
    ("Montero", "Santa Cruz"),
    ("Warnes", "Santa Cruz"),
    ("Camiri", "Santa Cruz"),
    ("Cotoca", "Santa Cruz"),
    # La Paz
    ("La Paz", "La Paz"),
    ("El Alto", "La Paz"),
    ("Viacha", "La Paz"),
    ("Achacachi", "La Paz"),
    # Cochabamba
    ("Cochabamba", "Cochabamba"),
    ("Quillacollo", "Cochabamba"),
    ("Sacaba", "Cochabamba"),
    ("Colcapirhua", "Cochabamba"),
    # Chuquisaca
    ("Sucre", "Chuquisaca"),
    ("Monteagudo", "Chuquisaca"),
    ("Camargo", "Chuquisaca"),
    # Oruro
    ("Oruro", "Oruro"),
    ("Huanuni", "Oruro"),
    ("Challapata", "Oruro"),
    # Potosí
    ("Potosí", "Potosí"),
    ("Uyuni", "Potosí"),
    ("Villazón", "Potosí"),
    ("Tupiza", "Potosí"),
    # Tarija
    ("Tarija", "Tarija"),
    ("Yacuiba", "Tarija"),
    ("Bermejo", "Tarija"),
    ("Villamontes", "Tarija"),
    # Beni
    ("Trinidad", "Beni"),
    ("Riberalta", "Beni"),
    ("Guayaramerín", "Beni"),
    ("San Borja", "Beni"),
    # Pando
    ("Cobija", "Pando"),
    ("Porvenir", "Pando"),
    ("Puerto Rico", "Pando"),
]

def migrar():
    db_name = os.getenv("DB_NAME", "obras")
    db_user = os.getenv("DB_USER", "devpoppy")
    db_pass = os.getenv("DB_PASSWORD", "Ip12@10203040")
    db_host = os.getenv("DB_HOST", "147.15.29.190")
    db_port = os.getenv("DB_PORT", "5433")

    print(f"Conectando a PostgreSQL {db_host}:{db_port}/{db_name} como {db_user}...")
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
        print("1. Verificando tabla comercio.t_ciudad...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comercio.t_ciudad (
                id_ciudad SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                departamento VARCHAR(100) NOT NULL,
                estado BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Agregar constraint de unicidad para evitar duplicados de ciudad en el mismo departamento
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_ciudad_nombre_depto
            ON comercio.t_ciudad (LOWER(TRIM(nombre)), LOWER(TRIM(departamento)));
        """)

        print("2. Poblando ciudades base de Bolivia...")
        insertadas = 0
        for nombre, depto in CIUDADES_BOLIVIA:
            cur.execute("""
                INSERT INTO comercio.t_ciudad (nombre, departamento, estado)
                VALUES (%s, %s, TRUE)
                ON CONFLICT (LOWER(TRIM(nombre)), LOWER(TRIM(departamento))) DO NOTHING;
            """, (nombre, depto))
            if cur.rowcount > 0:
                insertadas += 1

        print(f"   Ciudades insertadas nuevas: {insertadas}")

        print("3. Ajustando columnas y restricciones en comercio.t_sucursal...")
        # Asegurar columnas necesarias
        cur.execute("""
            ALTER TABLE comercio.t_sucursal
            ADD COLUMN IF NOT EXISTS telefono VARCHAR(50);
        """)
        cur.execute("""
            ALTER TABLE comercio.t_sucursal
            ADD COLUMN IF NOT EXISTS estado BOOLEAN DEFAULT TRUE;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_sucursal
            ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;
        """)
        cur.execute("""
            ALTER TABLE comercio.t_sucursal
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """)

        # Si hay sucursal 1 huérfana de empresa y ciudad, vincularla a Empresa 1 y Santa Cruz de la Sierra
        cur.execute("""
            SELECT id_ciudad FROM comercio.t_ciudad 
            WHERE LOWER(nombre) LIKE '%santa cruz de la sierra%' LIMIT 1;
        """)
        row_scz = cur.fetchone()
        id_scz = row_scz[0] if row_scz else 1

        cur.execute("""
            UPDATE comercio.t_sucursal
            SET id_empresa = 1,
                id_ciudad = %s,
                telefono = COALESCE(telefono, '70011223'),
                activo = TRUE,
                estado = TRUE
            WHERE id_sucursal = 1 AND (id_empresa IS NULL OR id_ciudad IS NULL);
        """, (id_scz,))

        print("Migración y seeding de Ciudades y Sucursales finalizados con éxito.")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrar()
