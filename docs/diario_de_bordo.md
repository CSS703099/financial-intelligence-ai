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
Exercicios 01 a 05 concluidos e aprovados. Exercicio 06 ainda nao iniciado.

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

**Resultado:** Exercicio 05 aprovado e publicado. Exercicio 06 nao iniciado. Todas as metricas sao de dados ficticios, e divergencias nao significam fraude ou erro confirmado.
