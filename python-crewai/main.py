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
import httpx
import asyncio
from llm_router import generate_llm_response, TaskType, LLMProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Frontend Logistics Agent API",
    description="API for Chat Inteligente integration",
    version="1.0.0"
)

# Configuration
GATEKEEPER_API_URL = "http://localhost:8001/api/frontend"

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
        
        # Enhanced message processing with document search
        response_message, attachments = await process_message(message, user_context)
        
        response = ChatResponse(
            message=response_message,
            attachments=attachments,
            agent=request.agent_name,
            status="success",
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Response generated for: {request.agent_name}")
        return response.model_dump()
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def search_documents(query: str, semantic_search: bool = True) -> List[Dict[str, Any]]:
    """Search for documents using the Gatekeeper API with fallback"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First try semantic search
            params = {
                "search": query,
                "semantic_search": semantic_search,
                "limit": 5  # Limit to top 5 results for chat
            }
            
            response = await client.get(f"{GATEKEEPER_API_URL}/documents", params=params)
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get("data", [])
                
                # If no results with semantic search, try traditional search
                if not documents and semantic_search:
                    logger.info(f"🔄 No semantic results for '{query}', trying traditional search...")
                    params["semantic_search"] = False
                    response = await client.get(f"{GATEKEEPER_API_URL}/documents", params=params)
                    if response.status_code == 200:
                        data = response.json()
                        documents = data.get("data", [])
                
                search_method = "semantic" if semantic_search and documents else "traditional"
                logger.info(f"🔍 Found {len(documents)} documents for query: '{query}' (method: {search_method})")
                return documents
            else:
                logger.warning(f"⚠️ Document search failed: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"❌ Error searching documents: {str(e)}")
        return []

async def format_document_attachments(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format documents as chat attachments"""
    attachments = []
    
    for doc in documents:
        # Handle different field names that might come from the API
        doc_id = doc.get("id") or doc.get("_id", "")
        file_name = doc.get("number") or doc.get("file_name", "Documento")
        file_size = doc.get("size", "0")
        upload_date = doc.get("date") or doc.get("upload_date", "")
        doc_type = doc.get("type", "DOCUMENT")
        
        # Extract file extension for type if available
        if "." in file_name:
            ext = file_name.split(".")[-1].upper()
            if ext in ["PDF", "PNG", "JPG", "JPEG", "DOC", "DOCX", "XLS", "XLSX"]:
                doc_type = ext
        
        attachment = {
            "type": doc_type,
            "name": file_name,
            "id": doc_id,
            "size": file_size,
            "upload_date": upload_date,
            "url": f"{GATEKEEPER_API_URL}/documents/{doc_id}/view" if doc_id else "#",
            "client": doc.get("client", ""),
            "origin": doc.get("origin", ""),
            "destination": doc.get("destination", ""),
            "status": doc.get("status", "")
        }
        attachments.append(attachment)
    
    return attachments

async def generate_ai_response(message: str, user_context: Dict[str, Any], documents: List[Dict[str, Any]] = None) -> str:
    """Generate intelligent response using LLM Router"""
    try:
        # Build context-aware prompt
        user_name = user_context.get("name", "usuário")
        user_role = user_context.get("role", "operador")
        
        # Create system prompt for logistics assistant
        system_prompt = f"""Você é um assistente inteligente de logística especializado em ajudar {user_role}s.

Contexto do usuário:
- Nome: {user_name}  
- Função: {user_role}

Instruções:
1. Seja profissional, mas amigável
2. Foque em soluções práticas para logística
3. Use informações dos documentos quando disponíveis
4. Seja claro e direto
5. Ofereça próximos passos quando apropriado

"""

        # Add document context if available
        if documents:
            doc_info = []
            for doc in documents[:3]:  # Limit to 3 docs for context
                info = f"- {doc.get('number', 'Doc')}: {doc.get('client', '')} ({doc.get('status', 'N/A')})"
                doc_info.append(info)
            
            system_prompt += f"""
Documentos encontrados relacionados:
{chr(10).join(doc_info)}

Use essas informações para fornecer uma resposta mais específica e útil.
"""

        full_prompt = system_prompt + f"\nPergunta do usuário: {message}\n\nResposta:"

        # Generate response using LLM Router
        llm_response = await generate_llm_response(
            prompt=full_prompt,
            task_type=TaskType.LOGISTICS,
            temperature=0.7,  # Slightly creative but focused
            max_tokens=500,   # Reasonable length for chat
            user_context=user_context
        )

        logger.info(f"🧠 LLM Response generated using {llm_response.provider} ({llm_response.model_used})")
        return llm_response.content
        
    except Exception as e:
        logger.error(f"❌ LLM generation failed: {str(e)}")
        # Fallback to simple response
        return f"Desculpe {user_context.get('name', 'usuário')}, estou processando sua solicitação. Como posso ajudá-lo com documentos ou rastreamento de cargas?"

async def process_message(message: str, user_context: Dict[str, Any]) -> tuple[str, List[Dict[str, Any]]]:
    """Enhanced message processing with LLM and real document search"""
    
    # Extract user info
    user_name = user_context.get("name", "usuário")
    message_lower = message.lower()
    attachments = []
    
    # Always try to extract search terms for potential document queries
    search_terms = extract_search_terms(message)
    documents = []
    
    # Search for documents if we have relevant terms
    if search_terms and any(word in message_lower for word in ["documento", "cte", "nfe", "bl", "manifesto", "pdf", "status", "carga", "entrega", "rastrear"]):
        documents = await search_documents(search_terms, semantic_search=True)
        attachments = await format_document_attachments(documents)
        logger.info(f"🔍 Document search for '{search_terms}': found {len(documents)} documents")
    
    # Generate intelligent response using LLM with document context
    try:
        response_message = await generate_ai_response(message, user_context, documents)
        
        # If we found documents, add a note about them
        if documents:
            doc_count = len(documents)
            if doc_count > 0:
                response_message += f"\n\n📎 Encontrei {doc_count} documento(s) relacionado(s) que estão anexados abaixo."
    
    except Exception as e:
        logger.error(f"❌ AI response generation failed, using fallback: {str(e)}")
        
        # Fallback to rule-based responses
        if any(word in message_lower for word in ["documento", "cte", "nfe", "bl", "manifesto", "pdf"]):
            if documents:
                response_message = f"Encontrei {len(documents)} documento(s) relacionado(s) à sua busca. Os documentos estão anexados abaixo."
            else:
                response_message = f"Olá {user_name}! Não encontrei documentos específicos, mas posso ajudá-lo com outros tipos de consulta."
        
        elif any(word in message_lower for word in ["status", "carga", "entrega", "rastrear"]):
            if documents:
                response_message = f"Encontrei documentos relacionados ao seu rastreamento. Verifique os anexos para mais informações."
            else:
                response_message = f"Para rastreamento, por favor informe números específicos de embarque ou CT-e."
        
        elif any(word in message_lower for word in ["ajuda", "help", "como"]):
            response_message = f"Posso te ajudar com:\n\n• 📄 Consulta de documentos\n• 📦 Rastreamento de cargas\n• 📍 Status de entregas\n\nComo posso ajudá-lo?"
        
        else:
            if documents:
                response_message = f"Encontrei {len(documents)} documento(s) que podem ser relevantes. Verifique os anexos."
            else:
                response_message = f"Olá {user_name}! Como posso ajudá-lo com consultas logísticas?"
    
    return response_message, attachments

def extract_search_terms(message: str) -> str:
    """Extract potential search terms from message"""
    # Look for patterns like numbers, codes, etc.
    import re
    
    # Look for alphanumeric codes that might be tracking numbers
    patterns = [
        r'\b[A-Z]{2,}\d{3,}\b',  # Like ABC123, CTE456
        r'\b\d{4,}\b',  # 4+ digit numbers
        r'\b[A-Z]+\-\d+\b',  # Like CTE-123, EMB-456
        r'\b\d+\-[A-Z]+\-\d+\b',  # Like 123-ABC-456
    ]
    
    message_upper = message.upper()
    for pattern in patterns:
        matches = re.findall(pattern, message_upper)
        if matches:
            return matches[0]  # Return first match
    
    # Look for specific document types and key terms
    key_terms = ['MDF', 'CTE', 'CT-E', 'NFE', 'NF-E', 'BL', 'MANIFESTO', 'PDF', 'EMBARQUE', 'CONTAINER']
    for term in key_terms:
        if term in message_upper:
            return term
    
    # If no specific patterns, extract meaningful words (excluding common stop words)
    stop_words = ['preciso', 'quero', 'buscar', 'encontrar', 'ver', 'visualizar', 'consultar', 'documento', 'documentos',
                  'para', 'pelo', 'pela', 'com', 'sobre', 'que', 'uma', 'uns', 'das', 'dos', 'de', 'da', 'do']
    
    words = message.split()
    meaningful_words = [w for w in words if len(w) > 2 and w.lower() not in stop_words]
    
    if meaningful_words:
        return ' '.join(meaningful_words[:2])  # Max 2 words
    
    return message.strip()

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