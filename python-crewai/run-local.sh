#!/bin/bash

# MIT Tracking Python - Execução Local

echo "🚀 MIT Tracking Python Orchestrator - Local"
echo "============================================"

# Verificar se Ollama está rodando
echo "🔍 Verificando se Ollama está rodando..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama não está rodando!"
    echo "💡 Inicie o Ollama primeiro:"
    echo "   ollama serve"
    echo "   ollama pull llama3.2:3b"
    exit 1
fi

echo "✅ Ollama está rodando!"

# Verificar se Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado!"
    echo "💡 Instale o Docker primeiro"
    exit 1
fi

echo "✅ Docker encontrado!"

# Build da imagem se necessário
echo "🏗️  Verificando imagem Docker..."
if [[ "$(docker images -q python-crewai-mit-orchestrator 2> /dev/null)" == "" ]]; then
    echo "📦 Buildando imagem Docker..."
    docker build -t python-crewai-mit-orchestrator .
else
    echo "✅ Imagem já existe"
fi

# Rodar container em modo interativo
echo "🚀 Starting MIT Orchestrator (modo interativo)..."
echo "💡 Para sair: digite /sair ou Ctrl+C"
echo ""

docker run -it --rm \
    --name mit-orchestrator-local \
    --network="host" \
    -e OLLAMA_BASE_URL=http://localhost:11434 \
    -e OLLAMA_MODEL=llama3.2:3b \
    -e PYTHONUNBUFFERED=1 \
    python-crewai-mit-orchestrator

echo ""
echo "👋 Sessão encerrada!"