# 🔑 MIT Logistics - Configuração de API Keys

## 🎯 Resumo
O sistema MIT Logistics v2.0 utiliza **OpenAI** e **Google Gemini** para processamento de consultas logísticas. Este guia explica como configurar as chaves API necessárias.

## ⚡ Configuração Rápida

### 1. Copie o arquivo de exemplo
```bash
cp .env.example .env
```

### 2. Edite o arquivo .env
```bash
nano .env
# ou
code .env
```

### 3. Configure suas chaves API
```env
# OpenAI (obtenha em: https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-abc123...

# Gemini (obtenha em: https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=AIzaSyAbc123...
```

### 4. Teste a configuração
```bash
python3 test-config.py
```

### 5. Inicie o sistema
```bash
./start-system.sh
```

## 🌍 Formas de Configuração

### 📁 **Método 1: Arquivo .env (Recomendado)**
Edite o arquivo `.env` na raiz do projeto:
```env
OPENAI_API_KEY=sk-proj-sua-chave-aqui
GEMINI_API_KEY=AIzaSy-sua-chave-aqui
```

### 🖥️ **Método 2: Variáveis de Ambiente**
**Linux/macOS:**
```bash
export OPENAI_API_KEY="sk-proj-sua-chave"
export GEMINI_API_KEY="AIzaSy-sua-chave"
```

**Windows:**
```cmd
set OPENAI_API_KEY=sk-proj-sua-chave
set GEMINI_API_KEY=AIzaSy-sua-chave
```

### 🌐 **Método 3: Dashboard Web**
Acesse: `http://localhost:3000/settings/llm`
- Interface visual completa
- Teste de conectividade em tempo real
- Monitoramento de custos

## 🔗 Onde Obter as Chaves

### 🤖 OpenAI API Key
1. Acesse: https://platform.openai.com/api-keys
2. Faça login/cadastro
3. Clique em "Create new secret key"
4. Copie a chave (começa com `sk-proj-` ou `sk-`)

**Modelos Disponíveis:**
- `gpt-3.5-turbo` (padrão, mais barato)
- `gpt-4` (mais avançado, mais caro)
- `gpt-4-turbo` (mais rápido)

### 💎 Google Gemini API Key
1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com conta Google
3. Clique em "Create API key"
4. Copie a chave (começa com `AIzaSy`)

**Modelos Disponíveis:**
- `gemini-pro` (padrão)
- `gemini-pro-vision` (com suporte a imagens)

## ⚙️ Configurações Avançadas

### 🎛️ Parâmetros do LLM Router
```env
# Provedor preferido (auto = roteamento inteligente)
LLM_PREFERRED_PROVIDER=auto

# Limite diário de custo por provedor (USD)
LLM_MAX_DAILY_COST=50

# Temperatura (criatividade): 0.0-2.0
LLM_TEMPERATURE=0.3

# Máximo de tokens por resposta
LLM_MAX_TOKENS=1000
```

### 🔄 Estratégia de Roteamento
O sistema automaticamente escolhe o melhor provedor baseado no tipo de consulta:

| Tipo de Consulta | Provedor Preferido | Fallback |
|------------------|-------------------|----------|
| **Logística** (CT-e, containers) | OpenAI | Gemini |
| **Financeiro** (custos, câmbio) | Gemini | OpenAI |
| **Aduaneiro** (NCM, DI) | OpenAI | Gemini |
| **Análise** (relatórios) | OpenAI | Gemini |
| **Geral** | Configurável | Automático |

## 🔍 Validação e Teste

### ✅ Teste Rápido
```bash
# Teste básico de configuração
python3 test-config.py

# Output esperado:
# ✅ OpenAI API key configurada
# ✅ Gemini API key configurada  
# ✅ Configuração válida!
```

### 🧪 Teste via Dashboard
1. Inicie o sistema: `./start-system.sh`
2. Acesse: `http://localhost:3000/settings/llm`
3. Clique em "🧪 Testar" para cada provedor
4. Verifique se retorna sucesso

### 📊 Monitoramento
O dashboard mostra em tempo real:
- ✅ Status dos provedores
- 💰 Custo consumido hoje
- ⏱️ Tempo médio de resposta
- 📈 Número de requests
- ❌ Contagem de erros

## ❗ Requisitos Mínimos

### 🎯 Configuração Mínima
- **Pelo menos 1 API key** (OpenAI OU Gemini)
- Conexão com internet
- Python 3.9+

### 💰 Custos Estimados
**OpenAI (GPT-3.5-turbo):**
- ~$0.002 por 1K tokens
- ~200-500 tokens por consulta
- ~$0.001-0.003 por consulta

**Gemini Pro:**
- ~$0.001 por 1K tokens  
- ~150-400 tokens por consulta
- ~$0.0005-0.002 por consulta

**Limite Padrão:** $50/dia por provedor

## 🚨 Solução de Problemas

### ❌ "Nenhuma API key configurada"
```bash
# Verifique se o arquivo .env existe
ls -la .env

# Verifique se as variáveis estão definidas
python3 test-config.py
```

### ❌ "API key inválida"
- **OpenAI**: Deve começar com `sk-proj-` ou `sk-`
- **Gemini**: Deve começar com `AIzaSy`
- Verifique se não há espaços extras

### ❌ "Rate limit exceeded"
- Aguarde alguns minutos
- Verifique se não atingiu o limite diário
- Configure o limite em `LLM_MAX_DAILY_COST`

### ❌ "Connection error"
- Verifique sua conexão com internet
- Teste as APIs diretamente no dashboard

## 📞 Suporte

- **Dashboard LLM**: `http://localhost:3000/settings/llm`
- **Logs do sistema**: `./start-system.sh` (veja output)
- **Teste de config**: `python3 test-config.py`

---

💡 **Dica**: Use o modo `auto` para roteamento inteligente e economia de custos!