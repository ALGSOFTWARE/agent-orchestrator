#!/usr/bin/env python3
"""
Demo do Gatekeeper Agent - Sistema de Logística Inteligente

Este script demonstra como interagir com o Gatekeeper Agent,
simulando requisições de uma API de autenticação externa.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Configuração do servidor
GATEKEEPER_URL = "http://localhost:8001"

class GatekeeperDemo:
    """Demonstração das funcionalidades do Gatekeeper Agent"""
    
    def __init__(self, base_url: str = GATEKEEPER_URL):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_health(self) -> Dict[str, Any]:
        """Verifica se o Gatekeeper está funcionando"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Health check failed: {response.status}"}
        except Exception as e:
            return {"error": f"Connection failed: {str(e)}"}
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Obtém informações do sistema"""
        try:
            async with self.session.get(f"{self.base_url}/info") as response:
                return await response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def list_roles(self) -> Dict[str, Any]:
        """Lista roles disponíveis"""
        try:
            async with self.session.get(f"{self.base_url}/roles") as response:
                return await response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def simulate_auth_callback(self, user_id: str, role: str, permissions: list = None) -> Dict[str, Any]:
        """Simula callback da API de autenticação externa"""
        payload = {
            "userId": user_id,
            "role": role,
            "permissions": permissions or [],
            "sessionId": f"session_{user_id}_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth-callback",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                result["http_status"] = response.status
                return result
        except Exception as e:
            return {"error": str(e)}
    
    def print_section(self, title: str):
        """Imprime seção formatada"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_result(self, title: str, result: Dict[str, Any]):
        """Imprime resultado formatado"""
        print(f"\n{title}:")
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

async def main():
    """Função principal da demonstração"""
    print("🤖 DEMO: Gatekeeper Agent - Sistema de Logística Inteligente")
    print("🔗 Conectando ao Gatekeeper em:", GATEKEEPER_URL)
    
    async with GatekeeperDemo() as demo:
        
        # 1. Verificar saúde do sistema
        demo.print_section("1. HEALTH CHECK")
        health = await demo.check_health()
        demo.print_result("Status do Gatekeeper", health)
        
        if "error" in health:
            print("\n❌ ERRO: Gatekeeper não está acessível!")
            print("📋 Certifique-se de que o servidor está rodando:")
            print("   python gatekeeper_agent.py")
            return
        
        # 2. Obter informações do sistema
        demo.print_section("2. INFORMAÇÕES DO SISTEMA")
        info = await demo.get_system_info()
        demo.print_result("Informações do Sistema", info)
        
        # 3. Listar roles disponíveis
        demo.print_section("3. ROLES DISPONÍVEIS")
        roles = await demo.list_roles()
        demo.print_result("Roles e Permissões", roles)
        
        # 4. Testar autenticação válida - Admin
        demo.print_section("4. TESTE: AUTENTICAÇÃO ADMIN")
        admin_result = await demo.simulate_auth_callback(
            user_id="admin_001",
            role="admin",
            permissions=["read:all", "write:all"]
        )
        demo.print_result("Resultado Admin", admin_result)
        
        # 5. Testar autenticação válida - Logistics
        demo.print_section("5. TESTE: AUTENTICAÇÃO LOGISTICS")
        logistics_result = await demo.simulate_auth_callback(
            user_id="logistics_002",
            role="logistics",
            permissions=["read:cte", "write:document", "read:container"]
        )
        demo.print_result("Resultado Logistics", logistics_result)
        
        # 6. Testar autenticação válida - Finance
        demo.print_section("6. TESTE: AUTENTICAÇÃO FINANCE")
        finance_result = await demo.simulate_auth_callback(
            user_id="finance_003",
            role="finance",
            permissions=["read:financial", "write:payment"]
        )
        demo.print_result("Resultado Finance", finance_result)
        
        # 7. Testar autenticação inválida - Role inexistente
        demo.print_section("7. TESTE: ROLE INVÁLIDO")
        invalid_result = await demo.simulate_auth_callback(
            user_id="invalid_004",
            role="invalid_role",
            permissions=[]
        )
        demo.print_result("Resultado Role Inválido", invalid_result)
        
        # 8. Testar permissões inválidas
        demo.print_section("8. TESTE: PERMISSÕES INVÁLIDAS")
        invalid_perms_result = await demo.simulate_auth_callback(
            user_id="operator_005",
            role="operator",
            permissions=["read:financial", "write:admin"]  # Permissões não permitidas para operator
        )
        demo.print_result("Resultado Permissões Inválidas", invalid_perms_result)
        
        # 9. Resumo dos testes
        demo.print_section("9. RESUMO DOS TESTES")
        
        test_results = [
            ("Admin", admin_result.get("http_status") == 200),
            ("Logistics", logistics_result.get("http_status") == 200),
            ("Finance", finance_result.get("http_status") == 200),
            ("Role Inválido", invalid_result.get("http_status") == 422),
            ("Permissões Inválidas", invalid_perms_result.get("http_status") == 403)
        ]
        
        print("\n📊 Resultados dos Testes:")
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        total_tests = len(test_results)
        passed_tests = sum(1 for _, success in test_results if success)
        
        print(f"\n📈 Total: {passed_tests}/{total_tests} testes passaram")
        
        if passed_tests == total_tests:
            print("🎉 Todos os testes passaram! Gatekeeper funcionando corretamente.")
        else:
            print("⚠️  Alguns testes falharam. Verifique a configuração.")

def print_usage():
    """Imprime instruções de uso"""
    print("🚀 COMO EXECUTAR ESTA DEMO:")
    print("\n1. Inicie o Gatekeeper Agent:")
    print("   cd python-crewai")
    print("   python gatekeeper_agent.py")
    print("\n2. Execute esta demo:")
    print("   python examples/gatekeeper_demo.py")
    print("\n3. O Gatekeeper deve estar rodando em http://localhost:8001")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print_usage()
        sys.exit(0)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro na execução da demo: {str(e)}")
        print("\n" + "="*60)
        print_usage()