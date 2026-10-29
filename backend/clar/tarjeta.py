"""Tarjeta para compartir el avance (PNG vertical para WhatsApp e historias), con QR al sitio."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

import qrcode
import reportlab
from PIL import Image, ImageDraw, ImageFont

from .analisis import Analisis
from .pensums import DATOS

ANCHO, ALTO = 1080, 1350
FUENTES = Path(reportlab.__file__).parent / "fonts"
FONDO_ARRIBA, FONDO_ABAJO = (10, 26, 63), (13, 17, 23)
AZUL, CELESTE, AQUA = (29, 78, 216), (56, 189, 248), (45, 212, 191)
TEXTO, TEXTO_2, TENUE = (240, 249, 255), (177, 186, 196), (139, 148, 158)
SITIO_AUTOR = "akamariano.github.io"


def _fuente(tam: int, negrita: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FUENTES / ("VeraBd.ttf" if negrita else "Vera.ttf")), tam)


def _mezcla(a: Tuple[int, int, int], b: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))  # type: ignore[return-value]


def _degradado_ola(t: float) -> Tuple[int, int, int]:
    return _mezcla(AZUL, CELESTE, t / 0.55) if t < 0.55 else _mezcla(CELESTE, AQUA, (t - 0.55) / 0.45)


def _ajustar(draw: ImageDraw.ImageDraw, texto: str, ancho: int, tam: int, negrita: bool = True) -> ImageFont.FreeTypeFont:
    """La fuente más grande (hasta `tam`) con la que el texto cabe en `ancho`."""
    while tam > 18 and draw.textlength(texto, font=_fuente(tam, negrita)) > ancho:
        tam -= 2
    return _fuente(tam, negrita)


def generar_tarjeta(
    analisis: Analisis, cierre: Optional[str], sitio: str, nombre: str = "", origen: str = "traslado"
) -> bytes:
    p = analisis.pensum2022
    porcentaje = min(100, round(p.creditos * 100 / p.cierre)) if p.cierre else 0

    img = Image.new("RGB", (ANCHO, ALTO))
    d = ImageDraw.Draw(img)
    for y in range(ALTO):
        d.line([(0, y), (ANCHO, y)], fill=_mezcla(FONDO_ARRIBA, FONDO_ABAJO, y / ALTO))

    # Olas al pie
    capa = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    import math

    for i, (color, alto, fase) in enumerate([(AZUL, 230, 0.0), (CELESTE, 175, 1.4), (AQUA, 120, 2.6)]):
        puntos = [(x, ALTO - alto + 26 * math.sin(x / 120 + fase)) for x in range(0, ANCHO + 10, 10)]
        dc.polygon(puntos + [(ANCHO, ALTO), (0, ALTO)], fill=color + (46 + 14 * i,))
    img.paste(capa, (0, 0), capa)
    d = ImageDraw.Draw(img)

    # Encabezado
    logo = Image.open(DATOS / "logo.png").convert("RGBA").resize((128, 128))
    img.paste(logo, (80, 76), logo)
    d.text((232, 86), "Piletazo", font=_fuente(66, True), fill=TEXTO)
    d.text((234, 166), "Tu camino al cierre de pensum", font=_fuente(28), fill=(125, 211, 252))

    y = 248
    if nombre:
        d.text((80, y), nombre, font=_ajustar(d, nombre, ANCHO - 160, 44), fill=TEXTO)
        y += 64
    carrera = "Ingeniería en Ciencias y Sistemas · USAC" + (" · CLAR 2022" if origen == "clar2022" else "")
    d.text((80, y), carrera, font=_fuente(26), fill=TEXTO_2)

    # Porcentaje
    d.text((80, 380), "Voy por el", font=_fuente(46), fill=TEXTO_2)
    d.text((70, 432), f"{porcentaje} %", font=_fuente(210, True), fill=(94, 234, 212))
    d.text((80, 668), "de mi carrera", font=_fuente(46), fill=TEXTO_2)

    # Barra de avance
    x0, x1, yb = 80, ANCHO - 80, 752
    d.rounded_rectangle((x0, yb, x1, yb + 30), radius=15, fill=(27, 33, 43))
    lleno = x0 + (x1 - x0) * porcentaje / 100
    if lleno > x0 + 30:
        barra = Image.new("RGB", (int(lleno - x0), 30))
        db = ImageDraw.Draw(barra)
        for x in range(barra.width):
            db.line([(x, 0), (x, 30)], fill=_degradado_ola(x / max(1, barra.width - 1)))
        mascara = Image.new("L", barra.size, 0)
        ImageDraw.Draw(mascara).rounded_rectangle((0, 0, barra.width - 1, 29), radius=15, fill=255)
        img.paste(barra, (x0, yb), mascara)

    # Datos
    r = analisis.rendimiento
    datos = [
        ("Créditos CLAR", f"{p.creditos} / {p.cierre}"),
        ("Promedio", f"{r.promedio:.2f}" if r.promedio is not None else "—"),
        ("Cursos aprobados", str(r.cursos_aprobados)),
        ("Cierro pensum en", cierre or "—"),
    ]
    ancho_celda = (ANCHO - 160 - 24) // 2
    for i, (etiqueta, valor) in enumerate(datos):
        cx = 80 + (i % 2) * (ancho_celda + 24)
        cy = 820 + (i // 2) * 128
        d.rounded_rectangle((cx, cy, cx + ancho_celda, cy + 112), radius=14, fill=(21, 26, 34), outline=(38, 44, 54))
        d.text((cx + 22, cy + 16), etiqueta, font=_fuente(24), fill=TENUE)
        d.text((cx + 22, cy + 50), valor, font=_ajustar(d, valor, ancho_celda - 44, 42), fill=TEXTO)

    # Pie: QR al sitio y firma del desarrollador
    qr = qrcode.QRCode(border=2, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(sitio)
    qr.make(fit=True)
    imagen_qr = qr.make_image(fill_color=(10, 26, 63), back_color="white").convert("RGB").resize((196, 196))
    mascara_qr = Image.new("L", (196, 196), 0)
    ImageDraw.Draw(mascara_qr).rounded_rectangle((0, 0, 195, 195), radius=18, fill=255)
    img.paste(imagen_qr, (80, 1090), mascara_qr)

    tx = 304
    d.text((tx, 1094), "Calcula el tuyo en", font=_fuente(26), fill=TEXTO_2)
    dominio = sitio.replace("https://", "").replace("http://", "").rstrip("/")
    d.text((tx, 1128), dominio, font=_ajustar(d, dominio, ANCHO - tx - 80, 38), fill=(94, 234, 212))

    # Monograma MR con el degradado del sitio del autor
    mr = Image.new("RGB", (72, 72))
    dm = ImageDraw.Draw(mr)
    for k in range(144):
        dm.line([(k, 0), (0, k)], fill=_mezcla((0, 113, 227), (123, 92, 255), k / 143))
    mascara_mr = Image.new("L", (72, 72), 0)
    ImageDraw.Draw(mascara_mr).rounded_rectangle((0, 0, 71, 71), radius=18, fill=255)
    ImageDraw.Draw(mr).text((36, 37), "MR", font=_fuente(30, True), fill="white", anchor="mm")
    img.paste(mr, (tx, 1196), mascara_mr)
    d.text((tx + 90, 1198), "Desarrollado por Mariano Rac", font=_fuente(27, True), fill=TEXTO)
    d.text((tx + 90, 1234), SITIO_AUTOR, font=_fuente(25), fill=(125, 211, 252))

    salida = BytesIO()
    img.save(salida, format="PNG", optimize=True)
    return salida.getvalue()
