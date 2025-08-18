#!/bin/bash

# MIT Tracking System - Sistema Completo v3.0
# Versão: 3.0 (MongoDB + FastAPI + React + Gatekeeper)
# 
# Este script inicializa todo o ecossistema do sistema de logística:
# - MongoDB Atlas (já configurado)
# - Gatekeeper API (autenticação/roteamento)
# - Python CrewAI API (agentes de logística)
# - Frontend React (dashboard interativo)

set -e  # Sair em caso de erro

print_banner() {
    echo -e "\033[0;35m"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    MIT TRACKING SYSTEM v3.0                 ║"
    echo "║              Sistema de Logística Inteligente               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "\033[0m"
}

print_banner
echo "🚀 Iniciando MIT Tracking System..."
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

# Carregar e validar configurações
echo -e "${BLUE}🔑 Validando configurações...${NC}"

# Carregar variáveis de ambiente do arquivo .env
if [ -f ".env" ]; then
    echo -e "${BLUE}📄 Carregando configurações do arquivo .env...${NC}"
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo -e "${GREEN}✅ Arquivo .env carregado${NC}"
else
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado${NC}"
fi

# Verificar variáveis críticas
api_keys_found=false
if [ ! -z "$MONGODB_URL" ]; then
    echo -e "${GREEN}✅ MongoDB configurado${NC}"
    api_keys_found=true
else
    echo -e "${RED}❌ MONGODB_URL não configurado${NC}"
    exit 1
fi

if [ ! -z "$OPENAI_API_KEY" ] || [ ! -z "$GEMINI_API_KEY" ]; then
    echo -e "${GREEN}✅ API Keys LLM configuradas${NC}"
else
    echo -e "${YELLOW}⚠️  API Keys LLM não configuradas - algumas funcionalidades podem falhar${NC}"
fi

echo -e "${GREEN}✅ Pré-requisitos verificados!${NC}"

# Limpar portas se necessário
echo -e "${BLUE}🧹 Limpando portas...${NC}"
kill_port 3000  # Frontend
kill_port 3001  # Frontend alt
kill_port 3002  # Frontend alt2
kill_port 8000  # CrewAI API (legacy)
kill_port 8002  # CrewAI API (current)
kill_port 8001  # Gatekeeper API

# Função para iniciar Gatekeeper API
start_gatekeeper() {
    echo -e "${BLUE}🚪 Iniciando Gatekeeper API...${NC}"
    cd gatekeeper-api
    
    # Verificar se já está rodando
    if check_port 8001; then
        echo -e "${YELLOW}⚠️  Gatekeeper já rodando na porta 8001${NC}"
        cd ..
        return
    fi
    
    # Criar ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 Criando ambiente virtual para Gatekeeper...${NC}"
        python3 -m venv venv > /dev/null 2>&1
    fi
    
    # Ativar ambiente virtual e instalar dependências
    echo -e "${YELLOW}📦 Instalando dependências Gatekeeper...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    
    echo -e "${GREEN}🚀 Gatekeeper API iniciando na porta 8001...${NC}"
    venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > /dev/null 2>&1 &
    GATEKEEPER_PID=$!
    
    cd ..
    sleep 3
}

# Função para iniciar CrewAI Backend
start_crewai() {
    echo -e "${BLUE}🤖 Iniciando CrewAI Backend...${NC}"
    cd python-crewai
    
    # Verificar se já está rodando
    if check_port 8002; then
        echo -e "${YELLOW}⚠️  CrewAI já rodando na porta 8002${NC}"
        cd ..
        return
    fi
    
    # Criar ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 Criando ambiente virtual para CrewAI...${NC}"
        python3 -m venv venv > /dev/null 2>&1
    fi
    
    # Ativar ambiente virtual e instalar dependências
    echo -e "${YELLOW}📦 Instalando dependências CrewAI...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    
    echo -e "${GREEN}🚀 CrewAI API iniciando na porta 8002...${NC}"
    venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8002 --reload > /dev/null 2>&1 &
    CREWAI_PID=$!
    
    cd ..
    sleep 3
}

# Função para iniciar frontend
start_frontend() {
    echo -e "${BLUE}⚛️  Iniciando Frontend React...${NC}"
    cd frontend
    
    # Verificar se já está rodando
    if check_port 3000; then
        echo -e "${YELLOW}⚠️  Frontend já rodando na porta 3000${NC}"
        cd ..
        return
    fi
    
    echo -e "${YELLOW}📦 Instalando dependências Node.js...${NC}"
    npm install > /dev/null 2>&1
    
    echo -e "${GREEN}🚀 Frontend iniciando na porta 3000...${NC}"
    npm run dev > /dev/null 2>&1 &
    FRONTEND_PID=$!
    
    cd ..
    sleep 5
}

# Iniciar serviços
start_gatekeeper
start_crewai
start_frontend

# Aguardar serviços iniciarem
echo -e "${BLUE}⏳ Aguardando serviços iniciarem...${NC}"
sleep 10

# Verificar se tudo está rodando
echo -e "${BLUE}🔍 Verificando status dos serviços...${NC}"

services_ok=true

# Frontend (verificar portas 3000, 3001 ou 3002)
frontend_port=""
if check_port 3000; then
    frontend_port="3000"
    echo -e "${GREEN}✅ Frontend (3000): OK${NC}"
elif check_port 3001; then
    frontend_port="3001"
    echo -e "${GREEN}✅ Frontend (3001): OK${NC}"
elif check_port 3002; then
    frontend_port="3002"
    echo -e "${GREEN}✅ Frontend (3002): OK${NC}"
else
    echo -e "${RED}❌ Frontend (3000/3001/3002): FALHOU${NC}"
    services_ok=false
fi

# Gatekeeper API
if check_port 8001; then
    echo -e "${GREEN}✅ Gatekeeper API (8001): OK${NC}"
else
    echo -e "${RED}❌ Gatekeeper API (8001): FALHOU${NC}"
    services_ok=false
fi

# CrewAI API
if check_port 8002; then
    echo -e "${GREEN}✅ CrewAI API (8002): OK${NC}"
else
    echo -e "${RED}❌ CrewAI API (8002): FALHOU${NC}"
    services_ok=false
fi

# MongoDB Atlas Status
if [ ! -z "$MONGODB_URL" ]; then
    echo -e "${GREEN}✅ MongoDB Atlas: Configurado${NC}"
else
    echo -e "${RED}❌ MongoDB Atlas: Não configurado${NC}"
    services_ok=false
fi

echo "========================================"

if [ "$services_ok" = true ]; then
    echo -e "${GREEN}🎉 SISTEMA INICIADO COM SUCESSO!${NC}"
    echo ""
    echo -e "${BLUE}🌐 SISTEMA COMPLETO DISPONÍVEL:${NC}"
    if [ ! -z "$frontend_port" ]; then
        echo -e "   📱 Dashboard:        ${GREEN}http://localhost:$frontend_port${NC}"
        echo -e "   🤖 Agent Tester:    ${GREEN}http://localhost:$frontend_port/agents${NC}"
        echo -e "   ⚙️  Configurações:   ${GREEN}http://localhost:$frontend_port/settings${NC}"
        echo -e "   📊 Monitoramento:    ${GREEN}http://localhost:$frontend_port/monitoring${NC}"
    fi
    echo -e "   🔐 Gatekeeper API:   ${GREEN}http://localhost:8001${NC}"
    echo -e "   🧠 CrewAI API:       ${GREEN}http://localhost:8002${NC}"
    echo ""
    echo -e "${BLUE}📚 DOCUMENTAÇÃO APIS:${NC}"
    echo -e "   📖 Gatekeeper Docs:  ${GREEN}http://localhost:8001/docs${NC}"
    echo -e "   📖 CrewAI Docs:      ${GREEN}http://localhost:8002/docs${NC}"
    echo ""
    echo -e "${BLUE}🗄️  DATABASE:${NC}"
    echo -e "   📊 MongoDB Atlas:     ${GREEN}mit_logistics (405 documentos)${NC}"
    echo ""
    if [ ! -z "$frontend_port" ]; then
        echo -e "${YELLOW}🚀 ACESSE: http://localhost:$frontend_port${NC}"
    fi
    echo ""
    echo -e "${BLUE}📝 Para parar o sistema, pressione Ctrl+C${NC}"
    
    # Manter script rodando
    trap 'echo -e "\n${YELLOW}🛑 Parando sistema...${NC}"; kill $FRONTEND_PID $GATEKEEPER_PID $CREWAI_PID 2>/dev/null; exit 0' INT
    
    while true; do
        sleep 1
    done
else
    echo -e "${RED}❌ FALHA AO INICIAR ALGUNS SERVIÇOS${NC}"
    echo -e "${YELLOW}📋 Verifique os logs acima e tente novamente${NC}"
    echo -e "${BLUE}💡 Ou execute manualmente conforme o START-SYSTEM.md${NC}"
    exit 1
fi