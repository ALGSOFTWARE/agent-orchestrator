// 🔐 MIT Logistics Frontend - Authenticated Chat Component
// Interface de chat integrada com agentes IA do backend

'use client'

import { useState, useRef, useEffect } from 'react'
import { useAuthenticatedChat, getAgentStatusColor, getAgentStatusIcon } from '@/services/hooks/useAuthenticatedChat'
import { useCurrentUser } from '@/lib/store/auth'
import styles from '@/styles/pages/ChatPlayground.module.css'

// === COMPONENT TYPES === //

interface AuthenticatedChatProps {
  className?: string
  initialSessionId?: string
  showHeader?: boolean
  showSidebar?: boolean
}

// === MAIN COMPONENT === //

export default function AuthenticatedChat({
  className = '',
  initialSessionId,
  showHeader = true,
  showSidebar = true
}: AuthenticatedChatProps) {
  // Hooks
  const user = useCurrentUser()
  const {
    messages,
    sessions,
    agents,
    currentSession,
    selectedAgent,
    orders,
    selectedOrderId,
    isLoading,
    isSending,
    error,
    systemHealth,
    sendMessage,
    createNewSession,
    loadSession,
    refreshSessions,
    refreshAgents,
    setSelectedAgent,
    setSelectedOrder,
    refreshOrders,
    clearError,
    checkSystemHealth
  } = useAuthenticatedChat()

  // Estado local
  const [inputMessage, setInputMessage] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [showSessionList, setShowSessionList] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const selectedOrder = selectedOrderId
    ? orders.find(order => order.order_id === selectedOrderId)
    : undefined

  // === EFFECTS === //

  // Auto-scroll para última mensagem
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Carregar sessão inicial se fornecida
  useEffect(() => {
    if (initialSessionId && !currentSession) {
      loadSession(initialSessionId)
    }
  }, [initialSessionId, currentSession, loadSession])

  // === HANDLERS === //

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isSending) return

    const message = inputMessage.trim()
    setInputMessage('')
    await sendMessage(message, selectedAgent)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleCreateSession = async () => {
    const sessionName = prompt('Nome da nova conversa (opcional):')
    if (sessionName !== null) { // null = cancelado, '' = OK sem nome
      await createNewSession(sessionName || undefined)
      setShowSessionList(false)
    }
  }

  const handleLoadSession = async (sessionId: string) => {
    await loadSession(sessionId)
    setShowSessionList(false)
  }

  const handleRefreshSystem = async () => {
    await Promise.all([
      refreshSessions(),
      refreshAgents(),
      refreshOrders(),
      checkSystemHealth()
    ])
  }

  // === ERROR DISPLAY === //

  if (error === 'Autenticação necessária para acessar o chat') {
    return (
      <div className={`${styles.container} ${className}`}>
        <div className={styles.authRequired}>
          <h2>🔐 Autenticação Necessária</h2>
          <p>Para acessar o chat com agentes IA, você precisa estar logado.</p>
          <p>Use o sistema de autenticação para fazer login.</p>
        </div>
      </div>
    )
  }

  // === RENDER === //

  return (
    <div className={`${styles.container} ${className}`}>
      {/* Header */}
      {showHeader && (
        <div className={styles.header}>
          <div className={styles.headerContent}>
            <h1 className={styles.title}>
              <span className={styles.icon}>🤖</span>
              Chat Inteligente
              {user && <span className={styles.userBadge}>({user.role})</span>}
            </h1>
            <p className={styles.subtitle}>
              Conversas com agentes IA especializados em logística
            </p>
          </div>

          <div className={styles.headerActions}>
            {/* Status do Sistema */}
            <div className={styles.systemStatus}>
              <button
                onClick={checkSystemHealth}
                className={`${styles.statusButton} ${systemHealth?.status === 'healthy' ? styles.statusHealthy : styles.statusDegraded}`}
                title={`Sistema: ${systemHealth?.status || 'verificando'}`}
              >
                {systemHealth?.status === 'healthy' ? '🟢' : systemHealth?.status === 'degraded' ? '🟡' : '🔴'}
                {systemHealth?.status || 'offline'}
              </button>
            </div>

            {/* Sessões */}
            <button
              className={styles.configButton}
              onClick={() => setShowSessionList(!showSessionList)}
              title="Gerenciar sessões"
            >
              📂 Sessões ({sessions.length})
            </button>

            {/* Configurações */}
            <button
              className={styles.configButton}
              onClick={() => setShowSettings(!showSettings)}
              title="Configurações"
            >
              ⚙️ Config
            </button>

            {/* Atualizar */}
            <button
              className={styles.clearButton}
              onClick={handleRefreshSystem}
              disabled={isLoading}
              title="Atualizar sistema"
            >
              {isLoading ? '🔄' : '↻'} Atualizar
            </button>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className={styles.errorBanner}>
          <span>❌ {error}</span>
          <button onClick={clearError} className={styles.errorClose}>✕</button>
        </div>
      )}

      <div className={styles.chatLayout}>
        {/* Sidebar - Lista de Sessões */}
        {showSidebar && showSessionList && (
          <div className={styles.sidebar}>
            <div className={styles.sidebarHeader}>
              <h3>Conversas</h3>
              <button
                onClick={handleCreateSession}
                className={styles.newSessionButton}
                title="Nova conversa"
              >
                ➕ Nova
              </button>
            </div>

            <div className={styles.sessionList}>
              {sessions.map(session => (
                <div
                  key={session.session_id}
                  className={`${styles.sessionItem} ${
                    currentSession?.session_id === session.session_id ? styles.sessionActive : ''
                  }`}
                  onClick={() => handleLoadSession(session.session_id)}
                >
                  <div className={styles.sessionName}>
                    {session.session_name || 'Conversa sem título'}
                  </div>
                  <div className={styles.sessionMeta}>
                    {session.message_count} msgs • {session.agents_used?.join(', ') || 'Agente padrão'}
                  </div>
                  <div className={styles.sessionDate}>
                    {new Date(session.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}

              {sessions.length === 0 && (
                <div className={styles.emptyState}>
                  <p>Nenhuma conversa ainda</p>
                  <button onClick={handleCreateSession} className={styles.startChatButton}>
                    Iniciar primeira conversa
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Main Chat Area */}
        <div className={styles.chatMain}>
          {/* Settings Panel */}
          {showSettings && (
            <div className={styles.configPanel}>
              <div className={styles.configHeader}>
                <h3>Configurações do Chat</h3>
                <button
                  onClick={() => setShowSettings(false)}
                  className={styles.configClose}
                >
                  ✕
                </button>
              </div>

              <div className={styles.configGrid}>
                <div className={styles.configGroup}>
                  <label>Agente Selecionado</label>
                  <select
                    value={selectedAgent}
                    onChange={(e) => setSelectedAgent(e.target.value)}
                    className={styles.agentSelect}
                  >
                    {agents.map(agent => (
                      <option key={agent.name} value={agent.name}>
                        {getAgentStatusIcon(agent.status)} {agent.display_name}
                      </option>
                    ))}
                  </select>

                  {/* Info do agente selecionado */}
                  {(() => {
                    const agent = agents.find(a => a.name === selectedAgent)
                    return agent ? (
                      <div className={styles.agentInfo}>
                        <p className={styles.agentDescription}>{agent.description}</p>
                        <p className={`${styles.agentStatus} ${getAgentStatusColor(agent.status)}`}>
                          Status: {agent.status}
                        </p>
                        <div className={styles.agentCapabilities}>
                          <strong>Capacidades:</strong>
                          <ul>
                            {agent.capabilities.map((cap, i) => (
                              <li key={i}>{cap}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    ) : null
                  })()}
                </div>

                <div className={styles.configGroup}>
                  <label>Order foco da conversa</label>
                  <div className={styles.orderSelector}>
                    <select
                      value={selectedOrderId ?? ''}
                      onChange={(e) => setSelectedOrder(e.target.value || null)}
                      className={styles.agentSelect}
                    >
                      <option value="">Todas as orders</option>
                      {orders.map(order => (
                        <option key={order.order_id} value={order.order_id}>
                          {order.title || order.order_id}
                          {order.customer_name ? ` • ${order.customer_name}` : ''}
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={() => refreshOrders()}
                      className={styles.orderRefreshButton}
                      title="Atualizar lista de orders"
                      type="button"
                    >
                      ↻
                    </button>
                  </div>
                  {selectedOrder ? (
                    <div className={styles.orderInfo}>
                      <p><strong>{selectedOrder.title}</strong></p>
                      {selectedOrder.customer_name && (
                        <p>Cliente: {selectedOrder.customer_name}</p>
                      )}
                      {selectedOrder.status && (
                        <p>Status: {selectedOrder.status}</p>
                      )}
                    </div>
                  ) : (
                    <div className={styles.orderInfoMuted}>
                      <p>Nenhuma order específica selecionada. As respostas considerarão todas as orders.</p>
                    </div>
                  )}
                </div>

                <div className={styles.configGroup}>
                  <label>Sessão Atual</label>
                  <div className={styles.currentSession}>
                    {currentSession ? (
                      <>
                        <p><strong>{currentSession.session_name}</strong></p>
                        <p>Criada em: {new Date(currentSession.created_at).toLocaleString()}</p>
                        <p>Mensagens: {currentSession.message_count}</p>
                      </>
                    ) : (
                      <p>Nenhuma sessão ativa</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Messages Area */}
          <div className={styles.messagesContainer}>
            {messages.length === 0 ? (
              <div className={styles.welcomeMessage}>
                <div className={styles.welcomeContent}>
                  <h2>👋 Olá, {user?.userName || 'usuário'}!</h2>
                  <p>Como posso ajudar com suas operações logísticas hoje?</p>

                  <div className={styles.suggestionChips}>
                    <button
                      onClick={() => setInputMessage('Rastrear minha carga')}
                      className={styles.suggestionChip}
                    >
                      📍 Rastrear carga
                    </button>
                    <button
                      onClick={() => setInputMessage('Status dos meus embarques')}
                      className={styles.suggestionChip}
                    >
                      📋 Status embarques
                    </button>
                    <button
                      onClick={() => setInputMessage('Consultar CT-e')}
                      className={styles.suggestionChip}
                    >
                      📄 Consultar CT-e
                    </button>
                    <button
                      onClick={() => setInputMessage('Relatório de entregas')}
                      className={styles.suggestionChip}
                    >
                      📊 Relatórios
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className={styles.messagesList}>
                {messages.map((message, index) => (
                  <div
                    key={message.id}
                    className={`${styles.message} ${
                      message.role === 'user' ? styles.userMessage : styles.assistantMessage
                    }`}
                  >
                    <div className={styles.messageHeader}>
                      <span className={styles.messageRole}>
                        {message.role === 'user' ? (
                          <>👤 Você</>
                        ) : (
                          <>🤖 {message.agent_name || 'Agente'}</>
                        )}
                      </span>
                      <span className={styles.messageTime}>
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>

                    <div className={styles.messageContent}>
                      {message.content}
                    </div>

                    {/* Attachments */}
                    {message.attachments && message.attachments.length > 0 && (
                      <div className={styles.messageAttachments}>
                        {message.attachments.map((attachment, i) => (
                          <div key={i} className={styles.attachment}>
                            📎 {attachment.name}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}

                {/* Loading indicator */}
                {isSending && (
                  <div className={`${styles.message} ${styles.assistantMessage} ${styles.loadingMessage}`}>
                    <div className={styles.messageHeader}>
                      <span className={styles.messageRole}>🤖 {selectedAgent}</span>
                    </div>
                    <div className={styles.messageContent}>
                      <div className={styles.typingIndicator}>
                        <span></span><span></span><span></span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className={styles.inputContainer}>
            <div className={styles.selectedContextBar}>
              <div className={styles.contextLabel}>
                📦 Contexto:
                {selectedOrder ? (
                  <span className={styles.contextBadge}>
                    {selectedOrder.title || selectedOrder.order_id}
                    {selectedOrder.customer_name ? ` • ${selectedOrder.customer_name}` : ''}
                  </span>
                ) : (
                  <span className={styles.contextNeutral}>todas as orders</span>
                )}
              </div>
              {selectedOrder && (
                <button
                  type="button"
                  onClick={() => setSelectedOrder(null)}
                  className={styles.clearContextButton}
                >
                  Limpar contexto
                </button>
              )}
            </div>
            <div className={styles.inputArea}>
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder={`Enviar mensagem para ${agents.find(a => a.name === selectedAgent)?.display_name || 'agente'}...`}
                rows={3}
                disabled={isSending}
                className={styles.messageInput}
              />

              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isSending}
                className={styles.sendButton}
              >
                {isSending ? '⏳' : '📤'} Enviar
              </button>
            </div>

            <div className={styles.inputHint}>
              🔒 Chat seguro e autenticado • Pressione Enter para enviar, Shift+Enter para nova linha
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
