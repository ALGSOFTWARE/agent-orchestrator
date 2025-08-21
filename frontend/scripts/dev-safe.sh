#!/bin/bash

# 🚀 Script de Inicialização Segura do Frontend MIT Logistics
# Resolve problemas comuns de primeira execução

set -e

echo "🔧 Iniciando frontend MIT Logistics com verificações de segurança..."

# 1. Verificar se estamos no diretório correto
if [ ! -f "package.json" ]; then
    echo "❌ Erro: Execute este script do diretório 'frontend'"
    exit 1
fi

# 2. Verificar Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt "18" ]; then
    echo "❌ Erro: Node.js 18+ necessário. Versão atual: $(node --version)"
    exit 1
fi

# 3. Limpar caches problemáticos
echo "🧹 Limpando caches..."
rm -rf .next
rm -rf node_modules/.cache
rm -rf tsconfig.tsbuildinfo

# 4. Verificar backend está rodando
echo "🔍 Verificando backend..."
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "⚠️  Backend não está rodando. Iniciando..."
    cd ../gatekeeper-api
    if [ ! -d "venv" ]; then
        echo "❌ Virtual env não encontrado. Execute setup do backend primeiro."
        exit 1
    fi
    source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > ../logs/backend.log 2>&1 &
    echo $! > ../logs/backend.pid
    cd ../frontend
    
    # Aguardar backend estar pronto
    echo "⏳ Aguardando backend ficar pronto..."
    for i in {1..30}; do
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            echo "✅ Backend está rodando!"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "❌ Timeout esperando backend"
            exit 1
        fi
        sleep 2
    done
fi

# 5. Verificar dependências
echo "📦 Verificando dependências..."
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    echo "📥 Instalando dependências..."
    npm ci --silent
fi

# 6. Verificar arquivos CSS Modules existem
echo "🎨 Verificando CSS Modules..."
CSS_MODULES_DIR="src/styles/modules"
if [ ! -d "$CSS_MODULES_DIR" ]; then
    echo "❌ Diretório CSS Modules não encontrado: $CSS_MODULES_DIR"
    exit 1
fi

# Contar arquivos CSS
CSS_COUNT=$(find $CSS_MODULES_DIR -name "*.module.css" | wc -l)
echo "✅ Encontrados $CSS_COUNT arquivos CSS Modules"

# 7. Pre-compilar TypeScript
echo "⚙️  Pre-compilando TypeScript..."
npx tsc --noEmit --skipLibCheck

# 8. Verificar portas disponíveis
echo "🔌 Verificando portas..."
if lsof -i :3000 > /dev/null 2>&1; then
    echo "⚠️  Porta 3000 em uso, Next.js usará 3001"
fi
if lsof -i :3001 > /dev/null 2>&1; then
    echo "❌ Porta 3001 também em uso!"
    echo "   Finalize processos: lsof -ti:3001 | xargs kill -9"
    exit 1
fi

# 9. Criar logs directory
mkdir -p ../logs

# 10. Iniciar Next.js com configurações otimizadas
echo "🚀 Iniciando Next.js..."
echo "   Frontend estará disponível em:"
echo "   • http://localhost:3000 (ou 3001 se 3000 ocupada)"
echo "   • Backend API: http://localhost:8001"
echo ""
echo "🔄 Se houver problemas, use Ctrl+C e execute novamente"
echo ""

# Configurar variáveis para melhor performance
export NODE_OPTIONS="--max-old-space-size=4096"
export NEXT_TELEMETRY_DISABLED=1

# Executar com retry automático
for attempt in {1..3}; do
    echo "🎯 Tentativa $attempt de 3..."
    if npm run dev; then
        break
    else
        if [ $attempt -lt 3 ]; then
            echo "❌ Falhou na tentativa $attempt. Limpando cache e tentando novamente..."
            rm -rf .next
            sleep 3
        else
            echo "❌ Todas as tentativas falharam."
            exit 1
        fi
    fi
done