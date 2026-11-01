import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { AuthService } from '../../services/auth';
import { SucursalService, Sucursal } from '../../services/sucursales';
import {
  DevolucionesService,
  DevolucionResumen,
  DevolucionDetalleCompleto,
  DevolucionesFiltros,
  ElegibilidadVentaResponse,
  DevolucionPresencialPayload,
  ItemPresencialDevolucion
} from '../../services/devoluciones';

@Component({
  selector: 'app-devoluciones',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './devoluciones.html',
  styleUrls: ['./devoluciones.css']
})
export class DevolucionesComponent implements OnInit {
  public authService = inject(AuthService);
  private devolucionesService = inject(DevolucionesService);
  private sucursalService = inject(SucursalService);
  private cdr = inject(ChangeDetectorRef);

  // --- DATOS Y LISTADO ---
  devoluciones: DevolucionResumen[] = [];
  total: number = 0;
  paginaActual: number = 1;
  limitePorPagina: number = 15;
  totalPaginas: number = 1;
  cargando: boolean = false;
  sucursales: Sucursal[] = [];

  // --- FILTROS DE BANDEJA ---
  filtroEstado: string = 'TODOS';
  filtroSucursal: number | null = null;
  filtroFechaInicio: string = '';
  filtroFechaFin: string = '';
  filtroBusqueda: string = '';

  // --- MODAL DETALLE / HISTORIAL ---
  mostrarModalDetalle: boolean = false;
  devolucionDetalle: DevolucionDetalleCompleto | null = null;
  cargandoDetalle: boolean = false;

  // --- MODAL REGISTRO PRESENCIAL (CU24W) ---
  mostrarModalPresencial: boolean = false;
  idVentaBusqueda: string = '';
  cargandoVentaPresencial: boolean = false;
  ventaElegiblePresencial: ElegibilidadVentaResponse | null = null;
  itemsPresenciales: {
    [id_detalle_venta: number]: {
      seleccionado: boolean;
      cantidad: number;
      condicion: 'REVENDIBLE' | 'DEFECTUOSO';
    }
  } = {};
  motivoPresencial: string = 'DEFECTO_FABRICA';
  observacionesPresenciales: string = '';
  idSucursalPresencial: number | null = null;
  reembolsoInmediatoPresencial: boolean = false;
  metodoReembolsoPresencial: string = 'EFECTIVO';
  referenciaReembolsoPresencial: string = '';
  guardandoPresencial: boolean = false;

  // --- MODAL DICTAMEN (APROBAR / RECHAZAR) ---
  mostrarModalDictamen: boolean = false;
  idDevolucionDictamen: number | null = null;
  codigoDevolucionDictamen: string = '';
  accionDictamen: 'APROBAR' | 'RECHAZAR' | 'EN_REVISION' = 'APROBAR';
  observacionesDictamen: string = '';
  guardandoDictamen: boolean = false;

  // --- MODAL RECEPCIÓN FÍSICA E INSPECCIÓN ---
  mostrarModalRecepcion: boolean = false;
  idDevolucionRecepcion: number | null = null;
  codigoDevolucionRecepcion: string = '';
  idSucursalRecepcion: number | null = null;
  itemsRecepcion: {
    [id_detalle_devolucion: number]: {
      cantidad: number;
      condicion: 'REVENDIBLE' | 'DEFECTUOSO';
    }
  } = {};
  observacionesRecepcion: string = '';
  guardandoRecepcion: boolean = false;

  // --- MODAL LIQUIDACIÓN REEMBOLSO ---
  mostrarModalReembolso: boolean = false;
  idDevolucionReembolso: number | null = null;
  codigoDevolucionReembolso: string = '';
  montoReembolsoLiquidacion: number = 0;
  metodoReembolso: string = 'EFECTIVO';
  referenciaReembolso: string = '';
  observacionesReembolso: string = '';
  guardandoReembolso: boolean = false;

  // --- TOAST NOTIFICATIONS ---
  mensajeToast: { tipo: 'exito' | 'error' | 'info'; texto: string } | null = null;

  ngOnInit(): void {
    this.cargarSucursales();
    this.cargarDevoluciones(1);
  }

  // =========================================================================
  // CARGA DE DATOS & SUCURSALES
  // =========================================================================

