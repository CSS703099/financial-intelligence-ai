# Financial Intelligence AI — Finanças & Automação

## Estado atual — MVP offline V1.5 (02/11/2026)

**Status:** MVP offline validado em testes automatizados e revisado visualmente.

### Funcionalidades

- Conciliação financeira de pedidos sintéticos com SQLite e Pandas.
- Dashboard Streamlit com filtros, indicadores, gráficos e exportação CSV.
- Simulador determinístico de inadimplência 30+ e 90+.
- Estrutura de IA explicável com evidências, validação e revisão humana.
- Demonstração offline de pareceres manuais para crédito e repasses.
- Exportação JSON condicionada à aprovação humana.
- Rastreabilidade com hash SHA-256 do dossiê.

### Qualidade e testes

Em 02/11/2026, a suíte local apresentou **62 testes aprovados, 1 XFAIL esperado e nenhuma falha inesperada**.

O XFAIL documenta uma limitação conhecida: o validador não detecta todas as contradições semânticas.

### Limites da versão

O projeto usa exclusivamente dados sintéticos e é independente do iFood.

Os pareceres da demonstração offline são exemplos escritos manualmente, não produzidos por inteligência artificial.

A chamada à OpenAI está implementada em código, mas sua operação real ainda não foi validada com sucesso. A hospedagem privada também está pendente.

Nenhuma análise executa decisões financeiras automaticamente.

### Executar localmente

```powershell
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m streamlit run app.py
```

As seções seguintes preservam o histórico técnico das etapas SQL e Python.

Projeto independente de portfólio, desenvolvido com exercícios progressivos em SQL, Python e SQLite. Objetivo futuro: aplicar IA a análises financeiras e à automação de relatórios.

> **Transparência:** base inteiramente **sintética**, sem dados internos ou vínculo de desenvolvimento com o iFood. **Ainda não há IA integrada nesta versão.** Os resultados são simulações, não resultados de produção.

## Progresso — Dia 1

| Etapa | Situação | Evidência |
|---|---|---|
| Ambiente Python e VS Code | Concluído | Banco criado no computador do aluno |
| SQLite | Concluído | 36 registros sintéticos |
| Exploração | Concluído | `sql/00_exploracao.sql` |
| Exercício 01 — indicadores | Aprovado 9/10 | `sql/01_exercicio.sql` |
| Exercício 02 — conciliação | Aprovado 10/10 | `sql/02_exercicio.sql` |
| Exercício 03 — análise por restaurante | Aprovado 10/10 | `sql/03_exercicio.sql` |
| Exercício 04 — CTE e prioridade | Aprovado 10/10 | `sql/04_exercicio.sql` |
| Exercício 05 — evolução mensal e `LAG()` | Aprovado 10/10 | `sql/05_exercicio.sql` |
| Exercício 06 — ranking e Pareto | Aprovado 10/10 | `sql/06_exercicio.sql` |
| Exercício 07 — detecção por regras e alertas | Aprovado 10/10 | `sql/07_exercicio.sql` |
| Exercício 08 — painel executivo de risco | Aprovado 10/10 | `sql/08_exercicio.sql` |
| Exercício 09 — controles de qualidade e integridade | Aprovado 10/10 | `sql/09_exercicio.sql` |
| Exercício 10 — comparação parametrizável de períodos | Aprovado 10/10 | `sql/10_exercicio.sql` |
| Exercício 11 — validação de equivalência e planos SQL | Aprovado 10/10 | `sql/11_exercicio.sql` |
| Exercício 12 — projeto integrador e auditoria final | Aprovado 10/10 | `sql/12_exercicio.sql` e `sql/12_auditoria.sql` |

**Etapa SQL inicial encerrada em 2026-11-01:** **12 de 12 exercícios aprovados**, média final **9,92/10** (11 exercícios com nota 10 e o exercício 01 com nota 9). Código SQL e auditoria final publicados no repositório privado.

## Sprint MVP — iFood GenAI (novembro/2026)

**Objetivo:** preparar até **12/11/2026** uma demonstração funcional de portfólio para a candidatura pretendida até **13/11/2026** (prazo informado: **17/11/2026**). Datas de planejamento, não promessa de implantação. O projeto é **independente**, não utiliza dados ou sistemas internos do iFood.

