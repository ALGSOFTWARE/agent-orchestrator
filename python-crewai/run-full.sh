#!/bin/bash

# MIT Tracking - Tudo em Docker (Ollama + Agent)

echo "🐳 MIT Tracking - Execução Completa Docker"
echo "=========================================="
echo "📦 Ollama + MIT Agent + Modelo - Tudo em Docker"
echo ""

# Verificar se Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado!"
    echo "💡 Instale o Docker primeiro"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado!"
    echo "💡 Instale o Docker Compose primeiro"
    exit 1
fi

echo "✅ Docker e Docker Compose encontrados!"

# Cleanup se houver containers rodando
echo "🧹 Limpando containers anteriores..."
docker-compose -f docker-compose-full.yml down --remove-orphans > /dev/null 2>&1

echo "📥 Iniciando serviços (pode demorar na primeira vez)..."
echo "   1️⃣  Subindo Ollama server..."
echo "   2️⃣  Baixando modelo llama3.2:3b (~2GB)..."
echo "   3️⃣  Iniciando MIT Tracking Agent..."
echo ""
echo "⏱️  Aguarde... (primeira execução pode levar 5-10 minutos)"
echo ""

# Subir todos os serviços
docker-compose -f docker-compose-full.yml up --build

echo ""
echo "🧹 Limpando..."
docker-compose -f docker-compose-full.yml down --remove-orphans