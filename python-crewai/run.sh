#!/bin/bash

# MIT Tracking Python Orchestrator - Docker Runner

echo "🚀 MIT Tracking Python Orchestrator"
echo "===================================="

# Check if Ollama is running
echo "🔍 Verificando se Ollama está rodando..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama não está rodando!"
    echo "💡 Inicie o Ollama primeiro:"
    echo "   ollama serve"
    echo "   ollama pull llama3.2:3b"
    exit 1
fi

echo "✅ Ollama está rodando!"

# Build and run
echo "🏗️  Building Docker image..."
docker-compose build

echo "🚀 Starting MIT Orchestrator..."
docker-compose up --remove-orphans

# Cleanup on exit
echo "🧹 Cleaning up..."
docker-compose down