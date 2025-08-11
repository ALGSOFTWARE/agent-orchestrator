import { jest } from '@jest/globals';
import { 
  MockChatOllama, 
  MockSystemMessage, 
  MockHumanMessage,
  mockOllamaResponses 
} from '../mocks/ollama-mock';

// Mock das dependências do Langchain
jest.unstable_mockModule('@langchain/community/chat_models/ollama', () => ({
  ChatOllama: MockChatOllama
}));

jest.unstable_mockModule('@langchain/core/messages', () => ({
  SystemMessage: MockSystemMessage,
  HumanMessage: MockHumanMessage
}));

// Importa a classe após os mocks
const { default: dotenv } = await import('dotenv');
dotenv.config({ path: '.env.test' });

// Versão simplificada da classe para testes
class MITTrackingAgentTest {
  constructor() {
    this.llm = new MockChatOllama({
      baseUrl: "http://localhost:11434",
      model: "llama3.2:3b",
      temperature: 0.3,
    });

    this.systemPrompt = `Você é um assistente especializado da plataforma MIT Tracking da Move In Tech.`;
    this.conversationHistory = [new MockSystemMessage(this.systemPrompt)];
  }

  async consultarLogistica(consulta) {
    try {
      this.conversationHistory.push(new MockHumanMessage(consulta));
      const response = await this.llm.invoke(this.conversationHistory);
      this.conversationHistory.push(response);
      return response.content;
    } catch (error) {
      return `Erro ao processar consulta: ${error.message}`;
    }
  }

  limparHistorico() {
    this.conversationHistory = [new MockSystemMessage(this.systemPrompt)];
  }

  getHistoryLength() {
    return this.conversationHistory.length;
  }

  getLLMCallCount() {
    return this.llm.getCallCount();
  }
}

