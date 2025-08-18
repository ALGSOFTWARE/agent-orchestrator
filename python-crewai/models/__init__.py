"""
Database Models - Sistema de Logística Inteligente

Este módulo define os modelos de dados para o sistema:
- Legacy models para compatibilidade
- Database models para persistência
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from beanie import Document, Link


# Legacy models (mantidos para compatibilidade)
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


# Database Models using Beanie (MongoDB ODM)
class Client(Document):
    """Modelo para clientes/empresas"""
    name: str
    cnpj: Optional[str] = None
    address: Optional[str] = None
    contacts: List[dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "clients"


class User(Document):
    """Modelo para usuários do sistema"""
    name: str
    email: EmailStr
    role: str  # "admin" | "logistics" | "finance" | "operator"
    client: Optional[Link[Client]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Settings:
        name = "users"


class Container(Document):
    """Modelo para containers de transporte"""
    container_number: str = Field(..., unique=True)
    type: Optional[str] = None
    current_status: str
    location: Optional[dict] = None  # {lat, lng, portCode}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "containers"


class Shipment(Document):
    """Modelo para embarques/fretes"""
    client: Link[Client]
    containers: List[Link[Container]] = Field(default_factory=list)
    status: str = "in_transit"  # "in_transit" | "delivered" | "delayed"
    departure_port: Optional[str] = None
    arrival_port: Optional[str] = None
    etd: Optional[datetime] = None
    eta: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "shipments"


class TrackingEvent(Document):
    """Modelo para eventos de rastreamento"""
    container: Optional[Link[Container]] = None
    shipment: Optional[Link[Shipment]] = None
    type: str  # "loaded" | "departed" | "arrived" | "delayed" | "incident"
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[dict] = None  # {lat, lng, portCode}
    source: str = "system"  # "system" | "manual" | "external_api"

    class Settings:
        name = "tracking_events"


class Context(Document):
    """Modelo para histórico de contexto/interações dos usuários"""
    user_id: str
    session_id: Optional[str] = None
    input: str
    output: str
    agents_involved: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default_factory=dict)

    class Settings:
        name = "contexts"


# Export all models
__all__ = [
    # Legacy models
    "AgentState",
    "QueryType", 
    "AgentStats",
    "OllamaConfig",
    "LogisticsQuery",
    "AgentResponse",
    "ConversationHistory",
    # Database models
    "User",
    "Client",
    "Container", 
    "Shipment",
    "TrackingEvent",
    "Context"
]