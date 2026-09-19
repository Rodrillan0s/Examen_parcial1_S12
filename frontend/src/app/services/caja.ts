import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Denominacion {
  id_denominacion: number;
  valor: number;
  moneda: string;
  tipo: 'BILLETE' | 'MONEDA';
  orden: number;
}

export interface CajaEstadoResponse {
  success: boolean;
  tiene_sesion_activa: boolean;
  caja_asignada?: {
    id_caja: number;
    codigo_caja: string;
    nombre: string;
    id_sucursal: number;
    sucursal_nombre?: string;
  };
  sesion_activa?: {
    id_sesion_caja: number;
    id_caja: number;
    codigo_caja: string;
    nombre_caja: string;
    id_sucursal: number;
    sucursal_nombre: string;
    monto_inicial: number;
    fecha_apertura: string;
    cajero_nombre: string;
    id_cajero: number;
  } | null;
}

export interface ConteoItemPayload {
  id_denominacion: number;
  cantidad: number;
}

export interface AbrirCajaPayload {
  id_caja: number;
  id_sucursal?: number;
  id_empresa?: number;
  conteo?: ConteoItemPayload[];
  conteo_items?: ConteoItemPayload[];
  monto_inicial?: number;
  observacion?: string;
  observaciones?: string;
}

export interface DenominacionEsperada {
  id_denominacion: number;
  valor: number;
  moneda: string;
  tipo: string;
  orden: number;
  cantidad_apertura: number;
  cantidad_recibida: number;
  cantidad_cambio: number;
  cantidad_esperada: number;
  subtotal_esperado: number;
  cantidad_contada?: number;
  subtotal_contado?: number;
  diferencia_unidades?: number;
}

export interface ResumenCajaResponse {
  success: boolean;
  resumen: {
    id_sesion_caja: number;
    estado: string;
    fecha_apertura: string;
    fecha_cierre?: string | null;
    monto_inicial: number;
    ventas_efectivo: number;
    ventas_tarjeta: number;
    ventas_electronicas: number;
    desglose_pagos: Record<string, number>;
    efectivo_esperado: number;
    efectivo_contado?: number | null;
    diferencia?: number | null;
    total_ventas: number;
    cant_ventas: number;
    cant_pagadas: number;
    cant_pendientes: number;
    denominaciones_esperadas?: DenominacionEsperada[];
  };
}

export interface CerrarCajaPayload {
  id_sesion_caja: number;
  conteo?: ConteoItemPayload[];
  conteo_items?: ConteoItemPayload[];
  observacion?: string;
  observaciones?: string;
}

export interface ProductoPos {
  id_producto: number;
  nombre: string;
  codigo?: string;
  precio_base: number;
  imagen_url?: string;
  categoria_nombre?: string;
  tiene_variantes: boolean;
  stock_total_sucursal: number;
}

export interface VariantePos {
  id_variante: number;
  id_producto: number;
  sku: string;
  codigo_barras?: string;
  precio: number;
  talla_nombre?: string;
  color_nombre?: string;
  color_hex?: string;
  stock_disponible: number;
}

export interface ClientePos {
  id_cliente: number;
  nombre: string;
  apellido: string;
  nombre_completo: string;
  nit_ci?: string;
  correo?: string;
  telefono?: string;
}

export interface ItemVentaPayload {
  id_variante: number;
  cantidad: number;
}

export interface RegistrarVentaPayload {
  id_sesion_caja: number;
  id_cliente?: number | null;
  id_empresa?: number;
  id_sucursal?: number;
  items: ItemVentaPayload[];
  descuento: number;
  observaciones?: string;
}

export interface VentaPosItem {
  id_venta: number;
  codigo_venta: string;
  fecha: string;
  cliente: string;
  nit_ci?: string;
  cajero: string;
  total: number;
  subtotal: number;
  descuento: number;
  estado: string;
  cant_items: number;
}

export interface MetodoPagoPos {
  id_metodo_pago: number;
  nombre: string;
  tipo: string;
}

