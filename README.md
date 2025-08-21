# 🚀 MIT Logistics - Sistema Completo de Agentes Inteligentes

Sistema completo para gestão e teste de agentes de IA especializados em logística, com visualizações inteligentes e processamento de documentos via OCR.

## 📋 Visão Geral

O MIT Logistics é uma plataforma completa que permite:
- 🤖 **Teste interativo de agentes de IA** especializados em logística
- 📊 **Visualizações inteligentes** com grafos de relacionamento e análise semântica
- 📄 **Upload e processamento de documentos** com OCR automático
- 🔍 **Busca semântica visual** em documentos processados
- 📈 **Monitoramento em tempo real** de serviços e métricas
- 🔐 **Sistema de autenticação** com controle de permissões
- 🌐 **Interface web moderna** para todas as funcionalidades
- 🐳 **Deploy containerizado** com Docker

## 🏗️ Arquitetura

```
MIT Logistics/
├── frontend/           # Next.js 14 + TypeScript + CSS Modules + D3.js
├── gatekeeper-api/     # Backend Python + FastAPI + MongoDB + OCR
├── python-crewai/      # Agentes CrewAI + LangChain + Ollama
├── start-system.sh     # Script de inicialização automática
└── START-SYSTEM.md     # Guia detalhado de setup
```

### Stack Tecnológico

**Frontend:**
- Next.js 14 com App Router
- TypeScript (strict mode)
- CSS Modules + CSS Custom Properties
- D3.js para visualizações interativas
- React Hooks para state management

**Backend (Gatekeeper API):**
- Python 3.12+ com FastAPI
- MongoDB com Beanie ODM
- AWS S3 para armazenamento de arquivos
- Tesseract OCR para processamento de documentos
- Embeddings para busca semântica

**Agentes IA (CrewAI):**
- CrewAI para orquestração de agentes
- LangChain para processamento de linguagem
- Ollama para modelos de IA locais
- Temperatura baixa (0.3) para precisão

**Visualizações:**
- D3.js force simulation para grafos de relacionamento
- t-SNE/PCA para redução dimensional
- Clustering automático por categoria
- Busca semântica visual

## 🚀 Como Rodar na Sua Máquina

### Método 1: Script Automático (Mais Fácil)

```bash
# 1. Navegue até o diretório do projeto
cd /home/narrador/Projetos/MIT

# 2. Torne o script executável
chmod +x start-system.sh

# 3. Execute o script (vai instalar tudo automaticamente)
./start-system.sh
```

O script vai:
- ✅ Verificar todos os pré-requisitos
- 📦 Instalar dependências automaticamente
- 🧠 Configurar Ollama e baixar modelos
- 🚀 Iniciar todos os serviços
- 🌐 Mostrar as URLs para acesso

### Método 2: Setup Manual

Se preferir fazer manualmente, consulte o arquivo `START-SYSTEM.md` para instruções detalhadas.

### Método 3: Apenas Frontend (Para desenvolvimento)

```bash
# Se quiser rodar apenas o frontend para ver a interface
cd /home/narrador/Projetos/MIT/frontend
chmod +x start-dev.sh
./start-dev.sh
```

## 🌐 URLs do Sistema

Após iniciar, acesse:

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🖥️ **Frontend** | http://localhost:3000 | Dashboard principal |
| 🤖 **Agent Tester** | http://localhost:3000/agents | Teste os agentes de IA |
| 📊 **Visualizações** | http://localhost:3000/visualizations | Grafos e análise semântica |
| 📄 **Documentos** | http://localhost:3000/documents | Upload e OCR de documentos |
| 📋 **Orders** | http://localhost:3000/orders | Gestão de operações logísticas |
| 🔍 **Busca** | http://localhost:3000/search | Busca semântica em documentos |
| 📈 **Monitoring** | http://localhost:3000/monitoring | Métricas em tempo real |
| 🔍 **API Explorer** | http://localhost:3000/api | Playground GraphQL |
| 🛡️ **Gatekeeper API** | http://localhost:8001 | API principal com OCR |
| 🧠 **Ollama** | http://localhost:11434 | Servidor de IA local |

## 🎯 Primeiros Passos

