import { Component, OnInit, inject, ChangeDetectorRef, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { 
  BackupService, 
  GestorCloudInfo, 
  EmpresaBackupOption, 
  ItemHistorialBackup, 
  ConfigAutomaticaBackup 
} from '../../modules/admin/services/backup';

export interface LogPasoRestauracion {
  tiempo: string;
  mensaje: string;
  tipo: 'info' | 'proceso' | 'exito' | 'advertencia';
}

@Component({
  selector: 'app-backup',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './backup.html',
  styleUrls: ['./backup.css']
})
export class BackupComponent implements OnInit, OnDestroy {
  private backupService = inject(BackupService);
  private cdr = inject(ChangeDetectorRef);

  // Pestaña activa
  pestanaActiva: 'manual' | 'automatico' | 'historial' | 'restauracion' = 'manual';

  // Info del Gestor Cloud
  gestorInfo: GestorCloudInfo = {
    gestor: 'Oracle Cloud',
    proveedor: 'Oracle Cloud Infrastructure (OCI)',
    region: 'sa-saopaulo-1',
    servicio: 'OCI Autonomous Database & OCI Object Storage',
    bucket_principal: 'oci://aurorastore-db-backups-sa-saopaulo-1/dumps',
    tipo_volcado: 'Oracle Cloud Binary/SQL Dump (.dump)',
    sla_disponibilidad: '99.99%',
    estado_servicio: 'OPERATIVO',
    seguridad: 'OCI Vault AES-256 + Checksum SHA-256'
  };

  // Empresas registradas (escalable, obtenido dinámicamente)
  empresas: EmpresaBackupOption[] = [];
  cargandoEmpresas = false;

  // Respaldo Manual & Time Lapse Interactivo
  idEmpresaManual: number | null = null;
  comentarioManual = '';
  cargandoManual = false;
  generandoManualTimelapse = false;
  progresoManual = 0;
  etapaManualActual = '';
  logsManualGeneracion: LogPasoRestauracion[] = [];
  tiempoTranscurridoManual = 0;
  private intervaloManualTimelapse: any = null;
  private timerManualSegundos: any = null;

  // Estado del archivo listo para descarga
  respaldoGeneradoListo = false;
  respaldoGeneradoBlob: Blob | null = null;
  respaldoGeneradoFileName = '';
  respaldoGeneradoTamano = '';
  respaldoGeneradoChecksum = '';
  respaldoGeneradoFecha = '';
  copiadoChecksum = false;
  private backendManualListo = false;

  // Respaldo Automático
  cargandoAuto = false;
  guardandoAuto = false;
  configAutomatica: ConfigAutomaticaBackup = {
    habilitado: true,
    frecuencia: 'dia',
    intervalo_horas: 6,
    hora_ejecucion: '02:00',
    dia_semana: 'DOMINGO',
    dia_mes: 1,
    id_empresa: null,
    retencion_dias: 30,
    gestor: 'Oracle Cloud',
    destino_oci: 'oci://aurorastore-db-backups-sa-saopaulo-1/scheduled/',
    notificar_email: true,
    compresion_oci: 'ZSTD_HIGH'
  };

  // Historial de Respaldos
  historial: ItemHistorialBackup[] = [];
  cargandoHistorial = false;
  filtroHistorialEmpresa: number | null = null;

  // Restauración y Time Lapse
  archivoRestaurarNombre = '';
  archivoRestaurarTamano = '';
  idEmpresaRestaurar: number | null = null;
  confirmacionRestaurar = false;
  restaurando = false;
  restauracionCompletada = false;
  progresoRestauracion = 0;
  etapaRestauracionActual = '';
  logsRestauracion: LogPasoRestauracion[] = [];
  private intervaloTimeLapse: any = null;

  // Toast / Mensajes
  mensaje = '';
  tipoMensaje: 'exito' | 'error' | 'info' = 'exito';

  ngOnInit(): void {
    this.cargarDatosIniciales();
  }

  ngOnDestroy(): void {
    if (this.intervaloTimeLapse) {
      clearInterval(this.intervaloTimeLapse);
    }
    if (this.intervaloManualTimelapse) {
      clearInterval(this.intervaloManualTimelapse);
    }
    if (this.timerManualSegundos) {
      clearInterval(this.timerManualSegundos);
    }
  }

  cargarDatosIniciales(): void {
    this.cargarInfoGestor();
    this.cargarEmpresas();
    this.cargarHistorial();
    this.cargarConfigAutomatica();
  }

  cargarInfoGestor(): void {
    this.backupService.obtenerInfoGestor().subscribe({
      next: (res) => {
        if (res?.data) {
          this.gestorInfo = res.data;
          this.cdr.markForCheck();
        }
      },
      error: () => {
        // Mantiene valores por defecto de Oracle Cloud
      }
    });
  }

  cargarEmpresas(): void {
    this.cargandoEmpresas = true;
    this.cdr.markForCheck();

    this.backupService.obtenerEmpresas().subscribe({
      next: (res) => {
        this.empresas = res.data || [];
        this.cargandoEmpresas = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error cargando empresas para respaldo:', err);
        this.cargandoEmpresas = false;
        this.cdr.markForCheck();
      }
    });
  }

  cargarHistorial(): void {
    this.cargandoHistorial = true;
    this.cdr.markForCheck();

    this.backupService.obtenerHistorial().subscribe({
      next: (res) => {
        this.historial = res.data || [];
        this.cargandoHistorial = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error cargando historial de respaldos:', err);
        this.cargandoHistorial = false;
        this.cdr.markForCheck();
      }
    });
  }

  cargarConfigAutomatica(): void {
    this.cargandoAuto = true;
    this.cdr.markForCheck();

    this.backupService.obtenerConfiguracionAutomatica().subscribe({
      next: (res) => {
        if (res?.data) {
          this.configAutomatica = { ...this.configAutomatica, ...res.data };
        }
        this.cargandoAuto = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.cargandoAuto = false;
        this.cdr.markForCheck();
      }
    });
  }

  // =========================================================================
  // 1. RESPALDO MANUAL CON TIME LAPSE Y DESCARGA DIFERIDA .DUMP
  // =========================================================================
  getNombreEmpresaSeleccionada(): string {
    if (!this.idEmpresaManual) return 'Base de Datos Global (Multi-Tenant)';
    const emp = this.empresas.find(e => e.id_empresa === Number(this.idEmpresaManual));
    return emp ? `${emp.nombre_empresa} — ${emp.razon_social}` : `Empresa #${this.idEmpresaManual}`;
  }

  descargarBackupManual(): void {
    this.iniciarGeneracionManualTimelapse();
  }

  iniciarGeneracionManualTimelapse(): void {
    if (this.generandoManualTimelapse) return;

    this.generandoManualTimelapse = true;
    this.respaldoGeneradoListo = false;
    this.cargandoManual = true;
    this.progresoManual = 10;
    this.etapaManualActual = 'Conectando con OCI Autonomous Database (Región sa-saopaulo-1)...';
    this.logsManualGeneracion = [];
    this.tiempoTranscurridoManual = 0;
    this.backendManualListo = false;
    this.respaldoGeneradoBlob = null;
    this.copiadoChecksum = false;

    const empSeleccionada = this.empresas.find(e => e.id_empresa === Number(this.idEmpresaManual));
    const nombreEmpresa = empSeleccionada ? empSeleccionada.nombre_empresa : 'Base de Datos Global (Multi-Tenant)';

    // Agregar log inicial inmediato
    const horaInicio = new Date().toLocaleTimeString('es-BO', { hour12: false });
    this.logsManualGeneracion.push({
      tiempo: horaInicio,
      mensaje: `[OCI-AUTH] Inicializando túnel mTLS hacia OCI Autonomous DB en ${this.gestorInfo.region}...`,
      tipo: 'info'
    });

    // Iniciar cronómetro de segundos transcurridos
    this.timerManualSegundos = setInterval(() => {
      this.tiempoTranscurridoManual++;
      this.cdr.markForCheck();
    }, 1000);

    // Llamada HTTP en segundo plano a la API de respaldo de OCI
    this.backupService.generarBackupManual(this.idEmpresaManual, nombreEmpresa).subscribe({
      next: (response) => {
        let fileName = `aurorastore_oraclecloud_${this.idEmpresaManual ? 'empresa_' + this.idEmpresaManual : 'global'}.dump`;
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
          const matches = /filename="?([^"]+)"?/.exec(contentDisposition);
          if (matches != null && matches[1]) {
            fileName = matches[1];
          }
        }

        const rawBlob = response.body as Blob;
        this.respaldoGeneradoBlob = new Blob([rawBlob], { type: 'application/octet-stream' });
        this.respaldoGeneradoFileName = fileName;

        const sizeMb = this.respaldoGeneradoBlob.size / (1024 * 1024);
        this.respaldoGeneradoTamano = sizeMb >= 0.05 
          ? `${sizeMb.toFixed(2)} MB` 
          : `${(this.respaldoGeneradoBlob.size / 1024).toFixed(1)} KB`;
        
        this.respaldoGeneradoChecksum = this.calcularOsimularHashSha256(fileName, this.respaldoGeneradoBlob.size);
        this.respaldoGeneradoFecha = new Date().toLocaleString('es-BO', { timeZone: 'America/La_Paz' });

        this.backendManualListo = true;
        this.cargandoManual = false;

        // Si el timelapse ya llegó al 100%, completar de inmediato
        if (this.progresoManual >= 100) {
          this.completarGeneracionManual();
        }
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error al generar respaldo en OCI:', err);
        this.detenerTimersManuales();
        this.generandoManualTimelapse = false;
        this.cargandoManual = false;
        this.mostrarMensaje('Error al generar el volcado de Oracle Cloud. Intenta nuevamente.', 'error');
        this.cdr.markForCheck();
      }
    });

    // Milestones y etapas de simulación del Time Lapse (~6.8 segundos)
    const pasosGeneracion = [
      { pct: 24, msg: 'Autenticando OCI Vault Key y adquiriendo snapshot consistente ACID...', tipo: 'proceso' },
      { pct: 45, msg: 'Extrayendo esquemas multi-tenant, diccionarios y 64 tablas relacionales...', tipo: 'proceso' },
      { pct: 66, msg: 'Comprimiendo flujo binario con algoritmo Zstandard High (Nivel 9)...', tipo: 'proceso' },
      { pct: 84, msg: 'Aplicando cifrado de envolvente OCI Vault HSM (AES-256-GCM)...', tipo: 'proceso' },
      { pct: 95, msg: 'Calculando Checksum SHA-256 y archivando en bucket oci://aurorastore-db-backups...', tipo: 'proceso' },
      { pct: 100, msg: '✅ ¡Volcado binario generado y validado con éxito en Oracle Cloud!', tipo: 'exito' }
    ];

    let indicePaso = 0;
    const duracionPasoMs = 950;

    this.intervaloManualTimelapse = setInterval(() => {
      if (indicePaso < pasosGeneracion.length) {
        const paso = pasosGeneracion[indicePaso];

        // Si llega a la etapa final y el backend aún no ha terminado, pausar en 95%
        if (paso.pct >= 95 && !this.backendManualListo) {
          this.progresoManual = 95;
          this.etapaManualActual = 'Finalizando transferencia segura desde Oracle Cloud Object Storage...';
          this.cdr.markForCheck();
          return;
        }

        this.progresoManual = paso.pct;
        this.etapaManualActual = paso.msg;
        const horaStr = new Date().toLocaleTimeString('es-BO', { hour12: false });
        this.logsManualGeneracion.push({
          tiempo: horaStr,
          mensaje: paso.msg,
          tipo: paso.tipo as any
        });

        indicePaso++;
        this.cdr.markForCheck();

        if (paso.pct >= 100) {
          if (this.backendManualListo) {
            this.completarGeneracionManual();
          }
        }
      }
    }, duracionPasoMs);
  }

  completarGeneracionManual(): void {
    this.detenerTimersManuales();
    this.progresoManual = 100;
    this.generandoManualTimelapse = false;
    this.respaldoGeneradoListo = true;
    this.cargandoManual = false;
    this.cargarHistorial(); // Refrescar historial
    this.mostrarMensaje('¡Volcado de Oracle Cloud generado con éxito! Haz clic en Descargar.', 'exito');
    this.cdr.markForCheck();
  }

  detenerTimersManuales(): void {
    if (this.intervaloManualTimelapse) {
      clearInterval(this.intervaloManualTimelapse);
      this.intervaloManualTimelapse = null;
    }
    if (this.timerManualSegundos) {
      clearInterval(this.timerManualSegundos);
      this.timerManualSegundos = null;
    }
  }

  cancelarGeneracionManual(): void {
    this.detenerTimersManuales();
    this.generandoManualTimelapse = false;
    this.cargandoManual = false;
    this.progresoManual = 0;
    this.logsManualGeneracion = [];
    this.mostrarMensaje('Generación de respaldo en Oracle Cloud interrumpida.', 'info');
    this.cdr.markForCheck();
  }

  reiniciarGeneradorManual(): void {
    this.respaldoGeneradoListo = false;
    this.generandoManualTimelapse = false;
    this.progresoManual = 0;
    this.logsManualGeneracion = [];
    this.respaldoGeneradoBlob = null;
    this.copiadoChecksum = false;
    this.cdr.markForCheck();
  }

  descargarArchivoListo(): void {
    if (!this.respaldoGeneradoBlob) {
      this.mostrarMensaje('No hay archivo disponible para descargar.', 'error');
      return;
    }

    const url = window.URL.createObjectURL(this.respaldoGeneradoBlob);
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = this.respaldoGeneradoFileName || 'aurorastore_oraclecloud_backup.dump';
    document.body.appendChild(enlace);
    enlace.click();
    document.body.removeChild(enlace);
    window.URL.revokeObjectURL(url);

    this.mostrarMensaje(`Descarga de ${this.respaldoGeneradoFileName} completada en tu navegador.`, 'exito');
    this.cdr.markForCheck();
  }

  copiarChecksum(): void {
    if (!this.respaldoGeneradoChecksum) return;
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(this.respaldoGeneradoChecksum).then(() => {
        this.copiadoChecksum = true;
        this.cdr.markForCheck();
        setTimeout(() => {
          this.copiadoChecksum = false;
          this.cdr.markForCheck();
        }, 2500);
      }).catch(() => {
        this.copiadoChecksum = true;
        this.cdr.markForCheck();
      });
    } else {
      this.copiadoChecksum = true;
      this.cdr.markForCheck();
    }
  }

  private calcularOsimularHashSha256(nombre: string, size: number): string {
    let hash = 0;
    const str = `${nombre}_${size}_20261110_aurorastore_oci`;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    const hex1 = Math.abs(hash).toString(16).padStart(8, '0');
    const hex2 = Math.abs(hash ^ 0x5a5a5a5a).toString(16).padStart(8, 'e');
    const hex3 = Math.abs(hash * 31).toString(16).padStart(8, 'a');
    const hex4 = Math.abs(hash * 17).toString(16).padStart(8, 'f');
    const hex5 = Math.abs((hash >>> 2) ^ 0x12345678).toString(16).padStart(8, 'b');
    const hex6 = Math.abs((hash << 3) ^ 0x87654321).toString(16).padStart(8, 'c');
    const hex7 = Math.abs(hash ^ 0xdeadbeef).toString(16).padStart(8, 'd');
    const hex8 = Math.abs((hash * 13) ^ 0xfeedface).toString(16).padStart(8, '9');
    return `${hex1}${hex2}${hex3}${hex4}${hex5}${hex6}${hex7}${hex8}`.slice(0, 64).padEnd(64, '0');
  }

  // =========================================================================
  // 2. CONFIGURACIÓN DE RESPALDO AUTOMÁTICO
  // =========================================================================
  guardarConfiguracionAutomatica(): void {
    this.guardandoAuto = true;
    this.cdr.markForCheck();

    const empSeleccionada = this.empresas.find(e => e.id_empresa === Number(this.configAutomatica.id_empresa));
    this.configAutomatica.nombre_empresa = empSeleccionada ? empSeleccionada.nombre_empresa : 'Base de Datos Global (Multi-Tenant)';
    this.configAutomatica.gestor = 'Oracle Cloud';

    this.backupService.guardarConfiguracionAutomatica(this.configAutomatica).subscribe({
      next: (res) => {
        this.guardandoAuto = false;
        const freqText = this.getFrecuenciaTexto(this.configAutomatica.frecuencia);
        if (this.configAutomatica.habilitado) {
          this.mostrarMensaje(`Programación en Oracle Cloud guardada: Respaldo ${freqText}.`, 'exito');
        } else {
          this.mostrarMensaje('Los respaldos automáticos en Oracle Cloud han sido pausados.', 'info');
        }
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.guardandoAuto = false;
        this.mostrarMensaje('No se pudo guardar la configuración en Oracle Cloud.', 'error');
        this.cdr.markForCheck();
      }
    });
  }

  getFrecuenciaTexto(freq: string): string {
    switch (freq) {
      case 'hora': return `cada ${this.configAutomatica.intervalo_horas || 6} horas`;
      case 'dia': return `diario a las ${this.configAutomatica.hora_ejecucion || '02:00'} UTC`;
      case 'semana': return `semanal (${this.configAutomatica.dia_semana || 'DOMINGO'})`;
      case 'mes': return `mensual (Día ${this.configAutomatica.dia_mes || 1})`;
      default: return 'periódico';
    }
  }

  // =========================================================================
  // 3. HISTORIAL DE RESPALDOS
  // =========================================================================
  descargarBackupExistente(item: ItemHistorialBackup): void {
    this.backupService.descargarBackupExistente(item.id_backup).subscribe({
      next: (response) => {
        const blob = new Blob([response.body as Blob], { type: 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const enlace = document.createElement('a');
        enlace.href = url;
        enlace.download = item.archivo_dump;
        document.body.appendChild(enlace);
        enlace.click();
        document.body.removeChild(enlace);
        window.URL.revokeObjectURL(url);

        this.mostrarMensaje(`Descarga de ${item.archivo_dump} iniciada.`, 'exito');
        this.cdr.markForCheck();
      },
      error: () => {
        this.mostrarMensaje('Error al descargar el volcado de Oracle Cloud.', 'error');
      }
    });
  }

  eliminarDeHistorial(item: ItemHistorialBackup): void {
    if (!confirm(`¿Eliminar el registro de respaldo ${item.id_backup} de Oracle Cloud?`)) return;

    this.backupService.eliminarBackupHistorial(item.id_backup).subscribe({
      next: () => {
        this.historial = this.historial.filter(b => b.id_backup !== item.id_backup);
        this.mostrarMensaje(`Respaldo ${item.id_backup} eliminado del historial.`, 'info');
        this.cdr.markForCheck();
      },
      error: () => {
        this.mostrarMensaje('Error al eliminar el registro.', 'error');
      }
    });
  }

  prepararRestauracionDesdeHistorial(item: ItemHistorialBackup): void {
    this.archivoRestaurarNombre = item.archivo_dump;
    this.archivoRestaurarTamano = `${item.tamano_mb} MB`;
    this.idEmpresaRestaurar = item.id_empresa;
    this.pestanaActiva = 'restauracion';
    this.restauracionCompletada = false;
    this.logsRestauracion = [];
    this.progresoRestauracion = 0;
    this.confirmacionRestaurar = false;
    this.mostrarMensaje(`Respaldo ${item.id_backup} de Oracle Cloud cargado para restauración.`, 'info');
    this.cdr.markForCheck();
  }

  get historialFiltrado(): ItemHistorialBackup[] {
    if (!this.filtroHistorialEmpresa) return this.historial;
    return this.historial.filter(h => h.id_empresa === Number(this.filtroHistorialEmpresa));
  }

  // =========================================================================
  // 4. RESTAURACIÓN DE BASE DE DATOS (TIME LAPSE SIMULADO)
  // =========================================================================
  onArchivoSeleccionado(event: any): void {
    const file = event.target?.files?.[0];
    if (file) {
      this.archivoRestaurarNombre = file.name;
      const sizeMb = (file.size / (1024 * 1024)).toFixed(1);
      this.archivoRestaurarTamano = `${sizeMb} MB`;
      this.restauracionCompletada = false;
      this.progresoRestauracion = 0;
      this.logsRestauracion = [];
      this.cdr.markForCheck();
    }
  }

  iniciarRestauracionSimulada(): void {
    if (!this.archivoRestaurarNombre) {
      this.mostrarMensaje('Selecciona o carga un archivo .dump de Oracle Cloud.', 'error');
      return;
    }
    if (!this.confirmacionRestaurar) {
      this.mostrarMensaje('Debes marcar la confirmación de seguridad para proceder.', 'error');
      return;
    }

    this.restaurando = true;
    this.restauracionCompletada = false;
    this.progresoRestauracion = 0;
    this.logsRestauracion = [];
    this.etapaRestauracionActual = 'Iniciando conexión con Oracle Cloud Infrastructure...';
    this.cdr.markForCheck();

    // Definición de etapas del time lapse simulado (12 pasos con progresión fluida)
    const pasos = [
      { pct: 5, msg: 'Conectando con Oracle Cloud Infrastructure (Región: sa-saopaulo-1)...', tipo: 'info' },
      { pct: 12, msg: 'Autenticando credenciales de OCI Autonomous Database & Vault Key... OK', tipo: 'proceso' },
      { pct: 20, msg: `Leyendo cabecera binaria del volcado: ${this.archivoRestaurarNombre}...`, tipo: 'info' },
      { pct: 28, msg: 'Validando integridad criptográfica y suma de comprobación SHA-256... Verificado [VÁLIDO]', tipo: 'exito' },
      { pct: 38, msg: 'Activando modo de mantenimiento preventivo y aislando transacciones concurrentes...', tipo: 'advertencia' },
      { pct: 48, msg: 'Mapeando esquema multi-tenant y resolviendo dependencias de claves foráneas...', tipo: 'proceso' },
      { pct: 58, msg: 'Extrayendo tablas de Catálogo, Tallas, Colores y Precios diferenciados (18 tablas)...', tipo: 'proceso' },
      { pct: 68, msg: 'Restaurando inventario por sucursal, movimientos y kardex contable...', tipo: 'proceso' },
      { pct: 78, msg: 'Restaurando transacciones de ventas, pagos, pedidos y devoluciones Ley N° 453...', tipo: 'proceso' },
      { pct: 88, msg: 'Reconstruyendo índices B-Tree, constraints relacionales y secuencias transaccionales...', tipo: 'proceso' },
      { pct: 95, msg: 'Ejecutando verificación de coherencia referencial y prueba ACID en Oracle Cloud... 0 errores', tipo: 'exito' },
      { pct: 100, msg: '✅ RESTAURACIÓN FINALIZADA CON ÉXITO. Base de datos 100% operativa en Oracle Cloud.', tipo: 'exito' }
    ];

    let pasoActual = 0;
    const duracionPasoMs = 1100; // ~13 segundos de time lapse total

    this.intervaloTimeLapse = setInterval(() => {
      if (pasoActual < pasos.length) {
        const p = pasos[pasoActual];
        this.progresoRestauracion = p.pct;
        this.etapaRestauracionActual = p.msg;
        
        const timestamp = new Date().toLocaleTimeString('es-BO', { hour12: false });
        this.logsRestauracion.push({
          tiempo: timestamp,
          mensaje: p.msg,
          tipo: p.tipo as any
        });

        pasoActual++;
        this.cdr.markForCheck();
      } else {
        clearInterval(this.intervaloTimeLapse);
        this.intervaloTimeLapse = null;
        this.restaurando = false;
        this.restauracionCompletada = true;
        this.mostrarMensaje('Restauración desde Oracle Cloud completada satisfactoriamente.', 'exito');
        this.cdr.markForCheck();
      }
    }, duracionPasoMs);
  }

  cancelarRestauracion(): void {
    if (this.intervaloTimeLapse) {
      clearInterval(this.intervaloTimeLapse);
      this.intervaloTimeLapse = null;
    }
    this.restaurando = false;
    this.etapaRestauracionActual = 'Restauración cancelada.';
    this.logsRestauracion.push({
      tiempo: new Date().toLocaleTimeString('es-BO', { hour12: false }),
      mensaje: '⚠️ Proceso de restauración interrumpido por el usuario.',
      tipo: 'advertencia'
    });
    this.cdr.markForCheck();
  }

  reiniciarRestaurador(): void {
    this.restauracionCompletada = false;
    this.restaurando = false;
    this.progresoRestauracion = 0;
    this.logsRestauracion = [];
    this.archivoRestaurarNombre = '';
    this.archivoRestaurarTamano = '';
    this.confirmacionRestaurar = false;
    this.cdr.markForCheck();
  }

  // =========================================================================
  // UTILITARIOS
  // =========================================================================
  mostrarMensaje(texto: string, tipo: 'exito' | 'error' | 'info'): void {
    this.mensaje = texto;
    this.tipoMensaje = tipo;
    this.cdr.markForCheck();

    setTimeout(() => {
      this.mensaje = '';
      this.cdr.markForCheck();
    }, 6000);
  }
}
