#!/bin/bash

echo "🧹 Limpeza de arquivos JavaScript/TypeScript..."
echo "================================================"

# Backup primeiro (opcional)
echo "📦 Criando backup..."
mkdir -p backup-js-ts
cp -r src/ backup-js-ts/src 2>/dev/null || true
cp -r agents/ backup-js-ts/agents 2>/dev/null || true
cp -r tests/ backup-js-ts/tests 2>/dev/null || true
cp *.js backup-js-ts/ 2>/dev/null || true
cp *.ts backup-js-ts/ 2>/dev/null || true
cp package*.json backup-js-ts/ 2>/dev/null || true

echo "✅ Backup criado em: backup-js-ts/"

# Remover arquivos JS/TS da raiz
echo "🗑️  Removendo arquivos JavaScript/TypeScript da raiz..."
rm -f *.js
rm -f *.ts
rm -f jest.config.*

# Remover pastas TypeScript
echo "🗑️  Removendo pasta src/ (TypeScript)..."
rm -rf src/

echo "🗑️  Removendo pasta agents/ (JavaScript)..."
rm -rf agents/

echo "🗑️  Removendo pasta tests/ (TypeScript)..."
rm -rf tests/

# Remover node_modules e arquivos relacionados
echo "🗑️  Removendo node_modules e dependências..."
rm -rf node_modules/
rm -f package.json
rm -f package-lock.json
rm -f tsconfig.json

echo ""
echo "✅ Limpeza concluída!"
echo "📁 Estrutura atual:"
ls -la | grep -v backup-js-ts | head -20

echo ""
echo "💡 Arquivos preservados:"
echo "  • python-crewai/ - Projeto Python principal"
echo "  • backup-js-ts/ - Backup dos arquivos removidos"
echo "  • README.md, CLAUDE.md, etc. - Documentação"

echo ""
echo "🚀 Agora o projeto é 100% Python!"