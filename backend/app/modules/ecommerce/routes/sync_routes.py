import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
from app.core.config import Config
from app.core.postgres import PostgreSQL
from app.core.security import verificar_token, tiene_permiso
from app.core.commerce_tenant import resolver_empresa_compra
from app.modules.ecommerce.repos import carrito_repos
from app.modules.reservas.repos import reserva_repos
from app.modules.pos.repos import pos_repos, caja_repos, caja_pago_repos

router = APIRouter(prefix="/api/sync", tags=["Sincronización Offline-First (PWA & Mobile)"])

# Registro en memoria de respaldo por (schema, id_usuario, id_empresa, operation_id)
# usado automáticamente si la tabla opcional t_sync_operacion aún no ha sido migrada.
_SYNC_MEMORY_LOCK = threading.Lock()
_SYNC_IDEMPOTENCY_MEMORY: Dict[tuple, Dict[str, Any]] = {}
_TABLA_SYNC_DISPONIBLE: Optional[bool] = None


def _tabla_sync_operacion_existe(schema: str) -> bool:
    global _TABLA_SYNC_DISPONIBLE
    if _TABLA_SYNC_DISPONIBLE is not None:
        return _TABLA_SYNC_DISPONIBLE
    db = PostgreSQL()
    db.create_connection()
    if not db.conn:
        return False
    try:
        row = db.execute_query(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = 't_sync_operacion' LIMIT 1;",
            (schema,),
            fetchone=True,
        )
        _TABLA_SYNC_DISPONIBLE = bool(row)
        return _TABLA_SYNC_DISPONIBLE
    except Exception:
        _TABLA_SYNC_DISPONIBLE = False
        return False
    finally:
        db.close_connection()


def limpiar_cache_sync_memoria() -> None:
    with _SYNC_MEMORY_LOCK:
        _SYNC_IDEMPOTENCY_MEMORY.clear()


class SyncOperationItemDTO(BaseModel):
    operation_id: str = Field(..., min_length=6, max_length=64, description="UUID idempotente único por operación")
    kind: str = Field(
        ...,
        description="CART_ADD_ITEM | CART_UPDATE_QTY | CART_REMOVE_ITEM | CART_CLEAR | RESERVA_SOLICITUD | VENTA_CONTADO",
    )
    tenant_id: Optional[int] = Field(None, description="ID de la empresa/tenant")
    branch_id: Optional[int] = Field(None, description="ID de sucursal cuando aplique")
    entity_id: Optional[Any] = Field(None, description="ID de entidad o clave local")
    client_version: Optional[Any] = Field(None, description="Versión o timestamp conocido por el cliente")
    created_at: Optional[str] = Field(None, description="Timestamp ISO de creación en el cliente")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Datos validados de la operación")


class SyncBatchRequestDTO(BaseModel):
    operations: List[SyncOperationItemDTO] = Field(..., min_length=1, max_length=50)


def _buscar_operacion_idempotente(schema: str, id_usuario: int, id_empresa: int, operation_id: str) -> Optional[Dict[str, Any]]:
    mem_key = (schema, int(id_usuario), int(id_empresa), str(operation_id))
    with _SYNC_MEMORY_LOCK:
        cached = _SYNC_IDEMPOTENCY_MEMORY.get(mem_key)
        if cached and cached.get("status") == "synced":
            res_copy = dict(cached)
            res_copy["idempotent_replay"] = True
            return res_copy

    if not _tabla_sync_operacion_existe(schema):
        return None

    db = PostgreSQL()
    db.create_connection()
    if not db.conn:
        return None
    try:
        row = db.execute_query(
            f"""
            SELECT response_json
            FROM {schema}.t_sync_operacion
            WHERE id_usuario = %s AND id_empresa = %s AND operation_id = %s
            LIMIT 1;
            """,
            (id_usuario, id_empresa, operation_id),
            fetchone=True,
        )
        if row and row[0]:
            stored = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            if stored.get("status") == "synced":
                stored["idempotent_replay"] = True
                with _SYNC_MEMORY_LOCK:
                    _SYNC_IDEMPOTENCY_MEMORY[mem_key] = dict(stored)
            return stored
    except Exception:
        # Si t_sync_operacion no existe aún, operar con el registro en memoria sin romper la petición
        pass
    finally:
        db.close_connection()
    return None


def _guardar_operacion_idempotente(
    schema: str,
    id_usuario: int,
    id_empresa: int,
    operation_id: str,
    kind: str,
    result_obj: Dict[str, Any],
) -> None:
    mem_key = (schema, int(id_usuario), int(id_empresa), str(operation_id))
    with _SYNC_MEMORY_LOCK:
        if len(_SYNC_IDEMPOTENCY_MEMORY) > 2000:
            _SYNC_IDEMPOTENCY_MEMORY.clear()
        _SYNC_IDEMPOTENCY_MEMORY[mem_key] = dict(result_obj)

    if not _tabla_sync_operacion_existe(schema):
        return

    db = PostgreSQL()
    db.create_connection()
    if not db.conn:
        return
    try:
        db.execute_query(
            f"""
            INSERT INTO {schema}.t_sync_operacion (
                operation_id, id_usuario, id_empresa, kind, status, http_status, conflict_code, response_json, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, now())
            ON CONFLICT (id_usuario, id_empresa, operation_id)
            DO UPDATE SET
                status = EXCLUDED.status,
                http_status = EXCLUDED.http_status,
                conflict_code = EXCLUDED.conflict_code,
                response_json = EXCLUDED.response_json,
                updated_at = now();
            """,
            (
                operation_id,
                id_usuario,
                id_empresa,
                kind,
                result_obj.get("status", "synced"),
                int(result_obj.get("http_status", 200)),
                result_obj.get("conflict_code"),
                json.dumps(result_obj),
            ),
            commit=True,
        )
    except Exception:
        pass
    finally:
        db.close_connection()


