
# GUIA PARA INICIANTES — Testes de contradições semânticas específicas
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
from copy import deepcopy
import pytest
from scripts.demo_parecer_offline import montar_demo
from scripts.ia_explicavel import validar_parecer, criar_dossie_credito
from scripts.simulador_credito import simular_cenario

@pytest.mark.parametrize("frase", [
    "A inadimplência caiu no cenário.",
    "A inadimplencia diminuiu após o choque.",
    "A taxa de atraso reduziu na simulação.",
])
def test_queda_falsa_rejeitada(frase):
    dossie, parecer = montar_demo("credito")
    parecer = deepcopy(parecer)
    parecer["diagnostico"] = frase
    with pytest.raises(ValueError, match="contradiz"):
        validar_parecer(parecer, dossie)

def test_negacao_nao_e_tratada_como_queda():
    dossie, parecer = montar_demo("credito")
    parecer = deepcopy(parecer)
    parecer["diagnostico"] = "A inadimplência não caiu no cenário."
    assert validar_parecer(parecer, dossie) == parecer

def test_movimentos_opostos_nao_inferem_direcao_agregada():
    dossie = criar_dossie_credito(simular_cenario(1_000_000, 120_000, 45_000, 1.0, -0.5))
    _, parecer = montar_demo("credito")
    parecer = deepcopy(parecer)
    parecer["prioridade"] = dossie["prioridade_calculada"]
    parecer["diagnostico"] = "A inadimplência caiu no cenário."
    assert validar_parecer(parecer, dossie) == parecer
