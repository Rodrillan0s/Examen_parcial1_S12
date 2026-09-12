import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface TenantPublico {
  id_empresa: number;
  nombre_empresa: string;
  razon_social?: string;
  logo?: string | null;
  ciudad?: string;
  correo?: string;
  telefono?: string;
  direccion_fiscal?: string;
}

export interface CategoriaFiltro {
  id_categoria: number;
  nombre: string;
  imagen_url?: string | null;
  total_prendas: number;
}

export interface TallaFiltro {
  id_talla: number;
  nombre: string;
}

export interface ColorFiltro {
  id_color: number;
  nombre: string;
  codigo_hex: string;
}

export interface FiltrosCatalogoResponse {
  categorias: CategoriaFiltro[];
  tallas: TallaFiltro[];
  colores: ColorFiltro[];
  temporadas: string[];
  colecciones: string[];
  precio_min?: number;
  precio_max?: number;
}

export interface PrendaCatalogo {
  id_producto: number;
  id_empresa: number;
  id_categoria: number;
  categoria_nombre: string;
  codigo_producto?: string;
  nombre: string;
  descripcion: string;
  marca: string;
  genero: string;
  precio: number;
  temporada: string;
  coleccion: string;
  fecha_registro?: string;
  imagen_principal?: string | null;
  total_imagenes: number;
  total_variantes: number;
  tallas_disponibles: { id_talla: number; nombre: string }[];
  colores_disponibles: { id_color: number; nombre: string; codigo_hex: string }[];
}

export interface VarianteDetalle {
  id_variante: number;
  id_talla: number;
  talla_nombre: string;
  id_color: number;
  color_nombre: string;
  codigo_hex: string;
  sku?: string;
  precio: number;
  modelo_ra_url?: string | null;
}

export interface ImagenDetalle {
  id_imagen: number;
  imagen_url: string;
  public_id: string;
  es_principal: boolean;
  orden: number;
}

export interface SucursalStockDetalle {
  id_sucursal: number;
  nombre: string;
  codigo_sucursal?: string;
  direccion: string;
  telefono?: string;
  horario: string;
  ciudad?: string;
  stock_total_sucursal: number;
  disponible: boolean;
  stock_por_variante: Record<string, number>; // id_variante -> stock
}

export interface DetallePrendaCatalogo {
  id_producto: number;
  id_empresa: number;
  empresa_nombre: string;
  id_categoria: number;
  categoria_nombre: string;
  codigo_producto?: string;
  nombre: string;
  descripcion: string;
  marca: string;
  genero: string;
  precio: number;
  temporada: string;
  coleccion: string;
  fecha_registro?: string;
  imagenes: ImagenDetalle[];
  imagen_principal?: string | null;
  variantes: VarianteDetalle[];
  tallas: { id_talla: number; nombre: string }[];
  colores: { id_color: number; nombre: string; codigo_hex: string }[];
  sucursales_stock: SucursalStockDetalle[];
  stock_total_general: number;
  hay_stock_disponible: boolean;
  permite_reserva: boolean;
  permite_compra: boolean;
  permite_vestidor_ra: boolean;
  recursos_ra?: {
    modelo_3d_url?: string | null;
    modelo_ar_url?: string | null;
  };
}

export interface RespuestaCatalogoProductos {
  success: boolean;
  empresa: TenantPublico | null;
  total: number;
  limit: number;
  offset: number;
  data: PrendaCatalogo[];
}

export interface DisponibilidadVarianteSucursal {
  id_sucursal: number;
  nombre: string;
  codigo_sucursal?: string;
  direccion: string;
  telefono?: string;
  correo?: string;
  horario: string;
  ciudad?: string;
  stock_disponible: number;
  disponible: boolean;
  permite_reserva: boolean;
  permite_compra: boolean;
}

