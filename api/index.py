"""Punto de entrada de la API de Piletazo en Vercel (función de Python)."""

import sys
from pathlib import Path

# El paquete `clar` vive en backend/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from clar.api import app  # noqa: E402,F401
