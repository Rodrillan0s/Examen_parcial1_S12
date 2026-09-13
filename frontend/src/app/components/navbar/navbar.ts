import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService, AuthTab } from '../../services/auth';
import { ThemeService } from '../../services/theme';
import { CarritoService } from '../../services/carrito';
import { HasPermissionDirective } from '../../directives/has-permission.directive';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, HasPermissionDirective],
  templateUrl: './navbar.html'
})
export class NavbarComponent implements OnInit {
  public authService   = inject(AuthService);
  public themeService  = inject(ThemeService);
  public carritoService = inject(CarritoService);

  isMobileMenuOpen = false;
  isBranchDropdownOpen = false;

  ngOnInit(): void {
    if (this.authService.estaAutenticado()) {
      this.carritoService.cargarCarrito().subscribe();
    }
  }

  abrirCarrito(): void {
    this.carritoService.abrirDrawer();
  }

  toggleMobileMenu() {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  toggleBranchDropdown() {
    this.isBranchDropdownOpen = !this.isBranchDropdownOpen;
  }

  selectBranch(branch: { id: number; nombre: string; ciudad: string }) {
    this.authService.setBranch(branch);
    this.isBranchDropdownOpen = false;
  }

  openAuth(tab: AuthTab = 'login') {
    this.authService.openAuthModal(tab);
    this.isMobileMenuOpen = false;
  }

  cerrarSesion() {
    this.authService.cerrarSesion();
  }
}
