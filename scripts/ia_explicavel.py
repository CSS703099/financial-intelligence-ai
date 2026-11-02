"""Python 05: contexto verificável, geração por LLM e revisão humana.

Somente dados sintéticos. Nenhuma ação externa de crédito é implementada.
Os testes podem injetar um cliente falso e nunca acessam uma API real.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any


TIPOS = {"credito", "repasses"}
PRIORIDADES = {"Crítico", "Alto", "Moderado", "Estável ou melhora", "Revisão necessária", "Sem alerta"}
CHAVES_PARECER = {"titulo", "diagnostico", "prioridade", "evidencias_ids", "acoes", "limitacoes", "revisao_humana_obrigatoria"}
CHAVES_ACAO = {"acao", "evidencias_ids"}

# Deliberadamente sem números livres: valores só aparecem em evidências
# calculadas pelo Python. Isso reduz uma classe de alucinações numéricas.
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "titulo": {"type": "string"},
        "diagnostico": {"type": "string"},
        "prioridade": {"type": "string", "enum": sorted(PRIORIDADES)},
        "evidencias_ids": {"type": "array", "items": {"type": "string"}},
        "acoes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"acao": {"type": "string"}, "evidencias_ids": {"type": "array", "items": {"type": "string"}}},
                "required": ["acao", "evidencias_ids"],
            },
        },
        "limitacoes": {"type": "array", "items": {"type": "string"}},
        "revisao_humana_obrigatoria": {"type": "boolean"},
    },
    "required": ["titulo", "diagnostico", "prioridade", "evidencias_ids", "acoes", "limitacoes", "revisao_humana_obrigatoria"],
}


def _fato(codigo: str, rotulo: str, valor: Any, unidade: str = "") -> dict:
    if not isinstance(valor, (float, int)) or isinstance(valor, bool):
        raise ValueError("Valor numérico inválido nas evidências.")
    return {"id": codigo, "rotulo": rotulo, "valor": round(float(valor), 2), "unidade": unidade}


def criar_dossie_credito(resultado: dict) -> dict:
    """Recebe somente a saída já validada de simular_cenario()."""
    chaves = ["saldo_carteira", "taxa_30_base_pct", "taxa_30_cenario_pct", "taxa_90_base_pct", "taxa_90_cenario_pct", "delta_saldo_30", "delta_saldo_90", "variacao_30_pp", "variacao_90_pp", "nivel_alerta"]
    if not all(chave in resultado for chave in chaves):
        raise ValueError("Resultado do simulador incompleto.")
    if resultado["nivel_alerta"] not in PRIORIDADES:
        raise ValueError("Prioridade não reconhecida.")
    return {
        "tipo": "credito",
        "prioridade_calculada": resultado["nivel_alerta"],
        "origem": "simulacao_hipotetica",
        "evidencias": [
            _fato("C1", "Saldo total da carteira", resultado["saldo_carteira"], "BRL"),
            _fato("C2", "Taxa 30+ inicial", resultado["taxa_30_base_pct"], "%"),
            _fato("C3", "Taxa 30+ simulada", resultado["taxa_30_cenario_pct"], "%"),
            _fato("C4", "Taxa 90+ inicial", resultado["taxa_90_base_pct"], "%"),
            _fato("C5", "Taxa 90+ simulada", resultado["taxa_90_cenario_pct"], "%"),
            _fato("C6", "Variação do saldo 30+", resultado["delta_saldo_30"], "BRL"),
            _fato("C7", "Variação do saldo 90+", resultado["delta_saldo_90"], "BRL"),
            _fato("C8", "Variação da taxa 30+", resultado["variacao_30_pp"], "p.p."),
            _fato("C9", "Variação da taxa 90+", resultado["variacao_90_pp"], "p.p."),
        ],
    }


def criar_dossie_repasses(indicadores: dict) -> dict:
    """Recebe métricas já calculadas por calcular_indicadores()."""
    chaves = ["total_pedidos", "pedidos_concluidos", "pedidos_divergentes", "taxa_divergencia_pct", "faturamento_bruto", "divergencia_absoluta", "divergencia_liquida"]
    if not all(chave in indicadores for chave in chaves):
        raise ValueError("Indicadores de repasses incompletos.")
    if indicadores["taxa_divergencia_pct"] is None:
        raise ValueError("Não é possível produzir parecer sem pedidos concluídos.")
    prioridade = "Revisão necessária" if indicadores["pedidos_divergentes"] else "Sem alerta"
    return {
        "tipo": "repasses",
        "prioridade_calculada": prioridade,
        "origem": "pedidos_sinteticos_concluidos",
        "evidencias": [
            _fato("R1", "Pedidos totais", indicadores["total_pedidos"]),
            _fato("R2", "Pedidos concluídos", indicadores["pedidos_concluidos"]),
            _fato("R3", "Pedidos com diferenças de repasse", indicadores["pedidos_divergentes"]),
            _fato("R4", "Taxa de divergência", indicadores["taxa_divergencia_pct"], "%"),
            _fato("R5", "Valor bruto", indicadores["faturamento_bruto"], "BRL"),
            _fato("R6", "Diferença absoluta de repasses", indicadores["divergencia_absoluta"], "BRL"),
            _fato("R7", "Diferença líquida de repasses", indicadores["divergencia_liquida"], "BRL"),
        ],
    }


def hash_dossie(dossie: dict) -> str:
    return hashlib.sha256(json.dumps(dossie, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _validar_texto(texto: Any, local: str) -> None:
    if not isinstance(texto, str) or not texto.strip() or len(texto) > 1000:
        raise ValueError(f"{local}: texto ausente, inválido ou muito extenso.")
    # Permitir apenas os rótulos de faixas 30+/90+. Outros números, moedas,
    # percentuais e contagens devem aparecer no painel determinístico de evidências.
    sem_faixas = re.sub(r"(?<!\d)(30|90)\+", "FAIXA", texto)
    if re.search(r"\d", sem_faixas):
        raise ValueError(f"{local}: afirmação numérica livre bloqueada; cite o ID da evidência.")
    if re.search(r"\b(fraude\s+(confirmada|comprovada)|perda\s+comprovada|lucro\s+garantido|bloqueio\s+autom[aá]tico)\b", texto, flags=re.I):
        raise ValueError(f"{local}: alegação não comprovada ou ação automática bloqueada.")


def validar_parecer(parecer: dict, dossie: dict) -> dict:
    """Valida conteúdo além do esquema JSON (sem garantia semântica completa)."""
    if not isinstance(parecer, dict) or set(parecer) != CHAVES_PARECER:
        raise ValueError("Esquema do parecer incorreto.")
    if parecer["revisao_humana_obrigatoria"] is not True:
        raise ValueError("O parecer exige revisão humana obrigatória.")
    if parecer["prioridade"] != dossie["prioridade_calculada"]:
        raise ValueError("Prioridade da IA difere da prioridade calculada.")
    ids_validos = {f["id"] for f in dossie["evidencias"]}

    def refs_validas(refs, local):
        if not isinstance(refs, list) or not refs or any(not isinstance(i, str) or i not in ids_validos for i in refs):
            raise ValueError(f"{local}: referência ausente ou inventada.")

    for k in ("titulo", "diagnostico"):
        _validar_texto(parecer[k], k)
    refs_validas(parecer["evidencias_ids"], "Parecer")
    for k in ("acoes", "limitacoes"):
        if not isinstance(parecer[k], list) or not 1 <= len(parecer[k]) <= 4:
            raise ValueError(f"{k}: quantidade inválida.")
    for i, acao in enumerate(parecer["acoes"]):
        if not isinstance(acao, dict) or set(acao) != CHAVES_ACAO:
            raise ValueError("Estrutura da ação incorreta.")
        _validar_texto(acao["acao"], f"Ação {i}")
        refs_validas(acao["evidencias_ids"], f"Ação {i}")
    for i, item in enumerate(parecer["limitacoes"]):
        _validar_texto(item, f"Limitação {i}")
    return parecer


INSTRUCOES = (
    "Você é um assistente de análise financeira de DADOS SINTÉTICOS. "
    "Produza um parecer em português, exclusivamente a partir das evidências fornecidas. "
    "Não recalcule nem adicione números no texto livre (exceto as faixas 30+ e 90+); "
    "use sempre IDs existentes para referenciar números exibidos separadamente pelo aplicativo. "
    "Copie exatamente a prioridade_calculada, não a altere. "
    "Não alegue fraude, causalidade, previsão, perda comprovada ou operação real. "
    "Não tome ações. Recomende apenas investigações sujeitas a revisão humana. "
    "Inclua limitações dos dados sintéticos e da ausência de evidência causal. "
    "Marque revisao_humana_obrigatoria como true."
)


def gerar_parecer(dossie: dict, *, cliente=None, modelo: str | None = None) -> dict:
    """Chama um LLM de verdade somente quando solicitado; permite cliente mock nos testes."""
    if dossie.get("tipo") not in TIPOS:
        raise ValueError("Tipo de dossiê inválido.")
    if not dossie.get("evidencias"):
        raise ValueError("Dossiê sem evidências.")
    if cliente is None:
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY não configurada; nenhum modelo foi chamado.")
        from openai import OpenAI
        cliente = OpenAI(timeout=25.0, max_retries=0)
    resposta = cliente.responses.create(
        model=modelo or os.environ.get("OPENAI_MODEL", "gpt-5-mini"),
        instructions=INSTRUCOES,
        input=json.dumps(dossie, ensure_ascii=False, sort_keys=True),
        text={"format": {"type": "json_schema", "name": "parecer_financeiro", "strict": True, "schema": SCHEMA}},
        store=False,
        max_output_tokens=1800,
    )
    if getattr(resposta, "status", "completed") != "completed":
        raise ValueError("Resposta incompleta do modelo; descarte e tente novamente.")
    conteudo = getattr(resposta, "output_text", None)
    if not conteudo:
        raise ValueError("Modelo recusou ou não forneceu JSON validável.")
    try:
        parecer = json.loads(conteudo)
    except json.JSONDecodeError as erro:
        raise ValueError("Resposta da IA não é um JSON válido.") from erro
    return validar_parecer(parecer, dossie)


def aprovar_parecer(parecer: dict, dossie: dict, *, aprovador: str) -> dict:
    """Gera um pacote exportável SOMENTE após aprovação humana explícita."""
    validar_parecer(parecer, dossie)
    if not isinstance(aprovador, str) or not aprovador.strip():
        raise ValueError("Aprovação humana identificada é obrigatória.")
    return {
        "status": "APROVADO_POR_HUMANO",
        "aprovador": aprovador.strip(),
        "dossie_sha256": hash_dossie(dossie),
        "dossie": dossie,
        "parecer": parecer,
        "aviso": "Parecer descritivo de dados sintéticos; não autoriza decisão financeira.",
    }
