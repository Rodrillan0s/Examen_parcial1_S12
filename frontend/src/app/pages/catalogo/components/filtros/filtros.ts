import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FiltrosCatalogoResponse, TenantPublico } from '../../../../services/catalogo-publico';

@Component({
  selector: 'app-catalogo-filtros',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './filtros.html'
})
export class CatalogoFiltrosComponent {
  @Input() filtrosDisponibles: FiltrosCatalogoResponse = {
    categorias: [],
    tallas: [],
    colores: [],
    temporadas: [],
    colecciones: []
  };
  @Input() totalProductos: number = 0;
  @Input() searchQuery: string = '';
  @Input() selectedCategory: number | null = null;
  @Input() selectedTalla: number | null = null;
  @Input() selectedColor: number | null = null;
  @Input() selectedTemporada: string = 'Todas';
  @Input() selectedColeccion: string = 'Todas';
  @Input() selectedSort: string = 'destacados';
  @Input() precioMin: number | null = null;
  @Input() precioMax: number | null = null;
  @Input() tenants: TenantPublico[] = [];
  @Input() selectedTenantId: number | null = null;

  @Output() busquedaChange = new EventEmitter<string>();
  @Output() categoriaChange = new EventEmitter<number | null>();
  @Output() tallaChange = new EventEmitter<number | null>();
  @Output() colorChange = new EventEmitter<number | null>();
  @Output() temporadaChange = new EventEmitter<string>();
  @Output() coleccionChange = new EventEmitter<string>();
  @Output() ordenChange = new EventEmitter<string>();
  @Output() precioMinChange = new EventEmitter<number | null>();
  @Output() precioMaxChange = new EventEmitter<number | null>();
  @Output() tenantChange = new EventEmitter<number>();
  @Output() limpiar = new EventEmitter<void>();

  mostrarDrawerMovil: boolean = false;
  private searchTimer: any = null;
  private priceTimer: any = null;

  // Secciones colapsables de la barra lateral
  colapsados = {
    categoria: false,
    color: false,
    talla: false,
    temporada: false,
    precio: false,
    sucursal: false
  };

  toggleColapso(sec: 'categoria' | 'color' | 'talla' | 'temporada' | 'precio' | 'sucursal'): void {
    this.colapsados[sec] = !this.colapsados[sec];
  }

  get listaCategorias(): any[] {
    if (this.filtrosDisponibles?.categorias && this.filtrosDisponibles.categorias.length > 0) {
      return this.filtrosDisponibles.categorias;
    }
    return [
      { id_categoria: 1, nombre: 'Vestidos', total_prendas: 42 },
      { id_categoria: 2, nombre: 'Blusas', total_prendas: 28 },
      { id_categoria: 3, nombre: 'Pantalones', total_prendas: 31 },
      { id_categoria: 4, nombre: 'Chaquetas', total_prendas: 18 },
      { id_categoria: 5, nombre: 'Faldas', total_prendas: 22 },
      { id_categoria: 6, nombre: 'Accesorios', total_prendas: 40 },
      { id_categoria: 7, nombre: 'Calzado', total_prendas: 26 }
    ];
  }

  get listaColores(): any[] {
    if (this.filtrosDisponibles?.colores && this.filtrosDisponibles.colores.length > 0) {
      return this.filtrosDisponibles.colores;
    }
    return [
      { id_color: 1, nombre: 'Beige', codigo_hex: '#E6D5C3' },
      { id_color: 2, nombre: 'Negro', codigo_hex: '#18181B' },
      { id_color: 3, nombre: 'Café', codigo_hex: '#6B4423' },
      { id_color: 4, nombre: 'Oliva', codigo_hex: '#3B4D3C' },
      { id_color: 5, nombre: 'Rojo Carmín', codigo_hex: '#8A283B' }
    ];
  }

  get listaTallas(): any[] {
    if (this.filtrosDisponibles?.tallas && this.filtrosDisponibles.tallas.length > 0) {
      return this.filtrosDisponibles.tallas;
    }
    return [
      { id_talla: 1, nombre: 'XS' },
      { id_talla: 2, nombre: 'S' },
      { id_talla: 3, nombre: 'M' },
      { id_talla: 4, nombre: 'L' },
      { id_talla: 5, nombre: 'XL' }
    ];
  }

  onTenantSelect(event: Event): void {
    const val = Number((event.target as HTMLSelectElement).value);
    if (!isNaN(val)) {
      this.tenantChange.emit(val);
    }
  }

  onSearchInput(val: string): void {
    this.searchQuery = val;
    if (this.searchTimer) clearTimeout(this.searchTimer);
    this.searchTimer = setTimeout(() => {
      this.busquedaChange.emit(this.searchQuery);
    }, 350);
  }

  limpiarBusqueda(): void {
    this.searchQuery = '';
    this.busquedaChange.emit('');
  }

  onPrecioMinChange(val: any): void {
    const parsed = val !== null && val !== '' && !isNaN(Number(val)) ? Number(val) : null;
    this.precioMin = parsed;
    if (this.priceTimer) clearTimeout(this.priceTimer);
    this.priceTimer = setTimeout(() => {
      this.precioMinChange.emit(this.precioMin);
    }, 400);
  }

  onPrecioMaxChange(val: any): void {
    const parsed = val !== null && val !== '' && !isNaN(Number(val)) ? Number(val) : null;
    this.precioMax = parsed;
    if (this.priceTimer) clearTimeout(this.priceTimer);
    this.priceTimer = setTimeout(() => {
      this.precioMaxChange.emit(this.precioMax);
    }, 400);
  }

  aplicarPresetPrecio(min: number | null, max: number | null): void {
    this.precioMin = min;
    this.precioMax = max;
    this.precioMinChange.emit(min);
    this.precioMaxChange.emit(max);
  }

  toggleCategoria(id: number | null): void {
    const nuevo = (this.selectedCategory === id) ? null : id;
    this.categoriaChange.emit(nuevo);
  }

  toggleTalla(id: number | null): void {
    const nuevo = (this.selectedTalla === id) ? null : id;
    this.tallaChange.emit(nuevo);
  }

  toggleColor(id: number | null): void {
    const nuevo = (this.selectedColor === id) ? null : id;
    this.colorChange.emit(nuevo);
  }

  onTemporadaSelect(val: string): void {
    this.temporadaChange.emit(val);
  }

  onColeccionSelect(val: string): void {
    this.coleccionChange.emit(val);
  }

  onOrdenSelect(val: string): void {
    this.ordenChange.emit(val);
  }

  onLimpiar(): void {
    this.precioMin = null;
    this.precioMax = null;
    this.limpiar.emit();
    this.mostrarDrawerMovil = false;
  }

  contarFiltrosActivos(): number {
    let count = 0;
    if (this.searchQuery.trim().length > 0) count++;
    if (this.selectedCategory !== null) count++;
    if (this.selectedTalla !== null) count++;
    if (this.selectedColor !== null) count++;
    if (this.selectedTemporada !== 'Todas') count++;
    if (this.selectedColeccion !== 'Todas') count++;
    if (this.selectedSort !== 'destacados') count++;
    if (this.precioMin !== null && this.precioMin > 0) count++;
    if (this.precioMax !== null && this.precioMax > 0) count++;
    return count;
  }

  toggleDrawer(): void {
    this.mostrarDrawerMovil = !this.mostrarDrawerMovil;
  }
}
