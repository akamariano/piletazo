import { HttpClient, httpResource } from '@angular/common/http';
import { Component, computed, DestroyRef, effect, inject, signal, untracked } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import {
  Consentimiento,
  guardarConsentimiento,
  guardarDatos,
  leerConsentimiento,
  leerDatos,
  olvidarTodo,
} from './data/almacenamiento';
import {
  CursoAprobado,
  CursoRed,
  CursosPorVacaciones,
  DuracionPracticas,
  Modalidad,
  Avisos,
  Origen,
  Plan,
  PromedioMeta,
  RespuestaCalculo,
  ValidacionCursando,
} from './data/modelos';
import { Icono } from './icono';
import { CargandoOla } from './cargando-ola';
import { Logo } from './logo';
import { MarcaMr } from './marca-mr';

const SEMESTRES = ['Primer', 'Segundo', 'Tercer', 'Cuarto', 'Quinto', 'Sexto', 'Séptimo', 'Octavo', 'Noveno', 'Décimo'];
const CARGA_POR_DEFECTO = 30;
const CORREO = 'marianoracnoguera@gmail.com';
const ASUNTO = 'Calculadora CLAR';

export type EstadoEtapa = 'completa' | 'en-curso' | 'pendiente';

@Component({
  imports: [CargandoOla, Icono, Logo, MarcaMr],
  selector: 'app-root',
  styleUrl: './app.css',
  templateUrl: './app.html',
})
export class App {
  protected readonly secciones = [
    { id: 'resumen', etiqueta: 'Resumen', icono: 'resumen' },
    { id: 'pipeline', etiqueta: 'Avance por semestre', icono: 'pipeline' },
    { id: 'proximo', etiqueta: 'Próximo semestre', icono: 'calendario' },
    { id: 'areas', etiqueta: 'Áreas', icono: 'libro' },
    { id: 'rutas', etiqueta: 'Rutas posibles', icono: 'ruta' },
    { id: 'cambios', etiqueta: 'Cambios del traslado', icono: 'comparar' },
    { id: 'red', etiqueta: 'Red curricular', icono: 'red' },
    { id: 'equivalencias', etiqueta: 'Equivalencias', icono: 'tabla' },
  ] as const;

  /** Quien empezó en CLAR 2022 no tiene traslado: se ocultan cambios y equivalencias. */
  protected readonly seccionesVisibles = computed(() =>
    this.origen() === 'traslado'
      ? this.secciones
      : this.secciones.filter((s) => s.id !== 'cambios' && s.id !== 'equivalencias'),
  );

  protected readonly consentimiento = signal<Consentimiento>(leerConsentimiento());
  protected readonly nombre = signal('');
  protected readonly carne = signal('');
  protected readonly aprobados = signal<CursoAprobado[]>([]);
  protected readonly vista = signal<'2021' | '2022'>('2022');
  protected readonly cargaMaxima = signal(CARGA_POR_DEFECTO);
  protected readonly proyectar = signal(false);
  protected readonly practicas = signal<DuracionPracticas>(1);
  protected readonly vacaciones = signal<CursosPorVacaciones>(0);
  protected readonly modalidad = signal<Modalidad>('eps');
  protected readonly origen = signal<Origen>('traslado');
  protected readonly plan = computed<Plan>(() => (this.origen() === 'clar2025' ? '2025' : '2022'));
  protected readonly nombreClar = computed(() => `CLAR ${this.plan()}`);
  /** Empezó directamente en un pensum CLAR: no hay traslado ni pensum anterior que mostrar. */
  protected readonly soloClar = computed(() => this.origen() !== 'traslado');
  protected readonly descripcionOrigen = computed(
    () =>
      ({
        traslado: 'pensum anterior trasladado al CLAR 2022',
        clar2022: 'CLAR 2022',
        clar2025: 'CLAR 2025',
      })[this.origen()],
  );
  /** Cursos que el estudiante lleva este semestre: cuentan como aprobados con 61. */
  protected readonly cursando = signal<string[]>([]);
  protected readonly errorCursando = signal('');
  protected readonly validando = signal('');
  private cursandoAntesDelEjemplo: string[] = [];

