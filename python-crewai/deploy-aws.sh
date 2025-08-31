#!/bin/bash

# 🚀 Deploy Script AWS EC2 - MIT Logistics/Gatekeeper
# Otimizado para Amazon Linux/Ubuntu em EC2

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 MIT Logistics Deploy Script - AWS EC2${NC}"
echo "=================================================="

# Check if running on EC2
if curl -s http://169.254.169.254/latest/meta-data/instance-id > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Detected AWS EC2 instance${NC}"
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
    INSTANCE_TYPE=$(curl -s http://169.254.169.254/latest/meta-data/instance-type)
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    echo -e "${BLUE}📊 Instance ID: ${INSTANCE_ID}${NC}"
    echo -e "${BLUE}📊 Instance Type: ${INSTANCE_TYPE}${NC}"
    echo -e "${BLUE}📊 Public IP: ${PUBLIC_IP}${NC}"
else
    echo -e "${YELLOW}⚠️  Not running on EC2, proceeding anyway...${NC}"
fi

# Check .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.production .env
    
    # Auto-configure some AWS-specific values
    if [ ! -z "$PUBLIC_IP" ]; then
        sed -i "s/DOMAIN=.*/DOMAIN=${PUBLIC_IP}/" .env
        echo -e "${GREEN}✅ Auto-configured domain to EC2 public IP${NC}"
    fi
    
    echo -e "${RED}❌ Please edit .env file with your credentials:${NC}"
    echo -e "${YELLOW}nano .env${NC}"
    echo ""
    echo -e "${BLUE}Required variables:${NC}"
    echo "- OPENAI_API_KEY"
    echo "- MONGODB_URL (Atlas recommended)"
    echo "- JWT_SECRET"
    echo "- MONGO_ROOT_PASSWORD (if using local MongoDB)"
    echo ""
    echo -e "${GREEN}Then run: ./deploy-aws.sh${NC}"
    exit 1
fi

# Source environment
source .env
echo -e "${GREEN}✅ Environment loaded${NC}"

# Validate required vars
required_vars=("OPENAI_API_KEY" "JWT_SECRET")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing required environment variables:${NC}"
    printf '%s\n' "${missing_vars[@]}"
    exit 1
fi

echo -e "${GREEN}✅ Required environment variables validated${NC}"

# Create directories with appropriate permissions
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p data/{mongodb,redis,prometheus,grafana}
mkdir -p logs/{api,agents}  
mkdir -p uploads models nginx/ssl monitoring/{prometheus,grafana}

# Set ownership to current user
sudo chown -R $USER:$USER data/ logs/ uploads/ || true

echo -e "${GREEN}✅ Directories created${NC}"

# Check system resources
echo -e "${BLUE}💻 Checking system resources...${NC}"
TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
AVAILABLE_SPACE=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')

echo -e "${BLUE}📊 Available Memory: ${TOTAL_MEM}MB${NC}"
echo -e "${BLUE}📊 Available Disk: ${AVAILABLE_SPACE}GB${NC}"

if [ $TOTAL_MEM -lt 1500 ]; then
    echo -e "${YELLOW}⚠️  Low memory detected. Consider upgrading to t2.small or larger${NC}"
fi

if [ $AVAILABLE_SPACE -lt 10 ]; then
    echo -e "${RED}❌ Insufficient disk space. Need at least 10GB free${NC}"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
    echo -e "${YELLOW}⚠️  Please logout and login again, then re-run this script${NC}"
    exit 0
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker Compose...${NC}"
    sudo apt update
    sudo apt install docker-compose-plugin -y
fi

echo -e "${GREEN}✅ Docker environment ready${NC}"

# Configure swap if needed (for low memory instances)
if [ $TOTAL_MEM -lt 2000 ] && [ ! -f /swapfile ]; then
    echo -e "${YELLOW}💾 Configuring swap for low memory instance...${NC}"
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo -e "${GREEN}✅ Swap configured${NC}"
fi

# AWS-specific optimizations
echo -e "${BLUE}⚡ Applying AWS optimizations...${NC}"

# Configure log rotation to prevent disk full
sudo tee /etc/logrotate.d/docker-containers > /dev/null <<EOF
/var/lib/docker/containers/*/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 0644 root root
}
EOF

echo -e "${GREEN}✅ AWS optimizations applied${NC}"

# Deploy function
deploy_containers() {
    echo -e "${BLUE}🐳 Starting containerized deployment...${NC}"
    
    # Pull latest images
    echo -e "${YELLOW}📥 Pulling base images...${NC}"
    docker-compose -f docker-compose.prod.yml pull || echo "Some images may not exist yet"
    
    # Build custom images
    echo -e "${YELLOW}🔨 Building application images...${NC}"
    docker-compose -f docker-compose.prod.yml build --parallel
    
    # Stop existing containers
    echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true
    
    # Start services in order
    echo -e "${YELLOW}🚀 Starting core services...${NC}"
    
    # Start database services first
    docker-compose -f docker-compose.prod.yml up -d mongodb redis
    echo -e "${YELLOW}⏳ Waiting for databases to initialize...${NC}"
    sleep 30
    
    # Start API
    docker-compose -f docker-compose.prod.yml up -d gatekeeper-api
    echo -e "${YELLOW}⏳ Waiting for API to be healthy...${NC}"
    sleep 45
    
    # Start agents
    docker-compose -f docker-compose.prod.yml up -d crewai-agents
    echo -e "${YELLOW}⏳ Waiting for agents to initialize...${NC}"
    sleep 30
    
    # Start monitoring and proxy
    docker-compose -f docker-compose.prod.yml up -d prometheus grafana nginx
    
    echo -e "${GREEN}✅ All services started${NC}"
}

# Health check function
check_health() {
    echo -e "${BLUE}🩺 Running health checks...${NC}"
    
    # Wait for services to stabilize
    echo -e "${YELLOW}⏳ Allowing services to stabilize (60s)...${NC}"
    sleep 60
    
    # Check API health
    echo -n "API Health Check... "
    if curl -f -s --max-time 10 "http://localhost:8001/health" > /dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
        return 1
    fi
    
    # Check MongoDB if local
    if [[ $MONGODB_URL == *"localhost"* ]]; then
        echo -n "MongoDB Connection... "
        if docker exec mongodb-prod mongosh --quiet --eval "db.admin.command('hello')" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ OK${NC}"
        else
            echo -e "${RED}❌ Failed${NC}"
            return 1
        fi
    fi
    
    # Check Redis
    echo -n "Redis Connection... "
    if docker exec redis-prod redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
        return 1
    fi
    
    return 0
}

# Configure system firewall
configure_firewall() {
    echo -e "${BLUE}🔥 Configuring firewall...${NC}"
    
    # Check if ufw is available
    if command -v ufw &> /dev/null; then
        sudo ufw --force reset
        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        sudo ufw allow ssh
        sudo ufw allow 80
        sudo ufw allow 443
        sudo ufw allow 8001
        sudo ufw --force enable
        echo -e "${GREEN}✅ UFW firewall configured${NC}"
    else
        echo -e "${YELLOW}⚠️  UFW not available, ensure EC2 Security Groups are configured${NC}"
    fi
}

# Show deployment info
show_info() {
    echo ""
    echo -e "${GREEN}🎉 AWS EC2 Deployment completed successfully!${NC}"
    echo "=================================================="
    echo -e "${BLUE}📊 Service URLs:${NC}"
    
    if [ ! -z "$PUBLIC_IP" ]; then
        echo "  🌐 API (Public): http://${PUBLIC_IP}:8001"
        echo "  🌐 API (Direct): http://${PUBLIC_IP}/health"
        echo "  📊 Grafana: http://${PUBLIC_IP}:3000"
        echo "  📈 Prometheus: http://${PUBLIC_IP}:9090"
    fi
    
    echo "  🌐 API (Local): http://localhost:8001"
    echo "  📊 Grafana (Local): http://localhost:3000"
    echo "  📈 Prometheus (Local): http://localhost:9090"
    
    echo ""
    echo -e "${BLUE}🔐 Default Credentials:${NC}"
    echo "  📊 Grafana: admin / ${GRAFANA_PASSWORD:-admin123}"
    echo ""
    echo -e "${BLUE}📱 Monitoring Commands:${NC}"
    echo "  View all containers: docker ps"
    echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f [service]"
    echo "  Restart service: docker-compose -f docker-compose.prod.yml restart [service]"
    echo "  Stop all: docker-compose -f docker-compose.prod.yml down"
    echo "  Check health: ./deploy-aws.sh health"
    echo ""
    echo -e "${BLUE}💡 Next Steps:${NC}"
    echo "  1. 🔒 Configure SSL: sudo certbot --nginx -d your-domain.com"
    echo "  2. 🔄 Setup auto-backup: crontab -e"
    echo "  3. 📊 Configure Grafana dashboards"
    echo "  4. 🚨 Setup CloudWatch monitoring"
    
    if [ ! -z "$PUBLIC_IP" ]; then
        echo ""
        echo -e "${GREEN}🎯 Test your deployment:${NC}"
        echo -e "${YELLOW}curl http://${PUBLIC_IP}:8001/health${NC}"
    fi
}

# Main execution
main() {
    configure_firewall
    deploy_containers
    
    if check_health; then
        show_info
        echo -e "${GREEN}🚀 AWS deployment ready for production!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Health checks failed. Checking logs...${NC}"
        docker-compose -f docker-compose.prod.yml logs --tail=50
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "health")
        check_health && echo -e "${GREEN}✅ All services healthy${NC}" || echo -e "${RED}❌ Some services unhealthy${NC}"
        ;;
    "logs")
        docker-compose -f docker-compose.prod.yml logs -f "${2:-}"
        ;;
    "stop")
        echo -e "${YELLOW}🛑 Stopping all services...${NC}"
        docker-compose -f docker-compose.prod.yml down
        ;;
    "restart")
        echo -e "${YELLOW}🔄 Restarting services...${NC}"
        docker-compose -f docker-compose.prod.yml restart "${2:-}"
        ;;
    "update")
        echo -e "${YELLOW}🔄 Updating deployment...${NC}"
        git pull
        docker-compose -f docker-compose.prod.yml pull
        docker-compose -f docker-compose.prod.yml build --parallel
        docker-compose -f docker-compose.prod.yml up -d
        ;;
    *)
        main
        ;;
esac