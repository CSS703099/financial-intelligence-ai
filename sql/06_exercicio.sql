WITH base_pedidos AS (
    -- Etapa 1: Filtrar pedidos concluídos e calcular as divergências
    SELECT 
        pedido_id,
        restaurante,
        SUBSTR(data_pedido, 1, 7) AS mes,
        ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) AS divergencia,
        ROUND(ABS((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real), 2) AS divergencia_absoluta
    FROM pedidos
    WHERE status = 'concluido'
),
pedidos_divergentes AS (
    -- Etapa 2: Manter apenas os pedidos que possuem divergência diferente de zero
    SELECT 
        pedido_id,
        restaurante,
        mes,
        divergencia,
        divergencia_absoluta
    FROM base_pedidos
    WHERE divergencia != 0
),
ranking_e_totais AS (
    -- Etapa 3: Aplicar ROW_NUMBER() e calcular totais gerais usando funções de janela
    SELECT 
        pedido_id,
        restaurante,
        mes,
        divergencia,
        divergencia_absoluta,
        ROW_NUMBER() OVER (
            ORDER BY divergencia_absoluta DESC, pedido_id ASC
        ) AS posicao_ranking,
        ROUND(
            (divergencia_absoluta * 100.0) / SUM(divergencia_absoluta) OVER (), 
            2
        ) AS participacao_pct,
        ROUND(
            (SUM(divergencia_absoluta) OVER (
                ORDER BY divergencia_absoluta DESC, pedido_id ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) * 100.0) / SUM(divergencia_absoluta) OVER (), 
            2
        ) AS acumulado_pct
    FROM pedidos_divergentes
)
-- Etapa 4: Selecionar e ordenar o resultado final
SELECT 
    pedido_id,
    restaurante,
    mes,
    divergencia,
    divergencia_absoluta,
    posicao_ranking,
    participacao_pct,
    acumulado_pct
FROM ranking_e_totais
ORDER BY posicao_ranking ASC;