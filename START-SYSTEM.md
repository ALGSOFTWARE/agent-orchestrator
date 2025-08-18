# 🚀 MIT Logistics - Guia de Inicialização

## 📋 Pré-requisitos

### 1. Node.js 18+
```bash
# Verificar se Node.js está instalado
node --version
npm --version
```

### 2. Ollama (para os agentes de IA)
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Ou no macOS com Homebrew
brew install ollama

# Iniciar o serviço Ollama
ollama serve

# Em outro terminal, baixar os modelos necessários
ollama pull llama3.2:3b
ollama pull mistral
```

### 3. Python 3.9+ (para o backend)
```bash
# Verificar se Python está instalado
python3 --version
pip3 --version
```

## 🏃‍♂️ Como Rodar o Sistema

### Opção 1: Script Automático (Recomendado)
```bash
cd /home/narrador/Projetos/MIT
chmod +x start-system.sh
./start-system.sh
```

### Opção 2: Manual (Passo a Passo)

#### 1. Backend Python (Gatekeeper + APIs)
```bash
# Terminal 1 - Backend
cd /home/narrador/Projetos/MIT/python-crewai
pip3 install -r requirements.txt
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 2. Frontend Next.js
```bash
# Terminal 2 - Frontend
cd /home/narrador/Projetos/MIT/frontend
npm install
npm run dev
```

#### 3. Verificar Ollama
```bash
# Terminal 3 - Verificar se Ollama está rodando
curl http://localhost:11434/api/version
```

## 🌐 URLs do Sistema

Após iniciar tudo, acesse:

- **🖥️ Frontend Dashboard**: http://localhost:3000
- **🤖 Agent Tester**: http://localhost:3000/agents
- **📊 Monitoring**: http://localhost:3000/monitoring
- **🛡️ Gatekeeper API**: http://localhost:8001
- **🧠 Ollama API**: http://localhost:11434

## 🔧 Troubleshooting

### Problema: Porta 3000 ocupada
```bash
# Matar processo na porta 3000
npx kill-port 3000
# Ou usar porta alternativa
npm run dev -- --port 3001
```

### Problema: Ollama não conecta
```bash
# Verificar se Ollama está rodando
ps aux | grep ollama

# Reiniciar Ollama
pkill ollama
ollama serve
```

### Problema: Dependências Python
```bash
# Reinstalar dependências
cd /home/narrador/Projetos/MIT/python-crewai
pip3 install --upgrade -r requirements.txt
```

## 🎯 Primeiros Passos

1. **Acesse**: http://localhost:3000
2. **Clique em "🔐 Entrar"** na página inicial
3. **Escolha um usuário teste** (ex: Admin ou Logistics)
4. **Explore**:
   - 🤖 **Agent Tester**: Teste os agentes de IA
   - 📊 **Monitoring**: Veja métricas em tempo real
   - 🔍 **API Explorer**: Explore as APIs GraphQL

## 📱 Funcionalidades Disponíveis

### 🔐 Autenticação
- Usuários de teste pré-configurados
- Diferentes níveis de permissão
- Simulação de sessões

### 🤖 Agent Tester
- MIT Tracking Agent (logística)
- Gatekeeper Agent (segurança)
- Customs Agent (aduaneiro)
- Financial Agent (financeiro)

### 📊 Monitoring Dashboard
- Status dos serviços em tempo real
- Métricas de CPU, Memória, Disco
- Logs de atividade
- Health checks automáticos

## 🐛 Logs e Debug

### Frontend (Next.js)
```bash
# Ver logs do frontend
cd /home/narrador/Projetos/MIT/frontend
npm run dev
```

### Backend (Python)
```bash
# Ver logs do backend
cd /home/narrador/Projetos/MIT/python-crewai
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload --log-level debug
```

### Ollama
```bash
# Ver logs do Ollama
ollama logs
```

## 📞 Suporte

Se encontrar problemas:
1. Verifique se todas as portas estão livres
2. Confirme que Ollama está rodando com os modelos
3. Verifique os logs de cada serviço
4. Reinicie os serviços se necessário

**Sistema testado em**: Ubuntu 20.04+, macOS 12+, Windows 11 (WSL2)