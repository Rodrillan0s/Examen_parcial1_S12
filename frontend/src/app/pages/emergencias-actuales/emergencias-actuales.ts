import { Component, OnInit, OnDestroy, inject, NgZone, PLATFORM_ID, ChangeDetectorRef } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { EmergenciasService, Emergencia } from '../../services/emergencias';
import { AuthService } from '../../services/auth';
import { LeafletService } from '../../services/leaflet';
import type * as LeafletType from 'leaflet';

@Component({
  selector: 'app-emergencias-actuales',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './emergencias-actuales.html'
})
export class EmergenciasActualesComponent implements OnInit, OnDestroy {
  private emergenciasService = inject(EmergenciasService);
  private authService = inject(AuthService);
  private leafletService = inject(LeafletService);
  private ngZone = inject(NgZone);
  private platformId = inject(PLATFORM_ID);
  private cdr = inject(ChangeDetectorRef);

  private L!: typeof LeafletType | any;
  private mapa: LeafletType.Map | null = null;
  private pinesLayerGroup: any = null;
  private marcadoresMap = new Map<number, any>();

  usuarioActual: any = null;
  emergencias: Emergencia[] = [];
  emergenciasFiltradas: Emergencia[] = [];

  // Filtros
  filtroEstado: string = '';
  textoBusqueda: string = '';
  cargando: boolean = true;

  // Métricas
  cantPendientes = 0;
  cantEnCurso = 0;

