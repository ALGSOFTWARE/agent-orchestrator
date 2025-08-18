"""
GraphQL Schemas para entidades logísticas
Usando Strawberry GraphQL para type safety
"""

from datetime import datetime
from typing import List, Optional
from strawberry import type, field
import strawberry


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
class CTe:
    """CT-e (Conhecimento de Transporte Eletrônico)"""
    id: str
    numero_cte: str
    status: str
    data_emissao: datetime
    transportadora: Transportadora
    origem: Endereco
    destino: Endereco
    valor_frete: float
    peso_bruto: float
    containers: List[str]
    previsao_entrega: Optional[datetime] = None
    observacoes: Optional[str] = None


@strawberry.type
class PosicaoGPS:
    """Posição GPS do container"""
    latitude: float
    longitude: float
    timestamp: datetime
    velocidade: Optional[float] = None
    endereco: Optional[str] = None


@strawberry.type
class Container:
    """Container de transporte"""
    id: str
    numero: str
    tipo: str
    status: str
    posicao_atual: Optional[PosicaoGPS] = None
    temperatura_atual: Optional[float] = None
    historico_posicoes: List[PosicaoGPS]
    cte_associado: Optional[str] = None
    peso_bruto: Optional[float] = None
    observacoes: Optional[str] = None


@strawberry.type
class BL:
    """Bill of Lading (Conhecimento de Embarque)"""
    id: str
    numero_bl: str
    status: str
    data_embarque: datetime
    porto_origem: str
    porto_destino: str
    navio: str
    containers: List[str]
    peso_total: float
    valor_mercadorias: float
    eta_destino: Optional[datetime] = None
    observacoes: Optional[str] = None


@strawberry.type
class Embarcador:
    """Empresa embarcadora"""
    id: str
    nome: str
    cnpj: str
    endereco: Endereco
    contato: Optional[str] = None
    email: Optional[str] = None


@strawberry.type
class Viagem:
    """Viagem multi-modal"""
    id: str
    codigo_viagem: str
    status: str
    tipo_modal: str
    origem: Endereco
    destino: Endereco
    data_inicio: datetime
    data_fim_prevista: datetime
    containers: List[str]
    custo_total: float
    observacoes: Optional[str] = None


@strawberry.type
class LogisticsStats:
    """Estatísticas do sistema logístico"""
    total_ctes: int
    total_containers: int
    total_bls: int
    containers_em_transito: int
    ctes_entregues: int
    valor_total_fretes: float


# Input Types para Mutations
@strawberry.input
class EnderecoInput:
    municipio: str
    uf: str
    cep: Optional[str] = None
    endereco_completo: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@strawberry.input
class TransportadoraInput:
    nome: str
    cnpj: str
    telefone: Optional[str] = None
    email: Optional[str] = None


@strawberry.input
class CTeInput:
    numero_cte: str
    status: str
    transportadora: TransportadoraInput
    origem: EnderecoInput
    destino: EnderecoInput
    valor_frete: float
    peso_bruto: float
    containers: List[str]
    previsao_entrega: Optional[datetime] = None
    observacoes: Optional[str] = None


@strawberry.input
class ContainerInput:
    numero: str
    tipo: str
    status: str
    cte_associado: Optional[str] = None
    peso_bruto: Optional[float] = None
    observacoes: Optional[str] = None


@strawberry.input
class BLInput:
    numero_bl: str
    status: str
    data_embarque: datetime
    porto_origem: str
    porto_destino: str
    navio: str
    containers: List[str]
    peso_total: float
    valor_mercadorias: float
    eta_destino: Optional[datetime] = None
    observacoes: Optional[str] = None


@strawberry.input
class PosicaoGPSInput:
    latitude: float
    longitude: float
    velocidade: Optional[float] = None
    endereco: Optional[str] = None


# === Chat Schemas ===

@strawberry.type
class ChatMessage:
    """Mensagem do chat com agente"""
    id: str
    content: str
    role: str  # 'user' ou 'agent'
    timestamp: datetime
    agent_type: Optional[str] = None
    session_id: Optional[str] = None
    provider: Optional[str] = None  # 'openai', 'gemini'
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    confidence: Optional[float] = None


@strawberry.type
class ChatResponse:
    """Resposta do agente com metadados"""
    message: ChatMessage
    success: bool
    error: Optional[str] = None
    agent_stats: Optional[str] = None


@strawberry.input
class ChatInput:
    """Input para enviar mensagem ao agente"""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    preferred_provider: Optional[str] = None


# === DATABASE COLLECTION SCHEMAS === #

@strawberry.type
class User:
    """Usuário do sistema"""
    id: str
    name: str
    email: str
    role: str
    client: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    login_count: int


@strawberry.type
class Client:
    """Cliente/Empresa"""
    id: str
    name: str
    cnpj: Optional[str] = None
    address: Optional[str] = None
    contacts: List[str]
    created_at: datetime


@strawberry.type
class ContainerDB:
    """Container do banco de dados"""
    id: str
    container_number: str
    type: Optional[str] = None
    current_status: str
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime


@strawberry.type
class ShipmentDB:
    """Embarque/Shipment"""
    id: str
    client_id: str
    container_ids: List[str]
    status: str
    departure_port: Optional[str] = None
    arrival_port: Optional[str] = None
    etd: Optional[datetime] = None
    eta: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    created_at: datetime


@strawberry.type
class TrackingEventDB:
    """Evento de rastreamento"""
    id: str
    container_id: Optional[str] = None
    shipment_id: Optional[str] = None
    type: str
    description: Optional[str] = None
    timestamp: datetime
    location: Optional[str] = None
    source: str


@strawberry.type
class ContextDB:
    """Contexto de conversas"""
    id: str
    user_id: str
    session_id: Optional[str] = None
    input: str
    output: str
    agents_involved: List[str]
    timestamp: datetime
    metadata: Optional[str] = None
    response_time: Optional[float] = None


@strawberry.type
class DatabaseStatsQL:
    """Estatísticas do banco de dados"""
    users: int
    clients: int
    containers: int
    shipments: int
    tracking_events: int
    contexts: int
    active_users: int
    timestamp: str


# === INPUT TYPES FOR MUTATIONS === #

@strawberry.input
class UserInput:
    """Input para criar/atualizar usuário"""
    name: str
    email: str
    role: str
    client_id: Optional[str] = None


@strawberry.input
class ClientInput:
    """Input para criar/atualizar cliente"""
    name: str
    cnpj: Optional[str] = None
    address: Optional[str] = None
    contacts: Optional[List[str]] = None


@strawberry.input
class ContainerDBInput:
    """Input para criar/atualizar container"""
    container_number: str
    type: Optional[str] = None
    current_status: str
    location: Optional[str] = None


@strawberry.input
class ShipmentDBInput:
    """Input para criar/atualizar shipment"""
    client_id: str
    container_ids: Optional[List[str]] = None
    status: Optional[str] = None
    departure_port: Optional[str] = None
    arrival_port: Optional[str] = None
    etd: Optional[datetime] = None
    eta: Optional[datetime] = None


@strawberry.input
class TrackingEventDBInput:
    """Input para criar/atualizar tracking event"""
    container_id: Optional[str] = None
    shipment_id: Optional[str] = None
    type: str
    description: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None


@strawberry.input
class ContextDBInput:
    """Input para criar/atualizar context"""
    user_id: str
    session_id: Optional[str] = None
    input: str
    output: str
    agents_involved: Optional[List[str]] = None
    metadata: Optional[str] = None
    response_time: Optional[float] = None