import { TestBed } from '@angular/core/testing';

import { Emergencias } from './emergencias';

describe('Emergencias', () => {
  let service: Emergencias;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Emergencias);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
