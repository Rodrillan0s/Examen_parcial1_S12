import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
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
  private bitacoraService = inject(BitacoraService);
  private cdr = inject(ChangeDetectorRef);

  eventos: BitacoraEvent[] = [];
  cargando: boolean = false;
  cargandoMas: boolean = false;
  
  // Paginación rápida (por defecto 10 registros para máxima velocidad de respuesta)
  page: number = 1;
  limit: number = 10;
  total: number = 0;
  pages: number = 0;
  Math = Math;

  // Filtros
  filtros = {
    modulo: '',
    accion: '',
    nivel: '',
    resultado: '',
    fecha_desde: '',
    fecha_hasta: '',
    search: ''
  };

  // Modal Detalles
  eventoSeleccionado: BitacoraEvent | null = null;
  cargandoDetalle: boolean = false;
  copiadoExitoso: boolean = false;

  ngOnInit(): void {
    this.cargarEventos();
  }

  cargarEventos(acumular: boolean = false): void {
    if (acumular) {
      this.cargandoMas = true;
    } else {
      this.cargando = true;
    }
    this.cdr.detectChanges();

    this.bitacoraService.obtenerEventos(this.filtros, this.page, this.limit).subscribe({
      next: (res) => {
        if (res && res.success) {
          if (acumular) {
            this.eventos = [...this.eventos, ...(res.data || [])];
          } else {
            this.eventos = res.data || [];
          }
          this.total = res.total || 0;
          this.pages = res.pages || 1;
        }
        this.cargando = false;
        this.cargandoMas = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando bitácora:', err);
        this.cargando = false;
        this.cargandoMas = false;
        this.cdr.detectChanges();
      }
    });
  }

  aplicarFiltros(): void {
    this.page = 1;
    this.cargarEventos(false);
  }

  limpiarFiltros(): void {
    this.filtros = {
      modulo: '',
      accion: '',
      nivel: '',
      resultado: '',
      fecha_desde: '',
      fecha_hasta: '',
      search: ''
    };
    this.page = 1;
    this.cargarEventos(false);
  }

  cambiarPagina(nuevaPagina: number): void {
    if (nuevaPagina >= 1 && nuevaPagina <= this.pages && nuevaPagina !== this.page) {
      this.page = nuevaPagina;
      this.cargarEventos(false);
    }
  }

  paginaSiguiente(): void {
    if (this.page < this.pages) {
      this.page++;
      this.cargarEventos(false);
    }
  }

  paginaAnterior(): void {
    if (this.page > 1) {
      this.page--;
      this.cargarEventos(false);
    }
  }

  cargarMasRegistros(): void {
    if (this.page < this.pages) {
      this.page++;
      this.cargarEventos(true);
    }
  }

  cambiarLimite(nuevoLimite: number): void {
    this.limit = nuevoLimite;
    this.page = 1;
    this.cargarEventos(false);
  }

  verDetalles(evento: BitacoraEvent): void {
    this.eventoSeleccionado = evento;
    this.cargandoDetalle = true;
    this.copiadoExitoso = false;
    this.cdr.detectChanges();
    
    this.bitacoraService.obtenerDetalleEvento(evento.id_bitacora).subscribe({
      next: (res) => {
        if (res && res.success) {
          this.eventoSeleccionado = res.data;
        }
        this.cargandoDetalle = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar los detalles del evento:', err);
        this.cargandoDetalle = false;
        this.cdr.detectChanges();
      }
    });
  }

  cerrarModal(): void {
    this.eventoSeleccionado = null;
    this.cargandoDetalle = false;
    this.copiadoExitoso = false;
  }

  copiarJSON(objeto: any): void {
    if (!objeto) return;
    const texto = JSON.stringify(objeto, null, 2);
    navigator.clipboard.writeText(texto).then(() => {
      this.copiadoExitoso = true;
      this.cdr.detectChanges();
      setTimeout(() => {
        this.copiadoExitoso = false;
        this.cdr.detectChanges();
      }, 2500);
    });
  }

  getNivelBadgeClass(nivel: string): string {
    switch ((nivel || '').toUpperCase()) {
      case 'INFO':
        return 'bg-sky-500/10 text-sky-400 border-sky-500/30';
      case 'WARNING':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'CRITICAL':
      case 'ERROR':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      default:
        return 'bg-zinc-800 text-zinc-400 border-zinc-700';
    }
  }

  getNivelDotClass(nivel: string): string {
    switch ((nivel || '').toUpperCase()) {
      case 'INFO': return 'bg-sky-400 shadow-[0_0_8px_rgba(56,189,248,0.6)]';
      case 'WARNING': return 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]';
      case 'CRITICAL':
      case 'ERROR': return 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]';
      default: return 'bg-zinc-400';
    }
  }

  getModuloIcon(modulo: string): string {
    switch ((modulo || '').toUpperCase()) {
      case 'AUTENTICACION': return 'ph ph-shield-key';
      case 'PERFIL': return 'ph ph-user-circle-gear';
      case 'USUARIOS': return 'ph ph-users-three';
      case 'ROLES': return 'ph ph-key';
      case 'PRODUCTOS': return 'ph ph-t-shirt';
      case 'COMPRAS': return 'ph ph-receipt';
      case 'INVENTARIO': return 'ph ph-package';
      case 'SUCURSALES': return 'ph ph-storefront';
      case 'EMPRESAS': return 'ph ph-buildings';
      default: return 'ph ph-terminal-window';
    }
  }

  formatearJSON(obj: any): string {
    if (!obj || (typeof obj === 'object' && Object.keys(obj).length === 0)) {
      return 'Sin registros o sin cambios';
    }
    return JSON.stringify(obj, null, 2);
  }
}
