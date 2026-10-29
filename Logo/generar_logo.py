"""
Genera el logo de Piletazo: una ola rompiendo, vista de lado, hecha de 0s y 1s.

La ola es una curva (cola que sube + espiral de la cresta). Sobre ella se trazan varias
corrientes paralelas y en cada una se colocan dígitos binarios siguiendo la tangente,
más pequeños y claros hacia la punta de la cresta. El color va del azul profundo (base)
al celeste y al aqua (cresta).

Uso:  python3 generar_logo.py      (escribe los SVG en esta carpeta)
"""

from __future__ import annotations

import math
import random
from pathlib import Path

CARPETA = Path(__file__).parent
FUENTE_MONO = "'Geist Mono', 'SF Mono', ui-monospace, Menlo, Consolas, monospace"
FUENTE = "Geist, 'SF Pro Display', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

# Paleta: azul profundo → azul → celeste → aqua → espuma
PALETA = [(0.0, (0x1d, 0x4e, 0xd8)), (0.45, (0x38, 0xbd, 0xf8)), (0.8, (0x2d, 0xd4, 0xbf)), (1.0, (0xcc, 0xfb, 0xf1))]
# Sobre fondo claro: azul profundo → azul → agua profunda, para mantener el contraste
PALETA_CLARA = [(0.0, (0x0b, 0x2a, 0x6f)), (0.5, (0x1d, 0x4e, 0xd8)), (0.8, (0x08, 0x91, 0xb2)), (1.0, (0x0e, 0x74, 0x90))]


def color(t: float, paleta=PALETA) -> str:
    t = max(0.0, min(1.0, t))
    for (t0, c0), (t1, c1) in zip(paleta, paleta[1:]):
        if t <= t1:
            k = (t - t0) / (t1 - t0)
            r, g, b = (round(a + (bb - a) * k) for a, bb in zip(c0, c1))
            return f"#{r:02x}{g:02x}{b:02x}"
    return "#ccfbf1"


