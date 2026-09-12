import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PrendaCatalogo } from '../../../../services/catalogo-publico';

@Component({
  selector: 'app-producto-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './producto-card.html'
})
export class ProductoCardComponent {
  @Input({ required: true }) prenda!: PrendaCatalogo;
  @Output() clickPrenda = new EventEmitter<number>();

  fallbackImg = 'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80';

  onErrorImagen(event: Event): void {
    const target = event.target as HTMLImageElement;
    if (target && target.src !== this.fallbackImg) {
      target.src = this.fallbackImg;
    }
  }

  onCardClick(): void {
    if (this.prenda?.id_producto) {
      this.clickPrenda.emit(this.prenda.id_producto);
    }
  }
}
