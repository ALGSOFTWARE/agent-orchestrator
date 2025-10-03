// 🪝 MIT Logistics Frontend - Authenticated Chat Hook
// Hook React para gerenciar estado e operações do chat autenticado

import { useState, useEffect, useCallback } from 'react'
import {
  authenticatedChatService,
  type AuthenticatedChatMessage,
  type ChatSession,
  type ChatAgent,
  type ChatRequest,
  type ChatResponse,
  type ChatOrderSummary
} from '../authenticatedChat'
import { useAuthStore } from '@/lib/store/auth'

// === HOOK STATE TYPES === //

interface ChatState {
  messages: AuthenticatedChatMessage[]
  sessions: ChatSession[]
  agents: ChatAgent[]
  currentSession: ChatSession | null
  selectedAgent: string
  orders: ChatOrderSummary[]
  selectedOrderId: string | null
  isLoading: boolean
  isSending: boolean
  error: string | null
  systemHealth: { status: string; details: Record<string, any> } | null
}

interface ChatActions {
  sendMessage: (message: string, agentName?: string) => Promise<void>
  createNewSession: (sessionName?: string) => Promise<void>
  loadSession: (sessionId: string) => Promise<void>
  loadHistory: (sessionId?: string) => Promise<void>
  refreshSessions: () => Promise<void>
  refreshAgents: () => Promise<void>
  setSelectedAgent: (agentName: string) => void
  setSelectedOrder: (orderId: string | null) => void
  refreshOrders: () => Promise<void>
  clearError: () => void
  checkSystemHealth: () => Promise<void>
}

type UseAuthenticatedChatReturn = ChatState & ChatActions

// === CUSTOM HOOK === //

