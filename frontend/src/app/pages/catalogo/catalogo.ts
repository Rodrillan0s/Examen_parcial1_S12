import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth';
import { ProductDetailModalComponent, ProductoFashion } from '../../components/product-detail-modal/product-detail-modal';

@Component({
  selector: 'app-catalogo',
  standalone: true,
  imports: [CommonModule, FormsModule, ProductDetailModalComponent],
  templateUrl: './catalogo.html'
})
export class CatalogoComponent {
  public authService = inject(AuthService);

  searchQuery = '';
  selectedCategory = 'Todos';
  selectedBranchFilter = 'Todas';
  selectedSort = 'destacados';
  selectedProductForModal: ProductoFashion | null = null;

  categorias = ['Todos', 'Otoño 2026', 'Sastrería', 'Alta Costura', 'Esenciales', 'Accesorios'];
  sucursales = ['Todas', 'Sucursal Central Equipetrol', 'Sucursal Calacoto Luxury', 'Sucursal Cochabamba Jardin'];

  // Catálogo completo de prendas
  todosProductos: ProductoFashion[] = [
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
        { nombre: 'Negro Azabache', hex: '#18181b' }
      ],
      descripcion: 'Confeccionado artesanalmente con 100% fibra de alpaca fina. Corte holgado arquitectónico con solapas cruzadas.',
      especificaciones: ['100% Fibra de Alpaca', 'Hecho en Bolivia'],
      sucursalesDisponibles: ['Sucursal Central Equipetrol', 'Sucursal Calacoto Luxury'],
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
      imagenes: ['https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80'],
      tallas: ['XS', 'S', 'M', 'L'],
      colores: [
        { nombre: 'Verde Botella', hex: '#1b382b' },
        { nombre: 'Monocromo Negro', hex: '#09090b' }
      ],
      descripcion: 'Silueta limpia y rígida que estiliza la figura con hombreras estructuradas.',
      especificaciones: ['Tejido Neopreno Premium', 'Construcción Rígida'],
      sucursalesDisponibles: ['Sucursal Central Equipetrol', 'Sucursal Cochabamba Jardin'],
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
      imagenes: ['https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80'],
      tallas: ['S', 'M', 'L'],
      colores: [
        { nombre: 'Marfil Perla', hex: '#fdfbf7' },
        { nombre: 'Rosa Champán', hex: '#e8c5b0' }
      ],
      descripcion: 'Caída fluida de seda natural importada con espalda escotada y pliegues hechos a mano.',
      especificaciones: ['Seda Natural 100%', 'Costuras Invisibles'],
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
      imagenes: ['https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80'],
      tallas: ['S', 'M', 'L', 'XL'],
      colores: [
        { nombre: 'Blanco Lino', hex: '#ffffff' },
        { nombre: 'Azul Celeste', hex: '#93c5fd' }
      ],
      descripcion: 'Lino de origen sostenible transpirable con lavado suavizado de piedra.',
      especificaciones: ['100% Lino Orgánico', 'Lavado a Piedra'],
      sucursalesDisponibles: ['Sucursal Central Equipetrol', 'Sucursal Calacoto Luxury', 'Sucursal Cochabamba Jardin'],
      etiqueta: 'Tendencia',
      popularidad: 91
    },
    {
      id: 105,
      nombre: 'Trench Coat Impermeable Obsidian',
      subtitulo: 'Prenda de Abrigo de Alto Rendimiento & Estilo Urbano',
      precio: 1650,
      categoria: 'Otoño 2026',
      imagenPrincipal: 'https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=800&q=80',
      imagenes: ['https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=800&q=80'],
      tallas: ['M', 'L', 'XL'],
      colores: [
        { nombre: 'Negro Azabache', hex: '#09090b' },
        { nombre: 'Azul Marino', hex: '#1e3a8a' }
      ],
      descripcion: 'Diseño clásico militar reinterpretado con membrana hidrófuga y cinturón con hebilla de titanio.',
      especificaciones: ['Membrana Hidrófuga', 'Cinturón Ajustable'],
      sucursalesDisponibles: ['Sucursal Central Equipetrol', 'Sucursal Calacoto Luxury'],
      etiqueta: 'Novedad',
      popularidad: 94
    },
    {
      id: 106,
      nombre: 'Bolso Tote de Cuero Vacuno Encerado',
      subtitulo: 'Marroquinería Artesanal de Lujo',
      precio: 780,
      precioAnterior: 920,
      categoria: 'Accesorios',
      imagenPrincipal: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=800&q=80',
      imagenes: ['https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=800&q=80'],
      tallas: ['Única'],
      colores: [
        { nombre: 'Cognac Roble', hex: '#7c2d12' },
        { nombre: 'Negro Carbón', hex: '#18181b' }
      ],
      descripcion: 'Cuero genuino curtido vegetal con compartimento acolchado para laptop e interiores de terciopelo.',
      especificaciones: ['100% Cuero Vacuno', 'Herrajes de Latón'],
      sucursalesDisponibles: ['Sucursal Central Equipetrol', 'Sucursal Cochabamba Jardin'],
      etiqueta: 'Artesanal',
      popularidad: 97
    }
  ];

  get productosFiltrados(): ProductoFashion[] {
    return this.todosProductos
      .filter(p => {
        const matchesCategory = this.selectedCategory === 'Todos' || p.categoria === this.selectedCategory;
        const matchesBranch = this.selectedBranchFilter === 'Todas' || p.sucursalesDisponibles.includes(this.selectedBranchFilter);
        const matchesSearch = !this.searchQuery || 
          p.nombre.toLowerCase().includes(this.searchQuery.toLowerCase()) || 
          p.subtitulo.toLowerCase().includes(this.searchQuery.toLowerCase());
        return matchesCategory && matchesBranch && matchesSearch;
      })
      .sort((a, b) => {
        if (this.selectedSort === 'precio-menor') return a.precio - b.precio;
        if (this.selectedSort === 'precio-mayor') return b.precio - a.precio;
        return (b.popularidad || 0) - (a.popularidad || 0);
      });
  }

  openQuickView(prod: ProductoFashion) {
    this.selectedProductForModal = prod;
  }

  closeQuickView() {
    this.selectedProductForModal = null;
  }
}
