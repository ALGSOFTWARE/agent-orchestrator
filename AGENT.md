# MIT Tracking Project

MIT Tracking é um agente conversacional especializado em consultas logísticas, desenvolvido com CrewAI, LangChain e integração com OpenAI e Google Gemini via roteamento inteligente. O sistema é focado em CT-e (Conhecimento de Transporte Eletrônico), rastreamento de containers e documentos de transporte.

## Architecture & Stack

- **Runtime**: Node.js 22+ with ES Modules
- **Language**: TypeScript (strict mode)
- **AI Framework**: CrewAI + LangChain
- **LLM**: OpenAI (GPT-3.5-turbo, GPT-4) + Google Gemini (Pro) com roteamento inteligente
- **Database**: MongoDB + Beanie ODM (Python) para persistência
- **Testing**: Jest with TypeScript support
- **Containerization**: Docker
- **Build Tool**: TypeScript Compiler (tsc) + tsx for development

## Project Structure

```
MIT/
├── frontend/                       # Next.js 14 React Dashboard
│   ├── src/app/                   # App Router (pages)
│   ├── src/components/            # UI components & features
│   ├── src/lib/                   # API clients, store, utils
│   ├── src/styles/                # CSS Modules & global styles
│   └── package.json              # Frontend dependencies
├── gatekeeper-api/                # Authentication & Routing API
│   ├── app/
│   │   ├── database.py            # MongoDB connection & config
│   │   ├── models.py              # Database models & schemas
│   │   ├── routes/                # API endpoints
│   │   └── services/              # Business logic services
│   └── requirements.txt           # Python dependencies
├── python-crewai/                 # CrewAI Agents Backend
│   ├── api/                       # GraphQL API server
│   ├── agents/                    # Specialized AI agents
│   ├── models/                    # Database models (Beanie ODM)
│   ├── tools/                     # Logistics tools
│   └── requirements.txt           # Python dependencies
├── .env                           # Environment variables
├── start-system.sh                # System startup script
└── CLAUDE.md                      # This documentation
```

## Build & Development Commands

### System Startup
```bash
# Start complete system (recommended)
./start-system.sh

# System includes:
# - MongoDB Atlas (cloud database)
# - Gatekeeper API (port 8001)
# - CrewAI API (port 8000)  
# - React Frontend (port 3000)
```

### Development (Individual Services)
```bash
# Frontend development
cd frontend && npm run dev

# Gatekeeper API
cd gatekeeper-api && python -m uvicorn app.main:app --reload --port 8001

# CrewAI Backend
cd python-crewai && python -m uvicorn api.main:app --reload --port 8000
```

### Frontend Commands
```bash
cd frontend/
npm install          # Install dependencies
npm run dev         # Development server
npm run build       # Production build
npm run start       # Production server
```

### API Development
```bash
# Install Python dependencies
cd gatekeeper-api && pip install -r requirements.txt
cd python-crewai && pip install -r requirements.txt

# Run individual APIs
python -m uvicorn app.main:app --reload --port 8001  # Gatekeeper
python -m uvicorn api.main:app --reload --port 8000  # CrewAI
```

## Development Environment

### Prerequisites
1. **Node.js 22+** - Required runtime
2. **MongoDB** - Database server
3. **Python 3.11+** - Para Beanie ODM e APIs Python
4. **OpenAI/Gemini API Keys**:
   ```bash
   export OPENAI_API_KEY="sk-..."
   export GEMINI_API_KEY="AIza..."
   ```

### Environment Configuration (.env file)
```bash
# Database
MONGODB_URL=mongodb+srv://dev:JiCoKnCCu6pHpIwZ@dev.fednd1d.mongodb.net/?retryWrites=true&w=majority&appName=dev
DATABASE_NAME=mit_logistics

# LLM APIs
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# Configuration
ROUTING_STRATEGY=automatic    # Automatic based on task type
TEMPERATURE=0.3              # Precise responses for logistics
MAX_DAILY_COST=50            # $50 per provider (configurable)
```

## Code Style & Standards

