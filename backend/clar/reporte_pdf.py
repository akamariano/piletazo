"""Reporte en PDF del avance del estudiante (descarga directa desde la página)."""

from __future__ import annotations

from datetime import date
from io import BytesIO
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .analisis import Analisis, describir_prerrequisito
from .pensums import DATOS
from .recomendacion import Recomendacion
from .rutas import Ruta

AZUL = colors.HexColor("#0b2a6f")
CELESTE = colors.HexColor("#0891b2")
LINEA = colors.HexColor("#c7dbe8")
TENUE = colors.HexColor("#55657a")
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

estilos = getSampleStyleSheet()
TITULO = ParagraphStyle("titulo", parent=estilos["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=AZUL, alignment=0, spaceAfter=2)
SUB = ParagraphStyle("sub", parent=estilos["Normal"], fontName="Helvetica", fontSize=9.5, textColor=TENUE, leading=13)
H2 = ParagraphStyle("h2", parent=estilos["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, textColor=AZUL, spaceBefore=12, spaceAfter=5)
TEXTO = ParagraphStyle("texto", parent=estilos["Normal"], fontName="Helvetica", fontSize=9, leading=12.5)
CELDA = ParagraphStyle("celda", parent=TEXTO, fontSize=8.5, leading=11)
DERECHA = ParagraphStyle("derecha", parent=CELDA, alignment=TA_RIGHT)
PIE = ParagraphStyle("pie", parent=SUB, fontSize=8, leading=11)


def _tabla(filas: List[list], anchos: List[float], total: bool = False) -> Table:
    t = Table(filas, colWidths=anchos, repeatRows=1)
    estilo = [
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 0), (-1, 0), TENUE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.9, AZUL),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINEA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
    ]
    if total:
        estilo += [("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"), ("LINEABOVE", (0, -1), (-1, -1), 0.9, AZUL)]
    t.setStyle(TableStyle(estilo))
    return t


def _p(texto: str, estilo=CELDA) -> Paragraph:
    return Paragraph(texto.replace("&", "&amp;").replace("<", "&lt;"), estilo)


def generar_pdf(
    analisis: Analisis,
    recomendacion: Recomendacion,
    ruta: Optional[Ruta],
    origen: str,
    nombre: str,
    carne: str,
    practicas: int,
    vacaciones: int,
    hoy: Optional[date] = None,
) -> bytes:
    hoy = hoy or date.today()
    salida = BytesIO()
    doc = SimpleDocTemplate(
        salida, pagesize=letter, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm, bottomMargin=16 * mm,
        title="Piletazo · Reporte", author="Piletazo",
    )
    ancho = doc.width
    traslado = origen == "traslado"
    p22, p21 = analisis.pensum2022, analisis.pensum2021
    partes: list = []

    titulo = "Reporte de traslado al pensum CLAR 2022" if traslado else "Reporte de avance en el pensum CLAR 2022"
    cabecera = Table(
        [[
            Image(str(DATOS / "logo.png"), width=15 * mm, height=15 * mm),
            [Paragraph(f"Piletazo · {titulo}", TITULO),
             Paragraph(f"Ingeniería en Ciencias y Sistemas · generado el {hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}", SUB)],
            [Paragraph(f"<b>{_esc(nombre) or '—'}</b>", ParagraphStyle('n', parent=DERECHA, fontSize=10)),
             Paragraph(f"Carné {_esc(carne) or '—'}", ParagraphStyle('c', parent=DERECHA, textColor=TENUE)),
             Paragraph("EPS" if analisis.modalidad == "eps" else "Tesis de investigación", ParagraphStyle('m', parent=DERECHA, textColor=TENUE))],
        ]],
        colWidths=[19 * mm, ancho - 19 * mm - 48 * mm, 48 * mm],
    )
    cabecera.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (0, 0), 0),
                                  ("LINEBELOW", (0, 0), (-1, 0), 0.6, LINEA), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    partes.append(cabecera)

    # Créditos
    partes.append(Paragraph("Créditos", H2))
    filas = [["Pensum", "Aprobados", "Cierre", "Obligatorios pendientes", "Con obligatorios aprobados"],
             ["CLAR 2022", p22.creditos, p22.cierre, f"{len(p22.obligatorios_pendientes)} ({p22.creditos_obligatorios_pendientes} CLAR)",
              p22.creditos + p22.creditos_obligatorios_pendientes]]
    if traslado:
        filas.append(["Anterior al CLAR", p21.creditos, p21.cierre,
                      f"{len(p21.obligatorios_pendientes)} ({p21.creditos_obligatorios_pendientes} créditos)",
                      p21.creditos + p21.creditos_obligatorios_pendientes])
    partes.append(_tabla(filas, [ancho * x for x in (0.26, 0.14, 0.12, 0.26, 0.22)]))
    etiqueta = "sin equivalencia en la red CLAR" if traslado else "de cursos fuera de la red CLAR"
    partes.append(Spacer(0, 4))
    partes.append(Paragraph(f"Créditos {etiqueta}: {analisis.creditos_sin_equivalencia}.", TEXTO))

    # Recomendación
    filas = [["Código", "Curso", "Motivo", "CLAR"]]
    filas += [[c.red.curso.codigo, _p(c.red.curso.nombre + (" (OB)" if c.red.curso.obligatorio else "")), _p(" · ".join(c.razones)),
               c.red.curso.creditos] for c in recomendacion.cursos]
    filas.append(["", "Total", "", recomendacion.creditos])
    partes.append(KeepTogether([Paragraph(f"Recomendación para el próximo semestre (máximo {recomendacion.maximo:g} CLAR)", H2),
                                _tabla(filas, [ancho * x for x in (0.1, 0.38, 0.42, 0.1)], total=True)]))

    # Ruta
    if ruta:
        detalle = (f"prácticas finales de {'6 meses' if practicas == 1 else '1 año'}, "
                   + ("sin escuelas de vacaciones" if vacaciones == 0 else f"{vacaciones} curso(s) por escuela de vacaciones"))
        resumen = (f"Cierre estimado: <b>{ruta.cierre}</b> · {ruta.semestres} semestres · {ruta.creditos_finales} CLAR."
                   if ruta.cierre else _esc(ruta.bloqueo or ""))
        filas = [["Periodo", "Cursos", "CLAR", "Acumulado"]]
        for p in ruta.periodos:
            cursos = ", ".join(f"{c.codigo} {c.nombre}" for c in p.cursos)
            if p.practicas:
                cursos += (" · " if cursos else "") + "Prácticas finales"
            filas.append([_p(p.nombre), _p(cursos), p.creditos, p.acumulado])
        partes.append(Paragraph(f"Ruta para cerrar ({detalle})", H2))
        partes.append(Paragraph(resumen, TEXTO))
        partes.append(Spacer(0, 4))
        partes.append(_tabla(filas, [ancho * x for x in (0.2, 0.58, 0.09, 0.13)]))

    # Áreas
    filas = [["Área"] + (["Pensum anterior"] if traslado else []) + ["CLAR 2022"]]
    for i, a in enumerate(p22.areas):
        fila = [a.area.nombre]
        if traslado:
            b = p21.areas[i]
            fila.append(f"{b.logrado} / {b.area.minimo} {'créditos' if b.area.unidad == 'creditos' else 'cursos'} "
                        f"({'completa' if b.cumple else 'pendiente'})")
        fila.append(f"{a.logrado} / {a.area.minimo} CLAR ({'completa' if a.cumple else 'pendiente'})" if a.area.minimo is not None
                    else f"{a.aprobados} de {len(a.cursos)} cursos ({a.creditos} CLAR)")
        filas.append(fila)
    partes.append(KeepTogether([Paragraph("Áreas con requisito", H2), _tabla(filas, [ancho / len(filas[0])] * len(filas[0]))]))

    if traslado:
        cambios = [f"<b>{r.curso.codigo} {_esc(r.curso.nombre)}:</b> dejarías de poder asignártelo; ahora te falta "
                   f"{_esc(', '.join(describir_prerrequisito(x) for x in r.faltantes))}." for r in analisis.pierden_disponibilidad]
        cambios += [f"<b>{r.curso.codigo} {_esc(r.curso.nombre)}:</b> se te desbloquea con el CLAR 2022." for r in analisis.ganan_disponibilidad]
        if cambios:
            partes.append(Paragraph("Cambios de prerrequisitos que te afectan", H2))
            partes += [Paragraph("• " + c, TEXTO) for c in cambios]

        filas = [["Código", "Curso", "Antes", "CLAR 2022", "Diferencia"]]
        filas += [[e.codigo, _p(e.nombre + ("" if e.creditos2022 is not None else " (sin equivalencia)")), e.creditos2021,
                   "—" if e.creditos2022 is None else e.creditos2022, f"{e.diferencia:+d}" if e.diferencia else "0"]
                  for e in analisis.equivalencias]
        d = analisis.creditos2022 - analisis.creditos2021
        filas.append(["", "Total", analisis.creditos2021, analisis.creditos2022, f"{d:+d}" if d else "0"])
        partes.append(Paragraph("Equivalencia de cursos aprobados", H2))
        partes.append(_tabla(filas, [ancho * x for x in (0.1, 0.54, 0.11, 0.13, 0.12)], total=True))

    partes.append(Spacer(0, 14))
    partes.append(Paragraph(
        "Reporte no oficial generado con Piletazo. Confirma tu situación con Control Académico de la Facultad de Ingeniería. "
        "Desarrollado por Mariano Rac · akamariano.github.io · Sugerencias: marianoracnoguera@gmail.com", PIE))

    def numerar(canvas, documento):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(TENUE)
        canvas.drawRightString(documento.pagesize[0] - 16 * mm, 9 * mm, f"Piletazo · página {documento.page}")
        canvas.restoreState()

    doc.build(partes, onFirstPage=numerar, onLaterPages=numerar)
    return salida.getvalue()


def _esc(texto: str) -> str:
    return (texto or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
