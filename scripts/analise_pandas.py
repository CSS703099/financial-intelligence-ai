import sqlite3
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
import math
from contextlib import closing
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
BANCO = RAIZ / "financial_intelligence.db"

def carregar_pedidos(caminho_banco=BANCO):
    """
    Carrega a tabela 'pedidos' do banco SQLite em um DataFrame Pandas
    utilizando conexão somente para leitura.
    """
    caminho = Path(caminho_banco)
    if not caminho.is_file():
        raise FileNotFoundError(
            f"Banco não encontrado: {caminho}"
        )
    with closing(
        sqlite3.connect(
            f"file:{caminho.resolve().as_posix()}?mode=ro",
            uri=True
        )
    ) as conexao:
        df = pd.read_sql_query(
            "SELECT * FROM pedidos",
            conexao
        )
    return df

def _centavos_validos(valor, coluna: str) -> int:
    """Converte BRL em centavos sem arredondar valores inválidos silenciosamente."""
    if isinstance(valor, (bool, complex)) or pd.isna(valor):
        raise ValueError(f"{coluna}: valor monetário inválido.")
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{coluna}: valor monetário inválido.") from None
    if not numero.is_finite() or numero < 0:
        raise ValueError(f"{coluna}: valor monetário inválido.")
    centavos = numero * 100
    arredondado = centavos.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)
    # Admite apenas resíduos de representação binária, não frações reais de centavo.
    if abs(centavos - arredondado) > Decimal("0.000001"):
        raise ValueError(f"{coluna}: mais de duas casas decimais.")
    inteiro = int(arredondado)
    if inteiro > 9_223_372_036_854_775_807:
        raise ValueError(f"{coluna}: valor fora do intervalo suportado.")
    return inteiro


def calcular_indicadores(df: pd.DataFrame) -> dict:
    """
    Calcula os 11 indicadores financeiros utilizando Pandas e operações em centavos,
    garantindo que o DataFrame original não seja modificado.
    """
    # 1. Garantir que o DataFrame original não seja alterado
    df_trab = df.copy()

    # 2. Contagens gerais
    total_pedidos = int(len(df_trab))
    
    # Filtrar pedidos concluídos e cancelados
    concluidos = df_trab.loc[df_trab["status"] == "concluido"].copy()
    cancelados = df_trab.loc[df_trab["status"] == "cancelado"].copy()
    
    pedidos_concluidos = int(len(concluidos))
    pedidos_cancelados = int(len(cancelados))

    # Caso a base esteja vazia de concluídos
    if pedidos_concluidos == 0:
        return {
            "total_pedidos": total_pedidos,
            "pedidos_concluidos": 0,
            "pedidos_cancelados": pedidos_cancelados,
            "faturamento_bruto": 0.0,
            "taxas_plataforma": 0.0,
            "taxas_logistica": 0.0,
            "repasses_realizados": 0.0,
            "pedidos_divergentes": 0,
            "divergencia_liquida": 0.0,
            "divergencia_absoluta": 0.0,
            "taxa_divergencia_pct": None
        }

    # 3. Conversão de colunas monetárias para centavos inteiros (precisão monetária)
    colunas_monetarias = [
        "valor_bruto",
        "taxa_plataforma",
        "taxa_logistica",
        "repasse_real"
    ]
    for coluna in colunas_monetarias:
        concluidos[f"{coluna}_centavos"] = concluidos[coluna].map(
            lambda valor: _centavos_validos(valor, coluna)
        )

    if ((concluidos["taxa_plataforma_centavos"] + concluidos["taxa_logistica_centavos"]) > concluidos["valor_bruto_centavos"]).any():
        raise ValueError("Taxas superiores ao valor bruto do pedido.")

    # 4. Cálculo de repasse esperado e divergências em centavos
    # Repasse esperado = valor_bruto - taxa_plataforma - taxa_logistica
    concluidos["repasse_esperado_centavos"] = (
        concluidos["valor_bruto_centavos"] 
        - concluidos["taxa_plataforma_centavos"] 
        - concluidos["taxa_logistica_centavos"]
    )

    # Divergência por pedido = repasse_esperado - repasse_real
    concluidos["divergencia_centavos"] = (
        concluidos["repasse_esperado_centavos"] 
        - concluidos["repasse_real_centavos"]
    )

    # Pedidos divergentes: divergência diferente de zero
    concluidos["eh_divergente"] = concluidos["divergencia_centavos"] != 0
    pedidos_divergentes = int(concluidos["eh_divergente"].sum())

    # 5. Totais financeiros em centavos convertidos para reais (divididos por 100.0)
    faturamento_bruto = float(concluidos["valor_bruto_centavos"].sum() / 100.0)
    taxas_plataforma = float(concluidos["taxa_plataforma_centavos"].sum() / 100.0)
    taxas_logistica = float(concluidos["taxa_logistica_centavos"].sum() / 100.0)
    repasses_realizados = float(concluidos["repasse_real_centavos"].sum() / 100.0)
    
    divergencia_liquida = float(concluidos["divergencia_centavos"].sum() / 100.0)
    divergencia_absoluta = float(concluidos["divergencia_centavos"].abs().sum() / 100.0)

    # 6. Taxa percentual de divergência arredondada a 2 casas decimais
    taxa_divergencia_pct = round((pedidos_divergentes * 100.0) / pedidos_concluidos, 2)

    return {
        "total_pedidos": total_pedidos,
        "pedidos_concluidos": pedidos_concluidos,
        "pedidos_cancelados": pedidos_cancelados,
        "faturamento_bruto": faturamento_bruto,
        "taxas_plataforma": taxas_plataforma,
        "taxas_logistica": taxas_logistica,
        "repasses_realizados": repasses_realizados,
        "pedidos_divergentes": pedidos_divergentes,
        "divergencia_liquida": divergencia_liquida,
        "divergencia_absoluta": divergencia_absoluta,
        "taxa_divergencia_pct": taxa_divergencia_pct
    }

def main():
    try:
        df = carregar_pedidos()
        indicadores = calcular_indicadores(df)
        print("FINANCIAL INTELLIGENCE AI — ANÁLISE PANDAS")
        print("-" * 45)
        for chave, valor in indicadores.items():
            print(f"{chave}: {valor}")
    except Exception as e:
        print(f"Erro na execução: {e}")

if __name__ == "__main__":
    main()