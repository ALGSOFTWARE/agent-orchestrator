"""
GraphQL Resolvers para operações CRUD no banco de dados real
Conecta com MongoDB Atlas via Gatekeeper API
"""

import aiohttp
import json
from datetime import datetime
from typing import List, Optional
import strawberry
from strawberry.types import Info

from .schemas import (
    User, Client, ContainerDB, ShipmentDB, TrackingEventDB, ContextDB, DatabaseStatsQL,
    UserInput, ClientInput, ContainerDBInput, ShipmentDBInput, TrackingEventDBInput, ContextDBInput
)

# Base URL do Gatekeeper API
GATEKEEPER_API_URL = "http://localhost:8001"


class GatekeeperAPIClient:
    """Cliente HTTP para o Gatekeeper API"""
    
    async def get(self, endpoint: str) -> dict:
        """Requisição GET"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GATEKEEPER_API_URL}{endpoint}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API Error: {response.status}")
    
    async def post(self, endpoint: str, data: dict) -> dict:
        """Requisição POST"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{GATEKEEPER_API_URL}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    raise Exception(f"API Error: {response.status}")
    
    async def put(self, endpoint: str, data: dict) -> dict:
        """Requisição PUT"""
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{GATEKEEPER_API_URL}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API Error: {response.status}")
    
    async def delete(self, endpoint: str) -> bool:
        """Requisição DELETE"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{GATEKEEPER_API_URL}{endpoint}") as response:
                return response.status in [200, 204]


# Instância global do cliente
api_client = GatekeeperAPIClient()


def convert_to_user(user_data: dict) -> User:
    """Converte dados da API para schema GraphQL User"""
    return User(
        id=user_data["_id"],
        name=user_data["name"],
        email=user_data["email"],
        role=user_data["role"],
        client=user_data.get("client", {}).get("id") if user_data.get("client") else None,
        is_active=user_data["is_active"],
        created_at=datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00")),
        last_login=datetime.fromisoformat(user_data["last_login"].replace("Z", "+00:00")) if user_data.get("last_login") else None,
        login_count=user_data["login_count"]
    )


def convert_to_client(client_data: dict) -> Client:
    """Converte dados da API para schema GraphQL Client"""
    return Client(
        id=client_data["_id"],
        name=client_data["name"],
        cnpj=client_data.get("cnpj"),
        address=client_data.get("address"),
        contacts=[json.dumps(contact) for contact in client_data.get("contacts", [])],
        created_at=datetime.fromisoformat(client_data["created_at"].replace("Z", "+00:00"))
    )


def convert_to_container(container_data: dict) -> ContainerDB:
    """Converte dados da API para schema GraphQL ContainerDB"""
    return ContainerDB(
        id=container_data["_id"],
        container_number=container_data["container_number"],
        type=container_data.get("type"),
        current_status=container_data["current_status"],
        location=json.dumps(container_data.get("location")) if container_data.get("location") else None,
        created_at=datetime.fromisoformat(container_data["created_at"].replace("Z", "+00:00")),
        updated_at=datetime.fromisoformat(container_data["updated_at"].replace("Z", "+00:00"))
    )


def convert_to_shipment(shipment_data: dict) -> ShipmentDB:
    """Converte dados da API para schema GraphQL ShipmentDB"""
    return ShipmentDB(
        id=shipment_data["_id"],
        client_id=shipment_data["client"]["id"],
        container_ids=[container["id"] for container in shipment_data.get("containers", [])],
        status=shipment_data["status"],
        departure_port=shipment_data.get("departure_port"),
        arrival_port=shipment_data.get("arrival_port"),
        etd=datetime.fromisoformat(shipment_data["etd"].replace("Z", "+00:00")) if shipment_data.get("etd") else None,
        eta=datetime.fromisoformat(shipment_data["eta"].replace("Z", "+00:00")) if shipment_data.get("eta") else None,
        delivery_date=datetime.fromisoformat(shipment_data["delivery_date"].replace("Z", "+00:00")) if shipment_data.get("delivery_date") else None,
        created_at=datetime.fromisoformat(shipment_data["created_at"].replace("Z", "+00:00"))
    )


def convert_to_tracking_event(event_data: dict) -> TrackingEventDB:
    """Converte dados da API para schema GraphQL TrackingEventDB"""
    return TrackingEventDB(
        id=event_data["_id"],
        container_id=event_data.get("container", {}).get("id") if event_data.get("container") else None,
        shipment_id=event_data.get("shipment", {}).get("id") if event_data.get("shipment") else None,
        type=event_data["type"],
        description=event_data.get("description"),
        timestamp=datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00")),
        location=json.dumps(event_data.get("location")) if event_data.get("location") else None,
        source=event_data["source"]
    )


def convert_to_context(context_data: dict) -> ContextDB:
    """Converte dados da API para schema GraphQL ContextDB"""
    return ContextDB(
        id=context_data["_id"],
        user_id=context_data["user_id"],
        session_id=context_data.get("session_id"),
        input=context_data["input"],
        output=context_data["output"],
        agents_involved=context_data.get("agents_involved", []),
        timestamp=datetime.fromisoformat(context_data["timestamp"].replace("Z", "+00:00")),
        metadata=json.dumps(context_data.get("metadata")) if context_data.get("metadata") else None,
        response_time=context_data.get("response_time")
    )


@strawberry.type
class CRUDQuery:
    """GraphQL Queries para dados reais do MongoDB"""
    
    @strawberry.field
    async def database_stats(self) -> DatabaseStatsQL:
        """Estatísticas do banco de dados"""
        stats_data = await api_client.get("/api/crud/stats")
        return DatabaseStatsQL(
            users=stats_data["users"],
            clients=stats_data["clients"],
            containers=stats_data["containers"],
            shipments=stats_data["shipments"],
            tracking_events=stats_data["tracking_events"],
            contexts=stats_data["contexts"],
            active_users=stats_data["active_users"],
            timestamp=stats_data["timestamp"]
        )
    
    @strawberry.field
    async def users(self, limit: Optional[int] = 100, skip: Optional[int] = 0, role: Optional[str] = None) -> List[User]:
        """Lista usuários"""
        params = f"?limit={limit}&skip={skip}"
        if role:
            params += f"&role={role}"
        
        users_data = await api_client.get(f"/api/crud/users{params}")
        return [convert_to_user(user) for user in users_data]
    
    @strawberry.field
    async def user(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID"""
        try:
            user_data = await api_client.get(f"/api/crud/users/{user_id}")
            return convert_to_user(user_data)
        except:
            return None
    
    @strawberry.field
    async def clients(self, limit: Optional[int] = 100, skip: Optional[int] = 0) -> List[Client]:
        """Lista clientes"""
        params = f"?limit={limit}&skip={skip}"
        clients_data = await api_client.get(f"/api/crud/clients{params}")
        return [convert_to_client(client) for client in clients_data]
    
    @strawberry.field
    async def client(self, client_id: str) -> Optional[Client]:
        """Busca cliente por ID"""
        try:
            client_data = await api_client.get(f"/api/crud/clients/{client_id}")
            return convert_to_client(client_data)
        except:
            return None
    
    @strawberry.field
    async def containers_db(self, limit: Optional[int] = 100, skip: Optional[int] = 0, status: Optional[str] = None) -> List[ContainerDB]:
        """Lista containers do banco"""
        params = f"?limit={limit}&skip={skip}"
        if status:
            params += f"&status={status}"
        
        containers_data = await api_client.get(f"/api/crud/containers{params}")
        return [convert_to_container(container) for container in containers_data]
    
    @strawberry.field
    async def container_db(self, container_id: str) -> Optional[ContainerDB]:
        """Busca container por ID"""
        try:
            container_data = await api_client.get(f"/api/crud/containers/{container_id}")
            return convert_to_container(container_data)
        except:
            return None
    
    @strawberry.field
    async def shipments(self, limit: Optional[int] = 100, skip: Optional[int] = 0, status: Optional[str] = None) -> List[ShipmentDB]:
        """Lista shipments"""
        params = f"?limit={limit}&skip={skip}"
        if status:
            params += f"&status={status}"
        
        shipments_data = await api_client.get(f"/api/crud/shipments{params}")
        return [convert_to_shipment(shipment) for shipment in shipments_data]
    
    @strawberry.field
    async def shipment(self, shipment_id: str) -> Optional[ShipmentDB]:
        """Busca shipment por ID"""
        try:
            shipment_data = await api_client.get(f"/api/crud/shipments/{shipment_id}")
            return convert_to_shipment(shipment_data)
        except:
            return None
    
    @strawberry.field
    async def tracking_events(self, limit: Optional[int] = 100, skip: Optional[int] = 0, type: Optional[str] = None) -> List[TrackingEventDB]:
        """Lista eventos de rastreamento"""
        params = f"?limit={limit}&skip={skip}"
        if type:
            params += f"&type={type}"
        
        events_data = await api_client.get(f"/api/crud/tracking-events{params}")
        return [convert_to_tracking_event(event) for event in events_data]
    
    @strawberry.field
    async def tracking_event(self, event_id: str) -> Optional[TrackingEventDB]:
        """Busca evento por ID"""
        try:
            event_data = await api_client.get(f"/api/crud/tracking-events/{event_id}")
            return convert_to_tracking_event(event_data)
        except:
            return None
    
    @strawberry.field
    async def contexts(self, limit: Optional[int] = 100, skip: Optional[int] = 0, user_id: Optional[str] = None) -> List[ContextDB]:
        """Lista contextos"""
        params = f"?limit={limit}&skip={skip}"
        if user_id:
            params += f"&user_id={user_id}"
        
        contexts_data = await api_client.get(f"/api/crud/contexts{params}")
        return [convert_to_context(context) for context in contexts_data]
    
    @strawberry.field
    async def context(self, context_id: str) -> Optional[ContextDB]:
        """Busca contexto por ID"""
        try:
            context_data = await api_client.get(f"/api/crud/contexts/{context_id}")
            return convert_to_context(context_data)
        except:
            return None


