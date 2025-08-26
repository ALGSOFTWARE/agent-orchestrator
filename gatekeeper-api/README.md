# Gatekeeper API - Sistema de Logística Inteligente

Microserviço de autenticação centralizada e roteamento para agentes especializados.

## 🏗️ Arquitetura

O Gatekeeper API funciona como o **ponto de entrada central** do sistema, responsável por:

1. **Autenticação e Autorização** - Validação de usuários e roles
2. **Roteamento Inteligente** - Encaminhamento para agentes especializados via CrewAI
3. **Gerenciamento de Contexto** - Histórico de interações e sessões
4. **Persistência de Dados** - MongoDB para usuários, clientes e contexto

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │────│  Gatekeeper API │────│   CrewAI API    │
│   (React)       │    │   (Port 8001)   │    │   (Port 8000)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    MongoDB      │
                       │  (Port 27017)   │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+**
2. **MongoDB** rodando em `localhost:27017`
3. **CrewAI API** rodando em `localhost:8000` (microserviço python-crewai)

### Installation

```bash
# Navegar para o diretório
cd gatekeeper-api

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente (opcional)
cp .env.example .env
```

### Environment Variables

```bash
# .env (opcional - valores padrão)
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=mit_logistics
CREWAI_BASE_URL=http://localhost:8000
LOG_LEVEL=INFO
```

### Running

```bash
# Desenvolvimento
python -m app.main

# Ou usando uvicorn diretamente
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

O serviço estará disponível em:
- **API**: http://localhost:8001
- **Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 📋 API Endpoints

### Authentication (`/auth`)

- `POST /auth/callback` - Callback principal de autenticação
- `GET /auth/login` - Redirecionamento para Identity Provider
- `POST /auth/validate` - Validação de sessão
- `GET /auth/roles` - Lista roles disponíveis
- `GET /auth/status` - Status do serviço de autenticação

### Users (`/users`)

- `GET /users/me` - Dados do usuário autenticado
- `GET /users/{user_id}` - Dados de usuário específico (admin)
- `GET /users/` - Listar usuários (admin)
- `POST /users/` - Criar usuário (admin)
- `PUT /users/{user_id}` - Atualizar usuário (admin)
- `DELETE /users/{user_id}` - Desativar usuário (admin)
- `GET /users/stats/summary` - Estatísticas de usuários (admin)

### Context (`/context`)

- `GET /context/{user_id}` - Histórico de interações
- `POST /context/{user_id}` - Adicionar contexto
- `GET /context/{user_id}/sessions` - Listar sessões
- `DELETE /context/{user_id}` - Limpar histórico (admin)
- `GET /context/stats/summary` - Estatísticas gerais (admin)

### System

- `GET /health` - Health check
- `GET /info` - Informações do sistema

## 🔐 Roles e Permissões

### Roles Disponíveis

- **`admin`** - Acesso total ao sistema
- **`logistics`** - Operações logísticas especializadas
- **`finance`** - Operações financeiras
- **`operator`** - Operações básicas de logística

### Mapeamento Role → Agent

- `admin` → `AdminAgent`
- `logistics` → `LogisticsAgent`
- `finance` → `FinanceAgent`
- `operator` → `LogisticsAgent` (compartilhado)

### Permissões por Role

```python
ROLE_PERMISSIONS = {
    "admin": ["*"],  # Acesso total
    "logistics": [
        "read:cte", "write:document", "read:container", 
        "write:tracking", "read:shipment"
    ],
    "finance": [
        "read:financial", "write:financial", "read:payment",
        "write:payment", "read:billing"
    ],
    "operator": [
        "read:cte", "write:document", "read:container"
    ]
}
```

## 🧪 Testing

### Manual Testing

```bash
# 1. Health Check
curl http://localhost:8001/health

# 2. System Info
curl http://localhost:8001/info

# 3. Authentication Test
curl -X POST http://localhost:8001/auth/callback \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test@example.com",
    "role": "logistics",
    "permissions": ["read:cte", "write:document"],
    "sessionId": "session123"
  }'

