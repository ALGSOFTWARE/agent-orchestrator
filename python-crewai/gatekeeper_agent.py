#!/usr/bin/env python3
"""
Gatekeeper Agent - Sistema de Logística Inteligente

O Gatekeeper Agent é o ponto de entrada do sistema que:
1. Recebe requisições da API de autenticação externa
2. Valida roles e permissões do usuário
3. Roteia requisições para agentes especializados (Logistics, Finance, Admin)
4. Retorna respostas consolidadas

Stack:
- FastAPI para endpoints REST
- CrewAI para orquestração de agentes de IA
- Ollama para processamento de linguagem natural
- Pydantic para validação de dados
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
import logging
from datetime import datetime
import uvicorn
import asyncio

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GatekeeperAgent")

# Configuração do FastAPI
app = FastAPI(
    title="Gatekeeper Agent - Sistema de Logística Inteligente",
    description="Controlador central de acesso e roteamento para agentes especializados",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums para validação
class UserRole(str, Enum):
    """Roles válidos no sistema"""
    ADMIN = "admin"
    LOGISTICS = "logistics"
    FINANCE = "finance"
    OPERATOR = "operator"

class AgentStatus(str, Enum):
    """Status de resposta dos agentes"""
    SUCCESS = "success"
    ERROR = "error"
    FORBIDDEN = "forbidden"

# Modelos Pydantic para validação
class AuthPayload(BaseModel):
    """Payload recebido da API de autenticação externa"""
    userId: str = Field(..., min_length=1, description="ID único do usuário")
    role: UserRole = Field(..., description="Role/papel do usuário no sistema")
    permissions: Optional[List[str]] = Field(
        default=[],
        description="Lista de permissões específicas do usuário"
    )
    sessionId: Optional[str] = Field(None, description="ID da sessão")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

    @validator('userId')
    def validate_user_id(cls, v):
        if not v or v.isspace():
            raise ValueError('userId não pode ser vazio')
        return v.strip()

class GatekeeperResponse(BaseModel):
    """Resposta padrão do Gatekeeper"""
    status: AgentStatus
    agent: Optional[str] = None
    message: str
    userId: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Resposta de erro padronizada"""
    status: str = "error"
    code: int
    message: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

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

class GatekeeperService:
    """Serviço principal do Gatekeeper Agent"""
    
    def __init__(self):
        self.active_sessions = {}
        logger.info("GatekeeperService inicializado")
    
    def validate_role(self, role: UserRole) -> bool:
        """Valida se o role é suportado pelo sistema"""
        return role in ROLE_AGENT_MAP
    
    def get_agent_for_role(self, role: UserRole) -> str:
        """Retorna o agente correspondente ao role"""
        return ROLE_AGENT_MAP.get(role)
    
    def validate_permissions(self, role: UserRole, requested_permissions: List[str]) -> bool:
        """Valida se as permissões solicitadas são compatíveis com o role"""
        if role == UserRole.ADMIN:
            return True  # Admin tem acesso total
        
        allowed_permissions = ROLE_PERMISSIONS.get(role, [])
        
        # Verifica se todas as permissões solicitadas estão permitidas
        for permission in requested_permissions:
            if permission not in allowed_permissions:
                return False
        
        return True
    
    async def route_to_agent(self, payload: AuthPayload) -> Dict[str, Any]:
        """
        Roteia a requisição para o agente apropriado usando CrewAI
        """
        from agents import route_to_specialized_agent
        
        agent_name = self.get_agent_for_role(payload.role)
        
        logger.info(f"Roteando usuário {payload.userId} para {agent_name}")
        
        # Preparar contexto do usuário
        user_context = {
            "userId": payload.userId,
            "role": payload.role.value,
            "permissions": payload.permissions,
            "sessionId": payload.sessionId,
            "timestamp": payload.timestamp.isoformat() if payload.timestamp else datetime.now().isoformat()
        }
        
        # Preparar dados da requisição inicial
        request_data = {
            "type": "authentication_success",
            "message": f"Usuário {payload.userId} autenticado com role {payload.role.value}",
            "timestamp": datetime.now().isoformat(),
            "initial_access": True
        }
        
        try:
            # Rotear para agente especializado usando CrewAI
            agent_response = await route_to_specialized_agent(
                agent_name=agent_name,
                user_context=user_context,
                request_data=request_data
            )
            
            return {
                "agent_response": agent_response,
                "user_context": user_context,
                "routing_success": True
            }
            
        except Exception as e:
            logger.error(f"Erro no roteamento para {agent_name}: {str(e)}")
            return {
                "agent_response": {
                    "status": "error",
                    "message": f"Erro interno no roteamento para {agent_name}",
                    "error": str(e)
                },
                "user_context": user_context,
                "routing_success": False
            }

