
# GUIA PARA INICIANTES — Testes de cálculos financeiros e tratamento dos dados
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
import pytest
import pandas as pd
from scripts.indicadores_financeiros import obter_indicadores
from scripts.analise_pandas import (
    carregar_pedidos,
    calcular_indicadores
)

def test_pandas_equivalente_ao_sql():
    """Compara os indicadores calculados via Pandas com a versão aprovada em SQL."""
    indicadores_sql = obter_indicadores()
    df = carregar_pedidos()
    indicadores_pandas = calcular_indicadores(df)
    
    assert set(indicadores_sql) == set(indicadores_pandas)
    for nome, valor_sql in indicadores_sql.items():
        assert indicadores_pandas[nome] == pytest.approx(
            valor_sql
        ), f"Divergência no indicador: {nome}"

def test_base_vazia():
    """Verifica se os totais zeram corretamente e a taxa retorna None quando não há pedidos concluídos."""
    df = carregar_pedidos()
    vazio = df.iloc[0:0].copy()
    indicadores = calcular_indicadores(vazio)
    
    assert indicadores["total_pedidos"] == 0
    assert indicadores["pedidos_concluidos"] == 0
    assert indicadores["divergencia_absoluta"] == 0.0
    assert indicadores["taxa_divergencia_pct"] is None

def test_sem_divergencias():
    """Garante que quando os repasses reais coincidem com os esperados, divergências e taxa são iguais a zero."""
    df = carregar_pedidos()
    df_sem_div = df.copy()
    
    # Ajustar repasse real para refletir exatamente (valor_bruto - taxa_plataforma - taxa_logistica) nos concluidos
    mascara = df_sem_div["status"] == "concluido"
    repasse_perfeito = (
        df_sem_div.loc[mascara, "valor_bruto"] 
        - df_sem_div.loc[mascara, "taxa_plataforma"] 
        - df_sem_div.loc[mascara, "taxa_logistica"]
    )
    df_sem_div.loc[mascara, "repasse_real"] = repasse_perfeito
    
    indicadores = calcular_indicadores(df_sem_div)
    
    assert indicadores["pedidos_divergentes"] == 0
    assert indicadores["divergencia_liquida"] == 0.0
    assert indicadores["divergencia_absoluta"] == 0.0
    assert indicadores["taxa_divergencia_pct"] == 0.0

def test_banco_inexistente():
    """Confere se carregar pedidos com caminho inválido lança FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        carregar_pedidos("banco_fantasma.db")

def test_dataframe_preservado():
    """Assegura que a função calcular_indicadores() não modifica o DataFrame original recebido."""
    df = carregar_pedidos()
    # Criar uma cópia e tirar snapshot das colunas/tamanho
    df_copia = df.copy()
    colunas_originais = list(df.columns)
    tamanho_original = len(df)
    
    _ = calcular_indicadores(df)
    
    # Verificar se o DataFrame original permaneceu intacto
    assert list(df.columns) == colunas_originais
    assert len(df) == tamanho_original
    pd.testing.assert_frame_equal(df, df_copia)