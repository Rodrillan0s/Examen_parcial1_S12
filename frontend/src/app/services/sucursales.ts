import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export interface Sucursal {
  id_sucursal?: number;
  nombre: string;
  direccion: string;
  id_empresa: number;
  activo: boolean;
}

export interface RespuestaApiSucursales {
  success: boolean;
  message: string;
  data: Sucursal[];
}

@Injectable({
  providedIn: 'root'
})
export class SucursalService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = `${environment.apiUrl}/api/sucursales`;

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    return token ? new HttpHeaders({ 'Authorization': `Bearer ${token}` }) : new HttpHeaders();
  }

  listarSucursales(id_empresa?: number): Observable<RespuestaApiSucursales> {
    const url = id_empresa ? `${this.apiUrl}?id_empresa=${id_empresa}` : this.apiUrl;
    return this.http.get<RespuestaApiSucursales>(url, { headers: this.getHeaders() });
  }

  crearSucursal(sucursal: Sucursal): Observable<any> {
    return this.http.post(this.apiUrl, sucursal, { headers: this.getHeaders() });
  }

  actualizarSucursal(id_sucursal: number, sucursal: Sucursal): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id_sucursal}`, sucursal, { headers: this.getHeaders() });
  }

  eliminarSucursal(id_sucursal: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id_sucursal}`, { headers: this.getHeaders() });
  }
}
