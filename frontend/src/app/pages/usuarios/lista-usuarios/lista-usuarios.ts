import { Component, OnInit, inject, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import { AuthService } from '../../../services/auth';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { DestroyRef } from '@angular/core';

export interface Empresa {
  id_empresa: number;
  nombre_empresa: string;
  nit?: string | null;
  estado: string;
}

export interface Usuario {
  nro_usuario?: number;
  ci: string;
  nombre_usuario: string;
  estado: string;
  id_empresa?: number | null;
  nombre_empresa?: string; 
  nombre_completo: string;
  correo: string;
  telefono: string;
  direccion: string;
  nombre_rol?: string; 
  nro_rol: number;     
  password?: string;
}

export interface RespuestaApiUsuarios {
  success: boolean;
  message: string;
  data: Usuario[];
}

export interface RespuestaApiEmpresas {
  success: boolean;
  message: string;
  data: Empresa[];
}

@Component({
  selector: 'app-lista-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './lista-usuarios.html'
})
export class ListaUsuariosComponent implements OnInit {
  
  private http = inject(HttpClient);
  private cdr = inject(ChangeDetectorRef);
  private authService = inject(AuthService);
  private ngZone = inject(NgZone);
  private apiUrl = environment.apiUrl;
  private destroyRef = inject(DestroyRef);

  // --- VARIABLES DE DATOS ---
  usuarios: Usuario[] = [];
  usuariosFiltrados: Usuario[] = []; // <-- Nueva variable para la vista filtrada
  empresas: Empresa[] = []; 
  
  // --- VARIABLE PARA EL FILTRO ---
  filtroEmpresa: string = ''; // '' significa "Mostrar Todas"

  cargando: boolean = false;
  mensajeError: string = '';

  mostrarModal: boolean = false;
  modoEdicion: boolean = false;
  
  usuarioForm: Usuario = this.inicializarUsuario();

  totalUsuarios: number = 0;
  usuariosActivos: number = 0;
  usuariosInactivos: number = 0;

  rolesDisponibles = [
    { id: 1, nombre: 'ADMINISTRADOR' },
    { id: 2, nombre: 'GERENTE TALLER' },
    { id: 3, nombre: 'MECANICO' },
    { id: 4, nombre: 'CLIENTE' }
  ];

  async ngOnInit() {
    this.cargando = true;
    
    // Esperar a que el token esté disponible (esto evita la petición 401 inicial)
    let intentos = 0;
    while (!this.authService.obtenerToken() && intentos < 10) {
      await new Promise(r => setTimeout(r, 50)); 
      intentos++;
    }

    // Si después de esperar sigue sin haber token, no hacemos nada
    if (this.authService.obtenerToken()) {
      this.cargarEmpresas();
      this.cargarUsuarios();
    } else {
      this.cargando = false;
      this.mensajeError = "No se pudo iniciar sesión. Por favor recarga.";
    }
  }

  // --- LÓGICA DE FILTRADO Y MÉTRICAS ---
  
  aplicarFiltros() {
    if (this.filtroEmpresa === '') {
      // Si no hay filtro, mostramos todos
      this.usuariosFiltrados = [...this.usuarios];
    } else {
      // Si hay filtro, convertimos el ID a número y filtramos
      const idBuscado = Number(this.filtroEmpresa);
      this.usuariosFiltrados = this.usuarios.filter(u => u.id_empresa === idBuscado);
    }
    // Actualizamos las métricas basándonos EN LO FILTRADO, no en el total general
    this.actualizarMetricas();
  }

  actualizarMetricas() {
    this.totalUsuarios = this.usuariosFiltrados.length;
    this.usuariosActivos = this.usuariosFiltrados.filter(u => u.estado === 'ACTIVO').length;
    this.usuariosInactivos = this.usuariosFiltrados.filter(u => u.estado === 'INACTIVO').length;
  }

  obtenerIniciales(nombre: string): string {
    if (!nombre) return 'XX';
    const partes = nombre.trim().split(' ');
    if (partes.length >= 2) {
      return (partes[0][0] + partes[1][0]).toUpperCase();
    }
    return nombre.substring(0, 2).toUpperCase();
  }

  inicializarUsuario(): Usuario {
    return {
      ci: '', nombre_usuario: '', nombre_completo: '', correo: '',
      telefono: '', direccion: '', estado: 'ACTIVO', nro_rol: 4, 
      id_empresa: null 
    };
  }

  // --- MÉTODOS DE RED ---

  cargarEmpresas() {
    // Obtenemos el token directamente del servicio
    const token = this.authService.obtenerToken();
    
    // Creamos los headers manualmente
    const headers = { 
      'Authorization': `Bearer ${token}` 
    };

    this.http.get<RespuestaApiEmpresas>(`${this.apiUrl}/api/empresas`, { headers })
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            this.empresas = res.data.filter(e => e.estado === 'ACTIVO');
          }
          this.cdr.detectChanges();
        });
      },
      error: (err) => console.error('Error cargando empresas:', err)
    });
  }

  cargarUsuarios() {
    this.cargando = true;
    this.mensajeError = '';
    
    this.http.get<RespuestaApiUsuarios>(`${this.apiUrl}/api/usuarios/`).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            this.usuarios = [...res.data]; 
            this.aplicarFiltros(); // <-- LLAMAMOS AL FILTRO AL TERMINAR DE CARGAR
          } else {
            this.mensajeError = res.message || 'Error al obtener datos.';
          }
          this.cargando = false;
          this.cdr.detectChanges(); 
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          this.mensajeError = 'Error de conexión al cargar los usuarios.';
          this.cargando = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  guardarUsuario() {
    if (!this.usuarioForm.ci || !this.usuarioForm.nombre_completo || !this.usuarioForm.nombre_usuario || !this.usuarioForm.id_empresa) {
      alert('Por favor complete todos los campos obligatorios, incluyendo la Empresa.');
      return;
    }

    this.cargando = true;

    if (this.modoEdicion) {
      this.http.put(`${this.apiUrl}/api/usuarios/${this.usuarioForm.nro_usuario}`, this.usuarioForm).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cerrarModal();
            this.cargarUsuarios();
          });
        },
        error: () => {
          this.ngZone.run(() => {
            alert('Error al actualizar el usuario.');
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    } else {
      if (!this.usuarioForm.password) {
        alert('La contraseña es obligatoria para usuarios nuevos.');
        this.cargando = false;
        return;
      }

      this.http.post(`${this.apiUrl}/api/usuarios/`, this.usuarioForm).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cerrarModal();
            this.cargarUsuarios();
          });
        },
        error: () => {
          this.ngZone.run(() => {
            alert('Error al crear el usuario. Verifique los datos.');
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    }
  }

  eliminarUsuario(id?: number) {
    if (!id) return;
    if (confirm('¿Está seguro que desea eliminar a este usuario?')) {
      this.http.delete(`${this.apiUrl}/api/usuarios/${id}`).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cargarUsuarios();
          });
        },
        error: () => alert('Error al eliminar el usuario.')
      });
    }
  }

  // --- CONTROL DEL MODAL ---

  abrirModalNuevo() {
    this.modoEdicion = false;
    this.usuarioForm = this.inicializarUsuario();
    this.mostrarModal = true;
  }

  abrirModalEditar(usuario: Usuario) {
    this.modoEdicion = true;
    this.usuarioForm = { ...usuario, password: '' }; 
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
  }
}