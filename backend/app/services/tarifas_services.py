from app.repos import tarifas_repos

def listar_tarifas():
    tarifas = tarifas_repos.obtener_todas_las_tarifas()
    return {
        "success": True,
        "message": "Conceptos de tarifa recuperados exitosamente del catálogo global.",
        "data": tarifas
    }

def registrar_tarifa(data: dict):
    descripcion = data.get('descripcion')
    monto = data.get('monto')
    tipo = data.get('tipo', 'SERVICIO')  # Si no mandan tipo, por defecto es SERVICIO

    if not descripcion or monto is None:
        raise ValueError("Los campos 'descripcion' y 'monto' son obligatorios.")

    if float(monto) < 0:
        raise ValueError("El precio base de la tarifa no puede ser un monto negativo.")

    nuevo_id = tarifas_repos.crear_tarifa_db(descripcion.strip(), float(monto), tipo.strip().upper())
    return {
        "success": True,
        "message": "Concepto de tarifa registrado exitosamente.",
        "id_concepto": nuevo_id
    }

def modificar_tarifa(id_concepto: int, data: dict):
    if id_concepto <= 0:
        raise ValueError("ID de concepto de tarifa no válido.")

    descripcion = data.get('descripcion')
    monto = data.get('monto')
    tipo = data.get('tipo')

    if not descripcion or monto is None or not tipo:
        raise ValueError("Los campos 'descripcion', 'monto' y 'tipo' son obligatorios para actualizar.")

    exito = tarifas_repos.actualizar_tarifa_db(id_concepto, descripcion.strip(), float(monto), tipo.strip().upper())
    if not exito:
        raise ValueError(f"No se pudo actualizar. El concepto de tarifa con ID {id_concepto} no existe.")

    return {
        "success": True,
        "message": "Concepto de tarifa actualizado exitosamente."
    }

def borrar_tarifa(id_concepto: int):
    if id_concepto <= 0:
        raise ValueError("ID de concepto de tarifa no válido.")

    exito = tarifas_repos.eliminar_tarifa_db(id_concepto)
    if not exito:
        raise ValueError(f"No se pudo eliminar. El concepto con ID {id_concepto} no existe.")

    return {
        "success": True,
        "message": "Concepto de tarifa eliminado físicamente de la base de datos."
    }