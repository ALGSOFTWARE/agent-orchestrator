// 🧪 MIT Logistics Frontend - Agent Tester Component

'use client'

import { useState, useRef, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent, Input, Button, Badge, Loading } from '@/components/ui'
import { ChatInterface } from './ChatInterface'
import { AgentMetrics } from './AgentMetrics'
import { QuickActions } from './QuickActions'
import { useToast } from '@/components/ui'
import type { UserContext, AgentType, ChatMessage, AgentTestResult } from '@/types'
import styles from '@/styles/modules/AgentTester.module.css'

interface AgentTesterProps {
  agentType: AgentType
  currentUser: UserContext
}

export function AgentTester({ agentType, currentUser }: AgentTesterProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentInput, setCurrentInput] = useState('')
  const [sessionId] = useState(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  const [metrics, setMetrics] = useState<AgentTestResult | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const toast = useToast()

  useEffect(() => {
    // Initialize conversation with welcome message
    const welcomeMessage: ChatMessage = {
      id: `welcome_${Date.now()}`,
      role: 'agent',
      content: getWelcomeMessage(agentType),
      timestamp: new Date().toISOString(),
      agent: agentType,
      metadata: {
        type: 'welcome',
        agentVersion: '2.0.0',
        engine: 'MIT-AI-v2.0',
        providers: 'OpenAI + Gemini'
      }
    }
    setMessages([welcomeMessage])
  }, [agentType])

  const getWelcomeMessage = (agent: AgentType): string => {
    const messages = {
      'mit-tracking': '🚚 Olá! Sou o MIT Tracking Agent v2.0 com IA OpenAI/Gemini. Posso ajudar você com consultas sobre CT-e, rastreamento de containers, status de entregas e muito mais. \n\n💡 Experimente perguntar:\n• "Onde está o CT-e 351234567890123?"\n• "Status do container ABCD1234567"\n• "Qual a previsão de entrega?"\n\nComo posso ajudar hoje?',
      'gatekeeper': '🛡️ Bem-vindo ao Gatekeeper Agent. Sou responsável pela autenticação e controle de acesso. Posso validar credenciais, verificar permissões e auditar acessos. Em que posso ajudar?',
      'customs': '🛃 Sou o Customs Agent, especialista em documentação aduaneira. Posso auxiliar com NCM, cálculos de impostos, status de desembaraço e conformidade regulatória. Qual sua dúvida?',
      'financial': '💰 Olá! Sou o Financial Agent. Posso analisar custos, gerar relatórios financeiros, acompanhar faturamento e calcular KPIs. Como posso ajudar na análise financeira?'
    }
    return messages[agent] || 'Olá! Como posso ajudar você hoje?'
  }

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return

    // Add user message
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setCurrentInput('')
    setIsLoading(true)

    try {
      // Call real MIT Tracking Agent v2 via GraphQL
      const response = await callMITTrackingAgent(message, sessionId, currentUser)
      
      const agentMessage: ChatMessage = {
        id: `agent_${Date.now()}`,
        role: 'agent',
        content: response.content,
        timestamp: new Date().toISOString(),
        agent: agentType,
        metadata: response.metadata
      }

      setMessages(prev => [...prev, agentMessage])
      setMetrics(response.testResult)

      if (response.testResult?.status === 'error') {
        toast.error('Erro no Agent', response.testResult.error)
      }

    } catch (error) {
      toast.error('Erro de Comunicação', 'Não foi possível conectar com o agente')
      
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        role: 'agent',
        content: '❌ Desculpe, ocorreu um erro interno. Tente novamente mais tarde.',
        timestamp: new Date().toISOString(),
        agent: agentType,
        metadata: {
          type: 'error',
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleQuickAction = (action: string) => {
    setCurrentInput(action)
    inputRef.current?.focus()
  }

  const handleClearChat = () => {
    const welcomeMessage: ChatMessage = {
      id: `welcome_${Date.now()}`,
      role: 'agent',
      content: getWelcomeMessage(agentType),
      timestamp: new Date().toISOString(),
      agent: agentType,
      metadata: {
        type: 'welcome',
        agentVersion: '2.0.0',
        engine: 'MIT-AI-v2.0',
        providers: 'OpenAI + Gemini'
      }
    }
    setMessages([welcomeMessage])
    setMetrics(null)
    toast.info('Chat Limpo', 'Conversa reiniciada')
  }

  return (
    <div className={styles.container}>
      <div className={styles.sidebar}>
        <Card>
          <CardHeader>
            <CardTitle level={4}>⚡ Ações Rápidas</CardTitle>
          </CardHeader>
          <CardContent>
            <QuickActions
              agentType={agentType}
              currentUser={currentUser}
              onAction={handleQuickAction}
            />
          </CardContent>
        </Card>

        {metrics && (
          <Card>
            <CardHeader>
              <CardTitle level={4}>📊 Métricas</CardTitle>
            </CardHeader>
            <CardContent>
              <AgentMetrics metrics={metrics} />
            </CardContent>
          </Card>
        )}
      </div>

      <div className={styles.main}>
        <Card className={styles.chatCard}>
          <CardHeader>
            <div className={styles.chatHeader}>
              <div className={styles.agentStatus}>
                <Badge variant="success" size="sm">
                  🟢 Online
                </Badge>
                <span className={styles.sessionId}>
                  Session: {sessionId.slice(-8)}
                </span>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearChat}
              >
                🗑️ Limpar Chat
              </Button>
            </div>
          </CardHeader>
          
          <CardContent className={styles.chatContent}>
            <ChatInterface
              messages={messages}
              isLoading={isLoading}
              agentType={agentType}
            />
            
            <div className={styles.inputArea}>
              <div className={styles.inputContainer}>
                <Input
                  ref={inputRef}
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSendMessage(currentInput)
                    }
                  }}
                  placeholder={`Digite sua mensagem para o ${agentType} agent...`}
                  disabled={isLoading}
                />
                
                <Button
                  onClick={() => handleSendMessage(currentInput)}
                  disabled={isLoading || !currentInput.trim()}
                  variant="default"
                >
                  {isLoading ? <Loading size="sm" variant="spinner" /> : '🚀'}
                </Button>
              </div>
              
              <div className={styles.inputHint}>
                💡 Pressione Enter para enviar, Shift+Enter para nova linha
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// Real API call to MIT Tracking Agent v2
async function callMITTrackingAgent(
  message: string,
  sessionId: string,
  user: UserContext
): Promise<{
  content: string
  metadata: Record<string, unknown>
  testResult: AgentTestResult
}> {
  const GRAPHQL_ENDPOINT = process.env.NEXT_PUBLIC_GATEKEEPER_URL || 'http://localhost:8001'
  
  const query = `
    mutation ChatWithAgent($input: ChatInput!) {
      chatWithAgent(chatInput: $input) {
        success
        error
        message {
          id
          content
          role
          timestamp
          agentType
          sessionId
          provider
          tokensUsed
          responseTime
          confidence
        }
        agentStats
      }
    }
  `
  
  const variables = {
    input: {
      message,
      sessionId,
      userId: user.userId
    }
  }
  
  try {
    const response = await fetch(`${GRAPHQL_ENDPOINT}/graphql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        variables
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.errors) {
      throw new Error(data.errors[0]?.message || 'GraphQL error')
    }
    
    const result = data.data.chatWithAgent
    
    if (!result.success) {
      throw new Error(result.error || 'Chat failed')
    }
    
    const { message: chatMessage, agentStats } = result
    
    return {
      content: chatMessage.content,
      metadata: {
        agentType: chatMessage.agentType,
        provider: chatMessage.provider,
        tokensUsed: chatMessage.tokensUsed,
        responseTime: chatMessage.responseTime,
        confidence: chatMessage.confidence,
        sessionId: chatMessage.sessionId,
        userId: user.userId,
        ...agentStats
      },
      testResult: {
        status: 'success',
        responseTime: chatMessage.responseTime || 1.0,
        agentType: 'mit-tracking',
        confidence: chatMessage.confidence || 0.9,
        tokensUsed: chatMessage.tokensUsed || 0,
        metadata: {
          engine: 'MIT-AI-v2.0',
          provider: chatMessage.provider,
          model: chatMessage.provider === 'openai' ? 'gpt-3.5-turbo' : 'gemini-pro'
        }
      }
    }
    
  } catch (error) {
    console.error('Error calling MIT Tracking Agent:', error)
    
    // Fallback para simulação em caso de erro
    const responseTime = 1.5
    const errorContent = `❌ Erro ao conectar com o agente: ${error instanceof Error ? error.message : 'Erro desconhecido'}\n\n💡 Verifique se o backend está rodando e as API keys estão configuradas.`
    
    return {
      content: errorContent,
      metadata: {
        agentType: 'mit-tracking',
        userId: user.userId,
        sessionId,
        responseTime,
        error: true,
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      },
      testResult: {
        status: 'error',
        responseTime,
        agentType: 'mit-tracking',
        confidence: 0.0,
        tokensUsed: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
        metadata: {
          engine: 'MIT-AI-v2.0',
          fallback: true
        }
      }
    }
  }
}