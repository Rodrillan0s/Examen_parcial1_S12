import { Component, OnInit, inject, ChangeDetectorRef, DestroyRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../../services/auth';
import { InventarioService, ItemInventario, ResumenInventario, MovimientoInventario, MovimientoPayload, FiltrosInventario } from '../../../services/inventario';
import { SucursalService, Sucursal } from '../../../services/sucursales';
import { TallasColoresService, Talla, ColorPrenda } from '../../../services/tallas-colores';

@Component({
  selector: 'app-lista-inventario',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './lista-inventario.html',
  styleUrls: ['./lista-inventario.css']
})
export class ListaInventarioComponent implements OnInit {
  private inventarioService = inject(InventarioService);
  private sucursalService = inject(SucursalService);
  private tallasColoresService = inject(TallasColoresService);
  public authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  private destroyRef = inject(DestroyRef);

  // Datos principales
  inventario: ItemInventario[] = [];
  resumen: ResumenInventario = {
    total_posiciones: 0,
    total_actual: 0,
    total_reservado: 0,
    total_disponible: 0,
    total_bajo_stock: 0,
    total_sin_stock: 0
  };

  // Catálogos para filtros
  sucursales: Sucursal[] = [];
  tallas: Talla[] = [];
  colores: ColorPrenda[] = [];

  // Filtros reactivos
  filtroSucursal: string = '';
  filtroBusqueda: string = '';
  filtroTalla: string = '';
  filtroColor: string = '';
  filtroEstado: string = '';
  filtroStock: '' | 'bajo_stock' | 'sin_stock' | 'disponible' = '';

  // Paginación
  paginaActual: number = 1;
  limite: number = 15;
  totalItems: number = 0;
  totalPaginas: number = 1;

  // Estados de interfaz
  cargando: boolean = false;
  procesandoMovimiento: boolean = false;
  mensajeExito: string = '';
  mensajeError: string = '';

  // Modal de Movimiento (Entrada, Salida, Ajuste)
  mostrarModalMovimiento: boolean = false;
  tipoMovimientoModal: 'ENTRADA' | 'SALIDA' | 'AJUSTE' = 'ENTRADA';
  itemSeleccionado: ItemInventario | null = null;
  cantidadMovimiento: number = 1;
  motivoMovimiento: string = '';
  modalError: string = '';
  stockCambioAlerta: boolean = false;

  // Proyecciones calculadas en tiempo real para el modal
  proyeccionStockActual: number = 0;
  proyeccionStockDisponible: number = 0;
  validacionValida: boolean = true;
  advertenciaStock: string = '';

  // Modal de Detalle de Variante por Sucursal
  mostrarModalDetalle: boolean = false;
  varianteDetalle: ItemInventario | null = null;
  sucursalesVariante: ItemInventario[] = [];
  cargandoDetalleVariante: boolean = false;

  // Modal / Drawer de Historial de Movimientos
  mostrarHistorial: boolean = false;
  cargandoHistorial: boolean = false;
  movimientos: MovimientoInventario[] = [];
  filtroTipoHistorial: string = '';
  totalMovimientos: number = 0;
  itemHistorialSeleccionado: ItemInventario | null = null;

  ngOnInit(): void {
    this.cargarCatalogos();
    this.cargarInventario();
  }

  cargarCatalogos(): void {
    // 1. Cargar sucursales de la empresa
    this.sucursalService.listarSucursales()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          if (res && res.data) {
            this.sucursales = res.data.filter(s => s.activo !== false);
            this.cdr.detectChanges();
          }
        },
        error: (err) => console.warn('Error cargando sucursales:', err)
      });

    // 2. Cargar tallas
    this.tallasColoresService.listarTallas()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res: any) => {
          if (res && res.data) {
            this.tallas = res.data;
            this.cdr.detectChanges();
          }
        },
        error: (err: any) => console.warn('Error cargando tallas:', err)
      });

    // 3. Cargar colores
    this.tallasColoresService.listarColores()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res: any) => {
          if (res && res.data) {
            this.colores = res.data;
            this.cdr.detectChanges();
          }
        },
        error: (err: any) => console.warn('Error cargando colores:', err)
      });
  }

  cargarInventario(): void {
    this.cargando = true;
    this.mensajeError = '';

    const filtros: FiltrosInventario = {
      id_sucursal: this.filtroSucursal || null,
      id_talla: this.filtroTalla || null,
      id_color: this.filtroColor || null,
      estado: this.filtroEstado !== '' ? this.filtroEstado : null,
      filtro_stock: this.filtroStock || null,
      busqueda: this.filtroBusqueda || null,
      pagina: this.paginaActual,
      limite: this.limite
    };

    this.inventarioService.consultarInventario(filtros)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.cargando = false;
          if (res && res.success) {
            this.inventario = res.items || [];
            this.totalItems = res.total || 0;
            this.totalPaginas = res.total_paginas || 1;
            if (res.resumen) {
              this.resumen = res.resumen;
            }
          } else {
            this.inventario = [];
            this.mensajeError = res?.message || 'No se pudo obtener el inventario.';
          }
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.cargando = false;
          this.inventario = [];
          this.mensajeError = err.error?.detail || 'Error al conectar con el servidor de inventario.';
          this.cdr.detectChanges();
        }
      });
  }

  aplicarFiltroStock(tipo: '' | 'bajo_stock' | 'sin_stock' | 'disponible'): void {
    this.filtroStock = this.filtroStock === tipo ? '' : tipo;
    this.paginaActual = 1;
    this.cargarInventario();
  }

  onFiltroChange(): void {
    this.paginaActual = 1;
    this.cargarInventario();
  }

  limpiarFiltros(): void {
    this.filtroSucursal = '';
    this.filtroBusqueda = '';
    this.filtroTalla = '';
    this.filtroColor = '';
    this.filtroEstado = '';
    this.filtroStock = '';
    this.paginaActual = 1;
    this.cargarInventario();
  }

  cambiarPagina(nuevaPagina: number): void {
    if (nuevaPagina >= 1 && nuevaPagina <= this.totalPaginas && nuevaPagina !== this.paginaActual) {
      this.paginaActual = nuevaPagina;
      this.cargarInventario();
    }
  }

  // MODAL DE MOVIMIENTOS (ENTRADA / SALIDA / AJUSTE)
  abrirModalMovimiento(item: ItemInventario, tipo: 'ENTRADA' | 'SALIDA' | 'AJUSTE'): void {
    this.itemSeleccionado = item;
    this.tipoMovimientoModal = tipo;
    this.modalError = '';
    this.motivoMovimiento = '';

    if (tipo === 'AJUSTE') {
      this.cantidadMovimiento = item.stock_actual;
    } else {
      this.cantidadMovimiento = 1;
    }

    this.recalcularProyeccion();
    this.mostrarModalMovimiento = true;
    this.cdr.detectChanges();
  }

  cerrarModalMovimiento(): void {
    this.mostrarModalMovimiento = false;
    this.itemSeleccionado = null;
    this.modalError = '';
    this.cdr.detectChanges();
  }

  recalcularProyeccion(): void {
    if (!this.itemSeleccionado) return;

    const actual = this.itemSeleccionado.stock_actual;
    const reservado = this.itemSeleccionado.stock_reservado;
    const cant = Number(this.cantidadMovimiento) || 0;

    this.advertenciaStock = '';
    this.validacionValida = true;

    if (this.tipoMovimientoModal === 'ENTRADA') {
      if (cant <= 0) {
        this.validacionValida = false;
        this.advertenciaStock = 'La cantidad debe ser mayor a 0.';
      }
      this.proyeccionStockActual = actual + cant;
      this.proyeccionStockDisponible = this.proyeccionStockActual - reservado;
    } else if (this.tipoMovimientoModal === 'SALIDA') {
      if (cant <= 0) {
        this.validacionValida = false;
        this.advertenciaStock = 'La cantidad a retirar debe ser mayor a 0.';
      } else if (cant > this.itemSeleccionado.stock_disponible) {
        this.validacionValida = false;
        this.advertenciaStock = `No es posible retirar ${cant} unidades. Stock disponible: ${this.itemSeleccionado.stock_disponible} (hay ${reservado} unidades reservadas para clientes).`;
      }
      this.proyeccionStockActual = Math.max(0, actual - cant);
      this.proyeccionStockDisponible = this.proyeccionStockActual - reservado;
    } else if (this.tipoMovimientoModal === 'AJUSTE') {
      if (cant < 0) {
        this.validacionValida = false;
        this.advertenciaStock = 'El stock ajustado no puede ser negativo.';
      } else if (cant < reservado) {
        this.validacionValida = false;
        this.advertenciaStock = `El nuevo stock no puede ser menor a las unidades reservadas vigentes (${reservado}).`;
      }
      this.proyeccionStockActual = cant;
      this.proyeccionStockDisponible = cant - reservado;
    }
  }

  guardarMovimiento(): void {
    if (!this.itemSeleccionado || !this.validacionValida) return;

    if (!this.motivoMovimiento || !this.motivoMovimiento.trim()) {
      this.modalError = 'Por favor ingrese el motivo del movimiento.';
      return;
    }

    this.procesandoMovimiento = true;
    this.modalError = '';

    const payload: MovimientoPayload = {
      id_sucursal: this.itemSeleccionado.id_sucursal,
      id_variante: this.itemSeleccionado.id_variante,
      tipo_movimiento: this.tipoMovimientoModal,
      cantidad: Number(this.cantidadMovimiento),
      motivo: this.motivoMovimiento.trim()
    };

    this.inventarioService.registrarMovimiento(payload)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.procesandoMovimiento = false;
          if (res && res.success) {
            this.cerrarModalMovimiento();
            this.mensajeExito = `Movimiento de ${this.tipoMovimientoModal} registrado exitosamente. Stock actualizado: ${res.stock_nuevo}`;
            this.cargarInventario();
            setTimeout(() => {
              this.mensajeExito = '';
              this.cdr.detectChanges();
            }, 5000);
          } else {
            this.modalError = res?.message || 'Error al procesar el movimiento de inventario.';
          }
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.procesandoMovimiento = false;
          const msg = err.error?.detail || err.error?.message || 'Error al comunicarse con el servidor.';
          this.modalError = msg;
          this.stockCambioAlerta = true;
          this.cdr.detectChanges();
        }
      });
  }

  recargarInventarioTrasError(): void {
    this.stockCambioAlerta = false;
    this.cargarInventario();
    if (this.itemSeleccionado) {
      this.inventarioService.obtenerInventarioPorId(this.itemSeleccionado.id_inventario)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
          next: (res) => {
            if (res && res.item) {
              this.itemSeleccionado = res.item;
              this.recalcularProyeccion();
              this.modalError = 'Stock sincronizado con los datos más recientes del servidor.';
              this.cdr.detectChanges();
            }
          },
          error: () => this.cargarInventario()
        });
    }
  }

  // DETALLE DE VARIANTE POR SUCURSAL
  abrirDetalleVariante(item: ItemInventario): void {
    this.varianteDetalle = item;
    this.mostrarModalDetalle = true;
    this.cargandoDetalleVariante = true;
    this.sucursalesVariante = [];

    this.inventarioService.consultarInventario({ id_variante: item.id_variante, limite: 100 })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.cargandoDetalleVariante = false;
          if (res && res.success) {
            this.sucursalesVariante = res.items || [];
          } else {
            this.sucursalesVariante = [item];
          }
          this.cdr.detectChanges();
        },
        error: () => {
          this.cargandoDetalleVariante = false;
          this.sucursalesVariante = [item];
          this.cdr.detectChanges();
        }
      });
  }

  cerrarDetalleVariante(): void {
    this.mostrarModalDetalle = false;
    this.varianteDetalle = null;
    this.sucursalesVariante = [];
    this.cdr.detectChanges();
  }

  // HISTORIAL DE MOVIMIENTOS
  abrirHistorial(item?: ItemInventario): void {
    this.itemHistorialSeleccionado = item || null;
    this.filtroTipoHistorial = '';
    this.mostrarHistorial = true;
    this.cargarHistorial();
  }

  cerrarHistorial(): void {
    this.mostrarHistorial = false;
    this.itemHistorialSeleccionado = null;
    this.movimientos = [];
    this.cdr.detectChanges();
  }

  cargarHistorial(): void {
    this.cargandoHistorial = true;

    const filtros = {
      id_inventario: this.itemHistorialSeleccionado?.id_inventario || null,
      id_sucursal: this.itemHistorialSeleccionado?.id_sucursal || null,
      id_variante: this.itemHistorialSeleccionado?.id_variante || null,
      tipo_movimiento: this.filtroTipoHistorial || null,
      limite: 50
    };

    this.inventarioService.consultarMovimientos(filtros)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.cargandoHistorial = false;
          if (res && res.success) {
            this.movimientos = res.items || [];
            this.totalMovimientos = res.total || 0;
          } else {
            this.movimientos = [];
          }
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.cargandoHistorial = false;
          this.movimientos = [];
          console.error('Error cargando movimientos:', err);
          this.cdr.detectChanges();
        }
      });
  }

  filtrarHistorial(tipo: string): void {
    this.filtroTipoHistorial = this.filtroTipoHistorial === tipo ? '' : tipo;
    this.cargarHistorial();
  }

  tienePermisoGestionar(): boolean {
    return this.authService.hasPermission('inventario.gestionar');
  }
}
