import { Routes } from '@angular/router';
import { ExplorarComponent } from './pages/explorar/explorar';
import { CatalogoComponent } from './pages/catalogo/catalogo';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout';
import { DashboardKpisComponent } from './pages/dashboard-kpis/dashboard-kpis';
import { ListaUsuariosComponent } from './pages/usuarios/lista-usuarios/lista-usuarios';
import { ListaEmpresasComponent } from './pages/empresas/lista-empresas/lista-empresas';
import { ListaSucursalesComponent } from './pages/sucursales/lista-sucursales/lista-sucursales';
import { ListaBitacoraComponent } from './pages/bitacora/lista-bitacora/lista-bitacora';
import { BackupComponent } from './pages/backup/backup';
import { BiDashboardComponent } from './pages/bi-dashboard/bi-dashboard';
import { TriajeChatComponent } from './pages/triaje-chat/triaje-chat';
import { PerfilComponent } from './pages/perfil/perfil';
import { ListaCategoriasComponent } from './pages/categorias/lista-categorias/lista-categorias';
import { TallasColoresComponent } from './pages/catalogo/tallas-colores/tallas-colores';
import { ProductosComponent } from './pages/catalogo/productos/productos';
import { CheckoutComponent } from './pages/checkout/checkout';
import { PedidoConfirmadoComponent } from './pages/pedido-confirmado/pedido-confirmado';
import { MisReservasComponent } from './pages/reservas/mis-reservas/mis-reservas';
import { MisPedidosComponent } from './pages/pedidos/mis-pedidos/mis-pedidos';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
  // RUTAS PÚBLICAS Y DE CLIENTE DE LA TIENDA E-COMMERCE DE ROPA
  { path: '', component: ExplorarComponent },
  { path: 'catalogo', component: CatalogoComponent },
  { path: 'catalogo/:id', component: CatalogoComponent },
  { path: 'login', component: ExplorarComponent },
  { path: 'perfil', component: PerfilComponent, canActivate: [authGuard] },
  { path: 'checkout', component: CheckoutComponent, canActivate: [authGuard] },
  { path: 'pedido-confirmado/:id', component: PedidoConfirmadoComponent, canActivate: [authGuard] },
  { path: 'mis-reservas', component: MisReservasComponent, canActivate: [authGuard] },
  { path: 'mis-pedidos', component: MisPedidosComponent, canActivate: [authGuard] },

  // RUTAS DE REDIRECCIÓN A NIVEL RAÍZ A /admin/* PARA EVITAR CAÍDAS A LA TIENDA PÚBLICA
  { path: 'kpis', redirectTo: 'admin/kpis', pathMatch: 'full' },
  { path: 'usuarios', redirectTo: 'admin/usuarios', pathMatch: 'full' },
  { path: 'roles', redirectTo: 'admin/usuarios', pathMatch: 'full' },
  { path: 'empresas', redirectTo: 'admin/empresas', pathMatch: 'full' },
  { path: 'sucursales', redirectTo: 'admin/sucursales', pathMatch: 'full' },
  { path: 'categorias', redirectTo: 'admin/categorias', pathMatch: 'full' },
  { path: 'tallas-colores', redirectTo: 'admin/tallas-colores', pathMatch: 'full' },
  { path: 'productos', redirectTo: 'admin/productos', pathMatch: 'full' },
  { path: 'bitacora', redirectTo: 'admin/bitacora', pathMatch: 'full' },
  { path: 'backup', redirectTo: 'admin/backup', pathMatch: 'full' },
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
      { path: 'empresas', component: ListaEmpresasComponent },
      { path: 'sucursales', component: ListaSucursalesComponent },
      { path: 'categorias', component: ListaCategoriasComponent },
      { path: 'tallas-colores', component: TallasColoresComponent },
      { path: 'productos', component: ProductosComponent },
      { path: 'bitacora', component: ListaBitacoraComponent },
      { path: 'backup', component: BackupComponent },
      { path: 'bi_dashboard', component: BiDashboardComponent },
      { path: 'bi-dashboard', component: BiDashboardComponent },
      { path: 'triaje-chat', component: TriajeChatComponent },
      { path: 'catalogo', component: CatalogoComponent }
    ]
  },

  { path: '**', redirectTo: '' }
];