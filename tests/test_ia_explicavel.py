"""Testes locais: não chamam API nem geram custos."""

# GUIA PARA INICIANTES — Testes de evidências, formato e validação de pareceres
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
import json
from types import SimpleNamespace

import pytest

from scripts.simulador_credito import simular_cenario
from scripts.ia_explicavel import (
    SCHEMA,
    aprovar_parecer, criar_dossie_credito, criar_dossie_repasses,
    gerar_parecer, hash_dossie, validar_parecer,
)


@pytest.fixture
def dossie():
    return criar_dossie_credito(simular_cenario(1_000_000, 120_000, 45_000, 1.5, 0.5))


@pytest.fixture
def parecer(dossie):
    return {
        "titulo": "Parecer didático de sensibilidade",
        "diagnostico": "A carteira simulada indica piora dos indicadores de atraso, segundo os parâmetros informados.",
        "prioridade": dossie["prioridade_calculada"],
        "evidencias_ids": ["C3", "C5"],
        "acoes": [{"acao": "Solicitar a um analista revisão das premissas e dos segmentos antes de decidir.", "evidencias_ids": ["C8", "C9"]}],
        "limitacoes": ["O cenário é hipotético e não demonstra causa ou comportamento futuro."],
        "revisao_humana_obrigatoria": True,
    }


def test_parecer_aprovavel_quando_validado(dossie, parecer):
    assert validar_parecer(parecer, dossie) == parecer


def test_id_de_evidencia_inventado_rejeitado(dossie, parecer):
    parecer["evidencias_ids"] = ["C99"]
    with pytest.raises(ValueError, match="inventada"):
        validar_parecer(parecer, dossie)


def test_numero_inventado_no_diagnostico_rejeitado(dossie, parecer):
    parecer["diagnostico"] += " A carteira perdeu R$ 900000."
    with pytest.raises(ValueError, match="numérica"):
        validar_parecer(parecer, dossie)


def test_prioridade_divergente_rejeitada(dossie, parecer):
    parecer["prioridade"] = "Crítico"
    with pytest.raises(ValueError, match="Prioridade"):
        validar_parecer(parecer, dossie)


def test_sem_aprovacao_humana_rejeitado(dossie, parecer):
    parecer["revisao_humana_obrigatoria"] = False
    with pytest.raises(ValueError, match="revisão humana"):
        validar_parecer(parecer, dossie)


def test_acao_sem_evidencia_rejeitada(dossie, parecer):
    parecer["acoes"][0]["evidencias_ids"] = []
    with pytest.raises(ValueError, match="referência"):
        validar_parecer(parecer, dossie)


def test_alegacao_fraude_comprovada_rejeitada(dossie, parecer):
    parecer["diagnostico"] += " Fraude comprovada."
    with pytest.raises(ValueError, match="alegação"):
        validar_parecer(parecer, dossie)


def test_aprovar_requer_identificador_revisor(dossie, parecer):
    with pytest.raises(ValueError, match="Aprovação"):
        aprovar_parecer(parecer, dossie, aprovador=" ")


def test_aprovacao_exportavel_tem_hash(dossie, parecer):
    saida = aprovar_parecer(parecer, dossie, aprovador="Revisor de teste")
    assert saida["status"] == "APROVADO_POR_HUMANO"
    assert saida["dossie_sha256"] == hash_dossie(dossie)


def test_hash_muda_com_cenario(dossie):
    outro = criar_dossie_credito(simular_cenario(1_000_000, 120_000, 45_000, 2.5, 0.5))
    assert hash_dossie(dossie) != hash_dossie(outro)


