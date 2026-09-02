from fastapi import BackgroundTasks
from app.repos import emergencias_repos
from app.services import notificaciones_services

#FUNCIONES DE LECTURA (GET)

def listar_todas_las_emergencias():
    emergencias = emergencias_repos.obtener_todas_las_emergencias()
    return {"success": True, "message": "Emergencias recuperadas exitosamente", "data": emergencias}

def listar_mis_emergencias(nro_usuario: int):
    emergencias = emergencias_repos.obtener_emergencias_por_usuario(nro_usuario)
    return {"success": True, "message": f"Emergencias del usuario {nro_usuario} recuperadas exitosamente", "data": emergencias}

def listar_emergencias_mi_taller(nro_usuario: int):
    if not nro_usuario:
        raise ValueError("No se pudo identificar al usuario autenticado.")
    emergencias = emergencias_repos.obtener_emergencias_por_taller_del_mecanico(nro_usuario)
    return {"success": True, "message": "Emergencias del taller recuperadas exitosamente", "data": emergencias}

def obtener_evidencias_emergencia(nro_emergencia: int, token_data: dict):
    emergencia = emergencias_repos.obtener_emergencia_por_id(nro_emergencia)
    if not emergencia:
        raise ValueError("La emergencia especificada no existe.")
    evidencias = emergencias_repos.obtener_evidencias_db(nro_emergencia)
    return {"success": True, "message": "Evidencias recuperadas con éxito", "data": evidencias}

#FUNCIONES DE ESCRITURA CON NOTIFICACIONES Y BASE64

def normalizar_rol(rol_usuario: str):
    return rol_usuario.strip().upper() if rol_usuario else ""

def registrar_emergencia(data: dict, token_data: dict, background_tasks: BackgroundTasks):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    tipo_emergencia = data.get('tipo_emergencia')
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    prioridad = data.get('prioridad', 'MEDIA')
    
    #VALIDACION NO AGRESIVA DE VEHICULO
    nro_vehiculo = data.get('nro_vehiculo', None)
    if 'nro_vehiculo' in data and not nro_vehiculo:
        raise ValueError("Si provee la llave 'nro_vehiculo', no puede estar vacía.")
    
    #VALIDACIONES POR ROL
    if rol == 'ADMINISTRADOR':
        nro_usuario = data.get('nro_usuario')
        if not nro_usuario:
            raise ValueError("Administrador: debe especificar el 'nro_usuario'.")
    elif rol == 'CLIENTE':
        nro_usuario = token_data.get('nro_usuario')
        evidencias = data.get('evidencias', [])
        if not evidencias:
            raise ValueError("Cliente: es obligatorio adjuntar al menos una evidencia.")
    else:
        raise ValueError("Rol no autorizado para crear emergencias.")

    nuevo_id = emergencias_repos.crear_emergencia_db(
        tipo_emergencia.upper(), latitud, longitud, 'PENDIENTE', prioridad.upper(), nro_usuario, nro_vehiculo
    )

    #PROCESAR EVIDENCIAS BASE64 AL CREAR
    if rol == 'CLIENTE' and data.get('evidencias'):
        for ev in data.get('evidencias'):
            tipo = ev.get('tipo_archivo', 'IMAGEN')
            base64_string = ev.get('base64', '')
            if base64_string:
                emergencias_repos.agregar_evidencia_db(nuevo_id, tipo.upper(), base64_string)

    #DISPARAR NOTIFICACION EN SEGUNDO PLANO
    background_tasks.add_task(
        notificaciones_services.enviar_push_nueva_emergencia, 
        nuevo_id, 
        tipo_emergencia.upper()
    )

    return {"success": True, "message": "Emergencia y evidencias creadas.", "nro_emergencia": nuevo_id}

def actualizar_emergencia(nro_emergencia: int, data: dict, token_data: dict):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    nro_taller_token = token_data.get('nro_taller')

    emergencia = emergencias_repos.obtener_emergencia_por_id(nro_emergencia)
    if not emergencia:
        raise ValueError("La emergencia no existe.")

    estado_actual = normalizar_rol(emergencia.get('estado'))
    estado_nuevo = normalizar_rol(data.get('estado'))

    estados_cerrados = ['CANCELADA', 'FINALIZADA', 'COMPLETADA']

    if estado_actual in estados_cerrados:
        raise ValueError("No se puede modificar una emergencia que ya fue cerrada.")

    if rol == 'ADMINISTRADOR':
        estado = data.get('estado')
        añadir = data.get('añadir_evidencias', [])

        if not estado and not añadir:
            raise ValueError("Admin: debe actualizar el 'estado' o cargar 'evidencias'.")

        if estado:
            emergencias_repos.actualizar_estado_emergencia_db(
                nro_emergencia,
                estado.upper()
            )

        if añadir:
            for ev in añadir:
                tipo = ev.get('tipo_archivo', 'IMAGEN')
                base64_string = ev.get('base64', '')

                if base64_string:
                    emergencias_repos.agregar_evidencia_db(
                        nro_emergencia,
                        tipo.upper(),
                        base64_string
                    )

    elif rol in ['MECANICO', 'MECÁNICO', 'TECNICO', 'TÉCNICO']:
        if emergencia['nro_taller'] != nro_taller_token:
            raise ValueError("Acceso Denegado: Emergencia no asignada a tu taller.")

        estado = data.get('estado')

        if not estado:
            raise ValueError("Mecánico: solo puede actualizar el 'estado'.")

        emergencias_repos.actualizar_estado_emergencia_db(
            nro_emergencia,
            estado.upper()
        )

    elif rol == 'CLIENTE':
        if emergencia['nro_usuario'] != token_data.get('nro_usuario'):
            raise ValueError("No puedes modificar emergencias de otros.")

        añadir = data.get('añadir_evidencias', [])
        eliminar = data.get('eliminar_evidencias', [])

        if estado_nuevo and estado_nuevo != 'CANCELADA':
            raise ValueError("Cliente: solo puede cancelar la emergencia.")

        if not estado_nuevo and not añadir and not eliminar:
            raise ValueError("Cliente: debe cancelar la emergencia o modificar evidencias.")

        if estado_nuevo == 'CANCELADA':
            emergencias_repos.actualizar_estado_emergencia_db(
                nro_emergencia,
                'CANCELADA'
            )

        for ev in añadir:
            tipo = ev.get('tipo_archivo', 'IMAGEN')
            base64_string = ev.get('base64', '')

            if base64_string:
                emergencias_repos.agregar_evidencia_db(
                    nro_emergencia,
                    tipo.upper(),
                    base64_string
                )

        for id_ev in eliminar:
            emergencias_repos.eliminar_evidencia_db(id_ev)

    else:
        raise ValueError("Rol no autorizado para actualizar emergencias.")

    return {
        "success": True,
        "message": "Emergencia actualizada correctamente."
    }

def borrar_emergencia(nro_emergencia: int, token_data: dict):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    emergencia = emergencias_repos.obtener_emergencia_por_id(nro_emergencia)
    if not emergencia: raise ValueError("Emergencia no encontrada.")
    if rol == 'CLIENTE' and emergencia['nro_usuario'] != token_data.get('nro_usuario'):
        raise ValueError("No tienes permiso para borrar esto.")
    
    emergencias_repos.eliminar_emergencia_db(nro_emergencia)
    return {"success": True, "message": "Emergencia eliminada."}