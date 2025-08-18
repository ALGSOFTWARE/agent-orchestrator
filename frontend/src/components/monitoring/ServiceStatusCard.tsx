// 📡 MIT Logistics Frontend - Service Status Card Component

'use client'

import { Card, CardHeader, CardTitle, CardContent, Badge, StatusBadge } from '@/components/ui'
import type { ServiceStatus } from '@/types'
import styles from '@/styles/modules/ServiceStatusCard.module.css'

interface ServiceStatusCardProps {
  service: ServiceStatus
  onRefresh?: () => void
}

export function ServiceStatusCard({ service, onRefresh }: ServiceStatusCardProps) {
  const getStatusIcon = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy': return '🟢'
      case 'unhealthy': return '🔴'
      case 'degraded': return '🟡'
      default: return '⚫'
    }
  }

  const getStatusColor = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy': return 'success'
      case 'unhealthy': return 'error'
      case 'degraded': return 'warning'
      default: return 'secondary'
    }
  }

  const getResponseTimeColor = (responseTime?: number) => {
    if (!responseTime) return 'secondary'
    if (responseTime < 500) return 'success'
    if (responseTime < 1000) return 'warning'
    return 'error'
  }

  const formatLastCheck = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 60000) return 'Agora mesmo'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}min atrás`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h atrás`
    return date.toLocaleDateString('pt-BR')
  }

  return (
    <Card className={styles.card} hoverable>
      <CardHeader>
        <div className={styles.header}>
          <div className={styles.serviceInfo}>
            <div className={styles.serviceIcon}>
              {getStatusIcon(service.status)}
            </div>
            <div>
              <CardTitle level={4}>{service.name}</CardTitle>
              <div className={styles.url}>{service.url}</div>
            </div>
          </div>
          
          <div className={styles.actions}>
            {onRefresh && (
              <button
                onClick={onRefresh}
                className={styles.refreshButton}
                title="Atualizar status"
              >
                🔄
              </button>
            )}
            <StatusBadge status={service.status === 'healthy' ? 'success' : 'error'}>
              {service.status}
            </StatusBadge>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className={styles.metrics}>
          {service.responseTime && (
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Tempo de Resposta</span>
              <Badge variant={getResponseTimeColor(service.responseTime)} size="sm">
                {service.responseTime}ms
              </Badge>
            </div>
          )}
          
          <div className={styles.metric}>
            <span className={styles.metricLabel}>Última Verificação</span>
            <span className={styles.metricValue}>
              {formatLastCheck(service.lastCheck)}
            </span>
          </div>
        </div>

        {service.details && Object.keys(service.details).length > 0 && (
          <div className={styles.details}>
            <div className={styles.detailsTitle}>Detalhes</div>
            <div className={styles.detailsGrid}>
              {Object.entries(service.details).map(([key, value]) => (
                <div key={key} className={styles.detailItem}>
                  <span className={styles.detailKey}>{key}:</span>
                  <span className={styles.detailValue}>
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

        <div className={styles.statusIndicator}>
          <div className={styles.indicatorBar}>
            <div 
              className={`${styles.indicatorFill} ${styles[service.status]}`}
              style={{
                width: service.status === 'healthy' ? '100%' : 
                       service.status === 'degraded' ? '60%' : '20%'
              }}
            />
          </div>
          <div className={styles.indicatorLabel}>
            {service.status === 'healthy' && 'Serviço operando normalmente'}
            {service.status === 'degraded' && 'Serviço com performance reduzida'}
            {service.status === 'unhealthy' && 'Serviço indisponível'}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}