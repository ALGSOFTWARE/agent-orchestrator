#!/bin/bash

# MIT Tracking System v4.0 - Stop Script
# Para parar todos os serviços JWT do sistema

echo "🛑 Parando MIT Tracking System JWT..."
echo "========================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para matar processo em uma porta
kill_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}🔪 Matando processo na porta $1...${NC}"
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 1

        if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
            echo -e "${RED}   ❌ Falha ao parar porta $1${NC}"
        else
            echo -e "${GREEN}   ✅ Porta $1 liberada${NC}"
        fi
    else
        echo -e "${BLUE}   ℹ️ Porta $1 já estava livre${NC}"
    fi
}

# Parar serviços nas portas conhecidas
echo -e "${BLUE}📡 Parando serviços...${NC}"
kill_port 3000  # Frontend Next.js (JWT)
kill_port 8000  # API Principal
kill_port 8001  # Gatekeeper API
kill_port 8002  # CrewAI Service
kill_port 8080  # Frontend Original (Vite)

# Limpar logs temporários
echo -e "${BLUE}🧹 Limpando logs temporários...${NC}"
rm -f /tmp/api-main.log /tmp/gatekeeper.log /tmp/crewai.log /tmp/frontend-jwt.log /tmp/frontend-original.log 2>/dev/null

# Matar processos relacionados ao MIT system
echo -e "${BLUE}🔍 Procurando processos relacionados...${NC}"
pkill -f "uvicorn.*app.main:app" 2>/dev/null && echo -e "${GREEN}   ✅ Processos uvicorn (gatekeeper/api) parados${NC}" || echo -e "${BLUE}   ℹ️ Nenhum processo uvicorn (gatekeeper/api) encontrado${NC}"
pkill -f "uvicorn.*api.simple_main:app" 2>/dev/null && echo -e "${GREEN}   ✅ Processos uvicorn (CrewAI) parados${NC}" || echo -e "${BLUE}   ℹ️ Nenhum processo uvicorn (CrewAI) encontrado${NC}"
pkill -f "next.*dev" 2>/dev/null && echo -e "${GREEN}   ✅ Processos Next.js parados${NC}" || echo -e "${BLUE}   ℹ️ Nenhum processo Next.js encontrado${NC}"

echo "========================================"
echo -e "${GREEN}✅ Sistema JWT parado com sucesso!${NC}"
echo ""
echo -e "${BLUE}💡 Para reiniciar: ./start-system-jwt.sh${NC}"