  cargarSucursales(): void {
    const idEmpresa = this.authService.getEffectiveCompanyId();
    this.sucursalService.listarSucursales(idEmpresa || undefined).subscribe({
      next: (res: any) => {
        this.sucursales = Array.isArray(res) ? res : (res?.data || []);
        if (this.sucursales.length > 0 && !this.idSucursalPresencial) {
          this.idSucursalPresencial = this.sucursales[0]?.id_sucursal ?? null;
          this.idSucursalRecepcion = this.sucursales[0]?.id_sucursal ?? null;
        }
        this.cdr.markForCheck();
      },
      error: () => {
        // Fallback no bloqueante si falla sucursales
      }
    });
  }

  cargarDevoluciones(pagina: number = 1): void {
    this.paginaActual = pagina;
    this.cargando = true;
    this.cdr.markForCheck();

    const filtros: DevolucionesFiltros = {
      page: this.paginaActual,
      limit: this.limitePorPagina,
      estado: this.filtroEstado !== 'TODOS' ? this.filtroEstado : undefined,
      id_sucursal: this.filtroSucursal || undefined,
      fecha_inicio: this.filtroFechaInicio || undefined,
      fecha_fin: this.filtroFechaFin || undefined,
      busqueda: this.filtroBusqueda.trim() || undefined,
      id_empresa: this.authService.getEffectiveCompanyId() || undefined
    };

    this.devolucionesService.listarDevolucionesPersonal(filtros).subscribe({
      next: (res: any) => {
        this.devoluciones = res.data || [];
        this.total = res.total || 0;
        this.totalPaginas = res.total_paginas || 1;
        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.cargando = false;
        this.mostrarToast('error', err?.error?.detail || 'Error al consultar bandeja de devoluciones.');
        this.cdr.markForCheck();
      }
    });
  }

  aplicarFiltros(): void {
    this.cargarDevoluciones(1);
  }

  limpiarFiltros(): void {
    this.filtroEstado = 'TODOS';
    this.filtroSucursal = null;
    this.filtroFechaInicio = '';
    this.filtroFechaFin = '';
    this.filtroBusqueda = '';
    this.cargarDevoluciones(1);
  }

  // =========================================================================
  // DETALLE COMPLETO DE DEVOLUCIÓN
  // =========================================================================

  abrirDetalle(idDevolucion: number): void {
    this.cargandoDetalle = true;
    this.mostrarModalDetalle = true;
    this.devolucionDetalle = null;
    this.cdr.markForCheck();

    this.devolucionesService.obtenerDetallePersonal(idDevolucion, this.authService.getEffectiveCompanyId() || undefined).subscribe({
      next: (res: any) => {
        this.devolucionDetalle = res.data;
        this.cargandoDetalle = false;
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.cargandoDetalle = false;
        this.mostrarModalDetalle = false;
        this.mostrarToast('error', err?.error?.detail || 'No se pudo obtener el detalle de la devolución.');
        this.cdr.markForCheck();
      }
    });
  }

  cerrarDetalle(): void {
    this.mostrarModalDetalle = false;
    this.devolucionDetalle = null;
    this.cdr.markForCheck();
  }

  // =========================================================================
  // CU24W: DEVOLUCIÓN PRESENCIAL (MOSTRADOR / CAJERO)
  // =========================================================================

  abrirModalPresencial(): void {
    this.mostrarModalPresencial = true;
    this.idVentaBusqueda = '';
    this.ventaElegiblePresencial = null;
    this.itemsPresenciales = {};
    this.motivoPresencial = 'DEFECTO_FABRICA';
    this.observacionesPresenciales = '';
    this.reembolsoInmediatoPresencial = false;
    this.metodoReembolsoPresencial = 'EFECTIVO';
    this.referenciaReembolsoPresencial = 'REC-PRES-' + Date.now().toString().slice(-6);
    this.cdr.markForCheck();
  }

  cerrarModalPresencial(): void {
    this.mostrarModalPresencial = false;
    this.ventaElegiblePresencial = null;
    this.itemsPresenciales = {};
    this.cdr.markForCheck();
  }

