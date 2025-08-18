from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Optional
from uuid import UUID
from beanie import PydanticObjectId

from ..models import Order, DocumentFile, CTEDocument, BLDocument, Container

router = APIRouter()

# === CRUD para Orders ===

@router.post("/orders", response_model=Order, status_code=201)
async def create_order(order: Order):
    await order.insert()
    return order

@router.get("/orders", response_model=List[Order])
async def list_orders(customer_name: Optional[str] = None, limit: int = 10, skip: int = 0):
    query = Order.find_all()
    if customer_name:
        query = Order.find(Order.customer_name == customer_name)
    return await query.skip(skip).limit(limit).to_list()

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: PydanticObjectId):
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: PydanticObjectId, order_update: dict = Body(...)):
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    updated_order = await order.update({"$set": order_update})
    return updated_order

@router.delete("/orders/{order_id}", status_code=204)
async def delete_order(order_id: PydanticObjectId):
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    await order.delete()
    return

# === Associação de documentos a uma Order ===

@router.post("/orders/{order_id}/documents", response_model=Order)
async def add_document_to_order(order_id: PydanticObjectId, file: DocumentFile):
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.other_documents.append(file)
    await order.save()
    return order

@router.post("/orders/{order_id}/link_cte/{cte_id}", response_model=Order)
async def link_cte_to_order(order_id: PydanticObjectId, cte_id: PydanticObjectId):
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    cte = await CTEDocument.get(cte_id)
    if not cte:
        raise HTTPException(status_code=404, detail="CTE Document not found")

    order.ctes.append(cte)
    cte.order = order
    await order.save()
    await cte.save()
    return order
