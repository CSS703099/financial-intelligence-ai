-- GUIA PARA INICIANTES: Identifica ocorrências e alertas por regras.
-- Consultas de estudo com dados sintéticos; veja docs/guia_para_iniciantes.md.

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
pedidos_divergentes AS (
    -- Etapa 2: Filtrar apenas os pedidos que possuem divergência diferente de zero
    SELECT 
        pedido_id,
        restaurante,
        mes,
        divergencia,
        divergencia_absoluta
    FROM base_pedidos
    WHERE divergencia != 0
),
recorrencia_e_regras AS (
    -- Etapa 3: Calcular recorrência por restaurante e definir os tipos, alertas e ações
    SELECT 
        pedido_id,
        restaurante,
        mes,
        divergencia,
        divergencia_absoluta,
        COUNT(*) OVER (PARTITION BY restaurante) AS qtd_divergencias_restaurante,
        CASE 
            WHEN divergencia > 0 THEN 'Repasse abaixo do esperado'
            ELSE 'Repasse acima do esperado'
        END AS tipo_divergencia,
        CASE 
            WHEN divergencia_absoluta >= 7.00 THEN 'Critico'
            WHEN divergencia_absoluta >= 5.00 OR COUNT(*) OVER (PARTITION BY restaurante) >= 4 THEN 'Alto'
            ELSE 'Moderado'
        END AS nivel_alerta,
        CASE 
            WHEN divergencia_absoluta >= 7.00 THEN 'Revisao imediata'
            WHEN divergencia_absoluta >= 5.00 OR COUNT(*) OVER (PARTITION BY restaurante) >= 4 THEN 'Auditoria prioritaria'
            ELSE 'Monitoramento'
        END AS acao_sugerida,
        -- Coluna auxiliar para ordenar a gravidade corretamente (Critico = 1, Alto = 2, Moderado = 3)
        CASE 
            WHEN divergencia_absoluta >= 7.00 THEN 1
            WHEN divergencia_absoluta >= 5.00 OR COUNT(*) OVER (PARTITION BY restaurante) >= 4 THEN 2
            ELSE 3
        END AS ordem_gravidade
    FROM pedidos_divergentes
)
-- Etapa 4: Seleção final e ordenação por gravidade, divergência absoluta e ID do pedido
SELECT 
    pedido_id,
    restaurante,
    mes,
    divergencia,
    divergencia_absoluta,
    qtd_divergencias_restaurante,
    tipo_divergencia,
    nivel_alerta,
    acao_sugerida
FROM recorrencia_e_regras
ORDER BY ordem_gravidade ASC, divergencia_absoluta DESC, pedido_id ASC;