export interface DisponibilidadVarianteResponse {
  variante: {
    id_variante: number;
    id_producto: number;
    producto_nombre: string;
    id_empresa: number;
    empresa_nombre: string;
    id_talla: number;
    talla_nombre: string;
    id_color: number;
    color_nombre: string;
    codigo_hex: string;
    sku?: string;
    precio: number;
  };
  stock_total: number;
  hay_disponibilidad: boolean;
  sucursales: DisponibilidadVarianteSucursal[];
}

@Injectable({
  providedIn: 'root'
})
export class CatalogoPublicoService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/catalogo`;

  obtenerTenants(): Observable<{ success: boolean; total: number; data: TenantPublico[] }> {
    return this.http.get<{ success: boolean; total: number; data: TenantPublico[] }>(`${this.apiUrl}/tenants`);
  }

  obtenerFiltros(id_empresa?: number): Observable<{ success: boolean; empresa: TenantPublico | null; data: FiltrosCatalogoResponse }> {
    let params = new HttpParams();
    if (id_empresa) params = params.set('id_empresa', id_empresa.toString());
    return this.http.get<{ success: boolean; empresa: TenantPublico | null; data: FiltrosCatalogoResponse }>(
      `${this.apiUrl}/filtros`,
      { params }
    );
  }

  consultarProductos(filtros?: {
    id_empresa?: number;
    busqueda?: string;
    id_categoria?: number;
    id_talla?: number;
    id_color?: number;
    temporada?: string;
    coleccion?: string;
    precio_min?: number;
    precio_max?: number;
    orden?: string;
    limit?: number;
    offset?: number;
  }): Observable<RespuestaCatalogoProductos> {
    let params = new HttpParams();
    if (filtros?.id_empresa) params = params.set('id_empresa', filtros.id_empresa.toString());
    if (filtros?.busqueda) params = params.set('busqueda', filtros.busqueda.trim());
    if (filtros?.id_categoria) params = params.set('id_categoria', filtros.id_categoria.toString());
    if (filtros?.id_talla) params = params.set('id_talla', filtros.id_talla.toString());
    if (filtros?.id_color) params = params.set('id_color', filtros.id_color.toString());
    if (filtros?.temporada && filtros.temporada !== 'Todas') params = params.set('temporada', filtros.temporada);
    if (filtros?.coleccion && filtros.coleccion !== 'Todas') params = params.set('coleccion', filtros.coleccion);
    if (filtros?.precio_min !== undefined && filtros.precio_min !== null) params = params.set('precio_min', filtros.precio_min.toString());
    if (filtros?.precio_max !== undefined && filtros.precio_max !== null) params = params.set('precio_max', filtros.precio_max.toString());
    if (filtros?.orden) params = params.set('orden', filtros.orden);
    if (filtros?.limit) params = params.set('limit', filtros.limit.toString());
    if (filtros?.offset) params = params.set('offset', filtros.offset.toString());

    return this.http.get<RespuestaCatalogoProductos>(`${this.apiUrl}/productos`, { params });
  }

  obtenerDetalleProducto(
    id_producto: number,
    id_empresa?: number
  ): Observable<{ success: boolean; data: DetallePrendaCatalogo }> {
    let params = new HttpParams();
    if (id_empresa) {
      params = params.set('id_empresa', id_empresa.toString());
    }

    return this.http.get<{ success: boolean; data: DetallePrendaCatalogo }>(
      `${this.apiUrl}/productos/${id_producto}`,
      { params }
    );
  }

  consultarDisponibilidadVariante(
    id_variante: number,
    id_empresa?: number
  ): Observable<{
    success: boolean;
    data: DisponibilidadVarianteResponse;
  }> {
    let params = new HttpParams();
    if (id_empresa) {
      params = params.set('id_empresa', id_empresa.toString());
    }

    return this.http.get<{
      success: boolean;
      data: DisponibilidadVarianteResponse;
    }>(
      `${this.apiUrl}/variantes/${id_variante}/disponibilidad`,
      { params }
    );
  }
}
