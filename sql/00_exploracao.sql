-- Dia 1: consulta exploratoria (dados sinteticos).
-- Exibe os primeiros dez pedidos, sem filtro de status.
SELECT
    pedido_id,
    data_pedido,
    restaurante,
    status,
    valor_bruto,
    taxa_plataforma,
    taxa_logistica,
    repasse_real
FROM pedidos
LIMIT 10;
