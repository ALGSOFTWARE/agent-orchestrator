# 🚀 MIT Logistics - Deploy para EC2

Guia completo para deploy automatizado do MIT Logistics em instância AWS EC2.

## 📋 Pré-requisitos

### 1. Instância EC2
- **OS**: Ubuntu 20.04+ ou Amazon Linux 2
- **Tipo**: t3.medium ou superior (recomendado: t3.large)
- **Storage**: 20GB+ SSD
- **RAM**: 4GB+ (recomendado: 8GB+)

### 2. Security Group
Configure as seguintes portas no Security Group:
- **22** (SSH) - Para administração
- **80** (HTTP) - Para acesso web
- **443** (HTTPS) - Para acesso web seguro

### 3. Chave SSH
- Tenha sua chave SSH privada (.pem) disponível
- Converta para formato OpenSSH se necessário

### 4. Domínio (Opcional)
- Para SSL automático, configure um domínio apontando para o IP da instância
- Exemplo: `mitlogistics.yourdomain.com`

## 🚀 Como Fazer Deploy

### Método 1: Deploy Automático (Recomendado)

```bash
# 1. Configure as variáveis de ambiente
export EC2_HOST=ec2-1-2-3-4.compute-1.amazonaws.com  # IP ou domínio da instância
export EC2_USER=ubuntu                                 # Usuário SSH (ubuntu/ec2-user)
export EC2_KEY=~/.ssh/your-key.pem                    # Caminho para sua chave SSH
export DOMAIN=mitlogistics.yourdomain.com             # Seu domínio (opcional)
export SSL_EMAIL=admin@yourdomain.com                 # Email para Let's Encrypt

# 2. Execute o script de deploy
cd /home/narrador/Projetos/MIT
./deploy-ec2.sh
```

### Método 2: Deploy Manual

Se preferir fazer passo a passo:

```bash
# 1. Conectar na instância
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-host

# 2. Instalar dependências
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git docker.io docker-compose nginx nodejs npm python3.9

# 3. Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:3b
ollama pull mistral

# 4. Clonar projeto
git clone your-repo-url mit-logistics
cd mit-logistics

# 5. Configurar e iniciar
./start-system.sh
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

| Variável | Descrição | Padrão | Obrigatório |
|----------|-----------|--------|-------------|
| `EC2_HOST` | IP ou domínio da instância EC2 | - | ✅ |
| `EC2_USER` | Usuário SSH | `ubuntu` | ❌ |
| `EC2_KEY` | Caminho para chave SSH | `~/.ssh/id_rsa` | ❌ |
| `DOMAIN` | Domínio para SSL | - | ❌ |
| `SSL_EMAIL` | Email para Let's Encrypt | `admin@mitlogistics.com` | ❌ |
| `DEPLOY_ENV` | Ambiente de deploy | `production` | ❌ |

### Tipos de Instância Recomendados

| Tipo | vCPU | RAM | Storage | Uso |
|------|------|-----|---------|-----|
| `t3.medium` | 2 | 4GB | 20GB | Desenvolvimento/Teste |
| `t3.large` | 2 | 8GB | 30GB | **Produção** (Recomendado) |
| `t3.xlarge` | 4 | 16GB | 50GB | Alto tráfego |
| `c5.large` | 2 | 4GB | 20GB | CPU intensivo |

### Configuração de DNS

Para usar um domínio personalizado:

1. **Registre um domínio** (ex: GoDaddy, Namecheap)
2. **Configure DNS** apontando para o IP da instância:
   ```
   Type: A Record
   Name: mitlogistics (ou @)
   Value: 1.2.3.4 (IP da instância)
   TTL: 300
   ```
3. **Aguarde propagação** (5-30 minutos)
4. **Execute deploy** com `DOMAIN` definido

## 📊 Monitoramento e Logs

Após o deploy, use os scripts de gerenciamento:

### Scripts Disponíveis

```bash
# Conectar na instância
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-host
cd /home/ubuntu/mit-logistics

