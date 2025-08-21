#!/usr/bin/env python3
"""
Test Script para Gatekeeper API

Script para testar as funcionalidades principais do Gatekeeper API:
- Authentication flow
- User management  
- Context management
- Integration com CrewAI

Usage:
    python test_gatekeeper.py
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any

# Configuração
GATEKEEPER_URL = "http://localhost:8001"
CREWAI_URL = "http://localhost:8000"

class GatekeeperTester:
    """Classe para tester o Gatekeeper API"""
    
    def __init__(self):
        self.base_url = GATEKEEPER_URL
        self.test_results = []
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🧪 Iniciando testes do Gatekeeper API...")
        print(f"🔗 URL: {self.base_url}")
        print("=" * 50)
        
        # Testes básicos
        await self.test_health_check()
        await self.test_system_info()
        
        # Testes de autenticação
        await self.test_auth_callback_admin()
        await self.test_auth_callback_logistics()
        await self.test_auth_callback_finance()
        await self.test_auth_roles()
        
        # Testes de usuários
        await self.test_user_creation()
        await self.test_user_stats()
        
        # Testes de contexto
        await self.test_context_addition()
        await self.test_context_retrieval()
        
        # Relatório final
        self.print_summary()
    
    async def test_health_check(self):
        """Testa health check"""
        print("🏥 Testando health check...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Health check OK - Status: {data.get('status')}")
                    self.test_results.append(("Health Check", True, "OK"))
                else:
                    print(f"❌ Health check failed - Status: {response.status_code}")
                    self.test_results.append(("Health Check", False, f"Status {response.status_code}"))
                    
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            self.test_results.append(("Health Check", False, str(e)))
    
    async def test_system_info(self):
        """Testa informações do sistema"""
        print("ℹ️  Testando system info...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/info")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ System info OK - Service: {data.get('service')}")
                    print(f"   Version: {data.get('version')}")
                    self.test_results.append(("System Info", True, "OK"))
                else:
                    print(f"❌ System info failed - Status: {response.status_code}")
                    self.test_results.append(("System Info", False, f"Status {response.status_code}"))
                    
        except Exception as e:
            print(f"❌ System info error: {str(e)}")
            self.test_results.append(("System Info", False, str(e)))
    
    async def test_auth_callback_admin(self):
        """Testa autenticação com role admin"""
        print("🔐 Testando autenticação - Role Admin...")
        
        payload = {
            "userId": "admin@test.com",
            "role": "admin",
            "permissions": ["*"],
            "sessionId": f"session_admin_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat()
        }
        
        await self._test_auth_callback("Admin Auth", payload)
    
    async def test_auth_callback_logistics(self):
        """Testa autenticação com role logistics"""
        print("🚚 Testando autenticação - Role Logistics...")
        
        payload = {
            "userId": "logistics@test.com",
            "role": "logistics",
            "permissions": ["read:cte", "write:document", "read:container"],
            "sessionId": f"session_logistics_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat()
        }
        
        await self._test_auth_callback("Logistics Auth", payload)
    
    async def test_auth_callback_finance(self):
        """Testa autenticação com role finance"""
        print("💰 Testando autenticação - Role Finance...")
        
        payload = {
            "userId": "finance@test.com",
            "role": "finance",
            "permissions": ["read:financial", "write:financial"],
            "sessionId": f"session_finance_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat()
        }
        
        await self._test_auth_callback("Finance Auth", payload)
    
    async def _test_auth_callback(self, test_name: str, payload: Dict[str, Any]):
        """Método auxiliar para testar auth callback"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/auth/callback",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {test_name} OK - Agent: {data.get('agent')}")
                    print(f"   User: {data.get('userId')}")
                    print(f"   Message: {data.get('message')}")
                    self.test_results.append((test_name, True, "OK"))
                else:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                    print(f"❌ {test_name} failed - Status: {response.status_code}")
                    print(f"   Error: {error_data}")
                    self.test_results.append((test_name, False, f"Status {response.status_code}"))
                    
        except Exception as e:
            print(f"❌ {test_name} error: {str(e)}")
            self.test_results.append((test_name, False, str(e)))
    
    async def test_auth_roles(self):
        """Testa endpoint de roles"""
        print("👥 Testando roles disponíveis...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/auth/roles")
                
                if response.status_code == 200:
                    data = response.json()
                    roles = data.get("available_roles", [])
                    print(f"✅ Roles OK - Disponíveis: {roles}")
                    self.test_results.append(("Auth Roles", True, "OK"))
                else:
                    print(f"❌ Roles failed - Status: {response.status_code}")
                    self.test_results.append(("Auth Roles", False, f"Status {response.status_code}"))
                    
        except Exception as e:
            print(f"❌ Roles error: {str(e)}")
            self.test_results.append(("Auth Roles", False, str(e)))
    
    async def test_user_creation(self):
        """Testa criação de usuário (simulado - precisa de admin auth)"""
        print("👤 Testando informações de usuário...")
        
        try:
            # Testar get user me (simulado)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/me",
                    params={"user_id": "admin@test.com"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ User info OK - Name: {data.get('name')}")
                    self.test_results.append(("User Info", True, "OK"))
                elif response.status_code == 404:
                    print("ℹ️  Usuário não encontrado (esperado na primeira execução)")
                    self.test_results.append(("User Info", True, "User not found (expected)"))
                else:
                    print(f"❌ User info failed - Status: {response.status_code}")
                    self.test_results.append(("User Info", False, f"Status {response.status_code}"))
                    
        except Exception as e:
            print(f"❌ User info error: {str(e)}")
            self.test_results.append(("User Info", False, str(e)))
    
    async def test_user_stats(self):
        """Testa estatísticas de usuários"""
        print("📊 Testando estatísticas de usuários...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/stats/summary",
                    params={"current_user_role": "admin"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ User stats OK - Total users: {data.get('total_users')}")
                    self.test_results.append(("User Stats", True, "OK"))
                else:
                    print(f"❌ User stats failed - Status: {response.status_code}")
                    self.test_results.append(("User Stats", False, f"Status {response.status_code}"))
                    
        except Exception as e:
            print(f"❌ User stats error: {str(e)}")
            self.test_results.append(("User Stats", False, str(e)))
    
    async def test_context_addition(self):
        """Testa adição de contexto"""
        print("📝 Testando adição de contexto...")
        
        payload = {
            "input": "Teste de entrada de contexto",
            "output": "Resposta de teste do sistema",
            "agents_involved": ["LogisticsAgent"],
            "session_id": f"test_session_{datetime.now().timestamp()}",
            "metadata": {"test": True, "timestamp": datetime.now().isoformat()}
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/context/admin@test.com",
                    json=payload,
                    params={
                        "current_user_id": "admin@test.com",
                        "current_user_role": "admin"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Context addition OK - ID: {data.get('context', {}).get('id')}")
                    self.test_results.append(("Context Addition", True, "OK"))
                else:
                    print(f"❌ Context addition failed - Status: {response.status_code}")
                    self.test_results.append(("Context Addition", False, f"Status {response.status_code}"))
                    
        except Exception as e:
            print(f"❌ Context addition error: {str(e)}")
            self.test_results.append(("Context Addition", False, str(e)))
    
    async def test_context_retrieval(self):
        """Testa recuperação de contexto"""
        print("📖 Testando recuperação de contexto...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/context/admin@test.com",
                    params={
                        "current_user_id": "admin@test.com",
                        "current_user_role": "admin",
                        "limit": 10
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    contexts = data.get("contexts", [])
                    print(f"✅ Context retrieval OK - Found {len(contexts)} contexts")
                    self.test_results.append(("Context Retrieval", True, "OK"))
                else:
                    print(f"❌ Context retrieval failed - Status: {response.status_code}")
                    self.test_results.append(("Context Retrieval", False, f"Status {response.status_code}"))
                    
        except Exception as e:
            print(f"❌ Context retrieval error: {str(e)}")
            self.test_results.append(("Context Retrieval", False, str(e)))
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "=" * 50)
        print("📋 RESUMO DOS TESTES")
        print("=" * 50)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"✅ Testes aprovados: {passed}/{total}")
        print(f"❌ Testes falharam: {total - passed}/{total}")
        print(f"📊 Taxa de sucesso: {(passed/total)*100:.1f}%")
        
        print("\nDetalhes:")
        for test_name, success, details in self.test_results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}: {details}")
        
        if passed == total:
            print("\n🎉 Todos os testes passaram! Gatekeeper API está funcionando corretamente.")
        else:
            print(f"\n⚠️  {total - passed} teste(s) falharam. Verifique os serviços:")
            print("   - MongoDB está rodando?")
            print("   - CrewAI API está rodando na porta 8000?")
            print("   - Gatekeeper API está rodando na porta 8001?")


async def main():
    """Função principal"""
    tester = GatekeeperTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())