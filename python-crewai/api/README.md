# MIT Tracking GraphQL API

🚚 **API GraphQL + OpenAPI** para sistema logístico completo com rastreamento em tempo real, gestão de CT-e, containers e documentos de transporte.

---

## 📋 Visão Geral

A MIT Tracking API oferece acesso programático completo ao sistema de logística, permitindo:

- **Consultas GraphQL flexíveis** - Query language poderosa
- **Documentação OpenAPI automática** - Swagger/ReDoc integrado
- **Tempo real** - Atualizações GPS e status instantâneos
- **Type Safety** - Schemas Strawberry GraphQL com validação
- **Containerizado** - Deploy pronto para produção

### 🔧 Stack Tecnológica
- **FastAPI** - Framework web assíncrono
- **Strawberry GraphQL** - Schema e resolvers type-safe
- **Docker** - Containerização completa
- **Uvicorn** - Servidor ASGI de alta performance
- **OpenAPI 3.0** - Documentação automática

---

## 🚀 Como Executar

### Método 1: Docker Completo (Recomendado)
```bash
cd python-crewai

# Iniciar API + Ollama em containers
./start-api.sh

# Acessar em http://localhost:8000
```

### Método 2: Desenvolvimento Local
```bash
cd python-crewai

# API local + Ollama opcional
./start-api-local.sh

# Acessar em http://127.0.0.1:8000
```

### Método 3: Docker Compose Manual
```bash
# Build e start
docker-compose -f docker-compose-api.yml up --build -d

# Ver logs
docker logs -f mit-api

# Parar
docker-compose -f docker-compose-api.yml down
```

---

## 🌐 Endpoints Principais

| Endpoint | Descrição | Documentação |
|----------|-----------|--------------|
| **`/`** | Root endpoint com informações da API | - |
| **`/graphql`** | GraphQL Playground interativo | 🎮 Interactive |
| **`/docs`** | Swagger UI - Documentação OpenAPI | 📚 Auto-generated |
| **`/redoc`** | ReDoc - Documentação alternativa | 📖 Clean docs |
| **`/health`** | Health check e status dos serviços | ✅ Monitoring |
| **`/metrics`** | Métricas de sistema e negócio | 📊 Analytics |

### REST Endpoints (Compatibilidade)
- `GET /api/v1/ctes` - Listar CT-e
- `GET /api/v1/containers` - Listar containers
- `GET /api/v1/bls` - Listar Bills of Lading

---

## 📊 Schema GraphQL

### 🚛 Entidades Principais

#### CT-e (Conhecimento de Transporte Eletrônico)
```graphql
type CTe {
  id: String!
  numero_cte: String!
  status: String!
  data_emissao: DateTime!
  transportadora: Transportadora!
  origem: Endereco!
  destino: Endereco!
  valor_frete: Float!
  peso_bruto: Float!
  containers: [String!]!
  previsao_entrega: DateTime
  observacoes: String
}
```

#### Container
```graphql
type Container {
  id: String!
  numero: String!
  tipo: String!
  status: String!
  posicao_atual: PosicaoGPS
  temperatura_atual: Float
  historico_posicoes: [PosicaoGPS!]!
  cte_associado: String
  peso_bruto: Float
  observacoes: String
}
```

#### BL (Bill of Lading)
```graphql
type BL {
  id: String!
  numero_bl: String!
  status: String!
  data_embarque: DateTime!
  porto_origem: String!
  porto_destino: String!
  navio: String!
  containers: [String!]!
  peso_total: Float!
  valor_mercadorias: Float!
  eta_destino: DateTime
  observacoes: String
}
```

---

## 🔍 Queries Principais

### Listar CT-e
```graphql
query {
  ctes {
    numero_cte
    status
    transportadora { nome }
    origem { municipio, uf }
    destino { municipio, uf }
    valor_frete
  }
}
```

### Buscar CT-e por Número
```graphql
query {
  cteByNumber(numero: "35240512345678901234567890123456789012") {
    numero_cte
    status
    data_emissao
    containers
    previsao_entrega
  }
}
```

### Rastrear Container
```graphql
query {
  containerByNumber(numero: "ABCD1234567") {
    numero
    status
    posicao_atual {
      latitude
      longitude
      timestamp
      endereco
    }
    temperatura_atual
  }
}
```

### Containers em Trânsito
```graphql
query {
  containersEmTransito {
    numero
    status
    posicao_atual {
      latitude
      longitude
      endereco
    }
    cte_associado
  }
}
```

### Dashboard Estatísticas
```graphql
query {
  logisticsStats {
    total_ctes
    total_containers
    containers_em_transito
    valor_total_fretes
  }
}
```

