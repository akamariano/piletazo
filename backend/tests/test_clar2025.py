from fastapi.testclient import TestClient

from clar.analisis import analizar
from clar.api import app
from clar.cursando import validar
from clar.entrada import estudiante_de_ejemplo
from clar.pensums import pensum
from clar.rutas import planificar_ruta

cliente = TestClient(app)


def test_red_clar_2025_completa_y_consistente():
    p = pensum("2025")
    codigos = {c.codigo for c in p.cursos}
    assert p.cierre == 300 and len(p.cursos) == 75
    assert all(q in codigos for c in p.cursos for r in c.prerrequisitos for q in r.split("|"))
    assert sum(c.creditos for c in pensum("2025", "tesis").cursos if c.obligatorio) == 273
    assert sum(c.creditos for c in p.cursos if c.obligatorio) == 276  # con EPS, 7999 es obligatorio
    # cursos que solo existen en el CLAR 2025
    assert {"0089", "0768", "0767", "0794", "0707", "0649", "0719", "0793", "0469", "0613", "0967"} <= codigos


def test_prerrequisitos_distintos_al_2022():
    assert pensum("2025").por_codigo["0281"].prerrequisitos == ["0964"]  # en 2022 pedía 0778 y 0781
    assert pensum("2025").por_codigo["0281"].semestre == 5


def test_analisis_y_ruta_con_plan_2025():
    quinto = estudiante_de_ejemplo("2025", 5)
    a = analizar(quinto, plan="2025")
    assert a.plan == "2025"
    assert a.clar.creditos == sum(c.creditos for c in quinto)
    estados = {r.curso.codigo: r.estado for r in a.clar.red}
    assert estados["0767"] == "disponible"  # pide 0281 y 0778, ya aprobados
    assert estados["0794"] == "bloqueado"
    ruta = planificar_ruta(quinto, 30, practicas=1, vacaciones=0, plan="2025")
    llevados = {c.codigo for p in ruta.periodos for c in p.cursos}
    assert ruta.cierre and ruta.creditos_finales >= 300
    assert {"0469", "0613", "0967"} <= llevados


def test_validar_cursando_usa_la_red_2025():
    quinto = estudiante_de_ejemplo("2025", 5)
    assert validar(quinto, "0767", plan="2025").valido
    v = validar(quinto, "0794", plan="2025")
    assert not v.valido and "0794 Seminario de Computación" in v.mensaje and "0767" in v.mensaje
    assert "no está en la red CLAR 2025" in validar(quinto, "0285", plan="2025").mensaje


def test_api_clar2025():
    e = cliente.get("/api/ejemplo", params={"origen": "clar2025"}).json()
    assert {"0014", "0601", "0722", "0767", "0774", "0796"} <= set(e["cursando"])
    r = cliente.post(
        "/api/calculo", json={"aprobados": e["aprobados"], "cursando": e["cursando"], "plan": "2025", "hoy": "2026-10-28"}
    ).json()
    assert r["analisis"]["plan"] == "2025"
    assert r["cursando"]["invalidos"] == []
    assert any(c["red"]["curso"]["codigo"] == "0794" for c in r["recomendacion"]["cursos"])
    tarjeta = cliente.post("/api/tarjeta", json={"aprobados": e["aprobados"], "plan": "2025", "origen": "clar2025"})
    assert tarjeta.status_code == 200
    pdf = cliente.post("/api/reporte", json={"aprobados": e["aprobados"], "plan": "2025", "origen": "clar2025"})
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
