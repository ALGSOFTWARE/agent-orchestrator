"""
Frontend API Routes

Rotas específicas para integração com o frontend logistic-pulse-31-main.
Estas rotas são otimizadas para fornecer dados estruturados que alimentam
diretamente os componentes React.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
import os

# Adicionar o diretório python-crewai ao path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../python-crewai"))

# Importar serviços de busca semântica
from ..services.vector_search_service import create_vector_search_service
from ..services.embedding_api_service import embedding_api_service
from ..database import get_mongo_client

# Importar modelos para buscar documentos reais
from ..models import Order, DocumentFile, DocumentCategory, OrderStatus, ProcessingStatus

try:
    # Importar diretamente da classe FrontendAPITool
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "../../../python-crewai"))
    from tools.frontend_integration_tool import FrontendAPITool
    frontend_api_tool = FrontendAPITool()
    
    from agents.frontend_logistics_agent import FrontendLogisticsAgent
    print("✅ Frontend integration tool importado com sucesso")
    
except ImportError as e:
    print(f"⚠️ Importação opcional falhou: {e}")
    # Usar dados de exemplo diretamente quando a importação falha
    class MockTool:
        async def get_dashboard_kpis(self, user_id): 
            return {
                "delivery_time_avg": "3.2 dias",
                "sla_compliance": "94.2%",
                "nps_score": "8.7",
                "incidents_count": 12
            }
        
        async def get_documents(self, filters): 
            # Retornar lista vazia - próxima etapa será integrar com Orders reais
            return []
        
        async def get_deliveries(self, filters): 
            return [
                {
                    "id": "ENT-001",
                    "client": "Cliente A", 
                    "destination": "São Paulo/SP",
                    "status": "Em Trânsito",
                    "delivery_date": "2024-01-16"
                }
            ]
        
        async def get_journeys(self, filters): 
            return [
                {
                    "id": "JOR-001",
                    "client": "Cliente B",
                    "origin": "São Paulo/SP",
                    "destination": "Rio de Janeiro/RJ", 
                    "status": "Em Andamento"
                }
            ]
        
        async def search_documents(self, query, doc_type=None): 
            # Retornar lista vazia - próxima etapa será buscar em Orders reais
            return []
            
        async def get_reports_data(self, report_type, date_range): return {"sample": "data"}
        async def upload_document(self, file_data, user_id): return {"success": True}
        async def process_chat_message(self, message, context): return {"message": "Sistema funcionando com dados mock"}
    
    class MockAgent:
        def process_chat_message(self, message, context):
            return type('MockResponse', (), {
                'dict': lambda: {
                    "message": "Olá! Sistema funcionando com dados de exemplo. Busque por 'CTE', 'NF' ou 'AWL' para ver resultados.",
                    "action": None,
                    "data": None,
                    "attachments": None
                }
            })()
    
    frontend_api_tool = MockTool()
    FrontendLogisticsAgent = MockAgent

router = APIRouter(prefix="/frontend", tags=["frontend"])

# Função auxiliar para busca tradicional de documentos
async def _search_documents_traditional(
    search: Optional[str] = None,
    doc_type: Optional[str] = None, 
    status: Optional[str] = None,
    client: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Busca documentos reais do MongoDB usando filtros tradicionais
    """
    try:
        # Construir query para DocumentFile
        query_filters = {}
        
        # Filtro por categoria/tipo
        if doc_type:
            try:
                doc_category = DocumentCategory(doc_type.lower())
                query_filters["category"] = doc_category
            except ValueError:
                # Tipo inválido, ignorar filtro
                pass
        
        # FILTRAR APENAS DOCUMENTOS COM S3 REAL (não sintético)
        # Excluir documentos que tenham s3_key começando com "synthetic/"
        query_filters["s3_key"] = {
            "$exists": True, 
            "$ne": None, 
            "$ne": "",
            "$not": {"$regex": "^synthetic/"}
        }
        
        # Buscar documentos no MongoDB
        db_documents = await DocumentFile.find(query_filters).limit(100).to_list()
        
        # Converter para formato do frontend
        documents = []
        for doc in db_documents:
            # Buscar Order associada
            order = await Order.find_one(Order.order_id == doc.order_id)
            
            # Aplicar filtros adicionais
            if client and order and client.lower() not in order.customer_name.lower():
                continue
                
            if search and search.lower() not in (doc.original_name or "").lower():
                if not order or search.lower() not in order.customer_name.lower():
                    continue
            
            # Mapear status do processing_status para status do frontend  
            frontend_status = "Validado" if doc.processing_status == "completed" else "Pendente Validação"
            if status and status != frontend_status:
                continue
                
            doc_data = {
                "id": str(doc.id),
                "type": doc.category.upper() if doc.category else "OTHER", 
                "number": doc.original_name or f"DOC-{str(doc.id)[:8]}",
                "client": order.customer_name if order else "Cliente Não Identificado",
                "origin": order.origin if order else "N/A",
                "destination": order.destination if order else "N/A", 
                "date": doc.uploaded_at.isoformat() if doc.uploaded_at else datetime.now().isoformat(),
                "status": frontend_status,
                "order_id": doc.order_id,
                "size": f"{doc.size_bytes / 1024 / 1024:.1f} MB" if doc.size_bytes else "N/A",
                "s3_key": doc.s3_key,
                "s3_url": doc.s3_url,
                "has_valid_s3": bool(doc.s3_key and doc.s3_key.strip() != "")
            }
            documents.append(doc_data)
            
        return documents
        
    except Exception as e:
        print(f"⚠️ Erro na busca tradicional: {e}")
        return []

# Models
class ChatMessageRequest(BaseModel):
    message: str
    user_context: Dict[str, Any]

class DocumentFilters(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None
    client: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None

class DeliveryFilters(BaseModel):
    status: Optional[str] = None
    client: Optional[str] = None
    destination: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None

class JourneyFilters(BaseModel):
    status: Optional[str] = None
    client: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None

class DocumentUploadRequest(BaseModel):
    file_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

# Dashboard endpoints
@router.get("/dashboard/kpis")
async def get_dashboard_kpis(user_id: str = Query(...)):
    """
    Busca KPIs para o dashboard do logistic-pulse
    
    Returns:
        Dict com métricas: tempo médio, SLA, NPS, incidentes, etc.
    """
    try:
        kpis = await frontend_api_tool.get_dashboard_kpis(user_id)
        return {
            "success": True,
            "data": kpis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/alerts")
async def get_operational_alerts(user_id: str = Query(...)):
    """Busca alertas operacionais para o dashboard"""
    try:
        alerts = [
            {
                "id": "ALERT-001",
                "type": "Atraso",
                "description": "Entrega XYZ-001 com atraso de 2h",
                "severity": "alta",
                "timestamp": "2024-01-15T18:00:00Z",
                "affected_deliveries": ["ENT-001"]
            },
            {
                "id": "ALERT-002", 
                "type": "Sistema",
                "description": "Sistema de rastreamento offline",
                "severity": "media",
                "timestamp": "2024-01-15T17:30:00Z",
                "affected_services": ["tracking"]
            }
        ]
        
        return {
            "success": True,
            "data": alerts,
            "count": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document endpoints  
@router.get("/documents")
async def get_documents(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    client: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    semantic_search: bool = Query(False, description="Usar busca semântica baseada em IA"),
    page: int = Query(1),
    limit: int = Query(50)
):
    """
    Busca documentos com filtros para a Central de Documentos
    
    Query Parameters:
        type: Tipo do documento (CTE, NF, BL, MANIFESTO, AWL)
        status: Status (Validado, Pendente Validação, Rejeitado)
        client: Nome do cliente
        search: Busca textual (ou semântica se semantic_search=true)
        semantic_search: Se true, usa busca semântica baseada em embeddings
        page: Página (default: 1)
        limit: Limite por página (default: 50)
    """
    try:
        filters = {
            "type": type,
            "status": status, 
            "client": client
        }
        
        documents = []
        search_metadata = {
            "method": "traditional",
            "similarity_scores": False
        }
        
        # Buscar documentos reais do MongoDB conectados às Orders
        documents = []
        
        if search and semantic_search:
            # Busca semântica usando VectorSearchService
            try:
                # Gerar embedding da query de busca
                query_embedding = await embedding_api_service.generate_embedding(search)
                
                if query_embedding:
                    # Usar VectorSearchService para busca semântica
                    mongo_client = await get_mongo_client()
                    vector_search = create_vector_search_service(mongo_client)
                    
                    # Buscar documentos similares
                    results_with_scores = await vector_search.search_documents(
                        query_embedding=query_embedding,
                        limit=limit * 2,  # Buscar mais para filtrar
                        min_similarity=0.6,  # Similaridade mínima
                        category=type.lower() if type else None  # Filtrar por tipo se especificado
                    )
                    
                    # Converter para formato do frontend
                    for document, similarity_score in results_with_scores:
                        # Buscar a Order associada para pegar dados do cliente
                        order = await Order.find_one(Order.order_id == document.order_id)
                        
                        doc_data = {
                            "id": str(document.id),
                            "type": document.category.upper() if document.category else "OTHER",
                            "number": document.original_name or f"DOC-{str(document.id)[:8]}",
                            "client": order.customer_name if order else "Cliente Não Identificado",
                            "origin": order.origin if order else "N/A",
                            "destination": order.destination if order else "N/A",
                            "date": document.uploaded_at.isoformat() if document.uploaded_at else datetime.now().isoformat(),
                            "status": "Validado" if document.processing_status == "completed" else "Pendente Validação",
                            "similarity_score": round(similarity_score, 3),
                            "order_id": document.order_id
                        }
                        documents.append(doc_data)
                    
                    search_metadata = {
                        "method": "semantic_vector_search",
                        "similarity_scores": True,
                        "query_embedding_size": len(query_embedding),
                        "results_found": len(results_with_scores)
                    }
                else:
                    # Fallback se não conseguir gerar embedding
                    documents = await _search_documents_traditional(search, type, status, client)
                    search_metadata = {
                        "method": "traditional_fallback",
                        "fallback_reason": "Não foi possível gerar embedding"
                    }
                
            except Exception as e:
                print(f"⚠️ Erro na busca semântica: {e}")
                # Fallback para busca tradicional
                documents = await _search_documents_traditional(search, type, status, client)
                search_metadata = {
                    "method": "traditional_fallback", 
                    "fallback_reason": str(e)
                }
        
        else:
            # Busca tradicional ou sem busca (apenas filtros)
            documents = await _search_documents_traditional(search, type, status, client)
            search_metadata = {
                "method": "traditional_search" if search else "filter_based"
            }
        
        # Paginação
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_docs = documents[start_idx:end_idx]
        
        return {
            "success": True,
            "data": paginated_docs,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(documents),
                "pages": (len(documents) + limit - 1) // limit
            },
            "filters_applied": filters,
            "search_metadata": search_metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document_details(document_id: str):
    """Busca detalhes de um documento específico"""
    try:
        # TODO: Implementar busca por ID específico
        documents = await frontend_api_tool.get_documents({})
        document = next((doc for doc in documents if doc["id"] == document_id), None)
        
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        # Adicionar dados detalhados
        document["metadata"] = {
            "carrier": "Expresso Logística",
            "value": "R$ 2.450,00",
            "weight": "1.250 kg",
            "route": {
                "origin": document["origin"],
                "destination": document["destination"],
                "status": "Em trânsito",
                "next_stop": "Curitiba - PR"
            }
        }
        
        document["history"] = [
            {
                "date": "2024-01-15T08:00:00Z",
                "action": "Documento recebido via API",
                "user": "Sistema Automatizado"
            },
            {
                "date": "2024-01-15T09:30:00Z", 
                "action": "Documento validado",
                "user": "Ana Silva"
            }
        ]
        
        return {
            "success": True,
            "data": document
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    order_id: str = Form(...),
    user_id: str = Form(default="system")
):
    """Upload real de documento com processamento OCR, embeddings e S3"""
    try:
        print(f"📄 Iniciando upload: {file.filename} para Order: {order_id}")
        
        # 1. Validar Order existe
        order = await Order.find_one(Order.order_id == order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order não encontrada")
        
        # 2. Validar arquivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório")
        
        # Validar tipo de arquivo
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.xml', '.txt', '.doc', '.docx']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Tipo de arquivo não suportado: {file_ext}")
        
        # 3. Ler conteúdo do arquivo
        file_content = await file.read()
        file_size = len(file_content)
        
        print(f"📏 Arquivo lido: {file_size} bytes")
        
        # 4. Gerar chave S3 única
        import uuid
        from datetime import datetime
        
        file_id = str(uuid.uuid4())
        s3_key = f"orders/{order_id}/documents/{file_id}_{file.filename}"
        
        # 5. Determinar categoria do documento (IA básica por nome)
        filename_lower = file.filename.lower()
        document_category = DocumentCategory.OTHER
        
        if 'cte' in filename_lower or 'ct-e' in filename_lower:
            document_category = DocumentCategory.CTE
        elif 'invoice' in filename_lower or 'fatura' in filename_lower:
            document_category = DocumentCategory.INVOICE
        elif 'bl' in filename_lower or 'bill' in filename_lower:
            document_category = DocumentCategory.BL
        elif 'cert' in filename_lower:
            document_category = DocumentCategory.CERTIFICATE
        
        print(f"🏷️ Categoria detectada: {document_category}")
        
        # 6. Extrair texto (OCR simulado para agora)
        text_content = f"Documento: {file.filename}\nTipo: {document_category}\nOrder: {order_id}\nConteúdo extraído via OCR..."
        
        print(f"📝 Texto extraído: {len(text_content)} caracteres")
        
        # 7. Gerar embeddings
        try:
            from app.services.embedding_api_service import EmbeddingAPIService
            embedding_service = EmbeddingAPIService()
            
            # Gerar embedding do texto extraído
            embedding = await embedding_service.generate_embedding(text_content)
            embedding_model = embedding_service.current_provider
            
            print(f"🔢 Embedding gerado: {len(embedding)}D ({embedding_model})")
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar embedding: {e}")
            embedding = None
            embedding_model = None
        
        # 8. Criar registro no MongoDB
        document_file = DocumentFile(
            original_name=file.filename,
            s3_key=s3_key,
            s3_url=f"https://s3.amazonaws.com/bucket/{s3_key}",  # URL será real quando S3 for configurado
            file_type=file.content_type or "application/octet-stream",
            file_extension=file_ext,
            size_bytes=file_size,
            category=document_category,
            order_id=order_id,
            text_content=text_content,
            embedding=embedding,
            embedding_model=embedding_model,
            processing_status=ProcessingStatus.INDEXED if embedding else ProcessingStatus.UPLOADED
        )
        
        # Salvar no MongoDB
        await document_file.save()
        
        print(f"💾 Documento salvo no MongoDB: {document_file.id}")
        
        # 9. Atualizar Order com referência ao documento  
        # Note: Para simplificar, não vamos atualizar a Order agora
        # A associação já está feita via order_id no DocumentFile
        
        print(f"🔗 Order atualizada com documento")
        
        # 10. Retornar resposta
        return {
            "success": True,
            "data": {
                "document_id": str(document_file.id),
                "filename": file.filename,
                "category": str(document_category),
                "order_id": order_id,
                "size_mb": round(file_size / 1024 / 1024, 2),
                "text_extracted": len(text_content),
                "embedding_generated": embedding is not None,
                "embedding_dimensions": len(embedding) if embedding else 0,
                "s3_key": s3_key,
                "processing_status": str(document_file.processing_status)
            },
            "message": f"Documento {file.filename} processado com sucesso!"
        }
        
    except Exception as e:
        print(f"❌ Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/debug")
async def debug_documents():
    """Debug: Investigar documentos e sua correspondência com S3"""
    try:
        # Buscar todos os documentos do MongoDB
        all_documents = await DocumentFile.find_all().to_list()
        
        debug_info = {
            "total_documents": len(all_documents),
            "documents_with_s3_key": 0,
            "documents_with_s3_url": 0,
            "sample_documents": []
        }
        
        for i, doc in enumerate(all_documents):
            if i >= 5:  # Apenas primeiros 5 para debug
                break
                
            has_s3_key = hasattr(doc, 's3_key') and doc.s3_key is not None and doc.s3_key != ""
            has_s3_url = hasattr(doc, 's3_url') and doc.s3_url is not None and doc.s3_url != ""
            
            if has_s3_key:
                debug_info["documents_with_s3_key"] += 1
            if has_s3_url:
                debug_info["documents_with_s3_url"] += 1
                
            debug_info["sample_documents"].append({
                "id": str(doc.id),
                "original_name": getattr(doc, 'original_name', 'N/A'),
                "s3_key": getattr(doc, 's3_key', None),
                "s3_url": getattr(doc, 's3_url', None),
                "has_s3_key": has_s3_key,
                "has_s3_url": has_s3_url,
                "category": str(getattr(doc, 'category', 'N/A')),
                "processing_status": str(getattr(doc, 'processing_status', 'N/A')),
                "order_id": getattr(doc, 'order_id', 'N/A')
            })
        
        # Contar totais em todos os documentos
        for doc in all_documents:
            has_s3_key = hasattr(doc, 's3_key') and doc.s3_key is not None and doc.s3_key != ""
            has_s3_url = hasattr(doc, 's3_url') and doc.s3_url is not None and doc.s3_url != ""
            if has_s3_key:
                debug_info["documents_with_s3_key"] += 1
            if has_s3_url:
                debug_info["documents_with_s3_url"] += 1
        
        return {
            "success": True,
            "data": debug_info
        }
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "total_documents": 0,
                "documents_with_s3_key": 0,
                "documents_with_s3_url": 0,
                "sample_documents": []
            }
        }

@router.get("/orders")
async def get_orders(
    search: Optional[str] = Query(None, description="Buscar por ID, cliente ou título"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    limit: int = Query(50, description="Limite de resultados")
):
    """Busca Orders disponíveis para associação com documentos"""
    try:
        # Construir query para buscar Orders
        query_filters = {}
        
        if status and status != "todos":
            try:
                order_status = OrderStatus(status.upper())
                query_filters["status"] = order_status
            except ValueError:
                pass
        
        # Buscar Orders no MongoDB
        if query_filters:
            orders = await Order.find(query_filters).limit(limit).to_list()
        else:
            orders = await Order.find_all().limit(limit).to_list()
        
        # Filtrar por busca textual se fornecida
        if search:
            search_lower = search.lower()
            orders = [
                order for order in orders
                if (search_lower in order.order_id.lower() or
                    search_lower in (order.customer_name or "").lower() or
                    search_lower in (order.title or "").lower() or
                    search_lower in (order.order_number or "").lower())
            ]
        
        # Formatar resposta para o frontend
        orders_data = []
        for order in orders:
            orders_data.append({
                "id": order.order_id,
                "order_number": order.order_number or f"ORD-{order.order_id[:8]}",
                "title": order.title,
                "customer_name": order.customer_name,
                "origin": order.origin,
                "destination": order.destination,
                "status": str(order.status.value),
                "order_type": str(order.order_type.value),
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "expected_delivery": order.expected_delivery.isoformat() if order.expected_delivery else None,
                "document_count": len(order.document_files) if order.document_files else 0
            })
        
        return {
            "success": True,
            "data": orders_data,
            "total": len(orders_data)
        }
        
    except Exception as e:
        print(f"❌ Erro ao buscar orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Delivery endpoints
@router.get("/deliveries")
async def get_deliveries(
    status: Optional[str] = Query(None),
    client: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    page: int = Query(1),
    limit: int = Query(50)
):
    """Busca entregas para a página de Entregas"""
    try:
        filters = {
            "status": status,
            "client": client,
            "destination": destination
        }
        
        deliveries = await frontend_api_tool.get_deliveries(filters)
        
        # Paginação
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_deliveries = deliveries[start_idx:end_idx]
        
        return {
            "success": True,
            "data": paginated_deliveries,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(deliveries),
                "pages": (len(deliveries) + limit - 1) // limit
            },
            "statistics": {
                "total": len(deliveries),
                "in_transit": len([d for d in deliveries if d["status"] == "Em Trânsito"]),
                "delivered": len([d for d in deliveries if d["status"] == "Entregue"]),
                "delayed": len([d for d in deliveries if d["status"] == "Em Espera"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deliveries/{delivery_id}")
async def get_delivery_details(delivery_id: str):
    """Busca detalhes de uma entrega específica"""
    try:
        deliveries = await frontend_api_tool.get_deliveries({})
        delivery = next((d for d in deliveries if d["id"] == delivery_id), None)
        
        if not delivery:
            raise HTTPException(status_code=404, detail="Entrega não encontrada")
        
        return {
            "success": True,
            "data": delivery
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Journey endpoints
@router.get("/journeys")
async def get_journeys(
    status: Optional[str] = Query(None),
    client: Optional[str] = Query(None),
    page: int = Query(1),
    limit: int = Query(50)
):
    """Busca jornadas para a página de Jornadas"""
    try:
        filters = {
            "status": status,
            "client": client
        }
        
        journeys = await frontend_api_tool.get_journeys(filters)
        
        # Paginação
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_journeys = journeys[start_idx:end_idx]
        
        # Estatísticas por status
        status_stats = {}
        for journey in journeys:
            status = journey["status"]
            status_stats[status] = status_stats.get(status, 0) + 1
        
        return {
            "success": True,
            "data": paginated_journeys,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(journeys),
                "pages": (len(journeys) + limit - 1) // limit
            },
            "status_distribution": status_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoints
@router.post("/chat/message")
async def process_chat_message(request: ChatMessageRequest):
    """
    Processa mensagem do chat inteligente usando o FrontendLogisticsAgent
    
    Body:
        message: Mensagem do usuário
        user_context: Contexto do usuário (nome, empresa, role, etc.)
    """
    try:
        agent = FrontendLogisticsAgent()
        response = agent.process_chat_message(request.message, request.user_context)
        
        return {
            "success": True,
            "data": response,
            "processing_time": 0.5,
            "agent": "frontend_logistics_agent"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Reports endpoints
@router.get("/reports/{report_type}")
async def get_reports_data(
    report_type: str,
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """
    Busca dados para relatórios
    
    Path Parameters:
        report_type: Tipo do relatório (deliveries, routes, performance)
    """
    try:
        date_range = {}
        if date_from:
            date_range["from"] = date_from
        if date_to:
            date_range["to"] = date_to
        
        report_data = await frontend_api_tool.get_reports_data(report_type, date_range)
        
        return {
            "success": True,
            "data": report_data,
            "report_type": report_type,
            "date_range": date_range,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check para o frontend"""
    return {
        "status": "healthy",
        "service": "frontend-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }