"""Propuesta de cursos para el próximo semestre."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

from .analisis import CursoRed, ProgresoPensum
from .critica import ruta_critica

NOMBRE_AREA = {
    "metodologia": "Metodología de Sistemas",
    "computacion": "Ciencias de la Computación",
    "software": "Desarrollo de Software",
}


@dataclass
class CursoRecomendado:
    red: CursoRed
    razones: List[str]
    desbloquea: int  # cuántos cursos pendientes dependen directa o indirectamente de este


@dataclass
class Recomendacion:
    cursos: List[CursoRecomendado]
    creditos: int
    maximo: float
    fuera_de_carga: List[CursoRecomendado]  # disponibles que no cupieron en la carga máxima


def recomendar(progreso: ProgresoPensum, maximo: float) -> Recomendacion:
    """
    Entre los cursos que el estudiante ya puede asignarse: primero los obligatorios que más
    cursos desbloquean y de semestres más bajos, luego lo que falte de las áreas con requisito,
    después optativos del área de Sistemas y por último otros optativos, sin pasar la carga máxima.
    """
    pendientes = [r for r in progreso.red if r.estado != "aprobado"]
    dependientes = _contar_dependientes(pendientes)
    criticos = set(ruta_critica(progreso).codigos)

    falta_por_area: Set[str] = set()
    for area in progreso.areas:
        if area.cumple is False and area.area.minimo is not None:
            falta_por_area.update(c.codigo for c in area.cursos if not c.aprobado)

    candidatos: List[CursoRecomendado] = []
    for r in pendientes:
        if r.estado != "disponible":
            continue
        desbloquea = dependientes.get(r.curso.codigo, 0)
        razones: List[str] = []
        if r.curso.obligatorio:
            razones.append(f"Obligatorio de {r.curso.semestre}.º semestre")
        if r.curso.codigo in criticos:
            razones.append("Ruta crítica: si lo atrasas, atrasas tu cierre")
        if desbloquea > 0:
            razones.append(f"Abre camino a {desbloquea} {'curso' if desbloquea == 1 else 'cursos'}")
        if r.curso.codigo in falta_por_area:
            razones.append("Completa un requisito de área")
        if r.curso.creditos == 0:
            razones.append("No suma carga de créditos")
        if not razones:
            razones.append(
                f"Optativo del área de {NOMBRE_AREA[r.curso.area]}"
                if r.curso.area
                else "Optativo fuera del área de Sistemas"
            )
        candidatos.append(CursoRecomendado(r, razones, desbloquea))

    def prioridad(c: CursoRecomendado):
        curso = c.red.curso
        grupo = 0 if curso.obligatorio else 1 if curso.codigo in falta_por_area else 2 if curso.area else 3
        return (grupo, curso.codigo not in criticos, -c.desbloquea, curso.semestre)

    candidatos.sort(key=prioridad)

    cursos: List[CursoRecomendado] = []
    fuera: List[CursoRecomendado] = []
    creditos = 0
    area_cubierta = False
    for c in candidatos:
        es_de_area = c.red.curso.codigo in falta_por_area
        # De un área con requisito basta un curso que la complete.
        if es_de_area and not c.red.curso.obligatorio and area_cubierta:
            fuera.append(c)
            continue
        if creditos + c.red.curso.creditos <= maximo:
            cursos.append(c)
            creditos += c.red.curso.creditos
            area_cubierta = area_cubierta or es_de_area
        else:
            fuera.append(c)

    return Recomendacion(cursos=cursos, creditos=creditos, maximo=maximo, fuera_de_carga=fuera)


def _contar_dependientes(pendientes: List[CursoRed]) -> Dict[str, int]:
    directos: Dict[str, List[str]] = {}
    for r in pendientes:
        for p in r.curso.prerrequisitos:
            for codigo in p.split("|"):
                directos.setdefault(codigo, []).append(r.curso.codigo)
    conteo: Dict[str, int] = {}
    for r in pendientes:
        vistos: Set[str] = set()
        cola = list(directos.get(r.curso.codigo, []))
        while cola:
            c = cola.pop()
            if c in vistos:
                continue
            vistos.add(c)
            cola.extend(directos.get(c, []))
        conteo[r.curso.codigo] = len(vistos)
    return conteo
