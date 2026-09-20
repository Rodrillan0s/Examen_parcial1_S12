import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
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

// ==============================================================================
// MODELOS W32: INDICADORES EMPRESARIALES AGREGADOS
// ==============================================================================

export interface KpisResumen {
  ventas: {
    cantidad_ventas: number;
    ventas_totales: number;
    ingresos_totales: number;
    ticket_promedio: number;
    ticket_minimo: number;
    ticket_maximo: number;
  };
  inventario: {
    total_productos_catalogo: number;
    total_variantes: number;
    stock_total: number;
    stock_disponible: number;
    stock_reservado: number;
    productos_stock_bajo: number;
    productos_agotados: number;
  };
  comparacion: {
    ventas_crecimiento_pct: number;
    transacciones_crecimiento_pct: number;
    ingresos_crecimiento_pct: number;
    periodo_anterior_disponible: boolean;
  };
}

export interface VentaTimelineItem {
  fecha: string;
  cantidad: number;
  total: number;
  ticket_promedio: number;
}

export interface ProductoMasVendidoItem {
  id_producto: number;
  nombre: string;
  categoria: string;
  unidades_vendidas: number;
  total_ingresos: number;
  precio_promedio: number;
  imagen_url: string;
}

export interface InventarioAlertaItem {
  id_producto: number;
  producto_nombre: string;
  sku: string;
  talla: string;
  color: string;
  sucursal_nombre: string;
  stock_actual: number;
  stock_disponible: number;
  stock_minimo: number;
  estado_alerta: 'AGOTADO' | 'BAJO_STOCK' | 'OPTIMO';
}

export interface VentaSucursalItem {
  id_sucursal: number;
  nombre_sucursal: string;
  ciudad: string;
  cantidad_ventas: number;
  total_ingresos: number;
  total_unidades: number;
  ticket_promedio: number;
}

export interface TenantSucursalItem {
  id: number;
  nombre: string;
  ciudad: string;
  direccion: string;
}

export interface TenantDashboardItem {
  id_empresa: number;
  nombre_empresa: string;
  razon_social: string;
  nit: string;
  ciudad: string;
  direccion: string;
  telefono: string;
  correo: string;
  logo: string;
  estado: string;
  total_sucursales: number;
  total_productos: number;
  total_stock_disponible: number;
  total_ventas_cantidad: number;
  total_ingresos_historico: number;
  sucursales: TenantSucursalItem[];
}

export interface RespuestaApi<T> {
  success: boolean;
  message: string;
  data: T;
}