| Entrega do sprint | Situação | Evidência |
|---|---|---|
| SQL — 12 exercícios e auditoria | Concluído | `sql/12_exercicio.sql`, `sql/12_auditoria.sql` |
| Python 01 — indicadores via SQLite | **Aprovado 10/10 e publicado** | `scripts/indicadores_financeiros.py` |
| Python 02 — Pandas e testes automatizados | **Aprovado 10/10 e publicado** | `scripts/analise_pandas.py`, `tests/test_analise_pandas.py`, `requirements-mvp.txt` |
| Python 03 — Dashboard Streamlit | **Aprovado 10/10 e publicado** | `app.py`, `scripts/dashboard_dados.py`, `tests/test_dashboard.py`, `.streamlit/config.toml` |
| Python 04 — Simulador de crédito 30+/90+ | **Aprovado 10/10 e publicado** | `scripts/simulador_credito.py`, `tests/test_simulador_credito.py`, `tests/test_simulador_ui.py`, `app.py` |
| IA generativa com avaliação e revisão humana | Planejado, dependente de testes | Ainda não implementada |
| Demonstração privada | Planejada, sujeita a autorização | Ainda não hospedada |

**Python 01:** função `obter_indicadores()` abre o SQLite em modo somente leitura, executa uma consulta SQL parametrizada pelo estado do banco (sem entrada de parâmetros externos), recupera uma linha com `fetchone()` e devolve um dicionário. **11 de 11 indicadores conferidos** no dataset sintético: 36 pedidos, 30 concluídos, 6 cancelados, faturamento bruto R$ 4.687,60, taxas da plataforma R$ 609,40, taxas logísticas R$ 235,50, repasses R$ 3.820,60, 7 divergentes, diferença líquida R$ 22,10, soma absoluta R$ 38,10 e taxa 23,33%.

**Limitações e melhorias programadas:** os indicadores não abrangem filtros interativos; em base sem pedidos, agregações `SUM()` podem retornar `NULL`; tratar exceções específicas e devolver código de saída diferente de zero em caso de falha; preparar testes de regressão antes do dashboard.

**Python 02:** leitura da tabela `pedidos` via `pd.read_sql_query()` em conexão SQLite somente leitura; implementação independente dos mesmos **11 indicadores** com operações de Pandas em centavos inteiros; separação das funções `carregar_pedidos()` e `calcular_indicadores()`; preservação do DataFrame de entrada; taxa `None` quando não há pedidos concluídos. **5 testes `pytest` passaram** na execução local informada pelo aluno: equivalência SQL/Pandas, base vazia, cenário sem divergências, banco inexistente e preservação do DataFrame. Os **11 indicadores** batem com o CSV sintético original; etapa aprovada **10/10** e publicada no commit `3725d9a`.

**Melhorias para o MVP:** adicionar testes com valores fixos de referência para o CSV, testar falhas com encerramento não zero, validar dados ausentes e tipos monetários antes da interface, além de preparar filtros interativos por período/restaurante.

**Python 04 — Simulador de crédito 30+/90+:** simulação determinística de sensibilidade com carteira **hipotética independente** dos pedidos de conciliação. Permite editar saldos da carteira, 30+ e 90+, alterar taxas em **pontos percentuais**, comparar saldos base/cenário lado a lado (`st.bar_chart(..., stack=False)`) e obter nível de alerta com justificativa e ação para **revisão humana**, por regras didáticas. Validação `0 ≤ 90+ ≤ 30+ ≤ carteira` tanto na base quanto no cenário, com `Decimal` e arredondamento monetário. O módulo **não treina modelo, não prevê inadimplência, não usa IA generativa e não executa decisões de crédito**.

**Evidências Python 04:** commit **`5fa74ed`** publicado na branch `main`, contendo `app.py`, `scripts/simulador_credito.py`, `tests/test_simulador_credito.py` e `tests/test_simulador_ui.py`. O aluno reportou `python -m py_compile app.py` sem erros, `pytest -v` com **28 testes aprovados em 4,73 s** e Streamlit inicializado em `127.0.0.1:8501`. Os dois testes individuais cobrem a igualdade limite 90+ = 30+ e a preservação dos indicadores de conciliação após tentativa de cenário inválido. **Nota final: 10/10.** A correção de indentação do gráfico foi validada pelos testes; a disposição visual pós-correção ainda merece conferência manual.

