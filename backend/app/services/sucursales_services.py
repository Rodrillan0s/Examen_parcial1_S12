from fastapi import Request
from app.repos import sucursales_repos
from app.services import bitacora_services

def is_global_admin(payload: dict) -> bool:
    roles = payload.get('roles', [])
    id_rol = payload.get('id_rol')
    return 'ADMINISTRADOR' in roles or id_rol == 1

def listar_sucursales(id_empresa: int = None, payload: dict = None):
    if payload and not is_global_admin(payload):
        # Override to user's company
        id_empresa = payload.get('id_empresa')
        
    sucursales = sucursales_repos.obtener_sucursales_por_empresa(id_empresa)
    return {
        "success": True,
        "message": "Sucursales recuperadas exitosamente",
        "data": sucursales
    }

def registrar_sucursal(data: dict, payload: dict, request: Request = None):
    nombre = data.get('nombre')
    direccion = data.get('direccion')
    id_empresa = data.get('id_empresa')
    activo = data.get('activo', True)
    
    if not nombre or len(nombre.strip()) == 0:
        raise ValueError("El campo 'nombre' es obligatorio.")
        
    if not is_global_admin(payload):
        # Forzar que la empresa sea la del administrador de tienda
        id_empresa = payload.get('id_empresa')
    else:
        if not id_empresa or not isinstance(id_empresa, int):
            raise ValueError("El campo 'id_empresa' es obligatorio para el Administrador Global.")

    nuevo_id = sucursales_repos.crear_sucursal_db(nombre, direccion, id_empresa, activo)

    
    bitacora_services.registrar_accion(
        modulo="SUCURSALES", accion="SUCURSAL_CREADA", nivel="INFO", resultado="EXITO",
        payload_jwt=payload, entidad="Sucursal", id_entidad=str(nuevo_id),
        descripcion=f"Sucursal creada: {nombre}",
        datos_nuevos={"nombre": nombre, "direccion": direccion, "id_empresa": id_empresa, "activo": activo},
        request=request
    )

    return {
        "success": True,
        "message": "Sucursal registrada exitosamente",
        "id_sucursal": nuevo_id
    }

def actualizar_sucursal(id_sucursal: int, data: dict, payload: dict, request: Request = None):
    if id_sucursal <= 0:
        raise ValueError("ID de sucursal no válido.")
        
    nombre = data.get('nombre')
    direccion = data.get('direccion')
    id_empresa = data.get('id_empresa')
    activo = data.get('activo')
    
    if not nombre or len(nombre.strip()) == 0:
        raise ValueError("El campo 'nombre' es obligatorio.")
        
    if activo is None:
        raise ValueError("El campo 'activo' es obligatorio para actualizar.")

    if not is_global_admin(payload):
        # Prevent moving the branch or updating another company's branch
        sucursal_db = sucursales_repos.obtener_sucursal_por_id(id_sucursal)
        if not sucursal_db:
            raise ValueError("Sucursal no encontrada.")
            
        if int(sucursal_db.get('id_empresa', 0)) != int(payload.get('id_empresa')):
            raise ValueError("No tiene permisos para editar esta sucursal.")
        
        # Ignorar cualquier intento de cambiar la empresa desde el frontend
        id_empresa = payload.get('id_empresa')
    else:
        if not id_empresa or not isinstance(id_empresa, int):
            raise ValueError("El campo 'id_empresa' es obligatorio y debe ser un número válido.")
        sucursal_db = sucursales_repos.obtener_sucursal_por_id(id_sucursal)
        if not sucursal_db:
            raise ValueError("Sucursal no encontrada.")
            
    # Audit log preparation
    datos_anteriores = {
        "nombre": sucursal_db.get("nombre"),
        "direccion": sucursal_db.get("direccion"),
        "id_empresa": sucursal_db.get("id_empresa"),
        "activo": sucursal_db.get("activo")
    }

    exito = sucursales_repos.actualizar_sucursal_db(id_sucursal, nombre, direccion, id_empresa, activo)
    
    if exito:
        bitacora_services.registrar_accion(
            modulo="SUCURSALES", accion="SUCURSAL_EDITADA", nivel="INFO", resultado="EXITO",
            payload_jwt=payload, entidad="Sucursal", id_entidad=str(id_sucursal),
            descripcion=f"Sucursal editada: {nombre}",
            datos_anteriores=datos_anteriores,
            datos_nuevos={"nombre": nombre, "direccion": direccion, "id_empresa": id_empresa, "activo": activo},
            request=request
        )

    return {
        "success": True,
        "message": "Sucursal actualizada exitosamente" if exito else "No se pudo actualizar la sucursal"
    }

def borrar_sucursal(id_sucursal: int, payload: dict, request: Request = None):
    if id_sucursal <= 0:
        raise ValueError("ID de sucursal no válido.")
        
    if not is_global_admin(payload):
        sucursal_db = sucursales_repos.obtener_sucursal_por_id(id_sucursal)
        if not sucursal_db or int(sucursal_db.get('id_empresa', 0)) != int(payload.get('id_empresa')):
            raise ValueError("No tiene permisos para desactivar esta sucursal.")
        
    exito = sucursales_repos.desactivar_sucursal_db(id_sucursal)
    
    if not exito:
        raise ValueError(f"No se pudo desactivar. La sucursal con ID {id_sucursal} no existe en la base de datos.")
    
    bitacora_services.registrar_accion(
        modulo="SUCURSALES", accion="SUCURSAL_DESACTIVADA", nivel="WARNING", resultado="EXITO",
        payload_jwt=payload, entidad="Sucursal", id_entidad=str(id_sucursal),
        descripcion=f"Sucursal desactivada",
        datos_anteriores={"activo": True},
        datos_nuevos={"activo": False},
        request=request
    )
    
    return {
        "success": True,
        "message": "Sucursal desactivada correctamente."
    }
