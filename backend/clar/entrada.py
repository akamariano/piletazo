"""Lectura de cursos aprobados: texto copiado del portal o red curricular guardada como HTML."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Dict, List, Optional

from .pensums import pensum

# Línea típica copiada de "Cursos aprobados" del portal:
# 0101    AREA MATEMATICA BASICA 1    7    2021-05    69.00
# 0006    IDIOMA TECNICO 1    2    2021-06    Aprobado    Equivalencia con creditos
LINEA_CURSO = re.compile(r"^\s*(\d{3,4})\s+(.+?)\s+(\d{1,2})\s+(\d{4}-\d{2})\s+(\S+)\s*(.*)$")
SOLO_CODIGO = re.compile(r"^\s*(\d{3,4})\b")


@dataclass
class CursoAprobado:
    codigo: str
    nombre: str
    creditos: int
    periodo: Optional[str] = None
    nota: Optional[str] = None
    observacion: Optional[str] = None


def normalizar_codigo(codigo: str) -> str:
    return codigo.strip().zfill(4)


def parsear_texto(texto: str) -> List[CursoAprobado]:
    anterior = pensum("2021").por_codigo
    cursos: List[CursoAprobado] = []
    for linea in texto.splitlines():
        m = LINEA_CURSO.match(linea)
        if m:
            cursos.append(
                CursoAprobado(
                    codigo=normalizar_codigo(m[1]),
                    nombre=m[2].strip(),
                    creditos=int(m[3]),
                    periodo=m[4],
                    nota=m[5],
                    observacion=m[6].strip() or None,
                )
            )
            continue
        # Línea con solo el código (y quizá el nombre): se completa con la red anterior
        c = SOLO_CODIGO.match(linea)
        if c:
            curso = anterior.get(normalizar_codigo(c[1]))
            if curso:
                cursos.append(CursoAprobado(curso.codigo, curso.nombre, curso.creditos))
    return _deduplicar(cursos)


class _LectorRed(HTMLParser):
    """Recoge los códigos de las tarjetas `.body-red-curricular.curso-aprobado` y las filas de tablas."""

    def __init__(self) -> None:
        super().__init__()
        self.aprobados: List[str] = []
        self.filas: List[List[str]] = []
        self._pila: List[Dict[str, bool]] = []
        self._en_codigo = False
        self._texto_codigo = ""
        self._fila: Optional[List[str]] = None
        self._celda: Optional[str] = None

    def handle_starttag(self, tag, attrs):
        clases = set((dict(attrs).get("class") or "").split())
        padre_aprobado = bool(self._pila) and self._pila[-1]["aprobado"]
        if tag == "div":
            aprobado = padre_aprobado or {"body-red-curricular", "curso-aprobado"} <= clases
            self._pila.append({"aprobado": aprobado})
            if aprobado and "body-red-codigo-division" in clases:
                self._en_codigo = True
                self._texto_codigo = ""
        elif tag == "tr":
            self._fila = []
        elif tag in ("td", "th") and self._fila is not None:
            self._celda = ""

    def handle_endtag(self, tag):
        if tag == "div" and self._pila:
            self._pila.pop()
            if self._en_codigo:
                self._en_codigo = False
                codigo = self._texto_codigo.strip()
                if codigo:
                    self.aprobados.append(normalizar_codigo(codigo))
        elif tag in ("td", "th") and self._celda is not None and self._fila is not None:
            self._fila.append(self._celda.strip())
            self._celda = None
        elif tag == "tr" and self._fila is not None:
            self.filas.append(self._fila)
            self._fila = None

    def handle_data(self, data):
        if self._en_codigo:
            self._texto_codigo += data
        if self._celda is not None:
            self._celda += data


def parsear_html(html: str) -> List[CursoAprobado]:
    lector = _LectorRed()
    lector.feed(html)
    anterior = pensum("2021").por_codigo
    if lector.aprobados:
        cursos = [
            CursoAprobado(anterior[c].codigo, anterior[c].nombre, anterior[c].creditos)
            for c in lector.aprobados
            if c in anterior
        ]
        return _deduplicar(cursos)
    return parsear_texto("\n".join("    ".join(fila) for fila in lector.filas))


def _deduplicar(cursos: List[CursoAprobado]) -> List[CursoAprobado]:
    vistos: Dict[str, CursoAprobado] = {}
    for c in cursos:
        vistos.setdefault(c.codigo, c)
    return list(vistos.values())


# Cursos optativos que un estudiante típico ya lleva al terminar 5.º semestre.
OPTATIVOS_DE_EJEMPLO = {"0006", "0008", "0039"}


def estudiante_de_ejemplo(clave_pensum: str, semestres: int = 5) -> List[CursoAprobado]:
    """Estudiante que acaba de terminar `semestres`: todos los obligatorios hasta ahí, idiomas 1–2 y deportes 1."""
    red = pensum(clave_pensum)  # type: ignore[arg-type]
    return [
        CursoAprobado(c.codigo, c.nombre, c.creditos, nota="Aprobado", observacion="Ejemplo")
        for c in red.cursos
        if c.semestre <= semestres and (c.obligatorio or c.codigo in OPTATIVOS_DE_EJEMPLO)
    ]
