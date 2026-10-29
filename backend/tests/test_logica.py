from datetime import date

from clar.analisis import analizar
from clar.entrada import parsear_html, parsear_texto
from clar.recomendacion import recomendar
from clar.rutas import horas_magistrales, planificar_ruta

HOY = date(2026, 10, 28)


def codigos(cursos):
    return [c.red.curso.codigo if hasattr(c, "red") else c.curso.codigo for c in cursos]


def test_reconoce_todas_las_filas_del_portal(texto_ejemplo):
    cursos = parsear_texto(texto_ejemplo)
    assert len(cursos) == 46
    idioma = next(c for c in cursos if c.codigo == "0006")
    assert (idioma.creditos, idioma.nota, idioma.observacion) == (2, "Aprobado", "Equivalencia con creditos")


def test_lee_la_red_curricular_guardada(html_ejemplo):
    cods = [c.codigo for c in parsear_html(html_ejemplo)]
    assert "0781" in cods
    assert "0281" not in cods
    assert "0000" not in cods


def test_suma_creditos_en_ambos_pensums(texto_ejemplo):
    a = analizar(parsear_texto(texto_ejemplo))
    assert a.creditos2021 == 185
    assert a.creditos2022 == 187
    assert a.creditos_sin_equivalencia == 12  # 0069, 0348, 0736, 0061


def test_detecta_cambios_de_disponibilidad(texto_ejemplo):
    a = analizar(parsear_texto(texto_ejemplo))
    assert "0797" in codigos(a.pierden_disponibilidad)  # ahora pide 0281 y 0774
    assert "0001" in codigos(a.ganan_disponibilidad)  # antes 200 créditos, ahora 0019


def test_progreso_de_areas(texto_ejemplo):
    a = analizar(parsear_texto(texto_ejemplo))
    social21, idioma21 = a.pensum2021.areas
    assert (social21.logrado, social21.cumple) == (11, True)
    assert (idioma21.logrado, idioma21.cumple) == (4, True)
    social22, idioma22 = a.pensum2022.areas
    assert (social22.logrado, social22.cumple) == (7, False)
    assert (idioma22.aprobados, idioma22.creditos, idioma22.cumple) == (4, 12, None)


def test_red_anterior_con_sus_prerrequisitos(texto_ejemplo):
    a = analizar(parsear_texto(texto_ejemplo))
    estados = {r.curso.codigo: r.estado for r in a.pensum2021.red}
    assert estados["0281"] == "disponible"
    assert estados["0069"] == "aprobado"


def test_recomendacion_de_octavo(aprobados_semestre_actual):
    a = analizar(aprobados_semestre_actual)
    r = recomendar(a.pensum2022, 30)
    assert {"0283", "0285", "0775", "0797", "0975"} <= set(codigos(r.cursos))
    assert r.creditos <= 30
    assert recomendar(a.pensum2022, 12).creditos <= 12


def test_ruta_cierra_con_obligatorios_y_300(aprobados_semestre_actual):
    ruta = planificar_ruta(aprobados_semestre_actual, 30, practicas=1, vacaciones=0, hoy=HOY)
    assert ruta.cierre == "Segundo semestre 2028"
    assert ruta.creditos_finales >= 300
    assert ruta.periodos[0].nombre == "Primer semestre 2027"
    llevados = {c.codigo for p in ruta.periodos for c in p.cursos}
    assert "0780" in llevados


def test_vacaciones_respetan_4_horas_y_no_alargan(aprobados_semestre_actual):
    sin = planificar_ruta(aprobados_semestre_actual, 30, practicas=1, vacaciones=0, hoy=HOY)
    con = planificar_ruta(aprobados_semestre_actual, 30, practicas=1, vacaciones=2, hoy=HOY)
    assert con.semestres <= sin.semestres
    for p in con.periodos:
        if p.tipo == "vacaciones":
            assert len(p.cursos) <= 2
            assert sum(horas_magistrales(c.codigo) for c in p.cursos) <= 4


def test_practicas_de_un_anio_ocupan_dos_semestres(aprobados_semestre_actual):
    ruta = planificar_ruta(aprobados_semestre_actual, 30, practicas=2, vacaciones=0, hoy=HOY)
    assert [p.practicas for p in ruta.periodos if p.practicas] == ["inicia", "termina"]


def test_horas_magistrales():
    assert horas_magistrales("0103") == 4
    assert horas_magistrales("0107") == 4
    assert horas_magistrales("0281") == 2


def test_optativos_del_area_de_sistemas(aprobados_semestre_actual):
    ruta = planificar_ruta(aprobados_semestre_actual, 30, practicas=1, vacaciones=0, hoy=HOY)
    optativos = [
        c for p in ruta.periodos for c in p.cursos if not c.obligatorio and c.codigo not in ("0001", "0010")
    ]
    assert optativos
    assert all(c.area for c in optativos)


def test_modalidad_eps_y_tesis(aprobados_semestre_actual):
    eps = analizar(aprobados_semestre_actual, "eps").pensum2022
    tesis = analizar(aprobados_semestre_actual, "tesis").pensum2022
    assert "7999" in codigos(eps.obligatorios_pendientes)
    assert "7999" not in codigos(tesis.obligatorios_pendientes)
    assert "0799" in codigos(tesis.obligatorios_pendientes)
    llevados = lambda m: {
        c.codigo
        for p in planificar_ruta(aprobados_semestre_actual, 30, 1, 0, modalidad=m, hoy=HOY).periodos
        for c in p.cursos
    }
    assert "7999" in llevados("eps")
    assert "7999" not in llevados("tesis")


def test_promedio_y_cursos_aprobados():
    from clar.analisis import rendimiento
    from clar.entrada import CursoAprobado

    r = rendimiento(
        [
            CursoAprobado("0101", "Básica 1", 2, nota="70.00"),
            CursoAprobado("0103", "Básica 2", 4, nota="90"),
            CursoAprobado("0006", "Idioma 1", 2, nota="Aprobado", observacion="Equivalencia con creditos"),
            CursoAprobado("2025", "Prácticas", 0, nota="80.00"),
            CursoAprobado("0773", "Archivos", 5, nota="61.00", observacion="Cursando"),
        ]
    )
    assert r.cursos_aprobados == 4  # el que se está cursando no cuenta
    assert r.cursos_con_nota == 3  # "Aprobado" no tiene nota numérica
    assert r.promedio == 80.0  # (70 + 90 + 80) / 3
    assert r.promedio_ponderado == 83.33  # (70·2 + 90·4) / 6; prácticas sin créditos no pesan


def test_promedio_del_historial_de_ejemplo(texto_ejemplo):
    r = analizar(parsear_texto(texto_ejemplo)).rendimiento
    assert r.cursos_aprobados == 46
    assert r.promedio == 61.0  # el historial anónimo usa 61 en todas las notas numéricas
    assert r.cursos_con_nota == 41
