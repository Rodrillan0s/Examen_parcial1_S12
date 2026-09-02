from app.repos import users_repos
from werkzeug.security import generate_password_hash

def listar_usuarios():
    usuarios = users_repos.obtener_todos_los_usuarios()
    return {
        "success": True,
        "message": "Usuarios recuperados exitosamente",
        "data": usuarios
    }

def registrar_usuario(data: dict):
    campos_requeridos = ['ci', 'nombre_completo', 'nombre_usuario', 'password', 'nro_rol', 'id_empresa']
    for campo in campos_requeridos:
        if not data.get(campo):
            raise ValueError(f"El campo '{campo}' es obligatorio.")

    password_hash = generate_password_hash(data['password'])

    datos_persona = (
        data['ci'], 
        data['nombre_completo'].upper(), 
        data.get('telefono'), 
        data.get('correo'), 
        data.get('direccion')
    )
    
    datos_usuario = (
        data['nombre_usuario'].upper(), 
        password_hash, 
        'ACTIVO', 
        data['ci'], 
        data['nro_rol'],
        data['id_empresa']
    )

    nuevo_id = users_repos.crear_usuario_db(datos_persona, datos_usuario)

    return {
        "success": True,
        "message": "Usuario registrado exitosamente",
        "nro_usuario": nuevo_id
    }

def actualizar_usuario(nro_usuario: int, data: dict):
    if nro_usuario <= 0:
        raise ValueError("ID de usuario no válido.")
        
    campos_requeridos = ['ci', 'nombre_completo', 'nombre_usuario', 'nro_rol', 'id_empresa']
    for campo in campos_requeridos:
        if not data.get(campo):
            raise ValueError(f"El campo '{campo}' es obligatorio.")

    ci = data['ci']
    
    datos_persona = (
        data['nombre_completo'].upper(), 
        data.get('telefono'), 
        data.get('correo'), 
        data.get('direccion')
    )
    
    cambiar_password = False
    if data.get('password') and len(data.get('password').strip()) > 0:
        cambiar_password = True
        password_hash = generate_password_hash(data['password'])
        datos_usuario = (
            data['nombre_usuario'], 
            password_hash,
            data['nro_rol'],
            data['id_empresa']
        )
    else:
        datos_usuario = (
            data['nombre_usuario'], 
            data['nro_rol'],
            data['id_empresa']
        )

    users_repos.actualizar_usuario_db(nro_usuario, ci, datos_persona, datos_usuario, cambiar_password)

    return {
        "success": True,
        "message": "Usuario actualizado exitosamente"
    }

def borrar_usuario(nro_usuario: int):
    if nro_usuario <= 0:
        raise ValueError("ID de usuario no válido.")
        
    users_repos.eliminar_usuario_db(nro_usuario)
    
    return {
        "success": True,
        "message": "Usuario eliminado correctamente."
    }