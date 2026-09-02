from app.repos import talleres_repos

def listar_talleres(id_empresa_filtro=None):
    talleres = talleres_repos.obtener_todos_los_talleres(id_empresa_filtro)
    return {
        "success": True,
        "message": "Talleres recuperados exitosamente",
        "data": talleres
    }

def registrar_taller(data: dict):
    nombre_taller = data.get('nombre_taller')
    direccion_escrita = data.get('direccion_escrita')
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    id_empresa = data.get('id_empresa')
    
    # En tu BD, el nombre y el id_empresa son NOT NULL obligatorios
    if not nombre_taller or not id_empresa:
        raise ValueError("Los campos 'nombre_taller' e 'id_empresa' son obligatorios.")

    nuevo_id = talleres_repos.crear_taller_db(
        nombre_taller.upper(), 
        direccion_escrita, 
        latitud, 
        longitud, 
        id_empresa
    )

    return {
        "success": True,
        "message": "Taller registrado exitosamente",
        "nro_taller": nuevo_id
    }

def actualizar_taller(nro_taller: int, data: dict):
    if nro_taller <= 0:
        raise ValueError("ID de taller no válido.")
        
    nombre_taller = data.get('nombre_taller')
    direccion_escrita = data.get('direccion_escrita')
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    disponibilidad = data.get('disponibilidad')
    id_empresa = data.get('id_empresa')
    
    if not nombre_taller or not id_empresa:
        raise ValueError("Los campos 'nombre_taller' e 'id_empresa' son obligatorios.")
    if disponibilidad is None:
        raise ValueError("El campo 'disponibilidad' es obligatorio para actualizar (true o false).")

    exito = talleres_repos.actualizar_taller_db(
        nro_taller, 
        nombre_taller.upper(), 
        direccion_escrita, 
        latitud, 
        longitud, 
        disponibilidad, 
        id_empresa
    )

    if not exito:
        raise ValueError(f"No se pudo actualizar. El taller con ID {nro_taller} no existe.")

    return {
        "success": True,
        "message": "Taller actualizado exitosamente"
    }

def borrar_taller(nro_taller: int):
    if nro_taller <= 0:
        raise ValueError("ID de taller no válido.")
        
    exito = talleres_repos.eliminar_taller_db(nro_taller)
    
    if not exito:
        raise ValueError(f"No se pudo eliminar. El taller con ID {nro_taller} no existe.")
    
    return {
        "success": True,
        "message": "Taller eliminado permanentemente de la base de datos."
    }

# =================================================================
#                   CRUD DE SERVICIOS DEL TALLER
# =================================================================

def listar_servicios_taller(nro_taller: int):
    if nro_taller <= 0:
        raise ValueError("ID de taller no válido.")
        
    servicios = talleres_repos.obtener_servicios_taller(nro_taller)
    return {
        "success": True,
        "message": f"Servicios del taller {nro_taller} recuperados exitosamente",
        "data": servicios
    }

def registrar_servicio_taller(nro_taller: int, data: dict):
    if nro_taller <= 0:
        raise ValueError("ID de taller no válido.")
        
    nombre_servicio = data.get('nombre_servicio')
    descripcion = data.get('descripcion')

    if not nombre_servicio or len(nombre_servicio.strip()) == 0:
        raise ValueError("El campo 'nombre_servicio' es obligatorio.")

    nuevo_id = talleres_repos.crear_servicio_taller_db(nro_taller, nombre_servicio.upper(), descripcion)
    return {
        "success": True,
        "message": "Servicio registrado exitosamente en el taller",
        "nro_servicio": nuevo_id
    }

def actualizar_servicio_taller(nro_servicio: int, nro_taller: int, data: dict):
    if nro_servicio <= 0 or nro_taller <= 0:
        raise ValueError("IDs no válidos.")
        
    nombre_servicio = data.get('nombre_servicio')
    descripcion = data.get('descripcion')

    if not nombre_servicio or len(nombre_servicio.strip()) == 0:
        raise ValueError("El campo 'nombre_servicio' es obligatorio.")

    exito = talleres_repos.actualizar_servicio_taller_db(nro_servicio, nro_taller, nombre_servicio.upper(), descripcion)
    if not exito:
        raise ValueError(f"No se pudo actualizar. El servicio con ID {nro_servicio} no existe en el taller {nro_taller}.")
        
    return {
        "success": True,
        "message": "Servicio actualizado exitosamente"
    }

def borrar_servicio_taller(nro_servicio: int, nro_taller: int):
    if nro_servicio <= 0 or nro_taller <= 0:
        raise ValueError("IDs no válidos.")
        
    exito = talleres_repos.eliminar_servicio_taller_db(nro_servicio, nro_taller)
    if not exito:
        raise ValueError(f"No se pudo eliminar. El servicio con ID {nro_servicio} no existe en el taller {nro_taller}.")
        
    return {
        "success": True,
        "message": "Servicio eliminado permanentemente."
    }