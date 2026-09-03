import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BitacoraService, BitacoraEvent } from '../../../services/bitacora';


@Component({
  selector: 'app-lista-bitacora',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './lista-bitacora.html',
  styleUrls: ['./lista-bitacora.css'],
  providers: [DatePipe]
})
export class ListaBitacoraComponent implements OnInit {
  eventos: BitacoraEvent[] = [];
  cargando: boolean = false;
  
  // Paginación
  page: number = 1;
  limit: number = 25;
  total: number = 0;
  pages: number = 0;
  Math = Math;

  // Filtros
  filtros: any = {
    modulo: '',
    accion: '',
    nivel: '',
    fecha_desde: '',
    fecha_hasta: '',
    search: ''
  };

  // Modal Detalles
  eventoSeleccionado: BitacoraEvent | null = null;
  cargandoDetalle: boolean = false;

  constructor(
    private bitacoraService: BitacoraService,
    private datePipe: DatePipe
  ) {}

  ngOnInit(): void {
    this.cargarEventos();
  }

  cargarEventos(): void {
    this.cargando = true;
    this.bitacoraService.obtenerEventos(this.filtros, this.page, this.limit).subscribe({
      next: (res) => {
        if (res.success) {
          this.eventos = res.data;
          this.total = res.total;
          this.pages = res.pages;
        }
        this.cargando = false;
      },
      error: (err) => {
        alert('Error al cargar la bitácora');
        this.cargando = false;
      }
    });
  }

  aplicarFiltros(): void {
    this.page = 1;
    this.cargarEventos();
  }

  limpiarFiltros(): void {
    this.filtros = {
      modulo: '',
      accion: '',
      nivel: '',
      fecha_desde: '',
      fecha_hasta: '',
      search: ''
    };
    this.page = 1;
    this.cargarEventos();
  }

  cambiarPagina(nuevaPagina: number): void {
    if (nuevaPagina >= 1 && nuevaPagina <= this.pages) {
      this.page = nuevaPagina;
      this.cargarEventos();
    }
  }

  verDetalles(evento: BitacoraEvent): void {
    this.eventoSeleccionado = evento;
    this.cargandoDetalle = true;
    
    // We could use the local event, but to show getting full details from backend:
    this.bitacoraService.obtenerDetalleEvento(evento.id_bitacora).subscribe({
      next: (res) => {
        if (res.success) {
          this.eventoSeleccionado = res.data;
        }
        this.cargandoDetalle = false;
      },
      error: (err) => {
        alert('Error al cargar los detalles del evento');
        this.cargandoDetalle = false;
      }
    });
  }

  cerrarModal(): void {
    this.eventoSeleccionado = null;
  }
  
  getNivelBadgeClass(nivel: string): string {
    switch (nivel) {
      case 'INFO': return 'badge-info bg-blue-100 text-blue-800 border border-blue-200';
      case 'WARNING': return 'badge-warning bg-yellow-100 text-yellow-800 border border-yellow-200';
      case 'CRITICAL': return 'badge-critical bg-red-100 text-red-800 border border-red-200';
      case 'ERROR': return 'badge-error bg-red-100 text-red-800 border border-red-200';
      default: return 'bg-gray-100 text-gray-800 border border-gray-200';
    }
  }
  
  formatearJSON(obj: any): string {
    if (!obj) return 'Ninguno';
    return JSON.stringify(obj, null, 2);
  }
}
