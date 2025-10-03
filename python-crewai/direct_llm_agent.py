#!/usr/bin/env python3
"""Agente logístico direto: roteamento para LLMs cloud ou simulação local."""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv

from llm_router import TaskType, detect_task_type, generate_llm_response

# Carregar variáveis para descoberta de API keys
load_dotenv()


class DirectLogisticsAgent:
    """Agente de Logística direto que trabalha com LLM Router ou fallback simulado."""

    _PREFERRED_MAP = {
        TaskType.LOGISTICS: "openai",
        TaskType.GENERAL: "openai",
        TaskType.CUSTOMS: "openai",
        TaskType.FINANCIAL: "gemini",
        TaskType.ANALYSIS: "gemini",
    }

    def __init__(self) -> None:
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")

        if self.openai_key or self.gemini_key:
            print("🤖 DirectLogisticsAgent inicializado com LLM Router (OpenAI/Gemini)")
        else:
            print("🤖 DirectLogisticsAgent inicializado em modo de simulação inteligente")

    async def process_message(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mensagem do usuário e retorna resposta estruturada."""

        user_name = user_context.get("name", "usuário")
        user_role = user_context.get("role", "user")
        task_type = detect_task_type(message)
        preferred_provider = self._PREFERRED_MAP.get(task_type, "openai")
        semantic_summary = user_context.get("semanticContextSummary")

        try:
            response_text = await self._get_llm_response(
                message=message,
                user_name=user_name,
                user_role=user_role,
                task_type=task_type,
                preferred_provider=preferred_provider,
                semantic_summary=semantic_summary,
            )

            return {
                "agent": "DirectLogisticsAgent",
                "status": "success",
                "response": response_text,
                "context": user_context,
                "specialization": "Logística e Transporte",
                "llm_provider": preferred_provider,
                "capabilities": [
                    "Análise de CT-e e documentos de transporte",
                    "Rastreamento de containers",
                    "Insights sobre ETA/ETD",
                    "Documentação multimodal",
                    "Status de entregas",
                ],
            }

        except Exception as exc:  # noqa: BLE001
            print(f"❌ Erro no DirectLogisticsAgent: {exc}")
            return {
                "agent": "DirectLogisticsAgent",
                "status": "error",
                "error": str(exc),
                "message": "Erro interno do agente de logística",
            }

    async def _get_llm_response(
        self,
        *,
        message: str,
        user_name: str,
        user_role: str,
        task_type: TaskType,
        preferred_provider: str,
        semantic_summary: Optional[str] = None,
    ) -> str:
        """Obtém resposta via LLM Router ou realiza simulação ao faltar credenciais."""

        context_section = ""
        if semantic_summary:
            context_section = (
                "\n\nContexto relevante recuperado dos documentos (use como base factual e cite a order/documento sempre que possível):\n"
                f"{semantic_summary}\n"
            )

        prompt = f"""Você é um especialista em logística da MIT Tracking, um sistema brasileiro de gestão logística.

Usuário: {user_name} ({user_role})
Pergunta: "{message}"

Você trabalha com:
- CT-e (Conhecimento de Transporte Eletrônico)
- BL (Bill of Lading)
- Rastreamento de containers
- Documentação multimodal
- Sistema MIT Tracking com documentos: CT-e, BL, AWL, Manifesto, NF

{context_section}

Responda como especialista em logística brasileira, sendo específico e prático.
- Priorize os trechos listados acima quando disponíveis.
- Cite a order e o documento de origem nas referências da resposta.
- Caso não haja contexto suficiente, deixe claro o que está faltando antes de inferir novos fatos."""

        if self.openai_key or self.gemini_key:
            llm_response = await generate_llm_response(
                prompt,
                task_type=task_type,
                preferred_provider=preferred_provider,
                user_context={"user_name": user_name, "user_role": user_role},
            )
            return (
                f"{llm_response.content}\n\n🧠 _Processado via {llm_response.provider.value} "
                f"({llm_response.tokens_used} tokens, {llm_response.response_time:.2f}s)_"
            )

        return self._get_intelligent_simulation(message, user_name)

    def _get_intelligent_simulation(self, message: str, user_name: str) -> str:
        """Simulação baseada em padrões quando não há LLM disponível."""

        message_lower = message.lower()

        if any(word in message_lower for word in ["documento", "documentos", "tipo", "temos"]):
            return f"""🔍 **Consulta de Documentos - MIT Tracking**

Olá {user_name}! Como especialista em logística, posso te informar sobre os tipos de documentos disponíveis no sistema:

📋 **Documentos Logísticos Disponíveis:**
• **CT-e** - Conhecimento de Transporte Eletrônico (transporte rodoviário)
• **BL** - Bill of Lading (conhecimento de embarque marítimo)
• **AWL** - Air Waybill (conhecimento aéreo)
• **Manifesto** - Manifesto de Carga
• **NF-e** - Nota Fiscal Eletrônica

🚛 **Funcionalidades do Sistema:**
• Busca semântica por documentos
• Rastreamento de containers em tempo real
• Análise de compliance regulatório
• Estatísticas operacionais
• ETA/ETD - previsões de chegada e saída

💡 **Para consultas específicas:**
• "Mostre CT-es da última semana"
• "Status do container ABCD1234"
• "Documentos da empresa XYZ"

Como posso ajudar com algum documento específico?"""

        if any(word in message_lower for word in ["rastreamento", "tracking", "container", "carga"]):
            return f"""📦 **Rastreamento de Cargas - MIT Tracking**

{user_name}, nosso sistema oferece rastreamento completo:

🚛 **Rastreamento Disponível:**
• Containers marítimos com posição GPS
• Cargas rodoviárias com CT-e
• Embarques aéreos com AWL
• Status em tempo real

📍 **Informações de Tracking:**
• Localização atual
• ETA (Estimated Time of Arrival)
• ETD (Estimated Time of Departure)
• Eventos da rota
• Status de entrega

💡 **Como consultar:**
• "Status do container MSKU1234567"
• "Rastreamento da carga ABC123"
• "Onde está meu embarque?"

Qual carga gostaria de rastrear?"""

        if any(word in message_lower for word in ["boa noite", "boa tarde", "bom dia", "olá", "oi"]):
            hora = datetime.now().hour
            saudacao = "Boa noite" if hora >= 18 else "Boa tarde" if hora >= 12 else "Bom dia"

            return f"""🤖 **{saudacao}, {user_name}!**

Sou seu assistente especialista em logística do MIT Tracking.

🚛 **Posso ajudar com:**
• Consulta de documentos (CT-e, BL, AWL, Manifestos)
• Rastreamento de containers e cargas
• Status de entregas e previsões
• Análise de documentação logística
• Relatórios operacionais

📋 **Documentos mais consultados:**
• CT-e para transporte rodoviário
• BL para embarques marítimos
• Manifestos de carga
• Notas fiscais vinculadas

💡 **Exemplos de consultas:**
• "Que documentos temos hoje?"
• "Status do container XYZ123"
• "CT-es em trânsito"
• "Embarques para São Paulo"

Em que posso ajudá-lo hoje?"""

        return f"""🤖 **Assistente Logístico MIT Tracking**

{user_name}, analisei sua consulta: "{message}"

🚛 **Sistema MIT Tracking - Capacidades:**

📋 **Documentos Suportados:**
• CT-e (Conhecimento de Transporte Eletrônico)
• BL (Bill of Lading) - embarques marítimos
• AWL (Air Waybill) - cargas aéreas
• Manifestos de transporte
• NF-e vinculadas aos embarques

🔍 **Funcionalidades:**
• Busca semântica inteligente
• Rastreamento GPS em tempo real
• Análise de compliance
• Estatísticas operacionais
• Previsões ETA/ETD

💡 **Para consultas mais específicas:**
• Use termos como "CT-e", "container", "embarque"
• Informe números de documentos para busca direta
• Solicite relatórios por período ou cliente

Como posso reformular minha resposta para melhor atendê-lo?"""


async def route_to_direct_agent(
    agent_name: str,
    user_context: Dict[str, Any],
    request_data: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Roteia requisições para o DirectLogisticsAgent."""

    if request_data is None:
        request_data = {"message": "Requisição geral"}

    message = request_data.get("message", "")

    agent = DirectLogisticsAgent()
    result = await agent.process_message(message, user_context)
    return result


async def test_agent() -> Dict[str, Any]:
    """Teste manual do agente direto."""

    user_context = {
        "userId": "admin_001",
        "name": "Administrador Sistema",
        "role": "admin",
    }

    test_message = "boa noite. que tipo de documentos temos no sistema hoje?"

    result = await route_to_direct_agent(
        "LogisticsAgent",
        user_context,
        {"message": test_message},
    )

    print("\n=== RESULTADO DO TESTE ===")
    print(f"Status: {result.get('status')}")
    print(f"LLM Provider: {result.get('llm_provider')}")
    print(f"Response: {result.get('response', 'N/A')[:300]}...")

    return result


if __name__ == "__main__":
    asyncio.run(test_agent())
