"""
CRUD Routes - Gatekeeper API
Endpoints completos para operações CRUD em todos os modelos do banco de dados.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from datetime import datetime, timedelta

from ..models import (
    User, Client, Container, Shipment, TrackingEvent, Context,
    UserRequest, UserRole
)
from ..database import DatabaseService

# Criar router para endpoints CRUD
crud_router = APIRouter(prefix="/api/crud", tags=["CRUD Operations"])

# =====================================================
# USER CRUD ENDPOINTS
# =====================================================

@crud_router.get("/users", response_model=List[User])
async def list_users(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    role: Optional[UserRole] = Query(None, description="Filtrar por role"),
    active_only: bool = Query(True, description="Apenas usuários ativos")
):
    """Lista todos os usuários com paginação e filtros"""
    try:
        # Construir filtros
        filters = {}
        if role:
            filters["role"] = role
        if active_only:
            filters["is_active"] = True
            
        # Buscar usuários
        if filters:
            users = await User.find(filters).skip(skip).limit(limit).to_list()
        else:
            users = await User.find_all().skip(skip).limit(limit).to_list()
            
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários: {str(e)}")


@crud_router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str = Path(..., description="ID do usuário")
):
    """Busca usuário por ID"""
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")


@crud_router.post("/users", response_model=User, status_code=201)
async def create_user(user_data: UserRequest):
    """Cria um novo usuário"""
    try:
        # Verificar se email já existe
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
            
        # Verificar se client existe (se fornecido)
        client = None
        if user_data.client_id:
            client = await Client.get(user_data.client_id)
            if not client:
                raise HTTPException(status_code=400, detail="Cliente não encontrado")
        
        # Criar usuário
        user = User(
            name=user_data.name,
            email=user_data.email,
            role=user_data.role,
            client=client
        )
        
        await user.insert()
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")


@crud_router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str = Path(..., description="ID do usuário"),
    user_data: UserRequest = ...
):
    """Atualiza um usuário existente"""
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
        # Verificar se email já existe (exceto o próprio usuário)
        if user_data.email != user.email:
            existing_user = await User.find_one(User.email == user_data.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        # Verificar client (se fornecido)
        client = None
        if user_data.client_id:
            client = await Client.get(user_data.client_id)
            if not client:
                raise HTTPException(status_code=400, detail="Cliente não encontrado")
        
        # Atualizar dados
        user.name = user_data.name
        user.email = user_data.email
        user.role = user_data.role
        user.client = client
        
        await user.save()
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")


@crud_router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str = Path(..., description="ID do usuário"),
    soft_delete: bool = Query(True, description="Soft delete (desativar) ou hard delete")
):
    """Remove um usuário (soft ou hard delete)"""
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
        if soft_delete:
            # Soft delete - apenas desativar
            user.is_active = False
            await user.save()
        else:
            # Hard delete - remover definitivamente
            await user.delete()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover usuário: {str(e)}")


# =====================================================
# CLIENT CRUD ENDPOINTS
# =====================================================

@crud_router.get("/clients", response_model=List[Client])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Lista todos os clientes"""
    try:
        clients = await Client.find_all().skip(skip).limit(limit).to_list()
        return clients
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar clientes: {str(e)}")


@crud_router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: str = Path(...)):
    """Busca cliente por ID"""
    try:
        client = await Client.get(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cliente: {str(e)}")


@crud_router.post("/clients", response_model=Client, status_code=201)
async def create_client(client_data: dict):
    """Cria um novo cliente"""
    try:
        # Validar CNPJ único (se fornecido)
        if client_data.get('cnpj'):
            existing = await Client.find_one(Client.cnpj == client_data['cnpj'])
            if existing:
                raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
        
        client = Client(**client_data)
        await client.insert()
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar cliente: {str(e)}")


@crud_router.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: str = Path(...), client_data: dict = ...):
    """Atualiza um cliente"""
    try:
        client = await Client.get(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
            
        # Validar CNPJ único (se alterado)
        if client_data.get('cnpj') and client_data['cnpj'] != client.cnpj:
            existing = await Client.find_one(Client.cnpj == client_data['cnpj'])
            if existing:
                raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
        
        # Atualizar campos
        for key, value in client_data.items():
            if hasattr(client, key):
                setattr(client, key, value)
                
        await client.save()
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar cliente: {str(e)}")


@crud_router.delete("/clients/{client_id}", status_code=204)
async def delete_client(client_id: str = Path(...)):
    """Remove um cliente"""
    try:
        client = await Client.get(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
            
        # Verificar se há usuários vinculados
        users_count = await User.find(User.client.id == client_id).count()
        if users_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Não é possível remover cliente com {users_count} usuários vinculados"
            )
            
        await client.delete()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover cliente: {str(e)}")


# =====================================================
# CONTAINER CRUD ENDPOINTS
# =====================================================

@crud_router.get("/containers", response_model=List[Container])
async def list_containers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filtrar por status")
):
    """Lista todos os containers"""
    try:
        filters = {}
        if status:
            filters["current_status"] = status
            
        if filters:
            containers = await Container.find(filters).skip(skip).limit(limit).to_list()
        else:
            containers = await Container.find_all().skip(skip).limit(limit).to_list()
            
        return containers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar containers: {str(e)}")


