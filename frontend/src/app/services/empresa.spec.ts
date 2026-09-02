import { TestBed } from '@angular/core/testing';

import { Empresa } from './empresa';

describe('Empresa', () => {
  let service: Empresa;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Empresa);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
