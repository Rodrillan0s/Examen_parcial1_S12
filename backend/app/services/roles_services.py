from app.repos import roles_repos

def listar_roles():
    roles = roles_repos.obtener_todos_los_roles()
    return {
        "success": True,
        "message": "Roles recuperados exitosamente",
        "data": roles
    }

def registrar_rol(data: dict):
    nombre_rol = data.get('nombre_rol')
    descripcion = data.get('descripcion')
    
    if not nombre_rol or len(nombre_rol.strip()) == 0:
        raise ValueError("El campo 'nombre_rol' es obligatorio.")

    # Guardamos el nombre del rol siempre en mayúsculas (ej. ADMINISTRADOR, MECANICO)
    nuevo_id = roles_repos.crear_rol_db(nombre_rol.upper(), descripcion)

    return {
        "success": True,
        "message": "Rol registrado exitosamente",
        "nro_rol": nuevo_id
    }

def actualizar_rol(nro_rol: int, data: dict):
    if nro_rol <= 0:
        raise ValueError("ID de rol no válido.")
        
    nombre_rol = data.get('nombre_rol')
    descripcion = data.get('descripcion')
    
    if not nombre_rol or len(nombre_rol.strip()) == 0:
        raise ValueError("El campo 'nombre_rol' es obligatorio.")

    exito = roles_repos.actualizar_rol_db(nro_rol, nombre_rol.upper(), descripcion)

    if not exito:
        raise ValueError(f"No se pudo actualizar. El rol con ID {nro_rol} no existe.")

    return {
        "success": True,
        "message": "Rol actualizado exitosamente"
    }

def borrar_rol(nro_rol: int):
    if nro_rol <= 0:
        raise ValueError("ID de rol no válido.")
        
    exito = roles_repos.eliminar_rol_db(nro_rol)
    
    if not exito:
        raise ValueError(f"No se pudo eliminar. El rol con ID {nro_rol} no existe.")
    
    return {
        "success": True,
        "message": "Rol eliminado permanentemente de la base de datos."
    }