import { Component, OnInit, inject,PLATFORM_ID } from '@angular/core';
import { CommonModule,isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.html'
})
export class HomeComponent implements OnInit {
  
  private authService = inject(AuthService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);

  usuarioActual: any = null;
  modoOscuro: boolean = false;
  modulosFiltrados: any[] = [];

  //LISTA DE MODULOS VISIBLES EN EL SISTEMA
  modulos = [
    {
      titulo: 'Seguridad y Usuarios',
      descripcion: 'Gestión de roles, personal administrativo y accesos al sistema.',
      icono: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
      ruta: '/usuarios',
      rolesPermitidos: ['ADMINISTRADOR'] //ADMINISTRADOR
    },
    {
      titulo: 'Red de Talleres',
      descripcion: 'Geolocalización, disponibilidad y asignación de talleres físicos.',
      icono: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
      ruta: '/talleres',
      rolesPermitidos: ['ADMINISTRADOR','GERENTE TALLER'] //ADMINISTRADOR Y DUEÑO DE TALLER
    },
    {
      titulo: 'Centro de Emergencias',
      descripcion: 'Monitor en tiempo real de solicitudes de auxilio e incidentes.',
      icono: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
      ruta: '/emergencias-actuales',
      rolesPermitidos: ['ADMINISTRADOR','GERENTE TALLER', 'MECANICO'] //ADMIN,DUEÑO Y MECANICO
    },
    {
      titulo: 'Tarifas y Cobros',
      descripcion: 'Gestión de precios base, órdenes de cobro y registros de pago.',
      icono: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      ruta: '/tarifas',
      rolesPermitidos: ['ADMINISTRADOR','GERENTE TALLER'] //ADMINISTRADOR Y DUEÑO
    },
    {
      titulo: 'Dinero Retenido',
      descripcion: 'Consulta y simulación de fondos retenidos por emergencia.',
      icono: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      ruta: '/dinero-retenido',
      rolesPermitidos: ['ADMINISTRADOR', 'CLIENTE']
    },
    {
      titulo: 'KPIs Operacionales',
      descripcion: 'Indicadores globales de emergencias, tiempos, SLA y eficiencia de talleres.',
      icono: 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z',
      ruta: '/kpis',
      rolesPermitidos: ['ADMINISTRADOR']
    },
    {
      titulo: 'Asistente ChatBot IA',
      descripcion: 'Triaje técnico automatizado para evaluación preliminar de fallas.',
      icono: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z',
      ruta: '/triaje-chat',
      rolesPermitidos: ['ADMINISTRADOR', 'GERENTE TALLER', 'MECANICO', 'CLIENTE'] //TODOS LOS ROLES
    }
  ];

  //METODO AL INICIAR LA PAGINA
  ngOnInit() {
    //VALIDAR QUE SE ESTE EJECUTANDO EN NAVEGADOR
    if (isPlatformBrowser(this.platformId)) {
      
      this.usuarioActual = this.authService.obtenerUsuario();
      
      // SI NO ESTA LOGUEADO LO REDIRIGE AL LOGIN
      if (!this.usuarioActual || this.authService.tokenExpirado()) 
        {
        this.cerrarSesion();
        return; 
      }

      // FILTRAMOS LA LISTA DE MODULOS SEGUN EL ROL DEL USUARIO
      const rolUsuario = this.usuarioActual.nombre_rol;
      this.modulosFiltrados = this.modulos.filter(modulo => modulo.rolesPermitidos.includes(rolUsuario));

      // VERIFICAR PREFERENCIA DE MODO OSCURO
      if (localStorage.getItem('tema_sistema') === 'dark') {
        this.modoOscuro = true;
        document.documentElement.classList.add('dark');
      }
    }
  }

  //METODO PARA ALTERNAR EL MODO OSCURO
  alternarModoOscuro() {
    this.modoOscuro = !this.modoOscuro;
    if (this.modoOscuro) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('tema_sistema', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('tema_sistema', 'light');
    }
  }

  //METODO PARA NAVEGAR A ALGUN MODULO
  navegarA(ruta: string) {
    this.router.navigate([ruta]);
  }

  //METODO PARA CERRAR SESION
  cerrarSesion() {
    this.authService.cerrarSesion();
    this.router.navigate(['/login']);
  }
}