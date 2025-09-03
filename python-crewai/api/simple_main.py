"""
MIT Tracking API Server - Versão Simplificada para Testes
FastAPI simples sem dependências complexas
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

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

@app.get("/chat/stats")
async def get_chat_stats():
    """Get chat system statistics"""
    try:
        # Import stats functions
        from cache.chat_cache import get_cache_stats
        from context.conversation_analyzer import get_conversation_analyzer
        from llm_router import get_llm_stats, get_llm_health
        
        cache_stats = get_cache_stats()
        analyzer = get_conversation_analyzer()
        conversation_stats = analyzer.get_session_stats()
        llm_stats = get_llm_stats()
        llm_health = get_llm_health()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cache": cache_stats,
            "conversations": conversation_stats,
            "llm": {
                "usage": llm_stats,
                "health": llm_health
            },
            "system_health": "healthy"
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "system_health": "degraded"
        }

@app.post("/chat/feedback")
async def submit_chat_feedback(feedback: dict):
    """Submit feedback about chat interactions"""
    try:
        session_id = feedback.get("session_id")
        rating = feedback.get("rating")  # 1-5
        comment = feedback.get("comment", "")
        message_id = feedback.get("message_id")
        
        # Log feedback for analysis
        logger.info(f"📝 Chat feedback - Session: {session_id}, Rating: {rating}, Comment: {comment[:50]}...")
        
        # In a real system, you'd save this to a database
        return {
            "status": "success",
            "message": "Feedback received, obrigado!",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing feedback: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/agents/route")
async def route_message(request: dict):
    """Route message to real frontend logistics agent with LLM and tools"""
    try:
        agent_name = request.get("agent_name", "unknown")
        user_context = request.get("user_context", {})
        request_data = request.get("request_data", {})
        message = request_data.get("message", "")
        session_id = request_data.get("session_id", "default")
        
        # Set up environment for CrewAI
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
        
        # Load API keys from .env file explicitly
        from pathlib import Path
        env_file = Path(__file__).parent.parent / ".env"
        load_dotenv(env_file)
        
        # Import LLM Router and tools
        from llm_router import generate_llm_response, TaskType, LLMProvider
        from tools.document_tools import (
            search_documents as search_documents_tool,
            analyze_document_content as analyze_document_content_tool,
            get_document_statistics as get_document_statistics_tool
        )
        from cache.chat_cache import get_cached_response, cache_response
        from context.conversation_analyzer import analyze_conversation
        
        try:
            # Check cache first
            cache_key_context = {
                "userId": user_context.get("userId"),
                "role": user_context.get("role"),
                "agent_name": agent_name
            }
            
            cached_response = get_cached_response(message, cache_key_context)
            if cached_response:
                logger.info(f"✅ Returning cached response for user {user_context.get('userId')}")
                # Mark as cached and return
                cached_response["metadata"]["cached"] = True
                return cached_response
            
            # Analyze conversation context
            conversation_analysis = analyze_conversation(message, user_context, session_id)
            
            # Determine task type and prepare prompt
            message_lower = message.lower()
            user_name = user_context.get('name', 'usuário')
            
            # Enhanced intent detection using conversation analysis
            intent = {
                'doc_types': conversation_analysis['doc_types'],
                'has_presupposition': conversation_analysis['intent'] == 'presupposed_query',
                'has_search_intent': conversation_analysis['intent'] in ['document_search', 'status_check'],
                'is_analysis_request': conversation_analysis['intent'] in ['document_analysis', 'presupposed_query'] and conversation_analysis['doc_types'],
                'is_general_search': conversation_analysis['intent'] in ['document_search', 'help_request']
            }
            is_document_query = bool(intent['doc_types']) or any(keyword in message_lower for keyword in [
                'documento', 'container', 'embarque', 'carga', 'search', 'busca', 'procur'
            ])
            
            if is_document_query:
                # Try to use document search tools with intelligent querying
                try:
                    # Determine search strategy based on intent
                    if intent['is_analysis_request']:
                        # User assumes docs exist - search specifically for those doc types
                        doc_types = intent['doc_types']
                        search_queries = []
                        
                        for doc_type in doc_types:
                            # Search for specific document type - first try as category, then as general search
                            type_result = search_documents_tool.func(doc_type, "semantic", 10)
                            search_queries.append(f"=== BUSCA POR {doc_type} ===\n{type_result}")
                        
                        search_result = "\n\n".join(search_queries) if search_queries else search_documents_tool.func(message, "semantic", 5)
                        
                        # Get general statistics
                        try:
                            stats = get_document_statistics_tool.func("30d")
                            # Try to get specific stats for the doc types mentioned
                            type_specific_stats = []
                            for doc_type in doc_types:
                                try:
                                    type_stats = get_document_statistics_tool.func("30d", doc_type)
                                    type_specific_stats.append(f"=== ESTATÍSTICAS {doc_type} ===\n{type_stats[:400]}")
                                except:
                                    pass
                            
                            stats_summary = "\n\n".join(type_specific_stats) if type_specific_stats else stats[:400] + "..."
                        except:
                            stats_summary = "Estatísticas temporariamente indisponíveis"
                        
                        # Create context-aware prompt for analysis-focused response
                        context_info = f"""
                        CONTEXTO CONVERSACIONAL:
                        - Nível de expertise: {conversation_analysis.get('expertise_level', 'novice')}
                        - Fluxo da conversa: {conversation_analysis.get('conversation_flow', 'exploration')}
                        - Resumo: {conversation_analysis.get('context_summary', 'Conversa iniciada')}
                        """
                        
                        prompt = f"""
                        Você é um especialista em logística da MIT Tracking analisando documentos reais do sistema.
                        
                        Usuário: {user_name}
                        Consulta: "{message}"
                        TIPOS DE DOCUMENTOS SOLICITADOS: {', '.join(doc_types)}
                        
                        {context_info}
                        
                        DADOS REAIS ENCONTRADOS NO SISTEMA:
                        {search_result}
                        
                        ESTATÍSTICAS DETALHADAS:
                        {stats_summary}
                        
                        INSTRUÇÕES PARA ANÁLISE ADAPTIVA:
                        1. O usuário PRESSUPÕE que existem documentos deste tipo no sistema
                        2. Adapte o nível de detalhamento ao expertise do usuário ({conversation_analysis.get('expertise_level', 'novice')})
                        3. Se encontrou documentos: extraia padrões, tendências e informações relevantes
                        4. Se não encontrou: explique claramente e sugira verificações
                        5. Forneça recomendações práticas baseadas nos dados
                        6. Use formatação profissional com seções organizadas
                        7. Seja específico sobre quantidades, tipos e características dos documentos
                        8. Considere o contexto conversacional para respostas mais relevantes
                        
                        Responda como especialista analisando dados REAIS do sistema.
                        """
                        
                    else:
                        # General search approach
                        search_result = search_documents_tool.func(message, "semantic", 5)
                        try:
                            stats = get_document_statistics_tool.func("30d")
                            stats_summary = stats[:300] + "..."
                        except:
                            stats_summary = "Estatísticas temporariamente indisponíveis"
                        
                        # Create context-aware prompt for search-focused response  
                        context_info = f"""
                        CONTEXTO CONVERSACIONAL:
                        - Nível de expertise: {conversation_analysis.get('expertise_level', 'novice')}
                        - Fluxo da conversa: {conversation_analysis.get('conversation_flow', 'exploration')}
                        - Resumo: {conversation_analysis.get('context_summary', 'Conversa iniciada')}
                        """
                        
                        prompt = f"""
                        Você é um assistente especializado em logística da MIT Tracking.
                        
                        Usuário: {user_name}
                        Consulta: "{message}"
                        
                        {context_info}
                        
                        DADOS REAIS ENCONTRADOS:
                        {search_result}
                        
                        ESTATÍSTICAS RECENTES:
                        {stats_summary}
                        
                        INSTRUÇÕES ADAPTIVAS:
                        1. Analise os dados reais encontrados na busca
                        2. Adapte o nível de detalhamento ao expertise do usuário ({conversation_analysis.get('expertise_level', 'novice')})
                        3. Se não encontrou documentos, explique e sugira termos alternativos
                        4. Use formatação profissional com emojis
                        5. Seja prático e específico nas recomendações
                        6. Considere o contexto conversacional para respostas mais relevantes
                        
                        Responda como especialista em logística com base nos dados reais apresentados.
                        """
                    
                except Exception as e:
                    # Fallback if tools fail
                    prompt = f"""
                    Você é um assistente especializado em logística da MIT Tracking.
                    
                    Usuário: {user_name}  
                    Consulta: "{message}"
                    
                    A busca nos documentos encontrou um problema técnico: {str(e)[:100]}
                    
                    INSTRUÇÕES:
                    1. Reconheça que houve um problema técnico com a busca
                    2. Oriente o usuário sobre como fazer consultas efetivas
                    3. Explique os tipos de documentos que o sistema suporta
                    4. Sugira consultas alternativas
                    5. Use formatação profissional com emojis
                    
                    Seja útil mesmo sem acesso aos dados.
                    """
                    
                task_type = TaskType.LOGISTICS
            else:
                # Context-aware general logistics query
                context_info = f"""
                CONTEXTO CONVERSACIONAL:
                - Nível de expertise: {conversation_analysis.get('expertise_level', 'novice')}
                - Fluxo da conversa: {conversation_analysis.get('conversation_flow', 'exploration')}
                - Resumo: {conversation_analysis.get('context_summary', 'Conversa iniciada')}
                """
                
                prompt = f"""
                Você é um assistente especializado em logística da MIT Tracking.
                
                Usuário: {user_name}
                Mensagem: "{message}"
                
                {context_info}
                
                CONTEXTO DO SISTEMA:
                - Sistema: MIT Tracking (Move In Tech)
                - Documentos suportados: CT-e, BL, AWL, Manifesto, NF
                - Funcionalidades: Busca semântica, análise de compliance, estatísticas
                - Especialização: Operações logísticas brasileiras
                
                INSTRUÇÕES ADAPTIVAS:
                1. Responda como um especialista experiente em logística
                2. Adapte o nível de detalhamento ao expertise do usuário ({conversation_analysis.get('expertise_level', 'novice')})
                3. Seja específico e prático nas recomendações
                4. Use formatação profissional com emojis e seções organizadas
                5. Forneça exemplos concretos quando relevante
                6. Oriente sobre como usar melhor o sistema
                7. Considere o contexto conversacional para respostas mais personalizadas
                
                Forneça uma resposta completa e profissional.
                """
                task_type = TaskType.GENERAL
            
            # Generate response using LLM Router
            llm_response = await generate_llm_response(
                prompt=prompt,
                task_type=task_type,
                preferred_provider=LLMProvider.AUTO,
                max_tokens=1200,
                temperature=0.3
            )
            
            response_text = llm_response.content if llm_response else "Desculpe, não consegui processar sua solicitação no momento."
            
            # Enhanced response processing
            attachments = []
            action = None
            data = None
            
            # Extract document references and create attachments
            if is_document_query and "search_result" in locals():
                try:
                    # Parse search results for document attachments
                    import re
                    doc_refs = re.findall(r'Documento: ([^\n]+)', str(search_result))
                    
                    for doc_ref in doc_refs[:5]:  # Limit to 5 attachments
                        if 'order_id' in doc_ref.lower():
                            # Extract order ID for direct document access
                            order_match = re.search(r'order_id[:\s]*([a-f0-9-]{36})', doc_ref, re.IGNORECASE)
                            if order_match:
                                order_id = order_match.group(1)
                                attachments.append({
                                    "type": "document_reference",
                                    "title": f"Documentos da Order {order_id[:8]}...",
                                    "description": doc_ref[:100] + "..." if len(doc_ref) > 100 else doc_ref,
                                    "order_id": order_id,
                                    "action": "view_order_documents"
                                })
                    
                    # If we found document attachments, suggest an action
                    if attachments:
                        action = "show_documents"
                        data = {"document_count": len(attachments)}
                        
                except Exception as attach_error:
                    logger.warning(f"Error processing attachments: {attach_error}")
            
        except Exception as e:
            # Fallback response
            error_msg = str(e)
            response_text = f"""🤖 **Assistente Logístico MIT**

