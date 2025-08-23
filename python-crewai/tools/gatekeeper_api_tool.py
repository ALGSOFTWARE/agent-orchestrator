"""
Gatekeeper API Tool - Cliente GraphQL/REST completo para agentes CrewAI

Esta ferramenta permite aos agentes:
1. Fazer consultas GraphQL/REST no Gatekeeper API
2. CRUD completo em Orders, DocumentFiles, CTEs, etc
3. Processamento de documentos e OCR
4. Integração com sistemas externos via webhooks
5. Operações em tempo real

Substitui o banco mockado por dados reais do sistema.
"""

import aiohttp
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("GatekeeperAPITool")


class APIEndpoint(str, Enum):
    """Endpoints disponíveis no Gatekeeper API"""
    GRAPHQL = "/graphql"
    ORDERS = "/orders"
    FILES = "/files"
    CONTEXT = "/context"
    AUTH = "/auth"
    HEALTH = "/health"


@dataclass
class APIResponse:
    """Resposta padronizada da API"""
    success: bool
    data: Any
    errors: Optional[List[str]] = None
    status_code: Optional[int] = None
    response_time: Optional[float] = None


class GatekeeperAPITool:
    """
    Cliente completo para Gatekeeper API
    
    Permite aos agentes CrewAI acessar dados reais do sistema
    através de GraphQL e REST endpoints.
    """
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.session = None
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CrewAI-Agent/1.0"
        }
        
        # Cache para esquemas e metadados
        self._schema_cache = {}
        self._stats = {
            "requests": 0,
            "errors": 0,
            "cache_hits": 0
        }
        
        logger.info("🔗 GatekeeperAPITool initialized")
    
    async def __aenter__(self):
        """Async context manager - entrada"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager - saída"""
        if self.session:
            await self.session.close()
    
    # === CORE HTTP METHODS ===
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> APIResponse:
        """Faz requisição HTTP genérica"""
        start_time = datetime.now()
        
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers
            )
        
        # Corrigir concatenação de URL
        if endpoint.startswith('/'):
            url = f"{self.base_url}{endpoint}"
        else:
            url = f"{self.base_url}/{endpoint}"
        self._stats["requests"] += 1
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                response_data = await response.json()
                response_time = (datetime.now() - start_time).total_seconds()
                
                if response.status >= 400:
                    self._stats["errors"] += 1
                    return APIResponse(
                        success=False,
                        data=None,
                        errors=[f"HTTP {response.status}: {response_data}"],
                        status_code=response.status,
                        response_time=response_time
                    )
                
                return APIResponse(
                    success=True,
                    data=response_data,
                    status_code=response.status,
                    response_time=response_time
                )
                
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Request failed: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                response_time=(datetime.now() - start_time).total_seconds()
            )
    
    # === GRAPHQL OPERATIONS ===
    
    async def execute_graphql(
        self, 
        query: str, 
        variables: Optional[Dict] = None,
        operation_name: Optional[str] = None
    ) -> APIResponse:
        """
        Executa qualquer query ou mutation GraphQL
        
        Args:
            query: Query ou mutation GraphQL
            variables: Variáveis para a query
            operation_name: Nome da operação (opcional)
        
        Returns:
            APIResponse com o resultado
        """
        payload = {
            "query": query,
            "variables": variables or {},
        }
        
        if operation_name:
            payload["operationName"] = operation_name
        
        logger.info(f"🔍 Executing GraphQL: {operation_name or 'unnamed'}")
        
        return await self._make_request("POST", APIEndpoint.GRAPHQL, payload)
    
    # === ORDER OPERATIONS ===
    
    async def get_order_by_id(self, order_id: str) -> APIResponse:
        """Busca Order por ID"""
        query = """
        query GetOrderById($id: ID!) {
            order(id: $id) {
                id
                order_id
                customer_name
                description
                created_at
                updated_at
                other_documents {
                    file_name
                    s3_url
                    file_type
                    size
                    text_content
                    uploaded_at
                }
            }
        }
        """
        return await self.execute_graphql(query, {"id": order_id}, "GetOrderById")
    
    async def search_orders(
        self, 
        filters: Optional[Dict] = None,
        limit: int = 50,
        offset: int = 0
    ) -> APIResponse:
        """
        Busca Orders com filtros avançados
        
        Args:
            filters: Filtros de busca (customer_name, date_range, etc)
            limit: Número máximo de resultados
            offset: Paginação
        """
        query = """
        query SearchOrders($filters: OrderFilters, $limit: Int, $offset: Int) {
            searchOrders(filters: $filters, limit: $limit, offset: $offset) {
                total
                orders {
                    id
                    order_id
                    customer_name
                    description
                    created_at
                    updated_at
                    other_documents {
                        file_name
                        file_type
                        text_content
                        uploaded_at
                    }
                }
            }
        }
        """
        variables = {
            "filters": filters or {},
            "limit": limit,
            "offset": offset
        }
        return await self.execute_graphql(query, variables, "SearchOrders")
    
    async def create_order(self, order_data: Dict) -> APIResponse:
        """
        Cria nova Order
        
        Args:
            order_data: Dados da Order (customer_name, description, etc)
        """
        mutation = """
        mutation CreateOrder($input: OrderInput!) {
            createOrder(input: $input) {
                id
                order_id
                customer_name
                description
                created_at
            }
        }
        """
        return await self.execute_graphql(mutation, {"input": order_data}, "CreateOrder")
    
    async def update_order(self, order_id: str, updates: Dict) -> APIResponse:
        """Atualiza Order existente"""
        mutation = """
        mutation UpdateOrder($id: ID!, $input: OrderUpdateInput!) {
            updateOrder(id: $id, input: $input) {
                id
                order_id
                customer_name
                description
                updated_at
            }
        }
        """
        variables = {"id": order_id, "input": updates}
        return await self.execute_graphql(mutation, variables, "UpdateOrder")
    
    # === DOCUMENT OPERATIONS ===
    
    async def get_order_documents(self, order_id: str) -> APIResponse:
        """Busca todos os documentos de uma Order"""
        query = """
        query GetOrderDocuments($orderId: ID!) {
            order(id: $orderId) {
                id
                other_documents {
                    file_name
                    s3_url
                    file_type
                    size
                    text_content
                    uploaded_at
                    indexed_at
                }
            }
        }
        """
        return await self.execute_graphql(query, {"orderId": order_id}, "GetOrderDocuments")
    
    async def upload_document(
        self, 
        order_id: str, 
        file_data: bytes, 
        file_name: str,
        file_type: str = "application/pdf"
    ) -> APIResponse:
        """
        Upload de documento para uma Order
        
        Note: Esta operação usa REST endpoint para upload de arquivo
        """
        # Primeiro faz upload do arquivo
        upload_response = await self._make_request(
            "POST", 
            f"{APIEndpoint.FILES}/upload", 
            data={
                "order_id": order_id,
                "file_name": file_name,
                "file_type": file_type
                # file_data seria enviado como multipart/form-data
            }
        )
        
        if not upload_response.success:
            return upload_response
        
        # Depois registra no GraphQL
        mutation = """
        mutation AddDocumentToOrder($orderId: ID!, $document: DocumentFileInput!) {
            addDocumentToOrder(orderId: $orderId, document: $document) {
                id
                other_documents {
                    file_name
                    s3_url
                    file_type
                }
            }
        }
        """
        document_data = {
            "file_name": file_name,
            "s3_url": upload_response.data.get("s3_url"),
            "file_type": file_type,
            "size": len(file_data)
        }
        
        return await self.execute_graphql(
            mutation, 
            {"orderId": order_id, "document": document_data},
            "AddDocumentToOrder"
        )
    
    # === SEMANTIC SEARCH ===
    
    async def semantic_search_documents(
        self, 
        query_text: str,
        order_filters: Optional[Dict] = None,
        limit: int = 10
    ) -> APIResponse:
        """
        Busca semântica nos documentos usando embeddings
        
        Args:
            query_text: Texto de busca
            order_filters: Filtros adicionais nas Orders
            limit: Número de resultados
        """
        search_query = """
        query SemanticSearch($text: String!, $filters: OrderFilters, $limit: Int) {
            semanticSearchDocuments(text: $text, filters: $filters, limit: $limit) {
                total
                results {
                    order {
                        id
                        order_id
                        customer_name
                    }
                    document {
                        file_name
                        text_content
                    }
                    similarity_score
                    matched_fragments
                }
            }
        }
        """
        variables = {
            "text": query_text,
            "filters": order_filters,
            "limit": limit
        }
        return await self.execute_graphql(search_query, variables, "SemanticSearch")
    
    # === CTE OPERATIONS ===
    
    async def get_cte_by_number(self, cte_number: str) -> APIResponse:
        """Busca CT-e por número"""
        query = """
        query GetCteByNumber($number: String!) {
            cteByNumber(number: $number) {
                id
                cte_number
                issuer_name
                recipient_name
                origin_city
                destination_city
                status
                created_at
                order {
                    id
                    order_id
                    customer_name
                }
            }
        }
        """
        return await self.execute_graphql(query, {"number": cte_number}, "GetCteByNumber")
    
    async def create_cte(self, cte_data: Dict, order_id: Optional[str] = None) -> APIResponse:
        """Cria novo CT-e"""
        mutation = """
        mutation CreateCte($input: CteInput!, $orderId: ID) {
            createCte(input: $input, orderId: $orderId) {
                id
                cte_number
                status
                created_at
            }
        }
        """
        variables = {"input": cte_data}
        if order_id:
            variables["orderId"] = order_id
            
        return await self.execute_graphql(mutation, variables, "CreateCte")
    
    # === CONTAINER OPERATIONS ===
    
    async def get_container_by_number(self, container_number: str) -> APIResponse:
        """Busca Container por número"""
        query = """
        query GetContainerByNumber($number: String!) {
            containerByNumber(number: $number) {
                id
                container_number
                container_type
                current_position {
                    latitude
                    longitude
                    timestamp
                    address
                }
                status
                last_updated
                order {
                    id
                    order_id
                }
            }
        }
        """
        return await self.execute_graphql(query, {"number": container_number}, "GetContainerByNumber")
    
    async def update_container_position(
        self, 
        container_id: str, 
        latitude: float, 
        longitude: float,
        timestamp: Optional[datetime] = None,
        address: Optional[str] = None
    ) -> APIResponse:
        """Atualiza posição de Container"""
        mutation = """
        mutation UpdateContainerPosition($id: ID!, $position: PositionInput!) {
            updateContainerPosition(id: $id, position: $position) {
                id
                container_number
                current_position {
                    latitude
                    longitude
                    timestamp
                    address
                }
                last_updated
            }
        }
        """
        position_data = {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": (timestamp or datetime.now()).isoformat(),
        }
        if address:
            position_data["address"] = address
        
        variables = {"id": container_id, "position": position_data}
        return await self.execute_graphql(mutation, variables, "UpdateContainerPosition")
    
    # === TRACKING EVENTS ===
    
    async def create_tracking_event(self, event_data: Dict) -> APIResponse:
        """Cria evento de rastreamento"""
        mutation = """
        mutation CreateTrackingEvent($input: TrackingEventInput!) {
            createTrackingEvent(input: $input) {
                id
                order_id
                event_type
                timestamp
                data
            }
        }
        """
        return await self.execute_graphql(mutation, {"input": event_data}, "CreateTrackingEvent")
    
    # === HEALTH & STATS ===
    
    async def health_check(self) -> APIResponse:
        """Verifica saúde do Gatekeeper API"""
        return await self._make_request("GET", APIEndpoint.HEALTH)
    
    async def get_api_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso da ferramenta"""
        health = await self.health_check()
        return {
            "tool_stats": self._stats,
            "api_health": health.success,
            "api_response_time": health.response_time,
            "cache_size": len(self._schema_cache)
        }
    
    # === UTILITY METHODS ===
    
    def clear_cache(self):
        """Limpa cache interno"""
        self._schema_cache.clear()
        logger.info("🗑️ Cache cleared")
    
    async def introspect_schema(self) -> APIResponse:
        """Faz introspection do schema GraphQL"""
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                types {
                    name
                    kind
                    description
                }
            }
        }
        """
        return await self.execute_graphql(introspection_query, operation_name="IntrospectionQuery")


