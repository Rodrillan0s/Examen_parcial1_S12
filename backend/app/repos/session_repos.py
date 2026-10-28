"""Current authorization state; JWT supplies identity, never current authority."""
from app.classes.postgres import PostgreSQL
from app.config import Config


def obtener_contexto_actual(id_usuario):
    db = PostgreSQL()
    db.create_connection()
    try:
        if db.conn is None:
            from fastapi import HTTPException
            raise HTTPException(503, detail='No se pudo verificar la sesión. Intente nuevamente.')
        s = Config.SCHEMA or 'comercio'
        row = db.execute_query(f'''
            SELECT u.id_usuario,u.id_empresa,u.estado,(SELECT r.id_rol FROM {s}.t_usuario_rol ur JOIN {s}.t_rol r USING(id_rol)
                    WHERE ur.id_usuario=u.id_usuario AND r.activo ORDER BY (r.id_rol=u.id_rol) DESC,r.id_rol LIMIT 1),e.estado,
                ARRAY(SELECT r.nombre FROM {s}.t_usuario_rol ur JOIN {s}.t_rol r USING(id_rol)
                      WHERE ur.id_usuario=u.id_usuario AND r.activo ORDER BY r.id_rol),
                ARRAY(SELECT us.id_sucursal FROM {s}.t_usuario_sucursal us JOIN {s}.t_sucursal b USING(id_sucursal)
                      WHERE us.id_usuario=u.id_usuario AND b.id_empresa=u.id_empresa AND b.activo ORDER BY us.id_sucursal),
                u.username,u.nombre,u.apellido,e.nombre_empresa
            FROM {s}.t_usuario u LEFT JOIN {s}.empresa e USING(id_empresa)
            WHERE u.id_usuario=%s
        ''', (id_usuario,), fetchone=True)
        if not row:
            return None
        return dict(zip(('id_usuario','id_empresa','activo','id_rol','estado_empresa','roles','sucursales',
                         'username','nombre','apellido','nombre_empresa'), row))
    finally:
        db.close_connection()
