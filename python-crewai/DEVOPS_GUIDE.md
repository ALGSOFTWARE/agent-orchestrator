# Guia DevOps - Sistema Gatekeeper

## 📋 Índice

1. [Ambientes e Infraestrutura](#ambientes-e-infraestrutura)
2. [Containerização](#containerização)
3. [CI/CD Pipeline](#cicd-pipeline)
4. [Monitoramento e Observabilidade](#monitoramento-e-observabilidade)
5. [Backup e Recuperação](#backup-e-recuperação)
6. [Segurança](#segurança)
7. [Scaling e Performance](#scaling-e-performance)
8. [Troubleshooting Avançado](#troubleshooting-avançado)

---

## 🏗️ Ambientes e Infraestrutura

### Arquitetura de Ambientes

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Development │    │   Staging   │    │ Production  │
│             │    │             │    │             │
│ - Local Dev │    │ - QA Tests  │    │ - Live Data │
│ - Unit Tests│    │ - Integration│    │ - High Avail│
│ - Hot Reload│    │ - Performance│    │ - Monitoring│
└─────────────┘    └─────────────┘    └─────────────┘
```

### 1. Ambiente de Desenvolvimento

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  mongodb-dev:
    image: mongo:7
    container_name: gatekeeper-mongo-dev
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: gatekeeper_dev
    volumes:
      - mongodb_dev_data:/data/db
      - ./scripts/init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js
    restart: unless-stopped

  gatekeeper-api-dev:
    build:
      context: ./gatekeeper-api
      dockerfile: Dockerfile.dev
    container_name: gatekeeper-api-dev
    ports:
      - "8001:8001"
    environment:
      - ENV=development
      - DEBUG=true
      - MONGODB_URL=mongodb://mongodb-dev:27017
      - DATABASE_NAME=gatekeeper_dev
    volumes:
      - ./gatekeeper-api:/app
      - /app/venv
    depends_on:
      - mongodb-dev
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

  python-crewai-dev:
    build:
      context: ./python-crewai
      dockerfile: Dockerfile.dev
    container_name: python-crewai-dev
    ports:
      - "8002:8002"
    environment:
      - ENV=development
      - GATEKEEPER_API_URL=http://gatekeeper-api-dev:8001
    volumes:
      - ./python-crewai:/app
      - /app/venv
    depends_on:
      - gatekeeper-api-dev
    restart: unless-stopped

volumes:
  mongodb_dev_data:
```

### 2. Ambiente de Staging

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  mongodb-staging:
    image: mongo:7
    container_name: gatekeeper-mongo-staging
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: gatekeeper_staging
    volumes:
      - mongodb_staging_data:/data/db
      - ./backups:/backups
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  gatekeeper-api-staging:
    image: gatekeeper-api:staging
    container_name: gatekeeper-api-staging
    ports:
      - "8001:8001"
    environment:
      - ENV=staging
      - DEBUG=false
      - MONGODB_URL=mongodb://mongodb-staging:27017
      - DATABASE_NAME=gatekeeper_staging
    env_file:
      - .env.staging
    depends_on:
      - mongodb-staging
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  mongodb_staging_data:
```

### 3. Ambiente de Produção

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mongodb-primary:
    image: mongo:7
    container_name: gatekeeper-mongo-primary
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: gatekeeper_prod
      MONGO_REPLICA_SET_NAME: rs0
    volumes:
      - mongodb_primary_data:/data/db
      - ./backups:/backups
      - ./configs/mongod.conf:/etc/mongod.conf
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '2.0'
    command: mongod --replSet rs0 --bind_ip_all

  gatekeeper-api-prod:
    image: gatekeeper-api:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 30s
        failure_action: rollback
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    ports:
      - "8001:8001"
    environment:
      - ENV=production
      - DEBUG=false
    env_file:
      - .env.prod
    depends_on:
      - mongodb-primary
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 15s
      timeout: 5s
      retries: 5

  nginx-proxy:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - gatekeeper-api-prod
    restart: unless-stopped

volumes:
  mongodb_primary_data:
```

---

## 🐳 Containerização

### 1. Dockerfile para Gatekeeper API

```dockerfile
# gatekeeper-api/Dockerfile
FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements primeiro (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 2. Dockerfile para Python-CrewAI

```dockerfile
# python-crewai/Dockerfile
FROM python:3.12-slim

# Instalar dependências do sistema incluindo Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    libtesseract-dev \
    poppler-utils \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p logs uploads temp

# Configurar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health')" || exit 1

EXPOSE 8002

CMD ["python", "-m", "tools.webhook_processor"]
```

### 3. Multi-stage Build para Produção

```dockerfile
# gatekeeper-api/Dockerfile.multistage
# Stage 1: Build
FROM python:3.12-slim AS builder

WORKDIR /app

# Instalar dependências de build
RUN apt-get update && apt-get install -y gcc g++

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim AS runtime

# Instalar apenas dependências de runtime
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar dependências do stage anterior
COPY --from=builder /root/.local /root/.local

WORKDIR /app

# Copiar código da aplicação
COPY . .

# Configurar PATH
ENV PATH=/root/.local/bin:$PATH

# Configurar usuário
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## 🔄 CI/CD Pipeline

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop, agents ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:7
        ports:
          - 27017:27017
        options: >-
          --health-cmd mongo
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-por
    
    - name: Install Python dependencies
      run: |
        cd python-crewai
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run integration tests
      env:
        MONGODB_URL: mongodb://localhost:27017
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        cd python-crewai
        python test_gatekeeper_integration.py
    
    - name: Run unit tests
      run: |
        cd python-crewai
        python -m pytest tests/ -v

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install linting tools
      run: |
        pip install black flake8 mypy
    
    - name: Run Black
      run: |
        black --check python-crewai/
        black --check gatekeeper-api/
    
    - name: Run Flake8
      run: |
        flake8 python-crewai/ --max-line-length=100
        flake8 gatekeeper-api/ --max-line-length=100
    
    - name: Run MyPy
      run: |
        mypy python-crewai/ --ignore-missing-imports
        mypy gatekeeper-api/ --ignore-missing-imports

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Bandit Security Scan
      run: |
        pip install bandit
        bandit -r python-crewai/ -f json -o security-report.json
        bandit -r gatekeeper-api/ -f json -o security-report-api.json
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: security-report*.json

  build-and-push:
    needs: [test, lint, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
    
    - name: Build and push Gatekeeper API
      uses: docker/build-push-action@v4
      with:
        context: ./gatekeeper-api
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-api:latest
        labels: ${{ steps.meta.outputs.labels }}
    
    - name: Build and push Python-CrewAI
      uses: docker/build-push-action@v4
      with:
        context: ./python-crewai
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-agents:latest
        labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Staging
      run: |
        # SSH para servidor de staging e executar deploy
        echo "${{ secrets.STAGING_DEPLOY_KEY }}" > deploy_key
        chmod 600 deploy_key
        ssh -i deploy_key -o StrictHostKeyChecking=no user@staging-server.com '
          cd /opt/gatekeeper &&
          docker-compose -f docker-compose.staging.yml pull &&
          docker-compose -f docker-compose.staging.yml up -d &&
          docker system prune -f
        '
    
    - name: Run smoke tests on staging
      run: |
        sleep 60  # Aguardar inicialização
        curl -f http://staging-server.com:8001/health
        # Adicionar mais testes de fumaça aqui

  deploy-production:
    needs: [deploy-staging]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Production
      run: |
        echo "${{ secrets.PROD_DEPLOY_KEY }}" > deploy_key
        chmod 600 deploy_key
        ssh -i deploy_key -o StrictHostKeyChecking=no user@prod-server.com '
          cd /opt/gatekeeper &&
          
          # Backup antes do deploy
          docker exec gatekeeper-mongo-primary mongodump --out /backups/pre-deploy-$(date +%Y%m%d-%H%M%S) &&
          
          # Deploy com zero downtime
          docker-compose -f docker-compose.prod.yml pull &&
          docker-compose -f docker-compose.prod.yml up -d --no-deps gatekeeper-api-prod &&
          
          # Aguardar health check
          sleep 30 &&
          
          # Verificar saúde
          curl -f http://localhost:8001/health &&
          
          # Cleanup
          docker system prune -f
        '
```

### 2. Scripts de Deploy

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "🚀 Deploying to $ENVIRONMENT with version $VERSION"

# Validar ambiente
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    echo "❌ Environment must be 'staging' or 'production'"
    exit 1
fi

# Configurar variáveis baseadas no ambiente
if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    SERVER="prod-server.com"
    BACKUP_REQUIRED=true
else
    COMPOSE_FILE="docker-compose.staging.yml"
    SERVER="staging-server.com"
    BACKUP_REQUIRED=false
fi

# Função para executar comandos no servidor
run_remote() {
    ssh -o StrictHostKeyChecking=no user@$SERVER "$1"
}

# Backup (apenas produção)
if [ "$BACKUP_REQUIRED" = true ]; then
    echo "📦 Creating backup..."
    run_remote "
        cd /opt/gatekeeper &&
        docker exec gatekeeper-mongo-primary mongodump --out /backups/deploy-$(date +%Y%m%d-%H%M%S)
    "
fi

# Pull das imagens
echo "📥 Pulling images..."
run_remote "
    cd /opt/gatekeeper &&
    docker-compose -f $COMPOSE_FILE pull
"

# Deploy
echo "🔄 Deploying services..."
run_remote "
    cd /opt/gatekeeper &&
    docker-compose -f $COMPOSE_FILE up -d
"

# Health check
echo "🏥 Running health checks..."
sleep 30

if run_remote "curl -f http://localhost:8001/health"; then
    echo "✅ Deploy successful!"
else
    echo "❌ Deploy failed - health check failed"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "🔙 Rolling back..."
        run_remote "
            cd /opt/gatekeeper &&
            docker-compose -f $COMPOSE_FILE rollback
        "
    fi
    
    exit 1
fi

# Cleanup
echo "🧹 Cleaning up..."
run_remote "docker system prune -f"

echo "🎉 Deploy completed successfully!"
```

---

## 📊 Monitoramento e Observabilidade

### 1. Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'gatekeeper-api'
    static_configs:
      - targets: ['gatekeeper-api:8001']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'python-crewai'
    static_configs:
      - targets: ['python-crewai:8002']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
    scrape_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 2. Grafana Dashboards

```json
{
  "dashboard": {
    "id": null,
    "title": "Gatekeeper System Metrics",
    "tags": ["gatekeeper"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket{job=\"gatekeeper-api\"})",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, http_request_duration_seconds_bucket{job=\"gatekeeper-api\"})",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "id": 2,
        "title": "Agent Query Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(agent_queries_successful_total[5m]) / rate(agent_queries_total[5m]) * 100",
            "legendFormat": "Success Rate %"
          }
        ]
      },
      {
        "id": 3,
        "title": "Document Processing Volume",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(documents_processed_total[1m])",
            "legendFormat": "Documents/minute"
          }
        ]
      },
      {
        "id": 4,
        "title": "Webhook Events",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(webhook_events_total[5m])",
            "legendFormat": "Events/second"
          }
        ]
      }
    ]
  }
}
```

### 3. Alert Rules

```yaml
# monitoring/alert_rules.yml
groups:
  - name: gatekeeper_alerts
    rules:
      - alert: APIHighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on Gatekeeper API"
          description: "API error rate is {{ $value }} errors per second"

      - alert: AgentQueryFailure
        expr: rate(agent_queries_failed_total[5m]) > 0.05
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Agent queries failing"
          description: "Agent query failure rate is {{ $value }} per second"

      - alert: MongoDBDown
        expr: up{job="mongodb"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "MongoDB is down"
          description: "MongoDB has been down for more than 30 seconds"

      - alert: DiskSpaceHigh
        expr: (1 - node_filesystem_free_bytes / node_filesystem_size_bytes) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Disk space usage is high"
          description: "Disk usage is {{ $value }}%"

      - alert: MemoryUsageHigh
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Memory usage is critically high"
          description: "Memory usage is {{ $value }}%"
```

### 4. Logging Stack

```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    container_name: elasticsearch
    environment:
      - node.name=elasticsearch
      - cluster.name=gatekeeper-logs
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    container_name: logstash
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
      - ./logstash/config:/usr/share/logstash/config
    ports:
      - "5044:5044"
      - "5000:5000/tcp"
      - "5000:5000/udp"
      - "9600:9600"
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.8.0
    container_name: filebeat
    user: root
    volumes:
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ../logs:/app/logs:ro
    depends_on:
      - logstash

volumes:
  elasticsearch_data:
```

---

## 💾 Backup e Recuperação

### 1. Estratégia de Backup

```bash
#!/bin/bash
# scripts/backup.sh

set -e

BACKUP_TYPE=${1:-incremental}  # full, incremental
RETENTION_DAYS=${2:-30}

# Configurações
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
S3_BUCKET="gatekeeper-backups"

echo "🗄️ Starting $BACKUP_TYPE backup at $TIMESTAMP"

# Função para backup do MongoDB
backup_mongodb() {
    echo "📦 Backing up MongoDB..."
    
    if [ "$BACKUP_TYPE" = "full" ]; then
        # Backup completo
        docker exec gatekeeper-mongo-primary mongodump \
            --out "$BACKUP_DIR/mongodb-full-$TIMESTAMP" \
            --gzip \
            --numParallelCollections 4
        
        tar -czf "$BACKUP_DIR/mongodb-full-$TIMESTAMP.tar.gz" \
            -C "$BACKUP_DIR" "mongodb-full-$TIMESTAMP"
        rm -rf "$BACKUP_DIR/mongodb-full-$TIMESTAMP"
    else
        # Backup incremental (oplog)
        docker exec gatekeeper-mongo-primary mongodump \
            --oplog \
            --out "$BACKUP_DIR/mongodb-incremental-$TIMESTAMP" \
            --gzip
    fi
}

# Função para backup de arquivos
backup_files() {
    echo "📁 Backing up application files..."
    
    tar -czf "$BACKUP_DIR/app-files-$TIMESTAMP.tar.gz" \
        -C /opt/gatekeeper \
        --exclude='*.log' \
        --exclude='temp/*' \
        --exclude='*.pyc' \
        configs/ uploads/ scripts/
}

# Função para upload para S3
upload_to_s3() {
    echo "☁️ Uploading to S3..."
    
    aws s3 sync "$BACKUP_DIR/" "s3://$S3_BUCKET/$(hostname)/" \
        --storage-class STANDARD_IA \
        --exclude "*" \
        --include "*$TIMESTAMP*"
}

# Função para limpeza de backups antigos
cleanup_old_backups() {
    echo "🧹 Cleaning up old backups..."
    
    # Local
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
    
    # S3 (configurar lifecycle policy)
    aws s3api put-bucket-lifecycle-configuration \
        --bucket $S3_BUCKET \
        --lifecycle-configuration file://s3-lifecycle.json
}

# Executar backups
mkdir -p "$BACKUP_DIR"

backup_mongodb
backup_files
upload_to_s3
cleanup_old_backups

echo "✅ Backup completed successfully at $TIMESTAMP"

# Verificar integridade
echo "🔍 Verifying backup integrity..."
if [ -f "$BACKUP_DIR/mongodb-$BACKUP_TYPE-$TIMESTAMP.tar.gz" ]; then
    tar -tzf "$BACKUP_DIR/mongodb-$BACKUP_TYPE-$TIMESTAMP.tar.gz" > /dev/null
    echo "✅ MongoDB backup integrity verified"
fi

if [ -f "$BACKUP_DIR/app-files-$TIMESTAMP.tar.gz" ]; then
    tar -tzf "$BACKUP_DIR/app-files-$TIMESTAMP.tar.gz" > /dev/null
    echo "✅ App files backup integrity verified"
fi

echo "🎉 Backup process completed successfully!"
```

### 2. Procedimento de Recuperação

```bash
#!/bin/bash
# scripts/restore.sh

set -e

BACKUP_DATE=${1}  # Format: YYYYMMDD-HHMMSS
RESTORE_TYPE=${2:-full}  # full, partial
S3_BUCKET="gatekeeper-backups"

if [ -z "$BACKUP_DATE" ]; then
    echo "❌ Usage: $0 <backup_date> [restore_type]"
    echo "Available backups:"
    aws s3 ls "s3://$S3_BUCKET/$(hostname)/" | grep tar.gz
    exit 1
fi

echo "🔄 Starting restore from backup: $BACKUP_DATE"

# Baixar backups do S3
download_backups() {
    echo "📥 Downloading backups from S3..."
    
    aws s3 cp "s3://$S3_BUCKET/$(hostname)/mongodb-full-$BACKUP_DATE.tar.gz" \
        "/tmp/mongodb-backup.tar.gz"
    
    aws s3 cp "s3://$S3_BUCKET/$(hostname)/app-files-$BACKUP_DATE.tar.gz" \
        "/tmp/app-files-backup.tar.gz"
}

# Parar serviços
stop_services() {
    echo "⏹️ Stopping services..."
    docker-compose -f docker-compose.prod.yml down
}

# Restaurar MongoDB
restore_mongodb() {
    echo "🗄️ Restoring MongoDB..."
    
    # Extrair backup
    tar -xzf /tmp/mongodb-backup.tar.gz -C /tmp/
    
    # Iniciar MongoDB temporariamente
    docker run -d --name temp-mongo \
        -v mongodb_restore:/data/db \
        mongo:7
    
    sleep 10
    
    # Restaurar dados
    docker exec temp-mongo mongorestore \
        --drop \
        /tmp/mongodb-full-$BACKUP_DATE/
    
    # Parar container temporário
    docker stop temp-mongo
    docker rm temp-mongo
}

# Restaurar arquivos da aplicação
restore_app_files() {
    echo "📁 Restoring application files..."
    
    # Backup dos arquivos atuais
    mv /opt/gatekeeper/configs /opt/gatekeeper/configs.backup.$(date +%Y%m%d-%H%M%S)
    mv /opt/gatekeeper/uploads /opt/gatekeeper/uploads.backup.$(date +%Y%m%d-%H%M%S)
    
    # Restaurar do backup
    tar -xzf /tmp/app-files-backup.tar.gz -C /opt/gatekeeper/
}

# Iniciar serviços
start_services() {
    echo "▶️ Starting services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Aguardar inicialização
    sleep 30
    
    # Verificar saúde
    if curl -f http://localhost:8001/health; then
        echo "✅ Services restored successfully"
    else
        echo "❌ Services failed to start properly"
        exit 1
    fi
}

# Executar restauração
download_backups
stop_services
restore_mongodb
restore_app_files
start_services

# Verificar dados
echo "🔍 Verifying restored data..."
docker exec gatekeeper-mongo-primary mongo --eval "
    db.adminCommand('listCollections').cursor.firstBatch.forEach(
        function(collection) {
            print('Collection: ' + collection.name + ', Documents: ' + 
                  db[collection.name].count());
        }
    )
"

echo "🎉 Restore completed successfully!"

# Cleanup
rm -f /tmp/mongodb-backup.tar.gz /tmp/app-files-backup.tar.gz
rm -rf /tmp/mongodb-full-$BACKUP_DATE
```

### 3. Disaster Recovery Plan

```markdown
# Disaster Recovery Plan

## RTO (Recovery Time Objective): 4 horas
## RPO (Recovery Point Objective): 1 hora

### Cenários de Disaster

1. **Perda do Servidor Principal**
   - Impacto: Total
   - Procedimento: Ativar servidor secundário
   - Tempo estimado: 2 horas

2. **Corrupção do Banco de Dados**
   - Impacto: Dados
   - Procedimento: Restore do backup mais recente
   - Tempo estimado: 1 hora

3. **Falha de Rede/Conectividade**
   - Impacto: Parcial
   - Procedimento: Ativar links redundantes
   - Tempo estimado: 30 minutos

### Procedimentos de Emergência

1. **Ativação do DR**
   ```bash
   # Verificar status atual
   ./scripts/health-check.sh
   
   # Ativar servidor secundário
   ./scripts/failover.sh
   
   # Restaurar do backup se necessário
   ./scripts/restore.sh <backup_date>
   ```

2. **Comunicação**
   - Stakeholders internos: Slack #emergency
   - Clientes: Status page
   - Equipe técnica: Chamada de emergência

3. **Validação pós-recovery**
   - Health checks automáticos
   - Testes funcionais críticos
   - Validação de integridade dos dados
```

---

## 🔒 Segurança

### 1. Container Security

```dockerfile
# Hardened Dockerfile
FROM python:3.12-slim AS base

# Usar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar apenas dependências necessárias
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copiar e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY --chown=appuser:appuser . .

# Configurar permissões
RUN chmod -R 755 /app && \
    chmod +x /app/entrypoint.sh

# Remover ferramentas desnecessárias
RUN apt-get remove -y --purge \
    && apt-get autoremove -y \
    && apt-get clean

USER appuser

EXPOSE 8001

ENTRYPOINT ["/app/entrypoint.sh"]
```

### 2. Network Security

```yaml
# docker-compose.secure.yml
version: '3.8'

networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
  backend:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.21.0.0/24

services:
  nginx-proxy:
    image: nginx:alpine
    networks:
      - frontend
    ports:
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/ssl/certs:ro
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    environment:
      - NGINX_SSL_PROTOCOLS=TLSv1.2 TLSv1.3
    restart: unless-stopped

  gatekeeper-api:
    image: gatekeeper-api:latest
    networks:
      - frontend
      - backend
    expose:
      - "8001"
    environment:
      - SSL_REQUIRED=true
      - ALLOWED_HOSTS=api.gatekeeper.com
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m

  mongodb:
    image: mongo:7
    networks:
      - backend
    expose:
      - "27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME_FILE=/run/secrets/mongo_root_username
      - MONGO_INITDB_ROOT_PASSWORD_FILE=/run/secrets/mongo_root_password
    secrets:
      - mongo_root_username
      - mongo_root_password
    volumes:
      - mongodb_data:/data/db:rw
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true

secrets:
  mongo_root_username:
    file: ./secrets/mongo_root_username.txt
  mongo_root_password:
    file: ./secrets/mongo_root_password.txt

volumes:
  mongodb_data:
    driver: local
```

### 3. Secrets Management

```bash
#!/bin/bash
# scripts/manage-secrets.sh

VAULT_ADDR=${VAULT_ADDR:-"https://vault.company.com:8200"}
VAULT_TOKEN_FILE="/etc/vault/token"

# Função para obter secret do Vault
get_secret() {
    local secret_path=$1
    local secret_key=$2
    
    curl -s -H "X-Vault-Token: $(cat $VAULT_TOKEN_FILE)" \
         "$VAULT_ADDR/v1/$secret_path" | \
         jq -r ".data.data.$secret_key"
}

# Função para definir secrets como variáveis de ambiente
load_secrets() {
    export MONGODB_ROOT_PASSWORD=$(get_secret "secret/mongodb" "root_password")
    export JWT_SECRET_KEY=$(get_secret "secret/api" "jwt_secret")
    export OPENAI_API_KEY=$(get_secret "secret/ai" "openai_key")
    export GOOGLE_API_KEY=$(get_secret "secret/ai" "google_key")
    export WEBHOOK_SECRET=$(get_secret "secret/webhooks" "signing_secret")
}

# Função para rotacionar secrets
rotate_secrets() {
    local secret_type=$1
    
    case $secret_type in
        "jwt")
            new_secret=$(openssl rand -base64 64)
            vault kv put secret/api jwt_secret="$new_secret"
            echo "JWT secret rotated"
            ;;
        "webhook")
            new_secret=$(openssl rand -hex 32)
            vault kv put secret/webhooks signing_secret="$new_secret"
            echo "Webhook secret rotated"
            ;;
        *)
            echo "Unknown secret type: $secret_type"
            exit 1
            ;;
    esac
    
    # Trigger deployment para aplicar novos secrets
    ./deploy.sh production
}

# Menu principal
case ${1:-"load"} in
    "load")
        load_secrets
        echo "Secrets loaded"
        ;;
    "rotate")
        rotate_secrets $2
        ;;
    *)
        echo "Usage: $0 [load|rotate] [secret_type]"
        exit 1
        ;;
esac
```

---

## ⚡ Scaling e Performance

### 1. Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  nginx-lb:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx-lb.conf:/etc/nginx/nginx.conf
    depends_on:
      - gatekeeper-api-1
      - gatekeeper-api-2
      - gatekeeper-api-3

  gatekeeper-api-1:
    image: gatekeeper-api:latest
    environment:
      - INSTANCE_ID=api-1
      - MONGODB_URL=mongodb://mongodb-primary:27017
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  gatekeeper-api-2:
    image: gatekeeper-api:latest
    environment:
      - INSTANCE_ID=api-2
      - MONGODB_URL=mongodb://mongodb-primary:27017
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  gatekeeper-api-3:
    image: gatekeeper-api:latest
    environment:
      - INSTANCE_ID=api-3
      - MONGODB_URL=mongodb://mongodb-primary:27017
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  # MongoDB Replica Set
  mongodb-primary:
    image: mongo:7
    command: mongod --replSet rs0 --bind_ip_all
    environment:
      MONGO_REPLICA_SET_NAME: rs0

  mongodb-secondary-1:
    image: mongo:7
    command: mongod --replSet rs0 --bind_ip_all
    depends_on:
      - mongodb-primary

  mongodb-secondary-2:
    image: mongo:7
    command: mongod --replSet rs0 --bind_ip_all
    depends_on:
      - mongodb-primary
```

### 2. Performance Tuning

```python
# performance/tuning.py
import asyncio
import aiohttp
from aiohttp import web
import uvloop  # Faster event loop
import ujson   # Faster JSON

# Configurar event loop mais rápido
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Configuração de performance para FastAPI
app_config = {
    "host": "0.0.0.0",
    "port": 8001,
    "workers": 4,  # CPU cores * 2
    "worker_class": "uvicorn.workers.UvicornWorker",
    "worker_connections": 1000,
    "max_requests": 1000,
    "max_requests_jitter": 100,
    "timeout": 30,
    "keepalive": 5,
    "preload": True,
}

# Pool de conexões otimizado
async def create_optimized_session():
    timeout = aiohttp.ClientTimeout(total=30, connect=5)
    connector = aiohttp.TCPConnector(
        limit=100,           # Total connection limit
        limit_per_host=30,   # Per-host connection limit
        keepalive_timeout=60,
        enable_cleanup_closed=True,
        ttl_dns_cache=300,
    )
    
    return aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        json_serialize=ujson.dumps,
        read_timeout=None,
        conn_timeout=5,
        auto_decompress=False  # Desabilitar descompressão automática
    )

# Cache em memória para consultas frequentes
from functools import lru_cache
import redis

redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True,
    max_connections=20,
    socket_keepalive=True,
    socket_keepalive_options={},
    health_check_interval=30
)

@lru_cache(maxsize=1000)
def cached_expensive_operation(key: str):
    """Cache de operações caras em memória"""
    # Verificar Redis primeiro
    cached = redis_client.get(f"cache:{key}")
    if cached:
        return ujson.loads(cached)
    
    # Executar operação cara
    result = expensive_operation(key)
    
    # Salvar no Redis
    redis_client.setex(
        f"cache:{key}",
        300,  # 5 minutos TTL
        ujson.dumps(result)
    )
    
    return result

# Otimização de queries MongoDB
class OptimizedQueries:
    @staticmethod
    async def get_orders_optimized(
        db,
        limit: int = 20,
        offset: int = 0,
        filters: dict = None
    ):
        """Query otimizada para orders"""
        pipeline = []
        
        # Match stage com índices
        if filters:
            pipeline.append({"$match": filters})
        
        # Lookup otimizado com pipeline
        pipeline.extend([
            {
                "$lookup": {
                    "from": "cte_data",
                    "localField": "_id",
                    "foreignField": "order_id", 
                    "as": "cte_data",
                    "pipeline": [
                        {"$project": {
                            "cte_number": 1,
                            "total_value": 1,
                            "issue_date": 1
                        }}
                    ]
                }
            },
            {"$unwind": {"path": "$cte_data", "preserveNullAndEmptyArrays": True}},
            {"$skip": offset},
            {"$limit": limit},
            {"$project": {
                "order_id": 1,
                "status": 1,
                "created_at": 1,
                "cte_data": 1
            }}
        ])
        
        return await db.orders.aggregate(pipeline).to_list(length=limit)
```

### 3. Auto-scaling com Kubernetes

```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gatekeeper-api
  labels:
    app: gatekeeper-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gatekeeper-api
  template:
    metadata:
      labels:
        app: gatekeeper-api
    spec:
      containers:
      - name: gatekeeper-api
        image: gatekeeper-api:latest
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: gatekeeper-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: gatekeeper-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 🔧 Troubleshooting Avançado

### 1. Debugging de Performance

```bash
#!/bin/bash
# scripts/debug-performance.sh

echo "🔍 Performance Debugging Report"
echo "================================"

# CPU Usage
echo "📊 CPU Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Memory Analysis
echo -e "\n💾 Memory Analysis:"
docker exec gatekeeper-api-prod python -c "
import psutil
import gc

process = psutil.Process()
print(f'RSS Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'VMS Memory: {process.memory_info().vms / 1024 / 1024:.2f} MB')
print(f'Memory Percent: {process.memory_percent():.2f}%')
print(f'Open Files: {len(process.open_files())}')
print(f'Connections: {len(process.connections())}')

# Garbage Collection
gc.collect()
print(f'GC Objects: {len(gc.get_objects())}')
"

# Database Performance
echo -e "\n🗄️ Database Performance:"
docker exec gatekeeper-mongo-primary mongo --eval "
db.runCommand({serverStatus: 1}).metrics.document;
db.runCommand({serverStatus: 1}).opcounters;
db.runCommand({collStats: 'orders'});
"

# Network Latency
echo -e "\n🌐 Network Latency:"
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8001/health"

# Application Logs Analysis
echo -e "\n📋 Recent Errors:"
docker logs gatekeeper-api-prod --tail=50 | grep -i error | tail -10

# Active Connections
echo -e "\n🔗 Active Connections:"
netstat -an | grep :8001 | wc -l
```

### 2. Memory Leak Detection

```python
# debugging/memory_profiler.py
import tracemalloc
import linecache
import psutil
import gc
from datetime import datetime

class MemoryProfiler:
    def __init__(self):
        self.snapshots = []
        tracemalloc.start()
    
    def take_snapshot(self, label: str):
        """Capturar snapshot da memória"""
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append((label, snapshot, datetime.now()))
        
        process = psutil.Process()
        print(f"[{label}] Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
    
    def compare_snapshots(self, index1: int, index2: int):
        """Comparar dois snapshots"""
        if len(self.snapshots) <= max(index1, index2):
            print("Invalid snapshot indices")
            return
        
        snapshot1 = self.snapshots[index1][1]
        snapshot2 = self.snapshots[index2][1]
        
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        print(f"Top 10 differences between snapshots:")
        for index, stat in enumerate(top_stats[:10], 1):
            print(f"{index}. {stat}")
    
    def get_top_memory_usage(self, limit: int = 10):
        """Obter top de uso de memória"""
        if not self.snapshots:
            print("No snapshots available")
            return
        
        snapshot = self.snapshots[-1][1]
        top_stats = snapshot.statistics('lineno')
        
        print(f"Top {limit} memory usage:")
        for index, stat in enumerate(top_stats[:limit], 1):
            print(f"{index}. {stat}")

# Uso
profiler = MemoryProfiler()

# Em pontos críticos da aplicação
profiler.take_snapshot("startup")

# Após processamento de documentos
profiler.take_snapshot("after_document_processing")

# Comparar
profiler.compare_snapshots(0, 1)
profiler.get_top_memory_usage()
```

### 3. Database Query Analysis

```python
# debugging/db_profiler.py
import pymongo
import time
from datetime import datetime

class DatabaseProfiler:
    def __init__(self, db_url: str):
        self.client = pymongo.MongoClient(db_url)
        self.db = self.client.gatekeeper
        self.enable_profiling()
    
    def enable_profiling(self):
        """Ativar profiling do MongoDB"""
        # Level 2: profile all operations
        self.db.set_profiling_level(2)
    
    def analyze_slow_queries(self, min_duration_ms: int = 100):
        """Analisar queries lentas"""
        profile_collection = self.db['system.profile']
        
        slow_queries = profile_collection.find({
            'millis': {'$gte': min_duration_ms}
        }).sort('millis', -1).limit(20)
        
        print(f"Slow queries (>{min_duration_ms}ms):")
        for query in slow_queries:
            print(f"""
Query: {query.get('command', {})}
Duration: {query.get('millis')}ms
Timestamp: {query.get('ts')}
Collection: {query.get('ns')}
            """)
    
    def analyze_index_usage(self, collection_name: str):
        """Analisar uso de índices"""
        collection = self.db[collection_name]
        
        # Estatísticas de índices
        stats = collection.aggregate([
            {'$indexStats': {}}
        ])
        
        print(f"Index usage for {collection_name}:")
        for stat in stats:
            print(f"""
Index: {stat['name']}
Usage: {stat['accesses']['ops']} operations
Since: {stat['accesses']['since']}
            """)
    
    def suggest_indexes(self, collection_name: str):
        """Sugerir índices baseado em queries do profile"""
        profile_collection = self.db['system.profile']
        
        # Analisar padrões de query
        queries = profile_collection.find({
            'ns': f'gatekeeper.{collection_name}',
            'millis': {'$gte': 50}
        })
        
        field_usage = {}
        for query in queries:
            command = query.get('command', {})
            if 'find' in command:
                filter_fields = command.get('filter', {}).keys()
                for field in filter_fields:
                    field_usage[field] = field_usage.get(field, 0) + 1
            elif 'aggregate' in command:
                pipeline = command.get('pipeline', [])
                for stage in pipeline:
                    if '$match' in stage:
                        match_fields = stage['$match'].keys()
                        for field in match_fields:
                            field_usage[field] = field_usage.get(field, 0) + 1
        
        # Sugerir índices
        print(f"Suggested indexes for {collection_name}:")
        sorted_fields = sorted(field_usage.items(), key=lambda x: x[1], reverse=True)
        for field, count in sorted_fields[:10]:
            print(f"db.{collection_name}.createIndex({{\"{field}\": 1}}) // Used {count} times")

# Uso
profiler = DatabaseProfiler("mongodb://localhost:27017")

# Analisar performance
profiler.analyze_slow_queries(100)
profiler.analyze_index_usage('orders')
profiler.suggest_indexes('orders')
```

### 4. Automated Health Checks

```python
# monitoring/health_checker.py
import aiohttp
import asyncio
import pymongo
import redis
from datetime import datetime
from typing import Dict, List
import smtplib
from email.mime.text import MIMEText

class HealthChecker:
    def __init__(self):
        self.checks = {
            'api': self.check_api_health,
            'database': self.check_database_health,
            'redis': self.check_redis_health,
            'agents': self.check_agents_health,
            'disk_space': self.check_disk_space,
            'memory': self.check_memory_usage,
        }
        self.alerts_sent = set()
    
    async def run_health_checks(self) -> Dict:
        """Executar todas as verificações"""
        results = {}
        overall_healthy = True
        
        for check_name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[check_name] = result
                
                if not result['healthy']:
                    overall_healthy = False
                    await self.handle_unhealthy_check(check_name, result)
                    
            except Exception as e:
                results[check_name] = {
                    'healthy': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                overall_healthy = False
        
        return {
            'overall_healthy': overall_healthy,
            'timestamp': datetime.now().isoformat(),
            'checks': results
        }
    
    async def check_api_health(self) -> Dict:
        """Verificar saúde da API"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = asyncio.get_event_loop().time()
                async with session.get('http://localhost:8001/health', timeout=5) as resp:
                    end_time = asyncio.get_event_loop().time()
                    response_time = (end_time - start_time) * 1000
                    
                    return {
                        'healthy': resp.status == 200,
                        'response_time_ms': response_time,
                        'status_code': resp.status,
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def check_database_health(self) -> Dict:
        """Verificar saúde do banco de dados"""
        try:
            client = pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
            start_time = asyncio.get_event_loop().time()
            client.admin.command('ismaster')
            end_time = asyncio.get_event_loop().time()
            
            db_stats = client.gatekeeper.command('dbStats')
            
            return {
                'healthy': True,
                'response_time_ms': (end_time - start_time) * 1000,
                'collections': db_stats['collections'],
                'data_size_mb': db_stats['dataSize'] / 1024 / 1024,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def check_agents_health(self) -> Dict:
        """Verificar saúde dos agentes"""
        try:
            # Simular query para agente
            from tools.gatekeeper_api_tool import CrewAIGatekeeperTool
            
            tool = CrewAIGatekeeperTool()
            start_time = asyncio.get_event_loop().time()
            result = tool.verificar_saude_sistema()
            end_time = asyncio.get_event_loop().time()
            
            return {
                'healthy': 'erro' not in result.lower(),
                'response_time_ms': (end_time - start_time) * 1000,
                'agent_response': result[:100] + '...' if len(result) > 100 else result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def handle_unhealthy_check(self, check_name: str, result: Dict):
        """Tratar verificação não saudável"""
        alert_key = f"{check_name}_{datetime.now().strftime('%Y%m%d_%H')}"
        
        # Evitar spam de alertas (máximo 1 por hora por check)
        if alert_key in self.alerts_sent:
            return
        
        self.alerts_sent.add(alert_key)
        
        # Enviar alerta
        await self.send_alert(check_name, result)
        
        # Auto-remediation para alguns casos
        if check_name == 'api' and 'connection' in result.get('error', '').lower():
            await self.restart_api_service()
        elif check_name == 'database' and 'timeout' in result.get('error', '').lower():
            await self.restart_database_service()
    
    async def send_alert(self, check_name: str, result: Dict):
        """Enviar alerta por email/Slack"""
        message = f"""
🚨 HEALTH CHECK ALERT 🚨

Check: {check_name}
Status: UNHEALTHY
Timestamp: {result['timestamp']}
Error: {result.get('error', 'Unknown error')}

Please investigate immediately.
        """
        
        # Enviar por email (implementar conforme necessário)
        print(f"ALERT: {message}")
    
    async def restart_api_service(self):
        """Reiniciar serviço da API"""
        print("🔄 Auto-remediation: Restarting API service...")
        # Implementar restart do container/serviço
    
    async def restart_database_service(self):
        """Reiniciar serviço do banco"""
        print("🔄 Auto-remediation: Restarting database service...")
        # Implementar restart do MongoDB

# Script para executar health checks
async def main():
    checker = HealthChecker()
    
    while True:
        print("🏥 Running health checks...")
        results = await checker.run_health_checks()
        
        if results['overall_healthy']:
            print("✅ All systems healthy")
        else:
            print("❌ Some systems unhealthy - check logs")
        
        # Aguardar 1 minuto antes da próxima verificação
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📝 Conclusão

Este guia DevOps fornece uma base sólida para operação do Sistema Gatekeeper em produção. Principais pontos:

### ✅ Checklist Final de Deploy

- [ ] Todos os ambientes configurados (dev, staging, prod)
- [ ] CI/CD pipeline testado e funcionando
- [ ] Monitoramento e alertas configurados
- [ ] Backups automatizados e testados
- [ ] Procedimentos de DR documentados
- [ ] Segurança implementada (secrets, network, containers)
- [ ] Performance tuning aplicado
- [ ] Health checks automáticos rodando
- [ ] Logging centralizado configurado
- [ ] Documentação atualizada

### 🎯 Próximos Passos

1. **Monitoramento Avançado**: Implementar observabilidade completa
2. **Auto-scaling**: Configurar scaling automático baseado em métricas
3. **Multi-region**: Expandir para múltiplas regiões
4. **Chaos Engineering**: Implementar testes de resiliência
5. **Performance**: Otimização contínua baseada em métricas reais

### 📞 Suporte DevOps

- **Documentação**: Consultar arquivos específicos de cada componente
- **Monitoramento**: Grafana dashboards e Prometheus alerts
- **Logs**: Elasticsearch + Kibana para análise de logs
- **Emergências**: Procedimentos de DR e runbooks documentados

---

*Documentação DevOps atualizada em: Agosto 2024*
*Versão: 2.0.0*