def _obtener_stock_sucursal_variante(schema: str, id_variante: int, id_sucursal: int, id_empresa: int) -> int:
    db = PostgreSQL()
    db.create_connection()
    if not db.conn:
        return 0
    try:
        row = db.execute_query(
            f"""
            SELECT COALESCE(SUM(GREATEST(0, inv.stock_disponible)), 0)
            FROM {schema}.t_inventario inv
            JOIN {schema}.t_sucursal s ON s.id_sucursal = inv.id_sucursal
            WHERE inv.id_variante = %s
              AND inv.id_sucursal = %s
              AND s.id_empresa = %s
              AND COALESCE(s.activo, TRUE) = TRUE
              AND (s.estado IS NULL OR s.estado::text IN ('true', 'TRUE', 't', '1', 'ACTIVO', 'ACTIVA'))
              AND COALESCE(inv.estado, TRUE) = TRUE;
            """,
            (id_variante, id_sucursal, id_empresa),
            fetchone=True,
        )
        return int(row[0]) if row and row[0] is not None else 0
    finally:
        db.close_connection()


def _verificar_sucursal_activa_empresa(schema: str, id_sucursal: int, id_empresa: int) -> Optional[Dict[str, Any]]:
    if id_sucursal <= 0:
        return None
    db = PostgreSQL()
    db.create_connection()
    if not db.conn:
        return None
    try:
        row = db.execute_query(
            f"""
            SELECT id_sucursal, nombre, activo, estado
            FROM {schema}.t_sucursal
            WHERE id_sucursal = %s AND id_empresa = %s
            LIMIT 1;
            """,
            (id_sucursal, id_empresa),
            fetchone=True,
        )
        if not row:
            return None
        activo_col = bool(row[2]) if row[2] is not None else True
        estado_val = row[3]
        if isinstance(estado_val, bool):
            estado_ok = estado_val
        elif estado_val is not None:
            estado_ok = str(estado_val).upper() in ("ACTIVO", "TRUE", "1", "ACTIVA")
        else:
            estado_ok = True
        activa = activo_col and estado_ok
        return {
            "id_sucursal": int(row[0]),
            "nombre": row[1],
            "activa": activa,
        }
    finally:
        db.close_connection()


def _resolver_metodo_pago_efectivo(schema: str, requested_id_metodo: Optional[int] = None) -> Dict[str, Any]:
    """
    Resuelve o valida el método de pago para ventas offline.
    Si requested_id_metodo apunta a un método electrónico (TARJETA, QR, PAYPAL), lo retorna con su tipo real
    para que el validador lo rechace con PAYMENT_REQUIRES_ONLINE.
    Si no se especificó id_metodo_pago o se pidió EFECTIVO, retorna el método EFECTIVO activo.
    """
    db = PostgreSQL()
    db.create_connection()
    if not db.conn:
        raise RuntimeError("No se pudo conectar a PostgreSQL para validar método de pago.")
    try:
        if requested_id_metodo and int(requested_id_metodo) > 0:
            row = db.execute_query(
                f"""
                SELECT id_metodo_pago, nombre, UPPER(tipo), estado
                FROM {schema}.t_metodo_pago
                WHERE id_metodo_pago = %s
                LIMIT 1;
                """,
                (int(requested_id_metodo),),
                fetchone=True,
            )
            if row:
                return {
                    "id_metodo_pago": int(row[0]),
                    "codigo": str(row[2]).upper(),
                    "nombre": row[1],
                    "tipo": str(row[2]).upper(),
                    "activo": bool(row[3]),
                }

        row_ef = db.execute_query(
            f"""
            SELECT id_metodo_pago, nombre, UPPER(tipo), estado
            FROM {schema}.t_metodo_pago
            WHERE UPPER(tipo) = 'EFECTIVO'
              AND COALESCE(estado, TRUE) = TRUE
            ORDER BY id_metodo_pago ASC
            LIMIT 1;
            """,
            fetchone=True,
        )
        if row_ef:
            return {
                "id_metodo_pago": int(row_ef[0]),
                "codigo": "EFECTIVO",
                "nombre": row_ef[1],
                "tipo": "EFECTIVO",
                "activo": bool(row_ef[3]),
            }

        # Si el entorno de pruebas aislado aún no tiene la semilla EFECTIVO en t_metodo_pago, crearla
        ins = db.execute_query(
            f"""
            INSERT INTO {schema}.t_metodo_pago (nombre, tipo, estado)
            VALUES ('Efectivo en Caja', 'EFECTIVO', TRUE)
            RETURNING id_metodo_pago, nombre, tipo, estado;
            """,
            fetchone=True,
            commit=True,
        )
        return {
            "id_metodo_pago": int(ins[0]),
            "codigo": "EFECTIVO",
            "nombre": ins[1],
            "tipo": "EFECTIVO",
            "activo": bool(ins[3]),
        }
    finally:
        db.close_connection()


