#!/usr/bin/env python3
"""
Mock MIT Tracking Agent v2 - Para testes do frontend
Simula respostas do agente sem dependências externas
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any

class MockMITTrackingAgentV2:
    """Versão simulada do MIT Tracking Agent v2 para testes"""
    
    def __init__(self, preferred_provider: Optional[str] = None):
        self.preferred_provider = preferred_provider or "openai"
        self.is_ready = True
        
    async def consultar_logistica(self, message: str, context: Optional[Dict] = None) -> str:
        """Simula consulta logística com respostas pré-definidas"""
        
        # Simular tempo de processamento
        await asyncio.sleep(0.5)
        
        # Respostas baseadas em palavras-chave
        message_lower = message.lower()
        
        if "cte" in message_lower or "conhecimento" in message_lower:
            return self._generate_cte_response(message)
        elif "container" in message_lower or "rastreamento" in message_lower:
            return self._generate_container_response(message)
        elif "bl" in message_lower or "bill" in message_lower:
            return self._generate_bl_response(message)
        elif "status" in message_lower or "situação" in message_lower:
            return self._generate_status_response(message)
        elif "onde" in message_lower or "localização" in message_lower:
            return self._generate_location_response(message)
        else:
            return self._generate_general_response(message)
    
    def _generate_cte_response(self, message: str) -> str:
        """Resposta para consultas de CT-e"""
        return """📋 **Consulta CT-e - MIT Tracking Agent**

🔍 **Informações encontradas:**
• **CT-e:** 351234567890123456789012345678901234
• **Status:** EM_TRANSITO
• **Transportadora:** Rápido Transportes Ltda
• **Origem:** São Paulo/SP
• **Destino:** Rio de Janeiro/RJ
• **Valor do Frete:** R$ 1.250,00

📍 **Última posição:** Rodovia Presidente Dutra, km 285
⏰ **Previsão de entrega:** 2024-08-18 14:30

💡 *Esta é uma simulação do MIT Tracking Agent v2 para demonstração do sistema.*"""

    def _generate_container_response(self, message: str) -> str:
        """Resposta para consultas de container"""
        return """🚢 **Rastreamento de Container - MIT Tracking Agent**

📦 **Container:** ABCD1234567
• **Status:** NO_PORTO
• **Localização:** Porto de Santos/SP
• **Linha:** Maersk Line
• **Navio:** MSC DANIELA

🗓️ **Cronograma:**
• **Chegada ao porto:** 2024-08-15 08:00 ✅
• **Descarregamento:** 2024-08-17 10:00 🔄
• **Liberação prevista:** 2024-08-19 16:00

📊 **Documentos:** BL disponível, DI em processamento

💡 *Dados simulados para demonstração do sistema de tracking.*"""

    def _generate_bl_response(self, message: str) -> str:
        """Resposta para consultas de BL"""
        return """📄 **Bill of Lading (BL) - MIT Tracking Agent**

🆔 **BL:** MAEU987654321
• **Embarcador:** Tech Solutions Brasil Ltda
• **Consignatário:** Import Corp USA
• **Porto de Origem:** Santos/Brasil
• **Porto de Destino:** Long Beach/USA

📦 **Carga:** 
• **Descrição:** Componentes eletrônicos
• **Peso:** 15.5 toneladas
• **Volume:** 28 m³

🚢 **Transporte:**
• **Navio:** Ever Given
• **Viagem:** EG0234
• **ETA Long Beach:** 2024-08-25

💡 *Informações simuladas do sistema MIT Tracking.*"""

    def _generate_status_response(self, message: str) -> str:
        """Resposta para consultas de status"""
        return """📊 **Status do Sistema - MIT Tracking Agent**

✅ **Serviços Ativos:**
• Rastreamento CT-e: Online
• Tracking de Containers: Online  
• Consulta BL: Online
• GPS em tempo real: Online

📈 **Estatísticas:**
• CT-es monitorados: 1.247
• Containers ativos: 89
• BLs processados hoje: 34
• Entregas concluídas: 156

⚡ **Performance:**
• Tempo de resposta médio: 0.3s
• Uptime: 99.8%
• Última atualização: 2024-08-17 03:15

💡 *Dashboard do MIT Tracking Agent v2.*"""

    def _generate_location_response(self, message: str) -> str:
        """Resposta para consultas de localização"""
        return """📍 **Localização - MIT Tracking Agent**

🚛 **Cargas em Trânsito:**

**CT-e 35123...1234:**
• 📍 Rodovia BR-116, km 125 (Região de Campinas/SP)
• ⏰ Última atualização: 14:32
• 🎯 Destino: Rio de Janeiro/RJ
• ⏱️ Previsão: 4h 20min

**Container ABCD1234567:**
• 📍 Porto de Santos - Pátio 3, Área B12
• 🚢 Aguardando embarque no MSC MAYA
• 📅 Sailing: 2024-08-18 23:00

🗺️ **Tracking em tempo real ativo para 23 cargas**

💡 *Posições atualizadas via GPS a cada 15 minutos.*"""

    def _generate_general_response(self, message: str) -> str:
        """Resposta geral para outras consultas"""
        return f"""🤖 **MIT Tracking Agent v2** - Sistema de Logística Inteligente

Olá! Sou especializado em consultas logísticas. Posso ajudar com:

📋 **CT-e (Conhecimento de Transporte Eletrônico)**
• Consulta por número
• Status e rastreamento  
• Informações de frete

📦 **Containers**
• Tracking marítimo
• Posição em tempo real
• Cronogramas de chegada

📄 **BL (Bill of Lading)**
• Consulta de conhecimentos
• Status de documentação
• Informações de carga

**Sua mensagem:** "{message}"

💡 *Digite sua consulta específica ou número de documento para obter informações detalhadas.*

---
*🔧 Esta é uma simulação para demonstração do sistema. Em produção, conectaria com OpenAI/Gemini.*"""

    async def shutdown(self):
        """Cleanup quando necessário"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do agente simulado"""
        return {
            "provider": self.preferred_provider,
            "status": "ready",
            "requests_processed": 42,
            "avg_response_time": 0.5,
            "mode": "simulation"
        }

# Função auxiliar para compatibilidade
def create_mock_agent(preferred_provider: Optional[str] = None) -> MockMITTrackingAgentV2:
    """Cria instância do agente simulado"""
    return MockMITTrackingAgentV2(preferred_provider)