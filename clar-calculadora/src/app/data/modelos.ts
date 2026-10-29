export type Area = 'metodologia' | 'computacion' | 'software';

/**
 * Prerrequisitos:
 *  - '0101'       curso aprobado
 *  - '0039|0031'  cualquiera de los cursos
 *  - '200CR'      créditos acumulados mínimos (en el pensum correspondiente)
 */
export interface Curso {
  codigo: string;
  nombre: string;
  creditos: number;
  semestre: number;
  obligatorio: boolean;
  prerrequisitos: string[];
  area?: Area | null;
  diplomado?: string | null;
}

/** Requisito de cierre de un área (social humanística, idioma técnico…). */
export interface RequisitoArea {
  nombre: string;
  cursos: string[];
  unidad: 'creditos' | 'cursos';
  /** null cuando el requisito es solo informativo. */
  minimo: number | null;
  nota: string;
}

export interface CursoAprobado {
  codigo: string;
  nombre: string;
  creditos: number;
  periodo?: string;
  nota?: string;
  observacion?: string;
}

// ---------- Respuesta de la API (/api/calculo) ----------

export type Modalidad = 'eps' | 'tesis';
/** Con qué pensum empezó el estudiante: el anterior (traslado al CLAR) o CLAR 2022 desde el inicio. */
export type Origen = 'traslado' | 'clar2022';
export type EstadoCurso = 'aprobado' | 'disponible' | 'bloqueado';
export type DuracionPracticas = 1 | 2; // semestres: 6 meses o 1 año
export type CursosPorVacaciones = 0 | 1 | 2;

export interface Equivalencia {
  codigo: string;
  nombre: string;
  creditos2021: number;
  creditos2022: number | null;
  diferencia: number;
  periodo?: string | null;
  observacion?: string | null;
}

export interface CursoRed {
  curso: Curso;
  estado: EstadoCurso;
  faltantes: string[];
  prerrequisitos2021: string[] | null;
  agregados: string[];
  quitados: string[];
  /** Podía asignarse con el pensum anterior pero ya no con el CLAR 2022. */
  pierdeDisponibilidad: boolean;
  /** No podía asignarse con el pensum anterior pero sí con el CLAR 2022. */
  ganaDisponibilidad: boolean;
  creditos2021: number | null;
}

export interface CursoArea {
  codigo: string;
  nombre: string;
  creditos: number;
  aprobado: boolean;
}

export interface ProgresoArea {
  area: RequisitoArea;
  cursos: CursoArea[];
  creditos: number;
  aprobados: number;
  logrado: number;
  total: number;
  cumple: boolean | null;
}

export interface ProgresoPensum {
  creditos: number;
  cierre: number;
  red: CursoRed[];
  obligatoriosPendientes: CursoRed[];
  creditosObligatoriosPendientes: number;
  areas: ProgresoArea[];
}

export interface Analisis {
  modalidad: Modalidad;
  aprobados: CursoAprobado[];
  equivalencias: Equivalencia[];
  creditos2021: number;
  creditos2022: number;
  creditosSinEquivalencia: number;
  pierdenDisponibilidad: CursoRed[];
  gananDisponibilidad: CursoRed[];
  cambiosPrerrequisitos: CursoRed[];
  pensum2021: ProgresoPensum;
  pensum2022: ProgresoPensum;
}

export interface CursoRecomendado {
  red: CursoRed;
  razones: string[];
  desbloquea: number;
}

export interface Recomendacion {
  cursos: CursoRecomendado[];
  creditos: number;
  maximo: number;
  fueraDeCarga: CursoRecomendado[];
}

export interface Periodo {
  nombre: string;
  tipo: 'semestre' | 'vacaciones';
  cursos: Curso[];
  creditos: number;
  acumulado: number;
  practicas: 'inicia' | 'continua' | 'termina' | 'inicia-y-termina' | null;
}

export interface Ruta {
  periodos: Periodo[];
  semestres: number;
  cierre: string | null;
  creditosFinales: number;
  bloqueo: string | null;
}

export interface ValidacionCursando {
  codigo: string;
  nombre: string;
  valido: boolean;
  faltantes: string[];
  mensaje: string;
}

export interface RespuestaCalculo {
  analisis: Analisis;
  cursando: { validos: string[]; invalidos: ValidacionCursando[] };
  recomendacion: Recomendacion;
  escenarios: { vacaciones: CursosPorVacaciones; ruta: Ruta }[];
  catalogo: Record<string, string>;
}
