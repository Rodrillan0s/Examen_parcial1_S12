from app.repos import escrow_repos


def retener_pago_simulado(data: dict, token_data: dict):
    rol = token_data.get('nombre_rol', '').upper()

    if rol not in ['ADMINISTRADOR', 'CLIENTE']:
        raise ValueError("No tienes permisos para retener fondos.")

    nro_emergencia = data.get('nro_emergencia')
    monto = data.get('monto')

    if not nro_emergencia or not monto:
        raise ValueError("Se requiere nro_emergencia y monto.")

    id_custodia = escrow_repos.crear_retencion_fondos_db(
        monto=monto,
        nro_emergencia=nro_emergencia
    )

    return {
        "success": True,
        "message": "Dinero retenido correctamente.",
        "id_custodia": id_custodia
    }


def obtener_mis_fondos(token_data: dict):
    nro_usuario = token_data.get('nro_usuario')

    if not nro_usuario:
        raise ValueError("Token inválido.")

    data = escrow_repos.obtener_fondos_usuario_db(nro_usuario)

    return {
        "success": True,
        "message": "Fondos retenidos obtenidos correctamente.",
        "data": data
    }


def obtener_resumen_usuarios(token_data: dict):
    rol = token_data.get('nombre_rol', '').upper()

    if rol != 'ADMINISTRADOR':
        raise ValueError("Solo el administrador puede ver el resumen por usuario.")

    data = escrow_repos.obtener_resumen_fondos_por_usuario_db()

    return {
        "success": True,
        "message": "Resumen de fondos retenidos obtenido correctamente.",
        "data": data
    }