import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';
import { FavoritosService } from '../../services/favoritos';
import { CatalogoPublicoService, DetallePrendaCatalogo } from '../../services/catalogo-publico';
import { ProductDetailModalComponent, ProductoFashion } from '../../components/product-detail-modal/product-detail-modal';
import { RecomendacionesService, RecomendacionML } from '../../services/recomendaciones.service';

export interface ProductoDestacadoItem extends ProductoFashion {
  rating?: number;
  reviews?: number;
}

@Component({
  selector: 'app-explorar',
  standalone: true,
  imports: [CommonModule, RouterLink, ProductDetailModalComponent],
  templateUrl: './explorar.html'
})
export class ExplorarComponent implements OnInit {
  public authService = inject(AuthService);
  private router = inject(Router);
  private catalogoService = inject(CatalogoPublicoService);
  private cdr = inject(ChangeDetectorRef);
  public favoritosService = inject(FavoritosService);
  private recomendacionesService = inject(RecomendacionesService);

  selectedProductForModal: DetallePrendaCatalogo | ProductoFashion | null = null;
  public recomendacionesML: RecomendacionML[] = [];

  // Historias circulares de categorías (8 avatares inspirados en la maqueta editorial)
  categoriasHistorias = [
    { nombre: 'Vestidos', imagen: 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=300&q=80' },
    { nombre: 'Blusas', imagen: 'https://images.unsplash.com/photo-1598554747436-c9293d6a588f?auto=format&fit=crop&w=300&q=80' },
    { nombre: 'Pantalones', imagen: 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=300&q=80' },
    { nombre: 'Chaquetas', imagen: 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=300&q=80' },
    { nombre: 'Faldas', imagen: 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=300&q=80' },
    { nombre: 'Accesorios', imagen: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=300&q=80' },
    { nombre: 'Calzado', imagen: 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=300&q=80' },
    { nombre: 'Nueva Colección', imagen: 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=300&q=80' }
  ];

  // 6 Productos destacados exactamente iguales a la maqueta de diseño
  productosDestacados: ProductoDestacadoItem[] = [
    {
      id: 201,
      nombre: 'Blusa Éter',
      subtitulo: 'Blusas • Nueva Colección',
      precio: 299,
      categoria: 'Blusas',
      imagenPrincipal: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
      imagenes: ['https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80'],
      tallas: ['S', 'M', 'L'],
      colores: [
        { nombre: 'Crema Marfil', hex: '#FAF0E6' },
        { nombre: 'Café Moka', hex: '#6B4423' }
      ],
      descripcion: 'Confección en satén de seda suave con caída fluida y escote refinado.',
      rating: 4.8,
      reviews: 42
    },
    {
      id: 202,
      nombre: 'Camisa Milano',
      subtitulo: 'Camisas • Otoño 2026',
      precio: 349,
      categoria: 'Blusas',
      imagenPrincipal: 'https://images.unsplash.com/photo-1598554747436-c9293d6a588f?auto=format&fit=crop&w=800&q=80',
      imagenes: ['https://images.unsplash.com/photo-1598554747436-c9293d6a588f?auto=format&fit=crop&w=800&q=80'],
      tallas: ['XS', 'S', 'M', 'L', 'XL'],
      colores: [
        { nombre: 'Azul Rayas', hex: '#6A82FB' },
        { nombre: 'Beige Arena', hex: '#E0C39E' },
        { nombre: 'Marrón Cuero', hex: '#6B4423' }
      ],
      descripcion: 'Algodón popelín italiano con estampado a rayas clásicas de sastrería.',
      rating: 4.9,
      reviews: 28
    },
    {
      id: 203,
      nombre: 'Blazer Aurora',
      subtitulo: 'Chaquetas • Sastrería Fina',
      precio: 699,
      categoria: 'Chaquetas',
      imagenPrincipal: 'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80',
      imagenes: ['https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80'],
      tallas: ['S', 'M', 'L'],
      colores: [
        { nombre: 'Gris Grafito', hex: '#9E9E9E' },
        { nombre: 'Vino Tinto', hex: '#6A1B29' }
      ],
      descripcion: 'Corte recto estructurado con lana noble y solapa de pico contemporánea.',
      rating: 4.9,
      reviews: 31
    },
    {
      id: 204,
      nombre: 'Vestido Noa',
      subtitulo: 'Vestidos • Noche & Cóctel',
      precio: 549,
      categoria: 'Vestidos',
      imagenPrincipal: 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=800&q=80',
      imagenes: ['https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=800&q=80'],
      tallas: ['XS', 'S', 'M'],
      colores: [
        { nombre: 'Negro Azabache', hex: '#18181B' },
        { nombre: 'Marrón Atacama', hex: '#6B4423' }
      ],
      descripcion: 'Vestido midi con mangas abullonadas y silueta entallada de alta definición.',
      rating: 4.7,
      reviews: 19
    },
    {
      id: 205,
      nombre: 'Suéter Lira',
      subtitulo: 'Tejidos • Esenciales',
      precio: 329,
      categoria: 'Tejidos',
      imagenPrincipal: 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=800&q=80',
      imagenes: ['https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=800&q=80'],
      tallas: ['S', 'M', 'L'],
      colores: [
        { nombre: 'Marfil Perla', hex: '#F5F5DC' },
        { nombre: 'Blanco Nieve', hex: '#FFFFFF' }
      ],
      descripcion: 'Punto acanalado en hilo suave con cuello cerrado y tacto ultra confortable.',
      rating: 4.6,
      reviews: 15
    },
    {
      id: 206,
      nombre: 'Cartera Siena',
      subtitulo: 'Accesorios • Cuero Artesanal',
      precio: 459,
      categoria: 'Accesorios',
      imagenPrincipal: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=800&q=80',
      imagenes: ['https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=800&q=80'],
      tallas: ['Única'],
      colores: [
        { nombre: 'Cuero Siena', hex: '#B87333' }
      ],
      descripcion: 'Bolso estructurado de mano con herrajes dorados y correa desmontable.',
      rating: 4.8,
      reviews: 27
    }
  ];

  ngOnInit(): void {
    // 1. Cargar productos destacados del catálogo
    this.catalogoService.consultarProductos({ limit: 6 }).subscribe({
      next: (res) => {
        if (res.data && res.data.length >= 4) {
          const mapped = res.data.map((p, idx) => ({
            id: p.id_producto,
            nombre: p.nombre,
            subtitulo: `${p.marca} • ${p.coleccion}`,
            precio: p.precio,
            categoria: p.categoria_nombre,
            imagenPrincipal: p.imagen_principal || this.productosDestacados[idx % this.productosDestacados.length].imagenPrincipal,
            imagenes: p.imagen_principal ? [p.imagen_principal] : [],
            tallas: p.tallas_disponibles?.map(t => t.nombre) || ['S', 'M', 'L'],
            colores: p.colores_disponibles?.map(c => ({ nombre: c.nombre, hex: c.codigo_hex })) || [{ nombre: 'Clásico', hex: '#18181B' }],
            descripcion: p.descripcion,
            popularidad: 95,
            etiqueta: p.temporada,
            rating: 4.7 + (idx % 3) * 0.1,
            reviews: 20 + idx * 7
          }));
          this.productosDestacados = mapped;
          this.cdr.markForCheck();
        }
      },
      error: () => {}
    });

    // 2. Cargar recomendaciones personalizadas por Mini Machine Learning
    this.recomendacionesService.obtenerMisRecomendaciones(4).subscribe({
      next: (res) => {
        if (res && res.recomendaciones && res.recomendaciones.length > 0) {
          this.recomendacionesML = res.recomendaciones;
          this.cdr.markForCheck();
        }
      },
      error: () => {}
    });
  }

  openQuickView(prod: any): void {
    if (prod?.id) {
      this.catalogoService.obtenerDetalleProducto(prod.id).subscribe({
        next: (res) => {
          if (res.data) {
            this.selectedProductForModal = res.data;
          } else {
            this.selectedProductForModal = prod;
          }
          this.cdr.markForCheck();
        },
        error: () => {
          this.router.navigate(['/catalogo']);
        }
      });
    } else {
      this.router.navigate(['/catalogo']);
    }
  }

  closeQuickView(): void {
    this.selectedProductForModal = null;
    this.cdr.markForCheck();
  }

  openAuth(tab: 'login' | 'register' = 'login'): void {
    this.authService.openAuthModal(tab);
  }

  toggleFavorito(prod: ProductoFashion, event: Event): void {
    event.stopPropagation();
    this.favoritosService?.toggleFavorito({
      id_producto: prod.id,
      nombre: prod.nombre,
      categoria_nombre: prod.categoria,
      precio: prod.precio,
      imagen_principal: prod.imagenPrincipal,
      subtitulo: prod.subtitulo
    });
    this.cdr.markForCheck();
  }

  esFavorito(id: number): boolean {
    return this.favoritosService?.esFavorito(id) ?? false;
  }
}
