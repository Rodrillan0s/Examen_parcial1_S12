import { Component, OnInit, inject, ChangeDetectorRef, DestroyRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { distinctUntilChanged } from 'rxjs';
import { 
  PrediccionesService, 
  RespuestaDemanda, 
  RespuestaReposicion, 
  RespuestaEvaluacion, 
  RecomendacionItem,
  ProyeccionPunto,
  HistoricoPunto
} from '../../services/predicciones';
import { AuthService } from '../../services/auth';
import { KpisService } from '../../services/kpis';
import { extraerMensajeError } from '../../utils/error-helper';

@Component({
  selector: 'app-predicciones',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './predicciones.html',
  styleUrls: ['./predicciones.css']
})
export class PrediccionesComponent implements OnInit {
  private prediccionesService = inject(PrediccionesService);
  public authService = inject(AuthService);
  private kpisService = inject(KpisService);
  private cdr = inject(ChangeDetectorRef);
  private destroyRef = inject(DestroyRef);

  pestanaActiva: 'demanda' | 'reposicion' | 'evaluacion' = 'demanda';
  cargando: boolean = false;
  mensajeError: string = '';

  // Multi-Tenant
  tenants: any[] = [];
  empresaSeleccionada: number | null = null;

  // Filtros
  sucursalSeleccionada: number | null = null;
  diasProyeccion: number = 14;
  diasHistoria: number = 60;
  leadTimeDias: number = 7;
  filtroRiesgo: 'TODOS' | 'CRITICO' | 'ALTO' | 'MODERADO' = 'TODOS';

  // Datos
  datosDemanda: RespuestaDemanda | null = null;
  datosReposicion: RespuestaReposicion | null = null;
  datosEvaluacion: RespuestaEvaluacion | null = null;

  get sucursalesDisponibles() {
    return this.authService.branchList || [
      { id: 1, nombre: 'Sucursal Central Equipetrol', ciudad: 'Santa Cruz' },
      { id: 2, nombre: 'Sucursal Calacoto Luxury', ciudad: 'La Paz' }
    ];
  }

  get recomendacionesFiltradas(): RecomendacionItem[] {
    if (!this.datosReposicion?.recomendaciones) return [];
    if (this.filtroRiesgo === 'TODOS') return this.datosReposicion.recomendaciones;
    return this.datosReposicion.recomendaciones.filter(r => r.riesgo_rotura === this.filtroRiesgo);
  }

  ngOnInit(): void {
    this.empresaSeleccionada = this.authService.getEffectiveCompanyId();
    this.sucursalSeleccionada = this.authService.activeBranch()?.id || null;

    if (this.authService.isGlobalAdmin()) {
      this.cargarTenants();
    }

    // Suscribirse reactivamente al cambio de Tenant en el Header
    this.authService.companyChanged$
      .pipe(
        distinctUntilChanged((p, c) => p?.id_empresa === c?.id_empresa),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe(empresa => {
        if (empresa && this.empresaSeleccionada !== empresa.id_empresa) {
          this.empresaSeleccionada = empresa.id_empresa;
          this.cargarDatos();
        }
      });

    // Suscribirse reactivamente al cambio de Sucursal en el Header
    this.authService.branchChanged$
      .pipe(
        distinctUntilChanged((p, c) => p?.id === c?.id),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe(branch => {
        const newBranchId = branch ? branch.id : null;
        if (this.sucursalSeleccionada !== newBranchId) {
          this.sucursalSeleccionada = newBranchId;
          this.cargarDatos();
        }
      });

    this.cargarDatos();
  }

  cargarTenants(): void {
    this.kpisService.obtenerTenants().subscribe({
      next: (res) => {
        if (res.success && res.data) {
          this.tenants = res.data;
          const current = this.authService.getEffectiveCompanyId();
          if (current && this.tenants.some(x => Number(x.id_empresa) === Number(current))) {
            this.empresaSeleccionada = Number(current);
          } else if (!this.empresaSeleccionada && this.tenants.length > 0) {
            this.empresaSeleccionada = Number(this.tenants[0].id_empresa);
          }
          this.cdr.detectChanges();
        }
      },
      error: () => {}
    });
  }

  onCambiarEmpresa(): void {
    this.empresaSeleccionada = this.empresaSeleccionada ? Number(this.empresaSeleccionada) : null;
    if (this.empresaSeleccionada) {
      const t = this.tenants.find(x => Number(x.id_empresa) === Number(this.empresaSeleccionada));
      if (t) {
        this.authService.setSelectedCompany({
          id_empresa: t.id_empresa,
          nombre_empresa: t.nombre_empresa
        });
      }
    }
    this.cargarDatos();
  }

  cambiarPestana(p: 'demanda' | 'reposicion' | 'evaluacion'): void {
    this.pestanaActiva = p;
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.mensajeError = '';
    this.cargando = true;

    const idEmpresa = this.empresaSeleccionada || this.authService.getEffectiveCompanyId() || undefined;
    const idSucursal = this.sucursalSeleccionada ? Number(this.sucursalSeleccionada) : undefined;

    if (this.pestanaActiva === 'demanda') {
      this.prediccionesService.obtenerDemanda({
        id_empresa: idEmpresa,
        id_sucursal: idSucursal,
        dias_proyeccion: this.diasProyeccion,
        dias_historia: this.diasHistoria
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.datosDemanda = res;
          this.cargando = false;
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.cargando = false;
          this.mensajeError = extraerMensajeError(err, 'Error cargando proyecciones de demanda');
          this.cdr.detectChanges();
        }
      });
    } else if (this.pestanaActiva === 'reposicion') {
      this.prediccionesService.obtenerReposicion({
        id_empresa: idEmpresa,
        id_sucursal: idSucursal,
        lead_time_dias: this.leadTimeDias
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.datosReposicion = res;
          this.cargando = false;
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.cargando = false;
          this.mensajeError = extraerMensajeError(err, 'Error calculando recomendaciones de reposición');
          this.cdr.detectChanges();
        }
      });
    } else {
      this.prediccionesService.evaluarModelo({
        id_empresa: idEmpresa,
        id_sucursal: idSucursal,
        dias_test: 14
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.datosEvaluacion = res;
          this.cargando = false;
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.cargando = false;
          this.mensajeError = extraerMensajeError(err, 'Error evaluando backtesting del modelo');
          this.cdr.detectChanges();
        }
      });
    }
  }

  // Helpers de visualización de barras proporcionales
  calcularPorcentajeAltura(valor: number, maximo: number): number {
    if (!maximo || maximo <= 0) return 0;
    return Math.min(100, Math.max(8, Math.round((valor / maximo) * 100)));
  }

  get maximoHistorico(): number {
    if (!this.datosDemanda?.historico?.length) return 10;
    const maxH = Math.max(...this.datosDemanda.historico.map(h => h.unidades));
    const maxP = Math.max(...(this.datosDemanda.proyecciones?.map(p => p.limite_superior) || [0]));
    return Math.max(maxH, maxP, 1);
  }
}
