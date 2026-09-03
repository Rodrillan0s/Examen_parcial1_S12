import { Injectable, inject, PLATFORM_ID, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { environment } from '../../environments/environment';

export interface Usuario {
  id_usuario?: number;
  nro_usuario?: number;
  correo: string;
  nombre_usuario: string;
  nombre: string;
  apellido: string;
  telefono?: string;
  id_rol?: number;
  nombre_rol?: string;
  id_empresa?: number;
  nombre_empresa?: string;
  roles?: string[];
  permisos?: string[];
  sucursales?: number[];
}

export type AuthTab = 'login' | 'register' | 'forgot' | 'verify';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl || 'http://127.0.0.1:5000';
  private platformId = inject(PLATFORM_ID);

  // Signals para reactividad en Angular 17/18
  currentUser = signal<Usuario | null>(this.obtenerUsuarioInicial());
  permissions = signal<string[]>(this.obtenerPermisosIniciales());
  roles = signal<string[]>(this.obtenerRolesIniciales());
  branches = signal<number[]>(this.obtenerSucursalesIniciales());
  
  isAuthModalOpen = signal<boolean>(false);
  authModalTab = signal<AuthTab>('login');
  
  // Estado de verificación de dispositivo pendiente
  pendingDeviceVerification = signal<{
    nro_usuario: number;
    codigo_simulado?: string;
    device_fingerprint?: string;
    nombre_dispositivo?: string;
  } | null>(null);

  // Sucursal seleccionada (Multi-tenant)
  activeBranch = signal<{ id: number; nombre: string; ciudad: string }>({
    id: 1,
    nombre: 'Sucursal Central Equipetrol',
    ciudad: 'Santa Cruz'
  });

  public branchList = [
    { id: 1, nombre: 'Sucursal Central Equipetrol', ciudad: 'Santa Cruz' },
    { id: 2, nombre: 'Sucursal Calacoto Luxury', ciudad: 'La Paz' },
    { id: 3, nombre: 'Sucursal Cochabamba Jardin', ciudad: 'Cochabamba' }
  ];

  private obtenerUsuarioInicial(): Usuario | null {
    if (isPlatformBrowser(this.platformId)) {
      const u = localStorage.getItem('usuario');
      return u ? JSON.parse(u) : null;
    }
    return null;
  }

  private obtenerPermisosIniciales(): string[] {
    const u = this.obtenerUsuarioInicial();
    if (u && Array.isArray(u.permisos)) return u.permisos;
    return this.extraerPermisosDeToken();
  }

  private obtenerRolesIniciales(): string[] {
    const u = this.obtenerUsuarioInicial();
    if (u && Array.isArray(u.roles)) return u.roles;
    return [];
  }

  private obtenerSucursalesIniciales(): number[] {
    const u = this.obtenerUsuarioInicial();
    if (u && Array.isArray(u.sucursales)) return u.sucursales;
    return [1];
  }

  private extraerPermisosDeToken(): string[] {
    const token = this.obtenerToken();
    if (!token) return [];
    try {
      const payloadBase64 = token.split('.')[1];
      const payloadDecodificado = JSON.parse(atob(payloadBase64));
      return payloadDecodificado.permisos || [];
    } catch {
      return [];
    }
  }

  // --- MÉTODOS DE AUTORIZACIÓN BASADOS EN PERMISOS ---

  hasPermission(codigo: string): boolean {
    if (!codigo) return true;
    const perms = this.permissions();
    return perms.includes(codigo);
  }

  hasAnyPermission(codigos: string[]): boolean {
    if (!codigos || codigos.length === 0) return true;
    const perms = this.permissions();
    return codigos.some(c => perms.includes(c));
  }

  hasAllPermissions(codigos: string[]): boolean {
    if (!codigos || codigos.length === 0) return true;
    const perms = this.permissions();
    return codigos.every(c => perms.includes(c));
  }

  // --- MÉTODOS DE AUTENTICACIÓN QUE LLAMAN AL BACKEND ---

  registrarCliente(datos: any) {
    return this.http.post<any>(`${this.apiUrl}/api/auth/register`, datos);
  }

  iniciarSesion(credenciales: any) {
    return this.http.post<any>(`${this.apiUrl}/api/auth/login`, credenciales);
  }

  verificarDispositivo(datos: any) {
    return this.http.post<any>(`${this.apiUrl}/api/auth/verify-device`, datos);
  }

  solicitarRecuperacionClave(correo: string) {
    return this.http.post<any>(`${this.apiUrl}/api/auth/forgot-password`, { correo });
  }

  verificarCodigoRecuperacion(correo: string, codigo_recuperacion: string) {
    return this.http.post<any>(`${this.apiUrl}/api/auth/verify-recovery-code`, { correo, codigo_recuperacion });
  }

  restablecerClave(datos: any) {
    return this.http.post<any>(`${this.apiUrl}/api/auth/reset-password`, datos);
  }

  // --- MANEJO DE SESIÓN LOCAL ---

  guardarSesion(token: string, usuario: Usuario) {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('token', token);
      localStorage.setItem('usuario', JSON.stringify(usuario));
    }
    this.currentUser.set(usuario);
    this.permissions.set(usuario.permisos || []);
    this.roles.set(usuario.roles || []);
    this.branches.set(usuario.sucursales || []);
    this.closeAuthModal();
  }

  cerrarSesion() {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('token');
      localStorage.removeItem('usuario');
    }
    this.currentUser.set(null);
    this.permissions.set([]);
    this.roles.set([]);
    this.branches.set([]);
    
    // Force a full reload to clear any remaining in-memory state in the SPA
    if (isPlatformBrowser(this.platformId)) {
      window.location.href = '/';
    }
  }

  obtenerToken(): string | null {
    if (isPlatformBrowser(this.platformId)) {
      return localStorage.getItem('token');
    }
    return null;
  }

  obtenerUsuario(): Usuario | null {
    if (this.currentUser()) {
      return this.currentUser();
    }
    if (isPlatformBrowser(this.platformId)) {
      const u = localStorage.getItem('usuario');
      return u ? JSON.parse(u) : null;
    }
    return null;
  }

  estaAutenticado(): boolean {
    return !!this.currentUser() && !this.tokenExpirado();
  }

  tokenExpirado(): boolean {
    const token = this.obtenerToken();
    if (!token) return true;
    try {
      const payloadBase64 = token.split('.')[1];
      const payloadDecodificado = JSON.parse(atob(payloadBase64));
      return Date.now() >= payloadDecodificado.exp * 1000;
    } catch {
      return true;
    }
  }

  esEmpleadoOAdmin(): boolean {
    const user = this.obtenerUsuario();
    if (!user) return false;
    const rol = (user.nombre_rol || '').toUpperCase();
    if (rol === 'ADMINISTRADOR' || user.id_rol === 1) return true;
    if (this.hasPermission('admin.acceder')) return true;
    return user.id_rol !== 2;
  }

  obtenerNombreRol(): string {
    const user = this.obtenerUsuario();
    if (!user) return 'INVITADO';
    if (user.nombre_rol) return user.nombre_rol;
    return user.id_rol === 2 ? 'CLIENTE' : 'PERSONAL';
  }

  // --- MÉTODOS DE DETECCIÓN DE NIVEL DE ACCESO Y ALCANCE (SCOPE) ---

  getScopeLevel(): 'PLATAFORMA' | 'EMPRESA' | 'SUCURSAL' {
    const user = this.obtenerUsuario();
    if (!user) return 'PLATAFORMA';
    
    const rol = (user.nombre_rol || '').toUpperCase();
    const rolesList = (user.roles || []).map(r => r.toUpperCase());

    if (rol === 'ADMINISTRADOR' || user.id_rol === 1 || rolesList.includes('ADMINISTRADOR')) {
      return 'PLATAFORMA';
    }
    if (rol === 'ADMINISTRADOR_TIENDA' || rolesList.includes('ADMINISTRADOR_TIENDA')) {
      return 'EMPRESA';
    }
    if (rol === 'ENCARGADO_SUCURSAL' || rol === 'CAJERO' || rolesList.includes('ENCARGADO_SUCURSAL') || rolesList.includes('CAJERO')) {
      return 'SUCURSAL';
    }
    return user.id_empresa ? 'EMPRESA' : 'PLATAFORMA';
  }

  isGlobalAdmin(): boolean {
    return this.getScopeLevel() === 'PLATAFORMA';
  }

  isStoreAdmin(): boolean {
    return this.getScopeLevel() === 'EMPRESA';
  }

  isBranchManager(): boolean {
    return this.getScopeLevel() === 'SUCURSAL';
  }

  getUserCompanyName(): string {
    const user = this.obtenerUsuario();
    if (user && user.nombre_empresa && user.nombre_empresa.trim().length > 0) {
      return user.nombre_empresa;
    }
    return 'AURA Atelier';
  }

  getUserBranchName(): string {
    const active = this.activeBranch();
    if (active && active.nombre) return active.nombre;
    return 'Sucursal Central Equipetrol';
  }

  getUserScopeContext() {
    const scope = this.getScopeLevel();
    const empresa = this.getUserCompanyName();
    const sucursal = this.getUserBranchName();

    if (scope === 'PLATAFORMA') {
      return {
        scope,
        headerTitle: 'AURA · Administración de plataforma',
        sidebarTitle: 'AURA',
        sidebarSubtitle: 'Administración de plataforma',
        badgeText: 'GLOBAL PLATFORM',
        badgeClass: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
      };
    } else if (scope === 'EMPRESA') {
      return {
        scope,
        headerTitle: `AURA · ${empresa}`,
        sidebarTitle: empresa,
        sidebarSubtitle: 'Gestión de Empresa',
        badgeText: 'MI EMPRESA',
        badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
      };
    } else {
      return {
        scope,
        headerTitle: `AURA · ${empresa} · ${sucursal}`,
        sidebarTitle: sucursal,
        sidebarSubtitle: `Sucursal · ${empresa}`,
        badgeText: 'MI SUCURSAL',
        badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/20'
      };
    }
  }


  // --- CONTROL DEL MODAL DE AUTENTICACIÓN INTEGRAD0 ---

  openAuthModal(tab: AuthTab = 'login') {
    this.authModalTab.set(tab);
    this.isAuthModalOpen.set(true);
  }

  closeAuthModal() {
    this.isAuthModalOpen.set(false);
  }

  setBranch(branch: { id: number; nombre: string; ciudad: string }) {
    this.activeBranch.set(branch);
  }
}
