import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface ItemElegibleDevolucion {
  id_detalle_venta: number;
  id_variante: number;
  cantidad_original: number;
  cantidad_devuelta: number;
  cantidad_elegible: number;
  precio_unitario: number;
  descuento_unitario: number;
  subtotal: number;
  precio_neto_unitario: number;
  producto_nombre: string;
  sku: string;
  talla: string;
  color: string;
  imagen_url?: string;
}

export interface ElegibilidadVentaResponse {
  venta: {
    id_venta: number;
    numero_venta: string;
    fecha_venta: string;
    subtotal: number;
    descuento: number;
    total: number;
    estado: string;
    tipo_venta: string;
    id_empresa: number;
    nombre_empresa?: string;
    id_sucursal?: number;
    nombre_sucursal?: string;
  };
  es_elegible: boolean;
  motivo_bloqueo?: string | null;
  items: ItemElegibleDevolucion[];
}

export interface ItemSolicitudDevolucion {
  id_detalle_venta: number;
  cantidad: number;
}

export interface SolicitarDevolucionPayload {
  id_venta: number;
  id_empresa?: number;
  motivo: string;
  descripcion?: string;
  evidencia_url?: string;
  items: ItemSolicitudDevolucion[];
}

export interface ItemPresencialDevolucion {
  id_detalle_venta: number;
  cantidad: number;
  condicion: 'REVENDIBLE' | 'DEFECTUOSO';
}

export interface DevolucionPresencialPayload {
  id_venta: number;
  id_sucursal?: number;
  id_empresa?: number;
  motivo: string;
  observaciones?: string;
  items: ItemPresencialDevolucion[];
  registrar_reembolso_inmediato?: boolean;
  metodo_reembolso?: string;
  referencia_reembolso?: string;
}

export interface ItemDetalleDevolucion {
  id_detalle_devolucion: number;
  id_detalle_venta: number;
  cantidad: number;
  condicion: string;
  precio_unitario: number;
  descuento_unitario: number;
  monto_reembolso: number;
  estado_item: string;
  producto_nombre: string;
  sku: string;
  talla: string;
  color: string;
  imagen_url?: string;
}

export interface DevolucionResumen {
  id_devolucion: number;
  codigo_devolucion: string;
  id_venta: number;
  numero_venta: string;
  tipo_devolucion: string;
  motivo: string;
  descripcion_cliente?: string;
  monto_reembolso: number;
  estado: string;
  fecha_devolucion: string;
  fecha_resolucion?: string;
  observaciones_resolucion?: string;
  id_sucursal?: number;
  nombre_sucursal?: string;
  cliente_nombre?: string;
  cliente_correo?: string;
  revisor_nombre?: string;
  total_prendas: number;
}

export interface DevolucionDetalleCompleto extends DevolucionResumen {
  total_venta: number;
  fecha_venta: string;
  tipo_venta: string;
  id_empresa: number;
  id_usuario_cliente: number;
  cliente_apellido?: string;
  evidencia_url?: string;
  id_usuario_revisor?: number;
  revisor_apellido?: string;
  metodo_reembolso?: string;
  referencia_reembolso?: string;
  fecha_reembolso?: string;
  items: ItemDetalleDevolucion[];
}

export interface DevolucionDetalleResponse {
  success: boolean;
  data: DevolucionDetalleCompleto;
}

export interface DevolucionesFiltros {
  page?: number;
  limit?: number;
  estado?: string;
  id_sucursal?: number;
  fecha_inicio?: string;
  fecha_fin?: string;
  busqueda?: string;
  id_empresa?: number;
}

export interface DevolucionesListResponse {
  success: boolean;
  data: DevolucionResumen[];
  total: number;
  page: number;
  limit: number;
  total_paginas: number;
}

