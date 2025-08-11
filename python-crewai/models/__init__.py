"""
Types and data structures for MIT Tracking Orchestrator
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class AgentState(Enum):
    """Estados possíveis do agente"""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class QueryType(Enum):
    """Tipos de consulta logística"""
    CTE = "cte"
    CONTAINER = "container"
    BL = "bl"
    ETA_ETD = "eta_etd"
    DELIVERY_STATUS = "delivery_status"
    GENERAL = "general"


@dataclass
class AgentStats:
    """Estatísticas do agente"""
    total_queries: int = 0
    successful_queries: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    session_duration: float = 0.0


class OllamaConfig(BaseModel):
    """Configuração do Ollama"""
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2:3b"
    temperature: float = 0.3


class LogisticsQuery(BaseModel):
    """Query de logística"""
    content: str
    query_type: Optional[QueryType] = None
    session_id: Optional[str] = None
    timestamp: datetime = datetime.now()


class AgentResponse(BaseModel):
    """Resposta do agente"""
    content: str
    confidence: float
    response_time: float
    sources: List[str]
    query_type: Optional[QueryType] = None
    agent_id: Optional[str] = None


@dataclass
class ConversationHistory:
    """Histórico da conversa"""
    messages: List[Dict[str, Any]]
    session_id: str
    start_time: datetime
    last_activity: datetime