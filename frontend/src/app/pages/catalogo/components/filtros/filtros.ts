import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FiltrosCatalogoResponse } from '../../../../services/catalogo-publico';

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

  @Output() busquedaChange = new EventEmitter<string>();
  @Output() categoriaChange = new EventEmitter<number | null>();
  @Output() tallaChange = new EventEmitter<number | null>();
  @Output() colorChange = new EventEmitter<number | null>();
  @Output() temporadaChange = new EventEmitter<string>();
  @Output() coleccionChange = new EventEmitter<string>();
  @Output() ordenChange = new EventEmitter<string>();
  @Output() precioMinChange = new EventEmitter<number | null>();
  @Output() precioMaxChange = new EventEmitter<number | null>();
  @Output() limpiar = new EventEmitter<void>();

  mostrarDrawerMovil: boolean = false;
  private searchTimer: any = null;
  private priceTimer: any = null;

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