### TypeScript Configuration
- **Strict mode** with `exactOptionalPropertyTypes` and `noUncheckedIndexedAccess`
- **ES2022 target** with ESNext modules
- **Path aliases**: `@/*` maps to `src/*`
- **Source maps** enabled for debugging
- **Declaration files** generated for library use

### Code Conventions
- Use **descriptive variable/function names**
- Prefer **functional programming patterns**
- Use **TypeScript interfaces** for public APIs
- **JSDoc comments** for complex functions
- **camelCase** for variables, **PascalCase** for classes/types
- Use "URL" (not "Url"), "API" (not "Api"), "ID" (not "Id")
- **NEVER** use `@ts-expect-error` or `@ts-ignore`

### File Organization
- **Types**: Define in `src/types/index.ts`
- **Agents**: Core logic in `src/agents/`
- **Utils**: Helper functions in `src/utils/`
- **Tests**: Mirror src structure in `tests/`
- **Database Models**: `python-crewai/models/__init__.py` e `gatekeeper-api/app/models.py`

## Agent Specialization

O MITTrackingAgent é especializado em:

### Logistics Domain Knowledge
- **CT-e (Conhecimento de Transporte Eletrônico)**: Consultas por número, status, validação
- **Container Tracking**: Rastreamento em tempo real, localização
- **BL (Bill of Lading)**: Conhecimentos de embarque marítimo
- **ETA/ETD**: Previsões de chegada e saída
- **Delivery Status**: Status de entregas e eventos de rota

### Example Queries Supported
```
"Onde está o meu BL?"
"Me mostre o CT-e da carga X"
"Qual o status da minha entrega?"
"CT-e número 351234567890123456789012345678901234"
"Quando chega o container ABCD1234567?"
```

### Response Characteristics
- **Domain-specific**: Focused on logistics terminology
- **Contextual**: Maintains conversation history via MongoDB
- **Precise**: Low temperature for accurate information
- **Bilingual**: Portuguese primary, English support
- **Persistent**: All interactions saved for learning and context

## Testing Strategy

### Test Structure
- **Unit tests**: Individual component testing
- **Integration tests**: Database connections, agent responses
- **Smoke tests**: Basic functionality verification
- **Mocks**: Isolated testing without external dependencies

### Test Commands
```bash
# Quick smoke test
npm run test:verbose -- tests/unit/smoke.test.ts

# Test specific agent
npm run test:verbose -- tests/unit/mitTrackingAgent.test.ts

# Integration with database
npm run test:verbose -- tests/integration/database-connection.test.ts
```

## Deployment

### Local Development
1. Configure `.env` file with MongoDB Atlas and API keys
2. Run `./start-system.sh` to start all services
3. Access frontend at `http://localhost:3000`

### Production Deployment
1. **Frontend**: Build and deploy React app
   ```bash
   cd frontend && npm run build
   ```
2. **APIs**: Deploy Python FastAPI services
   ```bash
   # Gatekeeper API
   cd gatekeeper-api && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
   
   # CrewAI API
   cd python-crewai && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

### Production Considerations
- **MongoDB Atlas**: Cloud database already configured
- **Environment Variables**: Configure production .env securely
- **Reverse Proxy**: Use Nginx for load balancing and SSL
- **Health Monitoring**: APIs include `/health` endpoints
- **Cost Management**: Monitor LLM API usage and costs
- **Database Backups**: MongoDB Atlas handles automatic backups

## Migration Commands

To standardize across different AI assistants, use these commands to migrate existing configuration files to AGENT.md:

```bash
# Claude Code (our current case)
mv CLAUDE.md AGENT.md.backup && ln -s AGENT.md CLAUDE.md

# Cline
mv .clinerules AGENT.md && ln -s AGENT.md .clinerules

# Cursor
mv .cursorrules AGENT.md && ln -s AGENT.md .cursorrules

# Gemini CLI
mv GEMINI.md AGENT.md && ln -s AGENT.md GEMINI.md

