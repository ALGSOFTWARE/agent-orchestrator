"""
FASE 2: Embedding Service
Serviço de geração de embeddings semânticos para busca inteligente

Funcionalidades:
- Geração de embeddings usando sentence-transformers
- Modelos otimizados para português
- Cache de embeddings para performance
- Busca semântica por similaridade
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import json
import hashlib

# Sentence Transformers para embeddings
try:
    from sentence_transformers import SentenceTransformer
    import torch
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logging.warning("sentence-transformers não disponível. Instale: pip install sentence-transformers")

from ..models import DocumentFile


class EmbeddingService:
    """Serviço de geração e gerenciamento de embeddings semânticos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        # Configuração baseada no ambiente (EC2-friendly)
        self.model_options = {
            'production': "neuralmind/bert-base-portuguese-cased",  # ~450MB, 768 dims, alta precisão
            'balanced': "paraphrase-multilingual-MiniLM-L12-v2",   # ~120MB, 384 dims, boa precisão  
            'lightweight': "all-MiniLM-L6-v2"                      # ~90MB, 384 dims, rápido
        }
        # Usar modelo balanceado por padrão (melhor custo-benefício)
        self.model_name = self.model_options['balanced']
        self.embedding_cache = {}  # Cache simples em memória
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa o modelo de embeddings com fallback inteligente"""
        if not EMBEDDINGS_AVAILABLE:
            self.logger.warning("Sentence Transformers não disponível - embeddings desabilitados")
            return
        
        try:
            self.logger.info(f"Tentando carregar modelo: {self.model_name}")
            
            # Tentar carregar modelo configurado com fallbacks
            model_attempts = [
                (self.model_name, "modelo configurado"),
                (self.model_options['lightweight'], "modelo lightweight (fallback)"),
                ('all-MiniLM-L6-v2', "modelo padrão mínimo (último recurso)")
            ]
            
            for model_name, description in model_attempts:
                try:
                    self.logger.info(f"Carregando {description}: {model_name}")
                    self.model = SentenceTransformer(model_name)
                    self.model_name = model_name
                    self.logger.info(f"✅ {description} carregado com sucesso")
                    break
                except Exception as e:
                    self.logger.warning(f"❌ Falha ao carregar {description}: {e}")
                    continue
            
            if self.model is None:
                self.logger.error("Todos os modelos falharam - embeddings desabilitados")
                return
            
            # Definir dispositivo (CPU por padrão para EC2)
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model = self.model.to(device)
            self.logger.info(f"🚀 Modelo rodando em: {device}")
            
            # Log informações do modelo
            try:
                model_info = self._get_model_info()
                self.logger.info(f"📊 Modelo info: {model_info}")
            except:
                pass
            
        except Exception as e:
            self.logger.error(f"Erro fatal ao inicializar embeddings: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Verifica se o serviço de embeddings está disponível"""
        return EMBEDDINGS_AVAILABLE and self.model is not None
    
    async def generate_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """
        Gera embedding para um texto
        
        Args:
            text: Texto para gerar embedding
            use_cache: Se deve usar cache de embeddings
            
        Returns:
            Lista de floats representando o embedding ou None se erro
        """
        if not self.is_available():
            self.logger.warning("Serviço de embeddings não disponível")
            return None
        
        # Verificar cache
        cache_key = self._get_cache_key(text)
        if use_cache and cache_key in self.embedding_cache:
            self.logger.debug("Embedding encontrado no cache")
            return self.embedding_cache[cache_key]
        
        try:
            # Preparar texto
            processed_text = self._preprocess_text(text)
            
            # Gerar embedding
            self.logger.debug(f"Gerando embedding para texto de {len(processed_text)} chars")
            
            # Executar em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self._generate_embedding_sync, 
                processed_text
            )
            
            # Converter para lista
            embedding_list = embedding.tolist()
            
            # Salvar no cache
            if use_cache:
                self.embedding_cache[cache_key] = embedding_list
            
            self.logger.debug(f"Embedding gerado: dimensão {len(embedding_list)}")
            return embedding_list
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar embedding: {e}")
            return None
    
    def _generate_embedding_sync(self, text: str) -> np.ndarray:
        """Gera embedding de forma síncrona (para thread pool)"""
        with torch.no_grad():
            embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    async def generate_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> List[Optional[List[float]]]:
        """
        Gera embeddings para múltiplos textos de forma eficiente
        
        Args:
            texts: Lista de textos
            use_cache: Se deve usar cache
            
        Returns:
            Lista de embeddings (pode conter None para falhas)
        """
        if not self.is_available():
            return [None] * len(texts)
        
        results = []
        batch_texts = []
        batch_indices = []
        
        # Separar textos que não estão no cache
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if use_cache and cache_key in self.embedding_cache:
                results.append(self.embedding_cache[cache_key])
            else:
                results.append(None)  # Placeholder
                batch_texts.append(self._preprocess_text(text))
                batch_indices.append(i)
        
        # Processar textos em batch
        if batch_texts:
            try:
                self.logger.debug(f"Gerando {len(batch_texts)} embeddings em batch")
                
                loop = asyncio.get_event_loop()
                batch_embeddings = await loop.run_in_executor(
                    None,
                    self._generate_embeddings_batch_sync,
                    batch_texts
                )
                
                # Inserir resultados de volta
                for i, embedding in enumerate(batch_embeddings):
                    original_index = batch_indices[i]
                    embedding_list = embedding.tolist()
                    results[original_index] = embedding_list
                    
                    # Cache
                    if use_cache:
                        cache_key = self._get_cache_key(texts[original_index])
                        self.embedding_cache[cache_key] = embedding_list
                        
            except Exception as e:
                self.logger.error(f"Erro no batch de embeddings: {e}")
                # Marcar falhas
                for i in batch_indices:
                    results[i] = None
        
        return results
    
    def _generate_embeddings_batch_sync(self, texts: List[str]) -> np.ndarray:
        """Gera embeddings em batch de forma síncrona"""
        with torch.no_grad():
            embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    async def update_document_embedding(self, document: DocumentFile) -> bool:
        """
        Atualiza o embedding de um documento
        
        Args:
            document: Documento para atualizar
            
        Returns:
            True se sucesso, False se erro
        """
        if not document.text_content:
            self.logger.warning(f"Documento {document.file_id} sem texto - pulando embedding")
            return False
        
        # Gerar embedding
        embedding = await self.generate_embedding(document.text_content)
        
        if embedding is None:
            self.logger.error(f"Falha ao gerar embedding para documento {document.file_id}")
            return False
        
        try:
            # Atualizar documento
            document.embedding = embedding
            document.embedding_model = self.model_name
            document.indexed_at = datetime.utcnow()
            document.add_processing_log(f"Embedding gerado: {len(embedding)} dimensões")
            
            await document.save()
            
            self.logger.info(f"Embedding atualizado para documento {document.file_id}")
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
        Encontra documentos similares usando busca semântica
        
        Args:
            query_text: Texto da consulta
            limit: Número máximo de resultados
            min_similarity: Similaridade mínima (0-1)
            order_id: Filtrar por Order específica
            
        Returns:
            Lista de (documento, score_similaridade)
        """
        if not self.is_available():
            self.logger.warning("Busca semântica não disponível")
            return []
        
        # Gerar embedding da consulta
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
            
            self.logger.info(f"Encontrados {len(similarities)} documentos similares")
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
        """Preprocessa texto para embedding"""
        # Limitir tamanho (modelos têm limite de tokens)
        max_chars = 4000  # Aproximadamente 512 tokens
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        # Limpeza básica
        text = text.strip()
        text = ' '.join(text.split())  # Normalizar espaços
        
        return text
    
    def _get_cache_key(self, text: str) -> str:
        """Gera chave de cache para um texto"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_model_info(self) -> Dict[str, Any]:
        """Retorna informações detalhadas do modelo"""
        if not self.model:
            return {}
        
        try:
            # Estimar tamanho do modelo
            model_size_mb = sum(p.numel() * p.element_size() for p in self.model.parameters()) / (1024 * 1024)
            
            return {
                'name': self.model_name,
                'size_mb': round(model_size_mb, 1),
                'device': str(next(self.model.parameters()).device),
                'max_seq_length': getattr(self.model, 'max_seq_length', 'unknown')
            }
        except:
            return {'name': self.model_name}
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do serviço"""
        stats = {
            'available': self.is_available(),
            'model_name': self.model_name,
            'cache_size': len(self.embedding_cache),
            'device': str(next(self.model.parameters()).device) if self.model else None,
            'model_options': self.model_options
        }
        
        if self.model:
            stats.update(self._get_model_info())
            
        return stats
    
    def switch_model(self, model_type: str) -> bool:
        """
        Muda para um modelo diferente (production/balanced/lightweight)
        Útil para ajustar baseado na capacidade da instância EC2
        """
        if model_type not in self.model_options:
            self.logger.error(f"Tipo de modelo inválido: {model_type}")
            return False
        
        old_model = self.model_name
        self.model_name = self.model_options[model_type]
        
        # Limpar modelo atual
        if self.model:
            del self.model
            self.model = None
        
        # Reinicializar com novo modelo
        self._initialize_model()
        
        if self.model:
            self.logger.info(f"Modelo alterado de {old_model} para {self.model_name}")
            return True
        else:
            self.logger.error(f"Falha ao mudar para modelo {model_type}")
            return False


# Instância global do serviço
embedding_service = EmbeddingService()