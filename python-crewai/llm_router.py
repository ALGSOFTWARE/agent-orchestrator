"""
LLM Router - Intelligent routing between OpenAI and Gemini
Smart provider selection based on task type and availability
"""

import os
import asyncio
import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum

# OpenAI
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger("LLMRouter")


class LLMProvider(str, Enum):
    """Available LLM providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    AUTO = "auto"


class TaskType(str, Enum):
    """Task types for intelligent routing"""
    GENERAL = "general"
    LOGISTICS = "logistics"
    FINANCIAL = "financial"
    CUSTOMS = "customs"
    ANALYSIS = "analysis"


@dataclass
class LLMResponse:
    """Response from LLM with metadata"""
    content: str
    provider: LLMProvider
    tokens_used: int
    response_time: float
    model_used: str


class LLMRouter:
    """Smart LLM routing between OpenAI and Gemini"""
    
    def __init__(self):
        self.stats = {
            "request_counts": {},
            "error_counts": {},
            "total_tokens": {},
            "avg_response_time": {}
        }
        
        # Initialize providers
        self.openai_client = None
        self.gemini_model = None
        
        self._init_openai()
        self._init_gemini()
        
        logger.info(f"🧠 LLM Router initialized - OpenAI: {OPENAI_AVAILABLE}, Gemini: {GEMINI_AVAILABLE}")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = AsyncOpenAI(
                    api_key=os.getenv("OPENAI_API_KEY")
                )
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI initialization failed: {e}")
                self.openai_client = None
    
    def _init_gemini(self):
        """Initialize Gemini client"""
        if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
            try:
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Gemini client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Gemini initialization failed: {e}")
                self.gemini_model = None
    
    def _select_provider(self, task_type: TaskType, preferred_provider: Optional[LLMProvider] = None) -> LLMProvider:
        """Select best provider for task type"""
        
        # Use preferred if specified and available
        if preferred_provider == LLMProvider.OPENAI and self.openai_client:
            return LLMProvider.OPENAI
        elif preferred_provider == LLMProvider.GEMINI and self.gemini_model:
            return LLMProvider.GEMINI
        
        # Smart routing based on task type
        if task_type in [TaskType.LOGISTICS, TaskType.FINANCIAL]:
            # OpenAI tends to be better for structured data
            if self.openai_client:
                return LLMProvider.OPENAI
        elif task_type == TaskType.ANALYSIS:
            # Gemini is good for analysis
            if self.gemini_model:
                return LLMProvider.GEMINI
        
        # Fallback to any available provider
        if self.openai_client:
            return LLMProvider.OPENAI
        elif self.gemini_model:
            return LLMProvider.GEMINI
        
        raise Exception("No LLM providers available")
    
    async def generate_response(
        self,
        prompt: str,
        task_type: TaskType = TaskType.GENERAL,
        preferred_provider: Optional[LLMProvider] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        user_context: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """Generate response using optimal provider"""
        
        start_time = time.time()
        provider = self._select_provider(task_type, preferred_provider)
        
        try:
            if provider == LLMProvider.OPENAI:
                return await self._generate_openai(prompt, temperature, max_tokens, start_time)
            elif provider == LLMProvider.GEMINI:
                return await self._generate_gemini(prompt, temperature, max_tokens, start_time)
            else:
                raise Exception(f"Unsupported provider: {provider}")
                
        except Exception as e:
            # Try fallback provider
            fallback_provider = LLMProvider.GEMINI if provider == LLMProvider.OPENAI else LLMProvider.OPENAI
            
            logger.warning(f"⚠️ Provider {provider} failed, trying {fallback_provider}: {e}")
            
            try:
                if fallback_provider == LLMProvider.OPENAI and self.openai_client:
                    return await self._generate_openai(prompt, temperature, max_tokens, start_time)
                elif fallback_provider == LLMProvider.GEMINI and self.gemini_model:
                    return await self._generate_gemini(prompt, temperature, max_tokens, start_time)
            except Exception as fallback_error:
                logger.error(f"❌ Fallback provider also failed: {fallback_error}")
            
            raise Exception(f"All LLM providers failed. Primary: {e}")
    
    async def _generate_openai(self, prompt: str, temperature: float, max_tokens: int, start_time: float) -> LLMResponse:
        """Generate response using OpenAI"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        response_time = time.time() - start_time
        
        # Update stats
        self._update_stats(LLMProvider.OPENAI, tokens_used, response_time, success=True)
        
        return LLMResponse(
            content=content,
            provider=LLMProvider.OPENAI,
            tokens_used=tokens_used,
            response_time=response_time,
            model_used="gpt-3.5-turbo"
        )
    
    async def _generate_gemini(self, prompt: str, temperature: float, max_tokens: int, start_time: float) -> LLMResponse:
        """Generate response using Gemini"""
        
        # Configure generation
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        # Generate response (Gemini is not async by default, so we run in executor)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: self.gemini_model.generate_content(prompt, generation_config=generation_config)
        )
        
        content = response.text
        tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
        response_time = time.time() - start_time
        
        # Update stats
        self._update_stats(LLMProvider.GEMINI, tokens_used, response_time, success=True)
        
        return LLMResponse(
            content=content,
            provider=LLMProvider.GEMINI,
            tokens_used=tokens_used,
            response_time=response_time,
            model_used="gemini-pro"
        )
    
    def _update_stats(self, provider: LLMProvider, tokens: int, response_time: float, success: bool):
        """Update usage statistics"""
        provider_str = provider.value
        
        if provider_str not in self.stats["request_counts"]:
            self.stats["request_counts"][provider_str] = 0
            self.stats["error_counts"][provider_str] = 0
            self.stats["total_tokens"][provider_str] = 0
            self.stats["avg_response_time"][provider_str] = 0.0
        
        if success:
            self.stats["request_counts"][provider_str] += 1
            self.stats["total_tokens"][provider_str] += tokens
            
            # Update average response time
            count = self.stats["request_counts"][provider_str]
            current_avg = self.stats["avg_response_time"][provider_str]
            self.stats["avg_response_time"][provider_str] = (current_avg * (count - 1) + response_time) / count
        else:
            self.stats["error_counts"][provider_str] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.stats.copy()
    
    def get_health(self) -> Dict[str, Any]:
        """Get health status of all providers"""
        return {
            "openai": {
                "available": self.openai_client is not None,
                "configured": bool(os.getenv("OPENAI_API_KEY"))
            },
            "gemini": {
                "available": self.gemini_model is not None,
                "configured": bool(os.getenv("GOOGLE_API_KEY"))
            }
        }


# Global router instance
_router = None

def get_router() -> LLMRouter:
    """Get global router instance"""
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router


# Convenience functions
async def generate_llm_response(
    prompt: str,
    task_type: TaskType = TaskType.GENERAL,
    preferred_provider: Optional[LLMProvider] = None,
    temperature: float = 0.3,
    max_tokens: int = 2000,
    user_context: Optional[Dict[str, Any]] = None
) -> LLMResponse:
    """Generate LLM response using global router"""
    router = get_router()
    return await router.generate_response(
        prompt=prompt,
        task_type=task_type,
        preferred_provider=preferred_provider,
        temperature=temperature,
        max_tokens=max_tokens,
        user_context=user_context
    )


def get_llm_stats() -> Dict[str, Any]:
    """Get global LLM statistics"""
    router = get_router()
    return router.get_stats()


def get_llm_health() -> Dict[str, Any]:
    """Get global LLM health status"""
    router = get_router()
    return router.get_health()


# Legacy compatibility
llm_router = get_router