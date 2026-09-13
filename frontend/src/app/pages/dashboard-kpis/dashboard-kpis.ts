import { Component, OnInit, inject, ChangeDetectorRef, NgZone, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { KpisService, DashboardMetricas, RolDistribucion, DeptoSucursal, EventoActividad, SucursalDetalle } from '../../services/kpis';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-dashboard-kpis',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard-kpis.html'
})
export class DashboardKpisComponent implements OnInit {

  private kpisService = inject(KpisService);
  public authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private platformId = inject(PLATFORM_ID);

  usuarioActual: any = null;
  metricas: DashboardMetricas | null = null;
  cargando: boolean = false;
  mensajeError: string = '';

  get alcance(): 'PLATAFORMA' | 'EMPRESA' | 'SUCURSAL' | 'OPERATIVO' {
    return this.metricas?.alcance || (this.authService.getScopeLevel() as any) || 'PLATAFORMA';
  }

  get isGlobalAdmin(): boolean {
    return this.authService.getAuthorityLevel() <= 2;
  }

  get isStoreAdmin(): boolean {
    return this.authService.getAuthorityLevel() === 3;
  }

  get isBranchManager(): boolean {
    return this.authService.getAuthorityLevel() === 4;
  }

  get isStaff(): boolean {
    return this.authService.getAuthorityLevel() === 5;
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.usuarioActual = this.authService.obtenerUsuario();

      if (!this.usuarioActual || this.authService.tokenExpirado()) {
        this.cerrarSesion();
        return;
      }

      // Si es cliente, redirigir inmediatamente a su perfil
      if (this.authService.esCliente()) {
        this.router.navigate(['/perfil']);
        return;
      }

      this.cargarMetricas();
    }
  }

  cargarMetricas(): void {
    setTimeout(() => {
      this.ngZone.run(() => {
        this.cargando = true;
        this.mensajeError = '';
        this.cdr.detectChanges();
      });

      this.kpisService.obtenerMetricasDashboard().subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            if (res.success) {
              this.metricas = res.data;
            } else {
              this.mensajeError = res.message || 'No se pudieron calcular las métricas.';
            }
            this.finalizarCarga();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            this.mensajeError = err.error?.detail || err.error?.message || 'Error al sincronizar con el motor de analítica.';
            this.finalizarCarga();
          });
        }
      });
    }, 0);
  }

  private finalizarCarga() {
    this.cargando = false;
    this.cdr.detectChanges();
  }

  refrescarDashboard(): void {
    this.cargarMetricas();
  }

  cerrarSesion(): void {
    this.authService.cerrarSesion();
  }

  // --- MATEMÁTICAS PROTEGIDAS PARA BARRAS DE PROGRESO ---

  getMaxUsuariosRol(): number {
    const list = this.metricas?.roles_distribucion || [];
    if (!list.length) return 1;
    return Math.max(...list.map(r => r.cantidad || 0));
  }

  getAnchoBarraRol(cantidad: number): number {
    const max = this.getMaxUsuariosRol();
    if (max === 0) return 0;
    return Number(((cantidad / max) * 100).toFixed(1));
  }

  getMaxSucursalesDepto(): number {
    const list = this.metricas?.sucursales_por_depto || [];
    if (!list.length) return 1;
    return Math.max(...list.map(d => d.cantidad || 0));
  }

  getAnchoBarraDepto(cantidad: number): number {
    const max = this.getMaxSucursalesDepto();
    if (max === 0) return 0;
    return Number(((cantidad / max) * 100).toFixed(1));
  }

  getSlaComoNumero(): number {
    const sla = this.metricas?.nivel_cumplimiento_sla || '99%';
    const n = Number(sla.replace('%', ''));
    return isNaN(n) ? 99 : n;
  }
}