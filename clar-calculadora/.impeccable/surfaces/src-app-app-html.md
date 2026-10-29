---
version: 1
slug: "src-app-app-html"
primary_target: "src/app/app.html"
related_targets: ["src/app/app.css","src/app/app.ts"]
---

# Superficie: Calculadora CLAR (pantalla principal)

Modo: Operate. Estudiante de Sistemas carga su historial, lee su situación en ambos pensums, decide qué asignarse y genera un reporte imprimible.

Requisitos confirmados: perfil (nombre, carné) guardado solo con consentimiento explícito; recomendación de próximo semestre con carga máxima 30 CLAR ajustable; proyección de créditos al aprobar los obligatorios pendientes; selector de pensum (anterior / CLAR 2022); áreas Social Humanística e Idioma Técnico; reporte PDF por diálogo de impresión; footer "Desarrollado por: Mariano Rac" → https://akamariano.github.io/ y sugerencias por correo a marianoracnoguera@gmail.com. Sin logos oficiales.

## Direction contract

THESIS: La carrera leída como un pipeline de compilación: diez etapas (semestres) que pasan, corren o esperan. Rechaza el dashboard claro de tarjetas iguales con un acento azul.

OWN-WORLD: Suelo grafito #0d1117, paneles #151a22 separados por costuras de 1px #262c36, un escalón de elevación #1b212b. Acentos de sintaxis solo para estado: verde aprobado, azul disponible/acción, ámbar afectado o pendiente, rojo pérdida/destructivo, violeta para cifras de créditos. Geist para la interfaz, Geist Mono solo para códigos de curso y cifras.

STORY: El estudiante pega su historial, ve de inmediato créditos y etapa actual, entiende qué perdió o ganó con el cambio, obtiene la carga recomendada y la imprime.

FIRST VIEWPORT: Riel izquierdo con navegación por secciones, perfil y acción de reporte. Área principal: barra de créditos con proyección, el pipeline de 10 semestres a todo el ancho, debajo dos paneles: próximo semestre (acción principal) y áreas. Entrada de datos colapsable cuando ya hay datos.

FORM: Consola de desarrollador oscura (challenger, catalogId digital-design-canon-dark-first-developer-console). seed:a954bb51b30f2209

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
