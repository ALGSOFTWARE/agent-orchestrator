"""
Frontend Logistics Interface Agent

Agente especializado para integração entre o frontend logistic-pulse-31-main 
e o sistema backend através de APIs REST e GraphQL.

Responsabilidades:
1. Processar mensagens do chat inteligente
2. Converter queries em dados estruturados para o frontend
3. Interpretar intenções do usuário em ações específicas
4. Fornecer respostas contextualizadas para operadores logísticos
5. Utilizar busca semântica para encontrar documentos relevantes
"""

from crewai import Agent
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime
import json
import re
import sys
import os

# Importar serviços de busca semântica
sys.path.append(os.path.join(os.path.dirname(__file__), "../../gatekeeper-api"))
try:
    from app.services.vector_search_service import create_vector_search_service
    from app.services.embedding_api_service import embedding_api_service
    from app.database import get_mongo_client
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Busca semântica não disponível: {e}")
    SEMANTIC_SEARCH_AVAILABLE = False

class DocumentQuery(BaseModel):
    """Modelo para queries de documentos"""
    type: Optional[str] = None  # CTE, AWL, BL, MANIFESTO, NF
    identifier: Optional[str] = None  # número da carga, embarque
    client: Optional[str] = None
    status: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None

class DeliveryQuery(BaseModel):
    """Modelo para queries de entregas"""
    delivery_id: Optional[str] = None
    client: Optional[str] = None
    status: Optional[str] = None
    destination: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None

class JourneyQuery(BaseModel):
    """Modelo para queries de jornadas"""
    journey_id: Optional[str] = None
    client: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    status: Optional[str] = None

class FrontendResponse(BaseModel):
    """Resposta estruturada para o frontend"""
    message: str
    action: Optional[str] = None  # "open_modal", "show_document", "display_data"
    data: Optional[Dict[str, Any]] = None
    ui_component: Optional[str] = None  # qual componente usar
    attachments: Optional[List[Dict[str, str]]] = None

