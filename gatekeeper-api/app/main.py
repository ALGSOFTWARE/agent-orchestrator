#!/usr/bin/env python3
"""
Gatekeeper API - Main FastAPI Application

Microserviço de autenticação e roteamento para o Sistema de Logística Inteligente.
Funciona como ponto de entrada central que:
1. Valida autenticação de usuários
2. Gerencia roles e permissões  
3. Roteia requisições para agentes especializados
4. Mantém histórico de contexto das interações
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import uvicorn

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GatekeeperAPI")

# Imports dos módulos internos
from .database import init_database
from .routes import auth, users, context, orders, files, visualizations
from .routes.crud import crud_router
from .models import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    logger.info("🚀 Iniciando Gatekeeper API...")
    
    # Inicializar banco de dados
    await init_database()
    logger.info("✅ Database inicializado")
    
    yield
    
    logger.info("🛑 Finalizando Gatekeeper API...")


# Configuração do FastAPI
app = FastAPI(
    title="Gatekeeper API - Sistema de Logística Inteligente",
    description="Microserviço de autenticação centralizada e roteamento para agentes especializados",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])  
app.include_router(context.router, prefix="/context", tags=["Context"])
app.include_router(crud_router, tags=["CRUD Operations"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(files.router, prefix="/files", tags=["File Upload"])
app.include_router(visualizations.router, tags=["Data Visualizations"])

# Health check
@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde do microserviço"""
    return {
        "status": "healthy",
        "service": "Gatekeeper API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Informações do sistema
@app.get("/info")
async def system_info():
    """Informações gerais do microserviço"""
    return {
        "service": "Gatekeeper API",
        "version": "1.0.0", 
        "description": "Microserviço de autenticação centralizada e roteamento",
        "architecture": "Microservices",
        "endpoints": {
            "/auth": "Rotas de autenticação e autorização",
            "/users": "Gerenciamento de usuários",
            "/context": "Histórico e contexto de interações",
            "/health": "Verificação de saúde",
            "/info": "Informações do sistema"
        },
        "external_services": {
            "crewai_agents": "http://localhost:8000",
            "mongodb": "mongodb://localhost:27017"
        }
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
            details=f"Erro na requisição: {request.url}",
            service="gatekeeper-api"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para exceções gerais"""
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code=500,
            message="Erro interno do servidor",
            details=str(exc),
            service="gatekeeper-api"
        ).dict()
    )

if __name__ == "__main__":
    # Configuração para execução local
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,  # Porta específica para o gatekeeper
        reload=True,
        log_level="info"
    )