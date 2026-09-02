import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TriajeChat } from './triaje-chat';

describe('TriajeChat', () => {
  let component: TriajeChat;
  let fixture: ComponentFixture<TriajeChat>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TriajeChat],
    }).compileComponents();

    fixture = TestBed.createComponent(TriajeChat);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