**Python 03:** dashboard **Streamlit 1.66.1** executado localmente pelo aluno, com filtro inclusivo por período e seleção de restaurantes, cartões financeiros, gráficos de impacto por restaurante e evolução mensal, conciliação por pedido, priorização por regras didáticas e exportação CSV. O painel reutiliza `carregar_pedidos()` e `calcular_indicadores()`; os arquivos `app.py`, `scripts/dashboard_dados.py`, `tests/test_dashboard.py`, `.streamlit/config.toml` e `requirements-mvp.txt` foram publicados no commit **`a192aa9`**, após `git rebase origin/main` e `git push origin main`. **7/7 testes novos e 12/12 testes no total** passaram na execução local informada pelo aluno; a interface foi exibida em `127.0.0.1:8501`, não hospedada externamente. **Avaliação: 10/10.** A conferência manual completa de exportação e filtros adicionais permanece recomendada para a demonstração. **Não há IA integrada.**

## Problema de negócio

Em um marketplace fictício, analisar os pedidos efetivamente concluídos, as taxas e os repasses. Modelo de teste:

```text
repasse_esperado = valor_bruto - taxa_plataforma - taxa_logistica
divergencia = repasse_esperado - repasse_real
```

Divergência positiva indica que o repasse realizado ficou abaixo do esperado pelo **modelo simplificado**. A divergência não comprova fraude ou prejuízo. Repasse não equivale a lucro.

## Resultados validados com a base sintética

- **36** pedidos na base; **30** concluídos.
- **R$ 4.687,60** de valor bruto dos pedidos concluídos.
- **R$ 609,40** em taxas da plataforma; **R$ 235,50** em taxas logísticas.
- **R$ 3.820,60** em repasses registrados.
- **7** pedidos com diferenças; divergência líquida assinada de **R$ 22,10**.
- Soma absoluta das diferenças: **R$ 38,10**.
- **Exercício 03:** Restaurante B lidera em divergências absolutas (R$ 27,40), seguido de A (R$ 6,20) e C (R$ 4,50).
- **Exercício 04:** taxas de divergência por restaurante: B 41,67% (Alta), A 16,67% (Media), C 8,33% (Baixa). Classificação exclusivamente didática.
- **Exercício 05:** setembro/2026 — 18 pedidos, 4 divergentes, taxa de 22,22%, R$ 24,40 absolutos; outubro/2026 — 12 pedidos, 3 divergentes, taxa de 25,00%, R$ 13,70 absolutos. A taxa aumentou **2,78 pontos percentuais**; o valor absoluto das diferenças diminuiu.
- **Exercício 06:** ranking de 7 pedidos divergentes; os 5 de maior magnitude somam **R$ 32,60**, ou **85,56%** do total absoluto de **R$ 38,10** (análise de Pareto didática).
- **Exercício 07:** 7 alertas gerados por regras explicáveis: **2 Critico, 4 Alto e 1 Moderado**; 5 divergências positivas e 2 negativas. A classificação considera impacto absoluto e recorrência do restaurante.
- **Exercício 08:** painel executivo por restaurante com `LEFT JOIN`, `COALESCE` e indicadores agregados. Restaurante B: **41,67%** dos pedidos divergentes, **R$ 27,40** absolutos e **71,92%** do impacto total (prioridade didática `Critico`); Restaurante A: **R$ 6,20** (`Alto`); Restaurante C: **R$ 4,50** (`Moderado`).
- **Exercício 09:** seis controles de integridade e financeiro com `UNION ALL`, CTEs e `CASE WHEN`: **5 OK**, **0 Falha** e **1 Revisar** (7 divergências de repasse). As ocorrências financeiras não são tratadas automaticamente como erros de qualidade.
- **Exercício 10:** comparação de setembro/2026 (**18** pedidos concluídos; **4** divergentes; **22,22%**; **R$ 24,40** absolutos) e outubro/2026 (**12** concluídos; **3** divergentes; **25,00%**; **R$ 13,70** absolutos), com **+2,78 p.p.** de variação. Utiliza CTE de parâmetros, `LEFT JOIN`, `COALESCE`, `NULLIF` e `LAG()`; preserva intervalos sem pedidos.
- **Exercício 11:** validação de equivalência entre filtro mensal com `SUBSTR` e filtro por intervalo de datas. **6 combinações** mês/restaurante retornaram `OK`, totalizando **30** pedidos concluídos, **7** divergências e **R$ 38,10** absolutos. Planos didáticos do SQLite: `SCAN pedidos` nos filtros de data e `SEARCH ... USING COVERING INDEX sqlite_autoindex_pedidos_1` na busca pela chave primária. **Não foi comprovado ganho de velocidade** na base pequena.
- **Exercício 12:** relatório integrador com **6 agrupamentos** mês/restaurante, ranking de impacto, taxa, divergência líquida e absoluta, participação, prioridade e ação sugerida. Maior impacto: **Restaurante B em setembro (R$ 19,90; 52,23% do impacto total; prioridade `Critico`)**. No agregado, Restaurante B concentra **R$ 27,40 (71,92%)**. A auditoria independente validou **8 de 8 controles `OK`**, incluindo 36 pedidos, 30 concluídos, 6 cancelados, 7 divergentes, R$ 22,10 líquidos e R$ 38,10 absolutos. Projeto final aprovado **10/10**.

