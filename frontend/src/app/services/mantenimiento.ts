import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export interface ClienteCrm {
  nro_usuario: number;
  nombre: string;
  apellido?: string;
  telefono?: string;
  username?: string;
}

export interface NotificacionCrmPayload {
  clientes: number[];
  asunto: string;
  mensaje: string;
  canal: string;
}

@Injectable({
  providedIn: 'root'
})
export class MantenimientoService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    return token ? new HttpHeaders({ Authorization: `Bearer ${token}` }) : new HttpHeaders();
  }

  obtenerClientesCrm(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/crm/clientes`, {
      headers: this.getHeaders()
    });
  }

  enviarNotificacionCrm(datos: NotificacionCrmPayload): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/crm/notificaciones/enviar`, datos, {
      headers: this.getHeaders()
    });
  }

  registrarPlan(datos: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/crm/mantenimiento`, datos, {
      headers: this.getHeaders()
    });
  }

  ejecutarRecordatoriosManual(): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/crm/mantenimiento/ejecutar-recordatorios`, {}, {
      headers: this.getHeaders()
    });
  }
}