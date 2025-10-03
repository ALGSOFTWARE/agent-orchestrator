"""Prototype pipeline for document embeddings and semantic search validation."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
import sys

# Ensure gatekeeper-app modules are importable when the script is executed directly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from app.database import init_database, get_mongo_client
from app.models import DocumentFile, ProcessingStatus
from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService

EMBEDDING_TEXT_MAX_CHARS = 4000


async def bootstrap_document_embeddings(limit: int = 10) -> int:
    """Generate embeddings for indexed documents that still lack vectors."""
    candidates = await DocumentFile.find(
        DocumentFile.processing_status == ProcessingStatus.INDEXED,
        DocumentFile.embedding == None  # noqa: E711 (Beanie comparison with None)
    ).limit(limit).to_list()

    if not candidates:
        return 0

    embedding_service = EmbeddingService()
    if not embedding_service.is_available():
        raise RuntimeError("Embedding service is not ready; install sentence-transformers and model deps.")

    updates = 0
    for document in candidates:
        text = (document.text_content or "").strip()
        if not text:
            continue

        snippet = text[:EMBEDDING_TEXT_MAX_CHARS]
        embedding = await embedding_service.generate_embedding(snippet)
        if not embedding:
            continue

        document.embedding = embedding
        document.embedding_model = embedding_service.model_name
        document.indexed_at = datetime.utcnow()
        document.add_processing_log(f"Embedding gerado ({len(snippet)} chars) via prototype pipeline.")
        updates += 1
        await document.save()

    return updates


async def validate_semantic_search(order_id: Optional[str] = None) -> None:
    """Run a sample semantic query using the fallback search if Atlas vector index is unavailable."""
    embedding_service = EmbeddingService()
    if not embedding_service.is_available():
        raise RuntimeError("Embedding service is not ready; install sentence-transformers and model deps.")

    query_source = await DocumentFile.find_one(DocumentFile.embedding != None)  # noqa: E711
    if not query_source or not query_source.text_content:
        print("Nenhum documento com embedding disponível para validar a busca.")
        return

    if order_id is None:
        order_id = query_source.order_id

    query_text = query_source.text_content[:600]
    query_embedding = await embedding_service.generate_embedding(query_text)
    if not query_embedding:
        print("Não foi possível gerar embedding para a consulta de validação.")
        return

    mongo_client = await get_mongo_client()
    search_service = VectorSearchService(mongo_client)
    results = await search_service.search_documents(
        query_embedding=query_embedding,
        limit=5,
        min_similarity=0.35,
        order_id=order_id
    )

    if not results:
        print("Nenhum resultado retornado pela busca semântica.")
        return

    print("Resultados da busca semântica prototipada:\n")
    for document, score in results:
        preview = (document.text_content or "")[:120].replace("\n", " ")
        print(f"- {document.original_name} | order={document.order_id} | score={score:.3f}\n  preview={preview}")


async def main() -> None:
    await init_database()
    updated = await bootstrap_document_embeddings(limit=5)
    if updated:
        print(f"Embeddings gerados para {updated} documentos.")
    await validate_semantic_search()


if __name__ == "__main__":
    asyncio.run(main())
