#!/bin/bash

# 🚀 MIT Logistics Frontend - Script de Desenvolvimento Simplificado

echo "🚀 Iniciando MIT Logistics Frontend..."

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale Node.js 18+ primeiro."
    exit 1
fi

# Verificar se npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado. Instale npm primeiro."
    exit 1
fi

# Instalar dependências
echo "📦 Instalando dependências..."
npm install

# Verificar se a instalação foi bem-sucedida
if [ $? -ne 0 ]; then
    echo "❌ Falha ao instalar dependências."
    exit 1
fi

echo "✅ Dependências instaladas com sucesso!"

# Iniciar servidor de desenvolvimento
echo "🚀 Iniciando servidor de desenvolvimento na porta 3000..."
echo "🌐 Abra http://localhost:3000 no seu navegador"
echo "⚠️  Nota: Alguns recursos (APIs) podem não funcionar sem o backend"

npm run dev