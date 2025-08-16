#!/bin/bash

# 🚀 MIT Logistics - Script de Deploy Completo para EC2
# Deploy automatizado do sistema MIT Logistics em instância EC2

echo "🚀 MIT Logistics - Deploy EC2"
echo "==============================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações padrão (podem ser sobrescritas via variáveis de ambiente)
EC2_USER=${EC2_USER:-ubuntu}
EC2_HOST=${EC2_HOST:-""}
EC2_KEY=${EC2_KEY:-"~/.ssh/id_rsa"}
DOMAIN=${DOMAIN:-""}
SSL_EMAIL=${SSL_EMAIL:-"admin@mitlogistics.com"}
GITHUB_REPO=${GITHUB_REPO:-""}
DEPLOY_ENV=${DEPLOY_ENV:-"production"}

# Funções auxiliares
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se os parâmetros obrigatórios foram fornecidos
check_requirements() {
    log_info "Verificando pré-requisitos..."

    if [ -z "$EC2_HOST" ]; then
        log_error "EC2_HOST não foi definido. Use: export EC2_HOST=your-ec2-ip-or-domain"
        exit 1
    fi

    if [ ! -f "$EC2_KEY" ]; then
        log_error "Chave SSH não encontrada em $EC2_KEY"
        exit 1
    fi

    # Testar conexão SSH
    log_info "Testando conexão SSH com $EC2_HOST..."
    if ! ssh -i "$EC2_KEY" -o ConnectTimeout=10 "$EC2_USER@$EC2_HOST" "echo 'Conexão OK'" &>/dev/null; then
        log_error "Não foi possível conectar via SSH em $EC2_HOST"
        log_info "Verifique se:"
        log_info "- A instância EC2 está rodando"
        log_info "- O Security Group permite SSH (porta 22)"
        log_info "- A chave SSH está correta: $EC2_KEY"
        exit 1
    fi

    log_success "Conexão SSH estabelecida com sucesso"
}

# Instalar dependências no servidor
install_dependencies() {
    log_info "Instalando dependências no servidor..."

    ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
        set -e
        
        # Atualizar sistema
        sudo apt update && sudo apt upgrade -y
        
        # Instalar dependências essenciais
        sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release
        
        # Instalar Node.js 18+
        if ! command -v node &> /dev/null; then
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt install -y nodejs
        fi
        
        # Instalar Python 3.9+
        if ! command -v python3.9 &> /dev/null; then
            sudo apt install -y python3.9 python3.9-pip python3.9-venv
        fi
        
        # Instalar Docker
        if ! command -v docker &> /dev/null; then
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt update
            sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            sudo usermod -aG docker $USER
        fi
        
        # Instalar Docker Compose
        if ! command -v docker-compose &> /dev/null; then
            sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
        fi
        
        # Instalar Nginx
        if ! command -v nginx &> /dev/null; then
            sudo apt install -y nginx
            sudo systemctl enable nginx
        fi
        
        # Instalar Ollama
        if ! command -v ollama &> /dev/null; then
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
        
        # Verificar instalações
        echo "✅ Node.js: $(node --version)"
        echo "✅ Python: $(python3.9 --version)"
        echo "✅ Docker: $(docker --version)"
        echo "✅ Docker Compose: $(docker-compose --version)"
        echo "✅ Nginx: $(nginx -v 2>&1)"
        echo "✅ Ollama: $(ollama --version 2>/dev/null || echo 'Instalado')"
EOF

    log_success "Dependências instaladas com sucesso"
}

# Configurar Ollama e baixar modelos
setup_ollama() {
    log_info "Configurando Ollama e baixando modelos..."

    ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
        set -e
        
        # Iniciar Ollama em background
        nohup ollama serve > /dev/null 2>&1 &
        sleep 10
        
        # Baixar modelos necessários
        ollama pull llama3.2:3b
        ollama pull mistral
        
        # Verificar modelos baixados
        ollama list
        
        # Criar service systemd para Ollama
        sudo tee /etc/systemd/system/ollama.service << 'SERVICE'
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

        sudo systemctl enable ollama
        sudo systemctl start ollama
EOF

    log_success "Ollama configurado e modelos baixados"
}

