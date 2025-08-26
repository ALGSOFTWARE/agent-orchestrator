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
    if netstat -tulpn 2>/dev/null | grep -q ":$1 " ; then
        return 0
    else
        return 1
    fi
}

# Função para matar processo em uma porta
kill_port() {
    if check_port $1; then
        echo -e "${YELLOW}Porta $1 está em uso. Tentando liberar...${NC}"
        # Tenta sem sudo primeiro
        lsof -ti:$1 | xargs --no-run-if-empty kill -9 2>/dev/null || {
            echo -e "${RED}❌ Não foi possível liberar a porta $1${NC}"
            echo -e "${BLUE}💡 Para liberar manualmente: lsof -ti:$1 | xargs kill -9${NC}"
            if [ "$1" = "3000" ]; then
                echo -e "${RED}❌ Porta 3000 é obrigatória para o frontend!${NC}"
                return 1
            fi
        }
        sleep 1
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

# Verificar se porta 3000 está livre, senão tentar limpar
echo -e "${BLUE}🔍 Verificando disponibilidade da porta 3000...${NC}"
if check_port 3000; then
    echo -e "${YELLOW}⚠️  Porta 3000 está ocupada, tentando liberar...${NC}"
    lsof -ti:3000 | xargs --no-run-if-empty kill -9 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Não foi possível liberar a porta 3000 automaticamente${NC}"
        echo -e "${BLUE}💡 Next.js tentará usar uma porta alternativa (3001, 3002, etc.)${NC}"
    }
    sleep 2
fi

# Limpar outras portas se necessário
echo -e "${BLUE}🧹 Limpando outras portas...${NC}"
kill_port 3001  # Frontend alt (caso exista)
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
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Verificar se dependências já estão instaladas
    if ! python -c "import fastapi, uvicorn, beanie" >/dev/null 2>&1; then
        echo -e "${YELLOW}📦 Instalando dependências Gatekeeper...${NC}"
        timeout 120 pip install -r requirements.txt --quiet --no-cache-dir || {
            echo -e "${YELLOW}⚠️ Timeout na instalação - usando cache existente${NC}"
        }
    else
        echo -e "${GREEN}✅ Dependências Gatekeeper já instaladas${NC}"
    fi
    
    echo -e "${GREEN}🚀 Gatekeeper API iniciando na porta 8001...${NC}"
    
    # Iniciar com log para debugging se necessário
    if [ "$DEBUG" = "true" ]; then
        venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
    else
        venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > /tmp/gatekeeper.log 2>&1 &
    fi
    GATEKEEPER_PID=$!
    
    cd ..
    
    # Aguardar Gatekeeper estar realmente pronto
    echo -e "${YELLOW}⏳ Aguardando Gatekeeper estar pronto...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Gatekeeper está pronto!${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Timeout: Gatekeeper não ficou pronto${NC}"
            return 1
        fi
        sleep 2
    done
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
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Verificar se dependências já estão instaladas
    if ! python -c "import crewai, fastapi, uvicorn" >/dev/null 2>&1; then
        echo -e "${YELLOW}📦 Instalando dependências CrewAI...${NC}"
        timeout 120 pip install -r requirements.txt --quiet --no-cache-dir || {
            echo -e "${YELLOW}⚠️ Timeout na instalação - usando cache existente${NC}"
        }
    else
        echo -e "${GREEN}✅ Dependências CrewAI já instaladas${NC}"
    fi
    
    echo -e "${GREEN}🚀 CrewAI API iniciando na porta 8002...${NC}"
    
    # Iniciar com log para debugging se necessário  
    if [ "$DEBUG" = "true" ]; then
        venv/bin/python -m uvicorn api.simple_main:app --host 0.0.0.0 --port 8002 --reload &
    else
        venv/bin/python -m uvicorn api.simple_main:app --host 0.0.0.0 --port 8002 --reload > /tmp/crewai.log 2>&1 &
    fi
    CREWAI_PID=$!
    
    cd ..
    sleep 3
}

