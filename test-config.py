#!/usr/bin/env python3
"""
MIT Logistics - Teste de Configuração
Valida se o sistema está carregando corretamente as configurações do .env
"""

import sys
import os
sys.path.append('./python-crewai')

def test_config():
    print("🔍 MIT Logistics - Teste de Configuração")
    print("=" * 50)
    
    try:
        # Import da configuração
        from config import config
        
        print("\n📄 Resumo das Configurações:")
        summary = config.get_summary()
        
        for key, value in summary.items():
            if key.endswith('_configured'):
                status = "✅" if value else "❌"
                print(f"   {status} {key}: {value}")
            else:
                print(f"   • {key}: {value}")
        
        print("\n🔑 Validação das API Keys:")
        is_valid, errors = config.validate_api_keys()
        
        if is_valid:
            print("   ✅ Configuração válida!")
        else:
            print("   ❌ Configuração inválida:")
            for error in errors:
                print(f"      • {error}")
        
        print("\n🌍 Variáveis de Ambiente:")
        env_vars = [
            'OPENAI_API_KEY', 'GEMINI_API_KEY', 
            'LLM_PREFERRED_PROVIDER', 'LLM_MAX_DAILY_COST'
        ]
        
        for var in env_vars:
            value = os.getenv(var, 'Não definida')
            if 'API_KEY' in var and value != 'Não definida':
                # Mascarar chaves API para segurança
                masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"   • {var}: {masked}")
            else:
                print(f"   • {var}: {value}")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return False

if __name__ == "__main__":
    success = test_config()
    
    if success:
        print("\n🎉 Sistema pronto para uso!")
        sys.exit(0)
    else:
        print("\n⚠️  Configure suas API keys no arquivo .env antes de continuar")
        print("   Exemplo:")
        print("   OPENAI_API_KEY=sk-proj-...")
        print("   GEMINI_API_KEY=AIzaSy...")
        sys.exit(1)