@Injectable({
  providedIn: 'root'
})
export class DevolucionesService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl || 'http://127.0.0.1:5000'}/api/devoluciones`;

  /**
   * CU25W / CU24W: Consulta si una venta es elegible para devolución y los saldos de cada ítem.
   */
  consultarElegibilidadVenta(idVenta: number, idEmpresa?: number): Observable<ElegibilidadVentaResponse> {
    let params = new HttpParams();
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.get<ElegibilidadVentaResponse>(`${this.apiUrl}/ventas/${idVenta}/elegibilidad`, { params });
  }

  /**
   * CU25W: Cliente envía solicitud de devolución online.
   */
  solicitarDevolucion(payload: SolicitarDevolucionPayload): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/solicitudes`, payload);
  }

  /**
   * CU25W: Cliente lista sus propias devoluciones solicitadas.
   */
  obtenerMisDevoluciones(page: number = 1, limit: number = 10, idEmpresa?: number): Observable<DevolucionesListResponse> {
    let params = new HttpParams().set('page', page.toString()).set('limit', limit.toString());
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.get<DevolucionesListResponse>(`${this.apiUrl}/mis-solicitudes`, { params });
  }

  /**
   * CU25W: Cliente consulta el detalle de una solicitud propia.
   */
  obtenerMiDevolucionDetalle(idDevolucion: number, idEmpresa?: number): Observable<DevolucionDetalleResponse> {
    let params = new HttpParams();
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.get<DevolucionDetalleResponse>(`${this.apiUrl}/mis-solicitudes/${idDevolucion}`, { params });
  }

  listarMisDevoluciones(page: number = 1, limit: number = 10, idEmpresa?: number): Observable<DevolucionesListResponse> {
    return this.obtenerMisDevoluciones(page, limit, idEmpresa);
  }

  verMiDevolucion(idDevolucion: number, idEmpresa?: number): Observable<DevolucionDetalleResponse> {
    return this.obtenerMiDevolucionDetalle(idDevolucion, idEmpresa);
  }

  /**
   * CU24W: Bandeja de devoluciones para personal autorizado con filtros y paginación.
   */
  listarDevolucionesPersonal(filtros: DevolucionesFiltros = {}): Observable<DevolucionesListResponse> {
    let params = new HttpParams();
    if (filtros.page) params = params.set('page', filtros.page.toString());
    if (filtros.limit) params = params.set('limit', filtros.limit.toString());
    if (filtros.estado && filtros.estado !== 'TODOS') params = params.set('estado', filtros.estado);
    if (filtros.id_sucursal) params = params.set('id_sucursal', filtros.id_sucursal.toString());
    if (filtros.fecha_inicio) params = params.set('fecha_inicio', filtros.fecha_inicio);
    if (filtros.fecha_fin) params = params.set('fecha_fin', filtros.fecha_fin);
    if (filtros.busqueda) params = params.set('busqueda', filtros.busqueda.trim());
    if (filtros.id_empresa) params = params.set('id_empresa', filtros.id_empresa.toString());

    return this.http.get<DevolucionesListResponse>(this.apiUrl, { params });
  }

  /**
   * CU24W: Personal consulta el detalle completo de una devolución.
   */
  obtenerDetallePersonal(idDevolucion: number, idEmpresa?: number): Observable<DevolucionDetalleCompleto> {
    let params = new HttpParams();
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.get<DevolucionDetalleCompleto>(`${this.apiUrl}/${idDevolucion}`, { params });
  }

  /**
   * CU24W: Cajero o encargado registra devolución presencial directa en mostrador.
   */
  registrarDevolucionPresencial(payload: DevolucionPresencialPayload): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/presencial`, payload);
  }

  /**
   * CU24W: Dictamen formal de la solicitud (Aprobar / Rechazar).
   */
  dictaminarSolicitud(
    idDevolucion: number,
    accion: 'APROBAR' | 'RECHAZAR' | 'EN_REVISION',
    observaciones: string,
    idEmpresa?: number
  ): Observable<any> {
    const body = { accion, observaciones, id_empresa: idEmpresa };
    return this.http.post<any>(`${this.apiUrl}/${idDevolucion}/revisar`, body);
  }

  /**
   * CU24W: Registra la recepción física e inspección de prendas y actualiza stock.
   */
  registrarRecepcionPrendas(
    idDevolucion: number,
    items: Array<{ id_detalle_devolucion: number; cantidad_recibida: number; condicion: string }>,
    idSucursal?: number,
    observaciones?: string,
    idEmpresa?: number
  ): Observable<any> {
    const body = {
      id_sucursal: idSucursal,
      id_empresa: idEmpresa,
      observaciones,
      items
    };
    return this.http.post<any>(`${this.apiUrl}/${idDevolucion}/recepcion`, body);
  }

  /**
   * CU24W: Registra y confirma la liquidación del reembolso financiero.
   */
  liquidarReembolso(
    idDevolucion: number,
    metodoReembolso: string,
    referenciaReembolso: string,
    observaciones?: string,
    idEmpresa?: number
  ): Observable<any> {
    const body = {
      metodo_reembolso: metodoReembolso,
      referencia_reembolso: referenciaReembolso,
      observaciones,
      id_empresa: idEmpresa
    };
    return this.http.post<any>(`${this.apiUrl}/${idDevolucion}/reembolso`, body);
  }
}
