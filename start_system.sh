#!/bin/bash

# 🚀 Script para inicializar o sistema completo MIT Logistics
# Execute com: bash start_system.sh

echo "🚀 Iniciando Sistema MIT Logistics..."
echo "=================================="

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar dependências
echo -e "${BLUE}📋 Verificando dependências...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python3 não encontrado. Instale Python 3.8+${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js não encontrado. Instale Node.js 18+${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ NPM não encontrado. Instale NPM${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependências verificadas${NC}"

# 1. Iniciar Backend - Gatekeeper API
echo -e "\n${BLUE}🔧 Iniciando Backend (Gatekeeper API)...${NC}"
cd gatekeeper-api

# Verificar se venv existe, senão criar
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Criando ambiente virtual Python...${NC}"
    python3 -m venv venv
fi

# Ativar venv
source venv/bin/activate

# Instalar dependências Python
echo -e "${YELLOW}📦 Instalando dependências Python...${NC}"
pip install -q fastapi uvicorn python-multipart beanie motor python-dotenv pydantic

# Iniciar API em background
echo -e "${GREEN}🚀 Iniciando API na porta 8001...${NC}"
python -m app.main &
API_PID=$!

# Aguardar API inicializar
sleep 5

# Testar se API está rodando
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ API rodando em http://localhost:8001${NC}"
else
    echo -e "${RED}❌ Erro ao inicializar API${NC}"
    kill $API_PID 2>/dev/null
    exit 1
fi

# 2. Iniciar Frontend
echo -e "\n${BLUE}🎨 Iniciando Frontend (Logistic Pulse)...${NC}"
cd ../logistic-pulse-31-main

# Instalar dependências Node.js
echo -e "${YELLOW}📦 Instalando dependências Node.js...${NC}"
npm install -q

# Verificar se axios está instalado (para API integration)
if ! npm list axios > /dev/null 2>&1; then
    echo -e "${YELLOW}📦 Instalando dependências de integração...${NC}"
    npm install -q axios @tanstack/react-query
fi

# Iniciar frontend em background
echo -e "${GREEN}🚀 Iniciando Frontend na porta 5173...${NC}"
npm run dev &
FRONTEND_PID=$!

# Aguardar frontend inicializar
sleep 8

echo -e "\n${GREEN}🎉 Sistema inicializado com sucesso!${NC}"
echo "=================================="
echo -e "${BLUE}🌐 Frontend:${NC} http://localhost:5173"
echo -e "${BLUE}🔧 API Docs:${NC} http://localhost:8001/docs"
echo -e "${BLUE}💬 Chat IA:${NC} http://localhost:5173 (aba Chat)"
echo ""
echo -e "${YELLOW}💡 Dicas:${NC}"
echo "• Use Ctrl+C para parar os serviços"
echo "• Logs da API: verifique o terminal"
echo "• Frontend auto-recarrega quando você edita arquivos"
echo ""
echo -e "${BLUE}🧪 Teste o chat com:${NC}"
echo "• 'Consultar CT-e da carga ABC123'"
echo "• 'Status da entrega para São Paulo'"
echo "• 'Mostrar documentos pendentes'"

# Função para cleanup quando script é interrompido
cleanup() {
    echo -e "\n${YELLOW}🛑 Parando serviços...${NC}"
    kill $API_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Serviços parados${NC}"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

# Manter script rodando
echo -e "${GREEN}✨ Sistema rodando... Pressione Ctrl+C para parar${NC}"
wait