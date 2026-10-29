from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict
from psycopg2.errors import UndefinedTable
from app.modules.saas.services import saas_services as service
from app.core.security import require_permission, require_platform_admin
from app.core.tenant_guard import resolver_tenant_operacion, validar_acceso_recurso_tenant

router = APIRouter(tags=['SaaS — Iteración 1'])


class PlanIn(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    nombre: str = Field(min_length=2, max_length=80)
    activo: bool


class SuscripcionIn(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    codigo_plan: Literal['BASICO', 'PROFESIONAL']
    inicio: datetime
    fin: datetime
    motivo: str = Field(min_length=3, max_length=500)


class CancelacionIn(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    motivo: str = Field(min_length=3, max_length=500)
    confirmar: Literal[True]


@router.get('/api/planes')
def planes(payload=Depends(require_permission('planes.ver'))):
    return {'success': True, 'data': service.listar_planes()}


@router.put('/api/planes/{codigo}', dependencies=[Depends(require_platform_admin)])
def actualizar_plan(codigo: Literal['BASICO', 'PROFESIONAL'], data: PlanIn, payload=Depends(require_permission('planes.gestionar'))):
    return {'success': True, 'data': service.actualizar_plan(codigo, data.nombre, data.activo, payload)}


@router.get('/api/mi-empresa/plan')
def mi_plan(id_empresa: int | None = Query(None, gt=0), payload=Depends(require_permission('suscripciones.ver'))):
    empresa = id_empresa or payload.get('id_empresa')
    if not empresa:
        raise HTTPException(400, detail='Seleccione una empresa.')
    validar_acceso_recurso_tenant(payload, empresa, 'plan')
    return {'success': True, 'data': service.consultar_plan(empresa)}


@router.get('/api/empresas/{id_empresa}/suscripciones')
def suscripciones(id_empresa: int, payload=Depends(require_permission('suscripciones.ver'))):
    validar_acceso_recurso_tenant(payload, id_empresa, 'suscripciones')
    try:
        return {'success': True, 'data': service.historial(id_empresa)}
    except UndefinedTable:
        raise HTTPException(503, detail={'code': 'MIGRACION_PENDIENTE', 'message': 'Aplique la migración SaaS.'})


@router.post('/api/empresas/{id_empresa}/suscripciones', status_code=201, dependencies=[Depends(require_platform_admin)])
def asignar_suscripcion(id_empresa: int, data: SuscripcionIn, payload=Depends(require_permission('suscripciones.gestionar'))):
    return {'success': True, 'data': service.crear_suscripcion(id_empresa, data.model_dump(), payload)}


@router.post('/api/empresas/{id_empresa}/suscripciones/{id_suscripcion}/cancelar', dependencies=[Depends(require_platform_admin)])
def cancelar_suscripcion(id_empresa: int, id_suscripcion: int, data: CancelacionIn, payload=Depends(require_permission('suscripciones.gestionar'))):
    return {'success': True, 'data': service.cancelar_suscripcion(id_empresa, id_suscripcion, data.motivo, payload)}
