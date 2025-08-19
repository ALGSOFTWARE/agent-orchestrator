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
    Order, OrderInput, DocumentFile, DocumentFileInput, 
    LogisticsStats, CTEDocument, BLDocument, Container
)

# Base URL do Gatekeeper API
GATEKEEPER_API_URL = "http://localhost:8001"

class GatekeeperAPIClient:
    """Cliente HTTP para o Gatekeeper API"""
    
    async def get(self, endpoint: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GATEKEEPER_API_URL}{endpoint}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API Error: {response.status}")
    
    async def post(self, endpoint: str, data: dict) -> dict:
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

api_client = GatekeeperAPIClient()

def convert_to_order(order_data: dict) -> Order:
    return Order(
        id=order_data["_id"],
        order_id=order_data["order_id"],
        customer_name=order_data.get("customer_name"),
        description=order_data.get("description"),
        created_at=datetime.fromisoformat(order_data["created_at"]),
        updated_at=datetime.fromisoformat(order_data["updated_at"]),
        ctes=[convert_to_cte(cte) for cte in order_data.get("ctes", [])],
        bls=[convert_to_bl(bl) for bl in order_data.get("bls", [])],
        containers=[convert_to_container(c) for c in order_data.get("containers", [])],
        other_documents=[convert_to_document_file(doc) for doc in order_data.get("other_documents", [])]
    )

def convert_to_document_file(doc_data: dict) -> DocumentFile:
    return DocumentFile(
        file_name=doc_data["file_name"],
        s3_url=doc_data["s3_url"],
        file_type=doc_data["file_type"],
        size=doc_data["size"],
        uploaded_at=datetime.fromisoformat(doc_data["uploaded_at"]),
        text_content=doc_data.get("text_content"),
        indexed_at=datetime.fromisoformat(doc_data["indexed_at"]) if doc_data.get("indexed_at") else None
    )

# Funções de conversão para os modelos linkados (simplificado)
def convert_to_cte(data: dict) -> CTEDocument: return CTEDocument(**data)
def convert_to_bl(data: dict) -> BLDocument: return BLDocument(**data)
def convert_to_container(data: dict) -> Container: return Container(**data)

@strawberry.type
class CRUDQuery:
    """GraphQL Queries para as novas entidades de Order e Documentos."""
    
    @strawberry.field
    async def orders(self, customer_name: Optional[str] = None, limit: int = 10, skip: int = 0) -> List[Order]:
        params = f"?limit={limit}&skip={skip}"
        if customer_name:
            params += f"&customer_name={customer_name}"
        orders_data = await api_client.get(f"/orders{params}")
        return [convert_to_order(order) for order in orders_data]

    @strawberry.field
    async def order(self, order_id: str) -> Optional[Order]:
        try:
            order_data = await api_client.get(f"/orders/{order_id}")
            return convert_to_order(order_data)
        except:
            return None

@strawberry.type
class CRUDMutation:
    """GraphQL Mutations para as novas entidades."""

    @strawberry.field
    async def create_order(self, order_input: OrderInput) -> Order:
        data = order_input.__dict__
        order_data = await api_client.post("/orders", data)
        return convert_to_order(order_data)

    @strawberry.field
    async def add_document_to_order(self, order_id: str, file_input: DocumentFileInput) -> Order:
        data = file_input.__dict__
        order_data = await api_client.post(f"/orders/{order_id}/documents", data)
        return convert_to_order(order_data)

    @strawberry.field
    async def link_cte_to_order(self, order_id: str, cte_id: str) -> Order:
        order_data = await api_client.post(f"/orders/{order_id}/link_cte/{cte_id}", {})
        return convert_to_order(order_data)
