import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth';
import { ThemeService } from '../../services/theme';
import { CarritoService } from '../../services/carrito';
import { 
  CatalogoPublicoService, 
  TenantPublico, 
  FiltrosCatalogoResponse, 
  PrendaCatalogo, 
  DetallePrendaCatalogo 
} from '../../services/catalogo-publico';
import { CatalogoFiltrosComponent } from './components/filtros/filtros';
import { ProductoCardComponent } from './components/producto-card/producto-card';
import { ProductDetailModalComponent } from '../../components/product-detail-modal/product-detail-modal';

@Component({
  selector: 'app-catalogo',
  standalone: true,
  imports: [
    CommonModule, 
    FormsModule, 
    RouterModule,
    CatalogoFiltrosComponent, 
    ProductoCardComponent, 
    ProductDetailModalComponent
  ],
  templateUrl: './catalogo.html'
})
export class CatalogoComponent implements OnInit {
  public catalogoService = inject(CatalogoPublicoService);
  public authService     = inject(AuthService);
  public themeService    = inject(ThemeService);
  public carritoService  = inject(CarritoService);
  private route          = inject(ActivatedRoute);
  private cdr            = inject(ChangeDetectorRef);

  // Tenants / Tiendas
  tenants: TenantPublico[] = [];
  selectedTenantId: number | null = null;
  selectedTenant: TenantPublico | null = null;

  // Productos & Paginación
  productos: PrendaCatalogo[] = [];
  totalProductos: number = 0;
  cargando: boolean = false;
  cargandoFiltros: boolean = false;

  // Filtros dinámicos
  filtrosDisponibles: FiltrosCatalogoResponse = {
    categorias: [],
    tallas: [],
    colores: [],
    temporadas: [],
    colecciones: []
  };

  // Valores de filtros activos
  searchQuery: string = '';
  selectedCategory: number | null = null;
  selectedTalla: number | null = null;
  selectedColor: number | null = null;
  selectedTemporada: string = 'Todas';
  selectedColeccion: string = 'Todas';
  selectedSort: string = 'destacados';
  precioMin: number | null = null;
  precioMax: number | null = null;

  // Paginación
  paginaActual: number = 1;
  limitePorPagina: number = 12;
  totalPaginas: number = 1;
  opcionesLimite: number[] = [12, 24, 48];

  // Detalle de Prenda (Modal)
  selectedProductForModal: DetallePrendaCatalogo | null = null;
  cargandoDetalle: boolean = false;
  private pendingProductId: number | null = null;

  ngOnInit(): void {
    // 1. Escuchar parámetros de ruta directa /catalogo/:id
    this.route.params.subscribe(params => {
      if (params['id']) {
        const id = parseInt(params['id'], 10);
        if (!isNaN(id)) {
          this.pendingProductId = id;
          this.abrirDetalle(id);
        }
      }
    });

    // 2. Escuchar queryParams (tenant / empresa / producto)
    this.route.queryParams.subscribe(params => {
      const urlTenant = params['empresa'] || params['tenant'];
      const initialTenantId = urlTenant ? parseInt(urlTenant, 10) : null;
      if (params['producto'] || params['id_producto']) {
        const prodId = parseInt(params['producto'] || params['id_producto'], 10);
        if (!isNaN(prodId)) {
          this.pendingProductId = prodId;
        }
      }
      this.cargarTenants(initialTenantId);
    });
  }

  cargarTenants(initialTenantId: number | null = null): void {
    this.catalogoService.obtenerTenants().subscribe({
      next: (res) => {
        this.tenants = res.data || [];
        if (this.tenants.length > 0) {
          if (initialTenantId && this.tenants.some(t => t.id_empresa === initialTenantId)) {
            this.selectedTenantId = initialTenantId;
          } else {
            this.selectedTenantId = this.tenants[0].id_empresa;
          }
          this.selectedTenant = this.tenants.find(t => t.id_empresa === this.selectedTenantId) || this.tenants[0];
          if (this.selectedTenantId) {
            this.carritoService.setEmpresaId(this.selectedTenantId);
          }
          this.cargarFiltrosYProductos();

          if (this.pendingProductId) {
            this.abrirDetalle(this.pendingProductId);
          }
        }
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error al cargar tiendas activas:', err);
        this.cdr.markForCheck();
      }
    });
  }

  cambiarTenant(idEmpresa: number): void {
    if (this.selectedTenantId === idEmpresa) return;
    this.selectedTenantId = idEmpresa;
    this.selectedTenant = this.tenants.find(t => t.id_empresa === idEmpresa) || null;
    this.carritoService.setEmpresaId(idEmpresa);
    this.limpiarFiltros(false);
    this.cargarFiltrosYProductos();
    this.cdr.markForCheck();
  }

  cargarFiltrosYProductos(): void {
    if (!this.selectedTenantId) return;

    this.cargandoFiltros = true;
    this.cdr.markForCheck();
    this.catalogoService.obtenerFiltros(this.selectedTenantId).subscribe({
      next: (res) => {
        this.filtrosDisponibles = res.data;
        if (res.empresa) {
          this.selectedTenant = res.empresa;
        }
        this.cargandoFiltros = false;
        this.cdr.markForCheck();
        this.aplicarFiltros();
      },
      error: (err) => {
        console.error('Error al cargar filtros dinámicos:', err);
        this.cargandoFiltros = false;
        this.cdr.markForCheck();
        this.aplicarFiltros();
      }
    });
  }

