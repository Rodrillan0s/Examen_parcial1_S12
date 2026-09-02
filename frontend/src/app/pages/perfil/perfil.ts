import { Component, OnInit, inject, NgZone, ChangeDetectorRef, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { PerfilService, PerfilUsuario } from '../../services/perfil';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './perfil.html'
})
export class PerfilComponent implements OnInit {
  private perfilService = inject(PerfilService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private ngZone = inject(NgZone);
  private cdr = inject(ChangeDetectorRef);
  private platformId = inject(PLATFORM_ID);

  perfil: PerfilUsuario | null = null;
  perfilForm: any = {}; 
  
  cargando: boolean = true;
  modoEdicion: boolean = false;
  mensaje: { texto: string, tipo: 'exito' | 'error' } | null = null;
  modoOscuro: boolean = false;
  mensajeError: string = '';

  // En perfil.component.ts
  async ngOnInit() {
    this.cargando = true;
    
    // Damos un tiempo mínimo para que la app termine de cargar (fase de hidratación)
    await new Promise(r => setTimeout(r, 300)); 
    
    this.cargarDatosPerfil();
  }

  // --- MÉTODOS DE LA BARRA DE NAVEGACIÓN ---
  alternarModoOscuro() {
    this.modoOscuro = !this.modoOscuro;
    if (this.modoOscuro) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('tema_sistema', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('tema_sistema', 'light');
    }
  }

  navegarA(ruta: string) {
    this.router.navigate([ruta]);
  }

  cerrarSesion() {
    this.authService.cerrarSesion();
    this.router.navigate(['/login']);
  }
  // ----------------------------------------

  // En tu perfil.component.ts
  async cargarDatosPerfil(reintentos = 3) {
    this.cargando = true;
    
    this.perfilService.obtenerPerfil().subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          this.perfil = res.data;
          this.cargando = false;
          this.cdr.detectChanges();
        });
      },
      error: (err) => {
        if (reintentos > 0) {
          // Si falló, esperamos 500ms y reintentamos
          setTimeout(() => this.cargarDatosPerfil(reintentos - 1), 500);
        } else {
          this.ngZone.run(() => {
            this.mostrarMensaje('No se pudo cargar el perfil tras varios intentos.', 'error');
            this.cargando = false;
            this.cdr.detectChanges();
          });
        }
      }
    });
  }

  activarEdicion() {
    if (this.perfil) {
      this.perfilForm = { 
        ci: this.perfil.ci,
        telefono: this.perfil.telefono,
        correo: this.perfil.correo,
        direccion: this.perfil.direccion,
        password: '' 
      };
      this.modoEdicion = true;
    }
  }

  cancelarEdicion() {
    this.modoEdicion = false;
    this.perfilForm = {};
  }

  guardarPerfil() {
    this.cargando = true;
    const payload: any = {
      ci: this.perfilForm.ci,
      telefono: this.perfilForm.telefono,
      correo: this.perfilForm.correo,
      direccion: this.perfilForm.direccion
    };

    if (this.perfilForm.password && this.perfilForm.password.trim() !== '') {
      payload.password = this.perfilForm.password;
    }

    this.perfilService.actualizarPerfil(payload).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          if (res.success) {
            this.mostrarMensaje(res.message, 'exito');
            this.modoEdicion = false;
            this.cargarDatosPerfil(); 
          } else {
            this.mostrarMensaje(res.message, 'error');
            this.cargando = false;
          }
          this.cdr.detectChanges();
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          this.mostrarMensaje('Error al actualizar', 'error');
          this.cargando = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  mostrarMensaje(texto: string, tipo: 'exito' | 'error') {
    this.mensaje = { texto, tipo };
    setTimeout(() => {
      this.mensaje = null;
      this.cdr.detectChanges();
    }, 4000);
  }
}