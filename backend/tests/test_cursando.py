from datetime import date

from fastapi.testclient import TestClient

from clar.analisis import analizar
from clar.api import app
from clar.cursando import con_cursando, validar
from clar.entrada import estudiante_de_ejemplo

cliente = TestClient(app)
QUINTO = estudiante_de_ejemplo("2022", 5)  # terminó 5.º semestre de CLAR 2022


def test_acepta_curso_con_prerrequisitos_aprobados():
    v = validar(QUINTO, "0773")  # pide 0772 y 0796, ya aprobados
    assert v.valido
    assert v.nombre == "Manejo e Implementación de Archivos"


def test_rechaza_curso_sin_prerrequisitos_y_lo_nombra():
    v = validar(QUINTO, "0283")  # pide 0774, que no está aprobado
    assert not v.valido
    assert v.mensaje.startswith("No tienes los prerrequisitos para este curso: 0283 Análisis y Diseño de Sistemas 1")
    assert "0774 Sistemas de Bases de Datos 1" in v.mensaje


def test_un_curso_en_curso_no_habilita_a_otro_del_mismo_semestre():
    aprobados, validos, invalidos = con_cursando(QUINTO, ["0773", "0774"])
    assert validos == ["0773"]
    assert [i.codigo for i in invalidos] == ["0774"]  # 0774 pide 0773, que apenas se está cursando
    assert any(a.codigo == "0773" and a.nota == "61.00" and a.observacion == "Cursando" for a in aprobados)


def test_rechaza_aprobados_y_cursos_fuera_del_clar():
    assert "Ya aprobaste" in validar(QUINTO, "0101").mensaje
    assert "no está en la red CLAR 2022" in validar(QUINTO, "0069").mensaje


def test_los_cursos_en_curso_suman_y_avanzan_la_simulacion():
    base = analizar(QUINTO).pensum2022.creditos
    con, validos, _ = con_cursando(QUINTO, ["0773", "0778", "0781", "0601", "0722"])
    assert len(validos) == 5
    assert analizar(con).pensum2022.creditos == base + 5 + 5 + 6 + 6 + 4


def test_api_calculo_y_validacion():
    aprobados = cliente.get("/api/ejemplo").json()["aprobados"]
    r = cliente.post("/api/cursando/validar", json={"aprobados": aprobados, "codigo": "0283"}).json()
    assert r["valido"] is False and "0283 Análisis y Diseño de Sistemas 1" in r["mensaje"]

    sin = cliente.post("/api/calculo", json={"aprobados": aprobados, "hoy": "2026-10-28"}).json()
    con = cliente.post(
        "/api/calculo", json={"aprobados": aprobados, "cursando": ["0773", "0283"], "hoy": "2026-10-28"}
    ).json()
    assert con["cursando"]["validos"] == ["0773"]
    assert con["cursando"]["invalidos"][0]["codigo"] == "0283"
    assert con["analisis"]["creditos2022"] == sin["analisis"]["creditos2022"] + 5
    # el curso en curso ya no se recomienda para el próximo semestre
    assert "0773" not in {c["red"]["curso"]["codigo"] for c in con["recomendacion"]["cursos"]}

    pdf = cliente.post("/api/reporte", json={"aprobados": aprobados, "cursando": ["0773"], "hoy": "2026-10-28"})
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    assert cliente.post("/api/calculo", json={"aprobados": aprobados, "cursando": ["abc"]}).status_code == 422
