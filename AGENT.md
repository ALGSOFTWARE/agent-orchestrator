---
project_area: "AI Agents & Chat Integration"
context_focus: "High-level overview of AI agent architecture and chat migration plan"
status: "Updated with Chat Migration Plan"
key_technologies:
  - "CrewAI"
  - "FastAPI"
  - "React TypeScript"
  - "MongoDB"
last_updated: "2025-09-02"
---

# Arquitetura de Agentes de IA

Este documento fornece uma visão geral da arquitetura de agentes de IA no projeto. Para uma descrição detalhada de cada agente e suas funções, consulte `AGENTS.md`.

- **Orquestração:** Os agentes são gerenciados pela biblioteca `crewai` e definidos no diretório `python-crewai/agents`.
- **Agente Principal:** O agente orquestrador principal é o `mit_tracking_agent_v2.py`.
- **Interação com o Sistema:** Os agentes interagem com o resto do sistema principalmente através da API Gatekeeper, utilizando uma ferramenta GraphQL dedicada para buscar e manipular dados, como `Orders` e `DocumentFiles`.

---

# 🚀 Plano de Migração - Chat para "Chat Inteligente"

## 📊 Análise da Situação Atual

### Frontend Atual (frontend/)
- ✅ ChatInterface funcional com tipos de agentes
- ✅ Integração real com CrewAI
- ✅ Sistema de mensagens estruturado
- ✅ Suporte a diferentes tipos de agentes

### Frontend Novo (logistic-pulse-31-main/)
- ✅ Interface UI completa e moderna
- ✅ SmartMenu e MessageInterpreter avançados
- ❌ Usando dados mock
- ❌ FrontendLogisticsAgent mock

### Backend
- ✅ CrewAI Service implementado
- ✅ frontend_logistics_agent.py real
- ✅ Busca semântica disponível
- ❌ Endpoint /chat/message usando mock

## 🎯 Estratégia de Migração em 4 Fases

### Fase 1: Integrar CrewAI Service Real
```python
# 1. Substituir MockAgent por RealFrontendLogisticsAgent
# 2. Ativar comunicação com python-crewai microservice  
# 3. Manter fallback para MessageInterpreter local
```

### Fase 2: Implementar Busca Semântica Real
```python
# 1. Integrar vector_search_service no chat
# 2. Conectar com DocumentFile collection real
# 3. Retornar documentos reais como anexos
```

### Fase 3: Migrar UI Components
```typescript
# 1. Melhorar ChatMessages com formatação do frontend atual
# 2. Adicionar AgentSelector ao SmartMenu
# 3. Integrar métricas reais no ChatHeader
```

### Fase 4: Funcionalidades Avançadas
```typescript
# 1. Upload de documentos via chat
# 2. Comandos de voz (opcional)
# 3. Histórico persistente de conversas
```

## 🔧 Implementação Detalhada

### Arquitetura de Integração

**Backend (gatekeeper-api)**:
```python
# Fluxo: Frontend → Gatekeeper API → CrewAI Service → Frontend Agent
POST /chat/message → CrewAIService.send_message_to_agent() → python-crewai/agents/frontend_logistics_agent.py
```

**CrewAI Agent**:
```python
# frontend_logistics_agent.py processará:
1. Interpretação de intenções (document_search, status_check, help)
2. Busca semântica em DocumentFile collection
3. Formatação de respostas com anexos reais
4. Ações específicas (show_document, open_modal)
```

**Frontend Response**:
```typescript
interface ChatResponse {
  message: string;
  action?: "show_document" | "open_modal" | "download_file";
  attachments?: DocumentAttachment[];
  data?: any; // Para modal de detalhes
}
```

### Fluxo de Comunicação Completo

```
Usuario digita → ChatInput → MessageInterpreter local → POST /chat/message → 
CrewAI Service → Frontend Logistics Agent → Vector Search → DocumentFile MongoDB → 
Resposta com anexos → ChatMessages renderiza → DocumentModal se necessário
```

## 🚀 Benefícios da Migração

### Para o Usuário:
- ✅ Chat inteligente real com IA treinada
- ✅ Busca semântica de documentos
- ✅ Interface moderna e intuitiva
- ✅ Ações guiadas no SmartMenu
- ✅ Download/visualização real de arquivos

### Para o Sistema:
- ✅ Integração completa frontend ↔ backend
- ✅ Uso do CrewAI especializado  
- ✅ Busca vetorial em documentos reais
- ✅ Arquitetura escalável e extensível

## 📋 Próximos Passos Recomendados

1. **Primeiro**: Implementar RealFrontendLogisticsAgent no backend
2. **Segundo**: Testar comunicação CrewAI ↔ Gatekeeper API
3. **Terceiro**: Integrar busca semântica real
4. **Quarto**: Migrar componentes UI do frontend atual  
5. **Quinto**: Testar fluxo completo end-to-end

## 🎯 Status de Implementação

- [x] Análise de código existente
- [x] Plano de migração definido
- [ ] Fase 1: CrewAI Service Real
- [ ] Fase 2: Busca Semântica
- [ ] Fase 3: UI Components
- [ ] Fase 4: Funcionalidades Avançadas
