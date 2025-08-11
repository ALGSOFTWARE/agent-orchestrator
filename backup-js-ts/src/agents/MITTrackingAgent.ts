import { ChatOllama } from "@langchain/community/chat_models/ollama";
import {
  HumanMessage,
  SystemMessage,
  BaseMessage,
} from "@langchain/core/messages";
import type {
  OllamaConfig,
  LogisticsQuery,
  AgentResponse,
  ConversationHistory,
  AgentStats,
} from "@/types";
import { AgentState } from "@/types";

export class MITTrackingAgent {
  private readonly llm: ChatOllama;
  private readonly systemPrompt: string;
  private conversationHistory: BaseMessage[];
  private stats: AgentStats;
  private state: AgentState;
  private readonly sessionId: string;
  private readonly startTime: Date;

  constructor(
    ollamaConfig: OllamaConfig = {
      baseUrl: "http://localhost:11434",
      model: "llama3.2:3b",
      temperature: 0.3,
    }
  ) {
    this.state = AgentState.INITIALIZING;

    this.llm = new ChatOllama({
      baseUrl: ollamaConfig.baseUrl,
      model: ollamaConfig.model,
      temperature: ollamaConfig.temperature,
    });

    this.systemPrompt = `Você é um assistente especializado da plataforma MIT Tracking da Move In Tech. 

Sua expertise inclui:
- Consulta e interpretação de CT-e (Conhecimento de Transporte Eletrônico)
- Consulat a Rastreamento em tempo real de containers e cargas
- Consulta a Informações sobre BL (Bill of Lading/Conhecimento de Embarque)
- Consulta a Cálculos e previsões de ETA (Estimated Time of Arrival) e ETD (Estimated Time of Departure)
- Consulta a Status de entregas e tracking logístico
- Comsulta a Identificação de atrasos e eventos de rota

Você deve responder especificamente sobre:
- Números de CT-e quando questionado
- Status atual de containers e cargas
- Localização de documentos logísticos
- Previsões de chegada e saída

Sempre mantenha um tom profissional e técnico, fornecendo informações claras e objetivas sobre logística e transporte.
Responda sempre em português, de forma clara e concisa.`;

    this.conversationHistory = [new SystemMessage(this.systemPrompt)];
    this.sessionId = this.generateSessionId();
    this.startTime = new Date();

    this.stats = {
      totalQueries: 0,
      successfulQueries: 0,
      errorCount: 0,
      averageResponseTime: 0,
      sessionDuration: 0,
    };

    this.state = AgentState.READY;
  }

