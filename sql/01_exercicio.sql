-- Dia 1 / Exercicio 01 — Indicadores financeiros
-- Consulta desenvolvida pelo aluno e aprovada com nota 9/10.
SELECT
    COUNT (*) AS quantidade_pedidos,
    ROUND(SUM(valor_bruto), 2) AS faturamento_bruto,
    ROUND(SUM(taxa_plataforma), 2) AS taxas_plataforma,
    ROUND(SUM(taxa_logistica), 2) AS taxas_logistica,
    ROUND(SUM(repasse_real), 2) AS repasses_realizados
FROM pedidos
WHERE status = 'concluido';
