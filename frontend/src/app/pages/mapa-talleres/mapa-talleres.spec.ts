import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MapaTalleres } from './mapa-talleres';

describe('MapaTalleres', () => {
  let component: MapaTalleres;
  let fixture: ComponentFixture<MapaTalleres>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MapaTalleres],
    }).compileComponents();

    fixture = TestBed.createComponent(MapaTalleres);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
