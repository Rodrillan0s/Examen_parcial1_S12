import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class LeafletService {
  private L: any = null;

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  async loadLeaflet(): Promise<any> {
    // 1. Prevenir ejecución en el servidor (SSR)
    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }

    // 2. Si ya se cargó previamente, lo devolvemos al instante
    if (this.L) {
      return this.L;
    }

    // 3. Importación dinámica con parche para Producción
    const leafletModule = await import('leaflet');
    
    // Aquí está la magia: si existe .default, usamos ese, sino el módulo directo
    this.L = leafletModule.default ? leafletModule.default : leafletModule;

    // 4. Configurar el ícono por defecto una sola vez
    this.configurarIconoDefault();

    return this.L;
  }

  private configurarIconoDefault() {
    const iconDefault = this.L.icon({
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });
    this.L.Marker.prototype.options.icon = iconDefault;
  }
}