// 🔐 MIT Logistics Frontend - Authenticated Chat Service
// Serviço para comunicação com agentes IA através do Gatekeeper API

import { gatekeeperClient } from '@/lib/api/client'
import { useAuthStore } from '@/lib/store/auth'

// === TYPES === //

export interface AuthenticatedChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  agent_name?: string
  attachments?: ChatAttachment[]
  metadata?: Record<string, any>
}

export interface ChatAttachment {
  name: string
  type: string
  size: number
  url?: string
}

export interface ChatRequest {
  message: string
  session_id?: string
  agent_name?: string
  attachments?: File[]
  order_id?: string
}

export interface ChatResponse {
  message_id: string
  content: string
  agent_name: string
  timestamp: string
  session_id: string
  attachments?: ChatAttachment[]
  metadata?: Record<string, any>
}

export interface ChatSession {
  session_id: string
  session_name: string
  created_at: string
  message_count: number
  last_activity: string
  agents_used: string[]
}

export interface ChatAgent {
  name: string
  display_name: string
  description: string
  status: 'healthy' | 'degraded' | 'offline'
  capabilities: string[]
}

export interface ChatOrderSummary {
  order_id: string
  title: string
  status?: string
  customer_name?: string
  priority?: number
}

// === AUTHENTICATED CHAT SERVICE === //

export class AuthenticatedChatService {
  private static instance: AuthenticatedChatService
  private currentSessionId: string | null = null

  private constructor() {}

  static getInstance(): AuthenticatedChatService {
    if (!this.instance) {
      this.instance = new AuthenticatedChatService()
    }
    return this.instance
  }

  // === SESSION MANAGEMENT === //

  async createSession(sessionName?: string): Promise<ChatSession> {
    try {
      this.validateAuthentication()

      const response = await gatekeeperClient.postRaw<ChatSession>('/chat/session', {
        session_name: sessionName
      })

      this.currentSessionId = response.session_id
      return response
    } catch (error) {
      console.error('❌ Erro ao criar sessão de chat:', error)
      throw this.handleError(error, 'Falha ao criar nova sessão de chat')
    }
  }

  async getUserSessions(daysBack: number = 30): Promise<ChatSession[]> {
    try {
      this.validateAuthentication()

      const response = await gatekeeperClient.getRaw<{sessions: ChatSession[]}>('/chat/sessions', {
        params: { days_back: daysBack }
      })

      return response.sessions || []
    } catch (error) {
      console.error('❌ Erro ao buscar sessões:', error)
      throw this.handleError(error, 'Falha ao carregar histórico de sessões')
    }
  }

  getCurrentSessionId(): string | null {
    return this.currentSessionId
  }

  setCurrentSessionId(sessionId: string): void {
    this.currentSessionId = sessionId
  }

  // === MESSAGE HANDLING === //

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      this.validateAuthentication()

      // Usar sessão atual ou criar nova se necessário
      const sessionId = request.session_id || this.currentSessionId || await this.createDefaultSession()

      // Preparar payload
      const payload = {
        message: request.message,
        session_id: sessionId,
        agent_name: request.agent_name || 'LogisticsAgent',
        order_id: request.order_id
      }

      const response = await gatekeeperClient.postRaw<ChatResponse>('/chat/message', payload)

      // Atualizar sessão atual
      this.currentSessionId = response.session_id

