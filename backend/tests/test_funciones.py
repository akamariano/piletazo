from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from clar.analisis import analizar, nota_para_meta
from clar.api import app
from clar.critica import ruta_critica
from clar.cursando import con_cursando
from clar.entrada import CursoAprobado, estudiante_de_ejemplo, leer_texto

cliente = TestClient(app, base_url="https://piletazogt.vercel.app")
QUINTO = estudiante_de_ejemplo("2022", 5)
SEXTO = ["0014", "0601", "0722", "0773", "0778", "0781"]


# ---------- Ruta crítica ----------

def test_ruta_critica_cadena_mas_larga():
    rc = ruta_critica(analizar(QUINTO).pensum2022)
    # 0773 → 0774 → 0283 → 0785 → 0780: cinco semestres encadenados
    assert rc.semestres_minimos == 5
    assert {"0773", "0774", "0283", "0785", "0780"} <= set(rc.codigos)
    assert "0014" not in rc.codigos  # Economía tiene holgura


def test_ruta_critica_se_acorta_al_cursar():
    con, _, _ = con_cursando(QUINTO, SEXTO)
    rc = ruta_critica(analizar(con).pensum2022)
    assert rc.semestres_minimos == 4
    assert not set(SEXTO) & set(rc.codigos)


def test_recomendacion_explica_la_ruta_critica():
    rec = cliente.post("/api/calculo", json={"aprobados": cliente.get("/api/ejemplo").json()["aprobados"]}).json()
    razones = {c["red"]["curso"]["codigo"]: c["razones"] for c in rec["recomendacion"]["cursos"]}
    assert any("Ruta crítica" in r for r in razones["0773"])


# ---------- ¿Y si repruebo? ----------

def test_reprobar_un_curso_critico_atrasa_el_cierre():
    e = cliente.get("/api/ejemplo").json()
    r = cliente.post("/api/calculo", json={"aprobados": e["aprobados"], "cursando": e["cursando"], "hoy": "2026-10-28"}).json()
    efecto = {x["codigo"]: x["semestresExtra"] for x in r["reprobar"]}
    assert set(efecto) == set(e["cursando"])
    assert efecto["0773"] == 1  # está en la cadena más larga
    assert efecto["0014"] == 0  # Economía no atrasa nada
    con_vacaciones = cliente.post(
        "/api/calculo", json={"aprobados": e["aprobados"], "cursando": e["cursando"], "vacaciones": 2, "hoy": "2026-10-28"}
    ).json()
    assert all(x["semestresExtra"] == 0 for x in con_vacaciones["reprobar"])  # las vacaciones absorben el atraso


# ---------- Promedio meta ----------

def _historial(*notas):
    return [CursoAprobado(f"{100 + i:04d}", "Curso", 4, nota=f"{n}") for i, n in enumerate(notas)]


def test_nota_necesaria_para_la_meta():
    m = nota_para_meta(_historial(70, 80), 2, 80)  # (70 + 80 + 2x) / 4 = 80 → x = 85
    assert m.posible and m.nota_necesaria == 85.0
    assert "85.00" in m.mensaje


def test_meta_imposible_y_meta_ya_alcanzada():
    imposible = nota_para_meta(_historial(61, 61, 61, 61), 1, 90)
    assert not imposible.posible and "No es posible" in imposible.mensaje
    alcanzada = nota_para_meta(_historial(90, 90), 2, 75)
    assert alcanzada.posible and alcanzada.nota_necesaria == 61.0
    assert "Marca los cursos" in nota_para_meta(_historial(80), 0, 85).mensaje


def test_api_meta_valida_el_rango():
    assert cliente.post("/api/promedio/meta", json={"aprobados": [], "cursando": ["0773"], "meta": 50}).status_code == 422
    r = cliente.post("/api/promedio/meta", json={"aprobados": [], "cursando": ["0773"], "meta": 75}).json()
    assert r["notaNecesaria"] == 75.0


# ---------- Tarjeta para compartir ----------

def test_tarjeta_png_con_qr():
    e = cliente.get("/api/ejemplo").json()
    r = cliente.post("/api/tarjeta", json={"aprobados": e["aprobados"], "cursando": e["cursando"], "nombre": "Ana", "hoy": "2026-10-28"})
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    imagen = Image.open(BytesIO(r.content))
    assert imagen.size == (1080, 1350)
    # el QR es blanco y negro en la esquina inferior izquierda
    pixeles = [imagen.getpixel((x, y)) for x in range(90, 270, 6) for y in range(1100, 1280, 6)]
    assert any(p == (255, 255, 255) for p in pixeles) and any(sum(p) < 150 for p in pixeles)


# ---------- Revisión de lo pegado ----------

def test_revision_de_lo_pegado():
    texto = (
        "Código    Curso    Créditos\n"
        "0101    AREA MATEMATICA BASICA 1    7    2021-05    69.00\n"
        "0101    AREA MATEMATICA BASICA 1    7    2021-05    69.00\n"
        "0999    CURSO INEXISTENTE    3    2021-05    70.00\n"
        "9876 linea rota sin datos\n"
    )
    cursos, avisos = leer_texto(texto)
    assert [c.codigo for c in cursos] == ["0101", "0999"]
    assert avisos.duplicados == ["0101"]
    assert avisos.codigos_desconocidos == ["0999 CURSO INEXISTENTE"]
    assert avisos.lineas_no_reconocidas == ["9876 linea rota sin datos"]
    r = cliente.post("/api/cursos/leer", json={"texto": texto}).json()
    assert r["avisos"]["duplicados"] == ["0101"]


def test_tarjeta_formatos_y_datos_opcionales():
    e = cliente.get("/api/ejemplo").json()
    base = {"aprobados": e["aprobados"], "cursando": e["cursando"], "nombre": "Ana", "hoy": "2026-10-28"}
    historia = cliente.post("/api/tarjeta", json={**base, "formato": "historia"})
    assert Image.open(BytesIO(historia.content)).size == (1080, 1920)
    sin_datos = cliente.post("/api/tarjeta", json={**base, "incluir": []})
    con_datos = cliente.post("/api/tarjeta", json={**base})
    assert sin_datos.status_code == con_datos.status_code == 200
    assert sin_datos.content != con_datos.content
    assert cliente.post("/api/tarjeta", json={**base, "incluir": ["notas"]}).status_code == 422
    assert cliente.post("/api/tarjeta", json={**base, "formato": "cuadrado"}).status_code == 422
