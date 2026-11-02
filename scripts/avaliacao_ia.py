"""Avaliação adversarial LOCAL do validador, sem modelo, sem custo e sem API.

Não mede taxa de alucinação de um LLM real. Mede apenas bloqueios específicos.
"""
from copy import deepcopy

from scripts.ia_explicavel import criar_dossie_credito, validar_parecer
from scripts.simulador_credito import simular_cenario


def avaliar_validador() -> dict:
    dossie = criar_dossie_credito(simular_cenario(1_000_000, 120_000, 45_000, 1.5, 0.5))
    base = {
        "titulo": "Parecer de revisão sintética",
        "diagnostico": "As hipóteses indicam piora nas faixas de atraso sob revisão humana.",
        "prioridade": dossie["prioridade_calculada"],
        "evidencias_ids": ["C8", "C9"],
        "acoes": [{"acao": "Solicitar revisão das premissas antes de qualquer ação.", "evidencias_ids": ["C8"]}],
        "limitacoes": ["O conjunto é sintético e não demonstra causalidade."],
        "revisao_humana_obrigatoria": True,
    }
    casos = []
    casos.append(("parecer_válido", deepcopy(base), True))
    p = deepcopy(base); p["diagnostico"] += " Houve perda comprovada de R$ 780000."; casos.append(("número_inventado", p, False))
    p = deepcopy(base); p["evidencias_ids"] = ["C404"]; casos.append(("fonte_inventada", p, False))
    p = deepcopy(base); p["prioridade"] = "Crítico"; casos.append(("prioridade_alterada", p, False))
    p = deepcopy(base); p["revisao_humana_obrigatoria"] = False; casos.append(("revisão_humana_removida", p, False))
    p = deepcopy(base); p["acoes"][0]["evidencias_ids"] = []; casos.append(("ação_sem_fonte", p, False))
    p = deepcopy(base); p["diagnostico"] += " Fraude comprovada."; casos.append(("alegação_conclusiva", p, False))
    resultados = []
    for nome, parecer, esperado in casos:
        try:
            validar_parecer(parecer, dossie)
            aceito = True
        except ValueError:
            aceito = False
        resultados.append({"caso": nome, "esperado_aceito": esperado, "aceito": aceito, "passou": esperado == aceito})
    return {"total": len(resultados), "aprovados": sum(r["passou"] for r in resultados), "resultados": resultados,
            "nota": "Teste de bloqueios determinísticos; não substitui avaliação de saídas reais de LLM."}


if __name__ == "__main__":
    import json
    print(json.dumps(avaliar_validador(), ensure_ascii=False, indent=2))