# === CREWAI TOOL WRAPPER ===

class CrewAIGatekeeperTool:
    """
    Wrapper para usar GatekeeperAPITool com CrewAI agents
    Fornece métodos síncronos e formatação de respostas
    """
    
    def __init__(self):
        self.api_tool = GatekeeperAPITool()
    
    def _run_async(self, coro):
        """Executa corrotina assíncrona de forma síncrona"""
        try:
            # Verifica se já existe um loop rodando
            loop = asyncio.get_running_loop()
            # Se existe, usa asyncio.run_coroutine_threadsafe
            import concurrent.futures
            import threading
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
                
        except RuntimeError:
            # Não há loop rodando, pode usar run_until_complete
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(coro)
    
    def _format_response(self, response: APIResponse) -> str:
        """Formata resposta para consumo pelos agentes"""
        if not response.success:
            return f"❌ Erro na consulta: {', '.join(response.errors or ['Erro desconhecido'])}"
        
        if not response.data:
            return "ℹ️ Consulta executada com sucesso, mas sem dados retornados."
        
        # Formatação básica dos dados
        try:
            return f"✅ Consulta executada com sucesso:\n{json.dumps(response.data, indent=2, ensure_ascii=False, default=str)}"
        except Exception as e:
            return f"✅ Consulta executada com sucesso (erro na formatação: {e})"
    
    # Métodos síncronos para CrewAI
    
    def consultar_order(self, order_id: str) -> str:
        """Consulta Order por ID - método síncrono para agents"""
        async def _query():
            async with self.api_tool as api:
                return await api.get_order_by_id(order_id)
        
        response = self._run_async(_query())
        return self._format_response(response)
    
    def buscar_orders(self, customer_name: str = None, limit: int = 10) -> str:
        """Busca Orders - método síncrono para agents"""
        filters = {}
        if customer_name:
            filters["customer_name"] = customer_name
        
        async def _query():
            async with self.api_tool as api:
                return await api.search_orders(filters, limit=limit)
        
        response = self._run_async(_query())
        return self._format_response(response)
    
    def consultar_cte(self, numero_cte: str) -> str:
        """Consulta CT-e por número - método síncrono para agents"""
        async def _query():
            async with self.api_tool as api:
                return await api.get_cte_by_number(numero_cte)
        
        response = self._run_async(_query())
        return self._format_response(response)
    
    def consultar_container(self, numero_container: str) -> str:
        """Consulta Container por número - método síncrono para agents"""
        async def _query():
            async with self.api_tool as api:
                return await api.get_container_by_number(numero_container)
        
        response = self._run_async(_query())
        return self._format_response(response)
    
    def busca_semantica(self, texto_busca: str, limit: int = 5) -> str:
        """Busca semântica em documentos - método síncrono para agents"""
        async def _query():
            async with self.api_tool as api:
                return await api.semantic_search_documents(texto_busca, limit=limit)
        
        response = self._run_async(_query())
        return self._format_response(response)
    
    def verificar_saude_sistema(self) -> str:
        """Verifica saúde do sistema - método síncrono para agents"""
        async def _query():
            async with self.api_tool as api:
                return await api.health_check()
        
        response = self._run_async(_query())
        return self._format_response(response)


# Instância global para uso pelos agents
gatekeeper_tool = CrewAIGatekeeperTool()

# Funções de conveniência para importação
def consultar_order(order_id: str) -> str:
    return gatekeeper_tool.consultar_order(order_id)

def buscar_orders(customer_name: str = None, limit: int = 10) -> str:
    return gatekeeper_tool.buscar_orders(customer_name, limit)

def consultar_cte(numero_cte: str) -> str:
    return gatekeeper_tool.consultar_cte(numero_cte)

def consultar_container(numero_container: str) -> str:
    return gatekeeper_tool.consultar_container(numero_container)

def busca_semantica(texto_busca: str, limit: int = 5) -> str:
    return gatekeeper_tool.busca_semantica(texto_busca, limit)

def verificar_saude_sistema() -> str:
    return gatekeeper_tool.verificar_saude_sistema()