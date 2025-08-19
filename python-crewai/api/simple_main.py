"""
MIT Tracking API Server - Versão Simplificada para Testes
FastAPI simples sem dependências complexas
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Criar aplicação FastAPI
app = FastAPI(
    title="MIT CrewAI API",
    description="Sistema de agentes de IA para logística",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "MIT CrewAI API v2.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MIT CrewAI API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat")
async def chat_endpoint(message: dict):
    """Endpoint simplificado para chat com agentes"""
    return {
        "agent": "MIT Logistics",
        "response": f"Received: {message.get('content', '')}",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)