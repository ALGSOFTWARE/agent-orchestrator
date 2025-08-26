"""
Webhook Processor - Sistema de processamento de webhooks em tempo real

Este módulo fornece:
1. Servidor de webhooks para receber eventos externos
2. Processamento automático de atualizações logísticas
3. Integração com transportadoras e sistemas externos
4. Triggers para ações dos agentes CrewAI
5. Sistema de filas para processamento assíncrono

Integra com gatekeeper_api_tool para persistir atualizações.
"""

import asyncio
import logging
import json
import hashlib
import hmac
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from aiohttp import web, ClientSession
from asyncio import Queue
import signal
import sys

from .gatekeeper_api_tool import GatekeeperAPITool

logger = logging.getLogger("WebhookProcessor")


class WebhookType(str, Enum):
    """Tipos de webhook suportados"""
    TRACKING_UPDATE = "tracking_update"
    TRANSPORT_STATUS = "transport_status"
    DOCUMENT_UPLOAD = "document_upload"
    PAYMENT_STATUS = "payment_status"
    CONTAINER_EVENT = "container_event"
    CUSTOMS_CLEARANCE = "customs_clearance"
    DELIVERY_CONFIRMATION = "delivery_confirmation"
    EXCEPTION_ALERT = "exception_alert"


class WebhookSource(str, Enum):
    """Fontes de webhook"""
    TRANSPORTADORA = "transportadora"
    RECEITA_FEDERAL = "receita_federal"
    PORTO = "porto"
    GPS_TRACKER = "gps_tracker"
    EDI_SYSTEM = "edi_system"
    CUSTOMER_PORTAL = "customer_portal"
    INTERNAL_SYSTEM = "internal_system"


@dataclass
class WebhookEvent:
    """Evento de webhook padronizado"""
    id: str
    type: WebhookType
    source: WebhookSource
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None
    processed: bool = False
    retries: int = 0
    order_id: Optional[str] = None
    container_id: Optional[str] = None


@dataclass
class WebhookConfig:
    """Configuração de webhook por fonte"""
    source: WebhookSource
    endpoint_path: str
    secret_key: str
    signature_header: str
    signature_method: str  # sha256, sha1, md5
    enabled: bool = True
    rate_limit: int = 100  # requests per minute
    timeout: int = 30  # seconds


