import { Component, OnInit, inject, ChangeDetectorRef, NgZone, DestroyRef, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { TalleresService, Taller, Empresa } from '../../services/talleres';
import { AuthService } from '../../services/auth';
import { LeafletService } from '../../services/leaflet'; 

// BORRAMOS el import estático de Leaflet. Solo traeremos los TIPOS para que TypeScript no moleste
import type * as Leaflet from 'leaflet'; 


@Component({
  selector: 'app-talleres',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './talleres.html'
})
export class TalleresComponent implements OnInit {
  private talleresService = inject(TalleresService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private destroyRef = inject(DestroyRef);
  private platformId = inject(PLATFORM_ID);

  private leafletService = inject(LeafletService);

  talleres: Taller[] = [];
  talleresFiltrados: Taller[] = [];
  empresas: Empresa[] = []; 
  
  filtroEmpresa: string = '';
  cargando = true;
  procesando = false;
  mensajeError = '';

  mostrarModal = false;
  modoEdicion = false;
  esAdmin = false;

  tallerForm: any = this.inicializarTaller();
  
  totalTalleres: number = 0;
  talleresOperativos: number = 0;
  talleresCerrados: number = 0;

  servicios: any[] = [];
  viendoServicios = false;
  nuevoServicio = { nombre_servicio: '', descripcion: '' };

  // --- VARIABLES DEL MAPA (Tipadas con la interfaz de arriba) ---
  private L: any;
  mapa: any = null;
  marcador: any = null;

  async ngOnInit() {
    // 1. BLOQUEAMOS EL SERVIDOR: Si estamos en Node.js, abortamos aquí mismo.
    if (!isPlatformBrowser(this.platformId)) {
      this.cargando = false;
      return;
    }

    this.cargando = true;

    // 2. Cargamos Leaflet desde el servicio (¡que ya trae el ícono configurado!)
    this.L = await this.leafletService.loadLeaflet();

    if (!this.L) {
      this.cargando = false;
      return;
    }
    
    // 3. Esperamos el token
    let intentos = 0;
    while (!this.authService.obtenerToken() && intentos < 10) {
      await new Promise(r => setTimeout(r, 50)); 
      intentos++;
    }

    if (this.authService.obtenerToken()) {
      this.ngZone.run(() => {
        const usuario = this.authService.obtenerUsuario();
        if (usuario && usuario.nombre_rol === 'ADMINISTRADOR') {
          this.esAdmin = true;
          this.cargarEmpresas();
        }
        this.cargarTalleres();
        this.cdr.markForCheck();
        this.cdr.detectChanges(); 
      });
    } else {
      this.cargando = false;
      this.mensajeError = "No se pudo iniciar sesión. Por favor recarga.";
      this.cdr.detectChanges();
    }
  }


  inicializarTaller() {
    return {
      nro_taller: null, nombre_taller: '', direccion_escrita: '', latitud: null, longitud: null, disponibilidad: true, id_empresa: null
    };
  }

  aplicarFiltros() {
    if (this.filtroEmpresa === '' || this.filtroEmpresa == null) {
      this.talleresFiltrados = [...this.talleres];
    } else {
      const idBuscado = Number(this.filtroEmpresa);
      this.talleresFiltrados = this.talleres.filter(t => t.id_empresa === idBuscado);
    }
    this.actualizarMetricas();
    this.cdr.markForCheck();
    this.cdr.detectChanges();
  }

  actualizarMetricas() {
    this.totalTalleres = this.talleresFiltrados.length;
    this.talleresOperativos = this.talleresFiltrados.filter(t => t.disponibilidad === true).length;
    this.talleresCerrados = this.talleresFiltrados.filter(t => t.disponibilidad === false).length;
  }

  obtenerIniciales(nombre: string): string {
    if (!nombre) return 'TA';
    const partes = nombre.trim().split(' ');
    if (partes.length >= 2) return (partes[0][0] + partes[1][0]).toUpperCase();
    return nombre.substring(0, 2).toUpperCase();
  }

  obtenerNombreEmpresa(id: number): string {
    const emp = this.empresas.find(e => e.id_empresa === id);
    return emp ? emp.nombre_empresa : `Empresa #${id}`;
  }

  cargarEmpresas() {
    this.talleresService.obtenerEmpresas().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) this.empresas = res.data.filter(e => e.estado === 'ACTIVO');
          this.cdr.detectChanges();
        });
      }
    });
  }

  cargarTalleres() {
    this.cargando = true;
    this.mensajeError = '';
    this.talleresService.obtenerTalleres().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            this.talleres = [...res.data];
            this.aplicarFiltros(); 
          } else {
            this.mensajeError = res.message || 'Error al obtener datos.';
          }
          this.cargando = false;
          this.cdr.detectChanges();
        });
      },
      error: () => {
        this.ngZone.run(() => {
          this.mensajeError = 'Error al cargar la lista de talleres.';
          this.cargando = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  // --- LÓGICA DEL MODAL Y EL MAPA LEAFLET ---
  
  abrirModalNuevo() {
    this.modoEdicion = false;
    this.tallerForm = this.inicializarTaller();
    this.mostrarModal = true;
    this.inicializarMapa(); 
  }

  abrirModalEdicion(taller: Taller) {
    this.modoEdicion = true;
    this.tallerForm = { ...taller }; 
    this.mostrarModal = true;
    this.inicializarMapa(taller.latitud, taller.longitud); 
  }

  cerrarModal() {
    this.mostrarModal = false;
    if (this.mapa) {
      this.mapa.remove();
      this.mapa = null;
      this.marcador = null;
    }
  }

  inicializarMapa(lat?: number, lng?: number) {
    if (!this.L) return; // Previene fallos si el usuario abre muy rápido el modal

    setTimeout(() => {
      const container = document.getElementById('mapa-taller');
      if (!container) return;

      const latInicial = lat || -17.7833; // Santa Cruz
      const lngInicial = lng || -63.1821;

      // Crear el mapa de Leaflet usando this.L
      this.mapa = this.L.map('mapa-taller').setView([latInicial, lngInicial], lat ? 15 : 12);

      // Usar OpenStreetMap como capa base
      this.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
      }).addTo(this.mapa);

      // Si ya hay coordenadas, poner el pin
      if (lat && lng) {
        this.marcador = this.L.marker([latInicial, lngInicial]).addTo(this.mapa);
      }

      // Evento de CLIC en el mapa
      this.mapa.on('click', (e: any) => {
        this.ngZone.run(() => {
          const nuevaLat = e.latlng.lat;
          const nuevaLng = e.latlng.lng;

          this.tallerForm.latitud = parseFloat(nuevaLat.toFixed(6));
          this.tallerForm.longitud = parseFloat(nuevaLng.toFixed(6));

          if (this.marcador) {
            this.marcador.setLatLng([nuevaLat, nuevaLng]);
          } else {
            this.marcador = this.L.marker([nuevaLat, nuevaLng]).addTo(this.mapa);
          }
          this.cdr.detectChanges();
        });
      });

      // Asegurar que Leaflet recalcule su tamaño
      setTimeout(() => {
        this.mapa?.invalidateSize();
      }, 200);

    }, 150);
  }

  guardarTaller() {
    if (!this.tallerForm.nombre_taller) {
      alert('El nombre del taller es obligatorio.');
      return;
    }
    if (this.esAdmin && !this.tallerForm.id_empresa) {
      alert('Debe seleccionar una empresa.');
      return;
    }

    this.procesando = true;

    if (this.tallerForm.latitud) this.tallerForm.latitud = parseFloat(this.tallerForm.latitud);
    if (this.tallerForm.longitud) this.tallerForm.longitud = parseFloat(this.tallerForm.longitud);

    const operacion = this.modoEdicion 
      ? this.talleresService.actualizarTaller(this.tallerForm.nro_taller, this.tallerForm)
      : this.talleresService.crearTaller(this.tallerForm);

    operacion.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.ngZone.run(() => {
          this.cerrarModal();
          this.cargarTalleres();
          this.procesando = false;
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          alert(err.error?.detail || 'Error al guardar el taller');
          this.procesando = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  eliminarTaller(id: number) {
    if (confirm('¿Estás seguro de eliminar este taller permanentemente?')) {
      this.talleresService.eliminarTaller(id).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
        next: () => this.ngZone.run(() => this.cargarTalleres()),
        error: (err) => this.ngZone.run(() => alert(err.error?.detail || 'Error al eliminar el taller'))
      });
    }
  }

  verServicios(id: number) {
    this.router.navigate([`/talleres/${id}/servicios`]);
  }
}