1. **Execute o sistema**: `./start-system.sh`
2. **Abra no navegador**: http://localhost:3000
3. **Faça login**: Clique em "🔐 Entrar" e escolha um usuário teste
4. **Explore**:
   - **📄 Documentos**: Faça upload de PDFs, imagens, XMLs para processamento OCR
   - **📊 Visualizações**: Veja grafos de relacionamento e mapas semânticos
   - **🔍 Busca**: Encontre documentos por similaridade semântica
   - **📋 Orders**: Gerencie operações logísticas
   - **🤖 Agent Tester**: Converse com os agentes especializados
   - **📈 Monitoring**: Veja métricas e status dos serviços

## 🤖 Agentes Disponíveis

### MIT Tracking Agent
- **Especialidade**: Logística e rastreamento
- **Funcionalidades**: CT-e, BL, containers, ETAs
- **Exemplos**: "Onde está meu container?", "Status do CT-e X"

### Gatekeeper Agent
- **Especialidade**: Segurança e autenticação
- **Funcionalidades**: Controle de acesso, permissões
- **Exemplos**: "Quem pode acessar X?", "Validar permissões"

### Customs Agent
- **Especialidade**: Documentação aduaneira
- **Funcionalidades**: DI, DUE, classificações fiscais
- **Exemplos**: "NCM do produto X", "Status da DI"

### Financial Agent
- **Especialidade**: Operações financeiras
- **Funcionalidades**: Câmbio, custos, faturamento
- **Exemplos**: "Cotação USD hoje", "Custo do frete"

## 📊 Funcionalidades Principais

### 📄 Sistema de Documentos com OCR
- **Upload de múltiplos formatos**: PDFs, imagens (JPG, PNG), XMLs, Word, JSON
- **OCR automático**: Extração de texto via Tesseract
- **Análise inteligente**: Reconhecimento de entidades logísticas
- **Visualização completa**: Preview do texto extraído com metadados
- **Armazenamento seguro**: AWS S3 com proxy de acesso
- **Categorização automática**: CT-e, BL, Faturas, Contratos, etc.

### 📊 Visualizações Inteligentes
- **🔗 Grafo de Relacionamentos**: 
  - Visualização interativa D3.js de Orders ↔ Documents
  - 30+ Orders, 250+ Documentos mapeados
  - Filtros por Order, tooltips, zoom, drag
  - Menu contextual com ações (metadados, download)
  
- **🗺️ Mapa Semântico**:
  - Clustering automático por similaridade usando t-SNE/PCA
  - Visualização 2D/3D com projeção isométrica  
  - Redução dimensional de embeddings de texto
  - Agrupamento por categoria com legendas coloridas

- **🔍 Busca Semântica Visual**:
  - Busca por similaridade em linguagem natural
  - Preview do texto com score de relevância
  - Filtros de similaridade ajustáveis
  - Resultados ranqueados com metadados

### 📋 Gestão de Orders
- **CRUD completo**: Criar, editar, listar operações logísticas  
- **Múltiplos tipos**: Import, Export, Domestic, International, etc.
- **Status tracking**: Created, In Progress, Shipped, Delivered, etc.
- **Relacionamento com documentos**: Associação automática
- **Dados sintéticos**: 30+ Orders pré-carregadas para demonstração

### 🔍 Busca Avançada
- **Busca textual**: Em títulos, descrições, conteúdo OCR
- **Filtros combinados**: Por categoria, status, data, Order
- **Busca semântica**: "documentos sobre café", "contratos de frete"
- **Resultados em tempo real**: Com highlighting de termos

### 🔐 Sistema de Autenticação
- Usuários teste pré-configurados
- 4 níveis de permissão (Admin, Logistics, Finance, Operator)
- Simulação completa de sessões e tokens

### 🤖 Interface de Teste de Agentes
- Chat interativo com cada agente
- Histórico de conversas
- Métricas de performance
- Ações rápidas pré-definidas

### 📈 Dashboard de Monitoramento
- Status de todos os serviços
- Métricas de CPU, memória, disco
- Gráficos em tempo real
- Logs de atividade
- Health checks automáticos