  protected readonly modo = signal<'pegar' | 'archivo'>('pegar');
  protected readonly texto = signal('');
  protected readonly error = signal('');
  protected readonly nombreArchivo = signal('');
  protected readonly editandoEntrada = signal(false);
  protected readonly seccionActiva = signal('resumen');
  private observador?: IntersectionObserver;
  protected readonly leyendo = signal(false);
  protected readonly descargando = signal(false);
  /** Se están viendo los cursos del estudiante de ejemplo: no se guardan ni pisan los del usuario. */
  protected readonly ejemplo = signal(false);
  private cursosAntesDelEjemplo: CursoAprobado[] = [];
  protected readonly errorPdf = signal('');
  protected readonly mensaje = signal('');
  protected readonly correoRespuesta = signal('');
  protected readonly copiado = signal(false);
  protected readonly correo = CORREO;
  protected readonly anio = new Date().getFullYear();
  private readonly http = inject(HttpClient);
  protected readonly fecha = new Date().toLocaleDateString('es-GT', { day: 'numeric', month: 'long', year: 'numeric' });

  /** Toda la lógica vive en la API de Python (backend/clar). */
  private readonly calculo = httpResource<RespuestaCalculo>(() => {
    const aprobados = this.aprobados();
    if (aprobados.length === 0) return undefined;
    return {
      url: '/api/calculo',
      method: 'POST',
      body: {
        aprobados,
        cursando: this.cursando(),
        modalidad: this.modalidad(),
        cargaMaxima: this.cargaMaxima(),
        practicas: this.practicas(),
        vacaciones: this.vacaciones(),
        plan: this.plan(),
      },
    };
  });

  // Mientras llega una respuesta nueva se sigue mostrando la anterior.
  private ultimaRespuesta: RespuestaCalculo | null = null;
  protected readonly respuesta = computed(() => {
    if (this.aprobados().length === 0) return (this.ultimaRespuesta = null);
    if (this.calculo.hasValue()) this.ultimaRespuesta = this.calculo.value();
    return this.ultimaRespuesta;
  });

  protected readonly calculando = computed(() => this.calculo.isLoading());
  /** Texto del aviso flotante de carga, o vacío si no hay nada cargando. */
  protected readonly cargando = computed(() =>
    this.descargando()
      ? 'Generando tu PDF…'
      : this.leyendo()
        ? 'Leyendo tus cursos…'
        : this.calculando()
          ? this.analisis() ? 'Recalculando…' : 'Calculando tu avance…'
          : '',
  );
  protected readonly errorServidor = computed(() =>
    this.calculo.error() ? 'No se pudo conectar con el servidor de la calculadora. Intenta de nuevo en un momento.' : '',
  );

  protected readonly analisis = computed(() => this.respuesta()?.analisis ?? null);

  protected readonly conjuntoCursando = computed(() => new Set(this.cursando()));
  protected readonly criticos = computed(() => new Set(this.respuesta()?.rutaCritica?.codigos ?? []));
  /** ¿Y si repruebo? por código de curso en curso. */
  protected readonly reprobarPorCodigo = computed(
    () => new Map((this.respuesta()?.reprobar ?? []).map((r) => [r.codigo, r] as const)),
  );

  // ---------- Revisión de lo cargado, promedio meta, tarjeta y perfil ----------
  protected readonly avisos = signal<Avisos | null>(null);
  protected readonly hayAvisos = computed(() => {
    const a = this.avisos();
    return !!a && a.lineasNoReconocidas.length + a.codigosDesconocidos.length + a.duplicados.length > 0;
  });
  protected readonly meta = signal<number | null>(null);
  protected readonly resultadoMeta = signal<PromedioMeta | null>(null);
  protected readonly tarjetaUrl = signal('');
  /** Datos opcionales de la tarjeta; el porcentaje y el nombre van siempre. */
  protected readonly datosTarjeta = [
    { clave: 'creditos', etiqueta: 'Créditos' },
    { clave: 'promedio', etiqueta: 'Promedio' },
    { clave: 'aprobados', etiqueta: 'Cursos aprobados' },
    { clave: 'cierre', etiqueta: 'Cierro pensum' },
  ] as const;
  protected readonly incluirTarjeta = signal<string[]>(['creditos', 'promedio', 'aprobados', 'cierre']);
  protected readonly avisoCompartir = signal('');
  private historiaBlob: Blob | null = null;
  protected readonly generandoTarjeta = signal(false);
  protected readonly puedeCompartirArchivo = signal(false);
  protected readonly avisoPerfil = signal('');
  private tarjetaBlob: Blob | null = null;
  /** Cursos marcados como CURSANDO, en el orden de la red CLAR 2022. */
  protected readonly cursosCursando = computed(() => {
    const cursando = this.conjuntoCursando();
    return (this.analisis()?.clar.red ?? []).filter((r) => cursando.has(r.curso.codigo));
  });

