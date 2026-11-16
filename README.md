# Financial Intelligence AI
### Conciliação de repasses com evidências, IA generativa e revisão humana

MVP de portfólio para investigar diferenças entre o repasse esperado e o repasse registrado de pedidos de um marketplace fictício. **Python e SQL calculam os valores; Gemini redige um parecer a partir dessas evidências.**

**Autor:** Caio Siqueira · [LinkedIn](https://www.linkedin.com/in/caio-siqueira-6b047020a/) · [GitHub](https://github.com/CSS703099)

> Projeto independente, com dados exclusivamente sintéticos. Não tem vínculo nem integração com sistemas internos do iFood. A aplicação foi demonstrada localmente e ainda não tem hospedagem pública.

## O que está implementado

- Dashboard Streamlit com filtros por período e restaurante, indicadores, gráficos, conciliação por pedido e exportação CSV.
- Cálculos em Python/Pandas e consultas SQL sobre SQLite; separação entre divergência líquida e soma absoluta das diferenças.
- Integração com a API Gemini, saída JSON estruturada e validação das referências às evidências.
- Revisão humana antes da exportação do parecer; mudanças no conteúdo ou no revisor invalidam a aprovação da sessão.
- Exportação JSON com hashes SHA-256 para comparação de integridade.
- Modo offline com exemplos manuais claramente separado da geração real por IA.
- Módulo adicional de simulação determinística de crédito 30+/90+, sem previsão estatística nem decisão automática.

## Resultado reproduzível da demonstração

| Indicador | Base sintética |
|---|---:|
| Pedidos totais | 36 |
| Pedidos concluídos | 30 |
| Pedidos com divergência | 7 |
| Taxa de divergência entre concluídos | 23,33% |
| Divergência líquida | R$ 22,10 |
| Soma absoluta das divergências | R$ 38,10 |

```text
repasse_esperado = valor_bruto - taxa_plataforma - taxa_logistica
divergencia = repasse_esperado - repasse_real
```

Diferença positiva indica pagamento abaixo do esperado pelo modelo simplificado. Não comprova fraude, prejuízo nem causa do desvio. Repasse não equivale a lucro.

## Validação

**92 testes aprovados no GitHub Actions em 06/11/2026**, execução [42299952406](https://github.com/CSS703099/financial-intelligence-ai/actions/runs/42299952406), commit `42bc5e7edcda54371de2c60c0f9907272623c6b0`.

A suíte cobre cálculos, cenários de crédito, validação do parecer, aprovação e componentes da interface. Os testes de IA usam clientes simulados: uma execução verde não comprova disponibilidade da API Gemini nem hospedagem pública.

[Consultar execuções mais recentes](https://github.com/CSS703099/financial-intelligence-ai/actions)

## Executar no Windows

Requer Python 3.13. Abra o terminal na raiz do repositório:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-mvp.txt
.\.venv\Scripts\python.exe scripts/criar_banco.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**A criação do banco é necessária no primeiro uso:** o SQLite não é versionado. O comando `criar_banco.py` recria a tabela de demonstração; use apenas o banco sintético deste projeto.

Para gerar um parecer real, configure `GEMINI_API_KEY` no ambiente local. O modelo é configurável por `GEMINI_MODEL`. Não coloque chaves no código, em commits ou em capturas. O modo offline permite explorar os exemplos sem chamar o provedor. A API pode consumir cota ou gerar custos conforme a conta.

Em Linux/macOS, use `python3 -m venv .venv` e substitua o executável dos comandos por `./.venv/bin/python`.

## Roteiro de demonstração

1. Abra a conciliação e confira os 36 pedidos / 30 concluídos sem filtros.
2. Filtre por restaurante e período e examine os pedidos divergentes.
3. Confira o cálculo de um pedido e os indicadores agregados.
4. Na área de parecer, gere a análise Gemini ou selecione o exemplo offline, identificando qual modo está em uso.
5. Revise o conteúdo, registre o revisor e exporte o JSON.
6. Altere o parecer ou a confirmação para demonstrar a invalidação da aprovação.

## Arquitetura e código

| Responsabilidade | Arquivo |
|---|---|
| Interface | [app.py](app.py) |
| Preparação do banco | [scripts/criar_banco.py](scripts/criar_banco.py) |
| Indicadores Pandas | [scripts/analise_pandas.py](scripts/analise_pandas.py) |
| Contexto, integração e validação de IA | [scripts/ia_explicavel.py](scripts/ia_explicavel.py) |
| Interação e revisão do parecer | [scripts/ia_streamlit.py](scripts/ia_streamlit.py) |
| Testes automatizados | [tests/](tests/) |
| Consultas e auditoria SQL | [sql/](sql/) |

[Guia de leitura do código](docs/guia_para_iniciantes.md) · [Histórico de aprendizagem e versões](docs/historico_portfolio.md)

## Limitações e próximos passos

- Publicar uma demonstração acessível e uma gravação curta de um mesmo caso de repasse, do cálculo à exportação.
- Registrar avaliação da geração real com entradas normais, ambíguas e inválidas, além de custos e latência.
- A validação restringe formato e inconsistências conhecidas; não garante veracidade semântica completa.
- Aprovação em sessão e hashes não são autenticação, assinatura digital nem trilha de auditoria inviolável.
- O protótipo não executa operações financeiras e não está preparado para produção.
- Houve relato histórico de erro intermitente de renderização no Chrome; a causa definitiva não foi estabelecida. Revalidar o fluxo visual no ambiente da demonstração.
