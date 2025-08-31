# 🚀 INSTRUÇÕES COMPLETAS DE DEPLOY - MIT Logistics/Gatekeeper MVP

## 📋 **PRÉ-REQUISITOS**

### 🔧 **Ferramentas Necessárias**
```bash
# 1. Docker e Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose-plugin

# 2. Git (se não tiver)
sudo apt update && sudo apt install git

# 3. Verificar instalação
docker --version
docker compose version
```

### 🔑 **Contas e Credenciais Necessárias**
- [ ] **OpenAI API Key**: https://platform.openai.com/api-keys
- [ ] **Digital Ocean Account**: https://cloud.digitalocean.com (ou AWS/outras)
- [ ] **Domínio**: gatekeeper-mvp.com (ou similar) - Namecheap/GoDaddy
- [ ] **Email para SSL**: admin@seudominio.com

---

## 🏃‍♂️ **OPÇÃO 1: DEPLOY RÁPIDO (RECOMENDADO)**

### **Passo 1: Preparar Ambiente**
```bash
# 1. Clone o projeto (se ainda não fez)
cd /seu/diretorio/projetos
git clone [URL_DO_REPOSITORIO]
cd python-crewai

# 2. Criar arquivo de ambiente
cp .env.production .env

# 3. IMPORTANTE: Editar o arquivo .env com suas credenciais
nano .env
```

### **Passo 2: Configurar Variáveis (.env)**
```bash
# === OBRIGATÓRIO ALTERAR ===
DOMAIN=seu-dominio.com
OPENAI_API_KEY=sk-seu-token-aqui
MONGO_ROOT_PASSWORD=SuaSenhaForte123!
JWT_SECRET=SeuJWTSecretMinimo32Caracteres!
REDIS_PASSWORD=SuaSenhaRedis123!
GRAFANA_PASSWORD=SuaSenhaGrafana123!

# === OPCIONAL (para S3) ===
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=gatekeeper-files

# === OPCIONAL (AI adicional) ===
GEMINI_API_KEY=AI...
```

### **Passo 3: Deploy Automático**
```bash
# 1. Tornar script executável
chmod +x deploy.sh

# 2. Executar deploy (vai baixar tudo e configurar)
./deploy.sh

# 3. Aguardar conclusão (5-10 minutos)
# O script vai mostrar o progresso
```

### **Passo 4: Verificar Deploy**
```bash
# 1. Verificar se todos os serviços estão rodando
docker ps

# 2. Testar API
curl http://localhost:8001/health

# 3. Ver logs se algo der errado
docker-compose -f docker-compose.prod.yml logs gatekeeper-api
docker-compose -f docker-compose.prod.yml logs crewai-agents
```

---

## 🔧 **OPÇÃO 2: DEPLOY MANUAL (CONTROLE TOTAL)**

### **Passo 1: Preparação Manual**
```bash
# 1. Criar diretórios necessários
mkdir -p data/{mongodb,redis,prometheus,grafana}
mkdir -p logs/{api,agents}
mkdir -p uploads models nginx/ssl monitoring/{prometheus,grafana}

# 2. Definir permissões
sudo chown -R $USER:$USER data/ logs/ uploads/
```

### **Passo 2: Configurar SSL (OPCIONAL para desenvolvimento)**
```bash
# Para desenvolvimento local (certificado auto-assinado)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=BR/ST=SP/L=SaoPaulo/O=GatekeeperMVP/CN=localhost"
```

### **Passo 3: Build e Deploy Manual**
```bash
# 1. Build das imagens
docker-compose -f docker-compose.prod.yml build

# 2. Inicializar banco de dados
docker-compose -f docker-compose.prod.yml up -d mongodb redis

# 3. Aguardar inicialização (30 segundos)
sleep 30

# 4. Subir API
docker-compose -f docker-compose.prod.yml up -d gatekeeper-api

# 5. Aguardar API estar saudável (60 segundos)
sleep 60

# 6. Subir agentes
docker-compose -f docker-compose.prod.yml up -d crewai-agents

# 7. Subir proxy e monitoring
docker-compose -f docker-compose.prod.yml up -d nginx prometheus grafana
```

---

## 🌐 **CONFIGURAÇÃO DE DOMÍNIO E SSL**

### **Para Produção Real:**

