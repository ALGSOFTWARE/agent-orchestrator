#!/usr/bin/env python3
"""
Testes Unitários para Gatekeeper Agent

Testa as funcionalidades principais do Gatekeeper:
- Validação de payload
- Roteamento por roles
- Validação de permissões
- Respostas de erro e sucesso
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, AsyncMock
import json
import sys
import os

# Adicionar diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gatekeeper_agent import app, GatekeeperService, UserRole, ROLE_AGENT_MAP

# Cliente de teste
client = TestClient(app)

class TestGatekeeperEndpoints:
    """Testes para endpoints do Gatekeeper"""
    
    def test_health_check(self):
        """Testa endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Gatekeeper Agent"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
    
    def test_system_info(self):
        """Testa endpoint de informações do sistema"""
        response = client.get("/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "Gatekeeper Agent"
        assert "supported_roles" in data
        assert "agent_mapping" in data
        assert "endpoints" in data
    
    def test_list_roles(self):
        """Testa endpoint de listagem de roles"""
        response = client.get("/roles")
        assert response.status_code == 200
        
        data = response.json()
        assert "available_roles" in data
        assert "role_permissions" in data
        
        # Verifica se todos os roles estão presentes
        expected_roles = ["admin", "logistics", "finance", "operator"]
        for role in expected_roles:
            assert role in data["available_roles"]

class TestAuthCallback:
    """Testes para o endpoint principal /auth-callback"""
    
    def test_auth_callback_valid_admin(self):
        """Testa autenticação válida para role admin"""
        payload = {
            "userId": "admin123",
            "role": "admin",
            "permissions": ["read:all", "write:all"],
            "sessionId": "session_admin_123"
        }
        
        with patch('agents.route_to_specialized_agent') as mock_route:
            mock_route.return_value = {
                "agent": "AdminAgent",
                "status": "success",
                "response": "Admin access granted"
            }
            
            response = client.post("/auth-callback", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert data["agent"] == "AdminAgent"
            assert data["userId"] == "admin123"
            assert "data" in data
    
    def test_auth_callback_valid_logistics(self):
        """Testa autenticação válida para role logistics"""
        payload = {
            "userId": "logistics456",
            "role": "logistics",
            "permissions": ["read:cte", "write:document"]
        }
        
        with patch('agents.route_to_specialized_agent') as mock_route:
            mock_route.return_value = {
                "agent": "LogisticsAgent",
                "status": "success",
                "response": "Logistics access granted"
            }
            
            response = client.post("/auth-callback", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert data["agent"] == "LogisticsAgent"
            assert data["userId"] == "logistics456"
    
    def test_auth_callback_valid_finance(self):
        """Testa autenticação válida para role finance"""
        payload = {
            "userId": "finance789",
            "role": "finance",
            "permissions": ["read:financial", "write:payment"]
        }
        
        with patch('agents.route_to_specialized_agent') as mock_route:
            mock_route.return_value = {
                "agent": "FinanceAgent",
                "status": "success",
                "response": "Finance access granted"
            }
            
            response = client.post("/auth-callback", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert data["agent"] == "FinanceAgent"
            assert data["userId"] == "finance789"
    
    def test_auth_callback_invalid_role(self):
        """Testa autenticação com role inválido"""
        payload = {
            "userId": "invalid123",
            "role": "invalid_role",
            "permissions": []
        }
        
        response = client.post("/auth-callback", json=payload)
        assert response.status_code == 422  # Validation error por Pydantic
    
    def test_auth_callback_empty_user_id(self):
        """Testa autenticação com userId vazio"""
        payload = {
            "userId": "",
            "role": "admin",
            "permissions": []
        }
        
        response = client.post("/auth-callback", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_auth_callback_missing_required_fields(self):
        """Testa autenticação com campos obrigatórios faltando"""
        payload = {
            "role": "admin"
            # userId faltando
        }
        
        response = client.post("/auth-callback", json=payload)
        assert response.status_code == 422
    
    def test_auth_callback_invalid_permissions_for_role(self):
        """Testa autenticação com permissões inválidas para o role"""
        payload = {
            "userId": "operator123",
            "role": "operator",
            "permissions": ["read:financial", "write:admin"]  # Permissões inválidas para operator
        }
        
        response = client.post("/auth-callback", json=payload)
        assert response.status_code == 403
        
        data = response.json()
        assert data["code"] == 403
        assert "permissões" in data["message"].lower()

class TestGatekeeperService:
    """Testes para a classe GatekeeperService"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.service = GatekeeperService()
    
    def test_validate_role_valid(self):
        """Testa validação de roles válidos"""
        assert self.service.validate_role(UserRole.ADMIN) == True
        assert self.service.validate_role(UserRole.LOGISTICS) == True
        assert self.service.validate_role(UserRole.FINANCE) == True
        assert self.service.validate_role(UserRole.OPERATOR) == True
    
    def test_get_agent_for_role(self):
        """Testa mapeamento de roles para agentes"""
        assert self.service.get_agent_for_role(UserRole.ADMIN) == "AdminAgent"
        assert self.service.get_agent_for_role(UserRole.LOGISTICS) == "LogisticsAgent"
        assert self.service.get_agent_for_role(UserRole.FINANCE) == "FinanceAgent"
        assert self.service.get_agent_for_role(UserRole.OPERATOR) == "LogisticsAgent"
    
    def test_validate_permissions_admin(self):
        """Testa validação de permissões para admin (deve aceitar tudo)"""
        permissions = ["read:all", "write:all", "delete:everything"]
        assert self.service.validate_permissions(UserRole.ADMIN, permissions) == True
    
    def test_validate_permissions_logistics_valid(self):
        """Testa validação de permissões válidas para logistics"""
        permissions = ["read:cte", "write:document"]
        assert self.service.validate_permissions(UserRole.LOGISTICS, permissions) == True
    
    def test_validate_permissions_logistics_invalid(self):
        """Testa validação de permissões inválidas para logistics"""
        permissions = ["read:financial", "write:admin"]
        assert self.service.validate_permissions(UserRole.LOGISTICS, permissions) == False
    
    def test_validate_permissions_finance_valid(self):
        """Testa validação de permissões válidas para finance"""
        permissions = ["read:financial", "write:payment"]
        assert self.service.validate_permissions(UserRole.FINANCE, permissions) == True
    
    def test_validate_permissions_finance_invalid(self):
        """Testa validação de permissões inválidas para finance"""
        permissions = ["read:cte", "write:document"]
        assert self.service.validate_permissions(UserRole.FINANCE, permissions) == False
    
    def test_validate_permissions_empty_list(self):
        """Testa validação com lista de permissões vazia"""
        assert self.service.validate_permissions(UserRole.LOGISTICS, []) == True
        assert self.service.validate_permissions(UserRole.FINANCE, []) == True
    
    @pytest.mark.asyncio
    async def test_route_to_agent_success(self):
        """Testa roteamento bem-sucedido para agente"""
        from gatekeeper_agent import AuthPayload
        
        payload = AuthPayload(
            userId="test123",
            role=UserRole.LOGISTICS,
            permissions=["read:cte"]
        )
        
        with patch('agents.route_to_specialized_agent') as mock_route:
            mock_route.return_value = {
                "agent": "LogisticsAgent",
                "status": "success",
                "response": "Test response"
            }
            
            result = await self.service.route_to_agent(payload)
            
            assert result["routing_success"] == True
            assert result["user_context"]["userId"] == "test123"
            assert result["user_context"]["role"] == "logistics"
            assert result["agent_response"]["agent"] == "LogisticsAgent"
    
    @pytest.mark.asyncio
    async def test_route_to_agent_error(self):
        """Testa tratamento de erro no roteamento"""
        from gatekeeper_agent import AuthPayload
        
        payload = AuthPayload(
            userId="test123",
            role=UserRole.LOGISTICS,
            permissions=["read:cte"]
        )
        
        with patch('agents.route_to_specialized_agent') as mock_route:
            mock_route.side_effect = Exception("Erro de teste")
            
            result = await self.service.route_to_agent(payload)
            
            assert result["routing_success"] == False
            assert result["agent_response"]["status"] == "error"
            assert "Erro de teste" in result["agent_response"]["error"]

class TestIntegration:
    """Testes de integração completos"""
    
    @pytest.mark.asyncio
    async def test_full_auth_flow_logistics(self):
        """Testa fluxo completo de autenticação para usuário logistics"""
        payload = {
            "userId": "logistics_user_001",
            "role": "logistics",
            "permissions": ["read:cte", "write:document"],
            "sessionId": "session_001"
        }
        
        with patch('agents.route_to_specialized_agent') as mock_route:
            mock_route.return_value = {
                "agent": "LogisticsAgent",
                "status": "success",
                "response": "Logistics agent response",
                "capabilities": ["CT-e processing", "Document analysis"]
            }
            
            response = client.post("/auth-callback", json=payload)
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert data["agent"] == "LogisticsAgent"
            assert data["userId"] == "logistics_user_001"
            assert "capabilities" in data["data"]["agent_response"]
            
            # Verifica se o mock foi chamado corretamente
            mock_route.assert_called_once()
            call_args = mock_route.call_args
            assert call_args[1]["agent_name"] == "LogisticsAgent"
            assert call_args[1]["user_context"]["userId"] == "logistics_user_001"
    
    def test_cors_headers(self):
        """Testa se headers CORS estão configurados"""
        response = client.options("/auth-callback")
        # FastAPI com CORS middleware deve permitir OPTIONS
        assert response.status_code in [200, 405]  # 405 se OPTIONS não implementado explicitamente
    
    def test_error_response_format(self):
        """Testa formato padronizado de respostas de erro"""
        payload = {
            "userId": "",  # userId inválido
            "role": "admin",
            "permissions": []
        }
        
        response = client.post("/auth-callback", json=payload)
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data  # FastAPI validation error format

if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])