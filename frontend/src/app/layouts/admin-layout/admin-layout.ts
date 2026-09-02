import {
  Component,
  OnInit,
  inject,
  PLATFORM_ID,
  HostListener,
  ChangeDetectorRef,
  NgZone,
  DestroyRef
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router, RouterOutlet, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth';
import { NotificacionesService, Notificacion } from '../../services/notificaciones';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterModule],
  templateUrl: './admin-layout.html'
})
export class AdminLayoutComponent implements OnInit {

  private authService           = inject(AuthService);
  private notificacionesService  = inject(NotificacionesService);
  private router                = inject(Router);
  private platformId            = inject(PLATFORM_ID);
  private cdr                   = inject(ChangeDetectorRef);
  private ngZone                = inject(NgZone);
  private destroyRef            = inject(DestroyRef);

  // ---- Estado general ----
  usuarioActual: any      = null;
  modoOscuro: boolean     = false;
  sidebarAbierto: boolean   = false;
  sidebarColapsado: boolean = false;

  // ---- Estado notificaciones ----
  mostrarNotificaciones: boolean = false;
  listaNotificaciones: Notificacion[] = [];
  cantidadNoLeidas: number = 0;

  // ---- Definición del menú ----
  menuNavegacion = [
    {
      titulo: 'Emergencias',
      icono: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
      rolesPermitidos: ['ADMINISTRADOR', 'GERENTE TALLER', 'MECANICO'],
      expandido: true,
      submenus: [
        { nombre: 'Visualizar Emergencias', ruta: '/emergencias-historial' },
        { nombre: 'Mapa de Emergencias',   ruta: '/emergencias-actuales' }
      ]
    },
    {
      titulo: 'Red de Talleres',
      icono: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0zM12 13a3 3 0 100-6 3 3 0 000 6z',
      rolesPermitidos: ['ADMINISTRADOR', 'GERENTE TALLER'],
      expandido: true,
      submenus: [
        { nombre: 'Talleres Asociados', ruta: '/talleres' },
        { nombre: 'Mapa de Talleres',   ruta: '/mapa-talleres' }
      ]
    },
    {
      titulo: 'Seguridad y Usuarios',
      icono: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
      rolesPermitidos: ['ADMINISTRADOR'],
      expandido: true,
      submenus: [
        { nombre: 'Gestión de Usuarios', ruta: '/usuarios' },
        { nombre: 'Roles y Permisos',    ruta: '/roles' },
        { nombre: 'Tenants (Empresas)',  ruta: '/empresas' },
        { nombre: 'Bitácora del Sistema', ruta: '/bitacora' },
        { nombre: 'Copias de Respaldo',  ruta: '/backup' }
      ]
    },
    {
      titulo: 'Pagos y Custodia',
      icono: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      rolesPermitidos: ['ADMINISTRADOR', 'CLIENTE'],
      expandido: true,
      submenus: [
        { nombre: 'Dinero Retenido', ruta: '/dinero-retenido' }
      ]
    },
    {
      titulo: 'Analítica y KPIs',
      icono: 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z',
      rolesPermitidos: ['ADMINISTRADOR', 'GERENTE TALLER'],
      expandido: true,
      submenus: [
        { nombre: 'Dashboard de KPIs', ruta: '/kpis' },
        { nombre: 'ETL (DataWareHousing)',ruta:'/bi_dashboard' }
      ]
    },
    {
      titulo: 'Asistente IA',
      icono: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z',
      rolesPermitidos: ['ADMINISTRADOR', 'GERENTE TALLER'],
      expandido: true,
      submenus: [
        { nombre: 'ChatBot', ruta: '/triaje-chat' }
      ]
    }
  ];

  menuFiltrado: any[] = [];

  // ------------------------------------------------------------------
  // LIFECYCLE
  // ------------------------------------------------------------------

  ngOnInit() {
    if (!isPlatformBrowser(this.platformId)) return;

    this.usuarioActual = this.authService.obtenerUsuario();

    if (!this.usuarioActual) {
      this.cerrarSesion();
      return;
    }

    // Filtrar menú según rol
    const rolUsuario = this.usuarioActual.nombre_rol;
    this.menuFiltrado = this.menuNavegacion.filter(m =>
      m.rolesPermitidos.includes(rolUsuario)
    );

    // Restaurar tema guardado
    if (localStorage.getItem('tema_sistema') === 'dark') {
      this.modoOscuro = true;
      document.documentElement.classList.add('dark');
    }

    this.verificarResolucion();

    // Iniciar WS + cargar historial desde BD
    this.notificacionesService.conectar();

    // Suscribirse al stream reactivo (mezcla BD + WS en tiempo real)
    this.notificacionesService.notificaciones$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((notis) => {
        this.ngZone.run(() => {
          this.listaNotificaciones = notis;
          this.cantidadNoLeidas   = notis.filter(n => !n.leida).length;
          this.cdr.detectChanges();
        });
      });
  }

