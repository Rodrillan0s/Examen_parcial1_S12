import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Notificaciones } from './notificaciones';

describe('Notificaciones', () => {
  let component: Notificaciones;
  let fixture: ComponentFixture<Notificaciones>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Notificaciones],
    }).compileComponents();

    fixture = TestBed.createComponent(Notificaciones);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
