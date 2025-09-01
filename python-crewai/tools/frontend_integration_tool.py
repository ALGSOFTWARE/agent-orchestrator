"""
Frontend Integration Tool

Ferramenta para integração entre o agente frontend_logistics_agent 
e o sistema gatekeeper-api, fornecendo endpoints específicos para 
alimentar os componentes React do logistic-pulse-31-main.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import asyncio
from datetime import datetime, timedelta
import json

class FrontendAPITool:
    """Tool para integração com APIs do frontend"""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url

    async def get_dashboard_kpis(self, user_id: str) -> Dict[str, Any]:
        """
        Busca KPIs para o dashboard
        Endpoint: GET /api/frontend/dashboard/kpis
        """
        return {
            "delivery_time_avg": "3.2 dias",
            "sla_compliance": "94.2%",
            "nps_score": "8.7",
            "incidents_count": 12,
            "total_deliveries": 2237,
            "success_rate": 94.2,
            "avg_time_hours": 2.4,
            "active_routes": 48,
            "trend_data": {
                "delivery_time": {"value": -0.3, "trend": "down"},
                "sla": {"value": 2.1, "trend": "up"},
                "nps": {"value": 0.5, "trend": "up"},
                "incidents": {"value": 3, "trend": "up"}
            }
        }

    async def get_documents(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca documentos com filtros
        Endpoint: GET /api/frontend/documents
        """
        # Simulação de dados - substituir por chamada real à API
        mock_documents = [
            {
                "id": "DOC-001",
                "number": "CTE-2024-001234",
                "type": "CTE",
                "client": "Empresa ABC Ltda",
                "journey_id": "JOR-001",
                "origin": "São Paulo/SP",
                "destination": "Rio de Janeiro/RJ",
                "upload_date": "2024-01-15T08:00:00Z",
                "emission_date": "2024-01-15T06:00:00Z",
                "status": "Validado",
                "size": "2.5 MB",
                "version": 1,
                "uploaded_by": "Sistema IA",
                "upload_source": "chat",
                "views": 12,
                "last_viewed": "2024-01-15T10:30:00Z"
            },
            {
                "id": "DOC-002",
                "number": "NF-2024-567890",
                "type": "NF",
                "client": "Empresa DEF S.A",
                "journey_id": "JOR-002",
                "origin": "Belo Horizonte/MG",
                "destination": "Salvador/BA",
                "upload_date": "2024-01-14T14:30:00Z",
                "emission_date": "2024-01-14T12:00:00Z",
                "status": "Pendente Validação",
                "size": "1.8 MB",
                "version": 2,
                "uploaded_by": "João Silva",
                "upload_source": "manual",
                "views": 5,
                "last_viewed": "2024-01-14T16:45:00Z"
            }
        ]
        
        # Aplicar filtros
        filtered_docs = mock_documents
        
        if filters.get("type"):
            filtered_docs = [doc for doc in filtered_docs if doc["type"] == filters["type"]]
        if filters.get("status"):
            filtered_docs = [doc for doc in filtered_docs if doc["status"] == filters["status"]]
        if filters.get("client"):
            filtered_docs = [doc for doc in filtered_docs if filters["client"].lower() in doc["client"].lower()]
            
        return filtered_docs

    async def get_deliveries(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca entregas
        Endpoint: GET /api/frontend/deliveries
        """
        mock_deliveries = [
            {
                "id": "ENT-001",
                "client": "Cliente A",
                "recipient": "João Silva",
                "origin": "São Paulo",
                "destination": "Av. Paulista, 1000 - São Paulo/SP",
                "status": "Em Trânsito",
                "delivery_date": "2024-01-16",
                "estimated_time": "14:00",
                "carrier": "Express Log",
                "driver": "Carlos Santos",
                "vehicle": "ABC-1234",
                "documents": ["CT-e", "NF-e", "DACTE"],
                "value": "R$ 2.500,00",
                "weight": "150kg",
                "volumes": 3,
                "occurrences": [],
                "coordinates": {"lat": -23.5505, "lng": -46.6333}
            },
            {
                "id": "ENT-002",
                "client": "Cliente B",
                "recipient": "Maria Santos",
                "origin": "Rio de Janeiro",
                "destination": "Rua das Flores, 500 - Rio de Janeiro/RJ",
                "status": "Entregue",
                "delivery_date": "2024-01-14",
                "estimated_time": "16:30",
                "actual_delivery_time": "16:15",
                "carrier": "Rápido Trans",
                "driver": "Pedro Oliveira",
                "vehicle": "XYZ-5678",
                "documents": ["CT-e", "NF-e"],
                "value": "R$ 1.800,00",
                "weight": "85kg",
                "volumes": 2,
                "occurrences": [],
                "coordinates": {"lat": -22.9068, "lng": -43.1729},
                "proof_of_delivery": {
                    "photo": "delivery-002.jpg",
                    "signature": "Maria Santos",
                    "gps_coords": "-22.9068, -43.1729",
                    "timestamp": "2024-01-14 16:15"
                }
            }
        ]
        
        # Aplicar filtros
        filtered_deliveries = mock_deliveries
        
        if filters.get("status"):
            filtered_deliveries = [d for d in filtered_deliveries if d["status"] == filters["status"]]
        if filters.get("client"):
            filtered_deliveries = [d for d in filtered_deliveries if filters["client"].lower() in d["client"].lower()]
            
        return filtered_deliveries

    async def get_journeys(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca jornadas
        Endpoint: GET /api/frontend/journeys
        """
        mock_journeys = [
            {
                "id": "JOR-001",
                "client": "Cliente A",
                "origin": "São Paulo",
                "destination": "Rio de Janeiro", 
                "status": "Em Trânsito",
                "progress": 65,
                "carrier": "Express Log",
                "checkpoints": [
                    {"name": "Origem", "status": "completed", "date": "2024-01-15 08:00"},
                    {"name": "Porto Santos", "status": "completed", "date": "2024-01-15 12:00"},
                    {"name": "CD Rio", "status": "current", "date": "2024-01-15 18:00"},
                    {"name": "Entrega", "status": "pending", "date": "2024-01-16 14:00"}
                ],
                "documents": ["CT-e", "NF-e", "Manifesto"],
                "coordinates": {"lat": -22.9068, "lng": -43.1729}
            },
            {
                "id": "JOR-002",
                "client": "Cliente B",
                "origin": "Belo Horizonte",
                "destination": "Brasília",
                "status": "Aguardando Documento",
                "progress": 30,
                "carrier": "Rápido Trans",
                "checkpoints": [
                    {"name": "Origem", "status": "completed", "date": "2024-01-14 10:00"},
                    {"name": "CD Central", "status": "current", "date": "2024-01-15 09:00"},
                    {"name": "Hub Brasília", "status": "pending", "date": "2024-01-16 08:00"},
                    {"name": "Entrega", "status": "pending", "date": "2024-01-16 16:00"}
                ],
                "documents": ["CT-e", "AWB"],
                "coordinates": {"lat": -15.7801, "lng": -47.9292}
            }
        ]
        
        # Aplicar filtros
        filtered_journeys = mock_journeys
        
        if filters.get("status"):
            filtered_journeys = [j for j in filtered_journeys if j["status"] == filters["status"]]
        if filters.get("client"):
            filtered_journeys = [j for j in filtered_journeys if filters["client"].lower() in j["client"].lower()]
            
        return filtered_journeys

    async def search_documents(self, query: str, doc_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca documentos por query textual
        Endpoint: GET /api/frontend/documents/search
        """
        documents = await self.get_documents({})
        
        # Filtrar por query
        results = []
        query_lower = query.lower()
        
        for doc in documents:
            if (query_lower in doc["number"].lower() or 
                query_lower in doc["client"].lower() or
                (doc_type and doc["type"] == doc_type)):
                results.append(doc)
                
        return results

    async def get_reports_data(self, report_type: str, date_range: Dict[str, str]) -> Dict[str, Any]:
        """
        Busca dados para relatórios
        Endpoint: GET /api/frontend/reports/{report_type}
        """
        if report_type == "deliveries":
            return {
                "monthly_data": [
                    {"month": "Jan", "entregas": 120, "atrasadas": 8},
                    {"month": "Fev", "entregas": 145, "atrasadas": 12},
                    {"month": "Mar", "entregas": 167, "atrasadas": 6},
                    {"month": "Abr", "entregas": 189, "atrasadas": 15},
                    {"month": "Mai", "entregas": 201, "atrasadas": 9},
                    {"month": "Jun", "entregas": 234, "atrasadas": 11}
                ],
                "status_distribution": [
                    {"name": "Entregues", "value": 1847, "color": "#22c55e"},
                    {"name": "Em Trânsito", "value": 234, "color": "#3b82f6"},
                    {"name": "Atrasadas", "value": 67, "color": "#ef4444"},
                    {"name": "Pendentes", "value": 89, "color": "#f59e0b"}
                ]
            }
        
        elif report_type == "routes":
            return {
                "efficiency_data": [
                    {"rota": "Rota A", "eficiencia": 92},
                    {"rota": "Rota B", "eficiencia": 87},
                    {"rota": "Rota C", "eficiencia": 95},
                    {"rota": "Rota D", "eficiencia": 83},
                    {"rota": "Rota E", "eficiencia": 89}
                ]
            }
        
        return {}

    async def upload_document(self, file_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Faz upload de documento
        Endpoint: POST /api/frontend/documents/upload
        """
        # Simular processamento de upload
        return {
            "id": f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "uploaded",
            "ai_detection": {
                "type": "CTE",
                "confidence": 0.95,
                "extracted_data": {
                    "number": "CTE-2024-001235",
                    "client": "Cliente Detectado",
                    "value": "R$ 3.200,00"
                }
            },
            "processing_time": 2.3
        }

    async def process_chat_message(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagem do chat via agente
        Endpoint: POST /api/frontend/chat/message
        """
        from ..agents.frontend_logistics_agent import FrontendLogisticsAgent
        
        agent = FrontendLogisticsAgent()
        response = agent.process_chat_message(message, user_context)
        
        return response.dict()

# Instância global da ferramenta
frontend_api_tool = FrontendAPITool()