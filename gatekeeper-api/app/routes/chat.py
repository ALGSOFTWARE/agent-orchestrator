"""
Chat Routes - Gatekeeper API

Rotas para o sistema de chat inteligente:
- POST /chat/message - Enviar mensagem para agentes IA
- GET /chat/history - Histórico de conversas
- POST /chat/session - Criar nova sessão de chat
- GET /chat/sessions - Listar sessões do usuário
"""

from fastapi import APIRouter, HTTPException, status, Query, Body
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import uuid

from ..models import ChatMessage, ChatSession, ChatRequest, ChatResponse
from ..database import DatabaseService
from ..services.crewai_service import CrewAIService

logger = logging.getLogger("GatekeeperAPI.Chat")
router = APIRouter()

# Instanciar serviço CrewAI
crewai_service = CrewAIService()


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    chat_request: ChatRequest,
    current_user_id: str = Query(..., description="ID do usuário que faz a requisição"),
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição")
):
    """
    Envia mensagem para o sistema de agentes IA e retorna resposta
    """
    try:
        logger.info(f"💬 Nova mensagem de chat do usuário {current_user_id}")
        
        # Criar contexto do usuário
        user_context = {
            "userId": current_user_id,
            "role": current_user_role,
            "sessionId": chat_request.session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Determinar agente baseado no tipo de mensagem ou usar LogisticsAgent por padrão
        agent_name = chat_request.agent_name or "LogisticsAgent"
        
        # Enviar mensagem para o agente via CrewAI service
        agent_response = await crewai_service.send_message_to_agent(
            agent_name=agent_name,
            message=chat_request.message,
            user_context=user_context
        )
        
        # Verificar se houve erro de comunicação com CrewAI e usar fallback inteligente
        if agent_response.get("success") == False:
            logger.info(f"🔄 CrewAI indisponível, usando fallback inteligente para: {chat_request.message}")
            agent_message_content = _generate_intelligent_fallback_response(chat_request.message, current_user_role)
        else:
            # CrewAI service retorna conteúdo no campo "message"
            agent_message_content = agent_response.get("message", "Processado com sucesso.")
        
        # Salvar mensagem do usuário no contexto
        await DatabaseService.add_context(
            user_id=current_user_id,
            input_text=chat_request.message,
            output_text=agent_message_content,
            agents=[agent_name],
            session_id=chat_request.session_id,
            metadata={
                "agent_used": agent_name,
                "response_status": agent_response.get("status", "unknown"),
                "processing_time": agent_response.get("processing_time", 0)
            }
        )
        
        # Criar resposta
        response = ChatResponse(
            message_id=str(uuid.uuid4()),
            content=agent_message_content,
            agent_name=agent_name,
            timestamp=datetime.now(),
            session_id=chat_request.session_id,
            attachments=agent_response.get("attachments", []),
            metadata={
                "processing_time": agent_response.get("processing_time", 0),
                "confidence": agent_response.get("confidence", 0.8)
            }
        )
        
        logger.info(f"✅ Resposta enviada pelo {agent_name}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro no chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no processamento da mensagem: {str(e)}"
        )


@router.get("/history")
async def get_chat_history(
    current_user_id: str = Query(..., description="ID do usuário"),
    session_id: Optional[str] = Query(None, description="ID da sessão específica"),
    limit: int = Query(50, ge=1, le=200, description="Limite de mensagens"),
    days_back: int = Query(7, ge=1, le=365, description="Dias para voltar no histórico")
):
    """
    Retorna histórico de conversas do usuário
    """
    try:
        # Usar o sistema de contexto existente
        context_data = await get_user_context(
            user_id=current_user_id,
            current_user_id=current_user_id,
            current_user_role="user",  # Assumindo role básico
            limit=limit,
            session_id=session_id,
            days_back=days_back
        )
        
        # Converter contextos para formato de chat
        messages = []
        for ctx in context_data.get("contexts", []):
            # Mensagem do usuário
            messages.append({
                "id": f"{ctx['id']}_user",
                "type": "user",
                "content": ctx["input"],
                "timestamp": ctx["timestamp"],
                "session_id": ctx["session_id"]
            })
            
            # Resposta do agente
            messages.append({
                "id": f"{ctx['id']}_agent",
                "type": "agent",
                "content": ctx["output"],
                "timestamp": ctx["timestamp"],
                "session_id": ctx["session_id"],
                "agent_name": ctx.get("agents_involved", ["LogisticsAgent"])[0] if ctx.get("agents_involved") else "LogisticsAgent"
            })
        
        # Ordenar por timestamp
        messages.sort(key=lambda x: x["timestamp"])
        
        return {
            "messages": messages,
            "pagination": context_data.get("pagination", {}),
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar histórico: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar histórico de conversas"
        )


@router.post("/session")
async def create_chat_session(
    current_user_id: str = Query(..., description="ID do usuário"),
    session_name: Optional[str] = Body(None, description="Nome da sessão")
):
    """
    Cria uma nova sessão de chat
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Salvar contexto inicial da sessão
        await DatabaseService.add_context(
            user_id=current_user_id,
            input_text="NOVA_SESSAO_INICIADA",
            output_text=f"Sessão de chat iniciada: {session_name or 'Chat Inteligente'}",
            agents=["SystemAgent"],
            session_id=session_id,
            metadata={
                "session_name": session_name,
                "session_type": "chat",
                "created_at": datetime.now().isoformat()
            }
        )
        
        return {
            "session_id": session_id,
            "session_name": session_name or "Nova Conversa",
            "created_at": datetime.now().isoformat(),
            "user_id": current_user_id
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar sessão: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar sessão de chat"
        )


@router.get("/sessions")
async def get_user_chat_sessions(
    current_user_id: str = Query(..., description="ID do usuário"),
    days_back: int = Query(30, ge=1, le=365, description="Dias para voltar")
):
    """
    Lista sessões de chat do usuário
    """
    try:
        # Usar o endpoint de sessões existente do contexto
        from .context import get_user_sessions
        
        sessions_data = await get_user_sessions(
            user_id=current_user_id,
            current_user_id=current_user_id,
            current_user_role="user",
            days_back=days_back
        )
        
        # Filtrar apenas sessões de chat e adicionar metadados
        chat_sessions = []
        for session in sessions_data.get("sessions", []):
            chat_sessions.append({
                "session_id": session["session_id"],
                "first_message": session["first_interaction"],
                "last_message": session["last_interaction"],
                "message_count": session["interaction_count"],
                "agents_used": session["agents_used"],
                "duration": session.get("duration_seconds", 0)
            })
        
        return {
            "user_id": current_user_id,
            "sessions": chat_sessions,
            "total": len(chat_sessions)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar sessões: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar sessões de chat"
        )


@router.get("/agents")
async def get_available_agents():
    """
    Lista agentes disponíveis para chat
    """
    try:
        agents = await crewai_service.get_available_agents()
        
        # Adicionar informações sobre cada agente
        agent_info = []
        for agent in agents:
            status = await crewai_service.get_agent_status(agent)
            agent_info.append({
                "name": agent,
                "display_name": agent.replace("Agent", " Agent"),
                "status": status.get("status", "unknown"),
                "description": _get_agent_description(agent)
            })
        
        return {
            "available_agents": agent_info,
            "default_agent": "LogisticsAgent"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar agentes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar agentes disponíveis"
        )


@router.get("/health")
async def chat_health_check():
    """
    Verifica status do sistema de chat
    """
    try:
        # Verificar conectividade com CrewAI
        crewai_healthy = await crewai_service.health_check()
        
        # Testar agentes
        agent_tests = await crewai_service.test_all_agents()
        
        overall_status = "healthy" if crewai_healthy and agent_tests.get("overall_status") == "healthy" else "degraded"
        
        return {
            "status": overall_status,
            "crewai_service": "healthy" if crewai_healthy else "unhealthy",
            "agents": agent_tests.get("agent_results", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no health check do chat: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def _get_agent_description(agent_name: str) -> str:
    """
    Retorna descrição do agente baseado no nome
    """
    descriptions = {
        "LogisticsAgent": "Especialista em operações logísticas, rastreamento e documentos",
        "AdminAgent": "Administrador do sistema com acesso completo",
        "FinanceAgent": "Especialista em análises financeiras e custos logísticos"
    }
    
    return descriptions.get(agent_name, "Agente especializado do sistema")


# Importar função necessária do módulo context
from .context import get_user_context


def _generate_intelligent_fallback_response(message: str, user_role: str) -> str:
    """
    Gera resposta inteligente quando CrewAI não está disponível
    """
    message_lower = message.lower()
    
    # Respostas para rastreamento (prioridade alta)
    if any(keyword in message_lower for keyword in ["rastrear", "tracking", "onde está", "onde esta", "localizar"]):
        return f"""📍 **Rastreamento de Cargas**

Posso te ajudar a rastrear suas cargas e embarques:

• **Status atual**: Informe o número da carga para status detalhado
• **Localização**: Coordenadas GPS e último checkpoint registrado  
• **Previsão**: Estimativa de chegada e próximas paradas
• **Histórico**: Timeline completa da jornada

🚛 Qual carga você gostaria de rastrear?

*Sistema de rastreamento funcionando - agentes IA em manutenção.*"""
    
    # Respostas para consultas de documentos
    elif any(keyword in message_lower for keyword in ["cte", "ct-e", "documento", "embarque", "carga"]):
        return f"""🔍 **Consulta de Documentos**

Para consultar documentos como CT-e, BL, NF-e e manifestos, posso te ajudar de algumas formas:

• **Por número**: "Consulte o CT-e ABC123" ou "Status da carga XYZ789"
• **Por cliente**: "Documentos da empresa Mercosul Line"
• **Por período**: "CT-es da última semana"

💡 **Dica**: Use números específicos de embarque ou documento para resultados mais precisos.

*Agentes de IA temporariamente indisponíveis - usando modo assistente.*"""
    
    # Respostas para help/ajuda
    elif any(keyword in message_lower for keyword in ["ajuda", "help", "como", "posso"]):
        return f"""🤖 **Assistente Logístico - Modo Limitado**

Como posso te ajudar hoje? Funcionalidades disponíveis:

📋 **Documentos**: Consulta CT-e, BL, NF-e, manifestos
📍 **Rastreamento**: Status e localização de cargas  
📊 **Relatórios**: Análises de performance e KPIs
🔍 **Busca**: Pesquisa por cliente, período ou número
⚙️ **Configurações**: Preferências e notificações

Digite sua solicitação específica ou escolha uma das opções acima.

*Agentes especializados temporariamente indisponíveis.*"""
    
    # Respostas para saudações
    elif any(keyword in message_lower for keyword in ["oi", "olá", "hello", "bom dia", "boa tarde"]):
        return f"""👋 **Olá! Bem-vindo ao Sistema Logístico Inteligente**

Sou seu assistente para operações logísticas. Posso te ajudar com:

• Consultas de documentos (CT-e, BL, NF-e)
• Rastreamento de cargas e embarques
• Status de entregas e rotas
• Relatórios e análises

Como posso te ajudar hoje?

*Modo assistente ativo - agentes especializados em manutenção.*"""
    
    # Respostas para relatórios
    elif any(keyword in message_lower for keyword in ["relatório", "report", "análise", "kpi", "dashboard"]):
        return f"""📊 **Relatórios e Análises**

Posso gerar relatórios sobre suas operações logísticas:

• **Performance**: KPIs de entrega e tempo de trânsito
• **Custos**: Análise de custos por rota e modal
• **Clientes**: Histórico e volume por cliente
• **Rotas**: Eficiência e otimização de trajetos

Que tipo de relatório você precisa?

*Dados atualizados - processamento avançado temporariamente limitado.*"""
    
    # Resposta genérica inteligente
    else:
        return f"""🤔 **Processando sua solicitação...**

Entendi que você precisa de ajuda com: "{message}"

Como os agentes especializados estão temporariamente indisponíveis, posso te orientar:

1. **Para documentos específicos**: Informe números de CT-e, BL ou embarque
2. **Para rastreamento**: Forneça o código da carga
3. **Para relatórios**: Especifique o período e tipo de análise
4. **Para dúvidas gerais**: Digite "ajuda" para ver todas as opções

Reformule sua pergunta de forma mais específica e vou te ajudar da melhor forma possível!

*Sistema funcionando em modo assistente básico.*"""