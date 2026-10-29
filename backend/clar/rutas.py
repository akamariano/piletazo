"""Simulación semestre a semestre hasta cerrar el pensum CLAR (2022 o 2025)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Literal, Optional

from .analisis import ProgresoPensum, analizar
from .entrada import CursoAprobado
from .pensums import Curso, Modalidad, Plan, pensum
from .recomendacion import recomendar

HORAS_MAXIMAS_VACACIONES = 4  # horas de clase magistral por escuela de vacaciones
HORAS_ESPECIALES = {"0103": 4, "0107": 4}  # Matemática Básica 2 e Intermedia 1
PRACTICAS_FINALES = "2009"
LIMITE_PERIODOS = 40

TipoPeriodo = Literal["semestre", "vacaciones"]
MarcaPracticas = Optional[Literal["inicia", "continua", "termina", "inicia-y-termina"]]


@dataclass
class Periodo:
    nombre: str
    tipo: TipoPeriodo
    cursos: List[Curso]
    creditos: int
    acumulado: int  # CLAR acumulados al terminar el periodo
    practicas: MarcaPracticas = None


@dataclass
class Ruta:
    periodos: List[Periodo] = field(default_factory=list)
    semestres: int = 0
    cierre: Optional[str] = None
    creditos_finales: int = 0
    bloqueo: Optional[str] = None  # por qué no se pudo cerrar con estas opciones


@dataclass(frozen=True)
class Calendario:
    tipo: TipoPeriodo
    numero: int  # 1 = primer semestre / vacaciones de junio, 2 = segundo semestre / vacaciones de diciembre
    anio: int

    @property
    def nombre(self) -> str:
        if self.tipo == "semestre":
            return f"{'Primer' if self.numero == 1 else 'Segundo'} semestre {self.anio}"
        return f"Vacaciones de {'junio' if self.numero == 1 else 'diciembre'} {self.anio}"

    def siguiente(self) -> "Calendario":
        """Primer semestre (ene–may), vacaciones de junio, segundo semestre (jul–nov), vacaciones de diciembre."""
        if self.tipo == "semestre":
            return Calendario("vacaciones", self.numero, self.anio)
        if self.numero == 1:
            return Calendario("semestre", 2, self.anio)
        return Calendario("semestre", 1, self.anio + 1)


def horas_magistrales(codigo: str) -> int:
    return HORAS_ESPECIALES.get(codigo, 2)


def siguiente_periodo(hoy: date) -> Calendario:
    """El primer periodo después del que está en curso hoy."""
    if hoy.month <= 5:
        return Calendario("vacaciones", 1, hoy.year)
    if hoy.month == 6:
        return Calendario("semestre", 2, hoy.year)
    if hoy.month <= 11:
        return Calendario("vacaciones", 2, hoy.year)
    return Calendario("semestre", 1, hoy.year + 1)


def planificar_ruta(
    aprobados_iniciales: List[CursoAprobado],
    carga_maxima: int,
    practicas: Literal[1, 2],
    vacaciones: Literal[0, 1, 2],
    modalidad: Modalidad = "eps",
    hoy: Optional[date] = None,
    plan: Plan = "2022",
) -> Ruta:
    """Los cursos cargados se toman como lo aprobado hasta el periodo en curso."""
    aprobados = list(aprobados_iniciales)
    obligatorios = [c.codigo for c in pensum(plan, modalidad).cursos if c.obligatorio]
    practicas_finales = pensum(plan, modalidad).por_codigo[PRACTICAS_FINALES]
    ruta = Ruta()
    calendario = siguiente_periodo(hoy or date.today())
    practicas_restantes: Optional[int] = None

    def estado() -> ProgresoPensum:
        return analizar(aprobados, modalidad, plan).clar

    def terminado() -> bool:
        p = estado()
        codigos = {a.codigo for a in aprobados}
        return (
            all(c in codigos for c in obligatorios)
            and p.creditos >= p.cierre
            and all(a.cumple is not False for a in p.areas)
        )

    while not terminado() and len(ruta.periodos) < LIMITE_PERIODOS:
        actual, calendario = calendario, calendario.siguiente()
        p = estado()
        orden = _solo_necesarios([c.red.curso for c in recomendar(p, float("inf")).cursos], p)

        if actual.tipo == "vacaciones":
            if vacaciones == 0:
                continue
            elegidos: List[Curso] = []
            horas = 0
            for curso in orden:
                # Las prácticas no se llevan en vacaciones.
                if curso.creditos == 0 or len(elegidos) >= vacaciones:
                    continue
                h = horas_magistrales(curso.codigo)
                if horas + h > HORAS_MAXIMAS_VACACIONES:
                    continue
                elegidos.append(curso)
                horas += h
            _aprobar(aprobados, elegidos)
            if elegidos:
                ruta.periodos.append(_periodo(actual, elegidos, estado().creditos, None))
            continue

        ruta.semestres += 1
        elegidos = [
            c
            for c in _solo_necesarios([c.red.curso for c in recomendar(p, carga_maxima).cursos], p)
            if c.codigo != PRACTICAS_FINALES
        ]

        marca: MarcaPracticas = None
        if practicas_restantes is None and any(c.codigo == PRACTICAS_FINALES for c in orden):
            practicas_restantes = practicas
            marca = "inicia"
        elif practicas_restantes:
            marca = "continua"
        if practicas_restantes:
            practicas_restantes -= 1
            if practicas_restantes == 0:
                marca = "inicia-y-termina" if marca == "inicia" else "termina"
                _aprobar(aprobados, [practicas_finales])

        if not elegidos and marca is None:
            ruta.creditos_finales = estado().creditos
            ruta.bloqueo = (
                "Con estas opciones ya no quedan cursos disponibles para llegar al cierre. "
                "Revisa la carga máxima o los cursos optativos."
            )
            return ruta

        _aprobar(aprobados, elegidos)
        ruta.periodos.append(_periodo(actual, elegidos, estado().creditos, marca))

    ruta.creditos_finales = estado().creditos
    if terminado():
        ruta.cierre = ruta.periodos[-1].nombre if ruta.periodos else "Ya cumples los requisitos de cierre"
    else:
        ruta.bloqueo = "La simulación superó el límite de periodos; revisa la carga máxima."
    return ruta


def _solo_necesarios(cursos: List[Curso], p: ProgresoPensum) -> List[Curso]:
    """
    Deja los obligatorios y los cursos de áreas pendientes, y solo los optativos necesarios
    para completar los créditos de cierre, prefiriendo los del área de Sistemas.
    """
    de_area = {c.codigo for a in p.areas if a.cumple is False for c in a.cursos if not c.aprobado}
    faltantes = max(0, p.cierre - p.creditos - p.creditos_obligatorios_pendientes)
    # Si los optativos del área de Sistemas alcanzan para cerrar, se esperan a ellos en lugar de llevar otros.
    optativos_sistemas = sum(
        r.curso.creditos for r in p.red if not r.curso.obligatorio and r.curso.area and r.estado != "aprobado"
    )
    solo_sistemas = optativos_sistemas >= faltantes
    resultado: List[Curso] = []
    for c in cursos:
        if c.obligatorio:
            resultado.append(c)
        elif c.codigo in de_area:
            faltantes -= c.creditos
            resultado.append(c)
        elif faltantes > 0 and (c.area or not solo_sistemas):
            faltantes -= c.creditos
            resultado.append(c)
    return resultado


def _aprobar(aprobados: List[CursoAprobado], cursos: List[Curso]) -> None:
    aprobados.extend(CursoAprobado(c.codigo, c.nombre, c.creditos) for c in cursos)


def _periodo(c: Calendario, cursos: List[Curso], acumulado: int, practicas: MarcaPracticas) -> Periodo:
    return Periodo(
        nombre=c.nombre,
        tipo=c.tipo,
        cursos=cursos,
        creditos=sum(x.creditos for x in cursos),
        acumulado=acumulado,
        practicas=practicas,
    )
