# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MIT Tracking - Agente Conversacional Especializado em Logística usando CrewAI e Ollama local. Este projeto implementa um assistente de IA focado em consultas logísticas, especialmente CT-e (Conhecimento de Transporte Eletrônico), rastreamento de containers e documentos de transporte.

## Technology Stack

- **Runtime**: Node.js 22 (ESM modules)
- **AI Framework**: CrewAI + Langchain
- **LLM**: Ollama local (modelo Mistral)
- **Containerization**: Docker
- **Architecture**: Simple conversational agent (no NestJS)

## Project Structure

```
crewai-agent/
├── agents/
│   └── conversationalAgent.js    # Agente especializado em logística
├── index.js                      # Ponto de entrada da aplicação
├── .env                          # Configurações do ambiente
├── Dockerfile                    # Container Node.js 22
├── .dockerignore                 # Exclusões do Docker
└── package.json                  # Dependências Node.js
```

## Development Commands

### Local Development
```bash
# Instalar dependências
npm install

# Executar localmente (requer Ollama rodando)
npm start
# ou
node index.js
```

### Docker Commands
```bash
# Build da imagem
docker build -t crewai-ollama .

# Executar container (conecta com Ollama no host)
docker run -it --rm crewai-ollama
```

## Prerequisites

1. **Ollama** deve estar rodando no host:
   ```bash
   ollama serve
   ollama pull mistral
   ```

2. **Docker** deve conseguir acessar `host.docker.internal:11434`

## Agent Specialization

O agente conversacional é especializado em:

- **CT-e (Conhecimento de Transporte Eletrônico)**: Consultas por número, status, informações
- **Rastreamento de Containers**: Status em tempo real, localização
- **BL (Bill of Lading)**: Conhecimentos de embarque
- **ETA/ETD**: Previsões de chegada e saída
- **Documentos Logísticos**: Consultas por ID, PDFs, XMLs

### Exemplo de Consultas Suportadas
- "Onde está o meu BL?"
- "Me mostre o CT-e da carga X"
- "Qual o status da minha entrega?"
- "CT-e número 351234567890123456789012345678901234"

## Configuration

- **Ollama URL**: `http://host.docker.internal:11434` (para container)
- **Model**: `mistral`
- **Temperature**: `0.3` (respostas mais precisas para logística)

## Development Notes

- Projeto usa ES modules (`"type": "module"` no package.json)
- Agent configurado com context específico de logística
- Integração Docker otimizada para comunicação com Ollama host
- Error handling para problemas de conexão Ollama
- Logging detalhado para debugging

## Testing the Application

1. Certifique-se que Ollama está rodando com modelo Mistral
2. Execute via Docker ou localmente
3. O agente executa automaticamente uma consulta de demonstração sobre CT-e
4. Verifique se as respostas são específicas do domínio logístico