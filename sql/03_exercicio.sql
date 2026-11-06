-- GUIA PARA INICIANTES: Agrupa indicadores por restaurante.
-- Consultas de estudo com dados sintéticos; veja docs/guia_para_iniciantes.md.

SELECT
     restaurante,
     COUNT(*) AS pedidos_concluidos,
     SUM(
        CASE
            WHEN ROUND((valor_bruto - taxa_plataforma - taxa_logistica)- repasse_real, 2) != 0
            THEN 1
            ELSE 0
        END
     ) AS pedidos_divergentes,
    ROUND(SUM((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real), 2) AS divergencia_liquida,
    ROUND(SUM(ABS((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real)), 2) AS divergencia_absoluta
FROM pedidos
WHERE status = 'concluido'
GROUP BY restaurante
ORDER BY divergencia_absoluta DESC;
