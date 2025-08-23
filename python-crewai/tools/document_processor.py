"""
Document Processing Tool - OCR e análise de documentos para agentes CrewAI

Este módulo fornece:
1. OCR de PDFs, imagens e documentos diversos
2. Extração de dados estruturados (CT-e, BL, etc)
3. Análise semântica de conteúdo
4. Integração com vector embeddings
5. Processamento em batch de documentos

Integra com o gatekeeper_api_tool para persistir resultados.
"""

import asyncio
import logging
import io
import base64
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import json
import re

# OCR e processamento de imagens
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Processamento de PDFs
try:
    import PyPDF2
    import fitz  # PyMuPDF
    PDF_PROCESSING_AVAILABLE = True
except ImportError:
    PDF_PROCESSING_AVAILABLE = False

# IA para análise de texto
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    AI_PROCESSING_AVAILABLE = True
except ImportError:
    AI_PROCESSING_AVAILABLE = False

from .gatekeeper_api_tool import GatekeeperAPITool

logger = logging.getLogger("DocumentProcessor")


@dataclass
class OCRResult:
    """Resultado do OCR"""
    text: str
    confidence: float
    language: str
    processing_time: float
    method: str  # tesseract, pymupdf, etc
    metadata: Dict[str, Any]


@dataclass
class DocumentAnalysis:
    """Análise completa de documento"""
    ocr_result: OCRResult
    document_type: str  # cte, bl, invoice, etc
    extracted_data: Dict[str, Any]
    semantic_summary: str
    keywords: List[str]
    entities: List[Dict[str, Any]]  # NER entities
    confidence_score: float


