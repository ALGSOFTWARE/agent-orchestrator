# 🚀 MIT Logistics - Sistema Completo de Agentes Inteligentes

Sistema completo para gestão e teste de agentes de IA especializados em logística, desenvolvido com Next.js, Python/CrewAI e Ollama.

## 📋 Visão Geral

O MIT Logistics é uma plataforma completa que permite:
- 🤖 **Teste interativo de agentes de IA** especializados em logística
- 📊 **Monitoramento em tempo real** de serviços e métricas
- 🔐 **Sistema de autenticação** com controle de permissões
- 🌐 **Interface web moderna** para todas as funcionalidades
- 🐳 **Deploy containerizado** com Docker

## 🏗️ Arquitetura

```
MIT Logistics/
├── frontend/           # Next.js 14 + TypeScript + CSS Modules
├── python-crewai/      # Backend Python + CrewAI + FastAPI
├── start-system.sh     # Script de inicialização automática
└── START-SYSTEM.md     # Guia detalhado de setup
```

### Stack Tecnológico

**Frontend:**
- Next.js 14 com App Router
- TypeScript (strict mode)
- CSS Modules + CSS Custom Properties
- Zustand (state management)
- Canvas API (charts personalizados)

**Backend:**
- Python 3.9+ com FastAPI
- CrewAI para orquestração de agentes
- LangChain para processamento de linguagem
- Ollama para modelos de IA locais

**IA/Modelos:**
- Ollama local (llama3.2:3b, mistral)
- Agentes especializados por domínio
- Temperatura baixa (0.3) para precisão

## 🚀 Como Rodar na Sua Máquina

### Método 1: Script Automático (Mais Fácil)

```bash
# 1. Navegue até o diretório do projeto
cd /home/narrador/Projetos/MIT

# 2. Torne o script executável
chmod +x start-system.sh

# 3. Execute o script (vai instalar tudo automaticamente)
./start-system.sh
```

O script vai:
- ✅ Verificar todos os pré-requisitos
- 📦 Instalar dependências automaticamente
- 🧠 Configurar Ollama e baixar modelos
- 🚀 Iniciar todos os serviços
- 🌐 Mostrar as URLs para acesso

### Método 2: Setup Manual

Se preferir fazer manualmente, consulte o arquivo `START-SYSTEM.md` para instruções detalhadas.

### Método 3: Apenas Frontend (Para desenvolvimento)

```bash
# Se quiser rodar apenas o frontend para ver a interface
cd /home/narrador/Projetos/MIT/frontend
chmod +x start-dev.sh
./start-dev.sh
```

## 🌐 URLs do Sistema

Após iniciar, acesse:

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🖥️ **Frontend** | http://localhost:3000 | Dashboard principal |
| 🤖 **Agent Tester** | http://localhost:3000/agents | Teste os agentes de IA |
| 📊 **Monitoring** | http://localhost:3000/monitoring | Métricas em tempo real |
| 🔍 **API Explorer** | http://localhost:3000/api | Playground GraphQL |
| 🛡️ **Gatekeeper API** | http://localhost:8001 | API de autenticação |
| 🧠 **Ollama** | http://localhost:11434 | Servidor de IA local |

## 🎯 Primeiros Passos

1. **Execute o sistema**: `./start-system.sh`
2. **Abra no navegador**: http://localhost:3000
3. **Faça login**: Clique em "🔐 Entrar" e escolha um usuário teste
4. **Explore**:
   - **Agent Tester**: Converse com os agentes especializados
   - **Monitoring**: Veja métricas e status dos serviços
   - **API Explorer**: Teste as APIs GraphQL

## 🤖 Agentes Disponíveis

### MIT Tracking Agent
- **Especialidade**: Logística e rastreamento
- **Funcionalidades**: CT-e, BL, containers, ETAs
- **Exemplos**: "Onde está meu container?", "Status do CT-e X"

### Gatekeeper Agent
- **Especialidade**: Segurança e autenticação
- **Funcionalidades**: Controle de acesso, permissões
- **Exemplos**: "Quem pode acessar X?", "Validar permissões"

### Customs Agent
- **Especialidade**: Documentação aduaneira
- **Funcionalidades**: DI, DUE, classificações fiscais
- **Exemplos**: "NCM do produto X", "Status da DI"

### Financial Agent
- **Especialidade**: Operações financeiras
- **Funcionalidades**: Câmbio, custos, faturamento
- **Exemplos**: "Cotação USD hoje", "Custo do frete"

## 📊 Funcionalidades

### 🔐 Sistema de Autenticação
- Usuários teste pré-configurados
- 4 níveis de permissão (Admin, Logistics, Finance, Operator)
- Simulação completa de sessões e tokens

### 🤖 Interface de Teste de Agentes
- Chat interativo com cada agente
- Histórico de conversas
- Métricas de performance
- Ações rápidas pré-definidas

### 📊 Dashboard de Monitoramento
- Status de todos os serviços
- Métricas de CPU, memória, disco
- Gráficos em tempo real
- Logs de atividade
- Health checks automáticos

### 🌐 Explorador de API
- Playground GraphQL interativo
- Documentação automática
- Exemplos de queries
- Schema explorer

## 🔧 Desenvolvimento

### Estrutura do Frontend
```
frontend/src/
├── app/                    # Next.js App Router
├── components/
│   ├── ui/                # Componentes base
│   ├── features/          # Componentes de funcionalidade
│   └── monitoring/        # Componentes de monitoramento
├── lib/                   # Utilities e configurações
├── styles/                # CSS Modules
└── types/                 # Definições TypeScript
```

### Scripts Disponíveis
```bash
# Frontend
npm run dev          # Desenvolvimento
npm run build        # Build de produção
npm run typecheck    # Verificação de tipos
npm test             # Testes

# Backend
python -m uvicorn api.main:app --reload   # Desenvolvimento
```

## 🐛 Troubleshooting

### Problemas Comuns

**❌ Erro: Porta 3000 ocupada**
```bash
npx kill-port 3000
# ou
./start-system.sh  # O script mata automaticamente
```

**❌ Ollama não conecta**
```bash
# Verificar se está rodando
curl http://localhost:11434/api/version

# Reiniciar se necessário
pkill ollama && ollama serve
```

**❌ Dependências Python**
```bash
cd python-crewai
pip3 install --upgrade -r requirements.txt
```

**❌ Modelos Ollama não encontrados**
```bash
ollama pull llama3.2:3b
ollama pull mistral
```

### Logs e Debug

```bash
# Logs do frontend
cd frontend && npm run dev

# Logs do backend
cd python-crewai && python -m uvicorn api.main:app --log-level debug

# Status do sistema
curl http://localhost:3000/api/health
curl http://localhost:8001/health
```

## 📱 Recursos Móveis

A interface é totalmente responsiva e funciona em:
- 📱 Smartphones (iOS/Android)
- 📱 Tablets
- 💻 Desktops
- 🖥️ Monitores ultrawide

## 🚀 Deploy em Produção

Para deploy em EC2/servidor, use o script automatizado:
```bash
# (Em desenvolvimento - será criado em breve)
./deploy-ec2.sh
```

## 📞 Suporte

**Sistema testado em:**
- Ubuntu 20.04+
- macOS 12+
- Windows 11 (WSL2)

**Requisitos mínimos:**
- Node.js 18+
- Python 3.9+
- 4GB RAM
- 10GB espaço livre

---

## 🎉 Pronto para Usar!

Execute `./start-system.sh` e abra http://localhost:3000 no seu navegador.

**Enjoy! 🚀**