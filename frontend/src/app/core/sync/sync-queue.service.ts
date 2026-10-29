import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subject, firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../services/auth';
import { IndexedDbService, CachedRecord } from '../storage/indexed-db.service';
import { NetworkStatusService } from '../network/network-status.service';

export type SyncOperationKind =
  | 'CART_ADD_ITEM'
  | 'CART_UPDATE_QTY'
  | 'CART_REMOVE_ITEM'
  | 'CART_CLEAR'
  | 'RESERVA_SOLICITUD'
  | 'VENTA_CONTADO';

export type SyncOperationStatus =
  | 'pending'
  | 'syncing'
  | 'synced'
  | 'conflict'
  | 'reconciliation_required'
  | 'failed_retryable'
  | 'failed_permanent';

export interface PendingOperation {
  operation_id: string;
  scope_key: string;
  user_id: number;
  tenant_id: number;
  branch_id: number | null;
  kind: SyncOperationKind;
  entity_id?: string | number | null;
  summary_label: string;
  payload: Record<string, any>;
  created_at: string;
  created_at_ms: number;
  fetched_at_ms: number;
  attempt_count: number;
  next_retry_at_ms?: number | null;
  status: SyncOperationStatus;
  reconciliation_required?: boolean;
  reconciliation_note?: string | null;
  last_error?: string | null;
  conflict_code?: string | null;
  conflict_detail?: Record<string, any> | null;
  client_version?: string | number | null;
}

export interface SyncBatchItemResult {
  operation_id: string;
  kind: SyncOperationKind;
  status: SyncOperationStatus;
  reconciliation_required?: boolean;
  http_status: number;
  conflict_code?: string | null;
  message?: string;
  data?: any;
  conflict_detail?: Record<string, any> | null;
  synced_at?: string;
  idempotent_replay?: boolean;
}

export interface SyncBatchResponse {
  success: boolean;
  total: number;
  synced_count: number;
  conflict_count: number;
  reconciliation_count?: number;
  failed_count: number;
  results: SyncBatchItemResult[];
}

export interface SyncCompletedEvent extends SyncBatchResponse {
  syncedCount: number;
  conflictCount: number;
  latestCartData?: any;
}

