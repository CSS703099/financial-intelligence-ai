WITH resumo_restaurantes AS (
    SELECT 
        restaurante,
        COUNT(*) AS pedidos_concluidos,
        SUM(
            CASE 
                WHEN ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) != 0 
                THEN 1 
                ELSE 0 
            END
        ) AS pedidos_divergentes,
        ROUND(SUM(ABS((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real)), 2) AS divergencia_absoluta
    FROM pedidos
    WHERE status = 'concluido'
    GROUP BY restaurante
)
SELECT 
    restaurante,
    pedidos_concluidos,
    pedidos_divergentes,
    ROUND((pedidos_divergentes * 100.0) / pedidos_concluidos, 2) AS taxa_divergencia_pct,
    divergencia_absoluta,
    CASE 
        WHEN (pedidos_divergentes * 100.0) / pedidos_concluidos >= 30 THEN 'Alta'
        WHEN (pedidos_divergentes * 100.0) / pedidos_concluidos >= 15 THEN 'Media'
        ELSE 'Baixa'
    END AS prioridade
FROM resumo_restaurantes
ORDER BY taxa_divergencia_pct DESC;