#!/bin/bash

echo "🚀 Iniciando MIT Tracking - Versão Simplificada..."
echo "================================================="

# Verificar Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando"
    exit 1
fi

# Limpar primeiro
echo "🧹 Limpando ambiente..."
docker-compose -f docker-compose-api.yml down --remove-orphans 2>/dev/null || true

# Iniciar todos os serviços de uma vez
echo "🔨 Iniciando todos os serviços..."
docker-compose -f docker-compose-api.yml --profile agent up --build -d

# Aguardar um pouco
sleep 10

echo ""
echo "📊 Status dos Containers:"
docker ps --filter "name=mit" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ Sistema iniciado!"
echo ""
echo "🌐 Endpoints:"
echo "  • GraphQL: http://localhost:8000/graphql"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
echo "🤖 Para usar o agente:"
echo "  docker attach mit-agent"
echo ""
echo "🛑 Para parar tudo:"
echo "  ./stop-all.sh"

# Perguntar se quer conectar
echo ""
read -p "🔗 Conectar ao agente agora? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Verificar se container existe
    if docker ps | grep -q mit-agent; then
        echo "🤖 Conectando ao agente..."
        docker attach mit-agent
    else
        echo "❌ Container mit-agent não encontrado"
        echo "📋 Containers disponíveis:"
        docker ps --filter "name=mit"
    fi
fi