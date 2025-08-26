---
project_area: "AI Agents"
context_focus: "Detailed description of specific AI agents and their roles"
status: "Updated"
key_technologies:
  - "CrewAI"
  - "FastAPI"
  - "GraphQL"
  - "Sentence-Transformers"
last_updated: "2025-08-19"
---

# Agentes de IA no Projeto MIT Logistics

Este documento descreve a arquitetura e o funcionamento dos agentes de IA dentro do ecossistema MIT Logistics.

## Visão Geral e Arquitetura Centrada em `Order`

O sistema evoluiu para uma arquitetura centrada na entidade `Order` (Pedido). Uma `Order` atua como um contêiner para todas as informações e documentos relacionados a uma operação logística específica. Os agentes de IA agora operam com este conceito central.

O fluxo de trabalho da IA, baseado em `crewai`, permanece, mas agora está focado em interagir com as `Orders`.

## Agente Principal: MIT Tracking Agent v2.0

Localizado em `python-crewai/agents/mit_tracking_agent_v2.py`.

### Responsabilidades:

1.  **Orquestração Focada em `Order`:** Recebe tarefas complexas (ex: "Na `Order` XYZ, analise o CT-e e o BL e me diga se há discrepâncias de peso") e as decompõe em passos.
2.  **Delegação:** Atribui cada passo a um agente especializado.
3.  **Síntese:** Coleta os resultados e formula uma resposta final no contexto da `Order`.

### Ferramentas Principais:

- **`gatekeeper_api_tool`**: A ferramenta mais importante. Usa GraphQL para interagir com a `gatekeeper-api` e realizar operações CRUD em `Orders` e `DocumentFiles`.
- **`logistics_tools`**: Ferramentas para consultar APIs externas de logística.

## Agentes Especializados

Localizados em `python-crewai/agents/specialized_agents.py`.

### 1. `DocumentAnalysisAgent` (Novo)

- **Foco:** Análise de conteúdo de documentos dentro de uma `Order`.
- **Ferramentas:** `gatekeeper_api_tool` para buscar `DocumentFiles` e seu `text_content` extraído.
- **Exemplo de Tarefa:** "Leia o PDF do CT-e na `Order` 123 e extraia o nome do remetente."

### 2. `SemanticSearchAgent` (Novo)

- **Foco:** Realizar buscas inteligentes nos documentos do sistema.
- **Ferramentas:** `gatekeeper_api_tool` para acessar o novo endpoint `/orders/search`.
- **Exemplo de Tarefa:** "Encontre todos os documentos que mencionam 'carga perigosa' relacionados a 'Porto de Santos'."

### 3. `LogisticsAgent`

- **Foco:** Tarefas operacionais de logística externa.
- **Ferramentas:** `logistics_tools`.
- **Exemplo de Tarefa:** "Rastrear o contêiner MSKU1234567."

## Fluxo de Processamento de Documentos (Upload e Embedding)

A interação dos agentes com os documentos agora depende de um processo assíncrono:

1.  **Upload:** Um usuário faz o upload de um arquivo através da interface em `/documents`. A `gatekeeper-api` o associa a uma `Order` e o salva no S3.
2.  **Marcação:** O `DocumentFile` é criado no banco de dados com o status `"processing"`.
3.  **Fila de Processamento:** Uma tarefa em segundo plano é acionada.
4.  **Extração e Embedding:** O `DocumentProcessorService` na `gatekeeper-api`:
    - Extrai o texto do arquivo (usando OCR para imagens/PDFs escaneados).
    - Gera um vetor de embedding a partir do texto usando um modelo `sentence-transformers`.
    - Salva o texto extraído e o vetor no `DocumentFile` correspondente.
5.  **Indexação:** O status do documento é atualizado para `"indexed"`.

A partir deste ponto, o `DocumentAnalysisAgent` pode ler o `text_content` e o `SemanticSearchAgent` pode realizar buscas vetoriais nos embeddings.