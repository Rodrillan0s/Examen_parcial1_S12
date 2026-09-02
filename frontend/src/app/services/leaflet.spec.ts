import { TestBed } from '@angular/core/testing';

import { Leaflet } from './leaflet';

describe('Leaflet', () => {
  let service: Leaflet;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Leaflet);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
