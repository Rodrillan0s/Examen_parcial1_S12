from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from app.repos import sucursales_repos, ciudades_repos
from app.services import bitacora_services
from app.utils.tenant_guard import (
    es_administrador_global,
    resolver_tenant_operacion,
    validar_acceso_recurso_tenant,
    validar_relaciones_tenant
)

def is_global_admin(payload: dict) -> bool:
    return es_administrador_global(payload)

def listar_sucursales(id_empresa: Optional[int] = None, payload: dict = None) -> Dict[str, Any]:
    empresa_efectiva = resolver_tenant_operacion(payload, id_empresa, permitir_global=True)
    sucursales = sucursales_repos.obtener_sucursales_por_empresa(empresa_efectiva)
    
    if payload and payload.get('alcance') == 'SUCURSAL':
        sucursales_autorizadas = payload.get('sucursales') or []
        sucursales = [s for s in sucursales if s.get('id_sucursal') in sucursales_autorizadas]

    return {
        "success": True,
        "message": "Sucursales recuperadas exitosamente",
        "data": sucursales
    }

def obtener_sucursal_detalle(id_sucursal: int, payload: dict) -> Dict[str, Any]:
    if id_sucursal <= 0:
        raise HTTPException(status_code=400, detail="ID de sucursal no válido.")

    sucursal = sucursales_repos.obtener_sucursal_por_id(id_sucursal)
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada.")

    validar_acceso_recurso_tenant(payload, sucursal.get('id_empresa'), "sucursal")

    return {
        "success": True,
        "data": sucursal
    }

def registrar_sucursal(data: dict, payload: dict, request: Optional[Request] = None) -> Dict[str, Any]:
    nombre = data.get('nombre') or data.get('nombre_sucursal')
    direccion = data.get('direccion') or data.get('direccion_sucursal')
    telefono = data.get('telefono') or data.get('telefono_sucursal')
    id_ciudad = data.get('id_ciudad')
    ciudad_nombre = data.get('ciudad')
    departamento = data.get('departamento')
    activo = data.get('activo', True)
    
    # Validaciones de obligatoriedad
    if not nombre or not str(nombre).strip():
        raise HTTPException(status_code=400, detail="El nombre de la sucursal es obligatorio.")
        
    if not direccion or not str(direccion).strip():
        raise HTTPException(status_code=400, detail="La dirección física de la sucursal es obligatoria.")

    if not telefono or not str(telefono).strip():
        raise HTTPException(status_code=400, detail="El teléfono de contacto de la sucursal es obligatorio.")

    # Aislamiento y Resolución Multi-Tenant
    id_empresa_solicitado = data.get('id_empresa')
    if id_empresa_solicitado in (0, '0', '', None):
        id_empresa_solicitado = None
    else:
        id_empresa_solicitado = int(id_empresa_solicitado)

    id_empresa = resolver_tenant_operacion(payload, id_empresa_solicitado, permitir_global=False)

    # Resolución de Ciudad
    if not id_ciudad:
        if ciudad_nombre and str(ciudad_nombre).strip() and departamento and str(departamento).strip():
            # Crear o buscar la ciudad ingresada por el usuario
            id_ciudad = ciudades_repos.obtener_o_crear_ciudad_db(str(ciudad_nombre).strip(), str(departamento).strip())
        else:
            raise ValueError("Debe seleccionar o indicar una ciudad y departamento para la sucursal.")
    else:
        ciudad_existente = ciudades_repos.obtener_ciudad_por_id_db(id_ciudad)
        if not ciudad_existente:
            raise ValueError("La ciudad seleccionada no es válida.")

    nuevo_id = sucursales_repos.crear_sucursal_db(
        nombre=str(nombre).strip(),
        direccion=str(direccion).strip(),
        telefono=str(telefono).strip(),
        id_ciudad=id_ciudad,
        id_empresa=id_empresa,
        activo=bool(activo)
    )

    # Auditoría
    try:
        bitacora_services.registrar_accion(
            modulo="SUCURSALES", 
            accion="REGISTRAR_SUCURSAL", 
            nivel="INFO", 
            resultado="EXITO",
            payload_jwt=payload, 
            entidad="Sucursal", 
            id_entidad=str(nuevo_id),
            descripcion=f"Sucursal registrada: {nombre} (Tenant #{id_empresa})",
            datos_nuevos={
                "nombre": nombre, 
                "direccion": direccion, 
                "telefono": telefono,
                "id_empresa": id_empresa, 
                "id_ciudad": id_ciudad,
                "activo": activo
            },
            request=request
        )
    except Exception as e:
        print(f"[BITACORA] Error al registrar sucursal: {e}")

    return {
        "success": True,
        "message": f"Sucursal '{nombre}' registrada exitosamente",
        "id_sucursal": nuevo_id
    }

