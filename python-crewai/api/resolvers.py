"""
GraphQL Resolvers para operações logísticas
Integra com o banco de dados mockado e MIT Tracking Agent
"""

from datetime import datetime
from typing import List, Optional
import json
import strawberry
from strawberry.types import Info

# from database.db_manager import get_database  # Legacy - usando MongoDB Atlas via Gatekeeper API

# Mock temporário para manter compatibilidade
def get_database():
    """Mock temporário - dados são agora gerenciados via Gatekeeper API + MongoDB Atlas"""
    return {
        'ctes': [],
        'containers': [],
        'bls': [],
        'transportadoras': [],
        'embarcadores': [],
        'viagens': []
    }
from .schemas import (
    CTe, Container, BL, Embarcador, Viagem, LogisticsStats,
    CTeInput, ContainerInput, BLInput, PosicaoGPSInput,
    Transportadora, Endereco, PosicaoGPS,
    ChatMessage, ChatResponse, ChatInput,
    User, Client, ContainerDB, ShipmentDB, TrackingEventDB, ContextDB, DatabaseStatsQL,
    UserInput, ClientInput, ContainerDBInput, ShipmentDBInput, TrackingEventDBInput, ContextDBInput
)
from .crud_resolvers import CRUDQuery, CRUDMutation

# Import do MIT Agent v2 (sempre usar versão simulada para testes)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

try:
    from mock_mit_agent_v2 import MockMITTrackingAgentV2, create_mock_agent
    MIT_AGENT_V2_AVAILABLE = True
    MIT_AGENT_MOCK_MODE = True
    print("✅ MIT Agent v2 simulado carregado")
except ImportError as e:
    MIT_AGENT_V2_AVAILABLE = False
    MIT_AGENT_MOCK_MODE = False
    print(f"❌ Erro ao carregar MIT Agent v2 simulado: {e}")


def convert_db_to_cte(cte_data: dict) -> CTe:
    """Converte dados do banco para schema GraphQL CTe"""
    return CTe(
        id=cte_data.get("_id", ""),
        numero_cte=cte_data.get("numero_cte", ""),
        status=cte_data.get("status", ""),
        data_emissao=datetime.fromisoformat(cte_data.get("data_emissao", "").replace("Z", "+00:00")),
        transportadora=Transportadora(
            nome=cte_data.get("transportadora", {}).get("nome", ""),
            cnpj=cte_data.get("transportadora", {}).get("cnpj", ""),
            telefone=cte_data.get("transportadora", {}).get("telefone"),
            email=cte_data.get("transportadora", {}).get("email")
        ),
        origem=Endereco(
            municipio=cte_data.get("origem", {}).get("municipio", ""),
            uf=cte_data.get("origem", {}).get("uf", ""),
            cep=cte_data.get("origem", {}).get("cep"),
            endereco_completo=cte_data.get("origem", {}).get("endereco_completo"),
            latitude=cte_data.get("origem", {}).get("latitude"),
            longitude=cte_data.get("origem", {}).get("longitude")
        ),
        destino=Endereco(
            municipio=cte_data.get("destino", {}).get("municipio", ""),
            uf=cte_data.get("destino", {}).get("uf", ""),
            cep=cte_data.get("destino", {}).get("cep"),
            endereco_completo=cte_data.get("destino", {}).get("endereco_completo"),
            latitude=cte_data.get("destino", {}).get("latitude"),
            longitude=cte_data.get("destino", {}).get("longitude")
        ),
        valor_frete=cte_data.get("valor_frete", 0.0),
        peso_bruto=cte_data.get("peso_bruto", 0.0),
        containers=cte_data.get("containers", []),
        previsao_entrega=datetime.fromisoformat(cte_data.get("previsao_entrega", "").replace("Z", "+00:00")) if cte_data.get("previsao_entrega") else None,
        observacoes=cte_data.get("observacoes")
    )


