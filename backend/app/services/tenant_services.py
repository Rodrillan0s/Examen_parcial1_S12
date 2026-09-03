from app.repos import tenant_repos
from fastapi import Request
from app.services import bitacora_services

def listar_empresas():
    empresas = tenant_repos.obtener_todas_las_empresas()
    return {
        "success": True,
        "message": "Empresas recuperadas exitosamente",
        "data": empresas
    }

def registrar_empresa(data: dict, payload: dict, request: Request = None):
    nombre_empresa = data.get('nombre_empresa')
    nit = data.get('nit')
    
    if not nombre_empresa or len(nombre_empresa.strip()) == 0:
        raise ValueError("El campo 'nombre_empresa' es obligatorio.")
    if not nit or len(str(nit).strip()) == 0:
        raise ValueError("El campo 'nit' es obligatorio.")

    nuevo_id = tenant_repos.crear_empresa_db(nombre_empresa.upper(), nit)

    bitacora_services.registrar_accion(
        modulo="EMPRESAS", accion="EMPRESA_CREADA", nivel="INFO", resultado="EXITO",
        payload_jwt=payload, entidad="Empresa", id_entidad=str(nuevo_id),
        descripcion=f"Empresa creada: {nombre_empresa.upper()}",
        datos_nuevos={"nombre_empresa": nombre_empresa.upper(), "nit": nit},
        request=request
    )

    return {
        "success": True,
        "message": "Empresas registrada exitosamente",
        "id_empresa": nuevo_id
    }

def actualizar_empresa(id_empresa: int, data: dict, payload: dict, request: Request = None):
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

    # Get previous state
    empresa_db = None
    try:
        from app.classes.postgres import PostgreSQL
        db = PostgreSQL()
        db.create_connection()
        r = db.execute_query(f"SELECT id_empresa, nombre_empresa, nit, estado FROM comercio.empresa WHERE id_empresa = %s", (id_empresa,), fetchone=True)
        if r:
            empresa_db = {"id_empresa": r[0], "nombre_empresa": r[1], "nit": r[2], "estado": r[3]}
        db.close_connection()
    except Exception:
        pass

    # Guardamos el resultado de la base de datos
    exito = tenant_repos.actualizar_empresa_db(id_empresa, nombre_empresa.upper(), nit, estado.upper())

    # Si exito es False, significa que el ID no existía
    if not exito:
        raise ValueError(f"No se pudo actualizar. La empresa con ID {id_empresa} no existe o ya fue eliminada.")

    if exito:
        bitacora_services.registrar_accion(
            modulo="EMPRESAS", accion="EMPRESA_EDITADA", nivel="INFO", resultado="EXITO",
            payload_jwt=payload, entidad="Empresa", id_entidad=str(id_empresa),
            descripcion=f"Empresa editada: {nombre_empresa.upper()}",
            datos_anteriores=empresa_db,
            datos_nuevos={"nombre_empresa": nombre_empresa.upper(), "nit": nit, "estado": estado.upper()},
            request=request
        )

    return {
        "success": True,
        "message": "Empresa actualizada exitosamente"
    }

def borrar_empresa(id_empresa: int, payload: dict, request: Request = None):
    if id_empresa <= 0:
        raise ValueError("ID de empresa no válido.")
        
    exito = tenant_repos.eliminar_empresa_db(id_empresa)
    
    if not exito:
        raise ValueError(f"No se pudo eliminar. La empresa con ID {id_empresa} no existe.")
        
    bitacora_services.registrar_accion(
        modulo="EMPRESAS", accion="EMPRESA_ELIMINADA", nivel="WARNING", resultado="EXITO",
        payload_jwt=payload, entidad="Empresa", id_entidad=str(id_empresa),
        descripcion=f"Empresa eliminada",
        request=request
    )
    
    return {
        "success": True,
        "message": "Empresa eliminada permanentemente de la base de datos."
    }