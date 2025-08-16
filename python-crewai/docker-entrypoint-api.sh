#!/bin/bash

# Docker entrypoint para MIT Tracking API
set -e

echo "🚀 Iniciando MIT Tracking API..."
echo "=================================="

# Verificar variáveis de ambiente
echo "📋 Configurações:"
echo "  • API_PORT: ${API_PORT:-8000}"
echo "  • API_HOST: ${API_HOST:-0.0.0.0}"
echo "  • OLLAMA_BASE_URL: ${OLLAMA_BASE_URL:-http://localhost:11434}"
echo "  • OLLAMA_MODEL: ${OLLAMA_MODEL:-llama3.2:3b}"
echo "  • ENVIRONMENT: ${ENVIRONMENT:-development}"
echo "  • DEBUG: ${DEBUG:-false}"

# Aguardar Ollama estar disponível
if [ "${OLLAMA_BASE_URL}" != "disabled" ]; then
    echo "🔄 Aguardando Ollama estar disponível..."
    
    # Extrair host e porta da URL
    OLLAMA_HOST=$(echo $OLLAMA_BASE_URL | sed 's|http://||' | sed 's|https://||' | cut -d: -f1)
    OLLAMA_PORT=$(echo $OLLAMA_BASE_URL | sed 's|http://||' | sed 's|https://||' | cut -d: -f2)
    
    # Aguardar conexão
    timeout 120 bash -c "until curl -f $OLLAMA_BASE_URL/api/tags > /dev/null 2>&1; do sleep 2; done"
    
    if [ $? -eq 0 ]; then
        echo "✅ Ollama disponível em $OLLAMA_BASE_URL"
        
        # Verificar se modelo existe
        echo "🔍 Verificando modelo $OLLAMA_MODEL..."
        if curl -s "$OLLAMA_BASE_URL/api/tags" | grep -q "$OLLAMA_MODEL"; then
            echo "✅ Modelo $OLLAMA_MODEL está disponível"
        else
            echo "⚠️  Modelo $OLLAMA_MODEL não encontrado, tentando baixar..."
            curl -X POST "$OLLAMA_BASE_URL/api/pull" -d "{\"name\":\"$OLLAMA_MODEL\"}" || true
        fi
    else
        echo "⚠️  Timeout aguardando Ollama - continuando sem agent integration"
        export OLLAMA_BASE_URL="disabled"
    fi
else
    echo "ℹ️  Ollama desabilitado - API funcionará sem agent integration"
fi

# Verificar banco de dados
echo "📊 Verificando banco de dados..."
if [ -f "/app/database/cte_documents.json" ]; then
    echo "✅ Banco de dados mockado disponível"
else
    echo "⚠️  Banco de dados não encontrado"
fi

# Criar diretório de logs se não existir
mkdir -p /app/logs

# Definir configurações do uvicorn baseado no ambiente
if [ "${ENVIRONMENT}" = "production" ]; then
    echo "🏭 Iniciando em modo PRODUÇÃO..."
    UVICORN_ARGS="--workers 4 --access-log --log-level info"
else
    echo "🛠️  Iniciando em modo DESENVOLVIMENTO..."
    UVICORN_ARGS="--reload --log-level debug"
fi

echo "🎯 Executando comando: $@"
echo "=================================="

# Executar comando
exec "$@" $UVICORN_ARGS