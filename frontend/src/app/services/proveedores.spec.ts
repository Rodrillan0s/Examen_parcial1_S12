import { TestBed } from '@angular/core/testing';

import { Proveedores } from './proveedores';

describe('Proveedores', () => {
  let service: Proveedores;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Proveedores);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
