import { Component, OnInit, inject, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface Rol {
  nro_rol?: number;
  nombre_rol: string;
  descripcion: string;
  fecha_registro?: string;
}

export interface RespuestaApiRoles {
  success: boolean;
  message: string;
  data: Rol[];
}

@Component({
  selector: 'app-roles',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './roles.html'
})
export class RolesComponent implements OnInit {
  
  private http = inject(HttpClient);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private apiUrl = environment.apiUrl;

  roles: Rol[] = [];
  cargando: boolean = false;
  mensajeError: string = '';
  mensajeExito: string = '';

  mostrarModal: boolean = false;
  modoEdicion: boolean = false;
  
  rolForm: Rol = this.inicializarRol();
  totalRoles: number = 0;

  ngOnInit() {
    this.cargarRoles();
  }

  inicializarRol(): Rol {
    return {
      nombre_rol: '',
      descripcion: ''
    };
  }

  cargarRoles() {
    this.cargando = true;
    this.mensajeError = '';
    
    // Petición GET limpia. El interceptor inyecta el token.
    this.http.get<RespuestaApiRoles>(`${this.apiUrl}/api/roles/`).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            this.roles = [...res.data];
            this.totalRoles = this.roles.length;
          } else {
            this.mostrarError(res.message || 'Error al obtener los roles.');
          }
          this.cargando = false;
          this.cdr.detectChanges(); 
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          this.mostrarError('Error de conexión al cargar los roles.');
          this.cargando = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  guardarRol() {
    if (!this.rolForm.nombre_rol || this.rolForm.nombre_rol.trim() === '') {
      this.mostrarError('El nombre del rol es obligatorio.');
      return;
    }

    this.cargando = true;

    if (this.modoEdicion && this.rolForm.nro_rol) {
      // Petición PUT
      this.http.put(`${this.apiUrl}/api/roles/${this.rolForm.nro_rol}`, this.rolForm).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cerrarModal();
            this.mostrarExito('Rol actualizado correctamente.');
            this.cargarRoles();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            const msj = err.error?.detail || 'Error al actualizar el rol.';
            this.mostrarError(msj);
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    } else {
      // Petición POST
      this.http.post(`${this.apiUrl}/api/roles/`, this.rolForm).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cerrarModal();
            this.mostrarExito('Rol registrado correctamente.');
            this.cargarRoles();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            const msj = err.error?.detail || 'Error al crear el rol.';
            this.mostrarError(msj);
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    }
  }

  eliminarRol(id?: number) {
    if (!id) return;
    
    if (confirm('¿Está seguro que desea eliminar este rol de forma permanente?')) {
      this.cargando = true;
      this.http.delete(`${this.apiUrl}/api/roles/${id}`).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.mostrarExito('Rol eliminado correctamente.');
            this.cargarRoles();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            // FastAPI devuelve el mensaje de restricción de llaves foráneas en err.error.detail
            const msj = err.error?.detail || 'Error al eliminar el rol.';
            this.mostrarError(msj);
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    }
  }

  // --- CONTROL DEL MODAL Y ALERTAS ---

  abrirModalNuevo() {
    this.modoEdicion = false;
    this.rolForm = this.inicializarRol();
    this.mostrarModal = true;
  }

  abrirModalEditar(rol: Rol) {
    this.modoEdicion = true;
    this.rolForm = { ...rol }; 
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
  }

  mostrarError(mensaje: string) {
    this.mensajeError = mensaje;
    setTimeout(() => {
      this.mensajeError = '';
      this.cdr.detectChanges();
    }, 5000);
  }

  mostrarExito(mensaje: string) {
    this.mensajeExito = mensaje;
    setTimeout(() => {
      this.mensajeExito = '';
      this.cdr.detectChanges();
    }, 4000);
  }
}