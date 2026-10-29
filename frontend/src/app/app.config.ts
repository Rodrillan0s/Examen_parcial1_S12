import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter, withNavigationErrorHandler } from '@angular/router';
import { errorInterceptor } from './interceptors/error-interceptor';
import { authInterceptor } from './interceptors/auth-interceptor';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(
      routes,
      withNavigationErrorHandler((navError) => {
        const underlying = (navError as any)?.error;
        const rawMsg = underlying?.message || (navError as any)?.message || String(underlying || navError || '');
        const isChunkError =
          rawMsg.includes('Loading chunk') ||
          rawMsg.includes('Failed to fetch dynamically imported module') ||
          rawMsg.includes('error loading dynamically imported module') ||
          rawMsg.includes('Failed to load module') ||
          rawMsg.includes('chunk-');

        if (isChunkError && typeof window !== 'undefined') {
          console.warn('[Router] Error de carga de chunk detectado en navegación:', rawMsg);
          const lastReload = sessionStorage.getItem('aurora_last_chunk_reload');
          const now = Date.now();
          if (!lastReload || now - Number(lastReload) > 5000) {
            sessionStorage.setItem('aurora_last_chunk_reload', String(now));
            window.location.reload();
          }
        }
      })
    ),
    provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),
  ],
};

