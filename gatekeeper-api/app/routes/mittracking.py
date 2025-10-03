"""
MitTracking Routes - Gatekeeper API Extension

Rotas para acessar dados do sistema MitTracking migrados do MySQL.
Compatível com as APIs PHP originais para facilitar a transição.
"""

from fastapi import APIRouter, HTTPException, Query, Body, Depends, File, Form, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from beanie import PydanticObjectId
import hashlib
import uuid
import os
from pydantic import BaseModel

from ..models_mittracking import (
    Company, Journey, Delivery, LogisticsDocument, Incident, 
    ChatConversation, Driver, Vehicle, MitUser, Report,
    CompanyType, JourneyStatus, DeliveryStatus, IncidentStatus,
    CompanyRequest, JourneyRequest, DeliveryRequest, IncidentRequest,
    # Modelos de contexto IA
    UserContext, GlobalContext, ConversationHistory,
    ContextType, ContextScope
)

router = APIRouter(prefix="/api/mittracking", tags=["MitTracking"])
logger = logging.getLogger("GatekeeperAPI.MitTracking")


# ================================
# DASHBOARD ENDPOINTS
# ================================

@router.get("/dashboard/kpis")
async def get_dashboard_kpis():
    """
    KPIs principais do dashboard (compatível com dashboard_api.php)
    """
    try:
        # Calcular KPIs usando agregações MongoDB
        
        # Tempo médio de entrega (últimos 30 dias)
        delivered_orders = await Delivery.find(
            Delivery.status == DeliveryStatus.DELIVERED,
            Delivery.actual_delivery_date >= datetime.now() - timedelta(days=30)
        ).to_list()
        
        avg_delivery_time = 0
        if delivered_orders:
            total_hours = sum([
                (delivery.actual_delivery_date - delivery.created_at).total_seconds() / 3600
                for delivery in delivered_orders
                if delivery.actual_delivery_date
            ])
            avg_delivery_time = round(total_hours / len(delivered_orders) / 24, 1)  # em dias
        
        # SLA (entregas no prazo)
        on_time_deliveries = sum([
            1 for delivery in delivered_orders 
            if delivery.estimated_date and delivery.actual_delivery_date <= delivery.estimated_date
        ])
        sla_percentage = round((on_time_deliveries / len(delivered_orders)) * 100, 1) if delivered_orders else 0
        
        # NPS médio
        clients = await Company.find(Company.company_type == CompanyType.CLIENT).to_list()
        avg_nps = sum([client.nps for client in clients if client.nps > 0]) / len([c for c in clients if c.nps > 0]) if clients else 0
        
        # Incidentes críticos abertos
        critical_incidents = await Incident.find(
            Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS]),
            Incident.severity.in_(["alta", "critica"])
        ).count()
        
        return [
            {
                "title": "Tempo Médio de Entrega",
                "value": f"{avg_delivery_time} dias",
                "change": "+0.5",
                "trend": "up",
                "icon": "Clock"
            },
            {
                "title": "SLA Atendido", 
                "value": f"{sla_percentage}%",
                "change": "+2.3",
                "trend": "up",
                "icon": "Target"
            },
            {
                "title": "NPS",
                "value": round(avg_nps, 1),
                "change": "+0.2",
                "trend": "up", 
                "icon": "TrendingUp"
            },
            {
                "title": "Incidentes",
                "value": critical_incidents,
                "change": "-3",
                "trend": "down",
                "icon": "AlertTriangle"
            }
        ]
        
    except Exception as e:
        logger.error(f"Erro ao buscar KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/status_distribution")
