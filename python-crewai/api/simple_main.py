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
        
        try:
            # Determine task type and prepare prompt
            message_lower = message.lower()
            user_name = user_context.get('name', 'usuário')
            
            # Enhanced intent detection with presupposition analysis
            def analyze_query_intent(message_lower, original_message):
                """Analyze query for specific intents and presuppositions"""
                
                # Document type mapping
                doc_type_map = {
                    'mdf': 'MDF', 'manifesto': 'MANIFESTO',
                    'cte': 'CTE', 'ct-e': 'CTE',
                    'bl': 'BL', 'bill': 'BL',
                    'awl': 'AWL', 'nf': 'NF', 'nota': 'NF'
                }
                
                # Patterns that indicate presupposition (user assumes docs exist)
                presupposition_patterns = [
                    'o que você pode me dizer sobre',
                    'me fale sobre', 'conte sobre', 'analise',
                    'quais são', 'como estão', 'status dos',
                    'que tipo de', 'quantos', 'há quanto'
                ]
                
                # Patterns that indicate search/lookup
                search_patterns = [
                    'buscar', 'procurar', 'encontrar', 'localizar',
                    'preciso de', 'quero ver', 'mostre'
                ]
                
                # Check for specific document types mentioned
                mentioned_doc_types = []
                for key, doc_type in doc_type_map.items():
                    if key in message_lower:
                        mentioned_doc_types.append(doc_type)
                
                # Determine intent type
                has_presupposition = any(pattern in message_lower for pattern in presupposition_patterns)
                has_search_intent = any(pattern in message_lower for pattern in search_patterns)
                
                return {
                    'doc_types': mentioned_doc_types,
                    'has_presupposition': has_presupposition,
                    'has_search_intent': has_search_intent,
                    'is_analysis_request': has_presupposition and mentioned_doc_types,
                    'is_general_search': has_search_intent or not has_presupposition
                }
            
            intent = analyze_query_intent(message_lower, message)
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
                        
                        # Create prompt for analysis-focused response
                        prompt = f"""
                        Você é um especialista em logística da MIT Tracking analisando documentos reais do sistema.
                        
                        Usuário: {user_name}
                        Consulta: "{message}"
                        TIPOS DE DOCUMENTOS SOLICITADOS: {', '.join(doc_types)}
                        
                        DADOS REAIS ENCONTRADOS NO SISTEMA:
                        {search_result}
                        
                        ESTATÍSTICAS DETALHADAS:
                        {stats_summary}
                        
                        INSTRUÇÕES PARA ANÁLISE:
                        1. O usuário PRESSUPÕE que existem documentos deste tipo no sistema
                        2. Analise os dados reais encontrados e forneça insights específicos
                        3. Se encontrou documentos: extraia padrões, tendências e informações relevantes
                        4. Se não encontrou: explique claramente e sugira verificações
                        5. Forneça recomendações práticas baseadas nos dados
                        6. Use formatação profissional com seções organizadas
                        7. Seja específico sobre quantidades, tipos e características dos documentos
                        
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
                        
                        # Create prompt for search-focused response  
                        prompt = f"""
                        Você é um assistente especializado em logística da MIT Tracking.
                        
                        Usuário: {user_name}
                        Consulta: "{message}"
                        
                        DADOS REAIS ENCONTRADOS:
                        {search_result}
                        
                        ESTATÍSTICAS RECENTES:
                        {stats_summary}
                        
                        INSTRUÇÕES:
                        1. Analise os dados reais encontrados na busca
                        2. Forneça insights específicos baseados nos documentos encontrados
                        3. Se não encontrou documentos, explique e sugira termos alternativos
                        4. Use formatação profissional com emojis
                        5. Seja prático e específico nas recomendações
                        
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
                # General logistics query
                prompt = f"""
                Você é um assistente especializado em logística da MIT Tracking.
                
                Usuário: {user_name}
                Mensagem: "{message}"
                
                CONTEXTO DO SISTEMA:
                - Sistema: MIT Tracking (Move In Tech)
                - Documentos suportados: CT-e, BL, AWL, Manifesto, NF
                - Funcionalidades: Busca semântica, análise de compliance, estatísticas
                - Especialização: Operações logísticas brasileiras
                
                INSTRUÇÕES:
                1. Responda como um especialista experiente em logística
                2. Seja específico e prático nas recomendações
                3. Use formatação profissional com emojis e seções organizadas
                4. Forneça exemplos concretos quando relevante
                5. Oriente sobre como usar melhor o sistema
                
                Forneça uma resposta completa e profissional.
                """
                task_type = TaskType.GENERAL
            
            # Generate response using LLM Router
            llm_response = await generate_llm_response(
                prompt=prompt,
                task_type=task_type,
                preferred_provider=LLMProvider.AUTO,
                max_tokens=800,
                temperature=0.3
            )
            
            response_text = llm_response.content if llm_response else "Desculpe, não consegui processar sua solicitação no momento."
            
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
        
        return {
            "message": response_text,
            "action": None,
            "data": None,
            "attachments": [],
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "success": True
        }
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)