import { Injectable, inject } from '@angular/core';
import { HttpClient,HttpHeaders } from '@angular/common/http';
import { Observable ,throwError} from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth'; 
export interface PerfilUsuario {
  ci: string;
  nombre_usuario: string;
  fecha_registro: string;
  nro_usuario: number;
  estado: string;
  nro_rol: number;
  id_empresa?: number;
  nombre_empresa?: string;
  nombre_completo: string;
  telefono: string;
  correo: string;
  direccion: string;
  nombre_rol: string;
  cant_vehiculos: number;
}

export interface ApiResponseGet {
  success: boolean;
  message: string;
  data: PerfilUsuario;
}

export interface ApiResponsePut {
  success: boolean;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class PerfilService {
  private http = inject(HttpClient);
  private authService = inject(AuthService); 
  private apiUrl = environment.apiUrl;

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    
    return token ? new HttpHeaders({ 'Authorization': `Bearer ${token}` }) : new HttpHeaders();
  }

  obtenerPerfil(): Observable<ApiResponseGet> {
    const token = this.authService.obtenerToken();
    
    if (!token) {
      return throwError(() => ({ status: 401, message: 'Token no disponible' }));
    }

    const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
    return this.http.get<ApiResponseGet>(`${this.apiUrl}/api/perfil`, { headers });
  }

  actualizarPerfil(datos: any): Observable<ApiResponsePut> {
    const headers = this.getHeaders();
    return this.http.put<ApiResponsePut>(`${this.apiUrl}/api/perfil/`, datos, { headers });
  }
}