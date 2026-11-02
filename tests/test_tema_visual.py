"""Testes de integridade de markup sem dependências de rede/API."""
from scripts.tema_visual import CSS, contexto_html


def test_estilo_preserva_componentes_streamlit():
    assert '[data-testid="stMetric"]' in CSS
    assert '[data-testid="stSidebar"]' in CSS
    assert '[data-testid="stTabs"]' in CSS
    assert '[data-testid="stDataFrame"]' in CSS


def test_markup_escapa_texto_injetado():
    html = contexto_html('<script>alert(1)</script>', 'Saldo < 30', 'Módulo & 01')
    assert '<script>' not in html
    assert '&lt;script&gt;' in html
    assert 'Saldo &lt; 30' in html
    assert 'Módulo &amp; 01' in html


def test_visual_nao_depende_de_assets_remotos():
    assert 'url(' not in CSS.lower()
    assert 'https://' not in CSS.lower()
    assert 'fetch(' not in CSS.lower()
