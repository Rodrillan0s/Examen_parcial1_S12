import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListaBitacora } from './lista-bitacora';

describe('ListaBitacora', () => {
  let component: ListaBitacora;
  let fixture: ComponentFixture<ListaBitacora>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListaBitacora],
    }).compileComponents();

    fixture = TestBed.createComponent(ListaBitacora);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
