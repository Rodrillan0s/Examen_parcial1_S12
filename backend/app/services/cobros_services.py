from app.repos import cobros_repos

def obtener_detalles_para_pago(nro_emergencia: int, nro_usuario: int):
    if not nro_emergencia or nro_emergencia <= 0:
        raise ValueError("Número de emergencia inválido.")

    resumen = cobros_repos.obtener_resumen_cobro_db(nro_emergencia, nro_usuario)
    if not resumen:
        raise ValueError("No se encontró una cotización aceptada para esta emergencia o no tienes permisos.")

    return {
        "success": True,
        "message": "Detalles de cobro recuperados.",
        "data": resumen
    }

def procesar_pago_simulado(data: dict, nro_usuario: int):
    id_orden = data.get('id_orden')
    monto = data.get('monto_pagado')
    metodo = data.get('metodo_pago', 'QR_TRANSFERENCIA')

    if not id_orden or not monto:
        raise ValueError("Se requiere el 'id_orden' y el 'monto_pagado' para procesar el pago.")

    # En un sistema real aquí llamaríamos al API de Stripe/Banco. Aquí simulamos el éxito:
    exito = cobros_repos.registrar_pago_db(int(id_orden), float(monto), metodo)
    
    if not exito:
        raise ValueError("Ocurrió un error al registrar el pago en la base de datos.")

    return {
        "success": True,
        "message": "¡Pago procesado exitosamente! La orden ha sido marcada como PAGADA."
    }