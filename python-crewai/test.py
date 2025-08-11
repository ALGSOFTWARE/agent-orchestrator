"""
Teste básico para verificar se a migração funcionou
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_basic_functionality():
    """Teste básico de funcionalidade"""
    
    print("🧪 Testando migração TypeScript -> Python...")
    
    try:
        # Test imports
        print("📦 Testando imports...")
        from agents.mit_tracking_agent import MITTrackingAgent
        from models import OllamaConfig, LogisticsQuery, QueryType
        print("✅ Imports OK")
        
        # Test agent creation
        print("🤖 Criando agente...")
        config = OllamaConfig(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            temperature=0.3
        )
        
        agent = MITTrackingAgent(config)
        print("✅ Agente criado")
        
        # Test basic query
        print("💬 Testando consulta básica...")
        test_query = "Qual é o status do CT-e 35123456789012345678901234567890123456?"
        
        query = LogisticsQuery(
            content=test_query,
            query_type=QueryType.CTE,
            session_id=agent.get_session_id()
        )
        
        response = await agent.process_logistics_query(query)
        print(f"✅ Resposta recebida: {len(response.content)} caracteres")
        
        # Show stats
        print("\n📊 Estatísticas finais:")
        stats = agent.get_stats()
        print(f"   • Total queries: {stats.total_queries}")
        print(f"   • Success rate: {agent.success_rate:.1f}%")
        
        # Cleanup
        await agent.shutdown()
        
        print("\n🎉 Migração testada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)