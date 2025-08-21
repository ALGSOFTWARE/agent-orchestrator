// 📊 MIT Logistics Frontend - Agent Metrics Component

'use client'

import { Badge } from '@/components/ui'
import type { AgentTestResult } from '@/types'
import styles from '@/styles/modules/AgentMetrics.module.css'

interface AgentMetricsProps {
  metrics: AgentTestResult
}

export function AgentMetrics({ metrics }: AgentMetricsProps) {
  const getStatusColor = (status: string) => {
    return status === 'success' ? 'success' : 'error'
  }

  const getResponseTimeColor = (time: number) => {
    if (time < 1000) return 'success'
    if (time < 2000) return 'warning'
    return 'error'
  }

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'secondary'
    if (confidence >= 0.9) return 'success'
    if (confidence >= 0.7) return 'warning'
    return 'error'
  }

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`
  }

  return (
    <div className={styles.container}>
      <div className={styles.metric}>
        <div className={styles.metricLabel}>Status</div>
        <Badge variant={getStatusColor(metrics.status)} size="sm">
          {metrics.status === 'success' ? '✅ Sucesso' : '❌ Erro'}
        </Badge>
      </div>

      <div className={styles.metric}>
        <div className={styles.metricLabel}>Tempo de Resposta</div>
        <div className={styles.metricValue}>
          <Badge variant={getResponseTimeColor(metrics.responseTime)} size="sm">
            {metrics.responseTime.toFixed(0)}ms
          </Badge>
        </div>
      </div>

      {metrics.confidence && (
        <div className={styles.metric}>
          <div className={styles.metricLabel}>Confiança</div>
          <div className={styles.metricValue}>
            <Badge variant={getConfidenceColor(metrics.confidence)} size="sm">
              {(metrics.confidence * 100).toFixed(1)}%
            </Badge>
          </div>
        </div>
      )}

      {metrics.tokensUsed && (
        <div className={styles.metric}>
          <div className={styles.metricLabel}>Tokens Usados</div>
          <div className={styles.metricValue}>
            <span className={styles.tokenCount}>
              {metrics.tokensUsed.toLocaleString()}
            </span>
          </div>
        </div>
      )}

      {metrics.error && (
        <div className={styles.errorSection}>
          <div className={styles.metricLabel}>Erro</div>
          <div className={styles.errorMessage}>
            {metrics.error}
          </div>
        </div>
      )}

      {metrics.metadata && (
        <div className={styles.metadataSection}>
          <div className={styles.metricLabel}>Detalhes Técnicos</div>
          <div className={styles.metadataGrid}>
            {Object.entries(metrics.metadata).map(([key, value]) => (
              <div key={key} className={styles.metadataItem}>
                <span className={styles.metadataKey}>{key}:</span>
                <span className={styles.metadataValue}>
                  {typeof value === 'object' 
                    ? JSON.stringify(value)
                    : String(value)
                  }
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className={styles.performanceIndicator}>
        <div className={styles.indicatorLabel}>Performance Geral</div>
        <div className={styles.indicatorBar}>
          <div 
            className={`${styles.indicatorFill} ${
              metrics.status === 'success' && metrics.responseTime < 2000
                ? styles.good
                : metrics.status === 'success'
                ? styles.average
                : styles.poor
            }`}
            style={{
              width: metrics.status === 'success' 
                ? `${Math.max(20, 100 - (metrics.responseTime / 50))}%`
                : '10%'
            }}
          />
        </div>
      </div>
    </div>
  )
}