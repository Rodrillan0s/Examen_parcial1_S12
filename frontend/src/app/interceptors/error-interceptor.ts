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
        // Ignorar rutas de autenticación pública (login, registro, etc.):
        // Un 401 en login significa "credenciales incorrectas", NO "sesión caducada".
        const esRutaAuth = req.url.includes('/api/auth/login') ||
                           req.url.includes('/api/auth/register') ||
                           req.url.includes('/api/auth/verify-device') ||
                           req.url.includes('/api/auth/forgot-password') ||
                           req.url.includes('/api/auth/reset-password');

        if (esRutaAuth) {
          return throwError(() => error);
        }

        const token = authService.obtenerToken();
        if (!token) {
          console.warn('Petición 401 sin token (posible carga inicial). Ignorando...');
          return throwError(() => error);
        }

        // Si SÍ hay token en una ruta protegida y el backend da 401, entonces sí caducó
        console.warn('El backend rechazó el token. Sesión caducada.');
        authService.cerrarSesion();
        setTimeout(() => router.navigate(['/']), 0);
      }
      return throwError(() => error);
    })
  );
};