# Deploy da aplicação
deploy_application() {
    log_info "Fazendo deploy da aplicação..."

    # Criar diretório de deploy
    ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" "mkdir -p /home/$EC2_USER/mit-logistics"

    # Fazer upload dos arquivos do projeto
    log_info "Fazendo upload dos arquivos..."
    rsync -avz --progress -e "ssh -i $EC2_KEY" \
        --exclude 'node_modules' \
        --exclude '.next' \
        --exclude '__pycache__' \
        --exclude '.git' \
        --exclude '*.log' \
        . "$EC2_USER@$EC2_HOST:/home/$EC2_USER/mit-logistics/"

    # Configurar aplicação no servidor
    ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
        set -e
        cd /home/ubuntu/mit-logistics
        
        # Configurar frontend
        cd frontend
        npm install
        npm run build
        cd ..
        
        # Configurar backend Python
        cd python-crewai
        python3.9 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..
        
        # Criar arquivo de ambiente de produção
        cat > .env.production << 'ENVFILE'
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://api.mitlogistics.com
NEXT_PUBLIC_GATEKEEPER_URL=https://gatekeeper.mitlogistics.com
NEXT_PUBLIC_OLLAMA_URL=http://localhost:11434
PYTHONPATH=/home/ubuntu/mit-logistics/python-crewai
ENVFILE

        # Criar docker-compose para produção
        cat > docker-compose.prod.yml << 'COMPOSE'
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    depends_on:
      - backend

  backend:
    build:
      context: ./python-crewai
      dockerfile: Dockerfile.api
    ports:
      - "8001:8001"
    environment:
      - PYTHONPATH=/app
      - OLLAMA_HOST=http://host.docker.internal:11434
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
COMPOSE
EOF

    log_success "Aplicação deployada com sucesso"
}

# Configurar Nginx como reverse proxy
configure_nginx() {
    log_info "Configurando Nginx..."

    # Criar configuração do Nginx
    ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << EOF
        sudo tee /etc/nginx/sites-available/mit-logistics << 'NGINX'
# MIT Logistics - Nginx Configuration

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name ${DOMAIN:-_};
    return 301 https://\$server_name\$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name ${DOMAIN:-_};

    # SSL Configuration (se certificados estiverem disponíveis)
    # ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    # SSL Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend APIs
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Gatekeeper API
    location /gatekeeper/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Health checks
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
NGINX

        # Ativar site
        sudo ln -sf /etc/nginx/sites-available/mit-logistics /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
        
        # Testar configuração
        sudo nginx -t
        
        # Reiniciar Nginx
        sudo systemctl restart nginx
        sudo systemctl enable nginx
EOF

    log_success "Nginx configurado como reverse proxy"
}

# Configurar SSL com Let's Encrypt (opcional)
setup_ssl() {
    if [ -n "$DOMAIN" ]; then
        log_info "Configurando SSL com Let's Encrypt para $DOMAIN..."

        ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << EOF
            # Instalar Certbot
            sudo apt install -y certbot python3-certbot-nginx
            
            # Obter certificado SSL
            sudo certbot --nginx -d $DOMAIN --email $SSL_EMAIL --agree-tos --non-interactive
            
            # Configurar renovação automática
            sudo systemctl enable certbot.timer
EOF

        log_success "SSL configurado para $DOMAIN"
    else
        log_warning "DOMAIN não definido, pulando configuração SSL"
    fi
}

# Criar scripts de gerenciamento
create_management_scripts() {
    log_info "Criando scripts de gerenciamento..."

    ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
        cd /home/ubuntu/mit-logistics
        
        # Script de start
        cat > start-production.sh << 'START'
#!/bin/bash
echo "🚀 Iniciando MIT Logistics em produção..."

# Iniciar Ollama
sudo systemctl start ollama
sleep 5

# Iniciar aplicações via Docker Compose
docker-compose -f docker-compose.prod.yml up -d

echo "✅ MIT Logistics iniciado!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8001"
START

        # Script de stop
        cat > stop-production.sh << 'STOP'
#!/bin/bash
echo "🛑 Parando MIT Logistics..."

# Parar Docker Compose
docker-compose -f docker-compose.prod.yml down

echo "✅ MIT Logistics parado!"
STOP

        # Script de status
        cat > status.sh << 'STATUS'
#!/bin/bash
echo "📊 Status do MIT Logistics"
echo "=========================="

echo "🐳 Docker Containers:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🧠 Ollama:"
systemctl status ollama --no-pager -l

echo ""
echo "🌐 Nginx:"
systemctl status nginx --no-pager -l

echo ""
echo "💾 Uso de disco:"
df -h

echo ""
echo "🖥️ Uso de memória:"
free -h
STATUS

        # Script de logs
        cat > logs.sh << 'LOGS'
#!/bin/bash
echo "📝 Logs do MIT Logistics"
echo "======================="

if [ "$1" = "frontend" ]; then
    docker-compose -f docker-compose.prod.yml logs -f frontend
elif [ "$1" = "backend" ]; then
    docker-compose -f docker-compose.prod.yml logs -f backend
elif [ "$1" = "nginx" ]; then
    sudo journalctl -u nginx -f
elif [ "$1" = "ollama" ]; then
    sudo journalctl -u ollama -f
else
    echo "Uso: ./logs.sh [frontend|backend|nginx|ollama]"
    echo "Ou: docker-compose -f docker-compose.prod.yml logs -f"
fi
LOGS

        # Tornar scripts executáveis
        chmod +x *.sh
EOF

    log_success "Scripts de gerenciamento criados"
}

