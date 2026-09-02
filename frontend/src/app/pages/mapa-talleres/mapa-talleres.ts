import { Component, OnInit, OnDestroy, inject, NgZone, PLATFORM_ID, ChangeDetectorRef } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms'; 
import { RouterLink } from '@angular/router'; 
import { TalleresService, Taller, Empresa } from '../../services/talleres';
import { LeafletService } from '../../services/leaflet';
import type * as LeafletType from 'leaflet';

@Component({
  selector: 'app-mapa-talleres',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './mapa-talleres.html'
})
export class MapaTalleresComponent implements OnInit, OnDestroy {
  private talleresService = inject(TalleresService);
  private leafletService = inject(LeafletService);
  private ngZone = inject(NgZone);
  private platformId = inject(PLATFORM_ID);
  private cdr = inject(ChangeDetectorRef); 

  private L!: typeof LeafletType | any;
  private mapa: LeafletType.Map | null = null;
  private pinesLayerGroup: any = null; 
  private marcadoresMap = new Map<number, any>(); 

  // Datos
  empresas: Empresa[] = [];
  talleresTodos: Taller[] = [];
  talleresFiltrados: Taller[] = [];

  // Filtros
  filtroEmpresa: string = '';
  textoBusqueda: string = '';
  cargando: boolean = true;

  // Métricas
  cantOperativos = 0;
  cantCerrados = 0;