# Gerenciar aplicação
./start-production.sh    # Iniciar tudo
./stop-production.sh     # Parar tudo
./status.sh             # Ver status
./logs.sh frontend      # Logs do frontend
./logs.sh backend       # Logs do backend
./logs.sh nginx         # Logs do Nginx
./logs.sh ollama        # Logs do Ollama
```

### URLs de Acesso

Após deploy bem-sucedido:

**Com domínio:**
- Frontend: https://yourdomain.com
- API: https://yourdomain.com/api
- Gatekeeper: https://yourdomain.com/gatekeeper
- Health: https://yourdomain.com/health

**Sem domínio:**
- Frontend: http://your-ec2-ip:3000
- API: http://your-ec2-ip:8001
- Health: http://your-ec2-ip/health

### Métricas do Sistema

```bash
# Ver uso de recursos
htop                    # CPU e memória em tempo real
df -h                   # Uso de disco
docker stats            # Estatísticas dos containers
sudo journalctl -u nginx -f  # Logs do Nginx
```

## 🔒 Segurança

### Firewall Automático
O script configura automaticamente:
- ✅ Bloqueia todas as portas por padrão
- ✅ Permite apenas SSH (22), HTTP (80), HTTPS (443)
- ✅ Nega tráfego de entrada não autorizado

### SSL/TLS
- ✅ Certificado SSL gratuito via Let's Encrypt
- ✅ Renovação automática do certificado
- ✅ Redirect HTTP → HTTPS
- ✅ Headers de segurança HSTS

### Melhores Práticas
- 🔐 Use chaves SSH fortes (mínimo RSA 2048-bit)
- 🔒 Mantenha o sistema atualizado
- 📊 Monitor logs regularmente
- 🔄 Faça backups periódicos

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão SSH
```bash
# Verificar permissões da chave
chmod 400 ~/.ssh/your-key.pem

# Testar conexão
ssh -i ~/.ssh/your-key.pem -v ubuntu@your-ec2-host
```

#### 2. Porta 80/443 Ocupadas
```bash
# Ver quem está usando a porta
sudo lsof -i :80
sudo lsof -i :443

# Parar Nginx se necessário
sudo systemctl stop nginx
```

#### 3. Ollama Não Inicia
```bash
# Verificar status
sudo systemctl status ollama

# Reiniciar serviço
sudo systemctl restart ollama

# Ver logs
sudo journalctl -u ollama -f
```

#### 4. Docker Sem Permissão
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Fazer logout/login ou:
newgrp docker
```

#### 5. Certificado SSL Falha
```bash
# Verificar se domínio aponta para IP correto
nslookup yourdomain.com

# Tentar renovar certificado
sudo certbot renew --dry-run
```

### Comandos de Debug

```bash
# Status geral do sistema
sudo systemctl status
docker ps -a
sudo netstat -tlnp

# Logs importantes
sudo journalctl -xe
docker-compose logs
sudo tail -f /var/log/nginx/error.log
```

## 🔄 Atualizações

Para atualizar a aplicação:

```bash
# 1. Conectar na instância
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-host
cd /home/ubuntu/mit-logistics

# 2. Parar aplicação
./stop-production.sh

# 3. Atualizar código
git pull origin main

# 4. Rebuild e restart
docker-compose -f docker-compose.prod.yml up --build -d

# 5. Verificar status
./status.sh
```

## 💰 Custos Estimados

### AWS EC2 (região us-east-1)

| Instância | Custo/hora | Custo/mês | Recomendação |
|-----------|------------|-----------|--------------|
| t3.medium | $0.0416 | ~$30 | Desenvolvimento |
| t3.large | $0.0832 | ~$60 | **Produção** |
| t3.xlarge | $0.1664 | ~$120 | Alto tráfego |

### Custos Adicionais
- **Storage EBS**: ~$3-5/mês (30GB)
- **Transfer**: ~$0-10/mês (dependente do tráfego)
- **Elastic IP**: $0 (se anexado à instância)

**Total estimado**: $35-70/mês para produção

## 📞 Suporte

### Logs para Suporte
Se encontrar problemas, colete estas informações:

```bash
# Sistema
uname -a
cat /etc/os-release
df -h
free -h

# Docker
docker --version
docker-compose --version
docker ps -a

# Aplicação
./status.sh
./logs.sh frontend | tail -100
./logs.sh backend | tail -100
```

### Contato
- 📧 Email: support@mitlogistics.com
- 📋 Issues: GitHub Repository
- 📖 Docs: Este arquivo

---

## 🎉 Pronto!

Após seguir este guia, você terá:
- ✅ MIT Logistics rodando em produção
- ✅ SSL configurado automaticamente
- ✅ Monitoramento e logs
- ✅ Scripts de gerenciamento
- ✅ Firewall configurado
- ✅ Backups automáticos

**Enjoy your MIT Logistics deployment! 🚀**