  protected readonly creditosCursando = computed(() => {
    const red = this.analisis()?.clar.red ?? [];
    const cursando = this.conjuntoCursando();
    return red.filter((r) => cursando.has(r.curso.codigo)).reduce((s, r) => s + r.curso.creditos, 0);
  });

  protected readonly progreso = computed(() => {
    const a = this.analisis();
    if (!a) return null;
    return this.vista() === '2022' || this.soloClar() ? a.clar : a.pensum2021;
  });

  protected readonly unidad = computed(() =>
    this.vista() === '2022' || this.soloClar() ? 'CLAR' : 'créditos',
  );

  protected readonly proyeccion = computed(() => {
    const p = this.progreso();
    if (!p) return null;
    const total = p.creditos + p.creditosObligatoriosPendientes;
    return {
      total,
      cursos: p.obligatoriosPendientes.length,
      creditos: p.creditosObligatoriosPendientes,
      optativosFaltantes: Math.max(0, p.cierre - total),
    };
  });

  protected readonly etapas = computed(() => {
    const p = this.progreso();
    if (!p) return [];
    return SEMESTRES.map((nombre, i) => {
      const cursos = p.red.filter((r) => r.curso.semestre === i + 1);
      const obligatorios = cursos.filter((r) => r.curso.obligatorio);
      const aprobados = obligatorios.filter((r) => r.estado === 'aprobado').length;
      const estado: EstadoEtapa =
        obligatorios.length > 0 && aprobados === obligatorios.length
          ? 'completa'
          : aprobados > 0 || cursos.some((r) => r.estado === 'disponible')
            ? 'en-curso'
            : 'pendiente';
      return {
        numero: i + 1,
        nombre,
        cursos,
        estado,
        aprobados,
        obligatorios: obligatorios.length,
        creditos: cursos.filter((r) => r.estado === 'aprobado').reduce((s, r) => s + r.curso.creditos, 0),
      };
    });
  });

  protected readonly recomendacion = computed(() => this.respuesta()?.recomendacion ?? null);

  /** La misma ruta con 0, 1 y 2 cursos por escuela de vacaciones, para comparar. */
  protected readonly escenarios = computed(() => this.respuesta()?.escenarios ?? []);

  protected readonly ruta = computed(() => this.escenarios().find((e) => e.vacaciones === this.vacaciones())?.ruta ?? null);

  protected readonly pedirPermiso = computed(
    () => this.consentimiento() === null && !this.ejemplo() && (this.aprobados().length > 0 || !!this.nombre().trim() || !!this.carne().trim()),
  );

