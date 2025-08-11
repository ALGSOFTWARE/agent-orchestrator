# Migração para Orquestrador de Agentes Multi-IA

## Situação Atual vs. Objetivo

### 🔍 Situação Atual
- **Single Agent**: Um único `MITTrackingAgent` especializado em logística
- **Framework**: TypeScript + LangChain + Ollama local
- **Limitação**: `crewai-js` é uma implementação limitada, não o CrewAI oficial (Python)
- **Funcionalidade**: Conversa 1:1 sobre CT-e, containers, BL

### 🎯 Objetivo: Orquestrador Multi-Agente
- **Multiple Agents**: Diferentes agentes especializados trabalhando em conjunto
- **Orchestration**: Coordenação inteligente de tarefas entre agentes
- **Scalability**: Adicionar novos agentes facilmente
- **Flexibility**: Suporte a diferentes LLMs (Ollama, OpenAI, Anthropic, etc.)

---

## Estratégias de Migração

### 🚀 Estratégia 1: Migração para Python + CrewAI (RECOMENDADO)

#### Vantagens
✅ **CrewAI Oficial**: Framework maduro e bem documentado  
✅ **Ecosystem**: Rico em ferramentas AI (LangChain, AutoGen, etc.)  
✅ **Community**: Maior comunidade Python para IA  
✅ **Future-proof**: Atualizações frequentes e novas features  

#### Arquitetura Proposta
```python
# Estrutura do projeto Python
mit-orchestrator/
├── agents/
│   ├── cte_specialist.py           # Especialista em CT-e
│   ├── container_tracker.py       # Rastreamento containers
│   ├── bl_processor.py            # Processamento BL
│   ├── eta_calculator.py          # Cálculos ETA/ETD
│   └── logistics_coordinator.py   # Coordenador geral
├── crews/
│   ├── logistics_crew.py          # Crew principal
│   └── specialized_crews.py       # Crews específicas
├── tools/
│   ├── database_connector.py      # Conexão BD
│   ├── api_integrator.py         # APIs externas
│   └── document_parser.py        # Parser documentos
├── tasks/
│   ├── query_routing.py          # Roteamento consultas
│   ├── data_aggregation.py       # Agregação dados
│   └── response_synthesis.py     # Síntese respostas
└── main.py                       # Entry point
```

#### Agentes Especializados
```python
from crewai import Agent, Task, Crew

# 1. Especialista CT-e
cte_agent = Agent(
    role="Especialista CT-e",
    goal="Processar consultas sobre Conhecimento de Transporte Eletrônico",
    backstory="Expert em regulamentações fiscais e documentação CT-e",
    tools=[cte_validator, status_checker]
)

# 2. Rastreador Containers
container_agent = Agent(
    role="Container Tracker",
    goal="Rastrear containers em tempo real",
    backstory="Especialista em logística marítima e tracking",
    tools=[port_api, vessel_tracker]
)

# 3. Coordenador Logístico
coordinator_agent = Agent(
    role="Coordenador Logístico",
    goal="Orquestrar respostas entre especialistas",
    backstory="Gerente experiente em operações logísticas",
    tools=[query_router, response_aggregator]
)
```

#### Implementação de Crews
```python
logistics_crew = Crew(
    agents=[cte_agent, container_agent, coordinator_agent],
    tasks=[
        Task(
            description="Analisar consulta do usuário",
            agent=coordinator_agent,
            expected_output="Roteamento para agente especializado"
        ),
        Task(
            description="Processar consulta específica",
            agent="dynamic",  # Escolhido pelo coordenador
            expected_output="Resposta especializada"
        ),
        Task(
            description="Sintetizar resposta final",
            agent=coordinator_agent,
            expected_output="Resposta consolidada ao usuário"
        )
    ],
    verbose=True,
    process=Process.sequential
)
```

---

### 🔄 Estratégia 2: Orquestração Nativa TypeScript

#### Vantagens
✅ **Manter Stack**: Continuar com TypeScript/Node.js  
✅ **Rápida Implementação**: Aproveitar código existente  
✅ **Controle Total**: Orquestração customizada  

#### Arquitetura TypeScript Proposta
```typescript
// src/orchestrator/AgentOrchestrator.ts
interface Agent {
  id: string;
  role: string;
  specialization: string[];
  llm: ChatOllama;
  processQuery(query: string): Promise<AgentResponse>;
}

interface Task {
  id: string;
  description: string;
  assignedAgent: string;
  dependencies: string[];
  status: TaskStatus;
}

class AgentOrchestrator {
  private agents: Map<string, Agent> = new Map();
  private taskQueue: Task[] = [];
  private conversationHistory: ConversationContext[] = [];

  async processComplexQuery(query: string): Promise<OrchestratedResponse> {
    // 1. Análise da consulta
    const queryAnalysis = await this.analyzeQuery(query);
    
    // 2. Roteamento para agentes especialistas
    const relevantAgents = this.selectAgents(queryAnalysis);
    
    // 3. Execução paralela/sequencial
    const responses = await this.executeAgentTasks(relevantAgents, query);
    
    // 4. Síntese da resposta
    return this.synthesizeResponse(responses);
  }
}
```

#### Agentes Especializados TypeScript
```typescript
// src/agents/specialized/
├── CTESpecialistAgent.ts      # CT-e queries
├── ContainerTrackerAgent.ts  # Container tracking  
├── BLProcessorAgent.ts       # Bill of Lading
├── ETACalculatorAgent.ts     # ETA/ETD predictions
├── DocumentParserAgent.ts    # Document analysis
└── CoordinatorAgent.ts       # Query routing
```

