#!/bin/bash
# Script de Deploy Manual (alternativa ao GitHub Actions)
# Uso: ./deploy.sh [staging|production]

set -e

ENV=${1:-staging}
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Validar parâmetros
if [[ "$ENV" != "staging" && "$ENV" != "production" ]]; then
    error "Uso: $0 [staging|production]"
fi

# Configurações por ambiente
if [[ "$ENV" == "staging" ]]; then
    HOST="ec2-13-217-85-36.compute-1.amazonaws.com"
    BRANCH="dev"
    DB_NAME="mit_logistics"
    NODE_ENV="staging"
    DEBUG="false"
    LOG_LEVEL="INFO"
elif [[ "$ENV" == "production" ]]; then
    HOST="ec2-13-217-85-36.compute-1.amazonaws.com" # Alterar para produção
    BRANCH="main"
    DB_NAME="mit_logistics_prod"
    NODE_ENV="production"
    DEBUG="false"
    LOG_LEVEL="WARNING"
fi

log "🚀 Iniciando deploy para $ENV"
log "Host: $HOST"
log "Branch: $BRANCH"

# Verificar se a chave SSH existe
if [[ ! -f "mit-api-key.pem" ]]; then
    error "Chave SSH 'mit-api-key.pem' não encontrada!"
fi

# Verificar se pode conectar no servidor
log "🔍 Testando conexão SSH..."
if ! ssh -i mit-api-key.pem -o ConnectTimeout=10 ubuntu@$HOST "echo 'Conexão OK'" > /dev/null 2>&1; then
    error "Não foi possível conectar no servidor $HOST"
fi

log "✅ Conexão SSH estabelecida"

# Criar pacote para deploy
log "📦 Criando pacote de deploy..."
tar -czf gatekeeper-api-$TIMESTAMP.tar.gz \
    --exclude='gatekeeper-api/venv' \
    --exclude='gatekeeper-api/__pycache__' \
    --exclude='gatekeeper-api/.env' \
    gatekeeper-api/

log "📤 Enviando código para servidor..."
scp -i mit-api-key.pem gatekeeper-api-$TIMESTAMP.tar.gz ubuntu@$HOST:/home/ubuntu/

log "🔧 Executando deploy no servidor..."
ssh -i mit-api-key.pem ubuntu@$HOST << EOF
set -e

# Função de log no servidor
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] \$1"
}

cd /home/ubuntu

# Backup da versão atual
if [ -d "gatekeeper-api" ]; then
    log "📋 Fazendo backup da versão atual..."
    sudo mv gatekeeper-api gatekeeper-api-backup-$TIMESTAMP
fi

# Extrair nova versão
log "📂 Extraindo nova versão..."
tar -xzf gatekeeper-api-$TIMESTAMP.tar.gz

# Instalar/atualizar dependências
cd gatekeeper-api
log "🐍 Configurando ambiente Python..."

# Criar venv se não existir
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Ativar venv e instalar dependências
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Criar arquivo .env
log "⚙️ Configurando variáveis de ambiente..."
cat > .env << EOL
# Database
MONGODB_URL=$MONGODB_URL
DATABASE_NAME=$DB_NAME

# API Keys
OPENAI_API_KEY=$OPENAI_API_KEY
GEMINI_API_KEY=$GEMINI_API_KEY

# App Config
NODE_ENV=$NODE_ENV
DEBUG=$DEBUG
LOG_LEVEL=$LOG_LEVEL
APP_NAME=MIT_Tracking_Agent
APP_VERSION=2.0.0

# LLM Config
LLM_PREFERRED_PROVIDER=auto
LLM_MAX_DAILY_COST=50
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1000

# Logistics
LOGISTICS_DOMAIN=mit-tracking
SUPPORTED_DOCUMENT_TYPES=CTE,BL,CONTAINER
EOL

# Verificar se OCR está disponível
log "🔍 Verificando OCR..."
if ! command -v tesseract &> /dev/null; then
    log "⚠️ Tesseract não encontrado, instalando..."
    sudo apt update
    sudo apt install -y tesseract-ocr tesseract-ocr-por tesseract-ocr-eng libtesseract-dev
fi

# Restart dos serviços
log "🔄 Reiniciando serviços..."
sudo systemctl restart gatekeeper-api
sleep 3

# Verificar se está rodando
log "🏥 Verificando saúde da aplicação..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "✅ Aplicação está rodando corretamente!"
else
    log "❌ Aplicação não respondeu ao health check"
    sudo journalctl -u gatekeeper-api --no-pager -n 20
    exit 1
fi

# Restart Nginx
sudo systemctl reload nginx

# Limpeza
rm -f /home/ubuntu/gatekeeper-api-$TIMESTAMP.tar.gz

log "🎉 Deploy concluído com sucesso!"
log "🌍 URL: https://$HOST"
EOF

# Limpeza local
rm -f gatekeeper-api-$TIMESTAMP.tar.gz

log "🎯 Deploy para $ENV concluído!"
log "🌐 Acesse: https://$HOST"
log "📊 Health: https://$HOST/health"
log "📚 Docs: https://$HOST/docs"

# Verificar se está online
log "🔍 Verificação final..."
if curl -f https://$HOST/health > /dev/null 2>&1; then
    log "✅ API está online e respondendo!"
else
    warn "⚠️ API pode estar ainda inicializando. Aguarde alguns segundos."
fi