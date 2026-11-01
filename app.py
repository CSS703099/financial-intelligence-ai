"""Dashboard privado e local para estudo, com dados sintéticos."""
import sqlite3

import pandas as pd
import streamlit as st

from scripts.analise_pandas import carregar_pedidos, calcular_indicadores
from scripts.dashboard_dados import (
    filtrar_pedidos,
    preparar_detalhes,
    resumo_mensal,
    resumo_restaurantes,
)


def moeda(valor: float) -> str:
    return "R$ " + f"{valor:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


st.set_page_config(
    page_title="Financial Intelligence AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Financial Intelligence AI")
st.caption("Conciliação financeira e auditoria | MVP de portfólio | Dados 100% sintéticos")

try:
    pedidos = carregar_pedidos()
except (FileNotFoundError, sqlite3.Error, pd.errors.DatabaseError) as erro:
    st.error(f"Falha ao carregar o banco: {erro}")
    st.stop()

if pedidos.empty:
    st.warning("A base de dados está vazia.")
    st.stop()

datas = pd.to_datetime(pedidos["data_pedido"], errors="raise")
menor_data, maior_data = datas.min().date(), datas.max().date()
opcoes = sorted(pedidos["restaurante"].unique().tolist())

with st.sidebar:
    st.header("Filtros")
    periodo = st.date_input(
        "Período dos pedidos",
        value=(menor_data, maior_data),
        min_value=menor_data,
        max_value=maior_data,
        format="DD/MM/YYYY",
        key="periodo",
    )
    restaurantes = st.multiselect(
        "Restaurantes", opcoes, default=opcoes, key="restaurantes"
    )
    st.caption("Os indicadores refletem somente o período e os restaurantes selecionados.")

if not isinstance(periodo, (list, tuple)) or len(periodo) != 2:
    st.info("Selecione a data inicial e final para continuar.")
    st.stop()

inicio, fim = periodo
if inicio > fim:
    st.warning("A data inicial não pode ser posterior à data final.")
    st.stop()

recorte = filtrar_pedidos(pedidos, restaurantes, inicio, fim)
if recorte.empty:
    st.warning("Nenhum pedido encontrado para os filtros selecionados.")
    st.stop()

indicadores = calcular_indicadores(recorte)
taxa = indicadores["taxa_divergencia_pct"]

linha1 = st.columns(4)
linha1[0].metric("Total de pedidos", str(indicadores["total_pedidos"]))
linha1[1].metric("Concluídos", str(indicadores["pedidos_concluidos"]))
linha1[2].metric("Divergentes", str(indicadores["pedidos_divergentes"]))
linha1[3].metric("Taxa de divergência", "N/D" if taxa is None else f"{taxa:.2f}%")

linha2 = st.columns(3)
linha2[0].metric("Faturamento bruto", moeda(indicadores["faturamento_bruto"]))
linha2[1].metric("Divergência absoluta", moeda(indicadores["divergencia_absoluta"]))
linha2[2].metric("Divergência líquida", moeda(indicadores["divergencia_liquida"]))

st.divider()
detalhes = preparar_detalhes(recorte)
restaurantes_resumo = resumo_restaurantes(detalhes)
mensal = resumo_mensal(detalhes)

visao, detalhes_tab, auditoria_tab = st.tabs(["Visão executiva", "Pedidos", "Priorização"])

with visao:
    st.subheader("Onde está o maior impacto?")
    if detalhes.empty:
        st.info("Não há pedidos concluídos nos filtros selecionados.")
    else:
        esquerdo, direito = st.columns(2)
        with esquerdo:
            st.markdown("**Impacto absoluto por restaurante (R$)**")
            st.bar_chart(restaurantes_resumo, x="restaurante", y="impacto_absoluto")
        with direito:
            st.markdown("**Evolução mensal do impacto absoluto (R$)**")
            st.line_chart(mensal, x="mes", y="impacto_absoluto")

with detalhes_tab:
    st.subheader("Conciliação dos pedidos concluídos")
    exibicao = detalhes[[
        "pedido_id", "data_pedido", "restaurante", "valor_bruto",
        "repasse_real", "repasse_esperado", "divergencia", "divergencia_absoluta",
    ]].sort_values("divergencia_absoluta", ascending=False)
    st.dataframe(exibicao, hide_index=True, width="stretch")
    st.download_button(
        "Exportar CSV dos pedidos filtrados",
        data=exibicao.to_csv(index=False).encode("utf-8-sig"),
        file_name="conciliacao_sintetica.csv",
        mime="text/csv",
    )

with auditoria_tab:
    st.subheader("Priorização por regras explicáveis")
    st.dataframe(restaurantes_resumo, hide_index=True, width="stretch")
    st.caption(
        "Crítico: impacto ≥ R$ 10 e taxa ≥ 30%; Alto: impacto ≥ R$ 5 "
        "ou taxa ≥ 30%; Moderado: diferença não zero; Senão: sem alerta. "
        "Regras didáticas aplicadas ao período e aos restaurantes filtrados."
    )

st.divider()
st.caption("Projeto independente de portfólio. Não representa dados ou operações reais do iFood. Não há IA integrada nesta etapa.")
