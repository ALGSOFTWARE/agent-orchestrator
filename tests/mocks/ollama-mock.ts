// Mock para ChatOllama - simula respostas do modelo LLM
import type { MockLLMResponse, MockMessage, OllamaConfig } from '@/types';

export const mockOllamaResponses = {
  cteConsulta: `Como assistente especializado da plataforma MIT Tracking, posso ajudar com consultas sobre CT-e.

Para consultar o status do seu CT-e:

1. **Sistema MIT Tracking**: Acesse a plataforma oficial
2. **Informações disponíveis**: Status, localização, ETA/ETD
3. **Interpretação de status**: Embarque, trânsito, entrega
4. **Atualizações**: Notificações em tempo real

Para o número CT-e específico, recomendo acessar o sistema diretamente para informações atualizadas.`,

  blConsulta: `O BL (Bill of Lading) pode ser consultado através do sistema MIT Tracking:

1. Digite o número do BL na busca
2. Verifique o status atual da carga
3. Consulte documentos associados
4. Acompanhe a localização em tempo real`,

  containerStatus: `Status do container disponível no MIT Tracking:

- **Em trânsito**: Container em movimento
- **No porto**: Aguardando embarque/desembarque  
- **Entregue**: Carga entregue ao destinatário
- **Atraso**: Possível atraso na programação`,

  etaConsulta: `ETA (Estimated Time of Arrival) pode ser consultado:

1. Sistema MIT Tracking mostra previsões atualizadas
2. Considera condições de tráfego e clima
3. Notificações automáticas de mudanças
4. Histórico de atualizações disponível`,

  genericError: `Desculpe, houve um problema ao processar sua consulta. Tente novamente ou contate o suporte técnico.`
};

export class MockChatOllama {
  private readonly config: OllamaConfig;
  private callCount: number;

  constructor(config: OllamaConfig) {
    this.config = config;
    this.callCount = 0;
  }

  async invoke(messages: MockMessage[]): Promise<MockLLMResponse> {
    this.callCount++;
    
    // Simula delay do modelo real
    await new Promise(resolve => setTimeout(resolve, 100));

    const lastMessage = messages[messages.length - 1];
    if (!lastMessage) {
      throw new Error('No messages provided');
    }
    const userInput = lastMessage.content.toLowerCase();

    // Determina resposta baseada na entrada
    let response;
    if (userInput.includes('ct-e') || userInput.includes('cte')) {
      response = mockOllamaResponses.cteConsulta;
    } else if (userInput.includes('bl') || userInput.includes('bill of lading')) {
      response = mockOllamaResponses.blConsulta;
    } else if (userInput.includes('container') || userInput.includes('status')) {
      response = mockOllamaResponses.containerStatus;
    } else if (userInput.includes('eta') || userInput.includes('etd')) {
      response = mockOllamaResponses.etaConsulta;
    } else if (userInput.includes('erro') || userInput.includes('error')) {
      throw new Error('Simulated LLM error');
    } else {
      response = `Como assistente MIT Tracking, posso ajudar com consultas sobre logística, CT-e, BL, containers e rastreamento. Sua pergunta: "${userInput}"`;
    }

    return {
      content: response,
      additional_kwargs: {},
      response_metadata: {
        model: this.config.model,
        finish_reason: 'stop'
      }
    };
  }

  getCallCount(): number {
    return this.callCount;
  }

  reset(): void {
    this.callCount = 0;
  }
}

// Mock para SystemMessage e HumanMessage
export class MockSystemMessage implements MockMessage {
  readonly content: string;
  readonly type: 'system' = 'system';

  constructor(content: string) {
    this.content = content;
  }
}

export class MockHumanMessage implements MockMessage {
  readonly content: string;
  readonly type: 'human' = 'human';

  constructor(content: string) {
    this.content = content;
  }
}