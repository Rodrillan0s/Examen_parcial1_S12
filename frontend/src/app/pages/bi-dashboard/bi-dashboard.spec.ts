import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BiDashboard } from './bi-dashboard';

describe('BiDashboard', () => {
  let component: BiDashboard;
  let fixture: ComponentFixture<BiDashboard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BiDashboard],
    }).compileComponents();

    fixture = TestBed.createComponent(BiDashboard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
