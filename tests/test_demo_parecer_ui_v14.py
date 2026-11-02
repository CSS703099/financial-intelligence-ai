"""Regressão: alternar cenário não pode deixar prioridade/IDs do anterior na interface."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / 'app.py'


def _area_ia():
    app = AppTest.from_file(str(APP), default_timeout=25).run()
    assert not app.exception
    app.radio[0].set_value('IA — parecer explicável').run()
    assert not app.exception
    return app


def _rastreabilidade(app):
    blocos = [str(x.value) for x in app.markdown if '**Prioridade didática:**' in str(x.value)]
    assert len(blocos) == 1, 'O painel deve apresentar exatamente um parecer didático.'
    return blocos[0]


def _trocar(app, tipo):
    seletor = next(x for x in app.selectbox if x.key == 'demo_offline_tipo')
    seletor.set_value(tipo).run()
    assert not app.exception
    return app


def test_alternar_credito_para_repasses_atualiza_prioridade_e_ids(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    app = _area_ia()
    credito = _rastreabilidade(app)
    assert '**Prioridade didática:** Moderado' in credito
    assert '**Evidências citadas:** C2, C3, C4, C5' in credito
    _trocar(app, 'repasses')
    repasses = _rastreabilidade(app)
    assert '**Prioridade didática:** Revisão necessária' in repasses
    assert '**Evidências citadas:** R2, R3, R4, R6' in repasses
    assert 'C2, C3, C4, C5' not in repasses


def test_alternar_repasses_para_credito_atualiza_prioridade_e_ids(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    app = _area_ia()
    _trocar(app, 'repasses')
    _trocar(app, 'credito')
    credito = _rastreabilidade(app)
    assert '**Prioridade didática:** Moderado' in credito
    assert '**Evidências citadas:** C2, C3, C4, C5' in credito
    assert 'R2, R3, R4, R6' not in credito
