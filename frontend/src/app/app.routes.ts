import { Routes } from '@angular/router';
import { ExplorarComponent } from './pages/explorar/explorar';
import { CatalogoComponent } from './pages/catalogo/catalogo';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout';
import { DashboardKpisComponent } from './pages/dashboard-kpis/dashboard-kpis';
import { ListaUsuariosComponent } from './pages/usuarios/lista-usuarios/lista-usuarios';
import { RolesComponent } from './pages/roles/roles';
import { ListaEmpresasComponent } from './pages/empresas/lista-empresas/lista-empresas';
import { ListaSucursalesComponent } from './pages/sucursales/lista-sucursales/lista-sucursales';
import { ListaBitacoraComponent } from './pages/bitacora/lista-bitacora/lista-bitacora';
import { BackupComponent } from './pages/backup/backup';
import { DineroRetenidoComponent } from './pages/dinero-retenido/dinero-retenido';
import { BiDashboardComponent } from './pages/bi-dashboard/bi-dashboard';
import { TriajeChatComponent } from './pages/triaje-chat/triaje-chat';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
  // RUTAS PÚBLICAS DE LA TIENDA E-COMMERCE DE ROPA
  { path: '', component: ExplorarComponent },
  { path: 'catalogo', component: CatalogoComponent },
  { path: 'login', component: ExplorarComponent },

  // RUTAS DE REDIRECCIÓN A NIVEL RAÍZ A /admin/* PARA EVITAR CAÍDAS A LA TIENDA PÚBLICA
  { path: 'kpis', redirectTo: 'admin/kpis', pathMatch: 'full' },
  { path: 'usuarios', redirectTo: 'admin/usuarios', pathMatch: 'full' },
  { path: 'roles', redirectTo: 'admin/roles', pathMatch: 'full' },
  { path: 'empresas', redirectTo: 'admin/empresas', pathMatch: 'full' },
  { path: 'bitacora', redirectTo: 'admin/bitacora', pathMatch: 'full' },
  { path: 'backup', redirectTo: 'admin/backup', pathMatch: 'full' },
  { path: 'dinero-retenido', redirectTo: 'admin/dinero-retenido', pathMatch: 'full' },
  { path: 'bi-dashboard', redirectTo: 'admin/bi_dashboard', pathMatch: 'full' },
  { path: 'bi_dashboard', redirectTo: 'admin/bi_dashboard', pathMatch: 'full' },
  { path: 'triaje-chat', redirectTo: 'admin/triaje-chat', pathMatch: 'full' },

  // RUTAS DE ADMINISTRACIÓN INTERNA (REQUIEREN AUTENTICACIÓN Y PERMISOS RBAC)
  {
    path: 'admin',
    component: AdminLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'kpis', pathMatch: 'full' },
      { path: 'kpis', component: DashboardKpisComponent },
      { path: 'usuarios', component: ListaUsuariosComponent },
      { path: 'roles', component: RolesComponent },
      { path: 'empresas', component: ListaEmpresasComponent },
      { path: 'sucursales', component: ListaSucursalesComponent },
      { path: 'bitacora', component: ListaBitacoraComponent },
      { path: 'backup', component: BackupComponent },
      { path: 'dinero-retenido', component: DineroRetenidoComponent },
      { path: 'bi_dashboard', component: BiDashboardComponent },
      { path: 'bi-dashboard', component: BiDashboardComponent },
      { path: 'triaje-chat', component: TriajeChatComponent },
      { path: 'catalogo', component: CatalogoComponent }
    ]
  },

  { path: '**', redirectTo: '' }
];