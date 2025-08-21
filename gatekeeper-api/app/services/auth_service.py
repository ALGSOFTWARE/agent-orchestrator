"""
Authentication Service - Gatekeeper API

Serviço responsável pela lógica de autenticação e autorização:
- Validação de roles e permissões
- Criação/atualização de usuários
- Integração com Identity Providers
- Gerenciamento de sessões
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models import User, Client, AuthPayload, UserRole
from ..database import DatabaseService

logger = logging.getLogger("GatekeeperAPI.AuthService")


class AuthService:
    """Serviço de autenticação e autorização"""
    
    def __init__(self):
        self.active_sessions = {}
        logger.info("🔐 AuthService inicializado")
    
    def validate_role(self, role: UserRole) -> bool:
        """Valida se o role é suportado pelo sistema"""
        return role in UserRole
    
    def validate_permissions(self, role: UserRole, requested_permissions: List[str]) -> bool:
        """
        Valida se as permissões solicitadas são compatíveis com o role
        
        Args:
            role: Role do usuário
            requested_permissions: Lista de permissões solicitadas
            
        Returns:
            True se todas as permissões são válidas para o role
        """
        # Permissões por role (importado das rotas para centralizar)
        role_permissions = {
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
        
        if role == UserRole.ADMIN:
            return True  # Admin tem acesso total
        
        allowed_permissions = role_permissions.get(role, [])
        
        # Verifica se todas as permissões solicitadas estão permitidas
        for permission in requested_permissions:
            if permission not in allowed_permissions:
                logger.warning(f"❌ Permissão '{permission}' não permitida para role '{role.value}'")
                return False
        
        return True
    
    async def create_or_update_user(self, auth_payload: AuthPayload) -> Optional[User]:
        """
        Cria ou atualiza usuário baseado no payload de autenticação
        
        Args:
            auth_payload: Dados de autenticação recebidos
            
        Returns:
            Usuário criado/atualizado ou None em caso de erro
        """
        try:
            # Buscar usuário existente por ID (usando userId como email para simplicidade)
            existing_user = await DatabaseService.get_user_by_email(auth_payload.userId)
            
            if existing_user:
                # Atualizar usuário existente
                existing_user.last_login = datetime.utcnow()
                existing_user.login_count += 1
                
                # Atualizar role se mudou
                if existing_user.role != auth_payload.role:
                    logger.info(f"🔄 Atualizando role do usuário {auth_payload.userId}: {existing_user.role} → {auth_payload.role}")
                    existing_user.role = auth_payload.role
                
                await existing_user.save()
                logger.info(f"✅ Usuário existente atualizado: {auth_payload.userId}")
                return existing_user
            else:
                # Criar novo usuário
                new_user = User(
                    name=auth_payload.userId,  # Por simplicidade, usando userId como nome
                    email=auth_payload.userId,  # Assumindo userId como email
                    role=auth_payload.role,
                    login_count=1,
                    last_login=datetime.utcnow()
                )
                
                await new_user.save()
                logger.info(f"✅ Novo usuário criado: {auth_payload.userId} com role {auth_payload.role}")
                return new_user
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar/atualizar usuário {auth_payload.userId}: {str(e)}")
            return None
    
    def create_session(self, user_id: str, session_id: str, role: UserRole) -> Dict[str, Any]:
        """
        Cria uma nova sessão para o usuário
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            role: Role do usuário
            
        Returns:
            Dados da sessão criada
        """
        session_data = {
            "user_id": user_id,
            "role": role.value,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "is_active": True
        }
        
        self.active_sessions[session_id] = session_data
        logger.info(f"🆔 Sessão criada para usuário {user_id}: {session_id}")
        
        return session_data
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Valida se uma sessão existe e está ativa
        
        Args:
            session_id: ID da sessão a validar
            
        Returns:
            Dados da sessão se válida, None caso contrário
        """
        session = self.active_sessions.get(session_id)
        
        if session and session.get("is_active"):
            # Atualizar última atividade
            session["last_activity"] = datetime.now().isoformat()
            return session
        
        return None
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalida uma sessão
        
        Args:
            session_id: ID da sessão a invalidar
            
        Returns:
            True se sessão foi invalidada, False se não existia
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["is_active"] = False
            logger.info(f"🚫 Sessão invalidada: {session_id}")
            return True
        
        return False
    
    def get_user_permissions(self, role: UserRole) -> List[str]:
        """
        Retorna as permissões padrão para um role
        
        Args:
            role: Role do usuário
            
        Returns:
            Lista de permissões do role
        """
        role_permissions = {
            UserRole.ADMIN: ["*"],
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
        
        return role_permissions.get(role, [])
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Retorna estatísticas do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Estatísticas do usuário
        """
        try:
            # Buscar usuário
            user = await DatabaseService.get_user_by_email(user_id)
            if not user:
                return {"error": "Usuário não encontrado"}
            
            # Buscar contexto/histórico
            contexts = await DatabaseService.get_user_context(user_id, limit=100)
            
            # Calcular estatísticas
            total_interactions = len(contexts)
            agents_used = set()
            
            for context in contexts:
                agents_used.update(context.agents_involved)
            
            return {
                "user_id": user_id,
                "name": user.name,
                "role": user.role,
                "login_count": user.login_count,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "total_interactions": total_interactions,
                "agents_used": list(agents_used),
                "account_created": user.created_at.isoformat(),
                "is_active": user.is_active
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do usuário {user_id}: {str(e)}")
            return {"error": str(e)}
    
    def get_active_sessions_count(self) -> int:
        """Retorna número de sessões ativas"""
        active_count = sum(1 for session in self.active_sessions.values() if session.get("is_active"))
        return active_count
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """
        Remove sessões inativas mais antigas que o limite especificado
        
        Args:
            max_age_hours: Idade máxima em horas para manter sessões
            
        Returns:
            Número de sessões removidas
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        sessions_to_remove = []
        for session_id, session_data in self.active_sessions.items():
            try:
                last_activity = datetime.fromisoformat(session_data["last_activity"])
                if last_activity < cutoff_time:
                    sessions_to_remove.append(session_id)
            except:
                # Se não conseguir parsear a data, remove a sessão
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]
            removed_count += 1
        
        if removed_count > 0:
            logger.info(f"🧹 Removidas {removed_count} sessões inativas")
        
        return removed_count