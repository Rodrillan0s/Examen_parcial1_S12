import { TestBed } from '@angular/core/testing';

import { Triaje } from './triaje';

describe('Triaje', () => {
  let service: Triaje;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Triaje);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
