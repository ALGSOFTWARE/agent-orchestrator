// 💬 MIT Logistics Frontend - Chat Playground Page

'use client'

import { useState, useEffect, useRef } from 'react'
import { useAvailableModels } from '@/hooks/useAvailableModels'
import styles from '@/styles/pages/ChatPlayground.module.css'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  model?: 'openai' | 'gemini'
}

interface ChatConfig {
  temperature: number
  maxTokens: number
  systemPrompt: string
  openaiModel: string
  geminiModel: string
}

const DEFAULT_SYSTEM_PROMPT = `Você é um assistente especializado em logística e transporte. Você tem acesso a informações sobre:

- CT-e (Conhecimento de Transporte Eletrônico)
- Rastreamento de containers e cargas
- Documentos de transporte (BL, manifesto, etc.)
- Status de entregas e previsões
- Transportadoras e embarcadores

Responda sempre de forma precisa, técnica e focada no contexto logístico. Use terminologia específica do setor quando apropriado.`

export default function ChatPlaygroundPage() {
  const { openaiModels, geminiModels, isLoading: modelsLoading, error: modelsError, lastUpdated, refresh: refreshModels } = useAvailableModels()
  const [config, setConfig] = useState<ChatConfig>({
    temperature: 0.3,
    maxTokens: 1000,
    systemPrompt: DEFAULT_SYSTEM_PROMPT,
    openaiModel: 'gpt-4o-mini',
    geminiModel: 'gemini-1.5-flash'
  })

  // Update default models when available models load
  useEffect(() => {
    if (openaiModels.length > 0 && !openaiModels.find(m => m.id === config.openaiModel)) {
      setConfig(prev => ({ ...prev, openaiModel: openaiModels[0].id }))
    }
    if (geminiModels.length > 0 && !geminiModels.find(m => m.id === config.geminiModel)) {
      setConfig(prev => ({ ...prev, geminiModel: geminiModels[0].id }))
    }
  }, [openaiModels, geminiModels, config.openaiModel, config.geminiModel])

  const [openaiMessages, setOpenaiMessages] = useState<ChatMessage[]>([])
  const [geminiMessages, setGeminiMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState({ openai: false, gemini: false })
  const [showConfig, setShowConfig] = useState(false)

  const openaiRef = useRef<HTMLDivElement>(null)
  const geminiRef = useRef<HTMLDivElement>(null)

  // No authentication required - this is a public sandbox

  // Auto scroll to bottom
  useEffect(() => {
    if (openaiRef.current) {
      openaiRef.current.scrollTop = openaiRef.current.scrollHeight
    }
    if (geminiRef.current) {
      geminiRef.current.scrollTop = geminiRef.current.scrollHeight
    }
  }, [openaiMessages, geminiMessages])

  const sendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    }

    // Add user message to both chats
    setOpenaiMessages(prev => [...prev, userMessage])
    setGeminiMessages(prev => [...prev, userMessage])
    setInputMessage('')
    
    // Set loading states
    setIsLoading({ openai: true, gemini: true })

    // Send to both APIs simultaneously
    await Promise.all([
      sendToOpenAI(userMessage),
      sendToGemini(userMessage)
    ])
  }

  const sendToOpenAI = async (userMessage: ChatMessage) => {
    try {
      const messages = [
        { role: 'system', content: config.systemPrompt },
        ...openaiMessages.map(msg => ({ role: msg.role, content: msg.content })),
        { role: 'user', content: userMessage.content }
      ]

      const response = await fetch('/api/chat/openai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages,
          model: config.openaiModel,
          temperature: config.temperature,
          max_tokens: config.maxTokens
        })
      })

      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.error)
      }

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.content,
        timestamp: new Date(),
        model: 'openai'
      }

      setOpenaiMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('OpenAI Error:', error)
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `❌ Erro OpenAI: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
        timestamp: new Date(),
        model: 'openai'
      }
      setOpenaiMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(prev => ({ ...prev, openai: false }))
    }
  }

  const sendToGemini = async (userMessage: ChatMessage) => {
    try {
      const messages = [
        { role: 'system', content: config.systemPrompt },
        ...geminiMessages.map(msg => ({ role: msg.role, content: msg.content })),
        { role: 'user', content: userMessage.content }
      ]

      const response = await fetch('/api/chat/gemini', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages,
          model: config.geminiModel,
          temperature: config.temperature,
          max_tokens: config.maxTokens
        })
      })

      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.error)
      }

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.content,
        timestamp: new Date(),
        model: 'gemini'
      }

      setGeminiMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Gemini Error:', error)
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `❌ Erro Gemini: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
        timestamp: new Date(),
        model: 'gemini'
      }
      setGeminiMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(prev => ({ ...prev, gemini: false }))
    }
  }

  const clearChats = () => {
    setOpenaiMessages([])
    setGeminiMessages([])
  }

  const resetConfig = () => {
    setConfig({
      temperature: 0.3,
      maxTokens: 1000,
      systemPrompt: DEFAULT_SYSTEM_PROMPT,
      openaiModel: 'gpt-4o-mini',
      geminiModel: 'gemini-1.5-flash'
    })
  }

  // Public sandbox - no authentication required

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>
            <span className={styles.icon}>💬</span>
            Sandbox de Agentes Conversacionais
          </h1>
          <p className={styles.subtitle}>
            Teste e compare agentes OpenAI vs Gemini - Sandbox público para criação de novos agentes
          </p>
        </div>

        <div className={styles.headerActions}>
          <button
            className={styles.configButton}
            onClick={() => setShowConfig(!showConfig)}
          >
            ⚙️ Configurações
          </button>
          <button
            className={styles.clearButton}
            onClick={clearChats}
          >
            🗑️ Limpar
          </button>
        </div>
      </div>

      {/* Configuration Panel */}
      {showConfig && (
        <div className={styles.configPanel}>
          <div className={styles.configHeader}>
            <div className={styles.configHeaderLeft}>
              <h3>Configurações do Chat</h3>
              {lastUpdated && (
                <div className={styles.lastUpdated}>
                  Modelos atualizados: {lastUpdated.toLocaleTimeString()}
                </div>
              )}
            </div>
            <div className={styles.configHeaderRight}>
              <button
                className={styles.refreshModelsButton}
                onClick={refreshModels}
                disabled={modelsLoading}
                title="Atualizar lista de modelos"
              >
                {modelsLoading ? '🔄' : '↻'} Modelos
              </button>
              <button
                className={styles.resetButton}
                onClick={resetConfig}
              >
                Reset
              </button>
            </div>
          </div>

          <div className={styles.configGrid}>
            <div className={styles.configGroup}>
              <label>Temperatura</label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={config.temperature}
                onChange={(e) => setConfig(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
              />
              <span>{config.temperature}</span>
            </div>

            <div className={styles.configGroup}>
              <label>Max Tokens</label>
              <input
                type="number"
                min="100"
                max="4000"
                step="100"
                value={config.maxTokens}
                onChange={(e) => setConfig(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
              />
            </div>

            <div className={styles.configGroup}>
              <label>
                Modelo OpenAI
                {modelsLoading && <span className={styles.loadingSpinner}>🔄</span>}
                {modelsError && <span className={styles.errorIcon} title={modelsError}>⚠️</span>}
              </label>
              <select
                value={config.openaiModel}
                onChange={(e) => setConfig(prev => ({ ...prev, openaiModel: e.target.value }))}
                disabled={modelsLoading}
              >
                {openaiModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name || model.id}
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.configGroup}>
              <label>
                Modelo Gemini
                {modelsLoading && <span className={styles.loadingSpinner}>🔄</span>}
                {modelsError && <span className={styles.errorIcon} title={modelsError}>⚠️</span>}
              </label>
              <select
                value={config.geminiModel}
                onChange={(e) => setConfig(prev => ({ ...prev, geminiModel: e.target.value }))}
                disabled={modelsLoading}
              >
                {geminiModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name || model.id}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className={styles.configGroup}>
            <label>Prompt do Sistema</label>
            <textarea
              value={config.systemPrompt}
              onChange={(e) => setConfig(prev => ({ ...prev, systemPrompt: e.target.value }))}
              rows={6}
              placeholder="Digite o prompt do sistema..."
            />
          </div>
        </div>
      )}

      {/* Chat Interface */}
      <div className={styles.chatContainer}>
        {/* OpenAI Chat */}
        <div className={styles.chatPanel}>
          <div className={styles.chatHeader}>
            <h3>
              <span className={styles.providerIcon}>🤖</span>
              OpenAI ({config.openaiModel})
            </h3>
            {isLoading.openai && <div className={styles.loadingDot}>⚡</div>}
          </div>
          
          <div className={styles.chatMessages} ref={openaiRef}>
            {openaiMessages.map((message, index) => (
              <div
                key={index}
                className={`${styles.message} ${message.role === 'user' ? styles.userMessage : styles.assistantMessage}`}
              >
                <div className={styles.messageContent}>
                  {message.content}
                </div>
                <div className={styles.messageTime}>
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))}
            {isLoading.openai && (
              <div className={`${styles.message} ${styles.assistantMessage} ${styles.loadingMessage}`}>
                <div className={styles.messageContent}>
                  <div className={styles.typingIndicator}>
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Gemini Chat */}
        <div className={styles.chatPanel}>
          <div className={styles.chatHeader}>
            <h3>
              <span className={styles.providerIcon}>💎</span>
              Gemini ({config.geminiModel})
            </h3>
            {isLoading.gemini && <div className={styles.loadingDot}>⚡</div>}
          </div>
          
          <div className={styles.chatMessages} ref={geminiRef}>
            {geminiMessages.map((message, index) => (
              <div
                key={index}
                className={`${styles.message} ${message.role === 'user' ? styles.userMessage : styles.assistantMessage}`}
              >
                <div className={styles.messageContent}>
                  {message.content}
                </div>
                <div className={styles.messageTime}>
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))}
            {isLoading.gemini && (
              <div className={`${styles.message} ${styles.assistantMessage} ${styles.loadingMessage}`}>
                <div className={styles.messageContent}>
                  <div className={styles.typingIndicator}>
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className={styles.inputContainer}>
        <div className={styles.inputArea}>
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Digite sua pergunta sobre logística..."
            rows={3}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                sendMessage()
              }
            }}
          />
          <button
            className={styles.sendButton}
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading.openai || isLoading.gemini}
          >
            {isLoading.openai || isLoading.gemini ? '⏳' : '📤'} Enviar
          </button>
        </div>
        
        <div className={styles.inputHint}>
          💡 Sandbox público - Teste e compare agentes • Pressione Enter para enviar, Shift+Enter para nova linha
        </div>
      </div>
    </div>
  )
}