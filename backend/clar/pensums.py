"""Carga de las redes curriculares (pensum anterior, CLAR 2022 y CLAR 2025) desde los JSON de `datos/`."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Literal, Optional

DATOS = Path(__file__).parent / "datos"

Modalidad = Literal["eps", "tesis"]
ClavePensum = Literal["2021", "2022", "2025"]
# Pensum CLAR que lleva el estudiante. Quien viene del pensum anterior se trasladó al CLAR 2022.
Plan = Literal["2022", "2025"]

# Con EPS se asigna además el Seminario de Investigación E.P.S. (7999);
# con tesis de investigación solo se lleva el Seminario de Investigación (0799).
SEMINARIO_EPS = "7999"


@dataclass(frozen=True)
class Curso:
    """Prerrequisitos: '0101' curso aprobado, '0039|0031' cualquiera, '200CR' créditos mínimos."""

    codigo: str
    nombre: str
    creditos: int
    semestre: int
    obligatorio: bool
    prerrequisitos: List[str] = field(default_factory=list)
    area: Optional[str] = None
    diplomado: Optional[str] = None


@dataclass(frozen=True)
class RequisitoArea:
    nombre: str
    cursos: List[str]
    unidad: Literal["creditos", "cursos"]
    minimo: Optional[int]  # None cuando el requisito es solo informativo
    nota: str


@dataclass(frozen=True)
class Pensum:
    clave: ClavePensum
    nombre: str
    cierre: int
    unidad: str
    cursos: List[Curso]
    areas: List[RequisitoArea]

    @property
    def por_codigo(self) -> Dict[str, Curso]:
        return {c.codigo: c for c in self.cursos}


@lru_cache(maxsize=None)
def _leer(clave: ClavePensum) -> Pensum:
    datos = json.loads((DATOS / f"pensum_{clave}.json").read_text(encoding="utf-8"))
    return Pensum(
        clave=clave,
        nombre=datos["nombre"],
        cierre=datos["cierre"],
        unidad=datos["unidad"],
        cursos=[Curso(**c) for c in datos["cursos"]],
        areas=[RequisitoArea(**a) for a in datos["areas"]],
    )


def pensum(clave: ClavePensum, modalidad: Modalidad = "eps") -> Pensum:
    base = _leer(clave)
    cursos = [
        replace(c, obligatorio=modalidad == "eps") if c.codigo == SEMINARIO_EPS else c for c in base.cursos
    ]
    return replace(base, cursos=cursos)


@lru_cache(maxsize=None)
def catalogo() -> Dict[str, str]:
    """Nombre de cada curso por código; si un código está en varias redes, gana el nombre del CLAR 2022."""
    nombres = {c.codigo: c.nombre for c in _leer("2021").cursos}
    nombres.update({c.codigo: c.nombre for c in _leer("2025").cursos})
    nombres.update({c.codigo: c.nombre for c in _leer("2022").cursos})
    return nombres
