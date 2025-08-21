---
project_area: "AI Agents"
context_focus: "High-level overview of AI agent architecture"
status: "Updated"
key_technologies:
  - "CrewAI"
last_updated: "2025-08-19"
---

# Arquitetura de Agentes de IA

Este documento fornece uma visão geral da arquitetura de agentes de IA no projeto. Para uma descrição detalhada de cada agente e suas funções, consulte `AGENTS.md`.

- **Orquestração:** Os agentes são gerenciados pela biblioteca `crewai` e definidos no diretório `python-crewai/agents`.
- **Agente Principal:** O agente orquestrador principal é o `mit_tracking_agent_v2.py`.
- **Interação com o Sistema:** Os agentes interagem com o resto do sistema principalmente através da API Gatekeeper, utilizando uma ferramenta GraphQL dedicada para buscar e manipular dados, como `Orders` e `DocumentFiles`.
