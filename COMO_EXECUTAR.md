# 🚀 Como Executar o Sistema MIT Logistics

## Opção 1: Script Automático (Recomendado)

```bash
cd /home/narrador/Projetos/MIT
bash start_system.sh
```

**O script irá:**
- ✅ Verificar dependências
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências
- ✅ Inicializar API (porta 8001)
- ✅ Inicializar Frontend (porta 5173)
- ✅ Configurar integração automática

## Opção 2: Execução Manual

### 1. Backend (Terminal 1)
```bash
cd /home/narrador/Projetos/MIT/gatekeeper-api

# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install fastapi uvicorn python-multipart beanie motor python-dotenv

# Executar API
python -m app.main
```

### 2. Frontend (Terminal 2)
```bash
cd /home/narrador/Projetos/MIT/logistic-pulse-31-main

# Instalar dependências
npm install

# Executar frontend
npm run dev
```

## 🌐 URLs de Acesso

- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8001/docs
- **Chat IA:** http://localhost:5173 (aba "Chat Inteligente")

## 🧪 Testar Integração

### No Chat, teste comandos como:

1. **Consulta de Documentos:**
   - "Consultar CT-e da carga ABC123"
   - "Mostrar documentos pendentes"
   - "Buscar NF-e do cliente Empresa ABC"

2. **Status de Entregas:**
   - "Status da entrega para São Paulo"
   - "Mostrar entregas em trânsito"
   - "Rastrear entrega ENT-001"

3. **Jornadas:**
   - "Mostrar jornadas em andamento"
   - "Status da jornada JOR-001"

## 🔧 Solução de Problemas

### API não inicia (porta 8001)
```bash
# Verificar se porta está em uso
sudo lsof -i :8001

# Matar processo se necessário
sudo kill -9 <PID>
```

### Frontend não inicia (porta 5173)
```bash
# Limpar cache do npm
npm run build --clean

# Ou usar yarn
yarn install
yarn dev
```

### Erro de CORS
Certifique-se que o frontend está em `http://localhost:5173` e a API em `http://localhost:8001`.

### MongoDB não conecta
```bash
# Instalar MongoDB localmente ou usar MongoDB Atlas
# Para desenvolvimento, a API funciona sem MongoDB (dados mock)
```

## 📱 Funcionalidades Disponíveis

### ✅ Integradas com AI
- Chat Inteligente com processamento NLP
- Busca automática de documentos
- Interpretação de comandos naturais
- Respostas contextualizadas

### ✅ Componentes Frontend
- Dashboard com KPIs em tempo real
- Central de Documentos (upload, visualização)
- Rastreamento de Entregas
- Jornadas Logísticas (Kanban)
- Relatórios e BI

### ✅ API Endpoints
- `/api/frontend/chat/message` - Chat com IA
- `/api/frontend/documents` - Gestão de documentos
- `/api/frontend/deliveries` - Entregas
- `/api/frontend/journeys` - Jornadas
- `/api/frontend/dashboard/kpis` - Métricas

## 🐛 Debug

### Logs da API
A API mostra logs detalhados no terminal, incluindo todas as requisições.

### DevTools do Browser
Use F12 para ver requests/responses da integração frontend-backend.

### Teste de Endpoints
```bash
# Testar health da API
curl http://localhost:8001/health

# Testar chat
curl -X POST http://localhost:8001/api/frontend/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"Olá", "user_context":{"name":"Teste"}}'
```

## 🎯 Próximos Passos

1. **Produção:** Configurar MongoDB e variáveis de ambiente
2. **Deploy:** Docker Compose para orquestração
3. **Monitoramento:** Adicionar logs estruturados
4. **Testes:** Implementar testes automatizados

---
**⚡ Status:** Sistema funcional e integrado
**📅 Última atualização:** Janeiro 2025