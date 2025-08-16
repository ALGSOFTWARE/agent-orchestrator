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