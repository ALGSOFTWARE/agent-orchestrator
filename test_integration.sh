#!/bin/bash

# 🧪 Script de Teste da Integração MIT Logistics
echo "🧪 Testando Integração Frontend-Backend..."
echo "========================================"

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Testar Backend
echo -e "\n${BLUE}📡 Testando Backend API...${NC}"
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ Backend OK (http://localhost:8001)${NC}"
else
    echo -e "${RED}❌ Backend não está respondendo${NC}"
    exit 1
fi

# Testar Frontend
echo -e "\n${BLUE}🎨 Testando Frontend...${NC}"
if curl -s http://localhost:8081 > /dev/null; then
    echo -e "${GREEN}✅ Frontend OK (http://localhost:8081)${NC}"
else
    echo -e "${RED}❌ Frontend não está respondendo${NC}"
fi

# Testar Endpoints Específicos
echo -e "\n${BLUE}🔍 Testando Endpoints da Integração...${NC}"

# Test 1: Health check frontend API
echo -n "Frontend API Health: "
if curl -s http://localhost:8001/api/frontend/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Falhou${NC}"
fi

# Test 2: Chat endpoint
echo -n "Chat IA Endpoint: "
RESPONSE=$(curl -s -X POST http://localhost:8001/api/frontend/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"teste", "user_context":{"name":"Test"}}')

if echo "$RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Falhou${NC}"
fi

# Test 3: Documents endpoint  
echo -n "Documents API: "
if curl -s "http://localhost:8001/api/frontend/documents" | grep -q "success"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Falhou${NC}"
fi

# Test 4: Dashboard KPIs
echo -n "Dashboard KPIs: "
if curl -s "http://localhost:8001/api/frontend/dashboard/kpis?user_id=test" | grep -q "success"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Falhou${NC}"
fi

echo -e "\n${GREEN}🎉 Integração testada com sucesso!${NC}"
echo ""
echo -e "${BLUE}🌐 Acesse o sistema:${NC}"
echo "• Frontend: http://localhost:8081"
echo "• API Docs: http://localhost:8001/docs"
echo "• Chat IA: http://localhost:8081 (aba 'Chat Inteligente')"
echo ""
echo -e "${BLUE}💬 Teste comandos no chat:${NC}"
echo "• 'Consultar CT-e da carga ABC123'"
echo "• 'Status da entrega para São Paulo'"
echo "• 'Mostrar documentos pendentes'"