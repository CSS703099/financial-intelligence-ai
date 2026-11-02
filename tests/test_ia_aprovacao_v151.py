"""Regressões de autorização, sem API externa."""
from copy import deepcopy
from scripts.ia_explicavel import aprovar_parecer, criar_dossie_credito, hash_parecer
from scripts.ia_streamlit import autorizacao_valida
from scripts.simulador_credito import simular_cenario


def _cenario():
    d = criar_dossie_credito(simular_cenario(1_000_000, 120_000, 45_000, 1.5, 0.5))
    p = {
        "titulo": "Parecer de teste", "diagnostico": "Indicadores simulados requerem revisão.",
        "prioridade": d["prioridade_calculada"], "evidencias_ids": ["C3"],
        "acoes": [{"acao": "Revisar premissas.", "evidencias_ids": ["C8"]}],
        "limitacoes": ["Dados hipotéticos, sem inferência causal."],
        "revisao_humana_obrigatoria": True,
    }
    return d, p


def test_aprovacao_exige_confirmacao_e_mesmo_revisor():
    d, p = _cenario()
    a = aprovar_parecer(p, d, aprovador="Revisor")
    assert autorizacao_valida(a, d, p, "Revisor", True)
    assert not autorizacao_valida(a, d, p, "Revisor", False)
    assert not autorizacao_valida(a, d, p, "Outro", True)
    assert not autorizacao_valida(a, d, p, "", True)


def test_aprovacao_invalida_se_parecer_mudar():
    d, p = _cenario()
    a = aprovar_parecer(p, d, aprovador="Revisor")
    alterado = deepcopy(p)
    alterado["diagnostico"] = "Outro texto de diagnóstico."
    assert hash_parecer(alterado) != a["parecer_sha256"]
    assert not autorizacao_valida(a, d, alterado, "Revisor", True)


def test_aprovacao_invalida_se_dossie_mudar():
    d, p = _cenario()
    a = aprovar_parecer(p, d, aprovador="Revisor")
    outro = deepcopy(d)
    outro["evidencias"][0]["valor"] += 1
    assert not autorizacao_valida(a, outro, p, "Revisor", True)
