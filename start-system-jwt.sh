#!/bin/bash

# MIT Tracking System v4.0 - JWT Authentication Ready
# Sistema completo com autenticação JWT e chat integrado

set -e  # Sair em caso de erro

print_banner() {
    echo -e "\033[0;35m"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           MIT TRACKING SYSTEM v4.0 - JWT READY              ║"
    echo "║          Sistema de Logística com Autenticação JWT          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "\033[0m"
}

print_banner
echo "🚀 Iniciando MIT Tracking System (JWT Authentication)..."
echo "========================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuração padrão para o microserviço CrewAI
export CREWAI_BASE_URL="${CREWAI_BASE_URL:-http://localhost:8002}"

# Função para verificar se uma porta está ocupada
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    fi

    if command -v ss >/dev/null 2>&1; then
        if ss -ltn 2>/dev/null | grep -E "[:.]$1\s" >/dev/null; then
            return 0
        fi
    fi

    return 1
}

# Função para aguardar health check de um serviço
wait_for_service() {
    local name=$1
    local url=$2
    local retries=${3:-30}
    local delay=${4:-2}

    echo -e "${BLUE}⏳ Aguardando ${name} em ${url}...${NC}"
    for attempt in $(seq 1 "$retries"); do
        if curl -fsS "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}   ✅ ${name} respondeu (tentativa ${attempt}/${retries})${NC}"
            return 0
        fi
        sleep "$delay"
    done

    echo -e "${RED}   ❌ ${name} não respondeu após ${retries} tentativas${NC}"
    return 1
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
kill_port 3000  # Next.js dev
kill_port 8080  # Frontend final
kill_port 8000  # API Principal
kill_port 8001  # Gatekeeper API
kill_port 8002  # CrewAI Service

# Função para iniciar API Principal
start_main_api() {
    echo -e "${BLUE}📊 Iniciando API Principal...${NC}"
    cd gatekeeper-api

    if check_port 8000; then
        echo -e "${YELLOW}⚠️ API Principal já rodando na porta 8000${NC}"
        cd ..
        return
    fi

    # Verificar se venv existe
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Ambiente virtual não encontrado. Criando...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi

    echo -e "${GREEN}🚀 API Principal iniciando na porta 8000...${NC}"
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/api-main.log 2>&1 &
    API_MAIN_PID=$!

    cd ..
    sleep 2
}

# Função para iniciar CrewAI (python-crewai)
start_crewai_service() {
    echo -e "${BLUE}🤖 Iniciando CrewAI Service...${NC}"
    cd python-crewai

    if check_port 8002; then
        echo -e "${YELLOW}⚠️ CrewAI Service já rodando na porta 8002${NC}"
        cd ..
        return
    fi

    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Ambiente virtual do CrewAI não encontrado. Criando...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi

    echo -e "${GREEN}🚀 CrewAI Service iniciando na porta 8002...${NC}"
    python -m uvicorn api.simple_main:app --host 0.0.0.0 --port 8002 --reload > /tmp/crewai.log 2>&1 &
    CREWAI_PID=$!

    cd ..
    sleep 2
}

# Função para iniciar Gatekeeper API
start_gatekeeper() {
    echo -e "${BLUE}🚪 Iniciando Gatekeeper API...${NC}"
    cd gatekeeper-api

    if check_port 8001; then
        echo -e "${YELLOW}⚠️ Gatekeeper já rodando na porta 8001${NC}"
        cd ..
        return
    fi

    # Usar mesmo venv da API principal
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}❌ Ambiente virtual não encontrado${NC}"
        cd ..
        exit 1
    fi

    echo -e "${GREEN}🚀 Gatekeeper API iniciando na porta 8001...${NC}"
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > /tmp/gatekeeper.log 2>&1 &
    GATEKEEPER_PID=$!

    cd ..
    sleep 2
}

