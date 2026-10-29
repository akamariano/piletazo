from fastapi.testclient import TestClient

from clar.api import app

cliente = TestClient(app)


def test_salud():
    assert cliente.get("/api/salud").json() == {"estado": "ok"}


def test_leer_texto_y_calcular(texto_ejemplo):
    leidos = cliente.post("/api/cursos/leer", json={"texto": texto_ejemplo}).json()["aprobados"]
    assert len(leidos) == 46

    r = cliente.post(
        "/api/calculo",
        json={"aprobados": leidos, "modalidad": "tesis", "cargaMaxima": 30, "practicas": 2, "hoy": "2026-10-28"},
    )
    assert r.status_code == 200
    datos = r.json()
    a = datos["analisis"]
    # Claves en camelCase, como las usa Angular
    assert a["creditos2022"] == 187
    assert a["creditosSinEquivalencia"] == 12
    assert "creditosObligatoriosPendientes" in a["clar"]
    assert a["pierdenDisponibilidad"][0]["curso"]["codigo"] == "0797"
    assert [e["vacaciones"] for e in datos["escenarios"]] == [0, 1, 2]
    assert datos["escenarios"][0]["ruta"]["cierre"]
    assert "fueraDeCarga" in datos["recomendacion"]
    assert datos["catalogo"]["0781"] == "Organización de Lenguajes y Compiladores 2"


def test_leer_html(html_ejemplo):
    r = cliente.post("/api/cursos/leer", json={"html": html_ejemplo})
    assert "0781" in [c["codigo"] for c in r.json()["aprobados"]]


def test_validaciones():
    assert cliente.post("/api/cursos/leer", json={}).status_code == 400
    assert cliente.post("/api/calculo", json={"aprobados": []}).status_code == 400
    malo = {"aprobados": [{"codigo": "abc", "nombre": "x", "creditos": 3}]}
    assert cliente.post("/api/calculo", json=malo).status_code == 422
    assert cliente.post("/api/calculo", json={"aprobados": [], "cargaMaxima": 99}).status_code == 422


def test_reporte_pdf(texto_ejemplo):
    leidos = cliente.post("/api/cursos/leer", json={"texto": texto_ejemplo}).json()["aprobados"]
    r = cliente.post(
        "/api/reporte",
        json={"aprobados": leidos, "nombre": "Mariano Rac", "carne": "202100000", "origen": "traslado", "vacaciones": 1, "hoy": "2026-10-28"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert 'filename="piletazo-202100000.pdf"' in r.headers["content-disposition"]
    assert r.content.startswith(b"%PDF")


def test_robots_y_sitemap():
    robots = cliente.get("/robots.txt")
    assert robots.status_code == 200
    assert "Disallow: /api/" in robots.text
    assert "Sitemap: http://testserver/sitemap.xml" in robots.text
    sitemap = cliente.get("/sitemap.xml")
    assert sitemap.headers["content-type"].startswith("application/xml")
    assert "<loc>http://testserver/</loc>" in sitemap.text


def test_404_personalizada_y_api_en_json():
    r = cliente.get("/ruta/que/no/existe")
    assert r.status_code == 404
    assert "text/html" in r.headers["content-type"]
    assert "ruta no encontrada" in r.text.lower()
    api = cliente.get("/api/no-existe")
    assert api.status_code == 404
    assert api.headers["content-type"].startswith("application/json")


def test_inicio_con_url_absoluta():
    html = cliente.get("/").text
    assert "__SITIO__" not in html
    assert '<link rel="canonical" href="http' in html


def test_estudiante_de_ejemplo_quinto_semestre():
    for origen, clave in (("clar2022", "clar"), ("traslado", "pensum2021")):
        aprobados = cliente.get("/api/ejemplo", params={"origen": origen}).json()["aprobados"]
        assert aprobados
        datos = cliente.post("/api/calculo", json={"aprobados": aprobados, "hoy": "2026-10-28"}).json()
        red = datos["analisis"][clave]["red"]
        obligatorios = [r for r in red if r["curso"]["obligatorio"]]
        assert all(r["estado"] == "aprobado" for r in obligatorios if r["curso"]["semestre"] <= 5)
        assert not any(r["estado"] == "aprobado" for r in obligatorios if r["curso"]["semestre"] >= 6)
    # Un estudiante CLAR 2022 de 5.º semestre ya puede llevar los obligatorios de sexto
    aprobados = cliente.get("/api/ejemplo").json()["aprobados"]
    rec = cliente.post("/api/calculo", json={"aprobados": aprobados}).json()["recomendacion"]
    assert {"0601", "0722", "0773", "0778", "0781"} <= {c["red"]["curso"]["codigo"] for c in rec["cursos"]}
    assert cliente.get("/api/ejemplo", params={"semestres": 11}).status_code == 422
