# 🔗 Integração Frontend-Backend

Este documento detalha a integração entre o frontend **logistic-pulse-31-main** e o backend **gatekeeper-api** com agentes **CrewAI** especializados.

## 🏗️ Arquitetura de Integração

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│                     │    │                     │    │                     │
│  Frontend React     │◄──►│  Gatekeeper API     │◄──►│  CrewAI Agents      │
│  (logistic-pulse)   │    │  (FastAPI)          │    │  (Python)           │
│                     │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 🚀 Agente Especializado: FrontendLogisticsAgent

### Responsabilidades
- ✅ Processar mensagens do chat inteligente
- ✅ Converter queries em dados estruturados para React
- ✅ Interpretar intenções do usuário (documentos, entregas, jornadas)
- ✅ Fornecer respostas contextualizadas

### Localização
- **Agente:** `python-crewai/agents/frontend_logistics_agent.py`
- **Ferramentas:** `python-crewai/tools/frontend_integration_tool.py` 
- **API Routes:** `gatekeeper-api/app/routes/frontend.py`

## 📡 Endpoints da API

### Base URL: `http://localhost:8001/api/frontend`

### 📊 Dashboard
```http
GET /dashboard/kpis?user_id={user_id}
```
Retorna KPIs para o Dashboard component.

**Response:**
```json
{
  "success": true,
  "data": {
    "delivery_time_avg": "3.2 dias",
    "sla_compliance": "94.2%",
    "nps_score": "8.7",
    "incidents_count": 12,
    "trend_data": {
      "delivery_time": {"value": -0.3, "trend": "down"}
    }
  }
}
```

### 📄 Documentos
```http
GET /documents?type={type}&status={status}&client={client}
POST /documents/upload
GET /documents/{document_id}
```

**Tipos suportados:** `CTE`, `NF`, `BL`, `MANIFESTO`, `AWL`
**Status:** `Validado`, `Pendente Validação`, `Rejeitado`

### 🚚 Entregas  
```http
GET /deliveries?status={status}&client={client}
GET /deliveries/{delivery_id}
```

**Status:** `Em Trânsito`, `Entregue`, `Em Espera`, `Entrega Parcial`

### 🛣️ Jornadas
```http
GET /journeys?status={status}&client={client}
```

**Status:** `Em Trânsito`, `Entregue`, `Aguardando Documento`

### 💬 Chat Inteligente
```http
POST /chat/message
```

**Body:**
```json
{
  "message": "Consultar CT-e da carga ABC123",
  "user_context": {
    "name": "João Silva", 
    "company": "Mercosul Line",
    "role": "Operador Logístico"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Encontrei o CT-e solicitado!...",
    "action": "show_document",
    "ui_component": "DocumentDetailModal",
    "data": {...},
    "attachments": [...]
  }
}
```

## 🔧 Configuração do Frontend

### 1. Instalar dependências
```bash
cd logistic-pulse-31-main
npm install axios @tanstack/react-query
```

### 2. Configurar cliente API
```typescript
// src/lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8001/api/frontend',
  timeout: 10000,
});

export default api;
```

### 3. Hooks personalizados
```typescript
// src/hooks/useDocuments.ts
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';

export const useDocuments = (filters: DocumentFilters) => {
  return useQuery({
    queryKey: ['documents', filters],
    queryFn: async () => {
      const { data } = await api.get('/documents', { params: filters });
      return data;
    }
  });
};
```

### 4. Integração com Chat
```typescript
// src/components/chat/ChatContainer.tsx
const handleSendMessage = async (message: string) => {
  try {
    const response = await api.post('/chat/message', {
      message,
      user_context: userProfile
    });
    
    const { data } = response.data;
    
    // Processar resposta e executar ações
    if (data.action === 'show_document') {
      setSelectedDocument(data.data);
      setIsDetailModalOpen(true);
    }
    
    // Adicionar resposta ao chat
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      type: 'agent',
      content: data.message,
      timestamp: new Date(),
      attachments: data.attachments
    }]);
    
  } catch (error) {
    console.error('Erro no chat:', error);
  }
};
```

## 🛠️ Configuração do Backend

### 1. Instalar dependências
```bash
cd gatekeeper-api
pip install fastapi uvicorn python-multipart
```

### 2. Executar API
```bash
cd gatekeeper-api
python -m app.main
# API disponível em http://localhost:8001
```

### 3. Executar agentes CrewAI
```bash
cd python-crewai
python -m agents.frontend_logistics_agent
```

## 🚀 Fluxo de Integração Completo

### Exemplo: Busca de Documento via Chat

1. **Frontend:** Usuário digita "Consultar CT-e da carga ABC123"

2. **API Call:** 
```http
POST /api/frontend/chat/message
{
  "message": "Consultar CT-e da carga ABC123",
  "user_context": {...}
}
```

3. **Backend:** FrontendLogisticsAgent processa:
   - Identifica tipo: "CT-e"
   - Extrai identificador: "ABC123"
   - Busca documento na base de dados
   - Formata resposta para React

4. **Response:**
```json
{
  "message": "Encontrei o CT-e da carga ABC123!...",
  "action": "show_document", 
  "ui_component": "DocumentDetailModal",
  "data": {documento completo},
  "attachments": [...]
}
```

5. **Frontend:** Recebe resposta e:
   - Exibe mensagem no chat
   - Abre DocumentDetailModal automaticamente
   - Anexa arquivos para download

## 📋 Checklist de Implementação

### ✅ Backend
- [x] Agente FrontendLogisticsAgent criado
- [x] Ferramentas de integração implementadas  
- [x] Rotas da API criadas (/api/frontend/*)
- [x] Modelos Pydantic definidos
- [x] Handlers de erro configurados

### 🔄 Frontend (Próximos passos)
- [ ] Cliente API configurado
- [ ] React Query setup
- [ ] Hooks personalizados criados
- [ ] Componentes integrados com API
- [ ] Chat atualizado com processamento IA
- [ ] Estados de loading implementados
- [ ] Tratamento de erros adicionado

## 📊 Monitoramento

### Health Checks
```http
GET /api/frontend/health
GET /health  # Geral da API
```

### Logs
- Frontend: Console do navegador
- Backend: Logs do FastAPI/uvicorn
- Agentes: Logs do CrewAI

## 🔒 Segurança

### Autenticação
- Tokens JWT para autenticação
- Middleware de CORS configurado
- Validação de entrada via Pydantic

### Rate Limiting
```python
# Implementar rate limiting se necessário
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

## 🚀 Deploy

### Desenvolvimento
1. Backend: `python -m app.main` (porta 8001)
2. Frontend: `npm run dev` (porta 5173)

### Produção
- Backend: Docker + Kubernetes
- Frontend: Build estático (Nginx)
- Banco: MongoDB Atlas
- Monitoramento: Prometheus + Grafana

---

**⚡ Status:** Integração base implementada e pronta para uso
**📅 Última atualização:** Janeiro 2024
**👥 Desenvolvido por:** MIT Team + Claude Code