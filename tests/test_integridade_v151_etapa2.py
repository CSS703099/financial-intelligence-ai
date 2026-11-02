"""Casos adversariais: dados monetários e consistência de evidências."""
import copy
import math
import pytest
from scripts.analise_pandas import calcular_indicadores, carregar_pedidos
from scripts.ia_explicavel import criar_dossie_credito, criar_dossie_repasses
from scripts.simulador_credito import simular_cenario


@pytest.mark.parametrize('valor', [float('nan'), float('inf'), -1, 'invalido', None, 1.234])
def test_rejeita_valor_monetario_invalido(valor):
    df = carregar_pedidos().query("status == 'concluido'").head(1).copy()
    df['valor_bruto'] = df['valor_bruto'].astype(object)
    df.loc[df.index[0], 'valor_bruto'] = valor
    with pytest.raises(ValueError):
        calcular_indicadores(df)


def test_rejeita_taxas_maiores_que_bruto():
    df = carregar_pedidos().query("status == 'concluido'").head(1).copy()
    df.loc[df.index[0], 'taxa_plataforma'] = 100000
    with pytest.raises(ValueError, match='Taxas superiores'):
        calcular_indicadores(df)


def test_repasses_rejeita_contagem_incoerente():
    indicadores = calcular_indicadores(carregar_pedidos())
    indicadores['pedidos_divergentes'] = indicadores['pedidos_concluidos'] + 1
    with pytest.raises(ValueError, match='Contagens'):
        criar_dossie_repasses(indicadores)


def test_repasses_rejeita_taxa_incoerente():
    indicadores = calcular_indicadores(carregar_pedidos())
    indicadores['taxa_divergencia_pct'] = 99
    with pytest.raises(ValueError, match='Taxa'):
        criar_dossie_repasses(indicadores)


def test_credito_rejeita_variacao_incoerente():
    resultado = simular_cenario(1000000, 120000, 45000, 1.5, 0.5)
    resultado['variacao_30_pp'] = 5
    with pytest.raises(ValueError, match='Variação'):
        criar_dossie_credito(resultado)


def test_credito_rejeita_saldo_incoerente():
    resultado = simular_cenario(1000000, 120000, 45000, 1.5, 0.5)
    resultado['delta_saldo_30'] = 1
    with pytest.raises(ValueError, match='Variação de saldo'):
        criar_dossie_credito(resultado)


def test_credito_rejeita_nao_finito():
    resultado = simular_cenario(1000000, 120000, 45000, 1.5, 0.5)
    resultado['taxa_30_base_pct'] = math.inf
    with pytest.raises(ValueError):
        criar_dossie_credito(resultado)