export function useAuthenticatedChat(): UseAuthenticatedChatReturn {
  // Estado do chat
  const [state, setState] = useState<ChatState>({
    messages: [],
    sessions: [],
    agents: [],
    currentSession: null,
    selectedAgent: 'LogisticsAgent',
    orders: [],
    selectedOrderId: null,
    isLoading: false,
    isSending: false,
    error: null,
    systemHealth: null
  })

  // Estado de autenticação
  const { isAuthenticated, user } = useAuthStore()

  // === UTILITY FUNCTIONS === //

  const updateState = useCallback((updates: Partial<ChatState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }, [])

  const handleError = useCallback((error: any, context: string) => {
    console.error(`❌ Erro no chat (${context}):`, error)
    updateState({
      error: error instanceof Error ? error.message : `Erro em ${context}`,
      isLoading: false,
      isSending: false
    })
  }, [updateState])

  // === CHAT ACTIONS === //

  const sendMessage = useCallback(async (message: string, agentName?: string) => {
    if (!isAuthenticated) {
      handleError(new Error('AUTHENTICATION_REQUIRED'), 'sendMessage')
      return
    }

    const trimmed = message.trim()
    if (!trimmed) return

    const tempId = `temp_${Date.now()}`
    setState(prev => ({
      ...prev,
      isSending: true,
      error: null,
      messages: [
        ...prev.messages,
        {
          id: tempId,
          role: 'user',
          content: trimmed,
          timestamp: new Date(),
          metadata: prev.selectedOrderId ? { order_id: prev.selectedOrderId } : undefined
        }
      ]
    }))

    try {
      const request: ChatRequest = {
        message: trimmed,
        session_id: state.currentSession?.session_id || `session_${Date.now()}`,
        agent_name: agentName || state.selectedAgent,
        order_id: state.selectedOrderId || undefined
      }

      const response = await authenticatedChatService.sendMessage(request)

      const agentMessage: AuthenticatedChatMessage = {
        id: response.message_id,
        role: 'assistant',
        content: response.content,
        timestamp: new Date(response.timestamp),
        agent_name: response.agent_name,
        attachments: response.attachments || [],
        metadata: response.metadata || {}
      }

      setState(prev => {
        const withoutTemp = prev.messages.filter(msg => msg.id !== tempId)
        return {
          ...prev,
          messages: [
            ...withoutTemp,
            {
              id: tempId,
              role: 'user',
              content: trimmed,
              timestamp: new Date(),
              metadata: prev.selectedOrderId ? { order_id: prev.selectedOrderId } : undefined
            },
            agentMessage
          ],
          isSending: false
        }
      })

      if (response.session_id !== state.currentSession?.session_id) {
        authenticatedChatService.setCurrentSessionId(response.session_id)
        await refreshSessions()
      }

    } catch (error) {
      setState(prev => ({
        ...prev,
        messages: prev.messages.filter(msg => msg.id !== tempId),
        isSending: false
      }))
      handleError(error, 'sendMessage')
    }
  }, [isAuthenticated, state.currentSession, state.selectedAgent, state.selectedOrderId, refreshSessions, handleError])

  const createNewSession = useCallback(async (sessionName?: string) => {
    if (!isAuthenticated) {
      handleError(new Error('AUTHENTICATION_REQUIRED'), 'createNewSession')
      return
    }

    updateState({ isLoading: true, error: null })

    try {
      const session = await authenticatedChatService.createSession(sessionName)

      updateState({
        currentSession: session,
        messages: [], // Limpar mensagens para nova sessão
        isLoading: false
      })

      await refreshSessions()
    } catch (error) {
      handleError(error, 'createNewSession')
    }
  }, [isAuthenticated, handleError, updateState])

  const loadSession = useCallback(async (sessionId: string) => {
    if (!isAuthenticated) {
      handleError(new Error('AUTHENTICATION_REQUIRED'), 'loadSession')
      return
    }

    updateState({ isLoading: true, error: null })

    try {
      // Definir sessão atual
      authenticatedChatService.setCurrentSessionId(sessionId)

      // Encontrar sessão nos dados locais
      const session = state.sessions.find(s => s.session_id === sessionId)
      if (session) {
        updateState({ currentSession: session })
      }

      // Carregar histórico da sessão
      await loadHistory(sessionId)
    } catch (error) {
      handleError(error, 'loadSession')
    }
  }, [isAuthenticated, state.sessions, handleError, updateState])

  const loadHistory = useCallback(async (sessionId?: string) => {
    if (!isAuthenticated) {
      handleError(new Error('AUTHENTICATION_REQUIRED'), 'loadHistory')
      return
    }

    updateState({ isLoading: true, error: null })

    try {
      const messages = await authenticatedChatService.getChatHistory(sessionId)
      updateState({
        messages,
        isLoading: false
      })
    } catch (error) {
      handleError(error, 'loadHistory')
    }
  }, [isAuthenticated, handleError, updateState])

  const refreshSessions = useCallback(async () => {
    if (!isAuthenticated) return

    try {
      const sessions = await authenticatedChatService.getUserSessions()
      updateState({ sessions })
    } catch (error) {
      handleError(error, 'refreshSessions')
    }
  }, [isAuthenticated, handleError, updateState])

  const refreshAgents = useCallback(async () => {
    try {
      const agents = await authenticatedChatService.getAvailableAgents()
      updateState({ agents })
    } catch (error) {
      handleError(error, 'refreshAgents')
    }
  }, [handleError, updateState])

  const setSelectedAgent = useCallback((agentName: string) => {
    updateState({ selectedAgent: agentName })
  }, [updateState])

  const setSelectedOrder = useCallback((orderId: string | null) => {
    setState(prev => ({ ...prev, selectedOrderId: orderId }))
  }, [])

  const refreshOrders = useCallback(async () => {
    if (!isAuthenticated) {
      setState(prev => ({ ...prev, orders: [], selectedOrderId: null }))
      return
    }

    try {
      const orders = await authenticatedChatService.listOrders()
      setState(prev => ({
        ...prev,
        orders,
        selectedOrderId: prev.selectedOrderId ?? orders[0]?.order_id ?? null
      }))
    } catch (error) {
      console.error('❌ Erro ao atualizar orders do chat:', error)
    }
  }, [isAuthenticated])

  const clearError = useCallback(() => {
    updateState({ error: null })
  }, [updateState])

  const checkSystemHealth = useCallback(async () => {
    try {
      const health = await authenticatedChatService.getSystemHealth()
      updateState({ systemHealth: health })
    } catch (error) {
      updateState({
        systemHealth: {
          status: 'offline',
          details: { error: 'Sistema indisponível' }
        }
      })
    }
  }, [updateState])

  // === EFFECTS === //

  // Inicialização quando usuário autentica
  useEffect(() => {
    if (isAuthenticated && user) {
      void refreshSessions()
      void refreshAgents()
      void refreshOrders()
      void checkSystemHealth()
    } else {
      setState({
        messages: [],
        sessions: [],
        agents: [],
        currentSession: null,
        selectedAgent: 'LogisticsAgent',
        orders: [],
        selectedOrderId: null,
        isLoading: false,
        isSending: false,
        error: null,
        systemHealth: null
      })
    }
  }, [isAuthenticated, user, refreshSessions, refreshAgents, refreshOrders, checkSystemHealth])

  // Verificar saúde do sistema periodicamente
  useEffect(() => {
    if (!isAuthenticated) return

    const interval = setInterval(checkSystemHealth, 60000) // A cada minuto
    return () => clearInterval(interval)
  }, [isAuthenticated, checkSystemHealth])

  // === RETURN HOOK INTERFACE === //

  return {
    // Estado
    messages: state.messages,
    sessions: state.sessions,
    agents: state.agents,
    currentSession: state.currentSession,
    selectedAgent: state.selectedAgent,
    orders: state.orders,
    selectedOrderId: state.selectedOrderId,
    isLoading: state.isLoading,
    isSending: state.isSending,
    error: state.error,
    systemHealth: state.systemHealth,

    // Ações
    sendMessage,
    createNewSession,
    loadSession,
    loadHistory,
    refreshSessions,
    refreshAgents,
    setSelectedAgent,
    setSelectedOrder,
    refreshOrders,
    clearError,
    checkSystemHealth
  }
}

// === UTILITIES === //

export function getAgentStatusColor(status: string): string {
  switch (status) {
    case 'healthy': return 'text-green-500'
    case 'degraded': return 'text-yellow-500'
    case 'offline': return 'text-red-500'
    default: return 'text-gray-500'
  }
}

export function getAgentStatusIcon(status: string): string {
  switch (status) {
    case 'healthy': return '🟢'
    case 'degraded': return '🟡'
    case 'offline': return '🔴'
    default: return '⚫'
  }
}