export interface VentaParaPago {
  id_venta: number;
  codigo_venta: string;
  fecha: string;
  estado: string;
  total: number;
  subtotal: number;
  descuento: number;
  id_cliente?: number | null;
  cliente_nombre?: string;
  cliente_correo?: string;
  nit_ci?: string;
  razon_social?: string;
  correo_facturacion?: string;
  tipo_documento?: string;
  items: Array<{
    id_detalle_venta: number;
    producto_nombre: string;
    sku: string;
    cantidad: number;
    precio_unitario: number;
    subtotal: number;
    talla?: string;
    color?: string;
  }>;
}

export interface DesgloseDenominacionPayload {
  id_denominacion: number;
  valor: number;
  cantidad: number;
  subtotal: number;
}

export interface ProcesarPagoCajaPayload {
  id_venta: number;
  id_metodo_pago: number;
  monto_recibido?: number;
  referencia_externa?: string;
  razon_social?: string;
  nit_ci?: string;
  correo_facturacion?: string;
  desglose_recibido?: DesgloseDenominacionPayload[];
  desglose_cambio?: DesgloseDenominacionPayload[];
}

export interface ResultadoPagoCaja {
  success: boolean;
  message: string;
  id_pago: number;
  id_venta: number;
  total: number;
  monto_recibido: number;
  cambio: number;
  metodo_pago: string;
  fecha_pago: string;
  estado_venta: string;
  desglose_recibido?: DesgloseDenominacionPayload[];
  desglose_cambio?: DesgloseDenominacionPayload[];
}

export interface DatosComprobanteVenta {
  id_venta: number;
  codigo_venta: string;
  fecha: string;
  estado: string;
  total: number;
  subtotal: number;
  descuento: number;
  nit_ci?: string;
  razon_social?: string;
  correo_facturacion?: string;
  tipo_documento?: string;
  id_cliente?: number | null;
  cliente_nombre?: string;
  cliente_correo?: string;
  items: Array<{
    id_detalle_venta: number;
    producto_nombre: string;
    sku: string;
    cantidad: number;
    precio_unitario: number;
    subtotal: number;
    talla?: string;
    color?: string;
  }>;
  pago?: {
    id_pago: number;
    monto: number;
    metodo: string;
    fecha: string;
    estado: string;
  };
}

