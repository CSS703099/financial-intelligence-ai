"""Testes locais: não chamam API nem geram custos."""

# GUIA PARA INICIANTES — Testes de evidências, formato e validação de pareceres
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
import json
from types import SimpleNamespace

import pytest

from scripts.simulador_credito import simular_cenario
from scripts.ia_explicavel import (
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
            self.responses = self
        def create(self, **kwargs):
            self.kwargs = kwargs
            return SimpleNamespace(status="completed", output_text=json.dumps(parecer))
    cliente = ClienteFalso()
    resultado = gerar_parecer(dossie, cliente=cliente, modelo="modelo-ficticio")
    assert resultado == parecer
    assert cliente.kwargs["text"]["format"]["strict"] is True
    assert cliente.kwargs["store"] is False
    assert cliente.kwargs["model"] == "modelo-ficticio"


def test_json_invalido_rejeitado(dossie):
    cliente = SimpleNamespace(responses=SimpleNamespace(create=lambda **_: SimpleNamespace(status="completed", output_text="não é json")))
    with pytest.raises(ValueError, match="JSON"):
        gerar_parecer(dossie, cliente=cliente)


def test_sem_chave_nao_chama_api(dossie, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        gerar_parecer(dossie)


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
