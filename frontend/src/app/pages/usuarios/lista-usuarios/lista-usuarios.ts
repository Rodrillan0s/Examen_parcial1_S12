import { Component, OnInit, inject, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
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
  public authService = inject(AuthService);
  private ngZone = inject(NgZone);
  private apiUrl = environment.apiUrl;
  private destroyRef = inject(DestroyRef);

  // --- VARIABLES DE DATOS ---
  usuarios: Usuario[] = [];
  usuariosFiltrados: Usuario[] = []; // <-- Nueva variable para la vista filtrada
  empresas: Empresa[] = []; 
  
  // --- VARIABLE PARA EL FILTRO ---
  filtroEmpresa: string = 'TODOS'; // 'TODOS' significa "Mostrar Todas"
  filtroEstado: string = 'TODOS';  // 'TODOS', 'ACTIVO', 'INACTIVO'
  filtroTexto: string = '';   // Búsqueda por texto

  get busquedaTexto(): string {
    return this.filtroTexto;
  }
  set busquedaTexto(val: string) {
    this.filtroTexto = val;
  }

  cargando: boolean = false;
  mensajeError: string = '';

  mostrarModal: boolean = false;
  modoEdicion: boolean = false;
  
  usuarioForm: Usuario = this.inicializarUsuario();

  totalUsuarios: number = 0;
  usuariosActivos: number = 0;
  usuariosInactivos: number = 0;

  rolesDisponibles: { id: number; id_rol?: number; nombre: string }[] = [
    { id: 1, id_rol: 1, nombre: 'ADMINISTRADOR' },
    { id: 2, id_rol: 2, nombre: 'CLIENTE' },
    { id: 3, id_rol: 3, nombre: 'ADMINISTRADOR_TIENDA' },
    { id: 4, id_rol: 4, nombre: 'ENCARGADO_SUCURSAL' },
    { id: 5, id_rol: 5, nombre: 'CAJERO' },
    { id: 6, id_rol: 6, nombre: 'PROVEEDOR' }
  ];

  // --- PROPIEDADES DE ALCANCE Y CONTEXTO ---
  get scope(): 'PLATAFORMA' | 'EMPRESA' | 'SUCURSAL' {
    return this.authService.getScopeLevel();
  }

  get isGlobalAdmin(): boolean {
    return this.authService.isGlobalAdmin();
  }

  get isStoreAdmin(): boolean {
    return this.authService.isStoreAdmin();
  }

  get isBranchManager(): boolean {
    return this.authService.isBranchManager();
  }

  get tituloWorkspace(): string {
    const scope = this.scope;
    if (scope === 'PLATAFORMA') return 'Usuarios de la plataforma';
    if (scope === 'EMPRESA') return `Equipo de ${this.authService.getUserCompanyName()}`;
    return `Equipo de ${this.authService.getUserBranchName()}`;
  }

  get subtituloWorkspace(): string {
    const scope = this.scope;
    if (scope === 'PLATAFORMA') return 'Gestiona el acceso global de usuarios y su asignación multi-tenant a empresas.';
    if (scope === 'EMPRESA') return 'Gestiona los miembros, personal operativo y roles asignados a tu empresa.';
    return 'Personal activo y asignado a tu sucursal.';
  }

  get botonCrearTexto(): string {
    const scope = this.scope;
    if (scope === 'PLATAFORMA') return '+ Nuevo usuario';
    if (scope === 'EMPRESA') return '+ Invitar usuario';
    return '+ Asignar personal';
  }

  get terceraMetricaTitulo(): string {
    const scope = this.scope;
    if (scope === 'PLATAFORMA') return 'Empresas Registradas';
    if (scope === 'EMPRESA') return 'Sucursales';
    return 'Sucursal Activa';
  }

  get terceraMetricaValor(): number {
    const scope = this.scope;
    if (scope === 'PLATAFORMA') return this.empresas.length || 1;
    if (scope === 'EMPRESA') return 1;
    return 1;
  }

  async ngOnInit() {
    this.cargando = true;
    
    // Esperar a que el token esté disponible
    let intentos = 0;
    while (!this.authService.obtenerToken() && intentos < 10) {
      await new Promise(r => setTimeout(r, 50)); 
      intentos++;
    }

    if (this.authService.obtenerToken()) {
      const currentUser = this.authService.obtenerUsuario();
      if (!this.isGlobalAdmin && currentUser?.id_empresa) {
        this.filtroEmpresa = String(currentUser.id_empresa);
      }
      this.cargarRoles();
      this.cargarEmpresas();
      this.cargarUsuarios();
    } else {
      this.cargando = false;
      this.mensajeError = "No se pudo iniciar sesión. Por favor recarga.";
    }
  }

  // --- LÓGICA DE FILTRADO Y MÉTRICAS ---
  
  aplicarFiltros() {
    let resultado = [...this.usuarios];

    const currentUser = this.authService.obtenerUsuario();

    // Para Administrador de Tienda o Encargado de Sucursal, forzar el filtrado por su empresa
    if (!this.isGlobalAdmin && currentUser?.id_empresa) {
      resultado = resultado.filter(u => u.id_empresa === currentUser.id_empresa);
    } else if (this.filtroEmpresa !== '' && this.filtroEmpresa !== 'TODOS') {
      const idBuscado = Number(this.filtroEmpresa);
      resultado = resultado.filter(u => u.id_empresa === idBuscado);
    }

    // Filtro por Estado (ACTIVO / INACTIVO)
    if (this.filtroEstado !== '' && this.filtroEstado !== 'TODOS') {
      resultado = resultado.filter(u => u.estado === this.filtroEstado);
    }

    // Filtro por Texto (Nombre, CI, Correo, Username, Rol)
    if (this.filtroTexto.trim() !== '') {
      const q = this.filtroTexto.toLowerCase().trim();
      resultado = resultado.filter(u =>
        (u.nombre_completo && u.nombre_completo.toLowerCase().includes(q)) ||
        (u.correo && u.correo.toLowerCase().includes(q)) ||
        (u.ci && u.ci.toLowerCase().includes(q)) ||
        (u.nombre_usuario && u.nombre_usuario.toLowerCase().includes(q)) ||
        (u.nombre_rol && u.nombre_rol.toLowerCase().includes(q))
      );
    }

    this.usuariosFiltrados = resultado;
    this.actualizarMetricas();
  }

  limpiarFiltros() {
    const currentUser = this.authService.obtenerUsuario();
    if (!this.isGlobalAdmin && currentUser?.id_empresa) {
      this.filtroEmpresa = String(currentUser.id_empresa);
    } else {
      this.filtroEmpresa = 'TODOS';
    }
    this.filtroEstado = 'TODOS';
    this.filtroTexto = '';
    this.aplicarFiltros();
  }

  actualizarMetricas() {
    this.totalUsuarios = this.usuariosFiltrados.length;
    this.usuariosActivos = this.usuariosFiltrados.filter(u => u.estado === 'ACTIVO').length;
    this.usuariosInactivos = this.usuariosFiltrados.filter(u => u.estado === 'INACTIVO').length;
  }

  getIniciales(nombre: string): string {
    return this.obtenerIniciales(nombre);
  }

  obtenerIniciales(nombre: string): string {
    if (!nombre) return 'AU';
    const partes = nombre.trim().split(' ');
    if (partes.length >= 2) {
      return (partes[0][0] + partes[1][0]).toUpperCase();
    }
    return nombre.substring(0, 2).toUpperCase();
  }

  inicializarUsuario(): Usuario {
    const currentUser = this.authService.obtenerUsuario();
    const defaultEmpresaId = (!this.isGlobalAdmin && currentUser?.id_empresa) ? currentUser.id_empresa : null;
    return {
      ci: '',
      nombre_usuario: '',
      nombre_completo: '',
      correo: '',
      telefono: '',
      direccion: '',
      estado: 'ACTIVO',
      nro_rol: this.isBranchManager ? 5 : (this.isStoreAdmin ? 4 : 3),
      id_empresa: defaultEmpresaId
    };
  }

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    return token ? new HttpHeaders({ 'Authorization': `Bearer ${token}` }) : new HttpHeaders();
  }

  // --- MÉTODOS DE RED ---

  cargarRoles() {
    this.http.get<any>(`${this.apiUrl}/api/roles/`, { headers: this.getHeaders() })
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success && res.data && res.data.length > 0) {
            const rolesMapeados = res.data.map((r: any) => ({
              id: Number(r.id_rol || r.nro_rol),
              nombre: String(r.nombre_rol || r.nombre || '').toUpperCase()
            }));

            // Filtrar cualquier rol legado del proyecto anterior
            const rolesFiltrados = rolesMapeados.filter((r: any) => 
              !['GERENTE TALLER', 'GERENTE_TALLER', 'GERENTE', 'MECANICO', 'MECÁNICO', 'TECNICO'].includes(r.nombre)
            );

            if (rolesFiltrados.length > 0) {
              this.rolesDisponibles = rolesFiltrados;
            }
          }
          this.cdr.detectChanges();
        });
      },
      error: (err) => console.log('Roles RBAC usando valores locales', err)
    });
  }

  cargarEmpresas() {
    this.http.get<RespuestaApiEmpresas>(`${this.apiUrl}/api/empresas`, { headers: this.getHeaders() })
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

    this.http.get<RespuestaApiUsuarios>(`${this.apiUrl}/api/usuarios/`, { headers: this.getHeaders() }).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            this.usuarios = [...res.data]; 
            this.aplicarFiltros();
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
    if (!this.usuarioForm.nombre_completo || !this.usuarioForm.nombre_usuario || !this.usuarioForm.id_empresa || !this.usuarioForm.nro_rol) {
      alert('Por favor complete todos los campos obligatorios: Nombre Completo, Usuario, Rol y Empresa.');
      return;
    }

    this.usuarioForm.nro_rol = Number(this.usuarioForm.nro_rol);
    this.usuarioForm.id_empresa = Number(this.usuarioForm.id_empresa);

    this.cargando = true;

    if (this.modoEdicion) {
      this.http.put(`${this.apiUrl}/api/usuarios/${this.usuarioForm.nro_usuario}`, this.usuarioForm, { headers: this.getHeaders() }).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cerrarModal();
            this.cargarUsuarios();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            const detail = err.error?.detail || 'Error al actualizar el usuario.';
            alert(detail);
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

      this.http.post(`${this.apiUrl}/api/usuarios/`, this.usuarioForm, { headers: this.getHeaders() }).subscribe({
        next: () => {
          this.ngZone.run(() => {
            this.cerrarModal();
            this.cargarUsuarios();
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            const detail = err.error?.detail || 'Error al crear el usuario. Verifique los datos.';
            alert(detail);
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
      this.http.delete(`${this.apiUrl}/api/usuarios/${id}`, { headers: this.getHeaders() }).subscribe({
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

  abrirModalEditar(usuario: any) {
    this.modoEdicion = true;
    const rolEncontrado = usuario.id_rol || usuario.nro_rol || 3;
    this.usuarioForm = { 
      ...usuario, 
      nro_rol: Number(rolEncontrado),
      id_empresa: usuario.id_empresa ? Number(usuario.id_empresa) : null,
      password: '' 
    }; 
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
  }
}