---

### 🌐 Estratégia 3: Arquitetura Híbrida (Python Backend + TS Frontend)

#### Vantagens
✅ **Best of Both**: CrewAI (Python) + Interface (TypeScript)  
✅ **Microservices**: Escalabilidade independente  
✅ **API-First**: Integração com outros sistemas  

#### Arquitetura
```
┌─────────────────┐    HTTP/gRPC    ┌─────────────────┐
│   TypeScript    │◄──────────────► │   Python        │
│   Frontend      │                 │   CrewAI        │
│   ├── CLI       │                 │   Orchestrator  │
│   ├── Web UI    │                 │   ├── Agents    │
│   └── API Proxy │                 │   ├── Crews     │
└─────────────────┘                 │   └── Tools     │
                                    └─────────────────┘
```

---

## Plano de Implementação Detalhado

### 📋 Fase 1: Preparação (1-2 semanas)
1. **Setup Python Environment**
   ```bash
   # Criar projeto Python paralelo
   mkdir mit-orchestrator-py
   cd mit-orchestrator-py
   
   # Setup virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # Install CrewAI stack
   pip install crewai langchain-ollama python-dotenv
   ```

2. **Migração Gradual de Dados**
   - Extrair prompts e especializações do TypeScript
   - Criar schemas de dados compatíveis
   - Migrar testes e casos de uso

### 📋 Fase 2: Desenvolvimento Core (2-3 semanas)
1. **Implementar Agentes Especializados**
   ```python
   # agents/cte_specialist.py
   class CTESpecialist(Agent):
       def __init__(self):
           super().__init__(
               role="Especialista CT-e",
               goal="Processar consultas CT-e com precisão",
               backstory="Expert em documentação fiscal eletrônica",
               tools=[cte_validator, status_checker, document_parser]
           )
   ```

2. **Orquestração Inteligente**
   ```python
   # orchestrator/intelligent_router.py
   class IntelligentRouter:
       def analyze_query(self, query: str) -> QueryAnalysis:
           # NLP para entender intenção
           # Classificar tipo de consulta
           # Determinar agentes necessários
           pass
   ```

### 📋 Fase 3: Integração e Testes (1-2 semanas)
1. **Testes de Integração**
   ```python
   # tests/integration/test_orchestrator.py
   def test_complex_logistics_query():
       query = "Onde está o container ABCD1234 do CT-e 35123456789?"
       response = orchestrator.process_query(query)
       assert "container" in response.content
       assert "CT-e" in response.content
   ```

2. **Performance Benchmarking**
   - Medir latência vs. agente único
   - Otimizar paralelização
   - Cache de respostas frequentes

### 📋 Fase 4: Deploy e Monitoramento (1 semana)
1. **Containerização**
   ```dockerfile
   # Dockerfile.orchestrator
   FROM python:3.11-slim
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "main.py"]
   ```

2. **Observabilidade**
   ```python
   # monitoring/agent_metrics.py
   class AgentMetrics:
       def track_query_distribution(self):
           # Qual agente mais usado
           # Tempo médio por especialização
           # Taxa de sucesso por tipo
   ```

---

## Comparação de Estratégias

| Aspecto | Python CrewAI | TypeScript Nativo | Híbrido |
|---------|---------------|-------------------|---------|
| **Desenvolvimento** | 3-4 semanas | 2-3 semanas | 4-5 semanas |
| **Manutenibilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Escalabilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Ecosystem** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## Recomendação Final

### 🏆 **Recomendação: Estratégia 1 - Python + CrewAI**

**Por quê?**
1. **Framework Maduro**: CrewAI está em desenvolvimento ativo com atualizações frequentes
2. **Ecosystem Rico**: Python tem o melhor ecossistema para IA/ML
3. **Patterns Estabelecidos**: Multi-agent orchestration é um padrão bem estabelecido em Python
4. **Future-proof**: Compatível com próximas evoluções da IA
5. **Community**: Maior suporte e exemplos disponíveis

**Cronograma Sugerido:**
- **Semana 1-2**: Setup e migração dos agentes base
- **Semana 3-4**: Implementação da orquestração
- **Semana 5**: Testes e otimizações
- **Semana 6**: Deploy e documentação

**Próximos Passos:**
1. Criar repositório Python paralelo
2. Migrar `MITTrackingAgent` para CrewAI Agent
3. Implementar orquestração básica
4. Expandir com agentes especializados
5. Integrar com interface TypeScript (opcional)

---

## Recursos Adicionais

### 📚 Documentação CrewAI
- [CrewAI Documentation](https://docs.crewai.com/)
- [Multi-Agent Patterns](https://docs.crewai.com/concepts/agents)
- [Task Orchestration](https://docs.crewai.com/concepts/tasks)

### 🛠️ Ferramentas Recomendadas
- **LangSmith**: Monitoramento e debugging
- **Weights & Biases**: Tracking de experimentos
- **FastAPI**: API REST para integração
- **Redis**: Cache de respostas
- **PostgreSQL**: Persistência de conversas

### 📊 Métricas de Sucesso
- **Accuracy**: Taxa de respostas corretas por tipo de consulta
- **Latency**: Tempo médio de resposta (objetivo: < 3s)
- **Coverage**: % de consultas que o orquestrador consegue responder
- **User Satisfaction**: Feedback qualitativo dos usuários