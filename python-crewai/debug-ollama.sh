#!/bin/bash

# Debug Ollama Container Issues

echo "🔍 Debugando problema do Ollama..."
echo "=================================="

# 1. Verificar se Docker tem recursos suficientes
echo "📊 Recursos Docker:"
docker system df
echo ""

# 2. Tentar rodar Ollama sozinho primeiro
echo "🧪 Testando Ollama container sozinho..."
docker run --rm -d --name test-ollama -p 11434:11434 ollama/ollama:latest
sleep 10

# 3. Verificar logs do container
echo "📝 Logs do container:"
docker logs test-ollama
echo ""

# 4. Verificar se Ollama responde
echo "🔍 Testando conectividade:"
if curl -s http://localhost:11434/api/tags >/dev/null; then
    echo "✅ Ollama container funciona!"
    docker stop test-ollama
else
    echo "❌ Ollama container não responde"
    echo "📝 Logs completos:"
    docker logs test-ollama
    docker stop test-ollama 2>/dev/null || true
fi

echo ""
echo "💡 Diagnóstico:"
echo "- Se funcionou: problema é no healthcheck do compose"
echo "- Se não funcionou: problema no container Ollama"