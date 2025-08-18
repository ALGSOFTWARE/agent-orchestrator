#!/bin/bash

# 🔴 MIT Logistics - Kill All Services
# Mata todos os serviços nas portas 3001 e 8002

echo "🔴 Parando todos os serviços MIT Logistics..."
echo

# Função para matar processos em uma porta específica
kill_port() {
    local port=$1
    echo "🔍 Verificando porta $port..."
    
    # Tenta primeiro sem sudo
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        echo "📋 Processos encontrados na porta $port: $pids"
        
        # Tenta kill normal primeiro
        echo "⚡ Tentando kill normal..."
        kill $pids 2>/dev/null
        sleep 2
        
        # Verifica se ainda existem processos
        local remaining=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$remaining" ]; then
            echo "💀 Kill normal falhou, usando kill -9..."
            kill -9 $remaining 2>/dev/null
            sleep 1
            
            # Se ainda existem, tenta com sudo
            remaining=$(lsof -ti:$port 2>/dev/null)
            if [ ! -z "$remaining" ]; then
                echo "🔐 Tentando com sudo..."
                sudo kill -9 $remaining 2>/dev/null
                sleep 1
            fi
        fi
        
        # Verificação final
        final_check=$(lsof -ti:$port 2>/dev/null)
        if [ -z "$final_check" ]; then
            echo "✅ Porta $port liberada com sucesso!"
        else
            echo "❌ Ainda há processos na porta $port"
        fi
    else
        echo "✅ Porta $port já está livre"
    fi
    echo
}

# Mata processos específicos por nome também
echo "🔍 Procurando processos por nome..."

# Mata processos Node.js relacionados ao Next.js
echo "📱 Matando processos Next.js..."
pkill -f "next-server" 2>/dev/null && echo "✅ Next.js server morto" || echo "ℹ️  Nenhum processo Next.js encontrado"

# Mata processos Python/uvicorn
echo "🐍 Matando processos Python/uvicorn..."
pkill -f "uvicorn.*api.main" 2>/dev/null && echo "✅ Uvicorn server morto" || echo "ℹ️  Nenhum processo uvicorn encontrado"

# Mata processos npm/node genéricos relacionados
echo "📦 Matando processos npm..."
pkill -f "npm.*dev" 2>/dev/null && echo "✅ npm dev morto" || echo "ℹ️  Nenhum processo npm dev encontrado"

echo

# Mata processos nas portas específicas
kill_port 3001
kill_port 8002

# Mata também portas comuns que podem estar em uso
echo "🧹 Limpando outras portas comuns..."
kill_port 3000
kill_port 8001
kill_port 8000

echo "=========================================="
echo "🔍 Status final das portas:"
echo

for port in 3000 3001 8000 8001 8002; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "❌ Porta $port: AINDA EM USO"
        lsof -ti:$port | head -3
    else
        echo "✅ Porta $port: LIVRE"
    fi
done

echo
echo "🏁 Limpeza concluída!"
echo "💡 Agora você pode executar o ./start-complete.sh"
echo