  constructor() {
    const datos = leerDatos();
    if (datos) {
      this.nombre.set(datos.nombre ?? '');
      this.carne.set(datos.carne ?? '');
      this.aprobados.set(datos.aprobados ?? []);
      this.cargaMaxima.set(datos.cargaMaxima ?? CARGA_POR_DEFECTO);
      this.vista.set(datos.vista ?? '2022');
      this.practicas.set(datos.practicas ?? 1);
      this.vacaciones.set(datos.vacaciones ?? 0);
      this.modalidad.set(datos.modalidad ?? 'eps');
      this.origen.set(datos.origen ?? 'traslado');
      this.cursando.set(datos.cursando ?? []);
    }
    this.importarDesdeEnlace();

    effect(() => {
      const datos = {
        nombre: this.nombre(),
        carne: this.carne(),
        aprobados: this.aprobados(),
        cargaMaxima: this.cargaMaxima(),
        vista: this.vista(),
        practicas: this.practicas(),
        vacaciones: this.vacaciones(),
        modalidad: this.modalidad(),
        origen: this.origen(),
        cursando: this.cursando(),
      };
      if (this.consentimiento() === 'si' && !this.ejemplo()) guardarDatos(datos);
    });

    // Marca en la navegación la sección que se está leyendo.
    effect(() => {
      if (this.analisis() && !this.editandoEntrada()) setTimeout(() => this.observarSecciones());
    });
    inject(DestroyRef).onDestroy(() => this.observador?.disconnect());

    // El promedio meta se recalcula cuando cambian los cursos aprobados o en curso.
    effect(() => {
      this.aprobados();
      this.cursando();
      const meta = untracked(this.meta);
      if (meta !== null) untracked(() => this.calcularMeta(String(meta)));
    });

    // Si un curso en curso deja de ser válido (p. ej. al cambiar los aprobados), se quita y se avisa.
    effect(() => {
      const invalidos = this.respuesta()?.cursando?.invalidos ?? [];
      if (invalidos.length === 0) return;
      const fuera = new Set(invalidos.map((i) => i.codigo));
      this.cursando.update((lista) => lista.filter((c) => !fuera.has(c)));
      this.errorCursando.set(invalidos.map((i) => i.mensaje).join(' '));
    });
  }

  protected async calcularDesdeTexto(): Promise<void> {
    await this.leer(
      { texto: this.texto() },
      'No se reconoció ningún curso. Copia las filas tal como aparecen en "Cursos aprobados": código, nombre, créditos, periodo y nota.',
    );
  }

  protected async cargarArchivos(evento: Event): Promise<void> {
    const archivos = Array.from((evento.target as HTMLInputElement).files ?? []);
    const archivo =
      archivos.find((f) => /\.html?$/i.test(f.name)) ?? archivos.find((f) => /\.txt$/i.test(f.name)) ?? archivos[0];
    if (!archivo) return;

    this.nombreArchivo.set(archivo.name);
    const contenido = await archivo.text();
    await this.leer(
      /\.html?$/i.test(archivo.name) ? { html: contenido } : { texto: contenido },
      `No se encontraron cursos aprobados en ${archivo.name}. Sube la red curricular guardada desde el portal (Guardar como → Página web completa) o un .txt con tus cursos.`,
    );
  }