class WebhookProcessor:
    """
    Processador de webhooks em tempo real
    
    Funcionalidades:
    - Servidor HTTP para receber webhooks
    - Validação de assinaturas
    - Fila de processamento assíncrono
    - Retry automático para falhas
    - Rate limiting por fonte
    - Integração com Gatekeeper API
    """
    
    def __init__(
        self, 
        port: int = 8002,
        gatekeeper_api: Optional[GatekeeperAPITool] = None
    ):
        self.port = port
        self.gatekeeper_api = gatekeeper_api or GatekeeperAPITool()
        
        # Configurações de webhook por fonte
        self.webhook_configs = {
            WebhookSource.TRANSPORTADORA: WebhookConfig(
                source=WebhookSource.TRANSPORTADORA,
                endpoint_path="/webhooks/transportadora",
                secret_key="transport_secret_key",
                signature_header="X-Transport-Signature",
                signature_method="sha256"
            ),
            WebhookSource.GPS_TRACKER: WebhookConfig(
                source=WebhookSource.GPS_TRACKER,
                endpoint_path="/webhooks/gps",
                secret_key="gps_secret_key",
                signature_header="X-GPS-Signature",
                signature_method="sha256"
            ),
            WebhookSource.PORTO: WebhookConfig(
                source=WebhookSource.PORTO,
                endpoint_path="/webhooks/porto",
                secret_key="porto_secret_key",
                signature_header="X-Porto-Signature",
                signature_method="sha256"
            )
        }
        
        # Sistema de filas
        self.event_queue: Queue = Queue()
        self.processing_workers = 3
        self.worker_tasks = []
        
        # Rate limiting
        self.rate_limits = {}
        
        # Estatísticas
        self.stats = {
            "events_received": 0,
            "events_processed": 0,
            "events_failed": 0,
            "events_retried": 0
        }
        
        # Handlers personalizados
        self.event_handlers = {}
        
        # App web
        self.app = None
        self.runner = None
        self.site = None
        
        logger.info(f"🎣 WebhookProcessor initialized on port {port}")
    
    # === SERVIDOR HTTP ===
    
    async def start_server(self):
        """Inicia servidor de webhooks"""
        self.app = web.Application()
        
        # Registrar rotas para cada fonte
        for source, config in self.webhook_configs.items():
            if config.enabled:
                self.app.router.add_post(
                    config.endpoint_path, 
                    self._create_webhook_handler(source)
                )
        
        # Rotas de health e stats
        self.app.router.add_get("/health", self._health_handler)
        self.app.router.add_get("/stats", self._stats_handler)
        self.app.router.add_post("/webhooks/generic", self._generic_webhook_handler)
        
        # Iniciar workers de processamento
        for i in range(self.processing_workers):
            task = asyncio.create_task(self._process_events_worker(f"worker-{i}"))
            self.worker_tasks.append(task)
        
        # Iniciar servidor web
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "0.0.0.0", self.port)
        await self.site.start()
        
        logger.info(f"🚀 Webhook server started on http://0.0.0.0:{self.port}")
        
        # Registrar handlers de shutdown
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._shutdown_handler)
    
    def _create_webhook_handler(self, source: WebhookSource):
        """Cria handler para fonte específica"""
        async def webhook_handler(request):
            return await self._handle_webhook_request(request, source)
        return webhook_handler
    
    async def _handle_webhook_request(self, request: web.Request, source: WebhookSource) -> web.Response:
        """Handle genérico para webhooks"""
        config = self.webhook_configs[source]
        
        try:
            # Rate limiting
            if not self._check_rate_limit(source):
                return web.Response(
                    status=429, 
                    text="Rate limit exceeded",
                    headers={"Retry-After": "60"}
                )
            
            # Ler dados
            raw_data = await request.read()
            
            # Validar assinatura
            signature = request.headers.get(config.signature_header)
            if not self._validate_signature(raw_data, signature, config):
                logger.warning(f"❌ Invalid signature for {source}")
                return web.Response(status=401, text="Invalid signature")
            
            # Parse JSON
            try:
                data = json.loads(raw_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON from {source}: {e}")
                return web.Response(status=400, text="Invalid JSON")
            
            # Criar evento
            event = WebhookEvent(
                id=f"{source}_{datetime.now().timestamp()}_{hash(raw_data) % 10000}",
                type=self._detect_webhook_type(data, source),
                source=source,
                timestamp=datetime.now(),
                data=data,
                signature=signature
            )
            
            # Adicionar à fila
            await self.event_queue.put(event)
            self.stats["events_received"] += 1
            
            logger.info(f"✅ Webhook received: {source} - {event.type}")
            
            return web.Response(status=200, text="OK")
            
        except Exception as e:
            logger.error(f"❌ Webhook processing error: {e}")
            return web.Response(status=500, text="Internal server error")
    
    async def _generic_webhook_handler(self, request: web.Request) -> web.Response:
        """Handler genérico para webhooks não configurados"""
        try:
            data = await request.json()
            
            event = WebhookEvent(
                id=f"generic_{datetime.now().timestamp()}",
                type=WebhookType.TRACKING_UPDATE,  # Default
                source=WebhookSource.INTERNAL_SYSTEM,
                timestamp=datetime.now(),
                data=data
            )
            
            await self.event_queue.put(event)
            return web.Response(status=200, text="OK")
            
        except Exception as e:
            logger.error(f"Generic webhook error: {e}")
            return web.Response(status=500, text="Error")
    
    # === VALIDAÇÃO ===
    
    def _check_rate_limit(self, source: WebhookSource) -> bool:
        """Verifica rate limiting por fonte"""
        now = datetime.now()
        minute_key = f"{source}_{now.minute}"
        
        if minute_key not in self.rate_limits:
            self.rate_limits[minute_key] = 0
        
        config = self.webhook_configs[source]
        self.rate_limits[minute_key] += 1
        
        # Limpar dados antigos
        old_keys = [k for k in self.rate_limits.keys() 
                   if k.split('_')[-1] != str(now.minute)]
        for key in old_keys:
            del self.rate_limits[key]
        
        return self.rate_limits[minute_key] <= config.rate_limit
    
    def _validate_signature(self, payload: bytes, signature: str, config: WebhookConfig) -> bool:
        """Valida assinatura HMAC"""
        if not signature or not config.secret_key:
            return True  # Skip validation se não configurado
        
        try:
            # Remover prefixo (ex: "sha256=")
            if "=" in signature:
                method, sig_value = signature.split("=", 1)
            else:
                sig_value = signature
            
            # Gerar signature esperada
            if config.signature_method == "sha256":
                expected = hmac.new(
                    config.secret_key.encode(),
                    payload,
                    hashlib.sha256
                ).hexdigest()
            elif config.signature_method == "sha1":
                expected = hmac.new(
                    config.secret_key.encode(),
                    payload,
                    hashlib.sha1
                ).hexdigest()
            else:
                return False
            
            return hmac.compare_digest(expected, sig_value)
            
        except Exception as e:
            logger.error(f"Signature validation error: {e}")
            return False
    
    def _detect_webhook_type(self, data: Dict, source: WebhookSource) -> WebhookType:
        """Detecta tipo de webhook baseado no conteúdo"""
        # Lógica de detecção baseada na fonte e conteúdo
        if source == WebhookSource.GPS_TRACKER:
            return WebhookType.TRACKING_UPDATE
        elif source == WebhookSource.TRANSPORTADORA:
            if "status" in data:
                return WebhookType.TRANSPORT_STATUS
            elif "position" in data or "location" in data:
                return WebhookType.TRACKING_UPDATE
        elif source == WebhookSource.PORTO:
            return WebhookType.CONTAINER_EVENT
        
        # Detecção genérica
        data_str = json.dumps(data).lower()
        if any(word in data_str for word in ["position", "location", "lat", "lng"]):
            return WebhookType.TRACKING_UPDATE
        elif any(word in data_str for word in ["status", "state"]):
            return WebhookType.TRANSPORT_STATUS
        elif any(word in data_str for word in ["document", "file", "upload"]):
            return WebhookType.DOCUMENT_UPLOAD
        elif any(word in data_str for word in ["payment", "pagamento"]):
            return WebhookType.PAYMENT_STATUS
        else:
            return WebhookType.TRACKING_UPDATE  # Default
    
    # === PROCESSAMENTO ===
    
    async def _process_events_worker(self, worker_id: str):
        """Worker para processar eventos da fila"""
        logger.info(f"🔄 Worker {worker_id} started")
        
        while True:
            try:
                # Buscar evento da fila
                event = await self.event_queue.get()
                
                # Processar evento
                success = await self._process_event(event)
                
                if success:
                    self.stats["events_processed"] += 1
                    event.processed = True
                else:
                    self.stats["events_failed"] += 1
                    
                    # Retry lógic
                    if event.retries < 3:
                        event.retries += 1
                        self.stats["events_retried"] += 1
                        # Re-adicionar à fila após delay
                        await asyncio.sleep(2 ** event.retries)  # Backoff exponencial
                        await self.event_queue.put(event)
                        logger.info(f"🔄 Retrying event {event.id} (attempt {event.retries})")
                
                # Marcar tarefa como concluída
                self.event_queue.task_done()
                
            except asyncio.CancelledError:
                logger.info(f"🛑 Worker {worker_id} cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def _process_event(self, event: WebhookEvent) -> bool:
        """Processa um evento específico"""
        try:
            logger.info(f"📥 Processing {event.type} from {event.source}")
            
            # Processar baseado no tipo
            if event.type == WebhookType.TRACKING_UPDATE:
                return await self._process_tracking_update(event)
            elif event.type == WebhookType.TRANSPORT_STATUS:
                return await self._process_transport_status(event)
            elif event.type == WebhookType.CONTAINER_EVENT:
                return await self._process_container_event(event)
            elif event.type == WebhookType.DOCUMENT_UPLOAD:
                return await self._process_document_upload(event)
            elif event.type == WebhookType.DELIVERY_CONFIRMATION:
                return await self._process_delivery_confirmation(event)
            else:
                return await self._process_generic_event(event)
                
        except Exception as e:
            logger.error(f"❌ Event processing failed: {e}")
            return False
    
    async def _process_tracking_update(self, event: WebhookEvent) -> bool:
        """Processa atualização de rastreamento"""
        data = event.data
        
        # Extrair dados de posição
        lat = data.get("latitude") or data.get("lat")
        lng = data.get("longitude") or data.get("lng") or data.get("lon")
        timestamp_str = data.get("timestamp") or data.get("time")
        container_number = data.get("container") or data.get("container_number")
        
        if not all([lat, lng, container_number]):
            logger.warning(f"Missing required fields in tracking update: {data}")
            return False
        
        try:
            # Buscar container no sistema
            async with self.gatekeeper_api as api:
                container_response = await api.get_container_by_number(container_number)
                
                if not container_response.success:
                    logger.warning(f"Container not found: {container_number}")
                    return False
                
                container_id = container_response.data["containerByNumber"]["id"]
                
                # Atualizar posição
                update_response = await api.update_container_position(
                    container_id=container_id,
                    latitude=float(lat),
                    longitude=float(lng),
                    timestamp=datetime.fromisoformat(timestamp_str) if timestamp_str else None,
                    address=data.get("address")
                )
                
                if update_response.success:
                    # Criar evento de tracking
                    await api.create_tracking_event({
                        "order_id": container_response.data["containerByNumber"]["order"]["id"],
                        "event_type": "POSITION_UPDATE",
                        "timestamp": datetime.now().isoformat(),
                        "data": data
                    })
                    
                    logger.info(f"✅ Position updated for container {container_number}")
                    return True
                else:
                    logger.error(f"Failed to update position: {update_response.errors}")
                    return False
                
        except Exception as e:
            logger.error(f"Tracking update processing error: {e}")
            return False
    
    async def _process_transport_status(self, event: WebhookEvent) -> bool:
        """Processa mudança de status de transporte"""
        data = event.data
        
        tracking_code = data.get("tracking_code") or data.get("codigo_rastreamento")
        new_status = data.get("status") or data.get("estado")
        
        if not all([tracking_code, new_status]):
            return False
        
        try:
            async with self.gatekeeper_api as api:
                # Buscar Order por tracking code
                search_response = await api.search_orders({
                    "tracking_code": tracking_code
                })
                
                if search_response.success and search_response.data.get("searchOrders", {}).get("orders"):
                    order = search_response.data["searchOrders"]["orders"][0]
                    order_id = order["id"]
                    
                    # Atualizar status da Order
                    await api.update_order(order_id, {"status": new_status})
                    
                    # Criar evento
                    await api.create_tracking_event({
                        "order_id": order_id,
                        "event_type": "STATUS_CHANGE",
                        "timestamp": datetime.now().isoformat(),
                        "data": data
                    })
                    
                    logger.info(f"✅ Status updated for order {order_id}: {new_status}")
                    return True
                
        except Exception as e:
            logger.error(f"Transport status processing error: {e}")
        
        return False
    
    async def _process_container_event(self, event: WebhookEvent) -> bool:
        """Processa evento de container no porto"""
        # Implementação específica para eventos portuários
        return True
    
    async def _process_document_upload(self, event: WebhookEvent) -> bool:
        """Processa upload de documento"""
        # Implementação para processar novos documentos
        return True
    
    async def _process_delivery_confirmation(self, event: WebhookEvent) -> bool:
        """Processa confirmação de entrega"""
        # Implementação para confirmações de entrega
        return True
    
    async def _process_generic_event(self, event: WebhookEvent) -> bool:
        """Processa evento genérico"""
        # Handler personalizado se registrado
        if event.type in self.event_handlers:
            handler = self.event_handlers[event.type]
            return await handler(event)
        
        # Log do evento para análise
        logger.info(f"📋 Generic event logged: {event.type} - {event.data}")
        return True
    
    # === HEALTH & STATS ===
    
    async def _health_handler(self, request: web.Request) -> web.Response:
        """Endpoint de health check"""
        health_data = {
            "status": "healthy",
            "service": "webhook-processor",
            "timestamp": datetime.now().isoformat(),
            "queue_size": self.event_queue.qsize(),
            "workers_active": len([t for t in self.worker_tasks if not t.done()]),
            "stats": self.stats
        }
        return web.json_response(health_data)
    
    async def _stats_handler(self, request: web.Request) -> web.Response:
        """Endpoint de estatísticas"""
        return web.json_response({
            "stats": self.stats,
            "queue_size": self.event_queue.qsize(),
            "rate_limits": self.rate_limits,
            "configured_sources": [s.value for s in self.webhook_configs.keys()],
            "worker_status": [
                {"id": f"worker-{i}", "done": task.done(), "cancelled": task.cancelled()}
                for i, task in enumerate(self.worker_tasks)
            ]
        })
    
    # === CUSTOM HANDLERS ===
    
    def register_event_handler(self, event_type: WebhookType, handler: Callable):
        """Registra handler personalizado para tipo de evento"""
        self.event_handlers[event_type] = handler
        logger.info(f"🔧 Registered custom handler for {event_type}")
    
    # === SHUTDOWN ===
    
    def _shutdown_handler(self, signum, frame):
        """Handler para shutdown graceful"""
        logger.info("🛑 Shutdown signal received")
        asyncio.create_task(self.shutdown())
    
    async def shutdown(self):
        """Shutdown graceful do servidor"""
        logger.info("🛑 Shutting down webhook processor...")
        
        # Cancelar workers
        for task in self.worker_tasks:
            task.cancel()
        
        # Esperar workers terminarem
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        # Parar servidor web
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        
        logger.info("✅ Webhook processor shutdown complete")


# === CREWAI INTEGRATION ===

class CrewAIWebhookTool:
    """Wrapper para integração com CrewAI agents"""
    
    def __init__(self):
        self.processor = None
    
    def start_webhook_server(self, port: int = 8002) -> str:
        """Inicia servidor de webhooks"""
        try:
            self.processor = WebhookProcessor(port=port)
            
            # Executar em background
            loop = asyncio.get_event_loop()
            loop.create_task(self.processor.start_server())
            
            return f"✅ Servidor de webhooks iniciado na porta {port}"
        except Exception as e:
            return f"❌ Erro ao iniciar servidor: {e}"
    
    def get_webhook_stats(self) -> str:
        """Retorna estatísticas dos webhooks"""
        if not self.processor:
            return "❌ Servidor de webhooks não iniciado"
        
        stats = self.processor.stats
        return f"""📊 Estatísticas de Webhooks:
- Eventos recebidos: {stats['events_received']}
- Eventos processados: {stats['events_processed']}
- Eventos falharam: {stats['events_failed']}
- Tentativas de retry: {stats['events_retried']}
- Fila atual: {self.processor.event_queue.qsize()} eventos
"""


# Instância global
webhook_tool = CrewAIWebhookTool()

def iniciar_servidor_webhooks(porta: int = 8002) -> str:
    return webhook_tool.start_webhook_server(porta)

def obter_stats_webhooks() -> str:
    return webhook_tool.get_webhook_stats()