"""
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
