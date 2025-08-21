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
    priority: Optional[int] = Query(None, description="Filtrar por prioridade")
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