class FrontendLogisticsAgent:
    """Agent especializado em integração frontend-backend para logística"""
    
    def __init__(self):
        self.document_keywords = {
            "CTE": ["cte", "ct-e", "conhecimento", "transporte", "frete"],
            "AWL": ["awl", "awb", "air waybill", "aéreo", "avião"],
            "BL": ["bl", "bill of lading", "conhecimento", "marítimo", "navio"],
            "MANIFESTO": ["manifesto", "manifest", "lista", "carga"],
            "NF": ["nf", "nfe", "nf-e", "nota fiscal", "fiscal"]
        }
        
        self.action_keywords = [
            "envie", "enviar", "mandar", "mostrar", "exibir", "ver", "consultar",
            "buscar", "procurar", "encontrar", "localizar", "quero", "preciso",
            "gostaria", "pode", "baixar", "download", "rastrear", "status"
        ]

    def create_agent(self) -> Agent:
        """Cria o agente CrewAI especializado"""
        return Agent(
            role="Frontend Logistics Interface Specialist",
            goal="""Processar mensagens do chat do frontend logistic-pulse e convertê-las 
                    em queries estruturadas para APIs backend, retornando respostas formatadas 
                    para exibição otimizada nos componentes React.""",
            backstory="""Você é um especialista em integração frontend-backend para sistemas 
                        logísticos. Você entende profundamente a arquitetura do logistic-pulse-31-main 
                        e sabe como converter solicitações de usuários em dados estruturados que 
                        alimentam os componentes React (Dashboard, Documentos, Entregas, Jornadas, Chat).""",
            verbose=True,
            tools=[
                self.process_chat_message,
                self.query_documents,
                self.query_deliveries,
                self.query_journeys,
                self.get_dashboard_kpis,
                self.format_frontend_response
            ]
        )

    def process_chat_message(self, user_message: str, user_context: Dict[str, Any]) -> FrontendResponse:
        """
        Processa mensagem do chat e identifica intenção do usuário
        
        Args:
            user_message: Mensagem do usuário
            user_context: Contexto do usuário (nome, empresa, role)
        
        Returns:
            FrontendResponse: Resposta estruturada para o frontend
        """
        message_lower = user_message.lower()
        
        # Detectar tipo de query
        if self._is_document_query(message_lower):
            return self._process_document_query(user_message, user_context)
        elif self._is_delivery_query(message_lower):
            return self._process_delivery_query(user_message, user_context)
        elif self._is_journey_query(message_lower):
            return self._process_journey_query(user_message, user_context)
        elif self._is_status_query(message_lower):
            return self._process_status_query(user_message, user_context)
        else:
            return self._provide_general_help(user_context)

    def _is_document_query(self, message: str) -> bool:
        """Identifica se é uma query de documento"""
        doc_keywords = [word for words in self.document_keywords.values() for word in words]
        return any(keyword in message for keyword in doc_keywords) or "documento" in message

    def _is_delivery_query(self, message: str) -> bool:
        """Identifica se é uma query de entrega"""
        delivery_keywords = ["entrega", "entregar", "destino", "destinatário"]
        return any(keyword in message for keyword in delivery_keywords)

    def _is_journey_query(self, message: str) -> bool:
        """Identifica se é uma query de jornada"""
        journey_keywords = ["jornada", "viagem", "rota", "trajeto", "embarque"]
        return any(keyword in message for keyword in journey_keywords)

    def _is_status_query(self, message: str) -> bool:
        """Identifica se é uma consulta de status"""
        status_keywords = ["status", "situação", "onde está", "andamento", "rastrear"]
        return any(keyword in message for keyword in status_keywords)

    def _process_document_query(self, message: str, context: Dict[str, Any]) -> FrontendResponse:
        """Processa query de documento com busca semântica quando possível"""
        doc_type = self._extract_document_type(message)
        identifier = self._extract_identifier(message)
        
        # Tentar busca semântica se disponível
        if SEMANTIC_SEARCH_AVAILABLE:
            try:
                # Esta seria a implementação assíncrona ideal, mas por compatibilidade com a interface atual
                # mantemos sincrona e usamos threading se necessário
                semantic_results = self._try_semantic_search(message, doc_type)
                
                if semantic_results and len(semantic_results) > 0:
                    document, score = semantic_results[0]
                    
                    return FrontendResponse(
                        message=f"""🔍 **Busca Semântica** - Encontrei um documento com {score:.1%} de relevância!

📋 **Documento Encontrado:**
• Arquivo: {document.original_filename or 'documento-sem-nome'}
• Categoria: {document.category.upper() if document.category else 'N/A'}
• Status: {'Processado' if document.processing_status == 'completed' else 'Processando'}
• Data Upload: {document.uploaded_at.strftime('%d/%m/%Y') if document.uploaded_at else 'N/A'}
• Score de Relevância: {score:.3f}

Este documento foi encontrado usando inteligência artificial para busca semântica.""",
                        action="show_document",
                        data={
                            "id": str(document.id),
                            "type": document.category.upper() if document.category else "DOC",
                            "number": document.original_filename or f"DOC-{str(document.id)[:8]}",
                            "client": context.get("company", "Cliente"),
                            "status": "Validado" if document.processing_status == "completed" else "Processando",
                            "similarity_score": score,
                            "semantic_search": True
                        },
                        ui_component="DocumentDetailModal",
                        attachments=[{
                            "type": document.category.upper() if document.category else "DOC",
                            "name": document.original_filename or f"documento-{str(document.id)[:8]}.pdf",
                            "url": document.s3_url or "#"
                        }]
                    )
            except Exception as e:
                print(f"⚠️ Erro na busca semântica: {e}")
        
        # Fallback para busca tradicional/mock
        query = DocumentQuery(
            type=doc_type,
            identifier=identifier,
            client=context.get("company")
        )
        
        mock_document = {
            "id": "DOC-001",
            "number": f"{doc_type}-2024-001234" if doc_type else "DOC-2024-001234",
            "type": doc_type or "CT-e",
            "client": context.get("company", "Cliente Exemplo"),
            "status": "Validado",
            "upload_date": datetime.now().isoformat(),
            "size": "2.5 MB"
        }
        
        return FrontendResponse(
            message=f"""📋 **Busca Tradicional** - Encontrei o documento solicitado!
            
• Tipo: {mock_document['type']}
• Número: {mock_document['number']}
• Cliente: {mock_document['client']}
• Status: {mock_document['status']}
• Data Upload: {mock_document['upload_date'][:10]}

Você pode visualizar os detalhes completos ou fazer download usando os botões abaixo.""",
            action="show_document",
            data=mock_document,
            ui_component="DocumentDetailModal",
            attachments=[{
                "type": mock_document['type'],
                "name": f"{mock_document['number']}.pdf",
                "url": "#"
            }]
        )
    
    def _try_semantic_search(self, query: str, doc_type: Optional[str] = None) -> List[Tuple[Any, float]]:
        """
        Tenta busca semântica de forma síncrona
        
        Args:
            query: Query de busca
            doc_type: Tipo de documento para filtrar
            
        Returns:
            Lista de tuplas (documento, score_similaridade)
        """
        try:
            import asyncio
            import threading
            from concurrent.futures import ThreadPoolExecutor
            
            # Executar busca semântica em thread separada para manter compatibilidade
            def run_async_search():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    return loop.run_until_complete(self._async_semantic_search(query, doc_type))
                except Exception as e:
                    print(f"⚠️ Erro na execução assíncrona: {e}")
                    return []
                finally:
                    loop.close()
            
            # Usar ThreadPoolExecutor para não bloquear
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_async_search)
                return future.result(timeout=5)  # Timeout de 5 segundos
                
        except Exception as e:
            print(f"⚠️ Erro na busca semântica síncrona: {e}")
            return []
    
    async def _async_semantic_search(self, query: str, doc_type: Optional[str] = None) -> List[Tuple[Any, float]]:
        """
        Busca semântica assíncrona
        
        Args:
            query: Query de busca
            doc_type: Tipo de documento para filtrar
            
        Returns:
            Lista de tuplas (documento, score_similaridade)
        """
        try:
            # Gerar embedding da query
            query_embedding = await embedding_api_service.generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Usar VectorSearchService
            mongo_client = await get_mongo_client()
            vector_search = create_vector_search_service(mongo_client)
            
            # Realizar busca
            results = await vector_search.search_documents(
                query_embedding=query_embedding,
                limit=5,
                min_similarity=0.6,
                category=doc_type.lower() if doc_type else None
            )
            
            return results
            
        except Exception as e:
            print(f"⚠️ Erro na busca semântica assíncrona: {e}")
            return []

    def _process_delivery_query(self, message: str, context: Dict[str, Any]) -> FrontendResponse:
        """Processa query de entrega"""
        identifier = self._extract_identifier(message)
        
        mock_delivery = {
            "id": "ENT-001",
            "client": context.get("company", "Cliente Exemplo"),
            "recipient": "João Silva",
            "destination": "São Paulo/SP",
            "status": "Em Trânsito",
            "estimated_delivery": "2024-01-16 14:00",
            "tracking_url": "#",
            "progress": 65
        }
        
        return FrontendResponse(
            message=f"""Encontrei informações sobre a entrega!

🚚 **Status da Entrega:**
• ID: {mock_delivery['id']}
• Destinatário: {mock_delivery['recipient']}
• Destino: {mock_delivery['destination']}
• Status: {mock_delivery['status']}
• Previsão: {mock_delivery['estimated_delivery']}
• Progresso: {mock_delivery['progress']}%

A entrega está dentro do prazo previsto.""",
            action="open_modal",
            data=mock_delivery,
            ui_component="DeliveryDetailModal"
        )

    def _process_journey_query(self, message: str, context: Dict[str, Any]) -> FrontendResponse:
        """Processa query de jornada"""
        identifier = self._extract_identifier(message)
        
        mock_journey = {
            "id": "JOR-001",
            "client": context.get("company", "Cliente Exemplo"),
            "origin": "São Paulo",
            "destination": "Rio de Janeiro",
            "status": "Em Trânsito",
            "progress": 65,
            "checkpoints": [
                {"name": "Origem", "status": "completed", "date": "2024-01-15 08:00"},
                {"name": "Hub São Paulo", "status": "completed", "date": "2024-01-15 12:00"},
                {"name": "Em Trânsito", "status": "current", "date": "2024-01-15 18:00"},
                {"name": "Destino", "status": "pending", "date": "2024-01-16 14:00"}
            ]
        }
        
        return FrontendResponse(
            message=f"""Encontrei a jornada solicitada!

🛣️ **Jornada Logística:**
• ID: {mock_journey['id']}
• Rota: {mock_journey['origin']} → {mock_journey['destination']}
• Status: {mock_journey['status']}
• Progresso: {mock_journey['progress']}%

A carga está atualmente em trânsito, dentro do cronograma previsto.""",
            action="open_modal",
            data=mock_journey,
            ui_component="JourneyDetailModal"
        )

    def _process_status_query(self, message: str, context: Dict[str, Any]) -> FrontendResponse:
        """Processa consulta de status geral"""
        return FrontendResponse(
            message=f"""Olá {context.get('name', 'usuário')}! 

📊 **Resumo das suas operações hoje:**
• 5 entregas em trânsito
• 2 documentos pendentes de validação  
• 1 jornada concluída
• SLA atual: 94.2%

Precisa de informações específicas sobre alguma carga ou documento?""",
            action="display_data",
            ui_component="StatusSummary"
        )

    def _provide_general_help(self, context: Dict[str, Any]) -> FrontendResponse:
        """Fornece ajuda geral"""
        return FrontendResponse(
            message=f"""Olá {context.get('name', '')}! Como posso ajudá-lo hoje?

💬 **Posso te ajudar com:**
• Consultar documentos logísticos (CT-e, NF-e, BL, Manifesto)
• Verificar status de cargas e entregas
• Acompanhar jornadas em andamento
• Localizar documentos por número de embarque
• Esclarecer dúvidas sobre operações

**Exemplo de comandos:**
- "Consultar CT-e da carga ABC123"
- "Status da entrega para São Paulo"
- "Mostrar jornadas em trânsito"

O que você gostaria de fazer?""",
            ui_component="HelpMenu"
        )

    def _extract_document_type(self, message: str) -> Optional[str]:
        """Extrai o tipo de documento da mensagem"""
        message_lower = message.lower()
        for doc_type, keywords in self.document_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return doc_type
        return None

    def _extract_identifier(self, message: str) -> Optional[str]:
        """Extrai identificador (número de carga, embarque, etc.)"""
        patterns = [
            r'\b\d{6,}\b',  # números com 6+ dígitos
            r'\b[A-Z]{2,}\d{3,}\b',  # letras seguidas de números
            r'\bcarga\s+([A-Z0-9]+)',
            r'\bembarque\s+([A-Z0-9]+)',
            r'\bnúmero\s+([A-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        return None

    def query_documents(self, query: DocumentQuery) -> List[Dict[str, Any]]:
        """
        Ferramenta para buscar documentos via API backend
        Será implementada com chamadas reais para o gatekeeper-api
        """
        # TODO: Implementar integração real com GraphQL/REST API
        pass

    def query_deliveries(self, query: DeliveryQuery) -> List[Dict[str, Any]]:
        """
        Ferramenta para buscar entregas via API backend
        """
        # TODO: Implementar integração real
        pass

    def query_journeys(self, query: JourneyQuery) -> List[Dict[str, Any]]:
        """
        Ferramenta para buscar jornadas via API backend
        """
        # TODO: Implementar integração real
        pass

    def get_dashboard_kpis(self) -> Dict[str, Any]:
        """
        Ferramenta para buscar KPIs do dashboard
        """
        # TODO: Implementar integração real
        pass

    def format_frontend_response(self, raw_data: Dict[str, Any], ui_context: str) -> FrontendResponse:
        """
        Ferramenta para formatar dados backend em resposta otimizada para o frontend
        """
        # TODO: Implementar formatação específica por componente
        pass

# Instância do agente para uso na crew
frontend_logistics_agent = FrontendLogisticsAgent().create_agent()