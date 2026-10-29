import { CursoAprobado } from './modelos';

export type Consentimiento = 'si' | 'no' | null;

export interface DatosGuardados {
  nombre: string;
  carne: string;
  aprobados: CursoAprobado[];
  cargaMaxima: number;
  vista: '2021' | '2022';
  practicas?: 1 | 2;
  vacaciones?: 0 | 1 | 2;
  modalidad?: 'eps' | 'tesis';
  origen?: 'traslado' | 'clar2022';
  cursando?: string[];
}

const CLAVE_DATOS = 'clar-calculadora:datos';
const CLAVE_CONSENTIMIENTO = 'clar-calculadora:consentimiento';
// La primera versión guardaba los cursos sin preguntar; se recuperan una vez y se borran.
const CLAVE_ANTERIOR = 'clar-calculadora:aprobados';

export function leerConsentimiento(): Consentimiento {
  const valor = leer(CLAVE_CONSENTIMIENTO);
  return valor === 'si' || valor === 'no' ? valor : null;
}

export function guardarConsentimiento(valor: 'si' | 'no'): void {
  escribir(CLAVE_CONSENTIMIENTO, valor);
  if (valor === 'no') borrar(CLAVE_DATOS);
}

export function leerDatos(): Partial<DatosGuardados> | null {
  if (leerConsentimiento() === 'si') {
    const datos = leer(CLAVE_DATOS);
    if (datos) return parsear(datos);
  }
  const anterior = leer(CLAVE_ANTERIOR);
  if (anterior) {
    borrar(CLAVE_ANTERIOR);
    const aprobados = parsear(anterior);
    return Array.isArray(aprobados) ? { aprobados } : null;
  }
  return null;
}

export function guardarDatos(datos: DatosGuardados): void {
  escribir(CLAVE_DATOS, JSON.stringify(datos));
}

export function olvidarTodo(): void {
  borrar(CLAVE_DATOS);
  borrar(CLAVE_CONSENTIMIENTO);
  borrar(CLAVE_ANTERIOR);
}

function leer(clave: string): string | null {
  try {
    return localStorage.getItem(clave);
  } catch {
    return null;
  }
}

function escribir(clave: string, valor: string): void {
  try {
    localStorage.setItem(clave, valor);
  } catch {}
}

function borrar(clave: string): void {
  try {
    localStorage.removeItem(clave);
  } catch {}
}

function parsear(texto: string) {
  try {
    return JSON.parse(texto);
  } catch {
    return null;
  }
}
