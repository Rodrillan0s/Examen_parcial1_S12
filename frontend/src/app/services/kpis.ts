import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export interface RolDistribucion {
  rol: string;
  cantidad: number;
}

export interface DeptoSucursal {
  departamento: string;
  cantidad: number;
}

export interface EventoActividad {
  id: number;
  modulo: string;
  accion: string;
  fecha: string;
  usuario: string;
  descripcion?: string;
}

export interface SucursalDetalle {
  id: number;
  nombre: string;
  ciudad: string;
  departamento: string;
  activo: boolean;
}

export interface DashboardMetricas {
  alcance: 'PLATAFORMA' | 'EMPRESA' | 'SUCURSAL' | 'OPERATIVO';
  titulo: string;
  nombre_empresa?: string;
  nombre_sucursal?: string;
  ciudad?: string;
  
  // Plataforma / Global
  total_empresas?: number;
  total_sucursales?: number;
  total_usuarios?: number;
  total_ciudades?: number;
  total_productos?: number;
  total_eventos_bitacora?: number;
  roles_distribucion?: RolDistribucion[];
  sucursales_por_depto?: DeptoSucursal[];
  actividad_reciente?: EventoActividad[];
  
  // Empresa / Tenant
  sucursales_detalle?: SucursalDetalle[];
  eficiencia_tienda?: string;

  // Sucursal
  personal_sucursal?: number;
  prendas_stock?: number;
  pedidos_retiro_pendientes?: number;
  ventas_hoy?: number;
  estado_operativo?: string;

  // Operativo
  ventas_turno?: number;
  prendas_consultadas?: number;
  clientes_atendidos?: number;
  estado_turno?: string;

  nivel_cumplimiento_sla?: string;
  disponibilidad_red?: string;
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