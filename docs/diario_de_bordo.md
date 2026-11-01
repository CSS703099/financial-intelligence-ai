# Diario de bordo — Financial Intelligence AI

## Dia 1 — 2026-11-01 (registro das entregas)

**Contexto:** treinamento individual para construcao de portfolio em Dados, Financas e IA aplicada a negocios. Projeto independente, com dados 100% sinteticos, sem vinculo de desenvolvimento com o iFood.

### Etapas verificadas
- [x] Python 3.13 e VS Code instalados.
- [x] Banco SQLite criado com 36 pedidos ficticios.
- [x] Consulta exploratoria: 10 registros retornados.
- [x] Exercicio 01 — Indicadores financeiros, nota **9/10**.
- [x] Exercicio 02 — Conciliacao financeira, nota **10/10**.
- [x] Exercicio 03 — Divergencias por restaurante, nota **10/10**.
- [x] Exercicio 04 — Taxa de divergencia com CTE e classificacao, nota **10/10**.
- [x] Exercicio 05 — Evolucao mensal com CTEs e `LAG()`, nota **10/10**.
- [x] Exercicio 06 — Ranking de divergencias e Pareto com funcoes de janela, nota **10/10**.
- [x] Exercicio 07 — Deteccao por regras e alertas financeiros, nota **10/10**.
- [x] Exercicio 08 — Painel executivo de risco por restaurante, nota **10/10**.
- [x] Exercicio 09 — Controles de qualidade e consistencia financeira, nota **10/10**.
- [x] Exercicio 10 — Comparacao parametrizada de periodos, nota **10/10**.
- [x] Exercicio 11 — Equivalencia financeira e analise de planos SQL, nota **10/10**.

### Exercicio 01 — Indicadores dos pedidos concluidos
- Quantidade de pedidos concluidos: **30**.
- Faturamento bruto: **R$ 4.687,60**.
- Taxas da plataforma: **R$ 609,40**.
- Taxas logisticas: **R$ 235,50**.
- Repasses realizados: **R$ 3.820,60**.

**Aprendizado:** `COUNT(*)` conta linhas, `SUM()` agrega valores e `WHERE` restringe os pedidos analisados. O status correto na base e `concluido`, sem acento. Um filtro incorreto retornava zero pedidos e somas nulas.

### Exercicio 02 — Conciliacao financeira
- Pedidos com divergencia: **7** (de 30 concluidos).
- Taxa de divergencia: **23,33%**.
- Divergencia liquida assinada: **R$ 22,10**.
- Soma absoluta das divergencias: **R$ 38,10**.
- Maior divergencia individual absoluta: **R$ 9,90** (pedido PED-0020).

**Aprendizado:** calculos entre colunas, `ROUND()`, `ABS()`, filtros combinados com `AND` e `ORDER BY`. O erro local `wrong number of arguments to function ROUND()` deixou de ocorrer apos revisar/salvar o arquivo. A causa exata nao foi comprovada; versao nao salva e uma hipotese.

### Limites de interpretacao
Divergencia financeira nao comprova fraude, falha ou prejuizo. O modelo de repasse e simplificado e os registros sao artificiais. Repasse ao restaurante nao equivale a lucro.

### Proxima atividade
Exercicios 01 a 11 concluidos e aprovados. Exercicio 12 ainda nao iniciado.

### Validacao do ambiente Git / GitHub — 2026-11-01

- [x] Git for Windows 2.56.0.windows.4 instalado e validado com `git --version`.
- [x] Repositorio privado `CSS703099/financial-intelligence-ai` clonado na pasta `financial-intelligence-ai`.
- [x] Pasta inicial `Financial_Intelligence_AI` preservada como backup.
- [x] `git status`: branch `main`, sem alteracoes locais pendentes, sincronizada com `origin/main` no momento do teste.
- [x] `py -3.13 scripts/criar_banco.py`: banco criado com 36 registros ficticios.
- [x] `py -3.13 scripts/executar_sql.py sql/01_exercicio.sql`: 30 pedidos concluidos; R$ 4.687,60 de valor bruto; R$ 609,40 de taxas da plataforma; R$ 235,50 de taxas logisticas; R$ 3.820,60 em repasses realizados.
- [x] `py -3.13 scripts/executar_sql.py sql/02_exercicio.sql`: 7 pedidos divergentes, de PED-0003 a PED-0035.

