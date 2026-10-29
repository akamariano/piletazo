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

  it('marca como CURSANDO los cursos que trae el ejemplo', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const app = fixture.componentInstance as unknown as { probarEjemplo: () => Promise<void>; cursando: () => string[] };
    const http = TestBed.inject(HttpTestingController);
    const carga = app.probarEjemplo();
    http.expectOne((r) => r.url === '/api/ejemplo').flush({ aprobados: [{ codigo: '0101', nombre: 'Área Matemática Básica 1', creditos: 9 }], cursando: ['0773', '0778'] });
    await carga;
    expect(app.cursando()).toEqual(['0773', '0778']);
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

describe('Funciones de apoyo', () => {
  beforeEach(async () => {
    localStorage.clear();
    history.replaceState(null, '', '/');
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('lleva el perfil a otro dispositivo con un enlace (#perfil=)', async () => {
    type ConPerfil = {
      nombre: { set: (v: string) => void; (): string };
      aprobados: { set: (v: unknown[]) => void; (): { codigo: string }[] };
      cursando: { set: (v: string[]) => void; (): string[] };
      copiarEnlacePerfil: () => Promise<void>;
    };
    let copiado = '';
    Object.defineProperty(navigator, 'clipboard', { value: { writeText: async (t: string) => void (copiado = t) }, configurable: true });

    const origen = TestBed.createComponent(App).componentInstance as unknown as ConPerfil;
    origen.nombre.set('Ana Pérez');
    origen.aprobados.set([{ codigo: '0101', nombre: 'Área Matemática Básica 1', creditos: 9 }]);
    origen.cursando.set(['0103']);
    await origen.copiarEnlacePerfil();
    expect(copiado).toContain('/#perfil=');

    history.replaceState(null, '', '/' + copiado.slice(copiado.indexOf('#')));
    const destino = TestBed.createComponent(App).componentInstance as unknown as ConPerfil;
    expect(destino.nombre()).toBe('Ana Pérez');
    expect(destino.aprobados().map((a) => a.codigo)).toEqual(['0101']);
    expect(destino.cursando()).toEqual(['0103']);
    expect(location.hash).toBe('');
  });

  it('pide a la API la nota necesaria para el promedio meta', async () => {
    const app = TestBed.createComponent(App).componentInstance as unknown as {
      calcularMeta: (v: string) => Promise<void>;
      resultadoMeta: () => { mensaje: string } | null;
    };
    const http = TestBed.inject(HttpTestingController);
    const calculo = app.calcularMeta('120');
    const peticion = http.expectOne('/api/promedio/meta');
    expect(peticion.request.body.meta).toBe(100); // se acota a 61–100
    peticion.flush({ meta: 100, notaNecesaria: null, posible: false, mensaje: 'No es posible este semestre' });
    await calculo;
    expect(app.resultadoMeta()!.mensaje).toContain('No es posible');
  });

  it('guarda la revisión de lo cargado', async () => {
    const app = TestBed.createComponent(App).componentInstance as unknown as {
      texto: { set: (v: string) => void };
      calcularDesdeTexto: () => Promise<void>;
      hayAvisos: () => boolean;
    };
    const http = TestBed.inject(HttpTestingController);
    app.texto.set('0101 AREA MATEMATICA BASICA 1 7 2021-05 69.00');
    const leer = app.calcularDesdeTexto();
    http.expectOne('/api/cursos/leer').flush({
      aprobados: [{ codigo: '0101', nombre: 'Área Matemática Básica 1', creditos: 7 }],
      avisos: { lineasNoReconocidas: [], codigosDesconocidos: [], duplicados: ['0101'] },
    });
    await leer;
    expect(app.hayAvisos()).toBe(true);
  });
});

describe('Tarjeta para compartir', () => {
  type ConTarjeta = {
    alternarDatoTarjeta: (clave: string, marcado: boolean) => void;
    compartirEn: (red: 'whatsapp' | 'instagram' | 'facebook') => Promise<void>;
    generarTarjeta: () => Promise<void>;
    avisoCompartir: () => string;
    aprobados: { set: (v: unknown[]) => void };
  };

  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('envía solo los datos marcados', async () => {
    const app = TestBed.createComponent(App).componentInstance as unknown as ConTarjeta;
    const http = TestBed.inject(HttpTestingController);
    app.alternarDatoTarjeta('promedio', false);
    const peticion = http.expectOne('/api/tarjeta');
    expect(peticion.request.body.incluir).toEqual(['creditos', 'aprobados', 'cierre']);
    expect(peticion.request.body.formato).toBe('post');
  });

  it('sin menú de compartir, abre WhatsApp con el texto y descarga la imagen', async () => {
    const app = TestBed.createComponent(App).componentInstance as unknown as ConTarjeta;
    const http = TestBed.inject(HttpTestingController);
    const abiertas: string[] = [];
    const original = window.open;
    window.open = ((url: string) => (abiertas.push(url), null)) as typeof window.open;
    const generar = app.generarTarjeta();
    http.expectOne('/api/tarjeta').flush(new Blob(['png'], { type: 'image/png' }));
    await generar;
    await app.compartirEn('whatsapp');
    window.open = original;
    expect(abiertas[0]).toContain('https://wa.me/?text=');
    expect(decodeURIComponent(abiertas[0])).toContain('Calcula el tuyo en');
    expect(app.avisoCompartir()).toContain('adjúntala en el chat');
  });

  it('para Instagram pide el formato de historia', async () => {
    const app = TestBed.createComponent(App).componentInstance as unknown as ConTarjeta;
    const http = TestBed.inject(HttpTestingController);
    const generar = app.generarTarjeta();
    http.expectOne('/api/tarjeta').flush(new Blob(['png'], { type: 'image/png' }));
    await generar;
    const compartir = app.compartirEn('instagram');
    const historia = http.expectOne('/api/tarjeta');
    expect(historia.request.body.formato).toBe('historia');
    historia.flush(new Blob(['png'], { type: 'image/png' }));
    await compartir;
    expect(app.avisoCompartir()).toContain('Instagram no permite publicar desde la web');
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