def actualizar_sucursal(id_sucursal: int, data: dict, payload: dict, request: Optional[Request] = None) -> Dict[str, Any]:
    if id_sucursal <= 0:
        raise ValueError("ID de sucursal no válido.")
        
    nombre = data.get('nombre')
    direccion = data.get('direccion')
    telefono = data.get('telefono')
    id_empresa = data.get('id_empresa')
    id_ciudad = data.get('id_ciudad')
    ciudad_nombre = data.get('ciudad')
    departamento = data.get('departamento')
    activo = data.get('activo')
    
    if not nombre or not str(nombre).strip():
        raise ValueError("El nombre de la sucursal es obligatorio.")
        
    if not direccion or not str(direccion).strip():
        raise ValueError("La dirección de la sucursal es obligatoria.")

    if not telefono or not str(telefono).strip():
        raise ValueError("El teléfono de la sucursal es obligatorio.")
        
    if activo is None:
        activo = True

    sucursal_db = sucursales_repos.obtener_sucursal_por_id(id_sucursal)
    if not sucursal_db:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada.")

    validar_acceso_recurso_tenant(payload, sucursal_db.get('id_empresa'), "sucursal")

    if not is_global_admin(payload):
        id_empresa = payload.get('id_empresa')
    else:
        if not id_empresa or not isinstance(id_empresa, int):
            id_empresa = sucursal_db.get('id_empresa')

    # Resolución de Ciudad
    if not id_ciudad:
        if ciudad_nombre and str(ciudad_nombre).strip() and departamento and str(departamento).strip():
            id_ciudad = ciudades_repos.obtener_o_crear_ciudad_db(str(ciudad_nombre).strip(), str(departamento).strip())
        else:
            id_ciudad = sucursal_db.get('id_ciudad')

    exito = sucursales_repos.actualizar_sucursal_db(
        id_sucursal=id_sucursal,
        nombre=str(nombre).strip(),
        direccion=str(direccion).strip(),
        telefono=str(telefono).strip(),
        id_ciudad=id_ciudad,
        id_empresa=id_empresa,
        activo=bool(activo)
    )
    
    if exito:
        try:
            bitacora_services.registrar_accion(
                modulo="SUCURSALES", 
                accion="ACTUALIZAR_SUCURSAL", 
                nivel="INFO", 
                resultado="EXITO",
                payload_jwt=payload, 
                entidad="Sucursal", 
                id_entidad=str(id_sucursal),
                descripcion=f"Sucursal actualizada: {nombre}",
                datos_anteriores=sucursal_db,
                datos_nuevos={
                    "nombre": nombre, 
                    "direccion": direccion, 
                    "telefono": telefono,
                    "id_empresa": id_empresa, 
                    "id_ciudad": id_ciudad,
                    "activo": activo
                },
                request=request
            )
        except Exception as e:
            print(f"[BITACORA] Error al actualizar sucursal: {e}")

    return {
        "success": True,
        "message": f"Sucursal '{nombre}' actualizada correctamente"
    }

def cambiar_estado_sucursal(id_sucursal: int, data: dict, payload: dict, request: Optional[Request] = None) -> Dict[str, Any]:
    if id_sucursal <= 0:
        raise HTTPException(status_code=400, detail="ID de sucursal no válido.")

    sucursal_db = sucursales_repos.obtener_sucursal_por_id(id_sucursal)
    if not sucursal_db:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada.")

    validar_acceso_recurso_tenant(payload, sucursal_db.get('id_empresa'), "sucursal")

    nuevo_activo = bool(data.get('activo', False))
    exito = sucursales_repos.cambiar_estado_sucursal_db(id_sucursal, nuevo_activo)
    if not exito:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el estado de la sucursal.")

    try:
        bitacora_services.registrar_accion(
            modulo="SUCURSALES", 
            accion="CAMBIAR_ESTADO_SUCURSAL", 
            nivel="INFO", 
            resultado="EXITO",
            payload_jwt=payload, 
            entidad="Sucursal", 
            id_entidad=str(id_sucursal),
            descripcion=f"Estado de sucursal {sucursal_db.get('nombre')} cambiado a {'ACTIVA' if nuevo_activo else 'INACTIVA'}",
            datos_anteriores={"activo": sucursal_db.get("activo")},
            datos_nuevos={"activo": nuevo_activo},
            request=request
        )
    except Exception as e:
        print(f"[BITACORA] Error al registrar cambio de estado de sucursal: {e}")

    return {
        "success": True,
        "message": f"Sucursal {'activada' if nuevo_activo else 'desactivada'} correctamente"
    }

def borrar_sucursal(id_sucursal: int, payload: dict, request: Optional[Request] = None) -> Dict[str, Any]:
    return cambiar_estado_sucursal(id_sucursal, {"activo": False}, payload, request)
