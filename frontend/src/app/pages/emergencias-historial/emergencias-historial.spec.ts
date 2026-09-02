import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmergenciasHistorialComponent } from './emergencias-historial';

describe('EmergenciasHistorial', () => {
  let component: EmergenciasHistorialComponent;
  let fixture: ComponentFixture<EmergenciasHistorialComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EmergenciasHistorialComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(EmergenciasHistorialComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
