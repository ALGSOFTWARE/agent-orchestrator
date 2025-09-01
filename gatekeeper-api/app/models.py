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


class DocumentVersionType(str, Enum):
    """Tipos de versionamento de documentos"""
    MAJOR = "major"          # Mudança significativa (1.0 -> 2.0)
    MINOR = "minor"          # Mudança menor (1.0 -> 1.1)
    REVISION = "revision"    # Correção/revisão (1.0 -> 1.0.1)
    AUTO = "auto"           # Versionamento automático do sistema


class ApprovalStatus(str, Enum):
    """Status de aprovação de documentos"""
    PENDING = "pending"              # Aguardando aprovação
    APPROVED = "approved"            # Aprovado
    REJECTED = "rejected"            # Rejeitado
    NEEDS_REVISION = "needs_revision" # Precisa de revisão
    ON_HOLD = "on_hold"             # Em espera
    WITHDRAWN = "withdrawn"          # Retirado pelo autor


class AuthStatus(str, Enum):
    """Status de autenticação"""
    AUTHENTICATED = "authenticated"
    INVALID_TOKEN = "invalid_token"
    EXPIRED_TOKEN = "expired_token"
    UNAUTHORIZED = "unauthorized"


class DocumentCategory(str, Enum):
    """Categorias de documentos para organização"""
    CTE = "cte"
    BL = "bl"
    INVOICE = "invoice"
    PHOTO = "photo"
    VIDEO = "video"
    EMAIL = "email"
    CONTRACT = "contract"
    CERTIFICATE = "certificate"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    """Status do processamento de documentos"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    ERROR = "error"


class OrderStatus(str, Enum):
    """Status da operação logística"""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderType(str, Enum):
    """Tipos de operações logísticas"""
    IMPORT = "import"
    EXPORT = "export"
    DOMESTIC_FREIGHT = "domestic_freight"
    INTERNATIONAL_FREIGHT = "international_freight"
    WAREHOUSING = "warehousing"
    CUSTOMS_CLEARANCE = "customs_clearance"


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

class DocumentVersion(Document):
    """Modelo para controle de versões de documentos"""
    # Identificação da versão
    version_id: str = Field(default_factory=lambda: str(uuid4()), unique=True)
    parent_document_id: str = Field(..., description="ID do documento original")
    
    # Informações da versão
    version_number: str = Field(..., description="Número da versão (ex: 1.0, 1.1, 2.0)")
    version_type: DocumentVersionType = Field(..., description="Tipo de versionamento")
    version_notes: Optional[str] = Field(None, description="Notas sobre as mudanças")
    
    # Dados da versão (snapshot do documento neste momento)
    s3_key: str = Field(..., description="Chave do arquivo da versão no S3")
    s3_url: str = Field(..., description="URL do arquivo da versão")
    file_hash: Optional[str] = Field(None, description="Hash MD5/SHA256 do arquivo")
    
    # Metadados da versão
    created_by: str = Field(..., description="Usuário que criou esta versão")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_current: bool = Field(default=False, description="Se é a versão atual")
    is_published: bool = Field(default=False, description="Se foi publicada")
    
    # Dados técnicos
    text_content: Optional[str] = Field(None, description="Texto extraído desta versão")
    embedding: Optional[List[float]] = Field(None, description="Embedding desta versão")
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.UPLOADED)
    
    class Settings:
        name = "document_versions"


class DocumentApproval(Document):
    """Modelo para controle de aprovação de documentos"""
    # Identificação
    approval_id: str = Field(default_factory=lambda: str(uuid4()), unique=True)
    document_id: str = Field(..., description="ID do documento sendo aprovado")
    version_id: Optional[str] = Field(None, description="ID da versão específica (se aplicável)")
    
    # Status e fluxo
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    approval_level: int = Field(default=1, description="Nível de aprovação (1, 2, 3...)")
    required_approvers: List[str] = Field(default_factory=list, description="Lista de aprovadores obrigatórios")
    
    # Histórico de aprovações
    approvals: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de aprovações/rejeições")
    current_approver: Optional[str] = Field(None, description="Aprovador atual")
    
    # Prazos e notificações
    created_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = Field(None, description="Prazo para aprovação")
    escalation_date: Optional[datetime] = Field(None, description="Data de escalação")
    
    # Comentários e feedback
    comments: List[Dict[str, Any]] = Field(default_factory=list, description="Comentários do processo")
    approval_criteria: Optional[str] = Field(None, description="Critérios de aprovação")
    
    class Settings:
        name = "document_approvals"
        
    def add_approval(self, approver_id: str, decision: ApprovalStatus, comments: Optional[str] = None):
        """Adiciona uma decisão de aprovação"""
        approval_record = {
            "approver_id": approver_id,
            "decision": decision.value,
            "comments": comments,
            "timestamp": datetime.utcnow().isoformat(),
            "approval_level": self.approval_level
        }
        self.approvals.append(approval_record)
        
        # Atualizar status geral baseado na decisão
        if decision == ApprovalStatus.APPROVED:
            # Verificar se todos os aprovadores obrigatórios aprovaram
            approved_by = {a["approver_id"] for a in self.approvals if a["decision"] == "approved"}
            if all(req_approver in approved_by for req_approver in self.required_approvers):
                self.status = ApprovalStatus.APPROVED
        elif decision in [ApprovalStatus.REJECTED, ApprovalStatus.NEEDS_REVISION]:
            self.status = decision


class DocumentFile(Document):
    """Modelo expandido para qualquer arquivo enviado via upload com capacidades de IA."""
    # Identificação básica
    file_id: str = Field(default_factory=lambda: str(uuid4()), unique=True)
    original_name: str = Field(..., description="Nome original do arquivo")
    s3_key: str = Field(..., description="Chave única no S3")
    s3_url: str = Field(..., description="URL de acesso ao arquivo")
    
    # Metadados do arquivo
    file_type: str = Field(..., description="MIME type do arquivo")
    file_extension: str = Field(..., description="Extensão do arquivo (.pdf, .jpg, etc.)")
    size_bytes: int = Field(..., description="Tamanho em bytes")
    category: DocumentCategory = Field(default=DocumentCategory.OTHER, description="Categoria do documento")
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    
    # Processamento e IA
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.UPLOADED)
    text_content: Optional[str] = Field(None, description="Texto extraído via OCR/parsing")
    extracted_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados extraídos automaticamente")
    
    # Embedding para busca semântica
    embedding: Optional[List[float]] = Field(None, description="Vetor de embedding para busca semântica")
    embedding_model: Optional[str] = Field(None, description="Modelo usado para gerar o embedding")
    indexed_at: Optional[datetime] = Field(None, description="Quando foi indexado para busca")
    
    # Relacionamentos - TODO DOCUMENTO DEVE ESTAR VINCULADO A UMA ORDER
    order_id: str = Field(..., description="ID da Order à qual pertence (obrigatório)")
    tags: List[str] = Field(default_factory=list, description="Tags para organização")
    
    # Controle de acesso
    is_public: bool = Field(default=True, description="Se o arquivo é público ou privado")
    access_count: int = Field(default=0, description="Número de acessos")
    
    # Logs de processamento
    processing_logs: List[str] = Field(default_factory=list, description="Logs do processamento")
    error_details: Optional[str] = Field(None, description="Detalhes de erro se houver")

    class Settings:
        name = "document_files"
        
    def increment_access(self):
        """Incrementa contador de acesso"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
        
    def add_processing_log(self, message: str):
        """Adiciona log de processamento"""
        timestamp = datetime.utcnow().isoformat()
        self.processing_logs.append(f"[{timestamp}] {message}")
        
    def mark_as_processing(self):
        """Marca documento como sendo processado"""
        self.processing_status = ProcessingStatus.PROCESSING
        self.add_processing_log("Iniciando processamento...")
        
    def mark_as_indexed(self, embedding_model: str):
        """Marca documento como indexado"""
        self.processing_status = ProcessingStatus.INDEXED
        self.embedding_model = embedding_model
        self.indexed_at = datetime.utcnow()
        self.add_processing_log(f"Indexado com sucesso usando {embedding_model}")
        
    def mark_as_error(self, error_message: str):
        """Marca documento com erro"""
        self.processing_status = ProcessingStatus.ERROR
        self.error_details = error_message
        self.add_processing_log(f"Erro: {error_message}")
    
    # Métodos de versionamento
    current_version: str = Field(default="1.0", description="Versão atual do documento")
    version_count: int = Field(default=1, description="Número total de versões")
    is_versioned: bool = Field(default=True, description="Se o documento suporta versionamento")
    
    # Relacionamentos com versões e aprovações
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="Status de aprovação atual")
    requires_approval: bool = Field(default=False, description="Se o documento requer aprovação")
    approved_by: List[str] = Field(default_factory=list, description="Lista de aprovadores")
    approved_at: Optional[datetime] = Field(None, description="Data da aprovação")
    
    # Controle de versões
    def create_new_version(self, version_type: DocumentVersionType, created_by: str, 
                          version_notes: Optional[str] = None, new_s3_key: Optional[str] = None) -> str:
        """Cria uma nova versão do documento"""
        import re
        
        # Calcular novo número de versão
        current_parts = self.current_version.split('.')
        major, minor = int(current_parts[0]), int(current_parts[1]) if len(current_parts) > 1 else 0
        revision = int(current_parts[2]) if len(current_parts) > 2 else 0
        
        if version_type == DocumentVersionType.MAJOR:
            new_version = f"{major + 1}.0"
        elif version_type == DocumentVersionType.MINOR:
            new_version = f"{major}.{minor + 1}"
        elif version_type == DocumentVersionType.REVISION:
            new_version = f"{major}.{minor}.{revision + 1}"
        else:  # AUTO
            new_version = f"{major}.{minor}.{revision + 1}"
        
        # Criar registro de versão (será salvo separadamente)
        version_data = {
            "parent_document_id": str(self.id),
            "version_number": new_version,
            "version_type": version_type,
            "version_notes": version_notes,
            "s3_key": new_s3_key or self.s3_key,
            "s3_url": self.s3_url,
            "created_by": created_by,
            "text_content": self.text_content,
            "embedding": self.embedding,
            "processing_status": self.processing_status,
            "is_current": True
        }
        
        # Atualizar documento principal
        self.current_version = new_version
        self.version_count += 1
        self.add_processing_log(f"Nova versão {new_version} criada por {created_by}")
        
        return new_version
    
    def request_approval(self, required_approvers: List[str], approval_level: int = 1, 
                        due_date: Optional[datetime] = None, criteria: Optional[str] = None):
        """Solicita aprovação do documento"""
        self.approval_status = ApprovalStatus.PENDING
        self.requires_approval = True
        self.add_processing_log(f"Aprovação solicitada para: {', '.join(required_approvers)}")
        
        # Retorna dados para criar DocumentApproval separadamente
        return {
            "document_id": str(self.id),
            "version_id": None,  # Se for versão específica
            "required_approvers": required_approvers,
            "approval_level": approval_level,
            "due_date": due_date,
            "approval_criteria": criteria
        }
    
    def approve_document(self, approver_id: str, comments: Optional[str] = None):
        """Aprova o documento"""
        self.approval_status = ApprovalStatus.APPROVED
        if approver_id not in self.approved_by:
            self.approved_by.append(approver_id)
        self.approved_at = datetime.utcnow()
        self.add_processing_log(f"Documento aprovado por {approver_id}")
    
    def reject_document(self, approver_id: str, reason: str):
        """Rejeita o documento"""
        self.approval_status = ApprovalStatus.REJECTED
        self.add_processing_log(f"Documento rejeitado por {approver_id}: {reason}")
    
    def get_version_history(self) -> Dict[str, Any]:
        """Retorna histórico simplificado de versões"""
        return {
            "current_version": self.current_version,
            "version_count": self.version_count,
            "approval_status": self.approval_status.value,
            "requires_approval": self.requires_approval,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None
        }

