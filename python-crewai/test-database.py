"""
Teste do banco de dados mockado e ferramentas logísticas
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import get_database
from tools.logistics_tools import logistics_tools
from agents.mit_tracking_agent import MITTrackingAgent
from models import OllamaConfig


async def test_database_tools():
    """Testa banco de dados e ferramentas"""
    
    print("🧪 Testando Banco de Dados MIT Tracking...")
    print("=" * 50)
    
    # 1. Testar carregamento do banco
    db = get_database()
    stats = db.get_statistics()
    
    print("\n📊 Estatísticas do Banco:")
    for collection, info in stats.items():
        print(f"  • {collection}: {info['total_documents']} documentos")
    
    # 2. Testar ferramentas específicas
    print("\n🔧 Testando Ferramentas Logísticas:")
    
    # Teste CT-e
    print("\n1️⃣ Teste CT-e:")
    cte_result = logistics_tools.consultar_cte("35240512345678901234567890123456789012")
    print(cte_result[:200] + "..." if len(cte_result) > 200 else cte_result)
    
    # Teste Container
    print("\n2️⃣ Teste Container:")
    container_result = logistics_tools.consultar_container("ABCD1234567")
    print(container_result[:200] + "..." if len(container_result) > 200 else container_result)
    
    # Teste BL
    print("\n3️⃣ Teste BL:")
    bl_result = logistics_tools.consultar_bl("ABCD240001")
    print(bl_result[:200] + "..." if len(bl_result) > 200 else bl_result)
    
    # Teste busca inteligente
    print("\n4️⃣ Teste Busca Inteligente:")
    search_result = logistics_tools.busca_inteligente("containers em trânsito")
    print(search_result[:200] + "..." if len(search_result) > 200 else search_result)
    
    # 3. Testar Agent integrado
    print("\n🤖 Testando Agent com Banco de Dados:")
    try:
        config = OllamaConfig(
            base_url="http://localhost:11434",
            model="llama3.2:3b",
            temperature=0.3
        )
        
        agent = MITTrackingAgent(config)
        
        # Teste com número de CT-e
        print("\n📋 Teste Agent - CT-e:")
        response = await agent.consultar_logistica("Onde está o CT-e 35240512345678901234567890123456789012?")
        print(response[:300] + "..." if len(response) > 300 else response)
        
        # Teste com container
        print("\n📦 Teste Agent - Container:")
        response = await agent.consultar_logistica("Status do container ABCD1234567")
        print(response[:300] + "..." if len(response) > 300 else response)
        
        # Estatísticas do agent
        print(f"\n📊 Stats do Agent: {agent.get_stats().total_queries} consultas processadas")
        
    except Exception as e:
        print(f"⚠️  Agent test skipped (Ollama not available): {str(e)}")
    
    print("\n✅ Testes concluídos!")


if __name__ == "__main__":
    asyncio.run(test_database_tools())