import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { TalleresService } from '../../services/talleres';

@Component({
  selector: 'app-servicios-taller',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './servicios-taller.html'
})
export class ServiciosTallerComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private talleresService = inject(TalleresService);
  private cdr = inject(ChangeDetectorRef);

  nroTaller: number = 0;
  servicios: any[] = [];
  cargando = true;
  mensajeError = '';
  procesando = false;

  mostrarModal = false;
  modoEdicion = false;
  
  // Lista predefinida
  serviciosPredefinidos: string[] = [
    'AUXILIO MECANICO BASICO',
    'SERVICIO DE GRUA',
    'CAMBIO O CARGA DE BATERIA',
    'CAMBIO DE LLANTAS',
    'SUMINISTRO DE COMBUSTIBLE',
    'CERRAJERIA AUTOMOTRIZ',
    'REVISION ELECTRICA',
    'MANTENIMIENTO PREVENTIVO',
    'OTROS'
  ];

  servicioSeleccionado: string = '';
  nombrePersonalizado: string = '';

  servicioForm = {
    nro_servicio: 0,
    descripcion: ''
  };

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.nroTaller = Number(id);
        this.cargarServicios();
      } else {
        this.mensajeError = "No se especificó un taller válido.";
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  cargarServicios() {
    this.cargando = true;
    this.mensajeError = '';
    this.cdr.detectChanges();
    
    this.talleresService.obtenerServiciosTaller(this.nroTaller).subscribe({
      next: (res) => {
        if (res.success) {
          this.servicios = res.data;
        }
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.mensajeError = 'Error al cargar los servicios del taller.';
        this.cargando = false;
        this.cdr.detectChanges();
        console.error(err);
      }
    });
  }

  abrirModalNuevo() {
    this.modoEdicion = false;
    this.servicioForm = { nro_servicio: 0, descripcion: '' };
    this.servicioSeleccionado = '';
    this.nombrePersonalizado = '';
    this.mostrarModal = true;
    this.cdr.detectChanges();
  }

  abrirModalEdicion(servicio: any) {
    this.modoEdicion = true;
    this.servicioForm = {
      nro_servicio: servicio.nro_servicio,
      descripcion: servicio.descripcion
    };

    // Evaluamos si el nombre existe en nuestra lista predefinida
    if (this.serviciosPredefinidos.includes(servicio.nombre_servicio)) {
      this.servicioSeleccionado = servicio.nombre_servicio;
      this.nombrePersonalizado = '';
    } else {
      // Si el nombre no está en la lista, marcamos "OTROS" y llenamos el input personalizado
      this.servicioSeleccionado = 'OTROS';
      this.nombrePersonalizado = servicio.nombre_servicio;
    }

    this.mostrarModal = true;
    this.cdr.detectChanges();
  }

  cerrarModal() {
    this.mostrarModal = false;
    this.procesando = false;
    this.cdr.detectChanges();
  }

  guardarServicio() {
    // Definimos cuál será el nombre final a enviar al backend
    const nombreFinal = this.servicioSeleccionado === 'OTROS' 
      ? this.nombrePersonalizado.trim() 
      : this.servicioSeleccionado;

    if (!nombreFinal) {
      alert('Debe especificar un nombre para el servicio.');
      return;
    }

    this.procesando = true;
    this.cdr.detectChanges();

    const datos = {
      nombre_servicio: nombreFinal,
      descripcion: this.servicioForm.descripcion
    };

    const peticion = this.modoEdicion
      ? this.talleresService.actualizarServicioTaller(this.nroTaller, this.servicioForm.nro_servicio, datos)
      : this.talleresService.crearServicioTaller(this.nroTaller, datos);

    peticion.subscribe({
      next: () => {
        this.cerrarModal();
        this.cargarServicios();
      },
      error: (err) => {
        alert(err.error?.detail || 'Error al guardar el servicio');
        this.procesando = false;
        this.cdr.detectChanges();
      }
    });
  }

  eliminarServicio(nro_servicio: number) {
    if (confirm('¿Seguro que deseas eliminar este servicio del catálogo operativo?')) {
      this.talleresService.eliminarServicioTaller(this.nroTaller, nro_servicio).subscribe({
        next: () => this.cargarServicios(),
        error: (err) => alert(err.error?.detail || 'Error al eliminar el servicio')
      });
    }
  }
}