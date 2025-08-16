# MIT Tracking Project

MIT Tracking é um agente conversacional especializado em consultas logísticas, desenvolvido com CrewAI, LangChain e integração local com Ollama. O sistema é focado em CT-e (Conhecimento de Transporte Eletrônico), rastreamento de containers e documentos de transporte.

## Architecture & Stack

- **Runtime**: Node.js 22+ with ES Modules
- **Language**: TypeScript (strict mode)
- **AI Framework**: CrewAI + LangChain
- **LLM**: Ollama local (models: llama3.2:3b, mistral)
- **Testing**: Jest with TypeScript support
- **Containerization**: Docker
- **Build Tool**: TypeScript Compiler (tsc) + tsx for development

## Project Structure

```
MIT/
├── src/
│   ├── agents/
│   │   └── MITTrackingAgent.ts     # Core logistics agent
│   ├── types/
│   │   └── index.ts                # TypeScript definitions
│   ├── utils/
│   │   └── InterfaceInterativa.ts  # Interactive CLI interface
│   ├── index.ts                    # Main CrewAI entry point
│   ├── interactive-agent.ts        # Interactive CLI mode
│   └── simple-agent.ts             # Demo/testing mode
├── tests/
│   ├── unit/                       # Unit tests
│   ├── integration/               # Integration tests
│   ├── mocks/                     # Test mocks
│   └── setup.ts                   # Test configuration
├── agents/                        # Legacy JS agents (being migrated)
├── Dockerfile                     # Production container
└── package.json
```

## Build & Development Commands

### Development
```bash
# Install dependencies
npm install

# Start interactive agent (main mode)
npm start

# Development with hot reload
npm run dev

# Demo mode (single query)
npm run demo

# CrewAI mode
npm run crewai
```

### Build & Type Checking
```bash
# Build TypeScript to dist/
npm run build

# Type check without emitting files
npm run typecheck
```

### Testing
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage report
npm run test:coverage

# Verbose test output
npm run test:verbose
```

### Docker
```bash
# Build container
docker build -t crewai-ollama .

# Run container (connects to host Ollama)
docker run -it --rm crewai-ollama
```

## Development Environment

### Prerequisites
1. **Node.js 22+** - Required runtime
2. **Ollama** running locally:
   ```bash
   ollama serve
   ollama pull llama3.2:3b
   ollama pull mistral
   ```

### Environment Configuration
- **Ollama URL**: `http://localhost:11434` (local) or `http://host.docker.internal:11434` (container)
- **Primary Model**: `llama3.2:3b`
- **Fallback Model**: `mistral`
- **Temperature**: `0.3` (precise responses for logistics)

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
- **Contextual**: Maintains conversation history
- **Precise**: Low temperature for accurate information
- **Bilingual**: Portuguese primary, English support

## Testing Strategy

### Test Structure
- **Unit tests**: Individual component testing
- **Integration tests**: Ollama connection, agent responses
- **Smoke tests**: Basic functionality verification
- **Mocks**: Isolated testing without external dependencies

### Test Commands
```bash
# Quick smoke test
npm run test:verbose -- tests/unit/smoke.test.ts

# Test specific agent
npm run test:verbose -- tests/unit/mitTrackingAgent.test.ts

# Integration with Ollama
npm run test:verbose -- tests/integration/ollama-connection.test.ts
```

## Deployment

### Local Development
1. Ensure Ollama is running with required models
2. Run `npm start` for interactive mode
3. Use `npm run dev` for development with hot reload

### Docker Deployment
1. Build image: `docker build -t crewai-ollama .`
2. Ensure host Ollama is accessible
3. Run: `docker run -it --rm crewai-ollama`

### Production Considerations
- Ollama must be running and accessible
- Models must be pre-downloaded
- Container networking configured for Ollama access
- Resource allocation appropriate for LLM inference

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
1. **Ollama Connection**: Check if `http://localhost:11434` is accessible
2. **Model Loading**: Ensure models are pulled (`ollama pull llama3.2:3b`)
3. **TypeScript Errors**: Run `npm run typecheck` for detailed errors
4. **Test Failures**: Check Ollama availability for integration tests

### Logging
- Agent responses include conversation context
- Error handling for connection failures
- Detailed logs in interactive mode
- Jest verbose output for test debugging

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
🌐 React Frontend :3000 --> 🔀 Nginx Proxy :80
                                ├── 📊 GraphQL API :8000
                                └── 🚪 Gatekeeper Agent :8001
                                      └── 🤖 CrewAI Agents
                                            └── 🧠 Ollama :11434
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

**🎯 Resultado Final:** Dashboard completo para teste e validação de todos os agentes do sistema, permitindo que as equipes de produto testem fluxos completos de forma visual e interativa!