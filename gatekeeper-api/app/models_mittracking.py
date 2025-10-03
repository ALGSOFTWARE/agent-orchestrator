"""
MitTracking Models - Gatekeeper API Extension

Modelos MongoDB para o sistema MitTracking migrados do MySQL.
Seguindo os padrões estabelecidos no Gatekeeper com Beanie ODM.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from beanie import Document, Link
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


# Enums específicos do MitTracking
class CompanyType(str, Enum):
    """Tipos de empresa no sistema"""
    CLIENT = "cliente"
    TRANSPORTER = "transportadora"


class CompanyStatus(str, Enum):
    """Status das empresas"""
    ACTIVE = "ativo"
    INACTIVE = "inativo"
    SUSPENDED = "suspenso"


class JourneyStatus(str, Enum):
    """Status das jornadas"""
    SCHEDULED = "agendada"
    IN_PROGRESS = "em_andamento"
    COMPLETED = "concluida"
    CANCELLED = "cancelada"


class CheckpointStatus(str, Enum):
    """Status dos checkpoints"""
    PENDING = "pendente"
    IN_PROGRESS = "em_andamento"
    COMPLETED = "concluido"
    DELAYED = "atrasado"


class DeliveryStatus(str, Enum):
    """Status das entregas"""
    WAITING = "aguardando"
    IN_TRANSIT = "em_transito"
    DELIVERED = "entregue"
    DELAYED = "atrasada"
    RETURNED = "devolvida"


class DocumentTypeEnum(str, Enum):
    """Tipos de documentos logísticos"""
    CTE = "cte"
    NFE = "nfe"
    BL = "bl"
    AWB = "awb"
    MANIFESTO = "manifesto"
    OTHER = "outro"


class DocumentStatus(str, Enum):
    """Status dos documentos"""
    PENDING = "pendente"
    APPROVED = "aprovado"
    REJECTED = "rejeitado"
    EXPIRED = "vencido"
    ANALYZING = "em_analise"
    VALIDATED = "validado"


class IncidentType(str, Enum):
    """Tipos de incidentes"""
    DELAY = "atraso"
    DAMAGE = "avaria"
    LOSS = "perda"
    THEFT = "roubo"
    ACCIDENT = "acidente"
    STOPPED_TIME = "tempo_parado"
    SYSTEM_FAILURE = "falha"
    OTHER = "outro"


class IncidentSeverity(str, Enum):
    """Severidade dos incidentes"""
    LOW = "baixa"
    MEDIUM = "media"
    HIGH = "alta"
    CRITICAL = "critica"


class IncidentStatus(str, Enum):
    """Status dos incidentes"""
    OPEN = "aberta"
    IN_PROGRESS = "em_andamento"
    RESOLVED = "resolvida"
    CANCELLED = "cancelada"


class ContextType(str, Enum):
    """Tipos de contexto para IA"""
    SHORT_TERM = "curto_prazo"        # Contexto da sessão atual
    GENERAL = "geral"                 # Contexto histórico do usuário
    GLOBAL = "global"                 # Contexto compartilhado globalmente


class ContextScope(str, Enum):
    """Escopo do contexto"""
    USER = "usuario"                  # Específico do usuário
    COMPANY = "empresa"               # Específico da empresa
    SYSTEM = "sistema"                # Sistema global


class ChatMessageTypeEnum(str, Enum):
    """Tipos de mensagem do chat"""
    TEXT = "texto"
    IMAGE = "imagem"
    DOCUMENT = "documento"
    SYSTEM = "sistema"


class VehicleType(str, Enum):
    """Tipos de veículos"""
    TRUCK = "caminhao"
    VAN = "van"
    TRAILER = "carreta"
    OTHER = "outro"


# ================================
# MODELOS DE CONTEXTO IA
# ================================

class UserContext(Document):
    """Contexto do usuário para IA"""
    user_id: str = Field(..., description="ID do usuário")
    context_type: ContextType = Field(..., description="Tipo de contexto")
    content: Dict[str, Any] = Field(default_factory=dict, description="Conteúdo do contexto")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Data de expiração (para contexto de curto prazo)")
    
    class Settings:
        name = "user_contexts"
        indexes = ["user_id", "context_type", "created_at"]


class GlobalContext(Document):
    """Contexto global compartilhado do sistema"""
    context_key: str = Field(..., description="Chave única do contexto")
    scope: ContextScope = Field(..., description="Escopo do contexto")
    content: Dict[str, Any] = Field(default_factory=dict, description="Conteúdo do contexto")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    # Controle de acesso
    company_id: Optional[str] = Field(None, description="ID da empresa (se escopo empresa)")
    is_active: bool = Field(default=True, description="Se o contexto está ativo")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "global_contexts"
        indexes = ["context_key", "scope", "company_id"]


class ConversationHistory(Document):
    """Histórico de conversas com a IA"""
    user_id: str = Field(..., description="ID do usuário")
    session_id: str = Field(..., description="ID da sessão")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Mensagens da conversa")
    context_summary: Dict[str, Any] = Field(default_factory=dict, description="Resumo do contexto da conversa")
    
    # Metadados
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(None, description="Fim da sessão")
    total_messages: int = Field(default=0, description="Total de mensagens")
    
    class Settings:
        name = "conversation_histories"
        indexes = ["user_id", "session_id", "start_time"]


# ================================
# MODELOS PRINCIPAIS
# ================================

class MitUser(Document):
    """Usuários do sistema MitTracking (extensão do User existente)"""
    # Campos básicos
    name: str = Field(..., description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Email único")
    password_hash: str = Field(..., description="Hash da senha")
    user_type: str = Field(..., description="Tipo: admin|operador|cliente|funcionario")
    is_active: bool = Field(default=True, description="Se o usuário está ativo")
    
    # Contexto IA
    current_session_id: Optional[str] = Field(None, description="ID da sessão atual da IA")
    ai_preferences: Dict[str, Any] = Field(default_factory=dict, description="Preferências da IA do usuário")
    context_retention_days: int = Field(default=30, description="Dias para reter contexto de curto prazo")
    
    # Empresa associada
    company_id: Optional[str] = Field(None, description="ID da empresa do usuário")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Último login")
    last_ai_interaction: Optional[datetime] = Field(None, description="Última interação com IA")
    
    class Settings:
        name = "mit_users"
        indexes = ["email", "user_type", "company_id", "current_session_id"]


class Company(Document):
    """Empresas - Clientes e Transportadoras unificadas"""
    # Identificação
    name: str = Field(..., description="Nome da empresa")
    company_name: str = Field(..., description="Razão social") 
    cnpj: Optional[str] = Field(None, description="CNPJ da empresa")
    company_type: CompanyType = Field(..., description="Tipo da empresa")
    
    # Contato
    email: Optional[str] = Field(None, description="Email principal")
    phone: Optional[str] = Field(None, description="Telefone")
    
    # Endereço
    address: Optional[str] = Field(None, description="Endereço completo")
    city: Optional[str] = Field(None, description="Cidade")
    state: Optional[str] = Field(None, description="Estado (UF)")
    zip_code: Optional[str] = Field(None, description="CEP")
    
    # Métricas (específicas para clientes)
    score: float = Field(default=0.0, description="Score de desempenho")
    nps: int = Field(default=0, description="Net Promoter Score")
    total_shipments: int = Field(default=0, description="Total de embarques")
    chat_engagement: float = Field(default=0.0, description="Engajamento no chat")
    
    # Status e controle
    status: CompanyStatus = Field(default=CompanyStatus.ACTIVE)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = Field(None, description="Última atividade")
    
    class Settings:
        name = "companies"
        indexes = ["cnpj", "company_type", "status", "name"]


class Employee(Document):
    """Funcionários do sistema"""
    user: Link[MitUser] = Field(..., description="Usuário relacionado")
    position: Optional[str] = Field(None, description="Cargo")
    department: Optional[str] = Field(None, description="Departamento")
    employee_number: Optional[str] = Field(None, description="Matrícula")
    phone: Optional[str] = Field(None, description="Telefone")
    address: Optional[str] = Field(None, description="Endereço")
    hire_date: Optional[datetime] = Field(None, description="Data de admissão")
    is_active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "employees"
        indexes = ["employee_number", "department"]


class Driver(Document):
    """Motoristas"""
    name: str = Field(..., description="Nome do motorista")
    cpf: str = Field(..., description="CPF único")
    license_number: str = Field(..., description="Número da CNH")
    license_category: str = Field(..., description="Categoria da CNH")
    license_expiry: Optional[datetime] = Field(None, description="Validade da CNH")
    phone: Optional[str] = Field(None, description="Telefone")
    email: Optional[str] = Field(None, description="Email")
    address: Optional[str] = Field(None, description="Endereço")
    
    # Relacionamentos
    transporter: Optional[Link[Company]] = Field(None, description="Transportadora")
    
    # Status
    is_active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "drivers"
        indexes = ["cpf", "license_number", "transporter"]


class Vehicle(Document):
    """Veículos da frota"""
    license_plate: str = Field(..., description="Placa única")
    model: Optional[str] = Field(None, description="Modelo")
    brand: Optional[str] = Field(None, description="Marca")
    year: Optional[int] = Field(None, description="Ano")
    color: Optional[str] = Field(None, description="Cor")
    vehicle_type: VehicleType = Field(default=VehicleType.TRUCK, description="Tipo do veículo")
    capacity_kg: Optional[float] = Field(None, description="Capacidade em kg")
    
    # Relacionamentos
    transporter: Optional[Link[Company]] = Field(None, description="Transportadora proprietária")
    current_driver: Optional[Link[Driver]] = Field(None, description="Motorista atual")
    
    # Status
    is_active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "vehicles"
        indexes = ["license_plate", "transporter", "vehicle_type"]


class Journey(Document):
    """Jornadas - Super documento com checkpoints embutidos"""
    # Identificação
    code: str = Field(..., description="Código único da jornada")
    
    # Relacionamentos principais
    client: Link[Company] = Field(..., description="Cliente")
    transporter: Optional[Link[Company]] = Field(None, description="Transportadora")
    vehicle: Optional[Link[Vehicle]] = Field(None, description="Veículo")
    driver: Optional[Link[Driver]] = Field(None, description="Motorista")
    
    # Rota
    origin: str = Field(..., description="Origem")
    destination: str = Field(..., description="Destino")
    origin_coordinates: List[float] = Field(default=[], description="[longitude, latitude]")
    destination_coordinates: List[float] = Field(default=[], description="[longitude, latitude]")
    distance_km: Optional[float] = Field(None, description="Distância em km")
    estimated_time_hours: Optional[float] = Field(None, description="Tempo estimado em horas")
    
    # Checkpoints embutidos
    checkpoints: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de checkpoints")
    
    # Status e progresso
    status: JourneyStatus = Field(default=JourneyStatus.SCHEDULED)
    progress_percentage: float = Field(default=0.0, description="Progresso em %")
    
    # Datas importantes
    start_date: Optional[datetime] = Field(None, description="Data de início")
    end_date: Optional[datetime] = Field(None, description="Data de fim")
    estimated_date: Optional[datetime] = Field(None, description="Data estimada")
    
    # Observações
    observations: Optional[str] = Field(None, description="Observações gerais")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "journeys"
        indexes = ["code", "client", "transporter", "status", "created_at"]
    
    def add_checkpoint(self, name: str, description: str, order: int, 
                      coordinates: List[float] = None, estimated_date: datetime = None):
        """Adiciona checkpoint à jornada"""
        checkpoint = {
            "name": name,
            "description": description,
            "order": order,
            "coordinates": coordinates or [],
            "status": CheckpointStatus.PENDING.value,
            "estimated_date": estimated_date,
            "completed_date": None,
            "observations": None
        }
        self.checkpoints.append(checkpoint)
        self.checkpoints.sort(key=lambda x: x["order"])
        self.updated_at = datetime.utcnow()
    
    def update_checkpoint_status(self, checkpoint_index: int, status: CheckpointStatus, 
                               completed_date: datetime = None, observations: str = None):
        """Atualiza status de um checkpoint"""
        if 0 <= checkpoint_index < len(self.checkpoints):
            self.checkpoints[checkpoint_index]["status"] = status.value
            if completed_date:
                self.checkpoints[checkpoint_index]["completed_date"] = completed_date
            if observations:
                self.checkpoints[checkpoint_index]["observations"] = observations
            self.updated_at = datetime.utcnow()
            self._update_progress()
    
    def _update_progress(self):
        """Atualiza progresso baseado nos checkpoints"""
        if not self.checkpoints:
            self.progress_percentage = 0.0
            return
        
        completed = sum(1 for cp in self.checkpoints if cp["status"] == CheckpointStatus.COMPLETED.value)
        self.progress_percentage = round((completed / len(self.checkpoints)) * 100, 2)
        
        # Atualizar status da jornada baseado no progresso
        if self.progress_percentage == 100:
            self.status = JourneyStatus.COMPLETED
        elif self.progress_percentage > 0:
            self.status = JourneyStatus.IN_PROGRESS


class Delivery(Document):
    """Entregas individuais"""
    # Identificação
    code: str = Field(..., description="Código único da entrega")
    
    # Relacionamentos
    journey: Optional[Link[Journey]] = Field(None, description="Jornada relacionada")
    client: Link[Company] = Field(..., description="Cliente")
    
    # Destinatário e endereço
    recipient_name: Optional[str] = Field(None, description="Nome do destinatário")
    delivery_address: str = Field(..., description="Endereço de entrega")
    delivery_coordinates: List[float] = Field(default=[], description="[longitude, latitude]")
    city: Optional[str] = Field(None, description="Cidade")
    state: Optional[str] = Field(None, description="Estado")
    zip_code: Optional[str] = Field(None, description="CEP")
    
    # Informações da carga
    cargo_value: Optional[float] = Field(None, description="Valor da carga")
    weight_kg: Optional[float] = Field(None, description="Peso em kg")
    volume_count: int = Field(default=1, description="Número de volumes")
    
    # Status e datas
    status: DeliveryStatus = Field(default=DeliveryStatus.WAITING)
    estimated_date: Optional[datetime] = Field(None, description="Data estimada")
    estimated_time: Optional[str] = Field(None, description="Horário estimado")
    actual_delivery_date: Optional[datetime] = Field(None, description="Data real de entrega")
    
    # Comprovação de entrega
    digital_signature: Optional[str] = Field(None, description="Assinatura digital")
    delivery_photo: Optional[str] = Field(None, description="Foto da entrega")
    
    # Observações
    observations: Optional[str] = Field(None, description="Observações")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "deliveries"
        indexes = ["code", "journey", "client", "status", "estimated_date", "actual_delivery_date"]


class LogisticsDocument(Document):
    """Documentos logísticos (CT-e, NF-e, BL, AWB, etc.)"""
    # Identificação
    code: str = Field(..., description="Código interno do documento")
    document_number: str = Field(..., description="Número oficial do documento")
    document_type: DocumentTypeEnum = Field(..., description="Tipo do documento")
    
    # Relacionamentos
    journey: Optional[Link[Journey]] = Field(None, description="Jornada relacionada")
    delivery: Optional[Link[Delivery]] = Field(None, description="Entrega relacionada")
    client: Optional[Link[Company]] = Field(None, description="Cliente relacionado")
    
    # Localização
    origin: Optional[str] = Field(None, description="Origem")
    destination: Optional[str] = Field(None, description="Destino")
    
    # Informações do arquivo
    file_path: Optional[str] = Field(None, description="Caminho do arquivo")
    file_size: Optional[int] = Field(None, description="Tamanho em bytes")
    file_version: int = Field(default=1, description="Versão do arquivo")
    
    # Datas
    issue_date: Optional[datetime] = Field(None, description="Data de emissão")
    upload_date: Optional[datetime] = Field(None, description="Data do upload")
    expiry_date: Optional[datetime] = Field(None, description="Data de vencimento")
    
    # Controle
    status: DocumentStatus = Field(default=DocumentStatus.PENDING)
    uploaded_by: Optional[str] = Field(None, description="Quem fez o upload")
    upload_source: str = Field(default="manual", description="Origem: chat|manual|api")
    
    # Métricas
    view_count: int = Field(default=0, description="Número de visualizações")
    last_viewed: Optional[datetime] = Field(None, description="Última visualização")
    
    # Valor (se aplicável)
    document_value: Optional[float] = Field(None, description="Valor do documento")
    
    # Observações
    observations: Optional[str] = Field(None, description="Observações")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "logistics_documents"
        indexes = ["document_number", "document_type", "journey", "client", "status"]
    
    def increment_view(self):
        """Incrementa contador de visualização"""
        self.view_count += 1
        self.last_viewed = datetime.utcnow()


class Incident(Document):
    """Ocorrências e incidentes"""
    # Identificação
    incident_type: IncidentType = Field(..., description="Tipo do incidente")
    title: str = Field(..., description="Título do incidente")
    description: str = Field(..., description="Descrição detalhada")
    
    # Relacionamentos
    journey: Optional[Link[Journey]] = Field(None, description="Jornada relacionada")
    delivery: Optional[Link[Delivery]] = Field(None, description="Entrega relacionada")
    client: Optional[Link[Company]] = Field(None, description="Cliente relacionado")
    
    # Severidade e status
    severity: IncidentSeverity = Field(default=IncidentSeverity.MEDIUM)
    status: IncidentStatus = Field(default=IncidentStatus.OPEN)
    
    # Datas
    occurrence_date: datetime = Field(..., description="Data da ocorrência")
    resolution_date: Optional[datetime] = Field(None, description="Data de resolução")
    
    # Responsável
    responsible_person: Optional[str] = Field(None, description="Responsável pela resolução")
    actions_taken: Optional[str] = Field(None, description="Ações tomadas")
    
    # Observações
    observations: Optional[str] = Field(None, description="Observações adicionais")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "incidents"
        indexes = ["incident_type", "journey", "delivery", "client", "severity", "status", "occurrence_date"]


class ChatConversation(Document):
    """Conversas de chat por cliente"""
    # Identificação
    client: Link[Company] = Field(..., description="Cliente da conversa")
    
    # Relacionamentos opcionais
    journey: Optional[Link[Journey]] = Field(None, description="Jornada relacionada")
    delivery: Optional[Link[Delivery]] = Field(None, description="Entrega relacionada")
    
    # Mensagens embutidas
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de mensagens")
    
    # Status da conversa
    is_active: bool = Field(default=True, description="Conversa ativa")
    is_archived: bool = Field(default=False, description="Conversa arquivada")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = Field(None, description="Última mensagem")
    
    class Settings:
        name = "chat_conversations"
        indexes = ["client", "journey", "delivery", "is_active", "last_message_at"]
    
    def add_message(self, message_type: ChatMessageTypeEnum, content: str, 
                   sender_id: str = None, sender_name: str = None, 
                   file_path: str = None, is_read: bool = False):
        """Adiciona mensagem à conversa"""
        message = {
            "id": str(uuid4()),
            "type": message_type.value,
            "content": content,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "file_path": file_path,
            "is_read": is_read,
            "read_date": None,
            "sent_date": datetime.utcnow()
        }
        self.messages.append(message)
        self.last_message_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_message_as_read(self, message_id: str):
        """Marca mensagem como lida"""
        for message in self.messages:
            if message["id"] == message_id:
                message["is_read"] = True
                message["read_date"] = datetime.utcnow()
                break


class Report(Document):
    """Relatórios gerados"""
    # Identificação
    report_type: str = Field(..., description="Tipo do relatório")
    name: str = Field(..., description="Nome do relatório")
    description: Optional[str] = Field(None, description="Descrição")
    
    # Parâmetros e filtros
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros utilizados")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filtros aplicados")
    
    # Período
    period_start: Optional[datetime] = Field(None, description="Início do período")
    period_end: Optional[datetime] = Field(None, description="Fim do período")
    
    # Status
    status: str = Field(default="generating", description="Status: generating|completed|error")
    
    # Arquivo gerado
    file_path: Optional[str] = Field(None, description="Caminho do arquivo gerado")
    file_format: Optional[str] = Field(None, description="Formato: pdf|xlsx|csv")
    
    # Controle
    created_by: Optional[str] = Field(None, description="Criado por (usuário)")
    
    # Timestamps
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Data de conclusão")
    
    # Observações
    observations: Optional[str] = Field(None, description="Observações")
    
    class Settings:
        name = "reports"
        indexes = ["report_type", "status", "created_by", "requested_at"]


class SystemLog(Document):
    """Logs do sistema para auditoria"""
    level: str = Field(..., description="Nível: debug|info|warning|error|critical")
    category: Optional[str] = Field(None, description="Categoria do log")
    message: str = Field(..., description="Mensagem do log")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Dados de contexto")
    
    # Usuário e IP (se aplicável)
    user_id: Optional[str] = Field(None, description="ID do usuário")
    ip_address: Optional[str] = Field(None, description="IP do usuário")
    user_agent: Optional[str] = Field(None, description="User agent")
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "system_logs"
        indexes = ["level", "category", "user_id", "created_at"]


# ================================
# MODELOS DE REQUEST/RESPONSE
# ================================

class CompanyRequest(BaseModel):
    """Request para criar/atualizar empresa"""
    name: str = Field(..., min_length=1)
    company_name: str = Field(..., min_length=1)
    cnpj: Optional[str] = None
    company_type: CompanyType
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class JourneyRequest(BaseModel):
    """Request para criar jornada"""
    code: str = Field(..., min_length=1)
    client_id: str = Field(..., min_length=1)
    transporter_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    driver_id: Optional[str] = None
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    origin_coordinates: Optional[List[float]] = None
    destination_coordinates: Optional[List[float]] = None
    estimated_date: Optional[datetime] = None
    observations: Optional[str] = None


class DeliveryRequest(BaseModel):
    """Request para criar entrega"""
    code: str = Field(..., min_length=1)
    client_id: str = Field(..., min_length=1)
    journey_id: Optional[str] = None
    recipient_name: Optional[str] = None
    delivery_address: str = Field(..., min_length=1)
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    cargo_value: Optional[float] = None
    weight_kg: Optional[float] = None
    volume_count: int = Field(default=1)
    estimated_date: Optional[datetime] = None


class IncidentRequest(BaseModel):
    """Request para criar incidente"""
    incident_type: IncidentType
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    journey_id: Optional[str] = None
    delivery_id: Optional[str] = None
    client_id: Optional[str] = None
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    occurrence_date: datetime


# ================================
# EXPORT ALL MODELS
# ================================

__all__ = [
    # Enums
    "CompanyType", "CompanyStatus", "JourneyStatus", "CheckpointStatus", 
    "DeliveryStatus", "DocumentTypeEnum", "DocumentStatus", "IncidentType",
    "IncidentSeverity", "IncidentStatus", "ChatMessageTypeEnum", "VehicleType",
    
    # Document Models
    "MitUser", "Company", "Employee", "Driver", "Vehicle", "Journey", 
    "Delivery", "LogisticsDocument", "Incident", "ChatConversation", 
    "Report", "SystemLog",
    
    # Request Models
    "CompanyRequest", "JourneyRequest", "DeliveryRequest", "IncidentRequest"
]