### 🌐 Explorador de API
- Playground GraphQL interativo
- Documentação automática
- Exemplos de queries
- Schema explorer

## 🔧 Desenvolvimento

### Estrutura do Frontend
```
frontend/src/
├── app/                    # Next.js App Router
│   ├── (dashboard)/        # Rotas do dashboard  
│   │   ├── documents/      # Upload e gestão de documentos
│   │   ├── visualizations/ # Grafos e mapas semânticos
│   │   ├── orders/         # Gestão de operações
│   │   ├── search/         # Busca semântica
│   │   └── monitoring/     # Monitoramento
├── components/
│   ├── ui/                 # Componentes base (Button, Modal, etc)
│   ├── features/           # DocumentUpload, OrderCard, etc
│   ├── visualizations/     # NetworkGraph, SemanticMap, etc
│   └── monitoring/         # Métricas e dashboards
├── lib/                    # API clients, utils, store
├── styles/                 # CSS Modules responsivos
└── types/                  # Definições TypeScript
```

### Estrutura da Gatekeeper API
```
gatekeeper-api/
├── app/
│   ├── routes/             # Endpoints REST
│   │   ├── files.py        # Upload, OCR, proxy S3
│   │   ├── orders.py       # CRUD de operações
│   │   ├── visualizations.py # Grafos e análise
│   │   └── context.py      # Busca semântica
│   ├── services/           # Lógica de negócio
│   │   ├── document_processor.py  # OCR e análise
│   │   ├── embedding_service.py   # Embeddings
│   │   └── vector_search_service.py # Busca semântica
│   ├── models.py           # Modelos MongoDB
│   └── database.py         # Conexão e config
└── requirements.txt        # Dependências Python
```

### APIs Principais

**📄 Documents & OCR**
```bash
POST /files/upload          # Upload com OCR automático
GET  /files/{id}/ocr-text   # Texto extraído completo  
GET  /files/{id}/view       # Proxy para visualização
GET  /files/                # Listar documentos
```

**📊 Visualizações**
```bash
GET /visualizations/graph/order-documents    # Dados do grafo
GET /visualizations/semantic-map/documents   # Mapa semântico  
GET /visualizations/semantic-search/similar  # Busca semântica
```

**📋 Orders**
```bash
GET    /orders/          # Listar operações
POST   /orders/          # Criar operação
PUT    /orders/{id}      # Atualizar operação  
DELETE /orders/{id}      # Deletar operação
```

### Scripts Disponíveis
```bash
# Frontend
cd frontend
npm run dev          # Desenvolvimento
npm run build        # Build de produção  
npm run typecheck    # Verificação de tipos

# Gatekeeper API  
cd gatekeeper-api
python -m uvicorn app.main:app --reload --port 8001

# Sistema completo
./start-system.sh    # Iniciar tudo automaticamente
```

## 🐛 Troubleshooting

### Problemas Comuns

**❌ Erro: Porta 3000 ocupada**
```bash
npx kill-port 3000
# ou
./start-system.sh  # O script mata automaticamente
```

**❌ Gatekeeper API não conecta (porta 8001)**
```bash
# Verificar se está rodando
curl http://localhost:8001/health

# Iniciar manualmente
cd gatekeeper-api
python -m uvicorn app.main:app --reload --port 8001
```

**❌ MongoDB não conecta**
```bash
# Verificar se MongoDB está rodando
sudo systemctl status mongod
# ou
brew services list | grep mongodb

# Iniciar se necessário  
sudo systemctl start mongod
# ou
brew services start mongodb/brew/mongodb-community
```

**❌ AWS S3 Access Denied**
```bash
# Verificar variáveis de ambiente
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY  
echo $AWS_REGION

# Configurar se necessário no .env do gatekeeper-api
```

**❌ OCR não funciona (Tesseract)**
```bash
# Instalar Tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-por  # Ubuntu
brew install tesseract tesseract-lang                 # macOS

# Verificar instalação
tesseract --version
```

**❌ Ollama não conecta**
```bash
# Verificar se está rodando
curl http://localhost:11434/api/version

# Reiniciar se necessário
pkill ollama && ollama serve
```

