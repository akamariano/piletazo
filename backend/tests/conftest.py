from pathlib import Path

import pytest

from clar.entrada import parsear_texto

# Historial de ejemplo basado en un caso real, sin notas ni datos personales.
DATOS = Path(__file__).parent / "datos"


@pytest.fixture(scope="session")
def texto_ejemplo() -> str:
    return (DATOS / "historial_ejemplo.txt").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def html_ejemplo() -> str:
    return (DATOS / "red_curricular_ejemplo.html").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def aprobados_semestre_actual():
    """El mismo historial más los cuatro cursos del semestre en curso."""
    return parsear_texto((DATOS / "historial_ejemplo_semestre_actual.txt").read_text(encoding="utf-8"))
