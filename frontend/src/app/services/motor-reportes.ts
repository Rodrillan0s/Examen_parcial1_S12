import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';
import * as XLSX from 'xlsx';

export interface ReportRequest {
  tipo_reporte: string;
  reporte?: string;
  filtros?: Record<string, any>;
  groupBy?: string | null;
  orderBy?: string | null;
  orderDirection?: 'ASC' | 'DESC';
  formato?: string;
}

export interface ColumnaMeta {
  campo: string;
  titulo: string;
  tipo: 'string' | 'number' | 'currency' | 'date' | 'badge';
}

export interface CatalogoReporteItem {
  codigo: string;
  nombre: string;
  descripcion: string;
  vista: string;
  filtros_permitidos: string[];
  agrupaciones_permitidas: string[];
  columnas: ColumnaMeta[];
  campo_monto: string;
}

export interface OpcionAmbiguedad {
  tipo: 'producto' | 'categoria' | 'sucursal' | 'metodo_pago';
  id: number;
  nombre: string;
  detalle: string;
}

export interface AmbiguedadDetectada {
  termino: string;
  opciones: OpcionAmbiguedad[];
}

export interface ParseCommandResponse {
  success: boolean;
  valido: boolean;
  comando_original: string;
  resumen_interpretacion: string;
  report_request: ReportRequest;
  ambiguities: AmbiguedadDetectada[];
}

export interface ReporteEjecutadoData {
  tipo_reporte: string;
  codigo: string;
  nombre: string;
  descripcion: string;
  columnas: ColumnaMeta[];
  items: Record<string, any>[];
  resumen: {
    total_registros: number;
    total_monto: number;
    promedio_monto: number;
    campo_monto_usado: string;
  };
  filtros_aplicados: Record<string, any>;
  groupBy?: string | null;
  orderBy?: string | null;
  orderDirection?: string;
}

@Injectable({
  providedIn: 'root'
})
export class MotorReportesService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private apiUrl = environment.apiUrl;

  private getHeaders(): HttpHeaders {
    const token = this.authService.obtenerToken();
    return token
      ? new HttpHeaders({ Authorization: `Bearer ${token}` })
      : new HttpHeaders();
  }

  // ============================================================================
  // COMUNICACIÓN CON EL BACKEND
  // ============================================================================

  obtenerCatalogo(): Observable<{ success: boolean; catalogo: CatalogoReporteItem[]; total: number }> {
    return this.http.get<{ success: boolean; catalogo: CatalogoReporteItem[]; total: number }>(
      `${this.apiUrl}/api/motor-reportes/catalogo`,
      { headers: this.getHeaders() }
    );
  }

  parsearComando(command: string, contexto: any = {}): Observable<ParseCommandResponse> {
    return this.http.post<ParseCommandResponse>(
      `${this.apiUrl}/api/motor-reportes/parse-command`,
      { command, contexto },
      { headers: this.getHeaders() }
    );
  }

  ejecutarReporte(request: ReportRequest): Observable<{ success: boolean; data: ReporteEjecutadoData }> {
    return this.http.post<{ success: boolean; data: ReporteEjecutadoData }>(
      `${this.apiUrl}/api/motor-reportes/ejecutar`,
      request,
      { headers: this.getHeaders() }
    );
  }

  exportarPdf(request: ReportRequest): Observable<Blob> {
    return this.http.post(
      `${this.apiUrl}/api/motor-reportes/exportar/pdf`,
      request,
      { headers: this.getHeaders(), responseType: 'blob' }
    );
  }

  // ============================================================================
  // EXPORTACIÓN A EXCEL CLIENT-SIDE CON SHEETJS
  // ============================================================================

  exportarExcel(filas: any[], nombreArchivo: string, columnas?: ColumnaMeta[], nombreHoja: string = 'Reporte') {
    if (!filas || !filas.length) {
      alert('No hay datos para exportar.');
      return;
    }

    // Si se especifican columnas, ordenar y mapear títulos amigables
    let dataToExport = filas;
    if (columnas && columnas.length > 0) {
      dataToExport = filas.map(fila => {
        const obj: Record<string, any> = {};
        for (const col of columnas) {
          obj[col.titulo || col.campo] = fila[col.campo] ?? '';
        }
        return obj;
      });
    }

    const worksheet: XLSX.WorkSheet = XLSX.utils.json_to_sheet(dataToExport);

    // Ajuste automático de ancho
    const keys = Object.keys(dataToExport[0]);
    worksheet['!cols'] = keys.map(k => {
      const maxLen = Math.max(
        k.length,
        ...dataToExport.map(row => (row[k] ? row[k].toString().length : 0))
      );
      return { wch: Math.min(Math.max(maxLen + 2, 10), 45) };
    });

    const workbook: XLSX.WorkBook = {
      Sheets: { [nombreHoja]: worksheet },
      SheetNames: [nombreHoja]
    };

    XLSX.writeFile(workbook, `${nombreArchivo}.xlsx`);
  }

  // ============================================================================
  // WEB SPEECH API (SIN TOKENS NI IA - 100% NATIVO DE NAVEGADOR)
  // ============================================================================

  isSpeechRecognitionSupported(): boolean {
    if (typeof window === 'undefined') return false;
    return !!((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);
  }

  crearReconocedorVoz(
    onResult: (textoTranscrito: string, isFinal: boolean) => void,
    onError: (error: any) => void,
    onEnd: () => void
  ): any {
    if (!this.isSpeechRecognitionSupported()) return null;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.lang = 'es-ES'; // Español nativo
    recognition.continuous = false; // Detenerse tras una frase
    recognition.interimResults = true; // Mostrar transcripción en tiempo real
    recognition.maxAlternatives = 1;

    recognition.onresult = (event: any) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      if (finalTranscript.trim()) {
        onResult(finalTranscript.trim(), true);
      } else if (interimTranscript.trim()) {
        onResult(interimTranscript.trim(), false);
      }
    };

    recognition.onerror = (event: any) => {
      onError(event.error);
    };

    recognition.onend = () => {
      onEnd();
    };

    return recognition;
  }
}
