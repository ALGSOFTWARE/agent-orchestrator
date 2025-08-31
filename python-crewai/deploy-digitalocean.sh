#!/bin/bash

# 🌊 Deploy Script Digital Ocean - MIT Logistics/Gatekeeper
# Otimizado para Ubuntu 22.04 no Digital Ocean

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}🌊 MIT Logistics Deploy Script - Digital Ocean${NC}"
echo "=================================================="

# Check if running on Digital Ocean
if curl -s --max-time 5 http://169.254.169.254/metadata/v1/id > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Detected Digital Ocean Droplet${NC}"
    DROPLET_ID=$(curl -s http://169.254.169.254/metadata/v1/id)
    PUBLIC_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
    REGION=$(curl -s http://169.254.169.254/metadata/v1/region)
    echo -e "${BLUE}📊 Droplet ID: ${DROPLET_ID}${NC}"
    echo -e "${BLUE}📊 Public IP: ${PUBLIC_IP}${NC}"
    echo -e "${BLUE}📊 Region: ${REGION}${NC}"
else
    echo -e "${YELLOW}⚠️  Not running on Digital Ocean, proceeding anyway...${NC}"
    PUBLIC_IP=$(curl -s ifconfig.me || echo "unknown")
fi

# Check system resources
echo -e "${BLUE}💻 Checking system resources...${NC}"
TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
AVAILABLE_SPACE=$(df -BG / | awk 'NR==2{print $4}' | sed 's/G//')
CPU_CORES=$(nproc)

echo -e "${BLUE}📊 CPU Cores: ${CPU_CORES}${NC}"
echo -e "${BLUE}📊 Total Memory: ${TOTAL_MEM}MB${NC}"
echo -e "${BLUE}📊 Available Disk: ${AVAILABLE_SPACE}GB${NC}"

# Recommendations based on resources
if [ $TOTAL_MEM -lt 1500 ]; then
    echo -e "${RED}❌ Warning: Less than 1.5GB RAM detected${NC}"
    echo -e "${YELLOW}💡 Recommendation: Upgrade to at least $12/month droplet${NC}"
fi

if [ $AVAILABLE_SPACE -lt 10 ]; then
    echo -e "${RED}❌ Error: Less than 10GB free space${NC}"
    exit 1
fi

# Check .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.production .env
    
    # Auto-configure Digital Ocean specific values
    if [ ! -z "$PUBLIC_IP" ] && [ "$PUBLIC_IP" != "unknown" ]; then
        sed -i "s/DOMAIN=.*/DOMAIN=${PUBLIC_IP}/" .env
        echo -e "${GREEN}✅ Auto-configured domain to Droplet public IP${NC}"
    fi
    
    echo -e "${RED}❌ Please edit .env file with your credentials:${NC}"
    echo -e "${YELLOW}nano .env${NC}"
    echo ""
    echo -e "${BLUE}🔑 Required credentials:${NC}"
    echo "- OPENAI_API_KEY (get from https://platform.openai.com/api-keys)"
    echo "- MONGODB_URL (recommend MongoDB Atlas - free tier)"
    echo "- JWT_SECRET (generate random 32+ char string)"
    echo ""
    echo -e "${GREEN}Then run: ./deploy-digitalocean.sh${NC}"
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
    printf '  - %s\n' "${missing_vars[@]}"
    exit 1
fi

echo -e "${GREEN}✅ Required environment variables validated${NC}"

# Create directories
echo -e "${BLUE}📁 Creating application directories...${NC}"
mkdir -p data/{mongodb,redis,prometheus,grafana}
mkdir -p logs/{api,agents}
mkdir -p uploads models nginx/ssl monitoring/{prometheus,grafana}
mkdir -p backups

echo -e "${GREEN}✅ Directories created${NC}"

# Configure swap (important for small droplets)
if [ $TOTAL_MEM -lt 3000 ] && [ ! -f /swapfile ]; then
    echo -e "${YELLOW}💾 Configuring swap for better performance...${NC}"
    
    # Calculate swap size (1.5x RAM, max 4GB)
    SWAP_SIZE=$((TOTAL_MEM * 3 / 2))
    if [ $SWAP_SIZE -gt 4096 ]; then
        SWAP_SIZE=4096
    fi
    
    fallocate -l ${SWAP_SIZE}M /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    
    echo -e "${GREEN}✅ ${SWAP_SIZE}MB swap configured${NC}"
fi

# Optimize Digital Ocean droplet
echo -e "${BLUE}⚡ Applying Digital Ocean optimizations...${NC}"

# Configure log rotation
tee /etc/logrotate.d/docker-containers > /dev/null <<EOF
/var/lib/docker/containers/*/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 0644 root root
    postrotate
        /usr/bin/docker kill --signal=USR1 \$(docker ps -q) 2>/dev/null || true
    endscript
}
EOF

# Configure automatic updates (security only)
echo 'Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
};' > /etc/apt/apt.conf.d/50unattended-upgrades

echo -e "${GREEN}✅ Digital Ocean optimizations applied${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}🐳 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}🐳 Installing Docker Compose...${NC}"
    apt update
    apt install docker-compose-plugin -y
fi

echo -e "${GREEN}✅ Docker environment ready${NC}"

# Deploy function
deploy_application() {
    echo -e "${BLUE}🚀 Starting application deployment...${NC}"
    
    # Pull base images
    echo -e "${YELLOW}📥 Pulling base images...${NC}"
    docker-compose -f docker-compose.prod.yml pull 2>/dev/null || echo "Some images will be built locally"
    
    # Build custom images
    echo -e "${YELLOW}🔨 Building application images...${NC}"
    docker-compose -f docker-compose.prod.yml build --parallel
    
    # Clean up old containers
    echo -e "${YELLOW}🧹 Cleaning up old containers...${NC}"
    docker-compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
    docker system prune -f
    
    # Start database services first
    echo -e "${YELLOW}🗄️  Starting database services...${NC}"
    docker-compose -f docker-compose.prod.yml up -d mongodb redis
    
    echo -e "${YELLOW}⏳ Waiting for databases (45s)...${NC}"
    sleep 45
    
    # Start API service
    echo -e "${YELLOW}🔗 Starting API service...${NC}"
    docker-compose -f docker-compose.prod.yml up -d gatekeeper-api
    
    echo -e "${YELLOW}⏳ Waiting for API to be ready (60s)...${NC}"
    sleep 60
    
    # Start agent services
    echo -e "${YELLOW}🤖 Starting AI agents...${NC}"
    docker-compose -f docker-compose.prod.yml up -d crewai-agents
    
    echo -e "${YELLOW}⏳ Waiting for agents (30s)...${NC}"
    sleep 30
    
    # Start monitoring and proxy
    echo -e "${YELLOW}📊 Starting monitoring services...${NC}"
    docker-compose -f docker-compose.prod.yml up -d prometheus grafana nginx
    
    echo -e "${GREEN}✅ All services deployed${NC}"
}

# Health check function
check_services_health() {
    echo -e "${BLUE}🩺 Running comprehensive health checks...${NC}"
    
    # Give services time to fully initialize
    echo -e "${YELLOW}⏳ Final stabilization period (60s)...${NC}"
    sleep 60
    
    local all_healthy=true
    
    # Check API health
    echo -n "🔗 API Health Check... "
    if curl -f -s --max-time 10 "http://localhost:8001/health" > /dev/null; then
        echo -e "${GREEN}✅ Healthy${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
        all_healthy=false
    fi
    
    # Check API via public IP
    if [ ! -z "$PUBLIC_IP" ] && [ "$PUBLIC_IP" != "unknown" ]; then
        echo -n "🌐 Public API Access... "
        if curl -f -s --max-time 10 "http://${PUBLIC_IP}:8001/health" > /dev/null; then
            echo -e "${GREEN}✅ Accessible${NC}"
        else
            echo -e "${RED}❌ Not accessible${NC}"
            echo -e "${YELLOW}   💡 Check firewall: ufw allow 8001${NC}"
            all_healthy=false
        fi
    fi
    
    # Check database connections if local
    if [[ $MONGODB_URL == *"localhost"* ]] || [[ $MONGODB_URL == *"127.0.0.1"* ]] || [[ $MONGODB_URL == *"mongodb-prod"* ]]; then
        echo -n "🗄️  MongoDB Connection... "
        if docker exec mongodb-prod mongosh --quiet --eval "db.admin.command('hello')" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Connected${NC}"
        else
            echo -e "${RED}❌ Failed${NC}"
            all_healthy=false
        fi
    else
        echo -e "${GREEN}✅ Using external MongoDB (Atlas)${NC}"
    fi
    
    # Check Redis
    echo -n "🔄 Redis Connection... "
    if docker exec redis-prod redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Connected${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
        all_healthy=false
    fi
    
    # Check container status
    echo -e "${BLUE}📊 Container Status:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(mongodb|redis|gatekeeper|crewai|grafana|prometheus)"
    
    if [ "$all_healthy" = true ]; then
        return 0
    else
        return 1
    fi
}

# Show deployment summary
show_deployment_summary() {
    echo ""
    echo -e "${GREEN}🎉 Digital Ocean deployment completed!${NC}"
    echo "=================================================="
    echo -e "${BLUE}🌐 Access URLs:${NC}"
    
    if [ ! -z "$PUBLIC_IP" ] && [ "$PUBLIC_IP" != "unknown" ]; then
        echo "  🚀 Main API: http://${PUBLIC_IP}:8001"
        echo "  🩺 Health Check: http://${PUBLIC_IP}:8001/health"
        echo "  📊 Grafana: http://${PUBLIC_IP}:3000"
        echo "  📈 Prometheus: http://${PUBLIC_IP}:9090"
    else
        echo "  🚀 Main API: http://YOUR_DROPLET_IP:8001"
    fi
    
    echo ""
    echo -e "${BLUE}🔐 Default Credentials:${NC}"
    echo "  📊 Grafana: admin / ${GRAFANA_PASSWORD:-admin123}"
    
    echo ""
    echo -e "${BLUE}💰 Cost Information:${NC}"
    echo "  💸 Current Droplet: ~$12-18/month"
    echo "  💳 Credits Used: ~$0.40/day ($12/month)"
    echo "  🎁 Remaining Credits: $200 - usage"
    
    echo ""
    echo -e "${BLUE}📊 Performance Metrics:${NC}"
    echo "  🖥️  CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "  💾 Memory Usage: $(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')%"
    echo "  💿 Disk Usage: $(df -h / | awk 'NR==2{print $5}')"
    
    echo ""
    echo -e "${BLUE}🛠️  Management Commands:${NC}"
    echo "  📋 Check status: docker ps"
    echo "  📊 View logs: docker-compose -f docker-compose.prod.yml logs -f [service]"
    echo "  🔄 Restart: docker-compose -f docker-compose.prod.yml restart [service]"
    echo "  🛑 Stop all: docker-compose -f docker-compose.prod.yml down"
    echo "  🩺 Health check: ./deploy-digitalocean.sh health"
    echo "  🔄 Update: ./deploy-digitalocean.sh update"
    
    echo ""
    echo -e "${PURPLE}🚀 Next Steps:${NC}"
    echo "  1. 🔒 Configure domain: Point DNS to ${PUBLIC_IP:-YOUR_DROPLET_IP}"
    echo "  2. 🛡️  SSL Certificate: certbot --nginx -d yourdomain.com"
    echo "  3. 📊 Configure Grafana dashboards"
    echo "  4. 💾 Setup automated backups"
    echo "  5. 🚨 Configure uptime monitoring"
    
    if [ ! -z "$PUBLIC_IP" ] && [ "$PUBLIC_IP" != "unknown" ]; then
        echo ""
        echo -e "${GREEN}🧪 Test your deployment:${NC}"
        echo -e "${YELLOW}curl http://${PUBLIC_IP}:8001/health${NC}"
        echo ""
        echo -e "${PURPLE}🎯 Share with investors:${NC}"
        echo -e "${YELLOW}\"Our MVP is live at http://${PUBLIC_IP}:8001\"${NC}"
    fi
}

# Backup function
create_backup() {
    echo -e "${BLUE}💾 Creating deployment backup...${NC}"
    
    local backup_name="mit-logistics-backup-$(date +%Y%m%d_%H%M%S)"
    mkdir -p backups/$backup_name
    
    # Backup environment file
    cp .env backups/$backup_name/
    
    # Backup docker compose
    cp docker-compose.prod.yml backups/$backup_name/
    
    # Backup application data (if local MongoDB)
    if [[ $MONGODB_URL == *"localhost"* ]]; then
        docker exec mongodb-prod mongodump --out /backup/$backup_name 2>/dev/null || true
    fi
    
    # Create restore script
    cat > backups/$backup_name/restore.sh << 'EOF'
#!/bin/bash
echo "Restoring MIT Logistics deployment..."
cp .env ../../../
cp docker-compose.prod.yml ../../../
echo "Files restored. Run ./deploy-digitalocean.sh to redeploy."
EOF
    chmod +x backups/$backup_name/restore.sh
    
    echo -e "${GREEN}✅ Backup created: backups/$backup_name${NC}"
}

# Main deployment flow
main() {
    create_backup
    deploy_application
    
    if check_services_health; then
        show_deployment_summary
        echo -e "${GREEN}🌊 Digital Ocean deployment successful! Ready for demo!${NC}"
        return 0
    else
        echo -e "${RED}❌ Health checks failed. Showing recent logs...${NC}"
        docker-compose -f docker-compose.prod.yml logs --tail=20
        echo ""
        echo -e "${YELLOW}💡 Troubleshooting commands:${NC}"
        echo "  🔍 Check logs: docker-compose -f docker-compose.prod.yml logs [service]"
        echo "  🔄 Restart failing service: docker-compose -f docker-compose.prod.yml restart [service]"
        echo "  🆘 Get help: ./deploy-digitalocean.sh logs"
        return 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "health")
        check_services_health && echo -e "${GREEN}✅ All services healthy${NC}" || echo -e "${RED}❌ Some services need attention${NC}"
        ;;
    "logs")
        if [ -z "$2" ]; then
            echo -e "${BLUE}📋 Available services: gatekeeper-api, crewai-agents, mongodb, redis, grafana, prometheus, nginx${NC}"
            docker-compose -f docker-compose.prod.yml logs --tail=50
        else
            docker-compose -f docker-compose.prod.yml logs -f "$2"
        fi
        ;;
    "stop")
        echo -e "${YELLOW}🛑 Stopping all services...${NC}"
        docker-compose -f docker-compose.prod.yml down
        echo -e "${GREEN}✅ All services stopped${NC}"
        ;;
    "restart")
        echo -e "${YELLOW}🔄 Restarting services...${NC}"
        if [ -z "$2" ]; then
            docker-compose -f docker-compose.prod.yml restart
        else
            docker-compose -f docker-compose.prod.yml restart "$2"
        fi
        echo -e "${GREEN}✅ Services restarted${NC}"
        ;;
    "update")
        echo -e "${YELLOW}🔄 Updating deployment...${NC}"
        git pull
        docker-compose -f docker-compose.prod.yml pull 2>/dev/null || true
        docker-compose -f docker-compose.prod.yml build --parallel
        docker-compose -f docker-compose.prod.yml up -d
        echo -e "${GREEN}✅ Update completed${NC}"
        ;;
    "backup")
        create_backup
        ;;
    "status")
        echo -e "${BLUE}📊 Digital Ocean Deployment Status${NC}"
        echo "=================================="
        echo -e "${YELLOW}🖥️  System Resources:${NC}"
        echo "  CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
        echo "  Memory: $(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')%"
        echo "  Disk: $(df -h / | awk 'NR==2{print $5}')"
        echo ""
        echo -e "${YELLOW}🐳 Container Status:${NC}"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        check_services_health
        ;;
    *)
        main
        ;;
esac