  protected async probarEjemplo(): Promise<void> {
    this.leyendo.set(true);
    this.error.set('');
    try {
      const { aprobados, cursando } = await firstValueFrom(
        this.http.get<{ aprobados: CursoAprobado[]; cursando: string[] }>('/api/ejemplo', {
          params: { origen: this.origen(), semestres: 5 },
        }),
      );
      if (!this.ejemplo()) {
        this.cursosAntesDelEjemplo = this.aprobados();
        this.cursandoAntesDelEjemplo = this.cursando();
      }
      this.cursando.set(cursando ?? []);
      this.errorCursando.set('');
      this.ejemplo.set(true);
      this.aprobados.set(aprobados);
      this.editandoEntrada.set(false);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch {
      this.error.set('No se pudo cargar el ejemplo. Intenta de nuevo en un momento.');
    } finally {
      this.leyendo.set(false);
    }
  }

  protected salirDelEjemplo(): void {
    this.ejemplo.set(false);
    this.aprobados.set(this.cursosAntesDelEjemplo);
    this.cursando.set(this.cursandoAntesDelEjemplo);
    this.cursosAntesDelEjemplo = [];
    this.cursandoAntesDelEjemplo = [];
  }

  /** Marca o desmarca un curso como CURSANDO; antes de marcarlo, la API revisa los prerrequisitos. */
  protected async alternarCursando(codigo: string, nombre: string): Promise<void> {
    if (this.conjuntoCursando().has(codigo)) {
      this.cursando.update((lista) => lista.filter((c) => c !== codigo));
      this.errorCursando.set('');
      return;
    }
    if (this.aprobados().some((a) => a.codigo === codigo) || this.validando()) return;
    this.validando.set(codigo);
    try {
      const v = await firstValueFrom(
        this.http.post<ValidacionCursando>('/api/cursando/validar', {
          aprobados: this.aprobados(),
          codigo,
          modalidad: this.modalidad(),
          plan: this.plan(),
        }),
      );
      if (v.valido) {
        this.cursando.update((lista) => [...lista, codigo]);
        this.errorCursando.set('');
      } else {
        this.errorCursando.set(v.mensaje);
      }
    } catch {
      this.errorCursando.set(`No se pudo revisar ${codigo} ${nombre}. Intenta de nuevo en un momento.`);
    } finally {
      this.validando.set('');
    }
  }

  // ---------- Promedio meta ----------

  protected async calcularMeta(valor: string): Promise<void> {
    const meta = Number(valor);
    if (!valor || !Number.isFinite(meta)) {
      this.meta.set(null);
      this.resultadoMeta.set(null);
      return;
    }
    const acotada = Math.min(100, Math.max(61, meta));
    this.meta.set(acotada);
    try {
      this.resultadoMeta.set(
        await firstValueFrom(
          this.http.post<PromedioMeta>('/api/promedio/meta', {
            aprobados: this.aprobados(),
            cursando: this.cursando(),
            meta: acotada,
          }),
        ),
      );
    } catch {
      this.resultadoMeta.set({ meta: acotada, notaNecesaria: null, posible: false, mensaje: 'No se pudo calcular. Intenta de nuevo.' });
    }
  }

  // ---------- Tarjeta para compartir ----------

  protected readonly nombreTarjeta = computed(() => (this.ejemplo() ? 'Estudiante de ejemplo' : this.nombre().trim()));
  protected readonly porcentajeCarrera = computed(() => {
    const p = this.analisis()?.clar;
    return p && p.cierre ? Math.min(100, Math.round((p.creditos * 100) / p.cierre)) : 0;
  });
  private readonly textoCompartir = computed(
    () =>
      `Voy por el ${this.porcentajeCarrera()} % de mi carrera en Ingeniería en Ciencias y Sistemas USAC 🌊 ` +
      `Calcula el tuyo en ${typeof location !== 'undefined' ? location.origin : ''}`,
  );

  protected async abrirTarjeta(dialogo: HTMLDialogElement): Promise<void> {
    this.avisoCompartir.set('');
    dialogo.showModal();
    await this.generarTarjeta();
  }

  protected alternarDatoTarjeta(clave: string, marcado: boolean): void {
    this.incluirTarjeta.update((lista) => (marcado ? [...new Set([...lista, clave])] : lista.filter((c) => c !== clave)));
    this.generarTarjeta();
  }

  private pedirTarjeta(formato: 'post' | 'historia'): Promise<Blob> {
    return firstValueFrom(
      this.http.post('/api/tarjeta', {
        aprobados: this.aprobados(),
        cursando: this.cursando(),
        modalidad: this.modalidad(),
        cargaMaxima: this.cargaMaxima(),
        practicas: this.practicas(),
        vacaciones: this.vacaciones(),
        origen: this.origen(),
        plan: this.plan(),
        nombre: this.nombreTarjeta(),
        incluir: this.incluirTarjeta(),
        formato,
      }, { responseType: 'blob' }),
    );
  }

  protected async generarTarjeta(): Promise<void> {
    this.generandoTarjeta.set(true);
    this.historiaBlob = null;
    try {
      const png = await this.pedirTarjeta('post');
      if (this.tarjetaUrl()) URL.revokeObjectURL(this.tarjetaUrl());
      this.tarjetaBlob = png;
      this.tarjetaUrl.set(URL.createObjectURL(png));
      const archivo = new File([png], 'piletazo-mi-avance.png', { type: 'image/png' });
      this.puedeCompartirArchivo.set(typeof navigator.canShare === 'function' && navigator.canShare({ files: [archivo] }));
    } catch {
      this.tarjetaUrl.set('');
    } finally {
      this.generandoTarjeta.set(false);
    }
  }

  /**
   * En el celular se usa el menú de compartir del sistema, que sí adjunta la imagen.
   * En la computadora, WhatsApp y Facebook solo aceptan texto o enlaces desde la web, e Instagram
   * no permite publicar desde la web: se abre lo que se puede y se descarga la imagen para adjuntarla.
   */
  protected async compartirEn(red: 'whatsapp' | 'instagram' | 'facebook'): Promise<void> {
    this.avisoCompartir.set('');
    const sitio = location.origin;
    const nativo = this.puedeCompartirArchivo();
    // La ventana se abre antes de cualquier espera para que el navegador no la bloquee.
    if (!nativo && red === 'whatsapp') {
      window.open('https://wa.me/?text=' + encodeURIComponent(this.textoCompartir()), '_blank', 'noopener');
    } else if (!nativo && red === 'facebook') {
      window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(sitio + '/'), '_blank', 'noopener');
    }
    try {
      let blob = this.tarjetaBlob;
      if (red === 'instagram') {
        this.historiaBlob ??= await this.pedirTarjeta('historia');
        blob = this.historiaBlob;
      }
      if (!blob) return;
      const nombreArchivo = red === 'instagram' ? 'piletazo-historia.png' : 'piletazo-mi-avance.png';
      const archivo = new File([blob], nombreArchivo, { type: 'image/png' });
      if (nativo && navigator.canShare?.({ files: [archivo] })) {
        await navigator.share({ files: [archivo], text: this.textoCompartir() });
        return;
      }
      this.descargar(blob, nombreArchivo);
      this.avisoCompartir.set(
        red === 'whatsapp'
          ? 'Se abrió WhatsApp con el mensaje y se descargó tu imagen: adjúntala en el chat.'
          : red === 'facebook'
            ? 'Se abrió Facebook con el enlace a Piletazo y se descargó tu imagen para que la subas en tu publicación.'
            : 'Instagram no permite publicar desde la web. Se descargó tu historia (1080×1920): pásala a tu celular y súbela en Instagram → Tu historia.',
      );
    } catch {
      this.avisoCompartir.set('No se pudo preparar la imagen. Intenta de nuevo.');
    }
  }