# Instância do serviço
gatekeeper_service = GatekeeperService()

# Health check
@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Endpoint de verificação de saúde do serviço"""
    return {
        "status": "healthy",
        "service": "Gatekeeper Agent",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Endpoint principal do Gatekeeper
@app.post("/auth-callback", response_model=GatekeeperResponse)
async def auth_callback(payload: AuthPayload):
    """
    Endpoint principal que recebe callbacks da API de autenticação externa
    
    Fluxo:
    1. Valida payload recebido
    2. Verifica se role é válido
    3. Valida permissões
    4. Roteia para agente apropriado
    5. Retorna resposta consolidada
    """
    try:
        logger.info(f"Recebida requisição de autenticação para usuário {payload.userId} com role {payload.role}")
        
        # 1. Validar role
        if not gatekeeper_service.validate_role(payload.role):
            logger.warning(f"Role inválido: {payload.role} para usuário {payload.userId}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{payload.role}' não autorizado no sistema"
            )
        
        # 2. Validar permissões
        if payload.permissions and not gatekeeper_service.validate_permissions(payload.role, payload.permissions):
            logger.warning(f"Permissões inválidas para role {payload.role}: {payload.permissions}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissões solicitadas não compatíveis com o role do usuário"
            )
        
        # 3. Rotear para agente apropriado
        agent_name = gatekeeper_service.get_agent_for_role(payload.role)
        agent_response = await gatekeeper_service.route_to_agent(payload)
        
        # 4. Retornar resposta de sucesso
        response = GatekeeperResponse(
            status=AgentStatus.SUCCESS,
            agent=agent_name,
            message=f"Usuário autenticado e encaminhado para {agent_name}",
            userId=payload.userId,
            data=agent_response
        )
        
        logger.info(f"Requisição processada com sucesso para usuário {payload.userId}")
        return response
        
    except HTTPException:
        # Re-raise HTTPExceptions (já tratadas)
        raise
    except Exception as e:
        logger.error(f"Erro interno no processamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# Endpoint para listar roles disponíveis
@app.get("/roles", response_model=Dict[str, List[str]])
async def list_roles():
    """Lista roles disponíveis e suas permissões"""
    return {
        "available_roles": list(ROLE_AGENT_MAP.keys()),
        "role_permissions": {
            role.value: permissions 
            for role, permissions in ROLE_PERMISSIONS.items()
        }
    }

# Endpoint para informações do sistema
@app.get("/info", response_model=Dict[str, Any])
async def system_info():
    """Informações do sistema Gatekeeper"""
    return {
        "service": "Gatekeeper Agent",
        "version": "1.0.0",
        "description": "Controlador central de acesso e roteamento",
        "supported_roles": list(ROLE_AGENT_MAP.keys()),
        "agent_mapping": {role.value: agent for role, agent in ROLE_AGENT_MAP.items()},
        "endpoints": [
            "/auth-callback - Endpoint principal de autenticação",
            "/health - Verificação de saúde",
            "/roles - Lista de roles disponíveis",
            "/info - Informações do sistema"
        ]
    }

# Handler de exceções personalizado
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler personalizado para HTTPExceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.status_code,
            message=exc.detail,
            details=f"Erro na requisição: {request.url}"
        ).dict()
    )

if __name__ == "__main__":
    # Configuração para execução local
    uvicorn.run(
        "gatekeeper_agent:app",
        host="0.0.0.0",
        port=8001,  # Porta diferente da API principal (8000)
        reload=True,
        log_level="info"
    )