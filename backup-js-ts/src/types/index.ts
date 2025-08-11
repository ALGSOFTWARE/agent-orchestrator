import type { BaseMessage } from '@langchain/core/messages';

// Tipos base para logística
export type DocumentType = 'CTE' | 'BL' | 'CONTAINER' | 'MANIFEST';

export type CargoStatus = 
  | 'EMBARQUE' 
  | 'TRANSITO' 
  | 'PORTO' 
  | 'ENTREGUE' 
  | 'ATRASO' 
  | 'CANCELADO'
  | 'PENDENTE';

export type CommandType = 
  | 'sair' 
  | 'menu' 
  | 'exemplos' 
  | 'limpar' 
  | 'consulta' 
  | 'vazio';

// Interfaces para configuração
export interface OllamaConfig {
  readonly baseUrl: string;
  readonly model: string;
  readonly temperature: number;
  readonly timeout?: number;
}

export interface AgentConfig {
  readonly role: string;
  readonly goal: string;
  readonly backstory: string;
  readonly verbose?: boolean;
}

// Interfaces para documentos logísticos
export interface CTEDocument {
  readonly number: string;
  readonly status: CargoStatus;
  readonly origin: string;
  readonly destination: string;
  readonly eta?: Date;
  readonly etd?: Date;
  readonly carrier: string;
}

export interface BLDocument {
  readonly number: string;
  readonly status: CargoStatus;
  readonly vessel: string;
  readonly port: string;
  readonly discharge: string;
  readonly eta?: Date;
}

export interface ContainerInfo {
  readonly id: string;
  readonly status: CargoStatus;
  readonly location: string;
  readonly route: string;
  readonly eta?: Date;
  readonly etd?: Date;
}

// Interfaces para consultas e respostas
export interface LogisticsQuery {
  readonly content: string;
  readonly type: DocumentType;
  readonly documentNumber?: string;
  readonly timestamp: Date;
}

export interface AgentResponse {
  readonly content: string;
  readonly confidence: number;
  readonly responseTime: number;
  readonly sources?: string[];
}

// Interface para histórico de conversa
export interface ConversationHistory {
  readonly messages: BaseMessage[];
  readonly sessionId: string;
  readonly startTime: Date;
  readonly lastActivity: Date;
}

// Interface para comandos da interface
export interface CommandResult {
  readonly tipo: CommandType;
  readonly mensagem: string;
  readonly dados?: Record<string, unknown>;
}

// Interface para configurações de teste
export interface TestConfig {
  readonly OLLAMA_TIMEOUT: number;
  readonly MOCK_RESPONSES: boolean;
  readonly VERBOSE_LOGS: boolean;
}

// Interface para estatísticas do agente
export interface AgentStats {
  totalQueries: number;
  successfulQueries: number;
  errorCount: number;
  averageResponseTime: number;
  sessionDuration: number;
}

// Interface para mock do LLM
export interface MockLLMResponse {
  readonly content: string;
  readonly additional_kwargs: Record<string, unknown>;
  readonly response_metadata: {
    readonly model: string;
    readonly finish_reason: string;
  };
}

// Interface para mock de mensagens
export interface MockMessage {
  readonly content: string;
  readonly type: 'system' | 'human' | 'ai';
}

// Tipos para eventos da interface
export interface InterfaceEvents {
  readonly userInput: (input: string) => void;
  readonly commandProcessed: (command: CommandResult) => void;
  readonly responseProcessed: (data: { input: string; response: string }) => void;
  readonly error: (error: Error) => void;
  readonly exit: () => void;
}

// Interface para métricas de performance
export interface PerformanceMetrics {
  readonly queryProcessingTime: number;
  readonly llmResponseTime: number;
  readonly totalResponseTime: number;
  readonly memoryUsage: NodeJS.MemoryUsage;
  readonly timestamp: Date;
}

// Tipos utilitários
export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
export type AsyncResult<T> = Promise<T>;

// Interface para configuração de ambiente
export interface EnvironmentConfig {
  readonly NODE_ENV: 'development' | 'production' | 'test';
  readonly OLLAMA_BASE_URL: string;
  readonly OLLAMA_MODEL: string;
  readonly LOG_LEVEL: 'error' | 'warn' | 'info' | 'debug';
  readonly TEST_TIMEOUT?: number;
}

// Interface para validação de entrada
export interface InputValidation {
  readonly isValid: boolean;
  readonly errors: string[];
  readonly sanitizedInput: string;
}

// Enums para melhor type safety
export enum LogLevel {
  ERROR = 'error',
  WARN = 'warn',
  INFO = 'info',
  DEBUG = 'debug'
}

export enum AgentState {
  INITIALIZING = 'initializing',
  READY = 'ready',
  PROCESSING = 'processing',
  ERROR = 'error',
  SHUTDOWN = 'shutdown'
}

// Type guards para runtime checking
export const isCargoStatus = (value: string): value is CargoStatus => {
  return ['EMBARQUE', 'TRANSITO', 'PORTO', 'ENTREGUE', 'ATRASO', 'CANCELADO', 'PENDENTE'].includes(value);
};

export const isDocumentType = (value: string): value is DocumentType => {
  return ['CTE', 'BL', 'CONTAINER', 'MANIFEST'].includes(value);
};

export const isCommandType = (value: string): value is CommandType => {
  return ['sair', 'menu', 'exemplos', 'limpar', 'consulta', 'vazio'].includes(value);
};