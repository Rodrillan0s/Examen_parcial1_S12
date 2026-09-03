import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth';

export interface ProductoFashion {
  id: number;
  nombre: string;
  subtitulo: string;
  precio: number;
  precioAnterior?: number;
  categoria: string;
  imagenPrincipal: string;
  imagenes: string[];
  tallas: string[];
  colores: { nombre: string; hex: string }[];
  descripcion: string;
  especificaciones: string[];
  sucursalesDisponibles: string[];
  etiqueta?: string;
  popularidad?: number;
}

@Component({
  selector: 'app-product-detail-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './product-detail-modal.html'
})
export class ProductDetailModalComponent {
  @Input() producto: ProductoFashion | null = null;
  @Output() close = new EventEmitter<void>();

  public authService = inject(AuthService);

  selectedImageIndex = 0;
  selectedSize = 'M';
  selectedColorIndex = 0;
  quantity = 1;
  addedToast = false;

  selectImage(idx: number) {
    this.selectedImageIndex = idx;
  }

  selectSize(size: string) {
    this.selectedSize = size;
  }

  selectColor(idx: number) {
    this.selectedColorIndex = idx;
  }

  incrementQuantity() {
    this.quantity++;
  }

  decrementQuantity() {
    if (this.quantity > 1) this.quantity--;
  }

  addToCart() {
    this.addedToast = true;
    setTimeout(() => {
      this.addedToast = false;
    }, 2500);
  }

  buyNow() {
    if (!this.authService.estaAutenticado()) {
      this.authService.openAuthModal('login');
    } else {
      this.addToCart();
    }
  }

  closeModal() {
    this.close.emit();
  }
}
