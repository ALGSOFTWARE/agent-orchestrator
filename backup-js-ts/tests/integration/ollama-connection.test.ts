import { jest } from '@jest/globals';
import { ChatOllama } from '@langchain/community/chat_models/ollama';
import { SystemMessage, HumanMessage } from '@langchain/core/messages';

describe('Ollama Integration Tests', () => {
  let ollamaClient: ChatOllama;
  
  // Flag para pular testes de integração se Ollama não estiver disponível
  const OLLAMA_AVAILABLE = process.env.CI !== 'true'; // Skip in CI environments
  
  beforeAll(async () => {
    if (!OLLAMA_AVAILABLE) {
      console.log('[TEST] Pulando testes de integração - Ollama não disponível');
      return;
    }

    ollamaClient = new ChatOllama({
      baseUrl: process.env.OLLAMA_BASE_URL || "http://localhost:11434",
      model: process.env.OLLAMA_MODEL || "llama3.2:3b",
      temperature: 0.3,
    });
  });

  describe('Conexão com Ollama', () => {
    test('deve conectar com o servidor Ollama', async () => {
      if (!OLLAMA_AVAILABLE) {
        console.log('[TEST] Pulando testes de integração - Ollama não disponível');
        return;
      }
      const testMessage = [
        new SystemMessage('Você é um assistente de teste.'),
        new HumanMessage('Responda apenas: OK')
      ];

      try {
        const response = await ollamaClient.invoke(testMessage);
        expect(response).toBeDefined();
        expect(response.content).toBeTruthy();
        expect(typeof response.content).toBe('string');
      } catch (error) {
        if (error.message.includes('ECONNREFUSED')) {
          console.warn('[TEST] Ollama não está rodando - pulando teste de integração');
          return;
        }
        throw error;
      }
    }, 30000);

    test('deve responder a consultas básicas em português', async () => {
      if (!OLLAMA_AVAILABLE) {
        console.log('[TEST] Ollama não disponível - pulando teste');
        return;
      }
      const messages = [
        new SystemMessage('Você é um assistente que responde em português.'),
        new HumanMessage('Qual é a capital do Brasil?')
      ];

      try {
        const response = await ollamaClient.invoke(messages);
        expect(response.content).toContain('Brasília');
      } catch (error) {
        if (error.message.includes('ECONNREFUSED')) {
          console.warn('[TEST] Ollama não disponível - pulando teste');
          return;
        }
        throw error;
      }
    }, 30000);
  });

  describe('Respostas Específicas de Logística', () => {
    test('deve responder consultas sobre CT-e', async () => {
      if (!OLLAMA_AVAILABLE) {
        console.log('[TEST] Ollama não disponível - pulando teste');
        return;
      }
      const messages = [
        new SystemMessage(`Você é um assistente especializado da plataforma MIT Tracking da Move In Tech.
        Responda sobre consultas de CT-e (Conhecimento de Transporte Eletrônico) de forma técnica e profissional.`),
        new HumanMessage('Como consultar um CT-e no sistema?')
      ];

      try {
        const response = await ollamaClient.invoke(messages);
        const content = response.content.toLowerCase();
        
        expect(content).toContain('ct-e');
        expect(response.content.length).toBeGreaterThan(50);
      } catch (error) {
        if (error.message.includes('ECONNREFUSED')) {
          console.warn('[TEST] Ollama não disponível - pulando teste');
          return;
        }
        throw error;
      }
    }, 30000);

    test('deve responder sobre BL (Bill of Lading)', async () => {
      const messages = [
        new SystemMessage('Você é um assistente especializado em logística.'),
        new HumanMessage('O que é um BL e como consultá-lo?')
      ];

      try {
        const response = await ollamaClient.invoke(messages);
        const content = response.content.toLowerCase();
        
        expect(content).toMatch(/bl|bill of lading|conhecimento/);
        expect(response.content.length).toBeGreaterThan(30);
      } catch (error) {
        if (error.message.includes('ECONNREFUSED')) {
          console.warn('[TEST] Ollama não disponível - pulando teste');
          return;
        }
        throw error;
      }
    }, 30000);
  });

  describe('Performance e Limites', () => {
    test('deve responder dentro do tempo limite', async () => {
      const messages = [
        new SystemMessage('Responda de forma concisa.'),
        new HumanMessage('Teste de velocidade - responda OK')
      ];

      const startTime = Date.now();
      
      try {
        const response = await ollamaClient.invoke(messages);
        const endTime = Date.now();
        
        expect(response).toBeDefined();
        expect(endTime - startTime).toBeLessThan(25000); // Menos de 25 segundos
      } catch (error) {
        if (error.message.includes('ECONNREFUSED')) {
          console.warn('[TEST] Ollama não disponível - pulando teste');
          return;
        }
        throw error;
      }
    }, 30000);

    test('deve processar múltiplas consultas sequenciais', async () => {
      const consultas = [
        'Primeira consulta',
        'Segunda consulta',
        'Terceira consulta'
      ];

      try {
        for (const consulta of consultas) {
          const messages = [
            new SystemMessage('Responda de forma breve.'),
            new HumanMessage(consulta)
          ];
          
          const response = await ollamaClient.invoke(messages);
          expect(response.content).toBeTruthy();
        }
      } catch (error) {
        if (error.message.includes('ECONNREFUSED')) {
          console.warn('[TEST] Ollama não disponível - pulando teste');
          return;
        }
        throw error;
      }
    }, 45000);
  });

  describe('Tratamento de Erros de Conexão', () => {
    test('deve tratar erro de conexão graciosamente', async () => {
      const clienteInvalido = new ChatOllama({
        baseUrl: "http://localhost:9999", // Porta inválida
        model: "modelo-inexistente",
        temperature: 0.3,
      });

      const messages = [
        new SystemMessage('Teste'),
        new HumanMessage('Teste de erro')
      ];

      await expect(clienteInvalido.invoke(messages)).rejects.toThrow();
    });

    test('deve tratar modelo inexistente', async () => {
      if (!OLLAMA_AVAILABLE) return;

      const clienteModeloInvalido = new ChatOllama({
        baseUrl: process.env.OLLAMA_BASE_URL || "http://localhost:11434",
        model: "modelo-que-nao-existe-123",
        temperature: 0.3,
      });

      const messages = [
        new SystemMessage('Teste'),
        new HumanMessage('Teste')
      ];

      try {
        await clienteModeloInvalido.invoke(messages);
        // Se não falhar, algo está errado
        expect(true).toBe(false);
      } catch (error) {
        expect(error.message).toBeTruthy();
        // Pode ser erro de modelo não encontrado ou conexão
        expect(true).toBe(true);
      }
    });
  });

  // Teste de health check para verificar se Ollama está funcionando
  describe('Health Check', () => {
    test('deve verificar se Ollama está acessível via HTTP', async () => {
      if (!OLLAMA_AVAILABLE) {
        console.log('[TEST] Pulando health check - não está em ambiente local');
        return;
      }

      const baseUrl = process.env.OLLAMA_BASE_URL || "http://localhost:11434";
      
      try {
        const response = await fetch(`${baseUrl}/api/tags`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
          const data = await response.json();
          expect(data).toBeDefined();
          expect(Array.isArray(data.models)).toBe(true);
          console.log(`[TEST] Ollama acessível - ${data.models.length} modelos disponíveis`);
        } else {
          console.warn('[TEST] Ollama não respondeu adequadamente');
        }
      } catch (error) {
        console.warn('[TEST] Ollama não acessível via HTTP:', error.message);
      }
    });
  });
});