# Função para iniciar Frontend Original (Vite)
start_frontend_original() {
    echo -e "${BLUE}🌟 Iniciando Frontend Original (Vite)...${NC}"
    cd original-logistic-pulse

    if check_port 8080; then
        echo -e "${YELLOW}⚠️ Frontend Original já rodando na porta 8080${NC}"
        cd ..
        return
    fi

    # Verificar se node_modules existe
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}📦 Instalando dependências do frontend original...${NC}"
        npm install
    fi

    echo -e "${GREEN}🚀 Frontend Original iniciando na porta 8080...${NC}"
    npm run dev > /tmp/frontend-original.log 2>&1 &
    FRONTEND_ORIGINAL_PID=$!

    cd ..
    sleep 3
}

# Função para iniciar Frontend JWT (Next.js)
start_frontend_jwt() {
    echo -e "${BLUE}⚛️ Iniciando Frontend JWT (Next.js)...${NC}"
    cd frontend

    if check_port 3000; then
        echo -e "${YELLOW}⚠️ Frontend Next.js já rodando na porta 3000${NC}"
        cd ..
        return
    fi

    # Verificar se node_modules existe
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}📦 Instalando dependências do frontend JWT...${NC}"
        npm install
    fi

    echo -e "${GREEN}🚀 Frontend JWT iniciando na porta 3000...${NC}"
    npm run dev > /tmp/frontend-jwt.log 2>&1 &
    FRONTEND_JWT_PID=$!

    cd ..
    sleep 3
}

# Iniciar serviços
echo -e "${BLUE}🔄 Iniciando serviços...${NC}"

startup_sequence=()

start_main_api
startup_sequence+=("API Principal")
wait_for_service "API Principal" "http://localhost:8000/health"

start_crewai_service
startup_sequence+=("CrewAI Service")
wait_for_service "CrewAI Service" "${CREWAI_BASE_URL}/health"

start_gatekeeper
startup_sequence+=("Gatekeeper API")
wait_for_service "Gatekeeper API" "http://localhost:8001/health"

start_frontend_original
startup_sequence+=("Frontend Original")

start_frontend_jwt
startup_sequence+=("Frontend JWT")

# Aguardar serviços iniciarem
echo -e "${BLUE}⏳ Verificação final dos serviços...${NC}"
sleep 3

# Verificar status
echo -e "${BLUE}🔍 Verificando status dos serviços...${NC}"

services_ok=true

# API Principal
if check_port 8000; then
    echo -e "${GREEN}✅ API Principal (8000): OK${NC}"
    # Teste de health check
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}   🌟 Health check: OK${NC}"
    else
        echo -e "${YELLOW}   ⚠️ Health check: Aguardando...${NC}"
    fi
else
    echo -e "${RED}❌ API Principal (8000): FALHOU${NC}"
    services_ok=false
fi

# CrewAI Service
if check_port 8002; then
    echo -e "${GREEN}✅ CrewAI Service (8002): OK${NC}"
    if curl -s "${CREWAI_BASE_URL}/health" >/dev/null 2>&1; then
        echo -e "${GREEN}   🌟 Health check: OK${NC}"
    else
        echo -e "${YELLOW}   ⚠️ Health check: Aguardando...${NC}"
        services_ok=false
    fi
else
    echo -e "${RED}❌ CrewAI Service (8002): FALHOU${NC}"
    services_ok=false
fi

# Gatekeeper API
if check_port 8001; then
    echo -e "${GREEN}✅ Gatekeeper API (8001): OK${NC}"
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        echo -e "${GREEN}   🌟 Health check: OK${NC}"
    else
        echo -e "${YELLOW}   ⚠️ Health check: Aguardando...${NC}"
        services_ok=false
    fi
else
    echo -e "${RED}❌ Gatekeeper API (8001): FALHOU${NC}"
    services_ok=false
fi

# Frontend Original (Vite)
if check_port 8080; then
    echo -e "${GREEN}✅ Frontend Original (8080): OK${NC}"
else
    echo -e "${RED}❌ Frontend Original (8080): FALHOU${NC}"
    services_ok=false
fi

# Frontend JWT (Next.js)
if check_port 3000; then
    echo -e "${GREEN}✅ Frontend JWT (3000): OK${NC}"
