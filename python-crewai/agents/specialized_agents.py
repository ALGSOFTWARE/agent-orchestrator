#!/usr/bin/env python3
"""
Agentes Especializados - Sistema de Logística Inteligente

Este módulo define os agentes especializados que são orquestrados pelo Gatekeeper:
- AdminAgent: Gerenciamento geral e supervisão
- LogisticsAgent: Operações logísticas, CT-e, containers, rastreamento
- FinanceAgent: Operações financeiras, pagamentos, relatórios

Cada agente é implementado usando CrewAI para processamento inteligente.
"""

from crewai import Agent, Task, Crew
from typing import Dict, List, Any, Optional, Mapping
import json
import logging
from datetime import datetime
from enum import Enum
import asyncio
from langchain_openai import ChatOpenAI

# Import do LLM Router
from llm_router import generate_llm_response, TaskType, LLMProvider

# Configuração de logging
logger = logging.getLogger("SpecializedAgents")


def create_llm_router(task_type: TaskType = TaskType.GENERAL, temperature: float = 0.3):
    """Criar LLM usando OpenAI como base, mas com roteamento inteligente"""
    try:
        # Se OpenAI está disponível, usar OpenAI diretamente com temperatura baixa
        import os
        if os.getenv("OPENAI_API_KEY"):
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            # Fallback para mock se não há API key
            logger.warning("No OpenAI key found - using mock LLM")
            return None
    except Exception as e:
        logger.error(f"Failed to create OpenAI LLM: {e}")
        return None

class AgentType(str, Enum):
    """Tipos de agentes especializados"""
    ADMIN = "AdminAgent"
    LOGISTICS = "LogisticsAgent"
    FINANCE = "FinanceAgent"

class BaseSpecializedAgent:
    """Classe base para agentes especializados"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.created_at = datetime.now()
        self.session_history = []
    
    def log_interaction(self, user_id: str, request: str, response: str):
        """Registra interação para histórico"""
        self.session_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "request": request,
            "response": response,
            "agent": self.agent_type.value
        })

class AdminAgent(BaseSpecializedAgent):
    """
    Agente Administrativo - Supervisão geral do sistema
    
    Responsabilidades:
    - Visualização de todos os pedidos e fretes
    - Gerenciamento de usuários e permissões
    - Relatórios executivos e dashboards
    - Monitoramento do sistema
    """
    
    def __init__(self):
        super().__init__(AgentType.ADMIN)
        
        # Use LLM Router com TaskType.GENERAL para tarefas administrativas
        llm_wrapper = create_llm_router(task_type=TaskType.GENERAL, temperature=0.3)
        
        self.agent = Agent(
            role="Administrador do Sistema Logístico",
            goal="Supervisionar operações gerais e fornecer visão executiva do sistema",
            backstory="""
            Você é um administrador experiente do sistema de logística inteligente.
            Tem acesso completo a todas as funcionalidades e dados do sistema.
            Sua função é supervisionar operações, gerenciar usuários, e fornecer
            insights estratégicos para otimização dos processos logísticos.
            
            Você pode visualizar e analisar:
            - Todos os pedidos e fretes em qualquer etapa
            - Performance de operadores e equipes
            - Métricas financeiras e operacionais
            - Status geral do sistema
            """,
            verbose=True,
            allow_delegation=True,
            llm=llm_wrapper
        )
    
    async def process_request(self, user_context: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisições administrativas"""
        user_id = user_context.get("userId", "unknown")
        
        try:
            # Criar tarefa para o agente
            task = Task(
                description=f"""
                Como administrador do sistema, analise e responda à seguinte requisição:
                
                Contexto do Usuário: {json.dumps(user_context, indent=2)}
                Dados da Requisição: {json.dumps(request_data, indent=2)}
                
                Forneça uma resposta administrativa completa incluindo:
                1. Análise da requisição
                2. Dados relevantes (se aplicável)
                3. Recomendações ou ações necessárias
                4. Status geral do sistema relacionado à requisição
                """,
                agent=self.agent,
                expected_output="Resposta administrativa estruturada em JSON"
            )
            
            # Executar crew
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            
            response = {
                "agent": self.agent_type.value,
                "status": "success",
                "response": str(result),
                "context": user_context,
                "capabilities": [
                    "Visualização completa de pedidos e fretes",
                    "Gerenciamento de usuários",
                    "Relatórios executivos",
                    "Monitoramento do sistema"
                ]
            }
            
            self.log_interaction(user_id, str(request_data), str(result))
            return response
            
        except Exception as e:
            logger.error(f"Erro no AdminAgent: {str(e)}")
            return {
                "agent": self.agent_type.value,
                "status": "error",
                "error": str(e),
                "message": "Erro interno do agente administrativo"
            }