  buscarVentaParaPresencial(): void {
    const query = this.idVentaBusqueda.trim();
    if (!query) {
      this.mostrarToast('info', 'Ingresa el ID o número de venta a consultar.');
      return;
    }

    const idVenta = parseInt(query, 10);
    if (isNaN(idVenta) || idVenta <= 0) {
      this.mostrarToast('error', 'Por favor ingresa un ID numérico de venta válido.');
      return;
    }

    this.cargandoVentaPresencial = true;
    this.ventaElegiblePresencial = null;
    this.itemsPresenciales = {};
    this.cdr.markForCheck();

    this.devolucionesService.consultarElegibilidadVenta(idVenta, this.authService.getEffectiveCompanyId() || undefined).subscribe({
      next: (res: any) => {
        this.cargandoVentaPresencial = false;
        this.ventaElegiblePresencial = res;
        if (res.es_elegible && res.items?.length) {
          res.items.forEach((it: any) => {
            if (it.cantidad_elegible > 0) {
              this.itemsPresenciales[it.id_detalle_venta] = {
                seleccionado: false,
                cantidad: it.cantidad_elegible,
                condicion: 'REVENDIBLE'
              };
            }
          });
        }
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.cargandoVentaPresencial = false;
        this.mostrarToast('error', err?.error?.detail || 'No se pudo consultar la venta.');
        this.cdr.markForCheck();
      }
    });
  }

  toggleItemPresencial(idDet: number): void {
    if (this.itemsPresenciales[idDet]) {
      this.itemsPresenciales[idDet].seleccionado = !this.itemsPresenciales[idDet].seleccionado;
      this.cdr.markForCheck();
    }
  }

  ajustarCantidadPresencial(idDet: number, cant: number, max: number): void {
    if (this.itemsPresenciales[idDet]) {
      this.itemsPresenciales[idDet].cantidad = Math.max(1, Math.min(cant, max));
      this.cdr.markForCheck();
    }
  }

  hayItemsPresenciales(): boolean {
    return Object.values(this.itemsPresenciales).some(it => it.seleccionado && it.cantidad > 0);
  }

  calcularReembolsoPresencial(): number {
    if (!this.ventaElegiblePresencial?.items) return 0;
    let tot = 0;
    for (const it of this.ventaElegiblePresencial.items) {
      const sel = this.itemsPresenciales[it.id_detalle_venta];
      if (sel?.seleccionado && sel.cantidad > 0) {
        tot += it.precio_neto_unitario * sel.cantidad;
      }
    }
    return Math.round(tot * 100) / 100;
  }

  confirmarDevolucionPresencial(): void {
    if (!this.hayItemsPresenciales()) {
      this.mostrarToast('info', 'Selecciona al menos una prenda para la devolución presencial.');
      return;
    }
    if (!this.ventaElegiblePresencial?.venta) return;

    const itemsPayload: ItemPresencialDevolucion[] = Object.entries(this.itemsPresenciales)
      .filter(([_, val]) => val.seleccionado && val.cantidad > 0)
      .map(([idDet, val]) => ({
        id_detalle_venta: Number(idDet),
        cantidad: val.cantidad,
        condicion: val.condicion
      }));

    const payload: DevolucionPresencialPayload = {
      id_venta: this.ventaElegiblePresencial.venta.id_venta,
      id_sucursal: this.idSucursalPresencial || this.ventaElegiblePresencial.venta.id_sucursal || undefined,
      id_empresa: this.authService.getEffectiveCompanyId() || undefined,
      motivo: this.motivoPresencial,
      observaciones: this.observacionesPresenciales.trim() || undefined,
      items: itemsPayload,
      registrar_reembolso_inmediato: this.reembolsoInmediatoPresencial,
      metodo_reembolso: this.reembolsoInmediatoPresencial ? this.metodoReembolsoPresencial : undefined,
      referencia_reembolso: this.reembolsoInmediatoPresencial ? this.referenciaReembolsoPresencial.trim() : undefined
    };

    this.guardandoPresencial = true;
    this.cdr.markForCheck();

    this.devolucionesService.registrarDevolucionPresencial(payload).subscribe({
      next: (res: any) => {
        this.guardandoPresencial = false;
        this.cerrarModalPresencial();
        this.mostrarToast('exito', `Devolución presencial ${res?.data?.codigo_devolucion || ''} registrada y stock actualizado.`);
        this.cargarDevoluciones(1);
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.guardandoPresencial = false;
        this.mostrarToast('error', err?.error?.detail || 'Error al procesar la devolución presencial.');
        this.cdr.markForCheck();
      }
    });
  }

  // =========================================================================
  // CU24W: DICTAMEN (APROBAR / RECHAZAR SOLICITUD)
  // =========================================================================

  abrirModalDictamen(dev: DevolucionResumen | DevolucionDetalleCompleto): void {
    this.idDevolucionDictamen = dev.id_devolucion;
    this.codigoDevolucionDictamen = dev.codigo_devolucion;
    this.accionDictamen = 'APROBAR';
    this.observacionesDictamen = '';
    this.mostrarModalDictamen = true;
    this.cdr.markForCheck();
  }

