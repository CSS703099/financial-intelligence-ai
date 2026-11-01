# Financial Intelligence AI — Finanças & Automação

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

## Como executar

Requisitos: Python **3.9+**, sem dependências externas.

No terminal, aberto na raiz deste repositório:

```powershell
py -3.13 scripts/criar_banco.py
py -3.13 scripts/executar_sql.py sql/00_exploracao.sql
py -3.13 scripts/executar_sql.py sql/01_exercicio.sql
py -3.13 scripts/executar_sql.py sql/02_exercicio.sql
py -3.13 scripts/executar_sql.py sql/03_exercicio.sql
py -3.13 scripts/executar_sql.py sql/04_exercicio.sql
py -3.13 scripts/executar_sql.py sql/05_exercicio.sql
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
docs/diario_de_bordo.md
.gitignore
```

## Próximas etapas

Consolidação SQL, testes, Python/Pandas, interface interativa, prompts avaliados, integração de API e automações de IA. Funcionalidades futuras não devem ser apresentadas como já implementadas.

## Segurança

Nunca publique tokens, senhas, chaves de API nem dados reais de clientes. Para métricas financeiras, mantenha os cálculos verificáveis em SQL/Python e use LLMs para auxiliar a interpretação, com testes e revisão humana.
