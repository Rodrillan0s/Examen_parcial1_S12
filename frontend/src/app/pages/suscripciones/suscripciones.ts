import { Component, OnInit, inject, ChangeDetectorRef, NgZone, DestroyRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../services/auth';
import { Empresa, EmpresaService } from '../../services/empresa';
import {
  SaasService,
  PlanVigenciaData,
  SuscripcionItem,
  CodigoPlan,
  AsignarSuscripcionPayload,
  CancelarSuscripcionPayload
} from '../../services/saas';
import { extraerMensajeError } from '../../utils/error-helper';

@Component({
  selector: 'app-suscripciones',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './suscripciones.html'
})
export class SuscripcionesComponent implements OnInit {
  private saasService = inject(SaasService);
  private empresaService = inject(EmpresaService);
  public authService = inject(AuthService);
  private route = inject(ActivatedRoute);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private destroyRef = inject(DestroyRef);

  // Estado de empresa
  empresas: Empresa[] = [];
  empresaSeleccionadaId: number | null = null;
  empresaActual: Empresa | null = null;

  // Datos de vigencia y plan actual
  planVigencia: PlanVigenciaData | null = null;
  historial: SuscripcionItem[] = [];

  // Estados UI
  cargandoPlan: boolean = false;
  cargandoHistorial: boolean = false;
  guardando: boolean = false;
  mensajeError: string = '';
  mensajeExito: string = '';
  errorHistorial: string = '';
  private solicitudPlan = 0;
  private solicitudHistorial = 0;
  private inicioRenovacionExacto: string | null = null;
  private inicioRenovacionInput = '';

  // Modal Asignar / Renovar Suscripción
  mostrarModalAsignar: boolean = false;
  modalError: string = '';
  formPlan: CodigoPlan = 'BASICO';
  formInicio: string = '';
  formFin: string = '';
  formMotivo: string = '';

  // Modal Cancelar Suscripción
  mostrarModalCancelar: boolean = false;
  suscripcionACancelar: SuscripcionItem | null = null;
  formCancelarMotivo: string = '';
  formCancelarConfirmar: boolean = false;

  get isGlobalAdmin(): boolean {
    return this.authService.isGlobalAdmin();
  }

  get puedeGestionar(): boolean {
    return this.isGlobalAdmin && this.authService.hasPermission('suscripciones.gestionar');
  }

  get porcentajeUsoSucursales(): number {
    const limite = this.planVigencia?.limites?.sucursales_activas;
    if (!limite || limite <= 0) return 0;
    const uso = this.planVigencia?.uso?.sucursales_activas || 0;
    return Math.min(100, Math.round((uso / limite) * 100));
  }

  ngOnInit() {
    // Si es admin global, cargar listado de empresas en paralelo con la empresa activa si ya se conoce
    if (this.isGlobalAdmin) {
      const paramEmpresa = Number(this.route.snapshot.queryParams['empresa'] || 0);
      const effEmpresa = this.authService.getEffectiveCompanyId() || 1;
      this.empresaSeleccionadaId = paramEmpresa > 0 ? paramEmpresa : effEmpresa;
      this.cargarDatosEmpresa();
      this.cargarEmpresas();
    } else {
      // Empresa directa desde sesión
      const user = this.authService.obtenerUsuario();
      this.empresaSeleccionadaId = user?.id_empresa || null;
      this.cargarDatosEmpresa();
    }
  }

  trackBySuscripcionId(index: number, item: SuscripcionItem): number {
    return item.id_suscripcion || index;
  }

  cargarEmpresas() {
    const empresaPrevia = this.empresaSeleccionadaId;
    this.empresaService.listarEmpresas()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            if (res && res.data) {
              this.empresas = res.data;

              // Revisar si viene ?empresa=ID en queryParams
              const paramEmpresa = this.route.snapshot.queryParams['empresa'];
              if (paramEmpresa) {
                const id = Number(paramEmpresa);
                if (this.empresas.some(e => e.id_empresa === id)) {
                  this.empresaSeleccionadaId = id;
                }
              }

              // Si la empresa seleccionada no existe en el listado, tomar la del usuario o la primera
              if (!this.empresaSeleccionadaId || !this.empresas.some(e => e.id_empresa === this.empresaSeleccionadaId)) {
                const user = this.authService.obtenerUsuario();
                if (user?.id_empresa && this.empresas.some(e => e.id_empresa === user.id_empresa)) {
                  this.empresaSeleccionadaId = user.id_empresa;
                } else if (this.empresas.length > 0) {
                  this.empresaSeleccionadaId = this.empresas[0].id_empresa || null;
                }
              }

              this.actualizarEmpresaActual();
              if (this.empresaSeleccionadaId !== empresaPrevia) {
                this.cargarDatosEmpresa();
              } else {
                this.cdr.detectChanges();
              }
            }
          });
        },
        error: (err) => {
          this.mensajeError = extraerMensajeError(err, 'No fue posible cargar el listado de empresas.');
          this.cdr.markForCheck();
        }
      });
  }

  onSeleccionarEmpresa() {
    this.actualizarEmpresaActual();
    this.cargarDatosEmpresa();
  }

  private actualizarEmpresaActual() {
    if (this.empresaSeleccionadaId && this.empresas.length > 0) {
      this.empresaActual = this.empresas.find(e => e.id_empresa === this.empresaSeleccionadaId) || null;
    } else {
      this.empresaActual = null;
    }
  }

  cargarDatosEmpresa() {
    this.mensajeError = '';
    this.errorHistorial = '';
    this.planVigencia = null;
    this.historial = [];
    this.solicitudPlan++;
    this.solicitudHistorial++;
    this.cargandoPlan = false;
    this.cargandoHistorial = false;
    if (this.isGlobalAdmin && !this.empresaSeleccionadaId) return;
    this.cargarVigenciaPlan();
    if (this.empresaSeleccionadaId) {
      this.cargarHistorial(this.empresaSeleccionadaId);
    }
  }

  cargarVigenciaPlan() {
    const solicitud = ++this.solicitudPlan;
    this.cargandoPlan = true;
    const targetEmpresa = this.isGlobalAdmin ? (this.empresaSeleccionadaId || undefined) : undefined;

    this.saasService.consultarPlan(targetEmpresa)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          if (solicitud !== this.solicitudPlan) return;
          this.ngZone.run(() => {
            if (res && res.data) {
              this.planVigencia = res.data;
              if (!this.empresaSeleccionadaId && res.data.id_empresa) {
                this.empresaSeleccionadaId = res.data.id_empresa;
              }
            }
            this.cargandoPlan = false;
            this.cdr.detectChanges();
          });
        },
        error: (err) => {
          if (solicitud !== this.solicitudPlan) return;
          this.ngZone.run(() => {
            this.mensajeError = extraerMensajeError(err, 'No se pudo obtener el estado de suscripción de la empresa.');
            this.planVigencia = null;
            this.cargandoPlan = false;
            this.cdr.detectChanges();
          });
        }
      });
  }

  cargarHistorial(idEmpresa: number) {
    const solicitud = ++this.solicitudHistorial;
    this.cargandoHistorial = true;

    this.saasService.obtenerHistorialSuscripciones(idEmpresa)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          if (solicitud !== this.solicitudHistorial) return;
          this.ngZone.run(() => {
            if (res && res.data) {
              this.historial = res.data;
            } else {
              this.historial = [];
            }
            this.cargandoHistorial = false;
            this.cdr.detectChanges();
          });
        },
        error: (err) => {
          if (solicitud !== this.solicitudHistorial) return;
          this.ngZone.run(() => {
            // Un 503 por MIGRACION_PENDIENTE o error de consulta
            const msg = extraerMensajeError(err, 'Error al obtener el historial de suscripciones.');
            this.errorHistorial = msg;
            this.historial = [];
            this.cargandoHistorial = false;
            this.cdr.detectChanges();
          });
        }
      });
  }

  // --- MODAL ASIGNAR / RENOVAR ---

  abrirModalAsignar() {
    if (!this.puedeGestionar || !this.empresaSeleccionadaId) return;

    this.modalError = '';
    this.formPlan = 'BASICO';
    this.inicioRenovacionExacto = null;
    this.inicioRenovacionInput = '';

    // Establecer fechas predeterminadas
    const ahora = new Date();
    // Si la empresa ya tiene fin vigente, sugerir renovación contigua
    if (this.planVigencia && this.planVigencia.fin) {
      const fechaFinActual = new Date(this.planVigencia.fin);
      if (fechaFinActual > ahora) {
        this.formInicio = this.formatearFechaLocalInput(fechaFinActual);
        this.inicioRenovacionExacto = this.planVigencia.fin;
        this.inicioRenovacionInput = this.formInicio;
        const unMesDespues = new Date(fechaFinActual);
        unMesDespues.setMonth(unMesDespues.getMonth() + 1);
        this.formFin = this.formatearFechaLocalInput(unMesDespues);
        this.formMotivo = 'Renovación administrativa contigua';
        this.formPlan = this.planVigencia.codigo_plan || 'BASICO';
        this.mostrarModalAsignar = true;
        return;
      }
    }

    this.formInicio = this.formatearFechaLocalInput(ahora);
    const unMesDespues = new Date(ahora);
    unMesDespues.setMonth(unMesDespues.getMonth() + 1);
    this.formFin = this.formatearFechaLocalInput(unMesDespues);
    this.formMotivo = 'Asignación de periodo administrativo';
    this.mostrarModalAsignar = true;
  }

  cerrarModalAsignar() {
    this.mostrarModalAsignar = false;
    this.modalError = '';
    this.guardando = false;
  }

  guardarSuscripcion() {
    if (!this.empresaSeleccionadaId || !this.puedeGestionar) return;

    if (!this.formPlan) {
      this.modalError = 'Debe seleccionar un plan.';
      return;
    }

    if (!this.formInicio || !this.formFin) {
      this.modalError = 'Las fechas de inicio y fin son obligatorias.';
      return;
    }

    const dInicio = new Date(this.formInicio);
    const dFin = new Date(this.formFin);

    if (isNaN(dInicio.getTime()) || isNaN(dFin.getTime())) {
      this.modalError = 'Formato de fechas inválido.';
      return;
    }

    if (dFin <= dInicio) {
      this.modalError = 'La fecha de fin debe ser posterior a la fecha de inicio.';
      return;
    }

    if (!this.formMotivo || this.formMotivo.trim().length < 3) {
      this.modalError = 'Debe especificar un motivo válido de al menos 3 caracteres.';
      return;
    }

    // Advertencia informativa de capacidad de sucursales
    if (this.formPlan === 'BASICO' && this.planVigencia?.uso?.sucursales_activas && this.planVigencia.uso.sucursales_activas > 2) {
      this.modalError = `La empresa cuenta actualmente con ${this.planVigencia.uso.sucursales_activas} sucursales activas. El plan BASICO admite un máximo de 2. Asigne PROFESIONAL o resuelva las sucursales antes de continuar.`;
      return;
    }

    this.guardando = true;
    this.modalError = '';

    const payload: AsignarSuscripcionPayload = {
      codigo_plan: this.formPlan,
      inicio: this.inicioRenovacionExacto && this.formInicio === this.inicioRenovacionInput
        ? this.inicioRenovacionExacto : dInicio.toISOString(),
      fin: dFin.toISOString(),
      motivo: this.formMotivo.trim()
    };

    this.saasService.asignarSuscripcion(this.empresaSeleccionadaId, payload)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            this.guardando = false;
            this.cerrarModalAsignar();
            this.mostrarNotificacionExito(`¡Suscripción al plan '${res.data.codigo_plan}' registrada exitosamente!`);
            this.cargarDatosEmpresa();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            this.guardando = false;
            this.modalError = extraerMensajeError(err, 'Error al registrar la suscripción.');
            this.cdr.detectChanges();
          });
        }
      });
  }

  // --- MODAL CANCELAR ---

  abrirModalCancelar(item: SuscripcionItem) {
    if (!this.puedeGestionar) return;
    this.suscripcionACancelar = item;
    this.formCancelarMotivo = '';
    this.formCancelarConfirmar = false;
    this.modalError = '';
    this.mostrarModalCancelar = true;
  }

  cerrarModalCancelar() {
    this.mostrarModalCancelar = false;
    this.suscripcionACancelar = null;
    this.modalError = '';
    this.guardando = false;
  }

  confirmarCancelacion() {
    if (!this.suscripcionACancelar || !this.empresaSeleccionadaId || !this.puedeGestionar) return;

    if (!this.formCancelarMotivo || this.formCancelarMotivo.trim().length < 3) {
      this.modalError = 'Debe indicar un motivo de cancelación de al menos 3 caracteres.';
      return;
    }

    if (!this.formCancelarConfirmar) {
      this.modalError = 'Debe marcar la casilla de confirmación explícita para proceder.';
      return;
    }

    this.guardando = true;
    this.modalError = '';

    const payload: CancelarSuscripcionPayload = {
      motivo: this.formCancelarMotivo.trim(),
      confirmar: true
    };

    this.saasService.cancelarSuscripcion(
      this.empresaSeleccionadaId,
      this.suscripcionACancelar.id_suscripcion,
      payload
    )
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.guardando = false;
            this.cerrarModalCancelar();
            this.mostrarNotificacionExito('Suscripción cancelada correctamente en el historial.');
            this.cargarDatosEmpresa();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            this.guardando = false;
            this.modalError = extraerMensajeError(err, 'Error al cancelar la suscripción.');
            this.cdr.detectChanges();
          });
        }
      });
  }

  // --- HELPERS DE FORMATEO Y ESTÉTICA ---

  estadoPeriodo(item: SuscripcionItem): string {
    if (item.estado === 'CANCELADA') return 'CANCELADA';
    const ahora = Date.now();
    if (new Date(item.inicio).getTime() > ahora) return 'PROGRAMADA';
    return new Date(item.fin).getTime() > ahora ? 'VIGENTE' : 'VENCIDA';
  }

  puedeCancelar(item: SuscripcionItem): boolean {
    return this.puedeGestionar && item.estado === 'ACTIVA';
  }

  private formatearFechaLocalInput(d: Date): string {
    const pad = (n: number) => n < 10 ? '0' + n : n;
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  formatearFechaDisplay(fechaStr: string | null | undefined): string {
    if (!fechaStr) return '—';
    try {
      const d = new Date(fechaStr);
      return d.toLocaleString('es-BO', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return fechaStr;
    }
  }

  obtenerBadgeEstadoClass(estado: string | undefined): string {
    const est = (estado || '').toUpperCase();
    if (est === 'VIGENTE') {
      return 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800';
    }
    if (est === 'PROGRAMADA') {
      return 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400 border border-amber-200 dark:border-amber-800';
    }
    if (est === 'VENCIDA' || est === 'EMPRESA_INACTIVA') {
      return 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400 border border-rose-200 dark:border-rose-800';
    }
    if (est === 'CANCELADA') {
      return 'bg-stone-100 text-zinc-600 dark:bg-slate-900 dark:text-slate-400 border border-stone-200 dark:border-slate-800';
    }
    return 'bg-zinc-100 text-zinc-700 dark:bg-slate-900 dark:text-slate-300 border border-zinc-200 dark:border-slate-800';
  }

  mostrarNotificacionExito(msg: string) {
    this.mensajeExito = msg;
    setTimeout(() => {
      this.mensajeExito = '';
      this.cdr.detectChanges();
    }, 4500);
  }
}
