#!/bin/bash

# 🚀 MIT Logistics - Script de Inicialização Automática
# Este script inicia todos os componentes do sistema

echo "🚀 MIT Logistics - Iniciando Sistema..."
echo "========================================"

# Carregar variáveis de ambiente do arquivo .env
if [ -f ".env" ]; then
    echo -e "${BLUE}📄 Carregando configurações do arquivo .env...${NC}"
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo -e "${GREEN}✅ Arquivo .env carregado com sucesso${NC}"
else
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado, usando variáveis do sistema${NC}"
fi

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

# Teste de configuração
echo -e "${BLUE}🔑 Validando configurações...${NC}"

# Executar teste de configuração Python
if python3 test-config.py; then
    echo -e "${GREEN}✅ Configurações validadas com sucesso!${NC}"
    api_keys_found=true
else
    echo -e "${RED}❌ Falha na validação das configurações!${NC}"
    echo -e "${YELLOW}💡 Edite o arquivo .env e configure suas API keys:${NC}"
    echo "   OPENAI_API_KEY=sk-proj-..."
    echo "   GEMINI_API_KEY=AIzaSy..."
    echo ""
    echo -e "${BLUE}📖 Ou configure através do dashboard em /settings/llm${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Pré-requisitos verificados!${NC}"

# Limpar portas se necessário
echo -e "${BLUE}🧹 Limpando portas...${NC}"
kill_port 3000  # Frontend
kill_port 8000  # GraphQL API
kill_port 8001  # Gatekeeper
kill_port 8002  # MIT Tracking

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

# Frontend (verificar portas 3000 ou 3001)
frontend_port=""
if check_port 3000; then
    frontend_port="3000"
    echo -e "${GREEN}✅ Frontend (3000): OK${NC}"
elif check_port 3001; then
    frontend_port="3001"
    echo -e "${GREEN}✅ Frontend (3001): OK${NC}"
else
    echo -e "${RED}❌ Frontend (3000/3001): FALHOU${NC}"
    services_ok=false
fi

# Gatekeeper
if check_port 8001; then
    echo -e "${GREEN}✅ Gatekeeper (8001): OK${NC}"
else
    echo -e "${RED}❌ Gatekeeper (8001): FALHOU${NC}"
    services_ok=false
fi

# API Status (verificação simplificada)
if [ "$api_keys_found" = true ]; then
    echo -e "${GREEN}✅ APIs LLM: Configuradas${NC}"
else
    echo -e "${RED}❌ APIs LLM: Não configuradas${NC}"
    services_ok=false
fi

echo "========================================"

if [ "$services_ok" = true ]; then
    echo -e "${GREEN}🎉 SISTEMA INICIADO COM SUCESSO!${NC}"
    echo ""
    echo -e "${BLUE}🌐 URLs disponíveis:${NC}"
    if [ ! -z "$frontend_port" ]; then
        echo -e "   Frontend:     ${GREEN}http://localhost:$frontend_port${NC}"
        echo -e "   Agent Tester: ${GREEN}http://localhost:$frontend_port/agents${NC}"
        echo -e "   LLM Config:   ${GREEN}http://localhost:$frontend_port/settings/llm${NC}"
        echo -e "   Monitoring:   ${GREEN}http://localhost:$frontend_port/monitoring${NC}"
    fi
    echo -e "   Gatekeeper:   ${GREEN}http://localhost:8001${NC}"
    echo ""
    if [ ! -z "$frontend_port" ]; then
        echo -e "${YELLOW}💡 Dica: Abra http://localhost:$frontend_port no seu navegador${NC}"
    fi
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