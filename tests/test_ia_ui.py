"""Testes AppTest da interface; não chamam API."""

# GUIA PARA INICIANTES — Testes de comportamento da tela de IA
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
from pathlib import Path
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]


def test_area_ia_exibe_evidencias_sem_chave(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=20).run()
    assert not app.exception
    app.radio[0].set_value("IA — parecer explicável").run()
    assert not app.exception
    assert app.button(key="ia_gerar").disabled
    assert any(b.label.startswith("Gerar parecer") and b.disabled for b in app.button)


def test_troca_de_area_preserva_conciliacao():
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=20).run()
    assert not app.exception
    assert len(app.metric) == 7
    app.radio[0].set_value("Crédito — cenários 30+/90+").run()
    assert not app.exception
    assert len(app.metric) == 4
    app.radio[0].set_value("Conciliação de repasses").run()
    assert not app.exception
    assert len(app.metric) == 7


def test_erro_api_nao_expoe_mensagem_bruta():
    from scripts.ia_streamlit import mensagem_publica_erro_api

    class ErroAPI(Exception):
        code = 400

    segredo = "TOKEN-PRIVADO-EXEMPLO"
    mensagem = mensagem_publica_erro_api(ErroAPI("Chave: " + segredo))
    assert "HTTP 400" in mensagem
    assert segredo not in mensagem
    assert "Chave:" not in mensagem

    sem_http = mensagem_publica_erro_api(RuntimeError("Senha interna: " + segredo))
    assert segredo not in sem_http
    assert "Senha interna" not in sem_http