  aplicarFiltros(): void {
    if (!this.selectedTenantId) return;
    this.cargando = true;
    this.cdr.markForCheck();

    const offset = (this.paginaActual - 1) * this.limitePorPagina;

    this.catalogoService.consultarProductos({
      id_empresa: this.selectedTenantId,
      busqueda: this.searchQuery,
      id_categoria: this.selectedCategory || undefined,
      id_talla: this.selectedTalla || undefined,
      id_color: this.selectedColor || undefined,
      temporada: this.selectedTemporada,
      coleccion: this.selectedColeccion,
      precio_min: this.precioMin !== null ? this.precioMin : undefined,
      precio_max: this.precioMax !== null ? this.precioMax : undefined,
      orden: this.selectedSort,
      limit: this.limitePorPagina,
      offset: offset
    }).subscribe({
      next: (res) => {
        this.productos = res.data || [];
        this.totalProductos = res.total || 0;
        this.totalPaginas = Math.ceil(this.totalProductos / this.limitePorPagina) || 1;
        if (this.paginaActual > this.totalPaginas && this.totalPaginas > 0) {
          this.paginaActual = this.totalPaginas;
        }
        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error al consultar productos:', err);
        this.productos = [];
        this.totalProductos = 0;
        this.totalPaginas = 1;
        this.cargando = false;
        this.cdr.markForCheck();
      }
    });
  }

  // --- Handlers de Filtros Component ---
  onBusquedaChange(q: string): void {
    this.searchQuery = q;
    this.paginaActual = 1;
    this.aplicarFiltros();
  }

  onCategoriaChange(idCat: number | null): void {
    this.selectedCategory = idCat;
    this.paginaActual = 1;
    this.aplicarFiltros();
  }

  onTallaChange(idTalla: number | null): void {
    this.selectedTalla = idTalla;
    this.paginaActual = 1;
    this.aplicarFiltros();
  }

  onColorChange(idColor: number | null): void {
    this.selectedColor = idColor;
    this.paginaActual = 1;
    this.aplicarFiltros();
  }

  onTemporadaChange(t: string): void {
    this.selectedTemporada = t;
    this.paginaActual = 1;
    this.aplicarFiltros();
  }

  onColeccionChange(c: string): void {
    this.selectedColeccion = c;
    this.paginaActual = 1;
    this.aplicarFiltros();
  }

  onOrdenChange(o: string): void {
    this.selectedSort = o;
    this.paginaActual = 1;
    this.aplicarFiltros();
  }

  onPrecioMinChange(min: number | null): void {
    this.precioMin = min;
    this.paginaActual = 1;
    this.aplicarFiltros();
  }

  onPrecioMaxChange(max: number | null): void {
    this.precioMax = max;
    this.paginaActual = 1;
    this.aplicarFiltros();
  }

  limpiarFiltros(recargar: boolean = true): void {
    this.searchQuery = '';
    this.selectedCategory = null;
    this.selectedTalla = null;
    this.selectedColor = null;
    this.selectedTemporada = 'Todas';
    this.selectedColeccion = 'Todas';
    this.selectedSort = 'destacados';
    this.precioMin = null;
    this.precioMax = null;
    this.paginaActual = 1;

    if (recargar) {
      this.aplicarFiltros();
    }
  }

  // --- Handlers de Paginación ---
  cambiarPagina(nuevaPagina: number): void {
    if (nuevaPagina < 1 || nuevaPagina > this.totalPaginas || nuevaPagina === this.paginaActual) return;
    this.paginaActual = nuevaPagina;
    this.aplicarFiltros();
    window.scrollTo({ top: 180, behavior: 'smooth' });
  }

  cambiarLimite(nuevoLimite: any): void {
    const lim = parseInt(nuevoLimite, 10);
    if (!isNaN(lim) && lim > 0 && lim !== this.limitePorPagina) {
      this.limitePorPagina = lim;
      this.paginaActual = 1;
      this.aplicarFiltros();
    }
  }

  getPaginasVisibles(): number[] {
    const paginas: number[] = [];
    const maxBtns = 5;
    let start = Math.max(1, this.paginaActual - Math.floor(maxBtns / 2));
    let end = Math.min(this.totalPaginas, start + maxBtns - 1);
    if (end - start + 1 < maxBtns) {
      start = Math.max(1, end - maxBtns + 1);
    }
    for (let i = start; i <= end; i++) {
      paginas.push(i);
    }
    return paginas;
  }

  // --- Detalle de Prenda ---
  abrirDetalle(idProducto: number): void {
    this.cargandoDetalle = true;
    this.cdr.markForCheck();
    this.catalogoService.obtenerDetalleProducto(idProducto, this.selectedTenantId || undefined).subscribe({
      next: (res) => {
        this.selectedProductForModal = res.data;
        this.cargandoDetalle = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error al abrir detalle:', err);
        this.cargandoDetalle = false;
        this.cdr.markForCheck();
      }
    });
  }

  cerrarModalDetalle(): void {
    this.selectedProductForModal = null;
    this.cdr.markForCheck();
  }
}
