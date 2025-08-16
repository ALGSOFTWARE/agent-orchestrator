#!/bin/bash

echo "🚀 Iniciando MIT Tracking API com GraphQL..."
echo "=============================================="

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Limpar containers anteriores
echo "🧹 Limpando containers anteriores..."
docker-compose -f docker-compose-api.yml down --remove-orphans

# Construir e iniciar serviços
echo "🔨 Construindo e iniciando serviços..."
docker-compose -f docker-compose-api.yml up --build -d

# Aguardar serviços estarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# Verificar status dos serviços
echo "📊 Status dos serviços:"
docker-compose -f docker-compose-api.yml ps

echo ""
echo "✅ API inicializada com sucesso!"
echo ""
echo "🔗 Endpoints disponíveis:"
echo "  • API Principal: http://localhost:8000"
echo "  • GraphQL Playground: http://localhost:8000/graphql"
echo "  • API Docs (Swagger): http://localhost:8000/docs"
echo "  • ReDoc: http://localhost:8000/redoc"
echo "  • Health Check: http://localhost:8000/health"
echo "  • Métricas: http://localhost:8000/metrics"
echo ""
echo "🛠️  Comandos úteis:"
echo "  • Ver logs da API: docker logs -f mit-api"
echo "  • Ver logs do Ollama: docker logs -f mit-ollama"
echo "  • Iniciar com agente: ./start-complete.sh"
echo "  • Parar tudo: docker-compose -f docker-compose-api.yml down"
echo ""
echo "📖 Exemplo GraphQL Query:"
echo "  query { ctes { id numero_cte status } }"