-- GUIA PARA INICIANTES: Verifica qualidade e integridade dos dados.
-- Consultas de estudo com dados sintéticos; veja docs/guia_para_iniciantes.md.

WITH testes_qualidade AS (
    -- 1. ID_DUPLICADO: Verifica se há IDs repetidos (com o FROM pedidos adicionado!)
    SELECT 
        'ID_DUPLICADO' AS controle,
        'Qualidade' AS categoria,
        COUNT(*) - COUNT(DISTINCT pedido_id) AS ocorrencias
    FROM pedidos

    UNION ALL

    -- 2. CAMPO_OBRIGATORIO: Verifica nulos ou strings vazias em qualquer coluna obrigatória
    SELECT 
        'CAMPO_OBRIGATORIO',
        'Qualidade',
        COUNT(*) 
    FROM pedidos
    WHERE pedido_id IS NULL OR pedido_id = ''
       OR restaurante IS NULL OR restaurante = ''
       OR data_pedido IS NULL OR data_pedido = ''
       OR status IS NULL OR status = ''
       OR valor_bruto IS NULL
       OR taxa_plataforma IS NULL
       OR taxa_logistica IS NULL
       OR repasse_real IS NULL

    UNION ALL

    -- 3. STATUS_INVALIDO: Status diferentes de 'concluido' ou 'cancelado' (incluindo nulos)
    SELECT 
        'STATUS_INVALIDO',
        'Qualidade',
        COUNT(*) 
    FROM pedidos
    WHERE status NOT IN ('concluido', 'cancelado') 
       OR status IS NULL

    UNION ALL

    -- 4. VALOR_NEGATIVO: Valores negativos em qualquer uma das quatro colunas monetárias
    SELECT 
        'VALOR_NEGATIVO',
        'Qualidade',
        COUNT(*) 
    FROM pedidos
    WHERE valor_bruto < 0 
       OR taxa_plataforma < 0 
       OR taxa_logistica < 0 
       OR repasse_real < 0

    UNION ALL

    -- 5. CANCELADO_MOVIMENTADO: Pedidos cancelados que possuem taxas ou repasses diferentes de zero
    SELECT 
        'CANCELADO_MOVIMENTADO',
        'Qualidade',
        COUNT(*) 
    FROM pedidos
    WHERE status = 'cancelado' 
      AND (taxa_plataforma != 0 OR taxa_logistica != 0 OR repasse_real != 0)

    UNION ALL

    -- 6. DIVERGENCIA_REPASSE: Pedidos concluídos com diferença entre o repasse esperado e real
    SELECT 
        'DIVERGENCIA_REPASSE',
        'Financeiro',
        COUNT(*) 
    FROM pedidos
    WHERE status = 'concluido'
      AND ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) != 0
),
classificacao_testes AS (
    -- Etapa de classificação de situação, ação sugerida e prioridade de ordenação
    SELECT 
        controle,
        categoria,
        ocorrencias,
        CASE 
            WHEN ocorrencias = 0 THEN 'OK'
            WHEN categoria = 'Qualidade' THEN 'Falha'
            ELSE 'Revisar'
        END AS situacao,
        CASE 
            WHEN ocorrencias = 0 THEN 'Sem acao'
            WHEN categoria = 'Qualidade' THEN 'Corrigir dados'
            ELSE 'Investigar repasses'
        END AS acao_sugerida,
        -- Coluna auxiliar para ordenação: Falha (1), Revisar (2), OK (3)
        CASE 
            WHEN ocorrencias = 0 THEN 3
            WHEN categoria = 'Qualidade' THEN 1
            ELSE 2
        END AS ordem_situacao
    FROM testes_qualidade
)
-- Relatório final ordenado por gravidade e nome do controle
SELECT 
    controle,
    categoria,
    ocorrencias,
    situacao,
    acao_sugerida
FROM classificacao_testes
ORDER BY ordem_situacao ASC, controle ASC;