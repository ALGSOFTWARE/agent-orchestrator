#!/bin/bash

# 🚀 Deploy Script para MIT Logistics/Gatekeeper MVP
# Para Digital Ocean App Platform ou Docker Swarm

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 MIT Logistics/Gatekeeper Deploy Script${NC}"
echo "=================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.production .env
    echo -e "${RED}❌ Please edit .env file with your credentials and run again${NC}"
    exit 1
fi

# Source environment variables
source .env

echo -e "${GREEN}✅ Environment loaded${NC}"

# Validate required environment variables
required_vars=("DOMAIN" "MONGO_ROOT_PASSWORD" "JWT_SECRET" "OPENAI_API_KEY")
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

echo -e "${GREEN}✅ All required environment variables set${NC}"

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p data/{mongodb,redis,prometheus,grafana}
mkdir -p logs/{api,agents}
mkdir -p uploads models nginx/ssl monitoring/{prometheus,grafana}

echo -e "${GREEN}✅ Directories created${NC}"

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker environment verified${NC}"

# Function to deploy with Docker Compose
deploy_docker_compose() {
    echo -e "${BLUE}🐳 Starting Docker Compose deployment...${NC}"
    
    # Pull latest images
    echo -e "${YELLOW}📥 Pulling latest images...${NC}"
    docker-compose -f docker-compose.prod.yml pull
    
    # Build custom images
    echo -e "${YELLOW}🔨 Building custom images...${NC}"
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    # Stop any existing containers
    echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
    docker-compose -f docker-compose.prod.yml down --remove-orphans
    
    # Start services
    echo -e "${YELLOW}🚀 Starting services...${NC}"
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be healthy
    echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
    sleep 30
    
    # Check service health
    check_service_health
}

# Function to check service health
check_service_health() {
    echo -e "${BLUE}🩺 Checking service health...${NC}"
    
    services=("mongodb-prod" "redis-prod" "gatekeeper-api-prod" "crewai-agents-prod")
    
    for service in "${services[@]}"; do
        echo -n "Checking $service... "
        
        # Get container status
        status=$(docker inspect --format="{{.State.Health.Status}}" "$service" 2>/dev/null || echo "not found")
        
        if [ "$status" = "healthy" ]; then
            echo -e "${GREEN}✅ Healthy${NC}"
        elif [ "$status" = "starting" ]; then
            echo -e "${YELLOW}⏳ Starting...${NC}"
            # Wait a bit more for starting services
            sleep 10
            status=$(docker inspect --format="{{.State.Health.Status}}" "$service" 2>/dev/null || echo "not found")
            if [ "$status" = "healthy" ]; then
                echo -e "${GREEN}✅ Now Healthy${NC}"
            else
                echo -e "${RED}❌ Still not healthy${NC}"
            fi
        else
            echo -e "${RED}❌ $status${NC}"
        fi
    done
}

# Function to show deployment info
show_deployment_info() {
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo "=================================================="
    echo -e "${BLUE}📊 Service URLs:${NC}"
    echo "  🌐 Main API: http://localhost:8001"
    echo "  📊 Grafana: http://localhost:3000"
    echo "  📈 Prometheus: http://localhost:9090"
    echo ""
    echo -e "${BLUE}🔐 Default Credentials:${NC}"
    echo "  Grafana: admin / ${GRAFANA_PASSWORD}"
    echo ""
    echo -e "${BLUE}📝 Useful Commands:${NC}"
    echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f [service]"
    echo "  Restart service: docker-compose -f docker-compose.prod.yml restart [service]"
    echo "  Stop all: docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo -e "${YELLOW}🚨 Remember to:${NC}"
    echo "  1. Set up SSL certificates in nginx/ssl/"
    echo "  2. Configure your domain DNS to point to this server"
    echo "  3. Set up automated backups"
    echo "  4. Configure monitoring alerts"
    echo ""
}

# Function for production health check
production_health_check() {
    echo -e "${BLUE}🔍 Running production health checks...${NC}"
    
    # Test API endpoint
    echo -n "Testing API health endpoint... "
    if curl -f -s "http://localhost:8001/health" > /dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
        return 1
    fi
    
    # Test MongoDB connection
    echo -n "Testing MongoDB connection... "
    if docker exec mongodb-prod mongosh --quiet --eval "db.admin.command('hello')" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
        return 1
    fi
    
    # Test Redis connection
    echo -n "Testing Redis connection... "
    if docker exec redis-prod redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
        return 1
    fi
    
    return 0
}

# Main deployment flow
main() {
    deploy_docker_compose
    
    echo -e "${YELLOW}⏳ Waiting for services to stabilize...${NC}"
    sleep 60
    
    if production_health_check; then
        show_deployment_info
        echo -e "${GREEN}🚀 MVP is ready for VC demo!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Health checks failed. Check logs for issues.${NC}"
        echo "Run: docker-compose -f docker-compose.prod.yml logs"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "health")
        production_health_check
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
    *)
        main
        ;;
esac