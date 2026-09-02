import { Component, OnInit, inject, ChangeDetectorRef, NgZone, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { KpisService, DashboardMetricas } from '../../services/kpis';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-dashboard-kpis',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-kpis.html'
})
export class DashboardKpisComponent implements OnInit {

  private kpisService = inject(KpisService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private platformId = inject(PLATFORM_ID);

  usuarioActual: any = null;
  modoOscuro: boolean = false;
  metricas: DashboardMetricas | null = null;
  cargando: boolean = false;
  mensajeError: string = '';

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.usuarioActual = this.authService.obtenerUsuario();

      if (!this.usuarioActual || this.authService.tokenExpirado()) {
        this.cerrarSesion();
        return;
      }

      this.cargarMetricas();
    }
  }

  cargarMetricas(): void {
    // Usamos setTimeout para escapar del ciclo actual y forzar la detección de cambios
    setTimeout(() => {
      this.ngZone.run(() => {
        this.cargando = true;
        this.mensajeError = '';
        this.metricas = null;
        this.cdr.detectChanges(); // Forzamos mostrar el loader
      });

      this.kpisService.obtenerMetricasDashboard().subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            if (res.success) {
              this.metricas = res.data;
            } else {
              this.mensajeError = res.message || 'No se pudieron cargar los KPIs.';
            }
            this.finalizarCarga();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            this.mensajeError = err.error?.detail || 'Error al conectar con el módulo de analítica.';
            this.finalizarCarga();
          });
        }
      });
    }, 0);
  }

  private finalizarCarga() {
    this.cargando = false;
    this.cdr.detectChanges(); // Forzamos quitar el loader y mostrar los datos
  }

  refrescarDashboard(): void {
    this.cargarMetricas();
  }

  cerrarSesion(): void {
    this.authService.cerrarSesion();
    this.router.navigate(['/login']);
  }

  // ==============================================================
  // MATEMÁTICAS PROTEGIDAS CONTRA DATOS NULOS
  // ==============================================================

  getPorcentajeCancelados(): number {
    const total = this.metricas?.total_casos_historicos || 0;
    const cancelados = this.metricas?.casos_cancelados || 0;
    if (total === 0) return 0;
    return Number(((cancelados / total) * 100).toFixed(2));
  }

  getTotalIncidentesPorTipo(): number {
    if (!this.metricas?.incidentes_por_tipo?.length) return 0;
    return this.metricas.incidentes_por_tipo.reduce((total, item) => total + (item?.cantidad || 0), 0);
  }

  getMaxIncidentes(): number {
    if (!this.metricas?.incidentes_por_tipo?.length) return 1;
    return Math.max(...this.metricas.incidentes_por_tipo.map(item => item?.cantidad || 0));
  }

  getAnchoBarraIncidente(cantidad: number): number {
    const maximo = this.getMaxIncidentes();
    if (maximo === 0) return 0;
    return Number(((cantidad / maximo) * 100).toFixed(2));
  }

  getMaxTiempoTaller(): number {
    if (!this.metricas?.talleres_eficientes?.length) return 1;
    return Math.max(...this.metricas.talleres_eficientes.map(item => item?.tiempo_promedio_min || 0));
  }

  getAnchoBarraTaller(tiempo: number): number {
    const maximo = this.getMaxTiempoTaller();
    if (maximo === 0) return 0;
    return Number(((tiempo / maximo) * 100).toFixed(2));
  }

  getSlaComoNumero(): number {
    const sla = this.metricas?.nivel_cumplimiento_sla || '0%';
    const numero = Number(sla.replace('%', ''));
    return isNaN(numero) ? 0 : numero;
  }

  getTextoTiempo(minutos: number | undefined | null): string {
    if (minutos === undefined || minutos === null || minutos <= 0) return '0 min';
    if (minutos < 60) return `${minutos} min`;
    const horas = Math.floor(minutos / 60);
    const minRestantes = Math.round(minutos % 60);
    return `${horas} h ${minRestantes} min`;
  }

  trackByTipo(index: number, item: any): string {
    return item?.tipo || index.toString();
  }

  trackByTaller(index: number, item: any): string {
    return item?.taller || index.toString();
  }

  trackByPunto(index: number): number {
    return index;
  }
}