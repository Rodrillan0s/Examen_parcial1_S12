import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, catchError, of } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ItemCarrito {
  id_detalle_carrito: number;
  id_variante: number;
  id_producto: number;
  producto_nombre: string;
  codigo_producto?: string;
  talla_nombre: string;
  color_nombre: string;
  codigo_hex: string;
  sku?: string;
  imagen_url?: string | null;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
  stock_disponible: number;
  disponible: boolean;
  advertencia_stock?: string | null;
}

export interface CarritoData {
  id_carrito: number;
  id_empresa: number;
  nombre_empresa: string;
  items: ItemCarrito[];
  total_items: number;
  subtotal: number;
  descuento: number;
  total: number;
  puede_continuar_compra: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class CarritoService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/carrito`;

  private carritoSubject = new BehaviorSubject<CarritoData | null>(null);
  public carrito$ = this.carritoSubject.asObservable();

  private totalItemsSubject = new BehaviorSubject<number>(0);
  public totalItems$ = this.totalItemsSubject.asObservable();

  private subtotalSubject = new BehaviorSubject<number>(0);
  public subtotal$ = this.subtotalSubject.asObservable();

  private drawerAbiertoSubject = new BehaviorSubject<boolean>(false);
  public drawerAbierto$ = this.drawerAbiertoSubject.asObservable();

  private cargandoSubject = new BehaviorSubject<boolean>(false);
  public cargando$ = this.cargandoSubject.asObservable();

  // Tenant activo actualmente en el cliente
  private currentEmpresaId: number | null = null;

  setEmpresaId(idEmpresa: number): void {
    if (this.currentEmpresaId !== idEmpresa) {
      this.currentEmpresaId = idEmpresa;
      this.cargarCarrito(idEmpresa).subscribe();
    }
  }

  getEmpresaId(): number | null {
    return this.currentEmpresaId;
  }

  abrirDrawer(): void {
    this.drawerAbiertoSubject.next(true);
  }

  cerrarDrawer(): void {
    this.drawerAbiertoSubject.next(false);
  }

  alternarDrawer(): void {
    this.drawerAbiertoSubject.next(!this.drawerAbiertoSubject.value);
  }

  private actualizarEstado(data: CarritoData | null): void {
    this.carritoSubject.next(data);
    if (data) {
      this.totalItemsSubject.next(data.total_items || 0);
      this.subtotalSubject.next(data.total || 0);
    } else {
      this.totalItemsSubject.next(0);
      this.subtotalSubject.next(0);
    }
  }

  cargarCarrito(idEmpresa?: number): Observable<{ success: boolean; data: CarritoData } | null> {
    const empId = idEmpresa || this.currentEmpresaId;
    let params = new HttpParams();
    if (empId) params = params.set('id_empresa', empId.toString());

    this.cargandoSubject.next(true);
    return this.http.get<{ success: boolean; data: CarritoData }>(`${this.apiUrl}`, { params }).pipe(
      tap(res => {
        if (res && res.success) {
          this.actualizarEstado(res.data);
        }
        this.cargandoSubject.next(false);
      }),
      catchError(err => {
        this.cargandoSubject.next(false);
        // Si no está autenticado o hay error, no romper flujo
        return of(null);
      })
    );
  }

  agregarItem(idVariante: number, cantidad: number, idEmpresa?: number): Observable<{ success: boolean; message: string; data: CarritoData }> {
    const empId = idEmpresa || this.currentEmpresaId;
    const body: any = {
      id_variante: idVariante,
      cantidad: cantidad
    };
    if (empId) body.id_empresa = empId;

    this.cargandoSubject.next(true);
    return this.http.post<{ success: boolean; message: string; data: CarritoData }>(`${this.apiUrl}/items`, body).pipe(
      tap(res => {
        if (res && res.success) {
          this.actualizarEstado(res.data);
        }
        this.cargandoSubject.next(false);
      }),
      catchError(err => {
        this.cargandoSubject.next(false);
        throw err;
      })
    );
  }

  actualizarCantidad(idDetalle: number, cantidad: number, idEmpresa?: number): Observable<{ success: boolean; message: string; data: CarritoData }> {
    const empId = idEmpresa || this.currentEmpresaId;
    const body: any = { cantidad };
    if (empId) body.id_empresa = empId;

    this.cargandoSubject.next(true);
    return this.http.put<{ success: boolean; message: string; data: CarritoData }>(`${this.apiUrl}/items/${idDetalle}`, body).pipe(
      tap(res => {
        if (res && res.success) {
          this.actualizarEstado(res.data);
        }
        this.cargandoSubject.next(false);
      }),
      catchError(err => {
        this.cargandoSubject.next(false);
        throw err;
      })
    );
  }

  eliminarItem(idDetalle: number, idEmpresa?: number): Observable<{ success: boolean; message: string; data: CarritoData }> {
    const empId = idEmpresa || this.currentEmpresaId;
    let params = new HttpParams();
    if (empId) params = params.set('id_empresa', empId.toString());

    this.cargandoSubject.next(true);
    return this.http.delete<{ success: boolean; message: string; data: CarritoData }>(`${this.apiUrl}/items/${idDetalle}`, { params }).pipe(
      tap(res => {
        if (res && res.success) {
          this.actualizarEstado(res.data);
        }
        this.cargandoSubject.next(false);
      }),
      catchError(err => {
        this.cargandoSubject.next(false);
        throw err;
      })
    );
  }

  vaciarCarrito(idEmpresa?: number): Observable<{ success: boolean; message: string; data: CarritoData }> {
    const empId = idEmpresa || this.currentEmpresaId;
    let params = new HttpParams();
    if (empId) params = params.set('id_empresa', empId.toString());

    this.cargandoSubject.next(true);
    return this.http.delete<{ success: boolean; message: string; data: CarritoData }>(`${this.apiUrl}/vaciar`, { params }).pipe(
      tap(res => {
        if (res && res.success) {
          this.actualizarEstado(res.data);
        }
        this.cargandoSubject.next(false);
      }),
      catchError(err => {
        this.cargandoSubject.next(false);
        throw err;
      })
    );
  }
}
