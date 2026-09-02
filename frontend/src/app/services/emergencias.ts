import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export interface Emergencia {
  nro_emergencia: number;
  tipo_emergencia: string;
  latitud: number;
  longitud: number;
  fecha_inicio: string;
  fecha_fin?: string;
  estado: string;
  prioridad: string;
  nro_usuario: number;
  nro_taller?: number;
  id_empresa?: number;
  nombre_taller?: string;
  nombre_usuario?: string;
  telefono_cliente?: string;
  // Nuevos campos del vehículo que vienen del backend
  nro_vehiculo?: number;
  vehiculo_placa?: string;
  vehiculo_marca?: string;
  vehiculo_año?: number;
}

export interface RespuestaApiEmergencias {
  success: boolean;
  message: string;
  data: Emergencia[];
}

export interface DiagnosticoIAData {
  diagnostico_estimado: string;
  prioridad_sugerida: string;
  requiere_grua: boolean;
}

export interface RespuestaDiagnosticoIA {
  success: boolean;
  message: string;
  data: DiagnosticoIAData;
}

@Injectable({
  providedIn: 'root'
})
export class EmergenciasService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    return token ? new HttpHeaders({ 'Authorization': `Bearer ${token}` }) : new HttpHeaders();
  }

  obtenerTodasLasEmergencias(): Observable<RespuestaApiEmergencias> {
    return this.http.get<RespuestaApiEmergencias>(`${this.apiUrl}/api/emergencias/`, { headers: this.getHeaders() });
  }

  obtenerMisEmergencias(): Observable<RespuestaApiEmergencias> {
    return this.http.get<RespuestaApiEmergencias>(`${this.apiUrl}/api/emergencias/mis-emergencias`, { headers: this.getHeaders() });
  }

  obtenerEmergenciasMiTaller(): Observable<RespuestaApiEmergencias> {
    return this.http.get<RespuestaApiEmergencias>(`${this.apiUrl}/api/emergencias/mi-taller`, { headers: this.getHeaders() });
  }

  // --- NUEVO ENDPOINT DE EVIDENCIAS ---
  obtenerEvidenciasEmergencia(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/emergencias/${id}/evidencias`, { headers: this.getHeaders() });
  }

  crearEmergencia(datos: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/api/emergencias/`, datos, { headers: this.getHeaders() });
  }

  actualizarEmergencia(id: number, datos: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/api/emergencias/${id}`, datos, { headers: this.getHeaders() });
  }

  eliminarEmergencia(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/api/emergencias/${id}`, { headers: this.getHeaders() });
  }
  
  emitirOferta(datos: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/api/ofertas/`, datos, { headers: this.getHeaders() });
  }

  generarDiagnosticoIA(nroEmergencia: number): Observable<RespuestaDiagnosticoIA> {
    return this.http.get<RespuestaDiagnosticoIA>(
      `${this.apiUrl}/api/diagnostico/${nroEmergencia}`,
      { headers: this.getHeaders() }
    );
  }

  // Añade este método en tu EmergenciasService
  obtenerEmergenciaPorId(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/emergencias/${id}`, { headers: this.getHeaders() });
  }
}