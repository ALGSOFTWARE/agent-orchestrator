# 🔐 Configuração de Secrets no GitHub

## Passo a Passo para Configurar CI/CD

### 1. Configurar Secrets no Repository

Vá em: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

#### 🔑 **Secrets Obrigatórios:**

```bash
# AWS EC2 Connection
EC2_HOST=ec2-13-217-85-36.compute-1.amazonaws.com
EC2_USER=ubuntu
EC2_SSH_KEY=<conteúdo-completo-do-arquivo-mit-api-key.pem>

# Para produção (se tiver instância separada)
EC2_HOST_PROD=<ip-da-instancia-de-producao>

# Database
MONGODB_URL=mongodb+srv://dev:JiCoKnCCu6pHpIwZ@dev.fednd1d.mongodb.net/?retryWrites=true&w=majority&appName=dev
MONGODB_URL_PROD=<string-de-conexao-mongodb-producao>

# API Keys
OPENAI_API_KEY=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
GEMINI_API_KEY=AIzaSyB2ZdNCz4WhZPedLyww1en1rPb8X85MulI
```

### 2. Como Adicionar SSH Key

1. **Copiar conteúdo da chave:**
```bash
cat mit-api-key.pem
```

2. **Colar COMPLETO** (incluindo `-----BEGIN` e `-----END`) no secret `EC2_SSH_KEY`

### 3. Ambientes (Opcional mas Recomendado)

Criar environments para proteção adicional:

**Settings** → **Environments** → **New environment**

- **staging** (para branch dev)
- **production** (para branch main)

### 4. Triggers de Deploy

#### 🔄 **Automático:**
- **dev** → Deploy para staging
- **main** → Deploy para produção  
- **PR para main** → Apenas testes

#### ⚡ **Manual (se necessário):**
- GitHub Actions → Run workflow

## 📊 Fluxo Completo

```mermaid
graph LR
    A[Push dev] --> B[Tests]
    B --> C[Deploy Staging]
    
    D[Push main] --> E[Tests]
    E --> F[Deploy Production]
    
    G[PR main] --> H[Tests Only]
```

## 🧪 Primeira Execução

1. **Commit este arquivo**
2. **Push para branch dev**
3. **Verificar Actions tab no GitHub**
4. **Conferir logs de deploy**

## 🚨 Troubleshooting

### Se falhar SSH:
- Verificar se `EC2_SSH_KEY` tem conteúdo completo
- Confirmar que `EC2_HOST` está correto
- Security Groups devem permitir SSH do GitHub (0.0.0.0/0)

### Se falhar Health Check:
- Verificar se serviço subiu: `systemctl status gatekeeper-api`
- Conferir logs: `journalctl -u gatekeeper-api -f`

### Se falhar Dependencies:
- Pode faltar alguma dependência do sistema
- OCR pode precisar de reinstalação