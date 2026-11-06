"""Python 05: contexto verificável, geração por LLM e revisão humana.

Somente dados sintéticos. Nenhuma ação externa de crédito é implementada.
Os testes podem injetar um cliente falso e nunca acessam uma API real.
"""

# GUIA PARA INICIANTES — Evidências, parecer e revisão
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
from __future__ import annotations

import hashlib
import math
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
    if not math.isfinite(float(valor)):
        raise ValueError("Valor numérico não finito nas evidências.")
    return {"id": codigo, "rotulo": rotulo, "valor": round(float(valor), 2), "unidade": unidade}


def criar_dossie_credito(resultado: dict) -> dict:
    """Recebe somente a saída já validada de simular_cenario()."""
    chaves = ["saldo_carteira", "taxa_30_base_pct", "taxa_30_cenario_pct", "taxa_90_base_pct", "taxa_90_cenario_pct", "delta_saldo_30", "delta_saldo_90", "variacao_30_pp", "variacao_90_pp", "nivel_alerta"]
    if not all(chave in resultado for chave in chaves):
        raise ValueError("Resultado do simulador incompleto.")
    if resultado["nivel_alerta"] not in PRIORIDADES:
        raise ValueError("Prioridade não reconhecida.")
    for chave in ("saldo_carteira", "taxa_30_base_pct", "taxa_30_cenario_pct", "taxa_90_base_pct", "taxa_90_cenario_pct", "delta_saldo_30", "delta_saldo_90", "variacao_30_pp", "variacao_90_pp"):
        _fato("VALID", chave, resultado[chave])
    if resultado["saldo_carteira"] < 0:
        raise ValueError("Saldo de carteira negativo.")
    for sufixo in ("base", "cenario"):
        t30 = resultado[f"taxa_30_{sufixo}_pct"]
        t90 = resultado[f"taxa_90_{sufixo}_pct"]
        if not (0 <= t90 <= t30 <= 100):
            raise ValueError("Taxas de crédito incoerentes.")
    for faixa in (30, 90):
        esperado = resultado[f"taxa_{faixa}_cenario_pct"] - resultado[f"taxa_{faixa}_base_pct"]
        if not math.isclose(resultado[f"variacao_{faixa}_pp"], esperado, abs_tol=0.011):
            raise ValueError("Variação de taxa incoerente.")
        # Os saldos preservam centavos; taxas exibidas podem ter sido arredondadas.
        base = resultado.get(f"saldo_{faixa}_base")
        cenario = resultado.get(f"saldo_{faixa}_cenario")
        if base is not None and cenario is not None:
            _fato("VALID", "saldo base", base)
            _fato("VALID", "saldo cenário", cenario)
            if not (0 <= base <= resultado["saldo_carteira"] and 0 <= cenario <= resultado["saldo_carteira"]):
                raise ValueError("Saldos de crédito incoerentes.")
            if not math.isclose(resultado[f"delta_saldo_{faixa}"], cenario - base, abs_tol=0.011):
                raise ValueError("Variação de saldo incoerente.")
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
    for chave in ("total_pedidos", "pedidos_concluidos", "pedidos_divergentes"):
        valor = indicadores[chave]
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise ValueError("Contagem de repasses inválida.")
    total = indicadores["total_pedidos"]
    concluidos = indicadores["pedidos_concluidos"]
    divergentes = indicadores["pedidos_divergentes"]
    if not (0 < concluidos <= total and divergentes <= concluidos):
        raise ValueError("Contagens de repasses incoerentes.")
    for chave in ("taxa_divergencia_pct", "faturamento_bruto", "divergencia_absoluta", "divergencia_liquida"):
        _fato("VALID", chave, indicadores[chave])
    taxa = indicadores["taxa_divergencia_pct"]
    if not (0 <= taxa <= 100) or not math.isclose(taxa, round(100 * divergentes / concluidos, 2), abs_tol=0.011):
        raise ValueError("Taxa de divergência incoerente.")
    if indicadores["faturamento_bruto"] < 0 or indicadores["divergencia_absoluta"] < 0:
        raise ValueError("Valores financeiros incoerentes.")
    if abs(indicadores["divergencia_liquida"]) > indicadores["divergencia_absoluta"] + 0.011:
        raise ValueError("Divergência líquida superior à absoluta.")
    if divergentes == 0 and (abs(indicadores["divergencia_liquida"]) > 0.011 or indicadores["divergencia_absoluta"] > 0.011):
        raise ValueError("Divergências financeiras sem pedidos divergentes.")
    prioridade = "Revisão necessária" if divergentes else "Sem alerta"
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


