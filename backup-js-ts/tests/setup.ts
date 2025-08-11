// Setup global para testes Jest
import dotenv from 'dotenv';
import type { TestConfig } from '@/types';

// Carrega variáveis de ambiente de teste
dotenv.config({ path: '.env.test' });

// Se não houver .env.test, usa configurações padrão de teste
if (!process.env.OLLAMA_BASE_URL) {
  process.env.OLLAMA_BASE_URL = 'http://localhost:11434';
  process.env.OLLAMA_MODEL = 'llama3.2:3b';
  process.env.NODE_ENV = 'test';
}

// Declaração global para TypeScript
declare global {
  var testConfig: TestConfig;
}

// Configurações globais para testes
global.testConfig = {
  OLLAMA_TIMEOUT: 15000,
  MOCK_RESPONSES: true,
  VERBOSE_LOGS: false
};

// Console personalizado para testes (reduz ruído)
if (!global.testConfig.VERBOSE_LOGS) {
  const originalConsoleLog = console.log;
  const originalConsoleError = console.error;
  
  console.log = (...args) => {
    // Só mostra logs que começam com [TEST] ou são de erro
    if (args[0]?.toString().includes('[TEST]')) {
      originalConsoleLog(...args);
    }
  };
  
  console.error = (...args) => {
    // Sempre mostra errors
    originalConsoleError(...args);
  };
}

console.log('[TEST] Setup de testes carregado com sucesso');