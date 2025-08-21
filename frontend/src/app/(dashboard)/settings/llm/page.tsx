'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Loading } from '@/components/ui/Loading'
import styles from '@/styles/pages/LLMConfigPage.module.css'

interface LLMProvider {
  id: 'openai' | 'gemini'
  name: string
  description: string
  icon: string
  status: 'healthy' | 'error' | 'disabled' | 'cost_limit_exceeded'
  model: string
  dailyCostRemaining?: number
  avgResponseTime?: number
  requestCount?: number
  errorCount?: number
}

interface LLMConfig {
  providers: LLMProvider[]
  preferredProvider: 'openai' | 'gemini' | 'auto'
  maxDailyCost: number
  temperature: number
  maxTokens: number
}

export default function LLMConfigPage() {
  const [config, setConfig] = useState<LLMConfig | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [testingProvider, setTestingProvider] = useState<string | null>(null)
  const [testResults, setTestResults] = useState<Record<string, any>>({})
  
  // Form states
  const [formData, setFormData] = useState({
    openaiApiKey: '',
    openaiModel: 'gpt-3.5-turbo',
    geminiApiKey: '',
    geminiModel: 'gemini-pro',
    preferredProvider: 'auto' as 'auto' | 'openai' | 'gemini',
    maxDailyCost: 50,
    temperature: 0.3,
    maxTokens: 1000
  })

  useEffect(() => {
    loadLLMConfig()
  }, [])

  const loadLLMConfig = async () => {
    try {
      setIsLoading(true)
      
      // Mock response - substituir por chamada real à API
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockConfig: LLMConfig = {
        providers: [
          {
            id: 'openai',
            name: 'OpenAI',
            description: 'GPT-3.5-turbo, GPT-4 - Melhor para análises complexas',
            icon: '🤖',
            status: process.env.NEXT_PUBLIC_OPENAI_API_KEY ? 'healthy' : 'disabled',
            model: 'gpt-3.5-turbo',
            dailyCostRemaining: 45.50,
            avgResponseTime: 1.2,
            requestCount: 156,
            errorCount: 2
          },
          {
            id: 'gemini',
            name: 'Google Gemini',
            description: 'Gemini Pro - Melhor custo-benefício',
            icon: '💎',
            status: process.env.NEXT_PUBLIC_GEMINI_API_KEY ? 'healthy' : 'disabled',
            model: 'gemini-pro',
            dailyCostRemaining: 28.30,
            avgResponseTime: 0.8,
            requestCount: 234,
            errorCount: 1
          }
        ],
        preferredProvider: 'auto',
        maxDailyCost: 50,
        temperature: 0.3,
        maxTokens: 1000
      }
      
      setConfig(mockConfig)
      
      // Populate form with current config
      setFormData({
        openaiApiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY || '',
        openaiModel: mockConfig.providers[0]?.model || 'gpt-3.5-turbo',
        geminiApiKey: process.env.NEXT_PUBLIC_GEMINI_API_KEY || '',
        geminiModel: mockConfig.providers[1]?.model || 'gemini-pro',
        preferredProvider: mockConfig.preferredProvider as 'auto' | 'openai' | 'gemini',
        maxDailyCost: mockConfig.maxDailyCost,
        temperature: mockConfig.temperature,
        maxTokens: mockConfig.maxTokens
      })
      
    } catch (error) {
      console.error('Failed to load LLM config:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const testProvider = async (providerId: 'openai' | 'gemini') => {
    setTestingProvider(providerId)
    
    try {
      // Mock test - substituir por chamada real
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const mockTestResult = {
        success: Math.random() > 0.2, // 80% success rate
        responseTime: Math.random() * 2 + 0.5,
        tokensUsed: Math.floor(Math.random() * 100 + 50),
        cost: Math.random() * 0.01,
        model: providerId === 'openai' ? formData.openaiModel : formData.geminiModel,
        response: `Teste bem-sucedido! Modelo ${providerId === 'openai' ? formData.openaiModel : formData.geminiModel} respondendo corretamente.`
      }
      
      setTestResults(prev => ({
        ...prev,
        [providerId]: mockTestResult
      }))
      
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [providerId]: {
          success: false,
          error: error instanceof Error ? error.message : 'Test failed'
        }
      }))
    } finally {
      setTestingProvider(null)
    }
  }

  const saveConfig = async () => {
    setIsSaving(true)
    
    try {
      // Mock save - substituir por chamada real à API
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Simulate success
      alert('✅ Configuração salva com sucesso!')
      
      // Reload config to reflect changes
      await loadLLMConfig()
      
    } catch (error) {
      alert('❌ Erro ao salvar configuração')
      console.error('Failed to save config:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'success'
      case 'error': return 'error'
      case 'disabled': return 'secondary'
      case 'cost_limit_exceeded': return 'warning'
      default: return 'secondary'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'healthy': return '✅ Ativo'
      case 'error': return '❌ Erro'
      case 'disabled': return '⚪ Desabilitado'
      case 'cost_limit_exceeded': return '💰 Limite de custo atingido'
      default: return '❓ Desconhecido'
    }
  }

  if (isLoading) {
    return (
      <div className={styles.llmConfigPage}>
        <div className={styles.header}>
          <h1>🧠 Configuração de LLM</h1>
          <p>Configurar OpenAI e Google Gemini</p>
        </div>
        <Loading size="lg" />
      </div>
    )
  }

  return (
    <div className={styles.llmConfigPage}>
      <div className={styles.header}>
        <h1>🧠 Configuração de LLM</h1>
        <p>Configure os provedores de IA e preferências de roteamento</p>
      </div>

      {/* Provider Status Overview */}
      <section className={styles.statusOverview}>
        <h2>📊 Status dos Provedores</h2>
        <div className={styles.providersGrid}>
          {config?.providers.map((provider) => (
            <Card key={provider.id} className={styles.providerCard}>
              <div className={styles.providerHeader}>
                <div className={styles.providerInfo}>
                  <span className={styles.providerIcon}>{provider.icon}</span>
                  <div>
                    <h3>{provider.name}</h3>
                    <p>{provider.description}</p>
                  </div>
                </div>
                <Badge variant={getStatusColor(provider.status)}>
                  {getStatusLabel(provider.status)}
                </Badge>
              </div>

              {provider.status === 'healthy' && (
                <div className={styles.providerStats}>
                  <div className={styles.stat}>
                    <span className={styles.statLabel}>Modelo:</span>
                    <span className={styles.statValue}>{provider.model}</span>
                  </div>
                  <div className={styles.stat}>
                    <span className={styles.statLabel}>Custo restante hoje:</span>
                    <span className={styles.statValue}>${provider.dailyCostRemaining?.toFixed(2)}</span>
                  </div>
                  <div className={styles.stat}>
                    <span className={styles.statLabel}>Tempo de resposta:</span>
                    <span className={styles.statValue}>{provider.avgResponseTime?.toFixed(1)}s</span>
                  </div>
                  <div className={styles.stat}>
                    <span className={styles.statLabel}>Requests hoje:</span>
                    <span className={styles.statValue}>{provider.requestCount}</span>
                  </div>
                  {provider.errorCount! > 0 && (
                    <div className={styles.stat}>
                      <span className={styles.statLabel}>Erros:</span>
                      <span className={styles.statValueError}>{provider.errorCount}</span>
                    </div>
                  )}
                </div>
              )}

              <div className={styles.providerActions}>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => testProvider(provider.id)}
                  disabled={testingProvider === provider.id || provider.status === 'disabled'}
                  isLoading={testingProvider === provider.id}
                >
                  {testingProvider === provider.id ? 'Testando...' : '🧪 Testar'}
                </Button>
                
                {testResults[provider.id] && (
                  <div className={styles.testResult}>
                    {testResults[provider.id].success ? (
                      <div className={styles.testSuccess}>
                        ✅ Teste OK ({testResults[provider.id].responseTime?.toFixed(2)}s)
                      </div>
                    ) : (
                      <div className={styles.testError}>
                        ❌ Falhou: {testResults[provider.id].error}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Configuration Form */}
      <section className={styles.configSection}>
        <Card>
          <h2>⚙️ Configurações</h2>
          
          <div className={styles.configForm}>
            {/* OpenAI Configuration */}
            <div className={styles.providerConfig}>
              <h3>🤖 OpenAI</h3>
              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label htmlFor="openaiApiKey">API Key</label>
                  <Input
                    id="openaiApiKey"
                    type="password"
                    value={formData.openaiApiKey}
                    onChange={(e) => setFormData(prev => ({ ...prev, openaiApiKey: e.target.value }))}
                    placeholder="sk-..."
                  />
                </div>
                <div className={styles.formGroup}>
                  <label htmlFor="openaiModel">Modelo</label>
                  <select
                    id="openaiModel"
                    value={formData.openaiModel}
                    onChange={(e) => setFormData(prev => ({ ...prev, openaiModel: e.target.value }))}
                    className={styles.select}
                  >
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Recomendado)</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Gemini Configuration */}
            <div className={styles.providerConfig}>
              <h3>💎 Google Gemini</h3>
              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label htmlFor="geminiApiKey">API Key</label>
                  <Input
                    id="geminiApiKey"
                    type="password"
                    value={formData.geminiApiKey}
                    onChange={(e) => setFormData(prev => ({ ...prev, geminiApiKey: e.target.value }))}
                    placeholder="AIza..."
                  />
                </div>
                <div className={styles.formGroup}>
                  <label htmlFor="geminiModel">Modelo</label>
                  <select
                    id="geminiModel"
                    value={formData.geminiModel}
                    onChange={(e) => setFormData(prev => ({ ...prev, geminiModel: e.target.value }))}
                    className={styles.select}
                  >
                    <option value="gemini-pro">Gemini Pro (Recomendado)</option>
                    <option value="gemini-pro-vision">Gemini Pro Vision</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Routing Configuration */}
            <div className={styles.routingConfig}>
              <h3>🔄 Roteamento</h3>
              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label htmlFor="preferredProvider">Provedor Preferido</label>
                  <select
                    id="preferredProvider"
                    value={formData.preferredProvider}
                    onChange={(e) => setFormData(prev => ({ ...prev, preferredProvider: e.target.value as any }))}
                    className={styles.select}
                  >
                    <option value="auto">🔄 Automático (Recomendado)</option>
                    <option value="openai">🤖 Sempre OpenAI</option>
                    <option value="gemini">💎 Sempre Gemini</option>
                  </select>
                </div>
                <div className={styles.formGroup}>
                  <label htmlFor="maxDailyCost">Limite Diário de Custo (USD)</label>
                  <Input
                    id="maxDailyCost"
                    type="number"
                    min="1"
                    max="1000"
                    step="1"
                    value={formData.maxDailyCost}
                    onChange={(e) => setFormData(prev => ({ ...prev, maxDailyCost: parseInt(e.target.value) }))}
                  />
                </div>
              </div>
            </div>

            {/* Model Parameters */}
            <div className={styles.modelParams}>
              <h3>🎛️ Parâmetros do Modelo</h3>
              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label htmlFor="temperature">Temperature</label>
                  <Input
                    id="temperature"
                    type="number"
                    min="0"
                    max="2"
                    step="0.1"
                    value={formData.temperature}
                    onChange={(e) => setFormData(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                  />
                  <small>0 = Mais determinístico, 2 = Mais criativo</small>
                </div>
                <div className={styles.formGroup}>
                  <label htmlFor="maxTokens">Max Tokens</label>
                  <Input
                    id="maxTokens"
                    type="number"
                    min="100"
                    max="4000"
                    step="100"
                    value={formData.maxTokens}
                    onChange={(e) => setFormData(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
                  />
                  <small>Máximo de tokens na resposta</small>
                </div>
              </div>
            </div>
          </div>

          <div className={styles.configActions}>
            <Button
              onClick={saveConfig}
              isLoading={isSaving}
              disabled={isSaving}
            >
              {isSaving ? 'Salvando...' : '💾 Salvar Configurações'}
            </Button>
            
            <Button
              variant="outline"
              onClick={loadLLMConfig}
              disabled={isSaving}
            >
              🔄 Recarregar
            </Button>
          </div>
        </Card>
      </section>

      {/* Routing Strategy Info */}
      <section className={styles.infoSection}>
        <Card>
          <h3>🧠 Como Funciona o Roteamento Inteligente</h3>
          <div className={styles.routingInfo}>
            <div className={styles.infoItem}>
              <h4>📋 Consultas Logísticas</h4>
              <p>CT-e, containers, rastreamento → Preferencialmente <strong>OpenAI</strong></p>
            </div>
            <div className={styles.infoItem}>
              <h4>💰 Consultas Financeiras</h4>
              <p>Custos, câmbio, faturamento → Preferencialmente <strong>Gemini</strong></p>
            </div>
            <div className={styles.infoItem}>
              <h4>🔄 Fallback Automático</h4>
              <p>Se um provedor falha, usa automaticamente o outro</p>
            </div>
            <div className={styles.infoItem}>
              <h4>💡 Controle de Custos</h4>
              <p>Quando o limite diário é atingido, usa o provedor alternativo</p>
            </div>
          </div>
        </Card>
      </section>
    </div>
  )
}