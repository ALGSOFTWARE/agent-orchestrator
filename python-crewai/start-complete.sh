#!/bin/bash

echo "🚀 Iniciando MIT Tracking - Sistema Completo..."
echo "=============================================="
echo "📦 API GraphQL + Agente Interativo + Ollama"
echo ""

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Verificar se está no diretório correto
if [ ! -f "docker-compose-api.yml" ]; then
    echo "❌ Execute este script do diretório python-crewai/"
    exit 1
fi

# Limpar containers anteriores
echo "🧹 Limpando containers e volumes anteriores..."
docker-compose -f docker-compose-api.yml down --remove-orphans --volumes
docker-compose -f docker-compose.yml down --remove-orphans --volumes 2>/dev/null || true

# Construir e iniciar TODOS os serviços
echo "🔨 Construindo e iniciando sistema completo..."
echo "   • Ollama (LLM local)"
echo "   • MIT Tracking API (GraphQL + OpenAPI)"
echo "   • MIT Interactive Agent (CLI)"
echo ""

# Iniciar API primeiro
echo "🔨 Iniciando API e Ollama..."
docker-compose -f docker-compose-api.yml up --build -d

# Aguardar API estar pronta antes de iniciar agente
echo "⏳ Aguardando API estar disponível..."
timeout 60 bash -c "
    while ! curl -f http://localhost:8000/health >/dev/null 2>&1; do 
        echo '   🔄 API ainda inicializando...'
        sleep 3
    done
"

# Aguardar Ollama estar pronto
echo "⏳ Aguardando Ollama inicializar..."
timeout 120 bash -c "
    while ! curl -f http://localhost:11434/api/tags >/dev/null 2>&1; do 
        echo '   🔄 Ollama ainda inicializando...'
        sleep 5
    done
"

if [ $? -eq 0 ]; then
    echo "✅ Ollama pronto!"
    
    # Verificar e baixar modelo se necessário
    echo "🔍 Verificando modelo llama3.2:3b..."
    if ! curl -s http://localhost:11434/api/tags | grep -q "llama3.2:3b"; then
        echo "📥 Baixando modelo llama3.2:3b (pode demorar alguns minutos)..."
        docker exec mit-ollama ollama pull llama3.2:3b
        echo "✅ Modelo baixado!"
    else
        echo "✅ Modelo llama3.2:3b já disponível!"
    fi
else
    echo "⚠️  Timeout aguardando Ollama - alguns recursos podem não funcionar"
fi

# Aguardar API estar pronta
echo "⏳ Aguardando API estar pronta..."
timeout 60 bash -c "
    while ! curl -f http://localhost:8000/health >/dev/null 2>&1; do 
        echo '   🔄 API ainda inicializando...'
        sleep 3
    done
"

if [ $? -eq 0 ]; then
    echo "✅ API pronta!"
else
    echo "⚠️  API pode ainda estar inicializando"
fi

# Agora iniciar o agente interativo
echo "🤖 Iniciando agente interativo..."
docker-compose -f docker-compose-api.yml --profile agent up -d

# Aguardar agente estar pronto
sleep 5

# Status dos serviços
echo ""
echo "📊 Status dos Serviços:"
docker-compose -f docker-compose-api.yml --profile agent ps

echo ""
echo "🎉 SISTEMA MIT TRACKING COMPLETAMENTE ATIVO!"
echo "=============================================="
echo ""
echo "🌐 ENDPOINTS DA API:"
echo "  • 🎮 GraphQL Playground: http://localhost:8000/graphql"
echo "  • 📚 API Docs (Swagger): http://localhost:8000/docs"
echo "  • 📖 ReDoc: http://localhost:8000/redoc"
echo "  • ✅ Health Check: http://localhost:8000/health"
echo "  • 📊 Métricas: http://localhost:8000/metrics"
echo ""
echo "🤖 AGENTE INTERATIVO:"
echo "  • Para usar: docker attach mit-agent"
echo "  • Para sair sem parar: Ctrl+P, Ctrl+Q"
echo ""
echo "🔧 COMANDOS ÚTEIS:"
echo "  • Ver logs API: docker logs -f mit-api"
echo "  • Ver logs Ollama: docker logs -f mit-ollama" 
echo "  • Ver logs Agent: docker logs -f mit-agent"
echo "  • Conectar Agent: docker attach mit-agent"
echo "  • Parar tudo: docker-compose -f docker-compose-api.yml --profile agent down"
echo ""
echo "📖 EXEMPLO GRAPHQL QUERY:"
echo "  query { ctes { numero_cte status transportadora { nome } } }"
echo ""
echo "🚀 Sistema completo rodando! Acesse os endpoints acima."

# Opção de conectar automaticamente ao agente
echo ""
read -p "🤖 Deseja conectar ao agente interativo agora? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔗 Conectando ao agente interativo..."
    echo "💡 Para sair sem parar o agente: Ctrl+P, depois Ctrl+Q"
    echo "⏸️  Para parar tudo: Ctrl+C e depois execute o comando de parar acima"
    sleep 2
    docker attach mit-agent
fi