  async ngOnInit() {
    if (!isPlatformBrowser(this.platformId)) return;

    this.usuarioActual = this.authService.obtenerUsuario();
    if (!this.usuarioActual) return;

    this.L = await this.leafletService.loadLeaflet();
    if (!this.L) return;

    this.ngZone.runOutsideAngular(() => {
      this.mapa = this.L.map('mapa-completo', {
        center: [-17.7833, -63.1821], // Santa Cruz por defecto
        zoom: 13,
        zoomControl: true
      });

      this.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap',
        maxZoom: 19
      }).addTo(this.mapa!);

      this.pinesLayerGroup = this.L.featureGroup().addTo(this.mapa!);
    });

    this.cargarEmergenciasPorRol();
  }

  ngOnDestroy() {
    if (this.mapa) {
      this.mapa.remove();
      this.mapa = null;
    }
  }

  // --- NUEVO MÉTODO PARA EL BOTÓN ACTUALIZAR ---
  refrescarMapa() {
    this.cargarEmergenciasPorRol();
  }

  cargarEmergenciasPorRol() {
    setTimeout(() => {
      this.ngZone.run(() => {
        this.cargando = true;
        this.cdr.detectChanges(); // Forzar loader
      });

      const rol = this.usuarioActual.nombre_rol;
      let peticion$;
      
      if (rol === 'ADMINISTRADOR') {
        peticion$ = this.emergenciasService.obtenerTodasLasEmergencias();
      } else if (rol === 'CLIENTE') {
        peticion$ = this.emergenciasService.obtenerMisEmergencias();
      } else {
        peticion$ = this.emergenciasService.obtenerEmergenciasMiTaller();
      }

      peticion$.subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            if (res.success) {
              this.emergencias = res.data;
              this.aplicarFiltros();
            }
            this.cargando = false;
            this.cdr.detectChanges();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            console.error('Error cargando emergencias:', err);
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    }, 0);
  }

  aplicarFiltros() {
    this.emergenciasFiltradas = this.emergencias.filter(e => {
      const matchEstado = this.filtroEstado ? e.estado === this.filtroEstado : true;
      const matchTexto = this.textoBusqueda ? e.tipo_emergencia.toLowerCase().includes(this.textoBusqueda.toLowerCase()) : true;
      return matchEstado && matchTexto;
    });

    this.cantPendientes = this.emergenciasFiltradas.filter(e => e.estado === 'PENDIENTE').length;
    this.cantEnCurso = this.emergenciasFiltradas.filter(e => e.estado === 'EN CURSO' || e.estado === 'ACEPTADO').length;

    this.pintarPines();
    this.cdr.detectChanges();
  }

  pintarPines() {
    if (!this.mapa || !this.L || !this.pinesLayerGroup) return;

    this.ngZone.runOutsideAngular(() => {
      this.pinesLayerGroup.clearLayers();
      this.marcadoresMap.clear();
      const bounds: LeafletType.LatLngTuple[] = [];

      this.emergenciasFiltradas.forEach(emergencia => {
        if (emergencia.latitud == null || emergencia.longitud == null) return;

        let iconColor = '#dc2626'; // Rojo
        if (emergencia.estado === 'EN CURSO' || emergencia.estado === 'ACEPTADO') iconColor = '#f59e0b'; // Naranja
        if (emergencia.estado === 'RESUELTO') iconColor = '#16a34a'; // Verde

        const iconSvg = `
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 42" width="32" height="42">
            <path d="M16 0C7.163 0 0 7.163 0 16c0 10 16 26 16 26S32 26 32 16C32 7.163 24.837 0 16 0z" fill="${iconColor}" stroke="white" stroke-width="1.5"/>
            <circle cx="16" cy="15" r="5" fill="white"/>
            <path d="M15 11h2v5h-2zm0 6h2v2h-2z" fill="${iconColor}"/>
          </svg>
        `;

        const customIcon = this.L.divIcon({
          html: iconSvg,
          className: '',
          iconSize: [32, 42],
          iconAnchor: [16, 42],
          popupAnchor: [0, -44]
        });

        const marker = this.L.marker(
          [emergencia.latitud, emergencia.longitud],
          { icon: customIcon }
        ).addTo(this.pinesLayerGroup);

        this.marcadoresMap.set(emergencia.nro_emergencia, marker);

        const nombreCliente = emergencia.nombre_usuario ? `👤 ${emergencia.nombre_usuario}` : 'Usuario Anónimo';
        
        const tooltipHtml = `
          <div style="min-width:220px; font-family: sans-serif;">
            <div style="background:${iconColor}; color:white; padding:10px 12px; border-radius:6px 6px 0 0; font-weight:700; font-size:12px; line-height:1.2;">
              Emergencia #${emergencia.nro_emergencia}
              <div style="font-size:10px; color:rgba(255,255,255,0.9); font-weight:500; margin-top:3px; text-transform:uppercase;">
                ⚠️ ${emergencia.tipo_emergencia}
              </div>
            </div>
            <div style="padding:10px 12px; background:white; border-radius:0 0 6px 6px; border: 1px solid #e2e8f0; border-top:none;">
              <div style="font-size:11px; color:#64748b; margin-bottom:8px; font-weight: 600;">
                ${nombreCliente}
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size:10px; font-weight:800; color:${iconColor};">
                  ● ${emergencia.estado}
                </span>
                <span style="font-size:9px; color:#94a3b8; font-weight:600;">
                  📅 ${emergencia.fecha_inicio.substring(0, 16)}
                </span>
              </div>
            </div>
          </div>
        `;

        marker.bindTooltip(tooltipHtml, {
          direction: 'top',
          offset: [0, -44],
          opacity: 1,
          className: 'leaflet-tooltip-taller-moderno'
        });

        bounds.push([emergencia.latitud, emergencia.longitud]);
      });

      if (bounds.length > 0) {
        this.mapa!.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
      }
    });
  }

  enfocarEmergencia(emergencia: Emergencia) {
    if (!this.mapa || !this.L || !emergencia.latitud || !emergencia.longitud) return;

    this.ngZone.runOutsideAngular(() => {
      this.mapa!.flyTo([emergencia.latitud, emergencia.longitud], 18, {
        animate: true,
        duration: 1.5
      });

      const marker = this.marcadoresMap.get(emergencia.nro_emergencia);
      if (marker) {
        setTimeout(() => marker.openTooltip(), 1500);
      }
    });
  }
}