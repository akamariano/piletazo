"""Comparación del historial del estudiante entre el pensum anterior y el CLAR 2022."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Literal, Optional, Set

from .entrada import CursoAprobado
from .pensums import Curso, Modalidad, Pensum, Plan, RequisitoArea, catalogo, pensum

EstadoCurso = Literal["aprobado", "disponible", "bloqueado"]
CREDITOS = re.compile(r"^(\d+)CR$")
NOTA = re.compile(r"^\d{1,3}(\.\d+)?$")


@dataclass
class Rendimiento:
    """Promedio de las notas numéricas de los cursos aprobados (sin los que se están cursando)."""

    cursos_aprobados: int
    cursos_con_nota: int
    promedio: Optional[float]
    promedio_ponderado: Optional[float]  # ponderado por créditos


def rendimiento(aprobados: List[CursoAprobado]) -> Rendimiento:
    reales = [a for a in aprobados if a.observacion != "Cursando"]
    notas = [(float(a.nota), a.creditos) for a in reales if a.nota and NOTA.match(a.nota) and 0 <= float(a.nota) <= 100]
    promedio = round(sum(n for n, _ in notas) / len(notas), 2) if notas else None
    con_creditos = [(n, c) for n, c in notas if c > 0]
    ponderado = (
        round(sum(n * c for n, c in con_creditos) / sum(c for _, c in con_creditos), 2) if con_creditos else None
    )
    return Rendimiento(len(reales), len(notas), promedio, ponderado)


@dataclass
class Equivalencia:
    codigo: str
    nombre: str
    creditos2021: int
    creditos2022: Optional[int]
    diferencia: int
    periodo: Optional[str] = None
    observacion: Optional[str] = None


@dataclass
class CursoRed:
    curso: Curso
    estado: EstadoCurso
    faltantes: List[str]
    prerrequisitos2021: Optional[List[str]]
    agregados: List[str] = field(default_factory=list)
    quitados: List[str] = field(default_factory=list)
    # Podía asignarse con el pensum anterior pero ya no con el CLAR 2022.
    pierde_disponibilidad: bool = False
    # No podía asignarse con el pensum anterior pero sí con el CLAR 2022.
    gana_disponibilidad: bool = False
    creditos2021: Optional[int] = None


@dataclass
class CursoArea:
    codigo: str
    nombre: str
    creditos: int
    aprobado: bool


@dataclass
class ProgresoArea:
    area: RequisitoArea
    cursos: List[CursoArea]
    creditos: int
    aprobados: int
    logrado: int  # avance en la unidad del requisito (créditos o cursos)
    total: int
    cumple: Optional[bool]  # None cuando el requisito es solo informativo


@dataclass
class ProgresoPensum:
    creditos: int
    cierre: int
    red: List[CursoRed]
    obligatorios_pendientes: List[CursoRed]
    creditos_obligatorios_pendientes: int
    areas: List[ProgresoArea]


@dataclass
class Analisis:
    modalidad: Modalidad
    plan: Plan
    aprobados: List[CursoAprobado]
    equivalencias: List[Equivalencia]
    creditos2021: int
    creditos2022: int
    creditos_sin_equivalencia: int
    rendimiento: Rendimiento
    pierden_disponibilidad: List[CursoRed]
    ganan_disponibilidad: List[CursoRed]
    cambios_prerrequisitos: List[CursoRed]
    pensum2021: ProgresoPensum
    clar: ProgresoPensum

    @property
    def red(self) -> List[CursoRed]:
        return self.clar.red


def cumple(prerrequisito: str, aprobados: Set[str], creditos: int) -> bool:
    cr = CREDITOS.match(prerrequisito)
    if cr:
        return creditos >= int(cr[1])
    return any(c in aprobados for c in prerrequisito.split("|"))


def describir_prerrequisito(prerrequisito: str) -> str:
    cr = CREDITOS.match(prerrequisito)
    if cr:
        return f"{cr[1]} créditos"
    nombres = catalogo()
    return " ó ".join(f"{c} {nombres[c]}" if c in nombres else c for c in prerrequisito.split("|"))


def analizar(aprobados: List[CursoAprobado], modalidad: Modalidad = "eps", plan: Plan = "2022") -> Analisis:
    """`clar` es el pensum CLAR del estudiante (2022 o 2025); `pensum2021`, el anterior, para el traslado."""
    anterior = pensum("2021", modalidad)
    clar = pensum(plan, modalidad)
    por2021 = anterior.por_codigo
    por_clar = clar.por_codigo
    codigos = {a.codigo for a in aprobados}

    equivalencias: List[Equivalencia] = []
    for a in aprobados:
        nuevo = por_clar.get(a.codigo)
        creditos2022 = nuevo.creditos if nuevo else None
        nombre = nuevo.nombre if nuevo else (por2021[a.codigo].nombre if a.codigo in por2021 else a.nombre)
        equivalencias.append(
            Equivalencia(
                codigo=a.codigo,
                nombre=nombre,
                creditos2021=a.creditos,
                creditos2022=creditos2022,
                diferencia=(creditos2022 or 0) - a.creditos,
                periodo=a.periodo,
                observacion=a.observacion,
            )
        )

    creditos2021 = sum(e.creditos2021 for e in equivalencias)
    creditos2022 = sum(e.creditos2022 or 0 for e in equivalencias)
    sin_equivalencia = sum(e.creditos2021 for e in equivalencias if e.creditos2022 is None)

    red: List[CursoRed] = []
    for curso in clar.cursos:
        previo = por2021.get(curso.codigo)
        pre2021 = previo.prerrequisitos if previo else None
        faltantes = [p for p in curso.prerrequisitos if not cumple(p, codigos, creditos2022)]
        aprobado = curso.codigo in codigos
        disponible2022 = not faltantes
        disponible2021 = pre2021 is not None and all(cumple(p, codigos, creditos2021) for p in pre2021)
        red.append(
            CursoRed(
                curso=curso,
                estado="aprobado" if aprobado else "disponible" if disponible2022 else "bloqueado",
                faltantes=faltantes,
                prerrequisitos2021=pre2021,
                agregados=[p for p in curso.prerrequisitos if not _incluye(pre2021, p)] if pre2021 is not None else [],
                quitados=[p for p in pre2021 if not _incluye(curso.prerrequisitos, p)] if pre2021 is not None else [],
                pierde_disponibilidad=not aprobado and disponible2021 and not disponible2022,
                gana_disponibilidad=not aprobado and pre2021 is not None and not disponible2021 and disponible2022,
                creditos2021=previo.creditos if previo else None,
            )
        )

    red2021: List[CursoRed] = []
    for curso in anterior.cursos:
        faltantes = [p for p in curso.prerrequisitos if not cumple(p, codigos, creditos2021)]
        red2021.append(
            CursoRed(
                curso=curso,
                estado="aprobado" if curso.codigo in codigos else "bloqueado" if faltantes else "disponible",
                faltantes=faltantes,
                prerrequisitos2021=curso.prerrequisitos,
                creditos2021=curso.creditos,
            )
        )

    pendientes = [r for r in red if r.estado != "aprobado"]
    return Analisis(
        modalidad=modalidad,
        plan=plan,
        aprobados=aprobados,
        equivalencias=equivalencias,
        creditos2021=creditos2021,
        creditos2022=creditos2022,
        creditos_sin_equivalencia=sin_equivalencia,
        rendimiento=rendimiento(aprobados),
        pierden_disponibilidad=[r for r in pendientes if r.pierde_disponibilidad],
        ganan_disponibilidad=[r for r in pendientes if r.gana_disponibilidad],
        cambios_prerrequisitos=[
            r
            for r in pendientes
            if not r.pierde_disponibilidad and not r.gana_disponibilidad and (r.agregados or r.quitados)
        ],
        pensum2021=_progreso(red2021, creditos2021, anterior, codigos),
        clar=_progreso(red, creditos2022, clar, codigos),
    )


def _progreso(red: List[CursoRed], creditos: int, p: Pensum, codigos: Set[str]) -> ProgresoPensum:
    obligatorios = [r for r in red if r.curso.obligatorio and r.estado != "aprobado"]
    return ProgresoPensum(
        creditos=creditos,
        cierre=p.cierre,
        red=red,
        obligatorios_pendientes=obligatorios,
        creditos_obligatorios_pendientes=sum(r.curso.creditos for r in obligatorios),
        areas=[_progreso_area(a, p.por_codigo, codigos) for a in p.areas],
    )


def _progreso_area(area: RequisitoArea, cursos: Dict[str, Curso], codigos: Set[str]) -> ProgresoArea:
    lista = [CursoArea(c, cursos[c].nombre, cursos[c].creditos, c in codigos) for c in area.cursos]
    creditos = sum(c.creditos for c in lista if c.aprobado)
    aprobados = sum(1 for c in lista if c.aprobado)
    logrado = creditos if area.unidad == "creditos" else aprobados
    total = sum(c.creditos for c in lista) if area.unidad == "creditos" else len(lista)
    return ProgresoArea(
        area=area,
        cursos=lista,
        creditos=creditos,
        aprobados=aprobados,
        logrado=logrado,
        total=total,
        cumple=None if area.minimo is None else logrado >= area.minimo,
    )


def _incluye(lista: Iterable[str], prerrequisito: str) -> bool:
    """'0039' y '0039|0031' se consideran el mismo prerrequisito."""
    opciones = set(prerrequisito.split("|"))
    return any(opciones & set(p.split("|")) for p in lista)


@dataclass
class PromedioMeta:
    meta: float
    nota_necesaria: Optional[float]
    posible: bool
    mensaje: str


def nota_para_meta(aprobados: List[CursoAprobado], cursando: int, meta: float) -> PromedioMeta:
    """Promedio que se necesita en los cursos en curso para que el promedio simple llegue a `meta`."""
    r = rendimiento(aprobados)
    suma = (r.promedio or 0) * r.cursos_con_nota
    if cursando <= 0:
        return PromedioMeta(meta, None, False, "Marca los cursos que estás cursando para calcular la nota que necesitas.")
    necesaria = (meta * (r.cursos_con_nota + cursando) - suma) / cursando
    maximo = (suma + 100 * cursando) / (r.cursos_con_nota + cursando)
    plural = "curso" if cursando == 1 else "cursos"
    if necesaria > 100:
        return PromedioMeta(
            meta, round(necesaria, 2), False,
            f"No es posible este semestre: necesitarías {necesaria:.2f}. Con 100 en tus {cursando} {plural} llegarías a {maximo:.2f}.",
        )
    if necesaria <= 61:
        return PromedioMeta(
            meta, 61.0, True, f"Con aprobar con 61 tus {cursando} {plural} en curso ya alcanzas un promedio de {meta:.2f}.",
        )
    necesaria = math.ceil(necesaria * 100) / 100
    return PromedioMeta(
        meta, necesaria, True, f"Necesitas un promedio de {necesaria:.2f} en tus {cursando} {plural} en curso para llegar a {meta:.2f}.",
    )
