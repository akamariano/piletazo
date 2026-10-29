"""
Ruta crítica del pensum: los obligatorios pendientes que no tienen holgura.

Cada curso ocupa un semestre y no puede llevarse junto con sus prerrequisitos. Con eso, la cadena
de prerrequisitos más larga entre los obligatorios pendientes fija el mínimo de semestres para
cerrar; los cursos de esa cadena son críticos: si uno se atrasa un semestre, el cierre también.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List

from .analisis import CursoRed, ProgresoPensum


@dataclass
class RutaCritica:
    codigos: List[str] = field(default_factory=list)
    # Mínimo de semestres para cerrar solo por cadenas de prerrequisitos (sin límite de carga).
    semestres_minimos: int = 0


def ruta_critica(progreso: ProgresoPensum) -> RutaCritica:
    pendientes: Dict[str, CursoRed] = {
        r.curso.codigo: r for r in progreso.red if r.curso.obligatorio and r.estado != "aprobado"
    }
    if not pendientes:
        return RutaCritica()

    def previos(codigo: str) -> List[str]:
        return [c for p in pendientes[codigo].curso.prerrequisitos for c in p.split("|") if c in pendientes]

    siguientes: Dict[str, List[str]] = {c: [] for c in pendientes}
    for codigo in pendientes:
        for p in previos(codigo):
            siguientes[p].append(codigo)

    @lru_cache(maxsize=None)
    def nivel(codigo: str) -> int:  # semestres que deben pasar antes de poder llevarlo
        return max((nivel(p) + 1 for p in previos(codigo)), default=0)

    @lru_cache(maxsize=None)
    def cola(codigo: str) -> int:  # semestres desde que se lleva hasta el último que depende de él
        return 1 + max((cola(s) for s in siguientes[codigo]), default=0)

    total = max(nivel(c) + cola(c) for c in pendientes)
    criticos = [c for c in pendientes if nivel(c) + cola(c) == total]
    return RutaCritica(criticos, total)
