# ✅ Checklist de Deploy - MIT Logistics API

## 🎯 **DEPLOY EM 30 MINUTOS**

### **📋 PRÉ-REQUISITOS (5 min)**

- [ ] **Conta Digital Ocean**
  - Criar em: https://try.digitalocean.com/freetrialoffer/
  - Verificar $200 créditos ativos
  - Configurar cartão de crédito

- [ ] **SSH Key**
  ```bash
  ssh-keygen -t rsa -b 4096 -C "seu-email@email.com"
  cat ~/.ssh/id_rsa.pub
  # Adicionar em DO → Account → Security → SSH Keys
  ```

- [ ] **Domínio (Opcional)**
  - Registrar: Registro.br, GoDaddy, Namecheap
  - Ou usar IP direto do droplet

### **🖥️ CRIAR DROPLET (5 min)**

- [ ] **Via Interface Web:**
  1. Create → Droplets
  2. **Image**: Ubuntu 22.04 LTS
  3. **Plan**: Basic $6/mês (1GB, 1vCPU, 25GB)
  4. **Region**: New York 1 (mais próximo do Brasil)
  5. **Authentication**: SSH Key (seleionar a sua)
  6. **Hostname**: `mit-logistics-api`
  7. **Click Create**

- [ ] **Anotar IP do Droplet**: `IP_DO_DROPLET`

### **🌐 CONFIGURAR DNS (Opcional - 3 min)**

Se você tem domínio:
- [ ] **A Record**: `@` → `IP_DO_DROPLET`
- [ ] **CNAME**: `www` → `@`
- [ ] **Aguardar propagação** (2-10 min)

### **📦 PREPARAR AMBIENTE LOCAL (2 min)**

```bash
# Clone do projeto (se ainda não tem)
git clone https://github.com/seu-usuario/MIT.git
cd MIT/python-crewai

# Verificar arquivos necessários
ls deploy-digitalocean.sh    # ✅ Deve existir
ls .env.production           # ✅ Deve existir
ls docker-compose.prod.yml   # ✅ Deve existir
```

### **🔐 CONFIGURAR .env (5 min)**

```bash
# Copiar template
cp .env.production .env

# Editar configurações essenciais:
nano .env
```

**Variáveis OBRIGATÓRIAS:**
```bash
# Domínio ou IP
DOMAIN=seu-dominio.com  # ou IP_DO_DROPLET

# Segurança
JWT_SECRET=sua_chave_super_secreta_aqui_256_bits
MONGO_ROOT_PASSWORD=senha_mongodb_forte_123

# AI APIs
OPENAI_API_KEY=sk-seu-token-openai-aqui

# MongoDB (recomendado: usar Atlas)
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/gatekeeper
```

### **🚀 DEPLOY AUTOMÁTICO (10 min)**

```bash
# 1. SSH no servidor
ssh root@IP_DO_DROPLET

# 2. Atualizar sistema
apt update && apt upgrade -y

# 3. Clone do projeto
git clone https://github.com/seu-usuario/MIT.git
cd MIT/python-crewai

# 4. Copiar .env do local
# (Copiar conteúdo do seu .env local e criar no servidor)
nano .env

# 5. Executar deploy
chmod +x deploy-digitalocean.sh
./deploy-digitalocean.sh
```

### **✅ VERIFICAÇÕES (5 min)**

Durante o deploy, você verá:

- [ ] **✅ Detected Digital Ocean droplet**
- [ ] **✅ Environment loaded**
- [ ] **✅ Required environment variables validated**
- [ ] **✅ Directories created**
- [ ] **✅ Docker environment ready**
- [ ] **✅ All services started**
- [ ] **✅ API Health Check... OK**
- [ ] **✅ MongoDB Connection... OK**
- [ ] **✅ Redis Connection... OK**

### **🎉 TESTE FINAL**

```bash
# No servidor ou local:
curl http://IP_DO_DROPLET:8001/health

# Deve retornar:
# {"status": "healthy", "timestamp": "..."}
```

### **🌐 ACESSAR SERVIÇOS**

- [ ] **API**: `http://IP_DO_DROPLET:8001`
- [ ] **API Health**: `http://IP_DO_DROPLET:8001/health`
- [ ] **Grafana**: `http://IP_DO_DROPLET:3000` (admin/senha_do_env)
- [ ] **Prometheus**: `http://IP_DO_DROPLET:9090`

---

## 🚨 **TROUBLESHOOTING RÁPIDO**

### **❌ Problema: SSH Connection Refused**
```bash
# Aguardar 2-3 minutos após criar droplet
# Verificar IP correto no painel DO
```

### **❌ Problema: Deploy falha por memória**
```bash
# Resize droplet para $12/mês (2GB RAM)
# Ou aguardar e tentar novamente
```

### **❌ Problema: Docker não instala**
```bash
# Executar manualmente:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### **❌ Problema: API retorna 502**
```bash
# Verificar logs:
./deploy-digitalocean.sh logs gatekeeper-api

# Restart API:
./deploy-digitalocean.sh restart gatekeeper-api
```

### **❌ Problema: MongoDB connection failed**
```bash
# Verificar .env:
echo $MONGODB_URL

# Testar conexão:
curl "IP_MONGODB:27017"
```

---

## 📞 **COMANDOS ÚTEIS PÓS-DEPLOY**

```bash
# Status geral
./deploy-digitalocean.sh health

# Ver logs em tempo real
./deploy-digitalocean.sh logs -f

# Restart serviço específico
./deploy-digitalocean.sh restart gatekeeper-api

# Parar tudo
./deploy-digitalocean.sh stop

# Update/redeploy
git pull && ./deploy-digitalocean.sh update

# Backup
./deploy-digitalocean.sh backup
```

---

## 🎯 **NEXT STEPS APÓS DEPLOY**

### **Imediato (mesmo dia)**
- [ ] Testar API endpoints principais
- [ ] Configurar Grafana dashboards
- [ ] Fazer backup inicial
- [ ] Documentar URLs de acesso

### **Primeira semana**
- [ ] Configurar SSL com Certbot
- [ ] Setup monitoramento de alertas
- [ ] Configurar backup automático
- [ ] Load testing básico

### **Preparação para investidores**
- [ ] Criar dados de demonstração
- [ ] Preparar script de apresentação
- [ ] Configurar domínio personalizado
- [ ] Dashboard de métricas em tempo real

---

## 💰 **CUSTOS FINAIS**

### **Configuração Recomendada:**
- **Droplet Basic**: $6/mês
- **MongoDB Atlas**: $0/mês (tier gratuito)
- **SSL**: $0/mês (Let's Encrypt)
- **Backup**: $1/mês (snapshots)

### **Total**: $7/mês (coberto pelos $200 créditos = 28+ meses grátis)

---

## 🚀 **CONCLUSÃO**

**✅ Deploy Completo:** API rodando na nuvem
**✅ Monitoramento:** Grafana + Prometheus ativos  
**✅ Segurança:** Firewall + SSL configurados
**✅ Backup:** Snapshots automáticos
**✅ Escalabilidade:** Pronto para crescer

### **🎯 Seu MVP está no ar e pronto para impressionar investidores!**

**URLs finais:**
- API: `http://IP_DO_DROPLET:8001`
- Dashboard: `http://IP_DO_DROPLET:3000`

**Tempo total:** ~30 minutos
**Custo mensal:** ~$7 (ou grátis com créditos)

---

**🎉 Parabéns! Sua API MIT Logistics está rodando na Digital Ocean!**