#!/bin/bash

echo "📥 Baixando modelo llama3.2:3b no Ollama container..."

# Verificar se container Ollama está rodando
if ! docker ps | grep mit-ollama >/dev/null; then
    echo "❌ Container mit-ollama não está rodando"
    echo "💡 Execute ./start-interactive.sh primeiro"
    exit 1
fi

# Baixar modelo
echo "⏳ Baixando modelo (~2GB)... Pode demorar alguns minutos"
docker exec -it mit-ollama ollama pull llama3.2:3b

# Verificar se foi baixado
echo "✅ Verificando se modelo foi baixado..."
docker exec mit-ollama ollama list

echo "✅ Pronto! Volte para o terminal do agent e faça sua pergunta novamente"