def _procesar_operacion_individual(op: SyncOperationItemDTO, token_data: dict) -> Dict[str, Any]:
    schema = Config.SCHEMA or "comercio"
    id_usuario = int(token_data.get("nro_usuario") or token_data.get("id_usuario") or 0)
    if not id_usuario:
        return {
            "operation_id": op.operation_id,
            "kind": op.kind,
            "status": "failed_permanent",
            "http_status": 401,
            "conflict_code": "UNAUTHORIZED",
            "message": "Sesión no válida o expirada.",
        }

    kind = (op.kind or "").strip().upper()
    payload = op.payload or {}

    # 1. Resolver y autorizar empresa (el tenant_id del cliente NUNCA sustituye la autoridad del servidor)
    requested_tenant = op.tenant_id or payload.get("id_empresa")
    if requested_tenant is not None:
        try:
            requested_tenant = int(requested_tenant)
        except (TypeError, ValueError):
            requested_tenant = None

    try:
        empresa_id = resolver_empresa_compra(token_data, requested_tenant)
    except HTTPException as he:
        return {
            "operation_id": op.operation_id,
            "kind": kind or op.kind,
            "status": "conflict" if he.status_code in (403, 409) else "failed_permanent",
            "http_status": he.status_code,
            "conflict_code": "TENANT_FORBIDDEN",
            "message": str(he.detail),
        }
    except Exception as e:
        logger.warning(f"Error resolviendo tenant en sync: {e}")
        return {
            "operation_id": op.operation_id,
            "kind": kind or op.kind,
            "status": "failed_permanent",
            "http_status": 400,
            "conflict_code": "INVALID_TENANT",
            "message": str(e),
        }

    # 2. Verificar idempotencia (si ya se sincronizó con éxito antes, devolver resultado previo sin re-ejecutar)
    prev = _buscar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id)
    if prev and prev.get("status") == "synced":
        return prev

    try:
        # ======================================================================
        # CASO 1: CARRITO — AGREGAR / FIJAR CANTIDAD DE PRENDA (CU08W)
        # ======================================================================
        if kind == "CART_ADD_ITEM":
            id_variante = int(payload.get("id_variante") or 0)
            cantidad = int(payload.get("cantidad") or 1)
            expected_price = payload.get("expected_unit_price")
            mode = str(payload.get("mode") or "ADD").upper()

            if id_variante <= 0 or cantidad <= 0:
                return {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "failed_permanent",
                    "http_status": 400,
                    "conflict_code": "INVALID_PAYLOAD",
                    "message": "Variante y cantidad (> 0) son obligatorias.",
                }

            var_data = carrito_repos.obtener_datos_variante_tenant(id_variante, empresa_id)
            if not var_data:
                res_conf = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "conflict",
                    "http_status": 409,
                    "conflict_code": "PRODUCT_INACTIVE",
                    "message": "La prenda seleccionada no existe o no pertenece a esta tienda.",
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                return res_conf

            if not var_data["producto_activo"] or not var_data["variante_activa"]:
                res_conf = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "conflict",
                    "http_status": 409,
                    "conflict_code": "PRODUCT_INACTIVE",
                    "message": f"La prenda '{var_data['producto_nombre']}' fue desactivada mientras estabas sin conexión.",
                    "conflict_detail": {"id_variante": id_variante, "producto_nombre": var_data["producto_nombre"]},
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                return res_conf

            if expected_price is not None:
                try:
                    exp_p = round(float(expected_price), 2)
                    cur_p = round(float(var_data["precio_vigente"]), 2)
                    if abs(exp_p - cur_p) >= 0.01 and not payload.get("accept_price_change"):
                        res_conf = {
                            "operation_id": op.operation_id,
                            "kind": kind,
                            "status": "conflict",
                            "http_status": 409,
                            "conflict_code": "PRICE_CHANGED",
                            "message": f"El precio de '{var_data['producto_nombre']}' cambió de Bs. {exp_p:.2f} a Bs. {cur_p:.2f}.",
                            "conflict_detail": {
                                "id_variante": id_variante,
                                "producto_nombre": var_data["producto_nombre"],
                                "expected_unit_price": exp_p,
                                "current_unit_price": cur_p,
                            },
                        }
                        _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                        return res_conf
                except (TypeError, ValueError):
                    pass

            stock_disp = carrito_repos.obtener_stock_total_variante(id_variante, empresa_id)
            if stock_disp < cantidad:
                res_conf = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "conflict",
                    "http_status": 409,
                    "conflict_code": "STOCK_INSUFFICIENT",
                    "message": (
                        f"Stock insuficiente para '{var_data['producto_nombre']}'. "
                        f"Solicitaste {cantidad} y hay {stock_disp} disponible(s)."
                    ),
                    "conflict_detail": {
                        "id_variante": id_variante,
                        "producto_nombre": var_data["producto_nombre"],
                        "requested_quantity": cantidad,
                        "available_stock": stock_disp,
                    },
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                return res_conf

            # Si mode == 'SET', fijar la cantidad exacta para evitar duplicar en reintentos
            if mode == "SET":
                carrito_actual = carrito_repos.consultar_carrito_completo(id_usuario, empresa_id)
                existente = next(
                    (it for it in carrito_actual.get("items", []) if int(it["id_variante"]) == id_variante),
                    None,
                )
                if existente:
                    carrito = carrito_repos.actualizar_cantidad_item(
                        id_usuario=id_usuario,
                        id_empresa=empresa_id,
                        id_detalle_carrito=int(existente["id_detalle_carrito"]),
                        nueva_cantidad=cantidad,
                    )
                else:
                    carrito = carrito_repos.agregar_item_al_carrito(
                        id_usuario=id_usuario,
                        id_empresa=empresa_id,
                        id_variante=id_variante,
                        cantidad=cantidad,
                    )
            else:
                try:
                    carrito = carrito_repos.agregar_item_al_carrito(
                        id_usuario=id_usuario,
                        id_empresa=empresa_id,
                        id_variante=id_variante,
                        cantidad=cantidad,
                    )
                except ValueError as ve:
                    res_conf = {
                        "operation_id": op.operation_id,
                        "kind": kind,
                        "status": "conflict",
                        "http_status": 409,
                        "conflict_code": "STOCK_INSUFFICIENT",
                        "message": str(ve),
                        "conflict_detail": {
                            "id_variante": id_variante,
                            "available_stock": stock_disp,
                        },
                    }
                    _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                    return res_conf

            res_ok = {
                "operation_id": op.operation_id,
                "kind": kind,
                "status": "synced",
                "http_status": 200,
                "conflict_code": None,
                "message": "Prenda sincronizada en tu bolsa de compras.",
                "data": carrito,
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "idempotent_replay": False,
            }
            _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_ok)
            return res_ok

        # ======================================================================
        # CASO 2: CARRITO — ACTUALIZAR CANTIDAD (CU08W)
        # ======================================================================
        elif kind == "CART_UPDATE_QTY":
            id_detalle = int(payload.get("id_detalle_carrito") or 0)
            id_variante = int(payload.get("id_variante") or 0)
            cantidad = int(payload.get("cantidad") or 1)

            if cantidad <= 0:
                return {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "failed_permanent",
                    "http_status": 400,
                    "conflict_code": "INVALID_PAYLOAD",
                    "message": "La cantidad debe ser mayor a 0.",
                }

            # Si el ítem se creó offline con id_detalle negativo, resolver por id_variante
            if id_detalle <= 0 and id_variante > 0:
                carrito_actual = carrito_repos.consultar_carrito_completo(id_usuario, empresa_id)
                existente = next(
                    (it for it in carrito_actual.get("items", []) if int(it["id_variante"]) == id_variante),
                    None,
                )
                if existente:
                    id_detalle = int(existente["id_detalle_carrito"])
                else:
                    sub_op = SyncOperationItemDTO(
                        operation_id=op.operation_id,
                        kind="CART_ADD_ITEM",
                        tenant_id=empresa_id,
                        payload={"id_variante": id_variante, "cantidad": cantidad, "mode": "SET"},
                    )
                    return _procesar_operacion_individual(sub_op, token_data)

            try:
                carrito = carrito_repos.actualizar_cantidad_item(
                    id_usuario=id_usuario,
                    id_empresa=empresa_id,
                    id_detalle_carrito=id_detalle,
                    nueva_cantidad=cantidad,
                )
            except ValueError as ve:
                stock_disp = carrito_repos.obtener_stock_total_variante(id_variante, empresa_id) if id_variante > 0 else 0
                res_conf = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "conflict",
                    "http_status": 409,
                    "conflict_code": "STOCK_INSUFFICIENT",
                    "message": str(ve),
                    "conflict_detail": {
                        "id_detalle_carrito": id_detalle,
                        "id_variante": id_variante,
                        "requested_quantity": cantidad,
                        "available_stock": stock_disp,
                    },
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                return res_conf

            res_ok = {
                "operation_id": op.operation_id,
                "kind": kind,
                "status": "synced",
                "http_status": 200,
                "conflict_code": None,
                "message": "Cantidad actualizada en tu bolsa de compras.",
                "data": carrito,
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "idempotent_replay": False,
            }
            _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_ok)
            return res_ok

        # ======================================================================
        # CASO 3: CARRITO — ELIMINAR PRENDA (CU08W)
        # ======================================================================
        elif kind == "CART_REMOVE_ITEM":
            id_detalle = int(payload.get("id_detalle_carrito") or 0)
            id_variante = int(payload.get("id_variante") or 0)

            if id_detalle <= 0 and id_variante > 0:
                carrito_actual = carrito_repos.consultar_carrito_completo(id_usuario, empresa_id)
                existente = next(
                    (it for it in carrito_actual.get("items", []) if int(it["id_variante"]) == id_variante),
                    None,
                )
                if existente:
                    id_detalle = int(existente["id_detalle_carrito"])

            if id_detalle > 0:
                carrito = carrito_repos.eliminar_item_del_carrito(
                    id_usuario=id_usuario,
                    id_empresa=empresa_id,
                    id_detalle_carrito=id_detalle,
                )
            else:
                carrito = carrito_repos.consultar_carrito_completo(id_usuario, empresa_id)

            res_ok = {
                "operation_id": op.operation_id,
                "kind": kind,
                "status": "synced",
                "http_status": 200,
                "conflict_code": None,
                "message": "Prenda eliminada de la bolsa.",
                "data": carrito,
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "idempotent_replay": False,
            }
            _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_ok)
            return res_ok

        # ======================================================================
        # CASO 4: CARRITO — VACIAR BOLSA (CU08W)
        # ======================================================================
        elif kind == "CART_CLEAR":
            carrito = carrito_repos.vaciar_carrito_cliente(id_usuario, empresa_id)
            res_ok = {
                "operation_id": op.operation_id,
                "kind": kind,
                "status": "synced",
                "http_status": 200,
                "conflict_code": None,
                "message": "Bolsa de compras vaciada.",
                "data": carrito,
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "idempotent_replay": False,
            }
            _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_ok)
            return res_ok

        # ======================================================================
        # CASO 5: RESERVA — SOLICITUD PENDIENTE VALIDADA Y CONFIRMADA ONLINE (CU10W)
        # ======================================================================
        elif kind == "RESERVA_SOLICITUD":
            # Regla #6: Nunca procesar cobros electrónicos offline; reservas desde cola deben ser sin pago
            if payload.get("con_pago"):
                return {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "conflict",
                    "http_status": 409,
                    "conflict_code": "PAYMENT_REQUIRES_ONLINE",
                    "message": "Las reservas con pago anticipado requieren validación interactiva en línea.",
                }

            id_sucursal = int(payload.get("id_sucursal") or op.branch_id or 0)
            items = payload.get("items") or []
            if id_sucursal <= 0 or not isinstance(items, list) or len(items) == 0:
                return {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "failed_permanent",
                    "http_status": 400,
                    "conflict_code": "INVALID_PAYLOAD",
                    "message": "Sucursal e ítems de la reserva son obligatorios.",
                }

            from app.modules.saas.services.saas_services import exigir_vigencia
            try:
                exigir_vigencia(empresa_id)
            except HTTPException as he:
                return {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "conflict" if he.status_code in (403, 409) else "failed_permanent",
                    "http_status": he.status_code,
                    "conflict_code": "TENANT_FORBIDDEN",
                    "message": str(he.detail),
                }

            suc_info = _verificar_sucursal_activa_empresa(schema, id_sucursal, empresa_id)
            if not suc_info or not suc_info["activa"]:
                res_conf = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "conflict",
                    "http_status": 409,
                    "conflict_code": "BRANCH_INACTIVE",
                    "message": "La sucursal seleccionada para la reserva no está activa o no pertenece a esta tienda.",
                    "conflict_detail": {"id_sucursal": id_sucursal},
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                return res_conf

            accept_price_change_global = bool(payload.get("accept_price_change"))
            items_limpios: List[Dict[str, Any]] = []

            for raw_item in items:
                id_var = int(raw_item.get("id_variante") or 0)
                cant = int(raw_item.get("cantidad") or 0)
                if id_var <= 0 or cant <= 0:
                    return {
                        "operation_id": op.operation_id,
                        "kind": kind,
                        "status": "failed_permanent",
                        "http_status": 400,
                        "conflict_code": "INVALID_PAYLOAD",
                        "message": "Cada prenda reservada debe tener variante y cantidad (> 0).",
                    }

                var_data = carrito_repos.obtener_datos_variante_tenant(id_var, empresa_id)
                if not var_data or not var_data["producto_activo"] or not var_data["variante_activa"]:
                    nombre_p = var_data["producto_nombre"] if var_data else f"Variante #{id_var}"
                    res_conf = {
                        "operation_id": op.operation_id,
                        "kind": kind,
                        "status": "conflict",
                        "http_status": 409,
                        "conflict_code": "PRODUCT_INACTIVE",
                        "message": f"La prenda '{nombre_p}' ya no se encuentra disponible para reserva.",
                        "conflict_detail": {"id_variante": id_var, "producto_nombre": nombre_p},
                    }
                    _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                    return res_conf

                exp_price = raw_item.get("expected_unit_price", payload.get("expected_unit_price"))
                accept_item_price = accept_price_change_global or bool(raw_item.get("accept_price_change"))
                if exp_price is not None and not accept_item_price:
                    try:
                        exp_p = round(float(exp_price), 2)
                        cur_p = round(float(var_data["precio_vigente"]), 2)
                        if abs(exp_p - cur_p) >= 0.01:
                            res_conf = {
                                "operation_id": op.operation_id,
                                "kind": kind,
                                "status": "conflict",
                                "http_status": 409,
                                "conflict_code": "PRICE_CHANGED",
                                "message": (
                                    f"El precio de '{var_data['producto_nombre']}' cambió de "
                                    f"Bs. {exp_p:.2f} a Bs. {cur_p:.2f} antes de confirmar tu reserva."
                                ),
                                "conflict_detail": {
                                    "id_variante": id_var,
                                    "producto_nombre": var_data["producto_nombre"],
                                    "expected_unit_price": exp_p,
                                    "current_unit_price": cur_p,
                                },
                            }
                            _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                            return res_conf
                    except (TypeError, ValueError):
                        pass

                stock_suc = _obtener_stock_sucursal_variante(schema, id_var, id_sucursal, empresa_id)
                if stock_suc < cant:
                    res_conf = {
                        "operation_id": op.operation_id,
                        "kind": kind,
                        "status": "conflict",
                        "http_status": 409,
                        "conflict_code": "STOCK_INSUFFICIENT",
                        "message": (
                            f"Stock insuficiente en sucursal '{suc_info['nombre']}' para '{var_data['producto_nombre']}'. "
                            f"Solicitaste {cant} y hay {stock_suc} disponible(s)."
                        ),
                        "conflict_detail": {
                            "id_variante": id_var,
                            "producto_nombre": var_data["producto_nombre"],
                            "id_sucursal": id_sucursal,
                            "requested_quantity": cant,
                            "available_stock": stock_suc,
                        },
                    }
                    _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                    return res_conf

                items_limpios.append({"id_variante": id_var, "cantidad": cant})

            try:
                reserva = reserva_repos.crear_reserva(
                    id_usuario=id_usuario,
                    id_empresa=empresa_id,
                    datos={
                        "id_sucursal": id_sucursal,
                        "fecha_hora_visita": payload.get("fecha_hora_visita"),
                        "observaciones": payload.get("observaciones"),
                        "items": items_limpios,
                        "con_pago": False,
                        "monto_pagado": 0.0,
                    },
                )
            except ValueError as ve:
                res_conf = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "conflict",
                    "http_status": 409,
                    "conflict_code": "STOCK_INSUFFICIENT",
                    "message": str(ve),
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_conf)
                return res_conf
            except HTTPException as he:
                return {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "conflict" if he.status_code in (403, 409) else "failed_permanent",
                    "http_status": he.status_code,
                    "conflict_code": "TENANT_FORBIDDEN",
                    "message": str(he.detail),
                }

            res_ok = {
                "operation_id": op.operation_id,
                "kind": kind,
                "status": "synced",
                "http_status": 201,
                "conflict_code": None,
                "message": f"Reserva {reserva.get('codigo_reserva')} confirmada en línea exitosamente.",
                "data": reserva,
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "idempotent_replay": False,
            }
            _guardar_operacion_idempotente(schema, id_usuario, empresa_id, op.operation_id, kind, res_ok)
            return res_ok

        # ======================================================================
        # CASO 6: POS / CAJA — VENTA DE CONTADO EN EFECTIVO OFFLINE (CU24W)
        # ======================================================================
        elif kind == "VENTA_CONTADO":
            # 1. Validar rol y permisos RBAC de Punto de Venta / Caja en servidor
            roles_usuario = {str(r).upper() for r in (token_data.get("roles") or [])}
            rol_principal = str(token_data.get("nombre_rol") or token_data.get("rol") or "").upper()
            if rol_principal:
                roles_usuario.add(rol_principal)

            tiene_acceso_pos = (
                tiene_permiso(token_data, "pos.vender")
                or tiene_permiso(token_data, "pos.cobrar")
                or tiene_permiso(token_data, "caja.ver")
                or bool(roles_usuario.intersection({"ADMIN_EMPRESA", "ADMINISTRADOR", "SUPERADMIN", "CAJERO", "VENDEDOR", "ENCARGADO"}))
            )
            if not tiene_acceso_pos or (roles_usuario == {"CLIENTE"}):
                return {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "conflict",
                    "http_status": 403,
                    "conflict_code": "ROLE_FORBIDDEN",
                    "message": "Acceso denegado. No posee permisos para registrar ventas en Punto de Venta (POS).",
                }

            # 2. Autorizar tenant y sucursal del empleado/cajero
            from app.core.tenant_guard import resolver_tenant_operacion, obtener_sucursales_autorizadas
            from app.modules.saas.services.saas_services import exigir_vigencia
            try:
                empresa_pos = resolver_tenant_operacion(token_data, requested_tenant or empresa_id)
                exigir_vigencia(empresa_pos)
            except HTTPException as he:
                return {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "failed_permanent",
                    "http_status": he.status_code,
                    "conflict_code": "TENANT_FORBIDDEN",
                    "message": str(he.detail),
                }

            id_sucursal = int(payload.get("id_sucursal") or op.branch_id or token_data.get("id_sucursal") or 0)
            suc_info = _verificar_sucursal_activa_empresa(schema, id_sucursal, empresa_pos)
            if not suc_info or not suc_info["activa"]:
                res_inc = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "reconciliation_required",
                    "reconciliation_required": True,
                    "http_status": 409,
                    "conflict_code": "BRANCH_INACTIVE",
                    "message": "La sucursal de la venta en efectivo no está activa o no pertenece a la empresa.",
                    "conflict_detail": {"id_sucursal": id_sucursal, "reconciliation_required": True},
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_inc)
                return res_inc

            suc_permitidas = obtener_sucursales_autorizadas(token_data)
            if suc_permitidas is not None and id_sucursal not in suc_permitidas:
                return {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "failed_permanent",
                    "http_status": 403,
                    "conflict_code": "TENANT_FORBIDDEN",
                    "message": "No tiene autorización para registrar ventas en esta sucursal.",
                }

            # 3. Prohibir estrictamente pagos electrónicos offline (solo EFECTIVO)
            metodo_tipo = str(payload.get("metodo_tipo") or payload.get("metodo_pago") or "EFECTIVO").strip().upper()
            req_id_metodo = payload.get("id_metodo_pago")
            metodo_info = _resolver_metodo_pago_efectivo(schema, req_id_metodo)
            if metodo_tipo != "EFECTIVO" or metodo_info["tipo"] != "EFECTIVO":
                res_qr = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "reconciliation_required",
                    "reconciliation_required": True,
                    "http_status": 409,
                    "conflict_code": "PAYMENT_REQUIRES_ONLINE",
                    "message": (
                        f"El método de pago '{metodo_tipo if metodo_tipo != 'EFECTIVO' else metodo_info['tipo']}' "
                        "no está permitido en modo offline. Solo se admiten ventas de contado en EFECTIVO."
                    ),
                    "conflict_detail": {"reconciliation_required": True, "tipo_detectado": metodo_tipo},
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_qr)
                return res_qr

            # 4. Validar descuento manual si existe
            descuento = round(float(payload.get("descuento") or 0.0), 2)
            if descuento < 0:
                descuento = 0.0
            if descuento > 0 and not (
                tiene_permiso(token_data, "pos.descuento")
                or bool(roles_usuario.intersection({"ADMIN_EMPRESA", "ADMINISTRADOR", "SUPERADMIN", "ENCARGADO"}))
            ):
                res_inc = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "reconciliation_required",
                    "reconciliation_required": True,
                    "http_status": 403,
                    "conflict_code": "DISCOUNT_FORBIDDEN",
                    "message": "Incidencia en venta offline: el usuario no posee permiso 'pos.descuento' para aplicar descuento.",
                    "conflict_detail": {"descuento": descuento, "reconciliation_required": True},
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_inc)
                return res_inc

            # 5. Validar ítems, vigencia de prendas, precios y stock físico en la sucursal
            items_raw = payload.get("items") or []
            if not isinstance(items_raw, list) or len(items_raw) == 0:
                return {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "failed_permanent",
                    "http_status": 400,
                    "conflict_code": "INVALID_PAYLOAD",
                    "message": "La venta debe incluir al menos una prenda.",
                }

            accept_price_change_global = bool(payload.get("accept_price_change"))
            items_pos: List[Dict[str, int]] = []
            subtotal_servidor = 0.0

            for raw_item in items_raw:
                id_var = int(raw_item.get("id_variante") or 0)
                cant = int(raw_item.get("cantidad") or 0)
                if id_var <= 0 or cant <= 0:
                    return {
                        "operation_id": op.operation_id,
                        "kind": kind,
                        "status": "failed_permanent",
                        "http_status": 400,
                        "conflict_code": "INVALID_PAYLOAD",
                        "message": "Variante y cantidad (> 0) son obligatorias en cada línea de venta.",
                    }

                var_data = carrito_repos.obtener_datos_variante_tenant(id_var, empresa_pos)
                if not var_data or not var_data["producto_activo"] or not var_data["variante_activa"]:
                    nombre_p = var_data["producto_nombre"] if var_data else f"Variante #{id_var}"
                    res_inc = {
                        "operation_id": op.operation_id,
                        "kind": kind,
                        "status": "reconciliation_required",
                        "reconciliation_required": True,
                        "http_status": 409,
                        "conflict_code": "PRODUCT_INACTIVE",
                        "message": (
                            f"Incidencia de conciliación en venta en efectivo: la prenda '{nombre_p}' "
                            "fue desactivada antes de sincronizar."
                        ),
                        "conflict_detail": {
                            "id_variante": id_var,
                            "producto_nombre": nombre_p,
                            "reconciliation_required": True,
                        },
                    }
                    _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_inc)
                    return res_inc

                cur_p = round(float(var_data["precio_vigente"]), 2)
                exp_price = raw_item.get("expected_unit_price", raw_item.get("precio_unitario"))
                accept_item_price = accept_price_change_global or bool(raw_item.get("accept_price_change"))
                if exp_price is not None and not accept_item_price:
                    try:
                        exp_p = round(float(exp_price), 2)
                        if abs(exp_p - cur_p) >= 0.01:
                            res_inc = {
                                "operation_id": op.operation_id,
                                "kind": kind,
                                "status": "reconciliation_required",
                                "reconciliation_required": True,
                                "http_status": 409,
                                "conflict_code": "PRICE_CHANGED",
                                "message": (
                                    f"Incidencia de conciliación en venta en efectivo: el precio oficial de "
                                    f"'{var_data['producto_nombre']}' cambió de Bs. {exp_p:.2f} a Bs. {cur_p:.2f}."
                                ),
                                "conflict_detail": {
                                    "id_variante": id_var,
                                    "producto_nombre": var_data["producto_nombre"],
                                    "expected_unit_price": exp_p,
                                    "current_unit_price": cur_p,
                                    "reconciliation_required": True,
                                },
                            }
                            _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_inc)
                            return res_inc
                    except (TypeError, ValueError):
                        pass

                stock_suc = _obtener_stock_sucursal_variante(schema, id_var, id_sucursal, empresa_pos)
                if stock_suc < cant:
                    res_inc = {
                        "operation_id": op.operation_id,
                        "kind": kind,
                        "status": "reconciliation_required",
                        "reconciliation_required": True,
                        "http_status": 409,
                        "conflict_code": "STOCK_INSUFFICIENT",
                        "message": (
                            f"Incidencia de conciliación en venta en efectivo: stock insuficiente para "
                            f"'{var_data['producto_nombre']}' ({var_data['talla_nombre']} / {var_data['color_nombre']}). "
                            f"Vendido offline: {cant}, stock confirmado en sucursal: {stock_suc}."
                        ),
                        "conflict_detail": {
                            "id_variante": id_var,
                            "producto_nombre": var_data["producto_nombre"],
                            "id_sucursal": id_sucursal,
                            "requested_quantity": cant,
                            "available_stock": stock_suc,
                            "reconciliation_required": True,
                        },
                    }
                    _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_inc)
                    return res_inc

                subtotal_servidor = round(subtotal_servidor + round(cur_p * cant, 2), 2)
                items_pos.append({"id_variante": id_var, "cantidad": cant})

            total_servidor = round(subtotal_servidor - descuento, 2)
            if total_servidor <= 0:
                res_inc = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "reconciliation_required",
                    "reconciliation_required": True,
                    "http_status": 409,
                    "conflict_code": "INVALID_TOTAL",
                    "message": "El descuento supera o iguala el subtotal oficial de la venta.",
                    "conflict_detail": {
                        "subtotal": subtotal_servidor,
                        "descuento": descuento,
                        "reconciliation_required": True,
                    },
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_inc)
                return res_inc

            monto_recibido_raw = payload.get("monto_recibido")
            monto_recibido = round(float(monto_recibido_raw), 2) if monto_recibido_raw is not None else total_servidor
            if monto_recibido < total_servidor:
                res_inc = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "reconciliation_required",
                    "reconciliation_required": True,
                    "http_status": 409,
                    "conflict_code": "MONTO_INSUFICIENTE",
                    "message": (
                        f"Incidencia de conciliación: el efectivo recibido (Bs. {monto_recibido:.2f}) "
                        f"es menor al total oficial calculado por el servidor (Bs. {total_servidor:.2f})."
                    ),
                    "conflict_detail": {
                        "monto_recibido": monto_recibido,
                        "total_actual": total_servidor,
                        "reconciliation_required": True,
                    },
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_inc)
                return res_inc

            # 6. Resolver sesión activa de caja para el cajero en la sucursal
            sesion_activa = caja_repos.obtener_sesion_activa_usuario(id_usuario, id_sucursal)
            if not sesion_activa:
                res_inc = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "reconciliation_required",
                    "reconciliation_required": True,
                    "http_status": 409,
                    "conflict_code": "CAJA_CERRADA",
                    "message": (
                        "Incidencia de conciliación: no tienes una sesión de caja ABIERTA en esta sucursal. "
                        "Abre tu turno de caja y pulsa 'Reintentar' para asentar la venta en efectivo."
                    ),
                    "conflict_detail": {
                        "id_sucursal": id_sucursal,
                        "id_sesion_caja_original": payload.get("id_sesion_caja"),
                        "reconciliation_required": True,
                    },
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_inc)
                return res_inc

            id_sesion_activa = int(sesion_activa["id_sesion_caja"])
            id_cliente_pos = payload.get("id_cliente")
            if id_cliente_pos is not None:
                try:
                    id_cliente_pos = int(id_cliente_pos)
                except (TypeError, ValueError):
                    id_cliente_pos = None

            # 7. Ejecutar registro transaccional de venta POS + cobro en efectivo
            try:
                venta_res = pos_repos.ejecutar_registro_venta_pos(
                    id_sesion_caja=id_sesion_activa,
                    id_usuario=id_usuario,
                    id_sucursal=id_sucursal,
                    id_empresa=empresa_pos,
                    id_cliente=id_cliente_pos,
                    descuento=descuento,
                    items=items_pos,
                )
            except ValueError as ve:
                res_inc = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "reconciliation_required",
                    "reconciliation_required": True,
                    "http_status": 409,
                    "conflict_code": "STOCK_INSUFFICIENT",
                    "message": f"Incidencia en venta en efectivo: {str(ve)}",
                    "conflict_detail": {"id_sucursal": id_sucursal, "reconciliation_required": True},
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_inc)
                return res_inc

            try:
                ref_offline = f"OFFLINE-{op.operation_id[:8].upper()}"
                pago_res = caja_pago_repos.ejecutar_pago_caja(
                    id_venta=int(venta_res["id_venta"]),
                    id_usuario=id_usuario,
                    id_sucursal=id_sucursal,
                    id_empresa=empresa_pos,
                    id_sesion_caja=id_sesion_activa,
                    id_metodo_pago=int(metodo_info["id_metodo_pago"]),
                    monto_recibido=monto_recibido,
                    referencia_externa=ref_offline,
                    datos_facturacion=payload.get("datos_facturacion"),
                    desglose_recibido=payload.get("desglose_recibido") or [],
                    desglose_cambio=payload.get("desglose_cambio") or [],
                )
            except Exception as pago_err:
                # Compensación transaccional: si el cobro falla, revertir la venta pendiente para no dejar stock descontado
                try:
                    pos_repos.anular_venta_pendiente_pos(
                        id_venta=int(venta_res["id_venta"]),
                        id_usuario=id_usuario,
                        id_sucursal=id_sucursal,
                        id_empresa=empresa_pos,
                        motivo=f"Reversión automática por fallo al asentar cobro offline: {str(pago_err)}",
                    )
                except Exception:
                    pass
                res_inc = {
                    "operation_id": op.operation_id,
                    "kind": kind,
                    "status": "reconciliation_required",
                    "reconciliation_required": True,
                    "http_status": 409,
                    "conflict_code": "PAYMENT_REGISTRATION_ERROR",
                    "message": f"Incidencia al registrar cobro en efectivo: {str(pago_err)}",
                    "conflict_detail": {"reconciliation_required": True},
                }
                _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_inc)
                return res_inc

            combined_data = {
                **venta_res,
                **pago_res,
                "estado_venta": "PAGADO",
                "estado": "PAGADO",
                "referencia_offline": f"OFFLINE-{op.operation_id[:8].upper()}",
            }
            res_ok = {
                "operation_id": op.operation_id,
                "kind": kind,
                "status": "synced",
                "reconciliation_required": False,
                "http_status": 200,
                "conflict_code": None,
                "message": f"Venta de contado en efectivo #{venta_res.get('numero_venta')} sincronizada y cobrada.",
                "data": combined_data,
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "idempotent_replay": False,
            }
            _guardar_operacion_idempotente(schema, id_usuario, empresa_pos, op.operation_id, kind, res_ok)
            return res_ok

        else:
            return {
                "operation_id": op.operation_id,
                "kind": kind,
                "status": "failed_permanent",
                "http_status": 400,
                "conflict_code": "UNSUPPORTED_OPERATION",
                "message": f"Tipo de operación '{kind}' no soportado en la cola de sincronización.",
            }

    except HTTPException as he:
        return {
            "operation_id": op.operation_id,
            "kind": kind,
            "status": "conflict" if he.status_code in (403, 409) else "failed_retryable",
            "http_status": he.status_code,
            "conflict_code": "SERVER_REJECTED",
            "message": str(he.detail),
        }
    except Exception as e:
        logger.warning(f"Error resolviendo tenant en sync: {e}")
        return {
            "operation_id": op.operation_id,
            "kind": kind,
            "status": "failed_retryable",
            "http_status": 500,
            "conflict_code": "SERVER_ERROR",
            "message": f"Error al procesar operación: {str(e)}",
        }


