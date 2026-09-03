from app.classes.postgres import PostgreSQL
from app.config import Config

# --- LEER USUARIOS ---
def obtener_todos_los_usuarios():
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            SELECT 
                u.id_usuario, u.username, u.correo, u.nombre, u.apellido,
                u.telefono, u.estado, u.id_empresa,
                r.nombre AS nombre_rol, r.id_rol
            FROM {schema}.t_usuario u
            LEFT JOIN {schema}.t_usuario_rol ur ON ur.id_usuario = u.id_usuario
            LEFT JOIN {schema}.t_rol r ON r.id_rol = ur.id_rol
            ORDER BY u.id_usuario ASC;
        """
        resultados = db.execute_query(query, fetchall=True)
        
        usuarios = []
        if resultados:
            for r in resultados:
                usuarios.append({
                    "nro_usuario": r[0],
                    "id_usuario": r[0],
                    "nombre_usuario": r[1],
                    "username": r[1],
                    "correo": r[2],
                    "nombre": r[3],
                    "apellido": r[4],
                    "nombre_completo": f"{r[3] or ''} {r[4] or ''}".strip(),
                    "telefono": r[5],
                    "estado": "ACTIVO" if r[6] else "INACTIVO",
                    "id_empresa": r[7],
                    "nombre_rol": r[8] or "CLIENTE",
                    "id_rol": r[9] or 2,
                    "nro_rol": r[9] or 2
                })
        return usuarios
    finally:
        db.close_connection()

def obtener_usuarios_por_empresa(id_empresa: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            SELECT 
                u.id_usuario, u.username, u.correo, u.nombre, u.apellido,
                u.telefono, u.estado, u.id_empresa,
                r.nombre AS nombre_rol, r.id_rol
            FROM {schema}.t_usuario u
            LEFT JOIN {schema}.t_usuario_rol ur ON ur.id_usuario = u.id_usuario
            LEFT JOIN {schema}.t_rol r ON r.id_rol = ur.id_rol
            WHERE u.id_empresa = %s
            ORDER BY u.id_usuario ASC;
        """
        resultados = db.execute_query(query, (id_empresa,), fetchall=True)
        
        usuarios = []
        if resultados:
            for r in resultados:
                usuarios.append({
                    "nro_usuario": r[0],
                    "id_usuario": r[0],
                    "nombre_usuario": r[1],
                    "username": r[1],
                    "correo": r[2],
                    "nombre": r[3],
                    "apellido": r[4],
                    "nombre_completo": f"{r[3] or ''} {r[4] or ''}".strip(),
                    "telefono": r[5],
                    "estado": "ACTIVO" if r[6] else "INACTIVO",
                    "id_empresa": r[7],
                    "nombre_rol": r[8] or "CLIENTE",
                    "id_rol": r[9] or 2,
                    "nro_rol": r[9] or 2
                })
        return usuarios
    finally:
        db.close_connection()

def obtener_usuario_por_id(id_usuario: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"""
            SELECT 
                u.id_usuario, u.username, u.correo, u.nombre, u.apellido,
                u.telefono, u.estado, u.id_empresa,
                r.nombre AS nombre_rol, r.id_rol
            FROM {schema}.t_usuario u
            LEFT JOIN {schema}.t_usuario_rol ur ON ur.id_usuario = u.id_usuario
            LEFT JOIN {schema}.t_rol r ON r.id_rol = ur.id_rol
            WHERE u.id_usuario = %s;
        """
        r = db.execute_query(query, (id_usuario,), fetchone=True)
        
        if r:
            return {
                "nro_usuario": r[0],
                "id_usuario": r[0],
                "nombre_usuario": r[1],
                "username": r[1],
                "correo": r[2],
                "nombre": r[3],
                "apellido": r[4],
                "nombre_completo": f"{r[3] or ''} {r[4] or ''}".strip(),
                "telefono": r[5],
                "estado": "ACTIVO" if r[6] else "INACTIVO",
                "id_empresa": r[7],
                "nombre_rol": r[8] or "CLIENTE",
                "id_rol": r[9] or 2,
                "nro_rol": r[9] or 2
            }
        return None
    finally:
        db.close_connection()

# --- CREAR USUARIO ---
def crear_usuario_db(datos_persona, datos_usuario):
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query_usuario = f"""
            INSERT INTO {schema}.t_usuario (username, correo, password_hash, nombre, apellido, telefono, estado, id_empresa)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE, %s)
            RETURNING id_usuario;
        """
        params = (
            datos_usuario.get('username') or datos_usuario.get('nombre_usuario'),
            datos_usuario.get('correo'),
            datos_usuario.get('password_hash'),
            datos_usuario.get('nombre'),
            datos_usuario.get('apellido'),
            datos_usuario.get('telefono'),
            datos_usuario.get('id_empresa')
        )
        resultado = db.execute_query(query_usuario, params, fetchone=True, commit=True)
        id_user = resultado[0] if resultado else None
        
        # Asignar rol por defecto si viene en datos
        id_rol = datos_usuario.get('id_rol') or datos_usuario.get('nro_rol')
        if id_user and id_rol:
            from app.repos import rbac_repos
            rbac_repos.asignar_roles_a_usuario(id_user, [id_rol])
            
        return id_user
    finally:
        db.close_connection()

# --- ACTUALIZAR USUARIO ---
def actualizar_usuario_db(nro_usuario, ci, datos_persona, datos_usuario, cambiar_password=False):
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        if cambiar_password:
            query = f"""
                UPDATE {schema}.t_usuario
                SET username = %s, correo = %s, password_hash = %s, nombre = %s, apellido = %s, telefono = %s, id_empresa = %s
                WHERE id_usuario = %s;
            """
            params = (
                datos_usuario.get('username'),
                datos_usuario.get('correo'),
                datos_usuario.get('password_hash'),
                datos_usuario.get('nombre'),
                datos_usuario.get('apellido'),
                datos_usuario.get('telefono'),
                datos_usuario.get('id_empresa'),
                nro_usuario
            )
        else:
            query = f"""
                UPDATE {schema}.t_usuario
                SET username = %s, correo = %s, nombre = %s, apellido = %s, telefono = %s, id_empresa = %s
                WHERE id_usuario = %s;
            """
            params = (
                datos_usuario.get('username'),
                datos_usuario.get('correo'),
                datos_usuario.get('nombre'),
                datos_usuario.get('apellido'),
                datos_usuario.get('telefono'),
                datos_usuario.get('id_empresa'),
                nro_usuario
            )
        
        db.execute_query(query, params, commit=True)
        
        id_rol = datos_usuario.get('id_rol') or datos_usuario.get('nro_rol')
        if id_rol:
            from app.repos import rbac_repos
            rbac_repos.asignar_roles_a_usuario(nro_usuario, [id_rol])
            
        return True
    finally:
        db.close_connection()

# --- ELIMINAR USUARIO ---
def eliminar_usuario_db(nro_usuario: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = Config.SCHEMA or 'comercio'
        query = f"UPDATE {schema}.t_usuario SET estado = FALSE WHERE id_usuario = %s;"
        db.execute_query(query, (nro_usuario,), commit=True)
        return True
    finally:
        db.close_connection()