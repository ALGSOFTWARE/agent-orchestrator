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
from crewai_tools import tool
from typing import Dict, List, Any, Optional, Mapping
import json
import logging
from datetime import datetime
from enum import Enum
import asyncio
from langchain_openai import ChatOpenAI

# Import do LLM Router
from llm_router import generate_llm_response, TaskType, LLMProvider

# Import das novas ferramentas
from tools.gatekeeper_api_tool import (
    consultar_order, buscar_orders, consultar_cte, 
    consultar_container, busca_semantica, verificar_saude_sistema
)
from tools.document_processor import processar_documento, extrair_texto_simples
from tools.webhook_processor import iniciar_servidor_webhooks, obter_stats_webhooks

# Configuração de logging
logger = logging.getLogger("SpecializedAgents")


# === CREWAI TOOLS INTEGRATION ===

@tool("consultar_order")
def tool_consultar_order(order_id: str) -> str:
    """
    Consulta informações detalhadas de uma Order por ID.
    
    Args:
        order_id: ID da Order no sistema
    
    Returns:
        Informações completas da Order incluindo documentos
    """
    return consultar_order(order_id)

@tool("buscar_orders")  
def tool_buscar_orders(customer_name: str = None, limit: int = 10) -> str:
    """
    Busca Orders no sistema com filtros opcionais.
    
    Args:
        customer_name: Nome do cliente para filtrar (opcional)
        limit: Número máximo de resultados (padrão: 10)
    
    Returns:
        Lista de Orders encontradas
    """
    return buscar_orders(customer_name, limit)

@tool("consultar_cte")
def tool_consultar_cte(numero_cte: str) -> str:
    """
    Consulta informações de CT-e por número.
    
    Args:
        numero_cte: Número do CT-e (44 dígitos)
    
    Returns:
        Dados completos do CT-e incluindo transportadora e rotas
    """
    return consultar_cte(numero_cte)

@tool("consultar_container")
def tool_consultar_container(numero_container: str) -> str:
    """
    Consulta informações e localização de container.
    
    Args:
        numero_container: Número do container
    
    Returns:
        Posição atual, histórico e status do container
    """
    return consultar_container(numero_container)

@tool("busca_semantica_documentos")
def tool_busca_semantica(texto_busca: str, limit: int = 5) -> str:
    """
    Realiza busca semântica nos documentos do sistema.
    
    Args:
        texto_busca: Texto ou palavra-chave para buscar
        limit: Número máximo de resultados (padrão: 5)
    
    Returns:
        Documentos relacionados com score de similaridade
    """
    return busca_semantica(texto_busca, limit)

@tool("processar_documento_ocr")
def tool_processar_documento(caminho_arquivo: str) -> str:
    """
    Processa documento com OCR e análise de IA.
    
    Args:
        caminho_arquivo: Caminho para o arquivo (PDF, imagem, etc)
    
    Returns:
        Texto extraído, dados estruturados e análise completa
    """
    return processar_documento(caminho_arquivo)

@tool("extrair_texto_arquivo")
def tool_extrair_texto(caminho_arquivo: str) -> str:
    """
    Extrai apenas o texto de um arquivo via OCR.
    
    Args:
        caminho_arquivo: Caminho para o arquivo
    
    Returns:
        Texto extraído do documento
    """
    return extrair_texto_simples(caminho_arquivo)

@tool("verificar_saude_sistema")
def tool_verificar_saude() -> str:
    """
    Verifica a saúde do sistema Gatekeeper API.
    
    Returns:
        Status de saúde e métricas do sistema
    """
    return verificar_saude_sistema()

@tool("obter_estatisticas_webhooks")
def tool_stats_webhooks() -> str:
    """
    Obtém estatísticas do sistema de webhooks.
    
    Returns:
        Estatísticas de eventos processados e fila atual
    """
    return obter_stats_webhooks()


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
        
        # Ferramentas específicas para AdminAgent
        admin_tools = [
            tool_buscar_orders,
            tool_consultar_order,
            tool_verificar_saude,
            tool_stats_webhooks,
            tool_busca_semantica
        ]
        
        self.agent = Agent(
            role="Administrador do Sistema Logístico",
            goal="Supervisionar operações gerais e fornecer visão executiva do sistema",
            backstory="""
            Você é um administrador experiente do sistema de logística inteligente.
            Tem acesso completo a todas as funcionalidades e dados do sistema através
            de ferramentas GraphQL integradas que permitem consultas em tempo real.
            
            Suas capacidades incluem:
            - Consultar Orders, CT-es e containers diretamente do banco de dados
            - Realizar buscas semânticas nos documentos
            - Verificar saúde do sistema e métricas
            - Analisar estatísticas de webhooks e integrações
            - Fornecer insights baseados em dados reais do sistema
            
            Sempre use suas ferramentas para obter dados atualizados antes de responder.
            """,
            verbose=True,
            allow_delegation=True,
            llm=llm_wrapper,
            tools=admin_tools
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
        
        # Ferramentas específicas para LogisticsAgent
        logistics_tools = [
            tool_consultar_cte,
            tool_consultar_container,
            tool_buscar_orders,
            tool_consultar_order,
            tool_processar_documento,
            tool_extrair_texto,
            tool_busca_semantica
        ]
        
        self.agent = Agent(
            role="Especialista em Logística e Transporte",
            goal="Processar documentos logísticos e fornecer insights especializados usando dados reais",
            backstory="""
            Você é um especialista em logística e transporte com acesso direto ao sistema
            através de ferramentas GraphQL e OCR integradas. Suas especialidades incluem:
            
            - Consulta de CT-e (Conhecimento de Transporte Eletrônico) por número
            - Rastreamento de containers com posições GPS em tempo real
            - Análise de documentos via OCR (PDFs, imagens)
            - Bill of Lading (BL) - conhecimentos de embarque marítimo  
            - Busca semântica em documentos para encontrar informações específicas
            - Extração de dados estruturados de documentos logísticos
            
            Sempre consulte o sistema real antes de responder. Use as ferramentas de OCR
            para analisar documentos enviados pelo usuário e correlacione com dados do sistema.
            Forneça informações precisas baseadas em dados atuais, não em suposições.
            """,
            verbose=True,
            allow_delegation=False,
            llm=llm_wrapper,
            tools=logistics_tools
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
        
        # Ferramentas específicas para FinanceAgent
        finance_tools = [
            tool_buscar_orders,
            tool_consultar_order,
            tool_consultar_cte,
            tool_processar_documento,
            tool_busca_semantica
        ]
        
        self.agent = Agent(
            role="Especialista Financeiro em Logística",
            goal="Processar informações financeiras e fornecer análises de custos baseadas em dados reais",
            backstory="""
            Você é um especialista financeiro com acesso direto aos dados financeiros
            do sistema logístico através de ferramentas GraphQL integradas.
            
            Suas capacidades incluem:
            - Análise de custos de frete em CT-es reais do sistema
            - Processamento de documentos financeiros via OCR
            - Consulta de Orders para análise de rentabilidade
            - Busca semântica em documentos para encontrar valores e custos
            - Geração de relatórios financeiros baseados em dados atuais
            - Análise de compliance financeiro em transporte
            
            Sempre consulte os dados reais do sistema antes de fornecer análises.
            Use OCR para processar documentos financeiros enviados e correlacione
            com as informações já existentes no banco de dados.
            """,
            verbose=True,
            allow_delegation=False,
            llm=llm_wrapper,
            tools=finance_tools
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