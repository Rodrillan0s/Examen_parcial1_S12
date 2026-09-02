from app.repos import profile_repos
from app.utils import security
from werkzeug.security import generate_password_hash

def obtener_perfil_usuario(nro_usuario):

    if not nro_usuario:
        raise ValueError('Debe Estar Logueado para ver su perfil.')
    
    usuario_db=profile_repos.get_profile(nro_usuario)

    if not usuario_db:
        raise ValueError('El usuario no se encuentra registrado en el Sistema.')
    
    return {
        'success':True,
        'message':'Datos del Usuario Obtenido Exitosamente',
        'data':usuario_db
    }

def actualizar_perfil_usuario(nro_usuario: int, datos_perfil: dict):
    datos_perfil['nro_usuario'] = nro_usuario
    
   
    password_plano = datos_perfil.get('password')
    if password_plano:
        datos_perfil['password_hash'] = generate_password_hash(password_plano) 
    else:
        
        datos_perfil['password_hash'] = None

    return profile_repos.update_profile(datos_perfil)