"""
Simple FastAPI server for Frontend Logistics Agent
Serves as interface for the chat integration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Frontend Logistics Agent API",
    description="API for Chat Inteligente integration",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    agent_name: str
    user_context: Dict[str, Any]
    request_data: Dict[str, Any]

class ChatResponse(BaseModel):
    message: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    attachments: List[Dict[str, Any]] = []
    agent: str
    status: str = "success"
    timestamp: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "frontend_logistics_agent",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/agents/route")
async def route_message(request: ChatRequest):
    """Route message to frontend logistics agent"""
    try:
        logger.info(f"🚀 Processing message for agent: {request.agent_name}")
        
        # Extract message from request
        message = request.request_data.get("message", "")
        user_context = request.user_context
        
        # Simple message processing (we'll enhance this later)
        response_message = process_message(message, user_context)
        
        response = ChatResponse(
            message=response_message,
            agent=request.agent_name,
            status="success",
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Response generated for: {request.agent_name}")
        return response.dict()
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def process_message(message: str, user_context: Dict[str, Any]) -> str:
    """Simple message processing - will be enhanced with real AI agent"""
    
    # Extract user info
    user_name = user_context.get("name", "usuário")
    
    # Simple keyword-based responses
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["documento", "cte", "nfe", "bl"]):
        return f"Olá {user_name}! Entendi que você está procurando documentos. Posso ajudá-lo a buscar CT-e, NF-e, BL ou outros documentos logísticos. Qual documento específico você precisa?"
    
    elif any(word in message_lower for word in ["status", "carga", "entrega", "rastrear"]):
        return f"Certo {user_name}! Vou verificar o status da sua carga. Por favor, me informe o número do embarque ou código de rastreamento."
    
    elif any(word in message_lower for word in ["ajuda", "help", "como"]):
        return f"Claro {user_name}! Posso te ajudar com:\n\n• 📄 Consulta de documentos (CT-e, NF-e, BL)\n• 📦 Rastreamento de cargas\n• 📍 Status de entregas\n• 🔍 Busca por embarques\n\nO que você gostaria de fazer?"
    
    else:
        return f"Olá {user_name}! Recebi sua mensagem: \"{message}\"\n\nSou o assistente inteligente de logística. Posso te ajudar com consultas de documentos, rastreamento de cargas e muito mais. Como posso ajudá-lo?"

@app.get("/agents/list")
async def list_agents():
    """List available agents"""
    return {
        "available_agents": [
            "frontend_logistics_agent",
            "AdminAgent", 
            "LogisticsAgent",
            "FinanceAgent"
        ]
    }

@app.get("/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get agent status"""
    return {
        "agent": agent_name,
        "status": "active",
        "version": "1.0.0",
        "capabilities": [
            "document_search",
            "shipment_tracking", 
            "delivery_status",
            "user_assistance"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)