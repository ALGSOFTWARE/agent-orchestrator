"""Routes for semantic document and order event vectors."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ..middleware.auth import get_current_user
from ..models import OrderEventKind
from ..services.semantic_index_service import SemanticIndexService

router = APIRouter()
semantic_service = SemanticIndexService()


class DocumentVectorChunk(BaseModel):
    """Payload unit for document vectorization."""

    chunk_id: Optional[str] = Field(None, description="Identificador lógico do chunk")
    chunk_index: Optional[int] = Field(None, ge=0, description="Posição do chunk no documento")
    text: str = Field(..., min_length=1, description="Trecho utilizado para embedding")
    embedding: List[float] = Field(..., description="Embedding do chunk")
    embedding_model: Optional[str] = Field(None, description="Modelo de embedding utilizado")
    source_category: Optional[str] = Field(None, description="Categoria do documento de origem")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    relevance_score: Optional[float] = Field(None, description="Score opcional atribuído na ingestão")


class DocumentVectorsUpsertRequest(BaseModel):
    order_id: str = Field(..., description="Order relacionada aos chunks")
    chunks: List[DocumentVectorChunk]


class OrderEventVectorRequest(BaseModel):
    event_id: str = Field(..., description="Identificador único do evento")
    summary: str = Field(..., min_length=1, description="Resumo utilizado para embedding")
    embedding: List[float] = Field(..., description="Embedding do evento")
    embedding_model: str = Field(..., description="Modelo utilizado na vetorização")
    event_type: OrderEventKind = Field(..., description="Tipo do evento")
    event_timestamp: Optional[datetime] = Field(None, description="Timestamp original do evento")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    related_document_ids: Optional[List[str]] = Field(default_factory=list)


@router.post("/documents/{source_document_id}")
async def upsert_document_vectors(
    source_document_id: str,
    payload: DocumentVectorsUpsertRequest,
    _current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Registra embeddings de chunks derivados de um documento."""

    if not payload.chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="É necessário enviar ao menos um chunk para indexação."
        )

    vectors = await semantic_service.upsert_document_vectors(
        order_id=payload.order_id,
        source_document_id=source_document_id,
        chunks=[chunk.dict() for chunk in payload.chunks],
    )

    response_payload = [
        {
            "vector_id": str(vector.id),
            "chunk_id": vector.chunk_id,
            "chunk_index": vector.chunk_index,
            "order_id": vector.order_id,
            "source_document_id": vector.source_document_id,
            "embedding_model": vector.embedding_model,
            "relevance_score": vector.relevance_score,
            "updated_at": vector.updated_at.isoformat(),
        }
        for vector in vectors
    ]

    return {"count": len(response_payload), "vectors": response_payload}


@router.get("/documents")
async def list_document_vectors(
    order_id: Optional[str] = Query(None, description="Filtrar por order"),
    source_document_id: Optional[str] = Query(None, description="Filtrar por documento original"),
    limit: int = Query(50, ge=1, le=500, description="Limite de vetores retornados"),
    include_embedding: bool = Query(False, description="Se verdadeiro, inclui o embedding completo."),
    _current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Lista vetores armazenados para uma order ou documento."""

    vectors = await semantic_service.list_document_vectors(
        order_id=order_id,
        source_document_id=source_document_id,
        limit=limit,
    )

    response_payload = []
    for vector in vectors:
        item = {
            "vector_id": str(vector.id),
            "chunk_id": vector.chunk_id,
            "chunk_index": vector.chunk_index,
            "order_id": vector.order_id,
            "source_document_id": vector.source_document_id,
            "embedding_model": vector.embedding_model,
            "source_category": vector.source_category,
            "updated_at": vector.updated_at.isoformat(),
        }
        if include_embedding:
            item["embedding"] = vector.embedding
        response_payload.append(item)

    return {"count": len(response_payload), "vectors": response_payload}


@router.delete("/documents/{source_document_id}")
async def delete_document_vectors(
    source_document_id: str,
    _current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Remove vetores vinculados a um documento específico."""

    deleted_count = await semantic_service.delete_document_vectors(
        source_document_id=source_document_id
    )

    return {"deleted": deleted_count}


@router.post("/orders/{order_id}/events")
async def register_order_event_vector(
    order_id: str,
    payload: OrderEventVectorRequest,
    _current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Registra embedding associado a um evento relevante da order."""

    event_vector = await semantic_service.register_order_event_vector(
        order_id=order_id,
        event_id=payload.event_id,
        summary=payload.summary,
        embedding=payload.embedding,
        embedding_model=payload.embedding_model,
        event_type=payload.event_type,
        event_timestamp=payload.event_timestamp,
        metadata=payload.metadata,
        related_document_ids=payload.related_document_ids,
    )

    return {
        "vector_id": str(event_vector.id),
        "order_id": event_vector.order_id,
        "event_id": event_vector.event_id,
        "event_type": event_vector.event_type,
        "event_timestamp": event_vector.event_timestamp.isoformat(),
        "embedding_model": event_vector.embedding_model,
        "updated_at": event_vector.updated_at.isoformat(),
    }


@router.get("/orders/{order_id}/events")
async def list_order_event_vectors(
    order_id: str,
    limit: int = Query(50, ge=1, le=200, description="Limite de eventos retornados"),
    include_embedding: bool = Query(False, description="Se verdadeiro, inclui o embedding completo."),
    _current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Lista embeddings de eventos associados a uma order."""

    events = await semantic_service.list_order_event_vectors(order_id=order_id, limit=limit)

    response_payload = []
    for event in events:
        item = {
            "vector_id": str(event.id),
            "order_id": event.order_id,
            "event_id": event.event_id,
            "event_type": event.event_type,
            "event_timestamp": event.event_timestamp.isoformat(),
            "embedding_model": event.embedding_model,
            "updated_at": event.updated_at.isoformat(),
            "related_document_ids": event.related_document_ids,
        }
        if include_embedding:
            item["embedding"] = event.embedding
        response_payload.append(item)

    return {"count": len(response_payload), "events": response_payload}


@router.delete("/orders/events/{event_id}")
async def delete_order_event_vector(
    event_id: str,
    _current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Remove embedding associado a um evento específico da order."""

    deleted = await semantic_service.delete_order_event_vector(event_id=event_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado ou já removido."
        )

    return {"deleted": True}
