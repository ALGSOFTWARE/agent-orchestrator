from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Link
from uuid import UUID, uuid4

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
