#!/usr/bin/env python3
"""
MIT Logistics - Teste do Chat com Agente v2
Testa a integração completa do chat com OpenAI/Gemini
"""

import asyncio
import sys
import os
sys.path.append('./python-crewai')

async def test_chat():
    print("🧪 MIT Logistics - Teste do Chat Agent v2")
    print("=" * 50)
    
    try:
        # Import do agente v2
        from agents.mit_tracking_agent_v2 import MITTrackingAgentV2
        from llm_router import LLMProvider
        
        print("✅ Módulos importados com sucesso")
        
        # Criar agente
        print("\n🤖 Criando MIT Tracking Agent v2...")
        agent = MITTrackingAgentV2()
        
        if not agent.is_ready:
            print("❌ Agente não está pronto")
            return False
        
        print(f"✅ Agente criado: {agent.get_session_id()}")
        
        # Teste de consultas
        test_queries = [
            "Olá! Como você funciona?",
            "Onde está o CT-e 351234567890123456789012345678901234?",
            "Status do container ABCD1234567",
            "Qual a previsão de entrega?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Teste {i}: {query}")
            print("-" * 30)
            
            try:
                response = await agent.consultar_logistica(query)
                print(f"✅ Resposta recebida:")
                print(f"   {response[:100]}...")
                
                # Verificar se a resposta contém metadados de provider
                if "🧠 _Processado via" in response:
                    print("✅ Metadados de LLM detectados")
                
            except Exception as e:
                print(f"❌ Erro na consulta: {e}")
                return False
        
        # Testar estatísticas
        print(f"\n📊 Estatísticas do Agente:")
        stats = agent.get_stats()
        print(f"   • Total de consultas: {stats.total_queries}")
        print(f"   • Sucessos: {stats.successful_queries}")
        print(f"   • Erros: {stats.error_count}")
        print(f"   • Tempo médio: {stats.average_response_time:.2f}s")
        
        # Testar estatísticas do LLM
        try:
            llm_stats = agent.get_llm_stats()
            print(f"\n🧠 Estatísticas LLM:")
            if llm_stats.get('usage', {}).get('request_counts'):
                for provider, count in llm_stats['usage']['request_counts'].items():
                    print(f"   • {provider}: {count} requests")
        except Exception as e:
            print(f"⚠️  Estatísticas LLM não disponíveis: {e}")
        
        print(f"\n🎉 Teste concluído com sucesso!")
        print(f"📋 Session ID: {agent.get_session_id()}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Verifique se o python-crewai está configurado corretamente")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

async def test_graphql_endpoint():
    """Testa o endpoint GraphQL"""
    print("\n🌐 Testando endpoint GraphQL...")
    
    try:
        import aiohttp
        
        query = """
        query TestConnection {
          chatTestConnection
          hello
        }
        """
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:8001/graphql',
                json={'query': query},
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ GraphQL endpoint respondendo")
                    print(f"   Hello: {data.get('data', {}).get('hello', 'N/A')}")
                    print(f"   Chat Connection: {data.get('data', {}).get('chatTestConnection', 'N/A')}")
                    return True
                else:
                    print(f"❌ GraphQL endpoint erro: {response.status}")
                    return False
                    
    except ImportError:
        print("⚠️  aiohttp não disponível, pulando teste GraphQL")
        return True
    except Exception as e:
        print(f"❌ Erro no teste GraphQL: {e}")
        return False

if __name__ == "__main__":
    async def main():
        success1 = await test_chat()
        success2 = await test_graphql_endpoint()
        
        if success1 and success2:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("\n🚀 Sistema pronto para uso:")
            print("   • Frontend: http://localhost:3001/agents")
            print("   • Chat disponível na página de agentes")
            print("   • API GraphQL: http://localhost:8001/graphql")
            sys.exit(0)
        else:
            print("\n❌ ALGUNS TESTES FALHARAM")
            print("   Verifique as configurações e tente novamente")
            sys.exit(1)
    
    asyncio.run(main())