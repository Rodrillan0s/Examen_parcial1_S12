import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; 
import { BackupService } from '../../services/backup';

@Component({
  selector: 'app-backup',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './backup.html'
})
export class BackupComponent {
  private backupService = inject(BackupService);
  private cdr = inject(ChangeDetectorRef); // <-- AÑADIDO: Para forzar el repintado de la pantalla

  // Estados para el manual
  cargandoManual = false;
  
  // Estados para el automático (Simulado EC2)
  cargandoAuto = false;
  configAutomatica = {
    habilitado: false,
    frecuencia: 'diario',
    hora_ejecucion: '02:00',
    retencion_dias: 7
  };

  // Estado de mensajes globales
  mensaje = '';
  tipoMensaje: 'exito' | 'error' = 'exito';

  descargarBackup() {
    this.cargandoManual = true;
    this.mensaje = '';

    this.backupService.generarBackupManual().subscribe({
      next: (response) => {
        let fileName = 'backup_red_talleres.sql'; 
        const contentDisposition = response.headers.get('Content-Disposition');
        
        if (contentDisposition) {
          const matches = /filename="?([^"]+)"?/.exec(contentDisposition);
          if (matches != null && matches[1]) {
            fileName = matches[1];
          }
        }

        const blob = new Blob([response.body as Blob], { type: 'application/sql' });
        const url = window.URL.createObjectURL(blob);

        const enlace = document.createElement('a');
        enlace.href = url;
        enlace.download = fileName;
        document.body.appendChild(enlace);
        enlace.click();

        document.body.removeChild(enlace);
        window.URL.revokeObjectURL(url);

        this.mostrarMensaje('Copia de seguridad descargada exitosamente.', 'exito');
        this.cargandoManual = false;
        this.cdr.detectChanges(); // <-- OBLIGA A QUITAR EL LOADER
      },
      error: async (err) => {
        console.error('Error completo recibido:', err);
        this.cargandoManual = false;

        let mensajeError = 'Error al generar la copia de seguridad. Verifica la conexión.';

        if (err.status === 403) {
          mensajeError = 'Acceso denegado. Solo los administradores pueden hacer esto.';
        } else if (err.error instanceof Blob && err.error.type === 'application/json') {
          // <-- DESENCAPSULAMOS EL BLOB PARA LEER EL JSON DEL SERVIDOR FLASK
          try {
            const textoJson = await err.error.text();
            const errorObj = JSON.parse(textoJson);
            mensajeError = errorObj.error || errorObj.message || mensajeError;
          } catch (e) {
            console.error('No se pudo parsear el JSON dentro del Blob', e);
          }
        } else if (typeof err.error === 'string') {
          mensajeError = err.error;
        }

        this.mostrarMensaje(mensajeError, 'error');
        this.cdr.detectChanges(); // <-- OBLIGA A QUITAR EL LOADER Y MOSTRAR EL ERROR REAL
      }
    });
  }

  guardarConfiguracionAutomatica() {
    this.cargandoAuto = true;
    this.mensaje = '';

    // Simulamos una petición al backend
    setTimeout(() => {
      this.cargandoAuto = false;
      if (this.configAutomatica.habilitado) {
        this.mostrarMensaje(`Respaldo programado en EC2 para ejecución ${this.configAutomatica.frecuencia}.`, 'exito');
      } else {
        this.mostrarMensaje('Los respaldos automáticos en EC2 han sido deshabilitados.', 'exito');
      }
      this.cdr.detectChanges(); 
    }, 5000); 
  }

  mostrarMensaje(texto: string, tipo: 'exito' | 'error') {
    this.mensaje = texto;
    this.tipoMensaje = tipo;
    this.cdr.detectChanges(); // Actualiza para mostrar el mensaje

    setTimeout(() => { 
      this.mensaje = ''; 
      this.cdr.detectChanges(); // Actualiza para ocultar el mensaje a los 5 segundos
    }, 5000);
  }
}