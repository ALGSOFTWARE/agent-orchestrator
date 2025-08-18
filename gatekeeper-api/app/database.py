"""
Database Configuration - Gatekeeper API

Configuração e inicialização do MongoDB usando Beanie ODM.
Gerencia conexão, inicialização de modelos e configurações de banco.
"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional, List

from .models import User, Client, Context, Container, Shipment, TrackingEvent

logger = logging.getLogger("GatekeeperAPI.Database")

# Configurações do banco
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mit_logistics")

# Cliente MongoDB global
client: Optional[AsyncIOMotorClient] = None


async def init_database():
    """
    Inicializa a conexão com MongoDB e configura os modelos Beanie
    """
    global client
    
    try:
        logger.info(f"🔌 Conectando ao MongoDB: {MONGODB_URL}")
        
        # Criar cliente MongoDB
        client = AsyncIOMotorClient(MONGODB_URL)
        
        # Testar conexão
        await client.admin.command('ping')
        logger.info("✅ Conexão com MongoDB estabelecida")
        
        # Obter database
        database = client[DATABASE_NAME]
        
        # Inicializar Beanie com os modelos
        await init_beanie(
            database=database,
            document_models=[
                User,
                Client, 
                Context,
                Container,
                Shipment,
                TrackingEvent
            ]
        )
        
        logger.info("✅ Modelos Beanie inicializados")
        
        # Criar índices adicionais se necessário
        await create_indexes()
        
        logger.info("✅ Database totalmente configurado")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar database: {str(e)}")
        raise


async def create_indexes():
    """
    Cria índices adicionais no banco de dados para otimização
    """
    try:
        # Índices para User
        await User.create_index("email", unique=True)
        
        # Índices para Context (para consultas por usuário e sessão)
        await Context.create_index([("user_id", 1), ("timestamp", -1)])
        await Context.create_index("session_id")
        
        # Índices para Container
        await Container.create_index("container_number", unique=True)
        
        logger.info("✅ Índices criados com sucesso")
        
    except Exception as e:
        logger.warning(f"⚠️  Erro ao criar índices (podem já existir): {str(e)}")


async def close_database():
    """
    Fecha a conexão com o banco de dados
    """
    global client
    if client:
        client.close()
        logger.info("🔌 Conexão com MongoDB fechada")


async def get_database_info():
    """
    Retorna informações sobre o banco de dados
    """
    global client
    if not client:
        return {"status": "disconnected"}
    
    try:
        # Info do servidor
        server_info = await client.server_info()
        
        # Info do database
        db = client[DATABASE_NAME]
        collections = await db.list_collection_names()
        
        # Estatísticas das collections principais
        stats = {}
        for collection_name in ["users", "clients", "contexts"]:
            if collection_name in collections:
                count = await db[collection_name].count_documents({})
                stats[collection_name] = {"count": count}
        
        return {
            "status": "connected",
            "server_version": server_info.get("version"),
            "database_name": DATABASE_NAME,
            "collections": collections,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter info do database: {str(e)}")
        return {"status": "error", "error": str(e)}


# Utility functions para operações comuns
class DatabaseService:
    """Serviço com operações comuns do banco de dados"""
    
    @staticmethod
    async def health_check() -> bool:
        """Verifica se o banco está funcionando"""
        global client
        try:
            if client:
                await client.admin.command('ping')
                return True
            return False
        except:
            return False
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Busca usuário por email"""
        try:
            return await User.find_one(User.email == email)
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email: {str(e)}")
            return None
    
    @staticmethod
    async def create_user(name: str, email: str, role: str, client_id: Optional[str] = None) -> Optional[User]:
        """Cria novo usuário"""
        try:
            user_data = {
                "name": name,
                "email": email, 
                "role": role
            }
            
            if client_id:
                client_doc = await Client.get(client_id)
                if client_doc:
                    user_data["client"] = client_doc
            
            user = User(**user_data)
            await user.save()
            return user
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            return None
    
    @staticmethod
    async def add_context(user_id: str, input_text: str, output_text: str, 
                         agents: list = None, session_id: str = None, 
                         metadata: dict = None) -> Optional[Context]:
        """Adiciona entrada de contexto"""
        try:
            context = Context(
                user_id=user_id,
                session_id=session_id,
                input=input_text,
                output=output_text,
                agents_involved=agents or [],
                metadata=metadata or {}
            )
            await context.save()
            return context
            
        except Exception as e:
            logger.error(f"Erro ao adicionar contexto: {str(e)}")
            return None
    
    @staticmethod
    async def get_user_context(user_id: str, limit: int = 50) -> List[Context]:
        """Recupera histórico de contexto do usuário"""
        try:
            contexts = await Context.find(
                Context.user_id == user_id
            ).sort(-Context.timestamp).limit(limit).to_list()
            return contexts
            
        except Exception as e:
            logger.error(f"Erro ao recuperar contexto: {str(e)}")
            return []