def _validar_texto(texto: Any, local: str, ids_validos=None) -> None:
    if not isinstance(texto, str) or not texto.strip() or len(texto) > 1000:
        raise ValueError(f"{local}: texto ausente, inv\u00e1lido ou muito extenso.")

    sem_faixas = re.sub(r"(?<!\w)(30|90)\+(?!\w)", "FAIXA", texto)

    def substituir_id(match):
        identificador = match.group(0)

        if ids_validos is not None and identificador in ids_validos:
            return "EVIDENCIA"

        raise ValueError(
            f"{local}: refer\u00eancia inventada ou n\u00e3o autorizada."
        )

    sem_ids = re.sub(
        r"(?<!\w)[CR]\d+(?!\w)",
        substituir_id,
        sem_faixas
    )

    if re.search(r"\d", sem_ids):
        raise ValueError(
            f"{local}: afirma\u00e7\u00e3o num\u00e9rica livre bloqueada; cite o ID da evid\u00eancia."
        )

    if re.search(
        r"\b(fraude\s+(confirmada|comprovada)|perda\s+comprovada|lucro\s+garantido|bloqueio\s+autom[a\u00e1]tico)\b",
        texto,
        flags=re.I
    ):
        raise ValueError(
            f"{local}: alega\u00e7\u00e3o n\u00e3o comprovada ou a\u00e7\u00e3o autom\u00e1tica bloqueada."
        )



def _validar_direcao_credito(parecer: dict, dossie: dict) -> None:
    """Bloqueia afirmacoes direcionais explicitas em conflito com as taxas 30+/90+.

    Controle conservador: nao interpreta negacao, ironia ou todas as formas
    de linguagem natural. Casos ambiguos devem passar por revisao humana.
    """
    if dossie.get("tipo") != "credito":
        return
    fatos = {item["id"]: item["valor"] for item in dossie["evidencias"]}
    mudancas = (fatos["C8"], fatos["C9"])
    # Nao inferir uma direcao agregada se as faixas divergirem.
    if all(v > 0.011 for v in mudancas):
        direcao = "aumento"
    elif all(v < -0.011 for v in mudancas):
        direcao = "queda"
    else:
        return
    diagnostico = parecer["diagnostico"].casefold()
    import unicodedata
    texto = "".join(c for c in unicodedata.normalize("NFD", diagnostico)
                    if unicodedata.category(c) != "Mn")
    # Checar somente declaracoes diretas sobre inadimplencia, sem negacao.
    padrao = re.compile(
        r"\b(?:inadimplencia|taxas? de atraso)\b"
        r"[^.!?;]{0,65}?"
        r"\b(caiu|cairam|diminuiu|diminuiram|reduziu|reduziram|"
        r"aumentou|aumentaram|subiu|subiram|cresceu|cresceram)\b"
    )
    for trecho in re.split(r"[.!?;]", texto):
        match = padrao.search(trecho)
        if not match:
            continue
        verbo = match.group(1)
        prefixo = trecho[:match.start(1)]
        if re.search(r"\b(?:nao|nunca|jamais)\s+$", prefixo):
            continue
        queda = verbo in {"caiu", "cairam", "diminuiu", "diminuiram", "reduziu", "reduziram"}
        if (direcao == "aumento" and queda) or (direcao == "queda" and not queda):
            raise ValueError("Diagnostico contradiz a direcao das taxas de inadimplencia.")


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
        _validar_texto(parecer[k], k, ids_validos)
    _validar_direcao_credito(parecer, dossie)
    refs_validas(parecer["evidencias_ids"], "Parecer")
    for k in ("acoes", "limitacoes"):
        if not isinstance(parecer[k], list) or not 1 <= len(parecer[k]) <= 4:
            raise ValueError(f"{k}: quantidade inválida.")
    for i, acao in enumerate(parecer["acoes"]):
        if not isinstance(acao, dict) or set(acao) != CHAVES_ACAO:
            raise ValueError("Estrutura da ação incorreta.")
        _validar_texto(acao["acao"], f"Ação {i}", ids_validos)
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



SCHEMA_GEMINI = {
    **SCHEMA,
    "properties": {
        chave: valor for chave, valor in SCHEMA["properties"].items()
        if chave != "limitacoes"
    },
    "required": [chave for chave in SCHEMA["required"] if chave != "limitacoes"],
}

