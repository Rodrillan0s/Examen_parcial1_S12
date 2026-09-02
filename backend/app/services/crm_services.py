from app.repos import crm_repos, notificaciones_repos
from app.classes.websocket_manager import manager


ROLES_CRM = ['ADMINISTRADOR', 'GERENTE TALLER', 'MECANICO', 'MECÁNICO']


def registrar_nuevo_plan(data: dict, token_data: dict):
    if token_data.get('nombre_rol') not in ROLES_CRM:
        raise ValueError("Solo el personal del taller puede registrar planes de mantenimiento.")

    id_empresa = token_data.get('id_empresa')
    if not id_empresa:
        raise ValueError("El usuario no pertenece a una empresa/taller válido.")

    id_plan = crm_repos.crear_plan_mantenimiento_db(
        tipo_servicio=data.get('tipo_servicio'),
        kilometraje_esperado=data.get('kilometraje_esperado'),
        fecha_estimada=data.get('fecha_estimada'),
        nro_vehiculo=data.get('nro_vehiculo'),
        id_empresa=id_empresa
    )

    return {
        "success": True,
        "message": "Plan de mantenimiento creado exitosamente.",
        "id_plan": id_plan
    }


async def procesar_recordatorios_automaticos():
    planes_vencidos = crm_repos.obtener_planes_vencidos_pendientes_db()
    notificados = 0

    for plan in planes_vencidos:
        nro_usuario = plan['nro_usuario']
        titulo = "Recordatorio de Mantenimiento"
        cuerpo = f"Es momento de realizar: {plan['tipo_servicio']} a tu vehículo."
        tipo_ref = "MANTENIMIENTO_PREVENTIVO"

        notificaciones_repos.guardar_notificacion_db(
            titulo,
            cuerpo,
            tipo_ref,
            nro_usuario,
            nro_emergencia=0
        )

        mensaje_push = {
            "tipo_alerta": tipo_ref,
            "titulo": titulo,
            "cuerpo": cuerpo,
            "data": {
                "id_plan": plan['id_plan']
            }
        }

        await manager.send_personal_message(mensaje_push, nro_usuario)

        crm_repos.actualizar_estado_plan_db(plan['id_plan'], 'NOTIFICADO')
        notificados += 1

    return {
        "success": True,
        "message": f"Se enviaron {notificados} recordatorios de mantenimiento."
    }


def listar_clientes_crm(token_data: dict):
    if token_data.get('nombre_rol') not in ROLES_CRM:
        raise ValueError("No tienes permisos para ver clientes del CRM.")

    clientes = crm_repos.obtener_clientes_crm_db()

    return {
        "success": True,
        "message": "Clientes obtenidos correctamente.",
        "data": clientes
    }


async def enviar_notificacion_crm(data: dict, token_data: dict):
    if token_data.get('nombre_rol') not in ROLES_CRM:
        raise ValueError("No tienes permisos para enviar notificaciones CRM.")

    clientes = data.get('clientes', [])
    asunto = data.get('asunto', '')
    mensaje = data.get('mensaje', '')
    canal = data.get('canal', 'WEBSOCKET')

    if not clientes or not isinstance(clientes, list):
        raise ValueError("Debe seleccionar al menos un cliente.")

    if not asunto:
        raise ValueError("Debe ingresar un asunto.")

    if not mensaje:
        raise ValueError("Debe ingresar un mensaje.")

    enviados = 0
    tipo_ref = "CRM_PERSONALIZADO"

    for nro_usuario in clientes:
        notificaciones_repos.guardar_notificacion_db(
            asunto,
            mensaje,
            tipo_ref,
            nro_usuario,
            nro_emergencia=0
        )

        mensaje_push = {
            "tipo_alerta": tipo_ref,
            "titulo": asunto,
            "cuerpo": mensaje,
            "canal": canal,
            "data": {
                "origen": "CRM"
            }
        }

        await manager.send_personal_message(mensaje_push, nro_usuario)
        enviados += 1

    return {
        "success": True,
        "message": f"Se enviaron {enviados} notificaciones correctamente."
    }