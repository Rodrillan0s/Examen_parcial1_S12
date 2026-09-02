import { TestBed } from '@angular/core/testing';

import { Talleres } from './talleres';

describe('Talleres', () => {
  let service: Talleres;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Talleres);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
