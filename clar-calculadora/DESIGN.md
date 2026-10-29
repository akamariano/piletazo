---
name: Piletazo
description: Consola oscura que lee la carrera de Ciencias y Sistemas como un pipeline de compilación.
colors:
  suelo: "#0d1117"
  panel: "#151a22"
  elevado: "#1b212b"
  elevado-hover: "#222934"
  costura: "#262c36"
  costura-fuerte: "#343b47"
  costura-hover: "#4a5260"
  texto: "#e6edf3"
  texto-2: "#b1bac4"
  tenue: "#8b949e"
  placeholder: "#6e7681"
  accion: "#2f81f7"
  accion-hover: "#4c93f9"
  azul: "#79c0ff"
  azul-fondo: "rgb(121 192 255 / 0.12)"
  verde: "#56d364"
  verde-fondo: "rgb(86 211 100 / 0.12)"
  ambar: "#e3b341"
  ambar-fondo: "rgb(227 179 65 / 0.12)"
  rojo: "#f85149"
  rojo-fondo: "rgb(248 81 73 / 0.12)"
  rojo-texto: "#ffa198"
  cian: "#5eead4"
  celeste: "#38bdf8"
  aqua: "#2dd4bf"
  papel: "#ffffff"
  tinta: "#111111"
typography:
  display:
    fontFamily: "Geist Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "44px"
    fontWeight: 500
    lineHeight: 1.1
    letterSpacing: "-0.03em"
    fontFeature: "tnum"
  headline:
    fontFamily: "Geist, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "24px"
    fontWeight: 600
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Geist, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "15px"
    fontWeight: 600
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Geist, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.55
  body-sm:
    fontFamily: "Geist, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "13px"
    fontWeight: 400
  label:
    fontFamily: "Geist, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "12px"
    fontWeight: 500
  code:
    fontFamily: "Geist Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "12px"
    fontWeight: 400
    fontFeature: "tnum"
  print-body:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "10.5pt"
    fontWeight: 400
    lineHeight: 1.45
rounded:
  chip: "4px"
  sm: "5px"
  radio: "6px"
  pill: "20px"
  full: "50%"
spacing:
  xxs: "2px"
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  xxl: "32px"
components:
  button:
    backgroundColor: "{colors.elevado}"
    textColor: "{colors.texto}"
    typography: "{typography.body}"
    rounded: "{rounded.radio}"
    padding: "8px 14px"
  button-hover:
    backgroundColor: "{colors.elevado-hover}"
  button-primary:
    backgroundColor: "{colors.accion}"
    textColor: "{colors.papel}"
    rounded: "{rounded.radio}"
    padding: "8px 14px"
  button-primary-hover:
    backgroundColor: "{colors.accion-hover}"
  button-danger:
    backgroundColor: "transparent"
    textColor: "{colors.rojo}"
    rounded: "{rounded.radio}"
    padding: "8px 14px"
  button-danger-hover:
    backgroundColor: "{colors.rojo-fondo}"
  input:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.texto}"
    rounded: "{rounded.radio}"
    padding: "8px 10px"
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.texto}"
    rounded: "{rounded.radio}"
    padding: "18px 20px"
  nav-item:
    textColor: "{colors.texto-2}"
    rounded: "{rounded.radio}"
    padding: "7px 10px"
  nav-item-active:
    backgroundColor: "{colors.elevado}"
    textColor: "{colors.texto}"
  status-chip-ok:
    backgroundColor: "{colors.verde-fondo}"
    textColor: "{colors.verde}"
    rounded: "{rounded.pill}"
    padding: "1px 8px"
  status-chip-aviso:
    backgroundColor: "{colors.ambar-fondo}"
    textColor: "{colors.ambar}"
    rounded: "{rounded.pill}"
    padding: "1px 8px"
  status-chip-info:
    backgroundColor: "{colors.azul-fondo}"
    textColor: "{colors.azul}"
    rounded: "{rounded.pill}"
    padding: "1px 8px"
  pipeline-stage:
    backgroundColor: "{colors.suelo}"
    textColor: "{colors.texto}"
    rounded: "{rounded.radio}"
    padding: "10px 10px 9px"
  pipeline-stage-current:
    backgroundColor: "{colors.azul-fondo}"
  course-cell:
    backgroundColor: "{colors.suelo}"
    textColor: "{colors.tenue}"
    rounded: "{rounded.sm}"
    padding: "7px 9px"
  course-cell-approved:
    backgroundColor: "{colors.verde-fondo}"
    textColor: "{colors.texto}"
