import { TestBed } from '@angular/core/testing';

import { Backup } from './backup';

describe('Backup', () => {
  let service: Backup;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Backup);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
