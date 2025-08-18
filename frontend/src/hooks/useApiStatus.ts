// 📊 MIT Logistics Frontend - API Status Monitor Hook

'use client'

import { useState, useEffect, useCallback } from 'react'
import { checkServiceHealth } from '@/lib/api/client'

interface ServiceStatus {
  service: string
  status: 'healthy' | 'unhealthy' | 'checking'
  responseTime: number | null
  lastChecked: string
  error?: string
}

interface ApiStatusState {
  api: ServiceStatus
  gatekeeper: ServiceStatus
  openai: ServiceStatus
  gemini: ServiceStatus
  lastUpdate: string
}

const initialStatus: ServiceStatus = {
  service: '',
  status: 'checking',
  responseTime: null,
  lastChecked: new Date().toISOString(),
}

export function useApiStatus(refreshInterval: number = 30000) {
  const [status, setStatus] = useState<ApiStatusState>({
    api: { ...initialStatus, service: 'API' },
    gatekeeper: { ...initialStatus, service: 'Gatekeeper' },
    openai: { ...initialStatus, service: 'OpenAI' },
    gemini: { ...initialStatus, service: 'Gemini' },
    lastUpdate: new Date().toISOString()
  })

  const [isChecking, setIsChecking] = useState(false)

  // Check individual service status
  const checkService = useCallback(async (serviceName: 'api' | 'gatekeeper') => {
    // Only run on client side
    if (typeof window === 'undefined') {
      return {
        service: serviceName,
        status: 'checking' as const,
        responseTime: null,
        lastChecked: new Date().toISOString(),
        error: 'Server-side rendering'
      } as ServiceStatus
    }

    try {
      const result = await checkServiceHealth(serviceName)
      return {
        service: serviceName,
        status: result.status,
        responseTime: result.responseTime,
        lastChecked: new Date().toISOString(),
        error: result.error
      } as ServiceStatus
    } catch (error) {
      return {
        service: serviceName,
        status: 'unhealthy' as const,
        responseTime: null,
        lastChecked: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Connection failed'
      } as ServiceStatus
    }
  }, [])

  // Check LLM provider status (mock for now)
  const checkLLMStatus = useCallback(async (provider: 'openai' | 'gemini') => {
    // Only run on client side
    if (typeof window === 'undefined') {
      return {
        service: provider,
        status: 'checking' as const,
        responseTime: null,
        lastChecked: new Date().toISOString(),
        error: 'Server-side rendering'
      } as ServiceStatus
    }

    try {
      // Mock LLM status check - in real implementation, this would check API keys and quota
      const hasApiKey = provider === 'openai' 
        ? !!process.env.NEXT_PUBLIC_OPENAI_API_KEY 
        : !!process.env.NEXT_PUBLIC_GEMINI_API_KEY

      if (!hasApiKey) {
        return {
          service: provider,
          status: 'unhealthy' as const,
          responseTime: null,
          lastChecked: new Date().toISOString(),
          error: 'API key not configured'
        } as ServiceStatus
      }

      // Simulate API check with random response time
      await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 200))
      
      return {
        service: provider,
        status: 'healthy' as const,
        responseTime: Math.random() * 800 + 200,
        lastChecked: new Date().toISOString()
      } as ServiceStatus
    } catch (error) {
      return {
        service: provider,
        status: 'unhealthy' as const,
        responseTime: null,
        lastChecked: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Check failed'
      } as ServiceStatus
    }
  }, [])

  // Check all services
  const checkAllServices = useCallback(async () => {
    if (isChecking) return
    
    setIsChecking(true)
    
    try {
      const [apiStatus, gatekeeperStatus, openaiStatus, geminiStatus] = await Promise.all([
        checkService('api'),
        checkService('gatekeeper'),
        checkLLMStatus('openai'),
        checkLLMStatus('gemini')
      ])

      setStatus({
        api: apiStatus,
        gatekeeper: gatekeeperStatus,
        openai: openaiStatus,
        gemini: geminiStatus,
        lastUpdate: new Date().toISOString()
      })
    } catch (error) {
      console.error('Error checking services:', error)
    } finally {
      setIsChecking(false)
    }
  }, [checkService, checkLLMStatus, isChecking])

  // Initial check and setup interval
  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return

    checkAllServices()
    
    const interval = setInterval(checkAllServices, refreshInterval)
    
    return () => clearInterval(interval)
  }, [checkAllServices, refreshInterval])

  // Manual refresh function
  const refresh = useCallback(() => {
    checkAllServices()
  }, [checkAllServices])

  // Get overall health status
  const overallStatus = useCallback(() => {
    const services = [status.api, status.gatekeeper, status.openai, status.gemini]
    const healthyCount = services.filter(s => s.status === 'healthy').length
    const checkingCount = services.filter(s => s.status === 'checking').length
    
    if (checkingCount > 0) return 'checking'
    if (healthyCount === services.length) return 'healthy'
    if (healthyCount > 0) return 'partial'
    return 'unhealthy'
  }, [status])

  return {
    status,
    isChecking,
    refresh,
    overallStatus: overallStatus(),
    lastUpdate: status.lastUpdate
  }
}

export type { ApiStatusState, ServiceStatus }