export interface EmitirComprobantePayload {
  razon_social: string;
  nit_ci: string;
  correo_facturacion?: string;
  tipo_documento?: string;
  enviar_correo?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class CajaService {
  private http = inject(HttpClient);
  private cajaApiUrl = `${environment.apiUrl}/api/caja`;
  private posApiUrl = `${environment.apiUrl}/api/pos`;
  private comprobantesApiUrl = `${environment.apiUrl}/api/comprobantes`;

  // --- MÓDULO CAJA ---
  obtenerDenominaciones(): Observable<{ success: boolean; denominaciones: Denominacion[] }> {
    return this.http.get<{ success: boolean; denominaciones: Denominacion[] }>(`${this.cajaApiUrl}/denominaciones`);
  }

  obtenerEstadoCaja(idSucursal?: number, idEmpresa?: number): Observable<CajaEstadoResponse> {
    let params = new HttpParams();
    if (idSucursal) params = params.set('id_sucursal', idSucursal.toString());
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.get<CajaEstadoResponse>(`${this.cajaApiUrl}/estado`, { params });
  }

  abrirCaja(payload: AbrirCajaPayload): Observable<any> {
    return this.http.post<any>(`${this.cajaApiUrl}/abrir`, payload);
  }

  obtenerResumenCaja(idSesionCaja: number): Observable<ResumenCajaResponse> {
    return this.http.get<ResumenCajaResponse>(`${this.cajaApiUrl}/resumen?id_sesion_caja=${idSesionCaja}`);
  }

  cerrarCaja(payload: CerrarCajaPayload): Observable<any> {
    return this.http.post<any>(`${this.cajaApiUrl}/cerrar`, payload);
  }

  // --- MÓDULO POS ---
  buscarProductos(query?: string, idCategoria?: number, idSucursal?: number, idEmpresa?: number): Observable<{ success: boolean; productos: ProductoPos[]; total: number }> {
    let params = new HttpParams();
    if (query && query.trim()) params = params.set('q', query.trim());
    if (idCategoria) params = params.set('id_categoria', idCategoria.toString());
    if (idSucursal) params = params.set('id_sucursal', idSucursal.toString());
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.get<{ success: boolean; productos: ProductoPos[]; total: number }>(`${this.posApiUrl}/productos`, { params });
  }

  obtenerVariantesProducto(idProducto: number, idSucursal?: number, idEmpresa?: number): Observable<{ success: boolean; variantes: VariantePos[] }> {
    let params = new HttpParams();
    if (idSucursal) params = params.set('id_sucursal', idSucursal.toString());
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.get<{ success: boolean; variantes: VariantePos[] }>(`${this.posApiUrl}/productos/${idProducto}/variantes`, { params });
  }

  buscarClientes(query: string, idEmpresa?: number): Observable<{ success: boolean; clientes: ClientePos[] }> {
    let params = new HttpParams().set('q', query.trim());
    if (idEmpresa) params = params.set('id_empresa', idEmpresa.toString());
    return this.http.get<{ success: boolean; clientes: ClientePos[] }>(`${this.posApiUrl}/clientes/buscar`, { params });
  }

  registrarVentaPos(payload: RegistrarVentaPayload): Observable<any> {
    return this.http.post<any>(`${this.posApiUrl}/ventas`, payload);
  }

  obtenerHistorialVentas(idSesionCaja: number): Observable<{ success: boolean; ventas: VentaPosItem[]; total: number }> {
    return this.http.get<{ success: boolean; ventas: VentaPosItem[]; total: number }>(`${this.posApiUrl}/ventas?id_sesion_caja=${idSesionCaja}`);
  }

  obtenerDetalleVenta(idVenta: number): Observable<any> {
    return this.http.get<any>(`${this.posApiUrl}/ventas/${idVenta}`);
  }

  // --- MÓDULO W28: PAGO EN CAJA ---
  obtenerMetodosPagoCaja(): Observable<{ success: boolean; metodos: MetodoPagoPos[] }> {
    return this.http.get<{ success: boolean; metodos: MetodoPagoPos[] }>(`${this.cajaApiUrl}/pagos/metodos`);
  }

  obtenerVentaParaPago(idVenta: number): Observable<{ success: boolean; venta: VentaParaPago }> {
    return this.http.get<{ success: boolean; venta: VentaParaPago }>(`${this.cajaApiUrl}/pagos/venta/${idVenta}`);
  }

  procesarPagoCaja(payload: ProcesarPagoCajaPayload): Observable<ResultadoPagoCaja> {
    return this.http.post<ResultadoPagoCaja>(`${this.cajaApiUrl}/pagos/procesar`, payload);
  }

  // --- MÓDULO W29: EMISIÓN COMPROBANTE ---
  obtenerDatosComprobanteVenta(idVenta: number): Observable<{ success: boolean; venta: DatosComprobanteVenta }> {
    return this.http.get<{ success: boolean; venta: DatosComprobanteVenta }>(`${this.comprobantesApiUrl}/venta/${idVenta}/datos`);
  }

  emitirComprobanteVenta(idVenta: number, payload: EmitirComprobantePayload): Observable<{ success: boolean; message: string; pdf_url: string; correo_enviado: boolean }> {
    return this.http.post<{ success: boolean; message: string; pdf_url: string; correo_enviado: boolean }>(`${this.comprobantesApiUrl}/venta/${idVenta}/emitir`, payload);
  }

  descargarComprobantePdf(idVenta: number): Observable<Blob> {
    return this.http.get(`${this.comprobantesApiUrl}/venta/${idVenta}/pdf`, { responseType: 'blob' });
  }
}
