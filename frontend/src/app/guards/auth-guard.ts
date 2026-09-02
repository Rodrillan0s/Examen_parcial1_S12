import { CanActivateFn, Router } from '@angular/router';
import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { AuthService } from '../services/auth';

export const authGuard: CanActivateFn = (route, state) => {
  const platformId = inject(PLATFORM_ID);
  
  // 1. Si estamos en el servidor de Node.js (SSR), lo dejamos pasar temporalmente.
  // Esto evita que el servidor fuerce redirecciones ciegas.
  if (!isPlatformBrowser(platformId)) {
    return true; 
  }

  // 2. Si ya estamos en el navegador, hacemos la validación real de seguridad
  const authService = inject(AuthService);
  const router = inject(Router);

  const usuario = authService.obtenerUsuario();
  const tokenExpirado = authService.tokenExpirado();

  if (!usuario || tokenExpirado) {
    authService.cerrarSesion();
    router.navigate(['/login']);
    return false; 
  }

  return true;
};