import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MantenimientoCrm } from './mantenimiento-crm';

describe('MantenimientoCrm', () => {
  let component: MantenimientoCrm;
  let fixture: ComponentFixture<MantenimientoCrm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MantenimientoCrm],
    }).compileComponents();

    fixture = TestBed.createComponent(MantenimientoCrm);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
