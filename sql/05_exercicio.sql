WITH mensal AS (
    -- Etapa 1: Consolidar os dados brutos por mês
    SELECT 
        SUBSTR(data_pedido, 1, 7) AS mes,
        COUNT(*) AS pedidos_concluidos,
        SUM(
            CASE 
                WHEN ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) != 0 
                THEN 1 ELSE 0 
            END
        ) AS pedidos_divergentes,
        ROUND(SUM(ABS((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real)), 2) AS divergencia_absoluta
    FROM pedidos
    WHERE status = 'concluido'
    GROUP BY SUBSTR(data_pedido, 1, 7)
),
com_taxas AS (
    -- Etapa 2: Calcular a taxa de divergência de cada mês
    SELECT 
        mes,
        pedidos_concluidos,
        pedidos_divergentes,
        ROUND((pedidos_divergentes * 100.0) / pedidos_concluidos, 2) AS taxa_divergencia_pct,
        divergencia_absoluta
    FROM mensal
)
-- Etapa 3: Aplicar LAG(), calcular a variação em p.p. e definir a tendência
SELECT 
    mes,
    pedidos_concluidos,
    pedidos_divergentes,
    taxa_divergencia_pct,
    divergencia_absoluta,
    LAG(taxa_divergencia_pct) OVER (ORDER BY mes ASC) AS taxa_mes_anterior,
    CASE 
        WHEN LAG(taxa_divergencia_pct) OVER (ORDER BY mes ASC) IS NULL THEN NULL
        ELSE ROUND(taxa_divergencia_pct - LAG(taxa_divergencia_pct) OVER (ORDER BY mes ASC), 2)
    END AS variacao_pp,
    CASE 
        WHEN LAG(taxa_divergencia_pct) OVER (ORDER BY mes ASC) IS NULL THEN 'Sem historico'
        WHEN (taxa_divergencia_pct - LAG(taxa_divergencia_pct) OVER (ORDER BY mes ASC)) > 0 THEN 'Aumentou'
        WHEN (taxa_divergencia_pct - LAG(taxa_divergencia_pct) OVER (ORDER BY mes ASC)) < 0 THEN 'Diminuiu'
        ELSE 'Estavel'
    END AS tendencia
FROM com_taxas
ORDER BY mes ASC;