Olá {user_context.get('name', 'usuário')}! Sou especializado em operações logísticas.

🚛 **Posso ajudar com:**
- **Documentos**: Busca de CT-e, BL, AWL, Manifestos, Notas Fiscais
- **Embarques**: Status de cargas, tracking de containers  
- **Compliance**: Validação regulatória de documentos
- **Análises**: Relatórios e estatísticas operacionais

⚠️ **Sistema de IA temporariamente indisponível**
Erro técnico: {error_msg[:100]}

💡 **Sugestões:**
- Tente reformular sua pergunta
- Use termos específicos como "CT-e", "container", "embarque"
- Para suporte técnico, contate a equipe MIT

Como posso ajudar especificamente?"""
        
        final_response = {
            "message": response_text,
            "action": action,
            "data": data,
            "attachments": attachments,
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "success": True,
            "metadata": {
                "model_used": llm_response.model_used if llm_response else "fallback",
                "provider": llm_response.provider if llm_response else "none",
                "tokens_used": llm_response.tokens_used if llm_response else 0,
                "response_time": llm_response.response_time if llm_response else 0,
                "intent_detected": "document_query" if is_document_query else "general_query",
                "doc_types_mentioned": intent.get('doc_types', []) if 'intent' in locals() else [],
                "cached": False,
                "conversation_analysis": conversation_analysis,
                "user_expertise_level": conversation_analysis.get('expertise_level', 'novice'),
                "suggested_followups": conversation_analysis.get('suggested_followups', [])
            }
        }
        
        # Cache the response (with appropriate TTL)
        ttl = 1800 if is_document_query else 3600  # 30 min for docs, 1 hour for general
        cache_response(message, cache_key_context, final_response, ttl)
        
        return final_response
    except Exception as e:
        # Fallback with error details for debugging
        import traceback
        error_details = traceback.format_exc()
        
        return {
            "message": f"Sistema de agentes temporariamente indisponível. Erro: {str(e)[:100]}",
            "action": None,
            "data": {"error_details": error_details},
            "attachments": [],
            "agent": "error_handler",
            "timestamp": datetime.now().isoformat(),
            "session_id": request_data.get("session_id"),
            "success": False
        }

@app.post("/cache/invalidate")
async def invalidate_cache(request: dict):
    """Invalidate cache entries matching a pattern"""
    try:
        pattern = request.get("pattern", "")
        if not pattern:
            return {"error": "Pattern is required"}
        
        from cache.chat_cache import invalidate_cache_pattern
        invalidate_cache_pattern(pattern)
        
        return {
            "status": "success",
            "message": f"Cache entries matching '{pattern}' invalidated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/chat/insights/{session_id}")
async def get_conversation_insights(session_id: str):
    """Get insights about a specific conversation session"""
    try:
        from context.conversation_analyzer import get_conversation_analyzer
        
        analyzer = get_conversation_analyzer()
        
        if session_id not in analyzer.active_sessions:
            return {
                "error": "Session not found",
                "session_id": session_id
            }
        
        context = analyzer.active_sessions[session_id]
        
        # Generate detailed insights
        insights = {
            "session_id": session_id,
            "user_id": context.user_id,
            "conversation_summary": analyzer._summarize_context(context),
            "total_turns": len(context.turns),
            "user_expertise_level": context.user_expertise_level,
            "conversation_flow": context.conversation_flow,
            "active_documents": context.active_documents,
            "recent_intents": [turn.intent for turn in context.turns[-5:]] if context.turns else [],
            "document_types_discussed": list(set(
                doc_type for turn in context.turns 
                for doc_type in turn.doc_types
            )),
            "suggested_next_actions": analyzer._suggest_followups(context),
            "conversation_patterns": analyzer._generate_insights(context),
            "timestamp": datetime.now().isoformat()
        }
        
        return insights
        
    except Exception as e:
        return {
            "error": str(e),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)