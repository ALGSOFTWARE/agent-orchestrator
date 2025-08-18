"""
Database Models - Gatekeeper API

Modelos Pydantic e Beanie para o microserviço de autenticação.
Inclui modelos para usuários, clientes, contexto e validação de dados.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from beanie import Document, Link
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

# Enums para validação
class UserRole(str, Enum):
    """Roles válidos no sistema"""
    ADMIN = "admin"
    LOGISTICS = "logistics"
    FINANCE = "finance"
    OPERATOR = "operator"


class AgentStatus(str, Enum):
    """Status de resposta dos agentes"""
    SUCCESS = "success"
    ERROR = "error"
    FORBIDDEN = "forbidden"


class AuthStatus(str, Enum):
    """Status de autenticação"""
    AUTHENTICATED = "authenticated"
    INVALID_TOKEN = "invalid_token"
    EXPIRED_TOKEN = "expired_token"
    UNAUTHORIZED = "unauthorized"


# Modelos de Request/Response
class AuthPayload(BaseModel):
    """Payload recebido da API de autenticação externa"""
    userId: str = Field(..., min_length=1, description="ID único do usuário")
    role: UserRole = Field(..., description="Role/papel do usuário no sistema")
    permissions: Optional[List[str]] = Field(
        default=[],
        description="Lista de permissões específicas do usuário"
    )
    sessionId: Optional[str] = Field(None, description="ID da sessão")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

    @validator('userId')
    def validate_user_id(cls, v):
        if not v or v.isspace():
            raise ValueError('userId não pode ser vazio')
        return v.strip()


class UserRequest(BaseModel):
    """Requisição para criar/atualizar usuário"""
    name: str = Field(..., min_length=1)
    email: EmailStr
    role: UserRole
    client_id: Optional[str] = None


class ContextRequest(BaseModel):
    """Requisição para adicionar contexto"""
    input: str = Field(..., min_length=1)
    output: str = Field(..., min_length=1) 
    agents_involved: List[str] = Field(default=[])
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default={})


class GatekeeperResponse(BaseModel):
    """Resposta padrão do Gatekeeper"""
    status: AgentStatus
    agent: Optional[str] = None
    message: str
    userId: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Resposta de erro padronizada"""
    status: str = "error"
    code: int
    message: str
    details: Optional[str] = None
    service: str = "gatekeeper-api"
    timestamp: datetime = Field(default_factory=datetime.now)


# Database Models usando Beanie (MongoDB ODM)

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

class Client(Document):
    """Modelo para clientes/empresas"""
    name: str
    cnpj: Optional[str] = None
    address: Optional[str] = None
    contacts: List[dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "clients"
        indexes = ["cnpj"]


class User(Document):
    """Modelo para usuários do sistema"""
    name: str
    email: EmailStr
    role: UserRole
    client: Optional[Link[Client]] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    login_count: int = 0

    class Settings:
        name = "users"
        indexes = ["email", "role"]


class Context(Document):
    """Modelo para histórico de contexto/interações dos usuários"""
    user_id: str
    session_id: Optional[str] = None
    input: str
    output: str
    agents_involved: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default_factory=dict)
    response_time: Optional[float] = None

    class Settings:
        name = "contexts"
        indexes = ["user_id", "session_id", "timestamp"]


class Container(Document):
    """Modelo para containers de transporte"""
    container_number: str = Field(..., unique=True)
    type: Optional[str] = None
    current_status: str
    location: Optional[dict] = None  # {lat, lng, portCode}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    order: Optional[Link[Order]] = None # Link para a Ordem

    class Settings:
        name = "containers"
        indexes = ["container_number", "current_status"]


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
        indexes = ["status", "client", "created_at"]


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
        indexes = ["container", "shipment", "timestamp", "type"]


# Export all models
__all__ = [
    # Enums
    "UserRole",
    "AgentStatus", 
    "AuthStatus",
    # Request/Response models
    "AuthPayload",
    "UserRequest",
    "ContextRequest", 
    "GatekeeperResponse",
    "ErrorResponse",
    # Database models
    "User",
    "Client",
    "Context",
    "Container",
    "Shipment", 
    "TrackingEvent",
    "Order",
    "DocumentFile",
    "CTEDocument",
    "BLDocument"
]