@router.get("/ping", summary="Comprobación rápida de conectividad real con la API (0 consultas SQL)")
def sync_ping():
    return {
        "success": True,
        "status": "ONLINE",
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


def _ejecutar_lote_sync(body: SyncBatchRequestDTO, token_data: dict) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    synced_count = 0
    conflict_count = 0
    reconciliation_count = 0
    failed_count = 0

    for op in body.operations:
        res = _procesar_operacion_individual(op, token_data)
        st = res.get("status")
        if st == "synced":
            synced_count += 1
        elif st in ("conflict", "reconciliation_required"):
            conflict_count += 1
            if st == "reconciliation_required" or res.get("reconciliation_required"):
                reconciliation_count += 1
        else:
            failed_count += 1
        results.append(res)

    return {
        "success": True,
        "total": len(results),
        "synced_count": synced_count,
        "conflict_count": conflict_count,
        "reconciliation_count": reconciliation_count,
        "failed_count": failed_count,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }


@router.post("/lote", summary="CU38W / CU39W: Procesar lote de operaciones offline (reservas, ventas en efectivo y carrito)")
def sync_lote_batch(
    body: SyncBatchRequestDTO,
    token_data: dict = Depends(verificar_token),
):
    return _ejecutar_lote_sync(body, token_data)


@router.post("/operations", summary="CU38W / CU39W: Alias compatible para procesar lote de operaciones offline")
def sync_operations_batch(
    body: SyncBatchRequestDTO,
    token_data: dict = Depends(verificar_token),
):
    return _ejecutar_lote_sync(body, token_data)
