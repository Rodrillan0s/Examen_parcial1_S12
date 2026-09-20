import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { NavbarComponent } from './components/navbar/navbar';
import { FooterComponent } from './components/footer/footer';
import { AuthModalComponent } from './components/auth-modal/auth-modal';
import { CarritoDrawerComponent } from './components/carrito-drawer/carrito-drawer';
import { AssistantFloatingComponent } from './components/assistant/assistant-floating';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule, 
    RouterOutlet, 
    NavbarComponent, 
    FooterComponent, 
    AuthModalComponent, 
    CarritoDrawerComponent,
    AssistantFloatingComponent
  ],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private router = inject(Router);
  esRutaAdmin: boolean = false;

  constructor() {
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: any) => {
        const url = event.urlAfterRedirects || event.url || '';
        this.esRutaAdmin = url.startsWith('/admin');
      });
  }
}
