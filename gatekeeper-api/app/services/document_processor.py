"""
FASE 2: Document Processing Service
Sistema de processamento inteligente de documentos

Funcionalidades:
- OCR de imagens e PDFs
- Extração de texto estruturado
- Análise de conteúdo logístico
- Preparação para embedding
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
import io
import tempfile
from datetime import datetime


# OCR e processamento de imagens
try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_bytes
    import PyPDF2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("Dependências de OCR não instaladas. Instale: pip install pytesseract Pillow pdf2image PyPDF2")

# Processamento de texto
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    import re
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK não disponível. Instale: pip install nltk")

from ..models import DocumentFile, ProcessingStatus, DocumentCategory
from .embedding_service import EmbeddingService
from .semantic_index_service import SemanticIndexService


class DocumentProcessor:
    """Processa documentos para extração de texto e análise inteligente"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_nltk()
        self.embedding_service = EmbeddingService()
        self.semantic_index_service = SemanticIndexService()
        self.semantic_index_enabled = os.getenv("SEMANTIC_INDEX_ENABLED", "true").lower() not in {"0", "false", "no"}
        self.chunk_size = self._get_config_int("DOCUMENT_INDEX_CHUNK_SIZE", default=1500, minimum=400, maximum=4000)
        self.chunk_overlap = self._get_config_int(
            "DOCUMENT_INDEX_CHUNK_OVERLAP",
            default=200,
            minimum=0,
            maximum=max(0, self.chunk_size // 2)
        )
    
    def _setup_nltk(self):
        """Baixa recursos necessários do NLTK"""
        if NLTK_AVAILABLE:
            try:
                # Download de recursos básicos
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
            except Exception as e:
                self.logger.warning(f"Erro ao baixar recursos NLTK: {e}")

    def _get_config_int(self, env_key: str, *, default: int, minimum: int, maximum: int) -> int:
        """Lê valor inteiro do ambiente respeitando limites informados."""

        try:
            value = int(os.getenv(env_key, default))
        except (TypeError, ValueError):
            return default

        if minimum is not None:
            value = max(minimum, value)
        if maximum is not None:
            value = min(maximum, value)
        return value

    async def process_document(self, document: DocumentFile, file_content: bytes) -> Dict[str, Any]:
        """
        Processa um documento e extrai informações inteligentes
        
        Args:
            document: Objeto DocumentFile do banco
            file_content: Conteúdo binário do arquivo
            
        Returns:
            Dict com texto extraído e metadados
        """
        try:
            # Atualizar status para processando
            document.processing_status = ProcessingStatus.PROCESSING
            await document.save()
            
            # Extrair texto baseado no tipo de arquivo
            text_content = await self._extract_text(document, file_content)
            
            # Processar e estruturar o texto
            processed_text = self._process_text(text_content)
            
            # Analisar conteúdo logístico
            logistics_info = self._analyze_logistics_content(processed_text)
            
            # Atualizar documento no banco
            document.text_content = processed_text['clean_text']
            document.processing_status = ProcessingStatus.INDEXED
            document.indexed_at = datetime.utcnow()
            document.add_processing_log(f"Texto extraído: {len(processed_text['clean_text'])} chars")
            
            # Se encontrou informações logísticas, adicionar como tags
            if logistics_info['entities']:
                logistics_tags = [entity['value'] for entity in logistics_info['entities'][:5]]
                document.tags.extend(logistics_tags)
                document.tags = list(set(document.tags))  # Remove duplicatas
            
            await document.save()

            semantic_chunks = 0
            try:
                semantic_chunks = await self._index_document_semantics(document)
            except Exception as index_error:  # pragma: no cover - log e seguir
                self.logger.warning(
                    "Falha ao indexar semanticamente o documento %s: %s",
                    document.file_id,
                    index_error
                )

            if semantic_chunks:
                document.embedding_model = getattr(self.embedding_service, "model_name", None)
                document.add_processing_log(
                    f"Semantic index atualizado com {semantic_chunks} chunks."
                )
                await document.save()
            
            return {
                'success': True,
                'text_length': len(processed_text['clean_text']),
                'sentences': len(processed_text['sentences']),
                'logistics_entities': logistics_info['entities'],
                'confidence_score': logistics_info['confidence'],
                'semantic_chunks_indexed': semantic_chunks,
                'processing_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro no processamento do documento {document.file_id}: {e}")
            document.processing_status = ProcessingStatus.ERROR
            document.add_processing_log(f"Erro: {str(e)}")
            await document.save()
            
            return {
                'success': False,
                'error': str(e),
                'processing_time': datetime.utcnow().isoformat()
            }

    def _split_text_for_embedding(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> List[str]:
        """Divide texto em chunks com sobreposição leve para geração de embedding."""

        chunk_size = chunk_size or self.chunk_size
        overlap = self.chunk_overlap if overlap is None else overlap
        overlap = min(overlap, max(0, chunk_size // 2))

        cleaned = (text or "").strip()
        if not cleaned:
            return []

        if len(cleaned) <= chunk_size:
            return [cleaned]

        sentences: List[str] = []
        if NLTK_AVAILABLE:
            try:
                sentences = sent_tokenize(cleaned)
            except Exception:
                sentences = []

        if not sentences:
            normalized = cleaned.replace("\n", " ")
            sentences = [segment.strip() for segment in normalized.split('.') if segment.strip()]
            sentences = [f"{segment}." for segment in sentences]

        chunks: List[str] = []
        current = ""

        for sentence in sentences:
            snippet = sentence.strip()
            if not snippet:
                continue
            if snippet[-1] not in {'.', '!', '?'}:
                snippet = f"{snippet}."

            candidate = f"{current} {snippet}".strip() if current else snippet

            if len(candidate) <= chunk_size:
                current = candidate
                continue

            if current:
                chunks.append(current.strip())
                if overlap:
                    overlap_text = current[-overlap:].strip()
                    current = f"{overlap_text} {snippet}".strip() if overlap_text else snippet
                else:
                    current = snippet
            else:
                current = snippet

            while len(current) > chunk_size:
                chunks.append(current[:chunk_size].strip())
                current = current[chunk_size:].strip()

        if current:
            chunks.append(current.strip())

        if not chunks:
            return [cleaned]

        # Sanitizar chunks vazios ou duplicados por corte agressivo
        sanitized = []
        for chunk in chunks:
            trimmed = chunk.strip()
            if trimmed and (not sanitized or trimmed != sanitized[-1]):
                sanitized.append(trimmed)

        return sanitized

    async def _index_document_semantics(self, document: DocumentFile) -> int:
        """Gera embeddings e atualiza o índice semântico para o documento fornecido."""

        if not getattr(self, "embedding_service", None):
            return 0

        if not getattr(self, "semantic_index_enabled", True):
            return 0

        if not self.embedding_service.is_available():
            self.logger.debug(
                "Serviço de embeddings indisponível; ignorando indexação semântica para %s",
                document.file_id
            )
            return 0

        text = (document.text_content or "").strip()
        if not text:
            return 0

        chunks = self._split_text_for_embedding(text)
        if not chunks:
            return 0

        embeddings_payload: List[Dict[str, Any]] = []
        model_name = getattr(self.embedding_service, "model_name", "unknown")
        processed_at = datetime.utcnow().isoformat()

        for index, chunk_text in enumerate(chunks):
            embedding = await self.embedding_service.generate_embedding(chunk_text)
            if not embedding:
                continue

            embeddings_payload.append({
                "chunk_id": f"{document.file_id}-chunk-{index}",
                "chunk_index": index,
                "text": chunk_text,
                "embedding": embedding,
                "embedding_model": model_name,
                "source_category": getattr(document.category, "value", document.category),
                "metadata": {
                    "source": "DocumentProcessor",
                    "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
                    "processed_at": processed_at,
                    "original_filename": document.original_name,
                },
            })

        if not embeddings_payload:
            return 0

        await self.semantic_index_service.upsert_document_vectors(
            order_id=document.order_id,
            source_document_id=document.file_id,
            chunks=embeddings_payload,
        )

        self.logger.info(
            "Indexação semântica aplicada: %s chunks para documento %s",
            len(embeddings_payload),
            document.file_id
        )

        return len(embeddings_payload)
    
    async def _extract_text(self, document: DocumentFile, file_content: bytes) -> str:
        """Extrai texto de diferentes tipos de arquivo"""
        
        if not OCR_AVAILABLE:
            raise Exception("Dependências de OCR não instaladas")
        
        file_type = document.file_type.lower()
        
        # PDF
        if 'pdf' in file_type:
            return await self._extract_text_from_pdf(file_content)
        
        # Imagens
        elif any(img_type in file_type for img_type in ['image', 'jpeg', 'jpg', 'png', 'tiff', 'bmp']):
            return await self._extract_text_from_image(file_content)
        
        # Texto puro
        elif 'text' in file_type:
            return file_content.decode('utf-8', errors='ignore')
        
        # JSON/XML estruturados
        elif file_type in ['application/json', 'application/xml', 'text/xml']:
            return file_content.decode('utf-8', errors='ignore')
        
        else:
            # Tentar como texto por último
            try:
                return file_content.decode('utf-8', errors='ignore')
            except:
                raise Exception(f"Tipo de arquivo não suportado para OCR: {file_type}")
    
    async def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extrai texto de PDF usando PyPDF2 e OCR como fallback"""
        
        # Primeiro, tentar extrair texto diretamente
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text_parts = []
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    text_parts.append(text)
            
            if text_parts:
                extracted_text = '\n'.join(text_parts)
                # Se conseguiu texto suficiente, retorna
                if len(extracted_text.strip()) > 50:
                    return extracted_text
        except Exception as e:
            self.logger.warning(f"Falha na extração direta de PDF: {e}")
        
        # Se não conseguiu texto suficiente, usar OCR
        self.logger.info("Usando OCR para PDF (imagens ou texto não extraível)")
        
        try:
            # Converter PDF para imagens
            images = convert_from_bytes(file_content, dpi=150)
            
            text_parts = []
            for i, image in enumerate(images):
                # OCR em cada página
                page_text = pytesseract.image_to_string(image, lang='por+eng')
                if page_text.strip():
                    text_parts.append(f"=== Página {i+1} ===\n{page_text}")
            
            return '\n\n'.join(text_parts)
            
        except Exception as e:
            self.logger.error(f"Erro no OCR do PDF: {e}")
            raise Exception(f"Não foi possível extrair texto do PDF: {e}")
    
    async def _extract_text_from_image(self, file_content: bytes) -> str:
        """Extrai texto de imagem usando Tesseract OCR"""
        
        try:
            # Carregar imagem
            image = Image.open(io.BytesIO(file_content))
            
            # Melhorar qualidade para OCR
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # OCR com português e inglês
            text = pytesseract.image_to_string(image, lang='por+eng')
            
            return text
            
        except Exception as e:
            self.logger.error(f"Erro no OCR da imagem: {e}")
            raise Exception(f"Não foi possível extrair texto da imagem: {e}")
    
    def _process_text(self, raw_text: str) -> Dict[str, Any]:
        """Processa e limpa o texto extraído"""
        
        if not NLTK_AVAILABLE:
            # Processamento básico sem NLTK
            clean_text = self._basic_text_cleaning(raw_text)
            return {
                'clean_text': clean_text,
                'sentences': clean_text.split('.'),
                'word_count': len(clean_text.split())
            }
        
        # Limpeza básica
        clean_text = self._basic_text_cleaning(raw_text)
        
        # Tokenização em sentenças
        try:
            sentences = sent_tokenize(clean_text, language='portuguese')
        except:
            sentences = clean_text.split('.')
        
        # Tokenização em palavras
        try:
            words = word_tokenize(clean_text, language='portuguese')
            # Remover stopwords em português
            stop_words = set(stopwords.words('portuguese'))
            filtered_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        except:
            words = clean_text.split()
            filtered_words = [word for word in words if len(word) > 2]
        
        return {
            'clean_text': clean_text,
            'sentences': sentences,
            'words': words,
            'filtered_words': filtered_words,
            'word_count': len(words),
            'sentence_count': len(sentences)
        }
    
    def _basic_text_cleaning(self, text: str) -> str:
        """Limpeza básica de texto"""
        
        # Remover quebras de linha excessivas
        text = re.sub(r'\n+', '\n', text)
        
        # Remover espaços excessivos
        text = re.sub(r'\s+', ' ', text)
        
        # Remover caracteres especiais desnecessários
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
        
        return text.strip()
    
    def _analyze_logistics_content(self, processed_text: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa conteúdo específico de documentos logísticos"""
        
        text = processed_text['clean_text'].lower()
        
        # Padrões logísticos brasileiros
        logistics_patterns = {
            'cte_number': r'ct-?e\s*n[ºo°]?\s*(\d{8,})',
            'nfe_number': r'nf-?e\s*n[ºo°]?\s*(\d{8,})',
            'cnpj': r'cnpj[:\s]*(\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2})',
            'container': r'[A-Z]{4}\s*\d{7}',
            'bl_number': r'bl\s*n[ºo°]?\s*([A-Z0-9\-]{6,})',
            'peso': r'peso[:\s]*(\d+(?:\.\d+)?)\s*(?:kg|quilos?)',
            'valor': r'valor[:\s]*r?\$?\s*(\d+(?:\.\d+)?)',
            'origem': r'origem[:\s]*([A-Za-z\s\-]{3,30})',
            'destino': r'destino[:\s]*([A-Za-z\s\-]{3,30})',
            'transportadora': r'transportadora[:\s]*([A-Za-z\s\-]{3,50})'
        }
        
        entities = []
        confidence_scores = []
        
        for entity_type, pattern in logistics_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(1) if match.groups() else match.group(0)
                entities.append({
                    'type': entity_type,
                    'value': value.strip(),
                    'position': match.span()
                })
                confidence_scores.append(0.8)  # Score base para padrões específicos
        
        # Calcular confiança geral
        total_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            'entities': entities,
            'confidence': total_confidence,
            'is_logistics_document': len(entities) > 0,
            'entity_count': len(entities)
        }


# Instância global do processador
document_processor = DocumentProcessor()
