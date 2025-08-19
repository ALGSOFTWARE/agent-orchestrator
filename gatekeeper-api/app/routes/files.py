
import boto3
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from botocore.exceptions import NoCredentialsError, ClientError
from typing import Optional
import magic
import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ..models import DocumentFile, DocumentCategory, ProcessingStatus, Order
from ..services.document_processor import document_processor
from ..services.embedding_api_service import embedding_api_service
from ..services.vector_search_service import create_vector_search_service

load_dotenv()

router = APIRouter()

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
        # Usando python-magic para detectar o tipo de conteúdo de forma mais segura
        file_content = file.file.read(2048)
        mime_type = magic.from_buffer(file_content, mime=True)
        file.file.seek(0)

        # Gerar nome único para evitar conflitos
        file_extension = os.path.splitext(file.filename or "unknown")[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Configurar ExtraArgs baseado na opção public
        extra_args = {'ContentType': mime_type}
        if public:
            extra_args['ACL'] = 'public-read'

        # Upload para S3
        s3_client.upload_fileobj(
            file.file,
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
        try:
            # Re-baixar o arquivo para processamento (em produção, usar fila assíncrona)
            file.file.seek(0)  # Reset file pointer
            file_content = file.file.read()
            
            # Processar documento (OCR + análise)
            processing_result = await document_processor.process_document(document_file, file_content)
            
            # Se processamento foi bem-sucedido e temos embedding service disponível
            if processing_result.get('success') and embedding_api_service.is_available():
                # Gerar embedding para busca semântica via API
                await embedding_api_service.update_document_embedding(document_file)
                
        except Exception as e:
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
            "created_at": document_file.uploaded_at.isoformat(),
            "relationship": "documento → order (mapa mental)",
            "intelligent_processing": {
                "enabled": True,
                "ocr_available": document_processor is not None,
                "embeddings_available": embedding_api_service.is_available(),
                "embedding_provider": embedding_api_service.current_provider
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
