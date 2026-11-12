import { Injectable, PLATFORM_ID, inject, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { hasVerifiedConfirmation, OperationIdentity, sameOperationRequest, VerifiedSyncResult } from '../sync/sync-confirmation';

export type StoreName =
  | 'products'
  | 'product_details'
  | 'catalog_filters'
  | 'branches'
  | 'stock_snapshots'
  | 'cart_drafts'
  | 'pending_operations'
  | 'sync_attempts'
  | 'sync_receipts'
  | 'metadata'
  | 'pos_contingency_quotas';

export interface CachedRecord<T = any> {
  key: string;
  scope_key: string;
  user_id?: number | null;
  tenant_id: number;
  branch_id?: number | null;
  data: T;
  fetched_at: string;
  fetched_at_ms: number;
  updated_at?: string | null;
  version?: string | null;
  expires_at_ms: number;
  is_partial?: boolean;
}

export interface TenantCacheAudit {
  tenantId: number;
  totalProducts: number;
  totalDetails: number;
  totalBranches: number;
  hasFilters: boolean;
  hasTenants: boolean;
  status: 'COMPLETO' | 'PARCIAL' | 'VACIO';
  lastFetchedAt: string | null;
  lastFetchedAtMs: number;
}

export type StorageHealthStatus = 'OK' | 'QUOTA_WARNING' | 'FALLBACK_MEMORY';

const DB_NAME = 'aurora_store_pwa_db';
const DB_VERSION = 4;
const DURABLE_STORES: ReadonlySet<StoreName> = new Set(['pending_operations', 'sync_attempts', 'sync_receipts']);

const MAX_PAGES_PER_SCOPE = 40;
const MAX_DETAILS_PER_SCOPE = 150;

@Injectable({
  providedIn: 'root'
})
export class IndexedDbService {
  private platformId = inject(PLATFORM_ID);
  private dbPromise: Promise<IDBDatabase | null> | null = null;

  /**
   * Fallback para cachés descartables. Las operaciones e historias críticas
   * requieren confirmación de IndexedDB y nunca dependen de esta memoria.
   */
  private memoryFallback = new Map<StoreName, Map<string, any>>();

  public storageStatus = signal<StorageHealthStatus>('OK');
  public storageWarningMessage = signal<string | null>(null);

  constructor() {
    const stores: StoreName[] = [
      'products',
      'product_details',
      'catalog_filters',
      'branches',
      'stock_snapshots',
      'cart_drafts',
      'pending_operations',
      'sync_attempts',
      'sync_receipts',
      'metadata',
      'pos_contingency_quotas'
    ];
    for (const s of stores) {
      this.memoryFallback.set(s, new Map<string, any>());
    }
  }

  public buildPublicScopeKey(tenantId: number | null | undefined): string {
    return `public|e:${tenantId || 1}`;
  }

  public buildPrivateScopeKey(userId: number | null | undefined, tenantId: number | null | undefined, branchId?: number | null): string {
    const u = userId || 0;
    const e = tenantId || 0;
    return branchId ? `u:${u}|e:${e}|b:${branchId}` : `u:${u}|e:${e}`;
  }

  public buildUserTenantPrefix(userId: number | null | undefined, tenantId?: number | null): string {
    const u = userId || 0;
    return tenantId !== undefined && tenantId !== null ? `u:${u}|e:${tenantId}` : `u:${u}|`;
  }

  private openDb(): Promise<IDBDatabase | null> {
    if (!isPlatformBrowser(this.platformId) || typeof indexedDB === 'undefined') {
      this.storageStatus.set('FALLBACK_MEMORY');
      return Promise.resolve(null);
    }

    if (this.dbPromise) {
      return this.dbPromise;
    }

    this.dbPromise = new Promise<IDBDatabase | null>((resolve) => {
      const unavailable = () => {
        this.storageStatus.set('FALLBACK_MEMORY');
        resolve(null);
      };
      const open = (version?: number) => {
        try {
          const req = indexedDB.open(DB_NAME, version);
          req.onupgradeneeded = event => {
            this.applySchemaMigrations(req.result, event.oldVersion, event.newVersion || DB_VERSION, req.transaction);
          };
          req.onsuccess = () => {
            const db = req.result;
            const required: StoreName[] = ['products', 'product_details', 'catalog_filters', 'branches',
              'stock_snapshots', 'cart_drafts', 'pending_operations', 'sync_attempts', 'sync_receipts', 'metadata', 'pos_contingency_quotas'];
            if (required.some(store => !db.objectStoreNames.contains(store))) {
              const next = db.version + 1;
              db.close();
              open(next);
              return;
            }
            db.onversionchange = () => { db.close(); this.dbPromise = null; };
            this.storageStatus.set('OK');
            resolve(db);
          };
          req.onerror = () => {
            // Earlier releases could repair stores using a higher physical
            // version. Reopen that version, preserving every pending record.
            if (req.error?.name === 'VersionError' && version !== undefined) open();
            else unavailable();
          };
          req.onblocked = unavailable;
        } catch { unavailable(); }
      };
      open(DB_VERSION);
    });

    return this.dbPromise;
  }

  private applySchemaMigrations(
    db: IDBDatabase,
    _oldVersion: number,
    _newVersion: number,
    tx?: IDBTransaction | null
  ): void {
    const storeDefs: { name: StoreName; keyPath: string }[] = [
      { name: 'products', keyPath: 'key' },
      { name: 'product_details', keyPath: 'key' },
      { name: 'catalog_filters', keyPath: 'key' },
      { name: 'branches', keyPath: 'key' },
      { name: 'stock_snapshots', keyPath: 'key' },
      { name: 'cart_drafts', keyPath: 'key' },
      { name: 'pending_operations', keyPath: 'operation_id' },
      { name: 'sync_attempts', keyPath: 'attempt_id' },
      { name: 'sync_receipts', keyPath: 'operation_id' },
      { name: 'metadata', keyPath: 'key' },
      { name: 'pos_contingency_quotas', keyPath: 'key' }
    ];

    for (const def of storeDefs) {
      let store: IDBObjectStore;
      if (!db.objectStoreNames.contains(def.name)) {
        store = db.createObjectStore(def.name, { keyPath: def.keyPath });
      } else if (tx) {
        try {
          store = tx.objectStore(def.name);
        } catch {
          continue;
        }
      } else {
        continue;
      }

      try {
        if (!store.indexNames.contains('by_scope')) {
          store.createIndex('by_scope', 'scope_key', { unique: false });
        }
        if (!store.indexNames.contains('by_tenant')) {
          store.createIndex('by_tenant', 'tenant_id', { unique: false });
        }
        if (!store.indexNames.contains('by_fetched_at')) {
          store.createIndex('by_fetched_at', 'fetched_at_ms', { unique: false });
        }
        if (def.name === 'pending_operations' && !store.indexNames.contains('by_status')) {
          store.createIndex('by_status', 'status', { unique: false });
        }
      } catch (err) {
        console.warn(`[IndexedDB] Error al verificar índices en store ${def.name}:`, err);
      }
    }
  }

  private storageFailure(error?: unknown): Error {
    const quota = (error as DOMException | undefined)?.name === 'QuotaExceededError';
    this.storageStatus.set(quota ? 'QUOTA_WARNING' : 'FALLBACK_MEMORY');
    const message = 'No se pudo confirmar el almacenamiento local. La operación no se ha dado por guardada; conserve sus datos y reintente.';
    this.storageWarningMessage.set(message);
    return new Error(message, { cause: error });
  }

  public async put<T = any>(storeName: StoreName, value: T): Promise<void> {
    const durable = DURABLE_STORES.has(storeName);
    const keyField = storeName === 'pending_operations' || storeName === 'sync_receipts'
      ? 'operation_id' : storeName === 'sync_attempts' ? 'attempt_id' : 'key';
    const recordKey = String((value as any)?.[keyField] || '');
    const cache = () => {
      if (recordKey) this.memoryFallback.get(storeName)?.set(recordKey, structuredClone(value));
    };
    if (!durable) cache();
    const db = await this.openDb();
    if (!db) {
      if (durable) throw this.storageFailure();
      return;
    }
    await new Promise<void>((resolve, reject) => {
      let failure: Error | undefined;
      try {
        const tx = db.transaction(storeName === 'pending_operations' ? [storeName, 'sync_receipts'] : storeName,
          'readwrite', durable ? { durability: 'strict' } : undefined);
        tx.oncomplete = () => resolve();
        tx.onabort = () => durable ? reject(failure ?? this.storageFailure(tx.error)) : resolve();
        tx.onerror = () => { /* onabort reports failure after the rollback. */ };
        if (storeName === 'pending_operations') {
          const receipt = tx.objectStore('sync_receipts').get(recordKey);
          receipt.onsuccess = () => {
            try {
              if (receipt.result) {
                failure = new Error('La operación ya tiene un recibo durable; no se vuelve a crear el pendiente.');
                tx.abort();
              } else tx.objectStore(storeName).put(value);
            } catch (error) { failure = this.storageFailure(error); tx.abort(); }
          };
        } else tx.objectStore(storeName).put(value);
      } catch (error) {
        if (durable) reject(this.storageFailure(error));
        else resolve();
      }
    });
    if (storeName === 'products') {
      await this.enforceBoundedStore('products', (value as any)?.scope_key, MAX_PAGES_PER_SCOPE);
    } else if (storeName === 'product_details') {
      await this.enforceBoundedStore('product_details', (value as any)?.scope_key, MAX_DETAILS_PER_SCOPE);
    }
  }

  /** Persist evidence and retire the exact request in one durable transaction. */
  public async acknowledgeOperation(op: OperationIdentity, result: VerifiedSyncResult): Promise<void> {
    if (!hasVerifiedConfirmation(op, result)) throw new Error('La respuesta no contiene una confirmación verificable.');
    const db = await this.openDb();
    if (!db) throw this.storageFailure();
    await new Promise<void>((resolve, reject) => {
      let failure: Error | undefined;
      const tx = db.transaction(['pending_operations', 'sync_receipts', 'sync_attempts'], 'readwrite', { durability: 'strict' });
      tx.oncomplete = () => resolve();
      tx.onabort = () => reject(failure ?? this.storageFailure(tx.error));
      tx.onerror = () => { /* Wait for rollback. */ };
      const pending = tx.objectStore('pending_operations');
      const request = pending.get(op.operation_id);
      request.onsuccess = () => {
        try {
          const current = request.result as OperationIdentity | undefined;
          if (!current || !sameOperationRequest(current, op)) {
            failure = new Error('La operación local cambió durante el envío; se conserva para revisión.');
            tx.abort();
            return;
          }
          const now = Date.now();
          const evidence = { ...result, scope_key: op.scope_key, user_id: op.user_id, tenant_id: op.tenant_id,
            request: op, fetched_at_ms: now, confirmed_at: new Date(now).toISOString() };
          tx.objectStore('sync_receipts').put(evidence);
          tx.objectStore('sync_attempts').put({ ...evidence, attempt_id: `${op.operation_id}_confirmed_${now}` });
          pending.delete(op.operation_id);
        } catch (error) {
          failure = this.storageFailure(error);
          tx.abort();
        }
      };
    });
  }

  public async get<T = any>(storeName: StoreName, key: string): Promise<T | null> {
    const durable = DURABLE_STORES.has(storeName);
    const fallback = () => structuredClone(this.memoryFallback.get(storeName)?.get(key) ?? null);
    const db = await this.openDb();
    if (!db) {
      if (durable) throw this.storageFailure();
      return fallback();
    }
    return new Promise<T | null>((resolve, reject) => {
      const fail = (error?: unknown) => durable ? reject(this.storageFailure(error)) : resolve(fallback());
      try {
        const tx = db.transaction(storeName, 'readonly');
        const req = tx.objectStore(storeName).get(key);
        req.onsuccess = () => resolve(req.result ?? (durable ? null : fallback()));
        req.onerror = () => fail(req.error);
        tx.onabort = () => fail(tx.error);
      } catch (error) { fail(error); }
    });
  }

  public async getAllByScope<T = any>(storeName: StoreName, scopePrefix: string): Promise<T[]> {
    const durable = DURABLE_STORES.has(storeName);
    const filter = (items: any[]) => items.filter(item => String(item?.scope_key || '').startsWith(scopePrefix));
    const fallback = () => structuredClone(filter(Array.from(this.memoryFallback.get(storeName)?.values() ?? [])));
    const db = await this.openDb();
    if (!db) {
      if (durable) throw this.storageFailure();
      return fallback();
    }
    return new Promise<T[]>((resolve, reject) => {
      const fail = (error?: unknown) => durable ? reject(this.storageFailure(error)) : resolve(fallback());
      try {
        const tx = db.transaction(storeName, 'readonly');
        const req = tx.objectStore(storeName).getAll();
        req.onsuccess = () => {
          const records = filter(req.result || []);
          resolve(durable || records.length ? records : fallback());
        };
        req.onerror = () => fail(req.error);
        tx.onabort = () => fail(tx.error);
      } catch (error) { fail(error); }
    });
  }

  public async delete(storeName: StoreName, key: string): Promise<void> {
    if (DURABLE_STORES.has(storeName)) throw new Error('La evidencia y las operaciones pendientes requieren confirmación; no se pueden borrar directamente.');
    this.memoryFallback.get(storeName)?.delete(key);
    const db = await this.openDb();
    if (!db) return;

    await new Promise<void>((resolve) => {
      try {
        const tx = db.transaction(storeName, 'readwrite');
        tx.objectStore(storeName).delete(key);
        tx.oncomplete = () => resolve();
        tx.onerror = () => resolve();
      } catch {
        resolve();
      }
    });
  }

  /**
   * Purga cachés privados. Conserva pendientes, intentos y recibos particionados;
   * la cola solo los muestra/envía tras autenticar al mismo usuario y empresa.
   */
  public async purgePrivateData(scopePrefix?: string): Promise<void> {
    const privateStores: StoreName[] = [
      'cart_drafts',
      'products',
      'product_details',
      'branches',
      'stock_snapshots'
    ];

    for (const storeName of privateStores) {
      const mem = this.memoryFallback.get(storeName);
      if (mem) {
        for (const [k, v] of Array.from(mem.entries())) {
          const sk = String(v?.scope_key || '');
          const isPrivateRecord = sk.startsWith('u:');
          if (!scopePrefix) {
            if (isPrivateRecord || storeName === 'cart_drafts') {
              mem.delete(k);
            }
          } else if (sk.startsWith(scopePrefix)) {
            mem.delete(k);
          }
        }
      }
    }

    const db = await this.openDb();
    if (!db) return;

    for (const storeName of privateStores) {
      await new Promise<void>((resolve) => {
        try {
          const tx = db.transaction(storeName, 'readwrite');
          const store = tx.objectStore(storeName);
          const req = store.openCursor();
          req.onsuccess = () => {
            const cursor = req.result;
            if (!cursor) return;
            const val = cursor.value;
            const sk = String(val?.scope_key || '');
            const isPrivateRecord = sk.startsWith('u:');
            if (!scopePrefix) {
              if (isPrivateRecord || storeName === 'cart_drafts') {
                cursor.delete();
              }
            } else if (sk.startsWith(scopePrefix)) {
              cursor.delete();
            }
            cursor.continue();
          };
          tx.oncomplete = () => resolve();
          tx.onerror = () => resolve();
        } catch {
          resolve();
        }
      });
    }
  }

  private async enforceBoundedStore(storeName: StoreName, scopeKey: string | undefined, maxRecords: number): Promise<void> {
    if (!scopeKey) return;
    try {
      const records = await this.getAllByScope<CachedRecord>(storeName, scopeKey);
      const now = Date.now();
      const expired = records.filter((r) => r.expires_at_ms && r.expires_at_ms < now);
      for (const exp of expired) {
        await this.delete(storeName, exp.key);
      }

      const valid = records
        .filter((r) => !r.expires_at_ms || r.expires_at_ms >= now)
        .sort((a, b) => (b.fetched_at_ms || 0) - (a.fetched_at_ms || 0));

      if (valid.length > maxRecords) {
        const toRemove = valid.slice(maxRecords);
        for (const item of toRemove) {
          await this.delete(storeName, item.key);
        }
      }
    } catch {
      // Ignore housekeeping errors
    }
  }

  private async evictOldestCatalogCache(): Promise<void> {
    for (const storeName of ['products', 'product_details'] as StoreName[]) {
      const all = await this.getAllByScope<CachedRecord>(storeName, '');
      const sorted = all.sort((a, b) => (a.fetched_at_ms || 0) - (b.fetched_at_ms || 0));
      const half = Math.ceil(sorted.length / 2);
      for (let i = 0; i < half; i++) {
        await this.delete(storeName, sorted[i].key);
      }
    }
  }

  public async countByScope(storeName: StoreName, scopePrefix: string): Promise<number> {
    const items = await this.getAllByScope(storeName, scopePrefix);
    return items.length;
  }

  public async saveBranches(tenantId: number, branches: any[]): Promise<void> {
    const scopeKey = this.buildPublicScopeKey(tenantId);
    const now = Date.now();
    const nowIso = new Date(now).toISOString();
    const ttl = 24 * 60 * 60 * 1000;

    await this.put<CachedRecord>('branches', {
      key: `branches_e:${tenantId}`,
      scope_key: scopeKey,
      tenant_id: tenantId,
      data: branches,
      fetched_at: nowIso,
      fetched_at_ms: now,
      expires_at_ms: now + ttl
    });
  }

  public async getBranches<T = any>(tenantId: number): Promise<T[] | null> {
    const cached = await this.get<CachedRecord<T[]>>('branches', `branches_e:${tenantId}`);
    if (cached?.data && Array.isArray(cached.data)) {
      return cached.data;
    }
    return null;
  }

  public async auditTenantCache(tenantId: number): Promise<TenantCacheAudit> {
    const scopeKey = this.buildPublicScopeKey(tenantId);
    const now = Date.now();

    // 1. Contar productos únicos disponibles offline
    const pages = await this.getAllByScope<CachedRecord>('products', scopeKey);
    const uniqueProductIds = new Set<number>();
    let lastFetchedMs = 0;
    let lastFetchedAt: string | null = null;

    for (const page of pages) {
      if ((page.fetched_at_ms || 0) > lastFetchedMs) {
        lastFetchedMs = page.fetched_at_ms;
        lastFetchedAt = page.fetched_at;
      }
      const list = Array.isArray(page.data) ? page.data : (page.data?.data || page.data?.productos || []);
      for (const item of list) {
        const pId = item?.id_producto || item?.id;
        if (pId) uniqueProductIds.add(Number(pId));
      }
    }

    // 2. Contar detalles cacheados
    const details = await this.getAllByScope<CachedRecord>('product_details', scopeKey);
    for (const d of details) {
      if ((d.fetched_at_ms || 0) > lastFetchedMs) {
        lastFetchedMs = d.fetched_at_ms;
        lastFetchedAt = d.fetched_at;
      }
      const prod = d.data;
      const pId = prod?.id_producto || prod?.id;
      if (pId) uniqueProductIds.add(Number(pId));
    }

    // 3. Verificar filtros y categorías
    const filters = await this.get<CachedRecord>('catalog_filters', `filters_e:${tenantId}`);
    const hasFilters = Boolean(filters?.data?.data?.categorias?.length || filters?.data?.categorias?.length);
    if (filters && (filters.fetched_at_ms || 0) > lastFetchedMs) {
      lastFetchedMs = filters.fetched_at_ms;
      lastFetchedAt = filters.fetched_at;
    }

    // 4. Verificar tenants públicos
    const tenants = await this.get<CachedRecord>('catalog_filters', 'public_tenants_list');
    const hasTenants = Boolean(tenants?.data?.data?.length || tenants?.data?.length);

    // 5. Verificar sucursales
    const branches = await this.getBranches(tenantId);
    let totalBranches = branches?.length || 0;
    if (totalBranches === 0 && filters?.data?.data?.sucursales?.length) {
      totalBranches = filters.data.data.sucursales.length;
    }

    // Determinar estado de salud del almacenamiento local para este tenant
    let status: 'COMPLETO' | 'PARCIAL' | 'VACIO' = 'VACIO';
    const totalProducts = uniqueProductIds.size;
    if (totalProducts >= 4 && totalBranches >= 1 && hasFilters) {
      status = 'COMPLETO';
    } else if (totalProducts > 0 || totalBranches > 0 || hasFilters) {
      status = 'PARCIAL';
    }

    const audit: TenantCacheAudit = {
      tenantId,
      totalProducts,
      totalDetails: details.length,
      totalBranches,
      hasFilters,
      hasTenants,
      status,
      lastFetchedAt,
      lastFetchedAtMs: lastFetchedMs
    };

    // Guardar metadata del diagnóstico
    try {
      await this.put<CachedRecord>('metadata', {
        key: `cache_audit_e:${tenantId}`,
        scope_key: scopeKey,
        tenant_id: tenantId,
        data: audit,
        fetched_at: new Date(now).toISOString(),
        fetched_at_ms: now,
        expires_at_ms: now + (24 * 60 * 60 * 1000)
      });
    } catch (_) {}

    return audit;
  }
}

