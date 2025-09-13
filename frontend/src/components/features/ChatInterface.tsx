// 💬 MIT Logistics Frontend - Chat Interface Component

'use client'

import { useEffect, useRef } from 'react'
import { Badge, Loading } from '@/components/ui'
import type { ChatMessage, AgentType } from '@/types'
import styles from '@/styles/modules/ChatInterface.module.css'

interface ChatInterfaceProps {
  messages: ChatMessage[]
  isLoading: boolean
  agentType: AgentType
}

export function ChatInterface({ messages, isLoading, agentType }: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const getMessageIcon = (role: 'user' | 'agent', agentType?: AgentType) => {
    if (role === 'user') return '👤'
    
    switch (agentType) {
      case 'mit-tracking': return '📍'
      case 'gatekeeper': return '🛡️'
      case 'customs': return '🛃'
      case 'financial': return '💳'
      default: return '🤖'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const formatContent = (content: string) => {
    // Simple formatting for better readability
    return content
      .split('\n')
      .map((line, index) => (
        <span key={index}>
          {line}
          {index < content.split('\n').length - 1 && <br />}
        </span>
      ))
  }

  return (
    <div className={styles.container}>
      <div className={styles.messages}>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`${styles.message} ${styles[message.role]}`}
          >
            <div className={styles.messageHeader}>
              <div className={styles.messageInfo}>
                <span className={styles.messageIcon}>
                  {getMessageIcon(message.role, message.agent as AgentType)}
                </span>
                <span className={styles.messageSender}>
                  {message.role === 'user' ? 'Você' : `${message.agent || 'Agent'} AI`}
                </span>
                {message.metadata?.type ? (
                  <Badge variant="outline" size="sm">
                    {message.metadata.type as string}
                  </Badge>
                ) : null}
              </div>
              <span className={styles.messageTime}>
                {formatTimestamp(message.timestamp)}
              </span>
            </div>
            
            <div className={styles.messageContent}>
              {formatContent(message.content)}
            </div>
            
            {message.metadata && Object.keys(message.metadata).length > 1 && (
              <div className={styles.messageMetadata}>
                <details className={styles.metadataDetails}>
                  <summary className={styles.metadataSummary}>
                    📊 Metadados da resposta
                  </summary>
                  <div className={styles.metadataContent}>
                    {Object.entries(message.metadata)
                      .filter(([key]) => key !== 'type')
                      .map(([key, value]) => (
                        <div key={key} className={styles.metadataItem}>
                          <span className={styles.metadataKey}>{key}:</span>
                          <span className={styles.metadataValue}>
                            {typeof value === 'object' && value !== null
                              ? JSON.stringify(value, null, 2)
                              : String(value ?? '')
                            }
                          </span>
                        </div>
                      ))}
                  </div>
                </details>
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className={`${styles.message} ${styles.agent} ${styles.loading}`}>
            <div className={styles.messageHeader}>
              <div className={styles.messageInfo}>
                <span className={styles.messageIcon}>
                  {getMessageIcon('agent', agentType)}
                </span>
                <span className={styles.messageSender}>
                  {agentType} AI
                </span>
              </div>
            </div>
            
            <div className={styles.messageContent}>
              <Loading variant="dots" size="sm" text="Processando..." />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}