"""Semantic Retrieval Service

Executa busca semântica sobre os vetores de documento para enriquecer o chat.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from ..database import get_mongo_client
from .embedding_service import EmbeddingService


class SemanticRetrievalService:
    """Busca trechos relevantes no índice semântico de documentos."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("GatekeeperAPI.SemanticRetrieval")
        self.embedding_service = EmbeddingService()
        self.mongo_client = None
        self.collection = None
        self.vector_search_config = {
            "index_name": "document_vectors_index",
            "path": "embedding",
            "numCandidates": 150,
            "limit": 5,
        }
        self.traditional_pool = 200

    async def _ensure_collection(self) -> None:
        if self.collection is not None:
            return
        self.mongo_client = await get_mongo_client()
        self.collection = self.mongo_client.gatekeeper.document_vectors

    async def retrieve_semantic_context(
        self,
        query_text: str,
        *,
        order_id: Optional[str] = None,
        limit: int = 5,
        min_similarity: float = 0.35,
    ) -> List[Dict[str, Any]]:
        """Retorna lista de trechos relevantes para a mensagem fornecida."""

        if not query_text or not query_text.strip():
            return []

        if not self.embedding_service.is_available():
            self.logger.debug("Serviço de embeddings indisponível para retrieve.")
            return []

        query_embedding = await self.embedding_service.generate_embedding(query_text.strip())
        if not query_embedding:
            return []

        await self._ensure_collection()

        documents: List[Dict[str, Any]] = []

        # Tenta vector search nativo (Mongo Atlas)
        try:
            documents = await self._vector_search(query_embedding, order_id=order_id, limit=limit)
        except Exception as exc:  # noqa: BLE001
            self.logger.debug("Vector search indisponível: %s", exc)

        # Fallback para cálculo manual
        if not documents:
            documents = await self._fallback_search(
                query_embedding,
                order_id=order_id,
                limit=limit,
                min_similarity=min_similarity,
            )

        # Preparar saída amigável para o chat
        results: List[Dict[str, Any]] = []
        for doc in documents[:limit]:
            results.append(self._build_payload(doc))

        return results

    async def _vector_search(
        self,
        query_embedding: List[float],
        *,
        order_id: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        pipeline: List[Dict[str, Any]] = [
            {
                "$vectorSearch": {
                    "index": self.vector_search_config["index_name"],
                    "path": self.vector_search_config["path"],
                    "queryVector": query_embedding,
                    "numCandidates": self.vector_search_config["numCandidates"],
                    "limit": limit,
                }
            },
            {
                "$addFields": {
                    "similarity_score": {"$meta": "vectorSearchScore"}
                }
            },
        ]

        if order_id:
            pipeline[0]["$vectorSearch"]["filter"] = {"order_id": {"$eq": order_id}}

        cursor = self.collection.aggregate(pipeline)
        documents = await cursor.to_list(length=limit)
        for doc in documents:
            doc.setdefault("similarity_score", 0.0)
        return documents

    async def _fallback_search(
        self,
        query_embedding: List[float],
        *,
        order_id: Optional[str],
        limit: int,
        min_similarity: float,
    ) -> List[Dict[str, Any]]:
        filter_query: Dict[str, Any] = {"embedding": {"$exists": True, "$ne": None}}
        if order_id:
            filter_query["order_id"] = order_id

        cursor = self.collection.find(filter_query).limit(self.traditional_pool)
        raw_docs = await cursor.to_list(length=self.traditional_pool)

        if not raw_docs:
            return []

        query_vec = np.array(query_embedding)
        scored_docs: List[Dict[str, Any]] = []

        for doc in raw_docs:
            embedding = doc.get("embedding")
            if not embedding:
                continue
            doc_vec = np.array(embedding)
            similarity = self._cosine_similarity(query_vec, doc_vec)
            if similarity >= min_similarity:
                doc["similarity_score"] = float(similarity)
                scored_docs.append(doc)

        scored_docs.sort(key=lambda item: item.get("similarity_score", 0.0), reverse=True)
        return scored_docs[:limit]

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        try:
            denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
            if denom == 0:
                return 0.0
            return float(np.dot(vec1, vec2) / denom)
        except Exception:  # noqa: BLE001
            return 0.0

    def _build_payload(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        text = (doc.get("text") or "").strip()
        if len(text) > 600:
            text = f"{text[:600].rstrip()}…"

        metadata = doc.get("metadata") or {}
        document_name = metadata.get("original_filename") or metadata.get("document_name") or doc.get("source_document_id")
        similarity = float(doc.get("similarity_score", 0.0))

        return {
            "order_id": doc.get("order_id"),
            "document_id": doc.get("source_document_id"),
            "document_name": document_name,
            "source_category": doc.get("source_category"),
            "score": round(similarity, 4),
            "chunk_text": text,
            "metadata": metadata,
            "embedding_model": doc.get("embedding_model"),
            "chunk_id": doc.get("chunk_id"),
            "retrieved_at": datetime.utcnow().isoformat(),
        }
