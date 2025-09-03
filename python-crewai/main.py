"""
Simple FastAPI server for Frontend Logistics Agent
Serves as interface for the chat integration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import logging
import httpx
import asyncio
from llm_router import generate_llm_response, TaskType, LLMProvider
from agents.logistics_crew import LogisticsCrew
import uuid

# Disable CrewAI telemetry to avoid external service calls
import os
os.environ['OTEL_SDK_DISABLED'] = 'true'
os.environ['CREWAI_TELEMETRY_DISABLED'] = 'true'

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

# In-memory conversation storage (em produção usaria Redis ou DB)
conversation_memory = {}

class ConversationMemory:
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Obter ou criar sessão de conversa"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "id": session_id,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "messages": [],
                "context": {},
                "user_preferences": {},
                "document_history": []
            }
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str, attachments: List = None, metadata: Dict = None):
        """Adicionar mensagem à sessão"""
        session = self.get_session(session_id)
        
        message = {
            "id": str(uuid.uuid4()),
            "role": role,  # user, assistant, system
            "content": content,
            "timestamp": datetime.now(),
            "attachments": attachments or [],
            "metadata": metadata or {}
        }
        
        session["messages"].append(message)
        session["last_activity"] = datetime.now()
        
        # Manter apenas os últimos 20 mensagens para não sobrecarregar
        if len(session["messages"]) > 20:
            session["messages"] = session["messages"][-20:]
    
    def get_conversation_context(self, session_id: str, max_messages: int = 10) -> str:
        """Obter contexto das últimas mensagens"""
        session = self.get_session(session_id)
        recent_messages = session["messages"][-max_messages:]
        
        context_parts = []
        for msg in recent_messages:
            role_display = {"user": "Usuário", "assistant": "Assistente", "system": "Sistema"}.get(msg["role"], msg["role"])
            context_parts.append(f"{role_display}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def update_user_context(self, session_id: str, user_context: Dict[str, Any]):
        """Atualizar contexto do usuário na sessão"""
        session = self.get_session(session_id)
        session["context"].update(user_context)
    
    def add_document_to_history(self, session_id: str, documents: List[Dict[str, Any]]):
        """Adicionar documentos visualizados ao histórico"""
        session = self.get_session(session_id)
        for doc in documents:
            if doc not in session["document_history"]:
                session["document_history"].append({
                    **doc,
                    "accessed_at": datetime.now()
                })
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Limpar sessões antigas"""
        cutoff = datetime.now() - timedelta(hours=hours)
        old_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session["last_activity"] < cutoff
        ]
        
        for session_id in old_sessions:
            del self.sessions[session_id]
        
        logger.info(f"🧹 Limpeza de sessões: {len(old_sessions)} sessões antigas removidas")

# Instância global de memória
memory = ConversationMemory()

# Initialize CrewAI Logistics Crew
try:
    logistics_crew = LogisticsCrew()
    logger.info("🤖 LogisticsCrew initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize LogisticsCrew: {str(e)}")
    logistics_crew = None

