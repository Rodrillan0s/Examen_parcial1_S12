import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MantenimientoService, ClienteCrm } from '../../services/mantenimiento';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-mantenimiento-crm',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './mantenimiento-crm.html'
})
export class MantenimientoCrmComponent implements OnInit {
  private crmService = inject(MantenimientoService);
  private authService = inject(AuthService);

  clientes: ClienteCrm[] = [];
  clientesFiltrados: ClienteCrm[] = [];
  clientesSeleccionados: number[] = [];

  busqueda = '';
  asunto = '';
  mensaje = '';

  cargando = false;
  procesando = false;
  alerta: string | null = null;
  tipoAlerta: 'ok' | 'error' = 'ok';

  ngOnInit() {
    this.cargarClientes();
  }

  cargarClientes() {
    this.cargando = true;

    this.crmService.obtenerClientesCrm().subscribe({
      next: (res) => {
        this.clientes = res.data || [];
        this.clientesFiltrados = [...this.clientes];
        this.cargando = false;
      },
      error: (err) => {
        this.mostrarAlerta(err.error?.detail || 'No se pudieron cargar los clientes.', 'error');
        this.cargando = false;
      }
    });
  }

  filtrarClientes() {
    const texto = this.busqueda.trim().toLowerCase();

    if (!texto) {
      this.clientesFiltrados = [...this.clientes];
      return;
    }

    this.clientesFiltrados = this.clientes.filter(c => {
      const nombreCompleto = `${c.nombre || ''} ${c.apellido || ''}`.toLowerCase();
      const telefono = `${c.telefono || ''}`.toLowerCase();
      const username = `${c.username || ''}`.toLowerCase();

      return nombreCompleto.includes(texto) || telefono.includes(texto) || username.includes(texto);
    });
  }

  toggleCliente(nroUsuario: number) {
    if (this.estaSeleccionado(nroUsuario)) {
      this.clientesSeleccionados = this.clientesSeleccionados.filter(id => id !== nroUsuario);
    } else {
      this.clientesSeleccionados.push(nroUsuario);
    }
  }

  estaSeleccionado(nroUsuario: number): boolean {
    return this.clientesSeleccionados.includes(nroUsuario);
  }

  seleccionarTodosFiltrados() {
    const idsFiltrados = this.clientesFiltrados.map(c => c.nro_usuario);
    const todosSeleccionados = idsFiltrados.every(id => this.clientesSeleccionados.includes(id));

    if (todosSeleccionados) {
      this.clientesSeleccionados = this.clientesSeleccionados.filter(id => !idsFiltrados.includes(id));
    } else {
      const nuevos = idsFiltrados.filter(id => !this.clientesSeleccionados.includes(id));
      this.clientesSeleccionados = [...this.clientesSeleccionados, ...nuevos];
    }
  }

  enviarNotificacion() {
    if (this.clientesSeleccionados.length === 0) {
      this.mostrarAlerta('Selecciona al menos un cliente.', 'error');
      return;
    }

    if (!this.asunto.trim()) {
      this.mostrarAlerta('Escribe un asunto.', 'error');
      return;
    }

    if (!this.mensaje.trim()) {
      this.mostrarAlerta('Escribe el mensaje.', 'error');
      return;
    }

    this.procesando = true;

    const payload = {
      clientes: this.clientesSeleccionados,
      asunto: this.asunto.trim(),
      mensaje: this.mensaje.trim(),
      canal: 'WEBSOCKET'
    };

    this.crmService.enviarNotificacionCrm(payload).subscribe({
      next: (res) => {
        this.mostrarAlerta(res.message || 'Notificación enviada correctamente.', 'ok');
        this.asunto = '';
        this.mensaje = '';
        this.clientesSeleccionados = [];
        this.procesando = false;
      },
      error: (err) => {
        this.mostrarAlerta(err.error?.detail || 'Error al enviar la notificación.', 'error');
        this.procesando = false;
      }
    });
  }

  limpiarSeleccion() {
    this.clientesSeleccionados = [];
  }

  puedeUsarCrm(): boolean {
    const rol = this.authService.obtenerUsuario()?.nombre_rol?.toUpperCase();
    return ['ADMINISTRADOR', 'GERENTE TALLER', 'MECANICO', 'MECÁNICO'].includes(rol);
  }

  private mostrarAlerta(texto: string, tipo: 'ok' | 'error') {
    this.alerta = texto;
    this.tipoAlerta = tipo;
  }
}