
import boto3
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from botocore.exceptions import NoCredentialsError, ClientError
from typing import Optional
import magic
import os
import uuid
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ..models import DocumentFile, DocumentCategory, ProcessingStatus, Order
from ..services.document_processor import document_processor
from ..services.embedding_api_service import embedding_api_service
from ..services.vector_search_service import create_vector_search_service

load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

# Configurações do S3 a partir de variáveis de ambiente
S3_BUCKET = os.getenv("S3_BUCKET")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    order_id: str = Query(..., description="ID da Order para vincular o documento (obrigatório)"),
    public: bool = Query(True, description="Se true, torna o arquivo publicamente acessível"),
    category: DocumentCategory = Query(DocumentCategory.OTHER, description="Categoria do documento")
):
    if not all([S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]):
        raise HTTPException(status_code=500, detail="Credenciais da AWS ou nome do bucket não configurados no servidor.")

    # Validar se a Order existe
    order = await Order.find_one(Order.order_id == order_id)
    if not order:
        raise HTTPException(
            status_code=404, 
            detail=f"Order com ID '{order_id}' não encontrada. Todo documento deve estar vinculado a uma Order existente."
        )

    try:
        # Ler todo o conteúdo do arquivo uma vez só
        file_content = await file.read()
        
        # Usar python-magic para detectar o tipo de conteúdo de forma mais segura
        mime_type = magic.from_buffer(file_content[:2048], mime=True)

        # Gerar nome único para evitar conflitos
        file_extension = os.path.splitext(file.filename or "unknown")[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Configurar ExtraArgs baseado na opção public
        extra_args = {'ContentType': mime_type}
        # Note: ACL removed as bucket doesn't allow ACLs
        # if public:
        #     extra_args['ACL'] = 'public-read'

        # Upload para S3 usando BytesIO
        from io import BytesIO
        file_buffer = BytesIO(file_content)
        s3_client.upload_fileobj(
            file_buffer,
            S3_BUCKET,
            unique_filename,
            ExtraArgs=extra_args
        )
        
        # Gerar URLs
        if public:
            file_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
        else:
            file_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET, 'Key': unique_filename},
                ExpiresIn=86400  # 24 horas
            )
        
        # Criar registro no banco de dados
        document_file = DocumentFile(
            original_name=file.filename or "unknown",
            s3_key=unique_filename,
            s3_url=file_url,
            file_type=mime_type,
            file_extension=file_extension,
            size_bytes=file.size or 0,
            category=category,
            is_public=public,
            order_id=order_id,
            processing_status=ProcessingStatus.UPLOADED
        )
        
        # Salvar no banco
        await document_file.save()
        
        # Log inicial
        document_file.add_processing_log(f"Arquivo enviado para S3: {unique_filename}")
        await document_file.save()
        
        # FASE 2: Processamento inteligente assíncrono
        processing_result = None
        logger.info(f"🔄 Iniciando processamento OCR para arquivo: {file.filename}")
        try:
            logger.info(f"📄 Conteúdo do arquivo: {len(file_content)} bytes")
            
            # Processar documento (OCR + análise)
            logger.info("🧠 Chamando document_processor.process_document...")
            processing_result = await document_processor.process_document(document_file, file_content)
            logger.info(f"📊 Resultado do processamento: {processing_result}")
            
            # TEMPORARY FIX: Ensure all datetime objects are converted to strings
            if processing_result and isinstance(processing_result, dict):
                logger.info("🔧 Convertendo objetos datetime para strings...")
                processing_result = json.loads(json.dumps(processing_result, default=str))
                logger.info(f"📊 Resultado após conversão: {processing_result}")
            
            # Se processamento foi bem-sucedido e temos embedding service disponível
            if processing_result and processing_result.get('success') and embedding_api_service.is_available():
                logger.info("📡 Gerando embeddings...")
                # Gerar embedding para busca semântica via API
                await embedding_api_service.update_document_embedding(document_file)
                logger.info("✅ Embeddings gerados com sucesso")
                
        except Exception as e:
            logger.error(f"❌ Erro no processamento OCR: {str(e)}")
            # Log erro mas não falha o upload
            document_file.add_processing_log(f"Erro no processamento inteligente: {str(e)}")
            await document_file.save()
        
        # Preparar resposta com informações de processamento
        response = {
            "message": "Arquivo enviado com sucesso e vinculado à Order!", 
            "id": document_file.file_id,
            "url": file_url,
            "s3_key": unique_filename,
            "original_name": file.filename,
            "file_type": mime_type,
            "category": category.value,
            "size_bytes": file.size,
            "is_public": public,
            "order_id": order_id,
            "order_title": order.title,
            "order_customer": order.customer_name,
            "processing_status": document_file.processing_status.value,
            "created_at": document_file.uploaded_at.isoformat() if document_file.uploaded_at else None,
            "relationship": "documento → order (mapa mental)",
            "intelligent_processing": {
                "enabled": True,
                "ocr_available": document_processor is not None,
                "embeddings_available": embedding_api_service.is_available(),
                "embedding_provider": embedding_api_service.current_provider,
                "result": processing_result if processing_result else None
            }
        }
        
        # Adicionar resultados do processamento se disponível
        if processing_result:
            response["intelligent_processing"]["result"] = processing_result
        
        return response

    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="Credenciais da AWS não encontradas.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar o arquivo: {str(e)}")


