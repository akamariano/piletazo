// Después de `ng build`: pone el dominio público en canonical, Open Graph y JSON-LD,
// y la verificación de Google Search Console si está definida.
import { readFileSync, writeFileSync } from 'node:fs';

const archivo = new URL('../dist/clar-calculadora/browser/index.html', import.meta.url);
const dominio =
  process.env.PILETAZO_URL ||
  (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : '');
const sitio = dominio.replace(/\/+$/, '');
const verificacion = (process.env.GOOGLE_SITE_VERIFICATION || '').trim();

let html = readFileSync(archivo, 'utf8').replaceAll('__SITIO__', sitio);
if (verificacion) {
  html = html.replace(
    '<!--__VERIFICACION_GOOGLE__-->',
    `<meta name="google-site-verification" content="${verificacion.replace(/"/g, '')}">`,
  );
}
writeFileSync(archivo, html);
console.log(`index.html listo para ${sitio || '(sin dominio: URLs relativas)'}`);