  protected descargarTarjeta(): void {
    if (this.tarjetaBlob) this.descargar(this.tarjetaBlob, 'piletazo-mi-avance.png');
  }

  private descargar(blob: Blob, nombre: string): void {
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = nombre;
    enlace.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  protected cerrarTarjeta(dialogo: HTMLDialogElement): void {
    dialogo.close();
  }

  // ---------- Llevar mis datos a otro dispositivo ----------

  private perfil() {
    return {
      app: 'piletazo',
      version: 1,
      nombre: this.nombre(),
      carne: this.carne(),
      aprobados: this.aprobados(),
      cursando: this.cursando(),
      modalidad: this.modalidad(),
      origen: this.origen(),
      cargaMaxima: this.cargaMaxima(),
      practicas: this.practicas(),
      vacaciones: this.vacaciones(),
    };
  }

  protected exportarPerfil(): void {
    const blob = new Blob([JSON.stringify(this.perfil(), null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = 'piletazo-mis-datos.json';
    enlace.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    this.avisoPerfil.set('Archivo descargado. Ábrelo con «Importar mis datos» en el otro dispositivo.');
  }

  protected async importarArchivo(evento: Event): Promise<void> {
    const archivo = (evento.target as HTMLInputElement).files?.[0];
    if (!archivo) return;
    try {
      this.aplicarPerfil(JSON.parse(await archivo.text()));
      this.avisoPerfil.set('Datos importados.');
    } catch {
      this.avisoPerfil.set('Ese archivo no es un perfil de Piletazo.');
    }
    (evento.target as HTMLInputElement).value = '';
  }

  /** El perfil va en el fragmento (#) del enlace: el navegador nunca lo envía al servidor. */
  protected async copiarEnlacePerfil(): Promise<void> {
    const bytes = new TextEncoder().encode(JSON.stringify(this.perfil()));
    let binario = '';
    bytes.forEach((b) => (binario += String.fromCharCode(b)));
    const codigo = btoa(binario).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    const enlace = `${location.origin}/#perfil=${codigo}`;
    try {
      await navigator.clipboard.writeText(enlace);
      this.avisoPerfil.set('Enlace copiado. Contiene tus datos: compártelo solo contigo.');
    } catch {
      this.avisoPerfil.set('No se pudo copiar el enlace.');
    }
  }

  private importarDesdeEnlace(): void {
    const hash = typeof location !== 'undefined' ? location.hash : '';
    if (!hash.startsWith('#perfil=')) return;
    try {
      const base64 = hash.slice(8).replace(/-/g, '+').replace(/_/g, '/');
      const binario = atob(base64 + '='.repeat((4 - (base64.length % 4)) % 4));
      const bytes = Uint8Array.from(binario, (c) => c.charCodeAt(0));
      this.aplicarPerfil(JSON.parse(new TextDecoder().decode(bytes)));
      this.avisoPerfil.set('Datos importados desde el enlace.');
    } catch {
      this.avisoPerfil.set('El enlace no contiene un perfil válido.');
    }
    history.replaceState(null, '', location.pathname);
  }

  private aplicarPerfil(p: Record<string, unknown>): void {
    if (p['app'] !== 'piletazo' || !Array.isArray(p['aprobados'])) throw new Error('perfil inválido');
    this.ejemplo.set(false);
    this.nombre.set(String(p['nombre'] ?? ''));
    this.carne.set(String(p['carne'] ?? ''));
    this.aprobados.set(p['aprobados'] as CursoAprobado[]);
    this.cursando.set(Array.isArray(p['cursando']) ? (p['cursando'] as string[]) : []);
    if (p['modalidad'] === 'eps' || p['modalidad'] === 'tesis') this.modalidad.set(p['modalidad']);
    if (p['origen'] === 'traslado' || p['origen'] === 'clar2022' || p['origen'] === 'clar2025') this.origen.set(p['origen']);
    if (typeof p['cargaMaxima'] === 'number') this.cargaMaxima.set(p['cargaMaxima']);
    if (p['practicas'] === 1 || p['practicas'] === 2) this.practicas.set(p['practicas']);
    if (p['vacaciones'] === 0 || p['vacaciones'] === 1 || p['vacaciones'] === 2) this.vacaciones.set(p['vacaciones']);
    this.editandoEntrada.set(false);
  }

  protected quitarCursando(): void {
    this.cursando.set([]);
    this.errorCursando.set('');
  }

  protected responderPermiso(valor: 'si' | 'no'): void {
    guardarConsentimiento(valor);
    this.consentimiento.set(valor);
  }

  protected olvidar(): void {
    olvidarTodo();
    this.ejemplo.set(false);
    this.cursando.set([]);
    this.errorCursando.set('');
    this.cursosAntesDelEjemplo = [];
    this.consentimiento.set(null);
    this.nombre.set('');
    this.carne.set('');
    this.aprobados.set([]);
    this.texto.set('');
    this.nombreArchivo.set('');
    this.cargaMaxima.set(CARGA_POR_DEFECTO);
    this.practicas.set(1);
    this.vacaciones.set(0);
    this.modalidad.set('eps');
    this.origen.set('traslado');
    this.editandoEntrada.set(false);
  }

  protected cambiarCarga(valor: string): void {
    const n = Number(valor);
    if (Number.isFinite(n)) this.cargaMaxima.set(Math.min(45, Math.max(0, Math.round(n))));
  }

  protected readonly cursoCorto = (c: { codigo: string; nombre: string }) => `${c.codigo} ${c.nombre}`;

  protected imprimir(): void {
    window.print();
  }

  /** El PDF lo genera la API de Python y se descarga directamente. */
  protected async descargarPdf(): Promise<void> {
    if (this.aprobados().length === 0 || this.descargando()) return;
    this.descargando.set(true);
    this.errorPdf.set('');
    try {
      const pdf = await firstValueFrom(
        this.http.post('/api/reporte', {
          aprobados: this.aprobados(),
          modalidad: this.modalidad(),
          cargaMaxima: this.cargaMaxima(),
          practicas: this.practicas(),
          vacaciones: this.vacaciones(),
          cursando: this.cursando(),
          origen: this.origen(),
          plan: this.plan(),
          nombre: this.nombre().trim(),
          carne: this.carne().trim(),
        }, { responseType: 'blob' }),
      );
      const url = URL.createObjectURL(pdf);
      const enlace = document.createElement('a');
      enlace.href = url;
      enlace.download = `piletazo-${this.carne().trim().replace(/[^\w-]/g, '') || 'reporte'}.pdf`;
      enlace.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch {
      this.errorPdf.set('No se pudo generar el PDF. Puedes usar «Imprimir» y guardar como PDF.');
    } finally {
      this.descargando.set(false);
    }
  }

  protected porcentaje(valor: number, total: number): number {
    return total > 0 ? Math.min(100, (valor / total) * 100) : 0;
  }

  /** '0101' → '0101 Área Matemática Básica 1', '0039|0031' → '… ó …', '200CR' → '200 créditos'. */
  protected readonly describir = (prerrequisito: string): string => {
    const cr = /^(\d+)CR$/.exec(prerrequisito);
    if (cr) return `${cr[1]} créditos`;
    const catalogo = this.respuesta()?.catalogo ?? {};
    return prerrequisito
      .split('|')
      .map((c) => (catalogo[c] ? `${c} ${catalogo[c]}` : c))
      .join(' ó ');
  };

  protected tituloCurso(r: CursoRed): string {
    const lineas = [`${r.curso.codigo} ${r.curso.nombre}`, `${r.curso.creditos} ${this.unidad()}`];
    if (r.curso.prerrequisitos.length) {
      lineas.push('Prerrequisitos: ' + r.curso.prerrequisitos.map(this.describir).join(', '));
    }
    if (r.faltantes.length) {
      lineas.push('Te falta: ' + r.faltantes.map(this.describir).join(', '));
    }
    return lineas.join('\n');
  }

  // ---------- Contacto ----------

  private cuerpoCorreo(): string {
    const respuesta = this.correoRespuesta().trim();
    return this.mensaje().trim() + (respuesta ? `\n\nPuedes responderme a: ${respuesta}` : '');
  }

  protected abrirGmail(): void {
    const url = new URL('https://mail.google.com/mail/');
    url.searchParams.set('view', 'cm');
    url.searchParams.set('fs', '1');
    url.searchParams.set('to', CORREO);
    url.searchParams.set('su', ASUNTO);
    url.searchParams.set('body', this.cuerpoCorreo());
    window.open(url.toString(), '_blank', 'noopener');
  }

  protected enlaceCorreo(): string {
    return `mailto:${CORREO}?subject=${encodeURIComponent(ASUNTO)}&body=${encodeURIComponent(this.cuerpoCorreo())}`;
  }

  protected async copiarCorreo(): Promise<void> {
    try {
      await navigator.clipboard.writeText(CORREO);
      this.copiado.set(true);
      setTimeout(() => this.copiado.set(false), 2000);
    } catch {}
  }

  private observarSecciones(): void {
    this.observador?.disconnect();
    if (typeof IntersectionObserver === 'undefined') return;
    this.observador = new IntersectionObserver(
      (entradas) => {
        const visible = entradas
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
        if (visible) this.seccionActiva.set(visible.target.id);
      },
      { rootMargin: '-15% 0px -70% 0px' },
    );
    for (const s of this.seccionesVisibles()) {
      const el = document.getElementById(s.id);
      if (el) this.observador.observe(el);
    }
  }

  private async leer(cuerpo: { texto?: string; html?: string }, sinCursos: string): Promise<void> {
    this.leyendo.set(true);
    this.error.set('');
    try {
      const { aprobados, avisos } = await firstValueFrom(
        this.http.post<{ aprobados: CursoAprobado[]; avisos?: Avisos }>('/api/cursos/leer', cuerpo),
      );
      this.avisos.set(avisos ?? null);
      if (aprobados.length === 0) {
        this.error.set(sinCursos);
        return;
      }
      this.establecer(aprobados);
    } catch {
      this.error.set('No se pudo conectar con el servidor de la calculadora. Intenta de nuevo en un momento.');
    } finally {
      this.leyendo.set(false);
    }
  }

  private establecer(cursos: CursoAprobado[]): void {
    this.ejemplo.set(false);
    this.cursosAntesDelEjemplo = [];
    this.cursandoAntesDelEjemplo = [];
    this.error.set('');
    const nuevos = new Set(cursos.map((c) => c.codigo));
    this.cursando.update((lista) => lista.filter((c) => !nuevos.has(c)));
    this.aprobados.set(cursos);
    this.editandoEntrada.set(false);
  }
}