def test_cliente_falso_reproduz_chamada_e_esquema(dossie, parecer):
    class ClienteFalso:
        def __init__(self):
            self.kwargs = None
            self.models = self
        def generate_content(self, **kwargs):
            self.kwargs = kwargs
            return SimpleNamespace(text=json.dumps({k: v for k, v in parecer.items() if k != "limitacoes"}))
    cliente = ClienteFalso()
    resultado = gerar_parecer(dossie, cliente=cliente, modelo="modelo-ficticio")
    from scripts.ia_explicavel import LIMITACOES_PADRAO
    assert resultado == {**parecer, "limitacoes": list(LIMITACOES_PADRAO)}
    assert resultado["limitacoes"] is not parecer["limitacoes"]
    assert cliente.kwargs["model"] == "modelo-ficticio"
    assert cliente.kwargs["config"].response_mime_type == "application/json"
    from scripts.ia_explicavel import SCHEMA_GEMINI
    assert cliente.kwargs["config"].response_json_schema == SCHEMA_GEMINI


def test_json_invalido_rejeitado(dossie):
    cliente = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **_: SimpleNamespace(text="não é json")))
    with pytest.raises(ValueError, match="JSON"):
        gerar_parecer(dossie, cliente=cliente)


def test_sem_chave_nao_chama_api(dossie, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        gerar_parecer(dossie)


def test_resposta_vazia_rejeitada(dossie):
    cliente = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **_: SimpleNamespace(text=None)))
    with pytest.raises(ValueError, match="JSON"):
        gerar_parecer(dossie, cliente=cliente)


def test_falha_api_nao_gera_aprovacao(dossie):
    def falhar(**kwargs):
        raise RuntimeError("API temporariamente indisponível")
    cliente = SimpleNamespace(models=SimpleNamespace(generate_content=falhar))
    with pytest.raises(RuntimeError, match="indisponível"):
        gerar_parecer(dossie, cliente=cliente)


def test_repasses_dados_sinteticos():
    dossie = criar_dossie_repasses({
        "total_pedidos": 36, "pedidos_concluidos": 30,
        "pedidos_divergentes": 7, "taxa_divergencia_pct": 23.33,
        "faturamento_bruto": 4687.6, "divergencia_absoluta": 38.1,
        "divergencia_liquida": 22.1,
    })
    assert dossie["tipo"] == "repasses"
    assert dossie["prioridade_calculada"] == "Revisão necessária"
    assert len(dossie["evidencias"]) == 7


def test_nao_descarta_limitacoes_invalidas_do_modelo(dossie, parecer):
    """Qualquer limitacao produzida pelo modelo e rejeitada, nunca encoberta."""
    suspeito = {**parecer, "limitacoes": ["Fraude comprovada."]}
    cliente = SimpleNamespace(models=SimpleNamespace(
        generate_content=lambda **_: SimpleNamespace(text=json.dumps(suspeito))
    ))
    with pytest.raises(ValueError, match="limitacoes"):
        gerar_parecer(dossie, cliente=cliente)


def test_modelo_nao_pode_inventar_campos_extras(dossie, parecer):
    resposta = {k: v for k, v in parecer.items() if k != "limitacoes"}
    resposta["campo_inventado"] = "informacao adicional"
    cliente = SimpleNamespace(models=SimpleNamespace(
        generate_content=lambda **_: SimpleNamespace(text=json.dumps(resposta))
    ))
    with pytest.raises(ValueError, match="Campos ausentes ou inesperados"):
        gerar_parecer(dossie, cliente=cliente)


def test_bloqueio_automatico_com_ambas_grafias_rejeitado():
    from scripts.ia_explicavel import _validar_texto
    for texto in ("bloqueio automatico", "bloqueio autom\u00e1tico"):
        with pytest.raises(ValueError, match="alega"):
            _validar_texto(texto, "diagnostico", set())


def test_acao_texto_aceita_ids_validos(dossie, parecer):
    parecer["acoes"][0]["acao"] = "Verificar as variacoes C8 e C9."
    assert validar_parecer(parecer, dossie) == parecer


def test_acao_texto_rejeita_id_inventado(dossie, parecer):
    parecer["acoes"][0]["acao"] = "Investigar a evidencia C999."
    with pytest.raises(ValueError, match="inventada"):
        validar_parecer(parecer, dossie)


def test_acao_texto_rejeita_valor_numerico_livre(dossie, parecer):
    parecer["acoes"][0]["acao"] = "Investigar R$ 900000 conforme C8."
    with pytest.raises(ValueError, match="numérica"):
        validar_parecer(parecer, dossie)