  async ngOnInit() {
    if (!isPlatformBrowser(this.platformId)) return;

    this.L = await this.leafletService.loadLeaflet();
    if (!this.L) return;

    this.ngZone.runOutsideAngular(() => {
      this.mapa = this.L.map('mapa-completo', {
        center: [-17.7833, -63.1821], 
        zoom: 13,
        zoomControl: true
      });

      this.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap',
        maxZoom: 19
      }).addTo(this.mapa!);

      
      this.pinesLayerGroup = this.L.featureGroup().addTo(this.mapa!);
    });

    this.cargarDatosCombinados();
  }

  ngOnDestroy() {
    if (this.mapa) {
      this.mapa.remove();
      this.mapa = null;
    }
  }

  // Carga Empresas y luego Talleres para tener la info completa
  cargarDatosCombinados() {
    this.cargando = true; 

    this.talleresService.obtenerEmpresas().subscribe({
      next: (resEmp) => {
        if (resEmp.success) this.empresas = resEmp.data;
        
        this.talleresService.obtenerTalleres().subscribe({
          next: (resTal) => {
            if (resTal.success) {
              this.talleresTodos = resTal.data;
              this.aplicarFiltros(); 
            }
            this.cargando = false; 
            this.cdr.detectChanges(); 
          },
          error: () => {
            this.cargando = false; 
            this.cdr.detectChanges();
          }
        });
      },
      error: () => {
        this.cargando = false; 
        this.cdr.detectChanges();
      }
    });
  }

  obtenerNombreEmpresa(id: number): string {
    const emp = this.empresas.find(e => e.id_empresa === id);
    return emp ? emp.nombre_empresa : 'Empresa Independiente';
  }

  aplicarFiltros() {
    this.talleresFiltrados = this.talleresTodos.filter(t => {
      const matchEmpresa = this.filtroEmpresa ? t.id_empresa === Number(this.filtroEmpresa) : true;
      const matchTexto = this.textoBusqueda ? t.nombre_taller.toLowerCase().includes(this.textoBusqueda.toLowerCase()) : true;
      return matchEmpresa && matchTexto;
    });

    this.cantOperativos = this.talleresFiltrados.filter(t => t.disponibilidad).length;
    this.cantCerrados = this.talleresFiltrados.filter(t => !t.disponibilidad).length;

    this.pintarPines();
    this.cdr.detectChanges(); // Forzamos actualización visual del panel
  }

  pintarPines() {
    if (!this.mapa || !this.L || !this.pinesLayerGroup) return;

    this.ngZone.runOutsideAngular(() => {
      // Limpiamos los pines y diccionarios anteriores
      this.pinesLayerGroup.clearLayers();
      this.marcadoresMap.clear();

      const bounds: LeafletType.LatLngTuple[] = [];

      this.talleresFiltrados.forEach(taller => {
        if (taller.latitud == null || taller.longitud == null) return;

        const iconColor = taller.disponibilidad ? '#1e3a8a' : '#dc2626';
        const iconSvg = `
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 42" width="32" height="42">
            <path d="M16 0C7.163 0 0 7.163 0 16c0 10 16 26 16 26S32 26 32 16C32 7.163 24.837 0 16 0z" fill="${iconColor}" stroke="white" stroke-width="1.5"/>
            <circle cx="16" cy="16" r="7" fill="white"/>
          </svg>
        `;

        const customIcon = this.L.divIcon({
          html: iconSvg,
          className: '',
          iconSize: [32, 42],
          iconAnchor: [16, 42],
          popupAnchor: [0, -44] // Tooltip hacia arriba
        });

        const marker = this.L.marker(
          [taller.latitud, taller.longitud],
          { icon: customIcon }
        ).addTo(this.pinesLayerGroup);

        // Guardamos el marcador para poder llamarlo desde la lista
        this.marcadoresMap.set(taller.nro_taller, marker);

        const estadoColor = taller.disponibilidad ? '#16a34a' : '#dc2626';
        const estadoTexto = taller.disponibilidad ? 'OPERATIVO' : 'CERRADO';
        const nombreEmpresa = this.obtenerNombreEmpresa(taller.id_empresa); // <-- Incorporamos el Tenant al Tooltip

        const fechaFormateada = new Date(taller.fecha_registro).toLocaleDateString();

        const tooltipHtml = `
          <div style="min-width:200px; font-family: sans-serif;">
            <div style="background:#1e3a8a; color:white; padding:10px 12px; border-radius:6px 6px 0 0; font-weight:700; font-size:12px; line-height:1.2;">
              ${taller.nombre_taller}
              <div style="font-size:9px; color:#cbd5e1; font-weight:500; margin-top:3px; text-transform:uppercase; letter-spacing:0.5px;">
                🏢 ${nombreEmpresa}
              </div>
            </div>
            <div style="padding:10px 12px; background:white; border-radius:0 0 6px 6px; border: 1px solid #e2e8f0; border-top:none;">
              <div style="font-size:11px; color:#64748b; margin-bottom:8px; line-height:1.4;">
                📍 ${taller.direccion_escrita || 'Ubicación GPS'}
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                <span style="background:${estadoColor}15; color:${estadoColor}; border:1px solid ${estadoColor}40; font-size:10px; font-weight:800; padding:3px 8px; border-radius:4px;">
                  ● ${estadoTexto}
                </span>
                <span style="font-size:9px; color:#94a3b8; font-weight:600;">
                  📅 ${fechaFormateada}
                </span>
              </div>
            </div>
          </div>
        `;

        marker.bindTooltip(tooltipHtml, {
          direction: 'top',
          offset: [0, -44],
          opacity: 1,
          className: 'leaflet-tooltip-taller-moderno' // Se recomienda quitar bordes por defecto de leaflet vía CSS si es posible
        });

        bounds.push([taller.latitud, taller.longitud]);
      });

      // Centrar mapa si hay resultados
      if (bounds.length > 0) {
        this.mapa!.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
      }
    });
  }

  // Se ejecuta al hacer clic en un taller del panel izquierdo
  enfocarTaller(taller: Taller) {
    if (!this.mapa || !this.L || !taller.latitud || !taller.longitud) return;

    this.ngZone.runOutsideAngular(() => {
      // Navegación suave estilo Google Maps
      this.mapa!.flyTo([taller.latitud, taller.longitud], 17, {
        animate: true,
        duration: 1.5
      });

      // Abrimos el tooltip del taller seleccionado
      const marker = this.marcadoresMap.get(taller.nro_taller);
      if (marker) {
        // Esperamos a que termine la animación para abrir el tooltip
        setTimeout(() => {
          marker.openTooltip();
        }, 1500);
      }
    });
  }
}