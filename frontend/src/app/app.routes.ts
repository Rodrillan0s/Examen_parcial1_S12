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
import { ListaInventarioComponent } from './pages/inventario/lista-inventario/lista-inventario';
import { PagoComponent } from './pages/pago/pago';
import { CajaComponent } from './pages/caja/caja';
import { CajaPagoComponent } from './pages/caja/pago/caja-pago';
import { CajaComprobanteComponent } from './pages/caja/comprobante/caja-comprobante';
import { ReportesComponent } from './pages/reportes/reportes';
import { authGuard } from './guards/auth-guard';
import { ProveedoresComponent } from './pages/proveedores/proveedores';

import { permissionGuard } from './guards/permission-guard';
import { scopeGuard } from './guards/scope-guard';

export const routes: Routes = [
  // RUTAS PÚBLICAS Y DE CLIENTE DE LA TIENDA E-COMMERCE DE ROPA
  { path: '', component: ExplorarComponent },
  { path: 'catalogo', component: CatalogoComponent },
  { path: 'catalogo/:id', component: CatalogoComponent },
  { path: 'login', component: ExplorarComponent },
  { path: 'perfil', component: PerfilComponent, canActivate: [authGuard] },
  { path: 'checkout', component: CheckoutComponent, canActivate: [authGuard] },
  { path: 'pedido-confirmado/:id', component: PedidoConfirmadoComponent, canActivate: [authGuard] },
  { path: 'pago/:id', component: PagoComponent, canActivate: [authGuard] },
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
  { path: 'inventario', redirectTo: 'admin/inventario', pathMatch: 'full' },
  { path: 'caja', redirectTo: 'admin/caja', pathMatch: 'full' },
  { path: 'pos', redirectTo: 'admin/caja', pathMatch: 'full' },
  { path: 'caja/pago/:id', redirectTo: 'admin/caja/pago/:id', pathMatch: 'full' },
  { path: 'caja/comprobante/:id', redirectTo: 'admin/caja/comprobante/:id', pathMatch: 'full' },
  { path: 'bitacora', redirectTo: 'admin/bitacora', pathMatch: 'full' },
  { path: 'backup', redirectTo: 'admin/backup', pathMatch: 'full' },
  { path: 'reportes', redirectTo: 'admin/reportes', pathMatch: 'full' },
  { path: 'bi-dashboard', redirectTo: 'admin/bi_dashboard', pathMatch: 'full' },
  { path: 'bi_dashboard', redirectTo: 'admin/bi_dashboard', pathMatch: 'full' },
  { path: 'triaje-chat', redirectTo: 'admin/triaje-chat', pathMatch: 'full' },
  { path: 'proveedores', redirectTo: 'admin/proveedores', pathMatch: 'full' },

  // RUTAS DE ADMINISTRACIÓN INTERNA (REQUIEREN AUTENTICACIÓN, PERMISOS RBAC Y CONTROL DE ALCANCE)
  {
    path: 'admin',
    component: AdminLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'kpis', pathMatch: 'full' },
      { path: 'kpis', component: DashboardKpisComponent, canActivate: [permissionGuard(['reportes.ver', 'admin.acceder'])] },
      { path: 'reportes', component: ReportesComponent, canActivate: [permissionGuard('reportes.ver')] },
      { path: 'usuarios', component: ListaUsuariosComponent, canActivate: [permissionGuard('usuarios.ver')] },
      { 
        path: 'empresas', 
        component: ListaEmpresasComponent, 
        canActivate: [scopeGuard(['PLATAFORMA']), permissionGuard('empresas.ver')] 
      },
      { path: 'sucursales', component: ListaSucursalesComponent, canActivate: [permissionGuard('sucursales.ver')] },
      { path: 'categorias', component: ListaCategoriasComponent, canActivate: [permissionGuard(['categorias.ver', 'productos.ver'])] },
      { path: 'tallas-colores', component: TallasColoresComponent, canActivate: [permissionGuard(['tallas.ver', 'productos.ver'])] },
      { path: 'productos', component: ProductosComponent, canActivate: [permissionGuard('productos.ver')] },
      { path: 'inventario', component: ListaInventarioComponent, canActivate: [permissionGuard('inventario.ver')] },
      { path: 'caja', component: CajaComponent, canActivate: [permissionGuard(['ventas.crear', 'ventas.ver', 'admin.acceder'])] },
      { path: 'caja/pago/:id', component: CajaPagoComponent, canActivate: [permissionGuard(['ventas.crear', 'admin.acceder'])] },
      { path: 'caja/comprobante/:id', component: CajaComprobanteComponent, canActivate: [permissionGuard(['ventas.crear', 'ventas.ver', 'admin.acceder'])] },
      { path: 'bitacora', component: ListaBitacoraComponent, canActivate: [permissionGuard('bitacora.ver')] },
      { 
        path: 'backup', 
        component: BackupComponent, 
        canActivate: [scopeGuard(['PLATAFORMA'])] 
      },
      { path: 'bi_dashboard', component: BiDashboardComponent, canActivate: [permissionGuard('reportes.ver')] },
      { path: 'bi-dashboard', component: BiDashboardComponent, canActivate: [permissionGuard('reportes.ver')] },
      { path: 'triaje-chat', component: TriajeChatComponent, canActivate: [permissionGuard('admin.acceder')] },
      { path: 'catalogo', component: CatalogoComponent, canActivate: [permissionGuard('productos.ver')] },
      { path: 'proveedores', component: ProveedoresComponent, canActivate: [permissionGuard('compras.ver')] }
    ]
  },

  { path: '**', redirectTo: '' }
];