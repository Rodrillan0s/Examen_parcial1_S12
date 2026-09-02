import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { AuthService } from '../services/auth';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error) => {
      // SOLO si el error es 401
      if (error.status === 401) {
        const token = authService.obtenerToken();
        
        // ¡CAMBIO CLAVE! 
        // Si el token es null o está vacío, NO cierres la sesión todavía.
        // Es probable que la página se esté recargando.
        if (!token) {
          console.warn('Petición 401 sin token (posible carga inicial). Ignorando...');
          return throwError(() => error);
        }

        // Si SÍ hay token y aun así el backend dice 401, entonces sí caducó
        console.warn('El backend rechazó el token. Sesión caducada.');
        authService.cerrarSesion();
        setTimeout(() => router.navigate(['/login']), 0);
      }
      return throwError(() => error);
    })
  );
};