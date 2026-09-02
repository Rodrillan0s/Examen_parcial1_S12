import { TestBed } from '@angular/core/testing';

import { Escrow } from './escrow';

describe('Escrow', () => {
  let service: Escrow;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Escrow);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