  private generateSessionId(): string {
    return `mit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private updateStats(responseTime: number, success: boolean): void {
    this.stats.totalQueries++;

    if (success) {
      this.stats.successfulQueries++;
    } else {
      this.stats.errorCount++;
    }

    // Calcula média móvel do tempo de resposta
    this.stats.averageResponseTime =
      (this.stats.averageResponseTime * (this.stats.totalQueries - 1) +
        responseTime) /
      this.stats.totalQueries;

    this.stats.sessionDuration = Date.now() - this.startTime.getTime();
  }

  public async consultarLogistica(consulta: string): Promise<string> {
    if (this.state !== AgentState.READY) {
      throw new Error(`Agente não está pronto. Estado atual: ${this.state}`);
    }

    if (!consulta || consulta.trim().length === 0) {
      throw new Error("Consulta não pode estar vazia");
    }

    this.state = AgentState.PROCESSING;
    const startTime = Date.now();

    try {
      console.log("\n🔍 Processando sua consulta...");

      // Adiciona a nova pergunta ao histórico
      this.conversationHistory.push(new HumanMessage(consulta.trim()));

      const response = await this.llm.invoke(this.conversationHistory);

      // Adiciona a resposta ao histórico para manter contexto
      this.conversationHistory.push(response);

      const responseTime = Date.now() - startTime;
      this.updateStats(responseTime, true);
      this.state = AgentState.READY;

      return response.content as string;
    } catch (error) {
      const responseTime = Date.now() - startTime;
      this.updateStats(responseTime, false);
      this.state = AgentState.ERROR;

      const errorMessage =
        error instanceof Error ? error.message : "Erro desconhecido";
      console.error("❌ Erro ao consultar:", errorMessage);

      // Retorna ao estado pronto após erro
      setTimeout(() => {
        this.state = AgentState.READY;
      }, 1000);

      return `Erro ao processar consulta: ${errorMessage}`;
    }
  }

  public limparHistorico(): void {
    this.conversationHistory = [new SystemMessage(this.systemPrompt)];
    console.log("🧹 Histórico da conversa limpo!");
  }

  public getHistoryLength(): number {
    return this.conversationHistory.length;
  }

  public getStats(): Readonly<AgentStats> {
    return { ...this.stats };
  }

  public getState(): AgentState {
    return this.state;
  }

  public getSessionId(): string {
    return this.sessionId;
  }

  public getConversationHistory(): Readonly<ConversationHistory> {
    return {
      messages: [...this.conversationHistory],
      sessionId: this.sessionId,
      startTime: this.startTime,
      lastActivity: new Date(),
    };
  }

  public async processLogisticsQuery(
    query: LogisticsQuery
  ): Promise<AgentResponse> {
    const startTime = Date.now();

    try {
      const response = await this.consultarLogistica(query.content);
      const responseTime = Date.now() - startTime;

      return {
        content: response,
        confidence: this.calculateConfidence(response),
        responseTime,
        sources: ["MIT Tracking Knowledge Base"],
      };
    } catch (error) {
      const responseTime = Date.now() - startTime;
      const errorMessage =
        error instanceof Error ? error.message : "Erro desconhecido";

      return {
        content: `Erro: ${errorMessage}`,
        confidence: 0,
        responseTime,
        sources: [],
      };
    }
  }

  private calculateConfidence(response: string): number {
    // Lógica simples de confiança baseada no comprimento e conteúdo da resposta
    if (response.includes("Erro")) return 0.1;
    if (response.length < 50) return 0.6;
    if (
      response.includes("CT-e") ||
      response.includes("BL") ||
      response.includes("container")
    )
      return 0.9;
    return 0.7;
  }

  public async shutdown(): Promise<void> {
    this.state = AgentState.SHUTDOWN;
    console.log(`🔄 Encerrando sessão ${this.sessionId}...`);
    console.log(`📊 Estatísticas da sessão:`);
    console.log(`   • Total de consultas: ${this.stats.totalQueries}`);
    console.log(
      `   • Consultas bem-sucedidas: ${this.stats.successfulQueries}`
    );
    console.log(`   • Erros: ${this.stats.errorCount}`);
    console.log(
      `   • Tempo médio de resposta: ${this.stats.averageResponseTime.toFixed(
        2
      )}ms`
    );
    console.log(
      `   • Duração da sessão: ${(
        this.stats.sessionDuration /
        1000 /
        60
      ).toFixed(2)} minutos`
    );
  }

  // Método para validação de entrada
  public validateInput(input: string): { isValid: boolean; error?: string } {
    if (!input || input.trim().length === 0) {
      return { isValid: false, error: "Entrada não pode estar vazia" };
    }

    if (input.length > 1000) {
      return {
        isValid: false,
        error: "Entrada muito longa (máximo 1000 caracteres)",
      };
    }

    return { isValid: true };
  }

  // Getter para verificar se o agente está pronto
  public get isReady(): boolean {
    return this.state === AgentState.READY;
  }

  // Getter para verificar se há erros
  public get hasErrors(): boolean {
    return this.stats.errorCount > 0;
  }

  // Getter para taxa de sucesso
  public get successRate(): number {
    if (this.stats.totalQueries === 0) return 0;
    return (this.stats.successfulQueries / this.stats.totalQueries) * 100;
  }
}
