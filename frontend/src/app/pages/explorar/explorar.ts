import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';
import { ProductDetailModalComponent, ProductoFashion } from '../../components/product-detail-modal/product-detail-modal';

@Component({
  selector: 'app-explorar',
  standalone: true,
  imports: [CommonModule, RouterLink, ProductDetailModalComponent],
  templateUrl: './explorar.html'
})
export class ExplorarComponent {
  public authService = inject(AuthService);

  selectedProductForModal: ProductoFashion | null = null;

  // Productos de demostración de alta gama para la ropa
  productosDestacados: ProductoFashion[] = [
    {
      id: 101,
      nombre: 'Abrigo Oversized Alpaca Pure',
      subtitulo: 'Sastrería de Lana de Alpaca Boliviana & Fibras de Lujo',
      precio: 1450,
      precioAnterior: 1800,
      categoria: 'Otoño 2026',
      imagenPrincipal: 'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80',
      imagenes: [
        'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80'
      ],
      tallas: ['S', 'M', 'L', 'XL'],
      colores: [
        { nombre: 'Camel Atacama', hex: '#c19a6b' },
        { nombre: 'Negro Azabache', hex: '#18181b' },
        { nombre: 'Gris Marfil', hex: '#71717a' }
      ],
      descripcion: 'Confeccionado artesanalmente con 100% fibra de alpaca fina. Corte holgado arquitectónico con solapas cruzadas y forro térmico de seda.',
      especificaciones: ['100% Fibra de Alpaca', 'Hecho en Bolivia', 'Limpieza en Seco'],
      sucursalesDisponibles: ['Sucursal Central Equipetrol', 'Sucursal Calacoto'],
      etiqueta: 'Edición Limitada',
      popularidad: 98
    },
    {
      id: 102,
      nombre: 'Blazer Neopreno Estructurado',
      subtitulo: 'Línea de Sastrería Urbana Minimalista',
      precio: 890,
      precioAnterior: 1100,
      categoria: 'Sastrería',
      imagenPrincipal: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
      imagenes: [
        'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80'
      ],
      tallas: ['XS', 'S', 'M', 'L'],
      colores: [
        { nombre: 'Verde Botella', hex: '#1b382b' },
        { nombre: 'Monocromo Negro', hex: '#09090b' }
      ],
      descripcion: 'Silueta limpia y rígida que estiliza la figura. Tecnología antipliegues con hombreras estructuradas y botones invisibles de imán.',
      especificaciones: ['Tejido Neopreno Premium', 'Construcción Rígida', 'Bolsillos Ocultos'],
      sucursalesDisponibles: ['Sucursal Central Equipetrol', 'Sucursal Cochabamba'],
      etiqueta: 'Más Vendido',
      popularidad: 95
    },
    {
      id: 103,
      nombre: 'Vestido de Seda Italiana Marfil',
      subtitulo: 'Colección Ceremonia & Alta Costura',
      precio: 2100,
      categoria: 'Alta Costura',
      imagenPrincipal: 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80',
      imagenes: [
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80'
      ],
      tallas: ['S', 'M', 'L'],
      colores: [
        { nombre: 'Marfil Perla', hex: '#fdfbf7' },
        { nombre: 'Rosa Champán', hex: '#e8c5b0' }
      ],
      descripcion: 'Caída fluida de seda natural importada con espalda escotada y pliegues hechos a mano. Diseño exclusivo de nuestro atelier principal.',
      especificaciones: ['Seda Natural 100%', 'Costuras Invisibles', 'Incluye Funda de Protección'],
      sucursalesDisponibles: ['Sucursal Calacoto Luxury'],
      etiqueta: 'Exclusivo Atelier',
      popularidad: 99
    },
    {
      id: 104,
      nombre: 'Camisa Oxford de Lino Orgánico',
      subtitulo: 'Esenciales de Verano & Resort Wear',
      precio: 450,
      precioAnterior: 550,
      categoria: 'Esenciales',
      imagenPrincipal: 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80',
      imagenes: [
        'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80'
      ],
      tallas: ['S', 'M', 'L', 'XL', 'XXL'],
      colores: [
        { nombre: 'Blanco Lino', hex: '#ffffff' },
        { nombre: 'Azul Celeste', hex: '#93c5fd' },
        { nombre: 'Arena Warm', hex: '#d1d5db' }
      ],
      descripcion: 'Lino de origen sostenible transpirable con lavado suavizado de piedra. Cuello italiano sutil y botones de nácar genuino.',
      especificaciones: ['100% Lino Orgánico', 'Lavado a Piedra', 'Tacto Ultra Suave'],
      sucursalesDisponibles: ['Sucursal Central Equipetrol', 'Sucursal Calacoto', 'Sucursal Cochabamba'],
      etiqueta: 'Tendencia',
      popularidad: 91
    }
  ];

  openQuickView(prod: ProductoFashion) {
    this.selectedProductForModal = prod;
  }

  closeQuickView() {
    this.selectedProductForModal = null;
  }

  openAuth(tab: 'login' | 'register' = 'login') {
    this.authService.openAuthModal(tab);
  }
}
