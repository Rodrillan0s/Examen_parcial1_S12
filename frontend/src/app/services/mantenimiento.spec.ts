import { TestBed } from '@angular/core/testing';

import { Mantenimiento } from './mantenimiento';

describe('Mantenimiento', () => {
  let service: Mantenimiento;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Mantenimiento);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
