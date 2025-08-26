from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Link
from uuid import UUID, uuid4
from enum import Enum

# Agent-related models
class AgentState(str, Enum):
    """Estados do agente"""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class QueryType(str, Enum):
    """Tipos de consulta"""
    CTE_LOOKUP = "cte_lookup"
    CONTAINER_TRACKING = "container_tracking"
    BL_LOOKUP = "bl_lookup"
    GENERAL_LOGISTICS = "general_logistics"
    STATUS_UPDATE = "status_update"

class AgentStats(BaseModel):
    """Estatísticas do agente"""
    total_queries: int = 0
    successful_queries: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    session_duration: float = 0.0

class LogisticsQuery(BaseModel):
    """Consulta logística estruturada"""
    content: str
    query_type: QueryType = QueryType.GENERAL_LOGISTICS
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class AgentResponse(BaseModel):
    """Resposta estruturada do agente"""
    content: str
    confidence: float
    response_time: float
    sources: List[str]
    query_type: QueryType
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ConversationHistory(BaseModel):
    """Histórico da conversa"""
    messages: List[Dict[str, str]]
    session_id: str
    start_time: datetime
    last_activity: datetime

class DocumentFile(BaseModel):
    """Modelo para qualquer arquivo enviado via upload."""
    file_name: str
    s3_url: str
    file_type: str
    size: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    # Campos para OCR e busca semântica futura
    text_content: Optional[str] = None
    embedding: Optional[List[float]] = None
    indexed_at: Optional[datetime] = None

class Order(Document):
    """Nó central que representa uma Ordem de Serviço ou Operação Logística."""
    order_id: str = Field(default_factory=lambda: str(uuid4()), unique=True)
    customer_name: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Documentos estruturados associados a esta Ordem
    ctes: List[Link["CTEDocument"]] = []
    bls: List[Link["BLDocument"]] = []
    containers: List[Link["Container"]] = []
    
    # Outros arquivos (fotos, vídeos, PDFs não estruturados, etc.)
    other_documents: List[DocumentFile] = []

    class Settings:
        name = "orders"

class CTEDocument(Document):
    """Conhecimento de Transporte Eletrônico."""
    cte_number: str = Field(..., unique=True)
    issuer_name: str
    recipient_name: str
    origin_city: str
    destination_city: str
    status: str = "Em trânsito"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    order: Optional[Link[Order]] = None  # Link para a Ordem

    class Settings:
        name = "cte_documents"

class BLDocument(Document):
    """Bill of Lading."""
    bl_number: str = Field(..., unique=True)
    shipping_line: str
    vessel_name: str
    port_of_loading: str
    port_of_discharge: str
    status: str = "Aguardando embarque"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    order: Optional[Link[Order]] = None  # Link para a Ordem

    class Settings:
        name = "bl_documents"

class Container(Document):
    """Container."""
    container_number: str = Field(..., unique=True)
    container_type: str
    current_position: Optional[Dict[str, Any]] = None
    status: str = "Vazio"
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    order: Optional[Link[Order]] = None # Link para a Ordem
    
    class Settings:
        name = "containers"

class Transportadora(Document):
    name: str = Field(..., unique=True)
    cnpj: str = Field(..., unique=True)
    
    class Settings:
        name = "transportadoras"

class Embarcador(Document):
    name: str = Field(..., unique=True)
    cnpj: str = Field(..., unique=True)

    class Settings:
        name = "embarcadores"
