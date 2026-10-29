"""API de la Calculadora CLAR. También sirve la página de Angular ya compilada."""

from __future__ import annotations

import os
from dataclasses import asdict, is_dataclass
from datetime import date
from pathlib import Path
from typing import Any, List, Literal, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .analisis import analizar
from .cursando import con_cursando, cursando_de_ejemplo, validar
from .entrada import CursoAprobado, estudiante_de_ejemplo, parsear_html, parsear_texto
from .pensums import catalogo
from .recomendacion import recomendar
from .reporte_pdf import generar_pdf
from .rutas import planificar_ruta

MAXIMO_TEXTO = 3_000_000  # una red curricular guardada pesa ~450 KB

app = FastAPI(
    title="Piletazo",
    description="Traslado del pensum anterior al pensum CLAR 2022 de Ingeniería en Ciencias y Sistemas (USAC). No oficial.",
    version="1.0.0",
)

origenes = [o for o in os.environ.get("CLAR_CORS", "http://localhost:4200").split(",") if o]
app.add_middleware(CORSMiddleware, allow_origins=origenes, allow_methods=["GET", "POST"], allow_headers=["*"])


class Esquema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class Lectura(Esquema):
    texto: Optional[str] = Field(None, max_length=MAXIMO_TEXTO)
    html: Optional[str] = Field(None, max_length=MAXIMO_TEXTO)


class Aprobado(Esquema):
    codigo: str = Field(pattern=r"^\d{4}$")
    nombre: str = Field(max_length=200)
    creditos: int = Field(ge=0, le=30)
    periodo: Optional[str] = Field(None, max_length=20)
    nota: Optional[str] = Field(None, max_length=20)
    observacion: Optional[str] = Field(None, max_length=200)


class Calculo(Esquema):
    aprobados: List[Aprobado] = Field(max_length=300)
    # Códigos de los cursos que se están llevando; cuentan como aprobados con nota 61.
    cursando: List[str] = Field([], max_length=15)
    modalidad: Literal["eps", "tesis"] = "eps"
    carga_maxima: int = Field(30, ge=0, le=45)
    practicas: Literal[1, 2] = 1
    hoy: Optional[date] = None


class ValidarCursando(Esquema):
    aprobados: List[Aprobado] = Field(max_length=300)
    codigo: str = Field(pattern=r"^\d{4}$")
    modalidad: Literal["eps", "tesis"] = "eps"


class Reporte(Calculo):
    nombre: str = Field("", max_length=120)
    carne: str = Field("", max_length=20)
    origen: Literal["traslado", "clar2022"] = "traslado"
    vacaciones: Literal[0, 1, 2] = 0


@app.get("/api/salud")
def salud() -> dict:
    return {"estado": "ok"}


@app.post("/api/cursos/leer")
def leer_cursos(lectura: Lectura) -> dict:
    if lectura.html:
        cursos = parsear_html(lectura.html)
    elif lectura.texto:
        cursos = parsear_texto(lectura.texto)
    else:
        raise HTTPException(400, "Envía el texto copiado o la página guardada.")
    return {"aprobados": a_json(cursos)}


@app.get("/api/ejemplo")
def ejemplo(origen: Literal["traslado", "clar2022"] = "clar2022", semestres: int = Query(5, ge=1, le=10)) -> dict:
    """Estudiante de ejemplo que terminó el semestre indicado y está llevando el siguiente."""
    aprobados = estudiante_de_ejemplo("2022" if origen == "clar2022" else "2021", semestres)
    cursando = cursando_de_ejemplo(aprobados, semestres + 1) if semestres < 10 else []
    return {"aprobados": a_json(aprobados), "cursando": cursando, "semestre": semestres}


@app.post("/api/cursando/validar")
def validar_cursando(datos: ValidarCursando) -> dict:
    """Comprueba si el estudiante cumple los prerrequisitos para marcar un curso como cursando."""
    return a_json(validar([CursoAprobado(**a.model_dump()) for a in datos.aprobados], datos.codigo, datos.modalidad))


def _aprobados_con_cursando(datos: Calculo):
    base = [CursoAprobado(**a.model_dump()) for a in datos.aprobados]
    for codigo in datos.cursando:
        if not codigo.isdigit() or len(codigo) != 4:
            raise HTTPException(422, f"Código de curso inválido: {codigo}")
    return con_cursando(base, datos.cursando, datos.modalidad)


@app.post("/api/calculo")
def calcular(calculo: Calculo) -> dict:
    aprobados, cursando_validos, cursando_invalidos = _aprobados_con_cursando(calculo)
    if not aprobados:
        raise HTTPException(400, "No hay cursos aprobados.")
    analisis = analizar(aprobados, calculo.modalidad)
    escenarios = [
        {
            "vacaciones": vacaciones,
            "ruta": planificar_ruta(
                aprobados,
                carga_maxima=calculo.carga_maxima,
                practicas=calculo.practicas,
                vacaciones=vacaciones,
                modalidad=calculo.modalidad,
                hoy=calculo.hoy,
            ),
        }
        for vacaciones in (0, 1, 2)
    ]
    return a_json(
        {
            "analisis": analisis,
            "recomendacion": recomendar(analisis.pensum2022, calculo.carga_maxima),
            "escenarios": escenarios,
            "catalogo": catalogo(),
            "cursando": {"validos": cursando_validos, "invalidos": cursando_invalidos},
        }
    )


@app.post("/api/reporte")
def reporte(datos: Reporte) -> Response:
    aprobados, cursando_validos, _ = _aprobados_con_cursando(datos)
    if not aprobados:
        raise HTTPException(400, "No hay cursos aprobados.")
    analisis = analizar(aprobados, datos.modalidad)
    ruta = planificar_ruta(
        aprobados,
        carga_maxima=datos.carga_maxima,
        practicas=datos.practicas,
        vacaciones=datos.vacaciones,
        modalidad=datos.modalidad,
        hoy=datos.hoy,
    )
    pdf = generar_pdf(
        analisis,
        recomendar(analisis.pensum2022, datos.carga_maxima),
        ruta,
        origen=datos.origen,
        nombre=datos.nombre.strip(),
        carne=datos.carne.strip(),
        practicas=datos.practicas,
        vacaciones=datos.vacaciones,
        hoy=datos.hoy,
        cursando=cursando_validos,
    )
    archivo = "piletazo-" + (datos.carne.strip() or "reporte") + ".pdf"
    archivo = "".join(c for c in archivo if c.isalnum() or c in "-_.")
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{archivo}"'})


def a_json(valor: Any) -> Any:
    """Convierte dataclasses a diccionarios con claves camelCase, como las espera Angular."""
    if is_dataclass(valor) and not isinstance(valor, type):
        valor = asdict(valor)
    if isinstance(valor, dict):
        return {(to_camel(k) if "_" in k else k): a_json(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [a_json(v) for v in valor]
    return valor


# ---------- Página, buscadores y 404 ----------

# Página de Angular compilada (ng build).
FRONTEND = Path(
    os.environ.get(
        "CLAR_FRONTEND",
        Path(__file__).resolve().parents[2] / "clar-calculadora" / "dist" / "clar-calculadora" / "browser",
    )
)
# Dominio público, p. ej. https://piletazo.ejemplo.com. Si no se define, se usa el de la petición.
SITIO = os.environ.get("PILETAZO_URL", "").rstrip("/")
# Código que da Google Search Console para verificar el sitio (meta google-site-verification).
VERIFICACION_GOOGLE = os.environ.get("GOOGLE_SITE_VERIFICATION", "").strip()
ACTUALIZADO = date(2026, 10, 28)


def sitio(request: Request) -> str:
    if SITIO:
        return SITIO
    base = str(request.base_url).rstrip("/")
    # Detrás de un proxy (Render, Railway…) la petición llega por http aunque el sitio use https.
    if request.headers.get("x-forwarded-proto") == "https":
        base = base.replace("http://", "https://", 1)
    return base


@app.get("/robots.txt", include_in_schema=False)
def robots(request: Request) -> PlainTextResponse:
    return PlainTextResponse(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /docs\n"
        "Disallow: /redoc\n"
        f"\nSitemap: {sitio(request)}/sitemap.xml\n"
    )


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap(request: Request) -> Response:
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{sitio(request)}/</loc><lastmod>{ACTUALIZADO.isoformat()}</lastmod>"
        "<changefreq>monthly</changefreq><priority>1.0</priority></url>\n"
        "</urlset>\n"
    )
    return Response(xml, media_type="application/xml")


def no_encontrado() -> Response:
    pagina = FRONTEND / "404.html"
    if pagina.is_file():
        return HTMLResponse(pagina.read_text(encoding="utf-8"), status_code=404)
    return HTMLResponse("<h1>404 · Ruta no encontrada o recurso no disponible</h1>", status_code=404)


@app.exception_handler(StarletteHTTPException)
def error_http(request: Request, error: StarletteHTTPException) -> Response:
    # La API responde JSON; el resto del sitio, la página 404 con la ola.
    if error.status_code == 404 and not request.url.path.startswith("/api/"):
        return no_encontrado()
    return JSONResponse({"detail": error.detail}, status_code=error.status_code, headers=getattr(error, "headers", None))


if FRONTEND.is_dir():

    @app.get("/", include_in_schema=False)
    def inicio(request: Request) -> HTMLResponse:
        html = (FRONTEND / "index.html").read_text(encoding="utf-8").replace("__SITIO__", sitio(request))
        if VERIFICACION_GOOGLE:
            html = html.replace(
                "<!--__VERIFICACION_GOOGLE__-->",
                f'<meta name="google-site-verification" content="{VERIFICACION_GOOGLE}">',
            )
        return HTMLResponse(html)

    @app.get("/{ruta:path}", include_in_schema=False)
    def archivo(ruta: str) -> Response:
        if ruta.startswith("api/"):
            raise HTTPException(404, "Recurso de la API no encontrado.")
        destino = (FRONTEND / ruta).resolve()
        if destino.is_file() and FRONTEND.resolve() in destino.parents and destino.name != "index.html":
            return FileResponse(destino)
        return no_encontrado()
