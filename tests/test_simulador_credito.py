"""Testes do motor determinístico (independente de Streamlit e do SQLite)."""
import math

import pytest

from scripts.simulador_credito import simular_cenario


def test_cenario_sem_choque():
    r = simular_cenario(1_000_000, 120_000, 45_000)
    assert r["taxa_30_base_pct"] == pytest.approx(12.0)
    assert r["taxa_90_base_pct"] == pytest.approx(4.5)
    assert r["saldo_30_cenario"] == pytest.approx(120_000.0)
    assert r["saldo_90_cenario"] == pytest.approx(45_000.0)
    assert r["nivel_alerta"] == "Estável ou melhora"


def test_choque_moderado_altera_taxas_e_saldos():
    r = simular_cenario(1_000_000, 120_000, 45_000, 1.5, 0.5)
    assert r["taxa_30_cenario_pct"] == pytest.approx(13.5)
    assert r["taxa_90_cenario_pct"] == pytest.approx(5.0)
    assert r["saldo_30_cenario"] == pytest.approx(135_000.0)
    assert r["saldo_90_cenario"] == pytest.approx(50_000.0)
    assert r["delta_saldo_30"] == pytest.approx(15_000.0)
    assert r["delta_saldo_90"] == pytest.approx(5_000.0)
    assert r["nivel_alerta"] == "Moderado"


def test_alerta_alto_e_critico():
    alto = simular_cenario(1_000_000, 120_000, 45_000, 2, 1)
    critico = simular_cenario(1_000_000, 120_000, 45_000, 3, 2)
    assert alto["nivel_alerta"] == "Alto"
    assert critico["nivel_alerta"] == "Crítico"
    assert "90+" in critico["justificativa"]
    assert critico["acao_sugerida"]


def test_cenario_melhora_reduz_saldos():
    r = simular_cenario(1_000_000, 120_000, 45_000, -1, -0.5)
    assert r["saldo_30_cenario"] == pytest.approx(110_000.0)
    assert r["saldo_90_cenario"] == pytest.approx(40_000.0)
    assert r["nivel_alerta"] == "Estável ou melhora"


@pytest.mark.parametrize("s30,s90", [(120_000, 130_000), (1_100_000, 45_000), (-1, 0), (12_000, -10)])
def test_saldos_base_invalidos(s30, s90):
    with pytest.raises(ValueError):
        simular_cenario(1_000_000, s30, s90)


def test_choque_invalido_90_ultrapassa_30():
    with pytest.raises(ValueError, match="Cenário impossível"):
        simular_cenario(1_000_000, 120_000, 45_000, 0, 10)


def test_choque_invalido_taxa_negativa():
    with pytest.raises(ValueError, match="Cenário impossível"):
        simular_cenario(1_000_000, 120_000, 45_000, -20, 0)


def test_carteira_zero_e_infinito_sao_invalidos():
    with pytest.raises(ValueError):
        simular_cenario(0, 0, 0)
    with pytest.raises(ValueError):
        simular_cenario(math.inf, 0, 0)


def test_reprodutibilidade_sem_banco():
    args = (1_000_000, 120_000, 45_000, 1.5, 0.5)
    assert simular_cenario(*args) == simular_cenario(*args)

def test_choque_exato_90_igual_30():
    """Valida o cenário limite onde o saldo 90+ iguala o saldo 30+ (taxas exatas de 20%)."""
    resultado = simular_cenario(
        saldo_carteira=100_000,
        saldo_30_base=20_000,
        saldo_90_base=10_000,
        variacao_30_pp=0,
        variacao_90_pp=10,
    )
    assert resultado["taxa_30_cenario_pct"] == 20.0
    assert resultado["taxa_90_cenario_pct"] == 20.0
    assert resultado["saldo_30_cenario"] == 20000.0
    assert resultado["saldo_90_cenario"] == 20000.0


def test_cenario_dados_invalidos_nao_alteram_conciliacao():
    """Garante que uma tentativa de cenário inválido (90+ > 30+) gera ValueError e preserva os 11 indicadores originais."""
    from scripts.indicadores_financeiros import obter_indicadores

    indicadores_antes = obter_indicadores()

    with pytest.raises(ValueError):
        simular_cenario(
            saldo_carteira=100_000,
            saldo_30_base=10_000,
            saldo_90_base=20_000,  # Inválido: 90+ superior a 30+
            variacao_30_pp=0,
            variacao_90_pp=0,
        )

    indicadores_depois = obter_indicadores()
    assert indicadores_antes == indicadores_depois