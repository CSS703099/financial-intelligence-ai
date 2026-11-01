WITH metricas_observadas AS (
    -- 1. TOTAL_PEDIDOS
    SELECT 'TOTAL_PEDIDOS' AS controle, COUNT(*) AS valor_obs, 36 AS valor_esp FROM pedidos
    
    UNION ALL
    
    -- 2. CONCLUIDOS
    SELECT 'CONCLUIDOS', COUNT(*), 30 FROM pedidos WHERE status = 'concluido'
    
    UNION ALL
    
    -- 3. CANCELADOS
    SELECT 'CANCELADOS', COUNT(*), 6 FROM pedidos WHERE status = 'cancelado'
    
    UNION ALL
    
    -- 4. PEDIDOS_DIVERGENTES
    SELECT 'PEDIDOS_DIVERGENTES', COUNT(*), 7 FROM pedidos 
    WHERE status = 'concluido' 
      AND ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) != 0
    
    UNION ALL
    
    -- 5. DIVERGENCIA_LIQUIDA
    SELECT 'DIVERGENCIA_LIQUIDA', 
           COALESCE(ROUND(SUM((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real), 2), 0), 
           22.10 
    FROM pedidos WHERE status = 'concluido'
    
    UNION ALL
    
    -- 6. DIVERGENCIA_ABSOLUTA
    SELECT 'DIVERGENCIA_ABSOLUTA', 
           COALESCE(ROUND(SUM(ABS((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real)), 2), 0), 
           38.10 
    FROM pedidos WHERE status = 'concluido'
    
    UNION ALL
    
    -- 7. IDS_DUPLICADOS
    SELECT 'IDS_DUPLICADOS', COUNT(*) - COUNT(DISTINCT pedido_id), 0 FROM pedidos
    
    UNION ALL
    
    -- 8. FALHAS_QUALIDADE (Contagem unificada de registros com falhas de integridade)
    SELECT 'FALHAS_QUALIDADE', 
           COUNT(*), 
           0 
    FROM pedidos 
    WHERE pedido_id IS NULL OR pedido_id = ''
       OR restaurante IS NULL OR restaurante = ''
       OR data_pedido IS NULL OR data_pedido = ''
       OR status IS NULL OR status = ''
       OR valor_bruto IS NULL OR valor_bruto < 0
       OR taxa_plataforma IS NULL OR taxa_plataforma < 0
       OR taxa_logistica IS NULL OR taxa_logistica < 0
       OR repasse_real IS NULL OR repasse_real < 0
       OR status NOT IN ('concluido', 'cancelado') OR status IS NULL
       OR (status = 'cancelado' AND (taxa_plataforma != 0 OR taxa_logistica != 0 OR repasse_real != 0))
)
SELECT 
    controle,
    valor_obs AS valor_observado,
    valor_esp AS valor_esperado,
    CASE 
        WHEN valor_obs = valor_esp THEN 'OK'
        ELSE 'DIVERGENTE'
    END AS validacao
FROM metricas_observadas;