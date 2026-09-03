from app.classes.postgres import PostgreSQL
from app.config import Config

# --- OBTENER PERMISOS EFECTIVOS DEL USUARIO (DISTINCT p.codigo) ---
def obtener_permisos_efectivos_usuario(id_usuario: int) -> list:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            SELECT DISTINCT p.codigo
            FROM {schema}.t_usuario_rol ur
            INNER JOIN {schema}.t_rol_permiso rp ON rp.id_rol = ur.id_rol
            INNER JOIN {schema}.t_permiso p ON p.id_permiso = rp.id_permiso
            INNER JOIN {schema}.t_rol r ON r.id_rol = ur.id_rol
            WHERE ur.id_usuario = %s AND p.activo = TRUE AND r.activo = TRUE
            ORDER BY p.codigo ASC;
        """
        res = db.execute_query(query, (id_usuario,), fetchall=True)
        if not res:
            return []
        return [r[0] for r in res]
    finally:
        db.close_connection()


# --- OBTENER ROLES ASIGNADOS AL USUARIO ---
def obtener_roles_usuario(id_usuario: int) -> list:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            SELECT r.id_rol, r.nombre, r.descripcion, r.activo
            FROM {schema}.t_usuario_rol ur
            INNER JOIN {schema}.t_rol r ON r.id_rol = ur.id_rol
            WHERE ur.id_usuario = %s AND r.activo = TRUE
            ORDER BY r.nombre ASC;
        """
        res = db.execute_query(query, (id_usuario,), fetchall=True)
        if not res:
            return []
        return [{"id_rol": r[0], "nombre": r[1], "descripcion": r[2], "activo": r[3]} for r in res]
    finally:
        db.close_connection()


# --- OBTENER SUCURSALES AUTORIZADAS DEL USUARIO ---
def obtener_sucursales_usuario(id_usuario: int) -> list:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            SELECT us.id_sucursal
            FROM {schema}.t_usuario_sucursal us
            INNER JOIN {schema}.t_sucursal s ON s.id_sucursal = us.id_sucursal
            WHERE us.id_usuario = %s AND s.activo = TRUE;
        """
        res = db.execute_query(query, (id_usuario,), fetchall=True)
        if not res:
            return []
        return [r[0] for r in res]
    finally:
        db.close_connection()


# --- CRUD ROLES ---
def obtener_todos_los_roles(solo_activos: bool = False) -> list:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        where_clause = "WHERE activo = TRUE" if solo_activos else ""
        query = f"""
            SELECT id_rol, nombre, descripcion, activo, created_at
            FROM {schema}.t_rol
            {where_clause}
            ORDER BY id_rol ASC;
        """
        resultados = db.execute_query(query, fetchall=True)
        roles = []
        if resultados:
            for r in resultados:
                roles.append({
                    "id_rol": r[0],
                    "nombre": r[1],
                    "descripcion": r[2],
                    "activo": r[3],
                    "created_at": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None
                })
        return roles
    finally:
        db.close_connection()

def crear_rol(nombre: str, descripcion: str) -> int:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            INSERT INTO {schema}.t_rol (nombre, descripcion, activo)
            VALUES (%s, %s, TRUE)
            RETURNING id_rol;
        """
        res = db.execute_query(query, (nombre, descripcion), fetchone=True, commit=True)
        return res[0] if res else None
    finally:
        db.close_connection()

def actualizar_rol(id_rol: int, nombre: str, descripcion: str, activo: bool = True) -> bool:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            UPDATE {schema}.t_rol
            SET nombre = %s, descripcion = %s, activo = %s
            WHERE id_rol = %s;
        """
        filas = db.execute_query(query, (nombre, descripcion, activo, id_rol), commit=True)
        return filas > 0
    finally:
        db.close_connection()

def desactivar_rol(id_rol: int) -> bool:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"UPDATE {schema}.t_rol SET activo = FALSE WHERE id_rol = %s;"
        filas = db.execute_query(query, (id_rol,), commit=True)
        return filas > 0
    finally:
        db.close_connection()


# --- CRUD PERMISOS ---
def obtener_todos_los_permisos() -> list:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            SELECT id_permiso, codigo, nombre, descripcion, modulo, activo
            FROM {schema}.t_permiso
            ORDER BY modulo ASC, codigo ASC;
        """
        resultados = db.execute_query(query, fetchall=True)
        permisos = []
        if resultados:
            for r in resultados:
                permisos.append({
                    "id_permiso": r[0],
                    "codigo": r[1],
                    "nombre": r[2],
                    "descripcion": r[3],
                    "modulo": r[4],
                    "activo": r[5]
                })
        return permisos
    finally:
        db.close_connection()