---

# Design System: Piletazo

## Overview

**Creative North Star: "La consola de compilación"**

La carrera se lee como un pipeline de CI: diez etapas (semestres) que pasan, corren o esperan, cursos que compilan en verde o quedan bloqueados por una dependencia. La interfaz es una consola de desarrollador oscura: suelo grafito, paneles planos separados por costuras de 1px y un único escalón de elevación. Nada flota; la profundidad se dice con tono y borde, no con sombra.

El color es sintaxis, no decoración. Cada acento existe para un estado: verde aprobado, azul disponible o acción, ámbar afectado o pendiente, rojo pérdida o destructivo, cian (aqua claro) para cifras de créditos. La densidad es alta y tabular, como un panel de herramientas que se usa sentado antes de asignarse cursos; la tipografía Geist lleva la interfaz y Geist Mono solo aparece donde hay códigos de curso y números.

El mismo sistema se invierte para el papel: el reporte imprimible abandona el oscuro y pasa a tinta negra sobre blanco, tamaño carta, con reglas finas en puntos tipográficos.

**Key Characteristics:**
- Oscuro por defecto (`color-scheme: dark`), plano, sin sombras de elevación.
- Costuras de 1px como único separador estructural entre paneles, filas y columnas de datos.
- Acentos de estado con su fondo translúcido al 12% como pareja fija.
- Geist Mono con cifras tabulares para todo dato que se compara.
- Un único radio (6px) para casi toda superficie.
- Iconos de trazo Lucide a 1.75px, heredando `currentColor`.

## Colors

Paleta de consola grafito con acentos de resaltado de sintaxis reservados al estado.

### Primary
- **Azul Acción** (`accion`): fondo del botón primario, borde de enfoque de campos, selección de segmentados y escenario activo. Es el único relleno sólido de color en la interfaz; su hover sube a `accion-hover`.
- **Azul Señal** (`azul`): enlaces, códigos de curso, icono de navegación activa, etapa en curso, curso disponible y anillo de `:focus-visible`. Su fondo `azul-fondo` marca la etapa en curso y el chip informativo.

### Secondary
- **Verde Compilado** (`verde`): aprobado, completo, barra de créditos ganados, diferencias positivas. El logotipo tipográfico "C" del riel también va en verde. Fondo `verde-fondo` para cursos aprobados y el veredicto de rutas.
- **Ámbar Advertencia** (`ambar`): afectado por el cambio, requisito de área pendiente, periodos de vacaciones, prerrequisitos faltantes. Fondo `ambar-fondo` en chips de aviso.
- **Rojo Pérdida** (`rojo`): créditos sin equivalencia, diferencias negativas, acción destructiva. Texto de error en `rojo-texto` sobre `rojo-fondo`.

### Tertiary
- **Cian Crédito** (`cian`): exclusivo para cifras de créditos (totales de carga, créditos por periodo y escenario) y para la proyección rayada de la barra de créditos y el interruptor de proyectar.

### Neutral
- **Suelo Grafito** (`suelo`): fondo de página, riel, pozos de barras y celdas de etapa y curso (que se hunden un tono por debajo del panel).
- **Panel** (`panel`): superficie de cada sección y fondo de campos.
- **Elevado** (`elevado`): el único escalón por encima del panel: botón secundario, pestaña activa, navegación activa, escenario elegido, `code` en línea.
- **Costura** (`costura`) y **Costura Fuerte** (`costura-fuerte`): bordes de 1px. La costura separa; la fuerte define controles y celdas de etapa.
- **Texto** (`texto`), **Texto 2** (`texto-2`), **Tenue** (`tenue`): tres niveles de tinta para contenido, descripciones y metadatos.

