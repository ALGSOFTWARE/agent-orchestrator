#!/bin/bash

# 🚀 MIT Logistics - Script de Inicialização Automática
# Este script inicia todos os componentes do sistema

echo "🚀 MIT Logistics - Iniciando Sistema..."
echo "========================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para verificar se uma porta está ocupada
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Função para matar processo em uma porta
kill_port() {
    if check_port $1; then
        echo -e "${YELLOW}Matando processo na porta $1...${NC}"
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Verificar pré-requisitos
echo -e "${BLUE}📋 Verificando pré-requisitos...${NC}"

# Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js não encontrado. Instale Node.js 18+ primeiro.${NC}"
    exit 1
fi

# Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 não encontrado. Instale Python 3.9+ primeiro.${NC}"
    exit 1
fi

# Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama não encontrado. Instale Ollama primeiro.${NC}"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo -e "${GREEN}✅ Pré-requisitos verificados!${NC}"

# Limpar portas se necessário
echo -e "${BLUE}🧹 Limpando portas...${NC}"
kill_port 3000  # Frontend
kill_port 8000  # GraphQL API
kill_port 8001  # Gatekeeper
kill_port 8002  # MIT Tracking

# Verificar se Ollama está rodando
echo -e "${BLUE}🧠 Verificando Ollama...${NC}"
if ! check_port 11434; then
    echo -e "${YELLOW}⚠️  Ollama não está rodando. Iniciando...${NC}"
    ollama serve &
    sleep 5
fi

# Verificar modelos Ollama
echo -e "${BLUE}📦 Verificando modelos Ollama...${NC}"
if ! ollama list | grep -q "llama3.2:3b"; then
    echo -e "${YELLOW}📥 Baixando modelo llama3.2:3b...${NC}"
    ollama pull llama3.2:3b
fi

if ! ollama list | grep -q "mistral"; then
    echo -e "${YELLOW}📥 Baixando modelo mistral...${NC}"
    ollama pull mistral
fi

# Função para iniciar backend
start_backend() {
    echo -e "${BLUE}🐍 Iniciando Backend Python...${NC}"
    cd python-crewai
    
    # Instalar dependências se necessário
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 Criando ambiente virtual...${NC}"
        python3 -m venv venv
    fi
    
    source venv/bin/activate 2>/dev/null || true
    
    echo -e "${YELLOW}📦 Instalando dependências Python...${NC}"
    pip3 install -r requirements.txt > /dev/null 2>&1
    
    echo -e "${GREEN}🚀 Gatekeeper API iniciando na porta 8001...${NC}"
    python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload &
    BACKEND_PID=$!
    
    cd ..
    sleep 3
}

# Função para iniciar frontend
start_frontend() {
    echo -e "${BLUE}⚛️  Iniciando Frontend Next.js...${NC}"
    cd frontend
    
    echo -e "${YELLOW}📦 Instalando dependências Node.js...${NC}"
    npm install > /dev/null 2>&1
    
    echo -e "${GREEN}🚀 Frontend iniciando na porta 3000...${NC}"
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    sleep 3
}

# Iniciar serviços
start_backend
start_frontend

# Aguardar serviços iniciarem
echo -e "${BLUE}⏳ Aguardando serviços iniciarem...${NC}"
sleep 10

# Verificar se tudo está rodando
echo -e "${BLUE}🔍 Verificando status dos serviços...${NC}"

services_ok=true

# Frontend
if check_port 3000; then
    echo -e "${GREEN}✅ Frontend (3000): OK${NC}"
else
    echo -e "${RED}❌ Frontend (3000): FALHOU${NC}"
    services_ok=false
fi

# Gatekeeper
if check_port 8001; then
    echo -e "${GREEN}✅ Gatekeeper (8001): OK${NC}"
else
    echo -e "${RED}❌ Gatekeeper (8001): FALHOU${NC}"
    services_ok=false
fi

# Ollama
if check_port 11434; then
    echo -e "${GREEN}✅ Ollama (11434): OK${NC}"
else
    echo -e "${RED}❌ Ollama (11434): FALHOU${NC}"
    services_ok=false
fi

echo "========================================"

if [ "$services_ok" = true ]; then
    echo -e "${GREEN}🎉 SISTEMA INICIADO COM SUCESSO!${NC}"
    echo ""
    echo -e "${BLUE}🌐 URLs disponíveis:${NC}"
    echo -e "   Frontend:     ${GREEN}http://localhost:3000${NC}"
    echo -e "   Agent Tester: ${GREEN}http://localhost:3000/agents${NC}"
    echo -e "   Monitoring:   ${GREEN}http://localhost:3000/monitoring${NC}"
    echo -e "   Gatekeeper:   ${GREEN}http://localhost:8001${NC}"
    echo -e "   Ollama:       ${GREEN}http://localhost:11434${NC}"
    echo ""
    echo -e "${YELLOW}💡 Dica: Abra http://localhost:3000 no seu navegador${NC}"
    echo ""
    echo -e "${BLUE}📝 Para parar o sistema, pressione Ctrl+C${NC}"
    
    # Manter script rodando
    trap 'echo -e "\n${YELLOW}🛑 Parando sistema...${NC}"; kill $FRONTEND_PID $BACKEND_PID 2>/dev/null; exit 0' INT
    
    while true; do
        sleep 1
    done
else
    echo -e "${RED}❌ FALHA AO INICIAR ALGUNS SERVIÇOS${NC}"
    echo -e "${YELLOW}📋 Verifique os logs acima e tente novamente${NC}"
    echo -e "${BLUE}💡 Ou execute manualmente conforme o START-SYSTEM.md${NC}"
    exit 1
fi