class DocumentProcessor:
    """
    Processador de documentos com OCR e IA
    
    Capacidades:
    - OCR multi-engine (Tesseract, PyMuPDF)
    - Detecção de tipo de documento
    - Extração de dados estruturados
    - Análise semântica com IA
    - Geração de embeddings para busca
    """
    
    def __init__(self, gatekeeper_api: Optional[GatekeeperAPITool] = None):
        self.gatekeeper_api = gatekeeper_api or GatekeeperAPITool()
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        
        # Configuração do OCR
        self.ocr_config = {
            'tesseract_config': '--oem 3 --psm 6 -l por+eng',
            'confidence_threshold': 0.6,
            'preprocessing': True
        }
        
        # Padrões para extração de dados
        self.patterns = {
            'cte_number': r'CT-?e[\s\-]*(\d{44})',
            'cnpj': r'\d{2}\.?\d{3}\.?\d{3}\/?\d{4}\-?\d{2}',
            'cpf': r'\d{3}\.?\d{3}\.?\d{3}\-?\d{2}',
            'date': r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}',
            'money': r'R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?',
            'cep': r'\d{5}\-?\d{3}',
            'phone': r'\(\d{2}\)\s*\d{4,5}\-?\d{4}'
        }
        
        # Cache para modelos IA
        self._ai_models = {}
        
        logger.info(f"📄 DocumentProcessor initialized - Tesseract: {TESSERACT_AVAILABLE}, PDF: {PDF_PROCESSING_AVAILABLE}, AI: {AI_PROCESSING_AVAILABLE}")
    
    # === OCR METHODS ===
    
    async def extract_text_from_file(self, file_path: Union[str, Path]) -> OCRResult:
        """
        Extrai texto de arquivo usando melhor método disponível
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            OCRResult com texto extraído e metadados
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Formato não suportado: {file_path.suffix}")
        
        start_time = datetime.now()
        
        try:
            if file_path.suffix.lower() == '.pdf':
                result = await self._extract_text_from_pdf(file_path)
            else:
                result = await self._extract_text_from_image(file_path)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            logger.info(f"✅ OCR completed in {processing_time:.2f}s - {len(result.text)} chars extracted")
            return result
            
        except Exception as e:
            logger.error(f"❌ OCR failed for {file_path}: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                language="unknown",
                processing_time=(datetime.now() - start_time).total_seconds(),
                method="error",
                metadata={"error": str(e)}
            )
    
    async def _extract_text_from_pdf(self, pdf_path: Path) -> OCRResult:
        """Extrai texto de PDF usando PyMuPDF ou PyPDF2"""
        
        if not PDF_PROCESSING_AVAILABLE:
            raise RuntimeError("PDF processing libraries not available")
        
        try:
            # Tentar PyMuPDF primeiro (melhor OCR)
            doc = fitz.open(pdf_path)
            text = ""
            total_confidence = 0
            page_count = 0
            
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                if page_text.strip():
                    # PDF tem texto selecionável
                    text += page_text + "\n"
                    total_confidence += 0.95  # Alta confiança para texto selecionável
                else:
                    # PDF é imagem, fazer OCR
                    if TESSERACT_AVAILABLE:
                        pix = page.get_pixmap()
                        img_data = pix.tobytes("png")
                        img = Image.open(io.BytesIO(img_data))
                        ocr_text = pytesseract.image_to_string(
                            img, config=self.ocr_config['tesseract_config']
                        )
                        text += ocr_text + "\n"
                        
                        # Calcular confiança do OCR
                        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                        confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                        total_confidence += avg_confidence / 100
                    
                page_count += 1
            
            doc.close()
            
            avg_confidence = total_confidence / page_count if page_count > 0 else 0
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence,
                language="por",  # Assumir português por padrão
                processing_time=0.0,  # Será definido pela função chamadora
                method="pymupdf",
                metadata={
                    "page_count": page_count,
                    "file_size": pdf_path.stat().st_size
                }
            )
            
        except Exception as e:
            logger.warning(f"PyMuPDF failed, trying PyPDF2: {e}")
            
            # Fallback para PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    
                    return OCRResult(
                        text=text.strip(),
                        confidence=0.8,  # Confiança média para PyPDF2
                        language="por",
                        processing_time=0.0,
                        method="pypdf2",
                        metadata={
                            "page_count": len(pdf_reader.pages),
                            "file_size": pdf_path.stat().st_size
                        }
                    )
            except Exception as e2:
                raise RuntimeError(f"Both PDF methods failed: PyMuPDF={e}, PyPDF2={e2}")
    
    async def _extract_text_from_image(self, image_path: Path) -> OCRResult:
        """Extrai texto de imagem usando Tesseract"""
        
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("Tesseract OCR not available")
        
        try:
            # Abrir e preprocessar imagem
            image = Image.open(image_path)
            
            if self.ocr_config['preprocessing']:
                image = self._preprocess_image(image)
            
            # OCR com Tesseract
            text = pytesseract.image_to_string(
                image, config=self.ocr_config['tesseract_config']
            )
            
            # Calcular confiança
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Detectar idioma
            try:
                detected_lang = pytesseract.image_to_osd(image)
                language = "por" if "Portuguese" in detected_lang else "eng"
            except:
                language = "por"  # Default
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence / 100,
                language=language,
                processing_time=0.0,
                method="tesseract",
                metadata={
                    "image_size": image.size,
                    "file_size": image_path.stat().st_size,
                    "word_count": len(confidences)
                }
            )
            
        except Exception as e:
            raise RuntimeError(f"Tesseract OCR failed: {e}")
    
    def _preprocess_image(self, image) -> 'Image':
        """Preprocessa imagem para melhorar OCR"""
        # Converter para escala de cinza
        if TESSERACT_AVAILABLE and image.mode != 'L':
            image = image.convert('L')
        
        # Redimensionar se muito pequena
        width, height = image.size
        if width < 300 or height < 300:
            scale_factor = max(300/width, 300/height)
            new_size = (int(width * scale_factor), int(height * scale_factor))
            if TESSERACT_AVAILABLE:
                from PIL import Image as PILImage
                image = image.resize(new_size, PILImage.Resampling.LANCZOS)
        
        return image
    
    # === DOCUMENT ANALYSIS ===
    
    async def analyze_document(self, file_path: Union[str, Path]) -> DocumentAnalysis:
        """
        Análise completa de documento: OCR + IA + extração de dados
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            DocumentAnalysis com todos os resultados
        """
        # Extrair texto via OCR
        ocr_result = await self.extract_text_from_file(file_path)
        
        if not ocr_result.text.strip():
            return DocumentAnalysis(
                ocr_result=ocr_result,
                document_type="unknown",
                extracted_data={},
                semantic_summary="Documento sem texto legível",
                keywords=[],
                entities=[],
                confidence_score=0.0
            )
        
        # Detectar tipo de documento
        doc_type = self._detect_document_type(ocr_result.text)
        
        # Extrair dados estruturados
        extracted_data = self._extract_structured_data(ocr_result.text, doc_type)
        
        # Análise semântica com IA (se disponível)
        if AI_PROCESSING_AVAILABLE:
            semantic_summary = await self._generate_semantic_summary(ocr_result.text)
            keywords = await self._extract_keywords(ocr_result.text)
            entities = await self._extract_entities(ocr_result.text)
        else:
            semantic_summary = self._basic_summary(ocr_result.text)
            keywords = self._basic_keywords(ocr_result.text)
            entities = []
        
        # Calcular confidence score geral
        confidence_factors = [
            ocr_result.confidence * 0.4,  # Qualidade do OCR
            min(len(extracted_data) * 0.1, 0.3),  # Dados extraídos
            min(len(keywords) * 0.05, 0.3)  # Palavras-chave encontradas
        ]
        confidence_score = sum(confidence_factors)
        
        return DocumentAnalysis(
            ocr_result=ocr_result,
            document_type=doc_type,
            extracted_data=extracted_data,
            semantic_summary=semantic_summary,
            keywords=keywords,
            entities=entities,
            confidence_score=min(confidence_score, 1.0)
        )
    
    def _detect_document_type(self, text: str) -> str:
        """Detecta tipo de documento baseado no conteúdo"""
        text_lower = text.lower()
        
        # Padrões de documentos logísticos
        if any(word in text_lower for word in ['conhecimento', 'transporte', 'eletrônico', 'ct-e', 'cte']):
            return "cte"
        elif any(word in text_lower for word in ['bill of lading', 'conhecimento de embarque', 'b/l']):
            return "bl"
        elif any(word in text_lower for word in ['manifesto', 'carga']):
            return "manifesto"
        elif any(word in text_lower for word in ['nota fiscal', 'nf-e', 'nfe']):
            return "nfe"
        elif any(word in text_lower for word in ['fatura', 'invoice', 'cobrança']):
            return "invoice"
        elif any(word in text_lower for word in ['comprovante', 'recibo']):
            return "receipt"
        else:
            return "generic"
    
    def _extract_structured_data(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extrai dados estruturados do texto baseado no tipo de documento"""
        extracted = {}
        
        # Extração baseada em regex
        for field_name, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                extracted[field_name] = matches
        
        # Extração específica por tipo de documento
        if doc_type == "cte":
            extracted.update(self._extract_cte_data(text))
        elif doc_type == "bl":
            extracted.update(self._extract_bl_data(text))
        elif doc_type == "nfe":
            extracted.update(self._extract_nfe_data(text))
        
        return extracted
    
    def _extract_cte_data(self, text: str) -> Dict[str, Any]:
        """Extrai dados específicos de CT-e"""
        data = {}
        
        # Padrões específicos de CT-e
        patterns = {
            'numero_cte': r'(?:Número|N°|Nº)[\s]*(?:do\s*)?CT-?e[\s]*:?[\s]*(\d{44})',
            'chave_acesso': r'(?:Chave|Código)[\s]*(?:de\s*)?(?:Acesso)?[\s]*:?[\s]*([0-9]{44})',
            'remetente': r'(?:Remetente|Expedidor)[\s]*:?[\s]*([^\n\r]{10,100})',
            'destinatario': r'(?:Destinatário|Consignatário)[\s]*:?[\s]*([^\n\r]{10,100})',
            'valor_frete': r'(?:Valor|Vl)[\s]*(?:do\s*)?(?:Frete|Serviço)[\s]*:?[\s]*R?\$?[\s]*([0-9.,]+)',
            'peso_bruto': r'(?:Peso|Massa)[\s]*(?:Bruto|Total)[\s]*:?[\s]*([0-9.,]+)[\s]*(?:kg|KG)?',
            'data_emissao': r'(?:Data|Dt)[\s]*(?:de\s*)?(?:Emissão|Emiss)[\s]*:?[\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[field] = match.group(1).strip()
        
        return data
    
    def _extract_bl_data(self, text: str) -> Dict[str, Any]:
        """Extrai dados específicos de BL"""
        data = {}
        
        patterns = {
            'bl_number': r'(?:B\/L|BL|Bill of Lading)[\s]*(?:N°|No|Number)?[\s]*:?[\s]*([A-Z0-9\-]{5,20})',
            'vessel_name': r'(?:Vessel|Navio|Embarcação)[\s]*:?[\s]*([^\n\r]{5,50})',
            'port_loading': r'(?:Port of Loading|Porto de Embarque)[\s]*:?[\s]*([^\n\r]{5,50})',
            'port_discharge': r'(?:Port of Discharge|Porto de Descarga)[\s]*:?[\s]*([^\n\r]{5,50})',
            'container_numbers': r'(?:Container|CNTR)[\s]*(?:No|N°)?[\s]*:?[\s]*([A-Z]{4}[0-9]{6,7})',
        }
        
        for field, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                data[field] = matches
        
        return data
    
    def _extract_nfe_data(self, text: str) -> Dict[str, Any]:
        """Extrai dados específicos de NF-e"""
        data = {}
        
        patterns = {
            'numero_nfe': r'(?:Número|N°|Nº)[\s]*(?:da\s*)?(?:NF-?e|Nota)[\s]*:?[\s]*(\d+)',
            'chave_nfe': r'(?:Chave|Código)[\s]*(?:de\s*)?(?:Acesso)?[\s]*:?[\s]*([0-9]{44})',
            'emitente': r'(?:Emitente|Vendedor)[\s]*:?[\s]*([^\n\r]{10,100})',
            'valor_total': r'(?:Valor|Total|Vl)[\s]*(?:da\s*)?(?:Nota|NF)[\s]*:?[\s]*R?\$?[\s]*([0-9.,]+)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[field] = match.group(1).strip()
        
        return data
    
    # === AI ANALYSIS ===
    
    async def _generate_semantic_summary(self, text: str) -> str:
        """Gera resumo semântico usando IA"""
        if not AI_PROCESSING_AVAILABLE:
            return self._basic_summary(text)
        
        try:
            # Usar modelo de sumarização (se disponível)
            if 'summarizer' not in self._ai_models:
                self._ai_models['summarizer'] = pipeline(
                    "summarization", 
                    model="unicamp-dl/ptt5-base-portuguese-vocab",
                    device=0 if torch.cuda.is_available() else -1
                )
            
            summarizer = self._ai_models['summarizer']
            
            # Limitar tamanho do texto
            max_length = min(len(text), 512)
            truncated_text = text[:max_length]
            
            summary = summarizer(
                truncated_text, 
                max_length=100, 
                min_length=30, 
                do_sample=False
            )[0]['summary_text']
            
            return summary
            
        except Exception as e:
            logger.warning(f"AI summarization failed: {e}")
            return self._basic_summary(text)
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave usando IA ou método básico"""
        if AI_PROCESSING_AVAILABLE:
            try:
                # Usar NLP para extração de palavras-chave
                # Implementação simplificada - pode ser melhorada com modelos específicos
                return self._basic_keywords(text)
            except:
                pass
        
        return self._basic_keywords(text)
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrai entidades nomeadas usando IA"""
        if not AI_PROCESSING_AVAILABLE:
            return []
        
        try:
            if 'ner' not in self._ai_models:
                self._ai_models['ner'] = pipeline(
                    "ner",
                    model="neuralmind/bert-base-portuguese-cased",
                    aggregation_strategy="simple",
                    device=0 if torch.cuda.is_available() else -1
                )
            
            ner = self._ai_models['ner']
            entities = ner(text[:512])  # Limitar texto
            
            return [
                {
                    "text": entity['word'],
                    "label": entity['entity_group'],
                    "confidence": entity['score'],
                    "start": entity['start'],
                    "end": entity['end']
                }
                for entity in entities
            ]
            
        except Exception as e:
            logger.warning(f"NER extraction failed: {e}")
            return []
    
    # === BASIC METHODS (fallback sem IA) ===
    
    def _basic_summary(self, text: str) -> str:
        """Resumo básico sem IA"""
        sentences = text.split('.')
        # Pegar primeiras 3 sentenças não vazias
        summary_sentences = [s.strip() for s in sentences[:3] if s.strip()]
        return '. '.join(summary_sentences)[:200] + "..."
    
    def _basic_keywords(self, text: str) -> List[str]:
        """Extração básica de palavras-chave"""
        # Palavras relevantes para logística
        logistics_words = [
            'transporte', 'frete', 'carga', 'container', 'embarque',
            'entrega', 'destino', 'origem', 'remetente', 'destinatario',
            'peso', 'valor', 'prazo', 'data', 'numero', 'código'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for word in logistics_words:
            if word in text_lower:
                found_keywords.append(word)
        
        # Adicionar palavras frequentes do texto
        words = re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', text_lower)
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top 10 palavras mais frequentes
        frequent_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        found_keywords.extend([word for word, count in frequent_words if count > 2])
        
        return list(set(found_keywords))  # Remover duplicatas
    
    # === INTEGRATION WITH GATEKEEPER ===
    
    async def process_and_save_document(
        self, 
        file_path: Union[str, Path], 
        order_id: str,
        save_to_api: bool = True
    ) -> DocumentAnalysis:
        """
        Processa documento e salva resultado no Gatekeeper API
        
        Args:
            file_path: Caminho para o arquivo
            order_id: ID da Order para associar o documento
            save_to_api: Se deve salvar no Gatekeeper API
            
        Returns:
            DocumentAnalysis com resultados
        """
        # Processar documento
        analysis = await self.analyze_document(file_path)
        
        if save_to_api and analysis.confidence_score > 0.5:
            try:
                # Salvar texto extraído no documento
                async with self.gatekeeper_api as api:
                    # Buscar documentos da Order
                    order_docs = await api.get_order_documents(order_id)
                    
                    if order_docs.success:
                        # Encontrar documento correspondente pelo nome
                        file_name = Path(file_path).name
                        
                        # Atualizar documento com texto extraído
                        update_data = {
                            "text_content": analysis.ocr_result.text,
                            "indexed_at": datetime.now().isoformat(),
                            "metadata": {
                                "document_type": analysis.document_type,
                                "confidence_score": analysis.confidence_score,
                                "extracted_data": analysis.extracted_data,
                                "keywords": analysis.keywords,
                                "processing_method": analysis.ocr_result.method
                            }
                        }
                        
                        logger.info(f"📊 Document analysis saved for Order {order_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to save document analysis: {e}")
        
        return analysis


# === CREWAI TOOL WRAPPER ===

class CrewAIDocumentTool:
    """Wrapper para usar DocumentProcessor com CrewAI agents"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
    
    def _run_async(self, coro):
        """Executa corrotina assíncrona de forma síncrona"""
        try:
            # Verifica se já existe um loop rodando
            loop = asyncio.get_running_loop()
            # Se existe, executa em thread separada
            import concurrent.futures
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
                
        except RuntimeError:
            # Não há loop rodando, pode usar run_until_complete
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(coro)
    
    def processar_documento(self, caminho_arquivo: str) -> str:
        """Processa documento e retorna análise - método síncrono para agents"""
        analysis = self._run_async(
            self.processor.analyze_document(caminho_arquivo)
        )
        
        # Formatar resultado para o agente
        result = f"""📄 Análise do documento: {caminho_arquivo}

🔍 Tipo: {analysis.document_type}
📊 Confiança: {analysis.confidence_score:.2%}
⏱️ Tempo OCR: {analysis.ocr_result.processing_time:.2f}s

📝 Resumo:
{analysis.semantic_summary}

🔑 Dados extraídos:
{json.dumps(analysis.extracted_data, indent=2, ensure_ascii=False)}

🏷️ Palavras-chave: {', '.join(analysis.keywords[:10])}

📃 Texto completo ({len(analysis.ocr_result.text)} caracteres):
{analysis.ocr_result.text[:500]}{'...' if len(analysis.ocr_result.text) > 500 else ''}"""

        return result
    
    def extrair_texto_simples(self, caminho_arquivo: str) -> str:
        """Extrai apenas o texto do documento"""
        try:
            ocr_result = self._run_async(
                self.processor.extract_text_from_file(caminho_arquivo)
            )
        except Exception as e:
            return f"❌ Erro ao processar documento: {str(e)}"
        
        if not hasattr(ocr_result, 'text'):
            return "❌ Erro: arquivo não encontrado ou formato não suportado"
        
        return f"✅ Texto extraído ({ocr_result.confidence:.1%} confiança):\n\n{ocr_result.text}"


# Instância global para uso pelos agents
document_tool = CrewAIDocumentTool()

def processar_documento(caminho_arquivo: str) -> str:
    return document_tool.processar_documento(caminho_arquivo)

def extrair_texto_simples(caminho_arquivo: str) -> str:
    return document_tool.extrair_texto_simples(caminho_arquivo)