  // ------------------------------------------------------------------
  // HOST LISTENERS
  // ------------------------------------------------------------------

  @HostListener('window:resize')
  onResize() {
    if (isPlatformBrowser(this.platformId)) {
      this.verificarResolucion();
    }
  }

  /**
   * Cierra el panel de notificaciones si el usuario hace clic
   * fuera del área marcada con [data-notif-panel].
   */
  @HostListener('document:click', ['$event'])
  onClickFuera(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (this.mostrarNotificaciones && !target.closest('[data-notif-panel]')) {
      this.mostrarNotificaciones = false;
    }
  }

  // ------------------------------------------------------------------
  // SIDEBAR
  // ------------------------------------------------------------------

  verificarResolucion() {
    const isDesktop = window.innerWidth >= 768;
    if (isDesktop && this.sidebarAbierto) {
      this.sidebarAbierto = false;
    }
  }

  toggleSidebar() {
    if (!isPlatformBrowser(this.platformId)) return;

    if (window.innerWidth < 768) {
      this.sidebarAbierto = !this.sidebarAbierto;
    } else {
      this.sidebarColapsado = !this.sidebarColapsado;
      if (this.sidebarColapsado) {
        this.menuFiltrado.forEach(m => m.expandido = false);
      }
    }
  }

  toggleAcordeon(modulo: any) {
    if (this.sidebarColapsado && window.innerWidth >= 768) {
      this.sidebarColapsado = false;
    }
    modulo.expandido = !modulo.expandido;
  }

  cerrarSidebarMobile() {
    this.sidebarAbierto = false;
  }

  // ------------------------------------------------------------------
  // TEMA
  // ------------------------------------------------------------------

  alternarModoOscuro() {
    if (!isPlatformBrowser(this.platformId)) return;

    this.modoOscuro = !this.modoOscuro;
    if (this.modoOscuro) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('tema_sistema', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('tema_sistema', 'light');
    }
  }

  // ------------------------------------------------------------------
  // NOTIFICACIONES
  // ------------------------------------------------------------------

  /**
   * Abre o cierra el panel.
   * Al abrir: marca todas como leídas en BD (PUT /leer marcar_todo=true)
   * y resetea el contador visual.
   */
  toggleNotificaciones() {
    this.mostrarNotificaciones = !this.mostrarNotificaciones;

    if (this.mostrarNotificaciones && this.cantidadNoLeidas > 0) {
      this.notificacionesService.marcarComoLeidas();
      this.cantidadNoLeidas = 0;
      this.cdr.detectChanges();
    }
  }

  /**
   * Botón "Marcar todas como leídas" dentro del panel.
   * Sincroniza con PUT /api/ws/leer { marcar_todo: true }
   */
  marcarTodasLeidas() {
    this.notificacionesService.marcarComoLeidas();
    this.cantidadNoLeidas = 0;
    this.cdr.detectChanges();
  }

  /**
   * Clic en una notificación individual.
   * Sincroniza con PUT /api/ws/leer { id_notificacion: N }
   * Solo actúa si viene de BD (tiene id_notificacion).
   */
  leerNotificacion(noti: Notificacion) {
    if (!noti.leida && noti.id_notificacion) {
      this.notificacionesService.marcarUnaComoLeida(noti.id_notificacion);
    }
  }

  /** Navega a la pantalla completa y cierra el panel. */
  irANotificaciones() {
    this.mostrarNotificaciones = false;
    this.router.navigate(['/notificaciones']);
  }

  // ------------------------------------------------------------------
  // HELPERS DE ICONOS (dinámicos según tipo_referencia del backend)
  // ------------------------------------------------------------------

  /**
   * Tipos reales del backend:
   *   NUEVA_EMERGENCIA | NUEVA_OFERTA | RESPUESTA_OFERTA
   */
  getIconoClase(tipo: string): string {
    const clases: Record<string, string> = {
      'NUEVA_EMERGENCIA': 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-800/30',
      'NUEVA_OFERTA':     'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/30',
      'RESPUESTA_OFERTA': 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800/30',
      // Genéricos de compatibilidad
      'EMERGENCIA': 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-800/30',
      'ALERTA':     'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/30',
      'INFO':       'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-800/30',
      'EXITO':      'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800/30',
    };
    return clases[tipo] ?? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-800/30';
  }

  getIconoPath(tipo: string): string {
    const iconos: Record<string, string> = {
      'NUEVA_EMERGENCIA': 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
      'NUEVA_OFERTA':     'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
      'RESPUESTA_OFERTA': 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
      // Genéricos de compatibilidad
      'EMERGENCIA': 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
      'ALERTA':     'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      'INFO':       'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      'EXITO':      'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    };
    return iconos[tipo] ?? 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z';
  }

  // ------------------------------------------------------------------
  // SESIÓN
  // ------------------------------------------------------------------

  cerrarSesion() {
    this.notificacionesService.desconectar();
    this.authService.cerrarSesion();
    this.router.navigate(['/login']);
  }
}