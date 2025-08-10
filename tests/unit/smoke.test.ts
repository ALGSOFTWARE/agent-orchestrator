import { jest } from '@jest/globals';

describe('Smoke Tests - Verificações Básicas', () => {
  
  describe('Importações de Módulos', () => {
    test('deve importar dependências principais sem erros', async () => {
      // Testa se as dependências principais podem ser importadas
      await expect(import('dotenv')).resolves.toBeDefined();
      await expect(import('@langchain/community/chat_models/ollama')).resolves.toBeDefined();
      await expect(import('@langchain/core/messages')).resolves.toBeDefined();
    });

    test('deve ter arquivos principais existentes', async () => {
      // Verifica se os arquivos principais existem
      const fs = await import('fs/promises');
      
      const arquivos = ['src/simple-agent.ts', 'src/interactive-agent.ts', 'src/index.ts'];
      
      for (const arquivo of arquivos) {
        const exists = await fs.access(`./${arquivo}`)
          .then(() => true)
          .catch(() => false);
        expect(exists).toBe(true);
      }
    });
  });

  describe('Configurações do Ambiente', () => {
    test('deve ter variáveis de ambiente de teste definidas', () => {
      expect(process.env.NODE_ENV).toBe('test');
      expect(process.env.OLLAMA_BASE_URL).toBeDefined();
      expect(process.env.OLLAMA_MODEL).toBeDefined();
    });

    test('deve ter configurações de teste apropriadas', () => {
      expect(process.env.NODE_ENV).toBe('test');
      expect(process.env.MOCK_LLM_RESPONSES).toBe('true');
      expect(process.env.LOG_LEVEL).toBe('error');
    });
  });

  describe('Estrutura do Projeto', () => {
    test('deve ter package.json com configurações corretas', async () => {
      const fs = await import('fs/promises');
      
      const packageJson = JSON.parse(
        await fs.readFile('./package.json', 'utf-8')
      );
      
      expect(packageJson.type).toBe('module');
      expect(packageJson.scripts.test).toBeDefined();
      expect(packageJson.devDependencies.jest).toBeDefined();
    });

    test('deve ter jest.config.ts configurado', async () => {
      const fs = await import('fs/promises');
      
      const jestConfigExists = await fs.access('./jest.config.ts')
        .then(() => true)
        .catch(() => false);
        
      expect(jestConfigExists).toBe(true);
    });
  });

  describe('Mocks e Utilidades de Teste', () => {
    test('deve ter mocks configurados corretamente', async () => {
      const { MockChatOllama } = await import('../mocks/ollama-mock');
      
      expect(MockChatOllama).toBeDefined();
      expect(typeof MockChatOllama).toBe('function');
      
      const mockInstance = new MockChatOllama({ model: 'test' });
      expect(mockInstance.invoke).toBeDefined();
      expect(typeof mockInstance.invoke).toBe('function');
    });

    test('deve ter respostas mock definidas', async () => {
      const { mockOllamaResponses } = await import('../mocks/ollama-mock');
      
      expect(mockOllamaResponses).toBeDefined();
      expect(mockOllamaResponses.cteConsulta).toBeDefined();
      expect(mockOllamaResponses.blConsulta).toBeDefined();
      expect(mockOllamaResponses.containerStatus).toBeDefined();
    });
  });

  describe('Configurações de Teste Global', () => {
    test('deve ter configurações globais de teste', () => {
      expect(global.testConfig).toBeDefined();
      expect(global.testConfig.OLLAMA_TIMEOUT).toBeDefined();
      expect(global.testConfig.MOCK_RESPONSES).toBe(true);
    });

    test('deve ter console configurado para testes', () => {
      // Verifica se o console está funcionando adequadamente em modo teste
      const originalLog = console.log;
      expect(typeof originalLog).toBe('function');
    });
  });

  describe('Funcionalidade Básica', () => {
    test('deve conseguir criar instância de mock do agente', async () => {
      const { MockChatOllama, MockSystemMessage } = await import('../mocks/ollama-mock');
      
      const mockLLM = new MockChatOllama({
        baseUrl: "http://localhost:11434",
        model: "test-model",
        temperature: 0.3,
      });
      
      const systemMsg = new MockSystemMessage("Sistema de teste");
      
      expect(mockLLM).toBeDefined();
      expect(systemMsg.content).toBe("Sistema de teste");
      expect(systemMsg.type).toBe("system");
    });

    test('deve conseguir simular interação básica', async () => {
      const { MockChatOllama, MockHumanMessage } = await import('../mocks/ollama-mock');
      
      const mockLLM = new MockChatOllama({ model: 'test' });
      const userMsg = new MockHumanMessage("teste básico");
      
      const response = await mockLLM.invoke([userMsg]);
      
      expect(response).toBeDefined();
      expect(response.content).toBeTruthy();
      expect(typeof response.content).toBe('string');
    });
  });

  describe('Performance Básica', () => {
    test('mocks devem responder rapidamente', async () => {
      const { MockChatOllama, MockHumanMessage } = await import('../mocks/ollama-mock');
      
      const mockLLM = new MockChatOllama({ model: 'test' });
      const startTime = Date.now();
      
      await mockLLM.invoke([new MockHumanMessage("teste de velocidade")]);
      
      const endTime = Date.now();
      expect(endTime - startTime).toBeLessThan(1000); // Menos de 1 segundo
    });

    test('deve poder executar múltiplas interações rapidamente', async () => {
      const { MockChatOllama, MockHumanMessage } = await import('../mocks/ollama-mock');
      
      const mockLLM = new MockChatOllama({ model: 'test' });
      const promises = [];
      
      for (let i = 0; i < 10; i++) {
        promises.push(mockLLM.invoke([new MockHumanMessage(`teste ${i}`)]));
      }
      
      const startTime = Date.now();
      const responses = await Promise.all(promises);
      const endTime = Date.now();
      
      expect(responses).toHaveLength(10);
      expect(endTime - startTime).toBeLessThan(2000); // Menos de 2 segundos para 10 consultas
    });
  });
});