class ChatRequest(BaseModel):
    agent_name: str
    user_context: Dict[str, Any]
    request_data: Dict[str, Any]
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    attachments: List[Dict[str, Any]] = []
    agent: str
    status: str = "success"
    timestamp: str
    session_id: Optional[str] = None

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
        session_id = request.session_id
        
        # Generate session_id if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"🔄 Generated new session_id: {session_id}")
        
        # Enhanced message processing with document search and memory
        response_message, attachments = await process_message(message, user_context, session_id)
        
        response = ChatResponse(
            message=response_message,
            attachments=attachments,
            agent=request.agent_name,
            status="success",
            timestamp=datetime.now().isoformat(),
            session_id=session_id
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

async def process_with_crewai(message: str, user_context: Dict[str, Any], session_id: str = None) -> tuple[str, List[Dict[str, Any]]]:
    """Process message using CrewAI agents for intelligent responses"""
    try:
        if not logistics_crew:
            logger.warning("⚠️ LogisticsCrew not available, falling back to basic processing")
            return await basic_message_processing(message, user_context, session_id)
        
        message_lower = message.lower()
        attachments = []
        
        # Determine the type of request and route to appropriate agent method
        if any(keyword in message_lower for keyword in ["find", "search", "show", "list", "mdf", "cte", "bl", "nfe", "documento"]):
            # Document search request
            logger.info("🔍 Routing to document search agent")
            response = await run_crew_async(
                lambda: logistics_crew.search_documents(message, user_context)
            )
            
            # Try to extract document information from response for attachments
            if "documento" in response.lower() and "encontr" in response.lower():
                documents = await search_documents(extract_search_terms(message), semantic_search=True)
                attachments = await format_document_attachments(documents)
        
        elif any(keyword in message_lower for keyword in ["analiz", "insight", "relatório", "análise", "tendência", "padrão"]):
            # Analysis request
            logger.info("📊 Routing to collaborative analysis")
            response = await run_crew_async(
                lambda: logistics_crew.collaborative_analysis(message, user_context)
            )
            
        elif any(keyword in message_lower for keyword in ["compliance", "conform", "regulation", "validat", "aprovação", "legal"]):
            # Compliance request - need document IDs, so search first
            logger.info("🛡️ Routing to compliance check")
            documents = await search_documents(extract_search_terms(message), semantic_search=True)
            document_ids = [doc.get("id", "") for doc in documents if doc.get("id")]
            
            if document_ids:
                response = await run_crew_async(
                    lambda: logistics_crew.check_compliance(document_ids, user_context)
                )
                attachments = await format_document_attachments(documents)
            else:
                response = await run_crew_async(
                    lambda: logistics_crew.handle_general_inquiry(message, user_context)
                )
        
        else:
            # General inquiry
            logger.info("💬 Routing to general inquiry handler")
            response = await run_crew_async(
                lambda: logistics_crew.handle_general_inquiry(message, user_context)
            )
        
        # Save messages to memory
        if session_id:
            memory.add_message(session_id, "user", message)
            memory.add_message(session_id, "assistant", response, attachments)
        
        return response, attachments
        
    except Exception as e:
        logger.error(f"❌ Error in CrewAI processing: {str(e)}")
        # Fallback to basic processing
        return await basic_message_processing(message, user_context, session_id)

async def run_crew_async(crew_function):
    """Run CrewAI function in a separate thread to avoid blocking"""
    import concurrent.futures
    
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, crew_function)
    return result

async def basic_message_processing(message: str, user_context: Dict[str, Any], session_id: str = None) -> tuple[str, List[Dict[str, Any]]]:
    """Basic message processing as fallback when CrewAI is not available"""
    message_lower = message.lower()
    attachments = []
    
    # Basic document search
    search_terms = extract_search_terms(message)
    documents = []
    
    if search_terms and any(word in message_lower for word in ["documento", "cte", "nfe", "bl", "manifesto", "pdf", "status", "carga"]):
        documents = await search_documents(search_terms, semantic_search=True)
        attachments = await format_document_attachments(documents)
    
    # Generate basic AI response
    response = await generate_ai_response(message, user_context, documents, session_id)
    
    if documents and "documento" not in response.lower():
        doc_count = len(documents)
        response += f"\n\n📎 Encontrei {doc_count} documento(s) relacionado(s)."
    
    return response, attachments

async def generate_ai_response(message: str, user_context: Dict[str, Any], documents: List[Dict[str, Any]] = None, session_id: str = None) -> str:
    """Generate intelligent response using LLM Router"""
    try:
        # Build context-aware prompt
        user_name = user_context.get("name", "usuário")
        user_role = user_context.get("role", "operador")
        
        # Obter contexto da conversa se tiver session_id
        conversation_context = ""
        if session_id:
            memory.update_user_context(session_id, user_context)
            conversation_context = memory.get_conversation_context(session_id, max_messages=5)
        
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
6. Use o histórico da conversa para dar respostas mais contextuais

