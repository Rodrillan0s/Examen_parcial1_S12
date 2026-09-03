import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './components/navbar/navbar';
import { FooterComponent } from './components/footer/footer';
import { AuthModalComponent } from './components/auth-modal/auth-modal';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, FooterComponent, AuthModalComponent],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {}
