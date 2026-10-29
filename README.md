# Piletazo

**Tu camino al cierre de pensum en Ingeniería en Ciencias y Sistemas (FIUSAC, USAC).**

### 🌊 Úsalo en línea: **[piletazogt.vercel.app](https://piletazogt.vercel.app)**

En la Facultad de Ingeniería, cerrar pensum se celebra con el *piletazo*. Piletazo es una app web que te ayuda a llegar ahí: cargas tus cursos aprobados y ves cuánto llevas, qué te conviene asignarte el próximo semestre y en qué semestre cerrarías.

> Herramienta **no oficial**. Confirma siempre tu situación con Control Académico de la Facultad de Ingeniería.

© 2026 **Mariano Roberto Rac Noguera**. Todos los derechos reservados. Consulta [Propiedad intelectual](#propiedad-intelectual) y el archivo [LICENSE](LICENSE).

![Logo de Piletazo](Logo/piletazo-horizontal-oscuro.svg)

---

## Propósito

Piletazo nació como un **proyecto personal**: lo hice para calcular y verificar mi propio futuro en la facultad después del cambio al pensum CLAR 2022. Al ver que a mis compañeros les servía lo mismo, lo convertí en una herramienta para cualquier estudiante de la carrera:

- **Si te trasladaron del pensum anterior al CLAR 2022:** cuántos créditos conservas, qué cursos cambiaron de valor en créditos, cuáles dejaste de poder asignarte por los nuevos prerrequisitos y cuáles se te desbloquearon.
- **Si empezaste en CLAR 2022:** tu avance por semestre, tus áreas con requisito, los cursos que te convienen el próximo semestre y las rutas posibles para cerrar.
- **Próximamente:**
  - Las **demás carreras de la Facultad de Ingeniería**: Civil, Industrial, Mecánica, Eléctrica, Química y el resto, cada una con su red de pensum.
  - Soporte para el pensum **CLAR 2025**.
  - Un plan **manual con arrastrar y soltar (drag and drop)**: acomodar tú mismo los cursos en cada semestre y escuela de vacaciones restante.

## Qué hace

| Función | Descripción |
|---|---|
| Carga de cursos | Pegas la tabla de *Cursos aprobados* del portal, o subes la red curricular guardada como `.html` o un `.txt`. |
| Créditos en ambos pensums | Suma en el pensum anterior (cierre 250) y en CLAR 2022 (cierre 300 CLAR), con la equivalencia curso por curso. |
| Proyección | Muestra a cuántos créditos llegarías si apruebas todos los obligatorios pendientes y cuántos optativos te faltarían. |
| Cambios del traslado | Muestra los cursos que pierdes o ganas por los nuevos prerrequisitos y los demás cambios de prerrequisitos. |
| Áreas con requisito | Social Humanística (10 créditos antes; 8 de 10 CLAR ahora) e Idioma Técnico. |
| Modalidad de graduación | **EPS** suma el 7999 Seminario de Investigación E.P.S. como obligatorio. **Tesis** solo lleva el 0799 Seminario de Investigación. |
| Recomendación | Propone cursos para el próximo semestre con carga máxima ajustable (30 CLAR por defecto). Prioriza los obligatorios que abren más camino, luego lo que falte de áreas y después optativos del área de Sistemas. |
| Rutas posibles | Simula semestre a semestre hasta cerrar, con prácticas finales de 6 meses o 1 año y 0, 1 o 2 cursos por escuela de vacaciones (junio y diciembre). Respeta el máximo de 4 horas de clase magistral por escuela: 2 h por curso; 4 h para Matemática Básica 2 e Intermedia 1. |
| Red curricular | Muestra la red del pensum, con distintivo **OB** en los cursos obligatorios y el estado de cada uno (aprobado, disponible o bloqueado). |
| Reporte | Se descarga en **PDF**, generado por el backend, o se imprime desde el navegador. |
| Perfil | Guarda tu nombre, carné y cursos en tu navegador, solo si lo aceptas. |
| Contacto | Formulario con asunto automático *Calculadora CLAR*. Se abre en Gmail o en tu app de correo. |

## Cómo funciona

```
CalculoClar/
├── backend/            API en Python (FastAPI): toda la lógica
│   ├── clar/
│   │   ├── datos/          redes curriculares en JSON (pensum anterior y CLAR 2022)
│   │   ├── pensums.py      carga de las redes y modalidad de graduación
│   │   ├── entrada.py      lectura del texto del portal y del HTML de la red
│   │   ├── analisis.py     créditos, equivalencias, prerrequisitos y áreas
│   │   ├── recomendacion.py  próximo semestre
│   │   ├── rutas.py        simulación hasta el cierre
│   │   ├── reporte_pdf.py  reporte PDF (ReportLab)
│   │   └── api.py          endpoints y servidor de la página compilada
│   └── tests/          pruebas con pytest
├── clar-calculadora/   interfaz en Angular (solo presentación, consume la API)
├── Logo/               logo en todas sus versiones y el script que lo genera
├── 2021/               imágenes del pensum anterior (la página guardada del portal no se publica)
└── CLAR_2022/          imagen de la red CLAR 2022 publicada (fuente de datos)
```

**Flujo:**

1. La página envía el texto o el HTML a `POST /api/cursos/leer` y recibe la lista de cursos aprobados.
2. Con esa lista, la modalidad, la carga máxima y la duración de prácticas, llama a `POST /api/calculo`. Recibe el análisis completo, la recomendación y las tres rutas (0, 1 y 2 cursos por vacaciones).
3. `POST /api/reporte` devuelve el PDF.

La documentación interactiva de la API queda en `/docs` cuando el servidor está corriendo.

**Privacidad:**

- Los cursos se envían al servidor solo para calcular; no se almacenan.
- El nombre y el carné nunca salen del navegador, salvo en el PDF que tú pides.
- El guardado local requiere tu permiso explícito y se borra con *Borrar mis datos*.
- El sitio cuenta visitas con Vercel Web Analytics: sin cookies y sin datos personales, solo páginas vistas, país y tipo de dispositivo.

## Correr en local

Requisitos: Python 3.9+ y Node 20+.

```bash
# 1. Backend
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt   # incluye uvicorn y pytest
.venv/bin/uvicorn clar.api:app --host 127.0.0.1 --port 8010

# 2. Frontend (en otra terminal)
cd clar-calculadora
npm install
npm start          # http://localhost:4200 (el proxy envía /api al puerto 8010)
```

Pruebas:

```bash
cd backend && .venv/bin/python -m pytest          # lógica y API
cd clar-calculadora && npm test -- --watch=false  # interfaz
```

### Un solo servidor (producción)

FastAPI sirve también la página compilada de Angular, así que basta con publicar un servicio:

```bash
cd clar-calculadora && npx ng build
cd ../backend && .venv/bin/uvicorn clar.api:app --host 0.0.0.0 --port 8000
```

Variables opcionales:

- `CLAR_FRONTEND`: ruta a la carpeta `browser` compilada.
- `CLAR_CORS`: orígenes permitidos, separados por comas.
- `PILETAZO_URL` y `GOOGLE_SITE_VERIFICATION`: ver [Aparecer en Google](#aparecer-en-google).

## Publicar gratis en Vercel

El proyecto está listo para el plan **Hobby** de Vercel, que es gratis para proyectos personales sin fines comerciales:

- **Página:** Angular se compila y se sirve como archivos estáticos desde la red de Vercel, con `404.html` como página de error.
- **API:** FastAPI corre como **función de Python** (`api/index.py`) en el mismo dominio, así que la página llama a `/api/...` sin configurar nada más.
- **Buscadores:** `robots.txt` y `sitemap.xml` también los responde la función.
- **Configuración:** está en `vercel.json`, `requirements.txt` (raíz) y `.vercelignore`.

### Opción A: desde GitHub (recomendada)

1. Sube el proyecto a un repositorio de GitHub.
2. Entra a [vercel.com](https://vercel.com), crea tu cuenta con GitHub y pulsa **Add New → Project**.
3. Importa el repositorio. No cambies nada: Vercel lee `vercel.json` (instalación, build y carpeta de salida).
4. Opcional: en **Environment Variables** agrega `GOOGLE_SITE_VERIFICATION`, y `PILETAZO_URL` si usas un dominio propio. Sin `PILETAZO_URL` se usa el dominio de Vercel automáticamente.
5. Pulsa **Deploy**. Quedará en `https://<nombre-del-proyecto>.vercel.app`.

Cada `git push` a la rama principal publica una versión nueva. Los pull requests generan vistas previas.

### Opción B: desde la terminal

```bash
npm i -g vercel
vercel login
vercel          # vista previa
vercel --prod   # producción
```

### Límites del plan gratis

Para el uso de una herramienta como esta no deberían ser un problema: ancho de banda mensual incluido y funciones con hasta 30 s por petición (los cálculos tardan menos de un segundo). El plan Hobby es **solo para uso no comercial**; si algún día cobras por la app, hay que pasar a un plan de pago.

## Aparecer en Google

La app ya incluye lo necesario para que Google la encuentre con búsquedas como *ingeniería USAC*, *sistemas USAC*, *red de pensum USAC* o *pensum CLAR 2022*:

- **Archivos para buscadores:**
  - `GET /robots.txt` permite indexar la página y bloquea `/api/` y `/docs`.
  - `GET /sitemap.xml` lista la página principal.
  - Ambos se generan en el backend con el dominio público.
- **Metadatos:**
  - Título y descripción con esas palabras clave.
  - Enlace canónico.
  - Open Graph y Twitter Card, con la imagen `og-imagen.png` de 1200×630.
  - Manifiesto web.
- **Datos estructurados** (JSON-LD de schema.org): `WebApplication` educativa, con el autor y la USAC como tema.
- **Contenido inicial en el HTML:** los buscadores leen el propósito de la app aunque no ejecuten JavaScript.
- **Página 404 propia** (`404.html`): una ola se lleva la página y muestra *«Error: ruta no encontrada o recurso no disponible»*. Responde con el código 404 real; la API responde 404 en JSON.

### Pasos al publicar

1. **Publica el sitio** en un dominio público ([Vercel](#publicar-gratis-en-vercel), Render, Railway u otro) y define estas variables:
   ```bash
   PILETAZO_URL=https://tu-dominio.com           # para robots, sitemap, canonical y Open Graph
   GOOGLE_SITE_VERIFICATION=codigo-de-google     # opcional: verificación por etiqueta meta
   ```
2. **Verifica la propiedad** en [Google Search Console](https://search.google.com/search-console):
   - Agrega el sitio.
   - Elige *Etiqueta HTML* y copia solo el valor de `content` en `GOOGLE_SITE_VERIFICATION`. También puedes verificar por DNS.
3. **Envía el sitemap:** en *Sitemaps*, envía `https://tu-dominio.com/sitemap.xml`.
4. **Pide la indexación:** en *Inspección de URLs*, pide indexar la página principal.

Google decide si muestra el sitio y en qué posición; puede tardar días o semanas. Ayuda compartir el enlace, por ejemplo en grupos de la carrera o en tu sitio personal.

## Cómo se creó

- **Datos:**
  - La red del pensum anterior (códigos, créditos, prerrequisitos y obligatorios) se extrajo automáticamente de la página de red curricular guardada desde el portal. Esa página no se publica en el repositorio porque contiene datos personales.
  - La red CLAR 2022 se transcribió a mano desde la imagen publicada por la Facultad (`CLAR_2022/RED_CLAR_2022.png`). Si encuentras un error, corrígelo en `backend/clar/datos/pensum_2022.json` o avísame.
- **Lógica:**
  - Empezó en TypeScript dentro de Angular y luego se trasladó a un backend en Python con FastAPI.
  - Las pruebas usan un historial de ejemplo basado en un caso real, sin notas ni datos personales.
- **Interfaz:**
  - Hecha en Angular 22 con componentes standalone y signals.
  - Tema oscuro tipo consola de desarrollador, con profundidad y la paleta azul, celeste y aqua de la marca.
  - La guía de diseño está en `clar-calculadora/DESIGN.md`.
- **Logo:**
  - Una ola rompiendo, vista de lado, hecha de 0s y 1s: el piletazo contado en el idioma de Sistemas.
  - Se genera con `Logo/generar_logo.py`, y `Logo/index.html` muestra todas las versiones.

## Supuestos y pendientes de confirmar

- **Escuelas de vacaciones:** la app supone que cualquier curso disponible puede ofrecerse en ellas.
- **Idioma Técnico en CLAR:** no está confirmado si los Idiomas Técnicos sustituyen la constancia de nivel 12 de CALUSAC.
- **Créditos extracurriculares:** no está confirmado si cuentan para los requisitos por créditos del pensum anterior.

## Propiedad intelectual

© 2026 **Mariano Roberto Rac Noguera**. Todos los derechos reservados.

Piletazo es obra original de Mariano Roberto Rac Noguera:

- su código fuente (frontend en Angular y backend en Python);
- su diseño e interfaz;
- sus textos;
- su nombre;
- su logo: la ola de 0s y 1s y todas sus versiones en [`Logo/`](Logo/).

Está protegido por la legislación de derecho de autor y propiedad intelectual de Guatemala y por los tratados internacionales aplicables.

| Permitido | No permitido sin autorización escrita del autor |
|---|---|
| Usar la app para consultar tu propio avance académico | Copiar, modificar o crear obras derivadas del código, el diseño o el logo |
| Ver y leer el código en este repositorio | Distribuir, publicar, sublicenciar o vender el software o partes de él |
| | Usar el nombre *Piletazo* o su logo en otro producto o servicio |

**Contenido de terceros**, que conserva sus propios derechos:

- **Redes curriculares:** los cursos, códigos, créditos y prerrequisitos son información publicada por la Facultad de Ingeniería de la USAC.
- **Iconos:** Lucide (licencia ISC).
- **Fuentes:** Geist y Geist Mono (SIL Open Font License 1.1).
- **Bibliotecas:** las de `package.json` y `requirements.txt`, cada una con su licencia.

Para permisos, licencias o colaboraciones, escríbeme a marianoracnoguera@gmail.com. El texto completo está en [LICENSE](LICENSE).

## Autor

**Mariano Rac**, desarrollador de software.

- Sitio: [akamariano.github.io](https://akamariano.github.io/)
- Sugerencias o información: marianoracnoguera@gmail.com