### Named Rules
**The Syntax Highlight Rule.** Un acento solo aparece si nombra un estado. Verde aprobado, azul disponible o acción, ámbar afectado, rojo pérdida, cian créditos. Ninguna superficie lleva color por adorno.

**The Twelve Percent Rule.** Cada acento de estado tiene una pareja de fondo al 12% de opacidad (`*-fondo`); los bordes coloreados van entre 35% y 65%. Nunca rellenos de estado sólidos.

## Typography

**Display Font:** Geist (con ui-sans-serif, system-ui, Segoe UI)
**Body Font:** Geist
**Label/Mono Font:** Geist Mono (con ui-monospace, SFMono-Regular, Menlo)

**Character:** Una sans geométrica neutra para leer y una mono hermana para los datos; juntas suenan a terminal sin volverse ilegibles. Los pesos se quedan entre 400 y 600.

### Hierarchy
- **Display** (Geist Mono 500, 44px, 1.1, −0.03em, cifras tabulares): la cifra de créditos del medidor; baja a 36px bajo 520px. Cifras secundarias de área a 26px y de datos a 20px.
- **Headline** (600, 24px, −0.02em): nombre del estudiante en la barra superior; 22px en el título de entrada.
- **Title** (600, 15px, −0.01em): títulos de panel; 13–14px en subtítulos de área, cambios y semestre.
- **Body** (400, 15px, 1.55): texto base; descripciones de cabecera limitadas a 68ch, pie a 80ch.
- **Body small** (13–14px): ayudas, notas del medidor, filas de tabla, navegación.
- **Label** (12px, 500 en chips y cabeceras de tabla): `dt` de datos, etiquetas de campo, leyendas, metadatos.
- **Code** (Geist Mono 12px, azul): códigos de curso de cuatro dígitos; 11.5px dentro de la red curricular.

### Named Rules
**The Mono Means Data Rule.** Geist Mono con `tabular-nums` solo para códigos de curso, cifras y el texto pegado del historial. Nunca para títulos ni prosa.

**The No Heavy Weight Rule.** El peso máximo es 600. La jerarquía se construye con tamaño y tinta (texto, texto-2, tenue), no con negritas de 700.

## Layout

Aplicación de una sola pantalla con riel fijo: rejilla de dos columnas, riel de 264px (sticky, alto completo, borde derecho de costura) y área principal de hasta 1280px con 24px arriba y 32px a los lados. Las secciones se apilan con 16px de separación.

El área principal sigue la historia: barra superior (nombre + selector de pensum), panel de créditos con medidor y una tira de cuatro datos separados por costuras verticales que sangra hasta los bordes del panel, el pipeline de 10 etapas a todo el ancho (rejilla de 10 columnas con 14px de hueco y conectores de 14×2px), y debajo dos columnas 1.25fr / 1fr (recomendación y áreas).

Ritmo de espaciado observado: 2, 4, 8, 12, 16, 20, 32px, con 6, 10, 14 y 18px como pasos intermedios frecuentes. Densidad alta: filas de lista de 10px vertical, celdas de tabla de 8×10px.

Responsive:
- **≤1100px:** pipeline a 5 columnas, las dos columnas se apilan.
- **≤860px:** el riel se disuelve (`display: contents`): marca y perfil arriba, la navegación se vuelve una tira horizontal sticky con desplazamiento, las acciones bajan al final en dos columnas. Datos a 2×2, comparativa de rutas a una columna, márgenes de 16px.
- **≤520px:** pipeline a 2 columnas sin conectores, tablas apilables con etiquetas por celda, padding de panel a 16px.

Impresión: el shell se oculta y aparece un reporte carta (márgenes 16mm × 14mm) en tinta `tinta` sobre `papel`, con reglas de 0.5–1.5pt.

## Elevation & Depth

El sistema es plano y tonal. No hay sombras de elevación: la profundidad se expresa con tres tonos (suelo, panel, elevado) y bordes de 1px. Los elementos internos de un panel (etapas, cursos, pozos de barra, pestañas) bajan al tono `suelo`, de modo que se leen como ranuras dentro de la superficie y no como tarjetas encima.

