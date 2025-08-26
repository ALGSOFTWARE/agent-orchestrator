from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging
from ..models import Order, DocumentFile
from ..services.embedding_api_service import embedding_api_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/visualizations", tags=["visualizations"])

from beanie import PydanticObjectId
from bson import ObjectId

@router.get("/graph/order-documents", response_model=Dict[str, Any])
async def get_order_documents_graph(
    order_id: Optional[str] = None,
    limit: int = Query(default=100, le=500, description="Limite de nodes no grafo")
):
    """
    Retorna dados para criar um grafo de relacionamentos entre Orders e DocumentFiles.
    """
    try:
        nodes = []
        edges = []
        
        # Se order_id específico, buscar apenas essa Order e seus documentos
        if order_id:
            # Tornar a busca mais robusta, tentando por _id e por order_id (uuid)
            order = None
            if ObjectId.is_valid(order_id):
                order = await Order.get(PydanticObjectId(order_id))
            
            if not order:
                order = await Order.find_one(Order.order_id == order_id)

            if not order:
                raise HTTPException(status_code=404, detail=f"Order com ID '{order_id}' não encontrada")
                
            nodes.append({
                "id": f"order_{str(order.id)}",
                "type": "order",
                "label": order.title,
                "data": {
                    "id": str(order.id),
                    "title": order.title,
                    "customer": order.customer_name,
                    "status": order.status.value if order.status else None,
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                    "total_documents": 0
                }
            })
            
            documents = await DocumentFile.find(
                DocumentFile.order_id == order.order_id
            ).limit(limit).to_list()
            
            for doc in documents:
                nodes.append({
                    "id": f"doc_{str(doc.id)}",
                    "type": "document",
                    "label": doc.original_name,
                    "data": {
                        "id": str(doc.id),
                        "file_id": doc.file_id,  # ← Adicionar file_id que o frontend precisa
                        "filename": doc.original_name,
                        "file_type": doc.file_type,
                        "category": doc.category,
                        "processing_status": doc.processing_status,
                        "created_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                        "file_size": doc.size_bytes,
                        "extracted_text_preview": doc.text_content[:200] if doc.text_content else None
                    }
                })
                
                edges.append({
                    "source": f"order_{str(order.id)}",
                    "target": f"doc_{str(doc.id)}",
                    "type": "contains"
                })
        
        else:
            orders = await Order.find().limit(limit // 2).to_list()
            
            for order in orders:
                nodes.append({
                    "id": f"order_{str(order.id)}",
                    "type": "order", 
                    "label": order.title,
                    "data": {
                        "id": str(order.id),
                        "title": order.title,
                        "customer": order.customer_name,
                        "status": order.status.value if order.status else None,
                        "created_at": order.created_at.isoformat() if order.created_at else None,
                        "total_documents": 0
                    }
                })
                
                documents = await DocumentFile.find(
                    DocumentFile.order_id == order.order_id
                ).limit(10).to_list()
                
                for doc in documents:
                    nodes.append({
                        "id": f"doc_{str(doc.id)}",
                        "type": "document",
                        "label": doc.original_name,
                        "data": {
                            "id": str(doc.id),
                            "file_id": doc.file_id,  # ← Adicionar file_id aqui também
                            "filename": doc.original_name,
                            "file_type": doc.file_type,
                            "category": doc.category,
                            "processing_status": doc.processing_status,
                            "created_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None
                        }
                    })
                    
                    edges.append({
                        "source": f"order_{str(order.id)}",
                        "target": f"doc_{str(doc.id)}",
                        "type": "contains"
                    })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "orders_count": len([n for n in nodes if n["type"] == "order"]),
                "documents_count": len([n for n in nodes if n["type"] == "document"])
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar grafo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/semantic-map/documents", response_model=Dict[str, Any])
async def get_documents_semantic_map(
    limit: int = Query(default=200, le=1000, description="Limite de documentos para o mapa"),
    method: str = Query(default="tsne", regex="^(tsne|pca)$", description="Método de redução: tsne ou pca"),
    dimensions: int = Query(default=2, ge=2, le=3, description="Dimensões do mapa (2D ou 3D)")
):
    """
    Retorna dados para criar um mapa semântico 2D/3D dos documentos baseado em embeddings.
    """
    try:
        from sklearn.manifold import TSNE
        from sklearn.decomposition import PCA
        import numpy as np
        
        documents = await DocumentFile.find(
            DocumentFile.embedding != None,
            DocumentFile.processing_status == "indexed"
        ).limit(limit).to_list()
        
        if len(documents) < 2:
            raise HTTPException(
                status_code=400, 
                detail="Não há documentos suficientes com embeddings para criar o mapa"
            )
        
        embeddings = []
        doc_data = []
        
        for doc in documents:
            if doc.embedding and len(doc.embedding) > 0:
                embeddings.append(doc.embedding)
                doc_data.append({
                    "id": f"doc_{str(doc.id)}",
                    "label": doc.original_name,
                    "category": doc.category,
                    "order_id": str(doc.order_id) if doc.order_id else None,
                    "data": {
                        "id": str(doc.id),
                        "file_id": doc.file_id,  # ← Adicionar file_id no mapa semântico também
                        "filename": doc.original_name,
                        "file_type": doc.file_type,
                        "category": doc.category,
                        "processing_status": doc.processing_status,
                        "created_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                        "extracted_text_preview": doc.text_content[:200] if doc.text_content else None,
                        "order_id": str(doc.order_id) if doc.order_id else None
                    }
                })
        
        if len(embeddings) < 2:
            raise HTTPException(
                status_code=400,
                detail="Não há embeddings válidos suficientes para criar o mapa"
            )
        
        X = np.array(embeddings)
        
        if method == "tsne":
            reducer = TSNE(
                n_components=dimensions, 
                random_state=42, 
                perplexity=min(30, len(embeddings) - 1)
            )
        else:
            reducer = PCA(n_components=dimensions, random_state=42)
        
        X_reduced = reducer.fit_transform(X)
        
        points = []
        for i, (coords, doc_info) in enumerate(zip(X_reduced, doc_data)):
            point = {
                "id": doc_info["id"],
                "x": float(coords[0]),
                "y": float(coords[1]),
                "label": doc_info["label"],
                "category": doc_info["category"],
                "order_id": doc_info["order_id"],
                "data": doc_info["data"]
            }
            
            if dimensions == 3:
                point["z"] = float(coords[2])
                
            points.append(point)
        
        clusters = {}
        colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7", "#dda0dd", "#98d8c8"]
        
        for point in points:
            category = point["category"] or "Sem categoria"
            if category not in clusters:
                clusters[category] = {
                    "name": category,
                    "color": colors[len(clusters) % len(colors)],
                    "documents": []
                }
            clusters[category]["documents"].append(point["id"])
        
        return {
            "points": points,
            "clusters": list(clusters.values()),
            "stats": {
                "total_documents": len(points),
                "dimensions": dimensions,
                "method": method,
                "categories_count": len(clusters)
            },
            "method_info": {
                "name": method.upper(),
                "description": "t-SNE para melhor separação de clusters" if method == "tsne" 
                              else "PCA para preservar variância global"
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar mapa semântico: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/semantic-search/similar", response_model=Dict[str, Any])
async def get_similar_documents_visual(
    query: str = Query(..., description="Consulta em linguagem natural"),
    limit: int = Query(10, description="Número máximo de resultados"),
    min_similarity: float = Query(0.5, description="Similaridade mínima (0-1)"),
    order_id: Optional[str] = Query(None, description="Filtrar por Order específica")
):
    """
    Busca semântica de documentos para visualização.
    """
    if not embedding_api_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Serviço de busca semântica não disponível."
        )
    
    try:
        results = await embedding_api_service.find_similar_documents(
            query_text=query,
            limit=limit,
            min_similarity=min_similarity,
            order_id=order_id
        )
        
        formatted_results = []
        for doc, similarity in results:
            formatted_results.append({
                "id": f"doc_{str(doc.id)}",
                "label": doc.original_name,
                "type": "document",
                "data": {
                    "id": str(doc.id),
                    "file_id": doc.file_id,  # ← Adicionar file_id na busca semântica também
                    "similarity": similarity,
                    "extracted_text_preview": doc.text_content[:200] if doc.text_content else None,
                    "category": doc.category,
                    "order_id": doc.order_id
                }
            })

        return {
            "query": query,
            "similar_documents": formatted_results
        }

    except Exception as e:
        logger.error(f"Erro na busca semântica visual: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno na busca: {str(e)}")