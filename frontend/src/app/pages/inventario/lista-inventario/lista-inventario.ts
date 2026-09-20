import { Component, OnInit, inject, ChangeDetectorRef, DestroyRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../../services/auth';
import { InventarioService, ItemInventario, ResumenInventario, MovimientoInventario, MovimientoPayload, FiltrosInventario } from '../../../services/inventario';
import { SucursalService, Sucursal } from '../../../services/sucursales';
import { TallasColoresService, Talla, ColorPrenda } from '../../../services/tallas-colores';
import { EmpresaService, Empresa } from '../../../services/empresa';
import { 
  ComprasLotesService, 
  PreviewResultadoData, 
  FilaPreview, 
  OrdenCompraItem, 
  LoteIngresoItem 
} from '../../../services/compras-lotes';

export type TabInventario = 'stock' | 'importacion' | 'ordenes' | 'lotes';

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
  private empresaService = inject(EmpresaService);
  public comprasLotesService = inject(ComprasLotesService);
  public authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  private destroyRef = inject(DestroyRef);

  // Navegación por pestañas
  tabActiva: TabInventario = 'stock';

  // Selección reactiva de empresa (Multi-Tenant)
  empresasDisponibles: Empresa[] = [];
  cargandoEmpresas: boolean = false;

  get esSuperAdmin(): boolean {
    return this.authService.getScopeLevel() === 'PLATAFORMA';
  }

  get empresaActivaId(): number | null {
    return this.authService.getEffectiveCompanyId();
  }

  get empresaActivaNombre(): string {
    return this.authService.getEffectiveCompanyName();
  }

  get empresaRequerida(): boolean {
    return this.esSuperAdmin && !this.empresaActivaId;
  }

  // Datos principales de stock
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

  // Filtros reactivos de stock
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

  // Estados de interfaz generales
  cargando: boolean = false;
  procesandoMovimiento: boolean = false;
  mensajeExito: string = '';
  mensajeError: string = '';

  // Modal de Movimiento manual
  mostrarModalMovimiento: boolean = false;
  tipoMovimientoModal: 'ENTRADA' | 'SALIDA' | 'AJUSTE' = 'ENTRADA';
  itemSeleccionado: ItemInventario | null = null;
  cantidadMovimiento: number = 1;
  motivoMovimiento: string = '';
  modalError: string = '';
  stockCambioAlerta: boolean = false;
  proyeccionStockActual: number = 0;
  proyeccionStockDisponible: number = 0;
  validacionValida: boolean = true;
  advertenciaStock: string = '';

  // Modal de Detalle de Variante
  mostrarModalDetalle: boolean = false;
  varianteDetalle: ItemInventario | null = null;
  sucursalesVariante: ItemInventario[] = [];
  cargandoDetalleVariante: boolean = false;

  // Modal / Drawer de Historial
  mostrarHistorial: boolean = false;
  cargandoHistorial: boolean = false;
  movimientos: MovimientoInventario[] = [];
  filtroTipoHistorial: string = '';
  totalMovimientos: number = 0;
  itemHistorialSeleccionado: ItemInventario | null = null;

  // ============================================================================
  // ESTADO: IMPORTACIÓN MASIVA DE LOTES (EXCEL)
  // ============================================================================
  archivoSeleccionado: File | null = null;
  nombreArchivoSeleccionado: string = '';
  analizandoExcel: boolean = false;
  confirmandoImportacion: boolean = false;
  descargandoPlantilla: boolean = false;
  previewData: PreviewResultadoData | null = null;
  sucursalDestinoImportacion: number | null = null;
  generarOrdenCompraImportacion: boolean = true;
  numeroLoteImportacion: string = '';
  guiaRemisionImportacion: string = '';
  observacionesImportacion: string = '';
  filtroEstadoPreview: string = 'TODOS';
  isDraggingFile: boolean = false;

  // ============================================================================
  // ESTADO: ÓRDENES DE COMPRA & PROCUREMENT
  // ============================================================================
  ordenesCompra: OrdenCompraItem[] = [];
  cargandoOrdenes: boolean = false;
  filtroEstadoOrden: string = 'TODOS';
  ordenSeleccionada: OrdenCompraItem | null = null;
  mostrarModalDetalleOrden: boolean = false;
  mostrarModalRechazar: boolean = false;
  motivoRechazo: string = '';
  mostrarModalRecepcion: boolean = false;
  loteRecepcionInput: string = '';
  guiaRecepcionInput: string = '';
  observacionesRecepcionInput: string = '';
  procesandoAccionOrden: boolean = false;

  // ============================================================================
  // ESTADO: LOTES INGRESADOS
  // ============================================================================
  lotes: LoteIngresoItem[] = [];
  cargandoLotes: boolean = false;

  get puedeGestionar(): boolean {
    return this.authService.hasPermission('inventario.gestionar');
  }

  get esNivelSucursal(): boolean {
    return this.authService.getScopeLevel() === 'SUCURSAL';
  }

  get sucursalAsignadaNombre(): string {
    return this.authService.activeBranch()?.nombre || 'Sucursal Asignada';
  }

  ngOnInit(): void {
    if (this.esSuperAdmin) {
      this.cargarEmpresas();
    }

    // Suscripción reactiva al cambio de empresa en el selector superior o directo
    this.authService.companyChanged$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        const br = this.authService.activeBranch();
        this.filtroSucursal = br && br.id ? String(br.id) : '';
        if (this.empresaRequerida) {
          this.inventario = [];
          this.sucursales = [];
          this.totalItems = 0;
          this.cargando = false;
          this.cdr.detectChanges();
        } else {
          this.cargarCatalogos();
          if (this.tabActiva === 'stock') {
            this.cargarInventario();
          } else if (this.tabActiva === 'ordenes') {
            this.cargarOrdenesCompra();
          } else if (this.tabActiva === 'lotes') {
            this.cargarLotes();
          }
        }
      });

    // Suscripción reactiva al cambio de sucursal en el selector superior
    this.authService.branchChanged$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((branch) => {
        if (this.esNivelSucursal) {
          const act = this.authService.activeBranch();
          this.filtroSucursal = act && act.id ? String(act.id) : '';
        } else {
          this.filtroSucursal = branch && branch.id ? String(branch.id) : '';
        }
        if (!this.empresaRequerida) {
          this.paginaActual = 1;
          if (this.tabActiva === 'stock') {
            this.cargarInventario();
          } else if (this.tabActiva === 'ordenes') {
            this.cargarOrdenesCompra();
          } else if (this.tabActiva === 'lotes') {
            this.cargarLotes();
          }
        }
      });
  }

  cargarEmpresas(): void {
    this.cargandoEmpresas = true;
    this.empresaService.listarEmpresas()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res: any) => {
          this.cargandoEmpresas = false;
          this.empresasDisponibles = (res?.data || []).filter((e: Empresa) => e.estado === 'ACTIVO');
          this.cdr.detectChanges();
        },
        error: () => {
          this.cargandoEmpresas = false;
          this.cdr.detectChanges();
        }
      });
  }

  seleccionarEmpresaDirecta(emp: Empresa): void {
    if (emp && emp.id_empresa) {
      this.authService.setSelectedCompany({
        id_empresa: emp.id_empresa,
        nombre_empresa: emp.nombre_empresa
      });
    }
  }

  cambiarTab(tab: TabInventario): void {
    this.tabActiva = tab;
    this.mensajeError = '';
    this.mensajeExito = '';

    if (this.empresaRequerida) {
      return;
    }

    if (tab === 'stock') {
      this.cargarInventario();
    } else if (tab === 'ordenes') {
      this.cargarOrdenesCompra();
    } else if (tab === 'lotes') {
      this.cargarLotes();
    } else if (tab === 'importacion') {
      if (!this.sucursalDestinoImportacion && this.sucursales.length > 0) {
        this.sucursalDestinoImportacion = this.sucursales[0].id_sucursal ?? null;
      }
    }
  }

  cargarCatalogos(): void {
    const idEmpresa = this.empresaActivaId || undefined;

    this.sucursalService.listarSucursales(idEmpresa)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          if (res && res.data) {
            this.sucursales = res.data.filter(s => s.activo !== false);
            if (this.esNivelSucursal) {
              const activeBr = this.authService.activeBranch();
              this.filtroSucursal = activeBr && activeBr.id ? String(activeBr.id) : (this.sucursales[0] ? String(this.sucursales[0].id_sucursal) : '');
            }
            if (this.sucursales.length > 0 && !this.sucursalDestinoImportacion) {
              this.sucursalDestinoImportacion = this.sucursales[0].id_sucursal ?? null;
            }
            this.cdr.detectChanges();
          }
        },
        error: (err) => console.warn('Error cargando sucursales:', err)
      });

    this.tallasColoresService.listarTallas(idEmpresa ? { id_empresa: idEmpresa } : undefined)
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

    this.tallasColoresService.listarColores(idEmpresa ? { id_empresa: idEmpresa } : undefined)
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

  // ============================================================================
  // MÓDULO 1: STOCK FÍSICO Y MOVIMIENTOS
  // ============================================================================
  cargarInventario(): void {
    if (this.empresaRequerida) {
      this.cargando = false;
      this.inventario = [];
      this.totalItems = 0;
      this.cdr.detectChanges();
      return;
    }

    // Aislamiento forzoso de sucursal para Encargados y Cajeros
    if (this.esNivelSucursal) {
      const activeBr = this.authService.activeBranch();
      if (activeBr && activeBr.id) {
        this.filtroSucursal = String(activeBr.id);
      }
    }

    this.cargando = true;
    this.mensajeError = '';

    const filtros: FiltrosInventario = {
      pagina: this.paginaActual,
      limite: this.limite,
      id_empresa: this.empresaActivaId || null,
      id_sucursal: this.filtroSucursal ? Number(this.filtroSucursal) : null,
      busqueda: this.filtroBusqueda.trim() || null,
      id_talla: this.filtroTalla ? Number(this.filtroTalla) : null,
      id_color: this.filtroColor ? Number(this.filtroColor) : null,
      estado: this.filtroEstado || null,
      filtro_stock: this.filtroStock || null
    };

    this.inventarioService.consultarInventario(filtros)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.cargando = false;
          if (res && res.success) {
            this.inventario = res.items || [];
            this.totalItems = res.total || 0;
            this.totalPaginas = res.total_paginas || Math.ceil(this.totalItems / this.limite) || 1;
            if (res.resumen) {
              this.resumen = res.resumen;
            }
          } else {
            this.inventario = [];
            this.totalItems = 0;
          }
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.cargando = false;
          this.mensajeError = err.error?.detail || err.error?.message || 'Error al conectar con el servidor de inventario.';
          this.cdr.detectChanges();
        }
      });
  }

  aplicarFiltros(): void {
    this.paginaActual = 1;
    this.cargarInventario();
  }

  onFiltroSucursalChange(): void {
    if (this.filtroSucursal) {
      const match = this.sucursales.find(s => String(s.id_sucursal) === this.filtroSucursal);
      if (match) {
        this.authService.setBranch({
          id: match.id_sucursal ?? 0,
          nombre: match.nombre,
          ciudad: match.ciudad || ''
        });
      }
    } else {
      this.authService.setBranch(null);
    }
    this.aplicarFiltros();
  }

  limpiarFiltros(): void {
    if (this.esNivelSucursal) {
      const activeBr = this.authService.activeBranch();
      this.filtroSucursal = activeBr && activeBr.id ? String(activeBr.id) : '';
    } else {
      this.filtroSucursal = '';
      this.authService.setBranch(null);
    }
    this.filtroBusqueda = '';
    this.filtroTalla = '';
    this.filtroColor = '';
    this.filtroEstado = '';
    this.filtroStock = '';
    this.paginaActual = 1;
    this.cargarInventario();
  }

  irAPagina(pag: number): void {
    if (pag >= 1 && pag <= this.totalPaginas && pag !== this.paginaActual) {
      this.paginaActual = pag;
      this.cargarInventario();
    }
  }

  // MODAL DE MOVIMIENTOS
  abrirModalMovimiento(item: ItemInventario, tipo: 'ENTRADA' | 'SALIDA' | 'AJUSTE'): void {
    this.itemSeleccionado = item;
    this.tipoMovimientoModal = tipo;
    this.cantidadMovimiento = tipo === 'AJUSTE' ? item.stock_actual : 1;
    this.motivoMovimiento = '';
    this.modalError = '';
    this.mostrarModalMovimiento = true;
    this.calcularProyeccion();
    this.cdr.detectChanges();
  }

  cerrarModalMovimiento(): void {
    this.mostrarModalMovimiento = false;
    this.itemSeleccionado = null;
    this.modalError = '';
    this.cdr.detectChanges();
  }

  calcularProyeccion(): void {
    if (!this.itemSeleccionado) return;
    const actual = this.itemSeleccionado.stock_actual;
    const reservado = this.itemSeleccionado.stock_reservado;
    const cant = Number(this.cantidadMovimiento) || 0;

    this.advertenciaStock = '';
    this.validacionValida = true;

    if (this.tipoMovimientoModal === 'ENTRADA') {
      this.proyeccionStockActual = actual + cant;
      this.proyeccionStockDisponible = this.proyeccionStockActual - reservado;
      if (cant <= 0) {
        this.validacionValida = false;
        this.advertenciaStock = 'La cantidad de entrada debe ser mayor a cero.';
      }
    } else if (this.tipoMovimientoModal === 'SALIDA') {
      this.proyeccionStockActual = actual - cant;
      this.proyeccionStockDisponible = this.proyeccionStockActual - reservado;
      if (cant <= 0) {
        this.validacionValida = false;
        this.advertenciaStock = 'La cantidad de salida debe ser mayor a cero.';
      } else if (this.proyeccionStockDisponible < 0) {
        this.validacionValida = false;
        this.advertenciaStock = `No se puede dar salida a ${cant} unidades. Stock disponible: ${this.itemSeleccionado.stock_disponible}.`;
      }
    } else if (this.tipoMovimientoModal === 'AJUSTE') {
      this.proyeccionStockActual = cant;
      this.proyeccionStockDisponible = cant - reservado;
      if (cant < 0) {
        this.validacionValida = false;
        this.advertenciaStock = 'El stock ajustado no puede ser negativo.';
      } else if (this.proyeccionStockDisponible < 0) {
        this.validacionValida = false;
        this.advertenciaStock = `El ajuste a ${cant} dejaría el stock disponible en negativo por reservas activas (${reservado}).`;
      }
    }

    this.stockCambioAlerta = this.proyeccionStockDisponible <= (this.itemSeleccionado.stock_minimo || 5);
  }

  guardarMovimiento(): void {
    if (!this.itemSeleccionado || !this.validacionValida) return;
    if (!this.motivoMovimiento.trim()) {
      this.modalError = 'Debe indicar el motivo o justificación del movimiento.';
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
            this.mensajeExito = `Movimiento de ${this.tipoMovimientoModal} registrado con éxito. Nuevo stock: ${res.stock_nuevo}`;
            this.cerrarModalMovimiento();
            this.cargarInventario();
          } else {
            this.modalError = res.message || 'No se pudo procesar el movimiento.';
          }
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.procesandoMovimiento = false;
          this.modalError = err.error?.detail || err.error?.message || 'Error al procesar el movimiento de inventario.';
          this.cdr.detectChanges();
        }
      });
  }

  abrirDetalleVariante(item: ItemInventario): void {
    this.varianteDetalle = item;
    this.mostrarModalDetalle = true;
    this.cargandoDetalleVariante = true;
    this.sucursalesVariante = [];

    this.inventarioService.consultarInventario({ id_variante: item.id_variante })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res: any) => {
          this.cargandoDetalleVariante = false;
          this.sucursalesVariante = res?.items || [item];
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
          this.movimientos = res?.items || [];
          this.totalMovimientos = res?.total || 0;
          this.cdr.detectChanges();
        },
        error: () => {
          this.cargandoHistorial = false;
          this.movimientos = [];
          this.cdr.detectChanges();
        }
      });
  }

  filtrarHistorial(tipo: string): void {
    this.filtroTipoHistorial = this.filtroTipoHistorial === tipo ? '' : tipo;
    this.cargarHistorial();
  }

  // ============================================================================
  // MÓDULO 2: IMPORTADOR MASIVO DE LOTES EXCEL (.XLSX)
  // ============================================================================

  descargarPlantillaExcel(): void {
    this.descargandoPlantilla = true;
    this.mensajeError = '';

    this.comprasLotesService.descargarPlantillaExcel().subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'plantilla_importacion_prendas_lote.xlsx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        this.descargandoPlantilla = false;
        this.mensajeExito = 'Plantilla oficial descargada con éxito. Complétala y cárgala aquí.';
        this.cdr.detectChanges();
      },
      error: () => {
        this.descargandoPlantilla = false;
        this.mensajeError = 'Error al descargar la plantilla desde el servidor.';
        this.cdr.detectChanges();
      }
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files?.[0];
    if (file) {
      this.procesarArchivoExcel(file);
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDraggingFile = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDraggingFile = false;
  }

  onFileDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDraggingFile = false;
    const file = event.dataTransfer?.files?.[0];
    if (file) {
      this.procesarArchivoExcel(file);
    }
  }

  procesarArchivoExcel(file: File): void {
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls') && !file.name.endsWith('.csv')) {
      this.mensajeError = 'Formato no soportado. Por favor sube un archivo Excel (.xlsx o .xls).';
      return;
    }

    this.archivoSeleccionado = file;
    this.nombreArchivoSeleccionado = file.name;
    this.analizandoExcel = true;
    this.mensajeError = '';
    this.mensajeExito = '';

    this.comprasLotesService.previsualizarArchivoExcel(file, this.sucursalDestinoImportacion || undefined)
      .subscribe({
        next: (res) => {
          this.analizandoExcel = false;
          if (res && res.success) {
            this.previewData = res.data;
            this.mensajeExito = `Archivo analizado: ${res.data.total_filas} filas detectadas (${res.data.total_prendas} prendas totales).`;
          }
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.analizandoExcel = false;
          this.mensajeError = err.error?.detail || err.error?.message || 'Error al procesar el archivo Excel.';
          this.cdr.detectChanges();
        }
      });
  }

  limpiarImportador(): void {
    this.archivoSeleccionado = null;
    this.nombreArchivoSeleccionado = '';
    this.previewData = null;
    this.filtroEstadoPreview = 'TODOS';
    this.numeroLoteImportacion = '';
    this.guiaRemisionImportacion = '';
    this.observacionesImportacion = '';
    this.cdr.detectChanges();
  }

  get filasPreviewFiltradas(): FilaPreview[] {
    if (!this.previewData || !this.previewData.filas) return [];
    if (this.filtroEstadoPreview === 'TODOS') return this.previewData.filas;
    return this.previewData.filas.filter(f => f.estado === this.filtroEstadoPreview);
  }

  confirmarImportacionLote(): void {
    if (!this.previewData || !this.previewData.filas.length) return;
    if (!this.sucursalDestinoImportacion) {
      this.mensajeError = 'Debe seleccionar la sucursal de destino para el ingreso del inventario.';
      return;
    }

    const filasValidas = this.previewData.filas.filter(f => f.estado !== 'ERROR');
    if (!filasValidas.length) {
      this.mensajeError = 'No hay filas válidas para importar. Por favor corrige los errores indicados.';
      return;
    }

    this.confirmandoImportacion = true;
    this.mensajeError = '';

    const payload = {
      id_sucursal: Number(this.sucursalDestinoImportacion),
      filas: filasValidas,
      generar_orden_compra: this.generarOrdenCompraImportacion,
      numero_lote: this.numeroLoteImportacion.trim() || undefined,
      guia_remision: this.guiaRemisionImportacion.trim() || undefined,
      observaciones: this.observacionesImportacion.trim() || 'Carga masiva desde archivo Excel'
    };

    this.comprasLotesService.confirmarImportacion(payload).subscribe({
      next: (res) => {
        this.confirmandoImportacion = false;
        this.mensajeExito = res.mensaje || 'Lote importado con éxito.';
        this.limpiarImportador();
        this.cargarInventario();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.confirmandoImportacion = false;
        this.mensajeError = err.error?.detail || err.error?.message || 'Error al confirmar la importación del lote.';
        this.cdr.detectChanges();
      }
    });
  }

  // ============================================================================
  // MÓDULO 3: ÓRDENES DE COMPRA & PROCUREMENT
  // ============================================================================

  cargarOrdenesCompra(): void {
    this.cargandoOrdenes = true;
    this.comprasLotesService.listarOrdenesCompra({
      estado: this.filtroEstadoOrden !== 'TODOS' ? this.filtroEstadoOrden : undefined
    }).subscribe({
      next: (res) => {
        this.cargandoOrdenes = false;
        this.ordenesCompra = res?.ordenes || [];
        this.cdr.detectChanges();
      },
      error: () => {
        this.cargandoOrdenes = false;
        this.ordenesCompra = [];
        this.cdr.detectChanges();
      }
    });
  }

  verDetalleOrden(orden: OrdenCompraItem): void {
    this.procesandoAccionOrden = true;
    this.comprasLotesService.obtenerDetalleOrden(orden.id_orden_compra).subscribe({
      next: (res) => {
        this.procesandoAccionOrden = false;
        this.ordenSeleccionada = res.orden;
        this.mostrarModalDetalleOrden = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.procesandoAccionOrden = false;
        this.mensajeError = err.error?.detail || 'Error cargando detalle de la orden.';
        this.cdr.detectChanges();
      }
    });
  }

  aprobarOrden(orden: OrdenCompraItem): void {
    if (!confirm(`¿Estás seguro de aprobar la Orden de Compra ${orden.numero_orden}?`)) return;

    this.procesandoAccionOrden = true;
    this.comprasLotesService.aprobarOrdenCompra(orden.id_orden_compra).subscribe({
      next: (res) => {
        this.procesandoAccionOrden = false;
        this.mensajeExito = res.mensaje || `Orden ${orden.numero_orden} aprobada. Ya puede ser recepcionada en almacén.`;
        this.cargarOrdenesCompra();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.procesandoAccionOrden = false;
        this.mensajeError = err.error?.detail || 'Error al aprobar la orden.';
        this.cdr.detectChanges();
      }
    });
  }

  abrirModalRechazar(orden: OrdenCompraItem): void {
    this.ordenSeleccionada = orden;
    this.motivoRechazo = '';
    this.mostrarModalRechazar = true;
    this.cdr.detectChanges();
  }

  confirmarRechazoOrden(): void {
    if (!this.ordenSeleccionada) return;
    if (!this.motivoRechazo.trim()) {
      alert('Debe ingresar un motivo para justificar el rechazo.');
      return;
    }

    this.procesandoAccionOrden = true;
    this.comprasLotesService.rechazarOrdenCompra(this.ordenSeleccionada.id_orden_compra, this.motivoRechazo.trim())
      .subscribe({
        next: (res) => {
          this.procesandoAccionOrden = false;
          this.mostrarModalRechazar = false;
          this.mensajeExito = res.mensaje || 'Orden rechazada.';
          this.cargarOrdenesCompra();
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.procesandoAccionOrden = false;
          this.mensajeError = err.error?.detail || 'Error al rechazar la orden.';
          this.cdr.detectChanges();
        }
      });
  }

  abrirModalRecepcion(orden: OrdenCompraItem): void {
    this.ordenSeleccionada = orden;
    this.loteRecepcionInput = `LOT-${orden.numero_orden}`;
    this.guiaRecepcionInput = '';
    this.observacionesRecepcionInput = '';
    this.mostrarModalRecepcion = true;
    this.cdr.detectChanges();
  }

  confirmarRecepcionOrden(): void {
    if (!this.ordenSeleccionada) return;

    this.procesandoAccionOrden = true;
    this.comprasLotesService.recibirMercaderiaOrden(this.ordenSeleccionada.id_orden_compra, {
      numero_lote: this.loteRecepcionInput.trim() || undefined,
      guia_remision: this.guiaRecepcionInput.trim() || undefined,
      observaciones: this.observacionesRecepcionInput.trim() || undefined
    }).subscribe({
      next: (res) => {
        this.procesandoAccionOrden = false;
        this.mostrarModalRecepcion = false;
        this.mensajeExito = res.mensaje || 'Mercadería recepcionada y cargada a inventario.';
        this.cargarOrdenesCompra();
        this.cargarInventario();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.procesandoAccionOrden = false;
        this.mensajeError = err.error?.detail || 'Error al confirmar la recepción.';
        this.cdr.detectChanges();
      }
    });
  }

  // ============================================================================
  // MÓDULO 4: LOTES DE MERCADERÍA
  // ============================================================================

  cargarLotes(): void {
    this.cargandoLotes = true;
    this.comprasLotesService.listarLotes().subscribe({
      next: (res) => {
        this.cargandoLotes = false;
        this.lotes = res?.lotes || [];
        this.cdr.detectChanges();
      },
      error: () => {
        this.cargandoLotes = false;
        this.lotes = [];
        this.cdr.detectChanges();
      }
    });
  }

  tienePermisoGestionar(): boolean {
    return this.authService.hasPermission('inventario.gestionar') || this.authService.obtenerNombreRol() === 'ADMINISTRADOR';
  }
}
