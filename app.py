
"""Dashboard privado e local para estudo, com dados sintéticos."""

import sqlite3

import pandas as pd
import streamlit as st

from scripts.analise_pandas import (
    carregar_pedidos,
    calcular_indicadores,
)
from scripts.simulador_credito import simular_cenario
from scripts.ia_streamlit import renderizar_ia
from scripts.demo_parecer_ui import renderizar_demo_offline
from scripts.tema_visual import aplicar_tema, faixa_contexto
from scripts.dashboard_dados import (
    filtrar_pedidos,
    preparar_detalhes,
    resumo_mensal,
    resumo_restaurantes,
)


def moeda(valor: float) -> str:
    """Formata valores monetários em reais."""
    return (
        "R$ "
        + f"{valor:,.2f}"
        .replace(",", "@")
        .replace(".", ",")
        .replace("@", ".")
    )


# ============================================================
# 1. CONFIGURAÇÃO GERAL DO DASHBOARD
# ============================================================

st.set_page_config(
    page_title="Financial Intelligence AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_tema()
st.title("Financial Intelligence AI")

st.caption(
    "Laboratório de finanças | "
    "Conciliação + cenários de crédito | "
    "Dados 100% sintéticos"
)


# ============================================================
# 2. SELEÇÃO DA ÁREA DE ANÁLISE
# ============================================================

# O simulador de crédito é independente dos dados de pedidos.
# Nenhuma simulação modifica o banco SQLite.

area = st.sidebar.radio(
    "Área de análise",
    [
        "Conciliação de repasses",
        "Crédito — cenários 30+/90+",
        "IA — parecer explicável",
    ],
    key="area_analise",
)


# ============================================================
# 3. SIMULADOR DE CRÉDITO — 30+ E 90+
# ============================================================

if area == "IA — parecer explicável":
    faixa_contexto("IA e governança", "Evidências auditáveis e aprovação humana", "MÓDULO 03")
    renderizar_ia()
    renderizar_demo_offline()
    st.stop()


if area == "Crédito — cenários 30+/90+":
    faixa_contexto("Cenários 30+ e 90+", "Simulação hipotética, sem decisão automática", "MÓDULO 02")

    st.subheader(
        "Simulador de carteira de crédito — 30+ e 90+"
    )

    st.info(
        "Dados hipotéticos independentes dos pedidos. "
        "90+ está contido em 30+. "
        "O cenário é uma análise de sensibilidade, "
        "não uma previsão nem uma recomendação "
        "automatizada de crédito."
    )

    # --------------------------------------------------------
    # 3.1. Parâmetros da carteira
    # --------------------------------------------------------

    a, b, c = st.columns(3)

    carteira = a.number_input(
        "Saldo total da carteira (R$)",
        min_value=1.0,
        value=1_000_000.0,
        step=10_000.0,
        format="%.2f",
        key="credito_carteira",
    )

    atraso30 = b.number_input(
        "Saldo de contratos 30+ (R$)",
        min_value=0.0,
        value=120_000.0,
        step=1_000.0,
        format="%.2f",
        key="credito_saldo30",
    )

    atraso90 = c.number_input(
        "Saldo de contratos 90+ (R$)",
        min_value=0.0,
        value=45_000.0,
        step=1_000.0,
        format="%.2f",
        key="credito_saldo90",
    )

    # --------------------------------------------------------
    # 3.2. Variação das taxas
    # --------------------------------------------------------

    d, e = st.columns(2)

    delta30 = d.slider(
        "Variação da taxa 30+ (p.p.)",
        min_value=-10.0,
        max_value=10.0,
        value=1.5,
        step=0.5,
        key="credito_delta30",
    )

    delta90 = e.slider(
        "Variação da taxa 90+ (p.p.)",
        min_value=-10.0,
        max_value=10.0,
        value=0.5,
        step=0.5,
        key="credito_delta90",
    )

    # --------------------------------------------------------
    # 3.3. Execução do simulador
    # --------------------------------------------------------

    try:
        resultado = simular_cenario(
            carteira,
            atraso30,
            atraso90,
            delta30,
            delta90,
        )

    except ValueError as erro:
        st.error(
            f"Corrija os parâmetros do cenário: {erro}"
        )
        st.stop()

    # --------------------------------------------------------
    # 3.4. Indicadores financeiros
    # --------------------------------------------------------

    st.session_state["ultimo_cenario_credito"] = resultado

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "30+ — base",
        f"{resultado['taxa_30_base_pct']:.2f}%",
    )

    k2.metric(
        "30+ — cenário",
        f"{resultado['taxa_30_cenario_pct']:.2f}%",
        delta=f"{delta30:+.2f} p.p.",
        delta_color="inverse",
    )

    k3.metric(
        "90+ — base",
        f"{resultado['taxa_90_base_pct']:.2f}%",
    )

    k4.metric(
        "90+ — cenário",
        f"{resultado['taxa_90_cenario_pct']:.2f}%",
        delta=f"{delta90:+.2f} p.p.",
        delta_color="inverse",
    )

    # --------------------------------------------------------
    # 3.5. Comparação dos saldos em atraso
    # --------------------------------------------------------

    st.markdown("### Comparação dos saldos em atraso")

    comparacao = pd.DataFrame(
        {
            "Faixa": [
                "30+",
                "90+",
            ],
            "Base (R$)": [
                resultado["saldo_30_base"],
                resultado["saldo_90_base"],
            ],
            "Cenário (R$)": [
                resultado["saldo_30_cenario"],
                resultado["saldo_90_cenario"],
            ],
        }
    )

    # stack=False impede a soma visual entre Base e Cenário.
    # As barras aparecem lado a lado.

    st.bar_chart(
        comparacao,
        x="Faixa",
        y=["Base (R$)", "Cenário (R$)"],
        stack=False,
    )

    st.dataframe(
        comparacao,
        hide_index=True,
        width="stretch",
    )

    # --------------------------------------------------------
    # 3.6. Diagnóstico e recomendação explicável
    # --------------------------------------------------------

    st.subheader(
        f"Prioridade didática: {resultado['nivel_alerta']}"
    )

    st.write(
        f"**Por quê:** {resultado['justificativa']}"
    )

    st.write(
        "**Ação proposta para revisão humana:** "
        f"{resultado['acao_sugerida']}"
    )

    st.caption(
        "As regras de prioridade são hipotéticas; "
        "nenhum contrato foi analisado e nenhuma "
        "decisão financeira é executada."
    )

    # Encerra somente a renderização desta área.
    # Não acessa nem modifica a base de pedidos.

    st.stop()


