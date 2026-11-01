-- Dia 1 / Exercicio 02 — Conciliacao financeira
-- Consulta desenvolvida pelo aluno, corrigida e aprovada com nota 10/10.
-- Diferenca positiva: repasse real menor que o esperado.
SELECT
    pedido_id,
    restaurante,
    valor_bruto,
    ROUND(valor_bruto - taxa_plataforma - taxa_logistica, 2) AS repasse_esperado,
    repasse_real,
    ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) AS divergencia
FROM pedidos
WHERE status = 'concluido'
  AND ROUND(ABS((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real), 2) != 0
ORDER BY pedido_id ASC;