def convert_db_to_container(container_data: dict) -> Container:
    """Converte dados do banco para schema GraphQL Container"""
    posicao_atual = None
    if container_data.get("posicao_atual"):
        pos = container_data["posicao_atual"]
        posicao_atual = PosicaoGPS(
            latitude=pos.get("latitude", 0.0),
            longitude=pos.get("longitude", 0.0),
            timestamp=datetime.fromisoformat(pos.get("timestamp", "").replace("Z", "+00:00")),
            velocidade=pos.get("velocidade"),
            endereco=pos.get("endereco")
        )
    
    historico_posicoes = []
    for pos in container_data.get("historico_posicoes", []):
        historico_posicoes.append(PosicaoGPS(
            latitude=pos.get("latitude", 0.0),
            longitude=pos.get("longitude", 0.0),
            timestamp=datetime.fromisoformat(pos.get("timestamp", "").replace("Z", "+00:00")),
            velocidade=pos.get("velocidade"),
            endereco=pos.get("endereco")
        ))
    
    return Container(
        id=container_data.get("_id", ""),
        numero=container_data.get("numero", ""),
        tipo=container_data.get("tipo", ""),
        status=container_data.get("status", ""),
        posicao_atual=posicao_atual,
        temperatura_atual=container_data.get("temperatura_atual"),
        historico_posicoes=historico_posicoes,
        cte_associado=container_data.get("cte_associado"),
        peso_bruto=container_data.get("peso_bruto"),
        observacoes=container_data.get("observacoes")
    )


def convert_db_to_bl(bl_data: dict) -> BL:
    """Converte dados do banco para schema GraphQL BL"""
    return BL(
        id=bl_data.get("_id", ""),
        numero_bl=bl_data.get("numero_bl", ""),
        status=bl_data.get("status", ""),
        data_embarque=datetime.fromisoformat(bl_data.get("data_embarque", "").replace("Z", "+00:00")),
        porto_origem=bl_data.get("porto_origem", ""),
        porto_destino=bl_data.get("porto_destino", ""),
        navio=bl_data.get("navio", ""),
        containers=bl_data.get("containers", []),
        peso_total=bl_data.get("peso_total", 0.0),
        valor_mercadorias=bl_data.get("valor_mercadorias", 0.0),
        eta_destino=datetime.fromisoformat(bl_data.get("eta_destino", "").replace("Z", "+00:00")) if bl_data.get("eta_destino") else None,
        observacoes=bl_data.get("observacoes")
    )


