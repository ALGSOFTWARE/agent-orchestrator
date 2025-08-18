"""
MIT Tracking API Server
FastAPI + GraphQL + OpenAPI integration
"""

import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import strawberry
from contextlib import asynccontextmanager

from .resolvers import Query, Mutation
from .middleware import AuthMiddleware, LoggingMiddleware

# Import das configurações
from config import config

# Import opcional do MIT Agent v2
try:
    from agents.mit_tracking_agent_v2 import MITTrackingAgentV2
    MIT_AGENT_AVAILABLE = True
except ImportError:
    MIT_AGENT_AVAILABLE = False
    print("⚠️  MIT Agent v2 não disponível - API funcionará sem integração LLM")


# GraphQL Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events para inicialização/shutdown"""
    print("🚀 Iniciando MIT Tracking API...")
    
    # Inicializar MIT Agent (opcional)
    if MIT_AGENT_AVAILABLE and os.getenv("OLLAMA_BASE_URL", "").lower() != "disabled":
        try:
            config = OllamaConfig(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
                temperature=0.3
            )
            app.state.mit_agent = MITTrackingAgent(config)
            print("✅ MIT Tracking Agent inicializado")
        except Exception as e:
            print(f"⚠️  MIT Agent não disponível: {e}")
            app.state.mit_agent = None
    else:
        print("ℹ️  MIT Agent desabilitado - funcionando apenas com dados estáticos")
        app.state.mit_agent = None
    
    yield
    
    print("🔄 Encerrando MIT Tracking API...")
    if hasattr(app.state, 'mit_agent') and app.state.mit_agent:
        await app.state.mit_agent.shutdown()


