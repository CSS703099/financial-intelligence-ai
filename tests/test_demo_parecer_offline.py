"""Auditoria offline independente da API, sem custos de geração."""
from copy import deepcopy

import pytest

from scripts.demo_parecer_offline import montar_demo
from scripts.ia_explicavel import aprovar_parecer, hash_dossie, validar_parecer
from scripts.simulador_credito import simular_cenario
from scripts.ia_explicavel import criar_dossie_credito


def test_modelo_manual_validado_sem_api(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    dossie, parecer = montar_demo("credito")
    assert dossie["tipo"] == "credito"
    assert parecer["prioridade"] == "Moderado"
    assert validar_parecer(parecer, dossie) == parecer
    assert "EXEMPLO MANUAL" in parecer["titulo"]


def test_cenario_critico_preserva_resultados_financeiros():
    cenario = simular_cenario(1_000_000, 120_000, 45_000, 1.5, 6.5)
    dossie = criar_dossie_credito(cenario)
    por_id = {e["id"]: e["valor"] for e in dossie["evidencias"]}
    assert cenario["nivel_alerta"] == "Crítico"
    assert por_id["C3"] == 13.5
    assert por_id["C5"] == 11.0
    assert por_id["C8"] == 1.5
    assert por_id["C9"] == 6.5


def test_parecer_inventou_id_impede_aprovacao():
    dossie, parecer = montar_demo("credito")
    invalido = deepcopy(parecer)
    invalido["evidencias_ids"] = ["C999"]
    with pytest.raises(ValueError, match="inventada"):
        aprovar_parecer(invalido, dossie, aprovador="Revisor local")


def test_aprovacao_exige_nome_e_vincula_hash():
    dossie, parecer = montar_demo("credito")
    with pytest.raises(ValueError, match="obrigatória"):
        aprovar_parecer(parecer, dossie, aprovador="  ")
    pacote = aprovar_parecer(parecer, dossie, aprovador="Revisor local")
    assert pacote["status"] == "APROVADO_POR_HUMANO"
    assert pacote["dossie_sha256"] == hash_dossie(dossie)
    assert pacote["dossie"] == dossie
    assert pacote["parecer"] == parecer


def test_troca_de_cenario_invalida_hash_anterior():
    original, _ = montar_demo("credito")
    novo = criar_dossie_credito(simular_cenario(1_000_000, 120_000, 45_000, 2.0, 1.0))
    assert hash_dossie(original) != hash_dossie(novo)


def test_lacuna_semantica_taxa_aumentou_mas_texto_diz_caiu():
    dossie, parecer = montar_demo("credito")
    enganoso = deepcopy(parecer)
    enganoso["diagnostico"] = "A inadimplencia caiu no cenario hipotetico."
    with pytest.raises(ValueError):
        validar_parecer(enganoso, dossie)
