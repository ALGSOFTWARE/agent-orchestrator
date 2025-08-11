"""
MIT Tracking Agent - Migração do TypeScript para Python com CrewAI
"""

import os
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from colorama import Fore, Style

from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, SystemMessage, BaseMessage
from crewai import Agent

from models import (
    AgentState, AgentStats, OllamaConfig, 
    LogisticsQuery, AgentResponse, ConversationHistory, QueryType
)
from tools.logistics_tools import (
    consultar_cte_tool,
    consultar_container_tool, 
    consultar_bl_tool,
    busca_inteligente_tool,
    estatisticas_tool
)


class MITTrackingAgent:
    """
    Agente especializado em consultas logísticas
    Migrado de TypeScript para Python com melhorias
    """
    
    def __init__(self, ollama_config: Optional[OllamaConfig] = None):
        """Inicializa o agente MIT Tracking"""
        
        # Configuração padrão
        if ollama_config is None:
            ollama_config = OllamaConfig(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
                temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
            )
        
        self.state = AgentState.INITIALIZING
        self.config = ollama_config
        
        # Inicializa LLM
        self.llm = ChatOllama(
            base_url=ollama_config.base_url,
            model=ollama_config.model,
            temperature=ollama_config.temperature,
        )
        
        # System prompt especializado em logística com ferramentas
        self.system_prompt = """Você é um assistente especializado da plataforma MIT Tracking da Move In Tech. 

IMPORTANTE: Você tem acesso a um banco de dados real com informações logísticas e DEVE manter contexto da conversa.

REGRAS DE CONTEXTO:
1. SEMPRE lembre-se dos documentos consultados na conversa (CT-e, containers, BL)
2. Quando o usuário usar pronomes demonstrativos ("esse", "este", "aquele") ou se referir a "o CT-e", "o container", refere-se ao ÚLTIMO documento consultado
3. Use as informações já obtidas do banco para responder perguntas sobre o mesmo documento
4. Só consulte o banco novamente se for um documento diferente

INSTRUÇÕES DE USO DAS FERRAMENTAS:
1. Para CT-e: Use números específicos (ex: 35240512345678901234567890123456789012)
2. Para Containers: Use formato ISO (ex: ABCD1234567)
3. Para BL: Use números específicos (ex: ABCD240001)
4. Para buscas gerais: Use a busca inteligente

EXEMPLOS DE CONTEXTO:
- Usuário: "Onde está o CT-e 123...?" → Consultar banco
- Usuário: "Quando esse CT-e foi emitido?" → Usar dados já obtidos, não consultar novamente
- Usuário: "Qual a transportadora dele?" → Usar dados do CT-e já consultado

SEMPRE mantenha o histórico da conversa e responda com base nos dados já obtidos quando possível.

Responda sempre em português, de forma clara e objetiva."""
        
        # Inicializa histórico de conversa
        self.conversation_history: List[BaseMessage] = [
            SystemMessage(content=self.system_prompt)
        ]
        
        # Identificação da sessão
        self.session_id = self._generate_session_id()
        self.start_time = datetime.now()
        
        # Estatísticas
        self.stats = AgentStats()
        
        # Estado pronto
        self.state = AgentState.READY
        
        print(f"{Fore.GREEN}🤖 MIT Tracking Agent inicializado!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📋 Session ID: {self.session_id}{Style.RESET_ALL}")
    
    def _generate_session_id(self) -> str:
        """Gera ID único para a sessão"""
        timestamp = int(time.time())
        random_part = str(uuid.uuid4())[:8]
        return f"mit-{timestamp}-{random_part}"
    
    def _update_stats(self, response_time: float, success: bool) -> None:
        """Atualiza estatísticas do agente"""
        self.stats.total_queries += 1
        
        if success:
            self.stats.successful_queries += 1
        else:
            self.stats.error_count += 1
        
        # Calcula média móvel do tempo de resposta
        total = self.stats.total_queries
        current_avg = self.stats.average_response_time
        self.stats.average_response_time = (current_avg * (total - 1) + response_time) / total
        
        # Duração da sessão
        self.stats.session_duration = (datetime.now() - self.start_time).total_seconds()
    
    def _usar_ferramentas_logisticas(self, consulta: str) -> str:
        """
        Usa ferramentas especializadas baseado no tipo de consulta
        """
        consulta_lower = consulta.lower()
        
        # Detectar se é uma pergunta sobre documento já consultado (contexto)
        pronomes_contexto = ['esse', 'esta', 'este', 'aquele', 'aquela', 'dele', 'dela', 'desse', 'dessa', 'ele', 'ela']
        referencias_contexto = ['o cte', 'o ct-e', 'o container', 'o bl', 'a carga', 'o documento']
        perguntas_contexto = ['quando foi emitido', 'data emissão', 'data de emissão', 'foi emitido', 'previsão entrega', 'previsão de entrega']
        
        is_context_query = any(pronome in consulta_lower for pronome in pronomes_contexto) or \
                          any(ref in consulta_lower for ref in referencias_contexto) or \
                          any(pergunta in consulta_lower for pergunta in perguntas_contexto)
        
        # Se é pergunta de contexto, retornar None para usar LLM com histórico
        if is_context_query and not any(c.isdigit() for c in consulta):
            return None
        
        # Detectar números específicos primeiro
        import re
        
        # CT-e patterns
        cte_patterns = [
            r'(\d{44})',  # CT-e completo
            r'cte.*?(\d{10,})',  # CT-e com texto
            r'ct-e.*?(\d{10,})',  # CT-e com hífen
        ]
        
        # Container patterns  
        container_pattern = r'([A-Z]{4}\d{7})'
        
        # BL patterns
        bl_pattern = r'([A-Z]{4}\d{6})'
        
        # Buscar CT-e
        for pattern in cte_patterns:
            matches = re.findall(pattern, consulta, re.IGNORECASE)
            if matches:
                return consultar_cte_tool(matches[0])
        
        # Buscar Container
        container_matches = re.findall(container_pattern, consulta.upper())
        if container_matches:
            return consultar_container_tool(container_matches[0])
        
        # Buscar BL
        bl_matches = re.findall(bl_pattern, consulta.upper())
        if bl_matches:
            return consultar_bl_tool(bl_matches[0])
        
        # Comandos especiais
        if 'estatísticas' in consulta_lower or 'estatisticas' in consulta_lower:
            return estatisticas_tool()
        
        # Busca inteligente para todo o resto
        return busca_inteligente_tool(consulta)

    async def consultar_logistica(self, consulta: str) -> str:
        """
        Processa consulta logística
        Equivalente ao método do TypeScript
        """
        
        # Validações
        if self.state != AgentState.READY:
            raise Exception(f"Agente não está pronto. Estado atual: {self.state.value}")
        
        if not consulta or not consulta.strip():
            raise Exception("Consulta não pode estar vazia")
        
        self.state = AgentState.PROCESSING
        start_time = time.time()
        
        try:
            print(f"\n{Fore.YELLOW}🔍 Processando sua consulta...{Style.RESET_ALL}")
            
            # PRIMEIRO: Tentar usar ferramentas logísticas
            tool_response = self._usar_ferramentas_logisticas(consulta.strip())
            
            # Se é consulta de contexto (None), usar apenas LLM com histórico
            if tool_response is None:
                self.conversation_history.append(HumanMessage(content=consulta.strip()))
                response = await self.llm.ainvoke(self.conversation_history)
                self.conversation_history.append(response)
                
                response_time = time.time() - start_time
                self._update_stats(response_time, True)
                self.state = AgentState.READY
                
                return response.content
            
            # Se encontrou resultado específico nas ferramentas
            if tool_response and not tool_response.startswith("❌"):
                # Usar resultado direto das ferramentas
                response_time = time.time() - start_time
                self._update_stats(response_time, True)
                self.state = AgentState.READY
                
                # Adicionar ao histórico para contexto futuro
                self.conversation_history.append(HumanMessage(content=consulta.strip()))
                self.conversation_history.append(HumanMessage(content=f"Resultado do banco: {tool_response}"))
                
                return f"{tool_response}\n\n💡 Dados obtidos do banco MIT Tracking em tempo real."
            
            # SE NÃO ENCONTROU nas ferramentas, usar LLM + contexto da ferramenta
            contexto_completo = f"""
Consulta do usuário: {consulta.strip()}

Resultado da busca no banco de dados:
{tool_response}

Com base nestes dados do banco MIT Tracking, responda ao usuário de forma clara e objetiva.
Se não foram encontrados dados específicos, oriente o usuário sobre formatos corretos e opções disponíveis.
"""
            
            # Adiciona pergunta ao histórico
            self.conversation_history.append(
                HumanMessage(content=contexto_completo)
            )
            
            # Invoca o LLM com contexto
            response = await self.llm.ainvoke(self.conversation_history)
            
            # Adiciona resposta ao histórico
            self.conversation_history.append(response)
            
            # Atualiza estatísticas
            response_time = time.time() - start_time
            self._update_stats(response_time, True)
            self.state = AgentState.READY
            
            return response.content
            
        except Exception as error:
            response_time = time.time() - start_time
            self._update_stats(response_time, False)
            self.state = AgentState.ERROR
            
            error_message = str(error)
            print(f"{Fore.RED}❌ Erro ao consultar: {error_message}{Style.RESET_ALL}")
            
            # Retorna ao estado pronto após 1 segundo
            import asyncio
            asyncio.create_task(self._reset_state_after_error())
            
            return f"Erro ao processar consulta: {error_message}"
    
    async def _reset_state_after_error(self):
        """Reset state after error with delay"""
        import asyncio
        await asyncio.sleep(1)
        self.state = AgentState.READY
    
    def reset_agent_state(self):
        """Força reset do estado do agente para READY"""
        self.state = AgentState.READY
        print(f"{Fore.GREEN}🔄 Estado do agente resetado para READY{Style.RESET_ALL}")
    
    def limpar_historico(self) -> None:
        """Limpa histórico da conversa"""
        self.conversation_history = [
            SystemMessage(content=self.system_prompt)
        ]
        print(f"{Fore.CYAN}🧹 Histórico da conversa limpo!{Style.RESET_ALL}")
    
    def get_history_length(self) -> int:
        """Retorna tamanho do histórico"""
        return len(self.conversation_history)
    
    def get_stats(self) -> AgentStats:
        """Retorna estatísticas do agente"""
        return self.stats
    
    def get_state(self) -> AgentState:
        """Retorna estado atual"""
        return self.state
    
    def get_session_id(self) -> str:
        """Retorna ID da sessão"""
        return self.session_id
    
    def get_conversation_history(self) -> ConversationHistory:
        """Retorna histórico completo da conversa"""
        messages = []
        for msg in self.conversation_history:
            messages.append({
                "type": msg.__class__.__name__,
                "content": msg.content
            })
        
        return ConversationHistory(
            messages=messages,
            session_id=self.session_id,
            start_time=self.start_time,
            last_activity=datetime.now()
        )
    
    async def process_logistics_query(self, query: LogisticsQuery) -> AgentResponse:
        """
        Processa query estruturada e retorna resposta estruturada
        """
        start_time = time.time()
        
        try:
            response_content = await self.consultar_logistica(query.content)
            response_time = time.time() - start_time
            
            return AgentResponse(
                content=response_content,
                confidence=self._calculate_confidence(response_content),
                response_time=response_time,
                sources=["MIT Tracking Knowledge Base"],
                query_type=query.query_type,
                agent_id=self.session_id
            )
            
        except Exception as error:
            response_time = time.time() - start_time
            
            return AgentResponse(
                content=f"Erro: {str(error)}",
                confidence=0.0,
                response_time=response_time,
                sources=[],
                query_type=query.query_type,
                agent_id=self.session_id
            )
    
    def _calculate_confidence(self, response: str) -> float:
        """Calcula confiança na resposta"""
        if "Erro" in response:
            return 0.1
        if len(response) < 50:
            return 0.6
        
        # Verifica termos logísticos específicos
        logistics_terms = ["CT-e", "BL", "container", "ETA", "ETD", "carga", "transporte"]
        found_terms = sum(1 for term in logistics_terms if term.lower() in response.lower())
        
        if found_terms >= 3:
            return 0.9
        elif found_terms >= 1:
            return 0.8
        
        return 0.7
    
    def validate_input(self, input_text: str) -> Dict[str, Any]:
        """Valida entrada do usuário"""
        if not input_text or not input_text.strip():
            return {"is_valid": False, "error": "Entrada não pode estar vazia"}
        
        if len(input_text) > 1000:
            return {"is_valid": False, "error": "Entrada muito longa (máximo 1000 caracteres)"}
        
        return {"is_valid": True}
    
    @property
    def is_ready(self) -> bool:
        """Verifica se agente está pronto"""
        return self.state == AgentState.READY
    
    @property
    def has_errors(self) -> bool:
        """Verifica se há erros"""
        return self.stats.error_count > 0
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso em percentual"""
        if self.stats.total_queries == 0:
            return 0.0
        return (self.stats.successful_queries / self.stats.total_queries) * 100
    
    async def shutdown(self) -> None:
        """Encerra o agente e mostra estatísticas"""
        self.state = AgentState.SHUTDOWN
        
        print(f"\n{Fore.YELLOW}🔄 Encerrando sessão {self.session_id}...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Estatísticas da sessão:{Style.RESET_ALL}")
        print(f"   • Total de consultas: {self.stats.total_queries}")
        print(f"   • Consultas bem-sucedidas: {self.stats.successful_queries}")
        print(f"   • Erros: {self.stats.error_count}")
        print(f"   • Tempo médio de resposta: {self.stats.average_response_time:.2f}s")
        print(f"   • Taxa de sucesso: {self.success_rate:.1f}%")
        print(f"   • Duração da sessão: {self.stats.session_duration/60:.2f} minutos")
        print(f"{Fore.GREEN}✅ Sessão encerrada com sucesso!{Style.RESET_ALL}")


def create_crewai_agent(mit_agent: MITTrackingAgent) -> Agent:
    """
    Cria um CrewAI Agent baseado no MITTrackingAgent
    Bridge entre nossa implementação e CrewAI
    """
    
    return Agent(
        role="Especialista em Logística MIT Tracking",
        goal="Processar consultas sobre CT-e, containers, BL e tracking logístico com precisão",
        backstory="""Você é um especialista experiente em logística e transporte, 
        com conhecimento profundo sobre documentação fiscal eletrônica (CT-e), 
        rastreamento de containers, conhecimentos de embarque (BL) e operações portuárias.
        Você trabalha para a plataforma MIT Tracking da Move In Tech.""",
        verbose=True,
        allow_delegation=False,
        llm=mit_agent.llm
    )