**Resultado:** configuracao local de Git, clonagem, geracao de dados e execucao dos dois exercicios validadas pelo usuario no terminal PowerShell. Exercicio 03 foi concluido posteriormente, com validacao da consulta e nota definitiva 10/10.

**Sincronizacao:** o registro acima foi adicionado pelo assistente diretamente no GitHub; executar `git pull --ff-only` na pasta clonada para baixar este novo commit antes de editar.

### Exercicio 03 — Conciliacao por restaurante (aprovado, 10/10)

Consulta desenvolvida pelo aluno e validada no SQLite com a base original de 36 pedidos sinteticos. Arquivo: `sql/03_exercicio.sql`.

| Restaurante | Concluidos | Divergentes | Diferenca liquida (R$) | Diferenca absoluta (R$) |
|---|---:|---:|---:|---:|
| Restaurante B | 12 | 5 | 11,40 | 27,40 |
| Restaurante A | 6 | 1 | 6,20 | 6,20 |
| Restaurante C | 12 | 1 | 4,50 | 4,50 |
| **Total** | **30** | **7** | **22,10** | **38,10** |

**Competencias demonstradas:** `GROUP BY`, `COUNT(*)`, `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`, `ABS()`, `ROUND()`, `ORDER BY ... DESC` e raciocinio financeiro sobre diferencas liquidas e absolutas.

**Incidente e resolucao:** na primeira tentativa, o aluno juntou dois comandos no terminal, gerando a mensagem de uso do script. Ao executar `py -3.13 scripts/executar_sql.py sql/03_exercicio.sql` corretamente, obteve as tres linhas acima. Nao houve erro na consulta SQL.

**Interpretacao:** Restaurante B concentra o maior volume de divergencias absolutas (R$ 27,40), merecendo prioridade de verificacao. A base e ficticia e divergencias nao comprovam erro ou fraude.

**Estado naquele momento:** Exercicio 03 aprovado; Exercicio 04 foi concluido posteriormente (detalhes abaixo).

### Exercicio 04 — Taxa de divergencia e classificacao (aprovado, 10/10)

- **Arquivo:** `sql/04_exercicio.sql`.
- **Commit do aluno:** `4129b01` em `main`, enviado com `git push origin main`.
- **Execucao local confirmada:** 3 linhas no SQLite, apos recriar o banco local com 36 pedidos sinteticos.

| Restaurante | Pedidos concluidos | Pedidos divergentes | Taxa | Divergencia absoluta (R$) | Prioridade |
|---|---:|---:|---:|---:|---|
| Restaurante B | 12 | 5 | 41,67% | 27,40 | Alta |
| Restaurante A | 6 | 1 | 16,67% | 6,20 | Media |
| Restaurante C | 12 | 1 | 8,33% | 4,50 | Baixa |

**Competencias demonstradas:** `WITH`/CTE, agregacoes por restaurante, contagem condicional via `SUM(CASE WHEN ...)`, calculo percentual com `100.0` (divisao decimal no SQLite), `ROUND()`, classificacao `CASE WHEN` e ordenacao de indicadores.

**Regra de classificacao (exclusivamente didatica):** Alta a partir de 30%, Media a partir de 15% e abaixo de 30%, Baixa abaixo de 15%. Nao representa indicador oficial ou risco validado de plataforma real.

**Recuperacao do ambiente:** o antigo checkout em pasta sincronizada ao OneDrive apresentou `HEAD` invalido. O usuario preservou uma copia de recuperacao, clonou o repositorio em `C:\\Users\\caion\\Projetos\\financial-intelligence-ai`, restaurou apenas o SQL 04, reproduziu os resultados, configurou a identidade local do Git e publicou o arquivo. O novo checkout passou no teste de sincronizacao `git status -sb`: `## main...origin/main`.

**Estado naquela etapa:** Exercicio 04 aprovado e publicado; o Exercicio 05 foi concluido posteriormente.

### Exercicio 05 — Analise temporal e LAG() (aprovado, 10/10)

- **Arquivo:** `sql/05_exercicio.sql`.
- **Commit publicado pelo aluno:** `e0738fd` na branch `main`.
- **Execucao local confirmada:** 2 linhas retornadas pelo SQLite com a base original sintetica.
- **Conceitos praticados:** CTEs encadeadas, `SUBSTR(data_pedido, 1, 7)`, agregacoes mensais, `SUM(CASE WHEN ...)`, `LAG(...) OVER (ORDER BY mes)`, variacao em pontos percentuais e classificacao condicional com `CASE WHEN`.

| Mes | Pedidos concluidos | Pedidos divergentes | Taxa divergencia | Divergencia absoluta (R$) | Taxa mes anterior | Variacao (p.p.) | Tendencia |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-09 | 18 | 4 | 22,22% | 24,40 | NULL | NULL | Sem historico |
| 2026-10 | 12 | 3 | 25,00% | 13,70 | 22,22% | +2,78 | Aumentou |

**Interpretacao:** a taxa aumentou de 22,22% para 25,00%, enquanto o volume absoluto das diferencas caiu de R$ 24,40 para R$ 13,70. E uma comparacao entre apenas dois meses, insuficiente para identificar uma tendencia sustentada.

**Aprendizado de versionamento:** o arquivo foi criado inicialmente na pasta antiga; o aluno o transferiu para o clone valido fora do OneDrive, executou a consulta, adicionou somente o SQL 05, criou o commit `e0738fd`, fez `git push origin main` e validou `git status -sb` sem pendencias.

**Resultado naquela etapa:** Exercicio 05 aprovado e publicado; o Exercicio 06 foi concluido posteriormente. Todas as metricas sao de dados ficticios, e divergencias nao significam fraude ou erro confirmado.

### Exercicio 06 — Ranking de divergencias e Pareto (aprovado, 10/10)

