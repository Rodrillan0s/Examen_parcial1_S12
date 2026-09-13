import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { CarritoService, CarritoData, ItemCarrito } from '../../services/carrito';
import { AuthService } from '../../services/auth';
import { PerfilService } from '../../services/perfil';
import { PedidoService, SucursalCheckout, CrearPedidoPayload } from '../../services/pedido';

@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './checkout.html'
})
export class CheckoutComponent implements OnInit {
  public carritoService = inject(CarritoService);
  public authService = inject(AuthService);
  private perfilService = inject(PerfilService);
  private pedidoService = inject(PedidoService);
  private router = inject(Router);

  // Datos del carrito
  carrito: CarritoData | null = null;
  cargandoCarrito: boolean = true;

  // Sucursales del Tenant
  sucursales: SucursalCheckout[] = [];
  sucursalSeleccionadaId: number | null = null;
  cargandoSucursales: boolean = false;

  // Modalidad de compra
  modalidadCompra: 'RETIRO_SUCURSAL' | 'ENTREGA_DOMICILIO' = 'RETIRO_SUCURSAL';

  // Datos de contacto del cliente
  nombreContacto: string = '';
  telefonoContacto: string = '';
  correoContacto: string = '';
  direccionEntrega: string = '';
  ciudadEntrega: string = 'Santa Cruz';
  notasEntrega: string = '';

  // Estados de proceso y feedback
  procesando: boolean = false;
  errorMensaje: string | null = null;

  ngOnInit(): void {
    if (!this.authService.estaAutenticado()) {
      this.router.navigate(['/catalogo']);
      this.authService.openAuthModal('login');
      return;
    }

    this.cargarDatosIniciales();
  }

  cargarDatosIniciales(): void {
    this.cargandoCarrito = true;
    this.cargandoSucursales = true;

    // 1. Cargar carrito activo
    this.carritoService.cargarCarrito().subscribe({
      next: (res) => {
        this.cargandoCarrito = false;
        if (res && res.success && res.data) {
          this.carrito = res.data;
          // Cargar sucursales del Tenant del carrito
          this.cargarSucursales(res.data.id_empresa);
        } else {
          this.carrito = null;
          this.cargandoSucursales = false;
        }
      },
      error: () => {
        this.cargandoCarrito = false;
        this.cargandoSucursales = false;
      }
    });

    // 2. Pre-cargar datos del cliente desde PerfilService
    this.perfilService.obtenerPerfil().subscribe({
      next: (res) => {
        if (res && res.success && res.data) {
          const p = res.data;
          this.nombreContacto = p.nombre_completo || `${p.nombre || ''} ${p.apellido || ''}`.trim();
          this.telefonoContacto = p.telefono || '';
          this.correoContacto = p.correo || '';
          if (p.direccion) this.direccionEntrega = p.direccion;
          if (p.ciudad) this.ciudadEntrega = p.ciudad;
        }
      },
      error: () => {
        // Fallback al usuario en AuthService
        const u = this.authService.currentUser();
        if (u) {
          this.nombreContacto = `${u.nombre || ''} ${u.apellido || ''}`.trim();
          this.correoContacto = u.correo || '';
        }
      }
    });
  }

  cargarSucursales(idEmpresa: number): void {
    this.pedidoService.obtenerSucursales(idEmpresa).subscribe({
      next: (res) => {
        this.sucursales = res.data || [];
        this.cargandoSucursales = false;
        if (this.sucursales.length > 0) {
          this.sucursalSeleccionadaId = this.sucursales[0].id_sucursal;
        }
      },
      error: () => {
        this.cargandoSucursales = false;
      }
    });
  }

  seleccionarSucursal(id: number): void {
    this.sucursalSeleccionadaId = id;
  }

  seleccionarModalidad(m: 'RETIRO_SUCURSAL' | 'ENTREGA_DOMICILIO'): void {
    this.modalidadCompra = m;
  }

  get sucursalSeleccionada(): SucursalCheckout | null {
    return this.sucursales.find(s => s.id_sucursal === this.sucursalSeleccionadaId) || null;
  }

  formularioValido(): boolean {
    if (!this.carrito || this.carrito.items.length === 0) return false;
    if (!this.sucursalSeleccionadaId) return false;
    if (!this.nombreContacto.trim()) return false;
    if (!this.telefonoContacto.trim()) return false;

    if (this.modalidadCompra === 'ENTREGA_DOMICILIO') {
      if (!this.direccionEntrega.trim() || !this.ciudadEntrega.trim()) return false;
    }

    return true;
  }

  confirmarPedido(): void {
    if (this.procesando) return;
    this.errorMensaje = null;

    if (!this.formularioValido()) {
      this.errorMensaje = 'Por favor completa todos los campos requeridos antes de confirmar.';
      return;
    }

    if (!this.carrito || this.carrito.items.length === 0) {
      this.errorMensaje = 'Tu bolsa de compras está vacía.';
      return;
    }

    this.procesando = true;

    const payload: CrearPedidoPayload = {
      id_sucursal: this.sucursalSeleccionadaId!,
      modalidad_compra: this.modalidadCompra,
      nombre_contacto: this.nombreContacto.trim(),
      telefono_contacto: this.telefonoContacto.trim(),
      correo_contacto: this.correoContacto.trim() || undefined,
      direccion_entrega: this.modalidadCompra === 'ENTREGA_DOMICILIO' ? this.direccionEntrega.trim() : undefined,
      ciudad_entrega: this.modalidadCompra === 'ENTREGA_DOMICILIO' ? this.ciudadEntrega.trim() : undefined,
      notas_entrega: this.notasEntrega.trim() || undefined,
      id_empresa: this.carrito.id_empresa
    };

    this.pedidoService.crearPedido(payload).subscribe({
      next: (res) => {
        this.procesando = false;
        if (res && res.success && res.data) {
          // Recargar el carrito para reflejar que quedó procesado
          this.carritoService.cargarCarrito().subscribe();
          // Navegar a la pantalla de pedido confirmado
          this.router.navigate(['/pedido-confirmado', res.data.id_pedido]);
        }
      },
      error: (err) => {
        this.procesando = false;
        this.errorMensaje = err?.error?.detail || 'Ocurrió un error al procesar tu pedido. Por favor intenta nuevamente.';
        // Si fue un problema de stock, recargar el carrito para sincronizar alertas
        this.carritoService.cargarCarrito().subscribe();
      }
    });
  }

  irAlCatalogo(): void {
    this.router.navigate(['/catalogo']);
  }
}
