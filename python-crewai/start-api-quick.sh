#!/bin/bash

echo "⚡ MIT Tracking API - Start Rápido..."
echo "=================================="

# Parar containers existentes
docker stop mit-api-minimal 2>/dev/null || true
docker rm mit-api-minimal 2>/dev/null || true

# Build e start rápido
echo "🔨 Build e start da API (versão mínima)..."
docker-compose -f docker-compose-minimal.yml up --build -d

# Aguardar um pouco
sleep 10

# Status
echo ""
echo "📊 Status:"
docker ps --filter "name=mit-api-minimal" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Verificar health
echo ""
echo "🔍 Verificando health..."
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✅ API funcionando!"
else
    echo "⚠️  API ainda inicializando..."
fi

echo ""
echo "🌐 Endpoints:"
echo "  • GraphQL: http://localhost:8000/graphql"
echo "  • Health: http://localhost:8000/health"
echo "  • Docs: http://localhost:8000/docs"

echo ""
echo "🧪 Teste rápido:"
echo "curl http://localhost:8000/health"