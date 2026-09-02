import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export interface IncidentePorTipo {
  tipo: string;
  cantidad: number;
}

export interface TallerEficiente {
  taller: string;
  tiempo_promedio_min: number;
}

export interface TiempoOperativo {
  promedio_asignacion_minutos: number;
  promedio_llegada_minutos: number;
}

export interface PuntoMapaCalor {
  lat: number;
  lng: number;
  tipo: string;
}

export interface DashboardMetricas {
  incidentes_por_tipo: IncidentePorTipo[];
  casos_cancelados: number;
  total_casos_historicos: number;
  talleres_eficientes: TallerEficiente[];
  tiempos_operativos: TiempoOperativo;
  nivel_cumplimiento_sla: string;
  mapa_calor: PuntoMapaCalor[];
}

export interface RespuestaDashboardMetricas {
  success: boolean;
  message: string;
  data: DashboardMetricas;
}

@Injectable({
  providedIn: 'root'
})
export class KpisService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();

    return token
      ? new HttpHeaders({ Authorization: `Bearer ${token}` })
      : new HttpHeaders();
  }

  obtenerMetricasDashboard(): Observable<RespuestaDashboardMetricas> {
    return this.http.get<RespuestaDashboardMetricas>(
      `${this.apiUrl}/api/dashboard/metricas`,
      { headers: this.getHeaders() }
    );
  }
}