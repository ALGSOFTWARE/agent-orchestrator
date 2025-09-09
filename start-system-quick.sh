#!/bin/bash

# MIT Tracking System - Quick Start (Skip Dependencies)
# Versão rápida que pula instalação de dependências se já estão instaladas

set -e  # Sair em caso de erro

print_banner() {
    echo -e "\033[0;35m"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║             MIT TRACKING SYSTEM v3.0 - QUICK START          ║"
    echo "║              Sistema de Logística Inteligente               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "\033[0m"
}

print_banner
echo "🚀 Iniciando MIT Tracking System (Modo Rápido)..."
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
        sleep 1
    fi
}

# Limpar portas se necessário
echo -e "${BLUE}🧹 Limpando portas...${NC}"
kill_port 3000  # Frontend
kill_port 8001  # Gatekeeper API
kill_port 8002  # CrewAI API

# Função para iniciar Gatekeeper API (rápido)
start_gatekeeper() {
    echo -e "${BLUE}🚪 Iniciando Gatekeeper API...${NC}"
    cd gatekeeper-api
    
    if check_port 8001; then
        echo -e "${YELLOW}⚠️ Gatekeeper já rodando na porta 8001${NC}"
        cd ..
        return
    fi
    
    # Verificar se venv existe
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Ambiente virtual não encontrado. Execute ./start-system.sh primeiro${NC}"
        cd ..
        exit 1
    fi
    
    echo -e "${GREEN}🚀 Gatekeeper API iniciando na porta 8001...${NC}"
    source venv/bin/activate
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > /tmp/gatekeeper.log 2>&1 &
    GATEKEEPER_PID=$!
    
    cd ..
    sleep 2
}

# Função para iniciar CrewAI Backend (rápido)
start_crewai() {
    echo -e "${BLUE}🤖 Iniciando CrewAI Backend...${NC}"
    cd python-crewai
    
    if check_port 8002; then
        echo -e "${YELLOW}⚠️ CrewAI já rodando na porta 8002${NC}"
        cd ..
        return
    fi
    
    # Verificar se venv existe
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Ambiente virtual não encontrado. Execute ./start-system.sh primeiro${NC}"
        cd ..
        exit 1
    fi
    
    echo -e "${GREEN}🚀 CrewAI API iniciando na porta 8002...${NC}"
    source venv/bin/activate
    python -m uvicorn api.simple_main:app --host 0.0.0.0 --port 8002 --reload > /tmp/crewai.log 2>&1 &
    CREWAI_PID=$!
    
    cd ..
    sleep 2
}

# Função para iniciar frontend (rápido)
start_frontend() {
    echo -e "${BLUE}⚛️ Iniciando Frontend React...${NC}"
    cd original-logistic-pulse
    
    if check_port 3000; then
        echo -e "${YELLOW}⚠️ Frontend já rodando na porta 3000${NC}"
        cd ..
        return
    fi
    
    # Verificar se node_modules existe
    if [ ! -d "node_modules" ]; then
        echo -e "${RED}❌ Node modules não encontrado. Execute ./start-system.sh primeiro${NC}"
        cd ..
        exit 1
    fi
    
    echo -e "${GREEN}🚀 Frontend iniciando na porta 3000...${NC}"
    npm run dev > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    cd ..
    sleep 3
}

# Iniciar serviços
start_gatekeeper
start_crewai  
start_frontend

# Aguardar serviços iniciarem
echo -e "${BLUE}⏳ Aguardando serviços iniciarem...${NC}"
sleep 5

# Verificar status
echo -e "${BLUE}🔍 Verificando status dos serviços...${NC}"

services_ok=true

# Frontend (check ports 3000-3010)
frontend_port=""
for port in {3000..3010}; do
    if check_port $port; then
        frontend_port="$port"
        echo -e "${GREEN}✅ Frontend ($port): OK${NC}"
        break
    fi
done
if [ -z "$frontend_port" ]; then
    echo -e "${RED}❌ Frontend (3000-3010): FALHOU${NC}"
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

echo "========================================"

if [ "$services_ok" = true ]; then
    echo -e "${GREEN}🎉 SISTEMA INICIADO COM SUCESSO!${NC}"
    echo ""
    echo -e "${BLUE}🌐 SISTEMA COMPLETO DISPONÍVEL:${NC}"
    if [ ! -z "$frontend_port" ]; then
        echo -e "   📱 Dashboard:        ${GREEN}http://localhost:$frontend_port${NC}"
        echo -e "   🔍 Busca Semântica:  ${GREEN}http://localhost:$frontend_port/search${NC}"
        echo -e "   📋 Orders:           ${GREEN}http://localhost:$frontend_port/orders${NC}"
        echo -e "   🤖 Agent Tester:     ${GREEN}http://localhost:$frontend_port/agents${NC}"
        echo -e "   📊 Monitoramento:    ${GREEN}http://localhost:$frontend_port/monitoring${NC}"
    fi
    echo ""
    echo -e "   🔐 Gatekeeper API:   ${GREEN}http://localhost:8001/docs${NC}"
    echo -e "   🧠 CrewAI API:       ${GREEN}http://localhost:8002/docs${NC}"
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
    echo ""
    echo -e "${BLUE}🔍 LOGS PARA DEBUG:${NC}"
    echo -e "   📄 Gatekeeper: ${GREEN}tail -f /tmp/gatekeeper.log${NC}"
    echo -e "   📄 CrewAI:     ${GREEN}tail -f /tmp/crewai.log${NC}"
    echo -e "   📄 Frontend:   ${GREEN}tail -f /tmp/frontend.log${NC}"
    echo ""
    echo -e "${BLUE}💡 Execute ./start-system.sh para instalação completa${NC}"
    exit 1
fi