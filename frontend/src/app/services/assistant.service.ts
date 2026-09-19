import { Injectable, inject, PLATFORM_ID, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export interface AssistantProduct {
  id_producto: number;
  nombre: string;
  codigo_producto?: string;
  precio: number;
  categoria?: string;
  genero?: string;
  imagen_url?: string;
  descripcion?: string;
  stock_disponible?: number;
  tallas?: string[];
  colores?: string[];
}

export interface AssistantMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tipo?: 'texto' | 'productos' | 'tabla' | 'indicadores' | 'reporte';
  datos?: any;
}

export interface ChatApiResponse {
  success: boolean;
  respuesta: string;
  tipo: 'texto' | 'productos' | 'tabla' | 'indicadores' | 'reporte';
  datos?: any;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AssistantService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private platformId = inject(PLATFORM_ID);
  private apiUrl = environment.apiUrl || 'http://127.0.0.1:5000';

  public isOpen = signal<boolean>(false);
  public isLoading = signal<boolean>(false);
  public isListening = signal<boolean>(false);
  public speechError = signal<string | null>(null);
  public messages = signal<AssistantMessage[]>([]);

  private recognition: any = null;

  constructor() {
    this.inicializarSpeechRecognition();
  }

  public toggleAssistant(): void {
    const nuevoEstado = !this.isOpen();
    this.isOpen.set(nuevoEstado);
    if (nuevoEstado && this.messages().length === 0) {
      this.agregarMensajeInicial();
    }
  }

  public openAssistant(): void {
    this.isOpen.set(true);
    if (this.messages().length === 0) {
      this.agregarMensajeInicial();
    }
  }

  public closeAssistant(): void {
    this.isOpen.set(false);
    this.detenerVoz();
  }

  public limpiarConversacion(): void {
    this.messages.set([]);
    this.agregarMensajeInicial();
  }

  public agregarMensajeInicial(): void {
    const user = this.authService.currentUser();
    const roles = this.authService.roles().map(r => r.toUpperCase());
    const esAdmin = roles.includes('ADMINISTRADOR') || roles.includes('SUPERADMIN') || 
                    roles.includes('ADMINISTRADOR_TIENDA') || roles.includes('ENCARGADO');

    let saludo = 'Hola 👋\n\nSoy el asistente inteligente de **Aurora Store**.\n';
    if (esAdmin) {
      saludo += `Puedo ayudarte a consultar ventas en tiempo real, inventario crítico, indicadores de gestión y reportes ejecutivos.\n\n¿En qué métrica o consulta puedo asistirte hoy?`;
    } else {
      saludo += `Puedo ayudarte a buscar prendas exclusivas, consultar disponibilidad de tallas y colores, tiendas físicas o el estado de tus compras y reservas.\n\n¿Qué deseas descubrir hoy?`;
    }

    this.messages.set([
      {
        id: 'msg_welcome_' + Date.now(),
        role: 'assistant',
        content: saludo,
        timestamp: new Date(),
        tipo: 'texto'
      }
    ]);
  }

  public enviarMensaje(texto: string): void {
    const mensajeLimpio = texto.trim();
    if (!mensajeLimpio || this.isLoading()) return;

    // Agregar mensaje del usuario
    const userMsg: AssistantMessage = {
      id: 'msg_u_' + Date.now(),
      role: 'user',
      content: mensajeLimpio,
      timestamp: new Date(),
      tipo: 'texto'
    };

    this.messages.update(prev => [...prev, userMsg]);
    this.isLoading.set(true);
    this.speechError.set(null);

    // Preparar historial breve para contexto (últimos 6)
    const historial = this.messages()
      .slice(-6)
      .map(m => ({ role: m.role, content: m.content }));

    const token = this.authService.obtenerToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    this.http.post<ChatApiResponse>(`${this.apiUrl}/api/asistente/chat`, {
      mensaje: mensajeLimpio,
      historial: historial
    }, { headers }).subscribe({
      next: (resp) => {
        this.isLoading.set(false);
        const botMsg: AssistantMessage = {
          id: 'msg_a_' + Date.now(),
          role: 'assistant',
          content: resp.respuesta || 'He procesado tu consulta.',
          timestamp: new Date(),
          tipo: resp.tipo || 'texto',
          datos: resp.datos
        };
        this.messages.update(prev => [...prev, botMsg]);
      },
      error: (err) => {
        this.isLoading.set(false);
        console.error('Error asistente chat:', err);
        const errorMsg: AssistantMessage = {
          id: 'msg_err_' + Date.now(),
          role: 'assistant',
          content: 'No pude procesar la solicitud en este momento. Las demás funciones de Aurora Store continúan funcionando normalmente.',
          timestamp: new Date(),
          tipo: 'texto'
        };
        this.messages.update(prev => [...prev, errorMsg]);
      }
    });
  }

  // =====================================================================
  // RECONOCIMIENTO DE VOZ MEDIANTE NATIVE WEB SPEECH API
  // =====================================================================

  private inicializarSpeechRecognition(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const windowAny = window as any;
    const SpeechRecognition = windowAny.SpeechRecognition || windowAny.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('Web Speech API no soportada en este navegador.');
      return;
    }

    try {
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'es-ES';
      this.recognition.continuous = false;
      this.recognition.interimResults = false;

      this.recognition.onstart = () => {
        this.isListening.set(true);
        this.speechError.set(null);
      };

      this.recognition.onend = () => {
        this.isListening.set(false);
      };

      this.recognition.onerror = (event: any) => {
        this.isListening.set(false);
        console.warn('Speech recognition error:', event.error);
        if (event.error !== 'no-speech') {
          this.speechError.set('No se pudo capturar audio del micrófono.');
        }
      };
    } catch (e) {
      console.error('Error inicializando SpeechRecognition:', e);
    }
  }

  public alternarVoz(onTextoDetectado: (texto: string) => void): void {
    if (this.isListening()) {
      this.detenerVoz();
    } else {
      this.iniciarVoz(onTextoDetectado);
    }
  }

  public iniciarVoz(onTextoDetectado: (texto: string) => void): void {
    if (!isPlatformBrowser(this.platformId)) return;

    if (!this.recognition) {
      this.inicializarSpeechRecognition();
    }

    if (!this.recognition) {
      this.speechError.set('Reconocimiento por voz no disponible en tu navegador.');
      return;
    }

    try {
      this.recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          onTextoDetectado(transcript);
        }
      };
      this.recognition.start();
    } catch (e) {
      console.warn('No se pudo iniciar el micrófono:', e);
      this.isListening.set(false);
    }
  }

  public detenerVoz(): void {
    if (this.recognition && this.isListening()) {
      try {
        this.recognition.stop();
      } catch (e) {
        // Ignorar
      }
      this.isListening.set(false);
    }
  }
}
