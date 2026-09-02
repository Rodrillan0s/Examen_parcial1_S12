import { TestBed } from '@angular/core/testing';

import { Kpis } from './kpis';

describe('Kpis', () => {
  let service: Kpis;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Kpis);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
