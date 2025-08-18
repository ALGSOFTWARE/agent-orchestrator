"""
Context Routes - Gatekeeper API

Rotas para gerenciamento de contexto e histórico de interações:
- GET /context/{user_id} - Histórico de interações do usuário
- POST /context/{user_id} - Adicionar nova entrada de contexto
- GET /context/{user_id}/sessions - Listar sessões do usuário
- DELETE /context/{user_id} - Limpar histórico (admin apenas)
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from ..models import Context, ContextRequest, UserRole
from ..database import DatabaseService

logger = logging.getLogger("GatekeeperAPI.Context")
router = APIRouter()


@router.get("/{user_id}")
async def get_user_context(
    user_id: str,
    current_user_id: str = Query(..., description="ID do usuário que faz a requisição"),
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição"),
    limit: int = Query(50, ge=1, le=200, description="Número máximo de registros"),
    session_id: Optional[str] = Query(None, description="Filtrar por sessão específica"),
    agent_filter: Optional[str] = Query(None, description="Filtrar por agente"),
    days_back: int = Query(30, ge=1, le=365, description="Número de dias para voltar no histórico")
):
    """
    Retorna histórico de contexto/interações de um usuário
    
    Permissões:
    - Usuários podem ver seu próprio histórico
    - Admins podem ver histórico de qualquer usuário
    """
    try:
        # Verificar permissões
        if current_user_id != user_id and current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode acessar seu próprio histórico"
            )
        
        # Construir filtros
        filters = {"user_id": user_id}
        
        if session_id:
            filters["session_id"] = session_id
        
        # Filtro por data
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        filters["timestamp"] = {"$gte": cutoff_date}
        
        # Buscar contextos
        query = Context.find(filters)
        
        if agent_filter:
            query = query.find({"agents_involved": {"$in": [agent_filter]}})
        
        contexts = await query.sort(-Context.timestamp).limit(limit).to_list()
        
        # Contar total
        total = await Context.find(filters).count()
        
        # Preparar resposta
        context_data = []
        for context in contexts:
            context_data.append({
                "id": str(context.id),
                "session_id": context.session_id,
                "input": context.input,
                "output": context.output,
                "agents_involved": context.agents_involved,
                "timestamp": context.timestamp.isoformat(),
                "metadata": context.metadata,
                "response_time": context.response_time
            })
        
        # Estatísticas do período
        stats = await _get_context_stats(user_id, days_back)
        
        return {
            "user_id": user_id,
            "contexts": context_data,
            "pagination": {
                "limit": limit,
                "total": total,
                "returned": len(context_data)
            },
            "filters": {
                "session_id": session_id,
                "agent_filter": agent_filter,
                "days_back": days_back
            },
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter contexto do usuário {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/{user_id}")
async def add_context(
    user_id: str,
    context_request: ContextRequest,
    current_user_id: str = Query(..., description="ID do usuário que faz a requisição"),
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição")
):
    """
    Adiciona nova entrada de contexto para um usuário
    
    Normalmente chamado automaticamente pelo sistema, mas pode ser usado
    manualmente por admins ou pelo próprio usuário.
    """
    try:
        # Verificar permissões
        if current_user_id != user_id and current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode adicionar contexto para si mesmo"
            )
        
        # Adicionar contexto
        context = await DatabaseService.add_context(
            user_id=user_id,
            input_text=context_request.input,
            output_text=context_request.output,
            agents=context_request.agents_involved,
            session_id=context_request.session_id,
            metadata=context_request.metadata
        )
        
        if not context:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao adicionar contexto"
            )
        
        logger.info(f"✅ Contexto adicionado para usuário {user_id}")
        
        return {
            "message": "Contexto adicionado com sucesso",
            "context": {
                "id": str(context.id),
                "user_id": context.user_id,
                "session_id": context.session_id,
                "timestamp": context.timestamp.isoformat(),
                "agents_involved": context.agents_involved
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar contexto para usuário {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{user_id}/sessions")
async def get_user_sessions(
    user_id: str,
    current_user_id: str = Query(..., description="ID do usuário que faz a requisição"),
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição"),
    days_back: int = Query(30, ge=1, le=365, description="Número de dias para voltar")
):
    """
    Lista sessões únicas do usuário com estatísticas
    """
    try:
        # Verificar permissões
        if current_user_id != user_id and current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode acessar suas próprias sessões"
            )
        
        # Filtro por data
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Aggregation para obter sessões únicas com estatísticas
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "timestamp": {"$gte": cutoff_date}
                }
            },
            {
                "$group": {
                    "_id": "$session_id",
                    "session_id": {"$first": "$session_id"},
                    "first_interaction": {"$min": "$timestamp"},
                    "last_interaction": {"$max": "$timestamp"},
                    "interaction_count": {"$sum": 1},
                    "agents_used": {"$addToSet": "$agents_involved"}
                }
            },
            {
                "$sort": {"last_interaction": -1}
            }
        ]
        
        # Executar aggregation
        sessions_raw = await Context.aggregate(pipeline).to_list()
        
        # Processar resultados
        sessions = []
        for session in sessions_raw:
            # Flatten agents_used (pode ser lista de listas)
            agents_flat = []
            for agent_list in session["agents_used"]:
                if isinstance(agent_list, list):
                    agents_flat.extend(agent_list)
                else:
                    agents_flat.append(agent_list)
            
            # Calcular duração da sessão
            duration = None
            if session["first_interaction"] and session["last_interaction"]:
                duration = (session["last_interaction"] - session["first_interaction"]).total_seconds()
            
            sessions.append({
                "session_id": session["session_id"],
                "first_interaction": session["first_interaction"].isoformat() if session["first_interaction"] else None,
                "last_interaction": session["last_interaction"].isoformat() if session["last_interaction"] else None,
                "interaction_count": session["interaction_count"],
                "agents_used": list(set(agents_flat)),  # Remove duplicatas
                "duration_seconds": duration
            })
        
        return {
            "user_id": user_id,
            "sessions": sessions,
            "total_sessions": len(sessions),
            "date_range": {
                "from": cutoff_date.isoformat(),
                "to": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter sessões do usuário {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.delete("/{user_id}")
async def clear_user_context(
    user_id: str,
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição"),
    session_id: Optional[str] = Query(None, description="Limpar apenas uma sessão específica"),
    older_than_days: int = Query(0, ge=0, description="Limpar apenas registros mais antigos que X dias")
):
    """
    Limpa histórico de contexto de um usuário (apenas admins)
    """
    try:
        # Verificar permissões (apenas admins)
        if current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem limpar histórico"
            )
        
        # Construir filtros
        filters = {"user_id": user_id}
        
        if session_id:
            filters["session_id"] = session_id
        
        if older_than_days > 0:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            filters["timestamp"] = {"$lt": cutoff_date}
        
        # Contar registros que serão removidos
        count_to_delete = await Context.find(filters).count()
        
        # Remover registros
        result = await Context.find(filters).delete()
        
        logger.info(f"✅ Removidos {count_to_delete} registros de contexto do usuário {user_id} por admin")
        
        return {
            "message": "Histórico limpo com sucesso",
            "user_id": user_id,
            "records_deleted": count_to_delete,
            "filters_applied": {
                "session_id": session_id,
                "older_than_days": older_than_days if older_than_days > 0 else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao limpar contexto do usuário {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/stats/summary")
async def get_context_summary(
    current_user_role: str = Query(..., description="Role do usuário que faz a requisição"),
    days_back: int = Query(7, ge=1, le=365, description="Número de dias para estatísticas")
):
    """
    Retorna resumo estatístico geral do contexto (apenas admins)
    """
    try:
        # Verificar permissões
        if current_user_role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem ver estatísticas gerais"
            )
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Total de interações no período
        total_interactions = await Context.find({"timestamp": {"$gte": cutoff_date}}).count()
        
        # Usuários únicos no período
        unique_users_pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$group": {"_id": "$user_id"}},
            {"$count": "unique_users"}
        ]
        unique_users_result = await Context.aggregate(unique_users_pipeline).to_list()
        unique_users = unique_users_result[0]["unique_users"] if unique_users_result else 0
        
        # Sessões únicas no período
        unique_sessions_pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$group": {"_id": "$session_id"}},
            {"$count": "unique_sessions"}
        ]
        unique_sessions_result = await Context.aggregate(unique_sessions_pipeline).to_list()
        unique_sessions = unique_sessions_result[0]["unique_sessions"] if unique_sessions_result else 0
        
        # Agentes mais utilizados
        agents_pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$unwind": "$agents_involved"},
            {"$group": {"_id": "$agents_involved", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        agents_stats = await Context.aggregate(agents_pipeline).to_list()
        
        return {
            "period": {
                "days_back": days_back,
                "from": cutoff_date.isoformat(),
                "to": datetime.utcnow().isoformat()
            },
            "summary": {
                "total_interactions": total_interactions,
                "unique_users": unique_users,
                "unique_sessions": unique_sessions,
                "avg_interactions_per_user": round(total_interactions / unique_users, 2) if unique_users > 0 else 0,
                "avg_interactions_per_session": round(total_interactions / unique_sessions, 2) if unique_sessions > 0 else 0
            },
            "top_agents": [
                {"agent": stat["_id"], "usage_count": stat["count"]}
                for stat in agents_stats
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de contexto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


async def _get_context_stats(user_id: str, days_back: int) -> dict:
    """
    Função auxiliar para obter estatísticas de contexto de um usuário
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Total de interações
        total = await Context.find({
            "user_id": user_id,
            "timestamp": {"$gte": cutoff_date}
        }).count()
        
        # Sessões únicas
        sessions_pipeline = [
            {"$match": {"user_id": user_id, "timestamp": {"$gte": cutoff_date}}},
            {"$group": {"_id": "$session_id"}},
            {"$count": "unique_sessions"}
        ]
        sessions_result = await Context.aggregate(sessions_pipeline).to_list()
        unique_sessions = sessions_result[0]["unique_sessions"] if sessions_result else 0
        
        # Agentes utilizados
        agents_pipeline = [
            {"$match": {"user_id": user_id, "timestamp": {"$gte": cutoff_date}}},
            {"$unwind": "$agents_involved"},
            {"$group": {"_id": "$agents_involved", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        agents_stats = await Context.aggregate(agents_pipeline).to_list()
        
        return {
            "total_interactions": total,
            "unique_sessions": unique_sessions,
            "agents_used": [
                {"agent": stat["_id"], "count": stat["count"]}
                for stat in agents_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas para usuário {user_id}: {str(e)}")
        return {
            "total_interactions": 0,
            "unique_sessions": 0,
            "agents_used": []
        }