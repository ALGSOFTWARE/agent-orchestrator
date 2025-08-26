"""
FASE 2: Embedding API Service
Serviço de embeddings usando APIs externas (OpenAI/Gemini)

Vantagens das APIs:
- Sem necessidade de baixar modelos (450MB+ → 0MB)
- Sem uso de RAM local (4GB+ → <100MB)
- Modelos sempre atualizados
- Escalabilidade automática
- Custo por uso (não por instância)
"""

import asyncio
import logging
import aiohttp
import os
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import hashlib
import json

from ..models import DocumentFile

class EmbeddingAPIService:
    """Serviço de embeddings usando APIs externas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configurações das APIs
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Modelo de embedding por API
        self.embedding_configs = {
            'openai': {
                'model': 'text-embedding-3-small',  # $0.02/1M tokens, 1536 dims
                'url': 'https://api.openai.com/v1/embeddings',
                'dimensions': 1536,
                'max_tokens': 8191,
                'cost_per_1k_tokens': 0.00002  # $0.02/1M = $0.00002/1K
            },
            'openai_large': {
                'model': 'text-embedding-3-large',  # $0.13/1M tokens, 3072 dims 
                'url': 'https://api.openai.com/v1/embeddings',
                'dimensions': 3072,
                'max_tokens': 8191,
                'cost_per_1k_tokens': 0.00013
            },
            'gemini': {
                'model': 'models/embedding-001',     # Gratuito até 1M tokens/min
                'url': 'https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent',
                'dimensions': 768,
                'max_tokens': 2048,
                'cost_per_1k_tokens': 0.0  # Gratuito!
            }
        }
        
        # Usar Gemini por padrão (gratuito)
        self.current_provider = 'gemini'
        self.embedding_cache = {}  # Cache em memória
        
        self.logger.info(f"🌐 Embedding API Service inicializado")
        self.logger.info(f"📡 Provider ativo: {self.current_provider}")
        self.logger.info(f"🔑 OpenAI disponível: {bool(self.openai_api_key)}")
        self.logger.info(f"🔑 Gemini disponível: {bool(self.gemini_api_key)}")
    
    def is_available(self) -> bool:
        """Verifica se pelo menos uma API está disponível"""
        return bool(self.openai_api_key or self.gemini_api_key)
    
    def get_current_config(self) -> Dict[str, Any]:
        """Retorna configuração do provider atual"""
        return self.embedding_configs.get(self.current_provider, {})
    
    async def generate_embedding_openai(self, text: str) -> Optional[List[float]]:
        """Gera embedding usando OpenAI API"""
        if not self.openai_api_key:
            return None
        
        config = self.embedding_configs['openai']
        
        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': config['model'],
            'input': text[:config['max_tokens'] * 4],  # Aproximação de tokens
            'encoding_format': 'float'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(config['url'], headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        embedding = data['data'][0]['embedding']
                        
                        # Log de custo aproximado
                        tokens_used = data['usage']['total_tokens']
                        cost = (tokens_used / 1000) * config['cost_per_1k_tokens']
                        self.logger.debug(f"💰 OpenAI embedding: {tokens_used} tokens, ~${cost:.6f}")
                        
                        return embedding
                    else:
                        error_text = await response.text()
                        self.logger.error(f"OpenAI API error {response.status}: {error_text}")
                        return None
        except Exception as e:
            self.logger.error(f"Erro na OpenAI API: {e}")
            return None
    
    async def generate_embedding_gemini(self, text: str) -> Optional[List[float]]:
        """Gera embedding usando Gemini API"""
        if not self.gemini_api_key:
            return None
        
        config = self.embedding_configs['gemini']
        url = f"{config['url']}?key={self.gemini_api_key}"
        
        payload = {
            'model': config['model'],
            'content': {
                'parts': [{'text': text[:config['max_tokens'] * 4]}]
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        embedding = data['embedding']['values']
                        
                        self.logger.debug(f"💎 Gemini embedding: GRATUITO, {len(embedding)} dims")
                        return embedding
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Gemini API error {response.status}: {error_text}")
                        return None
        except Exception as e:
            self.logger.error(f"Erro na Gemini API: {e}")
            return None
    
    async def generate_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """
        Gera embedding usando o provider configurado
        
        Args:
            text: Texto para gerar embedding
            use_cache: Se deve usar cache
            
        Returns:
            Lista de floats representando o embedding
        """
        # Verificar cache
        cache_key = self._get_cache_key(text)
        if use_cache and cache_key in self.embedding_cache:
            self.logger.debug("📦 Embedding encontrado no cache")
            return self.embedding_cache[cache_key]
        
        # Preparar texto
        processed_text = self._preprocess_text(text)
        
        # Tentar providers com fallback
        providers_to_try = [
            (self.current_provider, f"provider atual ({self.current_provider})"),
            ('gemini', 'Gemini (fallback gratuito)'),
            ('openai', 'OpenAI (fallback pago)')
        ]
        
        for provider, description in providers_to_try:
            if provider == 'openai' and not self.openai_api_key:
                continue
            if provider == 'gemini' and not self.gemini_api_key:
                continue
            
            self.logger.debug(f"🚀 Tentando {description}")
            
            if provider == 'openai':
                embedding = await self.generate_embedding_openai(processed_text)
            elif provider == 'gemini':
                embedding = await self.generate_embedding_gemini(processed_text)
            else:
                continue
            
            if embedding:
                # Cache do resultado
                if use_cache:
                    self.embedding_cache[cache_key] = embedding
                
                self.logger.debug(f"✅ Embedding gerado via {description}: {len(embedding)} dims")
                return embedding
            else:
                self.logger.warning(f"❌ Falha em {description}")
        
        self.logger.error("🚫 Todos os providers falharam")
        return None
    
    async def generate_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> List[Optional[List[float]]]:
        """
        Gera embeddings para múltiplos textos
        
        Args:
            texts: Lista de textos
            use_cache: Se deve usar cache
            
        Returns:
            Lista de embeddings (pode conter None para falhas)
        """
        results = []
        
        # Por enquanto, processar sequencialmente para evitar rate limits
        # Em produção, implementar batching real das APIs
        for text in texts:
            embedding = await self.generate_embedding(text, use_cache)
            results.append(embedding)
            
            # Pequeno delay para evitar rate limits
            await asyncio.sleep(0.1)
        
        return results
    
    async def update_document_embedding(self, document: DocumentFile) -> bool:
        """
        Atualiza o embedding de um documento via API
        
        Args:
            document: Documento para atualizar
            
        Returns:
            True se sucesso, False se erro
        """
        if not document.text_content:
            self.logger.warning(f"Documento {document.file_id} sem texto - pulando embedding")
            return False
        
        # Gerar embedding via API
        embedding = await self.generate_embedding(document.text_content)
        
        if embedding is None:
            self.logger.error(f"Falha ao gerar embedding para documento {document.file_id}")
            return False
        
        try:
            # Atualizar documento
            document.embedding = embedding
            document.embedding_model = f"{self.current_provider}:{self.get_current_config().get('model', 'unknown')}"
            document.indexed_at = datetime.utcnow()
            document.add_processing_log(f"Embedding gerado via {self.current_provider} API: {len(embedding)} dimensões")
            
            await document.save()
            
            self.logger.info(f"✅ Embedding atualizado para documento {document.file_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar embedding do documento {document.file_id}: {e}")
            return False
    
    async def find_similar_documents(
        self, 
        query_text: str, 
        limit: int = 10,
        min_similarity: float = 0.5,
        order_id: Optional[str] = None
    ) -> List[Tuple[DocumentFile, float]]:
        """
        Encontra documentos similares usando busca semântica via API
        
        Args:
            query_text: Texto da consulta
            limit: Número máximo de resultados
            min_similarity: Similaridade mínima (0-1)
            order_id: Filtrar por Order específica
            
        Returns:
            Lista de (documento, score_similaridade)
        """
        # Gerar embedding da consulta via API
        query_embedding = await self.generate_embedding(query_text)
        if query_embedding is None:
            return []
        
        try:
            # Buscar documentos com embeddings
            query_filter = {"embedding": {"$exists": True, "$ne": None}}
            if order_id:
                query_filter["order_id"] = order_id
            
            documents = await DocumentFile.find(query_filter).to_list()
            
            if not documents:
                self.logger.info("Nenhum documento com embedding encontrado")
                return []
            
            # Calcular similaridades
            similarities = []
            query_vector = np.array(query_embedding)
            
            for doc in documents:
                if doc.embedding:
                    doc_vector = np.array(doc.embedding)
                    
                    # Similaridade coseno
                    similarity = self._cosine_similarity(query_vector, doc_vector)
                    
                    if similarity >= min_similarity:
                        similarities.append((doc, similarity))
            
            # Ordenar por similaridade decrescente
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            self.logger.info(f"🔍 Encontrados {len(similarities)} documentos similares via {self.current_provider}")
            return similarities[:limit]
            
        except Exception as e:
            self.logger.error(f"Erro na busca semântica: {e}")
            return []
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcula similaridade coseno entre dois vetores"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm_vec1 = np.linalg.norm(vec1)
            norm_vec2 = np.linalg.norm(vec2)
            
            if norm_vec1 == 0 or norm_vec2 == 0:
                return 0.0
            
            similarity = dot_product / (norm_vec1 * norm_vec2)
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de similaridade: {e}")
            return 0.0
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocessa texto para embedding via API"""
        # Limitar tamanho baseado no provider atual
        config = self.get_current_config()
        max_chars = config.get('max_tokens', 2048) * 4  # Aproximação de chars por token
        
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        # Limpeza básica
        text = text.strip()
        text = ' '.join(text.split())  # Normalizar espaços
        
        return text
    
    def _get_cache_key(self, text: str) -> str:
        """Gera chave de cache para um texto"""
        # Incluir provider na chave do cache
        content = f"{self.current_provider}:{text}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def switch_provider(self, provider: str) -> bool:
        """
        Muda o provider de embeddings
        
        Args:
            provider: 'openai', 'gemini', ou 'openai_large'
        """
        if provider not in self.embedding_configs:
            self.logger.error(f"Provider inválido: {provider}")
            return False
        
        if provider == 'openai' and not self.openai_api_key:
            self.logger.error("OpenAI API key não configurada")
            return False
        
        if provider == 'gemini' and not self.gemini_api_key:
            self.logger.error("Gemini API key não configurada")
            return False
        
        old_provider = self.current_provider
        self.current_provider = provider
        
        self.logger.info(f"🔄 Provider alterado: {old_provider} → {provider}")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do serviço"""
        return {
            'available': self.is_available(),
            'current_provider': self.current_provider,
            'current_config': self.get_current_config(),
            'cache_size': len(self.embedding_cache),
            'providers_available': {
                'openai': bool(self.openai_api_key),
                'gemini': bool(self.gemini_api_key)
            },
            'cost_comparison': {
                'openai_small': '$0.02/1M tokens',
                'openai_large': '$0.13/1M tokens', 
                'gemini': 'GRATUITO até 1M tokens/min'
            }
        }


# Instância global do serviço
embedding_api_service = EmbeddingAPIService()