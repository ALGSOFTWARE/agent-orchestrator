"""
Endpoints para gerenciamento de Orders (Super-contêineres logísticos)
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel

from ..models import Order, OrderType, OrderStatus, DocumentFile
from datetime import datetime

router = APIRouter()

# Schemas para requests
class CreateOrderRequest(BaseModel):
    title: str
    description: Optional[str] = None
    order_type: OrderType
    customer_name: str
    customer_id: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    expected_delivery: Optional[datetime] = None
    estimated_value: Optional[float] = None
    currency: str = "BRL"
    tags: List[str] = []
    priority: int = 3
    assigned_users: List[str] = []

class UpdateOrderRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[OrderStatus] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    expected_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    estimated_value: Optional[float] = None
    actual_cost: Optional[float] = None
    tags: Optional[List[str]] = None
    priority: Optional[int] = None
    assigned_users: Optional[List[str]] = None

class AddNoteRequest(BaseModel):
    content: str
    note_type: str = "comment"

# === CRUD ENDPOINTS === #

@router.get("/", response_model=List[Order])
async def list_orders(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Limite de registros"),
    status: Optional[OrderStatus] = Query(None, description="Filtrar por status"),
    order_type: Optional[OrderType] = Query(None, description="Filtrar por tipo"),
    customer: Optional[str] = Query(None, description="Filtrar por cliente"),
    priority: Optional[int] = Query(None, description="Filtrar por prioridade"),
    search: Optional[str] = Query(None, description="Buscar em título, cliente, tags e descrição")
):
    """Lista todas as orders com filtros opcionais"""
    try:
        # Construir filtros
        filters = {}
        if status:
            filters["status"] = status
        if order_type:
            filters["order_type"] = order_type
        if customer:
            filters["customer_name"] = {"$regex": customer, "$options": "i"}
        if priority:
            filters["priority"] = priority
            
        # Implementar busca full-text
        if search:
            search_conditions = []
            search_regex = {"$regex": search, "$options": "i"}
            
            # Buscar em múltiplos campos
            search_conditions.extend([
                {"title": search_regex},
                {"customer_name": search_regex},
                {"description": search_regex},
                {"origin": search_regex},
                {"destination": search_regex},
                {"tags": {"$elemMatch": search_regex}}
            ])
            
            # Se já existem outros filtros, combinar com AND
            if filters:
                filters = {"$and": [filters, {"$or": search_conditions}]}
            else:
                filters = {"$or": search_conditions}
            
        # Buscar com paginação
        orders = await Order.find(filters).skip(skip).limit(limit).to_list()
        return orders
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar orders: {str(e)}")

@router.post("/", response_model=Order)
async def create_order(order_data: CreateOrderRequest):
    """Cria uma nova order"""
    try:
        # Criar a order
        order = Order(
            title=order_data.title,
            description=order_data.description,
            order_type=order_data.order_type,
            customer_name=order_data.customer_name,
            customer_id=order_data.customer_id,
            origin=order_data.origin,
            destination=order_data.destination,
            expected_delivery=order_data.expected_delivery,
            estimated_value=order_data.estimated_value,
            currency=order_data.currency,
            tags=order_data.tags,
            priority=order_data.priority,
            assigned_users=order_data.assigned_users
        )
        
        # Salvar no banco
        await order.save()
        
        return order
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar order: {str(e)}")

@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Busca uma order por ID"""
    try:
        order = await Order.find_one(Order.order_id == order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order não encontrada")
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar order: {str(e)}")

@router.put("/{order_id}", response_model=Order)
async def update_order(order_id: str, update_data: UpdateOrderRequest):
    """Atualiza uma order"""
    try:
        order = await Order.find_one(Order.order_id == order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order não encontrada")
        
        # Atualizar campos
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(order, field):
                setattr(order, field, value)
        
        # Atualizar timestamp
        order.updated_at = datetime.utcnow()
        order.last_activity = datetime.utcnow()
        
        await order.save()
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar order: {str(e)}")

@router.delete("/{order_id}")
async def delete_order(order_id: str):
    """Remove uma order"""
    try:
        order = await Order.find_one(Order.order_id == order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order não encontrada")
        
        await order.delete()
        return {"message": "Order removida com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover order: {str(e)}")

# === ENDPOINTS ESPECIALIZADOS === #

@router.get("/{order_id}/summary")
async def get_order_summary(order_id: str):
    """Retorna resumo da order para dashboards"""
    try:
        order = await Order.find_one(Order.order_id == order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order não encontrada")
        
        return order.get_summary()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resumo: {str(e)}")

@router.post("/{order_id}/notes")
async def add_note(order_id: str, note_data: AddNoteRequest, user_id: str = "system"):
    """Adiciona nota à order"""
    try:
        order = await Order.find_one(Order.order_id == order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order não encontrada")
        
        order.add_note(note_data.content, user_id, note_data.note_type)
        await order.save()
        
        return {"message": "Nota adicionada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar nota: {str(e)}")

@router.put("/{order_id}/status")
async def change_status(order_id: str, new_status: OrderStatus, user_id: str = "system", notes: Optional[str] = None):
    """Muda status da order"""
    try:
        order = await Order.find_one(Order.order_id == order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order não encontrada")
        
        order.add_status_change(new_status, user_id, notes)
        await order.save()
        
        return {"message": f"Status alterado para {new_status.value}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao alterar status: {str(e)}")

@router.get("/{order_id}/documents", response_model=List[DocumentFile])
async def get_order_documents(order_id: str):
    """Lista todos os documentos de uma order"""
    try:
        # Buscar documentos vinculados à order
        documents = await DocumentFile.find(DocumentFile.order_id == order_id).to_list()
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar documentos: {str(e)}")

@router.post("/{order_id}/documents/{document_id}")
async def link_document_to_order(order_id: str, document_id: str):
    """Vincula um documento existente à order"""
    try:
        # Buscar order
        order = await Order.find_one(Order.order_id == order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order não encontrada")
        
        # Buscar documento
        document = await DocumentFile.find_one(DocumentFile.file_id == document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        # Vincular
        document.order_id = order_id
        await document.save()
        
        # Atualizar contador na order
        order.document_count += 1
        order.last_activity = datetime.utcnow()
        await order.save()
        
        return {"message": "Documento vinculado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao vincular documento: {str(e)}")

# === ENDPOINTS DE ESTATÍSTICAS === #

@router.get("/stats/overview")
async def get_orders_stats():
    """Estatísticas gerais das orders"""
    try:
        total_orders = await Order.count()
        
        # Contar por status
        stats_by_status = {}
        for status in OrderStatus:
            count = await Order.find(Order.status == status).count()
            stats_by_status[status.value] = count
        
        # Contar por tipo
        stats_by_type = {}
        for order_type in OrderType:
            count = await Order.find(Order.order_type == order_type).count()
            stats_by_type[order_type.value] = count
        
        return {
            "total_orders": total_orders,
            "by_status": stats_by_status,
            "by_type": stats_by_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar estatísticas: {str(e)}")

# === ENDPOINTS ADMINISTRATIVOS === #

@router.post("/admin/fix-document-links")
async def fix_document_links():
    """
    Endpoint administrativo para corrigir Links entre Orders e DocumentFiles
    
    Problema: Orders têm document_count correto mas document_files array vazio
    Solução: Buscar DocumentFiles por order_id e criar Links corretos
    """
    try:
        from beanie import Link
        
        print("🔧 Iniciando correção de links Orders ↔ DocumentFiles...")
        
        # Contadores
        orders_fixed = 0
        links_created = 0
        errors = []
        
        # Encontrar Orders com problema (document_count > 0 mas document_files vazio)
        problematic_orders = []
        async for order in Order.find(Order.document_count > 0):
            if len(order.document_files) == 0:
                # Verificar se realmente existem documentos
                doc_count = await DocumentFile.find(DocumentFile.order_id == order.order_id).count()
                if doc_count > 0:
                    problematic_orders.append(order)
        
        if not problematic_orders:
            return {
                "message": "✅ Nenhuma Order com problema encontrada",
                "orders_analyzed": await Order.find(Order.document_count > 0).count(),
                "orders_fixed": 0,
                "links_created": 0
            }
        
        print(f"📊 Encontradas {len(problematic_orders)} Orders para corrigir...")
        
        # Corrigir cada Order
        for order in problematic_orders:
            try:
                # Buscar DocumentFiles vinculados
                documents = await DocumentFile.find(DocumentFile.order_id == order.order_id).to_list()
                
                if not documents:
                    errors.append(f"Order {order.order_id}: Nenhum documento encontrado")
                    continue
                
                # Criar Links para cada documento
                new_links = []
                for doc in documents:
                    link = Link(doc.id, DocumentFile)
                    new_links.append(link)
                
                # Atualizar a Order
                order.document_files = new_links
                order.updated_at = datetime.utcnow()
                order.last_activity = datetime.utcnow()
                
                # Corrigir document_count se necessário
                if order.document_count != len(documents):
                    order.document_count = len(documents)
                
                # Salvar
                await order.save()
                
                orders_fixed += 1
                links_created += len(new_links)
                
                print(f"✅ Order {order.order_id}: {len(new_links)} links criados")
                
            except Exception as e:
                error_msg = f"Order {order.order_id}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        # Validar correção
        remaining_problems = 0
        async for order in Order.find(Order.document_count > 0):
            if len(order.document_files) == 0:
                doc_count = await DocumentFile.find(DocumentFile.order_id == order.order_id).count()
                if doc_count > 0:
                    remaining_problems += 1
        
        result = {
            "message": "🛠️  Correção de links concluída",
            "orders_analyzed": len(problematic_orders),
            "orders_fixed": orders_fixed,
            "links_created": links_created,
            "remaining_problems": remaining_problems,
            "errors": errors[:5],  # Mostrar apenas primeiros 5 erros
            "validation": "✅ Sucesso" if remaining_problems == 0 else f"⚠️  {remaining_problems} Orders ainda com problema",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"📊 Resultado final: {orders_fixed} Orders corrigidas, {links_created} links criados")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na correção de links: {str(e)}")

@router.get("/admin/diagnose-links")
async def diagnose_document_links():
    """
    Endpoint para diagnosticar problemas de links entre Orders e DocumentFiles
    """
    try:
        # Estatísticas gerais
        total_orders = await Order.count()
        orders_with_count = await Order.find(Order.document_count > 0).count()
        total_documents = await DocumentFile.count()
        
        # Encontrar problemas
        problems = []
        orders_ok = 0
        
        async for order in Order.find(Order.document_count > 0).limit(20):  # Analisar 20 primeiras
            doc_count_field = order.document_count
            doc_files_length = len(order.document_files)
            actual_docs = await DocumentFile.find(DocumentFile.order_id == order.order_id).count()
            
            if doc_files_length != actual_docs:
                problems.append({
                    "order_id": order.order_id,
                    "title": order.title[:50] + "..." if len(order.title) > 50 else order.title,
                    "customer": order.customer_name,
                    "document_count_field": doc_count_field,
                    "document_files_length": doc_files_length,
                    "actual_documents": actual_docs,
                    "status": "INCONSISTENT" if doc_files_length == 0 and actual_docs > 0 else "MISMATCH"
                })
            else:
                orders_ok += 1
        
        return {
            "diagnosis": "📊 Diagnóstico Links Orders ↔ DocumentFiles",
            "statistics": {
                "total_orders": total_orders,
                "orders_with_documents": orders_with_count,
                "total_documents": total_documents,
                "orders_analyzed": min(20, orders_with_count),
                "orders_ok": orders_ok,
                "orders_with_problems": len(problems)
            },
            "problems": problems,
            "recommendation": "Use POST /orders/admin/fix-document-links para corrigir" if problems else "✅ Sistema funcionando corretamente",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no diagnóstico: {str(e)}")