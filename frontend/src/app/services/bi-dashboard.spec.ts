import { TestBed } from '@angular/core/testing';

import { BiDashboard } from './bi-dashboard';

describe('BiDashboard', () => {
  let service: BiDashboard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BiDashboard);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
