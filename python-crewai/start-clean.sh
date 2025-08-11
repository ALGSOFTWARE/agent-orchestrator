#!/bin/bash

# MIT Tracking - Start Clean (para tudo e inicia limpo)

echo "🧹 MIT Tracking - Start Clean"
echo "=============================="

# 1. Parar Ollama local se estiver rodando
echo "🛑 Parando Ollama local..."
pkill -f ollama 2>/dev/null || true
sudo systemctl stop ollama 2>/dev/null || true
echo "✅ Ollama local parado"

# 2. Limpar containers Docker
echo "🐳 Limpando containers Docker..."
docker-compose -f docker-compose-full.yml down --remove-orphans --volumes 2>/dev/null || true
docker system prune -f --volumes 2>/dev/null || true
echo "✅ Containers limpos"

# 3. Verificar se porta está livre
echo "🔍 Verificando porta 11434..."
if lsof -i :11434 >/dev/null 2>&1; then
    echo "⚠️  Porta 11434 ainda ocupada, tentando liberar..."
    sudo fuser -k 11434/tcp 2>/dev/null || true
    sleep 2
fi

if ! lsof -i :11434 >/dev/null 2>&1; then
    echo "✅ Porta 11434 livre"
else
    echo "❌ Porta 11434 ainda ocupada. Pode ser necessário reiniciar o sistema"
    exit 1
fi

# 4. Iniciar serviços limpos
echo ""
echo "🚀 Iniciando MIT Tracking (tudo no Docker)..."
echo "📥 Primeira execução demora ~5-10 min (download do modelo)"
echo "⏱️  Usando configuração robusta (healthcheck mais paciente)"
echo "💡 Para parar: Ctrl+C"
echo ""

# Usar configuração simples que resolve problemas de healthcheck
echo "🔧 Usando docker-compose-simple.yml (sem healthcheck)"

# Iniciar com configuração simples
docker-compose -f docker-compose-simple.yml up --build

echo ""
echo "🧹 Limpando após encerramento..."
docker-compose -f docker-compose-simple.yml down --remove-orphans