  cerrarModalDictamen(): void {
    this.mostrarModalDictamen = false;
    this.idDevolucionDictamen = null;
    this.observacionesDictamen = '';
    this.cdr.markForCheck();
  }

  confirmarDictamen(): void {
    if (!this.idDevolucionDictamen) return;
    if (!this.observacionesDictamen.trim()) {
      this.mostrarToast('info', 'Debes ingresar una justificación técnica para el dictamen.');
      return;
    }

    this.guardandoDictamen = true;
    this.cdr.markForCheck();

    this.devolucionesService.dictaminarSolicitud(
      this.idDevolucionDictamen,
      this.accionDictamen,
      this.observacionesDictamen.trim(),
      this.authService.getEffectiveCompanyId() || undefined
    ).subscribe({
      next: (res: any) => {
        this.guardandoDictamen = false;
        this.cerrarModalDictamen();
        this.mostrarToast('exito', `Dictamen emitido: ${res?.nuevo_estado || this.accionDictamen}.`);
        if (this.mostrarModalDetalle && this.devolucionDetalle?.id_devolucion === this.idDevolucionDictamen) {
          this.abrirDetalle(this.idDevolucionDictamen);
        }
        this.cargarDevoluciones(this.paginaActual);
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.guardandoDictamen = false;
        this.mostrarToast('error', err?.error?.detail || 'Error al emitir el dictamen.');
        this.cdr.markForCheck();
      }
    });
  }

  // =========================================================================
  // CU24W: RECEPCIÓN FÍSICA E INSPECCIÓN DE PRENDAS
  // =========================================================================

  abrirModalRecepcion(dev: DevolucionDetalleCompleto): void {
    this.idDevolucionRecepcion = dev.id_devolucion;
    this.codigoDevolucionRecepcion = dev.codigo_devolucion;
    this.idSucursalRecepcion = dev.id_sucursal || (this.sucursales[0]?.id_sucursal ?? null);
    this.observacionesRecepcion = '';
    this.itemsRecepcion = {};

    if (dev.items) {
      dev.items.forEach(it => {
        this.itemsRecepcion[it.id_detalle_devolucion] = {
          cantidad: it.cantidad,
          condicion: 'REVENDIBLE'
        };
      });
    }

    this.mostrarModalRecepcion = true;
    this.cdr.markForCheck();
  }

  cerrarModalRecepcion(): void {
    this.mostrarModalRecepcion = false;
    this.idDevolucionRecepcion = null;
    this.itemsRecepcion = {};
    this.cdr.markForCheck();
  }

  confirmarRecepcion(): void {
    if (!this.idDevolucionRecepcion) return;

    const itemsPayload = Object.entries(this.itemsRecepcion).map(([idDetDev, val]) => ({
      id_detalle_devolucion: Number(idDetDev),
      cantidad_recibida: val.cantidad,
      condicion: val.condicion
    }));

    if (itemsPayload.length === 0) {
      this.mostrarToast('info', 'No hay ítems para recepcionar.');
      return;
    }

    this.guardandoRecepcion = true;
    this.cdr.markForCheck();

    this.devolucionesService.registrarRecepcionPrendas(
      this.idDevolucionRecepcion,
      itemsPayload,
      this.idSucursalRecepcion || undefined,
      this.observacionesRecepcion.trim() || undefined,
      this.authService.getEffectiveCompanyId() || undefined
    ).subscribe({
      next: (res: any) => {
        this.guardandoRecepcion = false;
        this.cerrarModalRecepcion();
        this.mostrarToast('exito', `Prendas recepcionadas físicamente. Stock vendible actualizado para prendas REVENDIBLES.`);
        if (this.mostrarModalDetalle && this.devolucionDetalle?.id_devolucion === this.idDevolucionRecepcion) {
          this.abrirDetalle(this.idDevolucionRecepcion);
        }
        this.cargarDevoluciones(this.paginaActual);
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.guardandoRecepcion = false;
        this.mostrarToast('error', err?.error?.detail || 'Error al procesar la recepción física.');
        this.cdr.markForCheck();
      }
    });
  }

  // =========================================================================
  // CU24W: LIQUIDACIÓN DE REEMBOLSO FINANCIERO
  // =========================================================================