# ============================================================
# 4. CONCILIAÇÃO FINANCEIRA DE PEDIDOS
# ============================================================

# ------------------------------------------------------------
# 4.1. Carregamento do SQLite
# ------------------------------------------------------------

faixa_contexto("Conciliação de repasses", "Indicadores de pagamentos e divergências", "MÓDULO 01")

try:
    pedidos = carregar_pedidos()

except (
    FileNotFoundError,
    sqlite3.Error,
    pd.errors.DatabaseError,
) as erro:

    st.error(
        f"Falha ao carregar o banco: {erro}"
    )
    st.stop()


if pedidos.empty:
    st.warning(
        "A base de dados está vazia."
    )
    st.stop()


# ------------------------------------------------------------
# 4.2. Preparação dos filtros
# ------------------------------------------------------------

datas = pd.to_datetime(
    pedidos["data_pedido"],
    errors="raise",
)

menor_data = datas.min().date()
maior_data = datas.max().date()

opcoes = sorted(
    pedidos["restaurante"].unique().tolist()
)


with st.sidebar:

    st.header("Filtros")

    periodo = st.date_input(
        "Período dos pedidos",
        value=(
            menor_data,
            maior_data,
        ),
        min_value=menor_data,
        max_value=maior_data,
        format="DD/MM/YYYY",
        key="periodo",
    )

    restaurantes = st.multiselect(
        "Restaurantes",
        opcoes,
        default=opcoes,
        key="restaurantes",
    )

    st.caption(
        "Os indicadores refletem somente o período "
        "e os restaurantes selecionados."
    )


# ------------------------------------------------------------
# 4.3. Validação dos filtros
# ------------------------------------------------------------

if (
    not isinstance(periodo, (list, tuple))
    or len(periodo) != 2
):
    st.info(
        "Selecione a data inicial e final para continuar."
    )
    st.stop()


inicio, fim = periodo

if inicio > fim:
    st.warning(
        "A data inicial não pode ser posterior à data final."
    )
    st.stop()


recorte = filtrar_pedidos(
    pedidos,
    restaurantes,
    inicio,
    fim,
)

if recorte.empty:
    st.warning(
        "Nenhum pedido encontrado para os filtros selecionados."
    )
    st.stop()


# ============================================================
# 5. INDICADORES EXECUTIVOS
# ============================================================