@Injectable({
  providedIn: 'root',
})
export class SyncQueueService {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);
  private readonly idb = inject(IndexedDbService);
  private readonly network = inject(NetworkStatusService);
  private readonly syncLoteUrl = `${environment.apiUrl}/api/sync/lote`;

  readonly operations = signal<PendingOperation[]>([]);
  readonly activeOperations = computed(() => this.operations());
  readonly isSyncing = signal<boolean>(false);
  readonly lastSyncedAt = signal<string | null>(null);
  readonly lastSyncSummary = signal<string | null>(null);
  readonly lastSyncBannerMessage = signal<{ type: 'success' | 'warning' | 'error'; text: string } | null>(null);
  readonly reconciledHistory = signal<Array<Record<string, any>>>([]);

  /** Emitido cada vez que un lote termina de sincronizar operaciones */
  private readonly syncCompletedSubject = new Subject<SyncCompletedEvent>();
  readonly syncCompleted$ = this.syncCompletedSubject.asObservable();

  readonly pendingCount = computed(() =>
    this.operations().filter(
      (op) => op.status === 'pending' || op.status === 'syncing' || op.status === 'failed_retryable'
    ).length
  );

  readonly conflictCount = computed(() =>
    this.operations().filter(
      (op) => op.status === 'conflict' || op.status === 'reconciliation_required'
    ).length
  );

  readonly reconciliationCount = computed(() =>
    this.operations().filter(
      (op) => op.status === 'reconciliation_required' || Boolean(op.reconciliation_required)
    ).length
  );

  readonly totalActiveCount = computed(() => this.operations().length);

  private syncLock = false;

  constructor() {
    void this.refreshCountFromDb();

    this.network.reconnected$.subscribe((ts) => {
      if (ts > 0) {
        void this.syncNow(false);
      }
    });

    this.authService.companyChanged$.subscribe(() => {
      void this.refreshCountFromDb();
    });

    this.authService.branchChanged$.subscribe(() => {
      void this.refreshCountFromDb();
    });
  }

  public dismissBannerMessage(): void {
    this.lastSyncBannerMessage.set(null);
  }

  private getCurrentScope(overrideTenantId?: number | null, overrideBranchId?: number | null): {
    userId: number;
    tenantId: number;
    branchId: number | null;
  } {
    const user = this.authService.obtenerUsuario();
    const userId = Number(user?.id_usuario ?? user?.nro_usuario ?? 0);
    const tenantId = Number(
      overrideTenantId ??
        this.authService.getEffectiveCompanyId() ??
        user?.id_empresa ??
        1
    );
    const branchId =
      overrideBranchId !== undefined
        ? overrideBranchId
        : (this.authService.activeBranch()?.id ?? null);
    return { userId, tenantId, branchId };
  }

  /**
   * Genera un UUID v4 criptográficamente seguro para idempotencia (CU38W).
   */
  generateOperationId(): string {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID();
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  async refreshOperations(): Promise<void> {
    await this.refreshCountFromDb();
  }

  /**
   * Carga las operaciones pendientes del usuario y tenant activo desde IndexedDB.
   * Si alguna operación quedó en estado 'syncing' por cierre abrupto de la PWA,
   * la restaura automáticamente a 'pending'.
   */
  async refreshCountFromDb(): Promise<void> {
    const scope = this.getCurrentScope();
    if (!scope.userId) {
      this.operations.set([]);
      this.reconciledHistory.set([]);
      return;
    }

    const prefix = `u:${scope.userId}|`;
    const allUserOps = await this.idb.getAllByScope<PendingOperation>('pending_operations', prefix);
    const filteredOps = allUserOps.filter(
      (op) => !scope.tenantId || !op.tenant_id || Number(op.tenant_id) === Number(scope.tenantId)
    );

    const normalizedOps: PendingOperation[] = [];
    for (const op of filteredOps) {
      if (op.status === 'syncing') {
        const recovered: PendingOperation = { ...op, status: 'pending' };
        await this.idb.put('pending_operations', recovered);
        normalizedOps.push(recovered);
      } else {
        normalizedOps.push(op);
      }
    }

    normalizedOps.sort((a, b) => a.created_at_ms - b.created_at_ms);
    this.operations.set(normalizedOps);

    await this.syncProvisionalStockSnapshots(normalizedOps, scope.userId, scope.tenantId || 1);

    const historyKey = `u:${scope.userId}|e:${scope.tenantId || 1}|reconciled_sales`;
    const historyEntry = await this.idb.get<{ key: string; items: Array<Record<string, any>> }>('metadata', historyKey);
    this.reconciledHistory.set(historyEntry?.items || []);
  }

  /**
   * Calcula y persiste en `stock_snapshots` las unidades comprometidas localmente
   * por reservas y ventas en efectivo pendientes de confirmación del servidor.
   */
  private async syncProvisionalStockSnapshots(
    ops: PendingOperation[],
    userId: number,
    tenantId: number
  ): Promise<void> {
    const scopePrefix = `u:${userId}|e:${tenantId}`;
    const existingSnaps = await this.idb.getAllByScope<{ key: string }>('stock_snapshots', scopePrefix);
    for (const snap of existingSnaps) {
      if (snap?.key) {
        await this.idb.delete('stock_snapshots', snap.key);
      }
    }

    const nowMs = Date.now();
    const mapByBranchVariant = new Map<string, {
      key: string;
      scope_key: string;
      tenant_id: number;
      branch_id: number | null;
      id_variante: number;
      provisional_delta: number;
      fetched_at_ms: number;
      updated_at: string;
    }>();

    for (const op of ops) {
      if (op.kind !== 'RESERVA_SOLICITUD' && op.kind !== 'VENTA_CONTADO') continue;
      if (op.status === 'synced' || op.status === 'failed_permanent') continue;

      const branchId = op.branch_id ?? op.payload?.['id_sucursal'] ?? null;
      const scopeKey = `u:${userId}|e:${tenantId}|b:${branchId ?? 'all'}`;
      const items = Array.isArray(op.payload?.['items']) ? op.payload['items'] : [];

      for (const it of items) {
        const idVar = Number(it?.id_variante || 0);
        const cant = Number(it?.cantidad || 0);
        if (idVar <= 0 || cant <= 0) continue;

        const snapKey = `${scopeKey}_var_${idVar}`;
        const prev = mapByBranchVariant.get(snapKey);
        if (prev) {
          prev.provisional_delta += cant;
        } else {
          mapByBranchVariant.set(snapKey, {
            key: snapKey,
            scope_key: scopeKey,
            tenant_id: tenantId,
            branch_id: branchId !== null ? Number(branchId) : null,
            id_variante: idVar,
            provisional_delta: cant,
            fetched_at_ms: nowMs,
            updated_at: new Date(nowMs).toISOString(),
          });
        }
      }
    }

    for (const snap of mapByBranchVariant.values()) {
      await this.idb.put('stock_snapshots', snap);
    }
  }

  /**
   * Devuelve la cantidad provisionalmente comprometida en la cola offline para una variante
   * (en una sucursal específica o en todas las sucursales de la tienda activa).
   */
  getProvisionalDeltaForVariant(idVariante: number, branchId?: number | null): number {
    const targetVar = Number(idVariante || 0);
    if (targetVar <= 0) return 0;

    let delta = 0;
    for (const op of this.operations()) {
      if (op.kind !== 'RESERVA_SOLICITUD' && op.kind !== 'VENTA_CONTADO') continue;
      if (op.status === 'synced' || op.status === 'failed_permanent') continue;

      const opBranch = op.branch_id ?? op.payload?.['id_sucursal'] ?? null;
      if (branchId !== undefined && branchId !== null && opBranch !== null && Number(opBranch) !== Number(branchId)) {
        continue;
      }

      const items = Array.isArray(op.payload?.['items']) ? op.payload['items'] : [];
      for (const it of items) {
        if (Number(it?.id_variante) === targetVar) {
          delta += Math.max(0, Number(it?.cantidad || 0));
        }
      }
    }
    return delta;
  }

  /**
   * Devuelve un mapa `id_variante -> unidades comprometidas offline` para uso en catálogo y POS.
   */
  getProvisionalStockMap(branchId?: number | null): Map<number, number> {
    const map = new Map<number, number>();
    for (const op of this.operations()) {
      if (op.kind !== 'RESERVA_SOLICITUD' && op.kind !== 'VENTA_CONTADO') continue;
      if (op.status === 'synced' || op.status === 'failed_permanent') continue;

      const opBranch = op.branch_id ?? op.payload?.['id_sucursal'] ?? null;
      if (branchId !== undefined && branchId !== null && opBranch !== null && Number(opBranch) !== Number(branchId)) {
        continue;
      }

      const items = Array.isArray(op.payload?.['items']) ? op.payload['items'] : [];
      for (const it of items) {
        const idVar = Number(it?.id_variante || 0);
        const cant = Math.max(0, Number(it?.cantidad || 0));
        if (idVar > 0 && cant > 0) {
          map.set(idVar, (map.get(idVar) || 0) + cant);
        }
      }
    }
    return map;
  }

  async enqueueOperation(params: {
    kind: SyncOperationKind;
    summaryLabel: string;
    payload: Record<string, any>;
    entityId?: string | number | null;
    clientVersion?: string | number | null;
    tenantId?: number | null;
    branchId?: number | null;
    operationId?: string;
  }): Promise<PendingOperation> {
    return this.enqueue(params);
  }

  /**
   * Encola una operación autorizada localmente en IndexedDB.
   * Compacta operaciones redundantes sobre la misma variante del carrito si aún están en 'pending'.
   */
  async enqueue(params: {
    kind: SyncOperationKind;
    summaryLabel: string;
    payload: Record<string, any>;
    entityId?: string | number | null;
    clientVersion?: string | number | null;
    tenantId?: number | null;
    branchId?: number | null;
    operationId?: string;
  }): Promise<PendingOperation> {
    const scope = this.getCurrentScope(params.tenantId, params.branchId);
    const userId = scope.userId || 0;
    const tenantId = scope.tenantId || 1;
    const branchId = scope.branchId ?? null;
    const scopeKey = `u:${userId}|e:${tenantId}|b:${branchId ?? 'all'}`;

    await this.refreshCountFromDb();
    const currentOps = this.operations();

    // Compactación segura para carrito: si ya hay un CART_ADD_ITEM o CART_UPDATE_QTY 'pending' para la misma variante
    if (
      (params.kind === 'CART_ADD_ITEM' || params.kind === 'CART_UPDATE_QTY') &&
      params.entityId !== undefined &&
      params.entityId !== null
    ) {
      const existingPending = currentOps.find(
        (op) =>
          op.scope_key === scopeKey &&
          op.status === 'pending' &&
          (op.kind === 'CART_ADD_ITEM' || op.kind === 'CART_UPDATE_QTY') &&
          String(op.entity_id) === String(params.entityId)
      );

      if (existingPending) {
        const updatedOp: PendingOperation = {
          ...existingPending,
          summary_label: params.summaryLabel,
          payload: {
            ...existingPending.payload,
            ...params.payload,
            mode: 'SET',
          },
          client_version: params.clientVersion ?? existingPending.client_version,
        };
        await this.idb.put('pending_operations', updatedOp);
        await this.refreshCountFromDb();
        return updatedOp;
      }
    }

    // Si se elimina un item del carrito que fue agregado offline y aún no se sincronizó, cancelar ambos
    if (params.kind === 'CART_REMOVE_ITEM' && params.entityId !== undefined && params.entityId !== null) {
      const pendingAdd = currentOps.find(
        (op) =>
          op.scope_key === scopeKey &&
          op.status === 'pending' &&
          op.kind === 'CART_ADD_ITEM' &&
          String(op.entity_id) === String(params.entityId)
      );

      if (pendingAdd && Number(params.payload['id_detalle_carrito'] || 0) < 0) {
        await this.idb.delete('pending_operations', pendingAdd.operation_id);
        await this.refreshCountFromDb();
        return pendingAdd;
      }
    }

    const nowMs = Date.now();
    const nowIso = new Date(nowMs).toISOString();
    const op: PendingOperation = {
      operation_id: params.operationId || this.generateOperationId(),
      scope_key: scopeKey,
      user_id: userId,
      tenant_id: tenantId,
      branch_id: branchId,
      kind: params.kind,
      entity_id: params.entityId ?? null,
      summary_label: params.summaryLabel,
      payload: params.payload,
      created_at: nowIso,
      created_at_ms: nowMs,
      fetched_at_ms: nowMs,
      attempt_count: 0,
      next_retry_at_ms: null,
      status: 'pending',
      reconciliation_required: false,
      reconciliation_note: null,
      last_error: null,
      conflict_code: null,
      conflict_detail: null,
      client_version: params.clientVersion ?? nowIso,
    };

    await this.idb.put('pending_operations', op);
    await this.refreshCountFromDb();

    if (this.network.isOnline()) {
      void this.syncNow();
    }

    return op;
  }

  /**
   * Sincroniza en lote las operaciones pendientes o reintentables del usuario/tenant activo (CU38W).
   */
  async syncNow(force: boolean = false): Promise<SyncBatchResponse | null> {
    if (this.syncLock) return null;

    await this.refreshCountFromDb();
    const nowMs = Date.now();
    const eligible = this.operations().filter((op) => {
      if (op.status === 'pending') return true;
      if (op.status === 'failed_retryable') {
        if (force || !op.next_retry_at_ms) return true;
        return nowMs >= op.next_retry_at_ms;
      }
      return false;
    });

    if (eligible.length === 0) {
      return null;
    }

    const online = await this.network.verifyApiConnectivity(force);
    if (!online) return null;

    this.syncLock = true;
    this.isSyncing.set(true);
    this.network.setSyncingState(true);

    try {
      for (const op of eligible) {
        op.status = 'syncing';
        op.attempt_count = (op.attempt_count || 0) + 1;
        await this.idb.put('pending_operations', op);
      }
      await this.refreshCountFromDb();

      const requestBody = {
        operations: eligible.map((op) => ({
          operation_id: op.operation_id,
          kind: op.kind,
          tenant_id: op.tenant_id,
          branch_id: op.branch_id,
          entity_id: op.entity_id,
          client_version: op.client_version,
          created_at: op.created_at,
          payload: op.payload,
        })),
      };

      const response = await firstValueFrom(
        this.http.post<SyncBatchResponse>(this.syncLoteUrl, requestBody)
      );

      let latestCartData: any = undefined;

      for (const res of response.results || []) {
        const localOp = eligible.find((o) => o.operation_id === res.operation_id);
        if (!localOp) continue;

        const attemptNow = Date.now();
        await this.idb.put('sync_attempts', {
          attempt_id: `${res.operation_id}_${attemptNow}`,
          scope_key: localOp.scope_key,
          tenant_id: localOp.tenant_id,
          fetched_at_ms: attemptNow,
          operation_id: res.operation_id,
          kind: res.kind,
          status: res.status,
          http_status: res.http_status,
          conflict_code: res.conflict_code || null,
          reconciliation_required: Boolean(res.reconciliation_required || res.status === 'reconciliation_required'),
          message: res.message || null,
          attempted_at: new Date(attemptNow).toISOString(),
        });

        if (res.status === 'synced') {
          if (
            res.data &&
            (res.kind === 'CART_ADD_ITEM' ||
              res.kind === 'CART_UPDATE_QTY' ||
              res.kind === 'CART_REMOVE_ITEM' ||
              res.kind === 'CART_CLEAR')
          ) {
            latestCartData = res.data;
          }
          // Solo eliminar de pending_operations cuando existe confirmación verificable del servidor
          await this.idb.delete('pending_operations', localOp.operation_id);
        } else if (
          res.status === 'reconciliation_required' ||
          res.reconciliation_required ||
          (localOp.kind === 'VENTA_CONTADO' && res.status === 'conflict')
        ) {
          localOp.status = 'reconciliation_required';
          localOp.reconciliation_required = true;
          localOp.conflict_code = res.conflict_code || 'RECONCILIATION_REQUIRED';
          localOp.last_error = res.message || 'Incidencia en venta en efectivo: requiere conciliación de caja.';
          localOp.conflict_detail = res.conflict_detail || null;
          localOp.next_retry_at_ms = null;
          await this.idb.put('pending_operations', localOp);
        } else if (res.status === 'conflict') {
          localOp.status = 'conflict';
          localOp.reconciliation_required = false;
          localOp.conflict_code = res.conflict_code || 'CONFLICT';
          localOp.last_error = res.message || 'Conflicto detectado con el servidor.';
          localOp.conflict_detail = res.conflict_detail || null;
          localOp.next_retry_at_ms = null;
          await this.idb.put('pending_operations', localOp);
        } else {
          const isPermanent = res.status === 'failed_permanent';
          localOp.status = isPermanent ? 'failed_permanent' : 'failed_retryable';
          localOp.conflict_code = res.conflict_code || null;
          localOp.last_error = res.message || 'Error al sincronizar operación.';
          localOp.next_retry_at_ms = isPermanent
            ? null
            : Date.now() + Math.min(60_000, 2_000 * Math.pow(2, Math.max(0, (localOp.attempt_count || 1) - 1)));
          await this.idb.put('pending_operations', localOp);
        }
      }

      const nowStr = new Date().toISOString();
      this.lastSyncedAt.set(nowStr);
      if (response.synced_count > 0 || response.conflict_count > 0) {
        const text =
          response.synced_count > 0
            ? `${response.synced_count} operación(es) sincronizada(s) con éxito` +
              (response.conflict_count > 0 ? ` · ${response.conflict_count} incidencia(s)/conflicto(s)` : '')
            : `Se detectaron ${response.conflict_count} incidencia(s)/conflicto(s) al sincronizar.`;
        this.lastSyncSummary.set(text);
        this.lastSyncBannerMessage.set({
          type: response.conflict_count > 0 ? 'warning' : 'success',
          text,
        });
      }

      await this.refreshCountFromDb();

      if (response.synced_count > 0 || response.conflict_count > 0) {
        this.syncCompletedSubject.next({
          ...response,
          syncedCount: response.synced_count,
          conflictCount: response.conflict_count,
          latestCartData,
        });
      }

      return response;
    } catch (err: any) {
      for (const op of eligible) {
        op.status = 'failed_retryable';
        op.last_error = err?.error?.detail || err?.message || 'Error temporal de red al sincronizar.';
        op.next_retry_at_ms =
          Date.now() + Math.min(60_000, 2_000 * Math.pow(2, Math.max(0, (op.attempt_count || 1) - 1)));
        await this.idb.put('pending_operations', op);
      }
      await this.refreshCountFromDb();
      return null;
    } finally {
      this.syncLock = false;
      this.isSyncing.set(false);
      this.network.setSyncingState(false);
    }
  }

  /**
   * CU39W: Permite resolver un conflicto actualizando el payload y reintentando con el mismo operation_id.
   */
  async resolveConflictWithPatch(
    operationId: string,
    updatedPayloadPatch: Record<string, any>,
    updatedSummaryLabel?: string
  ): Promise<SyncBatchResponse | null> {
    const existing = await this.idb.get<PendingOperation>('pending_operations', operationId);
    if (!existing) return null;

    const updated: PendingOperation = {
      ...existing,
      summary_label: updatedSummaryLabel || existing.summary_label,
      payload: {
        ...existing.payload,
        ...updatedPayloadPatch,
      },
      status: 'pending',
      reconciliation_required: false,
      conflict_code: null,
      conflict_detail: null,
      last_error: null,
      next_retry_at_ms: null,
    };

    await this.idb.put('pending_operations', updated);
    await this.refreshCountFromDb();
    return this.syncNow(true);
  }

  async resolveConflictWithPayload(
    operationId: string,
    updatedPayloadPatch: Record<string, any>
  ): Promise<SyncBatchResponse | null> {
    return this.resolveConflictWithPatch(operationId, updatedPayloadPatch);
  }

  /**
   * CU39W: Acepta el cambio de precio informado por el servidor tanto para operaciones de carrito
   * como para reservas (`RESERVA_SOLICITUD`) o ventas en efectivo (`VENTA_CONTADO`).
   */
  async acceptConflictPriceChange(operationId: string): Promise<SyncBatchResponse | null> {
    const existing = await this.idb.get<PendingOperation>('pending_operations', operationId);
    if (!existing) return null;

    const detail = existing.conflict_detail || {};
    const targetVar = Number(detail['id_variante'] || 0);
    const currentPrice = Number(detail['current_unit_price'] || 0);

    const nextPayload: Record<string, any> = {
      ...existing.payload,
      accept_price_change: true,
    };

    if (currentPrice > 0 && nextPayload['expected_unit_price'] !== undefined) {
      nextPayload['expected_unit_price'] = currentPrice;
    }

    if (Array.isArray(nextPayload['items'])) {
      nextPayload['items'] = nextPayload['items'].map((it: any) => {
        if (targetVar > 0 && Number(it?.id_variante) === targetVar && currentPrice > 0) {
          return {
            ...it,
            expected_unit_price: currentPrice,
            precio_unitario: currentPrice,
            accept_price_change: true,
          };
        }
        return { ...it, accept_price_change: true };
      });

      if (existing.kind === 'VENTA_CONTADO') {
        const nuevoSubtotal = nextPayload['items'].reduce(
          (acc: number, it: any) =>
            acc + Number(it.expected_unit_price ?? it.precio_unitario ?? 0) * Number(it.cantidad || 1),
          0
        );
        const desc = Number(nextPayload['descuento'] || 0);
        const nuevoTotal = Math.max(0, Math.round((nuevoSubtotal - desc) * 100) / 100);
        nextPayload['expected_total'] = nuevoTotal;
        if (Number(nextPayload['monto_recibido'] || 0) < nuevoTotal) {
          nextPayload['monto_recibido'] = nuevoTotal;
        }
      }
    }

    return this.resolveConflictWithPatch(operationId, nextPayload);
  }

  /**
   * CU39W: Ajusta la cantidad solicitada al stock disponible real del servidor y reintenta la sincronización.
   */
  async adjustConflictQuantityToAvailable(operationId: string): Promise<SyncBatchResponse | null> {
    const existing = await this.idb.get<PendingOperation>('pending_operations', operationId);
    if (!existing) return null;

    const detail = existing.conflict_detail || {};
    const avail = Math.max(0, Number(detail['available_stock'] || 0));
    const targetVar = Number(detail['id_variante'] || 0);
    if (avail <= 0) return null;

    const nextPayload: Record<string, any> = { ...existing.payload };

    if (Array.isArray(nextPayload['items']) && targetVar > 0) {
      nextPayload['items'] = nextPayload['items'].map((it: any) =>
        Number(it?.id_variante) === targetVar ? { ...it, cantidad: avail } : it
      );
      if (existing.kind === 'VENTA_CONTADO') {
        const nuevoSubtotal = nextPayload['items'].reduce(
          (acc: number, it: any) =>
            acc + Number(it.expected_unit_price ?? it.precio_unitario ?? 0) * Number(it.cantidad || 1),
          0
        );
        const desc = Number(nextPayload['descuento'] || 0);
        nextPayload['expected_total'] = Math.max(0, Math.round((nuevoSubtotal - desc) * 100) / 100);
      }
    } else {
      nextPayload['cantidad'] = avail;
      nextPayload['mode'] = 'SET';
    }

    return this.resolveConflictWithPatch(
      operationId,
      nextPayload,
      `${existing.summary_label} (ajustado a ${avail} u.)`
    );
  }

  /**
   * CU39W / CU24W: Registra una incidencia de conciliación para una venta en efectivo rechazada
   * sin eliminar silenciosamente su trazabilidad. Conserva el historial auditable en IndexedDB (`metadata` y `sync_attempts`).
   */
  async reconcileCashSaleIncidence(operationId: string, resolutionNote: string): Promise<void> {
    const existing = await this.idb.get<PendingOperation>('pending_operations', operationId);
    if (!existing) return;

    const nowMs = Date.now();
    const noteClean = (resolutionNote || '').trim() || 'Conciliado manualmente en arqueo de caja.';
    const reconciledRecord = {
      operation_id: existing.operation_id,
      entity_id: existing.entity_id,
      summary_label: existing.summary_label,
      tenant_id: existing.tenant_id,
      branch_id: existing.branch_id,
      conflict_code: existing.conflict_code,
      last_error: existing.last_error,
      payload: existing.payload,
      reconciliation_note: noteClean,
      reconciled_at: new Date(nowMs).toISOString(),
    };

    const scopeKeyPrefix = `u:${existing.user_id}|e:${existing.tenant_id}|`;
    const historyKey = `${scopeKeyPrefix}reconciled_sales`;
    const prevHistory = await this.idb.get<{ key: string; items: Array<Record<string, any>> }>('metadata', historyKey);
    const items = [reconciledRecord, ...(prevHistory?.items || [])].slice(0, 50);

    await this.idb.put('metadata', {
      key: historyKey,
      scope_key: existing.scope_key,
      tenant_id: existing.tenant_id,
      fetched_at_ms: nowMs,
      items,
      updated_at: new Date(nowMs).toISOString(),
    });

    await this.idb.put('sync_attempts', {
      attempt_id: `${existing.operation_id}_reconciled_${nowMs}`,
      scope_key: existing.scope_key,
      tenant_id: existing.tenant_id,
      fetched_at_ms: nowMs,
      operation_id: existing.operation_id,
      kind: existing.kind,
      status: 'reconciled_incidence',
      http_status: 409,
      conflict_code: existing.conflict_code || 'CASH_SALE_RECONCILED',
      message: noteClean,
      attempted_at: new Date(nowMs).toISOString(),
    });

    await this.idb.delete('pending_operations', operationId);
    await this.refreshCountFromDb();
  }

  /**
   * CU39W: Permite descartar una operación en conflicto (carrito o reserva).
   * Para ventas en efectivo rechazadas (`VENTA_CONTADO` en `reconciliation_required`),
   * redirige a `reconcileCashSaleIncidence` para garantizar que jamás se eliminen silenciosamente.
   */
  async discardOperation(operationId: string, reconciliationNote?: string): Promise<void> {
    const existing = await this.idb.get<PendingOperation>('pending_operations', operationId);
    if (!existing) return;

    if (
      existing.kind === 'VENTA_CONTADO' &&
      (existing.status === 'reconciliation_required' ||
        existing.reconciliation_required ||
        existing.status === 'conflict')
    ) {
      await this.reconcileCashSaleIncidence(
        operationId,
        reconciliationNote || 'Venta en efectivo offline registrada como incidencia para arqueo/conciliación física.'
      );
      return;
    }

    await this.idb.delete('pending_operations', operationId);
    await this.refreshCountFromDb();
  }
}