### Shadow Vocabulary
- **Anillo de enfoque de campo** (`box-shadow: 0 0 0 3px rgb(47 129 247 / 0.25)`): solo en campos con foco, junto al borde `accion`.
- **Costura interior activa** (`box-shadow: inset 0 0 0 1px var(--costura-fuerte)`): ítem de navegación activo; es un borde, no una sombra.

### Named Rules
**The Seams Not Shadows Rule.** Las superficies se separan con costuras de 1px y cambio de tono. Si algo necesita destacar, sube a `elevado` o toma un borde de estado; nunca una sombra difusa.

## Shapes

Esquinas apenas suavizadas: un único radio de 6px (`--radio`) para paneles, botones, campos, etapas y avisos. Variantes menores solo donde el elemento es diminuto: 5px en celdas de curso, 4px en chips de periodo, pestañas internas y `code`. Formas totalmente redondas solo con significado: píldoras de estado (20px), interruptor, puntos de obligatorio y marcadores circulares de línea de tiempo y de aviso.

Los bordes son siempre de 1px. El borde discontinuo tiene dos usos fijos: la zona de soltar archivo y el botón destructivo (que pasa a sólido al hover). La proyección de créditos se dibuja con rayas diagonales de 45° en cian.

## Components

### Buttons
Controles de consola, compactos y tranquilos.
- **Shape:** radio de 6px, borde de 1px, 8px × 14px, 14px peso 500, icono de 16px a 8px del texto.
- **Default:** fondo `elevado`, borde `costura-fuerte`, texto `texto`; hover sube a `elevado-hover` con borde `costura-hover`. Transición de 150ms en fondo y borde.
- **Primary:** relleno sólido `accion` con texto blanco; hover a `accion-hover`. Una sola acción primaria por zona ("Generar reporte PDF", "Calcular", "Guardar").
- **Danger:** fondo transparente, texto `rojo`, borde discontinuo rojo al 55%; hover rellena con `rojo-fondo` y el borde se vuelve sólido. Siempre separado 18px del resto de acciones.
- **Disabled:** opacidad 0.45, cursor no permitido.

### Chips
- **Estado:** píldora de 1px × 8px, 12px peso 500, borde `currentColor`, texto del acento y fondo `*-fondo` (ok, aviso, info, baja). La variante tenue no lleva fondo.
- **Curso de periodo:** chip de 4px de radio sobre `suelo`, código en mono tenue y nombre a 12.5px.

### Cards / Containers
- **Corner Style:** 6px.
- **Background:** `panel`.
- **Shadow Strategy:** ninguna; ver Elevation & Depth.
- **Border:** 1px `costura`.
- **Internal Padding:** 18px × 20px (16px en teléfono). Las tiras de datos y las tablas sangran hasta el borde con márgenes negativos.
- **Avisos:** el de guardar usa borde azul al 45% sobre azul al 8%; el veredicto de rutas, borde verde al 40% sobre `verde-fondo`; el error, borde rojo al 40% sobre `rojo-fondo` con texto `rojo-texto`.

