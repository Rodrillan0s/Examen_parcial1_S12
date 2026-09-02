import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServiciosTaller } from './servicios-taller';

describe('ServiciosTaller', () => {
  let component: ServiciosTaller;
  let fixture: ComponentFixture<ServiciosTaller>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ServiciosTaller],
    }).compileComponents();

    fixture = TestBed.createComponent(ServiciosTaller);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
