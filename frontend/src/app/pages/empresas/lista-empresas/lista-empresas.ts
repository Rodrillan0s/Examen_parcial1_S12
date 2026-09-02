import { Component, OnInit, inject, ChangeDetectorRef, NgZone, DestroyRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../../services/auth';
import { Empresa, EmpresaService } from '../../../services/empresa';

@Component({
  selector: 'app-lista-empresas',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './lista-empresas.html'
})
export class ListaEmpresasComponent implements OnInit {

  private empresaService = inject(EmpresaService);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private destroyRef = inject(DestroyRef);

  empresas: Empresa[] = [];
  empresasFiltradas: Empresa[] = [];

  filtroEstado: string = '';

  cargando: boolean = false;
  mensajeError: string = '';

  mostrarModal: boolean = false;
  modoEdicion: boolean = false;

  empresaForm: Empresa = this.inicializarEmpresa();

  totalEmpresas: number = 0;
  empresasActivas: number = 0;
  empresasInactivas: number = 0;

  async ngOnInit() {
    this.cargando = true;

    let intentos = 0;

    while (!this.authService.obtenerToken() && intentos < 10) {
      await new Promise(resolve => setTimeout(resolve, 50));
      intentos++;
    }

    if (this.authService.obtenerToken()) {
      this.cargarEmpresas();
    } else {
      this.cargando = false;
      this.mensajeError = 'No se pudo iniciar sesión. Por favor recarga.';
    }
  }

  inicializarEmpresa(): Empresa {
    return {
      nombre_empresa: '',
      nit: '',
      estado: 'ACTIVO'
    };
  }

  cargarEmpresas() {
    this.cargando = true;
    this.mensajeError = '';

    this.empresaService.listarEmpresas()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            if (res.success) {
              this.empresas = [...res.data];
              this.aplicarFiltros();
            } else {
              this.mensajeError = res.message || 'Error al obtener empresas.';
            }

            this.cargando = false;
            this.cdr.detectChanges();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            this.mensajeError = err?.error?.detail || 'Error de conexión al cargar las empresas.';
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
  }

  aplicarFiltros() {
    if (this.filtroEstado === '') {
      this.empresasFiltradas = [...this.empresas];
    } else {
      this.empresasFiltradas = this.empresas.filter(e => e.estado === this.filtroEstado);
    }

    this.actualizarMetricas();
  }

  actualizarMetricas() {
    this.totalEmpresas = this.empresasFiltradas.length;
    this.empresasActivas = this.empresasFiltradas.filter(e => e.estado === 'ACTIVO').length;
    this.empresasInactivas = this.empresasFiltradas.filter(e => e.estado === 'INACTIVO').length;
  }

  obtenerIniciales(nombre: string): string {
    if (!nombre) return 'EM';

    const partes = nombre.trim().split(' ');

    if (partes.length >= 2) {
      return (partes[0][0] + partes[1][0]).toUpperCase();
    }

    return nombre.substring(0, 2).toUpperCase();
  }

  abrirModalNuevo() {
    this.modoEdicion = false;
    this.empresaForm = this.inicializarEmpresa();
    this.mostrarModal = true;
  }

  abrirModalEditar(empresa: Empresa) {
    this.modoEdicion = true;
    this.empresaForm = { ...empresa };
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
  }

  guardarEmpresa() {
    if (!this.empresaForm.nombre_empresa || this.empresaForm.nombre_empresa.trim().length === 0) {
      alert('El nombre de la empresa es obligatorio.');
      return;
    }

    if (!this.empresaForm.nit || String(this.empresaForm.nit).trim().length === 0) {
      alert('El NIT es obligatorio.');
      return;
    }

    if (!this.empresaForm.estado || this.empresaForm.estado.trim().length === 0) {
      alert('El estado es obligatorio.');
      return;
    }

    this.cargando = true;

    if (this.modoEdicion) {
      if (!this.empresaForm.id_empresa) {
        alert('No se encontró el ID de la empresa.');
        this.cargando = false;
        return;
      }

      this.empresaService.actualizarEmpresa(this.empresaForm.id_empresa, this.empresaForm)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
          next: () => {
            this.ngZone.run(() => {
              this.cerrarModal();
              this.cargarEmpresas();
            });
          },
          error: (err) => {
            this.ngZone.run(() => {
              alert(err?.error?.detail || 'Error al actualizar la empresa.');
              this.cargando = false;
              this.cdr.detectChanges();
            });
          }
        });
    } else {
      this.empresaService.crearEmpresa(this.empresaForm)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
          next: () => {
            this.ngZone.run(() => {
              this.cerrarModal();
              this.cargarEmpresas();
            });
          },
          error: (err) => {
            this.ngZone.run(() => {
              alert(err?.error?.detail || 'Error al crear la empresa. Verifique los datos.');
              this.cargando = false;
              this.cdr.detectChanges();
            });
          }
        });
    }
  }

  eliminarEmpresa(idEmpresa?: number) {
    if (!idEmpresa) return;

    const confirmar = confirm('¿Está seguro que desea eliminar esta empresa permanentemente?');

    if (!confirmar) return;

    this.cargando = true;

    this.empresaService.eliminarEmpresa(idEmpresa)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cargarEmpresas();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            alert(err?.error?.detail || 'Error al eliminar la empresa.');
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
  }
}