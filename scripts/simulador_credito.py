"""Simulador determinístico de crédito 30+/90+ com dados 100% hipotéticos.

30+: saldo integral de contratos com atraso de pelo menos 30 dias.
90+: saldo integral de contratos com atraso de pelo menos 90 dias.
O saldo 90+ é subconjunto do saldo 30+. NÃO usa a base de pedidos.
Não é previsão, decisão de crédito ou modelo de IA.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENTAVO = Decimal("0.01")
CEM = Decimal("100")


def _decimal_finito(valor, nome: str) -> Decimal:
    """Converte entradas de widget/usuário sem incorporar ruído binário de float."""
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as erro:
        raise ValueError(f"{nome} deve ser um número válido.") from erro
    if not numero.is_finite():
        raise ValueError(f"{nome} deve ser finito.")
    return numero


def _moeda(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def _avaliar_risco(variacao_30: Decimal, variacao_90: Decimal) -> tuple[str, str, str]:
    """Regras DIDÁTICAS e transparentes, sem ML e sem executar ações."""
    if variacao_90 >= Decimal("2"):
        return (
            "Crítico",
            "A taxa 90+ aumentou pelo menos 2,00 p.p. no cenário hipotético.",
            "Revisar imediatamente as hipóteses e priorizar uma análise humana da carteira 90+.",
        )
    if variacao_30 >= Decimal("2") or variacao_90 >= Decimal("1"):
        return (
            "Alto",
            "A taxa 30+ aumentou pelo menos 2,00 p.p. ou a 90+ pelo menos 1,00 p.p.",
            "Investigar segmentos que mais contribuiriam para a piora e validar possíveis intervenções.",
        )
    if variacao_30 > 0 or variacao_90 > 0:
        return (
            "Moderado",
            "Ao menos um dos indicadores 30+/90+ piorou, mas abaixo dos limiares de alerta alto.",
            "Acompanhar a evolução simulada e revisar premissas antes de qualquer decisão.",
        )
    return (
        "Estável ou melhora",
        "Nenhum dos indicadores 30+/90+ aumentou no cenário hipotético.",
        "Manter o monitoramento; não concluir que houve melhora real a partir de uma simulação.",
    )


def simular_cenario(
    saldo_carteira,
    saldo_30_base,
    saldo_90_base,
    variacao_30_pp=0,
    variacao_90_pp=0,
) -> dict:
    """Calcula cenário 30+/90+ com incrementos em pontos percentuais.

    Valida 0 <= saldo_90 <= saldo_30 <= saldo_carteira tanto no cenário
    inicial como no cenário projetado. Falhas geram ValueError explícito.
    """
    carteira = _moeda(_decimal_finito(saldo_carteira, "Saldo da carteira"))
    saldo30 = _moeda(_decimal_finito(saldo_30_base, "Saldo 30+"))
    saldo90 = _moeda(_decimal_finito(saldo_90_base, "Saldo 90+"))
    delta30 = _decimal_finito(variacao_30_pp, "Variação 30+")
    delta90 = _decimal_finito(variacao_90_pp, "Variação 90+")

    if carteira <= 0:
        raise ValueError("O saldo total da carteira deve ser maior que zero.")
    if not (Decimal(0) <= saldo90 <= saldo30 <= carteira):
        raise ValueError("Regra obrigatória: 0 ≤ saldo 90+ ≤ saldo 30+ ≤ saldo da carteira.")

    taxa30_base = saldo30 / carteira * CEM
    taxa90_base = saldo90 / carteira * CEM
    taxa30_nova = taxa30_base + delta30
    taxa90_nova = taxa90_base + delta90

    if not (Decimal(0) <= taxa90_nova <= taxa30_nova <= CEM):
        raise ValueError("Cenário impossível: as taxas devem obedecer 0% ≤ 90+ ≤ 30+ ≤ 100%.")

    novo30 = _moeda(carteira * taxa30_nova / CEM)
    novo90 = _moeda(carteira * taxa90_nova / CEM)
    nivel, justificativa, acao = _avaliar_risco(delta30, delta90)

    return {
        "saldo_carteira": float(carteira),
        "saldo_30_base": float(saldo30),
        "saldo_90_base": float(saldo90),
        "taxa_30_base_pct": float(_moeda(taxa30_base)),
        "taxa_90_base_pct": float(_moeda(taxa90_base)),
        "saldo_30_cenario": float(novo30),
        "saldo_90_cenario": float(novo90),
        "taxa_30_cenario_pct": float(_moeda(taxa30_nova)),
        "taxa_90_cenario_pct": float(_moeda(taxa90_nova)),
        "variacao_30_pp": float(delta30),
        "variacao_90_pp": float(delta90),
        "delta_saldo_30": float(novo30 - saldo30),
        "delta_saldo_90": float(novo90 - saldo90),
        "nivel_alerta": nivel,
        "justificativa": justificativa,
        "acao_sugerida": acao,
    }
