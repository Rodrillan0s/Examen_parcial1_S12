import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, shareReplay, catchError, tap } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { AuthService } from '../../auth/services/auth';

export type CodigoPlan = 'BASICO' | 'PROFESIONAL';

export interface PlanSaaS {
  codigo: CodigoPlan;
  nombre: string;
  max_sucursales: number;
  reportes_generativos: boolean;
  activo: boolean;
}

export type EstadoSuscripcion =
  | 'VIGENTE'
  | 'SIN_SUSCRIPCION'
  | 'PROGRAMADA'
  | 'VENCIDA'
  | 'CANCELADA'
  | 'EMPRESA_INACTIVA';

export interface SuscripcionItem {
  id_suscripcion: number;
  id_empresa: number;
  codigo_plan: CodigoPlan;
  inicio: string;
  fin: string;
  estado: 'ACTIVA' | 'CANCELADA';
  motivo: string;
  creado_por?: string | number;
  creado_en?: string;
}

export interface PlanVigenciaData {
  id_empresa: number;
  estado: EstadoSuscripcion;
  vigente: boolean;
  id_suscripcion: number | null;
  codigo_plan: CodigoPlan | null;
  inicio: string | null;
  fin: string | null;
  limites: { sucursales_activas: number | null };
  uso: { sucursales_activas: number } | null;
  disponibles: number;
  capacidades: { reportes_generativos: boolean };
}

export interface AsignarSuscripcionPayload {
  codigo_plan: CodigoPlan;
  inicio: string;
  fin: string;
  motivo: string;
}

export interface CancelarSuscripcionPayload {
  motivo: string;
  confirmar: true;
}

@Injectable({
  providedIn: 'root'
})
export class SaasService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    return token ? new HttpHeaders({ 'Authorization': `Bearer ${token}` }) : new HttpHeaders();
  }

  /**
   * Catálogo de planes disponibles (planes.ver)
   */
  listarPlanes(): Observable<{ success: boolean; data: PlanSaaS[] }> {
    return this.http.get<{ success: boolean; data: PlanSaaS[] }>(
      `${this.apiUrl}/api/planes`,
      { headers: this.getHeaders() }
    );
  }

  /**
   * Actualizar nombre y disponibilidad de un plan (planes.gestionar + plataforma)
   */
  actualizarPlan(codigo: CodigoPlan, data: { nombre: string; activo: boolean }): Observable<{ success: boolean; data: PlanSaaS }> {
    return this.http.put<{ success: boolean; data: PlanSaaS }>(
      `${this.apiUrl}/api/planes/${codigo}`,
      data,
      { headers: this.getHeaders() }
    );
  }

  private planCache = new Map<string, { obs$: Observable<{ success: boolean; data: PlanVigenciaData }>; timestamp: number }>();
  private readonly PLAN_CACHE_TTL = 20000; // 20s en memoria

  /**
   * Consulta de plan actual, vigencia, capacidades y límites de sucursales activas (suscripciones.ver)
   * Si es administrador de plataforma, puede pasar id_empresa explícito.
   */
  consultarPlan(idEmpresa?: number, forzar: boolean = false): Observable<{ success: boolean; data: PlanVigenciaData }> {
    const cacheKey = idEmpresa ? String(idEmpresa) : 'default';
    const ahora = Date.now();
    const entry = this.planCache.get(cacheKey);

    if (!forzar && entry && (ahora - entry.timestamp < this.PLAN_CACHE_TTL)) {
      return entry.obs$;
    }

    let params = new HttpParams();
    if (idEmpresa) {
      params = params.set('id_empresa', idEmpresa.toString());
    }

    const obs$ = this.http.get<{ success: boolean; data: PlanVigenciaData }>(
      `${this.apiUrl}/api/mi-empresa/plan`,
      { headers: this.getHeaders(), params }
    ).pipe(
      shareReplay({ bufferSize: 1, refCount: false }),
      catchError((err) => {
        this.planCache.delete(cacheKey);
        throw err;
      })
    );

    this.planCache.set(cacheKey, { obs$, timestamp: ahora });
    return obs$;
  }

  invalidarCachePlan(idEmpresa?: number): void {
    if (idEmpresa) {
      this.planCache.delete(String(idEmpresa));
    } else {
      this.planCache.clear();
    }
  }

  /**
   * Historial de suscripciones de una empresa (suscripciones.ver)
   */
  obtenerHistorialSuscripciones(idEmpresa: number): Observable<{ success: boolean; data: SuscripcionItem[] }> {
    return this.http.get<{ success: boolean; data: SuscripcionItem[] }>(
      `${this.apiUrl}/api/empresas/${idEmpresa}/suscripciones`,
      { headers: this.getHeaders() }
    );
  }

  /**
   * Asignar o renovar una suscripción administrativa (suscripciones.gestionar + plataforma)
   */
  asignarSuscripcion(idEmpresa: number, payload: AsignarSuscripcionPayload): Observable<{ success: boolean; data: SuscripcionItem }> {
    return this.http.post<{ success: boolean; data: SuscripcionItem }>(
      `${this.apiUrl}/api/empresas/${idEmpresa}/suscripciones`,
      payload,
      { headers: this.getHeaders() }
    ).pipe(
      tap(() => this.invalidarCachePlan(idEmpresa))
    );
  }

  /**
   * Cancelar una suscripción administrativa activa (suscripciones.gestionar + plataforma)
   */
  cancelarSuscripcion(idEmpresa: number, idSuscripcion: number, payload: CancelarSuscripcionPayload): Observable<{ success: boolean; data: { id_suscripcion: number; estado: string } }> {
    return this.http.post<{ success: boolean; data: { id_suscripcion: number; estado: string } }>(
      `${this.apiUrl}/api/empresas/${idEmpresa}/suscripciones/${idSuscripcion}/cancelar`,
      payload,
      { headers: this.getHeaders() }
    ).pipe(
      tap(() => this.invalidarCachePlan(idEmpresa))
    );
  }
}
