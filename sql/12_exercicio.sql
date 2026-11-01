WITH base_calculada AS (
    -- Etapa 1: Filtrar pedidos concluídos no período e calcular divergências por pedido
    SELECT 
        pedido_id,
        SUBSTR(data_pedido, 1, 7) AS mes,
        restaurante,
        ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) AS divergencia,
        ROUND(ABS((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real), 2) AS divergencia_absoluta
    FROM pedidos
    WHERE status = 'concluido'
      AND data_pedido >= '2026-09-01' AND data_pedido < '2026-11-01'
),
agregado_mensal AS (
    -- Etapa 2: Agrupar por mês e restaurante, calculando métricas e contagens
    SELECT 
        mes,
        restaurante,
        COUNT(*) AS pedidos_concluidos,
        SUM(CASE WHEN divergencia != 0 THEN 1 ELSE 0 END) AS pedidos_divergentes,
        ROUND(SUM(divergencia), 2) AS divergencia_liquida,
        ROUND(SUM(divergencia_absoluta), 2) AS divergencia_absoluta
    FROM base_calculada
    GROUP BY mes, restaurante
),
com_totais_e_ranking AS (
    -- Etapa 3: Calcular participações percentuais e aplicar o ranking com ROW_NUMBER()
    SELECT 
        mes,
        restaurante,
        pedidos_concluidos,
        pedidos_divergentes,
        COALESCE(
            ROUND((pedidos_divergentes * 100.0) / NULLIF(pedidos_concluidos, 0), 2),
            0
        ) AS taxa_divergencia_pct,
        divergencia_liquida,
        divergencia_absoluta,
        ROUND(
            (divergencia_absoluta * 100.0) / NULLIF(SUM(divergencia_absoluta) OVER (), 0),
            2
        ) AS participacao_impacto_pct,
        ROW_NUMBER() OVER (
            ORDER BY divergencia_absoluta DESC, mes ASC, restaurante ASC
        ) AS posicao_impacto
    FROM agregado_mensal
),
com_prioridades AS (
    -- Etapa 4: Aplicar regras de prioridade e ações sugeridas
    SELECT 
        posicao_impacto,
        mes,
        restaurante,
        pedidos_concluidos,
        pedidos_divergentes,
        taxa_divergencia_pct,
        divergencia_liquida,
        divergencia_absoluta,
        participacao_impacto_pct,
        CASE 
            WHEN divergencia_absoluta >= 10.00 AND taxa_divergencia_pct >= 30.0 THEN 'Critico'
            WHEN divergencia_absoluta >= 5.00 OR taxa_divergencia_pct >= 30.0 THEN 'Alto'
            WHEN pedidos_divergentes > 0 THEN 'Moderado'
            ELSE 'Sem alerta'
        END AS prioridade,
        CASE 
            WHEN divergencia_absoluta >= 10.00 AND taxa_divergencia_pct >= 30.0 THEN 'Revisao prioritaria'
            WHEN divergencia_absoluta >= 5.00 OR taxa_divergencia_pct >= 30.0 THEN 'Auditoria direcionada'
            WHEN pedidos_divergentes > 0 THEN 'Monitorar'
            ELSE 'Sem acao'
        END AS acao_sugerida
    FROM com_totais_e_ranking
)
-- Relatório final ordenado exatamente conforme solicitado
SELECT 
    posicao_impacto,
    mes,
    restaurante,
    pedidos_concluidos,
    pedidos_divergentes,
    taxa_divergencia_pct,
    divergencia_liquida,
    divergencia_absoluta,
    participacao_impacto_pct,
    prioridade,
    acao_sugerida
FROM com_prioridades
ORDER BY posicao_impacto ASC;