"""Smoke tests do Streamlit; executar no projeto completo, com dependências instaladas."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]


def test_streamlit_mostra_cenario_credito():
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=20).run()
    assert not app.exception
    app.radio[0].set_value("Crédito — cenários 30+/90+").run()
    assert not app.exception
    assert len(app.metric) == 4
    assert app.metric[0].value == "12.00%"
    assert app.metric[1].value == "13.50%"
    assert app.metric[2].value == "4.50%"
    assert app.metric[3].value == "5.00%"


def test_streamlit_rejeita_saldo_90_maior_30():
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=20).run()
    app.radio[0].set_value("Crédito — cenários 30+/90+").run()
    assert not app.exception
    app.number_input[2].set_value(150_000.0).run()
    assert not app.exception
    assert app.error