  abrirModalReembolso(dev: DevolucionResumen | DevolucionDetalleCompleto): void {
    this.idDevolucionReembolso = dev.id_devolucion;
    this.codigoDevolucionReembolso = dev.codigo_devolucion;
    this.montoReembolsoLiquidacion = dev.monto_reembolso;
    this.metodoReembolso = 'EFECTIVO';
    this.referenciaReembolso = 'REEMB-' + Date.now().toString().slice(-6);
    this.observacionesReembolso = '';
    this.mostrarModalReembolso = true;
    this.cdr.markForCheck();
  }

  cerrarModalReembolso(): void {
    this.mostrarModalReembolso = false;
    this.idDevolucionReembolso = null;
    this.cdr.markForCheck();
  }

  confirmarReembolso(): void {
    if (!this.idDevolucionReembolso) return;
    if (!this.referenciaReembolso.trim()) {
      this.mostrarToast('info', 'Ingresa la referencia o comprobante de pago bancario.');
      return;
    }

    this.guardandoReembolso = true;
    this.cdr.markForCheck();

    this.devolucionesService.liquidarReembolso(
      this.idDevolucionReembolso,
      this.metodoReembolso,
      this.referenciaReembolso.trim(),
      this.observacionesReembolso.trim() || undefined,
      this.authService.getEffectiveCompanyId() || undefined
    ).subscribe({
      next: (res: any) => {
        this.guardandoReembolso = false;
        this.cerrarModalReembolso();
        this.mostrarToast('exito', `Reembolso financiero liquidado exitosamente para la devolución.`);
        if (this.mostrarModalDetalle && this.devolucionDetalle?.id_devolucion === this.idDevolucionReembolso) {
          this.abrirDetalle(this.idDevolucionReembolso);
        }
        this.cargarDevoluciones(this.paginaActual);
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.guardandoReembolso = false;
        this.mostrarToast('error', err?.error?.detail || 'Error al liquidar el reembolso.');
        this.cdr.markForCheck();
      }
    });
  }

  // =========================================================================
  // HELPERS UI Y ESTILOS
  // =========================================================================

  mostrarToast(tipo: 'exito' | 'error' | 'info', texto: string): void {
    this.mensajeToast = { tipo, texto };
    this.cdr.markForCheck();
    setTimeout(() => {
      this.mensajeToast = null;
      this.cdr.markForCheck();
    }, 4500);
  }

  copiarCodigo(codigo: string): void {
    if (navigator?.clipboard) {
      navigator.clipboard.writeText(codigo).then(() => {
        this.mostrarToast('exito', `Código ${codigo} copiado al portapapeles.`);
      });
    }
  }

  getEstadoClase(estado: string): string {
    switch (estado?.toUpperCase()) {
      case 'SOLICITADA':
        return 'bg-blue-500/15 text-blue-700 dark:text-blue-300 border-blue-500/30';
      case 'EN_REVISION':
        return 'bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30';
      case 'APROBADA':
        return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30';
      case 'RECHAZADA':
        return 'bg-rose-500/15 text-rose-700 dark:text-rose-300 border-rose-500/30';
      case 'RECIBIDA':
        return 'bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 border-indigo-500/30';
      case 'PENDIENTE_REEMBOLSO':
        return 'bg-cyan-500/15 text-cyan-700 dark:text-cyan-300 border-cyan-500/30';
      case 'COMPLETADA':
        return 'bg-teal-500/15 text-teal-700 dark:text-teal-300 border-teal-500/30';
      case 'CANCELADA':
        return 'bg-zinc-500/15 text-zinc-700 dark:text-zinc-300 border-zinc-500/30';
      default:
        return 'bg-zinc-500/15 text-zinc-700 dark:text-zinc-300 border-zinc-500/30';
    }
  }

  getEstadoLabel(estado: string): string {
    switch (estado?.toUpperCase()) {
      case 'SOLICITADA': return 'Solicitada (Cliente)';
      case 'EN_REVISION': return 'En Revisión Técnica';
      case 'APROBADA': return 'Aprobada / Pendiente Recepción';
      case 'RECHAZADA': return 'Rechazada ✕';
      case 'RECIBIDA': return 'Prendas Recibidas en Tienda';
      case 'PENDIENTE_REEMBOLSO': return 'Pendiente Liquidar Reembolso';
      case 'COMPLETADA': return 'Completada / Reembolsada ✓';
      case 'CANCELADA': return 'Cancelada';
      default: return estado || 'En Proceso';
    }
  }
}