### Inputs / Fields
- **Style:** fondo `panel`, borde 1px `costura`, radio 6px, 8px × 10px; placeholder en `placeholder`.
- **Hover:** borde `costura-fuerte`.
- **Focus:** borde `accion` + anillo de 3px azul al 25%.
- **Textarea:** Geist Mono 13px, interlineado 1.6, redimensionable en vertical.
- **Select:** sin apariencia nativa, chevrón SVG en `tenue` a 12px de la derecha.
- **Interruptor:** pista de 34×20px; activado toma cian (pista al 25%, perilla sólida) con transición de 200ms y curva `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Segmentado:** opciones unidas con borde compartido; la elegida toma borde `accion` y fondo azul al 18%.

### Navigation
- **Riel:** ítems de 14px en `texto-2` con icono `tenue` de 16px; hover a fondo `panel`; activo a fondo `elevado` con costura interior y el icono en `azul`. `aria-current="location"`.
- **Teléfono:** tira horizontal sticky con ítems bordeados a 13px y desplazamiento lateral.
- **Pestañas de entrada:** contenedor `suelo` con 3px de holgura; la pestaña activa sube a `elevado`.

### Pipeline de semestres (signature)
Diez celdas sobre `suelo` con borde `costura-fuerte`, icono de estado (círculo vacío, en curso, check), nombre truncado y fracción mono `aprobados/obligatorios`. Completa: borde verde al 55%. En curso: borde azul al 65% y fondo `azul-fondo`. El conector de 2px entre etapas toma el color del estado de la etapa a la que lleva.

### Medidor de créditos (signature)
Cifra display en mono, barra de 10px en pozo `suelo` con relleno con el degradado `ola` (azul → celeste → aqua); la proyección se suma como tramo rayado cian que crece desde la izquierda en 600ms. Debajo, una tira de cuatro datos separados por costuras.

### Red curricular (signature)
Columnas por semestre de celdas de curso (código mono, nombre, créditos). Bloqueado: tenue sobre `suelo`. Disponible: borde azul al 60%. Aprobado: `verde-fondo` con código verde. Un punto de 5px marca obligatorios; un círculo ámbar de 18px en la esquina marca cursos afectados por el cambio; al hover o foco se revelan en mono ámbar los prerrequisitos faltantes.

## Do's and Don'ts

### Do:
- **Do** separar superficies con costuras de 1px (`costura`) y el salto de tono suelo → panel → elevado.
- **Do** emparejar cada acento de estado con su fondo `*-fondo` al 12% y bordes entre 35% y 65%.
- **Do** escribir códigos de curso y cifras en Geist Mono con `tabular-nums`; créditos en `cian`.
- **Do** usar el radio único de 6px salvo en elementos diminutos (4–5px) o formas con significado circular.
- **Do** usar iconos de trazo Lucide de 24×24 a 1.75px heredando `currentColor`.
- **Do** mantener las transiciones en 150–200ms para estados y 600ms con `cubic-bezier(0.16, 1, 0.3, 1)` para barras de progreso, y anularlas con `prefers-reduced-motion`.
- **Do** invertir a tinta sobre papel blanco en impresión, sin fondos oscuros.

### Don't:
- **Don't** usar sombras difusas de elevación ni tarjetas que floten sobre el suelo.
- **Don't** poner color de acento sin un estado que nombrar, ni rellenos sólidos de estado salvo el botón primario.
- **Don't** usar Geist Mono para títulos o prosa.
- **Don't** pasar de peso 600.
- **Don't** usar el escudo, logotipos ni marca de la USAC o FIUSAC; la marca es la "C" tipográfica en mono verde.
- **Don't** convertir la interfaz en un dashboard claro de tarjetas iguales con un acento azul.

## Identidad Piletazo (actualización)

- **Nombre y marca.** La app se llama Piletazo, por la tradición del piletazo al cerrar pensum. El logo es una ola rompiendo, vista de lado, hecha de 0s y 1s; se genera con `../Logo/generar_logo.py`. A 16–40 px se usa la versión de trazo (`favicon.svg`), porque los dígitos dejan de leerse.
- **Paleta de marca.** Azul `#1d4ed8`, celeste `#38bdf8`, aqua `#2dd4bf`, espuma `#ccfbf1`, fondo noche `#0a1a3f`. El degradado `ola` (azul → celeste → aqua) es la firma: barra de créditos, filete superior de cada panel y franja del creador. No se usa morado.
- **Acción.** Los botones primarios llevan el degradado celeste → aqua con texto oscuro `#04202a` (contraste alto); el foco y la selección usan celeste `#22b8e6`.
- **Profundidad.** Luz desde arriba (`brillo`), sombras con desplazamiento y desenfoque (`sombra-panel`, `sombra-elevada`), pozos hundidos para campos y barras (`sombra-pozo`). Lo disponible se eleva; lo bloqueado se hunde.
- **Movimiento.** Tres olas de fondo en desplazamiento lento (12–26 s), entrada escalonada del avance por semestre, llenado de la barra de créditos y paneles que suben al entrar en pantalla desde un estado ya visible. Todo se apaga con `prefers-reduced-motion`.
- **Distintivo OB.** Cada curso obligatorio lleva una placa mono "OB" que toma el color del estado del curso.
