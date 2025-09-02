"""
CrewAI Service - Gatekeeper API

Serviço responsável pela comunicação com o microserviço de agentes CrewAI:
- Roteamento de requisições para agentes especializados
- Comunicação HTTP com python-crewai microservice
- Tratamento de erros e fallbacks
- Health check dos agentes
"""

import logging
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger("GatekeeperAPI.CrewAIService")


class CrewAIService:
    """Serviço de comunicação com CrewAI agents"""
    
    def __init__(self):
        # URL do microserviço de agentes CrewAI
        self.crewai_base_url = "http://localhost:8000"  # Porta do python-crewai
        self.timeout = 30.0  # Timeout para requisições
        self.max_retries = 3
        
        # Cache de status dos agentes
        self.agent_status_cache = {}
        self.last_health_check = None
        
        logger.info("🤖 CrewAIService inicializado")
    
    async def route_to_agent(
        self, 
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
            logger.info(f"🚀 Roteando para {agent_name} - usuário {user_context.get('userId')}")
            
            # Preparar payload para o CrewAI service
            payload = {
                "agent_name": agent_name,
                "user_context": user_context,
                "request_data": request_data or {
                    "type": "general_query",
                    "message": "Requisição inicial de autenticação",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Fazer requisição HTTP para o microserviço CrewAI
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.crewai_base_url}/agents/route",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Resposta recebida do {agent_name}")
                    return result
                else:
                    logger.error(f"❌ Erro HTTP {response.status_code} do {agent_name}: {response.text}")
                    return self._create_error_response(
                        agent_name, 
                        f"Erro HTTP {response.status_code}", 
                        response.text
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"⏰ Timeout ao comunicar com {agent_name}")
            return self._create_error_response(
                agent_name, 
                "Timeout", 
                "Agente não respondeu dentro do tempo limite"
            )
        except httpx.RequestError as e:
            logger.error(f"🌐 Erro de rede ao comunicar com {agent_name}: {str(e)}")
            return self._create_error_response(
                agent_name, 
                "Network Error", 
                f"Erro de comunicação: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao rotear para {agent_name}: {str(e)}")
            return self._create_error_response(
                agent_name, 
                "Unexpected Error", 
                str(e)
            )
    
    async def send_message_to_agent(
        self, 
        agent_name: str, 
        message: str, 
        user_context: Dict[str, Any],
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Envia mensagem específica para um agente
        
        Args:
            agent_name: Nome do agente
            message: Mensagem a ser enviada
            user_context: Contexto do usuário
            
        Returns:
            Resposta do agente
        """
        request_data = {
            "type": "user_message",
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        
        return await self.route_to_agent(agent_name, user_context, request_data)
    
    async def health_check(self) -> bool:
        """
        Verifica se o serviço CrewAI está funcionando
        
        Returns:
            True se o serviço está saudável
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.crewai_base_url}/health")
                
                if response.status_code == 200:
                    self.last_health_check = datetime.now()
                    return True
                else:
                    logger.warning(f"⚠️ CrewAI service health check failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro no health check do CrewAI service: {str(e)}")
            return False
    
    async def get_available_agents(self) -> List[str]:
        """
        Retorna lista de agentes disponíveis
        
        Returns:
            Lista de nomes dos agentes disponíveis
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.crewai_base_url}/agents/list")
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("available_agents", [])
                else:
                    logger.warning(f"Erro ao obter lista de agentes: {response.status_code}")
                    return ["AdminAgent", "LogisticsAgent", "FinanceAgent"]  # Fallback
                    
        except Exception as e:
            logger.error(f"Erro ao obter agentes disponíveis: {str(e)}")
            return ["AdminAgent", "LogisticsAgent", "FinanceAgent"]  # Fallback
    
    async def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """
        Obtém status específico de um agente
        
        Args:
            agent_name: Nome do agente
            
        Returns:
            Status do agente
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.crewai_base_url}/agents/{agent_name}/status")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "agent": agent_name,
                        "status": "unknown",
                        "error": f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "agent": agent_name,
                "status": "error",
                "error": str(e)
            }
    
    async def upload_document_to_agent(
        self, 
        agent_name: str, 
        document_data: bytes, 
        filename: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Faz upload de documento para processamento por um agente
        
        Args:
            agent_name: Nome do agente
            document_data: Dados binários do documento
            filename: Nome do arquivo
            user_context: Contexto do usuário
            
        Returns:
            Resposta do processamento do documento
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:  # Timeout maior para uploads
                files = {"file": (filename, document_data)}
                data = {
                    "agent_name": agent_name,
                    "user_context": str(user_context)  # Converter para string para form-data
                }
                
                response = await client.post(
                    f"{self.crewai_base_url}/agents/upload",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return self._create_error_response(
                        agent_name,
                        "Upload Error",
                        f"Erro no upload: HTTP {response.status_code}"
                    )
                    
        except Exception as e:
            logger.error(f"Erro no upload para {agent_name}: {str(e)}")
            return self._create_error_response(
                agent_name,
                "Upload Error", 
                str(e)
            )
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do serviço CrewAI
        
        Returns:
            Estatísticas do serviço
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.crewai_base_url}/stats")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": "error", "message": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _create_error_response(self, agent_name: str, error_type: str, details: str) -> Dict[str, Any]:
        """
        Cria resposta de erro padronizada
        
        Args:
            agent_name: Nome do agente
            error_type: Tipo do erro
            details: Detalhes do erro
            
        Returns:
            Resposta de erro formatada
        """
        return {
            "agent": agent_name,
            "status": "error",
            "error_type": error_type,
            "message": f"Erro na comunicação com {agent_name}",
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "fallback_available": True
        }
    
    async def test_all_agents(self) -> Dict[str, Any]:
        """
        Testa comunicação com todos os agentes
        
        Returns:
            Resultado dos testes
        """
        agents = ["AdminAgent", "LogisticsAgent", "FinanceAgent"]
        results = {}
        
        test_context = {
            "userId": "test_user",
            "role": "admin",
            "timestamp": datetime.now().isoformat()
        }
        
        test_request = {
            "type": "health_check",
            "message": "Teste de comunicação",
            "timestamp": datetime.now().isoformat()
        }
        
        for agent in agents:
            try:
                start_time = datetime.now()
                result = await self.route_to_agent(agent, test_context, test_request)
                end_time = datetime.now()
                
                response_time = (end_time - start_time).total_seconds()
                
                results[agent] = {
                    "status": "success" if result.get("status") != "error" else "error",
                    "response_time": response_time,
                    "details": result
                }
                
            except Exception as e:
                results[agent] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "test_timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if all(r["status"] == "success" for r in results.values()) else "degraded",
            "agent_results": results
        }