---

## ✏️ Mutations Principais

### Criar CT-e
```graphql
mutation {
  createCte(cteInput: {
    numero_cte: "35240812345678901234567890123456789999"
    status: "EM_TRANSITO"
    transportadora: {
      nome: "Nova Transportadora"
      cnpj: "12345678000199"
    }
    origem: { municipio: "São Paulo", uf: "SP" }
    destino: { municipio: "Rio de Janeiro", uf: "RJ" }
    valor_frete: 1500.00
    peso_bruto: 2500.50
    containers: ["NOVO1234567"]
  }) {
    numero_cte
    status
  }
}
```

### Atualizar Posição Container
```graphql
mutation {
  updateContainerPosition(
    numero: "ABCD1234567"
    posicao: {
      latitude: -23.5505
      longitude: -46.6333
      endereco: "Rodovia Presidente Dutra, Km 150"
    }
  ) {
    numero
    posicao_atual {
      latitude
      longitude
      timestamp
    }
  }
}
```

### Atualizar Status CT-e
```graphql
mutation {
  updateCteStatus(
    numero: "35240512345678901234567890123456789012"
    novo_status: "ENTREGUE"
  ) {
    numero_cte
    status
  }
}
```

---

## 🐍 Cliente Python

```python
import requests

API_URL = "http://localhost:8000/graphql"

def graphql_request(query, variables={}):
    response = requests.post(
        API_URL,
        json={"query": query, "variables": variables},
        headers={"Content-Type": "application/json"}
    )
    return response.json()

# Listar CT-e
ctes = graphql_request("""
    query {
      ctes {
        numero_cte
        status
        transportadora { nome }
      }
    }
""")

print(ctes)
```

---

## 🌐 Cliente JavaScript

```javascript
const API_URL = 'http://localhost:8000/graphql';

async function graphqlRequest(query, variables = {}) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables }),
  });
  return response.json();
}

// Buscar container
const container = await graphqlRequest(`
  query GetContainer($numero: String!) {
    containerByNumber(numero: $numero) {
      numero
      status
      posicao_atual { latitude, longitude, endereco }
    }
  }
`, { numero: "ABCD1234567" });

console.log(container);
```

---

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|---------|-----------|
| `API_PORT` | `8000` | Porta da API |
| `API_HOST` | `0.0.0.0` | Host da API |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL do Ollama |
| `OLLAMA_MODEL` | `llama3.2:3b` | Modelo LLM |
| `ENVIRONMENT` | `development` | Ambiente (development/production) |
| `DEBUG` | `true` | Modo debug |
| `API_AUTH_ENABLED` | `false` | Autenticação habilitada |

### Docker Ports

| Porto | Serviço | Descrição |
|-------|---------|-----------|
| `8000` | MIT API | API principal |
| `8001` | WebSocket | Futura implementação |
| `11434` | Ollama | LLM local |

---

## 📊 Monitoramento

### Health Check
```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "database": {
    "status": "connected",
    "collections": 6,
    "total_documents": 24
  },
  "mit_agent": {
    "status": "ready",
    "model": "llama3.2:3b"
  }
}
```

### Métricas
```bash
curl http://localhost:8000/metrics
```

---

## 🚀 Deploy Produção

### Docker Swarm
```bash
docker stack deploy -c docker-compose-api.yml mit-tracking
```

### Kubernetes
```yaml
# Configuração k8s disponível em k8s/
kubectl apply -f k8s/
```

### Nginx Proxy
```nginx
# Configuração em nginx/nginx.conf
location /api/ {
    proxy_pass http://mit-api:8000/;
}
```

---

## 🧪 Testing

### GraphQL Queries no Playground
1. Abrir http://localhost:8000/graphql
2. Testar queries interativamente
3. Explorar schema documentation

### cURL Testing
```bash
# Query CT-e
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ ctes { numero_cte status } }"}'

# Health check
curl http://localhost:8000/health
```

---

## 🔮 Próximas Features

- **WebSocket subscriptions** - Updates em tempo real
- **Authentication JWT** - Segurança avançada
- **Rate limiting** - Controle de acesso
- **Caching Redis** - Performance otimizada
- **Database real** - PostgreSQL/MongoDB
- **Kubernetes** - Orquestração completa

---

## 📞 Suporte

- **GraphQL Playground**: Interface interativa em `/graphql`
- **API Documentation**: Swagger UI em `/docs`
- **Health Check**: Status em `/health`
- **Logs**: `docker logs -f mit-api`

Para issues e contribuições, acesse o repositório do projeto.