# Configurar firewall
configure_firewall() {
    log_info "Configurando firewall..."

    ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
        # Configurar UFW (se disponível)
        if command -v ufw &> /dev/null; then
            sudo ufw --force reset
            sudo ufw default deny incoming
            sudo ufw default allow outgoing
            sudo ufw allow ssh
            sudo ufw allow 80/tcp
            sudo ufw allow 443/tcp
            sudo ufw --force enable
        fi
EOF

    log_success "Firewall configurado"
}

# Iniciar aplicação
start_application() {
    log_info "Iniciando aplicação..."

    ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
        cd /home/ubuntu/mit-logistics
        
        # Iniciar via Docker Compose
        docker-compose -f docker-compose.prod.yml up -d
        
        # Aguardar serviços iniciarem
        sleep 30
        
        # Verificar status
        docker-compose -f docker-compose.prod.yml ps
EOF

    log_success "Aplicação iniciada!"
}

# Exibir informações finais
show_deployment_info() {
    echo ""
    echo "==============================="
    log_success "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
    echo "==============================="
    echo ""
    
    if [ -n "$DOMAIN" ]; then
        echo "🌐 Aplicação disponível em:"
        echo "   Frontend: https://$DOMAIN"
        echo "   Backend:  https://$DOMAIN/api"
        echo "   Gatekeeper: https://$DOMAIN/gatekeeper"
    else
        echo "🌐 Aplicação disponível em:"
        echo "   Frontend: http://$EC2_HOST:3000"
        echo "   Backend:  http://$EC2_HOST:8001"
    fi
    
    echo ""
    echo "📋 Scripts de gerenciamento disponíveis no servidor:"
    echo "   ./start-production.sh  - Iniciar aplicação"
    echo "   ./stop-production.sh   - Parar aplicação"
    echo "   ./status.sh           - Verificar status"
    echo "   ./logs.sh [service]   - Ver logs"
    echo ""
    echo "🔧 Comandos úteis:"
    echo "   ssh -i $EC2_KEY $EC2_USER@$EC2_HOST"
    echo "   cd /home/$EC2_USER/mit-logistics"
    echo ""
    
    if [ -n "$DOMAIN" ]; then
        echo "🔒 SSL certificado configurado para $DOMAIN"
        echo "📅 Renovação automática do SSL ativa"
    else
        echo "⚠️  Para configurar SSL, defina DOMAIN e execute novamente"
    fi
    
    echo ""
    log_info "Para acessar o servidor:"
    echo "ssh -i $EC2_KEY $EC2_USER@$EC2_HOST"
}

# Menu principal
main() {
    echo "🚀 MIT Logistics - Deploy para EC2"
    echo ""
    echo "Configuração:"
    echo "  EC2_HOST: $EC2_HOST"
    echo "  EC2_USER: $EC2_USER"
    echo "  EC2_KEY:  $EC2_KEY"
    echo "  DOMAIN:   ${DOMAIN:-'(não definido)'}"
    echo "  DEPLOY_ENV: $DEPLOY_ENV"
    echo ""
    
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Uso: $0 [opcoes]"
        echo ""
        echo "Variáveis de ambiente:"
        echo "  EC2_HOST     - IP ou domínio da instância EC2 (obrigatório)"
        echo "  EC2_USER     - Usuário SSH (padrão: ubuntu)"
        echo "  EC2_KEY      - Caminho para chave SSH (padrão: ~/.ssh/id_rsa)"
        echo "  DOMAIN       - Domínio para SSL (opcional)"
        echo "  SSL_EMAIL    - Email para Let's Encrypt (padrão: admin@mitlogistics.com)"
        echo ""
        echo "Exemplo:"
        echo "  export EC2_HOST=ec2-1-2-3-4.compute-1.amazonaws.com"
        echo "  export DOMAIN=mitlogistics.com"
        echo "  $0"
        exit 0
    fi
    
    read -p "Deseja continuar com o deploy? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deploy cancelado pelo usuário"
        exit 0
    fi
    
    # Executar deploy
    check_requirements
    install_dependencies
    setup_ollama
    deploy_application
    configure_nginx
    setup_ssl
    create_management_scripts
    configure_firewall
    start_application
    show_deployment_info
}

# Executar script principal
main "$@"