# 4. Get User Context
curl "http://localhost:8001/context/test@example.com?current_user_id=test@example.com&current_user_role=logistics"
```

### Automated Tests

```bash
# Executar testes
pytest

# Com coverage
pytest --cov=app

# Testes específicos
pytest tests/test_auth.py -v
```

## 🔄 Integration com CrewAI

O Gatekeeper se comunica com o microserviço CrewAI através de HTTP:

### Fluxo de Comunicação

1. **Frontend** → Gatekeeper API (`/auth/callback`)
2. **Gatekeeper** valida e roteia → CrewAI API (`/agents/route`)
3. **CrewAI** processa com agente especializado
4. **Resposta** volta via Gatekeeper → Frontend

### Formato de Comunicação

```python
# Request para CrewAI
{
    "agent_name": "LogisticsAgent",
    "user_context": {
        "userId": "user@example.com",
        "role": "logistics",
        "permissions": ["read:cte"],
        "sessionId": "session123"
    },
    "request_data": {
        "type": "authentication_success",
        "message": "Usuário autenticado",
        "timestamp": "2024-01-01T10:00:00Z"
    }
}
```

## 🗄️ Database Schema

### Users Collection

```javascript
{
  "_id": ObjectId,
  "name": "João Silva",
  "email": "joao@empresa.com",
  "role": "logistics",
  "client": ObjectId, // Referência para Client
  "is_active": true,
  "created_at": ISODate,
  "last_login": ISODate,
  "login_count": 15
}
```

### Context Collection

```javascript
{
  "_id": ObjectId,
  "user_id": "joao@empresa.com",
  "session_id": "session123",
  "input": "Onde está meu CT-e?",
  "output": "CT-e encontrado: status em trânsito",
  "agents_involved": ["LogisticsAgent"],
  "timestamp": ISODate,
  "metadata": {},
  "response_time": 1.23
}
```

## 🐳 Docker

```bash
# Build
docker build -t gatekeeper-api .

# Run
docker run -p 8001:8001 \
  -e MONGODB_URL=mongodb://host.docker.internal:27017 \
  -e CREWAI_BASE_URL=http://host.docker.internal:8000 \
  gatekeeper-api
```

## 📈 Monitoring

### Health Checks

- `/health` - Status geral do serviço
- `/auth/status` - Status detalhado com dependências

### Logs

Logs estruturados com levels:
- `INFO` - Operações normais
- `WARNING` - Situações de atenção
- `ERROR` - Erros que precisam investigação

### Metrics

Disponível via endpoints de estatísticas:
- Usuários ativos por role
- Sessões ativas
- Uso de agentes
- Performance de autenticação

## 🔧 Development

### Estrutura do Código

```
app/
├── main.py              # FastAPI app e configuração
├── models.py            # Modelos Pydantic e Beanie
├── database.py          # Configuração MongoDB
├── routes/
│   ├── auth.py         # Rotas de autenticação
│   ├── users.py        # Gerenciamento de usuários
│   └── context.py      # Histórico e contexto
└── services/
    ├── auth_service.py  # Lógica de autenticação
    └── crewai_service.py # Comunicação com CrewAI
```

### Adding New Features

1. **Novo Endpoint**: Adicionar em `routes/`
2. **Novo Model**: Adicionar em `models.py`
3. **Nova Lógica**: Adicionar service em `services/`
4. **Testes**: Adicionar em `tests/`

## 🚨 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   ```bash
   # Verificar se MongoDB está rodando
   mongosh --eval "db.adminCommand('ping')"
   ```

2. **CrewAI Service Unavailable**
   ```bash
   # Verificar se CrewAI está rodando
   curl http://localhost:8000/health
   ```

3. **Permission Denied Errors**
   - Verificar roles e permissões nos logs
   - Validar payload de autenticação

### Debug Mode

```bash
# Executar com debug
LOG_LEVEL=DEBUG python -m app.main
```

---

## 🤝 Contributing

1. Fork o repositório
2. Crie feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit changes (`git commit -am 'Add nova funcionalidade'`)
4. Push branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

## 📄 License

MIT License - veja [LICENSE](LICENSE) para detalhes.