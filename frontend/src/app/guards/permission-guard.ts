import { CanActivateFn, Router } from '@angular/router';
import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { AuthService } from '../services/auth';

/**
 * permissionGuard: Valida que el usuario autenticado cuente con los permisos necesarios.
 * Permite pasar un único código de permiso o un arreglo (donde basta tener al menos uno).
 */
export function permissionGuard(requiredPermissions: string | string[]): CanActivateFn {
  return (route, state) => {
    const platformId = inject(PLATFORM_ID);
    if (!isPlatformBrowser(platformId)) {
      return true;
    }

    const authService = inject(AuthService);
    const router = inject(Router);

    const usuario = authService.obtenerUsuario();
    if (!usuario || authService.tokenExpirado()) {
      authService.cerrarSesion();
      authService.openAuthModal('login');
      router.navigate(['/']);
      return false;
    }

    const permissionsToCheck = Array.isArray(requiredPermissions) ? requiredPermissions : [requiredPermissions];
    const tieneAcceso = authService.hasAnyPermission(permissionsToCheck);

    if (!tieneAcceso) {
      console.warn(`[PermissionGuard] Acceso denegado a '${state.url}'. Permisos requeridos:`, permissionsToCheck);

      // Redirección contextual según el rol/alcance del usuario
      if (authService.isCashier()) {
        router.navigate(['/admin/caja']);
      } else if (authService.hasPermission('reportes.ver') || authService.isStoreAdmin() || authService.isGlobalAdmin()) {
        router.navigate(['/admin/kpis']);
      } else {
        router.navigate(['/admin/caja']);
      }
      return false;
    }

    return true;
  };
}
