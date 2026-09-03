import { CanActivateFn, Router } from '@angular/router';
import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { AuthService } from '../services/auth';

export const authGuard: CanActivateFn = (route, state) => {
  const platformId = inject(PLATFORM_ID);
  
  if (!isPlatformBrowser(platformId)) {
    return true; 
  }

  const authService = inject(AuthService);
  const router = inject(Router);

  const usuario = authService.obtenerUsuario();
  const tokenExpirado = authService.tokenExpirado();

  // 1. Validar autenticación básica
  if (!usuario || tokenExpirado) {
    authService.cerrarSesion();
    authService.openAuthModal('login');
    router.navigate(['/']);
    return false; 
  }

  // 2. Si la ruta requiere rol administrativo/empleado (ej. /admin y sus hijas)
  const esRutaAdmin = state.url.startsWith('/admin');
  if (esRutaAdmin && !authService.esEmpleadoOAdmin()) {
    alert('Acceso restringido: Se requieren privilegios de empleado o administrador para acceder al panel de gestión.');
    router.navigate(['/']);
    return false;
  }

  return true;
};