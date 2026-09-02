import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export interface Empresa {
  id_empresa: number;
  nombre_empresa: string;
  nit: string;
  estado: string;
}

export interface Taller {
  nro_taller: number;
  nombre_taller: string;
  direccion_escrita: string;
  latitud: number;
  longitud: number;
  disponibilidad: boolean;
  fecha_registro: string;
  id_empresa: number;
}

@Injectable({ providedIn: 'root' })
export class TalleresService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  
  //BASE DE URL DE LA API FASTAPI
  private apiUrl = `${environment.apiUrl}/api/talleres`;
  private apiUrlEmpresas = `${environment.apiUrl}/api/empresas`; 

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    return token ? new HttpHeaders({ 'Authorization': `Bearer ${token}` }) : new HttpHeaders();
  }

  obtenerEmpresas(): Observable<{ success: boolean; message?: string; data: Empresa[] }> {
    return this.http.get<{ success: boolean; message?: string; data: Empresa[] }>(this.apiUrlEmpresas, { headers: this.getHeaders() });
  }

  obtenerTalleres(): Observable<{ success: boolean; message?: string; data: Taller[] }> {
    return this.http.get<{ success: boolean; message?: string; data: Taller[] }>(`${this.apiUrl}/`, { headers: this.getHeaders() });
  }

  crearTaller(datos: any): Observable<any> {
    
    return this.http.post<any>(`${this.apiUrl}/`, datos, { headers: this.getHeaders() });
  }

  actualizarTaller(nro_taller: number, datos: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${nro_taller}`, datos, { headers: this.getHeaders() });
  }

  eliminarTaller(nro_taller: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${nro_taller}`, { headers: this.getHeaders() });
  }

  //METODOS DEDICADOS A LOS SERVICIOS DE UN TALLER
  obtenerServiciosTaller(nro_taller: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${nro_taller}/servicios`, { headers: this.getHeaders() });
  }

  crearServicioTaller(nro_taller: number, datos: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${nro_taller}/servicios`, datos, { headers: this.getHeaders() });
  }

  actualizarServicioTaller(nro_taller: number, nro_servicio: number, datos: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${nro_taller}/servicios/${nro_servicio}`, datos, { headers: this.getHeaders() });
  }

  eliminarServicioTaller(nro_taller: number, nro_servicio: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${nro_taller}/servicios/${nro_servicio}`, { headers: this.getHeaders() });
  }
}