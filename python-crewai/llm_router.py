"""
🧠 MIT Logistics - LLM Router
Sistema de roteamento inteligente entre OpenAI e Google Gemini
"""

import os
import logging
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
import asyncio
from datetime import datetime
import json

# Import da nossa configuração
from config import config

# OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI package not available")

# Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Gemini package not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Provedores LLM disponíveis"""
    OPENAI = "openai"
    GEMINI = "gemini"
    AUTO = "auto"

class TaskType(Enum):
    """Tipos de tarefa para roteamento inteligente"""
    LOGISTICS = "logistics"           # CT-e, containers, rastreamento
    FINANCIAL = "financial"          # Câmbio, custos, faturamento
    CUSTOMS = "customs"              # Documentação aduaneira
    GENERAL = "general"              # Consultas gerais
    ANALYSIS = "analysis"            # Análise de dados
    CONVERSATION = "conversation"    # Chat conversacional

@dataclass
class LLMConfig:
    """Configuração para cada provedor LLM"""
    provider: LLMProvider
    api_key: str
    model: str
    temperature: float = 0.3
    max_tokens: int = 1000
    enabled: bool = True
    cost_per_1k_tokens: float = 0.0
    max_daily_cost: float = 50.0  # USD

@dataclass
class LLMResponse:
    """Resposta padronizada dos LLMs"""
    content: str
    provider: LLMProvider
    model: str
    tokens_used: int
    cost_estimate: float
    response_time: float
    timestamp: datetime
    metadata: Dict[str, Any]

