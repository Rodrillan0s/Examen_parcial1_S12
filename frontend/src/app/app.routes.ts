import { Routes } from '@angular/router';

//COMPONENTES
import { LoginComponent } from './pages/login/login';
import { ListaUsuariosComponent } from './pages/usuarios/lista-usuarios/lista-usuarios';
import { HomeComponent } from './pages/home/home';
import { PerfilComponent } from './pages/perfil/perfil';
import { RolesComponent } from './pages/roles/roles';
import { ListaEmpresasComponent } from './pages/empresas/lista-empresas/lista-empresas';
import { BackupComponent } from './pages/backup/backup';
import { TalleresComponent } from './pages/talleres/talleres';
import { MapaTalleresComponent } from './pages/mapa-talleres/mapa-talleres';
import { ServiciosTallerComponent } from './pages/servicios-taller/servicios-taller';
import { EmergenciasActualesComponent } from './pages/emergencias-actuales/emergencias-actuales';
import { EmergenciasHistorialComponent } from './pages/emergencias-historial/emergencias-historial';
import { NotificacionesComponent } from './pages/notificaciones/notificaciones';
import { DashboardKpisComponent } from './pages/dashboard-kpis/dashboard-kpis';
import { TrackingComponent } from './pages/tracking/tracking';
import { TriajeChatComponent } from './pages/triaje-chat/triaje-chat';
import { BiDashboardComponent } from './pages/bi-dashboard/bi-dashboard';
import { MantenimientoCrmComponent } from './pages/mantenimiento-crm/mantenimiento-crm';
import { DineroRetenidoComponent } from './pages/dinero-retenido/dinero-retenido';

//LAYOUTS
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout';

//GUARDS
import { publicGuard } from './guards/public-guard';
import { authGuard } from './guards/auth-guard';
import { BitacoraComponent } from './pages/bitacora/bitacora';




export const routes: Routes = [
    //RUTAS PUBLICAS
    { path: '', redirectTo: 'login', pathMatch: 'full' },
    { path: 'login', component: LoginComponent, canActivate: [publicGuard] },

    //RUTAS SIN SIDEBAR
    { path: 'home', component: HomeComponent, canActivate: [authGuard] },
    { path: 'perfil', component: PerfilComponent, canActivate: [authGuard] },

    //RUTAS CONSIDEBAR
    {
        path: '',
        component: AdminLayoutComponent,
        canActivate: [authGuard],
        children: [
            { path: 'usuarios', component: ListaUsuariosComponent },
            { path: 'roles', component: RolesComponent },
            { path: 'empresas', component: ListaEmpresasComponent },
            { path:'backup',component:BackupComponent },
            { path:'talleres', component: TalleresComponent },
            { path:'mapa-talleres', component: MapaTalleresComponent },
            { path:'talleres/:id/servicios', component:ServiciosTallerComponent },
            { path:'emergencias-actuales',component: EmergenciasActualesComponent },
            { path:'emergencias-historial', component:EmergenciasHistorialComponent },
            { path:'tracking', component:TrackingComponent },
            { path:'notificaciones', component:NotificacionesComponent },
            { path:'kpis', component:DashboardKpisComponent },
            { path:'bitacora', component:BitacoraComponent },
            { path:'triaje-chat', component:TriajeChatComponent },
            { path:'bi_dashboard', component:BiDashboardComponent },
            { path:'mantenimiento',component:MantenimientoCrmComponent },
            { path:'dinero-retenido',component:DineroRetenidoComponent }
        ]
    },
    { path: '**', redirectTo: 'login' }
];