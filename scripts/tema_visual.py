"""Identidade visual do Financial Intelligence AI — sem alterar regras de negócio.

Estilos são locais ao Streamlit e não carregam fontes/scripts externos.
Não é uma identidade oficial do iFood nem da OpenAI.
"""
from html import escape

CSS = r"""
<style>
:root {
    --fi-bg: #090b10;
    --fi-surface: #101620;
    --fi-surface-2: #161e2a;
    --fi-line: rgba(179, 194, 218, .16);
    --fi-text: #f1f5fa;
    --fi-muted: #a5b2c6;
    --fi-accent: #ef4858;
    --fi-success: #4cc3a2;
}
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #090b10 !important;
    color: var(--fi-text);
}
[data-testid="stAppViewContainer"] {
    background-image:
      radial-gradient(ellipse 720px 320px at 69% -75px, rgba(239,72,88,.12), transparent 72%),
      radial-gradient(ellipse 540px 340px at 12% 0%, rgba(65,105,160,.10), transparent 80%) !important;
    background-repeat: no-repeat !important;
}
.main .block-container, [data-testid="stMainBlockContainer"] {
    padding-top: clamp(1.6rem, 3vw, 3rem);
    max-width: 1480px;
    padding-bottom: 3rem;
}
/* Typography */
h1, h2, h3, h4 { letter-spacing: -0.025em; }
h1 { font-weight: 800 !important; line-height: 1.16 !important; }
h2, h3 { font-weight: 750 !important; }
.stCaptionContainer, [data-testid="stCaptionContainer"],
[data-testid="stMetricLabel"] { color: var(--fi-muted) !important; }
/* Sidebar and navigation */
[data-testid="stSidebar"] {
    background: #10141d !important;
    border-right: 1px solid var(--fi-line) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] > label {
    border-radius: .7rem;
    padding: .57rem .5rem;
    transition: background .2s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
    background: rgba(239,72,88,.08);
}
/* The actual Streamlit widgets are preserved for AppTest. */
[data-testid="stMetric"] {
    min-height: 116px;
    background: linear-gradient(145deg, #141b27, #10151f);
    border: 1px solid var(--fi-line);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    box-shadow: 0 8px 25px rgba(0,0,0,.12);
}
[data-testid="stMetricValue"] {
    font-size: clamp(1.45rem, 2.1vw, 2.3rem) !important;
    font-weight: 750 !important;
    letter-spacing: -.035em;
    color: var(--fi-text) !important;
}
[data-testid="stMetricDelta"] { font-size: .88rem; }
/* Tabs, separators, data and chart panels */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--fi-line);
    gap: .45rem;
}
[data-testid="stTabs"] [role="tab"] { border-radius: 8px 8px 0 0; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #ff7884 !important;
}
[data-testid="stDataFrame"], [data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"], [data-testid="stTable"] {
    border: 1px solid var(--fi-line);
    border-radius: 12px;
    overflow: hidden;
}
hr { border-color: var(--fi-line) !important; }
/* Controls: clear focus states and rounded surfaces */
.stButton > button, .stDownloadButton > button {
    border-radius: 10px !important;
    font-weight: 650 !important;
    min-height: 2.6rem;
    transition: transform .13s ease, border-color .13s ease;
}
.stButton > button:hover:not(:disabled),
.stDownloadButton > button:hover:not(:disabled) { transform: translateY(-1px); }
.stButton > button[kind="primary"] { background: var(--fi-accent) !important; }
[data-testid="stNumberInput"], [data-testid="stDateInput"],
[data-testid="stSelectbox"], [data-testid="stMultiSelect"],
[data-testid="stTextInput"] { border-radius: 10px; }
/* Small non-interactive section banner. */
.fi-context {
    display: flex; flex-wrap: wrap; align-items: center; gap: .65rem;
    background: linear-gradient(90deg, rgba(239,72,88,.10), rgba(22,30,42,.46));
    border: 1px solid var(--fi-line);
    border-left: 3px solid var(--fi-accent);
    border-radius: 11px;
    padding: .7rem .95rem;
    margin: .8rem 0 1.25rem;
}
.fi-context .fi-kicker {
    font-size: .65rem; letter-spacing: .12em; text-transform: uppercase;
    font-weight: 800; color: #ff9aa3;
}
.fi-context .fi-title { color: var(--fi-text); font-weight: 740; }
.fi-context .fi-description { color: var(--fi-muted); font-size: .79rem; }
@media (max-width: 720px) {
    [data-testid="stMetric"] { padding: .75rem; min-height: 94px; }
    .fi-context { gap: .42rem; }
    .main .block-container, [data-testid="stMainBlockContainer"] {
        padding-left: .75rem; padding-right: .75rem;
    }
}

/* FI HOTFIX V1.2: legibilidade */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p { font-size: .88rem !important; }
[data-testid="stMetricLabel"] p { font-size: .88rem !important; line-height: 1.35 !important; }
[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
</style>
"""


def contexto_html(titulo: str, descricao: str, secao: str) -> str:
    """HTML estático para a seção, com conteúdo escapado contra injeção."""
    return (
        '<div class="fi-context">'
        f'<span class="fi-kicker">{escape(secao)}</span>'
        f'<span class="fi-title">{escape(titulo)}</span>'
        f'<span class="fi-description">{escape(descricao)}</span>'
        '</div>'
    )


def aplicar_tema() -> None:
    """Não adiciona métricas, inputs ou regras de negócio."""
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)


def faixa_contexto(titulo: str, descricao: str, secao: str) -> None:
    import streamlit as st
    st.markdown(contexto_html(titulo, descricao, secao), unsafe_allow_html=True)
