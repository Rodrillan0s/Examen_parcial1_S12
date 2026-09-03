import { Component, OnInit, inject, ChangeDetectorRef, NgZone, DestroyRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../../services/auth';
import { Sucursal, SucursalService } from '../../../services/sucursales';
import { Empresa, EmpresaService } from '../../../services/empresa';

@Component({
  selector: 'app-lista-sucursales',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './lista-sucursales.html'
})
export class ListaSucursalesComponent implements OnInit {

  private sucursalService = inject(SucursalService);
  private empresaService = inject(EmpresaService);
  public authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private destroyRef = inject(DestroyRef);

  sucursales: Sucursal[] = [];
  sucursalesFiltradas: Sucursal[] = [];
  empresas: Empresa[] = []; // List of companies for global admins

  filtroEstado: string = 'TODOS';

  cargando: boolean = false;
  mensajeError: string = '';

  mostrarModal: boolean = false;
  modoEdicion: boolean = false;

  sucursalForm: Sucursal = this.inicializarSucursal();

  totalSucursales: number = 0;
  sucursalesActivas: number = 0;
  sucursalesInactivas: number = 0;

  get idEmpresaSesion(): number {
    const user = this.authService.obtenerUsuario();
    return user?.id_empresa || 0;
  }
  
  get isGlobalAdmin(): boolean {
    return this.authService.getScopeLevel() === 'PLATAFORMA';
  }

  async ngOnInit() {
    this.cargando = true;

    let intentos = 0;
    while (!this.authService.obtenerToken() && intentos < 10) {
      await new Promise(resolve => setTimeout(resolve, 50));
      intentos++;
    }

    if (this.authService.obtenerToken()) {
      if (this.isGlobalAdmin) {
        this.cargarEmpresas();
      }
      this.cargarSucursales();
    } else {
      this.cargando = false;
      this.mensajeError = 'No se pudo iniciar sesión. Por favor recarga.';
    }
  }

  cargarEmpresas() {
    this.empresaService.listarEmpresas()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            if (res.success) {
              this.empresas = res.data;
            }
          });
        }
      });
  }

  inicializarSucursal(): Sucursal {
    return {
      nombre: '',
      direccion: '',
      id_empresa: this.idEmpresaSesion,
      activo: true
    };
  }

  cargarSucursales() {
    this.cargando = true;
    this.mensajeError = '';

    // If EMPRESA admin, only load branches for their company.
    // Assuming backend already filters if they don't have global permission, 
    // but passing id_empresa explicitly enforces it on the query parameter.
    const idEmpresaParam = this.authService.getScopeLevel() !== 'PLATAFORMA' ? this.idEmpresaSesion : undefined;

    this.sucursalService.listarSucursales(idEmpresaParam)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            if (res.success) {
              this.sucursales = [...res.data];
              this.aplicarFiltros();
            } else {
              this.mensajeError = res.message || 'Error al obtener sucursales.';
            }

            this.cargando = false;
            this.cdr.detectChanges();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            this.mensajeError = err?.error?.detail || 'Error de conexión al cargar las sucursales.';
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
  }

  aplicarFiltros() {
    if (this.filtroEstado === 'TODOS') {
      this.sucursalesFiltradas = [...this.sucursales];
    } else {
      const targetActivo = this.filtroEstado === 'ACTIVO';
      this.sucursalesFiltradas = this.sucursales.filter(s => s.activo === targetActivo);
    }

    this.actualizarMetricas();
  }

  actualizarMetricas() {
    this.totalSucursales = this.sucursalesFiltradas.length;
    this.sucursalesActivas = this.sucursalesFiltradas.filter(s => s.activo === true).length;
    this.sucursalesInactivas = this.sucursalesFiltradas.filter(s => s.activo === false).length;
  }

  obtenerIniciales(nombre: string): string {
    if (!nombre) return 'SU';
    const partes = nombre.trim().split(' ');
    if (partes.length >= 2) {
      return (partes[0][0] + partes[1][0]).toUpperCase();
    }
    return nombre.substring(0, 2).toUpperCase();
  }

  abrirModalNuevo() {
    this.modoEdicion = false;
    this.sucursalForm = this.inicializarSucursal();
    this.mostrarModal = true;
  }

  abrirModalEditar(sucursal: Sucursal) {
    this.modoEdicion = true;
    this.sucursalForm = { ...sucursal };
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
  }

  guardarSucursal() {
    if (!this.sucursalForm.nombre || this.sucursalForm.nombre.trim().length === 0) {
      alert('El nombre de la sucursal es obligatorio.');
      return;
    }

    if (!this.sucursalForm.direccion || String(this.sucursalForm.direccion).trim().length === 0) {
      alert('La dirección es obligatoria.');
      return;
    }

    if (this.isGlobalAdmin && (!this.sucursalForm.id_empresa || this.sucursalForm.id_empresa === 0)) {
      alert('Debe seleccionar una empresa para la sucursal.');
      return;
    }

    if (!this.sucursalForm.id_empresa) {
      this.sucursalForm.id_empresa = this.idEmpresaSesion;
    }

    this.cargando = true;

    if (this.modoEdicion) {
      if (!this.sucursalForm.id_sucursal) {
        alert('No se encontró el ID de la sucursal.');
        this.cargando = false;
        return;
      }

      this.sucursalService.actualizarSucursal(this.sucursalForm.id_sucursal, this.sucursalForm)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
          next: () => {
            this.ngZone.run(() => {
              this.cerrarModal();
              this.cargarSucursales();
            });
          },
          error: (err) => {
            this.ngZone.run(() => {
              alert(err?.error?.detail || 'Error al actualizar la sucursal.');
              this.cargando = false;
              this.cdr.detectChanges();
            });
          }
        });
    } else {
      this.sucursalService.crearSucursal(this.sucursalForm)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
          next: () => {
            this.ngZone.run(() => {
              this.cerrarModal();
              this.cargarSucursales();
            });
          },
          error: (err) => {
            this.ngZone.run(() => {
              alert(err?.error?.detail || 'Error al crear la sucursal. Verifique los datos.');
              this.cargando = false;
              this.cdr.detectChanges();
            });
          }
        });
    }
  }

  eliminarSucursal(id_sucursal?: number) {
    if (!id_sucursal) return;

    const confirmar = confirm('¿Está seguro que desea desactivar esta sucursal?');

    if (!confirmar) return;

    this.cargando = true;

    this.sucursalService.eliminarSucursal(id_sucursal)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cargarSucursales();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            alert(err?.error?.detail || 'Error al desactivar la sucursal.');
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
  }
}
