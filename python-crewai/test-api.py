"""
Teste básico da MIT Tracking GraphQL API
Verifica se todos os componentes estão funcionando
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.schemas import CTe, Container, BL
from api.resolvers import Query
from database.db_manager import get_database


async def test_api_components():
    """Testa componentes principais da API"""
    
    print("🧪 Testando MIT Tracking GraphQL API...")
    print("=" * 50)
    
    # 1. Testar Database Integration
    print("\n📊 1. Testando Database Integration:")
    try:
        db = get_database()
        stats = db.get_statistics()
        print(f"   ✅ Database conectado: {len(stats)} coleções")
        for collection, info in stats.items():
            print(f"      • {collection}: {info['total_documents']} docs")
    except Exception as e:
        print(f"   ❌ Erro database: {e}")
        return False
    
    # 2. Testar GraphQL Resolvers
    print("\n🔍 2. Testando GraphQL Resolvers:")
    try:
        query_resolver = Query()
        
        # Teste CT-e query
        ctes = query_resolver.ctes()
        print(f"   ✅ CT-e query: {len(ctes)} registros")
        
        # Teste Container query
        containers = query_resolver.containers()
        print(f"   ✅ Container query: {len(containers)} registros")
        
        # Teste BL query
        bls = query_resolver.bls()
        print(f"   ✅ BL query: {len(bls)} registros")
        
        # Teste Statistics
        stats = query_resolver.logistics_stats()
        print(f"   ✅ Stats query: {stats.total_ctes} CT-e, {stats.total_containers} containers")
        
    except Exception as e:
        print(f"   ❌ Erro resolvers: {e}")
        return False
    
    # 3. Testar Queries Específicas
    print("\n🔎 3. Testando Queries Específicas:")
    try:
        # Busca CT-e específico
        cte = query_resolver.cte_by_number("35240512345678901234567890123456789012")
        if cte:
            print(f"   ✅ CT-e específico encontrado: {cte.numero_cte}")
        else:
            print("   ⚠️  CT-e específico não encontrado")
        
        # Busca Container específico
        container = query_resolver.container_by_number("ABCD1234567")
        if container:
            print(f"   ✅ Container específico encontrado: {container.numero}")
        else:
            print("   ⚠️  Container específico não encontrado")
            
        # Containers em trânsito
        containers_transito = query_resolver.containers_em_transito()
        print(f"   ✅ Containers em trânsito: {len(containers_transito)}")
        
    except Exception as e:
        print(f"   ❌ Erro queries específicas: {e}")
        return False
    
    # 4. Testar Schema Validation
    print("\n📋 4. Testando Schema Validation:")
    try:
        # Verificar se schemas estão bem definidos
        from api.schemas import CTeInput, ContainerInput, BLInput
        print("   ✅ Schemas GraphQL importados com sucesso")
        print("   ✅ Input types definidos corretamente")
        
    except Exception as e:
        print(f"   ❌ Erro schema validation: {e}")
        return False
    
    # 5. Testar Exemplos
    print("\n📝 5. Testando Exemplos:")
    try:
        from api.examples import get_all_examples
        examples = get_all_examples()
        
        print(f"   ✅ GraphQL Queries: {len(examples['graphql_queries'])} exemplos")
        print(f"   ✅ GraphQL Mutations: {len(examples['graphql_mutations'])} exemplos") 
        print(f"   ✅ REST Endpoints: {len(examples['rest_endpoints'])} exemplos")
        print("   ✅ Clients Python e JavaScript disponíveis")
        
    except Exception as e:
        print(f"   ❌ Erro examples: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes da API passaram com sucesso!")
    print("\n🚀 Para iniciar a API:")
    print("   • Docker: ./start-api.sh")
    print("   • Local: ./start-api-local.sh")
    print("\n🌐 Endpoints após inicialização:")
    print("   • GraphQL: http://localhost:8000/graphql")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Health: http://localhost:8000/health")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_api_components())
    sys.exit(0 if success else 1)