**❌ Dependências Python**
```bash
cd gatekeeper-api
pip3 install --upgrade -r requirements.txt

cd python-crewai  
pip3 install --upgrade -r requirements.txt
```

**❌ Modelos Ollama não encontrados**
```bash
ollama pull llama3.2:3b
ollama pull mistral
```

**❌ Upload de arquivos falha**
```bash
# Verificar se diretório existe
mkdir -p /tmp/uploads

# Verificar permissões
chmod 755 /tmp/uploads

# Verificar tamanho máximo (25MB por padrão)
```

### Logs e Debug

```bash
# Logs do frontend
cd frontend && npm run dev

# Logs da Gatekeeper API  
cd gatekeeper-api && python -m uvicorn app.main:app --reload --log-level debug

# Logs dos agentes CrewAI
cd python-crewai && python -m uvicorn api.main:app --log-level debug

# Status do sistema
curl http://localhost:3000/api/health
curl http://localhost:8001/health
curl http://localhost:11434/api/version

# Testar APIs principais
curl http://localhost:8001/files/
curl http://localhost:8001/orders/  
curl "http://localhost:8001/visualizations/graph/order-documents"
```

## 📱 Recursos Móveis

A interface é totalmente responsiva e funciona em:
- 📱 Smartphones (iOS/Android)
- 📱 Tablets
- 💻 Desktops
- 🖥️ Monitores ultrawide

## 🚀 Deploy em Produção

Para deploy em EC2/servidor, use o script automatizado:
```bash
# (Em desenvolvimento - será criado em breve)
./deploy-ec2.sh
```

## 📞 Suporte

**Sistema testado em:**
- Ubuntu 20.04+
- macOS 12+
- Windows 11 (WSL2)

**Requisitos mínimos:**
- Node.js 18+
- Python 3.12+
- MongoDB 4.4+
- Tesseract OCR
- 8GB RAM
- 20GB espaço livre

**Dependências principais:**
- **Frontend**: Next.js 14, TypeScript, D3.js
- **Backend**: FastAPI, MongoDB, Beanie ODM
- **IA**: CrewAI, LangChain, Ollama
- **OCR**: Tesseract, Pillow, PyPDF2
- **Storage**: AWS S3 (ou MinIO local)
- **Visualizações**: D3.js, scikit-learn (t-SNE/PCA)

## 📊 Dados de Demonstração

O sistema vem pré-carregado com dados sintéticos para demonstração:

### 📋 Orders (30+ operações)
- **Tipos**: Import, Export, Domestic Freight, International Freight, Customs Clearance, Warehousing
- **Status**: Created, In Progress, Shipped, In Transit, Delivered, Cancelled
- **Origens/Destinos**: Santos/SP, Porto Alegre/RS, Recife/PE → Hamburg/Germany, New York/USA, Shanghai/China
- **Clientes**: Global Trade Partners, Transportes Silva Ltda, Container Master, etc.
- **Valores**: USD 10K a USD 150K, múltiplas moedas (USD, BRL)

### 📄 Documentos (250+ arquivos)
- **CT-e**: Conhecimentos de Transporte Eletrônico
- **BL**: Bills of Lading marítimos  
- **Faturas**: Comerciais de exportação/importação
- **Contratos**: Prestação de serviços logísticos
- **Fotos**: Carregamento de containers, lacres, inspeções
- **Emails**: Correspondências, instruções de embarque
- **Certificados**: Diversos tipos

### 🧠 Processamento IA
- **OCR**: Texto extraído e indexado
- **Embeddings**: Vetores semânticos gerados
- **Clustering**: Agrupamento automático por similaridade
- **Relacionamentos**: Mapeamento Order ↔ Document

### 🎯 Casos de Uso para Testar
1. **Upload um PDF**: Arraste um documento real para ver o OCR
2. **Busca semântica**: Pesquise "coffee" ou "café" nas visualizações  
3. **Explore o grafo**: Clique em Orders e veja os documentos conectados
4. **Mapa semântico**: Observe os clusters de documentos similares
5. **Crie uma Order**: Teste o CRUD completo

---

## 🎉 Pronto para Usar!

Execute `./start-system.sh` e abra http://localhost:3000 no seu navegador.

**Sistema completo em produção! 🚀**