"""

        # Adicionar contexto da conversa se disponível
        if conversation_context:
            system_prompt += f"""
Histórico da conversa recente:
{conversation_context}

Baseie-se neste histórico para dar uma resposta mais contextual e personalizada.
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

async def process_message(message: str, user_context: Dict[str, Any], session_id: str = None) -> tuple[str, List[Dict[str, Any]]]:
    """Enhanced message processing with CrewAI agents"""
    
    logger.info(f"🚀 Processing message with CrewAI: {message[:50]}{'...' if len(message) > 50 else ''}")
    
    # Use CrewAI agents for intelligent processing
    try:
        response_message, attachments = await process_with_crewai(message, user_context, session_id)
        
        logger.info(f"✅ CrewAI processing completed successfully")
        return response_message, attachments
        
    except Exception as e:
        logger.error(f"❌ CrewAI processing failed, falling back to basic processing: {str(e)}")
        # Fallback to basic processing
        return await basic_message_processing(message, user_context, session_id)

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

@app.post("/documents/analyze")
async def analyze_documents(request: Dict[str, Any]):
    """Analyze documents and generate intelligent insights"""
    try:
        user_context = request.get("user_context", {})
        document_filters = request.get("filters", {})
        analysis_type = request.get("analysis_type", "general")  # general, compliance, risk, efficiency
        
        # Buscar documentos para análise
        search_query = document_filters.get("search", "")
        documents = await search_documents(search_query, semantic_search=True)
        
        if not documents:
            return {
                "analysis": {
                    "summary": "Nenhum documento encontrado para análise.",
                    "insights": [],
                    "recommendations": [],
                    "risk_score": 0
                },
                "processed_documents": 0
            }
        
        # Analisar documentos usando IA
        analysis_prompt = f"""Você é um especialista em análise de documentos logísticos. 
        
Analise os seguintes documentos e forneça insights detalhados:

Tipo de análise solicitada: {analysis_type}
Usuário: {user_context.get('name', 'N/A')} ({user_context.get('role', 'N/A')})

Documentos encontrados: {len(documents)}

Informações dos documentos:
"""
        
        # Adicionar informações dos documentos ao prompt
        for i, doc in enumerate(documents[:10]):  # Limitar a 10 documentos
            doc_info = f"""
Documento {i+1}:
- Número/ID: {doc.get('number', doc.get('file_name', 'N/A'))}
- Cliente: {doc.get('client', 'N/A')}
- Status: {doc.get('status', 'N/A')}
- Origem: {doc.get('origin', 'N/A')}
- Destino: {doc.get('destination', 'N/A')}
- Data: {doc.get('date', doc.get('upload_date', 'N/A'))}
"""
            analysis_prompt += doc_info
        
        analysis_prompt += f"""

Com base nestes dados, forneça uma análise estruturada incluindo:

1. RESUMO EXECUTIVO (2-3 linhas)
2. INSIGHTS PRINCIPAIS (3-5 pontos específicos)
3. RECOMENDAÇÕES PRÁTICAS (3-4 ações concretas)
4. SCORE DE RISCO (0-10, onde 10 é alto risco)
5. PRÓXIMOS PASSOS

Seja específico, prático e focado em ações que o {user_context.get('role', 'operador')} pode tomar.
Formato JSON não é necessário - use texto claro e organizado.
"""
        
        # Gerar análise usando LLM
        llm_response = await generate_llm_response(
            prompt=analysis_prompt,
            task_type=TaskType.ANALYSIS,
            temperature=0.3,  # Mais factual
            max_tokens=1500,  # Análise mais detalhada
            user_context=user_context
        )
        
        logger.info(f"📊 Document analysis generated for {len(documents)} documents")
        
        return {
            "analysis": {
                "type": analysis_type,
                "summary": llm_response.content,
                "processed_documents": len(documents),
                "analysis_date": datetime.now().isoformat(),
                "analyzer": {
                    "model": llm_response.model_used,
                    "provider": llm_response.provider,
                    "tokens_used": llm_response.tokens_used,
                    "response_time": llm_response.response_time
                }
            },
            "documents": [
                {
                    "id": doc.get("id", ""),
                    "name": doc.get("number", doc.get("file_name", "")),
                    "client": doc.get("client", ""),
                    "status": doc.get("status", "")
                }
                for doc in documents[:20]  # Retornar até 20 documentos
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error in document analysis: {str(e)}")
        return {
            "analysis": {
                "summary": f"Erro na análise de documentos: {str(e)}",
                "insights": [],
                "recommendations": [],
                "risk_score": 0
            },
            "processed_documents": 0,
            "error": str(e)
        }

@app.post("/agents/smart-actions")
async def get_smart_actions(request: Dict[str, Any]):
    """Get smart actions based on user context and recent activity"""
    try:
        user_context = request.get("user_context", {})
        user_name = user_context.get("name", "usuário")
        user_role = user_context.get("role", "operador")
        
        # Buscar documentos recentes para sugerir ações
        recent_docs = await search_documents("", semantic_search=False)  # Get recent docs
        
        smart_actions = []
        
        # Ação 1: Análise de documentos recentes
        if recent_docs:
            smart_actions.append({
                "id": "analyze-recent-docs",
                "title": "Analisar Documentos Recentes",
                "description": f"Análise inteligente de {len(recent_docs)} documentos encontrados",
                "category": "analysis",
                "priority": "high",
                "suggestedPrompt": f"Gerar análise completa dos documentos recentes com insights e recomendações",
                "estimatedTime": "45 segundos",
                "aiPowered": True,
                "action_type": "document_analysis",
                "analysis_params": {
                    "document_count": len(recent_docs),
                    "analysis_type": "general"
                }
            })
        
        # Ação adicional: Análise de conformidade
        smart_actions.append({
            "id": "compliance-analysis",
            "title": "Análise de Conformidade",
            "description": "Verificar conformidade documental e regulatória",
            "category": "analysis",
            "priority": "medium",
            "suggestedPrompt": "Analisar documentos para identificar problemas de conformidade e regulamentação",
            "estimatedTime": "60 segundos",
            "aiPowered": True,
            "action_type": "compliance_analysis",
            "analysis_params": {
                "analysis_type": "compliance"
            }
        })
        
        # Ação adicional: Análise de riscos
        smart_actions.append({
            "id": "risk-analysis", 
            "title": "Análise de Riscos",
            "description": "Identificar riscos operacionais e logísticos",
            "category": "prediction",
            "priority": "medium",
            "suggestedPrompt": "Identificar e analisar riscos potenciais nos documentos e operações",
            "estimatedTime": "90 segundos",
            "aiPowered": True,
            "action_type": "risk_analysis",
            "analysis_params": {
                "analysis_type": "risk"
            }
        })
        
        # Ação 2: Relatório de status inteligente
        smart_actions.append({
            "id": "intelligent-status-report",
            "title": "Relatório de Status Inteligente",
            "description": "Resumo personalizado das suas operações",
            "category": "analysis", 
            "priority": "medium",
            "suggestedPrompt": f"Gerar um relatório personalizado de status para {user_name} ({user_role})",
            "estimatedTime": "45 segundos",
            "aiPowered": True
        })
        
        # Ação 3: Predição de problemas
        smart_actions.append({
            "id": "predict-issues",
            "title": "Identificar Possíveis Problemas",
            "description": "IA analisa padrões para prever problemas",
            "category": "prediction",
            "priority": "medium", 
            "suggestedPrompt": "Analisar documentos e identificar possíveis problemas ou atrasos",
            "estimatedTime": "60 segundos",
            "aiPowered": True
        })
        
        # Ação 4: Sugestões de otimização
        smart_actions.append({
            "id": "optimization-suggestions", 
            "title": "Sugestões de Otimização",
            "description": "Recomendações baseadas em dados",
            "category": "optimization",
            "priority": "low",
            "suggestedPrompt": "Analisar operações e sugerir melhorias de eficiência",
            "estimatedTime": "90 segundos", 
            "aiPowered": True
        })
        
        return {
            "smart_actions": smart_actions,
            "user_context": {
                "name": user_name,
                "role": user_role,
                "total_recent_docs": len(recent_docs) if recent_docs else 0
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating smart actions: {str(e)}")
        return {
            "smart_actions": [],
            "error": str(e)
        }

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session conversation history and context"""
    try:
        session = memory.get_session(session_id)
        
        return {
            "session_id": session_id,
            "created_at": session["created_at"].isoformat(),
            "last_activity": session["last_activity"].isoformat(),
            "message_count": len(session["messages"]),
            "context": session["context"],
            "document_history_count": len(session["document_history"]),
            "messages": [
                {
                    "id": msg["id"],
                    "role": msg["role"],
                    "content": msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"],
                    "timestamp": msg["timestamp"].isoformat(),
                    "has_attachments": len(msg["attachments"]) > 0
                }
                for msg in session["messages"][-10:]  # Últimas 10 mensagens
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_active_sessions():
    """List all active sessions"""
    try:
        # Cleanup old sessions first
        memory.cleanup_old_sessions(hours=24)
        
        sessions_info = []
        for session_id, session in memory.sessions.items():
            sessions_info.append({
                "session_id": session_id,
                "created_at": session["created_at"].isoformat(),
                "last_activity": session["last_activity"].isoformat(),
                "message_count": len(session["messages"]),
                "user_name": session.get("context", {}).get("name", "Unknown")
            })
        
        return {
            "active_sessions": len(sessions_info),
            "sessions": sorted(sessions_info, key=lambda x: x["last_activity"], reverse=True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/list")
async def list_agents():
    """List available agents"""
    agents_list = [
        "frontend_logistics_agent",
        "AdminAgent", 
        "LogisticsAgent",
        "FinanceAgent"
    ]
    
    # Add CrewAI agents if available
    if logistics_crew:
        crewai_status = logistics_crew.get_crew_status()
        agents_list.extend([agent["name"] for agent in crewai_status["agents"]])
    
    return {
        "available_agents": agents_list,
        "crewai_enabled": logistics_crew is not None
    }

@app.get("/agents/crewai/status")
async def get_crewai_status():
    """Get CrewAI agents detailed status"""
    try:
        if logistics_crew:
            crew_status = logistics_crew.get_crew_status()
            return {
                "status": "active",
                "crew_info": crew_status,
                "integration_status": "enabled",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "inactive",
                "crew_info": None,
                "integration_status": "disabled",
                "error": "LogisticsCrew not initialized",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"❌ Error getting CrewAI status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get agent status"""
    # Check if this is a CrewAI agent
    if logistics_crew and agent_name in ["Document Search Agent", "Document Analysis Agent", "Compliance Agent"]:
        crew_status = logistics_crew.get_crew_status()
        for agent in crew_status["agents"]:
            if agent["name"] == agent_name:
                return {
                    "agent": agent_name,
                    "status": agent["status"],
                    "version": "1.0.0",
                    "role": agent["role"],
                    "tools": agent["tools"],
                    "type": "crewai_agent"
                }
    
    # Default agent status
    return {
        "agent": agent_name,
        "status": "active",
        "version": "1.0.0",
        "capabilities": [
            "document_search",
            "shipment_tracking", 
            "delivery_status",
            "user_assistance"
        ],
        "type": "standard_agent"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)