@crud_router.get("/containers/{container_id}", response_model=Container)
async def get_container(container_id: str = Path(...)):
    """Busca container por ID"""
    try:
        container = await Container.get(container_id)
        if not container:
            raise HTTPException(status_code=404, detail="Container não encontrado")
        return container
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar container: {str(e)}")


@crud_router.post("/containers", response_model=Container, status_code=201)
async def create_container(container_data: dict):
    """Cria um novo container"""
    try:
        # Validar número único
        if container_data.get('container_number'):
            existing = await Container.find_one(
                Container.container_number == container_data['container_number']
            )
            if existing:
                raise HTTPException(status_code=400, detail="Número de container já existe")
        
        container = Container(**container_data)
        await container.insert()
        return container
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar container: {str(e)}")


@crud_router.put("/containers/{container_id}", response_model=Container)
async def update_container(container_id: str = Path(...), container_data: dict = ...):
    """Atualiza um container"""
    try:
        container = await Container.get(container_id)
        if not container:
            raise HTTPException(status_code=404, detail="Container não encontrado")
            
        # Validar número único (se alterado)
        if (container_data.get('container_number') and 
            container_data['container_number'] != container.container_number):
            existing = await Container.find_one(
                Container.container_number == container_data['container_number']
            )
            if existing:
                raise HTTPException(status_code=400, detail="Número de container já existe")
        
        # Atualizar campos
        for key, value in container_data.items():
            if hasattr(container, key):
                setattr(container, key, value)
                
        container.updated_at = datetime.utcnow()
        await container.save()
        return container
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar container: {str(e)}")


@crud_router.delete("/containers/{container_id}", status_code=204)
async def delete_container(container_id: str = Path(...)):
    """Remove um container"""
    try:
        container = await Container.get(container_id)
        if not container:
            raise HTTPException(status_code=404, detail="Container não encontrado")
            
        # Verificar dependências
        shipments_count = await Shipment.find(
            Shipment.containers.id == container_id
        ).count()
        if shipments_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Container está vinculado a {shipments_count} embarques"
            )
            
        await container.delete()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover container: {str(e)}")


# =====================================================
# SHIPMENT CRUD ENDPOINTS
# =====================================================

