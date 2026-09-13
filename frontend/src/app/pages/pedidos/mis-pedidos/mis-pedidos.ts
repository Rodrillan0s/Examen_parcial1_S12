import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { PedidoService, PedidoResumen, PedidoData, PedidoFiltros } from '../../../services/pedido';
import { AuthService } from '../../../services/auth';
import { ThemeService } from '../../../services/theme';

@Component({
  selector: 'app-mis-pedidos',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './mis-pedidos.html',
  styleUrls: ['./mis-pedidos.css']
})
export class MisPedidosComponent implements OnInit {
  private pedidoService = inject(PedidoService);
  public authService = inject(AuthService);
  public themeService = inject(ThemeService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  // Listado y Paginación
  pedidos: PedidoResumen[] = [];
  total: number = 0;
  paginaActual: number = 1;
  limitePorPagina: number = 10;
  totalPaginas: number = 1;
  cargando: boolean = true;
  opcionesLimite: number[] = [5, 10, 20, 50];

  // Filtros
  filtroEstado: string = 'TODOS';
  filtroEstadoPago: string = 'TODOS';
  filtroFechaInicio: string = '';
  filtroFechaFin: string = '';
  filtroCodigo: string = '';

  // Modal de Detalle
  pedidoDetalle: PedidoData | null = null;
  mostrarModalDetalle: boolean = false;
  cargandoDetalle: boolean = false;

  // Preparación Futura Pasarela W27/W28
  mostrarModalPagoFuturo: boolean = false;
  pedidoParaPago: PedidoData | null = null;

  // Toast Feedback
  mensajeToast: { tipo: 'exito' | 'error' | 'info'; texto: string } | null = null;
  copiadoExitoso: boolean = false;

  ngOnInit(): void {
    if (!this.authService.estaAutenticado()) {
      this.router.navigate(['/catalogo']);
      return;
    }
    this.cargarPedidos(1);
  }

  cargarPedidos(pagina: number = 1): void {
    this.paginaActual = pagina;
    this.cargando = true;
    this.cdr.markForCheck();

    const filtros: PedidoFiltros = {
      page: this.paginaActual,
      limit: this.limitePorPagina,
      estado: this.filtroEstado !== 'TODOS' ? this.filtroEstado : undefined,
      estado_pago: this.filtroEstadoPago !== 'TODOS' ? this.filtroEstadoPago : undefined,
      fecha_inicio: this.filtroFechaInicio || undefined,
      fecha_fin: this.filtroFechaFin || undefined,
      codigo: this.filtroCodigo.trim() || undefined
    };

    this.pedidoService.obtenerMisPedidos(filtros).subscribe({
      next: (res) => {
        this.pedidos = res.data || [];
        this.total = res.total || 0;
        this.totalPaginas = res.total_paginas || 1;
        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.cargando = false;
        this.mostrarToast('error', err?.error?.detail || 'No fue posible cargar tu historial de pedidos.');
        this.cdr.markForCheck();
      }
    });
  }

  aplicarFiltros(): void {
    this.cargarPedidos(1);
  }

  limpiarFiltros(): void {
    this.filtroEstado = 'TODOS';
    this.filtroEstadoPago = 'TODOS';
    this.filtroFechaInicio = '';
    this.filtroFechaFin = '';
    this.filtroCodigo = '';
    this.cargarPedidos(1);
  }

  cambiarLimite(nuevoLimite: any): void {
    this.limitePorPagina = Number(nuevoLimite);
    this.cargarPedidos(1);
  }

  abrirDetalle(idPedido: number): void {
    this.cargandoDetalle = true;
    this.mostrarModalDetalle = true;
    this.pedidoDetalle = null;
    this.cdr.markForCheck();

    this.pedidoService.obtenerPedido(idPedido).subscribe({
      next: (res) => {
        this.pedidoDetalle = res.data;
        this.cargandoDetalle = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.cargandoDetalle = false;
        this.mostrarModalDetalle = false;
        this.mostrarToast('error', err?.error?.detail || 'No se pudo cargar el detalle del pedido.');
        this.cdr.markForCheck();
      }
    });
  }

  cerrarDetalle(): void {
    this.mostrarModalDetalle = false;
    this.pedidoDetalle = null;
    this.cdr.markForCheck();
  }

  abrirModalPagoFuturo(pedido: PedidoData): void {
    this.pedidoParaPago = pedido;
    this.mostrarModalPagoFuturo = true;
    this.cdr.markForCheck();
  }

  cerrarModalPagoFuturo(): void {
    this.mostrarModalPagoFuturo = false;
    this.pedidoParaPago = null;
    this.cdr.markForCheck();
  }

  copiarCodigo(codigo: string): void {
    if (navigator?.clipboard) {
      navigator.clipboard.writeText(codigo).then(() => {
        this.copiadoExitoso = true;
        this.mostrarToast('exito', `Código ${codigo} copiado al portapapeles.`);
        this.cdr.markForCheck();
        setTimeout(() => {
          this.copiadoExitoso = false;
          this.cdr.markForCheck();
        }, 2500);
      });
    }
  }

  mostrarToast(tipo: 'exito' | 'error' | 'info', texto: string): void {
    this.mensajeToast = { tipo, texto };
    this.cdr.markForCheck();
    setTimeout(() => {
      this.mensajeToast = null;
      this.cdr.markForCheck();
    }, 4000);
  }

  // --- Helpers de Estilo para Estados ---
  getEstadoClase(estado: string): string {
    switch (estado?.toUpperCase()) {
      case 'PENDIENTE_PAGO':
        return 'bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30';
      case 'CONFIRMADO':
      case 'APROBADO':
        return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30';
      case 'EN_PREPARACION':
        return 'bg-blue-500/15 text-blue-700 dark:text-blue-300 border-blue-500/30';
      case 'ENVIADO':
        return 'bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 border-indigo-500/30';
      case 'ENTREGADO':
        return 'bg-teal-500/15 text-teal-700 dark:text-teal-300 border-teal-500/30';
      case 'CANCELADO':
        return 'bg-rose-500/15 text-rose-700 dark:text-rose-300 border-rose-500/30';
      default:
        return 'bg-zinc-500/15 text-zinc-700 dark:text-zinc-300 border-zinc-500/30';
    }
  }

  getEstadoLabel(estado: string): string {
    switch (estado?.toUpperCase()) {
      case 'PENDIENTE_PAGO': return 'Pendiente de Pago';
      case 'CONFIRMADO': return 'Confirmado';
      case 'APROBADO': return 'Aprobado';
      case 'EN_PREPARACION': return 'En Preparación';
      case 'ENVIADO': return 'Enviado';
      case 'ENTREGADO': return 'Entregado';
      case 'CANCELADO': return 'Cancelado';
      default: return estado || 'Registrado';
    }
  }

  getEstadoPagoClase(estadoPago: string): string {
    switch (estadoPago?.toUpperCase()) {
      case 'PAGADO':
        return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30';
      case 'PENDIENTE':
        return 'bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30';
      case 'RECHAZADO':
      case 'CANCELADO':
        return 'bg-rose-500/15 text-rose-700 dark:text-rose-400 border-rose-500/30';
      default:
        return 'bg-zinc-500/15 text-zinc-700 dark:text-zinc-400 border-zinc-500/30';
    }
  }

  getEstadoPagoLabel(estadoPago: string): string {
    switch (estadoPago?.toUpperCase()) {
      case 'PAGADO': return 'Pagado ✓';
      case 'PENDIENTE': return 'Pago Pendiente';
      case 'RECHAZADO': return 'Pago Rechazado';
      case 'CANCELADO': return 'Anulado';
      default: return estadoPago || 'Pendiente';
    }
  }
}