# O campo limitacoes pertence ao Python, nao ao modelo.
INSTRUCOES_GEMINI = (
    "Voce e um assistente de analise financeira com dados exclusivamente sinteticos. "
    "Responda em portugues, somente com o objeto JSON do esquema fornecido. "
    "Copie exatamente prioridade_calculada, sem alterar o valor. "
    "Use somente IDs de evidencias existentes no dossie para referenciar dados. "
    "Nao inclua numeros em texto livre, exceto os nomes das faixas 30+ e 90+ e IDs. "
    "Nao inclua a chave limitacoes: o Python a acrescenta apos validar a estrutura. "
    "Nao afirme fraude, perda comprovada, causalidade, migracao individual de ativos, "
    "segmentos afetados nem comportamento futuro a partir de indicadores agregados. "
    "Recomende apenas verificacoes sujeitas a revisao humana, sem executar acoes. "
    "Defina revisao_humana_obrigatoria como true."
)

LIMITACOES_PADRAO = (
    "Os dados sao sinteticos e nao representam operacoes financeiras reais.",
    "Os indicadores agregados nao demonstram causas ou resultados futuros.",
    "As conclusoes dependem de verificacao e revisao humana."
)


def padronizar_limitacoes(parecer: dict) -> dict:
    if not isinstance(parecer, dict):
        raise ValueError("Parecer deve ser um objeto JSON.")

    if "limitacoes" in parecer:
        raise ValueError("Campo limitacoes enviado pelo modelo; resposta rejeitada.")
    if set(parecer) != set(SCHEMA_GEMINI["properties"]):
        raise ValueError("Campos ausentes ou inesperados no parecer do modelo.")

    return {
        **parecer,
        "limitacoes": list(LIMITACOES_PADRAO)
    }


def gerar_parecer(dossie: dict, *, cliente=None, modelo: str | None = None) -> dict:
    """Gera parecer via Gemini; cliente injetado permite testes sem API."""
    if dossie.get("tipo") not in TIPOS:
        raise ValueError("Tipo de dossiê inválido.")
    if not dossie.get("evidencias"):
        raise ValueError("Dossiê sem evidências.")
    if cliente is None:
        chave = os.environ.get("GEMINI_API_KEY")
        if not chave:
            raise RuntimeError("GEMINI_API_KEY não configurada; nenhum modelo foi chamado.")
        from google import genai
        cliente = genai.Client(api_key=chave, http_options={"timeout": 25000})
        fechar_cliente = True
    else:
        fechar_cliente = False
    try:
        from google.genai import types
        resposta = cliente.models.generate_content(
            model=modelo or os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
            contents=json.dumps(dossie, ensure_ascii=False, sort_keys=True),
            config=types.GenerateContentConfig(
                system_instruction=INSTRUCOES_GEMINI,
                response_mime_type="application/json",
                response_json_schema=SCHEMA_GEMINI,
                max_output_tokens=1800,
                temperature=0.2,
            ),
        )
        conteudo = getattr(resposta, "text", None)
        if not conteudo:
            raise ValueError("Modelo não forneceu JSON validável.")
        try:
            parecer = json.loads(conteudo)
        except json.JSONDecodeError as erro:
            raise ValueError("Resposta da IA não é um JSON válido.") from erro
        parecer = padronizar_limitacoes(parecer)
        return validar_parecer(parecer, dossie)
    finally:
        if fechar_cliente:
            cliente.close()


def hash_parecer(parecer: dict) -> str:
    """Identificador de conteúdo, NÃO assinatura digital autenticada."""
    return hashlib.sha256(json.dumps(parecer, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def aprovar_parecer(parecer: dict, dossie: dict, *, aprovador: str) -> dict:
    """Gera um pacote exportável SOMENTE após aprovação humana explícita."""
    validar_parecer(parecer, dossie)
    if not isinstance(aprovador, str) or not aprovador.strip():
        raise ValueError("Aprovação humana identificada é obrigatória.")
    return {
        "status": "APROVADO_POR_HUMANO",
        "aprovador": aprovador.strip(),
        "dossie_sha256": hash_dossie(dossie),
        "parecer_sha256": hash_parecer(parecer),
        "dossie": dossie,
        "parecer": parecer,
        "aviso": "Parecer descritivo de dados sintéticos; não autoriza decisão financeira.",
    }