def curva(cx=30.0, cy=26.0, r0=17.0, vueltas=0.85, k=0.36, n=900):
    """Puntos de la ola: cola (bezier cúbica) que sube y entra en la espiral de la cresta."""
    puntos = []
    p0, p1, p2, p3 = (-2.0, 64.0), (22.0, 64.0), (cx + r0 + 6.0, cy + 22.0), (cx + r0, cy)
    for i in range(n // 3):
        t = i / (n // 3)
        a = [(1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t**2, t**3]
        puntos.append((sum(w * p[0] for w, p in zip(a, (p0, p1, p2, p3))), sum(w * p[1] for w, p in zip(a, (p0, p1, p2, p3)))))
    total = 2 * math.pi * vueltas
    for i in range(n - n // 3 + 1):
        th = total * i / (n - n // 3)
        r = r0 * math.exp(-k * th)
        puntos.append((cx + r * math.cos(th), cy - r * math.sin(th)))
    return puntos


def con_longitud(puntos):
    """Longitud acumulada, tangente y normal (hacia el interior de la ola) en cada punto."""
    datos, s = [], 0.0
    for i, p in enumerate(puntos):
        if i:
            s += math.dist(p, puntos[i - 1])
        a, b = puntos[max(0, i - 1)], puntos[min(len(puntos) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1.0
        tx, ty = dx / l, dy / l
        datos.append((p, s, (tx, ty), (ty, -tx)))  # normal a la derecha del avance = interior de la espiral
    return datos, s


def ola_binaria(semilla=7, escala=1.0, espuma=True, paleta=PALETA, color_espuma="#ccfbf1") -> str:
    rnd = random.Random(semilla)
    datos, largo = con_longitud(curva())
    corrientes = 9
    separacion = 2.1
    piezas = []
    for banda in range(corrientes):
        desplazamiento = banda * separacion
        s_actual = rnd.uniform(0, 1.2)
        j = 0
        while s_actual < largo:
            while j < len(datos) - 1 and datos[j][1] < s_actual:
                j += 1
            (x, y), s, (tx, ty), (nx, ny) = datos[j]
            avance = s / largo
            # grosor de la ola: ancho en la base, fino en la punta de la cresta
            grosor = 19.0 * (1 - avance) ** 0.95 + 1.0
            if desplazamiento <= grosor:
                tam = (3.2 - 1.6 * avance**1.4) * (1 - 0.06 * banda)
                px, py = x + nx * desplazamiento, y + ny * desplazamiento
                angulo = math.degrees(math.atan2(ty, tx))
                digito = rnd.choice("01")
                tono = color(avance * 0.92 + (corrientes - 1 - banda) * 0.025, paleta)
                opacidad = 1.0 if banda < 6 else 0.85
                piezas.append(
                    f'<text x="{px:.2f}" y="{py:.2f}" font-size="{tam * escala:.2f}" fill="{tono}" '
                    f'fill-opacity="{opacidad}" transform="rotate({angulo:.1f} {px:.2f} {py:.2f})">{digito}</text>'
                )
                s_actual += tam * 0.74
            else:
                s_actual += 1.2
    if espuma:
        # salpicadura del piletazo sobre la cresta
        for x, y, tam, d in [(23.5, 8.5, 2.3, "1"), (19.5, 12.0, 1.9, "0"), (26.5, 4.5, 1.8, "0"), (16.0, 15.5, 1.5, "1"), (21.0, 4.0, 1.3, "1")]:
            piezas.append(f'<text x="{x}" y="{y}" font-size="{tam}" fill="{color_espuma}" fill-opacity="0.9">{d}</text>')
    return (
        f'<g font-family="{FUENTE_MONO}" font-weight="700" text-anchor="middle" dominant-baseline="central">\n    '
        + "\n    ".join(piezas)
        + "\n  </g>"
    )


def icono(fondo=True) -> str:
    base = (
        """<defs>
    <linearGradient id="piletazo-fondo" x1="0" y1="0" x2="0.8" y2="1">
      <stop offset="0" stop-color="#0a1a3f"/>
      <stop offset="1" stop-color="#062a3a"/>
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="15" fill="url(#piletazo-fondo)"/>
  """
        if fondo
        else ""
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Piletazo">\n  {base}{ola_binaria()}\n</svg>\n'


def favicon() -> str:
    """A 16–32 px los dígitos no se leen: la misma ola como trazos con degradado."""
    puntos = curva(n=240)
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in puntos)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Piletazo">
  <defs>
    <linearGradient id="f-fondo" x1="0" y1="0" x2="0.8" y2="1"><stop offset="0" stop-color="#0a1a3f"/><stop offset="1" stop-color="#062a3a"/></linearGradient>
    <linearGradient id="f-ola" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#1d4ed8"/><stop offset="0.55" stop-color="#38bdf8"/><stop offset="1" stop-color="#2dd4bf"/></linearGradient>
  </defs>
  <rect width="64" height="64" rx="15" fill="url(#f-fondo)"/>
  <path d="{d}" fill="none" stroke="url(#f-ola)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="45" y="11" font-family="{FUENTE_MONO}" font-weight="700" font-size="9" fill="#ccfbf1" text-anchor="middle" dominant-baseline="central">1</text>
</svg>
"""


def lockup(horizontal: bool, oscuro: bool) -> str:
    texto = "#f0f9ff" if oscuro else "#0b2a6f"
    lema = "#7dd3fc" if oscuro else "#0e7490"
    ola = (ola_binaria() if oscuro else ola_binaria(paleta=PALETA_CLARA, color_espuma="#0891b2")).replace("\n    ", "\n      ")
    if horizontal:
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 80" role="img" aria-label="Piletazo">
  <g transform="translate(6 8)">
      {ola}
  </g>
  <text x="84" y="46" font-family="{FUENTE}" font-size="34" font-weight="700" letter-spacing="-0.6" fill="{texto}">Piletazo</text>
  <text x="85" y="65" font-family="{FUENTE_MONO}" font-size="11" font-weight="500" fill="{lema}">tu camino al cierre de pensum</text>
</svg>
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 200" role="img" aria-label="Piletazo">
  <g transform="translate(80 6) scale(1.25)">
      {ola}
  </g>
  <text x="120" y="154" text-anchor="middle" font-family="{FUENTE}" font-size="36" font-weight="700" letter-spacing="-0.6" fill="{texto}">Piletazo</text>
  <text x="120" y="177" text-anchor="middle" font-family="{FUENTE_MONO}" font-size="12" font-weight="500" fill="{lema}">tu camino al cierre de pensum</text>
</svg>
"""


def simbolo(tinta: str) -> str:
    """Versión a una tinta: mismos dígitos, un solo color."""
    ola = ola_binaria()
    import re

    ola = re.sub(r'fill="#[0-9a-f]{6}"', f'fill="{tinta}"', ola)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Piletazo">\n  {ola}\n</svg>\n'


if __name__ == "__main__":
    archivos = {
        "piletazo-icono.svg": icono(),
        "piletazo-ola.svg": icono(fondo=False),
        "favicon.svg": favicon(),
        "piletazo-horizontal-oscuro.svg": lockup(True, True),
        "piletazo-horizontal-claro.svg": lockup(True, False),
        "piletazo-vertical-oscuro.svg": lockup(False, True),
        "piletazo-vertical-claro.svg": lockup(False, False),
        "piletazo-simbolo-blanco.svg": simbolo("#ffffff"),
        "piletazo-simbolo-azul.svg": simbolo("#1d4ed8"),
        "piletazo-simbolo-aqua.svg": simbolo("#2dd4bf"),
    }
    for nombre, contenido in archivos.items():
        (CARPETA / nombre).write_text(contenido, encoding="utf-8")
        print("escrito", nombre)