class Order(Document):
    """Super-contêiner: Nó central que representa uma Ordem de Serviço ou Operação Logística completa."""
    # Identificação e controle
    order_id: str = Field(default_factory=lambda: str(uuid4()), unique=True)
    order_number: Optional[str] = Field(None, description="Número da ordem (pode ser externo)")
    
    # Informações básicas
    title: str = Field(..., description="Título descritivo da operação")
    description: Optional[str] = Field(None, description="Descrição detalhada")
    order_type: OrderType = Field(..., description="Tipo de operação logística")
    status: OrderStatus = Field(default=OrderStatus.CREATED, description="Status atual da operação")
    
    # Informações comerciais
    customer_name: str = Field(..., description="Nome do cliente")
    customer_id: Optional[str] = Field(None, description="ID do cliente no sistema")
    origin: Optional[str] = Field(None, description="Origem da carga/operação")
    destination: Optional[str] = Field(None, description="Destino da carga/operação")
    
    # Datas importantes
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expected_delivery: Optional[datetime] = Field(None, description="Data prevista de entrega")
    actual_delivery: Optional[datetime] = Field(None, description="Data real de entrega")
    
    # Informações financeiras
    estimated_value: Optional[float] = Field(None, description="Valor estimado da operação")
    actual_cost: Optional[float] = Field(None, description="Custo real da operação")
    currency: Optional[str] = Field(default="BRL", description="Moeda")
    
    # Relacionamentos com documentos estruturados
    ctes: List[Link["CTEDocument"]] = Field(default_factory=list, description="CT-es vinculados")
    bls: List[Link["BLDocument"]] = Field(default_factory=list, description="BLs vinculados")
    containers: List[Link["Container"]] = Field(default_factory=list, description="Containers vinculados")
    
    # Documentos não estruturados (o coração do sistema)
    document_files: List[Link[DocumentFile]] = Field(default_factory=list, description="Todos os arquivos da operação")
    
    # Organização e busca
    tags: List[str] = Field(default_factory=list, description="Tags para organização")
    priority: int = Field(default=3, ge=1, le=5, description="Prioridade (1=baixa, 5=alta)")
    
    # Colaboração e notificações
    assigned_users: List[str] = Field(default_factory=list, description="Usuários responsáveis")
    watchers: List[str] = Field(default_factory=list, description="Usuários que acompanham")
    
    # Tracking e auditoria
    status_history: List[Dict[str, Any]] = Field(default_factory=list, description="Histórico de mudanças de status")
    notes: List[Dict[str, Any]] = Field(default_factory=list, description="Notas e comentários")
    
    # Análise e métricas
    document_count: int = Field(default=0, description="Contador de documentos")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Última atividade")

    class Settings:
        name = "orders"
        
    def add_status_change(self, new_status: OrderStatus, user_id: str, notes: Optional[str] = None):
        """Adiciona mudança de status ao histórico"""
        change = {
            "from_status": self.status.value if self.status else None,
            "to_status": new_status.value,
            "changed_by": user_id,
            "changed_at": datetime.utcnow().isoformat(),
            "notes": notes
        }
        self.status_history.append(change)
        self.status = new_status
        self.updated_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        
    def add_note(self, content: str, user_id: str, note_type: str = "comment"):
        """Adiciona nota ou comentário"""
        note = {
            "id": str(uuid4()),
            "content": content,
            "type": note_type,
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat()
        }
        self.notes.append(note)
        self.last_activity = datetime.utcnow()
        
    def add_document(self, document_file: DocumentFile):
        """Vincula um documento à ordem"""
        # Criar link para o documento
        doc_link = Link(document_file.id, DocumentFile)
        self.document_files.append(doc_link)
        
        # Atualizar contador e atividade
        self.document_count += 1
        self.last_activity = datetime.utcnow()
        
        # Atualizar o documento com o ID da ordem
        document_file.order_id = self.order_id
        
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo da ordem para dashboards"""
        return {
            "order_id": self.order_id,
            "title": self.title,
            "customer": self.customer_name,
            "status": self.status.value,
            "type": self.order_type.value,
            "document_count": self.document_count,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "priority": self.priority
        }

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