- **Arquivo:** `sql/06_exercicio.sql`, publicado na branch `main` do repositorio privado.
- **Execucao local confirmada pelo aluno:** sete linhas no SQLite, apos transferir a consulta para a pasta de trabalho valida fora do OneDrive.
- **Habilidades:** CTEs encadeadas, `ROW_NUMBER() OVER (...)`, `SUM(...) OVER ()`, janela acumulada com `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, `ABS()`, `ROUND()` e desempate deterministico no ranking.

| Posicao | Pedido | Divergencia assinada (R$) | Absoluta (R$) | Participacao | Acumulado |
|---|---|---:|---:|---:|---:|
| 1 | PED-0020 | 9,90 | 9,90 | 25,98% | 25,98% |
| 2 | PED-0008 | 7,00 | 7,00 | 18,37% | 44,36% |
| 3 | PED-0031 | 6,20 | 6,20 | 16,27% | 60,63% |
| 4 | PED-0026 | -5,00 | 5,00 | 13,12% | 73,75% |
| 5 | PED-0003 | 4,50 | 4,50 | 11,81% | 85,56% |
| 6 | PED-0014 | -3,00 | 3,00 | 7,87% | 93,44% |
| 7 | PED-0035 | 2,50 | 2,50 | 6,56% | 100,00% |

**Interpretacao:** as cinco maiores divergencias absolutas representam R$ 32,60, equivalentes a 85,56% do total absoluto de R$ 38,10. Percentuais individuais arredondados somam 99,98%, enquanto o acumulado final calculado sobre valores monetarios nao arredondados no percentual resulta em 100,00%.

**Cuidado analitico:** este ranking e uma priorizacao didatica de verificacao financeira, nao um indicio conclusivo de fraude ou prejuizo.

**Resultado naquela etapa:** Exercicio 06 aprovado e publicado; Exercicio 07 concluido posteriormente.

### Exercicio 07 — Deteccao por regras e alertas financeiros (aprovado, 10/10)

- **Arquivo:** `sql/07_exercicio.sql`, disponivel na branch `main` do repositorio privado.
- **Commit do aluno:** `1b58f8b` — `feat(sql): concluir exercicio 07 com alertas financeiros`.
- **Verificacao:** 7 pedidos divergentes e 9 colunas; resultado confirmado pelo aluno ao executar o SQL no clone principal fora do OneDrive.
- **Competencias:** CTEs, `COUNT(*) OVER (PARTITION BY restaurante)`, `CASE WHEN`, divergencias assinadas e absolutas, regras de gravidade, recomendacoes e ordenacao deterministica.

| Nivel de alerta | Pedidos | Acao sugerida |
|---|---:|---|
| Critico | 2 | Revisao imediata |
| Alto | 4 | Auditoria prioritaria |
| Moderado | 1 | Monitoramento |
| **Total** | **7** | |

**Controles da base sintetica:** 30 pedidos concluidos, 7 divergentes, dos quais 5 com diferenca positiva e 2 com diferenca negativa; soma absoluta R$ 38,10.

**Criterios didaticos:** Critico para divergencia absoluta >= R$ 7,00; Alto para divergencia absoluta >= R$ 5,00 ou restaurante com >= 4 pedidos divergentes (desde que nao Critico); Moderado para os demais casos. O calculo de recorrencia considera toda a base disponivel, sem janela temporal.

**Interpretacao:** o Restaurante B concentra 5 dos 7 pedidos divergentes, justificando priorizacao de verificacao segundo as regras. Recomendacoes nao sao ordens de execucao; divergencia nao comprova fraude, erro ou prejuizo.

**Estado naquela etapa:** Exercicio 07 aprovado, publicado e documentado; Exercicio 08 concluido posteriormente.

### Exercicio 08 — Painel executivo de risco por restaurante (aprovado, 10/10)

- **Arquivo:** `sql/08_exercicio.sql`, publicado na branch `main` do repositorio privado.
- **Commit do aluno:** `40b0348` — `feat(sql): concluir exercicio 08 com painel executivo de risco`.
- **Execucao local confirmada:** 3 linhas e 10 colunas na base sintetica de 36 pedidos, sendo 30 concluidos.
- **Competencias:** CTEs, resumo de pedidos por restaurante, filtragem de divergencias, `COUNT(*) OVER (PARTITION BY restaurante)`, classificacao por `CASE WHEN`, agregacao condicional, `LEFT JOIN`, `COALESCE`, percentual de participacao e ordenacao pela prioridade.

| Restaurante | Concluidos | Divergentes | Taxa de divergencia | Absoluta (R$) | Critico | Alto | Moderado | Participacao no impacto | Prioridade |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| B | 12 | 5 | 41,67% | 27,40 | 2 | 3 | 0 | 71,92% | Critico |
| A | 6 | 1 | 16,67% | 6,20 | 0 | 1 | 0 | 16,27% | Alto |
| C | 12 | 1 | 8,33% | 4,50 | 0 | 0 | 1 | 11,81% | Moderado |

**Controles:** 30 pedidos concluidos, 7 divergentes, R$ 38,10 em divergencias absolutas, 2 alertas Critico, 4 Alto, 1 Moderado, 100% de participacao somada.

**Interpretacao:** restaurante B tem prioridade de verificacao pelas regras didaticas, concentrando 71,92% do valor absoluto das divergencias e dois alertas criticos.

**Limitacoes reconhecidas:** o `LEFT JOIN` preserva estabelecimentos com pedidos concluidos e nenhum alerta; para incluir estabelecimentos sem qualquer pedido concluido, seria necessario um cadastro completo de restaurantes. Uma base sem divergencias exige tratar explicitamente o denominador nulo ou zero no calculo de participacao.

**Seguranca e escopo:** todos os registros sao ficticios; as regras nao comprovam fraude nem autorizam acoes financeiras automaticas. O painel ainda nao e uma interface visual interativa.

**Estado naquela etapa:** Exercicio 08 aprovado, publicado e documentado; Exercicio 09 concluido posteriormente.

### Exercicio 09 — Controles de qualidade e consistencia financeira (aprovado, 10/10)

- **Arquivo:** `sql/09_exercicio.sql`, publicado na branch `main` do repositorio privado.
- **Commit do aluno:** `e86a2dc` — `feat(sql): concluir exercicio 09 com controles de qualidade`.
- **Execucao local confirmada pelo aluno:** 6 linhas e 5 colunas com a base original de 36 pedidos sinteticos.
- **Competencias:** `UNION ALL`, CTEs, `COUNT(*) - COUNT(DISTINCT pedido_id)`, `IS NULL`, `NOT IN`, validacao de dominios e sinais monetarios, regras de cancelamento, conciliacao de repasses, `CASE WHEN` e ordenacao pela gravidade.

| Controle | Categoria | Ocorrencias | Situacao | Acao sugerida |
|---|---|---:|---|---|
| DIVERGENCIA_REPASSE | Financeiro | 7 | Revisar | Investigar repasses |
| CAMPO_OBRIGATORIO | Qualidade | 0 | OK | Sem acao |
| CANCELADO_MOVIMENTADO | Qualidade | 0 | OK | Sem acao |
| ID_DUPLICADO | Qualidade | 0 | OK | Sem acao |
| STATUS_INVALIDO | Qualidade | 0 | OK | Sem acao |
| VALOR_NEGATIVO | Qualidade | 0 | OK | Sem acao |

**Aprendizado e correcao:** a primeira execucao apresentou `sqlite3.OperationalError: no such column: pedido_id` porque a consulta do controle `ID_DUPLICADO` nao possuia `FROM pedidos`. O aluno identificou e corrigiu a ausencia da clausula, reexecutou com sucesso e recebeu nota definitiva **10/10**.

**Interpretacao:** 5 controles de qualidade estao em `OK` nesta base; a unica verificacao com ocorrencias e de natureza financeira (`Revisar`), com 7 repasses divergentes. Isso nao comprova falha de cadastro, fraude ou prejuizo. A chave primaria `pedido_id` e os `CHECK` do schema ja restringem alguns erros na tabela original; os controles sao uteis para validacao e auditoria.

**Progresso naquela etapa:** 9 de 12 exercicios aprovados, com media de **9,89/10**. O Exercicio 10 foi concluido posteriormente.

### Exercicio 10 — Comparacao parametrizada de periodos (aprovado, 10/10)

- **Arquivo:** `sql/10_exercicio.sql`, publicado na branch `main` do repositorio privado.
- **Commit do aluno:** `9c336b4` — `feat(sql): concluir exercicio 10 com comparacao parametrizada de periodos`.
- **Execucao local confirmada pelo aluno:** duas linhas e nove colunas na base original de 36 pedidos sinteticos.
- **Competencias:** CTE de parametros com `UNION ALL`, filtro de pedidos concluidos, calculo de divergencias, `LEFT JOIN` temporal, agregacoes condicionais, `COUNT(b.pedido_id)`, `COALESCE`, `NULLIF`, `LAG() OVER (ORDER BY ordem)` e variacao em pontos percentuais.

| Periodo | Inicio | Fim | Concluidos | Divergentes | Taxa | Absoluta (R$) | Taxa anterior | Variacao (p.p.) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Setembro/2026 | 2026-09-01 | 2026-09-30 | 18 | 4 | 22,22% | 24,40 | NULL | NULL |
| Outubro/2026 | 2026-10-01 | 2026-10-31 | 12 | 3 | 25,00% | 13,70 | 22,22% | +2,78 |

**Interpretacao:** a taxa de divergencia aumentou 2,78 pontos percentuais, apesar da reducao de R$ 10,70 na soma absoluta das divergencias. Apenas dois periodos nao sustentam inferencia de tendencia duradoura.

**Teste didatico de periodo vazio:** ao substituir temporariamente outubro por novembro/2026, sem pedidos na base, a logica preserva novembro, apresenta 0 concluidos, 0 divergentes, taxa exibida 0% e divergencia absoluta R$ 0,00. A variacao contra setembro fica -22,22 p.p., mas representa a convencao de exibicao de zero para ausencia de dados, nao uma melhoria financeira comprovada. A consulta publicada preserva os parametros setembro/outubro.

**Limitacoes reconhecidas:** os parametros sao definidos por CTE, e ainda nao sao entradas vinculadas de uma aplicacao. Para cenarios reais, validar intervalos e evitar sobreposicoes indevidas; distinguir periodo sem dados de taxa observada igual a zero.

**Progresso naquela etapa:** 10 de 12 exercicios aprovados na trilha SQL proposta, media de **9,90/10**. Exercicio 11 concluido posteriormente.

### Exercicio 11 — Equivalencia financeira e otimizacao de filtros SQL (aprovado, 10/10)

- **Arquivo:** `sql/11_exercicio.sql`, publicado no repositorio privado, branch `main`.
- **Commit do aluno:** `b1ceb9b` — `feat(sql): concluir exercicio 11 com validacao e otimizacao`.
- **Execucao local confirmada pelo aluno:** seis linhas, sete colunas, todas com `validacao = 'OK'`.
- **Competencias:** CTEs, calculo de divergencias, comparacao de filtro mensal por `SUBSTR` com filtro direto `data_pedido >= ... AND data_pedido < ...`, `UNION` de chaves, `LEFT JOIN`, verificacao de grupos ausentes, `NULLIF`, `COALESCE`, `EXPLAIN QUERY PLAN` e interpretacao de indices.

| Mes | Restaurante | Concluidos | Divergentes | Taxa | Absoluta (R$) | Validacao |
|---|---|---:|---:|---:|---:|---|
| 2026-09 | Restaurante A | 4 | 0 | 0,00% | 0,00 | OK |
| 2026-09 | Restaurante B | 7 | 3 | 42,86% | 19,90 | OK |
| 2026-09 | Restaurante C | 7 | 1 | 14,29% | 4,50 | OK |
| 2026-10 | Restaurante A | 2 | 1 | 50,00% | 6,20 | OK |
| 2026-10 | Restaurante B | 5 | 2 | 40,00% | 7,50 | OK |
| 2026-10 | Restaurante C | 5 | 0 | 0,00% | 0,00 | OK |

**Totais validados:** 30 pedidos concluidos, 7 divergentes e R$ 38,10 de diferencas absolutas. A comparacao identifica divergencias nos indicadores e combinacoes de chave presentes em apenas uma das versoes.

**Correcao durante a atividade:** a primeira consulta enviada nao disponibilizava `data_pedido` na CTE `base_calculada`, apesar de usa-la no filtro da CTE `otimizada`. O aluno acrescentou `data_pedido` a CTE, reexecutou com sucesso, apresentou os seis resultados corretos e recebeu nota definitiva **10/10**.

**EXPLAIN QUERY PLAN:** os dois filtros de data retornaram `SCAN pedidos` na base sem indice dedicado de data. A busca de `pedido_id = 'PED-0020'` retornou `SEARCH pedidos USING COVERING INDEX sqlite_autoindex_pedidos_1 (pedido_id=?)`. A busca por chave primaria utiliza o indice automatico. O filtro de datas por intervalo e mais favoravel a um futuro indice em `data_pedido`, mas **nenhuma melhoria de velocidade foi comprovada** no banco atual com 36 registros.

**Arquivo auxiliar:** `sql/11_plano.sql` permaneceu local, nao rastreado pelo Git, conforme `git status -sb` informado depois do push. Nao integrou o commit `b1ceb9b`.

**Seguranca e limites:** demonstracao didatica com dados sinteticos, sem dados reais nem IA integrada. Indices e benchmarks exigiriam avaliacao adicional com volume de dados maior e planos comparaveis.

**Progresso:** 11 de 12 exercicios aprovados na trilha SQL proposta; media **9,91/10**. Exercicio 12 ainda nao iniciado.
