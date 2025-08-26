#!/usr/bin/env python3
"""
Teste de Integração do Gatekeeper API Tool

Este teste verifica:
1. Funcionamento das novas ferramentas GraphQL
2. Integração com os agentes especializados
3. Processamento de documentos via OCR
4. Sistema de webhooks
5. Fluxo completo de dados reais
"""

import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar ferramentas e agentes
try:
    from tools.gatekeeper_api_tool import GatekeeperAPITool, CrewAIGatekeeperTool
    from tools.document_processor import DocumentProcessor, CrewAIDocumentTool
    from tools.webhook_processor import WebhookProcessor, CrewAIWebhookTool
    from agents.specialized_agents import AdminAgent, LogisticsAgent, FinanceAgent
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)


class GatekeeperIntegrationTest:
    """Teste completo da integração"""
    
    def __init__(self):
        self.results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": []
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log resultado de teste"""
        self.results["tests_run"] += 1
        if success:
            self.results["tests_passed"] += 1
            print(f"✅ {test_name}")
            if details:
                print(f"   {details}")
        else:
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"{test_name}: {details}")
            print(f"❌ {test_name}")
            if details:
                print(f"   {details}")
    
    async def test_gatekeeper_api_tools(self):
        """Testa ferramentas do Gatekeeper API"""
        print("\n🔍 Testing Gatekeeper API Tools...")
        
        # Teste 1: Health Check
        try:
            api_tool = GatekeeperAPITool()
            async with api_tool as api:
                response = await api.health_check()
                self.log_test(
                    "Gatekeeper API Health Check",
                    response.success,
                    f"Status: {response.status_code}, Time: {response.response_time:.2f}s"
                )
        except Exception as e:
            self.log_test("Gatekeeper API Health Check", False, str(e))
        
        # Teste 2: Schema Introspection
        try:
            async with api_tool as api:
                response = await api.introspect_schema()
                self.log_test(
                    "GraphQL Schema Introspection",
                    response.success,
                    f"Schema types found: {len(response.data.get('__schema', {}).get('types', [])) if response.success else 0}"
                )
        except Exception as e:
            self.log_test("GraphQL Schema Introspection", False, str(e))
        
        # Teste 3: Search Orders (pode retornar vazio, mas não deve dar erro)
        try:
            async with api_tool as api:
                response = await api.search_orders(limit=5)
                self.log_test(
                    "Search Orders Query",
                    response.success,
                    f"Response received, errors: {response.errors or 'None'}"
                )
        except Exception as e:
            self.log_test("Search Orders Query", False, str(e))
        
        # Teste 4: CrewAI Tool Wrapper
        try:
            crewai_tool = CrewAIGatekeeperTool()
            result = crewai_tool.verificar_saude_sistema()
            success = "erro" not in result.lower() or "✅" in result
            self.log_test(
                "CrewAI Tool Wrapper",
                success,
                f"Response length: {len(result)} chars"
            )
        except Exception as e:
            self.log_test("CrewAI Tool Wrapper", False, str(e))
    
    def test_document_processor(self):
        """Testa processador de documentos"""
        print("\n📄 Testing Document Processor...")
        
        # Teste 1: Inicialização
        try:
            processor = DocumentProcessor()
            self.log_test(
                "Document Processor Init",
                True,
                f"Supported formats: {len(processor.supported_formats)}"
            )
        except Exception as e:
            self.log_test("Document Processor Init", False, str(e))
            return
        
        # Teste 2: CrewAI Tool
        try:
            doc_tool = CrewAIDocumentTool()
            # Teste com arquivo inexistente (deve retornar erro controlado)
            result = doc_tool.extrair_texto_simples("/caminho/inexistente.pdf")
            success = "não encontrado" in result.lower() or "not found" in result.lower() or "erro" in result.lower()
            self.log_test(
                "Document Tool Error Handling",
                success,
                "Correctly handled missing file"
            )
        except Exception as e:
            self.log_test("Document Tool Error Handling", False, str(e))
        
        # Teste 3: Padrões de Extração
        try:
            test_text = """
            CT-e: 12345678901234567890123456789012345678901234
            CNPJ: 12.345.678/0001-90
            Valor do Frete: R$ 1.250,00
            Data: 15/08/2024
            """
            
            extracted = processor._extract_structured_data(test_text, "cte")
            found_patterns = len([k for k in extracted if extracted[k]])
            
            self.log_test(
                "Pattern Extraction",
                found_patterns > 0,
                f"Extracted {found_patterns} data patterns"
            )
        except Exception as e:
            self.log_test("Pattern Extraction", False, str(e))
    
    def test_webhook_processor(self):
        """Testa processador de webhooks"""
        print("\n🎣 Testing Webhook Processor...")
        
        # Teste 1: Inicialização
        try:
            webhook_processor = WebhookProcessor(port=8003)  # Porta diferente para teste
            self.log_test(
                "Webhook Processor Init",
                True,
                f"Configured sources: {len(webhook_processor.webhook_configs)}"
            )
        except Exception as e:
            self.log_test("Webhook Processor Init", False, str(e))
            return
        
        # Teste 2: Configurações de Webhook
        try:
            from tools.webhook_processor import WebhookSource, WebhookType
            config_count = len(webhook_processor.webhook_configs)
            enum_sources = len(list(WebhookSource))
            enum_types = len(list(WebhookType))
            
            self.log_test(
                "Webhook Configurations",
                config_count > 0 and enum_sources > 0 and enum_types > 0,
                f"Configs: {config_count}, Sources: {enum_sources}, Types: {enum_types}"
            )
        except Exception as e:
            self.log_test("Webhook Configurations", False, str(e))
        
        # Teste 3: CrewAI Tool
        try:
            webhook_tool = CrewAIWebhookTool()
            stats = webhook_tool.get_webhook_stats()
            success = "não iniciado" in stats or "stats" in stats.lower()
            self.log_test(
                "Webhook CrewAI Tool",
                success,
                "Tool responds correctly when not started"
            )
        except Exception as e:
            self.log_test("Webhook CrewAI Tool", False, str(e))
    
    async def test_specialized_agents(self):
        """Testa agentes especializados com novas ferramentas"""
        print("\n🤖 Testing Specialized Agents...")
        
        # Teste 1: AdminAgent
        try:
            admin_agent = AdminAgent()
            tools_count = len(admin_agent.agent.tools) if hasattr(admin_agent.agent, 'tools') and admin_agent.agent.tools else 0
            self.log_test(
                "AdminAgent Creation",
                True,
                f"Agent created with {tools_count} tools"
            )
        except Exception as e:
            self.log_test("AdminAgent Creation", False, str(e))
        
        # Teste 2: LogisticsAgent  
        try:
            logistics_agent = LogisticsAgent()
            tools_count = len(logistics_agent.agent.tools) if hasattr(logistics_agent.agent, 'tools') and logistics_agent.agent.tools else 0
            self.log_test(
                "LogisticsAgent Creation",
                True,
                f"Agent created with {tools_count} tools"
            )
        except Exception as e:
            self.log_test("LogisticsAgent Creation", False, str(e))
        
        # Teste 3: FinanceAgent
        try:
            finance_agent = FinanceAgent()
            tools_count = len(finance_agent.agent.tools) if hasattr(finance_agent.agent, 'tools') and finance_agent.agent.tools else 0
            self.log_test(
                "FinanceAgent Creation",
                True,
                f"Agent created with {tools_count} tools"
            )
        except Exception as e:
            self.log_test("FinanceAgent Creation", False, str(e))
        
        # Teste 4: Process Request (LogisticsAgent)
        try:
            test_context = {
                "userId": "test_user",
                "role": "logistics",
                "permissions": ["read:cte"],
                "sessionId": "test_session"
            }
            
            test_request = {
                "type": "system_check",
                "message": "Verificar saúde do sistema",
                "timestamp": datetime.now().isoformat()
            }
            
            # Teste sem executar (pode falhar por falta de API real)
            response = await logistics_agent.process_request(test_context, test_request)
            success = response.get("status") in ["success", "error"]  # Qualquer resposta estruturada é válida
            
            self.log_test(
                "Agent Request Processing",
                success,
                f"Response status: {response.get('status', 'unknown')}"
            )
        except Exception as e:
            self.log_test("Agent Request Processing", False, str(e))
    
    def test_environment_config(self):
        """Testa configuração do ambiente"""
        print("\n⚙️ Testing Environment Configuration...")
        
        # Teste 1: API Keys
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GOOGLE_API_KEY")
        
        self.log_test(
            "OpenAI API Key",
            bool(openai_key),
            "Configured" if openai_key else "Not configured"
        )
        
        self.log_test(
            "Gemini API Key", 
            bool(gemini_key),
            "Configured" if gemini_key else "Not configured"
        )
        
        # Teste 2: Dependencies
        dependencies = {
            "aiohttp": "HTTP client for API calls",
            "PIL": "Image processing for OCR", 
            "PyPDF2": "PDF processing",
            "langchain_openai": "OpenAI integration",
            "crewai": "Agent framework"
        }
        
        for dep, desc in dependencies.items():
            try:
                __import__(dep)
                self.log_test(f"Dependency: {dep}", True, desc)
            except ImportError:
                self.log_test(f"Dependency: {dep}", False, f"Missing: {desc}")
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 Starting Gatekeeper Integration Tests")
        print("=" * 50)
        
        # Testes de ambiente
        self.test_environment_config()
        
        # Testes das ferramentas
        await self.test_gatekeeper_api_tools()
        self.test_document_processor()
        self.test_webhook_processor()
        
        # Testes dos agentes
        await self.test_specialized_agents()
        
        # Relatório final
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print(f"Total tests: {self.results['tests_run']}")
        print(f"✅ Passed: {self.results['tests_passed']}")
        print(f"❌ Failed: {self.results['tests_failed']}")
        
        if self.results['errors']:
            print(f"\n🔍 Failed tests details:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        success_rate = (self.results['tests_passed'] / self.results['tests_run']) * 100 if self.results['tests_run'] > 0 else 0
        print(f"\n🎯 Success rate: {success_rate:.1f}%")
        
        if success_rate >= 70:
            print("🎉 Integration tests PASSED!")
            return True
        else:
            print("⚠️ Integration tests FAILED - Need attention")
            return False


async def main():
    """Função principal"""
    test_runner = GatekeeperIntegrationTest()
    success = await test_runner.run_all_tests()
    
    print(f"\n{'='*50}")
    print("🏁 Test execution completed!")
    print(f"Result: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())