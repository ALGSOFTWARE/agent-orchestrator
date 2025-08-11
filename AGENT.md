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