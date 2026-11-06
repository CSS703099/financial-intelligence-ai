"""Demonstração de parecer manual no Streamlit. Nenhuma chamada a IA/API.

Usa SOMENTE os cenários FIXOS didáticos de demo_parecer_offline;
não consome os sliders nem filtros atuais de outros módulos.
"""

# GUIA PARA INICIANTES — Tela da demonstração offline
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from scripts.demo_parecer_offline import montar_demo
from scripts.ia_explicavel import aprovar_parecer, hash_dossie, validar_parecer

ORIGEM = "MODELO_MANUAL_DE_TESTE_SEM_IA"


def _reiniciar_revisao_ao_trocar_cenario() -> None:
    """Uma revisão de crédito não pode valer para repasses (e vice-versa)."""
    for chave in (
        "demo_offline_revisor",
        "demo_offline_conferido",
        "demo_offline_palavra",
        "demo_offline_autorizacao",
    ):
        st.session_state.pop(chave, None)



def construir_exportacao(dossie: dict, parecer: dict, revisor: str) -> dict:
    """Valida novamente e marca a exportação como conteúdo MANUAL, não gerado por IA."""
    validar_parecer(parecer, dossie)
    pacote = aprovar_parecer(parecer, dossie, aprovador=revisor)
    pacote["origem_parecer"] = ORIGEM
    pacote["uso_permitido"] = "DEMONSTRACAO_LOCAL_COM_DADOS_SINTETICOS"
    return pacote


def formatar_parecer_para_painel(dossie: dict, parecer: dict) -> str:
    """Valida e apresenta TODO o parecer como um só bloco de Markdown.

    Isso impede que o Streamlit reutilize ações/limitações do cenário anterior
    enquanto atualiza prioridade e evidências do cenário novo.
    """
    validar_parecer(parecer, dossie)
    linhas = [
        "#### Parecer manual de exemplo",
        "**" + parecer["titulo"] + "**",
        parecer["diagnostico"],
        "**Prioridade didática:** " + parecer["prioridade"],
        "**Evidências citadas:** " + ", ".join(parecer["evidencias_ids"]),
        "**Ações sujeitas a revisão:**",
    ]
    for acao in parecer["acoes"]:
        linhas.append("- " + acao["acao"] + " — " + ", ".join(acao["evidencias_ids"]))
    linhas.append("**Limitações:**")
    for limitacao in parecer["limitacoes"]:
        linhas.append("- " + limitacao)
    return "\n\n".join(linhas)


def renderizar_demo_offline() -> None:
    with st.expander("Demonstração offline — parecer manual com aprovação humana (sem API)", expanded=False):
        st.warning(
            "EXEMPLO REDIGIDO MANUALMENTE: este parecer NÃO foi gerado por inteligência artificial. "
            "Não autoriza operações financeiras. A validação automática não comprova veracidade semântica."
        )
        tipo = st.selectbox(
            "Cenário didático fixo", ["credito", "repasses"],
            format_func=lambda x: "Carteira de crédito — exemplo fixo" if x == "credito" else "Conciliação de repasses — base integral",
            key="demo_offline_tipo",
            on_change=_reiniciar_revisao_ao_trocar_cenario,
        )
        st.caption(
            "Esta demonstração usa cenários independentes: NÃO acompanha automaticamente os sliders "
            "de crédito ou os filtros de restaurantes."
        )
        try:
            dossie, parecer = montar_demo(tipo)
        except (ValueError, FileNotFoundError, KeyError) as erro:
            st.error(f"Demonstração indisponível: {type(erro).__name__}.")
            return

        chave = hash_dossie(dossie)
        st.markdown("#### Evidências do cenário demonstrativo")
        st.dataframe(pd.DataFrame(dossie["evidencias"]), hide_index=True, width="stretch")
        st.caption("Dossiê SHA-256: " + chave[:16] + "…")
        # Parecer ATÔMICO: título, prioridade, IDs, ações e limitações são um
        # único elemento. Na troca de cenário não há filhos Markdown defasados.
        try:
            texto_parecer = formatar_parecer_para_painel(dossie, parecer)
        except (ValueError, KeyError, TypeError):
            st.error("Parecer demonstrativo inconsistente. Exibição e exportação bloqueadas.")
            return
        with st.container(key=f"demo_offline_resultado_{tipo}_{chave[:12]}"):
            st.markdown(texto_parecer)

        st.markdown("#### Revisão humana para exportar")
        revisor = st.text_input("Identificação do revisor (não inserir dados pessoais sensíveis)", key="demo_offline_revisor")
        conferido = st.checkbox("Revisei os dados sintéticos e entendo que é um exemplo MANUAL", key="demo_offline_conferido")
        texto_aprovar = st.text_input("Para aprovar a exportação, digite APROVAR", key="demo_offline_palavra")
        identificador = (tipo, chave, revisor.strip())
        salvo = st.session_state.get("demo_offline_autorizacao")
        if salvo and salvo["identificador"] != identificador:
            st.session_state.pop("demo_offline_autorizacao", None)
            salvo = None
        habilitado = bool(revisor.strip() and conferido and texto_aprovar.strip() == "APROVAR")
        if st.button("Autorizar apenas a exportação local do exemplo", disabled=not habilitado, key="demo_offline_aprovar"):
            try:
                pacote = construir_exportacao(dossie, parecer, revisor)
                st.session_state["demo_offline_autorizacao"] = {"identificador": identificador, "pacote": pacote}
                salvo = st.session_state["demo_offline_autorizacao"]
            except ValueError:
                st.error("A revisão não passou nas verificações. Exportação bloqueada.")
        if salvo and habilitado and salvo["identificador"] == identificador:
            st.success("Exemplo manual revisado. A exportação requer clique no botão abaixo.")
            st.download_button(
                "Baixar EXEMPLO MANUAL revisado (JSON)",
                data=json.dumps(salvo["pacote"], ensure_ascii=False, indent=2),
                file_name=f"parecer_EXEMPLO_{tipo}_manual.json",
                mime="application/json",
                key="demo_offline_download",
            )
