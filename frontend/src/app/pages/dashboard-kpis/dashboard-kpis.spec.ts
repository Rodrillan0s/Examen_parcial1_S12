import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardKpis } from './dashboard-kpis';

describe('DashboardKpis', () => {
  let component: DashboardKpis;
  let fixture: ComponentFixture<DashboardKpis>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardKpis],
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardKpis);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
