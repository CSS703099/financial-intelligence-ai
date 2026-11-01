WITH base_calculada AS (
    -- Etapa prévia: calcular valores e garantir que data_pedido seja incluída
    SELECT 
        pedido_id,
        data_pedido,
        SUBSTR(data_pedido, 1, 7) AS mes,
        restaurante,
        ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) AS divergencia,
        ROUND(ABS((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real), 2) AS divergencia_absoluta
    FROM pedidos
    WHERE status = 'concluido'
),
referencia AS (
    -- Etapa 1: Consulta de referência utilizando SUBSTR no filtro
    SELECT 
        mes,
        restaurante,
        COUNT(*) AS pedidos_concluidos,
        SUM(CASE WHEN divergencia != 0 THEN 1 ELSE 0 END) AS pedidos_divergentes,
        COALESCE(ROUND(SUM(divergencia_absoluta), 2), 0) AS divergencia_absoluta
    FROM base_calculada
    WHERE mes IN ('2026-09', '2026-10')
    GROUP BY mes, restaurante
),
otimizada AS (
    -- Etapa 2: Consulta otimizada utilizando filtro direto por intervalo sobre data_pedido
    SELECT 
        SUBSTR(data_pedido, 1, 7) AS mes,
        restaurante,
        COUNT(*) AS pedidos_concluidos,
        SUM(CASE WHEN divergencia != 0 THEN 1 ELSE 0 END) AS pedidos_divergentes,
        COALESCE(ROUND(SUM(divergencia_absoluta), 2), 0) AS divergencia_absoluta
    FROM base_calculada
    WHERE data_pedido >= '2026-09-01' AND data_pedido < '2026-11-01'
    GROUP BY SUBSTR(data_pedido, 1, 7), restaurante
),
todas_combinacoes AS (
    -- Etapa 3: Unir todas as chaves (mês + restaurante) de ambas as versões para validação robusta
    SELECT mes, restaurante FROM referencia
    UNION
    SELECT mes, restaurante FROM otimizada
),
validacao_comparada AS (
    -- Etapa 4: Comparar os resultados de cada versão combinada
    SELECT 
        t.mes,
        t.restaurante,
        COALESCE(o.pedidos_concluidos, 0) AS pedidos_concluidos,
        COALESCE(o.pedidos_divergentes, 0) AS pedidos_divergentes,
        COALESCE(
            ROUND((o.pedidos_divergentes * 100.0) / NULLIF(o.pedidos_concluidos, 0), 2),
            0
        ) AS taxa_divergencia_pct,
        COALESCE(o.divergencia_absoluta, 0) AS divergencia_absoluta,
        CASE 
            WHEN r.mes IS NULL OR o.mes IS NULL
              OR r.pedidos_concluidos != o.pedidos_concluidos
              OR r.pedidos_divergentes != o.pedidos_divergentes
              OR r.divergencia_absoluta != o.divergencia_absoluta
            THEN 'DIVERGENTE'
            ELSE 'OK'
        END AS validacao
    FROM todas_combinacoes t
    LEFT JOIN referencia r ON t.mes = r.mes AND t.restaurante = r.restaurante
    LEFT JOIN otimizada o ON t.mes = o.mes AND t.restaurante = o.restaurante
)
-- Relatório final ordenado por mês e restaurante
SELECT 
    mes,
    restaurante,
    pedidos_concluidos,
    pedidos_divergentes,
    taxa_divergencia_pct,
    divergencia_absoluta,
    validacao
FROM validacao_comparada
ORDER BY mes ASC, restaurante ASC;