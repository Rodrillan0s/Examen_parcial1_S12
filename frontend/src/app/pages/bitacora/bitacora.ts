import { Component, OnInit, inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth';

interface RegistroBitacora {
  id: number;
  fecha: string;
  hora: string;
  usuario: string;
  rol: string;
  modulo: string;
  accion: string;
  descripcion: string;
  ip: string;
  estado: 'EXITOSO' | 'ADVERTENCIA' | 'ERROR';
}

@Component({
  selector: 'app-bitacora',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './bitacora.html'
})
export class BitacoraComponent implements OnInit {

  private authService = inject(AuthService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);

  usuarioActual: any = null;
  modoOscuro: boolean = false;

  textoBusqueda: string = '';
  filtroModulo: string = '';
  filtroEstado: string = '';

  registros: RegistroBitacora[] = [
    {
      id: 1,
      fecha: '2026-06-09',
      hora: '08:15',
      usuario: 'Carlos Méndez',
      rol: 'ADMINISTRADOR',
      modulo: 'Seguridad y Usuarios',
      accion: 'Inicio de sesión',
      descripcion: 'El usuario ingresó correctamente al sistema administrativo.',
      ip: '192.168.1.25',
      estado: 'EXITOSO'
    },
    {
      id: 2,
      fecha: '2026-06-09',
      hora: '08:28',
      usuario: 'Laura Justiniano',
      rol: 'GERENTE TALLER',
      modulo: 'Red de Talleres',
      accion: 'Actualización',
      descripcion: 'Se actualizó la disponibilidad del taller AutoFix Norte.',
      ip: '192.168.1.31',
      estado: 'EXITOSO'
    },
    {
      id: 3,
      fecha: '2026-06-09',
      hora: '08:41',
      usuario: 'Mario Rojas',
      rol: 'MECANICO',
      modulo: 'Emergencias',
      accion: 'Cambio de estado',
      descripcion: 'La emergencia Nro. 1045 cambió de PENDIENTE a EN CURSO.',
      ip: '192.168.1.47',
      estado: 'EXITOSO'
    },
    {
      id: 4,
      fecha: '2026-06-09',
      hora: '09:02',
      usuario: 'Sistema',
      rol: 'SERVICIO INTERNO',
      modulo: 'Analítica y KPIs',
      accion: 'Consulta',
      descripcion: 'Se consultaron métricas operacionales globales del dashboard.',
      ip: '127.0.0.1',
      estado: 'EXITOSO'
    },
    {
      id: 5,
      fecha: '2026-06-09',
      hora: '09:18',
      usuario: 'Roberto Pérez',
      rol: 'ADMINISTRADOR',
      modulo: 'Seguridad y Usuarios',
      accion: 'Intento fallido',
      descripcion: 'Intento de acceso a módulo restringido desde una cuenta sin permisos suficientes.',
      ip: '192.168.1.52',
      estado: 'ADVERTENCIA'
    },
    {
      id: 6,
      fecha: '2026-06-09',
      hora: '09:36',
      usuario: 'Daniela Vargas',
      rol: 'GERENTE TALLER',
      modulo: 'Emergencias',
      accion: 'Cotización',
      descripcion: 'Se emitió una oferta comercial para la emergencia Nro. 1051.',
      ip: '192.168.1.36',
      estado: 'EXITOSO'
    },
    {
      id: 7,
      fecha: '2026-06-09',
      hora: '10:05',
      usuario: 'Sistema',
      rol: 'SERVICIO INTERNO',
      modulo: 'IA y Diagnóstico',
      accion: 'Análisis IA',
      descripcion: 'Se generó un prediagnóstico automático con evidencias multimedia.',
      ip: '127.0.0.1',
      estado: 'EXITOSO'
    },
    {
      id: 8,
      fecha: '2026-06-09',
      hora: '10:22',
      usuario: 'Luis Gutiérrez',
      rol: 'MECANICO',
      modulo: 'Emergencias',
      accion: 'Error de operación',
      descripcion: 'No se pudo actualizar el tracking por pérdida temporal de conexión.',
      ip: '192.168.1.61',
      estado: 'ERROR'
    },
    {
      id: 9,
      fecha: '2026-06-09',
      hora: '10:40',
      usuario: 'Fernanda Salinas',
      rol: 'ADMINISTRADOR',
      modulo: 'Copias de Respaldo',
      accion: 'Respaldo',
      descripcion: 'Se generó una copia de respaldo manual del sistema.',
      ip: '192.168.1.20',
      estado: 'EXITOSO'
    },
    {
      id: 10,
      fecha: '2026-06-09',
      hora: '11:03',
      usuario: 'Jorge Paz',
      rol: 'GERENTE TALLER',
      modulo: 'Red de Talleres',
      accion: 'Registro',
      descripcion: 'Se registró un nuevo taller asociado a la plataforma.',
      ip: '192.168.1.44',
      estado: 'EXITOSO'
    }
  ];

  registrosFiltrados: RegistroBitacora[] = [];

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.usuarioActual = this.authService.obtenerUsuario();

      if (!this.usuarioActual || this.authService.tokenExpirado()) {
        this.cerrarSesion();
        return;
      }

      if (localStorage.getItem('tema_sistema') === 'dark') {
        this.modoOscuro = true;
        document.documentElement.classList.add('dark');
      }

      this.aplicarFiltros();
    }
  }

  aplicarFiltros(): void {
    let data = [...this.registros];

    if (this.textoBusqueda.trim()) {
      const busqueda = this.textoBusqueda.toLowerCase().trim();

      data = data.filter(item =>
        item.usuario.toLowerCase().includes(busqueda) ||
        item.rol.toLowerCase().includes(busqueda) ||
        item.modulo.toLowerCase().includes(busqueda) ||
        item.accion.toLowerCase().includes(busqueda) ||
        item.descripcion.toLowerCase().includes(busqueda) ||
        item.ip.toLowerCase().includes(busqueda)
      );
    }

    if (this.filtroModulo) {
      data = data.filter(item => item.modulo === this.filtroModulo);
    }

    if (this.filtroEstado) {
      data = data.filter(item => item.estado === this.filtroEstado);
    }

    this.registrosFiltrados = data;
  }

  limpiarFiltros(): void {
    this.textoBusqueda = '';
    this.filtroModulo = '';
    this.filtroEstado = '';
    this.aplicarFiltros();
  }

  alternarModoOscuro(): void {
    this.modoOscuro = !this.modoOscuro;

    if (this.modoOscuro) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('tema_sistema', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('tema_sistema', 'light');
    }
  }

  navegarA(ruta: string): void {
    this.router.navigate([ruta]);
  }

  cerrarSesion(): void {
    this.authService.cerrarSesion();
    this.router.navigate(['/login']);
  }

  getModulos(): string[] {
    return [...new Set(this.registros.map(item => item.modulo))];
  }

  contarPorEstado(estado: 'EXITOSO' | 'ADVERTENCIA' | 'ERROR'): number {
    return this.registros.filter(item => item.estado === estado).length;
  }

  getClaseEstado(estado: string): string {
    if (estado === 'EXITOSO') {
      return 'bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-400 dark:border-green-900';
    }

    if (estado === 'ADVERTENCIA') {
      return 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-400 dark:border-yellow-900';
    }

    return 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-400 dark:border-red-900';
  }

  getClaseAccion(estado: string): string {
    if (estado === 'EXITOSO') {
      return 'text-green-700 dark:text-green-400';
    }

    if (estado === 'ADVERTENCIA') {
      return 'text-yellow-700 dark:text-yellow-400';
    }

    return 'text-red-700 dark:text-red-400';
  }

  trackByRegistro(index: number, item: RegistroBitacora): number {
    return item.id;
  }
}