@crud_router.get("/shipments", response_model=List[Shipment])
async def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    client_id: Optional[str] = Query(None, description="Filtrar por cliente")
):
    """Lista todos os embarques"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if client_id:
            filters["client.id"] = client_id
            
        if filters:
            shipments = await Shipment.find(filters).skip(skip).limit(limit).to_list()
        else:
            shipments = await Shipment.find_all().skip(skip).limit(limit).to_list()
            
        return shipments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar embarques: {str(e)}")


@crud_router.get("/shipments/{shipment_id}", response_model=Shipment)
async def get_shipment(shipment_id: str = Path(...)):
    """Busca embarque por ID"""
    try:
        shipment = await Shipment.get(shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Embarque não encontrado")
        return shipment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar embarque: {str(e)}")


@crud_router.post("/shipments", response_model=Shipment, status_code=201)
async def create_shipment(shipment_data: dict):
    """Cria um novo embarque"""
    try:
        # Validar cliente
        if not shipment_data.get('client_id'):
            raise HTTPException(status_code=400, detail="client_id é obrigatório")
            
        client = await Client.get(shipment_data['client_id'])
        if not client:
            raise HTTPException(status_code=400, detail="Cliente não encontrado")
        
        # Validar containers (se fornecidos)
        containers = []
        if shipment_data.get('container_ids'):
            for container_id in shipment_data['container_ids']:
                container = await Container.get(container_id)
                if not container:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Container {container_id} não encontrado"
                    )
                containers.append(container)
        
        # Preparar dados para criação
        creation_data = {k: v for k, v in shipment_data.items() 
                        if k not in ['client_id', 'container_ids']}
        creation_data['client'] = client
        creation_data['containers'] = containers
        
        shipment = Shipment(**creation_data)
        await shipment.insert()
        return shipment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar embarque: {str(e)}")


@crud_router.put("/shipments/{shipment_id}", response_model=Shipment)
async def update_shipment(shipment_id: str = Path(...), shipment_data: dict = ...):
    """Atualiza um embarque"""
    try:
        shipment = await Shipment.get(shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Embarque não encontrado")
            
        # Validar cliente (se alterado)
        if shipment_data.get('client_id'):
            client = await Client.get(shipment_data['client_id'])
            if not client:
                raise HTTPException(status_code=400, detail="Cliente não encontrado")
            shipment.client = client
        
        # Validar containers (se alterados)
        if shipment_data.get('container_ids'):
            containers = []
            for container_id in shipment_data['container_ids']:
                container = await Container.get(container_id)
                if not container:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Container {container_id} não encontrado"
                    )
                containers.append(container)
            shipment.containers = containers
        
        # Atualizar outros campos
        exclude_fields = ['client_id', 'container_ids']
        for key, value in shipment_data.items():
            if key not in exclude_fields and hasattr(shipment, key):
                setattr(shipment, key, value)
                
        await shipment.save()
        return shipment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar embarque: {str(e)}")


@crud_router.delete("/shipments/{shipment_id}", status_code=204)
async def delete_shipment(shipment_id: str = Path(...)):
    """Remove um embarque"""
    try:
        shipment = await Shipment.get(shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Embarque não encontrado")
            
        # Verificar dependências
        events_count = await TrackingEvent.find(
            TrackingEvent.shipment.id == shipment_id
        ).count()
        if events_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Embarque possui {events_count} eventos de rastreamento"
            )
            
        await shipment.delete()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover embarque: {str(e)}")


# =====================================================
# TRACKING EVENT CRUD ENDPOINTS
# =====================================================

@crud_router.get("/tracking-events", response_model=List[TrackingEvent])
async def list_tracking_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = Query(None, description="Filtrar por tipo"),
    container_id: Optional[str] = Query(None, description="Filtrar por container"),
    shipment_id: Optional[str] = Query(None, description="Filtrar por embarque")
):
    """Lista todos os eventos de rastreamento"""
    try:
        filters = {}
        if type:
            filters["type"] = type
        if container_id:
            filters["container.id"] = container_id
        if shipment_id:
            filters["shipment.id"] = shipment_id
            
        if filters:
            events = await TrackingEvent.find(filters).skip(skip).limit(limit).to_list()
        else:
            events = await TrackingEvent.find_all().skip(skip).limit(limit).to_list()
            
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar eventos: {str(e)}")


@crud_router.get("/tracking-events/{event_id}", response_model=TrackingEvent)
async def get_tracking_event(event_id: str = Path(...)):
    """Busca evento de rastreamento por ID"""
    try:
        event = await TrackingEvent.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar evento: {str(e)}")


@crud_router.post("/tracking-events", response_model=TrackingEvent, status_code=201)
async def create_tracking_event(event_data: dict):
    """Cria um novo evento de rastreamento"""
    try:
        # Validar container (se fornecido)
        container = None
        if event_data.get('container_id'):
            container = await Container.get(event_data['container_id'])
            if not container:
                raise HTTPException(status_code=400, detail="Container não encontrado")
        
        # Validar shipment (se fornecido)
        shipment = None
        if event_data.get('shipment_id'):
            shipment = await Shipment.get(event_data['shipment_id'])
            if not shipment:
                raise HTTPException(status_code=400, detail="Embarque não encontrado")
        
        # Preparar dados
        creation_data = {k: v for k, v in event_data.items() 
                        if k not in ['container_id', 'shipment_id']}
        creation_data['container'] = container
        creation_data['shipment'] = shipment
        
        event = TrackingEvent(**creation_data)
        await event.insert()
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar evento: {str(e)}")


@crud_router.put("/tracking-events/{event_id}", response_model=TrackingEvent)
async def update_tracking_event(event_id: str = Path(...), event_data: dict = ...):
    """Atualiza um evento de rastreamento"""
    try:
        event = await TrackingEvent.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
            
        # Validar container (se alterado)
        if event_data.get('container_id'):
            container = await Container.get(event_data['container_id'])
            if not container:
                raise HTTPException(status_code=400, detail="Container não encontrado")
            event.container = container
        
        # Validar shipment (se alterado)
        if event_data.get('shipment_id'):
            shipment = await Shipment.get(event_data['shipment_id'])
            if not shipment:
                raise HTTPException(status_code=400, detail="Embarque não encontrado")
            event.shipment = shipment
        
        # Atualizar outros campos
        exclude_fields = ['container_id', 'shipment_id']
        for key, value in event_data.items():
            if key not in exclude_fields and hasattr(event, key):
                setattr(event, key, value)
                
        await event.save()
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar evento: {str(e)}")


@crud_router.delete("/tracking-events/{event_id}", status_code=204)
async def delete_tracking_event(event_id: str = Path(...)):
    """Remove um evento de rastreamento"""
    try:
        event = await TrackingEvent.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
            
        await event.delete()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover evento: {str(e)}")


# =====================================================
# CONTEXT CRUD ENDPOINTS
# =====================================================

@crud_router.get("/contexts", response_model=List[Context])
async def list_contexts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[str] = Query(None, description="Filtrar por usuário"),
    session_id: Optional[str] = Query(None, description="Filtrar por sessão")
):
    """Lista todos os contextos/interações"""
    try:
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if session_id:
            filters["session_id"] = session_id
            
        if filters:
            contexts = await Context.find(filters).skip(skip).limit(limit).to_list()
        else:
            contexts = await Context.find_all().skip(skip).limit(limit).to_list()
            
        return contexts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar contextos: {str(e)}")


@crud_router.get("/contexts/{context_id}", response_model=Context)
async def get_context(context_id: str = Path(...)):
    """Busca contexto por ID"""
    try:
        context = await Context.get(context_id)
        if not context:
            raise HTTPException(status_code=404, detail="Contexto não encontrado")
        return context
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar contexto: {str(e)}")


@crud_router.post("/contexts", response_model=Context, status_code=201)
async def create_context(context_data: dict):
    """Cria um novo contexto/interação"""
    try:
        context = Context(**context_data)
        await context.insert()
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar contexto: {str(e)}")


@crud_router.put("/contexts/{context_id}", response_model=Context)
async def update_context(context_id: str = Path(...), context_data: dict = ...):
    """Atualiza um contexto"""
    try:
        context = await Context.get(context_id)
        if not context:
            raise HTTPException(status_code=404, detail="Contexto não encontrado")
            
        # Atualizar campos
        for key, value in context_data.items():
            if hasattr(context, key):
                setattr(context, key, value)
                
        await context.save()
        return context
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar contexto: {str(e)}")


@crud_router.delete("/contexts/{context_id}", status_code=204)
async def delete_context(context_id: str = Path(...)):
    """Remove um contexto"""
    try:
        context = await Context.get(context_id)
        if not context:
            raise HTTPException(status_code=404, detail="Contexto não encontrado")
            
        await context.delete()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover contexto: {str(e)}")


# =====================================================
# BULK OPERATIONS & UTILITIES
# =====================================================

@crud_router.get("/stats")
async def get_database_stats():
    """Estatísticas gerais do banco de dados"""
    try:
        stats = {
            "users": await User.count(),
            "clients": await Client.count(),
            "containers": await Container.count(),
            "shipments": await Shipment.count(),
            "tracking_events": await TrackingEvent.count(),
            "contexts": await Context.count(),
            "active_users": await User.find(User.is_active == True).count(),
            "timestamp": datetime.utcnow()
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")


@crud_router.post("/bulk-delete")
async def bulk_delete_by_filters(filters: dict):
    """Operação de exclusão em massa (cuidado!)"""
    try:
        if not filters:
            raise HTTPException(status_code=400, detail="Filtros são obrigatórios para bulk delete")
            
        results = {}
        
        # Implementar bulk delete para cada modelo conforme necessário
        # Exemplo para contextos mais antigos que X dias
        if filters.get('delete_old_contexts'):
            days = filters.get('days', 30)
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted_contexts = await Context.find(
                Context.timestamp < cutoff_date
            ).delete()
            results['deleted_contexts'] = deleted_contexts.deleted_count
            
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na exclusão em massa: {str(e)}")