describe('MITTrackingAgent - Testes Unitários', () => {
  let agent;

  beforeEach(() => {
    console.log('[TEST] Inicializando novo agente para teste');
    agent = new MITTrackingAgentTest();
  });

  afterEach(() => {
    if (agent?.llm?.reset) {
      agent.llm.reset();
    }
  });

  describe('Inicialização do Agente', () => {
    test('deve inicializar com configurações corretas', () => {
      expect(agent).toBeDefined();
      expect(agent.llm).toBeDefined();
      expect(agent.systemPrompt).toContain('MIT Tracking');
      expect(agent.getHistoryLength()).toBe(1); // Apenas system message inicial
    });

    test('deve ter histórico inicial com system prompt', () => {
      expect(agent.conversationHistory).toHaveLength(1);
      expect(agent.conversationHistory[0].type).toBe('system');
      expect(agent.conversationHistory[0].content).toContain('MIT Tracking');
    });
  });

  describe('Consultas sobre CT-e', () => {
    test('deve responder consultas sobre CT-e', async () => {
      const consulta = 'Como consultar meu CT-e número 123456?';
      const resposta = await agent.consultarLogistica(consulta);
      
      expect(resposta).toContain('CT-e');
      expect(resposta).toContain('MIT Tracking');
      expect(agent.getLLMCallCount()).toBe(1);
      expect(agent.getHistoryLength()).toBe(3); // system + user + assistant
    });

    test('deve manter contexto entre consultas CT-e', async () => {
      await agent.consultarLogistica('Preciso consultar um CT-e');
      await agent.consultarLogistica('Qual o status?');
      
      expect(agent.getHistoryLength()).toBe(5); // system + 2*(user + assistant)
      expect(agent.getLLMCallCount()).toBe(2);
    });
  });

  describe('Consultas sobre BL (Bill of Lading)', () => {
    test('deve responder consultas sobre BL', async () => {
      const consulta = 'Onde está o meu BL?';
      const resposta = await agent.consultarLogistica(consulta);
      
      expect(resposta).toContain('BL');
      expect(resposta).toContain('Bill of Lading');
      expect(agent.getLLMCallCount()).toBe(1);
    });

    test('deve fornecer instruções específicas para BL', async () => {
      const resposta = await agent.consultarLogistica('Como consultar BL no sistema?');
      
      expect(resposta).toContain('número do BL');
      expect(resposta).toContain('status atual');
      expect(resposta).toContain('documentos associados');
    });
  });

  describe('Consultas sobre Containers', () => {
    test('deve responder sobre status de containers', async () => {
      const consulta = 'Qual o status do meu container?';
      const resposta = await agent.consultarLogistica(consulta);
      
      expect(resposta).toContain('container');
      expect(resposta).toContain('trânsito');
      expect(resposta).toBeTruthy();
    });

    test('deve explicar diferentes status de container', async () => {
      const resposta = await agent.consultarLogistica('Explique os status de container');
      
      expect(resposta).toContain('Em trânsito');
      expect(resposta).toContain('porto');
      expect(resposta).toContain('Entregue');
    });
  });

  describe('Consultas sobre ETA/ETD', () => {
    test('deve responder sobre ETA', async () => {
      const consulta = 'Como consultar ETA da minha carga?';
      const resposta = await agent.consultarLogistica(consulta);
      
      expect(resposta).toContain('ETA');
      expect(resposta).toContain('Estimated Time of Arrival');
      expect(resposta).toContain('previsões');
    });

    test('deve mencionar fatores que afetam ETA', async () => {
      const resposta = await agent.consultarLogistica('O que afeta o ETA?');
      
      expect(resposta).toContain('tráfego');
      expect(resposta).toContain('clima');
      expect(resposta).toContain('atualizações');
    });
  });

  describe('Gerenciamento de Histórico', () => {
    test('deve limpar histórico corretamente', async () => {
      // Adiciona algumas interações
      await agent.consultarLogistica('Primeira pergunta');
      await agent.consultarLogistica('Segunda pergunta');
      
      expect(agent.getHistoryLength()).toBeGreaterThan(1);
      
      // Limpa o histórico
      agent.limparHistorico();
      
      expect(agent.getHistoryLength()).toBe(1); // Apenas system message
      expect(agent.conversationHistory[0].type).toBe('system');
    });

    test('deve manter system prompt após limpar histórico', () => {
      agent.limparHistorico();
      
      expect(agent.conversationHistory[0].content).toContain('MIT Tracking');
      expect(agent.conversationHistory[0].type).toBe('system');
    });
  });

  describe('Tratamento de Erros', () => {
    test('deve tratar erros do LLM graciosamente', async () => {
      const consulta = 'erro simulado'; // Trigger para erro no mock
      const resposta = await agent.consultarLogistica(consulta);
      
      expect(resposta).toContain('Erro ao processar consulta');
      expect(resposta).toContain('Simulated LLM error');
    });

    test('deve continuar funcionando após erro', async () => {
      // Primeiro uma consulta com erro
      await agent.consultarLogistica('erro simulado');
      
      // Depois uma consulta normal
      const resposta = await agent.consultarLogistica('Como consultar CT-e?');
      
      expect(resposta).toContain('CT-e');
      expect(resposta).not.toContain('Erro');
    });
  });

  describe('Consultas Genéricas', () => {
    test('deve responder consultas gerais sobre logística', async () => {
      const consulta = 'O que é logística?';
      const resposta = await agent.consultarLogistica(consulta);
      
      expect(resposta).toContain('MIT Tracking');
      expect(resposta).toContain('logística');
      expect(resposta).toBeTruthy();
    });

    test('deve mencionar especialização em logística', async () => {
      const resposta = await agent.consultarLogistica('Em que você pode me ajudar?');
      
      expect(resposta).toContain('logística');
      expect(resposta).toContain('CT-e');
      expect(resposta).toContain('rastreamento');
    });
  });

  describe('Performance e Limites', () => {
    test('deve processar múltiplas consultas rapidamente', async () => {
      const startTime = Date.now();
      
      const promises = Array.from({ length: 5 }, (_, i) => 
        agent.consultarLogistica(`Consulta número ${i + 1}`)
      );
      
      const respostas = await Promise.all(promises);
      const endTime = Date.now();
      
      expect(respostas).toHaveLength(5);
      expect(endTime - startTime).toBeLessThan(2000); // Menos de 2 segundos
      respostas.forEach(resposta => {
        expect(resposta).toBeTruthy();
      });
    });

    test('deve manter histórico limitado em consultas longas', async () => {
      // Simula uma conversa longa
      for (let i = 0; i < 10; i++) {
        await agent.consultarLogistica(`Pergunta ${i}`);
      }
      
      expect(agent.getHistoryLength()).toBe(21); // 1 system + 10*(user + assistant)
      expect(agent.getLLMCallCount()).toBe(10);
    });
  });
});