#!/bin/bash

echo "🛠️  Iniciando MIT Tracking API localmente..."
echo "============================================"

# Verificar se está no diretório correto
if [ ! -f "requirements-api.txt" ]; then
    echo "❌ Execute este script do diretório python-crewai/"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado"
    exit 1
fi

# Verificar se ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
pip install --quiet -r requirements-api.txt

# Verificar Ollama (opcional)
OLLAMA_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
echo "🔍 Verificando Ollama em $OLLAMA_URL..."

if curl -f "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama disponível"
    export OLLAMA_BASE_URL="$OLLAMA_URL"
else
    echo "⚠️  Ollama não disponível - API funcionará sem agent integration"
    export OLLAMA_BASE_URL="disabled"
fi

# Configurar variáveis de ambiente
export API_PORT=8000
export API_HOST=127.0.0.1
export ENVIRONMENT=development
export DEBUG=true
export API_AUTH_ENABLED=false

echo "🚀 Iniciando API em http://$API_HOST:$API_PORT..."
echo ""
echo "📊 Endpoints disponíveis:"
echo "  • GraphQL: http://$API_HOST:$API_PORT/graphql"
echo "  • Docs: http://$API_HOST:$API_PORT/docs"
echo "  • Health: http://$API_HOST:$API_PORT/health"
echo ""
echo "🛑 Pressione Ctrl+C para parar"
echo ""

# Executar API
python -m uvicorn api.main:app \
    --host $API_HOST \
    --port $API_PORT \
    --reload \
    --log-level debug