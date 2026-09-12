import os
import psycopg2
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, '.env'))
load_dotenv(os.path.join(os.path.dirname(base_dir), '.env'))
load_dotenv()

ROLES_JERARQUIA = [
    (1, "ADMINISTRADOR", "SuperAdministrador / Administrador global con autoridad máxima sobre la plataforma.", True),
    (2, "CLIENTE", "Cliente comprador del ecosistema e-commerce.", True),
    (3, "ADMINISTRADOR_TIENDA", "Administrador de tienda (Tenant) con autoridad sobre los usuarios de su empresa.", True),
    (4, "ENCARGADO", "Encargado operativo de sucursal con permisos delegados de tienda.", True),
    (5, "EMPLEADO", "Empleado operativo de sucursal o cajero con permisos básicos de venta.", True),
    (6, "PROVEEDOR", "Proveedor externo de prendas e insumos de catálogo.", True),
]

PERMISOS_ADICIONALES = [
    ("empresas.ver", "Ver empresas/tenants", "Gestión y consulta de cadenas de tiendas", "empresas"),
    ("empresas.crear", "Registrar empresa/tenant", "Crear nuevas tiendas matrices en la plataforma", "empresas"),
    ("empresas.editar", "Editar empresa/tenant", "Modificar datos fiscales y estado de tiendas", "empresas"),
    ("empresas.eliminar", "Eliminar empresa/tenant", "Desactivar o eliminar tiendas matrices", "empresas"),
    ("ciudades.ver", "Ver catálogo de ciudades", "Consultar ciudades y departamentos de Bolivia", "ciudades"),
    ("ciudades.crear", "Crear ciudad", "Registrar nuevas ciudades de referencia", "ciudades"),
    ("ciudades.editar", "Editar ciudad", "Modificar ciudades y estado", "ciudades"),
    ("ciudades.desactivar", "Desactivar ciudad", "Desactivar ciudades del catálogo", "ciudades"),
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
        print("1. Creando tabla comercio.t_usuario_permiso para permisos directos...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comercio.t_usuario_permiso (
                id_usuario_permiso SERIAL PRIMARY KEY,
                id_usuario INTEGER NOT NULL REFERENCES comercio.t_usuario(id_usuario) ON DELETE CASCADE,
                id_permiso INTEGER NOT NULL REFERENCES comercio.t_permiso(id_permiso) ON DELETE CASCADE,
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_usuario_permiso UNIQUE (id_usuario, id_permiso)
            );
        """)

        print("2. Verificando roles jerárquicos en comercio.t_rol...")
        for id_r, nombre, desc, activo in ROLES_JERARQUIA:
            # Comprobar si existe por nombre o id
            cur.execute("""
                SELECT id_rol FROM comercio.t_rol 
                WHERE id_rol = %s OR UPPER(nombre) = UPPER(%s);
            """, (id_r, nombre))
            row = cur.fetchone()
            if row:
                cur.execute("""
                    UPDATE comercio.t_rol 
                    SET nombre = %s, descripcion = %s, activo = %s
                    WHERE id_rol = %s;
                """, (nombre, desc, activo, row[0]))
            else:
                cur.execute("""
                    INSERT INTO comercio.t_rol (id_rol, nombre, descripcion, activo)
                    VALUES (%s, %s, %s, %s);
                """, (id_r, nombre, desc, activo))

        print("3. Registrando permisos adicionales en comercio.t_permiso...")
        for cod, nom, desc, mod in PERMISOS_ADICIONALES:
            cur.execute("""
                SELECT id_permiso FROM comercio.t_permiso WHERE codigo = %s;
            """, (cod,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO comercio.t_permiso (codigo, nombre, descripcion, modulo, activo)
                    VALUES (%s, %s, %s, %s, TRUE);
                """, (cod, nom, desc, mod))

        print("4. Mapeando permisos clave al rol 1 (ADMINISTRADOR)...")
        cur.execute("""
            INSERT INTO comercio.t_rol_permiso (id_rol, id_permiso)
            SELECT 1, p.id_permiso
            FROM comercio.t_permiso p
            WHERE NOT EXISTS (
                SELECT 1 FROM comercio.t_rol_permiso rp 
                WHERE rp.id_rol = 1 AND rp.id_permiso = p.id_permiso
            );
        """)

        print("Migración de Permisos Directos y Roles completada exitosamente.")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrar()