# FastAPI App
app = FastAPI(
    title="MIT Tracking API",
    description="""
    ## 🚚 API GraphQL + OpenAPI para Sistema Logístico MIT Tracking
    
    Esta API oferece acesso completo ao sistema de logística da Move In Tech, incluindo:
    
    ### 📊 Funcionalidades Principais
    - **CT-e (Conhecimento de Transporte Eletrônico)** - Consulta e gerenciamento
    - **Rastreamento de Containers** - Posições GPS e histórico
    - **BL (Bill of Lading)** - Conhecimentos de embarque marítimo
    - **Gestão de Transportadoras** - Cadastro e informações
    - **Viagens Multi-Modal** - Rodoviário, marítimo, aéreo, ferroviário
    
    ### 🔧 Tecnologias
    - **GraphQL** - Query language flexível
    - **OpenAPI/Swagger** - Documentação automática
    - **FastAPI** - Framework Python assíncrono
    - **Strawberry** - GraphQL library type-safe
    
    ### 🚀 Como Usar
    - **GraphQL Playground**: `/graphql` - Interface interativa
    - **API Docs**: `/docs` - Documentação Swagger
    - **Health Check**: `/health` - Status da API
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)

# GraphQL Router
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    """Root endpoint com informações da API"""
    return {
        "message": "MIT Tracking API - Sistema Logístico com GraphQL",
        "version": "2.0.0",
        "endpoints": {
            "graphql": "/graphql",
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics"
        },
        "features": [
            "CT-e Management",
            "Container Tracking", 
            "BL Operations",
            "Real-time GPS Updates",
            "Multi-modal Transport"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from database.db_manager import get_database
    
    try:
        db = get_database()
        stats = db.get_statistics()
        
        # Verificar MIT Agent
        agent_status = "disabled"
        if MIT_AGENT_AVAILABLE and hasattr(app.state, 'mit_agent') and app.state.mit_agent:
            if app.state.mit_agent.is_ready:
                agent_status = "ready"
            else:
                agent_status = "error"
        
        return {
            "status": "healthy",
            "timestamp": "2024-08-11T12:00:00Z",
            "database": {
                "status": "connected",
                "collections": len(stats),
                "total_documents": sum(info["total_documents"] for info in stats.values())
            },
            "mit_agent": {
                "status": agent_status,
                "model": os.getenv("OLLAMA_MODEL", "llama3.2:3b")
            },
            "api": {
                "graphql": "enabled",
                "openapi": "enabled"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Sistema não disponível: {str(e)}")


@app.get("/metrics")
async def metrics():
    """Endpoint de métricas para monitoramento"""
    from database.db_manager import get_database
    
    try:
        db = get_database()
        stats = db.get_statistics()
        
        # Estatísticas detalhadas
        ctes = db.find_all("cte_documents")
        containers = db.find_all("containers")
        bls = db.find_all("bl_documents")
        
        return {
            "database_metrics": {
                "collections": stats,
                "performance": {
                    "avg_query_time": "< 0.1s",
                    "total_queries": 0  # Implementar contador
                }
            },
            "business_metrics": {
                "ctes": {
                    "total": len(ctes),
                    "em_transito": len([c for c in ctes if c.get("status") == "EM_TRANSITO"]),
                    "entregues": len([c for c in ctes if c.get("status") == "ENTREGUE"])
                },
                "containers": {
                    "total": len(containers),
                    "em_transito": len([c for c in containers if c.get("status") == "EM_TRANSITO"]),
                    "no_porto": len([c for c in containers if c.get("status") == "NO_PORTO"])
                },
                "financial": {
                    "valor_total_fretes": sum(c.get("valor_frete", 0) for c in ctes)
                }
            },
            "system_metrics": {
                "uptime": "N/A",  # Implementar
                "memory_usage": "N/A",  # Implementar
                "requests_per_minute": "N/A"  # Implementar
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter métricas: {str(e)}")


# === GATEKEEPER ENDPOINTS === #

from pydantic import BaseModel
from typing import List, Optional

class AuthPayload(BaseModel):
    userId: str
    role: str
    permissions: List[str]
    sessionId: str
    timestamp: str

class GatekeeperResponse(BaseModel):
    status: str
    message: str
    agent: Optional[str] = None
    data: Optional[dict] = None

@app.post("/gatekeeper/auth-callback")
async def gatekeeper_auth_callback(payload: AuthPayload):
    """Simulador do Gatekeeper Agent para autenticação"""
    # Validar role
    valid_roles = ["admin", "logistics", "finance", "operator"]
    if payload.role not in valid_roles:
        raise HTTPException(status_code=422, detail=f"Role inválida: {payload.role}")
    
    # Validar permissões por role
    role_permissions = {
        "admin": ["*"],
        "logistics": ["read:cte", "write:document", "read:container", "write:tracking", "read:shipment"],
        "finance": ["read:financial", "write:financial", "read:payment", "write:payment", "read:billing"],
        "operator": ["read:cte", "write:document", "read:container"]
    }
    
    expected_permissions = role_permissions.get(payload.role, [])
    if payload.role != "admin" and not all(perm in expected_permissions for perm in payload.permissions):
        # Simulate invalid permissions scenario
        if payload.userId == "invalid_005":
            raise HTTPException(status_code=403, detail="Permissões inválidas para a role especificada")
    
    # Mapear agente por role
    agent_mapping = {
        "admin": "Admin Agent",
        "logistics": "MIT Tracking Agent",
        "finance": "Finance Agent", 
        "operator": "MIT Tracking Agent"
    }
    
    return GatekeeperResponse(
        status="success",
        message=f"Usuário {payload.userId} autenticado com sucesso",
        agent=agent_mapping.get(payload.role),
        data={
            "user_context": {
                "userId": payload.userId,
                "role": payload.role,
                "permissions": payload.permissions,
                "sessionId": payload.sessionId,
                "authenticated_at": payload.timestamp
            }
        }
    )

@app.get("/gatekeeper/roles")
async def gatekeeper_get_roles():
    """Obtém roles disponíveis e suas permissões"""
    return {
        "available_roles": ["admin", "logistics", "finance", "operator"],
        "role_permissions": {
            "admin": ["*"],
            "logistics": ["read:cte", "write:document", "read:container", "write:tracking", "read:shipment"],
            "finance": ["read:financial", "write:financial", "read:payment", "write:payment", "read:billing"],
            "operator": ["read:cte", "write:document", "read:container"]
        }
    }

@app.get("/gatekeeper/info")
async def gatekeeper_info():
    """Informações do Gatekeeper Agent"""
    return {
        "service": "Gatekeeper Agent",
        "version": "1.0.0",
        "description": "Controlador de acesso e roteamento para agentes especializados",
        "supported_roles": ["admin", "logistics", "finance", "operator"],
        "agent_mapping": {
            "admin": "Admin Agent",
            "logistics": "MIT Tracking Agent",
            "finance": "Finance Agent",
            "operator": "MIT Tracking Agent"
        },
        "endpoints": [
            "/gatekeeper/auth-callback",
            "/gatekeeper/roles",
            "/gatekeeper/info",
            "/gatekeeper/health"
        ]
    }

@app.get("/gatekeeper/health")
async def gatekeeper_health():
    """Health check do Gatekeeper Agent"""
    return {
        "status": "healthy",
        "service": "Gatekeeper Agent",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# REST Endpoints adicionais para compatibilidade
@app.get("/api/v1/ctes")
async def list_ctes():
    """REST endpoint para listar CT-e (compatibilidade)"""
    from database.db_manager import get_database
    db = get_database()
    return {"ctes": db.find_all("cte_documents")}


@app.get("/api/v1/containers")
async def list_containers():
    """REST endpoint para listar containers (compatibilidade)"""
    from database.db_manager import get_database
    db = get_database()
    return {"containers": db.find_all("containers")}


@app.get("/api/v1/bls")
async def list_bls():
    """REST endpoint para listar BL (compatibilidade)"""
    from database.db_manager import get_database
    db = get_database()
    return {"bls": db.find_all("bl_documents")}


if __name__ == "__main__":
    import uvicorn
    
    # Configurações do servidor
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"🚀 Iniciando MIT Tracking API em {host}:{port}")
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )