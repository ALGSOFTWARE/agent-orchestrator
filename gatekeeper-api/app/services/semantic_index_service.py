"""Semantic Index Service

Mantém coleções de vetores derivados de documentos e eventos de Order.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from ..models import DocumentVector, OrderEventKind, OrderEventVector


class SemanticIndexService:
    """Orquestra operações de manutenção no índice semântico."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("GatekeeperAPI.SemanticIndex")

    async def upsert_document_vectors(
        self,
        *,
        order_id: str,
        source_document_id: str,
        chunks: Iterable[Dict[str, Any]],
    ) -> List[DocumentVector]:
        """Insere ou atualiza chunks vetorizados de um `DocumentFile`."""

        saved: List[DocumentVector] = []
        utc_now = datetime.utcnow()

        for index, chunk in enumerate(chunks):
            text = (chunk.get("text") or "").strip()
            embedding = chunk.get("embedding")

            if not text or not embedding:
                self.logger.debug("Ignorando chunk vazio ou sem embedding (%s)", chunk)
                continue

            chunk_index = chunk.get("chunk_index", index)
            chunk_id = chunk.get("chunk_id") or f"{source_document_id}:{chunk_index}"
            text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            metadata = chunk.get("metadata") or {}

            existing = await DocumentVector.find_one(
                DocumentVector.source_document_id == source_document_id,
                DocumentVector.chunk_id == chunk_id,
            )

            if not existing:
                existing = await DocumentVector.find_one(
                    DocumentVector.source_document_id == source_document_id,
                    DocumentVector.text_hash == text_hash,
                )

            if existing:
                existing.text = text
                existing.text_hash = text_hash
                existing.embedding = embedding
                existing.embedding_model = chunk.get("embedding_model") or existing.embedding_model
                existing.source_category = chunk.get("source_category") or existing.source_category
                existing.metadata = metadata
                existing.relevance_score = chunk.get("relevance_score")
                existing.chunk_index = chunk_index
                existing.updated_at = utc_now
                await existing.save()
                saved.append(existing)
                continue

            created = DocumentVector(
                order_id=order_id,
                source_document_id=source_document_id,
                chunk_id=chunk_id,
                chunk_index=chunk_index,
                text=text,
                text_hash=text_hash,
                embedding=embedding,
                embedding_model=chunk.get("embedding_model") or "unknown",
                source_category=chunk.get("source_category"),
                metadata=metadata,
                relevance_score=chunk.get("relevance_score"),
                created_at=utc_now,
                updated_at=utc_now,
            )
            await created.insert()
            saved.append(created)

        return saved

    async def list_document_vectors(
        self,
        *,
        order_id: Optional[str] = None,
        source_document_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[DocumentVector]:
        """Retorna chunks vetorizados filtrando por order ou documento."""

        filters: Dict[str, Any] = {}
        if order_id:
            filters["order_id"] = order_id
        if source_document_id:
            filters["source_document_id"] = source_document_id

        query = DocumentVector.find(filters or {})
        results = await query.sort(DocumentVector.chunk_index).limit(limit).to_list()
        return results

    async def delete_document_vectors(self, *, source_document_id: str) -> int:
        """Remove todos os vetores associados a um `DocumentFile`."""

        delete_result = await DocumentVector.find(
            DocumentVector.source_document_id == source_document_id
        ).delete()
        return getattr(delete_result, "deleted_count", 0)

    async def register_order_event_vector(
        self,
        *,
        order_id: str,
        event_id: str,
        summary: str,
        embedding: List[float],
        embedding_model: str,
        event_type: OrderEventKind,
        event_timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        related_document_ids: Optional[List[str]] = None,
    ) -> OrderEventVector:
        """Insere ou atualiza embedding responsável por um evento de Order."""

        text_hash = hashlib.sha256(summary.strip().encode("utf-8")).hexdigest()
        existing = await OrderEventVector.find_one(
            OrderEventVector.order_id == order_id,
            OrderEventVector.event_id == event_id,
        )

        if not existing:
            existing = await OrderEventVector.find_one(
                OrderEventVector.order_id == order_id,
                OrderEventVector.text_hash == text_hash,
            )

        utc_now = datetime.utcnow()
        metadata = metadata or {}
        related_document_ids = related_document_ids or []
        event_timestamp = event_timestamp or utc_now

        if existing:
            existing.summary = summary
            existing.text_hash = text_hash
            existing.embedding = embedding
            existing.embedding_model = embedding_model
            existing.event_type = event_type
            existing.event_timestamp = event_timestamp
            existing.metadata = metadata
            existing.related_document_ids = related_document_ids
            existing.updated_at = utc_now
            await existing.save()
            return existing

        created = OrderEventVector(
            order_id=order_id,
            event_id=event_id,
            event_type=event_type,
            event_timestamp=event_timestamp,
            summary=summary,
            text_hash=text_hash,
            embedding=embedding,
            embedding_model=embedding_model,
            metadata=metadata,
            related_document_ids=related_document_ids,
            created_at=utc_now,
            updated_at=utc_now,
        )
        await created.insert()
        return created

    async def list_order_event_vectors(
        self,
        *,
        order_id: str,
        limit: int = 100,
    ) -> List[OrderEventVector]:
        """Lista eventos vetorizados de uma Order ordenados por tempo."""

        return await OrderEventVector.find(
            OrderEventVector.order_id == order_id
        ).sort(-OrderEventVector.event_timestamp).limit(limit).to_list()

    async def delete_order_event_vector(self, *, event_id: str) -> bool:
        """Remove embedding associado a um evento específico."""

        delete_result = await OrderEventVector.find(
            OrderEventVector.event_id == event_id
        ).delete()
        return bool(getattr(delete_result, "deleted_count", 0))
