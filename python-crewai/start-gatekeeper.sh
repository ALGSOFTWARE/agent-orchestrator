#!/bin/bash

# 🚪 Gatekeeper Agent Startup Script
# Sistema de Logística Inteligente

set -e

echo "🚪 Iniciando Gatekeeper Agent - Sistema de Logística Inteligente"
echo "=================================================================="

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
if [ ! -f "gatekeeper_agent.py" ]; then
    log_error "Script deve ser executado do diretório python-crewai"
    exit 1
fi

# Verificar Python
log_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 não encontrado. Instale Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
log_success "Python $PYTHON_VERSION encontrado"

# Verificar Ollama
log_info "Verificando Ollama..."
if ! command -v ollama &> /dev/null; then
    log_error "Ollama não encontrado. Instale: https://ollama.ai"
    exit 1
fi

# Verificar se Ollama está rodando
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    log_warning "Ollama não está rodando. Tentando iniciar..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 3
    
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_error "Falha ao iniciar Ollama"
        exit 1
    fi
    log_success "Ollama iniciado (PID: $OLLAMA_PID)"
else
    log_success "Ollama está rodando"
fi

# Verificar modelo llama3.2:3b
log_info "Verificando modelo llama3.2:3b..."
if ! ollama list | grep -q "llama3.2:3b"; then
    log_warning "Modelo llama3.2:3b não encontrado. Baixando..."
    ollama pull llama3.2:3b
    log_success "Modelo llama3.2:3b baixado"
else
    log_success "Modelo llama3.2:3b disponível"
fi

# Verificar dependências Python
log_info "Verificando dependências Python..."
if [ ! -f "requirements.txt" ]; then
    log_error "Arquivo requirements.txt não encontrado"
    exit 1
fi

# Instalar dependências se necessário
log_info "Instalando/verificando dependências..."
pip install -r requirements.txt > /dev/null 2>&1
log_success "Dependências verificadas"

# Verificar porta 8001
log_info "Verificando porta 8001..."
if lsof -Pi :8001 -sTCP:LISTEN -t > /dev/null 2>&1; then
    log_warning "Porta 8001 já está em uso"
    read -p "Deseja parar o processo existente? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PID=$(lsof -Pi :8001 -sTCP:LISTEN -t)
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
    log_info "Finalizando Gatekeeper Agent..."
    if [ ! -z "$GATEKEEPER_PID" ]; then
        kill $GATEKEEPER_PID 2>/dev/null || true
    fi
    if [ ! -z "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null || true
    fi
    log_success "Cleanup concluído"
}

# Configurar trap para cleanup
trap cleanup EXIT INT TERM

# Iniciar Gatekeeper Agent
log_info "Iniciando Gatekeeper Agent..."
echo ""
echo "🔗 Endpoints disponíveis:"
echo "   • Health Check: http://localhost:8001/health"
echo "   • System Info:  http://localhost:8001/info"
echo "   • Roles:        http://localhost:8001/roles"
echo "   • Auth Callback: http://localhost:8001/auth-callback"
echo "   • Docs:         http://localhost:8001/docs"
echo ""
echo "🧪 Para testar:"
echo "   python examples/gatekeeper_demo.py"
echo ""
echo "🛑 Para parar: Ctrl+C"
echo ""

# Executar Gatekeeper
python3 gatekeeper_agent.py &
GATEKEEPER_PID=$!

# Aguardar servidor inicializar
sleep 3

# Verificar se o servidor está respondendo
log_info "Verificando se o servidor está respondendo..."
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    log_success "Gatekeeper Agent está funcionando!"
    
    # Executar health check
    echo ""
    echo "📊 Status do Sistema:"
    curl -s http://localhost:8001/health | python3 -m json.tool
    
else
    log_error "Gatekeeper Agent não está respondendo"
    exit 1
fi

# Manter script rodando
log_info "Gatekeeper Agent rodando (PID: $GATEKEEPER_PID)"
log_info "Pressione Ctrl+C para parar..."

wait $GATEKEEPER_PID