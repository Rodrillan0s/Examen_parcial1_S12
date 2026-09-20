import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MapaSucursal } from './mapa-sucursal';

describe('MapaSucursal', () => {
  let component: MapaSucursal;
  let fixture: ComponentFixture<MapaSucursal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MapaSucursal],
    }).compileComponents();

    fixture = TestBed.createComponent(MapaSucursal);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
