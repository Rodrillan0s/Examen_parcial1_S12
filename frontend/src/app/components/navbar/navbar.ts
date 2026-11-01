import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService, AuthTab } from '../../services/auth';
import { ThemeService } from '../../services/theme';
import { CarritoService } from '../../services/carrito';
import { FavoritosService, PrendaFavorita } from '../../services/favoritos';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, RouterLinkActive],
  templateUrl: './navbar.html'
})
export class NavbarComponent implements OnInit {
  public authService      = inject(AuthService);
  public themeService     = inject(ThemeService);
  public carritoService   = inject(CarritoService);
  public favoritosService = inject(FavoritosService);
  private router          = inject(Router);

  isMobileMenuOpen = false;
  isBranchDropdownOpen = false;
  busquedaTexto: string = '';

  ngOnInit(): void {
    if (this.authService.estaAutenticado()) {
      this.carritoService.cargarCarrito().subscribe();
    }
  }

  get totalFavoritos(): number {
    return this.favoritosService ? this.favoritosService.totalFavoritos() : 0;
  }

  get mostrarModalFavoritos(): boolean {
    return this.favoritosService ? this.favoritosService.mostrarModalFavoritos() : false;
  }

  get listaFavoritos(): PrendaFavorita[] {
    return this.favoritosService ? this.favoritosService.favoritos() : [];
  }

  vaciarFavoritos(): void {
    this.favoritosService?.limpiarTodos();
  }

  abrirCarrito(): void {
    this.carritoService.abrirDrawer();
  }

  abrirFavoritos(): void {
    this.favoritosService?.abrirModal();
  }

  cerrarFavoritos(): void {
    this.favoritosService?.cerrarModal();
  }

  verPrendaFavorita(fav: PrendaFavorita): void {
    this.favoritosService?.cerrarModal();
    this.router.navigate(['/catalogo'], { queryParams: { producto: fav.id_producto } });
  }

  quitarFavorito(id: number, event: Event): void {
    event.stopPropagation();
    this.favoritosService?.eliminarFavorito(id);
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

  buscarEnCatalogo(): void {
    const q = this.busquedaTexto.trim();
    if (q) {
      this.router.navigate(['/catalogo'], { queryParams: { q } });
    } else {
      this.router.navigate(['/catalogo']);
    }
  }
}