# OpenAI Codex
mv AGENTS.md AGENT.md && ln -s AGENT.md AGENTS.md

# GitHub Copilot
mkdir -p .github/instructions
ln -s ../../AGENT.md .github/instructions/mit-tracking.instructions.md

# Replit
ln -s AGENT.md .replit.md

# Windsurf
ln -s AGENT.md .windsurfrules
```

This approach maintains backward compatibility while centralizing all AI assistant instructions in a single AGENT.md file.

## Debugging & Troubleshooting

### Common Issues
1. **API Keys**: Ensure OpenAI and/or Gemini API keys are properly configured
2. **Database Connection**: Verify MongoDB is running and accessible
3. **Rate Limits**: Monitor daily cost limits and request quotas
4. **TypeScript Errors**: Run `npm run typecheck` for detailed errors
5. **Test Failures**: Check API and database availability for integration tests

### Logging
- Agent responses include provider information and token usage
- Error handling for API failures with automatic fallback
- LLM routing statistics and cost tracking
- Jest verbose output for test debugging
- Real-time monitoring via `/settings/llm` dashboard
- Database operations logging for troubleshooting

## Database Architecture

### MongoDB + Beanie ODM
O sistema utiliza **MongoDB** como banco de dados principal com **Beanie ODM** (Object Document Mapper) para Python, proporcionando uma interface assíncrona e typada para operações de banco de dados.

### Database Models

#### Core Models
- **User**: Usuários do sistema com autenticação e roles (admin, logistics, finance, operator)
- **Client**: Empresas/clientes que utilizam o sistema
- **Context**: Histórico de interações e conversas dos usuários com os agentes
- **Container**: Containers de transporte com rastreamento
- **Shipment**: Embarques/fretes associados aos containers
- **TrackingEvent**: Eventos de rastreamento ao longo da cadeia logística

#### Database Configuration
```python
# Configurações principais
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "mit_logistics"

# Modelos inicializados automaticamente
document_models = [User, Client, Context, Container, Shipment, TrackingEvent]
```

### Key Features

#### 1. **Beanie ODM Integration**
- **Async/Await**: Operações assíncronas nativas
- **Type Safety**: Modelos tipados com Pydantic
- **Auto-indexing**: Criação automática de índices para performance
- **Relationships**: Suporte a links entre documentos

#### 2. **Gatekeeper API Database Service**
- **Connection Management**: Inicialização e health checks
- **Index Creation**: Índices otimizados para consultas frequentes
- **Service Layer**: `DatabaseService` com operações comuns

#### 3. **Context Persistence**
- **User Context**: Histórico completo de interações por usuário
- **Session Tracking**: Agrupamento de conversas por sessão
- **Agent Tracking**: Registro de quais agentes foram envolvidos
- **Metadata Storage**: Dados adicionais flexíveis por interação

### Database Operations

#### Essential Services
```python
# Health Check
await DatabaseService.health_check()

# User Operations  
user = await DatabaseService.get_user_by_email("user@example.com")
new_user = await DatabaseService.create_user("Name", "email@test.com", "logistics")

# Context Operations
context = await DatabaseService.add_context(
    user_id="user123",
    input_text="Onde está meu container?",
    output_text="Container ABCD1234 está em Santos/SP",
    agents=["logistics-agent"],
    session_id="sess123"
)

# Get User History
history = await DatabaseService.get_user_context("user123", limit=50)
```

### Database Indexes

#### Performance Optimizations
- **Users**: `email` (unique), `role`
- **Context**: `user_id + timestamp`, `session_id` 
- **Containers**: `container_number` (unique), `current_status`
- **Shipments**: `status`, `client`, `created_at`
- **TrackingEvents**: `container`, `shipment`, `timestamp`, `type`

### Environment Variables
```bash
# Database Configuration (MongoDB Atlas)
MONGODB_URL="mongodb+srv://dev:JiCoKnCCu6pHpIwZ@dev.fednd1d.mongodb.net/?retryWrites=true&w=majority&appName=dev"
DATABASE_NAME="mit_logistics"