@strawberry.type
class CRUDMutation:
    """GraphQL Mutations para operações CRUD"""
    
    @strawberry.field
    async def create_user(self, user_input: UserInput) -> User:
        """Cria novo usuário"""
        data = {
            "name": user_input.name,
            "email": user_input.email,
            "role": user_input.role,
        }
        if user_input.client_id:
            data["client_id"] = user_input.client_id
        
        user_data = await api_client.post("/api/crud/users", data)
        return convert_to_user(user_data)
    
    @strawberry.field
    async def update_user(self, user_id: str, user_input: UserInput) -> Optional[User]:
        """Atualiza usuário"""
        try:
            data = {
                "name": user_input.name,
                "email": user_input.email,
                "role": user_input.role,
            }
            if user_input.client_id:
                data["client_id"] = user_input.client_id
            
            user_data = await api_client.put(f"/api/crud/users/{user_id}", data)
            return convert_to_user(user_data)
        except:
            return None
    
    @strawberry.field
    async def delete_user(self, user_id: str, soft_delete: Optional[bool] = True) -> bool:
        """Remove usuário"""
        try:
            return await api_client.delete(f"/api/crud/users/{user_id}?soft_delete={soft_delete}")
        except:
            return False
    
    @strawberry.field
    async def create_client(self, client_input: ClientInput) -> Client:
        """Cria novo cliente"""
        data = {
            "name": client_input.name,
        }
        if client_input.cnpj:
            data["cnpj"] = client_input.cnpj
        if client_input.address:
            data["address"] = client_input.address
        if client_input.contacts:
            data["contacts"] = [json.loads(contact) for contact in client_input.contacts]
        
        client_data = await api_client.post("/api/crud/clients", data)
        return convert_to_client(client_data)
    
    @strawberry.field
    async def create_container(self, container_input: ContainerDBInput) -> ContainerDB:
        """Cria novo container"""
        data = {
            "container_number": container_input.container_number,
            "current_status": container_input.current_status,
        }
        if container_input.type:
            data["type"] = container_input.type
        if container_input.location:
            data["location"] = json.loads(container_input.location)
        
        container_data = await api_client.post("/api/crud/containers", data)
        return convert_to_container(container_data)
    
    @strawberry.field
    async def create_shipment(self, shipment_input: ShipmentDBInput) -> ShipmentDB:
        """Cria novo shipment"""
        data = {
            "client_id": shipment_input.client_id,
        }
        if shipment_input.container_ids:
            data["container_ids"] = shipment_input.container_ids
        if shipment_input.status:
            data["status"] = shipment_input.status
        if shipment_input.departure_port:
            data["departure_port"] = shipment_input.departure_port
        if shipment_input.arrival_port:
            data["arrival_port"] = shipment_input.arrival_port
        if shipment_input.etd:
            data["etd"] = shipment_input.etd.isoformat()
        if shipment_input.eta:
            data["eta"] = shipment_input.eta.isoformat()
        
        shipment_data = await api_client.post("/api/crud/shipments", data)
        return convert_to_shipment(shipment_data)
    
    @strawberry.field
    async def create_tracking_event(self, event_input: TrackingEventDBInput) -> TrackingEventDB:
        """Cria novo evento de rastreamento"""
        data = {
            "type": event_input.type,
        }
        if event_input.container_id:
            data["container_id"] = event_input.container_id
        if event_input.shipment_id:
            data["shipment_id"] = event_input.shipment_id
        if event_input.description:
            data["description"] = event_input.description
        if event_input.location:
            data["location"] = json.loads(event_input.location)
        if event_input.source:
            data["source"] = event_input.source
        
        event_data = await api_client.post("/api/crud/tracking-events", data)
        return convert_to_tracking_event(event_data)
    
    @strawberry.field
    async def create_context(self, context_input: ContextDBInput) -> ContextDB:
        """Cria novo contexto"""
        data = {
            "user_id": context_input.user_id,
            "input": context_input.input,
            "output": context_input.output,
        }
        if context_input.session_id:
            data["session_id"] = context_input.session_id
        if context_input.agents_involved:
            data["agents_involved"] = context_input.agents_involved
        if context_input.metadata:
            data["metadata"] = json.loads(context_input.metadata)
        if context_input.response_time:
            data["response_time"] = context_input.response_time
        
        context_data = await api_client.post("/api/crud/contexts", data)
        return convert_to_context(context_data)