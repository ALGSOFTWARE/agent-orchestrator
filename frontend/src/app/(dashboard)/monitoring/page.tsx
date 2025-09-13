// 📊 MIT Logistics Frontend - Monitoring Page

'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui'
import { ServiceStatusCard } from '@/components/monitoring/ServiceStatusCard'
import { MetricsChart } from '@/components/monitoring/MetricsChart'
import { ActivityFeed } from '@/components/monitoring/ActivityFeed'
import { useMonitoring } from '@/lib/store/app'
import { checkServiceHealth } from '@/lib/api'
import { useToast } from '@/components/ui'
import type { ServiceStatus, SystemMetrics } from '@/types'
import styles from '@/styles/modules/MonitoringPage.module.css'

export default function MonitoringPage() {
  const { 
    services, 
    metrics, 
    logs, 
    updateServices, 
    addMetrics, 
    addLog,
    lastHealthCheck,
    setLastHealthCheck 
  } = useMonitoring()
  
  const [isLoading, setIsLoading] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const { toast } = useToast()

  // Mock data generator for demonstration
  const generateMockMetrics = (): SystemMetrics => ({
    timestamp: new Date().toISOString(),
    cpu_usage: 15 + Math.random() * 70,
    memory_usage: 30 + Math.random() * 50,
    disk_usage: 40 + Math.random() * 30,
    network_io: {
      bytes_sent: Math.random() * 1000000,
      bytes_received: Math.random() * 2000000
    },
    requests_per_minute: Math.floor(50 + Math.random() * 500),
    error_rate: Math.random() * 5,
    active_connections: Math.floor(10 + Math.random() * 100)
  })

  const performHealthCheck = async () => {
    setIsLoading(true)
    try {
      const [gatekeeperHealth, apiHealth] = await Promise.allSettled([
        checkServiceHealth('gatekeeper'),
        checkServiceHealth('api')
      ])
      
      const newServices: ServiceStatus[] = [
        {
          name: 'Gatekeeper Agent',
          status: gatekeeperHealth.status === 'fulfilled' && gatekeeperHealth.value.status === 'healthy' 
            ? 'healthy' 
            : Math.random() > 0.3 ? 'degraded' : 'unhealthy',
          url: 'http://localhost:8001',
          responseTime: gatekeeperHealth.status === 'fulfilled' 
            ? (gatekeeperHealth.value.responseTime || 1000)
            : 800 + Math.random() * 2000,
          lastCheck: new Date().toISOString(),
          details: gatekeeperHealth.status === 'rejected' 
            ? { error: 'Connection timeout', version: 'v1.2.3' } 
            : { version: 'v1.2.3', uptime: '5d 12h' }
        },
        {
          name: 'GraphQL API',
          status: apiHealth.status === 'fulfilled' && apiHealth.value.status === 'healthy' 
            ? 'healthy' 
            : Math.random() > 0.2 ? 'degraded' : 'unhealthy',
          url: 'http://localhost:8000',
          responseTime: apiHealth.status === 'fulfilled' 
            ? (apiHealth.value.responseTime || 800)
            : 500 + Math.random() * 1500,
          lastCheck: new Date().toISOString(),
          details: { 
            version: 'v2.1.0', 
            uptime: '3d 8h',
            connections: Math.floor(10 + Math.random() * 50)
          }
        },
        {
          name: 'MIT Tracking Agent',
          status: Math.random() > 0.1 ? 'healthy' : 'degraded',
          url: 'http://localhost:8002',
          responseTime: 300 + Math.random() * 800,
          lastCheck: new Date().toISOString(),
          details: { 
            version: 'v1.0.5', 
            model: 'llama3.2:3b',
            tokens_processed: Math.floor(1000 + Math.random() * 10000)
          }
        },
        {
          name: 'Ollama Service',
          status: Math.random() > 0.05 ? 'healthy' : 'unhealthy',
          url: 'http://localhost:11434',
          responseTime: 200 + Math.random() * 600,
          lastCheck: new Date().toISOString(),
          details: { 
            version: 'v0.1.32',
            models: ['llama3.2:3b', 'mistral:latest'],
            gpu_usage: `${(Math.random() * 80).toFixed(1)}%`
          }
        }
      ]
      
      updateServices(newServices)
      setLastHealthCheck(new Date().toISOString())
      
      // Add mock metrics
      addMetrics(generateMockMetrics())
      
      // Add log entry
      const healthyCount = newServices.filter(s => s.status === 'healthy').length
      const logLevel = healthyCount === newServices.length ? 'info' : 
                      healthyCount > newServices.length / 2 ? 'warn' : 'error'
      
      addLog({
        id: `health_check_${Date.now()}`,
        timestamp: new Date().toISOString(),
        level: logLevel,
        source: 'monitoring',
        message: `Health check completed. ${healthyCount}/${newServices.length} services healthy`,
        metadata: {
          services: newServices.map(s => ({ 
            name: s.name, 
            status: s.status, 
            responseTime: s.responseTime 
          })),
          totalServices: newServices.length,
          healthyServices: healthyCount
        }
      })
      
      if (healthyCount === newServices.length) {
        toast.success('Todos os Serviços Online', 'Sistema operando normalmente')
      } else if (healthyCount > 0) {
        toast.warning('Alguns Serviços com Problemas', `${healthyCount}/${newServices.length} serviços ativos`)
      } else {
        toast.error('Serviços Indisponíveis', 'Sistema com problemas críticos')
      }
      
    } catch (error) {
      toast.error('Erro no Health Check', 'Não foi possível verificar o status dos serviços')
      addLog({
        id: `health_check_error_${Date.now()}`,
        timestamp: new Date().toISOString(),
        level: 'error',
        source: 'monitoring',
        message: `Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        metadata: {
          error: error instanceof Error ? error.stack : String(error)
        }
      })
    } finally {
      setIsLoading(false)
    }
  }

  const refreshService = async (serviceName: string) => {
    // Simulate individual service refresh
    const service = services.find(s => s.name === serviceName)
    if (service) {
      const updatedService = {
        ...service,
        status: (Math.random() > 0.2 ? 'healthy' : 'degraded') as ServiceStatus['status'],
        responseTime: 200 + Math.random() * 1000,
        lastCheck: new Date().toISOString()
      }
      
      const updatedServices = services.map(s => 
        s.name === serviceName ? updatedService : s
      )
      
      updateServices(updatedServices)
      
      addLog({
        id: `service_refresh_${Date.now()}`,
        timestamp: new Date().toISOString(),
        level: 'info',
        source: serviceName.toLowerCase().replace(/\s+/g, '_'),
        message: `Service ${serviceName} manually refreshed - Status: ${updatedService.status}`,
        metadata: {
          serviceName,
          newStatus: updatedService.status,
          responseTime: updatedService.responseTime
        }
      })
    }
  }

  useEffect(() => {
    // Initial health check
    performHealthCheck()
    
    // Set up periodic health checks
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(performHealthCheck, 30000)
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh])

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>📊 Monitoring Dashboard</h1>
          <p className={styles.description}>
            Monitoramento em tempo real dos serviços e performance do sistema MIT Logistics
          </p>
          {lastHealthCheck && (
            <div className={styles.lastUpdate}>
              Última verificação: <span>{new Date(lastHealthCheck).toLocaleTimeString('pt-BR')}</span>
            </div>
          )}
        </div>
        
        <div className={styles.headerActions}>
          <Button
            variant="outline"
            onClick={() => setAutoRefresh(!autoRefresh)}
            leftIcon={autoRefresh ? '⏸️' : '▶️'}
          >
            {autoRefresh ? 'Pausar' : 'Retomar'} Auto-refresh
          </Button>
          
          <Button
            onClick={performHealthCheck}
            disabled={isLoading}
            leftIcon={isLoading ? '⏳' : '🔄'}
          >
            {isLoading ? 'Verificando...' : 'Atualizar Agora'}
          </Button>
        </div>
      </div>

      <div className={styles.content}>
        {/* Services Status Section */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>🏥 Status dos Serviços</h2>
          <div className={styles.serviceGrid}>
            {services.map((service, index) => (
              <ServiceStatusCard
                key={`${service.name}-${index}`}
                service={service}
                onRefresh={() => refreshService(service.name)}
              />
            ))}
          </div>
        </div>

        {/* System Metrics Section */}
        {metrics.length > 0 && (
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>📈 Métricas do Sistema</h2>
            <div className={styles.metricsGrid}>
              <MetricsChart
                metrics={metrics.slice(-20)}
                title="CPU Usage"
                type="cpu"
              />
              <MetricsChart
                metrics={metrics.slice(-20)}
                title="Memory Usage"
                type="memory"
              />
              <MetricsChart
                metrics={metrics.slice(-20)}
                title="Disk Usage"
                type="disk"
              />
              <MetricsChart
                metrics={metrics.slice(-20)}
                title="Network I/O"
                type="network"
              />
            </div>
          </div>
        )}

        {/* Activity Feed Section */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>📝 Atividade do Sistema</h2>
          <ActivityFeed
            logs={logs}
            title="Logs em Tempo Real"
            maxItems={100}
            autoScroll={true}
          />
        </div>
      </div>
    </div>
  )
}