      return response
    } catch (error) {
      console.error('❌ Erro ao enviar mensagem:', error)
      throw this.handleError(error, 'Falha ao processar mensagem')
    }
  }

  async getChatHistory(sessionId?: string, limit: number = 50): Promise<AuthenticatedChatMessage[]> {
    try {
      this.validateAuthentication()

      const params: any = { limit }
      if (sessionId) params.session_id = sessionId

      const response = await gatekeeperClient.getRaw<{messages: any[]}>('/chat/history', {
        params
      })

      return this.formatMessages(response.messages || [])
    } catch (error) {
      console.error('❌ Erro ao buscar histórico:', error)
      throw this.handleError(error, 'Falha ao carregar histórico de conversas')
    }
  }

  // === AGENT MANAGEMENT === //

  async getAvailableAgents(): Promise<ChatAgent[]> {
    try {
      const response = await gatekeeperClient.getRaw<{available_agents: any[]}>('/chat/agents')

      return response.available_agents?.map(agent => ({
        name: agent.name,
        display_name: agent.display_name || agent.name,
        description: agent.description || 'Agente especializado',
        status: agent.status || 'offline',
        capabilities: this.getAgentCapabilities(agent.name)
      })) || []
    } catch (error) {
      console.error('❌ Erro ao buscar agentes:', error)
      // Retornar agentes padrão como fallback
      return this.getDefaultAgents()
    }
  }

  async getSystemHealth(): Promise<{status: string, details: Record<string, any>}> {
    try {
      const response = await gatekeeperClient.getRaw<any>('/chat/health')
      return {
        status: response.status || 'unknown',
        details: response
      }
    } catch (error) {
      console.error('❌ Erro no health check:', error)
      return {
        status: 'offline',
        details: { error: 'Sistema indisponível' }
      }
    }
  }

  async listOrders(limit: number = 25): Promise<ChatOrderSummary[]> {
    this.validateAuthentication()

    try {
      const response = await gatekeeperClient.getRaw<any[]>(
        '/orders/',
        { params: { limit } }
      )

      return (response || []).map((order) => ({
        order_id: order.order_id,
        title: order.title || order.order_number || order.order_id,
        status: order.status,
        customer_name: order.customer_name,
        priority: order.priority
      }))
    } catch (error) {
      console.error('❌ Erro ao listar orders para o chat:', error)
      throw this.handleError(error, 'Falha ao carregar orders disponíveis')
    }
  }

  // === UTILITY METHODS === //

  private validateAuthentication(): void {
    const { isAuthenticated, user } = useAuthStore.getState()

    if (!isAuthenticated || !user) {
      throw new Error('AUTHENTICATION_REQUIRED')
    }
  }

  private async createDefaultSession(): Promise<string> {
    const session = await this.createSession('Nova Conversa')
    return session.session_id
  }

  private formatMessages(messages: any[]): AuthenticatedChatMessage[] {
    return messages.map(msg => ({
      id: msg.id || `msg_${Date.now()}_${Math.random()}`,
      role: msg.type === 'user' ? 'user' : 'assistant',
      content: msg.content,
      timestamp: new Date(msg.timestamp),
      agent_name: msg.agent_name,
      attachments: msg.attachments || [],
      metadata: msg.metadata || {}
    }))
  }

  private getAgentCapabilities(agentName: string): string[] {
    const capabilities: Record<string, string[]> = {
      'LogisticsAgent': [
        'Rastreamento de cargas',
        'Consulta de documentos CT-e',
        'Status de entregas',
        'Análise de rotas'
      ],
      'AdminAgent': [
        'Administração do sistema',
        'Relatórios gerenciais',
        'Configurações avançadas'
      ],
      'FinanceAgent': [
        'Análises financeiras',
        'Custos logísticos',
        'Relatórios de pagamento'
      ]
    }

    return capabilities[agentName] || ['Funcionalidades gerais']
  }

  private getDefaultAgents(): ChatAgent[] {
    return [
      {
        name: 'LogisticsAgent',
        display_name: 'Agente Logístico',
        description: 'Especialista em operações logísticas e rastreamento',
        status: 'offline',
        capabilities: this.getAgentCapabilities('LogisticsAgent')
      },
      {
        name: 'AdminAgent',
        display_name: 'Agente Administrativo',
        description: 'Administração e configurações do sistema',
        status: 'offline',
        capabilities: this.getAgentCapabilities('AdminAgent')
      }
    ]
  }

  private handleError(error: any, defaultMessage: string): Error {
    // Tratar diferentes tipos de erro de forma consistente
    if (error?.message === 'AUTHENTICATION_REQUIRED') {
      return new Error('Autenticação necessária para acessar o chat')
    }

    if (error?.code === 401) {
      return new Error('Sessão expirada. Faça login novamente')
    }

    if (error?.code === 403) {
      return new Error('Sem permissão para acessar esta funcionalidade')
    }

    if (error?.code === 0 || error?.message?.includes('network')) {
      return new Error('Sistema temporariamente indisponível. Tente novamente em alguns instantes')
    }

    return new Error(error?.message || defaultMessage)
  }
}

// === SINGLETON EXPORT === //
export const authenticatedChatService = AuthenticatedChatService.getInstance()
