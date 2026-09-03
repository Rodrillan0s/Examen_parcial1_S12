import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService, AuthTab } from '../../services/auth';
import { HasPermissionDirective } from '../../directives/has-permission.directive';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, HasPermissionDirective],
  templateUrl: './navbar.html'
})
export class NavbarComponent {
  public authService = inject(AuthService);

  isMobileMenuOpen = false;
  isBranchDropdownOpen = false;

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
