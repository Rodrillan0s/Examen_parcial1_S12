import { Component, OnInit, inject, ChangeDetectorRef, NgZone, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { EmergenciasService, Emergencia, DiagnosticoIAData } from '../../services/emergencias';
import { AuthService } from '../../services/auth';
import * as XLSX from 'xlsx';

@Component({
  selector: 'app-emergencias-historial',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './emergencias-historial.html'
})
export class EmergenciasHistorialComponent implements OnInit {
  private emergenciasService = inject(EmergenciasService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private platformId = inject(PLATFORM_ID);

  usuarioActual: any = null;
  emergencias: Emergencia[] = [];
  emergenciasFiltradas: Emergencia[] = [];
  
  cargando: boolean = false;
  mensajeError: string = '';
  textoBusqueda: string = '';
  filtroEstado: string = ''; 

  // Control de Modal: Cotización
  mostrarModalCotizacion: boolean = false;
  procesandoAccion: boolean = false;
  
  // Control de Modal: Detalles y Evidencias
  mostrarModalDetalles: boolean = false;
  cargandoEvidencias: boolean = false;
  evidenciasDetalle: any[] = [];
  
  emergenciaSeleccionada: Emergencia | null = null;

  // Control de Diagnóstico IA
  cargandoDiagnostico: boolean = false;
  diagnosticoIA: DiagnosticoIAData | null = null;
  mensajeErrorDiagnostico: string = '';

  // VARIABLES PARA CARGA DE EVIDENCIA (ADMIN)
  archivoSeleccionado: File | null = null;
  tipoArchivoSeleccionado: string = 'IMAGEN';
  subiendoEvidencia: boolean = false;

  modoCaptura: 'ARCHIVO' | 'CAMARA' | 'AUDIO' = 'ARCHIVO';
  
  // Cámara
  streamCamara: MediaStream | null = null;
  fotoCapturadaBase64: string | null = null; 
  fotoPreview: string | null = null; 
  
  // Audio
  mediaRecorder: any = null;
  audioChunks: any[] = [];
  grabandoAudio: boolean = false;
  audioCapturadoBase64: string | null = null; 
  audioPreviewUrl: string | null = null;
  
  cotizacionForm = {
    precio_estimado: null,
    tiempo_estimado_minutos: null
  };

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.usuarioActual = this.authService.obtenerUsuario();
      if (this.usuarioActual) {
        this.cargarEmergencias();
      }
    }
  }

  // --- NUEVO: MÉTODO DE REFRESCO ---
  refrescarEmergencias() {
    this.cargarEmergencias();
  }

  // --- ACTUALIZADO: CARGA CON ANTI-BLOQUEO ---
  cargarEmergencias() {
    setTimeout(() => {
      this.ngZone.run(() => {
        this.cargando = true;
        this.cdr.detectChanges(); // Forzar renderizado del loader
      });

      const rol = this.usuarioActual.nombre_rol.toUpperCase();
      let peticion$;

      if (rol === 'ADMINISTRADOR' || rol === 'GERENTE TALLER') {
        peticion$ = this.emergenciasService.obtenerTodasLasEmergencias();
      } else if (rol === 'CLIENTE') {
        peticion$ = this.emergenciasService.obtenerMisEmergencias();
      } else {
        peticion$ = this.emergenciasService.obtenerEmergenciasMiTaller();
      }

      peticion$.subscribe({
        next: (res) => {
          this.ngZone.run(() => {
            if (res.success) {
              this.emergencias = res.data;
              this.aplicarFiltros();
            }
            this.cargando = false;
            this.cdr.detectChanges();
          });
        },
        error: () => {
          this.ngZone.run(() => {
            this.mensajeError = 'Error al conectar con el centro de control.';
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    }, 0);
  }

  exportarAExcel() {
    const datosParaExportar = this.emergenciasFiltradas.map(e => ({
      'Nro. Emergencia': e.nro_emergencia,
      'Tipo': e.tipo_emergencia,
      'Estado': e.estado,
      'Prioridad': e.prioridad,
      'Fecha Inicio': e.fecha_inicio,
      'Cliente': e.nombre_usuario,
      'Placa Vehículo': e.vehiculo_placa || 'N/A',
      'Marca/Modelo': e.vehiculo_marca || 'N/A',
      'Taller Asignado': e.nombre_taller || 'Sin asignar'
    }));

    const worksheet: XLSX.WorkSheet = XLSX.utils.json_to_sheet(datosParaExportar);
    const workbook: XLSX.WorkBook = { Sheets: { 'Emergencias': worksheet }, SheetNames: ['Emergencias'] };
    XLSX.writeFile(workbook, `Reporte_Emergencias_${new Date().toISOString().slice(0, 10)}.xlsx`);
  }

  aplicarFiltros() {
    let filtradas = [...this.emergencias];
    if (this.filtroEstado) {
      filtradas = filtradas.filter(e => e.estado.toUpperCase() === this.filtroEstado.toUpperCase());
    }
    if (this.textoBusqueda) {
      const busqueda = this.textoBusqueda.toLowerCase();
      filtradas = filtradas.filter(e => 
        e.tipo_emergencia.toLowerCase().includes(busqueda) || 
        (e.nombre_usuario && e.nombre_usuario.toLowerCase().includes(busqueda))
      );
    }
    this.emergenciasFiltradas = filtradas;
  }

  setFiltroEstado(estado: string) {
    this.filtroEstado = estado;
    this.aplicarFiltros();
  }

  esTallerOMecanico(): boolean {
    if (!this.usuarioActual) return false;
    const rol = this.usuarioActual.nombre_rol.toUpperCase();
    return ['ADMINISTRADOR','GERENTE TALLER', 'MECANICO', 'MECÁNICO'].includes(rol);
  }

  generarDiagnosticoIA() {
    if (!this.emergenciaSeleccionada) {
      alert('No hay una emergencia seleccionada.');
      return;
    }

    this.cargandoDiagnostico = true;
    this.diagnosticoIA = null;
    this.mensajeErrorDiagnostico = '';

    this.emergenciasService.generarDiagnosticoIA(this.emergenciaSeleccionada.nro_emergencia).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            this.diagnosticoIA = res.data;
          } else {
            this.mensajeErrorDiagnostico = res.message || 'No se pudo generar el diagnóstico IA.';
          }
          this.cargandoDiagnostico = false;
          this.cdr.detectChanges();
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          this.mensajeErrorDiagnostico = err.error?.detail || 'La IA no logró analizar la emergencia en este momento.';
          this.cargandoDiagnostico = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  esAdministrador(): boolean {
    return this.usuarioActual?.nombre_rol?.toUpperCase() === 'ADMINISTRADOR';
  }

  abrirModalDetalles(emergencia: Emergencia) {
    this.emergenciaSeleccionada = emergencia;
    this.mostrarModalDetalles = true;
    this.cargandoEvidencias = true;
    this.evidenciasDetalle = [];
    this.archivoSeleccionado = null; 
    
    this.emergenciasService.obtenerEvidenciasEmergencia(emergencia.nro_emergencia).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) this.evidenciasDetalle = res.data;
          this.cargandoEvidencias = false;
          this.cdr.detectChanges();
        });
      },
      error: () => {
        this.ngZone.run(() => {
          this.cargandoEvidencias = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      this.archivoSeleccionado = file;
      this.tipoArchivoSeleccionado = file.type.startsWith('audio') ? 'AUDIO' : 'IMAGEN';
    }
  }

  subirEvidenciaAdicional() {
    let payloadBase64 = '';
    let tipoArchivo = 'IMAGEN';

    if (this.modoCaptura === 'ARCHIVO' && this.archivoSeleccionado) {
      const reader = new FileReader();
      reader.onload = () => {
        payloadBase64 = (reader.result as string).split(',')[1];
        this.ejecutarSubidaBackend(payloadBase64, this.tipoArchivoSeleccionado);
      };
      reader.readAsDataURL(this.archivoSeleccionado);
      return;
    } else if (this.modoCaptura === 'CAMARA' && this.fotoCapturadaBase64) {
      payloadBase64 = this.fotoCapturadaBase64;
      tipoArchivo = 'IMAGEN';
    } else if (this.modoCaptura === 'AUDIO' && this.audioCapturadoBase64) {
      payloadBase64 = this.audioCapturadoBase64;
      tipoArchivo = 'AUDIO';
    } else {
      return;
    }

    this.ejecutarSubidaBackend(payloadBase64, tipoArchivo);
  }

  private ejecutarSubidaBackend(base64Limpio: string, tipo: string) {
    this.subiendoEvidencia = true;
    const payload = {
      añadir_evidencias: [{ tipo_archivo: tipo, base64: base64Limpio }]
    };

    this.emergenciasService.actualizarEmergencia(this.emergenciaSeleccionada!.nro_emergencia, payload).subscribe({
      next: () => {
        this.ngZone.run(() => {
          alert('Evidencia adjuntada exitosamente.');
          this.subiendoEvidencia = false;
          this.setModoCaptura('ARCHIVO'); 
          this.abrirModalDetalles(this.emergenciaSeleccionada!); 
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          alert('Error: ' + (err.error?.detail || 'Error de servidor.'));
          this.subiendoEvidencia = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  cerrarModalDetalles() {
    this.mostrarModalDetalles = false;
    this.cargandoDiagnostico = false;
    this.diagnosticoIA = null;
    this.mensajeErrorDiagnostico = '';
    
    this.detenerCamara();
    if (this.grabandoAudio) this.detenerGrabacion();

    if (!this.mostrarModalCotizacion) {
      this.emergenciaSeleccionada = null;
    }
  }

  setModoCaptura(modo: 'ARCHIVO' | 'CAMARA' | 'AUDIO') {
    this.modoCaptura = modo;
    this.detenerCamara();
    if (this.grabandoAudio) this.detenerGrabacion();
    
    this.archivoSeleccionado = null;
    this.fotoCapturadaBase64 = null;
    this.fotoPreview = null;
    this.audioCapturadoBase64 = null;
    this.audioPreviewUrl = null;

    if (modo === 'CAMARA') this.activarCamara();
  }

  async activarCamara() {
    try {
      this.streamCamara = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      this.cdr.detectChanges(); 
      setTimeout(() => {
        const video = document.getElementById('videoElement') as HTMLVideoElement;
        if (video) {
          video.srcObject = this.streamCamara;
          video.play().catch(e => console.log('Error al reproducir video', e)); 
        } else {
          console.error('No se encontró el elemento de video en el DOM');
        }
      }, 50);
    } catch (err) {
      console.error('Error de cámara:', err);
      alert('Permiso denegado o no hay cámara disponible.');
      this.modoCaptura = 'ARCHIVO';
      this.cdr.detectChanges();
    }
  }

  capturarFoto() {
    const video = document.getElementById('videoElement') as HTMLVideoElement;
    if (!video) return;
    
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640; 
    canvas.height = video.videoHeight || 480;
    
    canvas.getContext('2d')?.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    this.fotoPreview = canvas.toDataURL('image/jpeg', 0.8); 
    this.fotoCapturadaBase64 = this.fotoPreview.split(',')[1];
    
    this.detenerCamara();
    this.cdr.detectChanges(); 
  }

  detenerCamara() {
    if (this.streamCamara) {
      this.streamCamara.getTracks().forEach(track => track.stop());
      this.streamCamara = null;
    }
  }

  async iniciarGrabacion() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // @ts-ignore
      this.mediaRecorder = new (window as any).MediaRecorder(stream);
      this.audioChunks = [];
      this.grabandoAudio = true;
      this.cdr.detectChanges();

      this.mediaRecorder.ondataavailable = (e: any) => {
        if (e.data && e.data.size > 0) {
          this.audioChunks.push(e.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/mp3' });
        this.audioPreviewUrl = URL.createObjectURL(audioBlob);
        
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = () => {
          const base64data = reader.result as string;
          this.audioCapturadoBase64 = base64data.split(',')[1];
          this.cdr.detectChanges();
        };
        stream.getTracks().forEach(t => t.stop()); 
      };
      
      this.mediaRecorder.start();
    } catch (err) {
      console.error('Error de audio:', err);
      alert('Permiso denegado o no hay micrófono disponible.');
      this.grabandoAudio = false;
      this.cdr.detectChanges();
    }
  }

  detenerGrabacion() {
    if (this.mediaRecorder && this.grabandoAudio) {
      this.mediaRecorder.stop();
      this.grabandoAudio = false;
      this.cdr.detectChanges();
    }
  }

  pasarACotizacionDesdeDetalles() {
    this.mostrarModalDetalles = false;
    this.cotizacionForm = { precio_estimado: null, tiempo_estimado_minutos: null };
    this.mostrarModalCotizacion = true; 
  }

  abrirModalCotizacion(emergencia: Emergencia) {
    this.emergenciaSeleccionada = emergencia;
    this.cotizacionForm = { precio_estimado: null, tiempo_estimado_minutos: null };
    this.mostrarModalCotizacion = true;
  }

  cerrarModalCotizacion() {
    this.mostrarModalCotizacion = false;
    this.emergenciaSeleccionada = null;
    this.procesandoAccion = false;
  }

  enviarCotizacion() {
    if (!this.cotizacionForm.precio_estimado || !this.cotizacionForm.tiempo_estimado_minutos) {
      alert('Ingrese todos los datos de la oferta comercial.');
      return;
    }
    
    if (!this.emergenciaSeleccionada) {
      alert('No hay una emergencia seleccionada.');
      return;
    }

    this.procesandoAccion = true;
    
    const payloadOferta = {
      nro_emergencia: this.emergenciaSeleccionada.nro_emergencia,
      precio_estimado: this.cotizacionForm.precio_estimado,
      tiempo_estimado_minutos: this.cotizacionForm.tiempo_estimado_minutos
    };

    this.emergenciasService.emitirOferta(payloadOferta).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            alert('¡Oferta enviada exitosamente al cliente! El cliente recibirá una notificación.');
            this.cerrarModalCotizacion();
            this.cargarEmergencias(); 
          }
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          alert(err.error?.detail || 'Ocurrió un error al intentar enviar la cotización.');
          this.procesandoAccion = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  iniciarTracking(emergencia: Emergencia) {
    if (confirm('¿Confirmas que estás iniciando el viaje hacia la ubicación del incidente? El cliente podrá ver tu ruta.')) {
      this.cargando = true;
      this.emergenciasService.actualizarEmergencia(emergencia.nro_emergencia, { estado: 'EN CURSO' }).subscribe({
        next: () => {
          this.ngZone.run(() => {
            // 1. Actualizamos el objeto local para que el modal de tracking lo muestre correctamente
            emergencia.estado = 'EN CURSO';
            
            // 2. Redirigimos pasando la data (Ya no necesitas this.cargarEmergencias() aquí)
            this.router.navigate(['/tracking'], { state: { emergenciaData: emergencia } });
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            alert(err.error?.detail || 'No se pudo iniciar el tracking.');
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      });
    }
  }

  verTracking(emergencia: Emergencia) {
    this.router.navigate(['/tracking'], { state: { emergenciaData: emergencia } });
  }
}