"""
Authentication Routes - Gatekeeper API

Rotas responsáveis pela autenticação e autorização:
- POST /auth/callback - Callback de autenticação externa
- GET /auth/login - Redirecionamento para Identity Provider
- POST /auth/validate - Validação de token/sessão
- GET /auth/roles - Lista de roles disponíveis
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, List, Any
import logging
from datetime import datetime
import httpx

from ..models import (
    AuthPayload, 
    GatekeeperResponse, 
    AgentStatus, 
    UserRole,
    ErrorResponse
)
from ..database import DatabaseService
from ..services.auth_service import AuthService
from ..services.crewai_service import CrewAIService

logger = logging.getLogger("GatekeeperAPI.Auth")
router = APIRouter()

# Instâncias dos serviços
auth_service = AuthService()
crewai_service = CrewAIService()

# Configuração de mapeamento de roles para agentes
ROLE_AGENT_MAP = {
    UserRole.ADMIN: "AdminAgent",
    UserRole.LOGISTICS: "LogisticsAgent", 
    UserRole.FINANCE: "FinanceAgent",
    UserRole.OPERATOR: "LogisticsAgent"  # Operador usa o mesmo agente de logística
}

# Configuração de permissões por role
ROLE_PERMISSIONS = {
    UserRole.ADMIN: ["*"],  # Acesso total
    UserRole.LOGISTICS: [
        "read:cte", "write:document", "read:container", 
        "write:tracking", "read:shipment"
    ],
    UserRole.FINANCE: [
        "read:financial", "write:financial", "read:payment",
        "write:payment", "read:billing"
    ],
    UserRole.OPERATOR: [
        "read:cte", "write:document", "read:container"
    ]
}


@router.post("/callback", response_model=GatekeeperResponse)
async def auth_callback(payload: AuthPayload):
    """
    Endpoint principal que recebe callbacks da API de autenticação externa
    
    Fluxo:
    1. Valida payload recebido
    2. Verifica se role é válido  
    3. Valida permissões
    4. Cria/atualiza usuário no banco
    5. Roteia para agente apropriado via CrewAI
    6. Salva contexto da interação
    7. Retorna resposta consolidada
    """
    try:
        logger.info(f"🔐 Callback de autenticação para usuário {payload.userId} com role {payload.role}")
        
        # 1. Validar role
        if payload.role not in ROLE_AGENT_MAP:
            logger.warning(f"❌ Role inválido: {payload.role} para usuário {payload.userId}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{payload.role}' não autorizado no sistema"
            )
        
        # 2. Validar permissões
        if payload.permissions and not auth_service.validate_permissions(payload.role, payload.permissions):
            logger.warning(f"❌ Permissões inválidas para role {payload.role}: {payload.permissions}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissões solicitadas não compatíveis com o role do usuário"
            )
        
        # 3. Criar/atualizar usuário no banco
        user = await auth_service.create_or_update_user(payload)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar dados do usuário"
            )
        
        # 4. Rotear para agente apropriado
        agent_name = ROLE_AGENT_MAP[payload.role]
        logger.info(f"🚀 Roteando usuário {payload.userId} para {agent_name}")
        
        # Preparar contexto do usuário
        user_context = {
            "userId": payload.userId,
            "userName": user.name,
            "userEmail": user.email,
            "role": payload.role.value,
            "permissions": payload.permissions or ROLE_PERMISSIONS[payload.role],
            "sessionId": payload.sessionId,
            "timestamp": payload.timestamp.isoformat() if payload.timestamp else datetime.now().isoformat()
        }
        
        # Preparar dados da requisição inicial
        request_data = {
            "type": "authentication_success",
            "message": f"Usuário {payload.userId} autenticado com sucesso",
            "timestamp": datetime.now().isoformat(),
            "initial_access": True,
            "user_info": {
                "name": user.name,
                "email": user.email,
                "role": payload.role.value,
                "login_count": user.login_count
            }
        }
        
        # 5. Chamar agente via CrewAI service
        agent_response = await crewai_service.route_to_agent(
            agent_name=agent_name,
            user_context=user_context,
            request_data=request_data
        )
        
        # 6. Salvar contexto da interação
        await DatabaseService.add_context(
            user_id=payload.userId,
            input_text=f"Autenticação bem-sucedida - Role: {payload.role.value}",
            output_text=str(agent_response),
            agents=[agent_name],
            session_id=payload.sessionId,
            metadata={
                "auth_timestamp": datetime.now().isoformat(),
                "role": payload.role.value,
                "permissions": payload.permissions
            }
        )
        
        # 7. Retornar resposta de sucesso
        response = GatekeeperResponse(
            status=AgentStatus.SUCCESS,
            agent=agent_name,
            message=f"Usuário autenticado e conectado ao {agent_name}",
            userId=payload.userId,
            data={
                "agent_response": agent_response,
                "user_context": user_context,
                "available_actions": _get_available_actions(payload.role),
                "routing_success": True
            }
        )
        
        logger.info(f"✅ Autenticação processada com sucesso para usuário {payload.userId}")
        return response
        
    except HTTPException:
        # Re-raise HTTPExceptions (já tratadas)
        raise
    except Exception as e:
        logger.error(f"❌ Erro interno no processamento de autenticação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/login")
async def auth_login(redirect_uri: str = None):
    """
    Endpoint que redireciona para o Identity Provider
    Em produção, isso redirecionaria para Google, Microsoft, etc.
    """
    # Por enquanto, retorna informações de como fazer login
    return {
        "message": "Redirecionamento para Identity Provider",
        "redirect_uri": redirect_uri,
        "supported_providers": ["Google", "Microsoft", "Auth0"],
        "callback_url": "/auth/callback",
        "instructions": "Envie um POST para /auth/callback com o payload de autenticação"
    }


@router.post("/validate")
async def validate_session(session_id: str, user_id: str):
    """
    Valida se uma sessão ainda é válida
    """
    try:
        # Verificar se usuário existe
        user = await DatabaseService.get_user_by_email(user_id)  # Assumindo user_id como email por simplicidade
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar contexto recente da sessão
        contexts = await DatabaseService.get_user_context(user_id, limit=1)
        
        return {
            "status": "valid",
            "user_id": user_id,
            "session_id": session_id,
            "user_name": user.name,
            "role": user.role,
            "last_activity": contexts[0].timestamp if contexts else None,
            "is_active": user.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na validação de sessão: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro na validação de sessão"
        )


@router.get("/roles")
async def list_roles():
    """Lista roles disponíveis e suas permissões"""
    return {
        "available_roles": [role.value for role in UserRole],
        "role_agent_mapping": {role.value: agent for role, agent in ROLE_AGENT_MAP.items()},
        "role_permissions": {
            role.value: permissions 
            for role, permissions in ROLE_PERMISSIONS.items()
        }
    }


@router.get("/status")
async def auth_status():
    """Status do serviço de autenticação"""
    db_healthy = await DatabaseService.health_check()
    crewai_healthy = await crewai_service.health_check()
    
    return {
        "service": "Gatekeeper Auth",
        "status": "healthy" if db_healthy and crewai_healthy else "degraded",
        "components": {
            "database": "healthy" if db_healthy else "unhealthy",
            "crewai_service": "healthy" if crewai_healthy else "unhealthy"
        },
        "supported_roles": list(ROLE_AGENT_MAP.keys()),
        "timestamp": datetime.now().isoformat()
    }


def _get_available_actions(role: UserRole) -> List[str]:
    """Retorna ações disponíveis baseadas no role"""
    base_actions = ["view_profile", "logout"]
    
    if role == UserRole.ADMIN:
        return base_actions + [
            "view_all_users", "manage_users", "view_system_stats",
            "manage_clients", "view_all_shipments", "system_admin"
        ]
    elif role == UserRole.LOGISTICS:
        return base_actions + [
            "upload_documents", "track_containers", "manage_shipments",
            "view_cte", "update_tracking", "view_delivery_status"
        ]
    elif role == UserRole.FINANCE:
        return base_actions + [
            "view_financial_reports", "manage_payments", "view_billing",
            "export_financial_data", "manage_invoices"
        ]
    elif role == UserRole.OPERATOR:
        return base_actions + [
            "upload_documents", "view_cte", "track_containers", "basic_shipment_view"
        ]
    
    return base_actions