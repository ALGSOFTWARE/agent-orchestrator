#!/bin/bash

# MIT Tracking - Start Interactive (com input do usuário)

echo "🧹 MIT Tracking - Start Interactive"
echo "==================================="

# 1. Parar Ollama local se estiver rodando
echo "🛑 Parando Ollama local..."
pkill -f ollama 2>/dev/null || true
sudo systemctl stop ollama 2>/dev/null || true

# 2. Limpar containers Docker
echo "🐳 Limpando containers Docker..."
docker-compose -f docker-compose-simple.yml down --remove-orphans --volumes 2>/dev/null || true

# 3. Verificar se porta está livre
echo "🔍 Verificando porta 11434..."
if lsof -i :11434 >/dev/null 2>&1; then
    sudo fuser -k 11434/tcp 2>/dev/null || true
    sleep 2
fi

# 4. Subir Ollama em background
echo "🚀 Subindo Ollama..."
docker-compose -f docker-compose-simple.yml up -d ollama

# 5. Aguardar Ollama ficar pronto
echo "⏳ Aguardando Ollama inicializar..."
sleep 90

# 6. Testar se Ollama está funcionando
echo "🔍 Testando Ollama..."
if ! docker exec mit-ollama ollama list >/dev/null 2>&1; then
    echo "❌ Ollama não respondeu, aguardando mais 30s..."
    sleep 30
fi

# 7. Executar agent em modo interativo
echo ""
echo "🚀 Iniciando MIT Agent (modo interativo)..."
echo "💬 Agora você pode digitar suas perguntas!"
echo ""

docker run -it --rm \
    --name mit-agent-interactive \
    --network python-crewai_default \
    -e OLLAMA_BASE_URL=http://mit-ollama:11434 \
    -e OLLAMA_MODEL=llama3.2:3b \
    -e PYTHONUNBUFFERED=1 \
    -e CREW_VERBOSE=true \
    -v "$(pwd):/app" \
    python-crewai-mit-orchestrator

echo ""
echo "🧹 Limpando após encerramento..."
docker-compose -f docker-compose-simple.yml down --remove-orphans