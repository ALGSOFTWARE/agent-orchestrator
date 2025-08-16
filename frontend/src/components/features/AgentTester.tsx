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
        agentVersion: '1.0.0'
      }
    }
    setMessages([welcomeMessage])
  }, [agentType])

  const getWelcomeMessage = (agent: AgentType): string => {
    const messages = {
      'mit-tracking': '🚚 Olá! Sou o MIT Tracking Agent. Posso ajudar você com consultas sobre CT-e, rastreamento de containers, status de entregas e muito mais. Como posso ajudar hoje?',
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
      // Simulate API call to agent
      const response = await simulateAgentResponse(agentType, message, currentUser, sessionId)
      
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
        agentVersion: '1.0.0'
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

// Mock function to simulate agent responses
async function simulateAgentResponse(
  agentType: AgentType,
  message: string,
  user: UserContext,
  sessionId: string
): Promise<{
  content: string
  metadata: Record<string, unknown>
  testResult: AgentTestResult
}> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))

  const responseTime = 800 + Math.random() * 1200

  // Mock responses based on agent type and message content
  const responses = {
    'mit-tracking': {
      'ct-e': '📋 Consultando CT-e... Encontrado! CT-e 35123456789012345678901234567890123 - Status: AUTORIZADO. Destinatário: ACME LOGÍSTICA. Valor: R$ 1.250,00. ETA: 2024-01-15.',
      'container': '📦 Container MSKU1234567 localizado no Porto de Santos, Terminal ABC. Status: DESCARGA CONCLUÍDA. Próximo movimento: Liberação alfandegária prevista para hoje às 14:00.',
      'rastreamento': '🚛 Carga em trânsito. Última atualização: Km 340 da BR-116, sentido Rio de Janeiro. Previsão de chegada: 16:30 de hoje.',
      'default': '📍 Posso ajudar com consultas de CT-e, rastreamento de containers, status de entregas e previsões. Informe o número do documento ou container.'
    },
    'gatekeeper': {
      'auth': '🔐 Usuário validado com sucesso. Permissões ativas: read:cte, write:document. Sessão expira em 4h 23min.',
      'permission': '✅ Verificação de permissões concluída. Usuário tem acesso aos módulos: Tracking, Documents. Acesso negado: Financial Reports.',
      'session': '🕒 Sessão ativa desde 09:30. Última atividade: 2 minutos atrás. Token válido até 18:30.',
      'default': '🛡️ Sistema de autenticação ativo. Posso validar credenciais, verificar permissões ou auditar acessos.'
    },
    'customs': {
      'ncm': '📊 NCM 85171200 - Telefones para redes celulares. Imposto de Importação: 12%. ICMS: 18%. PIS/COFINS: 9,25%.',
      'due': '🛃 DU-E 12345678901 - Status: REGISTRADO. Produto: Eletrônicos. Valor: USD 50.000. Previsão de desembaraço: 2-3 dias úteis.',
      'documento': '📄 Documentos necessários: Invoice comercial, Packing List, BL original, Certificado de origem. Status: PENDENTE - Aguardando certificado.',
      'default': '🛃 Posso consultar NCM, calcular impostos, verificar status de DU-E e orientar sobre documentação aduaneira.'
    },
    'financial': {
      'custo': '💰 Análise de custos do último mês: Frete: R$ 45.670, Combustível: R$ 12.340, Pedágios: R$ 3.450. Total: R$ 61.460.',
      'faturamento': '📈 Faturamento Janeiro: R$ 234.567. Crescimento de 12% vs. mês anterior. Top clientes: ACME (35%), BETA (22%), GAMMA (18%).',
      'margem': '📊 Margem líquida atual: 18,5%. Container 20": R$ 2.340 lucro. Container 40": R$ 4.120 lucro. ROI médio: 23%.',
      'default': '💳 Posso analisar custos, calcular margens, gerar relatórios financeiros e acompanhar KPIs de performance.'
    }
  }

  // Find best matching response
  const agentResponses = responses[agentType]
  let content = agentResponses.default
  
  for (const [key, response] of Object.entries(agentResponses)) {
    if (key !== 'default' && message.toLowerCase().includes(key)) {
      content = response
      break
    }
  }

  // Add some contextual information
  content += `\n\n_Processado em ${responseTime.toFixed(0)}ms | Usuário: ${user.userId} | Sessão: ${sessionId.slice(-8)}_`

  return {
    content,
    metadata: {
      agentType,
      userId: user.userId,
      sessionId,
      responseTime,
      processingEngine: 'MIT-AI-v1.0',
      confidence: 0.85 + Math.random() * 0.15
    },
    testResult: {
      status: 'success',
      responseTime,
      agentType,
      confidence: 0.85 + Math.random() * 0.15,
      tokensUsed: Math.floor(50 + Math.random() * 200),
      metadata: {
        engine: 'MIT-AI-v1.0',
        model: agentType === 'mit-tracking' ? 'logistics-llm-3b' : 'general-llm-7b'
      }
    }
  }
}