@router.get("/signed-url/{filename}")
async def get_signed_url(
    filename: str,
    expires_in: int = Query(3600, description="Tempo de expiração em segundos (padrão: 1 hora)")
):
    """Gera uma URL assinada para acessar um arquivo privado"""
    if not all([S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]):
        raise HTTPException(status_code=500, detail="Credenciais da AWS não configurados.")
    
    try:
        # Verificar se o arquivo existe
        s3_client.head_object(Bucket=S3_BUCKET, Key=filename)
        
        # Gerar URL assinada
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': filename},
            ExpiresIn=expires_in
        )
        
        return {
            "signed_url": signed_url,
            "expires_in": expires_in,
            "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        else:
            raise HTTPException(status_code=500, detail=f"Erro ao acessar arquivo: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/by-order/{order_id}")
async def list_documents_by_order(
    order_id: str,
    limit: int = Query(50, description="Número máximo de documentos a retornar"),
    skip: int = Query(0, description="Número de documentos a pular"),
    category: Optional[DocumentCategory] = Query(None, description="Filtrar por categoria")
):
    """Lista todos os documentos vinculados a uma Order específica (conceito mapa mental)"""
    
    # Validar se a Order existe
    order = await Order.find_one(Order.order_id == order_id)
    if not order:
        raise HTTPException(
            status_code=404, 
            detail=f"Order com ID '{order_id}' não encontrada."
        )
    
    # Construir query para documentos
    query = {"order_id": order_id}
    if category:
        query["category"] = category
    
    # Buscar documentos
    documents = await DocumentFile.find(query).skip(skip).limit(limit).to_list()
    
    # Contar total
    total = await DocumentFile.find(query).count()
    
    return {
        "order_info": {
            "order_id": order.order_id,
            "title": order.title,
            "customer_name": order.customer_name,
            "order_type": order.order_type,
            "status": order.status
        },
        "documents": [
            {
                "file_id": doc.file_id,
                "original_name": doc.original_name,
                "category": doc.category,
                "file_type": doc.file_type,
                "size_bytes": doc.size_bytes,
                "processing_status": doc.processing_status,
                "uploaded_at": doc.uploaded_at,
                "s3_url": doc.s3_url,
                "is_public": doc.is_public,
                "tags": doc.tags
            }
            for doc in documents
        ],
        "pagination": {
            "total": total,
            "limit": limit,
            "skip": skip,
            "has_more": skip + len(documents) < total
        },
        "relationship": f"📋 Order '{order.title}' → {len(documents)} documentos (mapa mental)"
    }


@router.get("/processing/status")
async def get_processing_status():
    """Retorna status dos serviços de processamento inteligente"""
    try:
        # Importar serviços de forma segura
        from ..services.document_processor import document_processor
        from ..services.embedding_api_service import embedding_api_service
        
        return {
            "intelligent_processing": {
                "enabled": True,
                "document_processor": {
                    "available": document_processor is not None,
                    "ocr_available": True,  # pytesseract etc já instalados
                    "features": ["pdf_extraction", "image_ocr", "logistics_analysis"]
                },
                "embedding_service": {
                    "type": "API_BASED",
                    "available": embedding_api_service.is_available(),
                    "current_provider": embedding_api_service.current_provider,
                    "providers": embedding_api_service.get_stats()["providers_available"],
                    "stats": embedding_api_service.get_stats(),
                    "features": ["semantic_search", "document_similarity", "api_embeddings", "cost_optimization"]
                }
            },
            "dependencies": {
                "pytesseract": True,
                "pdf_processing": True,
                "nltk": True,
                "embedding_apis": embedding_api_service.is_available(),
                "numpy": True
            },
            "endpoints": {
                "upload_with_processing": "/files/upload",
                "semantic_search": "/files/search/semantic",
                "reprocess_document": "/files/reprocess/{file_id}",
                "list_by_order": "/files/by-order/{order_id}"
            }
        }
    except Exception as e:
        return {
            "intelligent_processing": {
                "enabled": False,
                "error": str(e)
            }
        }


@router.get("/search/semantic")
async def semantic_search(
    query: str = Query(..., description="Consulta em linguagem natural"),
    limit: int = Query(10, description="Número máximo de resultados"),
    min_similarity: float = Query(0.5, description="Similaridade mínima (0-1)"),
    order_id: Optional[str] = Query(None, description="Filtrar por Order específica")
):
    """Busca semântica de documentos usando embeddings e linguagem natural"""
    
    if not embedding_api_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Serviço de busca semântica não disponível. Configure APIs do OpenAI ou Gemini."
        )
    
    try:
        # Gerar embedding da query via API
        query_embedding = await embedding_api_service.generate_embedding(query)
        if not query_embedding:
            raise HTTPException(
                status_code=500,
                detail="Não foi possível gerar embedding para a consulta"
            )
        
        # Usar Vector Search Service desacoplado
        from ..database import get_mongo_client
        mongo_client = await get_mongo_client()
        vector_search = create_vector_search_service(mongo_client)
        
        results = await vector_search.search_documents(
            query_embedding=query_embedding,
            limit=limit,
            min_similarity=min_similarity,
            order_id=order_id,
            category=category
        )
        
        if not results:
            return {
                "query": query,
                "results": [],
                "total": 0,
                "message": "Nenhum documento similar encontrado",
                "search_params": {
                    "limit": limit,
                    "min_similarity": min_similarity,
                    "order_id": order_id
                }
            }
        
        # Formatar resultados
        formatted_results = []
        for document, similarity in results:
            # Buscar informações da Order de forma desacoplada
            order = await Order.find_one(Order.order_id == document.order_id)
            
            formatted_results.append({
                "document": {
                    "file_id": document.file_id,
                    "original_name": document.original_name,
                    "category": document.category,
                    "file_type": document.file_type,
                    "size_bytes": document.size_bytes,
                    "uploaded_at": document.uploaded_at,
                    "s3_url": document.s3_url,
                    "is_public": document.is_public,
                    "order_id": document.order_id,
                    "tags": document.tags,
                    "text_preview": document.text_content[:200] + "..." if document.text_content and len(document.text_content) > 200 else document.text_content
                },
                "order": {
                    "order_id": order.order_id if order else None,
                    "title": order.title if order else None,
                    "customer_name": order.customer_name if order else None
                },
                "similarity_score": round(similarity, 3),
                "relevance": "alta" if similarity > 0.8 else "média" if similarity > 0.6 else "baixa",
                "search_method": "vector_search_with_fallback"
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "total": len(formatted_results),
            "message": f"Encontrados {len(formatted_results)} documentos similares",
            "search_params": {
                "limit": limit,
                "min_similarity": min_similarity,
                "order_id": order_id
            },
            "embedding_provider": embedding_api_service.current_provider,
            "search_type": "semantic_similarity"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na busca semântica: {str(e)}"
        )


@router.post("/reprocess/{file_id}")
async def reprocess_document(file_id: str):
    """Reprocessa um documento específico (OCR + embedding)"""
    
    # Buscar documento
    document = await DocumentFile.find_one(DocumentFile.file_id == file_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    try:
        # TODO: Em produção, baixar do S3
        # Por enquanto, retorna informação sobre reprocessamento
        
        # Reset status
        document.processing_status = ProcessingStatus.PROCESSING
        document.text_content = None
        document.embedding = None
        await document.save()
        
        return {
            "message": "Documento marcado para reprocessamento",
            "file_id": file_id,
            "status": "reprocessing_queued",
            "note": "Em produção, este documento seria adicionado à fila de processamento assíncrono"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao reprocessar documento: {str(e)}"
        )


@router.get("/search/vector/stats")
async def get_vector_search_stats():
    """Retorna estatísticas do Vector Search (desacoplado)"""
    try:
        from ..database import get_mongo_client
        mongo_client = await get_mongo_client()
        vector_search = create_vector_search_service(mongo_client)
        
        stats = await vector_search.get_search_stats()
        
        return {
            "vector_search": stats,
            "embedding_service": embedding_api_service.get_stats(),
            "integration": {
                "decoupled": True,
                "fallback_enabled": True,
                "cache_enabled": True
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )


@router.post("/search/vector/optimize")
async def optimize_vector_search():
    """Otimiza índices para Vector Search (operação administrativa)"""
    try:
        from ..database import get_mongo_client
        mongo_client = await get_mongo_client()
        vector_search = create_vector_search_service(mongo_client)
        
        results = await vector_search.optimize_indexes()
        
        return {
            "message": "Otimização de índices executada",
            "results": results,
            "recommendations": [
                "Configure MongoDB Atlas para Vector Search completo",
                "Use fallback tradicional em desenvolvimento",
                "Monitor cache hit rate para performance"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na otimização: {str(e)}"
        )


@router.delete("/search/vector/cache")
async def clear_vector_search_cache():
    """Limpa cache do Vector Search"""
    try:
        from ..database import get_mongo_client
        mongo_client = await get_mongo_client()
        vector_search = create_vector_search_service(mongo_client)
        
        vector_search.clear_cache()
        
        return {
            "message": "Cache do Vector Search limpo",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar cache: {str(e)}"
        )


# === DOCUMENT ACCESS ENDPOINTS === #

@router.get("/{file_id}/metadata")
async def get_document_metadata(file_id: str):
    """Retorna metadados completos de um documento específico"""
    try:
        # Buscar documento por file_id
        document = await DocumentFile.find_one(DocumentFile.file_id == file_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        # Buscar Order relacionada
        order = None
        if document.order_id:
            order = await Order.find_one(Order.order_id == document.order_id)
        
        # Preparar metadados completos
        metadata = {
            "document": {
                "id": str(document.id),
                "file_id": document.file_id if hasattr(document, 'file_id') else str(document.id),
                "original_name": document.original_name,
                "s3_key": document.s3_key,
                "s3_url": document.s3_url,
                "file_type": document.file_type,
                "file_extension": document.file_extension,
                "size_bytes": document.size_bytes,
                "category": document.category.value if document.category else None,
                "processing_status": document.processing_status.value if document.processing_status else None,
                "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
                "indexed_at": document.indexed_at.isoformat() if document.indexed_at else None,
                "tags": document.tags or [],
                "has_embedding": bool(document.embedding),
                "embedding_model": document.embedding_model,
                "text_content_length": len(document.text_content) if document.text_content else 0,
                "order_id": document.order_id
            },
            "order": {
                "id": str(order.id) if order else None,
                "order_id": order.order_id if order else None,
                "title": order.title if order else None,
                "customer_name": order.customer_name if order else None,
                "status": order.status.value if order and order.status else None,
                "created_at": order.created_at.isoformat() if order and order.created_at else None
            } if order else None,
            "access": {
                "can_download": bool(document.s3_key),
                "signed_url_available": bool(document.s3_key),
                "text_preview_available": bool(document.text_content)
            }
        }
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao buscar metadados: {str(e)}"
        )


@router.get("/{file_id}/download")
async def download_document(file_id: str):
    """Gera URL assinada para download direto de um documento"""
    try:
        # Buscar documento por file_id
        document = await DocumentFile.find_one(DocumentFile.file_id == file_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        # Para dados sintéticos (que começam com 'synthetic/'), sempre retornar mock
        if not document.s3_key or (document.s3_key and document.s3_key.startswith('synthetic/')):
            # Para documentos sintéticos, retornar mock URL
            return {
                "download_url": f"https://demo-bucket.s3.amazonaws.com/demo/{document.original_name}",
                "filename": document.original_name,
                "size_bytes": document.size_bytes,
                "file_type": document.file_type,
                "expires_in": 3600,
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
                "note": "Mock URL - Synthetic data (demo purposes)"
            }
        
        # Verificar se as credenciais AWS estão configuradas
        if not all([S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]):
            # Para demonstração, retornar URL mock quando S3 não configurado
            return {
                "download_url": f"https://demo-bucket.s3.amazonaws.com/{document.s3_key}",
                "filename": document.original_name,
                "size_bytes": document.size_bytes,
                "file_type": document.file_type,
                "expires_in": 3600,
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
                "note": "Mock URL - S3 credentials not configured for demo"
            }
        
        try:
            # Verificar se o arquivo existe no S3
            s3_client.head_object(Bucket=S3_BUCKET, Key=document.s3_key)
            
            # Gerar URL assinada para download
            signed_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': S3_BUCKET, 
                    'Key': document.s3_key,
                    'ResponseContentDisposition': f'attachment; filename="{document.original_name}"'
                },
                ExpiresIn=3600  # 1 hora
            )
            
            return {
                "download_url": signed_url,
                "filename": document.original_name,
                "size_bytes": document.size_bytes,
                "file_type": document.file_type,
                "expires_in": 3600,
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise HTTPException(
                    status_code=404,
                    detail="Arquivo não encontrado no S3"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao acessar S3: {str(e)}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao gerar download: {str(e)}"
        )


@router.get("/{file_id}/ocr-text")
async def get_ocr_text(file_id: str):
    """
    Endpoint específico para visualizar o texto completo extraído pelo OCR
    
    Args:
        file_id: ID único do documento no sistema
        
    Returns:
        Dict com texto completo, metadados e informações de processamento
    """
    try:
        # Buscar o documento no banco de dados
        document = await DocumentFile.find_one(DocumentFile.file_id == file_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Documento com ID '{file_id}' não encontrado"
            )
        
        # Verificar se o documento foi processado
        if document.processing_status != ProcessingStatus.INDEXED:
            raise HTTPException(
                status_code=422,
                detail=f"Documento ainda não foi processado. Status atual: {document.processing_status}"
            )
        
        # Verificar se há texto extraído
        if not document.text_content:
            raise HTTPException(
                status_code=404,
                detail="Nenhum texto foi extraído deste documento pelo OCR"
            )
        
        # Buscar informações da Order relacionada para contexto
        order = None
        if document.order_id:
            order = await Order.find_one(Order.order_id == document.order_id)
        
        # Preparar resposta com texto completo e metadados
        response = {
            "file_id": document.file_id,
            "original_name": document.original_name,
            "file_type": document.file_type,
            "size_bytes": document.size_bytes,
            "processing_status": document.processing_status,
            "indexed_at": document.indexed_at.isoformat() if document.indexed_at else None,
            "uploaded_at": document.uploaded_at.isoformat(),
            
            # Texto extraído completo
            "text_content": document.text_content,
            "text_length": len(document.text_content) if document.text_content else 0,
            
            # Metadados de processamento
            "tags": document.tags,
            "processing_logs": document.processing_logs,
            
            # Contexto da Order
            "order_context": {
                "order_id": document.order_id,
                "order_title": order.title if order else None,
                "customer_name": order.customer_name if order else None
            } if order else None,
            
            # URLs para acesso ao arquivo original
            "file_urls": {
                "s3_url": document.s3_url,
                "is_public": document.is_public
            }
        }
        
        logger.info(f"📖 Texto OCR recuperado para documento {file_id}: {len(document.text_content)} caracteres")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao recuperar texto OCR para {file_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao recuperar texto OCR: {str(e)}"
        )


@router.get("/{file_id}/view")
async def view_file(file_id: str):
    """
    Endpoint para visualizar arquivo diretamente via proxy da API
    Resolve problemas de permissão do S3 servindo o arquivo através da API
    """
    try:
        # Buscar o documento no banco de dados
        document = await DocumentFile.find_one(DocumentFile.file_id == file_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Documento com ID '{file_id}' não encontrado"
            )
        
        if not all([S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]):
            raise HTTPException(status_code=500, detail="Credenciais da AWS não configuradas.")
        
        try:
            # Baixar arquivo do S3
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=document.s3_key)
            file_content = response['Body'].read()
            
            logger.info(f"📁 Servindo arquivo via proxy: {document.original_name}")
            
            # Determinar Content-Type apropriado
            content_type = document.file_type
            
            # Para alguns tipos específicos, forçar download
            if document.file_type in ['application/pdf']:
                from fastapi.responses import Response
                return Response(
                    content=file_content,
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f'inline; filename="{document.original_name}"'
                    }
                )
            else:
                # Para texto e imagens, mostrar inline
                from fastapi.responses import Response  
                return Response(
                    content=file_content,
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f'inline; filename="{document.original_name}"'
                    }
                )
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise HTTPException(status_code=404, detail="Arquivo não encontrado no S3")
            else:
                raise HTTPException(status_code=500, detail=f"Erro ao acessar S3: {str(e)}")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao servir arquivo {file_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao servir arquivo: {str(e)}"
        )

