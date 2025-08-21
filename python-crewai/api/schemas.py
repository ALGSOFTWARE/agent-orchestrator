"""
GraphQL Schemas para entidades logísticas
Usando Strawberry GraphQL para type safety
"""

from datetime import datetime
from typing import List, Optional
from strawberry import type, field
import strawberry

# === NOVOS SCHEMAS PARA ORDERS E DOCUMENTOS ===

@strawberry.type
class DocumentFile:
    """Representa um arquivo de documento no GraphQL."""
    file_name: str
    s3_url: str
    file_type: str
    size: int
    uploaded_at: datetime
    text_content: Optional[str] = None
    indexed_at: Optional[datetime] = None

@strawberry.input
class DocumentFileInput:
    """Input para criar um novo DocumentFile."""
    file_name: str
    s3_url: str
    file_type: str
    size: int

@strawberry.type
class Order:
    """Representa uma Ordem de Serviço (Order) no GraphQL."""
    id: str
    order_id: str
    customer_name: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    ctes: List["CTEDocument"] = field(default_factory=list)
    bls: List["BLDocument"] = field(default_factory=list)
    containers: List["Container"] = field(default_factory=list)
    other_documents: List[DocumentFile] = field(default_factory=list)

@strawberry.input
class OrderInput:
    """Input para criar ou atualizar uma Order."""
    customer_name: Optional[str] = None
    description: Optional[str] = None
    cte_ids: Optional[List[str]] = None
    bl_ids: Optional[List[str]] = None
    container_ids: Optional[List[str]] = None

# === SCHEMAS EXISTENTES (MODIFICADOS) ===

@strawberry.type
class CTEDocument:
    """CT-e (Conhecimento de Transporte Eletrônico)"""
    id: str
    cte_number: str
    status: str
    data_emissao: datetime
    transportadora: "Transportadora"
    origem: "Endereco"
    destino: "Endereco"
    valor_frete: float
    order_id: Optional[str] = None

@strawberry.type
class BLDocument:
    """Bill of Lading (Conhecimento de Embarque)"""
    id: str
    bl_number: str
    status: str
    data_embarque: datetime
    porto_origem: str
    porto_destino: str
    navio: str
    order_id: Optional[str] = None

@strawberry.type
class Container:
    """Container de transporte"""
    id: str
    numero: str
    tipo: str
    status: str
    order_id: Optional[str] = None

# === SCHEMAS DE APOIO (sem alterações) ===

@strawberry.type
class Endereco:
    """Endereço para origem/destino"""
    municipio: str
    uf: str
    cep: Optional[str] = None
    endereco_completo: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@strawberry.type
class Transportadora:
    """Dados da transportadora"""
    nome: str
    cnpj: str
    telefone: Optional[str] = None
    email: Optional[str] = None

@strawberry.type
class PosicaoGPS:
    """Posição GPS do container"""
    latitude: float
    longitude: float
    timestamp: datetime
    velocidade: Optional[float] = None
    endereco: Optional[str] = None

@strawberry.type
class LogisticsStats:
    """Estatísticas do sistema logístico"""
    total_orders: int
    total_ctes: int
    total_containers: int
    total_bls: int
    total_documents: int

# === SCHEMAS DE CHAT (sem alterações) ===

@strawberry.type
class ChatMessage:
    """Mensagem do chat com agente"""
    id: str
    content: str
    role: str
    timestamp: datetime
    agent_type: Optional[str] = None
    session_id: Optional[str] = None

@strawberry.type
class ChatResponse:
    """Resposta do agente com metadados"""
    message: ChatMessage
    success: bool
    error: Optional[str] = None

@strawberry.input
class ChatInput:
    """Input para enviar mensagem ao agente"""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
