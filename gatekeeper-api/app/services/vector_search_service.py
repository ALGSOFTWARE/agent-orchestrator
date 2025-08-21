"""
FASE 3: MongoDB Vector Search Service
Serviço desacoplado para busca vetorial em produção

Características do desacoplamento:
- Interface independente do provider de embeddings
- Abstração total da implementação do MongoDB
- Fallback automático para busca traditional  
- Cache de queries frequentes
- Configuração flexível por ambiente
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import hashlib

from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from ..models import DocumentFile, Order


class VectorSearchService:
    """Serviço desacoplado de busca vetorial com MongoDB Atlas"""
    
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.logger = logging.getLogger(__name__)
        self.mongo_client = mongo_client
        self.db = mongo_client.gatekeeper
        self.collection = self.db.document_files
        
        # Cache de queries
        self.query_cache = {}
        self.cache_ttl = timedelta(minutes=15)
        
        # Configurações de busca
        self.search_config = {
            'index_name': 'vector_search_index',
            'path': 'embedding',
            'numCandidates': 100,
            'limit': 10,
            'similarity_threshold': 0.7
        }
        
        self.logger.info("🔍 Vector Search Service inicializado")
        self._log_mongo_capabilities()
    
    async def _log_mongo_capabilities(self):
        """Log das capacidades do MongoDB"""
        try:
            # Verificar se estamos no Atlas (suporte a vector search)
            server_info = await self.db.command("serverStatus")
            version = server_info.get("version", "unknown")
            
            # Verificar coleções e índices
            collections = await self.db.list_collection_names()
            
            self.logger.info(f"📊 MongoDB {version}")
            self.logger.info(f"📁 Collections: {len(collections)}")
            
            # Verificar índices na coleção de documentos
            if "document_files" in collections:
                indexes = await self.collection.list_indexes().to_list(length=None)
                vector_indexes = [idx for idx in indexes if 'vector' in str(idx).lower()]
                
                self.logger.info(f"📇 Índices vector: {len(vector_indexes)}")
                if vector_indexes:
                    self.logger.info("✅ Vector Search disponível")
                else:
                    self.logger.warning("⚠️ Vector Search não configurado - usando busca tradicional")
        except Exception as e:
            self.logger.warning(f"Erro ao verificar capacidades MongoDB: {e}")
    
    async def create_vector_index(self) -> bool:
        """
        Cria índice vetorial no MongoDB Atlas
        
        IMPORTANTE: Este comando só funciona no MongoDB Atlas,
        não em instâncias locais do MongoDB
        """
        try:
            # Definição do índice vetorial para Atlas
            index_definition = {
                "mappings": {
                    "dynamic": True,
                    "fields": {
                        "embedding": {
                            "type": "knnVector",
                            "dimensions": 768,  # Gemini: 768, OpenAI: 1536
                            "similarity": "cosine"
                        },
                        "order_id": {
                            "type": "token"
                        },
                        "category": {
                            "type": "token"
                        },
                        "text_content": {
                            "type": "string"
                        }
                    }
                }
            }
            
            # Tentar criar índice (só funciona no Atlas)
            result = await self.collection.create_search_index(
                name=self.search_config['index_name'],
                definition=index_definition
            )
            
            self.logger.info(f"✅ Índice vetorial criado: {result}")
            return True
            
        except Exception as e:
            self.logger.warning(f"⚠️ Não foi possível criar índice vetorial: {e}")
            self.logger.info("💡 Para usar Vector Search, configure no MongoDB Atlas")
            return False
    
    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        min_similarity: float = 0.7,
        order_id: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Tuple[DocumentFile, float]]:
        """
        Busca vetorial usando MongoDB Atlas Vector Search
        
        Args:
            query_embedding: Vetor de busca
            limit: Máximo de resultados
            min_similarity: Similaridade mínima
            order_id: Filtrar por Order
            category: Filtrar por categoria
            
        Returns:
            Lista de (documento, score_similaridade)
        """
        try:
            # Pipeline de agregação para Vector Search
            pipeline = []
            
            # Estágio de busca vetorial
            vector_search_stage = {
                "$vectorSearch": {
                    "index": self.search_config['index_name'],
                    "path": self.search_config['path'],
                    "queryVector": query_embedding,
                    "numCandidates": self.search_config['numCandidates'],
                    "limit": limit
                }
            }
            
            # Adicionar filtros se necessário
            if order_id or category:
                filters = {}
                if order_id:
                    filters["order_id"] = {"$eq": order_id}
                if category:
                    filters["category"] = {"$eq": category}
                
                vector_search_stage["$vectorSearch"]["filter"] = filters
            
            pipeline.append(vector_search_stage)
            
            # Adicionar score de similaridade
            pipeline.append({
                "$addFields": {
                    "similarity_score": {"$meta": "vectorSearchScore"}
                }
            })
            
            # Filtrar por similaridade mínima
            pipeline.append({
                "$match": {
                    "similarity_score": {"$gte": min_similarity}
                }
            })
            
            # Executar busca
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=limit)
            
            # Converter para objetos DocumentFile
            documents_with_scores = []
            for result in results:
                try:
                    # Remover score do documento antes de criar objeto
                    score = result.pop("similarity_score", 0.0)
                    
                    # Criar objeto DocumentFile
                    document = DocumentFile(**result)
                    documents_with_scores.append((document, score))
                    
                except Exception as e:
                    self.logger.warning(f"Erro ao processar resultado: {e}")
                    continue
            
            self.logger.info(f"🔍 Vector Search: {len(documents_with_scores)} resultados")
            return documents_with_scores
            
        except Exception as e:
            self.logger.error(f"Erro na busca vetorial: {e}")
            return []
    
    async def traditional_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        min_similarity: float = 0.7,
        order_id: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Tuple[DocumentFile, float]]:
        """
        Busca tradicional com cálculo de similaridade em Python
        Fallback para quando Vector Search não está disponível
        """
        try:
            # Construir filtro básico
            filter_query = {"embedding": {"$exists": True, "$ne": None}}
            
            if order_id:
                filter_query["order_id"] = order_id
            if category:
                filter_query["category"] = category
            
            # Buscar documentos com embeddings
            cursor = self.collection.find(filter_query).limit(limit * 2)  # Buscar mais para filtrar
            documents = await cursor.to_list(length=None)
            
            if not documents:
                return []
            
            # Calcular similaridades em Python
            import numpy as np
            
            query_vector = np.array(query_embedding)
            similarities = []
            
            for doc_data in documents:
                try:
                    # Criar objeto DocumentFile
                    document = DocumentFile(**doc_data)
                    
                    if document.embedding:
                        doc_vector = np.array(document.embedding)
                        
                        # Similaridade coseno
                        similarity = self._cosine_similarity(query_vector, doc_vector)
                        
                        if similarity >= min_similarity:
                            similarities.append((document, similarity))
                            
                except Exception as e:
                    self.logger.warning(f"Erro ao processar documento: {e}")
                    continue
            
            # Ordenar por similaridade
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            self.logger.info(f"🔍 Traditional Search: {len(similarities)} resultados")
            return similarities[:limit]
            
        except Exception as e:
            self.logger.error(f"Erro na busca tradicional: {e}")
            return []
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calcula similaridade coseno"""
        try:
            import numpy as np
            dot_product = np.dot(vec1, vec2)
            norm_vec1 = np.linalg.norm(vec1)
            norm_vec2 = np.linalg.norm(vec2)
            
            if norm_vec1 == 0 or norm_vec2 == 0:
                return 0.0
            
            return float(dot_product / (norm_vec1 * norm_vec2))
        except:
            return 0.0
    
    async def search_documents(
        self,
        query_embedding: List[float],
        limit: int = 10,
        min_similarity: float = 0.7,
        order_id: Optional[str] = None,
        category: Optional[str] = None,
        use_cache: bool = True
    ) -> List[Tuple[DocumentFile, float]]:
        """
        Busca principal com fallback automático
        
        Tenta Vector Search primeiro, fallback para busca tradicional
        """
        # Verificar cache
        cache_key = self._get_cache_key(query_embedding, limit, min_similarity, order_id, category)
        
        if use_cache and cache_key in self.query_cache:
            cached_result, cached_time = self.query_cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                self.logger.debug("📦 Resultado encontrado no cache")
                return cached_result
        
        # Tentar Vector Search primeiro (MongoDB Atlas)
        try:
            results = await self.vector_search(
                query_embedding=query_embedding,
                limit=limit,
                min_similarity=min_similarity,
                order_id=order_id,
                category=category
            )
            
            if results:
                # Cache do resultado
                if use_cache:
                    self.query_cache[cache_key] = (results, datetime.now())
                
                self.logger.info(f"✅ Vector Search retornou {len(results)} resultados")
                return results
                
        except Exception as e:
            self.logger.warning(f"Vector Search falhou: {e}")
        
        # Fallback para busca tradicional
        self.logger.info("🔄 Usando busca tradicional como fallback")
        
        results = await self.traditional_search(
            query_embedding=query_embedding,
            limit=limit,
            min_similarity=min_similarity,
            order_id=order_id,
            category=category
        )
        
        # Cache do resultado
        if use_cache and results:
            self.query_cache[cache_key] = (results, datetime.now())
        
        return results
    
    def _get_cache_key(self, query_embedding, limit, min_similarity, order_id, category) -> str:
        """Gera chave de cache para a query"""
        # Hash do embedding (primeiros/últimos elementos para performance)
        embedding_sample = str(query_embedding[:5] + query_embedding[-5:])
        
        key_data = f"{embedding_sample}:{limit}:{min_similarity}:{order_id}:{category}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_search_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do serviço de busca"""
        try:
            # Estatísticas da coleção
            doc_count = await self.collection.count_documents({})
            embedding_count = await self.collection.count_documents({"embedding": {"$exists": True}})
            
            # Verificar índices
            indexes = await self.collection.list_indexes().to_list(length=None)
            vector_indexes = [idx for idx in indexes if 'vector' in str(idx).lower()]
            
            return {
                "documents_total": doc_count,
                "documents_with_embeddings": embedding_count,
                "embedding_coverage": f"{(embedding_count/doc_count*100):.1f}%" if doc_count > 0 else "0%",
                "vector_indexes": len(vector_indexes),
                "vector_search_available": len(vector_indexes) > 0,
                "cache_size": len(self.query_cache),
                "search_config": self.search_config,
                "fallback_strategy": "traditional_search"
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {"error": str(e)}
    
    def clear_cache(self):
        """Limpa cache de queries"""
        self.query_cache.clear()
        self.logger.info("🗑️ Cache de queries limpo")
    
    async def optimize_indexes(self) -> Dict[str, Any]:
        """Otimiza índices para performance"""
        try:
            results = {
                "vector_index": False,
                "text_index": False,
                "compound_indexes": []
            }
            
            # Tentar criar índice vetorial (Atlas only)
            vector_created = await self.create_vector_index()
            results["vector_index"] = vector_created
            
            # Criar índice de texto para fallback
            try:
                await self.collection.create_index([
                    ("text_content", "text"),
                    ("order_id", 1),
                    ("category", 1)
                ], name="text_search_index")
                results["text_index"] = True
                self.logger.info("✅ Índice de texto criado")
            except Exception as e:
                self.logger.warning(f"Índice de texto já existe ou erro: {e}")
            
            # Índices compostos para performance
            compound_indexes = [
                [("order_id", 1), ("category", 1), ("uploaded_at", -1)],
                [("processing_status", 1), ("indexed_at", -1)],
                [("file_type", 1), ("size_bytes", 1)]
            ]
            
            for idx_spec in compound_indexes:
                try:
                    idx_name = "_".join([f"{field}_{direction}" for field, direction in idx_spec])
                    await self.collection.create_index(idx_spec, name=idx_name)
                    results["compound_indexes"].append(idx_name)
                    self.logger.info(f"✅ Índice composto criado: {idx_name}")
                except Exception as e:
                    self.logger.debug(f"Índice já existe ou erro: {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao otimizar índices: {e}")
            return {"error": str(e)}


# Função factory para criar instância com desacoplamento
def create_vector_search_service(mongo_client: AsyncIOMotorClient) -> VectorSearchService:
    """Factory para criar serviço de busca vetorial desacoplado"""
    return VectorSearchService(mongo_client)