# Database has 405+ documents populated:
# - 30 clients, 50 users, 40 containers
# - 35 shipments, 150 tracking events, 100+ contexts
```

---

# 🎨 FRONTEND IMPLEMENTATION PLAN - Sistema de Logística Inteligente

## 🎯 Objetivo do Frontend
Criar um **Dashboard Interativo** para teste dos agentes do sistema de logística inteligente:

1. **🚪 Gatekeeper Agent** - Autenticação e roteamento
2. **🤖 Agentes Especializados** - Admin, Logistics, Finance  
3. **📊 Visualização** da comunicação entre agentes
4. **📋 Testes interativos** de todo o fluxo do sistema

## 🛠️ Stack Tecnológica ATUALIZADA

### Frontend React (SEM TAILWIND)
```json
{
  "framework": "Next.js 14",
  "styling": "CSS Modules + CSS Custom Properties",
  "state": "Zustand",
  "http": "Axios + TanStack Query", 
  "ui": "Radix UI + Lucide Icons",
  "charts": "Chart.js + React-Chartjs-2",
  "forms": "React Hook Form + Zod",
  "theme": "next-themes"
}
```

### Justificativa da Stack ATUALIZADA
- **Next.js 14:** App Router, SSR, TypeScript nativo
- **CSS Modules:** Escopo local, performance otimizada (SEM Tailwind)
- **CSS Custom Properties:** Design system consistente com variáveis CSS
- **Zustand:** State management simples e performático
- **Radix UI:** Componentes acessíveis e customizáveis

## 🎨 Design System (baseado em moveintech.com.br)
- **🎨 Paleta:** Azuis tech, cinzas modernos, acentos verdes
- **📱 Layout:** Dashboard responsivo com sidebar
- **⚡ UX:** Foco em "transformar dados em inteligência"
- **📊 Visualização:** Gráficos e métricas em tempo real

## 🏗️ Arquitetura do Sistema
```
🌐 React Frontend :3000 ──────┐
                              ├─► 🚪 Gatekeeper API :8001 ──┐
                              │   (Auth & Routing)         │
                              └─► 📊 CrewAI API :8000 ─────┤
                                  (GraphQL & Agents)      │
                                                          │
                              🗄️ MongoDB Atlas ◄─────────┘
                                 (mit_logistics DB)
