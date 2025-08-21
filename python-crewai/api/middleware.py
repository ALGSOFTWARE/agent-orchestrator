"""
Middlewares para MIT Tracking API
Autenticação, logging e outras funcionalidades transversais
"""

import time
import json
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import os


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisições"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log da requisição
        print(f"📥 {request.method} {request.url.path} - {request.client.host}")
        
        # Processar requisição
        response = await call_next(request)
        
        # Log da resposta
        process_time = time.time() - start_time
        print(f"📤 {response.status_code} - {process_time:.4f}s")
        
        # Adicionar headers de performance
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-API-Version"] = "2.0.0"
        
        return response


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware de autenticação (básico para desenvolvimento)"""
    
    def __init__(self, app):
        super().__init__(app)
        self.security = HTTPBearer(auto_error=False)
        
        # Rotas públicas (sem autenticação)
        self.public_paths = {
            "/",
            "/health",
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/graphql"  # GraphQL público por enquanto
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Verificar se é rota pública
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Verificar se autenticação está habilitada
        auth_enabled = os.getenv("API_AUTH_ENABLED", "false").lower() == "true"
        if not auth_enabled:
            return await call_next(request)
        
        # Verificar token de autorização
        authorization = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=401,
                content={"error": "Token de autorização necessário"}
            )
        
        # Validação básica do token
        api_key = os.getenv("API_KEY", "mit-tracking-dev-key")
        if authorization != f"Bearer {api_key}":
            return JSONResponse(
                status_code=403,
                content={"error": "Token inválido"}
            )
        
        # Continuar processamento
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting (implementação básica)"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests = {}  # Em produção, usar Redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Rate limiting desabilitado em desenvolvimento
        if os.getenv("ENVIRONMENT", "development") == "development":
            return await call_next(request)
        
        client_ip = request.client.host
        current_time = time.time()
        
        # Limpar registros antigos (mais de 1 minuto)
        if client_ip in self.client_requests:
            self.client_requests[client_ip] = [
                req_time for req_time in self.client_requests[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.client_requests[client_ip] = []
        
        # Verificar limite
        if len(self.client_requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit excedido",
                    "limit": self.requests_per_minute,
                    "reset_in_seconds": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Registrar requisição
        self.client_requests[client_ip].append(current_time)
        
        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware para tratamento global de erros"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            # Re-raise HTTP exceptions (já tratadas pelo FastAPI)
            raise
        except Exception as e:
            # Log do erro
            print(f"💥 Erro inesperado: {str(e)}")
            
            # Resposta padronizada de erro
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Erro interno do servidor",
                    "message": str(e) if os.getenv("DEBUG", "false").lower() == "true" else "Entre em contato com o suporte",
                    "timestamp": time.time(),
                    "path": request.url.path
                }
            )