import { Injectable, PLATFORM_ID, inject, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

export type StoreName =
  | 'products'
  | 'product_details'
  | 'catalog_filters'
  | 'branches'
  | 'stock_snapshots'
  | 'cart_drafts'
  | 'pending_operations'
  | 'sync_attempts'
  | 'metadata';

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

export type StorageHealthStatus = 'OK' | 'QUOTA_WARNING' | 'FALLBACK_MEMORY';

const DB_NAME = 'aurora_store_pwa_db';
const DB_VERSION = 3;

const MAX_PAGES_PER_SCOPE = 20;
const MAX_DETAILS_PER_SCOPE = 60;

@Injectable({
  providedIn: 'root'
})
export class IndexedDbService {
  private platformId = inject(PLATFORM_ID);
  private dbPromise: Promise<IDBDatabase | null> | null = null;

  /**
   * Fallback seguro en memoria cuando IndexedDB está bloqueado (modo incógnito estricto,
   * cuota agotada o entorno de pruebas sin IDB nativo).
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
      'metadata'
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
      try {
        const req = indexedDB.open(DB_NAME, DB_VERSION);

        req.onupgradeneeded = (event: IDBVersionChangeEvent) => {
          const db = (event.target as IDBOpenDBRequest).result;
          const tx = (event.target as IDBOpenDBRequest).transaction;
          this.applySchemaMigrations(db, event.oldVersion, event.newVersion || DB_VERSION, tx);
        };

        req.onsuccess = () => {
          const db = req.result;
          const requiredStores: StoreName[] = [
            'products',
            'product_details',
            'catalog_filters',
            'branches',
            'stock_snapshots',
            'cart_drafts',
            'pending_operations',
            'sync_attempts',
            'metadata'
          ];
          const missing = requiredStores.filter((s) => !db.objectStoreNames.contains(s));
          if (missing.length > 0) {
            console.warn('[IndexedDB] Almacenes faltantes detectados en versión ' + db.version + ':', missing);
            db.close();
            this.dbPromise = null;
            const nextVersion = db.version + 1;
            const upReq = indexedDB.open(DB_NAME, nextVersion);
            upReq.onupgradeneeded = (ev) => {
              this.applySchemaMigrations(upReq.result, ev.oldVersion, nextVersion, upReq.transaction);
            };
            upReq.onsuccess = () => {
              this.storageStatus.set('OK');
              resolve(upReq.result);
            };
            upReq.onerror = () => {
              this.storageStatus.set('FALLBACK_MEMORY');
              resolve(null);
            };
            return;
          }

          db.onversionchange = () => {
            db.close();
            this.dbPromise = null;
          };
          this.storageStatus.set('OK');
          resolve(db);
        };

        req.onerror = () => {
          this.storageStatus.set('FALLBACK_MEMORY');
          this.storageWarningMessage.set(
            'El almacenamiento local del navegador está restringido. AuroraStore continuará operando en modo online con memoria temporal.'
          );
          resolve(null);
        };

        req.onblocked = () => {
          this.storageStatus.set('FALLBACK_MEMORY');
          resolve(null);
        };
      } catch {
        this.storageStatus.set('FALLBACK_MEMORY');
        resolve(null);
      }
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
      { name: 'metadata', keyPath: 'key' }
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

  public async put<T = any>(storeName: StoreName, value: T): Promise<void> {
    const keyField = storeName === 'pending_operations' ? 'operation_id' : storeName === 'sync_attempts' ? 'attempt_id' : 'key';
    const recordKey = String((value as any)?.[keyField] || '');
    if (recordKey) {
      this.memoryFallback.get(storeName)?.set(recordKey, structuredClone ? structuredClone(value) : JSON.parse(JSON.stringify(value)));
    }

    const db = await this.openDb();
    if (!db) return;

    await new Promise<void>((resolve) => {
      try {
        const tx = db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        store.put(value);
        tx.oncomplete = () => resolve();
        tx.onerror = () => {
          const errName = tx.error?.name || '';
          if (errName === 'QuotaExceededError') {
            this.storageStatus.set('QUOTA_WARNING');
            this.storageWarningMessage.set(
              'Espacio local casi lleno. Se limpiaron cachés antiguos automáticamente; tus operaciones pendientes están protegidas.'
            );
            this.evictOldestCatalogCache().finally(() => resolve());
          } else {
            resolve();
          }
        };
      } catch {
        resolve();
      }
    });

    if (storeName === 'products') {
      await this.enforceBoundedStore('products', (value as any)?.scope_key, MAX_PAGES_PER_SCOPE);
    } else if (storeName === 'product_details') {
      await this.enforceBoundedStore('product_details', (value as any)?.scope_key, MAX_DETAILS_PER_SCOPE);
    }
  }

  public async get<T = any>(storeName: StoreName, key: string): Promise<T | null> {
    const db = await this.openDb();
    if (!db) {
      const item = this.memoryFallback.get(storeName)?.get(key) || null;
      return item ? JSON.parse(JSON.stringify(item)) : null;
    }

    return new Promise<T | null>((resolve) => {
      try {
        const tx = db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const req = store.get(key);
        req.onsuccess = () => {
          resolve(req.result ?? this.memoryFallback.get(storeName)?.get(key) ?? null);
        };
        req.onerror = () => {
          resolve(this.memoryFallback.get(storeName)?.get(key) ?? null);
        };
      } catch {
        resolve(this.memoryFallback.get(storeName)?.get(key) ?? null);
      }
    });
  }

  public async getAllByScope<T = any>(storeName: StoreName, scopePrefix: string): Promise<T[]> {
    const db = await this.openDb();
    if (!db) {
      const map = this.memoryFallback.get(storeName);
      if (!map) return [];
      const results: T[] = [];
      for (const val of map.values()) {
        if (String(val?.scope_key || '').startsWith(scopePrefix)) {
          results.push(JSON.parse(JSON.stringify(val)));
        }
      }
      return results;
    }

    return new Promise<T[]>((resolve) => {
      try {
        const tx = db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const req = store.getAll();
        req.onsuccess = () => {
          const all = (req.result || []) as any[];
          const filtered = all.filter((item) => String(item?.scope_key || '').startsWith(scopePrefix));
          if (!filtered.length && this.memoryFallback.get(storeName)?.size) {
            const map = this.memoryFallback.get(storeName)!;
            const memFiltered: T[] = [];
            for (const val of map.values()) {
              if (String(val?.scope_key || '').startsWith(scopePrefix)) {
                memFiltered.push(JSON.parse(JSON.stringify(val)));
              }
            }
            if (memFiltered.length) return resolve(memFiltered);
          }
          resolve(filtered);
        };
        req.onerror = () => {
          const map = this.memoryFallback.get(storeName);
          if (!map) return resolve([]);
          const results: T[] = [];
          for (const val of map.values()) {
            if (String(val?.scope_key || '').startsWith(scopePrefix)) {
              results.push(JSON.parse(JSON.stringify(val)));
            }
          }
          resolve(results);
        };
      } catch {
        resolve([]);
      }
    });
  }

  public async delete(storeName: StoreName, key: string): Promise<void> {
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
   * Purga rigurosamente todos los datos privados de usuario/tenant al cerrar sesión,
   * cambiar de cuenta o recibir 401, impidiendo cualquier fuga entre tenants o usuarios.
   */
  public async purgePrivateData(scopePrefix?: string): Promise<void> {
    const privateStores: StoreName[] = [
      'cart_drafts',
      'pending_operations',
      'sync_attempts',
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
            if (isPrivateRecord || storeName === 'cart_drafts' || storeName === 'pending_operations' || storeName === 'sync_attempts') {
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
              if (isPrivateRecord || storeName === 'cart_drafts' || storeName === 'pending_operations' || storeName === 'sync_attempts') {
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
}

