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

describe('Cursando', () => {
  type ConCursando = {
    alternarCursando: (codigo: string, nombre: string) => Promise<void>;
    cursando: () => string[];
    errorCursando: () => string;
  };

  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('rechaza un curso sin prerrequisitos y dice cuál es', async () => {
    const app = TestBed.createComponent(App).componentInstance as unknown as ConCursando;
    const http = TestBed.inject(HttpTestingController);
    const marcado = app.alternarCursando('0283', 'Análisis y Diseño de Sistemas 1');
    const peticion = http.expectOne('/api/cursando/validar');
    expect(peticion.request.body.codigo).toBe('0283');
    peticion.flush({
      codigo: '0283',
      nombre: 'Análisis y Diseño de Sistemas 1',
      valido: false,
      faltantes: ['0774 Sistemas de Bases de Datos 1'],
      mensaje: 'No tienes los prerrequisitos para este curso: 0283 Análisis y Diseño de Sistemas 1. Te falta: 0774 Sistemas de Bases de Datos 1.',
    });
    await marcado;
    expect(app.cursando()).toEqual([]);
    expect(app.errorCursando()).toContain('No tienes los prerrequisitos para este curso: 0283 Análisis y Diseño de Sistemas 1');
  });

  it('marca y desmarca un curso válido', async () => {
    const app = TestBed.createComponent(App).componentInstance as unknown as ConCursando;
    const http = TestBed.inject(HttpTestingController);
    const marcado = app.alternarCursando('0773', 'Manejo e Implementación de Archivos');
    http.expectOne('/api/cursando/validar').flush({ codigo: '0773', nombre: 'Manejo e Implementación de Archivos', valido: true, faltantes: [], mensaje: '' });
    await marcado;
    expect(app.cursando()).toEqual(['0773']);
    await app.alternarCursando('0773', 'Manejo e Implementación de Archivos');
    expect(app.cursando()).toEqual([]);
    http.expectNone('/api/cursando/validar');
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