class LLMRouter:
    """
    Roteador inteligente de LLMs
    
    Características:
    - Roteamento baseado no tipo de tarefa
    - Fallback automático entre provedores
    - Controle de custos
    - Métricas de performance
    - Load balancing
    """
    
    def __init__(self):
        self.configs: Dict[LLMProvider, LLMConfig] = {}
        self.clients: Dict[LLMProvider, Any] = {}
        self.usage_stats: Dict[str, Any] = {
            "daily_costs": {},
            "request_counts": {},
            "error_counts": {},
            "response_times": {}
        }
        
        # Estratégias de roteamento por tipo de tarefa
        self.routing_strategy = {
            TaskType.LOGISTICS: [LLMProvider.OPENAI, LLMProvider.GEMINI],
            TaskType.FINANCIAL: [LLMProvider.GEMINI, LLMProvider.OPENAI],  # Gemini melhor custo-benefício
            TaskType.CUSTOMS: [LLMProvider.OPENAI, LLMProvider.GEMINI],
            TaskType.GENERAL: [LLMProvider.GEMINI, LLMProvider.OPENAI],
            TaskType.ANALYSIS: [LLMProvider.OPENAI, LLMProvider.GEMINI],
            TaskType.CONVERSATION: [LLMProvider.GEMINI, LLMProvider.OPENAI]
        }
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Inicializar provedores LLM disponíveis"""
        
        # OpenAI Configuration
        openai_key = config.openai_api_key
        if openai_key and OPENAI_AVAILABLE:
            self.configs[LLMProvider.OPENAI] = LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key=openai_key,
                model=config.openai_model,
                temperature=config.llm_temperature,
                max_tokens=config.llm_max_tokens,
                cost_per_1k_tokens=0.002  # GPT-3.5-turbo rate
            )
            
            try:
                self.clients[LLMProvider.OPENAI] = OpenAI(api_key=openai_key)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI: {e}")
                self.configs[LLMProvider.OPENAI].enabled = False
        
        # Google Gemini Configuration
        gemini_key = config.gemini_api_key
        if gemini_key and GEMINI_AVAILABLE:
            self.configs[LLMProvider.GEMINI] = LLMConfig(
                provider=LLMProvider.GEMINI,
                api_key=gemini_key,
                model=config.gemini_model,
                temperature=config.llm_temperature,
                max_tokens=config.llm_max_tokens,
                cost_per_1k_tokens=0.001  # Gemini Pro rate
            )
            
            try:
                genai.configure(api_key=gemini_key)
                self.clients[LLMProvider.GEMINI] = genai.GenerativeModel(
                    self.configs[LLMProvider.GEMINI].model
                )
                logger.info("✅ Gemini client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
                self.configs[LLMProvider.GEMINI].enabled = False
    
    def _detect_task_type(self, prompt: str) -> TaskType:
        """
        Detectar tipo de tarefa baseado no prompt
        """
        prompt_lower = prompt.lower()
        
        # Keywords para cada tipo de tarefa
        logistics_keywords = ['cte', 'ct-e', 'container', 'rastreamento', 'entrega', 'transporte', 'frete']
        financial_keywords = ['custo', 'preço', 'valor', 'faturamento', 'pagamento', 'câmbio', 'moeda']
        customs_keywords = ['aduaneiro', 'ncm', 'di', 'due', 'importação', 'exportação', 'imposto']
        analysis_keywords = ['analisar', 'relatório', 'dashboard', 'métrica', 'estatística', 'comparar']
        
        # Scoring system
        scores = {
            TaskType.LOGISTICS: sum(1 for kw in logistics_keywords if kw in prompt_lower),
            TaskType.FINANCIAL: sum(1 for kw in financial_keywords if kw in prompt_lower),
            TaskType.CUSTOMS: sum(1 for kw in customs_keywords if kw in prompt_lower),
            TaskType.ANALYSIS: sum(1 for kw in analysis_keywords if kw in prompt_lower),
        }
        
        # Retornar tipo com maior score
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return TaskType.GENERAL
    
    def _select_provider(self, task_type: TaskType, preferred_provider: Optional[LLMProvider] = None) -> LLMProvider:
        """
        Selecionar provedor baseado no tipo de tarefa e disponibilidade
        """
        if preferred_provider and preferred_provider in self.configs:
            if self.configs[preferred_provider].enabled:
                if self._check_daily_cost_limit(preferred_provider):
                    return preferred_provider
        
        # Usar estratégia de roteamento
        providers = self.routing_strategy.get(task_type, [LLMProvider.OPENAI, LLMProvider.GEMINI])
        
        for provider in providers:
            if provider in self.configs and self.configs[provider].enabled:
                if self._check_daily_cost_limit(provider):
                    return provider
        
        # Fallback para qualquer provedor disponível
        for provider in [LLMProvider.OPENAI, LLMProvider.GEMINI]:
            if provider in self.configs and self.configs[provider].enabled:
                return provider
        
        raise Exception("❌ Nenhum provedor LLM disponível")
    
    def _check_daily_cost_limit(self, provider: LLMProvider) -> bool:
        """Verificar se o limite diário de custo foi atingido"""
        today = datetime.now().strftime('%Y-%m-%d')
        daily_cost = self.usage_stats["daily_costs"].get(f"{provider.value}_{today}", 0.0)
        max_cost = self.configs[provider].max_daily_cost
        
        return daily_cost < max_cost
    
    async def _call_openai(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Chamar OpenAI API"""
        start_time = datetime.now()
        
        try:
            client = self.clients[LLMProvider.OPENAI]
            response = client.chat.completions.create(
                model=config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            tokens_used = response.usage.total_tokens
            cost_estimate = (tokens_used / 1000) * config.cost_per_1k_tokens
            
            # Update usage stats
            self._update_usage_stats(LLMProvider.OPENAI, cost_estimate, response_time)
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider=LLMProvider.OPENAI,
                model=config.model,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate,
                response_time=response_time,
                timestamp=datetime.now(),
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
            
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            self._update_error_stats(LLMProvider.OPENAI)
            raise
    
    async def _call_gemini(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Chamar Google Gemini API"""
        start_time = datetime.now()
        
        try:
            client = self.clients[LLMProvider.GEMINI]
            response = client.generate_content(
                prompt,
                generation_config={
                    "temperature": config.temperature,
                    "max_output_tokens": config.max_tokens,
                }
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Estimativa de tokens (Gemini não fornece contagem exata)
            tokens_used = len(prompt.split()) + len(response.text.split())
            cost_estimate = (tokens_used / 1000) * config.cost_per_1k_tokens
            
            # Update usage stats
            self._update_usage_stats(LLMProvider.GEMINI, cost_estimate, response_time)
            
            return LLMResponse(
                content=response.text,
                provider=LLMProvider.GEMINI,
                model=config.model,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate,
                response_time=response_time,
                timestamp=datetime.now(),
                metadata={"safety_ratings": str(response.safety_ratings)}
            )
            
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}")
            self._update_error_stats(LLMProvider.GEMINI)
            raise
    
    def _update_usage_stats(self, provider: LLMProvider, cost: float, response_time: float):
        """Atualizar estatísticas de uso"""
        today = datetime.now().strftime('%Y-%m-%d')
        provider_key = provider.value
        daily_key = f"{provider_key}_{today}"
        
        # Update daily costs
        if daily_key not in self.usage_stats["daily_costs"]:
            self.usage_stats["daily_costs"][daily_key] = 0.0
        self.usage_stats["daily_costs"][daily_key] += cost
        
        # Update request counts
        if provider_key not in self.usage_stats["request_counts"]:
            self.usage_stats["request_counts"][provider_key] = 0
        self.usage_stats["request_counts"][provider_key] += 1
        
        # Update response times
        if provider_key not in self.usage_stats["response_times"]:
            self.usage_stats["response_times"][provider_key] = []
        self.usage_stats["response_times"][provider_key].append(response_time)
    
    def _update_error_stats(self, provider: LLMProvider):
        """Atualizar estatísticas de erro"""
        provider_key = provider.value
        if provider_key not in self.usage_stats["error_counts"]:
            self.usage_stats["error_counts"][provider_key] = 0
        self.usage_stats["error_counts"][provider_key] += 1
    
    async def generate_response(
        self, 
        prompt: str, 
        task_type: Optional[TaskType] = None,
        preferred_provider: Optional[LLMProvider] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Gerar resposta usando roteamento inteligente
        
        Args:
            prompt: Prompt para o LLM
            task_type: Tipo de tarefa (detectado automaticamente se não fornecido)
            preferred_provider: Provedor preferido pelo usuário
            user_context: Contexto do usuário (role, permissions, etc.)
        
        Returns:
            LLMResponse com conteúdo, métricas e metadados
        """
        
        # Detectar tipo de tarefa se não fornecido
        if task_type is None:
            task_type = self._detect_task_type(prompt)
        
        logger.info(f"🧠 Task type detected: {task_type.value}")
        
        # Selecionar provedor
        try:
            provider = self._select_provider(task_type, preferred_provider)
            config = self.configs[provider]
            
            logger.info(f"🎯 Using provider: {provider.value} (model: {config.model})")
            
            # Adicionar contexto do usuário ao prompt se disponível
            if user_context:
                context_info = f"\nContexto do usuário: {json.dumps(user_context, indent=2)}\n"
                prompt = context_info + prompt
            
            # Chamar o provedor selecionado
            if provider == LLMProvider.OPENAI:
                response = await self._call_openai(prompt, config)
            elif provider == LLMProvider.GEMINI:
                response = await self._call_gemini(prompt, config)
            else:
                raise Exception(f"❌ Provedor não suportado: {provider}")
            
            logger.info(f"✅ Response generated: {response.tokens_used} tokens, ${response.cost_estimate:.4f}, {response.response_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to generate response: {e}")
            
            # Tentar fallback para outro provedor
            if preferred_provider:
                logger.info("🔄 Trying fallback provider...")
                return await self.generate_response(prompt, task_type, None, user_context)
            
            raise Exception(f"❌ Todos os provedores falharam: {e}")
    
    def get_available_providers(self) -> List[LLMProvider]:
        """Retornar lista de provedores disponíveis"""
        return [
            provider for provider, config in self.configs.items() 
            if config.enabled and self._check_daily_cost_limit(provider)
        ]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retornar estatísticas de uso"""
        return {
            "providers_available": [p.value for p in self.get_available_providers()],
            "daily_costs": self.usage_stats["daily_costs"],
            "request_counts": self.usage_stats["request_counts"],
            "error_counts": self.usage_stats["error_counts"],
            "avg_response_times": {
                provider: sum(times) / len(times) if times else 0
                for provider, times in self.usage_stats["response_times"].items()
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check de todos os provedores"""
        health_status = {}
        
        for provider, config in self.configs.items():
            try:
                if not config.enabled:
                    health_status[provider.value] = {
                        "status": "disabled",
                        "message": "Provider disabled in configuration"
                    }
                    continue
                
                if not self._check_daily_cost_limit(provider):
                    health_status[provider.value] = {
                        "status": "cost_limit_exceeded",
                        "message": f"Daily cost limit of ${config.max_daily_cost} exceeded"
                    }
                    continue
                
                # Test connectivity (simplified)
                health_status[provider.value] = {
                    "status": "healthy",
                    "model": config.model,
                    "daily_cost_remaining": config.max_daily_cost - self.usage_stats["daily_costs"].get(
                        f"{provider.value}_{datetime.now().strftime('%Y-%m-%d')}", 0.0
                    )
                }
                
            except Exception as e:
                health_status[provider.value] = {
                    "status": "error",
                    "message": str(e)
                }
        
        return health_status

# Singleton instance
llm_router = LLMRouter()

# Convenience functions
async def generate_llm_response(
    prompt: str,
    task_type: Optional[TaskType] = None,
    preferred_provider: Optional[LLMProvider] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> LLMResponse:
    """Função de conveniência para gerar respostas"""
    return await llm_router.generate_response(prompt, task_type, preferred_provider, user_context)

def get_llm_health() -> Dict[str, Any]:
    """Função de conveniência para health check"""
    return llm_router.health_check()

def get_llm_stats() -> Dict[str, Any]:
    """Função de conveniência para estatísticas"""
    return llm_router.get_usage_stats()