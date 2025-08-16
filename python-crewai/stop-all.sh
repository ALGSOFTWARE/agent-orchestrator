#!/bin/bash

echo "🛑 Parando MIT Tracking - Sistema Completo..."
echo "============================================"

# Parar todos os perfis e serviços
echo "🔄 Parando serviços..."

# Parar com profile agent
docker-compose -f docker-compose-api.yml --profile agent down --remove-orphans

# Parar outros compose files como fallback
docker-compose -f docker-compose.yml down --remove-orphans 2>/dev/null || true
docker-compose -f docker-compose-full.yml down --remove-orphans 2>/dev/null || true

# Parar containers individuais se ainda estiverem rodando
echo "🧹 Verificando containers restantes..."
docker stop mit-api mit-ollama mit-agent 2>/dev/null || true
docker rm mit-api mit-ollama mit-agent 2>/dev/null || true

# Status final
RUNNING_CONTAINERS=$(docker ps --filter "name=mit-" --format "table {{.Names}}\t{{.Status}}" | tail -n +2)

if [ -z "$RUNNING_CONTAINERS" ]; then
    echo ""
    echo "✅ Todos os serviços MIT Tracking foram parados!"
    echo ""
    echo "🔧 Para iniciar novamente:"
    echo "  • Só API: ./start-api.sh"
    echo "  • Sistema completo: ./start-complete.sh"
    echo ""
else
    echo ""
    echo "⚠️  Alguns containers ainda rodando:"
    echo "$RUNNING_CONTAINERS"
    echo ""
    echo "🔧 Para forçar parada:"
    echo "  docker stop \$(docker ps -q --filter 'name=mit-')"
fi

# Opção de limpeza completa
echo ""
read -p "🗑️  Deseja remover volumes e imagens também? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Limpeza completa..."
    
    # Remover volumes
    docker volume rm $(docker volume ls -q | grep mit) 2>/dev/null || true
    
    # Remover imagens (opcional)
    echo "🗑️  Removendo imagens MIT Tracking..."
    docker rmi $(docker images --filter "reference=*mit*" -q) 2>/dev/null || true
    
    echo "✅ Limpeza completa realizada!"
fi

echo ""
echo "👋 MIT Tracking parado. Até logo!"