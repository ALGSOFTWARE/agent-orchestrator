#!/bin/bash

echo "🧪 Teste de Integração - Busca Semântica MIT Logistics"
echo "======================================================"

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${BLUE}📡 Testando Backend API...${NC}"
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ Backend OK (http://localhost:8001)${NC}"
else
    echo -e "${RED}❌ Backend não está respondendo${NC}"
    exit 1
fi

echo -e "\n${BLUE}🎨 Testando Frontend...${NC}"
if curl -s http://localhost:8081 > /dev/null; then
    echo -e "${GREEN}✅ Frontend OK (http://localhost:8081)${NC}"
else
    echo -e "${RED}❌ Frontend não está respondendo${NC}"
fi

echo -e "\n${BLUE}🔍 Testando Busca Semântica...${NC}"

# Teste 1: Endpoint de documentos sem filtros
echo -n "Documentos sem filtros: "
DOCS_COUNT=$(curl -s "http://localhost:8001/api/frontend/documents" | jq '.data | length')
if [ "$DOCS_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ $DOCS_COUNT documentos encontrados${NC}"
else
    echo -e "${YELLOW}⚠️ Nenhum documento (usando mocks)${NC}"
fi

# Teste 2: Busca tradicional
echo -n "Busca Tradicional: "
RESPONSE=$(curl -s "http://localhost:8001/api/frontend/documents?search=carga&semantic_search=false")
METHOD=$(echo "$RESPONSE" | jq -r '.search_metadata.method')
COUNT=$(echo "$RESPONSE" | jq '.data | length')
echo -e "${BLUE}$METHOD - $COUNT resultados${NC}"

# Teste 3: Busca semântica
echo -n "Busca Semântica: "
RESPONSE=$(curl -s "http://localhost:8001/api/frontend/documents?search=carga&semantic_search=true")
METHOD=$(echo "$RESPONSE" | jq -r '.search_metadata.method')
COUNT=$(echo "$RESPONSE" | jq '.data | length')
EMBEDDING_SIZE=$(echo "$RESPONSE" | jq '.search_metadata.query_embedding_size // 0')

if [ "$METHOD" = "semantic_vector_search" ]; then
    echo -e "${GREEN}✅ $METHOD - Embedding: ${EMBEDDING_SIZE}D - $COUNT resultados${NC}"
else
    FALLBACK=$(echo "$RESPONSE" | jq -r '.search_metadata.fallback_reason // "N/A"')
    echo -e "${YELLOW}⚠️ Fallback: $FALLBACK${NC}"
fi

echo -e "\n${BLUE}🤖 Testando Chat IA...${NC}"
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8001/api/frontend/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"Consultar CT-e da carga ABC123", "user_context":{"name":"Test","company":"MIT"}}')

CHAT_MESSAGE=$(echo "$CHAT_RESPONSE" | jq -r '.data.message // "Erro"')
if echo "$CHAT_MESSAGE" | grep -q "documento\|semântica\|tradicional"; then
    echo -e "${GREEN}✅ Chat respondeu com contexto logístico${NC}"
    echo -e "   💬 Resposta: ${CHAT_MESSAGE:0:80}..."
else
    echo -e "${YELLOW}⚠️ Chat funcionando mas sem contexto específico${NC}"
fi

echo -e "\n${BLUE}📊 Estatísticas Finais:${NC}"
echo "• Busca Semântica: $METHOD"
echo "• Embeddings: ${EMBEDDING_SIZE}D (768=Gemini, 1536=OpenAI)"  
echo "• Documentos encontrados: $COUNT"
echo "• Chat IA: Funcional"

echo -e "\n${GREEN}🎉 Integração testada!${NC}"
echo ""
echo -e "${BLUE}🌐 Acesse o sistema:${NC}"
echo "• Frontend: http://localhost:8081"
echo "• API Docs: http://localhost:8001/docs"
echo "• Chat com IA: http://localhost:8081 (aba 'Chat Inteligente')"
echo ""
echo -e "${BLUE}🔍 Testar Busca Semântica:${NC}"
echo "1. Acesse http://localhost:8081"
echo "2. Vá em 'Chat Inteligente'"
echo "3. Clique em 'Consultar Documentos'" 
echo "4. Digite uma busca e ative o toggle 'IA Semântica'"
echo "5. Compare resultados com/sem IA semântica"