class LogisticsAgent(BaseSpecializedAgent):
    """
    Agente de Logística - Operações logísticas especializadas
    
    Responsabilidades:
    - Processamento de documentos (CT-e, BL, etc.)
    - Rastreamento de containers e cargas
    - Análise de documentos via IA
    - Inserção e consulta de dados logísticos
    """
    
    def __init__(self):
        super().__init__(AgentType.LOGISTICS)
        
        # Use LLM Router com TaskType.LOGISTICS para tarefas logísticas
        llm_wrapper = create_llm_router(task_type=TaskType.LOGISTICS, temperature=0.3)
        
        self.agent = Agent(
            role="Especialista em Logística e Transporte",
            goal="Processar documentos logísticos e fornecer insights especializados",
            backstory="""
            Você é um especialista em logística e transporte com vasto conhecimento em:
            - CT-e (Conhecimento de Transporte Eletrônico)
            - BL (Bill of Lading) - conhecimentos de embarque marítimo
            - Rastreamento de containers e cargas
            - Documentação de transporte multimodal
            - ETA/ETD (previsões de chegada e saída)
            - Status de entregas e eventos de rota
            
            Sua função é analisar documentos, extrair informações relevantes,
            fornecer insights sobre operações logísticas e ajudar operadores
            a tomar decisões informadas sobre transporte e entrega.
            """,
            verbose=True,
            allow_delegation=False,
            llm=llm_wrapper
        )
    
    async def process_request(self, user_context: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisições logísticas"""
        user_id = user_context.get("userId", "unknown")
        
        try:
            # Criar tarefa para o agente
            task = Task(
                description=f"""
                Como especialista em logística, analise e responda à seguinte requisição:
                
                Contexto do Usuário: {json.dumps(user_context, indent=2)}
                Dados da Requisição: {json.dumps(request_data, indent=2)}
                
                Forneça uma resposta especializada incluindo:
                1. Análise dos dados logísticos apresentados
                2. Informações sobre CT-e, containers, ou documentos mencionados
                3. Status de rastreamento (se aplicável)
                4. Insights e recomendações logísticas
                5. Próximos passos sugeridos
                
                Foque em terminologia logística brasileira e processos de transporte.
                """,
                agent=self.agent,
                expected_output="Resposta logística especializada em formato estruturado"
            )
            
            # Executar crew
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            
            response = {
                "agent": self.agent_type.value,
                "status": "success",
                "response": str(result),
                "context": user_context,
                "specialization": "Logística e Transporte",
                "capabilities": [
                    "Análise de CT-e e documentos de transporte",
                    "Rastreamento de containers",
                    "Insights sobre ETA/ETD",
                    "Documentação multimodal",
                    "Status de entregas"
                ]
            }
            
            self.log_interaction(user_id, str(request_data), str(result))
            return response
            
        except Exception as e:
            logger.error(f"Erro no LogisticsAgent: {str(e)}")
            return {
                "agent": self.agent_type.value,
                "status": "error",
                "error": str(e),
                "message": "Erro interno do agente de logística"
            }

class FinanceAgent(BaseSpecializedAgent):
    """
    Agente Financeiro - Operações financeiras especializadas
    
    Responsabilidades:
    - Consultas e movimentações financeiras
    - Processamento de documentos financeiros
    - Geração de relatórios de pagamento
    - Análise de custos logísticos
    """
    
    def __init__(self):
        super().__init__(AgentType.FINANCE)
        
        # Use LLM Router com TaskType.FINANCIAL para tarefas financeiras
        llm_wrapper = create_llm_router(task_type=TaskType.FINANCIAL, temperature=0.3)
        
        self.agent = Agent(
            role="Especialista Financeiro em Logística",
            goal="Processar informações financeiras e fornecer análises de custos logísticos",
            backstory="""
            Você é um especialista financeiro com foco em operações logísticas.
            Tem experiência em:
            - Análise de custos de transporte e frete
            - Processamento de documentos financeiros
            - Relatórios de pagamentos e recebimentos
            - Análise de rentabilidade de rotas
            - Gestão de contas a pagar e receber relacionadas à logística
            - Compliance financeiro em transporte
            
            Sua função é analisar dados financeiros, gerar relatórios,
            fornecer insights sobre custos e ajudar na tomada de decisões
            financeiras relacionadas às operações logísticas.
            """,
            verbose=True,
            allow_delegation=False,
            llm=llm_wrapper
        )
    
    async def process_request(self, user_context: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisições financeiras"""
        user_id = user_context.get("userId", "unknown")
        
        try:
            # Criar tarefa para o agente
            task = Task(
                description=f"""
                Como especialista financeiro em logística, analise e responda à seguinte requisição:
                
                Contexto do Usuário: {json.dumps(user_context, indent=2)}
                Dados da Requisição: {json.dumps(request_data, indent=2)}
                
                Forneça uma resposta financeira especializada incluindo:
                1. Análise dos dados financeiros apresentados
                2. Cálculos de custos ou receitas (se aplicável)
                3. Relatórios ou extratos solicitados
                4. Análise de rentabilidade ou eficiência financeira
                5. Recomendações para otimização de custos
                
                Foque em aspectos financeiros do transporte e logística.
                """,
                agent=self.agent,
                expected_output="Resposta financeira especializada com análises e recomendações"
            )
            
            # Executar crew
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            
            response = {
                "agent": self.agent_type.value,
                "status": "success",
                "response": str(result),
                "context": user_context,
                "specialization": "Financeiro Logístico",
                "capabilities": [
                    "Análise de custos de transporte",
                    "Relatórios financeiros",
                    "Gestão de pagamentos",
                    "Análise de rentabilidade",
                    "Compliance financeiro"
                ]
            }
            
            self.log_interaction(user_id, str(request_data), str(result))
            return response
            
        except Exception as e:
            logger.error(f"Erro no FinanceAgent: {str(e)}")
            return {
                "agent": self.agent_type.value,
                "status": "error",
                "error": str(e),
                "message": "Erro interno do agente financeiro"
            }

class AgentFactory:
    """Factory para criar instâncias dos agentes especializados"""
    
    _instances = {}
    
    @classmethod
    def get_agent(cls, agent_type: AgentType) -> BaseSpecializedAgent:
        """Retorna instância singleton do agente solicitado"""
        if agent_type not in cls._instances:
            if agent_type == AgentType.ADMIN:
                cls._instances[agent_type] = AdminAgent()
            elif agent_type == AgentType.LOGISTICS:
                cls._instances[agent_type] = LogisticsAgent()
            elif agent_type == AgentType.FINANCE:
                cls._instances[agent_type] = FinanceAgent()
            else:
                raise ValueError(f"Tipo de agente não suportado: {agent_type}")
        
        return cls._instances[agent_type]
    
    @classmethod
    def list_available_agents(cls) -> List[str]:
        """Lista tipos de agentes disponíveis"""
        return [agent_type.value for agent_type in AgentType]

# Função utilitária para roteamento
async def route_to_specialized_agent(
    agent_name: str, 
    user_context: Dict[str, Any], 
    request_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Roteia requisição para o agente especializado apropriado
    
    Args:
        agent_name: Nome do agente (AdminAgent, LogisticsAgent, FinanceAgent)
        user_context: Contexto do usuário (role, permissions, etc.)
        request_data: Dados da requisição a serem processados
    
    Returns:
        Resposta do agente especializado
    """
    try:
        # Mapear nome do agente para enum
        agent_type_map = {
            "AdminAgent": AgentType.ADMIN,
            "LogisticsAgent": AgentType.LOGISTICS,
            "FinanceAgent": AgentType.FINANCE
        }
        
        if agent_name not in agent_type_map:
            raise ValueError(f"Agente não encontrado: {agent_name}")
        
        agent_type = agent_type_map[agent_name]
        agent = AgentFactory.get_agent(agent_type)
        
        # Processar requisição com dados padrão se não fornecidos
        if request_data is None:
            request_data = {
                "type": "general_query",
                "message": "Requisição geral do usuário",
                "timestamp": datetime.now().isoformat()
            }
        
        result = await agent.process_request(user_context, request_data)
        
        logger.info(f"Requisição processada com sucesso pelo {agent_name}")
        return result
        
    except Exception as e:
        logger.error(f"Erro no roteamento para {agent_name}: {str(e)}")
        return {
            "agent": agent_name,
            "status": "error",
            "error": str(e),
            "message": f"Erro no roteamento para {agent_name}"
        }