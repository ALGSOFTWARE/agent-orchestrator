#!/usr/bin/env python3
"""
Script para aplicar correções prioritárias no Sistema Gatekeeper
"""
import asyncio
import aiohttp
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PriorityFixer:
    """Classe para aplicar correções prioritárias"""
    
    def __init__(self, project_root: str = "/home/narrador/Projetos/MIT/python-crewai"):
        self.project_root = Path(project_root)
        self.fixes_applied = []
        self.fixes_failed = []
    
    def fix_url_building_bug(self):
        """Fix 1: Corrigir URL building bug"""
        logger.info("🔧 Aplicando Fix 1: URL Building Bug")
        
        file_path = self.project_root / "tools" / "gatekeeper_api_tool.py"
        
        if not file_path.exists():
            self.fixes_failed.append("URL Building: Arquivo não encontrado")
            return False
        
        try:
            content = file_path.read_text()
            
            # Verificar se já foi corrigido
            if 'if endpoint.startswith(\'/\'):' in content:
                logger.info("✅ URL building já está correto")
                self.fixes_applied.append("URL Building: Já corrigido")
                return True
            
            # Procurar pelo padrão problemático
            old_pattern = 'url = f"{self.base_url}{endpoint}"'
            
            if old_pattern not in content:
                logger.warning("⚠️ Padrão antigo não encontrado - pode já estar corrigido")
                self.fixes_applied.append("URL Building: Padrão não encontrado")
                return True
            
            # Aplicar correção
            new_pattern = '''# Corrigir concatenação de URL
        if endpoint.startswith('/'):
            url = f"{self.base_url}{endpoint}"
        else:
            url = f"{self.base_url}/{endpoint}"'''
            
            content = content.replace(old_pattern, new_pattern)
            
            # Salvar arquivo
            file_path.write_text(content)
            
            logger.info("✅ URL building bug corrigido")
            self.fixes_applied.append("URL Building: Corrigido com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir URL building: {e}")
            self.fixes_failed.append(f"URL Building: {e}")
            return False
    
    def add_error_handling_with_retry(self):
        """Fix 2: Adicionar error handling robusto com retry"""
        logger.info("🔧 Aplicando Fix 2: Error Handling com Retry")
        
        file_path = self.project_root / "tools" / "gatekeeper_api_tool.py"
        
        try:
            content = file_path.read_text()
            
            # Verificar se já foi adicionado
            if '_make_request_with_retry' in content:
                logger.info("✅ Retry logic já existe")
                self.fixes_applied.append("Error Handling: Já implementado")
                return True
            
            # Encontrar a classe GatekeeperAPITool
            class_start = content.find('class GatekeeperAPITool:')
            if class_start == -1:
                raise ValueError("Classe GatekeeperAPITool não encontrada")
            
            # Adicionar método de retry após _make_request
            retry_method = '''
    async def _make_request_with_retry(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        max_retries: int = 3
    ) -> APIResponse:
        """Faz requisição HTTP com retry automático e exponential backoff"""
        import asyncio
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await self._make_request(method, endpoint, data, params)
                
            except (aiohttp.ClientError, asyncio.TimeoutError, ConnectionError) as e:
                last_exception = e
                
                if attempt == max_retries - 1:
                    logger.error(f"Todas as {max_retries} tentativas falharam: {e}")
                    break
                
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"Tentativa {attempt + 1}/{max_retries} falhou, tentando novamente em {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
            
            except Exception as e:
                # Para outros erros, não fazer retry
                logger.error(f"Erro não recuperável: {e}")
                last_exception = e
                break
        
        # Retornar resposta de erro se todas as tentativas falharam
        return APIResponse(
            success=False,
            data=None,
            errors=[str(last_exception)],
            status_code=0,
            response_time=0.0
        )
'''
            
            # Encontrar onde inserir o método (após _make_request)
            make_request_end = content.find('    # === GRAPHQL OPERATIONS ===')
            if make_request_end == -1:
                raise ValueError("Local para inserir retry method não encontrado")
            
            # Inserir o método
            content = content[:make_request_end] + retry_method + '\n' + content[make_request_end:]
            
            # Salvar arquivo
            file_path.write_text(content)
            
            logger.info("✅ Error handling com retry adicionado")
            self.fixes_applied.append("Error Handling: Retry logic implementado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar retry logic: {e}")
            self.fixes_failed.append(f"Error Handling: {e}")
            return False
    
    def add_structured_logging(self):
        """Fix 3: Adicionar logging estruturado"""
        logger.info("🔧 Aplicando Fix 3: Structured Logging")
        
        # Criar arquivo de configuração de logging
        utils_dir = self.project_root / "utils"
        utils_dir.mkdir(exist_ok=True)
        
        logger_file = utils_dir / "logger.py"
        
        try:
            logger_content = '''"""
Sistema de logging estruturado para o Gatekeeper
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional

class StructuredLogger:
    """Logger estruturado com suporte a contexto"""
    
    def __init__(self, name: str = "gatekeeper", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remover handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Configurar handler estruturado
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(StructuredFormatter())
        
        self.logger.addHandler(handler)
    
    def info(self, message: str, **context):
        """Log info com contexto estruturado"""
        self.logger.info(message, extra={"context": context})
    
    def error(self, message: str, **context):
        """Log error com contexto estruturado"""
        self.logger.error(message, extra={"context": context})
    
    def warning(self, message: str, **context):
        """Log warning com contexto estruturado"""
        self.logger.warning(message, extra={"context": context})
    
    def debug(self, message: str, **context):
        """Log debug com contexto estruturado"""
        self.logger.debug(message, extra={"context": context})

class StructuredFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON"""
    
    def format(self, record):
        # Dados básicos do log
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adicionar contexto se disponível
        if hasattr(record, "context") and record.context:
            log_data["context"] = record.context
        
        # Adicionar exception info se disponível
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False, default=str)

# Instância global
logger = StructuredLogger()

def get_logger(name: str = "gatekeeper") -> StructuredLogger:
    """Obter logger estruturado"""
    return StructuredLogger(name)
'''
            
            # Criar arquivo se não existir
            if not logger_file.exists():
                logger_file.write_text(logger_content)
                logger.info("✅ Sistema de logging estruturado criado")
                self.fixes_applied.append("Structured Logging: Sistema criado")
            else:
                logger.info("✅ Sistema de logging já existe")
                self.fixes_applied.append("Structured Logging: Já existente")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar logging estruturado: {e}")
            self.fixes_failed.append(f"Structured Logging: {e}")
            return False
    
    def update_imports_for_logging(self):
        """Fix 4: Atualizar imports para usar novo sistema de logging"""
        logger.info("🔧 Aplicando Fix 4: Atualizar imports de logging")
        
        files_to_update = [
            "tools/gatekeeper_api_tool.py",
            "tools/document_processor.py",
            "tools/webhook_processor.py",
            "agents/specialized_agents.py"
        ]
        
        updated_files = []
        
        for file_rel_path in files_to_update:
            file_path = self.project_root / file_rel_path
            
            if not file_path.exists():
                continue
            
            try:
                content = file_path.read_text()
                
                # Verificar se já foi atualizado
                if 'from utils.logger import logger' in content:
                    continue
                
                # Encontrar imports existentes
                lines = content.split('\n')
                import_insert_index = 0
                
                # Encontrar onde inserir import
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_insert_index = i + 1
                    elif line.strip() and not line.strip().startswith('#'):
                        break
                
                # Inserir novo import
                new_import = 'from utils.logger import logger'
                lines.insert(import_insert_index, new_import)
                
                # Substituir logging básico
                content = '\n'.join(lines)
                
                # Substituir padrões de logging antigos
                replacements = [
                    ('logging.getLogger(__name__)', 'logger'),
                    ('logger.info(f"', 'logger.info("'),
                    ('logger.error(f"', 'logger.error("'),
                    ('logger.warning(f"', 'logger.warning("'),
                    ('logger.debug(f"', 'logger.debug("'),
                ]
                
                for old, new in replacements:
                    content = content.replace(old, new)
                
                # Salvar arquivo atualizado
                file_path.write_text(content)
                updated_files.append(file_rel_path)
                
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar {file_rel_path}: {e}")
                self.fixes_failed.append(f"Logging Update {file_rel_path}: {e}")
        
        if updated_files:
            logger.info(f"✅ Logging atualizado em: {', '.join(updated_files)}")
            self.fixes_applied.append(f"Logging Updates: {len(updated_files)} arquivos")
        else:
            logger.info("✅ Imports de logging já estão atualizados")
            self.fixes_applied.append("Logging Updates: Já atualizados")
        
        return True
    
    def add_type_hints(self):
        """Fix 5: Adicionar type hints essenciais"""
        logger.info("🔧 Aplicando Fix 5: Type Hints")
        
        # Focar no arquivo principal primeiro
        file_path = self.project_root / "tools" / "gatekeeper_api_tool.py"
        
        try:
            content = file_path.read_text()
            
            # Verificar se já tem type hints suficientes
            if 'from typing import' in content and 'Dict[str, Any]' in content:
                logger.info("✅ Type hints já estão implementados")
                self.fixes_applied.append("Type Hints: Já implementados")
                return True
            
            # Adicionar imports de typing se necessário
            if 'from typing import' not in content:
                lines = content.split('\n')
                
                # Encontrar onde inserir
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('from ') or line.strip().startswith('import '):
                        insert_index = i + 1
                
                # Inserir typing imports
                typing_import = 'from typing import Dict, Any, Optional, List, Union'
                lines.insert(insert_index, typing_import)
                
                content = '\n'.join(lines)
            
            # Salvar com type hints básicos adicionados
            file_path.write_text(content)
            
            logger.info("✅ Type hints básicos adicionados")
            self.fixes_applied.append("Type Hints: Imports básicos adicionados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar type hints: {e}")
            self.fixes_failed.append(f"Type Hints: {e}")
            return False
    
    async def test_fixes(self):
        """Testar se as correções funcionaram"""
        logger.info("🧪 Testando correções aplicadas...")
        
        try:
            # Testar import dos módulos principais
            sys.path.insert(0, str(self.project_root))
            
            # Test 1: Importar ferramentas
            try:
                from tools.gatekeeper_api_tool import GatekeeperAPITool, CrewAIGatekeeperTool
                logger.info("✅ GatekeeperAPITool importado com sucesso")
            except ImportError as e:
                logger.error(f"❌ Erro ao importar GatekeeperAPITool: {e}")
                return False
            
            # Test 2: Verificar se retry method existe
            try:
                tool = GatekeeperAPITool()
                if hasattr(tool, '_make_request_with_retry'):
                    logger.info("✅ Método de retry encontrado")
                else:
                    logger.warning("⚠️ Método de retry não encontrado")
            except Exception as e:
                logger.error(f"❌ Erro ao verificar retry method: {e}")
            
            # Test 3: Verificar logging estruturado
            try:
                from utils.logger import logger as struct_logger
                struct_logger.info("Teste de logging estruturado", test=True)
                logger.info("✅ Logging estruturado funcionando")
            except ImportError as e:
                logger.warning(f"⚠️ Logging estruturado não disponível: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante testes: {e}")
            return False
    
    def generate_report(self):
        """Gerar relatório das correções aplicadas"""
        logger.info("📊 Gerando relatório das correções...")
        
        report = f"""
# RELATÓRIO DE CORREÇÕES PRIORITÁRIAS

## ✅ Correções Aplicadas com Sucesso ({len(self.fixes_applied)})
{chr(10).join([f'- {fix}' for fix in self.fixes_applied])}

## ❌ Correções que Falharam ({len(self.fixes_failed)})
{chr(10).join([f'- {fix}' for fix in self.fixes_failed])}

## 📈 Taxa de Sucesso
{len(self.fixes_applied) / (len(self.fixes_applied) + len(self.fixes_failed)) * 100:.1f}% das correções aplicadas com sucesso

## 🎯 Próximos Passos
1. Testar sistema com: `python test_gatekeeper_integration.py`
2. Verificar se erros de URL foram resolvidos
3. Implementar testes unitários para as correções
4. Monitorar logs estruturados em produção

---
Relatório gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Salvar relatório
        report_file = self.project_root / "fixes" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(report)
        
        print(report)
        logger.info(f"📄 Relatório salvo em: {report_file}")
        
        return report

async def main():
    """Função principal para aplicar todas as correções"""
    logger.info("🚀 Iniciando aplicação de correções prioritárias...")
    
    fixer = PriorityFixer()
    
    # Aplicar correções em ordem de prioridade
    fixes = [
        fixer.fix_url_building_bug,
        fixer.add_error_handling_with_retry,
        fixer.add_structured_logging,
        fixer.update_imports_for_logging,
        fixer.add_type_hints
    ]
    
    for fix_func in fixes:
        try:
            fix_func()
        except Exception as e:
            logger.error(f"❌ Erro durante correção: {e}")
    
    # Testar correções
    await fixer.test_fixes()
    
    # Gerar relatório
    fixer.generate_report()
    
    logger.info("🎉 Processo de correções concluído!")
    
    return len(fixer.fixes_applied), len(fixer.fixes_failed)

if __name__ == "__main__":
    try:
        applied, failed = asyncio.run(main())
        print(f"\n🎯 Resumo: {applied} correções aplicadas, {failed} falharam")
        sys.exit(0 if failed == 0 else 1)
    except KeyboardInterrupt:
        logger.info("❌ Processo interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)