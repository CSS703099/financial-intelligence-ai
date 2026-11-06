# Financial Intelligence AI — Guia para iniciantes

## O que é este projeto?

É um laboratório de finanças e automação com **dados inteiramente fictícios**. Ele ajuda a identificar diferenças entre valores esperados e repasses, visualizar indicadores e experimentar cenários hipotéticos de atraso de crédito.

A demonstração offline usa **pareceres escritos manualmente**. Existe código para chamar uma API de IA, mas a execução real ainda precisa ser validada. Nenhuma decisão financeira é executada automaticamente.

## Entenda o fluxo

1. Um CSV fictício fornece os pedidos de exemplo.
2. `criar_banco.py` transforma o CSV em uma tabela SQLite local.
3. As consultas SQL e as funções Pandas calculam indicadores.
4. O Streamlit apresenta gráficos, filtros e simulações.
5. O módulo de evidências prepara dossiês para revisão.
6. Os pareceres passam por validações e aprovação humana antes de exportação.

## Mapa dos arquivos Python

| Arquivo | Para que serve | Como funciona / cuidado |
|---|---|---|
| `app.py` | Abre o aplicativo Streamlit, permite escolher áreas de análise e mostra os resultados de conciliação e crédito. | É a porta de entrada visual; usa funções de scripts/ para cálculos e telas. |
| `scripts/criar_banco.py` | Lê o CSV de pedidos fictícios e cria a tabela de pedidos no SQLite local. | Execute para recriar o banco de demonstração; ele substitui a tabela de pedidos. |
| `scripts/executar_sql.py` | Lê um exercício SQL e executa consultas no banco SQLite em modo somente leitura. | Permite aprender e conferir consultas sem modificar os pedidos. |
| `scripts/indicadores_financeiros.py` | Calcula os indicadores financeiros a partir de consultas SQL ao SQLite. | Serve como implementação de referência para comparar os resultados com Pandas. |
| `scripts/analise_pandas.py` | Carrega os pedidos e calcula métricas de conciliação usando Python e Pandas. | Valida valores monetários e preserva os dados de entrada. |
| `scripts/dashboard_dados.py` | Filtra pedidos e prepara tabelas resumidas por restaurante e período. | Separa a lógica de dados dos elementos visuais do Streamlit. |
| `scripts/simulador_credito.py` | Simula mudanças hipotéticas nas faixas de atraso de 30 e 90 dias. | É uma simulação por regras; não prevê o futuro nem toma decisões de crédito. |
| `scripts/ia_explicavel.py` | Monta dossiês verificáveis, define o formato de parecer, valida respostas e controla a aprovação humana. | A integração de LLM existe em código, mas a execução real da API ainda não foi validada. |
| `scripts/ia_streamlit.py` | Mostra evidências, permite solicitar um parecer por API quando configurada e exige revisão. | Sem chave configurada, não faz chamada real; o usuário deve aprovar antes da exportação. |
| `scripts/demo_parecer_offline.py` | Monta exemplos de pareceres escritos manualmente para demonstrar validação e revisão. | Não chama modelo de IA e não deve ser apresentado como geração automática. |
| `scripts/demo_parecer_ui.py` | Apresenta os pareceres manuais e o fluxo de revisão no Streamlit. | Os exemplos são fixos e independentes dos controles de outros módulos. |
| `scripts/avaliacao_ia.py` | Testa se o validador rejeita exemplos de respostas inválidas ou contraditórias. | Não mede desempenho de um modelo real; avalia apenas verificações determinísticas. |
| `scripts/tema_visual.py` | Define as cores e o estilo do painel Streamlit. | Não altera cálculos financeiros nem é identidade oficial do iFood. |

## Exercícios SQL

| Arquivo | Explicação simples |
|---|---|
| `sql/00_exploracao.sql` | Explora os registros para conhecer a tabela de pedidos. |
| `sql/01_exercicio.sql` | Calcula os primeiros indicadores financeiros. |
| `sql/02_exercicio.sql` | Compara valores para identificar divergências de conciliação. |
| `sql/03_exercicio.sql` | Agrupa indicadores por restaurante. |
| `sql/04_exercicio.sql` | Organiza resultados com CTE e critérios de prioridade. |
| `sql/05_exercicio.sql` | Compara períodos e usa LAG para observar a evolução. |
| `sql/06_exercicio.sql` | Cria ranking e análise de concentração (Pareto). |
| `sql/07_exercicio.sql` | Identifica ocorrências e alertas por regras. |
| `sql/08_exercicio.sql` | Produz uma visão consolidada para acompanhamento executivo. |
| `sql/09_exercicio.sql` | Verifica qualidade e integridade dos dados. |
| `sql/10_exercicio.sql` | Compara períodos usando parâmetros. |
| `sql/11_exercicio.sql` | Confere equivalência de consultas e planos SQL. |
| `sql/12_exercicio.sql` | Integra os exercícios anteriores em uma análise final. |
| `sql/12_auditoria.sql` | Confere a consistência dos resultados do exercício integrador. |

## Testes automatizados

Arquivos em `tests/` verificam que partes do programa continuam funcionando depois de mudanças. Testes aprovados não significam que uma aplicação financeira está pronta para produção.

| Arquivo | O que verifica |
|---|---|
| `tests/test_analise_pandas.py` | cálculos financeiros e tratamento dos dados |
| `tests/test_dashboard.py` | filtros e dados usados no painel |
| `tests/test_demo_parecer_offline.py` | pareceres manuais sem chamada à IA |
| `tests/test_demo_parecer_ui.py` | fluxo visual de revisão da demonstração |
| `tests/test_demo_parecer_ui_v14.py` | regressões da interface da versão 1.4 |
| `tests/test_demo_parecer_ui_v15.py` | regressões da interface da versão 1.5 |
| `tests/test_ia_aprovacao_v151.py` | vínculo entre revisor, dossiê e parecer |
| `tests/test_ia_explicavel.py` | evidências, formato e validação de pareceres |
| `tests/test_ia_ui.py` | comportamento da tela de IA |
| `tests/test_integridade_v151_etapa2.py` | integridade monetária e consistência de dossiês |
| `tests/test_semantica_v151_etapa3.py` | contradições semânticas específicas |
| `tests/test_simulador_credito.py` | regras e limites do simulador 30+/90+ |
| `tests/test_simulador_ui.py` | integração visual do simulador |
| `tests/test_tema_visual.py` | estilos e elementos visuais |

## Como executar

```powershell
.\.venv\Scripts\python.exe scripts/criar_banco.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**Atenção:** `criar_banco.py` recria a tabela de pedidos. Execute apenas se quiser reconstruir a base fictícia.

## Termos explicados

- **SQLite:** banco de dados armazenado em arquivo no computador.
- **Pandas:** biblioteca Python que trabalha com tabelas.
- **Streamlit:** ferramenta para criar painéis web em Python.
- **Conciliação:** comparação entre o valor esperado e o valor recebido.
- **30+ e 90+:** faixas hipotéticas de atraso de pelo menos 30 ou 90 dias.
- **Dossiê:** conjunto de evidências calculadas e identificadas.
- **Parecer:** texto que descreve um cenário e recomenda verificações.
- **Hash SHA-256:** identificador que ajuda a perceber mudanças; não é uma assinatura autenticada.
- **Teste automatizado:** programa que confere um comportamento esperado.

## Limitações importantes

- Dados sintéticos e independência em relação ao iFood.
- Pareceres offline manuais, não gerados por LLM.
- Integração real de API ainda não validada.
- Verificações semânticas parciais; não garantem ausência de erros.
- Sem implantação de produção ou decisão financeira automática.
