import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListaUsuarios } from './lista-usuarios';

describe('ListaUsuarios', () => {
  let component: ListaUsuarios;
  let fixture: ComponentFixture<ListaUsuarios>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListaUsuarios],
    }).compileComponents();

    fixture = TestBed.createComponent(ListaUsuarios);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