**Passo 1: Configurar DNS**
```bash
# No seu provedor de DNS (Namecheap/GoDaddy/CloudFlare):
A     @                → IP_DO_SEU_SERVIDOR
A     api              → IP_DO_SEU_SERVIDOR  
A     www              → IP_DO_SEU_SERVIDOR
A     monitor          → IP_DO_SEU_SERVIDOR
```

**Passo 2: Certificado SSL com Let's Encrypt**
```bash
# 1. Instalar certbot
sudo apt install certbot python3-certbot-nginx

# 2. Parar nginx temporariamente
docker-compose -f docker-compose.prod.yml stop nginx

# 3. Gerar certificados
sudo certbot certonly --standalone \
  -d gatekeeper-mvp.com \
  -d api.gatekeeper-mvp.com \
  -d www.gatekeeper-mvp.com \
  -d monitor.gatekeeper-mvp.com

# 4. Copiar certificados para nginx
sudo cp /etc/letsencrypt/live/gatekeeper-mvp.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/gatekeeper-mvp.com/privkey.pem nginx/ssl/
sudo chown $USER:$USER nginx/ssl/*

# 5. Reiniciar nginx
docker-compose -f docker-compose.prod.yml up -d nginx
```

---

## 📊 **ACESSO AOS SERVIÇOS**

### **URLs de Acesso:**
```bash
🌐 API Principal:     http://localhost:8001
📊 Grafana:          http://localhost:3000
📈 Prometheus:       http://localhost:9090
💾 MongoDB:          localhost:27017
🔄 Redis:            localhost:6379
```

### **Credenciais Padrão:**
```bash
📊 Grafana:          admin / [GRAFANA_PASSWORD do .env]
💾 MongoDB:          admin / [MONGO_ROOT_PASSWORD do .env]
🔄 Redis:            (sem user) / [REDIS_PASSWORD do .env]
```

---

## 🔍 **COMANDOS ÚTEIS DE MANUTENÇÃO**

### **Monitoramento:**
```bash
# Ver status de todos os serviços
docker ps

# Ver logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f

# Ver logs de um serviço específico
docker-compose -f docker-compose.prod.yml logs -f gatekeeper-api
docker-compose -f docker-compose.prod.yml logs -f crewai-agents

# Verificar saúde dos serviços
./deploy.sh health
```

### **Controle de Serviços:**
```bash
# Parar todos os serviços
docker-compose -f docker-compose.prod.yml down

# Reiniciar um serviço específico
docker-compose -f docker-compose.prod.yml restart gatekeeper-api

# Reiniciar tudo
docker-compose -f docker-compose.prod.yml restart

# Ver recursos utilizados
docker stats
```

### **Backup Manual:**
```bash
# Backup do MongoDB
docker exec mongodb-prod mongodump --authenticationDatabase admin \
  -u admin -p [MONGO_ROOT_PASSWORD] --out /backup/$(date +%Y%m%d_%H%M%S)

# Backup dos uploads
tar -czf backup_uploads_$(date +%Y%m%d).tar.gz uploads/
```

---

## 🐛 **TROUBLESHOOTING COMUM**

### **Problema 1: API não responde**
```bash
# 1. Verificar logs da API
docker-compose -f docker-compose.prod.yml logs gatekeeper-api

# 2. Verificar se MongoDB está saudável
docker exec mongodb-prod mongosh --eval "db.admin.command('hello')"

# 3. Reiniciar API
docker-compose -f docker-compose.prod.yml restart gatekeeper-api
```

### **Problema 2: Agentes não funcionam**
```bash
# 1. Verificar se API está respondendo
curl http://localhost:8001/health

# 2. Verificar logs dos agentes
docker-compose -f docker-compose.prod.yml logs crewai-agents

# 3. Verificar variáveis de ambiente
docker exec crewai-agents-prod env | grep OPENAI
```

### **Problema 3: MongoDB não inicia**
```bash
# 1. Verificar espaço em disco
df -h

# 2. Verificar permissões
ls -la data/mongodb/

# 3. Limpar e reinicializar
docker-compose -f docker-compose.prod.yml down
rm -rf data/mongodb/*
docker-compose -f docker-compose.prod.yml up -d mongodb
```

### **Problema 4: Sem espaço em disco**
```bash
# 1. Limpar containers e imagens antigas
docker system prune -a

# 2. Limpar logs antigos
find logs/ -name "*.log" -mtime +7 -delete

# 3. Limpar uploads antigos (cuidado!)
# find uploads/ -mtime +30 -delete
```

---

## 📈 **PREPARAÇÃO PARA DEMO VC**