```

## 📁 Estrutura do Projeto
```
frontend/
├── 📁 app/                    # Next.js App Router
│   ├── 📁 (dashboard)/        # Dashboard routes
│   │   ├── 📁 agents/         # Testes de agentes
│   │   ├── 📁 monitoring/     # Monitoramento
│   │   └── 📁 settings/       # Configurações
│   ├── 📁 api/               # API routes (proxy)
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Homepage
├── 📁 components/
│   ├── 📁 ui/                # Componentes base (Radix)
│   ├── 📁 agents/            # Componentes específicos
│   ├── 📁 charts/            # Visualizações
│   └── 📁 layout/            # Layout components
├── 📁 lib/
│   ├── 📁 api/               # Cliente API
│   ├── 📁 store/             # Zustand stores
│   ├── 📁 types/             # TypeScript types
│   └── 📁 utils/             # Utilities
├── 📁 styles/
│   ├── globals.css           # Global styles + CSS Variables
│   └── 📁 modules/           # CSS Modules
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
└── package.json
```

## 🚀 Funcionalidades Principais

### 1. 🔐 Simulador de Autenticação
- Interface para testar roles: Admin, Logistics, Finance, Operator
- Simulação de permissões diferentes por usuário
- Visualização de responses do Gatekeeper

### 2. 🤖 Playground de Agentes
- Chat interface para cada agente especializado
- Upload de documentos (CT-e, PDFs, imagens)
- Histórico de conversas por sessão
- Visualização de capabilities por agente

### 3. 📊 Dashboard de Monitoramento
- Status em tempo real de todos os serviços
- Métricas de performance (latência, throughput)
- Logs visuais das interações entre agentes
- Health checks automáticos

### 4. 🧪 Centro de Testes
- Cenários pré-definidos de teste
- Teste de fluxos completos (auth → agent → response)
- Comparação de responses entre agentes
- Export de resultados para relatórios

### 5. 📋 Explorador de API
- GraphQL Playground integrado
- REST endpoints com interface amigável
- Documentação interativa da API
- Gerador de código para diferentes linguagens

## 🧪 Fluxos de Teste

### Fluxo 1: Teste de Autenticação
1. **Seleção de usuário** (role + permissões)
2. **Envio para Gatekeeper** via interface
3. **Visualização da resposta** com routing info
4. **Teste de acesso** aos agentes autorizados

### Fluxo 2: Teste de Agente
1. **Autenticação** bem-sucedida
2. **Seleção do agente** (Admin/Logistics/Finance)
3. **Envio de mensagem/documento**
4. **Visualização da resposta** do CrewAI
5. **Análise de capabilities** do agente

### Fluxo 3: Teste Completo
1. **Simulação de usuário real**
2. **Upload de documento CT-e**
3. **Processamento pelo agente logística**
4. **Geração de insights**
5. **Visualização de métricas**

## 📱 Rotas da Aplicação
```
app/
├── page.tsx                 # → / (Overview)
├── (dashboard)/
│   ├── agents/
│   │   ├── page.tsx         # → /agents (Lista de agentes)
│   │   ├── [agent]/
│   │   │   └── page.tsx     # → /agents/admin|logistics|finance
│   │   └── playground/
│   │       └── page.tsx     # → /agents/playground
│   ├── monitoring/
│   │   ├── page.tsx         # → /monitoring (Dashboard principal)
│   │   ├── logs/
│   │   │   └── page.tsx     # → /monitoring/logs
│   │   └── metrics/
│   │       └── page.tsx     # → /monitoring/metrics
│   ├── api-explorer/
│   │   ├── page.tsx         # → /api-explorer (GraphQL + REST)
│   │   ├── graphql/
│   │   │   └── page.tsx     # → /api-explorer/graphql
│   │   └── rest/
│   │       └── page.tsx     # → /api-explorer/rest
│   └── settings/
│       └── page.tsx         # → /settings
```

## 🎭 Fases de Implementação

### Fase 1: Setup Base (1-2 dias)
1. ✅ Inicializar projeto Next.js com TypeScript
2. ✅ Configurar CSS Modules + CSS Custom Properties (sem Tailwind)
3. ✅ Setup Docker com nginx proxy
4. ✅ Integração básica com APIs existentes

### Fase 2: Componentes Core (2-3 dias)
5. ✅ Dashboard layout responsivo
6. ✅ Sistema de autenticação mock
7. ✅ Cliente GraphQL configurado
8. ✅ Componentes UI base (Radix)

### Fase 3: Funcionalidades (3-4 dias)
9. ✅ Agent tester interativo
10. ✅ Monitoring dashboard real-time
11. ✅ API explorer com playground
12. ✅ Upload de documentos

### Fase 4: Polimento (1-2 dias)
13. ✅ Testes automatizados
14. ✅ Documentação completa
15. ✅ Deploy scripts finalizados
16. ✅ Performance optimization

## 📋 TODO List Progress
- [⏳] Setup base do projeto Next.js com TypeScript
- [📋] Configurar CSS Modules + CSS Custom Properties (sem Tailwind)
- [📋] Setup Docker com nginx proxy
- [📋] Integração básica com APIs existentes
- [📋] Criar dashboard layout responsivo
- [📋] Implementar sistema de autenticação mock
- [📋] Configurar cliente GraphQL
- [📋] Criar componentes UI base com Radix
- [📋] Implementar Agent Tester interativo
- [📋] Criar Monitoring Dashboard real-time
- [📋] Implementar API Explorer com playground
- [📋] Adicionar funcionalidade de upload de documentos

---

**🎯 Goal**: Create intelligent logistics agents with persistent memory, multi-model LLM routing, and comprehensive testing for enterprise-grade logistics tracking and management.