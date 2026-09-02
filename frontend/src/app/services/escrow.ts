import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export interface FondoRetenido {
  id_custodia: number;
  monto_retenido: number;
  estado_custodia: string;
  fecha_retencion: string;
  nro_emergencia: number;
  tipo_emergencia: string;
  nombre_usuario?: string;
  vehiculo_placa?: string;
  vehiculo_marca?: string;
}

export interface ResumenUsuarioFondos {
  nro_usuario: number;
  nombre_completo: string;
  telefono: string;
  total_retenido: number;
  cantidad_retenciones: number;
}

@Injectable({
  providedIn: 'root'
})
export class EscrowService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    return token ? new HttpHeaders({ Authorization: `Bearer ${token}` }) : new HttpHeaders();
  }

  obtenerMisFondos(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/escrow/mis-fondos`, {
      headers: this.getHeaders()
    });
  }

  obtenerResumenUsuarios(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/escrow/resumen-usuarios`, {
      headers: this.getHeaders()
    });
  }

  retenerDinero(datos: { nro_emergencia: number; monto: number }): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/escrow/retener`, datos, {
      headers: this.getHeaders()
    });
  }
}