"""
GraphQL Resolvers para operações logísticas
Integra com o banco de dados mockado e MIT Tracking Agent
"""

from datetime import datetime
from typing import List, Optional
import strawberry
from strawberry.types import Info

from database.db_manager import get_database
from .schemas import (
    CTe, Container, BL, Embarcador, Viagem, LogisticsStats,
    CTeInput, ContainerInput, BLInput, PosicaoGPSInput,
    Transportadora, Endereco, PosicaoGPS
)


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


@strawberry.type
class Mutation:
    """GraphQL Mutations para operações logísticas"""
    
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