from fastapi import BackgroundTasks
from app.repos import ofertas_repos, emergencias_repos
from app.services import notificaciones_services

#NORMALIZAR ROL
def normalizar_rol(rol_usuario: str):
    return rol_usuario.strip().upper() if rol_usuario else ""

#FUNCIONES DE LECTURA (GET)

def listar_ofertas_por_emergencia(nro_emergencia: int, token_data: dict):
    #VALIDAMOS QUE LA EMERGENCIA EXISTA
    emergencia = emergencias_repos.obtener_emergencia_por_id(nro_emergencia)
    if not emergencia:
        raise ValueError("La emergencia no existe.")
        
    rol = normalizar_rol(token_data.get('nombre_rol'))
    #SOLO EL CLIENTE DUEÑO, O ADMINS/GERENTES PUEDEN VER TODAS LAS OFERTAS
    if rol == 'CLIENTE' and emergencia['nro_usuario'] != token_data.get('nro_usuario'):
        raise ValueError("No tiene permiso para ver las ofertas de esta emergencia.")

    ofertas = ofertas_repos.obtener_ofertas_por_emergencia_db(nro_emergencia)
    return {"success": True, "message": "Ofertas recuperadas", "data": ofertas}

def listar_mis_ofertas_taller(token_data: dict):
    nro_taller = token_data.get('nro_taller')
    if not nro_taller:
        raise ValueError("El usuario no tiene un taller asignado.")
    
    ofertas = ofertas_repos.obtener_ofertas_por_taller_db(nro_taller)
    return {"success": True, "message": "Ofertas emitidas recuperadas", "data": ofertas}

#EMITIR OFERTA (SE DISPARA NOTIFICACIÓN AL CLIENTE)
def emitir_oferta(data: dict, token_data: dict, background_tasks: BackgroundTasks):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    # ACEPTAMOS ADMINISTRADOR, GERENTE O MECANICO
    if rol not in ['ADMINISTRADOR', 'GERENTE TALLER', 'MECANICO', 'MECÁNICO']:
        raise ValueError("Rol no autorizado para emitir cotizaciones.")

    nro_emergencia = data.get('nro_emergencia')
    precio = data.get('precio_estimado')
    tiempo = data.get('tiempo_estimado_minutos')
    
    # IMPORTANTE: SI ES ADMINISTRADOR Y NO VIENE EN EL JSON, ESTO SERÁ NONE
    nro_taller = data.get('nro_taller') or token_data.get('nro_taller')

    # VALIDACIÓN EXPLÍCITA PARA EVITAR EL ERROR DE DB
    if not nro_taller:
        raise ValueError("No se pudo determinar el taller emisor. Asegúrese de que el usuario tenga un taller asignado o envíe el nro_taller.")

    emergencia = emergencias_repos.obtener_emergencia_por_id(nro_emergencia)
    if not emergencia:
        raise ValueError("La emergencia no existe.")
    
    if emergencia['estado'] != 'PENDIENTE':
        raise ValueError("Ya no se aceptan ofertas para esta emergencia.")

    # AHORA ESTAMOS SEGUROS QUE nro_taller TIENE VALOR
    id_oferta = ofertas_repos.crear_oferta_db(precio, tiempo, nro_emergencia, nro_taller)
    
    # DISPARAR NOTIFICACIÓN AL CLIENTE
    nro_usuario_cliente = emergencia['nro_usuario']
    background_tasks.add_task(
        notificaciones_services.enviar_push_nueva_oferta, 
        nro_emergencia, id_oferta, nro_usuario_cliente, precio
    )

    return {"success": True, "message": "Oferta enviada al cliente.", "id_oferta": id_oferta}

#RESPONDER OFERTA (SE DISPARA NOTIFICACIÓN AL TALLER)
def responder_oferta(id_oferta: int, data: dict, token_data: dict, background_tasks: BackgroundTasks):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    estado_respuesta = data.get('estado_oferta', '').strip().upper()

    oferta = ofertas_repos.obtener_oferta_por_id_db(id_oferta)
    if not oferta:
        raise ValueError("La oferta no existe.")
    
    emergencia = emergencias_repos.obtener_emergencia_por_id(oferta['nro_emergencia'])
    if rol == 'CLIENTE' and emergencia['nro_usuario'] != token_data.get('nro_usuario'):
        raise ValueError("No puede responder a ofertas de otras emergencias.")

    ofertas_repos.actualizar_estado_oferta_db(id_oferta, estado_respuesta)

    if estado_respuesta == 'ACEPTADA':
        ofertas_repos.rechazar_otras_ofertas_db(oferta['nro_emergencia'], id_oferta)
        ofertas_repos.asignar_taller_emergencia_db(oferta['nro_emergencia'], oferta['nro_taller'])

    #DISPARAR NOTIFICACIÓN A TODOS LOS DEL TALLER QUE EMITIÓ LA OFERTA
    background_tasks.add_task(
        notificaciones_services.enviar_push_respuesta_oferta,
        oferta['nro_emergencia'], id_oferta, estado_respuesta, oferta['nro_taller']
    )

    return {"success": True, "message": f"Oferta {estado_respuesta.lower()} exitosamente."}