@Injectable({
  providedIn: 'root'
})
export class KpisService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  // Estado reactivo global de tenant/tienda seleccionada
  private tiendaSeleccionadaSubject = new BehaviorSubject<TenantDashboardItem | null>(this.obtenerTiendaInicial());
  public tiendaSeleccionada$ = this.tiendaSeleccionadaSubject.asObservable();

  obtenerTiendaActual(): TenantDashboardItem | null {
    return this.tiendaSeleccionadaSubject.value;
  }

  establecerTiendaSeleccionada(tienda: TenantDashboardItem | null): void {
    this.tiendaSeleccionadaSubject.next(tienda);
    if (typeof localStorage !== 'undefined') {
      if (tienda) {
        localStorage.setItem('tenant_seleccionado', JSON.stringify(tienda));
      } else {
        localStorage.removeItem('tenant_seleccionado');
      }
    }
  }

  private obtenerTiendaInicial(): TenantDashboardItem | null {
    if (typeof localStorage !== 'undefined') {
      try {
        const stored = localStorage.getItem('tenant_seleccionado');
        return stored ? JSON.parse(stored) : null;
      } catch {
        return null;
      }
    }
    return null;
  }

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    return token
      ? new HttpHeaders({ Authorization: `Bearer ${token}` })
      : new HttpHeaders();
  }

  // Obtener listado de tiendas / tenants con métricas agregadas
  obtenerTenants(): Observable<RespuestaApi<TenantDashboardItem[]>> {
    return this.http.get<RespuestaApi<TenantDashboardItem[]>>(
      `${this.apiUrl}/api/kpis/tenants`,
      { headers: this.getHeaders() }
    );
  }

  // Compatibilidad anterior
  obtenerMetricasDashboard(id_empresa?: number): Observable<RespuestaDashboardMetricas> {
    let params = new HttpParams();
    if (id_empresa) params = params.set('id_empresa', id_empresa.toString());

    return this.http.get<RespuestaDashboardMetricas>(
      `${this.apiUrl}/api/dashboard/metricas`,
      { headers: this.getHeaders(), params }
    );
  }

  // W32: Resumen ejecutivo con variación temporal
  obtenerResumen(fecha_inicio?: string, fecha_fin?: string, id_sucursal?: number, id_empresa?: number): Observable<RespuestaApi<KpisResumen>> {
    let params = new HttpParams();
    if (fecha_inicio) params = params.set('fecha_inicio', fecha_inicio);
    if (fecha_fin) params = params.set('fecha_fin', fecha_fin);
    if (id_sucursal) params = params.set('id_sucursal', id_sucursal.toString());
    if (id_empresa) params = params.set('id_empresa', id_empresa.toString());

    return this.http.get<RespuestaApi<KpisResumen>>(
      `${this.apiUrl}/api/kpis/resumen`,
      { headers: this.getHeaders(), params }
    );
  }

  // W32: Serie temporal de ventas para gráfico de línea
  obtenerVentasTimeline(fecha_inicio?: string, fecha_fin?: string, id_sucursal?: number, id_empresa?: number): Observable<RespuestaApi<VentaTimelineItem[]>> {
    let params = new HttpParams();
    if (fecha_inicio) params = params.set('fecha_inicio', fecha_inicio);
    if (fecha_fin) params = params.set('fecha_fin', fecha_fin);
    if (id_sucursal) params = params.set('id_sucursal', id_sucursal.toString());
    if (id_empresa) params = params.set('id_empresa', id_empresa.toString());

    return this.http.get<RespuestaApi<VentaTimelineItem[]>>(
      `${this.apiUrl}/api/kpis/ventas`,
      { headers: this.getHeaders(), params }
    );
  }

  // W32: Ranking de productos con mayor recaudación
  obtenerProductosMasVendidos(fecha_inicio?: string, fecha_fin?: string, id_sucursal?: number, limit: number = 8, id_empresa?: number): Observable<RespuestaApi<ProductoMasVendidoItem[]>> {
    let params = new HttpParams().set('limit', limit.toString());
    if (fecha_inicio) params = params.set('fecha_inicio', fecha_inicio);
    if (fecha_fin) params = params.set('fecha_fin', fecha_fin);
    if (id_sucursal) params = params.set('id_sucursal', id_sucursal.toString());
    if (id_empresa) params = params.set('id_empresa', id_empresa.toString());

    return this.http.get<RespuestaApi<ProductoMasVendidoItem[]>>(
      `${this.apiUrl}/api/kpis/productos-mas-vendidos`,
      { headers: this.getHeaders(), params }
    );
  }

  // W32: Alertas de inventario crítico
  obtenerInventarioAlertas(id_sucursal?: number, id_empresa?: number): Observable<RespuestaApi<{ alertas_stock: InventarioAlertaItem[]; total_alertas: number }>> {
    let params = new HttpParams();
    if (id_sucursal) params = params.set('id_sucursal', id_sucursal.toString());
    if (id_empresa) params = params.set('id_empresa', id_empresa.toString());

    return this.http.get<RespuestaApi<{ alertas_stock: InventarioAlertaItem[]; total_alertas: number }>>(
      `${this.apiUrl}/api/kpis/inventario`,
      { headers: this.getHeaders(), params }
    );
  }

  // W32: Comparativa de ventas por sucursal
  obtenerVentasPorSucursal(fecha_inicio?: string, fecha_fin?: string, id_empresa?: number): Observable<RespuestaApi<VentaSucursalItem[]>> {
    let params = new HttpParams();
    if (fecha_inicio) params = params.set('fecha_inicio', fecha_inicio);
    if (fecha_fin) params = params.set('fecha_fin', fecha_fin);
    if (id_empresa) params = params.set('id_empresa', id_empresa.toString());

    return this.http.get<RespuestaApi<VentaSucursalItem[]>>(
      `${this.apiUrl}/api/kpis/ventas-sucursal`,
      { headers: this.getHeaders(), params }
    );
  }
}