#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Parando todos os serviços do MIT Tracking System...${NC}"

# Função para matar processo em uma porta
kill_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}   - Matando processo na porta $1...${NC}"
        lsof -ti:$1 | xargs --no-run-if-empty kill -9
        echo -e "${GREEN}   - Processo na porta $1 finalizado.${NC}"
    else
        echo -e "${GREEN}   - Nenhuma processo na porta $1.${NC}"
    fi
}

# Matar Frontend (porta 3000)
kill_port 3000

# Matar Gatekeeper API (porta 8001)
kill_port 8001

# Matar CrewAI API (porta 8002)
kill_port 8002

echo -e "${GREEN}✅ Sistema parado com sucesso!${NC}"
