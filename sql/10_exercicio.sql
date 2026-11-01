WITH parametros AS (
    -- Etapa 1: Definir os intervalos de datas configuráveis
    SELECT 
        'Setembro/2026' AS periodo,
        '2026-09-01' AS data_inicio,
        '2026-09-30' AS data_fim,
        1 AS ordem

    UNION ALL

    SELECT 
        'Outubro/2026',
        '2026-10-01',
        '2026-10-31',
        2
),
base_pedidos AS (
    -- Etapa 2: Filtrar apenas pedidos concluídos com as divergências calculadas
    SELECT 
        pedido_id,
        data_pedido,
        ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) AS divergencia,
        ROUND(ABS((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real), 2) AS divergencia_absoluta
    FROM pedidos
    WHERE status = 'concluido'
),
indicadores_periodo AS (
    -- Etapa 3: LEFT JOIN para associar os pedidos aos períodos (preservando períodos vazios)
    SELECT 
        p.periodo,
        p.data_inicio,
        p.data_fim,
        p.ordem,
        -- Contar pedidos usando pedido_id para evitar contagem incorreta em linhas vazias do LEFT JOIN
        COUNT(b.pedido_id) AS pedidos_concluidos,
        SUM(
            CASE 
                WHEN b.divergencia != 0 THEN 1 
                ELSE 0 
            END
        ) AS pedidos_divergentes,
        COALESCE(SUM(b.divergencia_absoluta), 0) AS divergencia_absoluta
    FROM parametros p
    LEFT JOIN base_pedidos b ON b.data_pedido BETWEEN p.data_inicio AND p.data_fim
    GROUP BY p.periodo, p.data_inicio, p.data_fim, p.ordem
),
taxas_periodo AS (
    -- Etapa 4: Calcular a taxa de divergência com tratamento seguro contra divisão por zero
    SELECT 
        periodo,
        data_inicio,
        data_fim,
        ordem,
        pedidos_concluidos,
        pedidos_divergentes,
        COALESCE(
            ROUND(
                (pedidos_divergentes * 100.0) / NULLIF(pedidos_concluidos, 0),
                2
            ),
            0
        ) AS taxa_divergencia_pct,
        divergencia_absoluta
    FROM indicadores_periodo
),
comparacao_periodos AS (
    -- Etapa 5: Aplicar LAG() para recuperar a taxa do período anterior
    SELECT 
        periodo,
        data_inicio,
        data_fim,
        ordem,
        pedidos_concluidos,
        pedidos_divergentes,
        taxa_divergencia_pct,
        divergencia_absoluta,
        LAG(taxa_divergencia_pct) OVER (ORDER BY ordem) AS taxa_anterior_pct
    FROM taxas_periodo
)
-- Etapa 6: Seleção final, cálculo da variação em p.p. e ordenação sem expor a coluna auxiliar
SELECT 
    periodo,
    data_inicio,
    data_fim,
    pedidos_concluidos,
    pedidos_divergentes,
    taxa_divergencia_pct,
    divergencia_absoluta,
    taxa_anterior_pct,
    CASE 
        WHEN taxa_anterior_pct IS NULL THEN NULL
        ELSE ROUND(taxa_divergencia_pct - taxa_anterior_pct, 2)
    END AS variacao_pp
FROM comparacao_periodos
ORDER BY ordem ASC;