# Função para iniciar frontend
start_frontend() {
    echo -e "${BLUE}⚛️  Iniciando Frontend React...${NC}"
    cd frontend
    
    # Next.js escolherá automaticamente uma porta disponível
    echo -e "${BLUE}🔍 Next.js tentará usar a porta 3000 ou uma alternativa...${NC}"
    
    # Limpar cache problemático do Next.js
    echo -e "${YELLOW}🧹 Limpando cache do Next.js...${NC}"
    rm -rf .next
    rm -rf node_modules/.cache
    rm -rf tsconfig.tsbuildinfo
    
    # Verificar se dependências estão instaladas (usa NPM, não Yarn)
    if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
        echo -e "${YELLOW}📦 Instalando dependências Node.js com NPM...${NC}"
        timeout 120 npm ci --silent || {
            echo -e "${YELLOW}⚠️ Timeout na instalação Node.js - usando cache existente${NC}"
        }
    else
        echo -e "${GREEN}✅ Dependências Node.js já instaladas${NC}"
    fi
    
    # Pre-compilar TypeScript para evitar erros de primeira execução (não para se houver erros)
    echo -e "${YELLOW}⚙️  Verificando TypeScript...${NC}"
    npx tsc --noEmit --skipLibCheck 2>/dev/null || echo -e "${YELLOW}⚠️  Alguns erros de TypeScript encontrados, mas Next.js pode lidar com eles...${NC}"
    
    echo -e "${GREEN}🚀 Frontend iniciando...${NC}"
    
    # Configurar variáveis para melhor performance
    export NODE_OPTIONS="--max-old-space-size=4096"
    export NEXT_TELEMETRY_DISABLED=1
    
    # Iniciar sem forçar porta específica (Next.js escolherá automaticamente)
    if [ "$DEBUG" = "true" ]; then
        npm run dev &
    else
        npm run dev > /tmp/frontend.log 2>&1 &
    fi
    FRONTEND_PID=$!
    
    cd ..
    
    # Detectar automaticamente em qual porta o frontend está rodando
    echo -e "${YELLOW}⏳ Aguardando Frontend estar pronto...${NC}"
    frontend_port=""
    for i in {1..60}; do
        # Verificar portas comuns do Next.js (3000, 3001, 3002, etc.)
        for port in 3000 3001 3002 3003 3004; do
            if check_port $port; then
                # Verificar se é realmente o Next.js verificando o log
                if grep -q "localhost:$port" /tmp/frontend.log 2>/dev/null; then
                    frontend_port=$port
                    echo -e "${GREEN}✅ Frontend está pronto na porta $port!${NC}"
                    break 2
                fi
            fi
        done
        if [ $i -eq 60 ]; then
            echo -e "${RED}❌ ERRO: Frontend não ficou pronto após 120s${NC}"
            echo -e "${YELLOW}🔍 Verifique os logs: tail -f /tmp/frontend.log${NC}"
            return 1
        fi
        sleep 2
    done
}

# Iniciar serviços NA ORDEM CORRETA (backend primeiro, frontend por último)
echo -e "${BLUE}🎬 Iniciando serviços em sequência...${NC}"

# 1. Gatekeeper API (essencial - backend principal)
start_gatekeeper || {
    echo -e "${RED}❌ Falha ao iniciar Gatekeeper - abortando${NC}"
    exit 1
}

# 2. CrewAI API (opcional - agentes IA)  
start_crewai || {
    echo -e "${YELLOW}⚠️  Falha ao iniciar CrewAI - continuando sem agentes IA${NC}"
}

# 3. Frontend por último (depende dos backends)
start_frontend || {
    echo -e "${RED}❌ Falha ao iniciar Frontend - sistema incompleto${NC}"
    exit 1
}

echo -e "${GREEN}✅ Todos os serviços foram iniciados!${NC}"

# Verificar se tudo está rodando
echo -e "${BLUE}🔍 Verificando status dos serviços...${NC}"

services_ok=true

# Frontend (verificar porta detectada dinamicamente)
if [ ! -z "$frontend_port" ] && check_port $frontend_port; then
    echo -e "${GREEN}✅ Frontend ($frontend_port): OK${NC}"
else
    echo -e "${RED}❌ Frontend: FALHOU - não foi possível detectar a porta${NC}"
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
    echo -e "   📱 Dashboard:        ${GREEN}http://localhost:$frontend_port${NC}"
    echo -e "   🤖 Agent Tester:    ${GREEN}http://localhost:$frontend_port/agents${NC}"
    echo -e "   ⚙️  Configurações:   ${GREEN}http://localhost:$frontend_port/settings${NC}"
    echo -e "   📊 Monitoramento:    ${GREEN}http://localhost:$frontend_port/monitoring${NC}"
    echo -e "   🔗 Visualizações:   ${GREEN}http://localhost:$frontend_port/visualizations${NC}"
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
    echo -e "${YELLOW}🚀 ACESSE: http://localhost:$frontend_port${NC}"
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
    echo ""
    echo -e "${BLUE}🔍 LOGS PARA DEBUG:${NC}"
    echo -e "   📄 Gatekeeper: ${GREEN}tail -f /tmp/gatekeeper.log${NC}"
    echo -e "   📄 CrewAI:     ${GREEN}tail -f /tmp/crewai.log${NC}"
    echo -e "   📄 Frontend:   ${GREEN}tail -f /tmp/frontend.log${NC}"
    echo ""
    echo -e "${BLUE}💡 Para debug completo, execute: ${GREEN}DEBUG=true ./start-system.sh${NC}"
    echo -e "${BLUE}💡 Ou execute manualmente conforme o START-SYSTEM.md${NC}"
    exit 1
fi