### **Passo 1: Dados de Demonstração**
```bash
# 1. Criar usuário demo
curl -X POST http://localhost:8001/api/users \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@gatekeeper-mvp.com", "password": "demo123", "role": "admin"}'

# 2. Carregar documentos de exemplo (CTe, etc.)
cp exemplos/*.pdf uploads/
```

### **Passo 2: Verificar Performance**
```bash
# 1. Teste de carga básico (se tiver Apache Bench)
ab -n 100 -c 10 http://localhost:8001/health

# 2. Verificar métricas no Grafana
# Abrir http://localhost:3000 e criar dashboard
```

### **Passo 3: Script de Demo**
```bash
# Criar arquivo com sequência da demo
echo "1. Login: demo@gatekeeper-mvp.com / demo123" > DEMO_SCRIPT.txt
echo "2. Upload de CT-e de exemplo" >> DEMO_SCRIPT.txt
echo "3. Mostrar processamento em tempo real" >> DEMO_SCRIPT.txt
echo "4. Mostrar dashboard de métricas" >> DEMO_SCRIPT.txt
echo "5. Falar sobre unit economics" >> DEMO_SCRIPT.txt
```

---

## 🚀 **DEPLOY EM DIGITAL OCEAN (PRODUÇÃO)**

### **Passo 1: Criar Droplet**
```bash
# 1. Criar conta na Digital Ocean
# 2. Criar Droplet:
#    - Ubuntu 22.04 LTS
#    - 4GB RAM, 2 vCPU (mínimo)
#    - Bloco de armazenamento 50GB
#    - Região mais próxima dos clientes
```

### **Passo 2: Configurar Servidor**
```bash
# 1. Conectar via SSH
ssh root@IP_DO_SERVIDOR

# 2. Instalar dependências
apt update && apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose-plugin git -y

# 3. Clonar projeto
git clone [URL_DO_REPO]
cd python-crewai

# 4. Configurar .env com dados reais
cp .env.production .env
nano .env  # Editar com dados reais

# 5. Deploy
chmod +x deploy.sh
./deploy.sh
```

### **Passo 3: Configurar Firewall**
```bash
# 1. Configurar UFW
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# 2. Ou usar Dashboard da Digital Ocean
```

---

## ✅ **CHECKLIST FINAL**

### **Antes da Apresentação:**
- [ ] Sistema rodando estável por 24h
- [ ] Backup testado e funcionando
- [ ] SSL configurado (se produção)
- [ ] Domínio apontando corretamente
- [ ] Dados de demo carregados
- [ ] Script de apresentação testado
- [ ] Grafana com dashboards bonitos
- [ ] Performance testada (< 200ms response time)
- [ ] Logs funcionando sem erros críticos

### **Durante a Demo:**
- [ ] Abrir URLs em abas separadas antes da apresentação
- [ ] Ter plan B (screenshots) se internet falhar
- [ ] Mostrar código funcionando, não apenas slides
- [ ] Enfatizar unit economics ($68 → $100k+)
- [ ] Falar sobre escalabilidade demonstrada

---

## 📞 **SUPORTE E RECURSOS ADICIONAIS**

### **Documentação Gerada:**
- `DEPLOYMENT_PLAN_MVP.md` - Plano completo com análise de custos
- `MVP_DEPLOYMENT_SUMMARY.md` - Resumo executivo para VC
- `SISTEMA_GATEKEEPER.md` - Documentação técnica completa
- `DEVOPS_GUIDE.md` - Guia de operações

### **Em Caso de Problemas:**
1. Verificar logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verificar saúde: `./deploy.sh health`
3. Reiniciar específico: `docker-compose -f docker-compose.prod.yml restart [serviço]`
4. Backup de emergência: Scripts em `database/backup/`

---

## 🎯 **TIMELINE SUGERIDA**

### **5 Dias Antes da Apresentação:**
- **Dia 1**: Setup infraestrutura + deploy inicial
- **Dia 2**: Testes + otimizações + SSL
- **Dia 3**: Load testing + dados de demo
- **Dia 4**: Dashboard final + rehearsal
- **Dia 5**: Buffer para ajustes finais

### **1 Dia Antes:**
- Verificar sistema 100% funcional
- Fazer backup completo
- Testar sequência de demo
- Preparar Plan B (screenshots)

---

**🚀 Pronto! Agora você tem todas as instruções para deployar o MVP e impressionar os VCs!**

*Boa sorte na apresentação! 🍀*