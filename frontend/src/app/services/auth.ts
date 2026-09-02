import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common'; 
import { environment } from '../../environments/environment';


@Injectable({
  providedIn: 'root'
})
export class AuthService {
  
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;
  private platformId = inject(PLATFORM_ID); 

  iniciarSesion(credenciales: any) {
    return this.http.post<any>(`${this.apiUrl}/api/auth/login`, credenciales);
  }

  guardarSesion(token: string, usuario: any) {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('token', token);
      localStorage.setItem('usuario', JSON.stringify(usuario));
    }
  }

  
  obtenerToken(): string | null {
    if (isPlatformBrowser(this.platformId)) {
      return localStorage.getItem('token');
    }
    return null;
  }

  obtenerUsuario() {

    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }
    

    const usuarioString = localStorage.getItem('usuario');
    return usuarioString ? JSON.parse(usuarioString) : null;
  }

  cerrarSesion() {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.clear();
    }
  }

  tokenExpirado(): boolean {
    const token = this.obtenerToken();
    
    //SI NO HAY TOKEN DEVUELVE TRUE DICIENDO QUE YA EXPIRO O DIRECTAMENTE NO HAY TOKEN
    if (!token) return true;

    try 
    {
      //DECODIFICAR EL PAYLOAD DEL TOKEN
      const payloadBase64 = token.split('.')[1];
      const payloadDecodificado = JSON.parse(atob(payloadBase64));
      
      //CALCULO
      const tiempoExpiracion = payloadDecodificado.exp * 1000;
      const tiempoActual = Date.now();

      //DEVUELVE TRUE SI YA PASO EL VENCIMIENTO
      return tiempoActual >= tiempoExpiracion;
    } 
    catch (error) 
    {
      //SI EL TOKEN FUE ADULTERADO O MODIFICADO DEVUELVE TRUE HACIENDO QUE LO BOTEN DEL SISTEMA
      return true; 
    }
  }
}