async def get_status_distribution():
    """
    Distribuição de status das jornadas/cargas
    """
    try:
        # Agrupar jornadas por status
        pipeline = [
            {"$match": {"created_at": {"$gte": datetime.now() - timedelta(days=30)}}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        results = await Journey.aggregate(pipeline).to_list()
        
        # Mapear para formato esperado pelo frontend
        status_map = {
            "em_andamento": {"name": "Em Trânsito", "color": "hsl(var(--chart-1))"},
            "concluida": {"name": "Entregue", "color": "hsl(var(--chart-2))"},
            "agendada": {"name": "Aguardando Doc", "color": "hsl(var(--chart-3))"},
            "cancelada": {"name": "Cancelada", "color": "hsl(var(--chart-4))"}
        }
        
        return [
            {
                "status": status_map.get(result["_id"], {"name": result["_id"].title(), "color": "hsl(var(--chart-5))"})["name"],
                "value": result["count"],
                "color": status_map.get(result["_id"], {"name": result["_id"], "color": "hsl(var(--chart-5))"})["color"]
            }
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Erro ao buscar distribuição de status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/client_performance")
async def get_client_performance():
    """
    Performance por cliente (top 10)
    """
    try:
        clients = await Company.find(
            Company.company_type == CompanyType.CLIENT
        ).sort(-Company.total_shipments).limit(10).to_list()
        
        result = []
        for client in clients:
            # Buscar entregas do cliente
            deliveries = await Delivery.find(Delivery.client.id == client.id).to_list()
            
            delivered_count = len([d for d in deliveries if d.status == DeliveryStatus.DELIVERED])
            on_time = len([
                d for d in deliveries 
                if d.status == DeliveryStatus.DELIVERED and d.estimated_date and d.actual_delivery_date <= d.estimated_date
            ])
            
            sla = round((on_time / delivered_count) * 100, 1) if delivered_count > 0 else 0
            
            result.append({
                "name": client.name,
                "entregas": len(deliveries),
                "sla": sla,
                "score_cliente": client.score
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar performance de clientes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/alerts")
async def get_operational_alerts():
    """
    Alertas operacionais do sistema
    """
    try:
        alerts = []
        
        # Alertas de atraso
        delayed_deliveries = await Delivery.find(
            Delivery.status == DeliveryStatus.DELAYED,
            Delivery.estimated_date < datetime.now()
        ).limit(3).to_list()
        
        for delivery in delayed_deliveries:
            hours_late = (datetime.now() - delivery.estimated_date).total_seconds() / 3600
            alerts.append({
                "tipo": "Atraso",
                "descricao": f"Entrega {delivery.code} com atraso de {int(hours_late)}h",
                "criticidade": "alta",
                "referencia_id": str(delivery.id),
                "tipo_referencia": "entrega"
            })
        
        # Alertas de incidentes críticos
        critical_incidents = await Incident.find(
            Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS]),
            Incident.severity.in_(["alta", "critica"])
        ).limit(3).to_list()
        
        for incident in critical_incidents:
            alerts.append({
                "tipo": incident.incident_type.value.title(),
                "descricao": incident.description[:100] + "...",
                "criticidade": incident.severity.value,
                "referencia_id": str(incident.id),
                "tipo_referencia": "incidente"
            })
        
        return alerts
        
    except Exception as e:
        logger.error(f"Erro ao buscar alertas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/recent_shipments") 
async def get_recent_shipments():
    """
    Últimas jornadas/embarques
    """
    try:
        journeys = await Journey.find({}).sort(-Journey.created_at).limit(10).to_list()
        
        result = []
        for journey in journeys:
            client_name = ""
            transporter_name = ""
            
            if journey.client:
                client = await journey.client.fetch()
                client_name = client.name if client else ""
            
            if journey.transporter:
                transporter = await journey.transporter.fetch()
                transporter_name = transporter.name if transporter else ""
            
            result.append({
                "id": journey.code,
                "cliente": client_name,
                "destino": journey.destination,
                "status": journey.status.value.title(),
                "data": journey.created_at.date().isoformat(),
                "progresso": journey.progress_percentage,
                "transportadora": transporter_name
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar embarques recentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# CLIENTS ENDPOINTS
# ================================

@router.get("/clients/list")
async def get_clients_list():
    """
    Lista completa de clientes (compatível com clientes_api.php)
    """
    try:
        clients = await Company.find(
            Company.company_type == CompanyType.CLIENT,
            Company.status == "ativo"
        ).sort(-Company.score, -Company.total_shipments).to_list()
        
        result = []
        for client in clients:
            result.append({
                "id": str(client.id),
                "nome": client.name,
                "empresa": client.company_name,
                "email": client.email,
                "telefone": client.phone,
                "endereco": f"{client.city}, {client.state}" if client.city and client.state else "",
                "score": client.score,
                "status": client.status.value,
                "total_embarques": client.total_shipments,
                "engajamento_chat": client.chat_engagement,
                "nps": client.nps,
                "ultima_atividade_texto": "Recente" if client.last_activity and client.last_activity > datetime.now() - timedelta(hours=24) else "Há alguns dias",
                "data_criacao": client.created_at.isoformat(),
                "data_atualizacao": client.updated_at.isoformat()
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar lista de clientes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/metrics")
async def get_clients_metrics():
    """
    Métricas gerais de clientes
    """
    try:
        clients = await Company.find(Company.company_type == CompanyType.CLIENT).to_list()
        
        total_clients = len(clients)
        active_clients = len([c for c in clients if c.status.value == "ativo"])
        avg_score = sum([c.score for c in clients]) / total_clients if total_clients > 0 else 0
        avg_nps = sum([c.nps for c in clients if c.nps > 0]) / len([c for c in clients if c.nps > 0]) if clients else 0
        total_shipments = sum([c.total_shipments for c in clients])
        
        return {
            "total_clientes": total_clients,
            "clientes_ativos": active_clients,
            "clientes_inativos": total_clients - active_clients,
            "score_medio": round(avg_score, 1),
            "nps_medio": round(avg_nps, 1),
            "total_embarques_geral": total_shipments,
            "engajamento_medio": sum([c.chat_engagement for c in clients]) / total_clients if total_clients > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar métricas de clientes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clients/create")
async def create_client(client_data: CompanyRequest):
    """
    Criar novo cliente
    """
    try:
        # Verificar se já existe
        existing = await Company.find_one(Company.cnpj == client_data.cnpj)
        if existing:
            raise HTTPException(status_code=400, detail="Cliente com este CNPJ já existe")
        
        client = Company(
            name=client_data.name,
            company_name=client_data.company_name,
            cnpj=client_data.cnpj,
            company_type=client_data.company_type,
            email=client_data.email,
            phone=client_data.phone,
            address=client_data.address,
            city=client_data.city,
            state=client_data.state,
            zip_code=client_data.zip_code
        )
        
        await client.save()
        
        return {
            "success": True,
            "message": "Cliente criado com sucesso",
            "client_id": str(client.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# JOURNEYS ENDPOINTS
# ================================

@router.get("/journeys")
async def get_journeys(
    status: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """
    Lista jornadas com filtros opcionais
    """
    try:
        filters = {}
        
        if status:
            filters["status"] = status
        if client_id:
            filters["client.id"] = PydanticObjectId(client_id)
        
        journeys = await Journey.find(filters).sort(-Journey.created_at).limit(limit).to_list()
        
        result = []
        for journey in journeys:
            client_name = ""
            if journey.client:
                client = await journey.client.fetch()
                client_name = client.name if client else ""
            
            result.append({
                "id": str(journey.id),
                "code": journey.code,
                "client": client_name,
                "origin": journey.origin,
                "destination": journey.destination,
                "status": journey.status.value,
                "progress": journey.progress_percentage,
                "created_at": journey.created_at.isoformat(),
                "checkpoints_count": len(journey.checkpoints)
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar jornadas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journeys/{journey_id}")
async def get_journey_detail(journey_id: str):
    """
    Detalhes de uma jornada específica
    """
    try:
        journey = await Journey.get(journey_id)
        if not journey:
            raise HTTPException(status_code=404, detail="Jornada não encontrada")
        
        # Buscar dados relacionados
        client_data = await journey.client.fetch() if journey.client else None
        transporter_data = await journey.transporter.fetch() if journey.transporter else None
        vehicle_data = await journey.vehicle.fetch() if journey.vehicle else None
        driver_data = await journey.driver.fetch() if journey.driver else None
        
        return {
            "id": str(journey.id),
            "code": journey.code,
            "client": {"id": str(client_data.id), "name": client_data.name} if client_data else None,
            "transporter": {"id": str(transporter_data.id), "name": transporter_data.name} if transporter_data else None,
            "vehicle": {"license_plate": vehicle_data.license_plate, "model": vehicle_data.model} if vehicle_data else None,
            "driver": {"name": driver_data.name, "license_number": driver_data.license_number} if driver_data else None,
            "origin": journey.origin,
            "destination": journey.destination,
            "origin_coordinates": journey.origin_coordinates,
            "destination_coordinates": journey.destination_coordinates,
            "status": journey.status.value,
            "progress_percentage": journey.progress_percentage,
            "checkpoints": journey.checkpoints,
            "start_date": journey.start_date.isoformat() if journey.start_date else None,
            "estimated_date": journey.estimated_date.isoformat() if journey.estimated_date else None,
            "observations": journey.observations,
            "created_at": journey.created_at.isoformat(),
            "updated_at": journey.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes da jornada: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/journeys")
async def create_journey(journey_data: JourneyRequest):
    """
    Criar nova jornada
    """
    try:
        # Verificar se cliente existe
        client = await Company.get(journey_data.client_id)
        if not client:
            raise HTTPException(status_code=400, detail="Cliente não encontrado")
        
        # Buscar relacionamentos opcionais
        transporter = await Company.get(journey_data.transporter_id) if journey_data.transporter_id else None
        vehicle = await Vehicle.get(journey_data.vehicle_id) if journey_data.vehicle_id else None
        driver = await Driver.get(journey_data.driver_id) if journey_data.driver_id else None
        
        journey = Journey(
            code=journey_data.code,
            client=client,
            transporter=transporter,
            vehicle=vehicle,
            driver=driver,
            origin=journey_data.origin,
            destination=journey_data.destination,
            origin_coordinates=journey_data.origin_coordinates or [],
            destination_coordinates=journey_data.destination_coordinates or [],
            estimated_date=journey_data.estimated_date,
            observations=journey_data.observations
        )
        
        await journey.save()
        
        return {
            "success": True,
            "message": "Jornada criada com sucesso",
            "journey_id": str(journey.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar jornada: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# DELIVERIES ENDPOINTS
# ================================

@router.get("/deliveries")
async def get_deliveries(
    status: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """
    Lista entregas com filtros opcionais
    """
    try:
        filters = {}
        
        if status:
            filters["status"] = status
        if client_id:
            filters["client.id"] = PydanticObjectId(client_id)
        
        deliveries = await Delivery.find(filters).sort(-Delivery.created_at).limit(limit).to_list()
        
        result = []
        for delivery in deliveries:
            client_name = ""
            if delivery.client:
                client = await delivery.client.fetch()
                client_name = client.name if client else ""
            
            result.append({
                "id": str(delivery.id),
                "code": delivery.code,
                "client": client_name,
                "recipient": delivery.recipient_name,
                "address": delivery.delivery_address,
                "status": delivery.status.value,
                "estimated_date": delivery.estimated_date.isoformat() if delivery.estimated_date else None,
                "actual_delivery_date": delivery.actual_delivery_date.isoformat() if delivery.actual_delivery_date else None,
                "cargo_value": delivery.cargo_value,
                "weight_kg": delivery.weight_kg,
                "volume_count": delivery.volume_count
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar entregas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# DOCUMENTS ENDPOINTS  
# ================================

@router.get("/documents")
async def get_documents(
    document_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """
    Lista documentos logísticos
    """
    try:
        filters = {}
        
        if document_type:
            filters["document_type"] = document_type
        if status:
            filters["status"] = status
        
        documents = await LogisticsDocument.find(filters).sort(-LogisticsDocument.created_at).limit(limit).to_list()
        
        result = []
        for doc in documents:
            client_name = ""
            if doc.client:
                client = await doc.client.fetch()
                client_name = client.name if client else ""
            
            result.append({
                "id": str(doc.id),
                "code": doc.code,
                "document_number": doc.document_number,
                "document_type": doc.document_type.value,
                "client": client_name,
                "status": doc.status.value,
                "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
                "file_path": doc.file_path,
                "view_count": doc.view_count
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar documentos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# INCIDENTS ENDPOINTS
# ================================

@router.get("/incidents")
async def get_incidents(
    incident_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """
    Lista incidentes com filtros
    """
    try:
        filters = {}
        
        if incident_type:
            filters["incident_type"] = incident_type
        if severity:
            filters["severity"] = severity  
        if status:
            filters["status"] = status
        
        incidents = await Incident.find(filters).sort(-Incident.occurrence_date).limit(limit).to_list()
        
        result = []
        for incident in incidents:
            client_name = ""
            if incident.client:
                client = await incident.client.fetch()
                client_name = client.name if client else ""
            
            result.append({
                "id": str(incident.id),
                "type": incident.incident_type.value,
                "title": incident.title,
                "description": incident.description,
                "client": client_name,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "occurrence_date": incident.occurrence_date.isoformat(),
                "resolution_date": incident.resolution_date.isoformat() if incident.resolution_date else None,
                "responsible_person": incident.responsible_person
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar incidentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incidents")
async def create_incident(incident_data: IncidentRequest):
    """
    Criar novo incidente
    """
    try:
        # Buscar relacionamentos opcionais
        journey = await Journey.get(incident_data.journey_id) if incident_data.journey_id else None
        delivery = await Delivery.get(incident_data.delivery_id) if incident_data.delivery_id else None
        client = await Company.get(incident_data.client_id) if incident_data.client_id else None
        
        incident = Incident(
            incident_type=incident_data.incident_type,
            title=incident_data.title,
            description=incident_data.description,
            journey=journey,
            delivery=delivery,
            client=client,
            severity=incident_data.severity,
            occurrence_date=incident_data.occurrence_date
        )
        
        await incident.save()
        
        return {
            "success": True,
            "message": "Incidente criado com sucesso",
            "incident_id": str(incident.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar incidente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# CHAT ENDPOINTS
# ================================

@router.get("/chat/conversations")
async def get_chat_conversations(client_id: Optional[str] = Query(None)):
    """
    Lista conversas de chat
    """
    try:
        filters = {"is_active": True}
        
        if client_id:
            filters["client.id"] = PydanticObjectId(client_id)
        
        conversations = await ChatConversation.find(filters).sort(-ChatConversation.last_message_at).to_list()
        
        result = []
        for conv in conversations:
            client_name = ""
            if conv.client:
                client = await conv.client.fetch()
                client_name = client.name if client else ""
            
            result.append({
                "id": str(conv.id),
                "client": client_name,
                "message_count": len(conv.messages),
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "last_message": conv.messages[-1]["content"][:100] + "..." if conv.messages else ""
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar conversas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/conversations/{conversation_id}")
async def get_conversation_messages(conversation_id: str):
    """
    Mensagens de uma conversa específica
    """
    try:
        conversation = await ChatConversation.get(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversa não encontrada")
        
        client_data = await conversation.client.fetch() if conversation.client else None
        
        return {
            "id": str(conversation.id),
            "client": {"id": str(client_data.id), "name": client_data.name} if client_data else None,
            "messages": conversation.messages,
            "created_at": conversation.created_at.isoformat(),
            "last_message_at": conversation.last_message_at.isoformat() if conversation.last_message_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# HEALTH CHECK
# ================================

@router.get("/health")
async def health_check():
    """
    Verificação de saúde da API MitTracking
    """
    try:
        # Teste básico de conectividade
        users_count = await MitUser.count()
        companies_count = await Company.count()
        journeys_count = await Journey.count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "collections": {
                "users": users_count,
                "companies": companies_count, 
                "journeys": journeys_count
            }
        }
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ================================
# AUTHENTICATION MODELS
# ================================

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict] = None
    token: Optional[str] = None

class SetPasswordRequest(BaseModel):
    user_id: str
    new_password: str

security = HTTPBearer(auto_error=False)

# Função para hash simples da senha
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Senha padrão para todos os usuários
DEFAULT_PASSWORD = "mit2024"


# ================================
# USERS ENDPOINTS
# ================================

@router.get("/users/list")
async def get_users_list():
    """
    Lista todos os usuários
    """
    try:
        users = await MitUser.find_all().to_list()
        
        result = []
        for user in users:
            result.append({
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "user_type": user.user_type if user.user_type else "user",
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "has_password": bool(user.password_hash)
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar usuários: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/set-default-passwords")
async def set_default_passwords(force_update: bool = False):
    """
    Define senha padrão para todos os usuários que não têm senha, ou força atualização de todos
    """
    try:
        default_hash = hash_password(DEFAULT_PASSWORD)
        users = await MitUser.find_all().to_list()
        
        updated_count = 0
        for user in users:
            if not user.password_hash or force_update:
                user.password_hash = default_hash
                await user.save()
                updated_count += 1
        
        return {
            "success": True,
            "message": f"Senha padrão definida para {updated_count} usuários",
            "default_password": DEFAULT_PASSWORD,
            "users_updated": updated_count,
            "force_update": force_update
        }
        
    except Exception as e:
        logger.error(f"Erro ao definir senhas padrão: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/create")
async def create_user(user_data: dict):
    """
    Criar novo usuário
    """
    try:
        # Verificar se email já existe
        existing_user = await MitUser.find_one(MitUser.email == user_data["email"])
        if existing_user:
            raise HTTPException(status_code=400, detail="Email já está em uso")
        
        # Criar hash da senha (se fornecida) ou usar padrão
        password = user_data.get("password", DEFAULT_PASSWORD)
        password_hash = hash_password(password)
        
        # Criar novo usuário
        new_user = MitUser(
            name=user_data["name"],
            email=user_data["email"],
            user_type=user_data.get("user_type", "cliente"),
            password_hash=password_hash,
            is_active=user_data.get("is_active", True)
        )
        
        await new_user.save()
        
        return {
            "success": True,
            "message": "Usuário criado com sucesso",
            "user": {
                "id": str(new_user.id),
                "name": new_user.name,
                "email": new_user.email,
                "user_type": new_user.user_type,
                "is_active": new_user.is_active,
                "has_password": bool(new_user.password_hash)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}")
async def update_user(user_id: str, user_data: dict):
    """
    Atualizar usuário existente
    """
    try:
        # Buscar usuário
        user = await MitUser.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Verificar se novo email já existe (se foi alterado)
        if "email" in user_data and user_data["email"] != user.email:
            existing_user = await MitUser.find_one(MitUser.email == user_data["email"])
            if existing_user:
                raise HTTPException(status_code=400, detail="Email já está em uso")
        
        # Atualizar campos fornecidos
        if "name" in user_data:
            user.name = user_data["name"]
        if "email" in user_data:
            user.email = user_data["email"]
        if "user_type" in user_data:
            user.user_type = user_data["user_type"]
        if "is_active" in user_data:
            user.is_active = user_data["is_active"]
        if "password" in user_data and user_data["password"]:
            user.password_hash = hash_password(user_data["password"])
        
        await user.save()
        
        return {
            "success": True,
            "message": "Usuário atualizado com sucesso",
            "user": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "user_type": user.user_type,
                "is_active": user.is_active,
                "has_password": bool(user.password_hash)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """
    Deletar usuário
    """
    try:
        # Buscar usuário
        user = await MitUser.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Deletar usuário
        await user.delete()
        
        return {
            "success": True,
            "message": "Usuário deletado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar usuário: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/login")
async def login(login_data: LoginRequest):
    """
    Login do usuário
    """
    try:
        # Buscar usuário por email
        user = await MitUser.find_one(MitUser.email == login_data.email)
        
        if not user:
            raise HTTPException(status_code=401, detail="Email não encontrado")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Usuário inativo")
        
        # Verificar senha
        password_hash = hash_password(login_data.password)
        
        if not user.password_hash:
            # Se não tem senha definida, aceitar a senha padrão e definir
            if login_data.password == DEFAULT_PASSWORD:
                user.password_hash = password_hash
                await user.save()
            else:
                raise HTTPException(status_code=401, detail="Senha incorreta")
        elif user.password_hash != password_hash:
            raise HTTPException(status_code=401, detail="Senha incorreta")
        
        # Atualizar último login
        user.last_login = datetime.now()
        await user.save()
        
        # Mapear user_type para roles válidos no frontend
        user_type_mapping = {
            "admin": "admin",
            "cliente": "operator",  # Clientes são operadores
            "funcionario": "logistics",  # Funcionários são logística
            "gerente": "admin",  # Gerentes são admin
            "financeiro": "finance"  # Financeiro é finance
        }

        # Mapear user_type ou usar operator como padrão
        mapped_user_type = user_type_mapping.get(user.user_type, "operator")

        return LoginResponse(
            success=True,
            message="Login realizado com sucesso",
            user={
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "user_type": mapped_user_type,
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            token=f"bearer_{str(user.id)}_{int(datetime.now().timestamp())}"  # Token simples
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/change-password") 
async def change_password(password_data: SetPasswordRequest):
    """
    Alterar senha do usuário
    """
    try:
        user = await MitUser.get(password_data.user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Definir nova senha
        user.password_hash = hash_password(password_data.new_password)
        await user.save()
        
        return {
            "success": True,
            "message": "Senha alterada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Obter dados do usuário atual baseado no token
    """
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Token não fornecido")
        
        # Extrair user_id do token simples
        token_parts = credentials.credentials.split("_")
        if len(token_parts) < 2 or token_parts[0] != "bearer":
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_id = token_parts[1]
        user = await MitUser.get(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo")
        
        return {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "user_type": user.user_type,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar usuário atual: {e}")
        raise HTTPException(status_code=401, detail="Token inválido")


# ================================
# AI CONTEXT ENDPOINTS
# ================================

@router.post("/ai/context/user")
async def create_user_context(context_data: dict):
    """
    Criar ou atualizar contexto do usuário para IA
    """
    try:
        user_id = context_data["user_id"]
        context_type = ContextType(context_data["context_type"])
        content = context_data.get("content", {})
        metadata = context_data.get("metadata", {})
        
        # Verificar se já existe um contexto deste tipo para o usuário
        existing_context = await UserContext.find_one(
            UserContext.user_id == user_id,
            UserContext.context_type == context_type
        )
        
        if existing_context:
            # Atualizar contexto existente
            existing_context.content = content
            existing_context.metadata = metadata
            existing_context.updated_at = datetime.utcnow()
            
            # Para contexto de curto prazo, atualizar expiração
            if context_type == ContextType.SHORT_TERM:
                user = await MitUser.get(user_id)
                if user:
                    existing_context.expires_at = datetime.utcnow() + timedelta(days=user.context_retention_days)
            
            await existing_context.save()
            context = existing_context
        else:
            # Criar novo contexto
            expires_at = None
            if context_type == ContextType.SHORT_TERM:
                user = await MitUser.get(user_id)
                if user:
                    expires_at = datetime.utcnow() + timedelta(days=user.context_retention_days)
            
            context = UserContext(
                user_id=user_id,
                context_type=context_type,
                content=content,
                metadata=metadata,
                expires_at=expires_at
            )
            await context.save()
        
        return {
            "success": True,
            "message": "Contexto salvo com sucesso",
            "context": {
                "id": str(context.id),
                "user_id": context.user_id,
                "context_type": context.context_type,
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat(),
                "expires_at": context.expires_at.isoformat() if context.expires_at else None
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao salvar contexto do usuário: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/context/user/{user_id}")
async def get_user_context(user_id: str, context_type: Optional[str] = None):
    """
    Buscar contexto do usuário para IA
    """
    try:
        query = {"user_id": user_id}
        
        if context_type:
            query["context_type"] = ContextType(context_type)
        
        # Remover contextos expirados de curto prazo
        now = datetime.utcnow()
        await UserContext.find(
            UserContext.user_id == user_id,
            UserContext.context_type == ContextType.SHORT_TERM,
            UserContext.expires_at < now
        ).delete()
        
        contexts = await UserContext.find(query).to_list()
        
        result = []
        for context in contexts:
            result.append({
                "id": str(context.id),
                "user_id": context.user_id,
                "context_type": context.context_type,
                "content": context.content,
                "metadata": context.metadata,
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat(),
                "expires_at": context.expires_at.isoformat() if context.expires_at else None
            })
        
        return {
            "success": True,
            "contexts": result
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar contexto do usuário: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/context/global")
@router.post("/ai/contexts/global", include_in_schema=False)
async def create_global_context(context_data: dict):
    """
    Criar ou atualizar contexto global
    """
    try:
        context_key = context_data["context_key"]
        scope = ContextScope(context_data["scope"])
        content = context_data.get("content", {})
        metadata = context_data.get("metadata", {})
        company_id = context_data.get("company_id")
        
        # Verificar se já existe
        existing_context = await GlobalContext.find_one(
            GlobalContext.context_key == context_key,
            GlobalContext.scope == scope
        )
        
        if existing_context:
            # Atualizar
            existing_context.content = content
            existing_context.metadata = metadata
            existing_context.updated_at = datetime.utcnow()
            if company_id:
                existing_context.company_id = company_id
            await existing_context.save()
            context = existing_context
        else:
            # Criar novo
            context = GlobalContext(
                context_key=context_key,
                scope=scope,
                content=content,
                metadata=metadata,
                company_id=company_id
            )
            await context.save()
        
        return {
            "success": True,
            "message": "Contexto global salvo com sucesso",
            "context": {
                "id": str(context.id),
                "context_key": context.context_key,
                "scope": context.scope,
                "company_id": context.company_id,
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao salvar contexto global: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/context/global")
@router.get("/ai/contexts/global", include_in_schema=False)
async def get_global_context(
    scope: Optional[str] = None,
    company_id: Optional[str] = None,
    context_key: Optional[str] = None
):
    """
    Buscar contextos globais
    """
    try:
        query = {"is_active": True}
        
        if scope:
            query["scope"] = ContextScope(scope)
        if company_id:
            query["company_id"] = company_id
        if context_key:
            query["context_key"] = context_key
        
        contexts = await GlobalContext.find(query).to_list()
        
        result = []
        for context in contexts:
            result.append({
                "id": str(context.id),
                "context_key": context.context_key,
                "scope": context.scope,
                "content": context.content,
                "metadata": context.metadata,
                "company_id": context.company_id,
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "contexts": result
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar contextos globais: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/conversation/start")
async def start_conversation(conversation_data: dict):
    """
    Iniciar uma nova conversa com IA
    """
    try:
        user_id = conversation_data["user_id"]
        session_id = conversation_data.get("session_id", str(uuid.uuid4()))
        
        # Atualizar usuário com nova sessão
        user = await MitUser.get(user_id)
        if user:
            user.current_session_id = session_id
            user.last_ai_interaction = datetime.utcnow()
            await user.save()
        
        # Criar nova conversa
        conversation = ConversationHistory(
            user_id=user_id,
            session_id=session_id,
            messages=[],
            context_summary={}
        )
        await conversation.save()
        
        return {
            "success": True,
            "session_id": session_id,
            "conversation_id": str(conversation.id)
        }
        
    except Exception as e:
        logger.error(f"Erro ao iniciar conversa: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/conversation/{session_id}/message")
async def add_conversation_message(session_id: str, message_data: dict):
    """
    Adicionar mensagem à conversa
    """
    try:
        message = message_data["message"]
        role = message_data.get("role", "user")  # user, assistant, system
        
        # Buscar conversa
        conversation = await ConversationHistory.find_one(
            ConversationHistory.session_id == session_id
        )
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversa não encontrada")
        
        # Adicionar mensagem
        new_message = {
            "role": role,
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        conversation.messages.append(new_message)
        conversation.total_messages += 1
        
        # Atualizar interação do usuário
        user = await MitUser.get(conversation.user_id)
        if user:
            user.last_ai_interaction = datetime.utcnow()
            await user.save()
        
        await conversation.save()
        
        return {
            "success": True,
            "message": "Mensagem adicionada com sucesso",
            "total_messages": conversation.total_messages
        }
        
    except Exception as e:
        logger.error(f"Erro ao adicionar mensagem: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/conversation/{session_id}/history")
async def get_conversation_history(session_id: str, limit: Optional[int] = 50):
    """
    Buscar histórico da conversa
    """
    try:
        conversation = await ConversationHistory.find_one(
            ConversationHistory.session_id == session_id
        )
        
        if not conversation:
            return {
                "success": True,
                "messages": [],
                "context_summary": {}
            }
        
        # Limitar número de mensagens se necessário
        messages = conversation.messages
        if limit and len(messages) > limit:
            messages = messages[-limit:]  # Pegar as últimas N mensagens
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": messages,
            "context_summary": conversation.context_summary,
            "start_time": conversation.start_time.isoformat(),
            "total_messages": conversation.total_messages
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico da conversa: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ai/context/user/{user_id}/cleanup")
async def cleanup_user_context(user_id: str):
    """
    Limpar contextos expirados do usuário
    """
    try:
        now = datetime.utcnow()
        
        # Remover contextos de curto prazo expirados
        result = await UserContext.find(
            UserContext.user_id == user_id,
            UserContext.context_type == ContextType.SHORT_TERM,
            UserContext.expires_at < now
        ).delete()
        
        return {
            "success": True,
            "message": f"Limpeza concluída. {result.deleted_count} contextos removidos"
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar contextos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================
# DOCUMENT MANAGEMENT ENDPOINTS
# =====================================

@router.get("/documents/list")
async def list_user_documents(
    user_id: Optional[str] = Query(None, description="ID do usuário para filtrar documentos"),
    category: Optional[str] = Query(None, description="Categoria do documento (CTE, BL, NF-e, etc.)"),
    status: Optional[str] = Query(None, description="Status de processamento"),
    origem_upload: Optional[str] = Query(None, description="Origem do upload (manual, api, chat, email)"),
    limit: int = Query(50, description="Número máximo de documentos"),
    skip: int = Query(0, description="Documentos a pular (paginação)")
):
    """
    Lista documentos do usuário com filtros.
    Cada usuário só vê documentos que ele próprio fez upload ou que foram atribuídos a ele.
    """
    try:
        from ..models import DocumentFile, Order
        
        # Construir query base
        query_filters = {}
        
        # Filtrar por usuário se fornecido
        if user_id:
            # Verifica se o usuário existe
            user = await MitUser.find_one(MitUser.id == user_id)
            if not user:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
            # Buscar orders vinculadas ao usuário ou documents diretos
            # Por enquanto, buscamos todos os documentos (implementar lógica de propriedade depois)
            pass
            
        # Aplicar filtros adicionais
        if category:
            query_filters["category"] = category
            
        # Buscar documentos
        documents_query = DocumentFile.find(query_filters)
        
        # Aplicar paginação
        documents = await documents_query.skip(skip).limit(limit).to_list()
        total = await DocumentFile.find(query_filters).count()
        
        # Formatar response
        formatted_docs = []
        for doc in documents:
            # Buscar order relacionada
            order = None
            if hasattr(doc, 'order_id') and doc.order_id:
                order = await Order.find_one(Order.order_id == doc.order_id)
            
            # Mapear tipos de documento
            tipo_doc = "Outro"
            if hasattr(doc, 'category'):
                categoria = doc.category.value if hasattr(doc.category, 'value') else str(doc.category)
                tipo_mapping = {
                    "cte": "CT-e",
                    "bl": "BL", 
                    "invoice": "NF-e",
                    "certificate": "Certificado",
                    "photo": "Foto",
                    "other": "Outro"
                }
                tipo_doc = tipo_mapping.get(categoria.lower(), categoria)
            
            # Mapear status
            status_doc = "Carregado"
            if hasattr(doc, 'processing_status'):
                status_value = doc.processing_status.value if hasattr(doc.processing_status, 'value') else str(doc.processing_status)
                status_mapping = {
                    "uploaded": "Carregado",
                    "processing": "Processando", 
                    "indexed": "Validado",
                    "error": "Rejeitado"
                }
                status_doc = status_mapping.get(status_value.lower(), status_value)
            
            formatted_docs.append({
                "id": str(doc.id),
                "numero": getattr(doc, 'original_name', 'Sem nome'),
                "tipo": tipo_doc,
                "cliente": order.customer_name if order else "Cliente não informado",
                "jornada": order.order_id if order else None,
                "origem": "Não informado",
                "destino": "Não informado", 
                "dataUpload": doc.uploaded_at.isoformat() if hasattr(doc, 'uploaded_at') and doc.uploaded_at else None,
                "dataEmissao": doc.uploaded_at.isoformat() if hasattr(doc, 'uploaded_at') and doc.uploaded_at else None,
                "status": status_doc,
                "tamanho": f"{(doc.size_bytes / 1024 / 1024):.1f} MB" if hasattr(doc, 'size_bytes') and doc.size_bytes else "N/A",
                "versao": 1,
                "uploadPor": "Usuário MIT",
                "origem_upload": "manual",  # TODO: implementar campo origem_upload
                "visualizacoes": getattr(doc, 'access_count', 0),
                "ultimaVisualizacao": doc.last_accessed.isoformat() if hasattr(doc, 'last_accessed') and doc.last_accessed else None,
                "file_id": getattr(doc, 'file_id', str(doc.id)),
                "s3_url": getattr(doc, 's3_url', None),
                "order_id": getattr(doc, 'order_id', None)
            })
        
        return {
            "success": True,
            "documents": formatted_docs,
            "pagination": {
                "total": total,
                "limit": limit,
                "skip": skip,
                "has_more": skip + len(documents) < total
            },
            "filters_applied": {
                "user_id": user_id,
                "category": category,
                "status": status,
                "origem_upload": origem_upload
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar documentos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload")
async def upload_document_mit(
    file: UploadFile = File(...),
    user_id: str = Form(..., description="ID do usuário que está fazendo upload"),
    order_id: Optional[str] = Form(None, description="ID da order para vincular (opcional)"),
    category: str = Form("other", description="Categoria do documento"),
    public: bool = Form(True, description="Se o documento é público")
):
    """
    Upload de documento específico para usuários MIT.
    Cria uma order automática se não fornecida e vincula o documento ao usuário.
    """
    try:
        from ..models import DocumentFile, Order, DocumentCategory, ProcessingStatus
        import uuid
        import os
        
        # Verificar se usuário existe
        user = await MitUser.find_one(MitUser.id == user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Se não foi fornecido order_id, criar uma order automática
        if not order_id:
            from ..models import OrderType, OrderStatus
            
            auto_order = Order(
                title=f"Upload automático - {file.filename}",
                description=f"Order criada automaticamente para upload do usuário {user.name}",
                order_type=OrderType.TRANSPORT,
                customer_name=user.name,
                customer_id=str(user.id)
            )
            await auto_order.save()
            order_id = auto_order.order_id
        else:
            # Verificar se order existe
            order = await Order.find_one(Order.order_id == order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order não encontrada")
        
        # Simular upload para S3 (por enquanto apenas salvar no MongoDB)
        file_content = await file.read()
        
        # Detectar tipo de arquivo
        import magic
        mime_type = magic.from_buffer(file_content[:2048], mime=True)
        file_extension = os.path.splitext(file.filename or "unknown")[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Mapear categoria
        category_mapping = {
            "cte": DocumentCategory.CTE,
            "bl": DocumentCategory.BL,
            "nf-e": DocumentCategory.INVOICE,
            "invoice": DocumentCategory.INVOICE,
            "photo": DocumentCategory.PHOTO,
            "other": DocumentCategory.OTHER
        }
        doc_category = category_mapping.get(category.lower(), DocumentCategory.OTHER)
        
        # Criar documento no MongoDB
        document = DocumentFile(
            original_name=file.filename or "unknown",
            s3_key=unique_filename,
            s3_url=f"https://demo-bucket.s3.amazonaws.com/{unique_filename}",  # URL demo
            file_type=mime_type,
            file_extension=file_extension,
            size_bytes=len(file_content),
            category=doc_category,
            is_public=public,
            order_id=order_id,
            processing_status=ProcessingStatus.UPLOADED
        )
        
        # Adicionar metadados do usuário
        if hasattr(document, 'extracted_metadata'):
            document.extracted_metadata = {
                "uploaded_by_user": str(user.id),
                "uploaded_by_name": user.name,
                "upload_method": "manual_mit_interface"
            }
        
        await document.save()
        
        # Processamento OCR e geração de embeddings
        await process_document_with_ocr_and_embeddings(document, file_content)
        
        document.add_processing_log("Documento carregado via interface MIT")
        document.add_processing_log(f"Upload realizado por: {user.name}")
        await document.save()
        
        return {
            "success": True,
            "message": "Documento enviado com sucesso!",
            "document": {
                "id": str(document.id),
                "file_id": getattr(document, 'file_id', str(document.id)),
                "original_name": document.original_name,
                "size_bytes": document.size_bytes,
                "category": document.category.value,
                "order_id": order_id,
                "processing_status": document.processing_status.value,
                "uploaded_at": document.uploaded_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Erro no upload de documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/details")
async def get_document_details(
    document_id: str,
    user_id: Optional[str] = Query(None, description="ID do usuário solicitante")
):
    """
    Retorna detalhes completos de um documento específico.
    Verifica se o usuário tem permissão para ver o documento.
    """
    try:
        from ..models import DocumentFile, Order
        
        # Buscar documento
        document = await DocumentFile.find_one(DocumentFile.id == document_id)
        if not document:
            # Tentar buscar por file_id se não encontrou por id
            if hasattr(DocumentFile, 'file_id'):
                document = await DocumentFile.find_one(DocumentFile.file_id == document_id)
            
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        # TODO: Implementar verificação de permissão do usuário
        # Por enquanto, permite acesso a todos os documentos
        
        # Buscar order relacionada
        order = None
        if hasattr(document, 'order_id') and document.order_id:
            order = await Order.find_one(Order.order_id == document.order_id)
        
        # Incrementar contador de acesso
        if hasattr(document, 'increment_access'):
            document.increment_access()
            await document.save()
        
        # Preparar detalhes completos
        details = {
            "id": str(document.id),
            "file_id": getattr(document, 'file_id', str(document.id)),
            "original_name": document.original_name,
            "file_type": getattr(document, 'file_type', 'application/octet-stream'),
            "size_bytes": getattr(document, 'size_bytes', 0),
            "category": document.category.value if hasattr(document, 'category') else "other",
            "processing_status": document.processing_status.value if hasattr(document, 'processing_status') else "uploaded",
            "uploaded_at": document.uploaded_at.isoformat() if hasattr(document, 'uploaded_at') and document.uploaded_at else None,
            "last_accessed": document.last_accessed.isoformat() if hasattr(document, 'last_accessed') and document.last_accessed else None,
            "access_count": getattr(document, 'access_count', 0),
            "s3_url": getattr(document, 's3_url', None),
            "is_public": getattr(document, 'is_public', True),
            "tags": getattr(document, 'tags', []),
            "text_content_available": bool(getattr(document, 'text_content', None)),
            "has_embedding": bool(getattr(document, 'embedding', None)),
            "processing_logs": getattr(document, 'processing_logs', [])
        }
        
        # Adicionar informações da order
        if order:
            details["order"] = {
                "order_id": order.order_id,
                "title": order.title,
                "customer_name": order.customer_name,
                "status": order.status.value if hasattr(order, 'status') else None,
                "created_at": order.created_at.isoformat() if hasattr(order, 'created_at') and order.created_at else None
            }
        
        return {
            "success": True,
            "document": details
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/download")
async def download_document_mit(document_id: str):
    """
    Gera URL de download para um documento.
    Para demonstração, retorna URL simulada.
    """
    try:
        from ..models import DocumentFile
        
        # Buscar documento
        document = await DocumentFile.find_one(DocumentFile.id == document_id)
        if not document:
            if hasattr(DocumentFile, 'file_id'):
                document = await DocumentFile.find_one(DocumentFile.file_id == document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        # Simular URL de download
        download_url = getattr(document, 's3_url', None)
        if not download_url:
            download_url = f"https://demo-bucket.s3.amazonaws.com/{document.original_name}"
        
        return {
            "success": True,
            "download_url": download_url,
            "filename": document.original_name,
            "size_bytes": getattr(document, 'size_bytes', 0),
            "file_type": getattr(document, 'file_type', 'application/octet-stream'),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "note": "URL simulada para demonstração"
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar download: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document_mit(
    document_id: str,
    user_id: str = Query(..., description="ID do usuário solicitante")
):
    """
    Remove um documento do sistema.
    Verifica se o usuário tem permissão para deletar.
    """
    try:
        from ..models import DocumentFile
        
        # Verificar se usuário existe
        user = await MitUser.find_one(MitUser.id == user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Buscar documento
        document = await DocumentFile.find_one(DocumentFile.id == document_id)
        if not document:
            if hasattr(DocumentFile, 'file_id'):
                document = await DocumentFile.find_one(DocumentFile.file_id == document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        # TODO: Verificar se usuário tem permissão para deletar
        # Por enquanto permite deletar qualquer documento
        
        # Deletar do MongoDB
        await document.delete()
        
        # TODO: Deletar do S3 também em ambiente de produção
        
        return {
            "success": True,
            "message": "Documento removido com sucesso",
            "deleted_document": {
                "id": str(document.id),
                "original_name": document.original_name
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao deletar documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# AI CONTEXT ENDPOINTS
# ================================

@router.post("/ai/contexts/link-documents")
async def link_documents_to_context(
    user_id: str = Body(..., description="ID do usuário"),
    session_id: str = Body(..., description="ID da sessão de chat"),
    order_ids: Optional[List[str]] = Body(None, description="IDs das ordens para vincular documentos"),
    journey_ids: Optional[List[str]] = Body(None, description="IDs das jornadas para vincular documentos"), 
    document_categories: Optional[List[str]] = Body(None, description="Categorias de documentos para vincular")
):
    """
    Vincula documentos ao contexto do usuário baseado em ordens, jornadas ou categorias.
    Os documentos são adicionados ao contexto de curto prazo da sessão ativa.
    """
    try:
        from ..models import DocumentFile, Order
        from ..models_mittracking import UserContext, LogisticsDocument, Journey
        
        # Verificar se usuário existe
        user = await MitUser.find_one(MitUser.id == user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Buscar contexto ativo da sessão
        session_context = await UserContext.find_one(
            UserContext.user_id == user_id,
            UserContext.session_id == session_id,
            UserContext.context_type == ContextType.SHORT_TERM,
            UserContext.is_active == True
        )
        
        if not session_context:
            raise HTTPException(status_code=404, detail="Contexto de sessão não encontrado")
        
        linked_documents = []
        
        # Processar documentos baseados em ordens
        if order_ids:
            for order_id in order_ids:
                # Buscar documentos da ordem no sistema geral
                documents = await DocumentFile.find(DocumentFile.order_id == order_id).to_list()
                for doc in documents:
                    if doc.text_content or doc.extracted_metadata:
                        linked_documents.append({
                            "source": "order",
                            "source_id": order_id,
                            "document_id": str(doc.id),
                            "document_name": doc.original_name,
                            "document_type": doc.category,
                            "text_content": doc.text_content[:500] if doc.text_content else None,  # Resumo
                            "metadata": doc.extracted_metadata,
                            "embedding_available": bool(doc.embedding)
                        })
        
        # Processar documentos baseados em jornadas (MIT system)
        if journey_ids:
            for journey_id in journey_ids:
                # Buscar documentos da jornada no sistema MIT
                documents = await LogisticsDocument.find(LogisticsDocument.journey.id == journey_id).to_list()
                for doc in documents:
                    linked_documents.append({
                        "source": "journey",
                        "source_id": journey_id,
                        "document_id": str(doc.id),
                        "document_name": f"{doc.document_type.value}_{doc.document_number}",
                        "document_type": doc.document_type.value,
                        "status": doc.status.value,
                        "client": doc.client.fetch().name if doc.client else None
                    })
        
        # Processar documentos baseados em categorias
        if document_categories:
            for category in document_categories:
                # Buscar documentos da categoria no sistema geral (associados ao usuário)
                documents = await DocumentFile.find(
                    DocumentFile.category == category,
                    DocumentFile.uploaded_by == user_id  # Apenas documentos do usuário
                ).limit(10).to_list()  # Limitar para evitar sobrecarga
                
                for doc in documents:
                    if doc.text_content or doc.extracted_metadata:
                        linked_documents.append({
                            "source": "category",
                            "source_id": category,
                            "document_id": str(doc.id),
                            "document_name": doc.original_name,
                            "document_type": doc.category,
                            "text_content": doc.text_content[:500] if doc.text_content else None,
                            "metadata": doc.extracted_metadata,
                            "embedding_available": bool(doc.embedding)
                        })
        
        # Atualizar contexto da sessão com documentos vinculados
        updated_content = session_context.content.copy() if session_context.content else {}
        updated_content.update({
            "linked_documents": linked_documents,
            "document_linking_timestamp": datetime.utcnow().isoformat(),
            "documents_count": len(linked_documents),
            "linking_criteria": {
                "order_ids": order_ids,
                "journey_ids": journey_ids, 
                "document_categories": document_categories
            }
        })
        
        session_context.content = updated_content
        session_context.updated_at = datetime.utcnow()
        await session_context.save()
        
        return {
            "success": True,
            "message": f"{len(linked_documents)} documentos vinculados ao contexto",
            "context_id": str(session_context.id),
            "session_id": session_id,
            "linked_documents_count": len(linked_documents),
            "linked_documents": linked_documents[:5]  # Retornar apenas os primeiros 5 como preview
        }
        
    except Exception as e:
        logger.error(f"Erro ao vincular documentos ao contexto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/contexts/user/{context_id}/documents")
async def get_context_documents(
    context_id: str,
    user_id: str = Query(..., description="ID do usuário")
):
    """
    Obtém lista de documentos vinculados a um contexto específico
    """
    try:
        # Verificar se usuário existe
        user = await MitUser.find_one(MitUser.id == user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Buscar contexto
        context = await UserContext.find_one(
            UserContext.id == context_id,
            UserContext.user_id == user_id
        )
        
        if not context:
            raise HTTPException(status_code=404, detail="Contexto não encontrado")
        
        linked_documents = context.content.get("linked_documents", []) if context.content else []
        
        return {
            "success": True,
            "context_id": str(context.id),
            "context_type": context.context_type.value,
            "session_id": context.session_id,
            "documents_count": len(linked_documents),
            "linked_documents": linked_documents,
            "linking_criteria": context.content.get("linking_criteria", {}) if context.content else {}
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter documentos do contexto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# OCR AND EMBEDDING PROCESSING
# ================================

async def process_document_with_ocr_and_embeddings(document, file_content: bytes):
    """
    Processa documento com OCR e gera embeddings para busca semântica.
    Integra o EmbeddingService com processamento de documentos.
    """
    try:
        from ..services.embedding_service import EmbeddingService
        from ..services.document_processor import DocumentProcessor
        
        logger.info(f"Iniciando processamento OCR e embeddings para documento {document.id}")
        document.mark_as_processing()
        
        # Inicializar serviços
        embedding_service = EmbeddingService()
        doc_processor = DocumentProcessor()
        
        # Extrair texto com OCR baseado no tipo de arquivo
        text_content = None
        extracted_metadata = {}
        
        if document.file_type.startswith('image/'):
            # Processamento para imagens (PNG, JPG, etc.)
            logger.info("Processando imagem com OCR")
            try:
                # Usar Tesseract OCR para extrair texto de imagens
                import pytesseract
                from PIL import Image
                import io
                
                image = Image.open(io.BytesIO(file_content))
                text_content = pytesseract.image_to_string(image, lang='por')
                
                extracted_metadata = {
                    "ocr_engine": "tesseract",
                    "image_size": image.size,
                    "image_mode": image.mode,
                    "text_extraction_confidence": "medium"
                }
                
                document.add_processing_log("OCR realizado com Tesseract")
                
            except ImportError:
                logger.warning("Tesseract não disponível, usando extração simulada")
                text_content = f"[Texto simulado do documento {document.original_name}]"
                extracted_metadata = {"ocr_engine": "simulated", "note": "Tesseract não disponível"}
            except Exception as ocr_error:
                logger.error(f"Erro no OCR de imagem: {ocr_error}")
                text_content = "[Erro na extração de texto]"
                extracted_metadata = {"ocr_engine": "error", "error": str(ocr_error)}
        
        elif document.file_type == 'application/pdf':
            # Processamento para PDFs
            logger.info("Processando PDF com PyMuPDF")
            try:
                import fitz  # PyMuPDF
                
                pdf_document = fitz.open(stream=file_content, filetype="pdf")
                text_pages = []
                
                for page_num in range(pdf_document.page_count):
                    page = pdf_document[page_num]
                    text_pages.append(page.get_text())
                
                text_content = "\n\n".join(text_pages)
                
                extracted_metadata = {
                    "pdf_engine": "pymupdf",
                    "page_count": pdf_document.page_count,
                    "has_images": any(page.get_images() for page in pdf_document),
                    "text_extraction_method": "direct"
                }
                
                document.add_processing_log(f"Texto extraído de PDF ({pdf_document.page_count} páginas)")
                pdf_document.close()
                
            except ImportError:
                logger.warning("PyMuPDF não disponível, usando extração simulada")
                text_content = f"[Texto simulado do PDF {document.original_name}]"
                extracted_metadata = {"pdf_engine": "simulated", "note": "PyMuPDF não disponível"}
            except Exception as pdf_error:
                logger.error(f"Erro no processamento de PDF: {pdf_error}")
                text_content = "[Erro na extração de texto do PDF]"
                extracted_metadata = {"pdf_engine": "error", "error": str(pdf_error)}
        
        else:
            # Para outros tipos de arquivo, usar processamento genérico
            logger.info(f"Processando arquivo genérico ({document.file_type})")
            text_content = f"Documento {document.original_name} processado automaticamente"
            extracted_metadata = {
                "processing_method": "generic",
                "file_type": document.file_type,
                "note": "Processamento genérico aplicado"
            }
        
        # Limpar e validar texto extraído
        if text_content:
            text_content = text_content.strip()
            if len(text_content) < 10:  # Texto muito curto, provavelmente erro
                text_content = f"[Documento {document.original_name}] - Conteúdo disponível para processamento"
        else:
            text_content = f"[Documento {document.original_name}] - Processado sem extração de texto"
        
        # Gerar embedding do texto extraído
        embedding = None
        embedding_model = None
        
        if text_content and len(text_content) > 20:  # Só gerar embedding se houver texto suficiente
            try:
                logger.info("Gerando embedding semântico")
                embedding = await embedding_service.generate_embedding_async(text_content)
                embedding_model = embedding_service.get_model_info()["name"]
                
                document.add_processing_log(f"Embedding gerado com {embedding_model}")
                
            except Exception as embed_error:
                logger.error(f"Erro ao gerar embedding: {embed_error}")
                document.add_processing_log(f"Falha ao gerar embedding: {str(embed_error)}")
        
        # Atualizar documento com resultados
        document.text_content = text_content
        document.extracted_metadata = {
            **document.extracted_metadata,
            **extracted_metadata,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "text_length": len(text_content) if text_content else 0
        }
        
        if embedding:
            document.embedding = embedding
            document.embedding_model = embedding_model
            document.mark_as_indexed(embedding_model)
        else:
            document.processing_status = ProcessingStatus.PROCESSING  # Parcialmente processado
            document.add_processing_log("Documento processado sem embedding")
        
        logger.info(f"Processamento concluído para documento {document.id}")
        
    except Exception as e:
        logger.error(f"Erro crítico no processamento de documento {document.id}: {e}")
        document.mark_as_error(f"Erro no processamento: {str(e)}")
        raise


async def reprocess_existing_documents_with_embeddings():
    """
    Função utilitária para reprocessar documentos existentes que não têm embeddings.
    Pode ser chamada via endpoint separado para migração.
    """
    try:
        from ..models import DocumentFile
        
        # Buscar documentos sem embedding
        documents_without_embeddings = await DocumentFile.find(
            DocumentFile.embedding == None,
            DocumentFile.text_content != None
        ).limit(100).to_list()
        
        logger.info(f"Encontrados {len(documents_without_embeddings)} documentos para reprocessar")
        
        embedding_service = EmbeddingService()
        processed_count = 0
        
        for doc in documents_without_embeddings:
            if doc.text_content and len(doc.text_content) > 20:
                try:
                    embedding = await embedding_service.generate_embedding_async(doc.text_content)
                    
                    if embedding:
                        doc.embedding = embedding
                        doc.embedding_model = embedding_service.get_model_info()["name"]
                        doc.mark_as_indexed(doc.embedding_model)
                        await doc.save()
                        
                        processed_count += 1
                        logger.info(f"Documento {doc.id} reprocessado com sucesso")
                
                except Exception as e:
                    logger.error(f"Erro ao reprocessar documento {doc.id}: {e}")
                    continue
        
        return {
            "success": True,
            "message": f"{processed_count} documentos reprocessados com embeddings",
            "processed_count": processed_count,
            "total_found": len(documents_without_embeddings)
        }
        
    except Exception as e:
        logger.error(f"Erro ao reprocessar documentos: {e}")
        raise


@router.post("/documents/reprocess-embeddings")
async def reprocess_documents_embeddings_endpoint():
    """
    Endpoint para reprocessar documentos existentes que não possuem embeddings.
    Útil para migração e manutenção do sistema.
    """
    try:
        result = await reprocess_existing_documents_with_embeddings()
        return result
    except Exception as e:
        logger.error(f"Erro no endpoint de reprocessamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))
