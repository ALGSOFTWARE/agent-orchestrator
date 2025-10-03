"""
Authentication Middleware - Gatekeeper API

Middleware para autenticação JWT e identificação de usuários
"""

import jwt
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os

from ..models import UserRole
from ..database import DatabaseService

logger = logging.getLogger("GatekeeperAPI.AuthMiddleware")

# Configurações JWT
JWT_SECRET = os.getenv("JWT_SECRET", "gatekeeper-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Instância do bearer token handler
security = HTTPBearer()


class AuthMiddleware:
    """Middleware de autenticação JWT"""
    
    @staticmethod
    def create_access_token(user_data: Dict[str, Any]) -> str:
        """
        Cria um token JWT para o usuário
        
        Args:
            user_data: Dados do usuário (id, email, role, etc.)
            
        Returns:
            Token JWT assinado
        """
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        
        payload = {
            "user_id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "role": user_data["role"],
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "gatekeeper-api"
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        logger.info(f"🔑 Token criado para usuário {user_data['id']} ({user_data['role']})")
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verifica e decodifica um token JWT
        
        Args:
            token: Token JWT a ser verificado
            
        Returns:
            Payload decodificado do token
            
        Raises:
            HTTPException: Se token inválido ou expirado
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Verificar se o token ainda é válido
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    
    @staticmethod
    async def get_current_user(credentials: HTTPAuthorizationCredentials = None) -> Dict[str, Any]:
        """
        Extrai e valida o usuário atual do token JWT
        
        Args:
            credentials: Credenciais HTTP Bearer
            
        Returns:
            Dados do usuário autenticado
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticação requerido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar token
        payload = AuthMiddleware.verify_token(credentials.credentials)
        
        # Buscar usuário no banco para verificar se ainda está ativo
        user = await DatabaseService.get_user_by_email(payload["email"])
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo ou não encontrado"
            )
        
        # Retornar dados do usuário
        return {
            "id": payload["user_id"],
            "email": payload["email"],
            "name": payload["name"],
            "role": payload["role"],
            "user": user  # Objeto completo do usuário
        }


# Dependência para obter usuário autenticado
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependência FastAPI para obter usuário autenticado
    """
    return await AuthMiddleware.get_current_user(credentials)


# Dependência para verificar se usuário é admin
async def get_current_admin_user(current_user: Dict[str, Any] = None):
    """
    Dependência FastAPI para verificar se usuário é administrador
    """
    if not current_user:
        credentials = security
        current_user = await get_current_user(credentials)
    
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    return current_user


# Dependência para usuário autenticado (opcional)
async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """
    Dependência FastAPI para obter usuário autenticado (opcional)
    Útil para endpoints que funcionam com ou sem autenticação
    """
    try:
        # Tentar extrair token do header Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = AuthMiddleware.verify_token(token)
        
        # Buscar usuário no banco
        user = await DatabaseService.get_user_by_email(payload["email"])
        if not user or not user.is_active:
            return None
        
        return {
            "id": payload["user_id"],
            "email": payload["email"],
            "name": payload["name"],
            "role": payload["role"],
            "user": user
        }
        
    except Exception as e:
        logger.warning(f"Falha na autenticação opcional: {str(e)}")
        return None


def create_demo_admin_token() -> str:
    """
    Cria um token demo para o usuário administrador
    Útil para desenvolvimento e testes
    """
    demo_admin = {
        "id": "admin-demo",
        "email": "admin@logistica.com.br",
        "name": "Administrador Sistema",
        "role": "admin"
    }
    
    return AuthMiddleware.create_access_token(demo_admin)


# Função utilitária para extrair contexto do usuário
def extract_user_context(current_user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrai contexto completo do usuário para envio aos agentes
    
    Args:
        current_user: Dados do usuário autenticado
        
    Returns:
        Contexto formatado para os agentes
    """
    return {
        "userId": current_user["id"],
        "userName": current_user["name"],
        "userEmail": current_user["email"],
        "role": current_user["role"],
        "timestamp": datetime.now().isoformat(),
        "permissions": _get_permissions_for_role(current_user["role"])
    }


def _get_permissions_for_role(role: str) -> list:
    """
    Retorna permissões baseadas no role do usuário
    """
    permissions_map = {
        "admin": ["*"],
        "logistics": ["read:cte", "write:document", "read:container", "write:tracking"],
        "finance": ["read:financial", "write:financial", "read:payment"],
        "operator": ["read:cte", "write:document", "read:container"]
    }
    
    return permissions_map.get(role, [])