"""V1.5: toda a narrativa do parecer deve mudar atomicamente com o cenário.

Testes não fazem chamadas à API nem autorizam operações financeiras.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from scripts.demo_parecer_offline import montar_demo
from scripts.demo_parecer_ui import formatar_parecer_para_painel

APP = Path(__file__).resolve().parents[1] / "app.py"


def abrir_app(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    app.radio[0].set_value("IA — parecer explicável").run()
    assert not app.exception
    return app


def trocar(app, tipo):
    seletor = next(x for x in app.selectbox if x.key == "demo_offline_tipo")
    seletor.set_value(tipo).run()
    assert not app.exception
    return app


def bloco_unico(app):
    blocos = [str(m.value) for m in app.markdown if str(m.value).startswith("#### Parecer manual de exemplo")]
    assert len(blocos) == 1, "O parecer deve existir em um único bloco Markdown."
    return blocos[0]


def assert_repasses(texto):
    assert "**Prioridade didática:** Revisão necessária" in texto
    assert "**Evidências citadas:** R2, R3, R4, R6" in texto
    assert "Conferir registros divergentes e premissas de conciliação" in texto
    assert "R3, R6" in texto
    assert "A base contém apenas pedidos sintéticos" in texto
    assert "C8, C9" not in texto
    assert "causalidade nem previsão" not in texto


def assert_credito(texto):
    assert "**Prioridade didática:** Moderado" in texto
    assert "**Evidências citadas:** C2, C3, C4, C5" in texto
    assert "Conferir premissas da simulação" in texto
    assert "C8, C9" in texto
    assert "não demonstra causalidade nem previsão" in texto
    assert "R3, R6" not in texto
    assert "A base contém apenas pedidos sintéticos" not in texto


def test_credito_para_repasses_atualiza_todo_parecer(monkeypatch):
    app = abrir_app(monkeypatch)
    assert_credito(bloco_unico(app))
    trocar(app, "repasses")
    assert_repasses(bloco_unico(app))


def test_repasses_para_credito_atualiza_todo_parecer(monkeypatch):
    app = abrir_app(monkeypatch)
    trocar(app, "repasses")
    assert_repasses(bloco_unico(app))
    trocar(app, "credito")
    assert_credito(bloco_unico(app))


def test_bloco_rejeita_acao_com_evidencia_de_outro_cenario():
    dossie, parecer = montar_demo("repasses")
    parecer["acoes"][0]["evidencias_ids"] = ["C8", "C9"]
    with pytest.raises(ValueError):
        formatar_parecer_para_painel(dossie, parecer)


def test_aprovacao_anterior_e_invalidada_ao_mudar_de_cenario(monkeypatch):
    app = abrir_app(monkeypatch)
    next(x for x in app.text_input if x.key == "demo_offline_revisor").set_value("Revisor de teste").run()
    next(x for x in app.checkbox if x.key == "demo_offline_conferido").check().run()
    next(x for x in app.text_input if x.key == "demo_offline_palavra").set_value("APROVAR").run()
    next(x for x in app.button if x.key == "demo_offline_aprovar").click().run()
    assert "demo_offline_autorizacao" in app.session_state
    trocar(app, "repasses")
    assert "demo_offline_autorizacao" not in app.session_state
    assert not any(x.key == "demo_offline_download" for x in app.button)
