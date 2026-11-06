"""Demonstração LOCAL de governança, sem LLM e sem qualquer requisição de API.

Os pareceres abaixo são modelos escritos manualmente, não saídas de IA.
"""

# GUIA PARA INICIANTES — Demonstração sem IA
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.analise_pandas import carregar_pedidos, calcular_indicadores
from scripts.ia_explicavel import (
    aprovar_parecer,
    criar_dossie_credito,
    criar_dossie_repasses,
    hash_dossie,
    validar_parecer,
)
from scripts.simulador_credito import simular_cenario


def montar_demo(tipo: str = "credito") -> tuple[dict, dict]:
    """Entrega evidências reais do Python e parecer EXEMPLO redigido manualmente."""
    if tipo == "credito":
        resultado = simular_cenario(1_000_000, 120_000, 45_000, 1.5, 0.5)
        dossie = criar_dossie_credito(resultado)
        parecer = {
            "titulo": "EXEMPLO MANUAL — revisão da carteira simulada",
            "diagnostico": "O cenário hipotético indica piora das faixas de atraso. A análise é apenas descritiva e depende de revisão humana.",
            "prioridade": dossie["prioridade_calculada"],
            "evidencias_ids": ["C2", "C3", "C4", "C5"],
            "acoes": [{
                "acao": "Conferir premissas da simulação antes de qualquer intervenção.",
                "evidencias_ids": ["C8", "C9"],
            }],
            "limitacoes": ["Os dados são sintéticos e o exercício não demonstra causalidade nem previsão."],
            "revisao_humana_obrigatoria": True,
        }
    elif tipo == "repasses":
        indicadores = calcular_indicadores(carregar_pedidos())
        dossie = criar_dossie_repasses(indicadores)
        parecer = {
            "titulo": "EXEMPLO MANUAL — revisão de repasses sintéticos",
            "diagnostico": "A conciliação identificou divergências de repasse; é necessária verificação humana das ocorrências.",
            "prioridade": dossie["prioridade_calculada"],
            "evidencias_ids": ["R2", "R3", "R4", "R6"],
            "acoes": [{
                "acao": "Conferir registros divergentes e premissas de conciliação antes de tomar decisões.",
                "evidencias_ids": ["R3", "R6"],
            }],
            "limitacoes": ["A base contém apenas pedidos sintéticos e não representa operações reais."],
            "revisao_humana_obrigatoria": True,
        }
    else:
        raise ValueError("Escolha credito ou repasses.")
    validar_parecer(parecer, dossie)
    return dossie, parecer


def main() -> None:
    parser = argparse.ArgumentParser(description="Demonstração offline de revisão humana, SEM IA")
    parser.add_argument("--tipo", choices=["credito", "repasses"], default="credito")
    args = parser.parse_args()

    dossie, parecer = montar_demo(args.tipo)
    print("\n=== DEMONSTRACAO OFFLINE: NAO GERADO POR IA ===")
    print("Tipo:", dossie["tipo"], "| prioridade calculada:", dossie["prioridade_calculada"])
    print("Hash do dossie:", hash_dossie(dossie)[:16], "...")
    print("Evidencias:")
    for item in dossie["evidencias"]:
        print(f"  {item['id']} — {item['rotulo']}: {item['valor']} {item['unidade']}")
    print("\nTitulo:", parecer["titulo"])
    print("Diagnostico:", parecer["diagnostico"])
    print("Acoes:", parecer["acoes"])
    print("Limitacoes:", parecer["limitacoes"])
    print("\nATENCAO: validacao automatizada nao garante veracidade semantica.")
    decisao = input("\nDigite APROVAR para autorizar somente a exportacao do EXEMPLO (Enter cancela): ").strip()
    if decisao != "APROVAR":
        print("SEM APROVACAO. Nenhum arquivo foi exportado.")
        return
    revisor = input("Identificacao do revisor (ex.: Revisor local): ").strip()
    if not revisor:
        print("SEM APROVACAO: revisor nao identificado. Nenhum arquivo foi exportado.")
        return
    pacote = aprovar_parecer(parecer, dossie, aprovador=revisor)
    pacote["origem_parecer"] = "MODELO_MANUAL_DE_TESTE_SEM_IA"
    pasta = Path.home() / "FinancialIntelligenceAI-Offline"
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"parecer_EXEMPLO_{args.tipo}.json"
    destino.write_text(json.dumps(pacote, ensure_ascii=False, indent=2), encoding="utf-8")
    print("EXEMPLO exportado localmente:", destino)
    print("Nenhuma chamada de API, publicacao, operacao financeira ou envio a terceiros foi realizado.")


if __name__ == "__main__":
    main()