indicadores = calcular_indicadores(recorte)

taxa = indicadores["taxa_divergencia_pct"]


# ------------------------------------------------------------
# 5.1. Primeira linha de indicadores
# ------------------------------------------------------------

linha1 = st.columns(4)

linha1[0].metric(
    "Total de pedidos",
    str(indicadores["total_pedidos"]),
)

linha1[1].metric(
    "Concluídos",
    str(indicadores["pedidos_concluidos"]),
)

linha1[2].metric(
    "Divergentes",
    str(indicadores["pedidos_divergentes"]),
)

linha1[3].metric(
    "Taxa de divergência",
    "N/D" if taxa is None else f"{taxa:.2f}%",
)


# ------------------------------------------------------------
# 5.2. Segunda linha de indicadores
# ------------------------------------------------------------

linha2 = st.columns(3)

linha2[0].metric(
    "Faturamento bruto",
    moeda(indicadores["faturamento_bruto"]),
)

linha2[1].metric(
    "Divergência absoluta",
    moeda(indicadores["divergencia_absoluta"]),
)

linha2[2].metric(
    "Divergência líquida",
    moeda(indicadores["divergencia_liquida"]),
)


# ============================================================
# 6. PROCESSAMENTO PARA OS GRÁFICOS
# ============================================================

st.divider()

detalhes = preparar_detalhes(recorte)

restaurantes_resumo = resumo_restaurantes(detalhes)

mensal = resumo_mensal(detalhes)


# ============================================================
# 7. ABAS DO DASHBOARD
# ============================================================

visao, detalhes_tab, auditoria_tab = st.tabs(
    [
        "Visão executiva",
        "Pedidos",
        "Priorização",
    ]
)


# ------------------------------------------------------------
# 7.1. Visão executiva
# ------------------------------------------------------------

with visao:

    st.subheader(
        "Onde está o maior impacto?"
    )

    if detalhes.empty:

        st.info(
            "Não há pedidos concluídos nos filtros selecionados."
        )

    else:

        esquerdo, direito = st.columns(2)

        with esquerdo:

            st.markdown(
                "**Impacto absoluto por restaurante (R$)**"
            )

            st.bar_chart(
                restaurantes_resumo,
                x="restaurante",
                y="impacto_absoluto",
            )

        with direito:

            st.markdown(
                "**Evolução mensal do impacto absoluto (R$)**"
            )

            # FI HOTFIX V1.2: mes categorico
            mensal_grafico = mensal.copy()
            mensal_grafico["Mês"] = mensal_grafico["mes"].dt.strftime("%m/%Y")
            st.bar_chart(mensal_grafico, x="Mês", y="impacto_absoluto")


# ------------------------------------------------------------
# 7.2. Conciliação por pedido
# ------------------------------------------------------------

with detalhes_tab:

    st.subheader(
        "Conciliação dos pedidos concluídos"
    )

    exibicao = detalhes[
        [
            "pedido_id",
            "data_pedido",
            "restaurante",
            "valor_bruto",
            "repasse_real",
            "repasse_esperado",
            "divergencia",
            "divergencia_absoluta",
        ]
    ].sort_values(
        "divergencia_absoluta",
        ascending=False,
    )

    st.dataframe(
        exibicao,
        hide_index=True,
        width="stretch",
    )

    st.download_button(
        "Exportar CSV dos pedidos filtrados",
        data=exibicao.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="conciliacao_sintetica.csv",
        mime="text/csv",
    )


# ------------------------------------------------------------
# 7.3. Priorização por regras
# ------------------------------------------------------------

with auditoria_tab:

    st.subheader(
        "Priorização por regras explicáveis"
    )

    st.dataframe(
        restaurantes_resumo,
        hide_index=True,
        width="stretch",
    )

    st.caption(
        "Crítico: impacto ≥ R$ 10 e taxa ≥ 30%; "
        "Alto: impacto ≥ R$ 5 ou taxa ≥ 30%; "
        "Moderado: diferença não zero; "
        "Senão: sem alerta. "
        "Regras didáticas aplicadas ao período "
        "e aos restaurantes filtrados."
    )


# ============================================================
# 8. INFORMAÇÕES E LIMITAÇÕES
# ============================================================

st.divider()

st.caption(
    "Projeto independente de portfólio. "
    "Não representa dados ou operações reais do iFood. "
    "IA generativa disponível apenas por clique na área de parecer e com chave de API."
)
