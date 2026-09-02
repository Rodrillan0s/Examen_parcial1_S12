import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DineroRetenido } from './dinero-retenido';

describe('DineroRetenido', () => {
  let component: DineroRetenido;
  let fixture: ComponentFixture<DineroRetenido>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DineroRetenido],
    }).compileComponents();

    fixture = TestBed.createComponent(DineroRetenido);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
