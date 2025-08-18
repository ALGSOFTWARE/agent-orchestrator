#!/bin/bash

# 🚀 MIT Logistics Frontend - Production Startup Script

set -e

echo "🚀 MIT Logistics Frontend - Deploy Produção"
echo "============================================"

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
if [ ! -f "docker-compose.yml" ]; then
    log_error "Script deve ser executado do diretório frontend"
    exit 1
fi

# Verificar Docker
log_info "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    log_error "Docker não encontrado. Instale Docker"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    log_error "Docker daemon não está rodando"
    exit 1
fi

log_success "Docker está funcionando"

# Verificar Docker Compose
log_info "Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose não encontrado"
    exit 1
fi

log_success "Docker Compose encontrado"

# Verificar se Ollama model existe (se não estiver em container)
if command -v ollama &> /dev/null; then
    log_info "Verificando modelo Ollama..."
    if ! ollama list | grep -q "llama3.2:3b"; then
        log_warning "Modelo llama3.2:3b não encontrado localmente"
        log_info "Será baixado automaticamente no container"
    else
        log_success "Modelo llama3.2:3b disponível"
    fi
fi

# Função para cleanup ao sair
cleanup() {
    log_info "Cleanup em progresso..."
}

# Configurar trap para cleanup
trap cleanup EXIT INT TERM

# Parar containers existentes
log_info "Parando containers existentes..."
docker-compose down --remove-orphans 2>/dev/null || true

# Limpar imagens antigas (opcional)
read -p "🧹 Deseja limpar imagens Docker antigas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Limpando imagens Docker antigas..."
    docker system prune -f
    log_success "Limpeza concluída"
fi

# Build e start dos containers
log_info "Fazendo build das imagens..."
docker-compose build --no-cache

log_info "Iniciando containers..."
docker-compose up -d

# Aguardar containers inicializarem
log_info "Aguardando containers inicializarem..."
sleep 10

# Verificar status dos containers
log_info "Verificando status dos containers..."
docker-compose ps

# Aguardar Ollama baixar modelo se necessário
log_info "Verificando se Ollama está pronto..."
OLLAMA_READY=false
for i in {1..30}; do
    if docker-compose exec ollama ollama list | grep -q "llama3.2:3b" 2>/dev/null; then
        OLLAMA_READY=true
        break
    elif [ $i -eq 1 ]; then
        log_info "Baixando modelo llama3.2:3b (pode demorar alguns minutos)..."
        docker-compose exec ollama ollama pull llama3.2:3b &
    fi
    sleep 10
done

if [ "$OLLAMA_READY" = true ]; then
    log_success "Ollama está pronto com modelo llama3.2:3b"
else
    log_warning "Ollama ainda está configurando. Verifique os logs."
fi

# Verificar health checks
log_info "Verificando health checks..."
sleep 5

# Verificar cada serviço
services=("nginx" "frontend" "graphql-api" "gatekeeper" "ollama")
for service in "${services[@]}"; do
    if docker-compose ps $service | grep -q "healthy\|Up"; then
        log_success "$service está funcionando"
    else
        log_warning "$service pode estar com problemas"
    fi
done

# Mostrar informações finais
echo ""
log_success "🚀 MIT Logistics Frontend - Produção"
echo ""
echo "🔗 URLs disponíveis:"
echo "   • 🌐 Frontend Principal:  http://localhost"
echo "   • 📊 GraphQL Playground:  http://localhost/api/graphql"
echo "   • 🚪 Gatekeeper API:      http://localhost/gatekeeper"
echo "   • 🧠 Ollama API:          http://localhost/ollama"
echo "   • 📈 Prometheus:          http://localhost:9090"
echo "   • 📊 Grafana:             http://localhost:3001 (admin/admin123)"
echo ""
echo "🛠️ Comandos úteis:"
echo "   • docker-compose logs -f [service]  # Ver logs"
echo "   • docker-compose ps                 # Status containers"
echo "   • docker-compose down               # Parar tudo"
echo "   • docker-compose restart [service]  # Reiniciar serviço"
echo ""
echo "📊 Monitoramento:"
echo "   • Health Check: http://localhost/health"
echo "   • Nginx Status: http://localhost/nginx-status"
echo ""

# Mostrar logs em tempo real
log_info "Mostrando logs dos principais serviços..."
echo "🛑 Para parar: Ctrl+C"
echo ""

# Seguir logs dos serviços principais
docker-compose logs -f nginx frontend graphql-api gatekeeper