## Como executar

Requisitos: Python para os scripts SQL/SQLite sem dependências externas; para a **fase MVP com Pandas/Pytest**, usar Python **3.13** e instalar as dependências listadas em `requirements-mvp.txt`.

No terminal, aberto na raiz deste repositório:

```powershell
py -3.13 scripts/criar_banco.py
py -3.13 scripts/executar_sql.py sql/00_exploracao.sql
py -3.13 scripts/executar_sql.py sql/01_exercicio.sql
py -3.13 scripts/executar_sql.py sql/02_exercicio.sql
py -3.13 scripts/executar_sql.py sql/03_exercicio.sql
py -3.13 scripts/executar_sql.py sql/04_exercicio.sql
py -3.13 scripts/executar_sql.py sql/05_exercicio.sql
py -3.13 scripts/executar_sql.py sql/06_exercicio.sql
py -3.13 scripts/executar_sql.py sql/07_exercicio.sql
py -3.13 scripts/executar_sql.py sql/08_exercicio.sql
py -3.13 scripts/executar_sql.py sql/09_exercicio.sql
py -3.13 scripts/executar_sql.py sql/10_exercicio.sql
py -3.13 scripts/executar_sql.py sql/11_exercicio.sql
py -3.13 scripts/executar_sql.py sql/12_exercicio.sql
py -3.13 scripts/executar_sql.py sql/12_auditoria.sql
py -3.13 scripts/indicadores_financeiros.py
```

Para as dependências e testes do sprint MVP no Windows (Python 3.13):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-mvp.txt
.\.venv\Scripts\python.exe scripts/analise_pandas.py
.\.venv\Scripts\python.exe -m pytest tests/test_analise_pandas.py -v
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501
```

Se não utiliza o Python Launcher do Windows, substitua `py -3.13` por `python`.

O banco `financial_intelligence.db` é gerado localmente e está no `.gitignore`.

## Estrutura

```text
dados/pedidos_sinteticos.csv
scripts/criar_banco.py
scripts/executar_sql.py
sql/00_exploracao.sql
sql/01_exercicio.sql
sql/02_exercicio.sql
sql/03_exercicio.sql
sql/04_exercicio.sql
sql/05_exercicio.sql
sql/06_exercicio.sql
sql/07_exercicio.sql
sql/08_exercicio.sql
sql/09_exercicio.sql
sql/10_exercicio.sql
sql/11_exercicio.sql
sql/12_exercicio.sql
sql/12_auditoria.sql
scripts/indicadores_financeiros.py
scripts/analise_pandas.py
scripts/dashboard_dados.py
scripts/simulador_credito.py
app.py
tests/test_analise_pandas.py
tests/test_dashboard.py
tests/test_simulador_credito.py
tests/test_simulador_ui.py
.streamlit/config.toml
requirements-mvp.txt
docs/diario_de_bordo.md
.gitignore
```

## Próximas etapas

**Formação inicial de SQL concluída; Python 01, 02, 03 e 04 aprovados e publicados.** O **dashboard Streamlit e o simulador de crédito funcionam localmente**, sem hospedagem remota. Próxima entrega: **Python 05 — integração e avaliação de IA generativa explicável**, com dados sintéticos, validação das saídas e revisão humana. **IA generativa e implantação privada ainda não foram implementadas.** Para uso profissional, ampliar testes de borda (inclusive ausência total de divergências), padronizar arredondamento por pedido e substituir valores esperados fixos por validações adequadas ao dataset em produção.

## Segurança

Nunca publique tokens, senhas, chaves de API nem dados reais de clientes. Para métricas financeiras, mantenha os cálculos verificáveis em SQL/Python e use LLMs para auxiliar a interpretação, com testes e revisão humana.
