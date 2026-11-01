WITH base_pedidos AS (
    -- Etapa 1: Preparação financeira de todos os pedidos concluídos
    SELECT 
        pedido_id,
        restaurante,
        SUBSTR(data_pedido, 1, 7) AS mes,
        ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) AS divergencia,
        ROUND(ABS((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real), 2) AS divergencia_absoluta
    FROM pedidos
    WHERE status = 'concluido'
),
resumo_restaurantes AS (
    -- Etapa 2: Total de pedidos concluídos por restaurante
    SELECT 
        restaurante,
        COUNT(*) AS pedidos_concluidos
    FROM base_pedidos
    GROUP BY restaurante
),
pedidos_divergentes AS (
    -- Etapa 3: Isolar apenas as divergências e calcular recorrência por restaurante
    SELECT 
        pedido_id,
        restaurante,
        divergencia,
        divergencia_absoluta,
        COUNT(*) OVER (PARTITION BY restaurante) AS qtd_divergencias_restaurante
    FROM base_pedidos
    WHERE divergencia != 0
),
alertas_individuais AS (
    -- Etapa 4: Classificar o nível de alerta de cada ocorrência
    SELECT 
        pedido_id,
        restaurante,
        divergencia_absoluta,
        CASE 
            WHEN divergencia_absoluta >= 7.00 THEN 'Critico'
            WHEN divergencia_absoluta >= 5.00 OR qtd_divergencias_restaurante >= 4 THEN 'Alto'
            ELSE 'Moderado'
        END AS nivel_alerta
    FROM pedidos_divergentes
),
consolidado_alertas AS (
    -- Etapa 5: Consolidar os alertas e divergências absolutas por restaurante
    SELECT 
        restaurante,
        COUNT(*) AS pedidos_divergentes,
        ROUND(SUM(divergencia_absoluta), 2) AS divergencia_absoluta,
        SUM(CASE WHEN nivel_alerta = 'Critico' THEN 1 ELSE 0 END) AS alertas_criticos,
        SUM(CASE WHEN nivel_alerta = 'Alto' THEN 1 ELSE 0 END) AS alertas_altos,
        SUM(CASE WHEN nivel_alerta = 'Moderado' THEN 1 ELSE 0 END) AS alertas_moderados
    FROM alertas_individuais
    GROUP BY restaurante
),
painel_completo AS (
    -- Etapa 6: Juntar com LEFT JOIN para incluir todos os restaurantes e calcular percentuais e prioridade
    SELECT 
        r.restaurante,
        r.pedidos_concluidos,
        COALESCE(c.pedidos_divergentes, 0) AS pedidos_divergentes,
        ROUND((COALESCE(c.pedidos_divergentes, 0) * 100.0) / r.pedidos_concluidos, 2) AS taxa_divergencia_pct,
        COALESCE(c.divergencia_absoluta, 0) AS divergencia_absoluta,
        COALESCE(c.alertas_criticos, 0) AS alertas_criticos,
        COALESCE(c.alertas_altos, 0) AS alertas_altos,
        COALESCE(c.alertas_moderados, 0) AS alertas_moderados,
        ROUND(
            (COALESCE(c.divergencia_absoluta, 0) * 100.0) / 
            (SELECT SUM(divergencia_absoluta) FROM alertas_individuais), 
            2
        ) AS participacao_impacto_pct,
        CASE 
            WHEN COALESCE(c.alertas_criticos, 0) > 0 THEN 'Critico'
            WHEN COALESCE(c.alertas_altos, 0) > 0 THEN 'Alto'
            WHEN COALESCE(c.pedidos_divergentes, 0) > 0 THEN 'Moderado'
            ELSE 'Sem alertas'
        END AS prioridade_restaurante,
        -- Coluna auxiliar para ordenação por prioridade (Critico = 1, Alto = 2, Moderado = 3, Sem alertas = 4)
        CASE 
            WHEN COALESCE(c.alertas_criticos, 0) > 0 THEN 1
            WHEN COALESCE(c.alertas_altos, 0) > 0 THEN 2
            WHEN COALESCE(c.pedidos_divergentes, 0) > 0 THEN 3
            ELSE 4
        END AS ordem_prioridade
    FROM resumo_restaurantes r
    LEFT JOIN consolidado_alertas c ON r.restaurante = c.restaurante
)
-- Etapa 7: Seleção final e ordenação executiva
SELECT 
    restaurante,
    pedidos_concluidos,
    pedidos_divergentes,
    taxa_divergencia_pct,
    divergencia_absoluta,
    alertas_criticos,
    alertas_altos,
    alertas_moderados,
    participacao_impacto_pct,
    prioridade_restaurante
FROM painel_completo
ORDER BY ordem_prioridade ASC, divergencia_absoluta DESC, restaurante ASC;