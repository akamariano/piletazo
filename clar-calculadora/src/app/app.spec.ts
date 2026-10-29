import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { App } from './app';
import { Logo } from './logo';

describe('App', () => {
  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('presenta Piletazo y su propósito al entrar', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const texto = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(texto).toContain('Piletazo');
    expect(texto).toContain('proyecto personal');
    expect(texto).toContain('Más carreras de Ingeniería');
    expect(texto).toContain('Probar con un ejemplo');
    expect(texto).toContain('Mariano Roberto Rac Noguera');
  });

  it('pide el estudiante de ejemplo a la API según el pensum elegido', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const http = TestBed.inject(HttpTestingController);
    (fixture.nativeElement as HTMLElement).querySelector<HTMLButtonElement>('.probar button')!.click();
    const peticion = http.expectOne((r) => r.url === '/api/ejemplo');
    expect(peticion.request.params.get('origen')).toBe('traslado');
    expect(peticion.request.params.get('semestres')).toBe('5');
  });

  it('describe los prerrequisitos por créditos y alternativas', () => {
    const app = TestBed.createComponent(App).componentInstance as unknown as { describir: (p: string) => string };
    expect(app.describir('200CR')).toBe('200 créditos');
    expect(app.describir('0039|0031')).toBe('0039 ó 0031');
  });
});

describe('Logo', () => {
  it('dibuja la versión simple y la completa', () => {
    const fixture = TestBed.createComponent(Logo);
    fixture.detectChanges();
    expect((fixture.nativeElement as HTMLElement).querySelector('svg')).toBeTruthy();
    fixture.componentRef.setInput('variante', 'simple');
    fixture.detectChanges();
    expect((fixture.nativeElement as HTMLElement).querySelector('path')).toBeTruthy();
  });
});
