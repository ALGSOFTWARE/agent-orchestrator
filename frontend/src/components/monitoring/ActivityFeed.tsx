// 📝 MIT Logistics Frontend - Activity Feed Component

'use client'

import { useEffect, useRef } from 'react'
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/ui'
import type { LogEntry } from '@/types'
import styles from '@/styles/modules/ActivityFeed.module.css'

interface ActivityFeedProps {
  logs: LogEntry[]
  title?: string
  maxItems?: number
  autoScroll?: boolean
}

export function ActivityFeed({ 
  logs, 
  title = "Atividade do Sistema", 
  maxItems = 50,
  autoScroll = true 
}: ActivityFeedProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const getLevelIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'info': return 'ℹ️'
      case 'warn': return '⚠️'
      case 'error': return '❌'
      case 'debug': return '🐛'
      default: return '📝'
    }
  }

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'info': return 'secondary'
      case 'warn': return 'warning'
      case 'error': return 'error'
      case 'debug': return 'outline'
      default: return 'outline'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const formatRelativeTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 60000) return 'agora'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}min`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`
    return '1d+'
  }

  const truncateMessage = (message: string, maxLength = 100) => {
    if (message.length <= maxLength) return message
    return message.substring(0, maxLength) + '...'
  }

  const displayLogs = logs.slice(-maxItems)

  return (
    <Card className={styles.card}>
      <CardHeader>
        <div className={styles.header}>
          <CardTitle level={4}>{title}</CardTitle>
          <div className={styles.info}>
            <span className={styles.count}>
              {displayLogs.length} de {logs.length} eventos
            </span>
            {autoScroll && (
              <Badge variant="outline" size="sm">
                Auto-scroll
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className={styles.content}>
        <div ref={containerRef} className={styles.feedContainer}>
          {displayLogs.length === 0 ? (
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>📋</span>
              <p className={styles.emptyText}>
                Nenhuma atividade registrada
              </p>
            </div>
          ) : (
            <div className={styles.feed}>
              {displayLogs.map((log) => (
                <div key={log.id} className={`${styles.logEntry} ${styles[log.level]}`}>
                  <div className={styles.logHeader}>
                    <div className={styles.logInfo}>
                      <span className={styles.logIcon}>
                        {getLevelIcon(log.level)}
                      </span>
                      <Badge variant={getLevelColor(log.level)} size="sm">
                        {log.level}
                      </Badge>
                      {log.source && (
                        <Badge variant="outline" size="sm">
                          {log.source}
                        </Badge>
                      )}
                    </div>
                    
                    <div className={styles.logTime}>
                      <span className={styles.timestamp}>
                        {formatTimestamp(log.timestamp)}
                      </span>
                      <span className={styles.relativeTime}>
                        {formatRelativeTime(log.timestamp)}
                      </span>
                    </div>
                  </div>
                  
                  <div className={styles.logMessage}>
                    {truncateMessage(log.message)}
                  </div>
                  
                  {log.metadata && Object.keys(log.metadata).length > 0 && (
                    <details className={styles.metadata}>
                      <summary className={styles.metadataSummary}>
                        📊 Metadados ({Object.keys(log.metadata).length})
                      </summary>
                      <div className={styles.metadataContent}>
                        {Object.entries(log.metadata).map(([key, value]) => (
                          <div key={key} className={styles.metadataItem}>
                            <span className={styles.metadataKey}>{key}:</span>
                            <span className={styles.metadataValue}>
                              {typeof value === 'object' 
                                ? JSON.stringify(value, null, 2)
                                : String(value)
                              }
                            </span>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
        
        {logs.length > maxItems && (
          <div className={styles.footer}>
            <p className={styles.footerText}>
              Mostrando os últimos {maxItems} eventos de {logs.length} total
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}