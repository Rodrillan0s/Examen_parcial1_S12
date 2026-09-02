from app.repos import vehiculos_repos

def listar_todos_los_vehiculos():
    vehiculos = vehiculos_repos.obtener_todos_los_vehiculos()
    return {
        "success": True,
        "message": "Vehículos recuperados exitosamente",
        "data": vehiculos
    }

def listar_mis_vehiculos(nro_usuario: int):
    vehiculos = vehiculos_repos.obtener_vehiculos_por_usuario(nro_usuario)
    return {
        "success": True,
        "message": f"Vehículos del usuario {nro_usuario} recuperados exitosamente",
        "data": vehiculos
    }

def registrar_vehiculo(data: dict):
    placa = data.get('placa')
    marca_modelo = data.get('marca_modelo')
    anio = data.get('anio')
    nro_usuario = data.get('nro_usuario')
    
    if not placa or not marca_modelo or not anio or not nro_usuario:
        raise ValueError("Los campos 'placa', 'marca_modelo', 'anio' y 'nro_usuario' son obligatorios.")

    placa_limpia = placa.strip().upper()

    # --- VALIDACIÓN DE PLACA DUPLICADA ---
    if vehiculos_repos.verificar_placa_db(placa_limpia):
        raise ValueError(f"La placa '{placa_limpia}' ya se encuentra registrada en otro vehículo.")
    # -------------------------------------

    nuevo_id = vehiculos_repos.crear_vehiculo_db(placa_limpia, marca_modelo.upper(), anio, nro_usuario)

    return {
        "success": True,
        "message": "Vehículo registrado exitosamente",
        "nro_vehiculo": nuevo_id
    }

def actualizar_vehiculo(nro_vehiculo: int, data: dict):
    if nro_vehiculo <= 0:
        raise ValueError("ID de vehículo no válido.")
        
    placa = data.get('placa')
    marca_modelo = data.get('marca_modelo')
    anio = data.get('anio')
    
    if not placa or not marca_modelo or not anio:
        raise ValueError("Los campos 'placa', 'marca_modelo' y 'anio' son obligatorios.")

    placa_limpia = placa.strip().upper()

    # --- VALIDACIÓN DE PLACA DUPLICADA EN ACTUALIZACIÓN ---
    # Le pasamos el nro_vehiculo para que no marque error si el usuario solo está modificando el año de su propio auto
    if vehiculos_repos.verificar_placa_db(placa_limpia, nro_vehiculo):
        raise ValueError(f"La placa '{placa_limpia}' ya se encuentra registrada en otro vehículo.")
    # ------------------------------------------------------

    exito = vehiculos_repos.actualizar_vehiculo_db(nro_vehiculo, placa_limpia, marca_modelo.upper(), anio)

    if not exito:
        raise ValueError(f"No se pudo actualizar. El vehículo con ID {nro_vehiculo} no existe.")

    return {
        "success": True,
        "message": "Vehículo actualizado exitosamente"
    }

def borrar_vehiculo(nro_vehiculo: int):
    if nro_vehiculo <= 0:
        raise ValueError("ID de vehículo no válido.")
        
    exito = vehiculos_repos.eliminar_vehiculo_db(nro_vehiculo)
    
    if not exito:
        raise ValueError(f"No se pudo eliminar. El vehículo con ID {nro_vehiculo} no existe.")
    
    return {
        "success": True,
        "message": "Vehículo eliminado permanentemente de la base de datos."
    }