import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmergenciasActuales } from './emergencias-actuales';

describe('EmergenciasActuales', () => {
  let component: EmergenciasActuales;
  let fixture: ComponentFixture<EmergenciasActuales>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EmergenciasActuales],
    }).compileComponents();

    fixture = TestBed.createComponent(EmergenciasActuales);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
