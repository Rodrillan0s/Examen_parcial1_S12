import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EscrowService, FondoRetenido, ResumenUsuarioFondos } from '../../services/escrow';
import { AuthService } from '../../services/auth';
import { EmergenciasService, Emergencia } from '../../services/emergencias';

@Component({
  selector: 'app-dinero-retenido',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dinero-retenido.html'
})
export class DineroRetenidoComponent implements OnInit {
  private escrowService = inject(EscrowService);
  private authService = inject(AuthService);
  private emergenciasService = inject(EmergenciasService);

  fondosLiberadosSimulados: number[] = []
  usuariosLiberadosSimulados: number[] = []
  montoLiberadoSimulado = 0
  cargando = false;
  cargandoEmergencias = false;
  procesando = false;

  alerta: string | null = null;
  tipoAlerta: 'ok' | 'error' = 'ok';

  totalRetenido = 0;
  fondos: FondoRetenido[] = [];
  resumenUsuarios: ResumenUsuarioFondos[] = [];

  emergencias: Emergencia[] = [];
  emergenciaSeleccionada: Emergencia | null = null;

  formRetencion = {
    nro_emergencia: null as number | null,
    monto: null as number | null
  };

  ngOnInit() {
    this.cargarDatos();
    this.cargarEmergencias();
  }

  cargarDatos() {
    if (this.esAdmin()) {
      this.cargarResumenUsuarios();
    } else {
      this.cargarMisFondos();
    }
  }

  liberarFondoSimulado(fondo: FondoRetenido) {
    if (this.fondosLiberadosSimulados.includes(fondo.id_custodia)) {
      return
    }

    this.fondosLiberadosSimulados.push(fondo.id_custodia)
    this.montoLiberadoSimulado += Number(fondo.monto_retenido || 0)

    this.fondos = this.fondos.map(f => {
      if (f.id_custodia === fondo.id_custodia) {
        return {
          ...f,
          estado_custodia: 'LIBERADO_SIMULADO'
        }
      }

      return f
    })

    this.totalRetenido = Math.max(
      0,
      this.totalRetenido - Number(fondo.monto_retenido || 0)
    )

    this.mostrarAlerta('Fondos liberados de forma simulada.', 'ok')
  }

  liberarFondosUsuarioSimulado(usuario: ResumenUsuarioFondos) {
    if (this.usuariosLiberadosSimulados.includes(usuario.nro_usuario)) {
      return
    }

    const monto = Number(usuario.total_retenido || 0)

    this.usuariosLiberadosSimulados.push(usuario.nro_usuario)
    this.montoLiberadoSimulado += monto

    this.resumenUsuarios = this.resumenUsuarios.map(u => {
      if (u.nro_usuario === usuario.nro_usuario) {
        return {
          ...u,
          total_retenido: 0
        }
      }

      return u
    })

    this.totalRetenido = Math.max(0, this.totalRetenido - monto)

    this.mostrarAlerta('Fondos del usuario liberados de forma simulada.', 'ok')
  }

  estaFondoLiberado(idCustodia: number): boolean {
    return this.fondosLiberadosSimulados.includes(idCustodia)
  }

  estaUsuarioLiberado(nroUsuario: number): boolean {
    return this.usuariosLiberadosSimulados.includes(nroUsuario)
  }
  
  cargarEmergencias() {
    this.cargandoEmergencias = true;

    const peticion = this.esAdmin()
      ? this.emergenciasService.obtenerTodasLasEmergencias()
      : this.emergenciasService.obtenerMisEmergencias();

    peticion.subscribe({
      next: (res) => {
        this.emergencias = res.data || [];
        this.cargandoEmergencias = false;
      },
      error: (err) => {
        this.mostrarAlerta(err.error?.detail || 'No se pudieron cargar las emergencias.', 'error');
        this.cargandoEmergencias = false;
      }
    });
  }

  seleccionarEmergencia() {
    const id = Number(this.formRetencion.nro_emergencia);

    this.emergenciaSeleccionada = this.emergencias.find(
      e => e.nro_emergencia === id
    ) || null;
  }

  cargarMisFondos() {
    this.cargando = true;

    this.escrowService.obtenerMisFondos().subscribe({
      next: (res) => {
        this.totalRetenido = Number(res.data?.total_retenido || 0);
        this.fondos = res.data?.fondos || [];
        this.cargando = false;
      },
      error: (err) => {
        this.mostrarAlerta(err.error?.detail || 'No se pudieron cargar los fondos retenidos.', 'error');
        this.cargando = false;
      }
    });
  }

  cargarResumenUsuarios() {
    this.cargando = true;

    this.escrowService.obtenerResumenUsuarios().subscribe({
      next: (res) => {
        this.resumenUsuarios = res.data || [];
        this.totalRetenido = this.resumenUsuarios.reduce(
          (total, item) => total + Number(item.total_retenido || 0),
          0
        );
        this.cargando = false;
      },
      error: (err) => {
        this.mostrarAlerta(err.error?.detail || 'No se pudo cargar el resumen de usuarios.', 'error');
        this.cargando = false;
      }
    });
  }

  retenerDinero() {
    if (!this.formRetencion.nro_emergencia) {
      this.mostrarAlerta('Selecciona una emergencia.', 'error');
      return;
    }

    if (!this.formRetencion.monto || this.formRetencion.monto <= 0) {
      this.mostrarAlerta('Ingresa un monto mayor a 0.', 'error');
      return;
    }

    this.procesando = true;

    this.escrowService.retenerDinero({
      nro_emergencia: this.formRetencion.nro_emergencia,
      monto: this.formRetencion.monto
    }).subscribe({
      next: (res) => {
        this.mostrarAlerta(res.message || 'Dinero retenido correctamente.', 'ok');
        this.formRetencion = { nro_emergencia: null, monto: null };
        this.emergenciaSeleccionada = null;
        this.procesando = false;
        this.cargarDatos();
      },
      error: (err) => {
        this.mostrarAlerta(err.error?.detail || 'No se pudo retener el dinero.', 'error');
        this.procesando = false;
      }
    });
  }

  esAdmin(): boolean {
    return this.authService.obtenerUsuario()?.nombre_rol?.toUpperCase() === 'ADMINISTRADOR';
  }

  formatearMonto(monto: number | null | undefined): string {
    return Number(monto || 0).toFixed(2);
  }

  private mostrarAlerta(texto: string, tipo: 'ok' | 'error') {
    this.alerta = texto;
    this.tipoAlerta = tipo;
  }
}