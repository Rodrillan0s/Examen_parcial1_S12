import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ImagenProducto {
  id_imagen?: number;
  imagen_url: string;
  public_id: string;
  es_principal?: boolean;
  orden?: number;
  created_at?: string;
  file?: File;
  subiendo?: boolean;
}

export interface VarianteProducto {
  id_variante?: number;
  id_talla: number;
  talla_nombre?: string;
  id_color: number;
  color_nombre?: string;
  codigo_hex?: string;
  sku?: string;
  precio?: number;
  activo?: boolean;
  estado?: boolean;
  tiene_stock?: boolean;
  total_movimientos?: number;
}

export interface Producto {
  id_producto?: number;
  id_empresa?: number;
  empresa_nombre?: string;
  id_categoria: number;
  categoria_nombre?: string;
  codigo_producto?: string;
  nombre: string;
  descripcion?: string;
  marca?: string;
  genero?: string;
  precio: number;
  temporada?: string;
  coleccion?: string;
  activo: boolean;
  estado?: boolean;
  fecha_registro?: string;
  updated_at?: string;
  imagen_principal?: string;
  total_imagenes?: number;
  total_variantes?: number;
  imagenes?: ImagenProducto[];
  variantes?: VarianteProducto[];
  tiene_ra?: boolean;
  tipo_prenda_ra?: 'TOP' | 'PANT' | 'DRESS' | string;
  modelo_2d_url?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ProductosService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/productos`;

  listarProductos(filtros?: {
    id_empresa?: number;
    solo_activos?: boolean;
    id_categoria?: number;
    busqueda?: string;
  }): Observable<{ success: boolean; total: number; data: Producto[] }> {
    let params = new HttpParams();
    if (filtros?.id_empresa) params = params.set('id_empresa', filtros.id_empresa.toString());
    if (filtros?.solo_activos) params = params.set('solo_activos', 'true');
    if (filtros?.id_categoria) params = params.set('id_categoria', filtros.id_categoria.toString());
    if (filtros?.busqueda) params = params.set('busqueda', filtros.busqueda);

    return this.http.get<{ success: boolean; total: number; data: Producto[] }>(this.apiUrl, { params });
  }

  obtenerProducto(id_producto: number): Observable<{ success: boolean; data: Producto }> {
    return this.http.get<{ success: boolean; data: Producto }>(`${this.apiUrl}/${id_producto}`);
  }

  crearProducto(datos: {
    id_empresa?: number;
    id_categoria: number;
    nombre: string;
    precio: number;
    descripcion?: string;
    codigo_producto?: string;
    temporada?: string;
    coleccion?: string;
    marca?: string;
    genero?: string;
    activo?: boolean;
    tallas_ids?: number[];
    colores_ids?: number[];
    imagenes?: { imagen_url: string; public_id: string; es_principal?: boolean }[];
    tiene_ra?: boolean;
    tipo_prenda_ra?: string;
    modelo_2d_url?: string;
  }): Observable<any> {
    return this.http.post(this.apiUrl, datos);
  }

  actualizarProducto(id_producto: number, datos: {
    id_categoria: number;
    nombre: string;
    precio: number;
    descripcion?: string;
    codigo_producto?: string;
    temporada?: string;
    coleccion?: string;
    marca?: string;
    genero?: string;
    activo?: boolean;
    tallas_ids?: number[];
    colores_ids?: number[];
    tiene_ra?: boolean;
    tipo_prenda_ra?: string;
    modelo_2d_url?: string;
  }): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id_producto}`, datos);
  }

  cambiarEstado(id_producto: number, activo: boolean): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id_producto}/estado`, { activo });
  }

  eliminarProducto(id_producto: number): Observable<{ success: boolean; action: string; message: string }> {
    return this.http.delete<{ success: boolean; action: string; message: string }>(`${this.apiUrl}/${id_producto}`);
  }

  subirImagenCloudinary(archivo: File): Observable<{ success: boolean; message: string; data: { imagen_url: string; public_id: string } }> {
    const formData = new FormData();
    formData.append('file', archivo);
    return this.http.post<{ success: boolean; message: string; data: { imagen_url: string; public_id: string } }>(
      `${this.apiUrl}/upload-image`,
      formData
    );
  }

  agregarImagenAProducto(id_producto: number, imagen_url: string, public_id: string, es_principal: boolean = false): Observable<any> {
    return this.http.post(`${this.apiUrl}/${id_producto}/imagenes`, {
      imagen_url,
      public_id,
      es_principal
    });
  }

  marcarPortada(id_producto: number, id_imagen: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id_producto}/imagenes/${id_imagen}/principal`, {});
  }

  eliminarImagen(id_producto: number, id_imagen: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id_producto}/imagenes/${id_imagen}`);
  }
}
