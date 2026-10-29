# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Name
Piletazo, por la tradición del piletazo al cerrar pensum en la Facultad de Ingeniería. Nació como proyecto personal de Mariano Rac para calcular y verificar su propio futuro en la facultad.

## Users
Estudiantes de Ingeniería en Ciencias y Sistemas (carrera 09, FIUSAC, USAC): quienes empezaron con el pensum anterior y fueron trasladados al CLAR 2022, y quienes empezaron directamente en CLAR 2022 y quieren ver su avance. La usan solos, normalmente antes de una asignación de cursos, para entender cuántos créditos tienen, qué perdieron o ganaron con el cambio y qué pueden llevar el próximo semestre. La comparten entre compañeros de la carrera.

## Product Purpose
Convertir el historial de cursos aprobados de un estudiante (copiado del portal o la red curricular guardada) en una lectura clara de su situación en ambos pensums: créditos, equivalencias, requisitos de área, cursos bloqueados o desbloqueados por los nuevos prerrequisitos y una propuesta de cursos para el próximo semestre. Éxito: el estudiante sale sabiendo qué asignarse y qué confirmar con Control Académico.

## Positioning
Cruza el historial real del estudiante con las dos redes curriculares de su carrera (la anterior y la CLAR 2022) y explica el efecto del traslado curso por curso, algo que el portal oficial no muestra.

## Operating Context
- Fuente de datos: tabla "Cursos aprobados" del portal (pegada como texto) o la página de red curricular guardada como `.html`.
- Uso en laptop y en teléfono, casi siempre en periodo de asignación.
- El reporte se descarga en PDF o se imprime para llevarlo a una consulta o compartirlo.

## Capabilities and Constraints
- Angular 22 (componentes standalone, signals) como interfaz; toda la lógica vive en una API de Python (FastAPI) en `../backend`, que también sirve la página compilada.
- Los cursos se envían a la API solo para calcular y no se almacenan. Nombre y carné no salen del navegador salvo en el PDF que el estudiante pide. El guardado local requiere consentimiento explícito.
- Reporte PDF: descarga directa generada por la API (ReportLab) y, como alternativa, diálogo de impresión.
- Origen del estudiante: traslado desde el pensum anterior o CLAR 2022 desde el inicio (oculta cambios y equivalencias).
- Modalidad de graduación: EPS (7999 obligatorio además de 0799) o tesis (solo 0799).
- Próximamente: las demás carreras de Ingeniería de la Facultad, CLAR 2025 y un plan manual con arrastrar y soltar por semestre y escuela de vacaciones.
- Recomendación del próximo semestre: carga máxima por defecto 30 CLAR, ajustable por el estudiante.
- Proyección de créditos si se aprueban todos los obligatorios pendientes.
- Rutas posibles: simulación semestre a semestre hasta el cierre (obligatorios, 300 CLAR y Social Humanística), con Prácticas Finales de 6 meses o 1 año en paralelo y escuelas de vacaciones (junio y diciembre) con 0, 1 o 2 cursos adelantados. Regla de vacaciones: máximo 4 horas de clase magistral; 2 h por curso, 4 h para Matemática Básica 2 (0103) y Matemática Intermedia 1 (0107). Supuesto no confirmado: cualquier curso disponible podría ofrecerse en vacaciones.
- Los optativos sugeridos priorizan las áreas de Sistemas (Metodología, Ciencias de la Computación, Desarrollo de Software).
- La red CLAR 2022 fue transcrita a mano de la red publicada; puede contener errores y debe poder corregirse en `src/app/data/pensum-2022.ts`.
- Pendiente de confirmar con Control Académico: si los Idiomas Técnicos sustituyen la constancia de nivel 12 de CALUSAC en el CLAR; si los créditos extracurriculares cuentan para requisitos por créditos.

## Brand Commitments
- Herramienta no oficial: no usar el escudo, logotipos ni marca de la USAC o FIUSAC.
- Debe decir claramente que no es oficial y que la situación se confirma con Control Académico.
- Footer: "Desarrollado por: Mariano Rac" con enlace a https://akamariano.github.io/ y enlace de sugerencias o información a marianoracnoguera@gmail.com.

## Evidence on Hand
- Red curricular anterior extraída de `../2021/FIUSAC.html`.
- Red CLAR 2022 transcrita de `../CLAR_2022/RED_CLAR_2022.png`.
- Historiales de ejemplo para pruebas en `backend/tests/datos/`, sin notas ni datos personales. Los datos personales reales (página guardada del portal, notas) quedan fuera del repositorio por `.gitignore`.
- No existen testimonios, cifras de uso ni avales oficiales; no inventarlos.

## Product Principles
1. La situación del estudiante primero: créditos y próximos pasos antes que el detalle.
2. Explicar cada cambio con el curso y el prerrequisito concretos, nunca con un veredicto sin razón.
3. Honestidad sobre la incertidumbre: lo transcrito o no confirmado se marca como tal.
4. Privacidad por defecto: nada se guarda sin permiso.
