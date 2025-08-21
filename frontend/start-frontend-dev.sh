#!/bin/bash

# 🎨 MIT Logistics Frontend - Development Startup Script

set -e

echo "🎨 Iniciando MIT Logistics Frontend - Desenvolvimento"
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se estamos no diretório correto
if [ ! -f "package.json" ]; then
    log_error "Script deve ser executado do diretório frontend"
    exit 1
fi

# Verificar Node.js
log_info "Verificando Node.js..."
if ! command -v node &> /dev/null; then
    log_error "Node.js não encontrado. Instale Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$NODE_VERSION" -lt 18 ]; then
    log_error "Node.js 18+ é necessário. Versão atual: $(node -v)"
    exit 1
fi

log_success "Node.js $(node -v) encontrado"

# Verificar npm
log_info "Verificando npm..."
if ! command -v npm &> /dev/null; then
    log_error "npm não encontrado"
    exit 1
fi
log_success "npm $(npm -v) encontrado"

# Instalar dependências
log_info "Instalando dependências..."
npm install
log_success "Dependências instaladas"

# Verificar se backend está rodando
log_info "Verificando backend..."
BACKEND_RUNNING=false

# Verificar GraphQL API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    log_success "GraphQL API está rodando (porta 8000)"
    BACKEND_RUNNING=true
else
    log_warning "GraphQL API não está rodando (porta 8000)"
fi

# Verificar Gatekeeper
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    log_success "Gatekeeper Agent está rodando (porta 8001)"
    BACKEND_RUNNING=true
else
    log_warning "Gatekeeper Agent não está rodando (porta 8001)"
fi

if [ "$BACKEND_RUNNING" = false ]; then
    log_warning "Backend não está rodando. Para melhor experiência:"
    echo ""
    echo "🚀 Execute o sistema completo:"
    echo "   cd ../python-crewai && ./start-complete.sh"
    echo ""
    echo "🔧 Ou apenas as APIs:"
    echo "   cd ../python-crewai && ./start-api.sh"
    echo ""
    echo "⏳ Aguardando 5 segundos antes de continuar..."
    sleep 5
fi

# Verificar porta 3000
log_info "Verificando porta 3000..."
if lsof -Pi :3000 -sTCP:LISTEN -t > /dev/null 2>&1; then
    log_warning "Porta 3000 já está em uso"
    read -p "Deseja parar o processo existente? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PID=$(lsof -Pi :3000 -sTCP:LISTEN -t)
        kill $PID
        log_success "Processo anterior finalizado"
        sleep 2
    else
        log_error "Não é possível iniciar com porta ocupada"
        exit 1
    fi
fi

# Função para cleanup ao sair
cleanup() {
    log_info "Finalizando desenvolvimento..."
    # Matar processo Next.js se ainda estiver rodando
    pkill -f "next dev" 2>/dev/null || true
    log_success "Cleanup concluído"
}

# Configurar trap para cleanup
trap cleanup EXIT INT TERM

# Mostrar informações de desenvolvimento
echo ""
log_success "🎨 MIT Logistics Frontend - Modo Desenvolvimento"
echo ""
echo "🔗 URLs disponíveis:"
echo "   • Frontend:      http://localhost:3000"
echo "   • API GraphQL:   http://localhost:3000/api/graphql"
echo "   • Gatekeeper:    http://localhost:3000/gatekeeper"
echo "   • Health Check:  http://localhost:3000/health"
echo ""
echo "📁 Estrutura do projeto:"
echo "   • Dashboard:     http://localhost:3000/"
echo "   • Agentes:       http://localhost:3000/agents"
echo "   • Monitoramento: http://localhost:3000/monitoring"
echo "   • API Explorer:  http://localhost:3000/api-explorer"
echo ""
echo "🛠️ Comandos úteis:"
echo "   • npm run type-check  # Verificar tipos TypeScript"
echo "   • npm run lint        # Executar linter"
echo "   • npm run build       # Build de produção"
echo ""
echo "🛑 Para parar: Ctrl+C"
echo ""

# Iniciar desenvolvimento
log_info "Iniciando servidor de desenvolvimento..."

# Executar Next.js em modo desenvolvimento
npm run dev