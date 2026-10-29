"""
Cursos que el estudiante está llevando este semestre.

Para calcular y simular se cuentan como aprobados con la nota mínima aprobatoria (61).
Solo se aceptan si sus prerrequisitos ya están aprobados: un curso que también se está
cursando no habilita a otro en el mismo semestre.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .analisis import cumple, describir_prerrequisito
from .entrada import CursoAprobado
from .pensums import Modalidad, pensum

NOTA_APROBATORIA = "61.00"
OBSERVACION = "Cursando"


@dataclass
class Validacion:
    codigo: str
    nombre: str
    valido: bool
    faltantes: List[str] = field(default_factory=list)
    mensaje: str = ""


def validar(aprobados: List[CursoAprobado], codigo: str, modalidad: Modalidad = "eps") -> Validacion:
    clar = pensum("2022", modalidad).por_codigo
    curso = clar.get(codigo)
    if curso is None:
        nombre = pensum("2021").por_codigo.get(codigo)
        return Validacion(
            codigo,
            nombre.nombre if nombre else codigo,
            False,
            mensaje=f"{codigo} {nombre.nombre if nombre else ''} no está en la red CLAR 2022.".replace("  ", " "),
        )

    codigos = {a.codigo for a in aprobados}
    if codigo in codigos:
        return Validacion(codigo, curso.nombre, False, mensaje=f"Ya aprobaste {codigo} {curso.nombre}.")

    creditos = sum(clar[c].creditos for c in codigos if c in clar)
    faltantes = [describir_prerrequisito(p) for p in curso.prerrequisitos if not cumple(p, codigos, creditos)]
    if faltantes:
        return Validacion(
            codigo,
            curso.nombre,
            False,
            faltantes,
            f"No tienes los prerrequisitos para este curso: {codigo} {curso.nombre}. Te falta: {', '.join(faltantes)}.",
        )
    return Validacion(codigo, curso.nombre, True)


def con_cursando(
    aprobados: List[CursoAprobado], cursando: List[str], modalidad: Modalidad = "eps"
) -> Tuple[List[CursoAprobado], List[str], List[Validacion]]:
    """Agrega los cursos en curso válidos como aprobados con nota 61; devuelve también los rechazados."""
    anterior = pensum("2021").por_codigo
    clar = pensum("2022", modalidad).por_codigo
    resultado = list(aprobados)
    validos: List[str] = []
    invalidos: List[Validacion] = []
    for codigo in dict.fromkeys(cursando):  # sin repetidos, en orden
        v = validar(aprobados, codigo, modalidad)
        if not v.valido:
            invalidos.append(v)
            continue
        curso = clar[codigo]
        # Para el pensum anterior cuenta su propio valor en créditos, si el curso existía.
        creditos = anterior[codigo].creditos if codigo in anterior else curso.creditos
        resultado.append(CursoAprobado(codigo, curso.nombre, creditos, nota=NOTA_APROBATORIA, observacion=OBSERVACION))
        validos.append(codigo)
    return resultado, validos, invalidos
