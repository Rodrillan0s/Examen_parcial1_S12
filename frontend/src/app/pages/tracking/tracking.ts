import { Component, OnInit, OnDestroy, inject, NgZone, PLATFORM_ID, ChangeDetectorRef } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { EmergenciasService, Emergencia } from '../../services/emergencias';
import { TalleresService, Taller } from '../../services/talleres';
import { LeafletService } from '../../services/leaflet';
import type * as LeafletType from 'leaflet';

@Component({
  selector: 'app-tracking',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './tracking.html'
})
export class TrackingComponent implements OnInit, OnDestroy {
  private router = inject(Router);
  private emergenciasService = inject(EmergenciasService);
  private talleresService = inject(TalleresService);
  private leafletService = inject(LeafletService);
  private ngZone = inject(NgZone);
  private platformId = inject(PLATFORM_ID);
  private cdr = inject(ChangeDetectorRef);

  private L!: typeof LeafletType | any;
  private mapa: LeafletType.Map | null = null;
  private rutaLayer: any = null;

  emergencia: Emergencia | null = null;
  nombreTallerBase: string = 'Localizando Taller Base';
  cargando: boolean = true;
  procesando: boolean = false;
  estadoGPS: string = 'Recuperando telemetría...';

  // Datos de ruta
  distanciaKm: string = '--';
  tiempoEstimado: string = '--';

  async ngOnInit() {
    if (!isPlatformBrowser(this.platformId)) return;

    const state = history.state;
    if (!state || !state.emergenciaData) {
      alert('Error de contexto: Redirigiendo a consola principal.');
      this.volver();
      return;
    }

    this.emergencia = state.emergenciaData;

    try {
      this.L = await this.leafletService.loadLeaflet();
      if (this.L) {
        this.obtenerUbicacionTallerYMap();
      }
    } catch (error) {
      console.error('Error cargando Leaflet:', error);
      this.estadoGPS = 'Falla crítica del motor de mapas.';
      this.cargando = false;
      this.cdr.detectChanges();
    }
  }

  ngOnDestroy() {
    if (this.mapa) {
      this.mapa.remove();
      this.mapa = null;
    }
  }

  obtenerUbicacionTallerYMap() {
    this.estadoGPS = 'Ubicando taller asignado...';

    if (!this.emergencia?.nro_taller) {
      alert('Esta orden aún no registra un taller asignado.');
      this.volver();
      return;
    }

    this.talleresService.obtenerTalleres().subscribe({
      next: (res) => {
        if (res.success) {
          const tallerAsignado = res.data.find(t => t.nro_taller === this.emergencia!.nro_taller);
          
          if (tallerAsignado) {
            this.nombreTallerBase = tallerAsignado.nombre_taller;
            const latTaller = Number(tallerAsignado.latitud);
            const lngTaller = Number(tallerAsignado.longitud);
            this.inicializarMapa(latTaller, lngTaller);
          } else {
            alert('Error: Taller base no encontrado en el padrón de proveedores.');
            this.volver();
          }
        }
      },
      error: (err) => {
        console.error('Error obteniendo taller:', err);
        this.estadoGPS = 'Error de comunicación con la red de talleres.';
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  inicializarMapa(latOrigen: number, lngOrigen: number) {
    this.ngZone.runOutsideAngular(() => {
      this.mapa = this.L.map('mapa-tracking', {
        zoomControl: false // UI Limpia
      });

      this.L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 19
      }).addTo(this.mapa!);

      this.L.control.zoom({ position: 'bottomleft' }).addTo(this.mapa!);

      const latDestino = Number(this.emergencia!.latitud);
      const lngDestino = Number(this.emergencia!.longitud);

      // --- ACTUALIZADO: ÍCONO DE ORIGEN ES UN AUTO B2B ---
      // Usamos un SVG de un auto sedán corporativo
      const svgOrigen = `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3C13 6.8 12 6 11 6H4c-1.1 0-2 .9-2 2v8c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/></svg>`;
      const iconOrigen = this.L.divIcon({
        html: `<div style="background:#0052cc; color:white; width:38px; height:38px; display:flex; align-items:center; justify-content:center; border:2px solid white; box-shadow:0 3px 5px rgba(0,0,0,0.3);">${svgOrigen}</div>`,
        className: '', iconSize: [38, 38], iconAnchor: [19, 19]
      });

      // MARCADOR DESTINO (SINIESTRO) - Triángulo de advertencia
      const svgDestino = `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
      const iconDestino = this.L.divIcon({
        html: `<div style="background:#dc2626; color:white; width:38px; height:38px; display:flex; align-items:center; justify-content:center; border:2px solid white; box-shadow:0 3px 5px rgba(0,0,0,0.3);">${svgDestino}</div>`,
        className: '', iconSize: [38, 38], iconAnchor: [19, 19]
      });

      this.L.marker([latOrigen, lngOrigen], { icon: iconOrigen }).addTo(this.mapa).bindPopup(`<div style="font-family:sans-serif; font-size:12px;"><b>Unidad en Servicio</b><br/>Saliendo de: ${this.nombreTallerBase}</div>`);
      this.L.marker([latDestino, lngDestino], { icon: iconDestino }).addTo(this.mapa).bindPopup('<div style="font-family:sans-serif; font-size:12px;"><b>Ubicación del Incidente</b><br/>Punto de auxilio</div>');

      this.trazarRuta(latOrigen, lngOrigen, latDestino, lngDestino);
    });
  }

  trazarRuta(latA: number, lngA: number, latB: number, lngB: number) {
    const url = `https://router.project-osrm.org/route/v1/driving/${lngA},${latA};${lngB},${latB}?overview=full&geometries=geojson`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.routes && data.routes.length > 0) {
          const route = data.routes[0];
          
          this.ngZone.run(() => {
            this.distanciaKm = (route.distance / 1000).toFixed(1);
            this.tiempoEstimado = Math.ceil(route.duration / 60) + ' min';
            this.cargando = false;
            this.cdr.detectChanges();
          });

          const latLngs = route.geometry.coordinates.map((coord: any[]) => [coord[1], coord[0]]);
          
          this.ngZone.runOutsideAngular(() => {
            this.rutaLayer = this.L.polyline(latLngs, { 
              color: '#0052cc', 
              weight: 4, 
              opacity: 0.9,
              dashArray: '8, 8'
            }).addTo(this.mapa!);
            
            this.mapa!.fitBounds(this.rutaLayer.getBounds(), { padding: [60, 60] });
          });
        } else {
          this.ngZone.run(() => {
            this.estadoGPS = 'Ruta terrestre no factible.';
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      })
      .catch(err => {
        console.error('Error de enrutamiento OSRM:', err);
        this.ngZone.run(() => {
          this.estadoGPS = 'Falla de conexión con el satélite de rutas.';
          this.cargando = false;
          this.cdr.detectChanges();
        });
      });
  }

  completarServicio() {
    if(!this.emergencia) return;
    
    if(confirm('CONFIRMACIÓN REQUERIDA: ¿La orden ha sido resuelta en su totalidad?')) {
      this.procesando = true;
      this.emergenciasService.actualizarEmergencia(this.emergencia.nro_emergencia, { estado: 'RESUELTO' }).subscribe({
        next: () => {
          this.ngZone.run(() => {
            alert('Servicio cerrado exitosamente. Volviendo al historial.');
            this.router.navigate(['/emergencias-historial']);
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            alert(err.error?.detail || 'Error de servidor al intentar cerrar la orden.');
            this.procesando = false;
            this.cdr.detectChanges();
          });
        }
      });
    }
  }

  volver() {
    this.router.navigate(['/emergencias-historial']);
  }
}