# Diario de bordo — Financial Intelligence AI

## Dia 1 — 2026-11-01 (registro das entregas)

**Contexto:** treinamento individual para construcao de portfolio em Dados, Financas e IA aplicada a negocios. Projeto independente, com dados 100% sinteticos, sem vinculo de desenvolvimento com o iFood.

### Etapas verificadas
- [x] Python 3.13 e VS Code instalados.
- [x] Banco SQLite criado com 36 pedidos ficticios.
- [x] Consulta exploratoria: 10 registros retornados.
- [x] Exercicio 01 — Indicadores financeiros, nota **9/10**.
- [x] Exercicio 02 — Conciliacao financeira, nota **10/10**.

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
Exercicio 03 — ainda nao iniciado. Aguardar resolucao e correcao antes de registrar como concluido.

### Validacao do ambiente Git / GitHub — 2026-11-01

- [x] Git for Windows 2.56.0.windows.4 instalado e validado com `git --version`.
- [x] Repositorio privado `CSS703099/financial-intelligence-ai` clonado na pasta `financial-intelligence-ai`.
- [x] Pasta inicial `Financial_Intelligence_AI` preservada como backup.
- [x] `git status`: branch `main`, sem alteracoes locais pendentes, sincronizada com `origin/main` no momento do teste.
- [x] `py -3.13 scripts/criar_banco.py`: banco criado com 36 registros ficticios.
- [x] `py -3.13 scripts/executar_sql.py sql/01_exercicio.sql`: 30 pedidos concluidos; R$ 4.687,60 de valor bruto; R$ 609,40 de taxas da plataforma; R$ 235,50 de taxas logisticas; R$ 3.820,60 em repasses realizados.
- [x] `py -3.13 scripts/executar_sql.py sql/02_exercicio.sql`: 7 pedidos divergentes, de PED-0003 a PED-0035.

**Resultado:** configuracao local de Git, clonagem, geracao de dados e execucao dos dois exercicios validadas pelo usuario no terminal PowerShell. Exercicio 03 continua **nao iniciado**.

**Sincronizacao:** o registro acima foi adicionado pelo assistente diretamente no GitHub; executar `git pull --ff-only` na pasta clonada para baixar este novo commit antes de editar.
