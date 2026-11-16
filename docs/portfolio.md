# Caio Siqueira — Portfólio de IA aplicada, dados e automação

[LinkedIn](https://www.linkedin.com/in/caio-siqueira-6b047020a/) · [GitHub](https://github.com/CSS703099)

Construo projetos para investigar problemas financeiros e operacionais, combinando cálculos verificáveis, integração de ferramentas e revisão humana. Minha experiência em logística e gestão orienta a escolha dos problemas.

## Comece por estes projetos

### 1. Financial Intelligence AI — conciliação de repasses

**Problema:** identificar e explicar diferenças de repasse em um marketplace fictício.

**Implementação:** Python, SQL, SQLite, Pandas e Streamlit. Gemini recebe evidências calculadas e produz parecer estruturado, validado antes da revisão humana e exportação.

**Evidência:** 36 pedidos sintéticos, 30 concluídos e 7 divergentes; 92 testes aprovados em [execução CI de 06/11/2026](https://github.com/CSS703099/financial-intelligence-ai/actions/runs/42299952406).

**Estado:** MVP local, integração Gemini implementada, sem hospedagem pública. Os testes usam simulações para o provedor.

[Projeto e instruções](https://github.com/CSS703099/financial-intelligence-ai)

### 2. Agente Trello com Gemini — organização de tarefas

**Problema:** transformar solicitações em consultas e ações sobre um quadro de tarefas.

**Implementação:** Python, Google ADK, Gemini e API do Trello; listagem, criação e movimentação por identificador.

**Evidência:** [registro de validação com Gemini e quadro real de laboratório](https://github.com/CSS703099/agente-trello-gemini/blob/main/evidencias/validacao.md), além de cinco testes locais documentados.

**Estado:** protótipo integrado. A confirmação é solicitada por instruções conversacionais; ainda não existe aprovação obrigatória validada na camada de ferramentas.

[Código](https://github.com/CSS703099/agente-trello-gemini)

### 3. Banco na Viagem — consultas com MCP

**Problema:** consultar contas, saldos e gastos no contexto de uma demonstração de planejamento de viagem.

**Implementação:** JavaScript, SDK MCP e validação de argumentos; transporte em memória no navegador e servidor STDIO. A seleção de ferramentas usa regras, sem LLM integrado.

**Evidência:** consultas documentadas sobre quatro contas e 21 movimentações fictícias em USD; testes de consultas, STDIO e roteamento no repositório.

[Demo](https://banco-na-viagem-caio.caio-loguslog.chatgpt.site/) · [Código](https://github.com/CSS703099/banco-na-viagem-mcp)

## Projetos complementares

| Projeto | Entrega e limite | Acesso |
|---|---|---|
| EcoTrip | Aplicação web estática com cálculo de emissões didáticas, testes e publicação GitHub Pages. Construção assistida por IA; sem IA em execução. | [Demo](https://css703099.github.io/ecotrip-calculadora/) · [Código](https://github.com/CSS703099/ecotrip-calculadora) |
| Detecção de anomalias | Notebook de classificação supervisionada de fraude. Random Forest selecionada na validação: 77 de 95 fraudes sinalizadas e 22 falsos alertas no teste salvo. Avaliação retrospectiva. | [Notebook e metodologia](https://github.com/CSS703099/deteccao-anomalias-transacoes) |
| Pedidos e entregas | Google Sheets V4.1 com filtros, custos e Apps Script de qualidade. 36 pedidos fictícios; execução da conferência pelo menu. | [Projeto](https://github.com/CSS703099/dashboard-pedidos-entregas-google-sheets) |
| Dashboard de vendas | Excel com fórmulas, filtros e indicadores de vendas e metas sobre 18 pedidos fictícios. | [Projeto](https://github.com/CSS703099/dashboard-vendas-excel) |
| Linha Clara | Prompt de atendimento e oito simulações documentadas; sem integração com pedidos reais. | [Projeto](https://github.com/CSS703099/dio-agente-atendimento-cliente) |
| Mentor de carreira | Prompt com entrevista em etapas e ensaios de dois perfis; não é aplicação hospedada. | [Projeto](https://github.com/CSS703099/ia-mentor-carreira-tech) |
| NotebookLM e MCP | Curadoria de fontes, estudo guiado e materiais gerados com IA; não é implementação de agente. | [Projeto](https://github.com/CSS703099/notebooklm-agentes-mcp) |
| Lab Natty or Not | Comparação de prompts para um boletim de repasses fictícios, com totais verificáveis. | [Projeto](https://github.com/CSS703099/lab-natty-or-not) |
| Saldo Claro | PRD de finanças pessoais e registro de interação com Lovable. O repositório contém o briefing e uma captura; não contém um aplicativo concluído. | [Projeto](https://github.com/CSS703099/dio-lab-vibe-coding-app-financas) |

## Experiência aplicada em operações

Em 2021, na Logus Serviços, estruturei o fechamento financeiro de entregadores com CSVs do Fleet, consulta ao cadastro via PROCV e consolidação com SOMASE no Excel. Conduzi a contratação da Transfeera para preparar pagamentos em lote.

Segundo meu relato do processo, após a implantação o fechamento e o lançamento passaram a ocorrer em até 30 minutos. A referência anterior de até 10 dias dizia respeito ao lançamento individual; os períodos têm escopos diferentes e não são usados para calcular uma redução percentual. Esse case é experiência de automação operacional com Excel, sem alegação de IA em produção.

## Formação

- Gestão de Investimentos e Mercado Financeiro — UniCesumar, concluído em agosto de 2026.
- Análise e Desenvolvimento de Sistemas — Estácio, conclusão prevista em junho de 2028.
- MBA em Análise de Dados e Processamento de Linguagem Natural — Unopar, em andamento.

Projetos de estudo não representam experiência profissional contratada com IA. Dados sintéticos e simulações estão identificados em cada entrega. Certificados de conclusão devem ser consultados em suas credenciais próprias.
