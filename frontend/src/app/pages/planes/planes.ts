import { Component, OnInit, inject, ChangeDetectorRef, NgZone, DestroyRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../services/auth';
import { SaasService, PlanSaaS, CodigoPlan } from '../../services/saas';
import { extraerMensajeError } from '../../utils/error-helper';

@Component({
  selector: 'app-planes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './planes.html'
})
export class PlanesComponent implements OnInit {
  private saasService = inject(SaasService);
  public authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private destroyRef = inject(DestroyRef);

  planes: PlanSaaS[] = [];
  cargando: boolean = false;
  guardando: boolean = false;
  mensajeError: string = '';
  mensajeModalError: string = '';
  mensajeExito: string = '';

  // Modal para editar plan
  mostrarModal: boolean = false;
  planEnEdicion: PlanSaaS | null = null;
  formNombre: string = '';
  formActivo: boolean = true;

  get puedeGestionar(): boolean {
    return this.authService.isGlobalAdmin() && this.authService.hasPermission('planes.gestionar');
  }

  ngOnInit() {
    this.cargarPlanes();
  }

  cargarPlanes() {
    this.cargando = true;
    this.mensajeError = '';

    this.saasService.listarPlanes()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            if (res && res.data) {
              this.planes = res.data;
            }
            this.cargando = false;
            this.cdr.detectChanges();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            this.mensajeError = extraerMensajeError(err, 'No fue posible cargar el catálogo de planes.');
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
  }

  abrirModalEditar(plan: PlanSaaS) {
    if (!this.puedeGestionar) return;
    this.planEnEdicion = plan;
    this.formNombre = plan.nombre;
    this.formActivo = plan.activo;
    this.mensajeModalError = '';
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
    this.planEnEdicion = null;
    this.mensajeModalError = '';
    this.guardando = false;
  }

  guardarPlan() {
    if (!this.planEnEdicion || !this.puedeGestionar) return;

    if (!this.formNombre || !this.formNombre.trim()) {
      this.mensajeModalError = 'El nombre comercial del plan es requerido.';
      return;
    }

    this.guardando = true;
    this.mensajeModalError = '';

    const codigo = this.planEnEdicion.codigo;
    const payload = {
      nombre: this.formNombre.trim(),
      activo: this.formActivo
    };

    this.saasService.actualizarPlan(codigo, payload)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            this.guardando = false;
            this.cerrarModal();
            this.mostrarNotificacionExito(`Plan '${res.data.nombre}' actualizado correctamente.`);
            this.cargarPlanes();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            this.guardando = false;
            this.mensajeModalError = extraerMensajeError(err, 'Error al actualizar el plan.');
            this.cdr.detectChanges();
          });
        }
      });
  }

  mostrarNotificacionExito(msg: string) {
    this.mensajeExito = msg;
    setTimeout(() => {
      this.mensajeExito = '';
      this.cdr.detectChanges();
    }, 4500);
  }
}
