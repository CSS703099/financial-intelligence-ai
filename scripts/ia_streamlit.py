"""Interface Python 05 — geração opcional e aprovação local explícita."""
import json
import os

import pandas as pd
import streamlit as st

from scripts.analise_pandas import carregar_pedidos, calcular_indicadores
from scripts.ia_explicavel import (
    aprovar_parecer,
    criar_dossie_credito,
    criar_dossie_repasses,
    gerar_parecer,
    hash_dossie,
)
from scripts.simulador_credito import simular_cenario


def renderizar_ia():
    st.subheader("IA generativa — parecer financeiro com evidências")
    st.caption("Somente dados sintéticos. Geração mediante clique; a IA não calcula os números nem executa decisões.")

    fonte = st.selectbox("Origem dos indicadores", ["Crédito 30+/90+", "Conciliação de repasses"], key="ia_fonte")
    if fonte == "Crédito 30+/90+":
        resultado = st.session_state.get("ultimo_cenario_credito")
        if resultado is None:
            st.info("Ainda não há cenário desta sessão. Usando apenas a simulação didática padrão do Python 04.")
            resultado = simular_cenario(1_000_000, 120_000, 45_000, 1.5, 0.5)
        dossie = criar_dossie_credito(resultado)
    else:
        try:
            dados = carregar_pedidos()
            dossie = criar_dossie_repasses(calcular_indicadores(dados))
        except (FileNotFoundError, ValueError, KeyError) as erro:
            st.error(f"Não foi possível preparar as evidências: {erro}")
            return

    identificador = hash_dossie(dossie)
    st.markdown("#### Evidências verificadas pelo Python")
    st.dataframe(pd.DataFrame(dossie["evidencias"]), hide_index=True, width="stretch")
    st.markdown(f"**Prioridade calculada:** {dossie['prioridade_calculada']}")
    st.caption("A IA recebe somente este dossiê resumido — nunca o CSV completo ou os registros individuais.")

    # Se mudar qualquer parâmetro/fonte, o parecer anterior deixa de valer.
    atual = st.session_state.get("ia_parecer")
    if atual is not None and atual.get("hash") != identificador:
        st.session_state.pop("ia_parecer", None)
        st.session_state.pop("ia_aprovacao", None)
        atual = None

    tem_chave = bool(os.environ.get("OPENAI_API_KEY"))
    if not tem_chave:
        st.warning("OPENAI_API_KEY ausente. A interface e os testes funcionam sem IA real; nenhuma chamada foi feita.")

    if st.button("Gerar parecer com IA (pode gerar custo de API)", disabled=not tem_chave, key="ia_gerar"):
        st.session_state.pop("ia_parecer", None)
        st.session_state.pop("ia_aprovacao", None)
        try:
            with st.spinner("Gerando e validando parecer..."):
                parecer = gerar_parecer(dossie)
            st.session_state["ia_parecer"] = {"hash": identificador, "conteudo": parecer}
            st.success("Parecer estruturado validado automaticamente. Pendente de revisão humana.")
        except Exception as erro:
            st.error(f"Parecer não aceito: {type(erro).__name__}. Nenhuma aprovação ocorreu.")
            st.caption("Confirme conectividade, saldo de API e modelo; se persistir, revise o log local.")

    atual = st.session_state.get("ia_parecer")
    if not atual or atual["hash"] != identificador:
        st.info("Ainda não há parecer gerado por IA para este dossiê. As evidências acima não constituem geração por IA.")
        return

    parecer = atual["conteudo"]
    st.markdown("#### Parecer gerado — NÃO APROVADO")
    st.write(f"**{parecer['titulo']}**")
    st.write(parecer["diagnostico"])
    st.write("**Evidências utilizadas:** " + ", ".join(parecer["evidencias_ids"]))
    st.write("**Ações para análise humana**")
    for item in parecer["acoes"]:
        st.write(f"• {item['acao']} (fontes: {', '.join(item['evidencias_ids'])})")
    st.write("**Limitações**")
    for item in parecer["limitacoes"]:
        st.write(f"• {item}")
    st.warning("Verificação automatizada não prova ausência de alucinações semânticas. Analise criticamente o texto.")

    aprovador = st.text_input("Identificação do revisor (sem dados pessoais sensíveis)", key="ia_revisor")
    confirmado = st.checkbox("Conferi fatos, limitações e recomendações; aprovo apenas para demonstração", key="ia_confirma")
    if st.button("Aprovar parecer para exportação", disabled=not (confirmado and aprovador.strip()), key="ia_aprovar"):
        try:
            st.session_state["ia_aprovacao"] = aprovar_parecer(parecer, dossie, aprovador=aprovador)
        except ValueError as erro:
            st.error(str(erro))

    aprovado = st.session_state.get("ia_aprovacao")
    if aprovado and aprovado.get("dossie_sha256") == identificador:
        st.success("Parecer aprovado explicitamente nesta sessão. Não houve envio ou ação financeira.")
        st.download_button(
            "Baixar parecer revisado (JSON)",
            data=json.dumps(aprovado, ensure_ascii=False, indent=2),
            file_name="parecer_financeiro_sintetico_aprovado.json",
            mime="application/json",
            key="ia_download",
        )
