import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListaEmpresas } from './lista-empresas';

describe('ListaEmpresas', () => {
  let component: ListaEmpresas;
  let fixture: ComponentFixture<ListaEmpresas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListaEmpresas],
    }).compileComponents();

    fixture = TestBed.createComponent(ListaEmpresas);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
