"""Transformações testáveis para o painel Financial Intelligence AI.

O dashboard usa somente dados sintéticos. Os cálculos financeiros
respeitam centavos inteiros e não alteram a entrada.
"""

# GUIA PARA INICIANTES — Preparação dos gráficos
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
from datetime import date

import pandas as pd

COLUNAS_MONETARIAS = (
    "valor_bruto",
    "taxa_plataforma",
    "taxa_logistica",
    "repasse_real",
)


def filtrar_pedidos(
    df: pd.DataFrame,
    restaurantes: list[str],
    inicio: date,
    fim: date,
) -> pd.DataFrame:
    """Recorta por restaurante e período inclusivo, preservando a entrada."""
    if inicio > fim:
        raise ValueError("Data inicial posterior à data final.")

    datas = pd.to_datetime(df["data_pedido"], errors="raise").dt.date
    mascara = datas.between(inicio, fim) & df["restaurante"].isin(restaurantes)
    return df.loc[mascara].copy()


def preparar_detalhes(df: pd.DataFrame) -> pd.DataFrame:
    """Inclui cálculos por pedido concluído em centavos (sem mutar df)."""
    dados = df.loc[df["status"] == "concluido"].copy()

    for coluna in COLUNAS_MONETARIAS:
        dados[f"{coluna}_centavos"] = (
            dados[coluna].mul(100).round().astype("int64")
        )

    dados["repasse_esperado_centavos"] = (
        dados["valor_bruto_centavos"]
        - dados["taxa_plataforma_centavos"]
        - dados["taxa_logistica_centavos"]
    )
    dados["divergencia_centavos"] = (
        dados["repasse_esperado_centavos"] - dados["repasse_real_centavos"]
    )
    dados["repasse_esperado"] = dados["repasse_esperado_centavos"] / 100
    dados["divergencia"] = dados["divergencia_centavos"] / 100
    dados["divergencia_absoluta"] = dados["divergencia_centavos"].abs() / 100
    return dados


def resumo_restaurantes(detalhes: pd.DataFrame) -> pd.DataFrame:
    """Agrega impacto e taxa por restaurante no filtro atual."""
    colunas = [
        "restaurante", "pedidos_concluidos", "pedidos_divergentes",
        "taxa_divergencia_pct", "impacto_absoluto", "prioridade",
    ]
    if detalhes.empty:
        return pd.DataFrame(columns=colunas)

    auxiliar = detalhes.assign(
        divergente=detalhes["divergencia_centavos"].ne(0).astype(int),
        impacto_centavos=detalhes["divergencia_centavos"].abs(),
    )
    resumo = auxiliar.groupby("restaurante", as_index=False).agg(
        pedidos_concluidos=("pedido_id", "count"),
        pedidos_divergentes=("divergente", "sum"),
        impacto_centavos=("impacto_centavos", "sum"),
    )
    resumo["taxa_divergencia_pct"] = (
        resumo["pedidos_divergentes"] * 100 / resumo["pedidos_concluidos"]
    ).round(2)
    resumo["impacto_absoluto"] = resumo["impacto_centavos"] / 100

    def classificar(linha):
        impacto = linha["impacto_absoluto"]
        taxa = linha["taxa_divergencia_pct"]
        if impacto >= 10 and taxa >= 30:
            return "Crítico"
        if impacto >= 5 or taxa >= 30:
            return "Alto"
        if linha["pedidos_divergentes"] > 0:
            return "Moderado"
        return "Sem alerta"

    resumo["prioridade"] = resumo.apply(classificar, axis=1)
    return (
        resumo[colunas]
        .sort_values(["impacto_absoluto", "restaurante"], ascending=[False, True])
        .reset_index(drop=True)
    )


def resumo_mensal(detalhes: pd.DataFrame) -> pd.DataFrame:
    """Soma o impacto absoluto por mês do período filtrado."""
    if detalhes.empty:
        return pd.DataFrame(columns=["mes", "impacto_absoluto"])
    auxiliar = detalhes.assign(
        mes=pd.to_datetime(detalhes["data_pedido"]).dt.to_period("M").dt.to_timestamp(),
        impacto_centavos=detalhes["divergencia_centavos"].abs(),
    )
    mensal = auxiliar.groupby("mes", as_index=False)["impacto_centavos"].sum()
    mensal["impacto_absoluto"] = mensal["impacto_centavos"] / 100
    return mensal[["mes", "impacto_absoluto"]].sort_values("mes")
