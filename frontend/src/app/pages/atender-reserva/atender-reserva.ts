import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { AuthService } from '../../services/auth';
import { AtenderReservaService } from '../../services/atender-reserva';

@Component({
  selector: 'app-atender-reserva',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './atender-reserva.html',
  styleUrls: ['./atender-reserva.css']
})
export class AtenderReservaComponent implements OnInit {

  private authService = inject(AuthService);
  private atenderReservaService = inject(AtenderReservaService);
  private router = inject(Router);

  reservas: any[] = [];
  reservaSeleccionada: any = null;

  sucursalActiva: any = null;

  cargando = false;
  procesando = false;

  mensaje = '';
  error = '';

  ngOnInit(): void {
    this.sucursalActiva = this.authService.activeBranch();

    if (this.sucursalActiva?.id) {
      this.cargarReservas();
    }

    this.authService.branchChanged$.subscribe(sucursal => {
      this.sucursalActiva = sucursal;
      this.reservas = [];
      this.reservaSeleccionada = null;

      if (sucursal?.id) {
        this.cargarReservas();
      }
    });
  }

  cargarReservas(): void {
    if (!this.sucursalActiva?.id) {
      this.error = 'No hay una sucursal activa seleccionada.';
      return;
    }

    this.cargando = true;
    this.mensaje = '';
    this.error = '';

    this.atenderReservaService
      .listarReservas(this.sucursalActiva.id)
      .subscribe({
        next: (respuesta) => {
          this.cargando = false;

          if (!respuesta?.success) {
            this.error =
              respuesta?.message ||
              'No se pudieron cargar las reservas.';
            return;
          }

          this.reservas = respuesta.data || [];
        },
        error: (error) => {
          this.cargando = false;

          this.error =
            error?.error?.detail ||
            error?.error?.message ||
            'No se pudieron cargar las reservas.';
        }
      });
  }

  seleccionarReserva(reserva: any): void {
    this.reservaSeleccionada = reserva;
    this.mensaje = '';
    this.error = '';
  }

  atenderReserva(reserva: any): void {
    if (!reserva) {
      return;
    }

    if (!this.sucursalActiva?.id) {
      this.error = 'No hay una sucursal activa.';
      return;
    }

    this.mensaje = '';
    this.error = '';

    /*
     * Si la reserva no está pagada,
     * continúa el proceso mediante CU24 - POS.
     */
    if (!reserva.venta_pagada) {
      this.irAlPOS(reserva);
      return;
    }

    /*
     * Si ya está pagada,
     * CU25 la atiende directamente.
     */
    this.procesando = true;

    this.atenderReservaService
      .atenderReserva(
        reserva.id_reserva,
        this.sucursalActiva.id
      )
      .subscribe({
        next: (respuesta) => {
          this.procesando = false;

          if (!respuesta?.success) {
            this.error =
              respuesta?.message ||
              'No se pudo atender la reserva.';
            return;
          }

          this.mensaje =
            respuesta.message ||
            'Reserva atendida correctamente.';

          reserva.estado = 'ATENDIDA';

          if (reserva.prendas) {
            reserva.prendas.forEach((item: any) => {
              item.estado_prenda = 'ATENDIDA';
            });
          }

          this.reservaSeleccionada = null;

          this.cargarReservas();
        },
        error: (error) => {
          this.procesando = false;

          this.error =
            error?.error?.detail ||
            error?.error?.message ||
            'No se pudo atender la reserva.';
        }
      });
  }

  private irAlPOS(reserva: any): void {
    this.router.navigate(
      ['/admin/caja'],
      {
        state: {
          reserva: {
            id_reserva: reserva.id_reserva,
            codigo_reserva: reserva.codigo_reserva,
            id_sucursal: reserva.id_sucursal,
            id_cliente: reserva.id_cliente,
            cliente: reserva.cliente,
            items: reserva.prendas
          }
        }
      }
    );
  }

  limpiarSeleccion(): void {
    this.reservaSeleccionada = null;
    this.mensaje = '';
    this.error = '';
  }

  recargar(): void {
    this.cargarReservas();
  }
}