def crear_permiso(codigo: str, nombre: str, descripcion: str, modulo: str) -> int:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            INSERT INTO {schema}.t_permiso (codigo, nombre, descripcion, modulo, activo)
            VALUES (%s, %s, %s, %s, TRUE)
            RETURNING id_permiso;
        """
        res = db.execute_query(query, (codigo, nombre, descripcion, modulo), fetchone=True, commit=True)
        return res[0] if res else None
    finally:
        db.close_connection()


# --- ASIGNACIÓN DE PERMISOS A ROL ---
def obtener_permisos_de_rol(id_rol: int) -> list:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            SELECT p.id_permiso, p.codigo, p.nombre, p.modulo
            FROM {schema}.t_rol_permiso rp
            INNER JOIN {schema}.t_permiso p ON p.id_permiso = rp.id_permiso
            WHERE rp.id_rol = %s AND p.activo = TRUE
            ORDER BY p.codigo ASC;
        """
        res = db.execute_query(query, (id_rol,), fetchall=True)
        if not res:
            return []
        return [{"id_permiso": r[0], "codigo": r[1], "nombre": r[2], "modulo": r[3]} for r in res]
    finally:
        db.close_connection()

def asignar_permisos_a_rol(id_rol: int, ids_permisos: list) -> bool:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        # 1. Eliminar asignaciones actuales del rol
        query_delete = f"DELETE FROM {schema}.t_rol_permiso WHERE id_rol = %s;"
        db.execute_query(query_delete, (id_rol,))

        # 2. Insertar nuevas asignaciones
        if ids_permisos:
            for id_permiso in ids_permisos:
                query_insert = f"""
                    INSERT INTO {schema}.t_rol_permiso (id_rol, id_permiso)
                    SELECT %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM {schema}.t_rol_permiso WHERE id_rol = %s AND id_permiso = %s
                    );
                """
                db.execute_query(query_insert, (id_rol, id_permiso, id_rol, id_permiso))

        if db.conn:
            db.conn.commit()
        return True
    except Exception as e:
        if db.conn:
            db.conn.rollback()
        raise ValueError(f"Error al asignar permisos al rol: {str(e)}")
    finally:
        db.close_connection()


# --- ASIGNACIÓN DE ROLES A USUARIO ---
def asignar_roles_a_usuario(id_usuario: int, ids_roles: list) -> bool:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        # 1. Eliminar roles actuales del usuario
        query_delete = f"DELETE FROM {schema}.t_usuario_rol WHERE id_usuario = %s;"
        db.execute_query(query_delete, (id_usuario,))

        # 2. Insertar nuevos roles
        if ids_roles:
            for id_rol in ids_roles:
                query_insert = f"""
                    INSERT INTO {schema}.t_usuario_rol (id_usuario, id_rol)
                    SELECT %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM {schema}.t_usuario_rol WHERE id_usuario = %s AND id_rol = %s
                    );
                """
                db.execute_query(query_insert, (id_usuario, id_rol, id_usuario, id_rol))

        if db.conn:
            db.conn.commit()
        return True
    except Exception as e:
        if db.conn:
            db.conn.rollback()
        raise ValueError(f"Error al asignar roles al usuario: {str(e)}")
    finally:
        db.close_connection()


# --- ASIGNACIÓN DE SUCURSALES A USUARIO ---
def asignar_sucursales_a_usuario(id_usuario: int, ids_sucursales: list) -> bool:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        # 1. Eliminar sucursales actuales del usuario
        query_delete = f"DELETE FROM {schema}.t_usuario_sucursal WHERE id_usuario = %s;"
        db.execute_query(query_delete, (id_usuario,))

        # 2. Insertar nuevas sucursales
        if ids_sucursales:
            for id_sucursal in ids_sucursales:
                query_insert = f"""
                    INSERT INTO {schema}.t_usuario_sucursal (id_usuario, id_sucursal)
                    SELECT %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM {schema}.t_usuario_sucursal WHERE id_usuario = %s AND id_sucursal = %s
                    );
                """
                db.execute_query(query_insert, (id_usuario, id_sucursal, id_usuario, id_sucursal))

        if db.conn:
            db.conn.commit()
        return True
    except Exception as e:
        if db.conn:
            db.conn.rollback()
        raise ValueError(f"Error al asignar sucursales al usuario: {str(e)}")
    finally:
        db.close_connection()


# --- CONSULTA DE SUCURSALES ---
def obtener_todas_las_sucursales() -> list:
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"SELECT id_sucursal, nombre, direccion, activo FROM {schema}.t_sucursal WHERE activo = TRUE ORDER BY id_sucursal ASC;"
        res = db.execute_query(query, fetchall=True)
        if not res:
            return []
        return [{"id_sucursal": r[0], "nombre": r[1], "direccion": r[2], "activo": r[3]} for r in res]
    finally:
        db.close_connection()
