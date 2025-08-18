"""
MIT Logistics - Configuration Management
Carrega configurações do arquivo .env e variáveis de ambiente
"""

import os
from pathlib import Path
from typing import Optional

class Config:
    """Gerenciamento de configurações do sistema"""
    
    def __init__(self):
        """Inicializa carregando configurações do .env"""
        self.load_env_file()
    
    def load_env_file(self):
        """Carrega variáveis do arquivo .env"""
        env_path = Path(__file__).parent.parent / '.env'
        
        if env_path.exists():
            print(f"📄 Carregando configurações do arquivo: {env_path}")
            
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Ignora comentários e linhas vazias
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Remove aspas se presentes
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            
                            # Define a variável de ambiente se ela não existir
                            if not os.getenv(key):
                                os.environ[key] = value
            
            print("✅ Configurações carregadas do .env")
        else:
            print(f"⚠️  Arquivo .env não encontrado em: {env_path}")
    
    # OpenAI Configuration
    @property
    def openai_api_key(self) -> Optional[str]:
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def openai_model(self) -> str:
        return os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Gemini Configuration
    @property
    def gemini_api_key(self) -> Optional[str]:
        return os.getenv('GEMINI_API_KEY')
    
    @property
    def gemini_model(self) -> str:
        return os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    # LLM Router Settings
    @property
    def llm_preferred_provider(self) -> str:
        return os.getenv('LLM_PREFERRED_PROVIDER', 'auto')
    
    @property
    def llm_max_daily_cost(self) -> float:
        return float(os.getenv('LLM_MAX_DAILY_COST', '50'))
    
    @property
    def llm_temperature(self) -> float:
        return float(os.getenv('LLM_TEMPERATURE', '0.3'))
    
    @property
    def llm_max_tokens(self) -> int:
        return int(os.getenv('LLM_MAX_TOKENS', '1000'))
    
    # Application Settings
    @property
    def node_env(self) -> str:
        return os.getenv('NODE_ENV', 'development')
    
    @property
    def app_name(self) -> str:
        return os.getenv('APP_NAME', 'MIT_Tracking_Agent')
    
    @property
    def app_version(self) -> str:
        return os.getenv('APP_VERSION', '2.0.0')
    
    @property
    def log_level(self) -> str:
        return os.getenv('LOG_LEVEL', 'info')
    
    # Frontend URLs
    @property
    def frontend_api_url(self) -> str:
        return os.getenv('NEXT_PUBLIC_API_URL', 'http://localhost:8001')
    
    @property
    def frontend_gatekeeper_url(self) -> str:
        return os.getenv('NEXT_PUBLIC_GATEKEEPER_URL', 'http://localhost:8001')
    
    # Validation
    def validate_api_keys(self) -> tuple[bool, list[str]]:
        """Valida se pelo menos uma API key está configurada"""
        errors = []
        has_api_key = False
        
        if self.openai_api_key:
            if not (self.openai_api_key.startswith('sk-') or self.openai_api_key.startswith('sk-proj-')):
                errors.append("OpenAI API key deve começar com 'sk-' ou 'sk-proj-'")
            else:
                has_api_key = True
                print("✅ OpenAI API key configurada")
        
        if self.gemini_api_key:
            if not self.gemini_api_key.startswith('AIza'):
                errors.append("Gemini API key deve começar com 'AIza'")
            else:
                has_api_key = True
                print("✅ Gemini API key configurada")
        
        if not has_api_key:
            errors.append("Nenhuma API key válida configurada (OpenAI ou Gemini)")
        
        return has_api_key, errors
    
    def get_summary(self) -> dict:
        """Retorna resumo das configurações"""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "node_env": self.node_env,
            "openai_configured": bool(self.openai_api_key),
            "gemini_configured": bool(self.gemini_api_key),
            "preferred_provider": self.llm_preferred_provider,
            "max_daily_cost": self.llm_max_daily_cost,
            "temperature": self.llm_temperature,
            "max_tokens": self.llm_max_tokens,
            "log_level": self.log_level
        }

# Instância global
config = Config()

# Validação na importação
is_valid, validation_errors = config.validate_api_keys()

if not is_valid:
    print("⚠️  Configuração incompleta:")
    for error in validation_errors:
        print(f"   • {error}")
    print("\n💡 Configure suas API keys no arquivo .env:")
    print("   OPENAI_API_KEY=sk-proj-...")
    print("   GEMINI_API_KEY=AIzaSy...")
else:
    print("✅ Configuração validada com sucesso!")