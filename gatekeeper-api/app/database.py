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

from .models import User, Client, Context, Container, Shipment, TrackingEvent, Order, DocumentFile, CTEDocument, BLDocument
from .models_mittracking import (
    MitUser, Company, Journey, Delivery, LogisticsDocument, Incident, 
    ChatConversation, Driver, Vehicle, Report, UserContext, GlobalContext, ConversationHistory
)

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
                TrackingEvent,
                Order,
                DocumentFile,
                CTEDocument,
                BLDocument,
                # MitTracking models
                MitUser,
                Company,
                Journey,
                Delivery,
                LogisticsDocument,
                Incident,
                ChatConversation,
                Driver,
                Vehicle,
                Report,
                UserContext,
                GlobalContext,
                ConversationHistory
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
        
        # Índices para Order (super-contêiner)
        await Order.create_index("order_id", unique=True)
        await Order.create_index("customer_name")
        await Order.create_index("status")
        await Order.create_index("order_type")
        await Order.create_index("created_at")
        await Order.create_index("last_activity")
        
        # Índices para DocumentFile (busca e relacionamentos)
        await DocumentFile.create_index("file_id", unique=True)
        await DocumentFile.create_index("order_id")
        await DocumentFile.create_index("category")
        await DocumentFile.create_index("processing_status")
        await DocumentFile.create_index("uploaded_at")
        await DocumentFile.create_index("original_name")
        
        # Índice especial para busca semântica (será usado para vector search)
        await DocumentFile.create_index("embedding")
        
        # Índices para CTEDocument
        await CTEDocument.create_index("cte_number", unique=True)
        
        # Índices para BLDocument  
        await BLDocument.create_index("bl_number", unique=True)
        
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
        for collection_name in ["users", "clients", "contexts", "orders", "document_files", "cte_documents", "bl_documents"]:
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
    
    @staticmethod
    async def get_order_by_id(order_id: str) -> Optional["Order"]:
        """Busca order por ID"""
        try:
            from .models import Order
            return await Order.find_one(Order.order_id == order_id)
        except Exception as e:
            logger.error(f"Erro ao buscar order: {str(e)}")
            return None
    
    @staticmethod
    async def get_documents_by_order(order_id: str) -> List["DocumentFile"]:
        """Busca todos os documentos de uma order"""
        try:
            from .models import DocumentFile
            return await DocumentFile.find(DocumentFile.order_id == order_id).to_list()
        except Exception as e:
            logger.error(f"Erro ao buscar documentos da order: {str(e)}")
            return []
    
    @staticmethod
    async def search_documents_by_text(query: str, limit: int = 20) -> List["DocumentFile"]:
        """Busca documentos por texto extraído"""
        try:
            from .models import DocumentFile
            # Busca simples por texto usando regex
            documents = await DocumentFile.find({
                "$or": [
                    {"original_name": {"$regex": query, "$options": "i"}},
                    {"text_content": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}}
                ]
            }).limit(limit).to_list()
            return documents
        except Exception as e:
            logger.error(f"Erro ao buscar documentos: {str(e)}")
            return []
    
    @staticmethod
    async def get_recent_orders(limit: int = 10) -> List["Order"]:
        """Busca orders mais recentes"""
        try:
            from .models import Order
            return await Order.find({}).sort(-Order.last_activity).limit(limit).to_list()
        except Exception as e:
            logger.error(f"Erro ao buscar orders recentes: {str(e)}")
            return []


async def get_mongo_client() -> AsyncIOMotorClient:
    """
    Retorna o cliente MongoDB global para uso em serviços desacoplados
    """
    global client
    if not client:
        await init_database()
    return client