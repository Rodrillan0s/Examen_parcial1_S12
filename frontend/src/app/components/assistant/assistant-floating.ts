import { Component, inject, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AssistantService, AssistantMessage, AssistantProduct } from '../../services/assistant.service';
import { ThemeService } from '../../services/theme';

@Component({
  selector: 'app-assistant-floating',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './assistant-floating.html',
  styleUrls: ['./assistant-floating.css']
})
export class AssistantFloatingComponent implements AfterViewChecked {
  public assistantService = inject(AssistantService);
  public themeService = inject(ThemeService);
  private router = inject(Router);

  @ViewChild('scrollContainer') private scrollContainer?: ElementRef;
  @ViewChild('inputMensaje') private inputMensajeRef?: ElementRef;

  public mensajeTexto: string = '';
  private debeHacerScroll: boolean = false;

  get isOpen(): boolean {
    return this.assistantService.isOpen();
  }

  get isLoading(): boolean {
    return this.assistantService.isLoading();
  }

  get isListening(): boolean {
    return this.assistantService.isListening();
  }

  get messages(): AssistantMessage[] {
    return this.assistantService.messages();
  }

  public alternarPanel(): void {
    this.assistantService.toggleAssistant();
    if (this.assistantService.isOpen()) {
      this.debeHacerScroll = true;
      setTimeout(() => {
        this.inputMensajeRef?.nativeElement?.focus();
      }, 200);
    }
  }

  public cerrarPanel(): void {
    this.assistantService.closeAssistant();
  }

  public reiniciarConversacion(): void {
    this.assistantService.limpiarConversacion();
    this.debeHacerScroll = true;
  }

  public enviar(): void {
    if (!this.mensajeTexto.trim() || this.isLoading) return;
    const texto = this.mensajeTexto;
    this.mensajeTexto = '';
    this.assistantService.enviarMensaje(texto);
    this.debeHacerScroll = true;
  }

  public onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.enviar();
    }
  }

  public alternarMicrofono(): void {
    this.assistantService.alternarVoz((transcripcion: string) => {
      this.mensajeTexto = transcripcion;
      // Enviar automáticamente el comando reconocido por voz
      this.enviar();
    });
  }

  public verProducto(producto: AssistantProduct | any): void {
    if (!producto) return;
    const id = producto.id_producto || producto.id;
    if (id) {
      this.router.navigate(['/catalogo', id]);
    } else {
      this.router.navigate(['/catalogo']);
    }
  }

  public getProductos(datos: any): AssistantProduct[] {
    return Array.isArray(datos) ? datos : [];
  }

  public getItemsTabla(datos: any): any[] {
    return Array.isArray(datos) ? datos : [];
  }

  public asAny(val: any): any {
    return val || {};
  }

  public sugerirConsulta(texto: string): void {
    this.mensajeTexto = texto;
    this.enviar();
  }

  public formatearTexto(texto: string): string {
    if (!texto) return '';
    // Formatear markdown básico: **negrita**, saltos de línea, viñetas
    let formatted = texto
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^- (.*$)/gim, '<li class="ml-4 list-disc">$1</li>')
      .replace(/\n/g, '<br>');
    return formatted;
  }

  public ngAfterViewChecked(): void {
    if (this.debeHacerScroll) {
      this.scrollAlFondo();
      this.debeHacerScroll = false;
    }
  }

  private scrollAlFondo(): void {
    try {
      if (this.scrollContainer) {
        this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
      }
    } catch (e) {
      // Ignorar
    }
  }
}
