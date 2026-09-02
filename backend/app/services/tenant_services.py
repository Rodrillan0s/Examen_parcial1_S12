from app.repos import tenant_repos

def listar_empresas():
    empresas = tenant_repos.obtener_todas_las_empresas()
    return {
        "success": True,
        "message": "Empresas recuperadas exitosamente",
        "data": empresas
    }

def registrar_empresa(data: dict):
    nombre_empresa = data.get('nombre_empresa')
    nit = data.get('nit')
    
    if not nombre_empresa or len(nombre_empresa.strip()) == 0:
        raise ValueError("El campo 'nombre_empresa' es obligatorio.")
    if not nit or len(str(nit).strip()) == 0:
        raise ValueError("El campo 'nit' es obligatorio.")

    nuevo_id = tenant_repos.crear_empresa_db(nombre_empresa.upper(), nit)

    return {
        "success": True,
        "message": "Empresas registrada exitosamente",
        "id_empresa": nuevo_id
    }

def actualizar_empresa(id_empresa: int, data: dict):
    if id_empresa <= 0:
        raise ValueError("ID de empresa no válido.")
        
    nombre_empresa = data.get('nombre_empresa')
    nit = data.get('nit')
    estado = data.get('estado') 
    
    if not nombre_empresa or len(nombre_empresa.strip()) == 0:
        raise ValueError("El campo 'nombre_empresa' es obligatorio.")
    if not nit or len(str(nit).strip()) == 0:
        raise ValueError("El campo 'nit' es obligatorio.")
    if not estado or len(estado.strip()) == 0:
        raise ValueError("El campo 'estado' es obligatorio para actualizar.")

    # Guardamos el resultado de la base de datos
    exito = tenant_repos.actualizar_empresa_db(id_empresa, nombre_empresa.upper(), nit, estado.upper())

    # Si exito es False, significa que el ID no existía
    if not exito:
        raise ValueError(f"No se pudo actualizar. La empresa con ID {id_empresa} no existe o ya fue eliminada.")

    return {
        "success": True,
        "message": "Empresa actualizada exitosamente"
    }

def borrar_empresa(id_empresa: int):
    if id_empresa <= 0:
        raise ValueError("ID de empresa no válido.")
        
    exito = tenant_repos.eliminar_empresa_db(id_empresa)
    
    # Si exito es False, significa que el ID no existía
    if not exito:
        raise ValueError(f"No se pudo eliminar. La empresa con ID {id_empresa} no existe en la base de datos.")
    
    return {
        "success": True,
        "message": "Empresa eliminada permanentemente de la base de datos."
    }