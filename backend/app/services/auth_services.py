from app.repos import auth_repos
from app.utils import security
from werkzeug.security import check_password_hash, generate_password_hash

def loguear_usuario(data: dict):
    ci = data.get('ci')
    password = data.get('password')

    if not ci or not password:
        raise ValueError("El CI y la contraseña son obligatorios.")

    usuario_db = auth_repos.obtener_usuario_por_ci(ci)

    if not usuario_db:
        raise ValueError("El usuario no existe o está inactivo.")

    password_hash = usuario_db['password_hash']

    if check_password_hash(password_hash, password):

        #CREAR EL TOKEN GENERADO PARA EL USUARIO
        token= security.create_access_token(
            usuario_db['nro_usuario'],
            usuario_db['nombre_usuario'],
            usuario_db["nombre_rol"],
            usuario_db['id_empresa'],
            usuario_db['nombre_completo'],
            usuario_db['nro_taller']
        )

        #RETORNAR RESPUESTA JSON DE EXITO
        return {
            "success": True,
            "message": "Login exitoso",
            "usuario": {
                "nro_usuario": usuario_db['nro_usuario'],
                "ci": usuario_db['ci'],
                "nombre_completo": usuario_db['nombre_completo'],
                "correo": usuario_db['correo'],
                "nombre_rol": usuario_db['nombre_rol'],
                "telefono": usuario_db['telefono'],
                "id_empresa":usuario_db["id_empresa"],
                "nro_taller":usuario_db["nro_taller"]
            },
            "token":token
        }

    #RETORNAR ERROR
    raise ValueError("Contraseña incorrecta.")

def registrar_nuevo_usuario(data: dict):
    
    #VALIDAR CAMPOS OBLIGATORIOS
    campos_obligatorios = ['ci', 'nombre_completo', 'nombre_usuario', 'password', 'nro_rol']
    for campo in campos_obligatorios:
        if not data.get(campo):
            raise ValueError(f"El campo '{campo}' es obligatorio.")
            
    #VALIDAR QUE EL NOMBRE DE USUARIO NO ESTE EN USO
    nombre_usuario = data.get('nombre_usuario').upper()
    if auth_repos.existe_nombre_usuario(nombre_usuario):
        raise ValueError(f"El nombre de usuario '{nombre_usuario}' ya se encuentra registrado.")

    #VALIDAR SI LA PERSONA YA EXISTE PARA NO REGISTRARLA
    ci = data.get('ci')
    persona_existe = auth_repos.existe_persona_por_ci(ci)
            
    #PREPARAR DATOS Y ENCRIPTAR LA CONSTRASEÑA
    password_plana = data.get('password')
    data['password_hash'] = generate_password_hash(password_plana)
    data['estado'] = 'ACTIVO'
    
    #INSERTAR EN DB
    nro_usuario = auth_repos.registrar_usuario_bd(data, persona_existe)
    
    if not nro_usuario:
        raise ValueError("No se pudo generar el identificador del nuevo usuario.")
        
    #RETORNAR RESPUESTA EXITOSA
    return {
        "success": True,
        "message": "Usuario registrado exitosamente.",
        "data": {
            "nro_usuario": nro_usuario,
            "ci": ci,
            "nombre_usuario": nombre_usuario
        }
    }