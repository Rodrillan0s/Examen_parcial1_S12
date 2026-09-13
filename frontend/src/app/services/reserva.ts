import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ItemReservaPayload {
  id_variante: number;
  cantidad: number;
}

export interface CrearReservaPayload {
  id_sucursal: number;
  fecha_hora_visita: string;
  observaciones?: string;
  items: ItemReservaPayload[];
  id_empresa?: number;
}

export interface SucursalReserva {
  id_sucursal: number;
  nombre: string;
  direccion: string;
  telefono?: string;
  ciudad: string;
}

export interface ItemReservaDetalle {
  id_detalle_reserva: number;
  id_variante: number;
  cantidad: number;
  estado_prenda: string;
  id_producto: number;
  producto_nombre: string;
  precio: number;
  talla: string;
  color: string;
  codigo_hex: string;
  imagen_url?: string;
}

export interface ReservaData {
  id_reserva: number;
  codigo_reserva: string;
  fecha_reserva: string;
  fecha_hora_visita: string;
  estado: 'PENDIENTE' | 'CONFIRMADA' | 'CANCELADA' | 'ATENDIDA' | 'VENCIDA' | string;
  observaciones?: string;
  fecha_cancelacion?: string | null;
  motivo_cancelacion?: string | null;
  sucursal: SucursalReserva;
  items: ItemReservaDetalle[];
  total_prendas: number;
}

@Injectable({
  providedIn: 'root'
})
export class ReservaService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/reservas`;

  /**
   * Crea una nueva reserva para visita en sucursal con control atómico de stock.
   */
  crearReserva(payload: CrearReservaPayload): Observable<{ success: boolean; message: string; data: ReservaData }> {
    return this.http.post<{ success: boolean; message: string; data: ReservaData }>(`${this.apiUrl}`, payload);
  }

  /**
   * Obtiene la lista de reservas realizadas por el cliente autenticado.
   */
  obtenerMisReservas(idEmpresa?: number): Observable<{ success: boolean; data: ReservaData[] }> {
    let params = new HttpParams();
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.get<{ success: boolean; data: ReservaData[] }>(`${this.apiUrl}/mis-reservas`, { params });
  }

  /**
   * Obtiene la información detallada de una reserva específica.
   */
  obtenerDetalleReserva(idReserva: number, idEmpresa?: number): Observable<{ success: boolean; data: ReservaData }> {
    let params = new HttpParams();
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.get<{ success: boolean; data: ReservaData }>(`${this.apiUrl}/${idReserva}`, { params });
  }

  /**
   * Cancela una reserva activa del cliente y libera el stock reservado en inventario.
   */
  cancelarReserva(idReserva: number, motivo?: string, idEmpresa?: number): Observable<{ success: boolean; data: any }> {
    let params = new HttpParams();
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.post<{ success: boolean; data: any }>(
      `${this.apiUrl}/${idReserva}/cancelar`,
      { motivo: motivo || 'Cancelación solicitada por el cliente.' },
      { params }
    );
  }
}
