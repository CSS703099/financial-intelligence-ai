"""Testes do dashboard Python 03 (não modificam o SQLite original)."""

# GUIA PARA INICIANTES — Testes de filtros e dados usados no painel
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from scripts.analise_pandas import carregar_pedidos, calcular_indicadores
from scripts.dashboard_dados import (
    filtrar_pedidos,
    preparar_detalhes,
    resumo_restaurantes,
)

RAIZ = Path(__file__).resolve().parents[1]


def test_filtro_setembro():
    dados = carregar_pedidos()
    filtrado = filtrar_pedidos(
        dados, ["Restaurante A", "Restaurante B", "Restaurante C"],
        date(2026, 9, 1), date(2026, 9, 30)
    )
    indicadores = calcular_indicadores(filtrado)
    assert indicadores["total_pedidos"] == 22
    assert indicadores["pedidos_concluidos"] == 18
    assert indicadores["pedidos_divergentes"] == 4
    assert indicadores["divergencia_absoluta"] == pytest.approx(24.40)


def test_filtro_restaurante_b():
    dados = carregar_pedidos()
    filtrado = filtrar_pedidos(
        dados, ["Restaurante B"], date(2026, 9, 1), date(2026, 10, 20)
    )
    indicadores = calcular_indicadores(filtrado)
    assert indicadores["total_pedidos"] == 12
    assert indicadores["pedidos_divergentes"] == 5
    assert indicadores["divergencia_absoluta"] == pytest.approx(27.40)


def test_filtro_sem_resultados():
    dados = carregar_pedidos()
    vazio = filtrar_pedidos(dados, [], date(2026, 9, 1), date(2026, 10, 20))
    assert vazio.empty
    assert calcular_indicadores(vazio)["taxa_divergencia_pct"] is None


def test_detalhes_financeiros_preservam_entrada():
    dados = carregar_pedidos()
    antes = dados.copy(deep=True)
    detalhes = preparar_detalhes(dados)
    d20 = detalhes.set_index("pedido_id").loc["PED-0020"]
    assert d20["divergencia_centavos"] == 990
    assert d20["divergencia_absoluta"] == pytest.approx(9.90)
    pd.testing.assert_frame_equal(dados, antes)


def test_priorizacao_restaurante_b():
    resumo = resumo_restaurantes(preparar_detalhes(carregar_pedidos()))
    linha = resumo.set_index("restaurante").loc["Restaurante B"]
    assert linha["impacto_absoluto"] == pytest.approx(27.40)
    assert linha["taxa_divergencia_pct"] == pytest.approx(41.67)
    assert linha["prioridade"] == "Crítico"


def test_streamlit_carrega_sem_erros():
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=15).run()
    assert not app.exception
    assert len(app.metric) == 7
    assert app.metric[0].value == "36"


def test_streamlit_filtro_restaurante():
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=15).run()
    assert not app.exception
    app.multiselect[0].set_value(["Restaurante B"]).run()
    assert not app.exception
    assert app.metric[0].value == "12"
    assert app.metric[2].value == "5"