@strawberry.type
class Query:
    """GraphQL Queries para consultas logísticas"""
    
    @strawberry.field
    def hello(self) -> str:
        """Teste básico da API"""
        return "MIT Tracking GraphQL API está funcionando! 🚚"
    
    # === CRUD DATABASE QUERIES === #
    
    @strawberry.field
    async def database_stats(self) -> DatabaseStatsQL:
        """Estatísticas do banco de dados"""
        crud_query = CRUDQuery()
        return await crud_query.database_stats()
    
    @strawberry.field
    async def users(self, limit: Optional[int] = 100, skip: Optional[int] = 0, role: Optional[str] = None) -> List[User]:
        """Lista usuários do banco"""
        crud_query = CRUDQuery()
        return await crud_query.users(limit=limit, skip=skip, role=role)
    
    @strawberry.field
    async def user(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID"""
        crud_query = CRUDQuery()
        return await crud_query.user(user_id=user_id)
    
    @strawberry.field
    async def clients(self, limit: Optional[int] = 100, skip: Optional[int] = 0) -> List[Client]:
        """Lista clientes do banco"""
        crud_query = CRUDQuery()
        return await crud_query.clients(limit=limit, skip=skip)
    
    @strawberry.field
    async def client(self, client_id: str) -> Optional[Client]:
        """Busca cliente por ID"""
        crud_query = CRUDQuery()
        return await crud_query.client(client_id=client_id)
    
    @strawberry.field
    async def containers_db(self, limit: Optional[int] = 100, skip: Optional[int] = 0, status: Optional[str] = None) -> List[ContainerDB]:
        """Lista containers do banco"""
        crud_query = CRUDQuery()
        return await crud_query.containers_db(limit=limit, skip=skip, status=status)
    
    @strawberry.field
    async def container_db(self, container_id: str) -> Optional[ContainerDB]:
        """Busca container por ID"""
        crud_query = CRUDQuery()
        return await crud_query.container_db(container_id=container_id)
    
    @strawberry.field
    async def shipments(self, limit: Optional[int] = 100, skip: Optional[int] = 0, status: Optional[str] = None) -> List[ShipmentDB]:
        """Lista shipments do banco"""
        crud_query = CRUDQuery()
        return await crud_query.shipments(limit=limit, skip=skip, status=status)
    
    @strawberry.field
    async def shipment(self, shipment_id: str) -> Optional[ShipmentDB]:
        """Busca shipment por ID"""
        crud_query = CRUDQuery()
        return await crud_query.shipment(shipment_id=shipment_id)
    
    @strawberry.field
    async def tracking_events(self, limit: Optional[int] = 100, skip: Optional[int] = 0, type: Optional[str] = None) -> List[TrackingEventDB]:
        """Lista eventos de rastreamento do banco"""
        crud_query = CRUDQuery()
        return await crud_query.tracking_events(limit=limit, skip=skip, type=type)
    
    @strawberry.field
    async def tracking_event(self, event_id: str) -> Optional[TrackingEventDB]:
        """Busca evento por ID"""
        crud_query = CRUDQuery()
        return await crud_query.tracking_event(event_id=event_id)
    
    @strawberry.field
    async def contexts(self, limit: Optional[int] = 100, skip: Optional[int] = 0, user_id: Optional[str] = None) -> List[ContextDB]:
        """Lista contextos do banco"""
        crud_query = CRUDQuery()
        return await crud_query.contexts(limit=limit, skip=skip, user_id=user_id)
    
    @strawberry.field
    async def context(self, context_id: str) -> Optional[ContextDB]:
        """Busca contexto por ID"""
        crud_query = CRUDQuery()
        return await crud_query.context(context_id=context_id)
    
    @strawberry.field
    def ctes(self) -> List[CTe]:
        """Lista todos os CT-e"""
        db = get_database()
        cte_data = db.find_all("cte_documents")
        return [convert_db_to_cte(cte) for cte in cte_data]
    
    @strawberry.field
    def cte_by_number(self, numero: str) -> Optional[CTe]:
        """Busca CT-e por número"""
        db = get_database()
        cte_data = db.find_cte_by_number(numero)
        return convert_db_to_cte(cte_data) if cte_data else None
    
    @strawberry.field
    def containers(self) -> List[Container]:
        """Lista todos os containers"""
        db = get_database()
        container_data = db.find_all("containers")
        return [convert_db_to_container(container) for container in container_data]
    
    @strawberry.field
    def container_by_number(self, numero: str) -> Optional[Container]:
        """Busca container por número"""
        db = get_database()
        container_data = db.find_container_by_number(numero)
        return convert_db_to_container(container_data) if container_data else None
    
    @strawberry.field
    def bls(self) -> List[BL]:
        """Lista todos os BL"""
        db = get_database()
        bl_data = db.find_all("bl_documents")
        return [convert_db_to_bl(bl) for bl in bl_data]
    
    @strawberry.field
    def bl_by_number(self, numero: str) -> Optional[BL]:
        """Busca BL por número"""
        db = get_database()
        bl_data = db.find_bl_by_number(numero)
        return convert_db_to_bl(bl_data) if bl_data else None
    
    @strawberry.field
    def containers_em_transito(self) -> List[Container]:
        """Lista containers em trânsito"""
        db = get_database()
        containers_data = db.search_logistics("status:EM_TRANSITO", collection="containers")
        return [convert_db_to_container(container) for container in containers_data]
    
    @strawberry.field
    def logistics_stats(self) -> LogisticsStats:
        """Estatísticas gerais do sistema"""
        db = get_database()
        stats = db.get_statistics()
        
        # Calcular estatísticas detalhadas
        ctes_data = db.find_all("cte_documents")
        containers_data = db.find_all("containers")
        bls_data = db.find_all("bl_documents")
        
        containers_em_transito = len([c for c in containers_data if c.get("status") == "EM_TRANSITO"])
        ctes_entregues = len([c for c in ctes_data if c.get("status") == "ENTREGUE"])
        valor_total_fretes = sum(c.get("valor_frete", 0) for c in ctes_data)
        
        return LogisticsStats(
            total_ctes=len(ctes_data),
            total_containers=len(containers_data),
            total_bls=len(bls_data),
            containers_em_transito=containers_em_transito,
            ctes_entregues=ctes_entregues,
            valor_total_fretes=valor_total_fretes
        )
    
    @strawberry.field
    def chat_test_connection(self) -> bool:
        """Testa se o agente MIT Tracking v2 está disponível"""
        agent = get_or_create_agent()
        return agent is not None and agent.is_ready


@strawberry.type
class Mutation:
    """GraphQL Mutations para operações logísticas"""
    
    # === CRUD DATABASE MUTATIONS === #
    
    @strawberry.field
    async def create_user(self, user_input: UserInput) -> User:
        """Cria novo usuário"""
        crud_mutation = CRUDMutation()
        return await crud_mutation.create_user(user_input=user_input)
    
    @strawberry.field
    async def update_user(self, user_id: str, user_input: UserInput) -> Optional[User]:
        """Atualiza usuário"""
        crud_mutation = CRUDMutation()
        return await crud_mutation.update_user(user_id=user_id, user_input=user_input)
    
    @strawberry.field
    async def delete_user(self, user_id: str, soft_delete: Optional[bool] = True) -> bool:
        """Remove usuário"""
        crud_mutation = CRUDMutation()
        return await crud_mutation.delete_user(user_id=user_id, soft_delete=soft_delete)
    
    @strawberry.field
    async def create_client(self, client_input: ClientInput) -> Client:
        """Cria novo cliente"""
        crud_mutation = CRUDMutation()
        return await crud_mutation.create_client(client_input=client_input)
    
    @strawberry.field
    async def create_container_db(self, container_input: ContainerDBInput) -> ContainerDB:
        """Cria novo container"""
        crud_mutation = CRUDMutation()
        return await crud_mutation.create_container(container_input=container_input)
    
    @strawberry.field
    async def create_shipment(self, shipment_input: ShipmentDBInput) -> ShipmentDB:
        """Cria novo shipment"""
        crud_mutation = CRUDMutation()
        return await crud_mutation.create_shipment(shipment_input=shipment_input)
    
    @strawberry.field
    async def create_tracking_event(self, event_input: TrackingEventDBInput) -> TrackingEventDB:
        """Cria novo evento de rastreamento"""
        crud_mutation = CRUDMutation()
        return await crud_mutation.create_tracking_event(event_input=event_input)
    
    @strawberry.field
    async def create_context(self, context_input: ContextDBInput) -> ContextDB:
        """Cria novo contexto"""
        crud_mutation = CRUDMutation()
        return await crud_mutation.create_context(context_input=context_input)
    
    @strawberry.field
    def create_cte(self, cte_input: CTeInput) -> CTe:
        """Cria novo CT-e"""
        db = get_database()
        
        # Converter input para formato do banco
        cte_data = {
            "_id": f"cte_{datetime.now().timestamp()}",
            "numero_cte": cte_input.numero_cte,
            "status": cte_input.status,
            "data_emissao": datetime.now().isoformat(),
            "transportadora": {
                "nome": cte_input.transportadora.nome,
                "cnpj": cte_input.transportadora.cnpj,
                "telefone": cte_input.transportadora.telefone,
                "email": cte_input.transportadora.email
            },
            "origem": {
                "municipio": cte_input.origem.municipio,
                "uf": cte_input.origem.uf,
                "cep": cte_input.origem.cep,
                "endereco_completo": cte_input.origem.endereco_completo,
                "latitude": cte_input.origem.latitude,
                "longitude": cte_input.origem.longitude
            },
            "destino": {
                "municipio": cte_input.destino.municipio,
                "uf": cte_input.destino.uf,
                "cep": cte_input.destino.cep,
                "endereco_completo": cte_input.destino.endereco_completo,
                "latitude": cte_input.destino.latitude,
                "longitude": cte_input.destino.longitude
            },
            "valor_frete": cte_input.valor_frete,
            "peso_bruto": cte_input.peso_bruto,
            "containers": cte_input.containers,
            "previsao_entrega": cte_input.previsao_entrega.isoformat() if cte_input.previsao_entrega else None,
            "observacoes": cte_input.observacoes
        }
        
        # Adicionar ao banco (simular inserção)
        db.collections["cte_documents"].append(cte_data)
        
        return convert_db_to_cte(cte_data)
    
    @strawberry.field
    def update_container_position(self, numero: str, posicao: PosicaoGPSInput) -> Optional[Container]:
        """Atualiza posição do container"""
        db = get_database()
        
        # Encontrar container
        for container_data in db.collections["containers"]:
            if container_data.get("numero") == numero:
                # Atualizar posição atual
                nova_posicao = {
                    "latitude": posicao.latitude,
                    "longitude": posicao.longitude,
                    "timestamp": datetime.now().isoformat(),
                    "velocidade": posicao.velocidade,
                    "endereco": posicao.endereco
                }
                
                # Mover posição atual para histórico
                if container_data.get("posicao_atual"):
                    container_data.setdefault("historico_posicoes", []).append(container_data["posicao_atual"])
                
                container_data["posicao_atual"] = nova_posicao
                
                return convert_db_to_container(container_data)
        
        return None
    
    @strawberry.field
    def update_cte_status(self, numero: str, novo_status: str) -> Optional[CTe]:
        """Atualiza status do CT-e"""
        db = get_database()
        cte_data = db.find_cte_by_number(numero)
        
        if cte_data:
            # Encontrar no array e atualizar
            for cte in db.collections["cte_documents"]:
                if cte.get("numero_cte") == numero:
                    cte["status"] = novo_status
                    return convert_db_to_cte(cte)
        
        return None
    
    @strawberry.field
    async def chat_with_agent(self, chat_input: ChatInput) -> ChatResponse:
        """Envia mensagem para o MIT Tracking Agent v2"""
        
        # Validações
        if not chat_input.message.strip():
            return ChatResponse(
                message=ChatMessage(
                    id=f"error_{datetime.now().timestamp()}",
                    content="Mensagem não pode estar vazia",
                    role="system",
                    timestamp=datetime.now()
                ),
                success=False,
                error="Mensagem vazia"
            )
        
        # Obter agente
        agent = get_or_create_agent(chat_input.preferred_provider)
        if not agent:
            return ChatResponse(
                message=ChatMessage(
                    id=f"error_{datetime.now().timestamp()}",
                    content="❌ Agente MIT Tracking v2 não está disponível. Verifique as configurações de API.",
                    role="system", 
                    timestamp=datetime.now()
                ),
                success=False,
                error="Agente não disponível"
            )
        
        try:
            # Processar consulta
            start_time = datetime.now()
            response_content = await agent.consultar_logistica(chat_input.message)
            end_time = datetime.now()
            
            # Extrair metadados da resposta
            provider = None
            tokens_used = None
            response_time = (end_time - start_time).total_seconds()
            
            # Parse da resposta para extrair metadados (formato: "resposta\n\n🧠 _Processado via provider (tokens, tempo)_")
            if "🧠 _Processado via" in response_content:
                parts = response_content.split("🧠 _Processado via")
                if len(parts) == 2:
                    content = parts[0].strip()
                    metadata_part = parts[1]
                    
                    # Extrair provider
                    if "openai" in metadata_part.lower():
                        provider = "openai"
                    elif "gemini" in metadata_part.lower():
                        provider = "gemini"
                    
                    # Extrair tokens
                    import re
                    token_match = re.search(r'(\d+)\s*tokens', metadata_part)
                    if token_match:
                        tokens_used = int(token_match.group(1))
                else:
                    content = response_content
            else:
                content = response_content
            
            # Criar mensagem de resposta
            message = ChatMessage(
                id=f"agent_{datetime.now().timestamp()}",
                content=content,
                role="agent",
                timestamp=datetime.now(),
                agent_type="mit-tracking-v2",
                session_id=chat_input.session_id or agent.get_session_id(),
                provider=provider,
                tokens_used=tokens_used,
                response_time=response_time,
                confidence=0.9  # Placeholder
            )
            
            # Obter estatísticas do agente
            stats = agent.get_stats()
            if isinstance(stats, dict):
                # Agente simulado retorna dict
                agent_stats = json.dumps(stats)
            else:
                # Agente real retorna objeto com atributos
                agent_stats = json.dumps({
                    "total_queries": getattr(stats, 'total_queries', 0),
                    "successful_queries": getattr(stats, 'successful_queries', 0),
                    "error_count": getattr(stats, 'error_count', 0),
                    "average_response_time": getattr(stats, 'average_response_time', 0.0),
                    "session_duration": getattr(stats, 'session_duration', 0.0)
                })
            
            return ChatResponse(
                message=message,
                success=True,
                agent_stats=agent_stats
            )
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erro no chat: {error_msg}")
            
            return ChatResponse(
                message=ChatMessage(
                    id=f"error_{datetime.now().timestamp()}",
                    content=f"❌ Erro interno: {error_msg}",
                    role="system",
                    timestamp=datetime.now(),
                    session_id=chat_input.session_id
                ),
                success=False,
                error=error_msg
            )


# === Chat Functions ===

# Instância global do agente (cache)
if MIT_AGENT_V2_AVAILABLE:
    if 'MIT_AGENT_MOCK_MODE' in globals() and MIT_AGENT_MOCK_MODE:
        _global_agent: Optional[MockMITTrackingAgentV2] = None
    else:
        _global_agent: Optional[MITTrackingAgentV2] = None
else:
    _global_agent = None

def get_or_create_agent(preferred_provider: Optional[str] = None):
    """Obtém ou cria instância do agente MIT Tracking v2"""
    global _global_agent
    
    if not MIT_AGENT_V2_AVAILABLE:
        return None
    
    if _global_agent is None:
        try:
            if 'MIT_AGENT_MOCK_MODE' in globals() and MIT_AGENT_MOCK_MODE:
                # Usar versão simulada
                _global_agent = create_mock_agent(preferred_provider)
                print("✅ MIT Agent v2 simulado criado")
            else:
                # Usar versão real
                provider = None
                if preferred_provider:
                    if preferred_provider.lower() == 'openai':
                        provider = LLMProvider.OPENAI
                    elif preferred_provider.lower() == 'gemini':
                        provider = LLMProvider.GEMINI
                
                _global_agent = MITTrackingAgentV2(preferred_provider=provider)
                print("✅ MIT Agent v2 real criado")
        except Exception as e:
            print(f"❌ Erro ao criar agente: {e}")
            return None
    
    return _global_agent


# Instância global de Query e Mutation
query_instance = None
mutation_instance = None