else
    echo -e "${RED}❌ Frontend JWT (3000): FALHOU${NC}"
    services_ok=false
fi

echo "========================================"

if [ "$services_ok" = true ]; then
    echo -e "${GREEN}🎉 SISTEMA JWT INICIADO COM SUCESSO!${NC}"
    echo ""
    echo -e "${BLUE}📋 Ordem verificada: ${startup_sequence[*]}${NC}"
    echo ""
    echo -e "${BLUE}🌐 SISTEMA COMPLETO COM AMBOS FRONTENDS DISPONÍVEL:${NC}"
    echo ""
    echo -e "${YELLOW}📱 FRONTEND ORIGINAL (Vite - Sistema Completo):${NC}"
    echo -e "   🏠 Dashboard:          ${GREEN}http://localhost:8080${NC}"
    echo -e "   📊 Monitoramento:      ${GREEN}http://localhost:8080/monitoring${NC}"
    echo -e "   🔍 API Explorer:       ${GREEN}http://localhost:8080/api-explorer${NC}"
    echo -e "   🤖 Agent Tester:       ${GREEN}http://localhost:8080/agents${NC}"
    echo -e "   📋 Orders:             ${GREEN}http://localhost:8080/orders${NC}"
    echo -e "   🔍 Search:             ${GREEN}http://localhost:8080/search${NC}"
    echo ""
    echo -e "${YELLOW}🔐 FRONTEND JWT (Next.js - Sistema de Autenticação):${NC}"
    echo -e "   🏠 Dashboard:          ${GREEN}http://localhost:3000${NC}"
    echo -e "   🔐 Login JWT:          ${GREEN}http://localhost:3000/auth${NC}"
    echo -e "   💬 Chat Autenticado:   ${GREEN}http://localhost:3000/chat${NC}"
    echo ""
    echo -e "   📚 API Principal:      ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "   🚪 Gatekeeper API:     ${GREEN}http://localhost:8001/docs${NC}"
    echo ""
    echo -e "${YELLOW}🔑 FUNCIONALIDADES:${NC}"
    echo -e "   • Frontend Original: Sistema completo (8080)"
    echo -e "   • Frontend JWT: Sistema de autenticação (3000)"
    echo -e "   • Login JWT: Qualquer email (demo)"
    echo -e "   • Chat: Exclusivamente autenticado"
    echo -e "   • Tokens: JWT reais do Gatekeeper"
    echo ""
    echo -e "${YELLOW}🚀 ACESSO PRINCIPAL: http://localhost:8080${NC}"
    echo -e "${YELLOW}🔐 SISTEMA JWT: http://localhost:3000${NC}"
    echo ""
    echo -e "${BLUE}📝 Para parar o sistema, pressione Ctrl+C${NC}"

    # Manter script rodando
    trap 'echo -e "\n${YELLOW}🛑 Parando sistema JWT...${NC}"; kill $FRONTEND_JWT_PID $FRONTEND_ORIGINAL_PID $GATEKEEPER_PID $CREWAI_PID $API_MAIN_PID 2>/dev/null; exit 0' INT

    while true; do
        sleep 1
    done
else
    echo -e "${RED}❌ FALHA AO INICIAR ALGUNS SERVIÇOS${NC}"
    echo ""
    echo -e "${BLUE}🔍 LOGS PARA DEBUG:${NC}"
    echo -e "   📄 API Principal:      ${GREEN}tail -f /tmp/api-main.log${NC}"
    echo -e "   📄 CrewAI Service:     ${GREEN}tail -f /tmp/crewai.log${NC}"
    echo -e "   📄 Gatekeeper:         ${GREEN}tail -f /tmp/gatekeeper.log${NC}"
    echo -e "   📄 Frontend Original:  ${GREEN}tail -f /tmp/frontend-original.log${NC}"
    echo -e "   📄 Frontend JWT:       ${GREEN}tail -f /tmp/frontend-jwt.log${NC}"
    echo ""
    echo -e "${BLUE}💡 Verifique os logs para mais detalhes${NC}"
    exit 1
fi
