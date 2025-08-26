"""
Users Routes - Gatekeeper API

Rotas para gerenciamento de usuários:
- GET /users/me - Dados do usuário autenticado
- GET /users/{user_id} - Dados de usuário específico  
- POST /users - Criar novo usuário
- PUT /users/{user_id} - Atualizar usuário
- DELETE /users/{user_id} - Desativar usuário
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
import logging
from datetime import datetime

from ..models import User, UserRequest, UserRole
from ..database import DatabaseService
from ..services.auth_service import AuthService

logger = logging.getLogger("GatekeeperAPI.Users")
router = APIRouter()

auth_service = AuthService()


@router.get("/me")
async def get_current_user(user_id: str = Query(..., description="ID do usuário autenticado")):
    """
    Retorna dados do usuário autenticado
    
    Args:
        user_id: ID do usuário (passado como query parameter por simplicidade)
        
    Returns:
        Dados completos do usuário
    """
    try:
        user = await DatabaseService.get_user_by_email(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Obter estatísticas do usuário
        stats = await auth_service.get_user_stats(user_id)
        
        return {
            "user_id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count,
            "client": {
                "id": str(user.client.id) if user.client else None,
                "name": user.client.name if user.client else None
            } if user.client else None,
            "stats": stats,
            "permissions": auth_service.get_user_permissions(UserRole(user.role))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter dados do usuário {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição")
):
    """
    Retorna dados de um usuário específico
    Requer role admin para acessar dados de outros usuários
    """
    try:
        # Verificar permissões
        if current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem acessar dados de outros usuários"
            )
        
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return {
            "user_id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count,
            "client": {
                "id": str(user.client.id) if user.client else None,
                "name": user.client.name if user.client else None
            } if user.client else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter usuário {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/")
async def list_users(
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição"),
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de registros"),
    role_filter: Optional[str] = Query(None, description="Filtrar por role"),
    active_only: bool = Query(True, description="Apenas usuários ativos")
):
    """
    Lista usuários (apenas para admins)
    """
    try:
        # Verificar permissões
        if current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem listar usuários"
            )
        
        # Construir filtros
        filters = {}
        if role_filter:
            filters["role"] = role_filter
        if active_only:
            filters["is_active"] = True
        
        # Buscar usuários
        query = User.find(filters)
        users = await query.skip(skip).limit(limit).to_list()
        
        # Contar total
        total = await User.find(filters).count()
        
        return {
            "users": [
                {
                    "user_id": str(user.id),
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "login_count": user.login_count
                }
                for user in users
            ],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "has_more": skip + limit < total
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/")
async def create_user(
    user_request: UserRequest,
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição")
):
    """
    Cria novo usuário (apenas para admins)
    """
    try:
        # Verificar permissões
        if current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem criar usuários"
            )
        
        # Verificar se usuário já existe
        existing_user = await DatabaseService.get_user_by_email(user_request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário com este email já existe"
            )
        
        # Criar usuário
        new_user = await DatabaseService.create_user(
            name=user_request.name,
            email=user_request.email,
            role=user_request.role.value,
            client_id=user_request.client_id
        )
        
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar usuário"
            )
        
        logger.info(f"✅ Novo usuário criado: {user_request.email} por admin")
        
        return {
            "message": "Usuário criado com sucesso",
            "user": {
                "user_id": str(new_user.id),
                "name": new_user.name,
                "email": new_user.email,
                "role": new_user.role,
                "created_at": new_user.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_request: UserRequest,
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição")
):
    """
    Atualiza usuário existente (apenas para admins)
    """
    try:
        # Verificar permissões
        if current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem atualizar usuários"
            )
        
        # Buscar usuário
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Atualizar dados
        user.name = user_request.name
        user.email = user_request.email
        user.role = user_request.role
        
        # Atualizar client se fornecido
        if user_request.client_id:
            from ..models import Client
            client = await Client.get(user_request.client_id)
            if client:
                user.client = client
        
        await user.save()
        
        logger.info(f"✅ Usuário atualizado: {user_id} por admin")
        
        return {
            "message": "Usuário atualizado com sucesso",
            "user": {
                "user_id": str(user.id),
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição")
):
    """
    Desativa usuário (soft delete - apenas para admins)
    """
    try:
        # Verificar permissões
        if current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem desativar usuários"
            )
        
        # Buscar usuário
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Desativar usuário (soft delete)
        user.is_active = False
        await user.save()
        
        logger.info(f"✅ Usuário desativado: {user_id} por admin")
        
        return {
            "message": "Usuário desativado com sucesso",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desativar usuário {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/stats/summary")
async def get_users_summary(
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição")
):
    """
    Retorna resumo estatístico dos usuários (apenas para admins)
    """
    try:
        # Verificar permissões
        if current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem ver estatísticas"
            )
        
        # Contar usuários por role
        role_counts = {}
        for role in UserRole:
            count = await User.find({"role": role.value, "is_active": True}).count()
            role_counts[role.value] = count
        
        # Contar usuários ativos vs inativos
        active_count = await User.find({"is_active": True}).count()
        inactive_count = await User.find({"is_active": False}).count()
        
        # Contar total de usuários
        total_count = await User.find({}).count()
        
        return {
            "total_users": total_count,
            "active_users": active_count,
            "inactive_users": inactive_count,
            "users_by_role": role_counts,
            "active_sessions": auth_service.get_active_sessions_count(),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de usuários: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )