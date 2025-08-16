// ⚡ MIT Logistics Frontend - Quick Actions Component

'use client'

import { Button } from '@/components/ui'
import type { UserContext, AgentType } from '@/types'
import styles from '@/styles/modules/QuickActions.module.css'

interface QuickActionsProps {
  agentType: AgentType
  currentUser: UserContext
  onAction: (action: string) => void
}

interface QuickAction {
  label: string
  action: string
  icon: string
  description: string
  requiredPermissions?: string[]
}

const QUICK_ACTIONS: Record<AgentType, QuickAction[]> = {
  'mit-tracking': [
    {
      label: 'Consultar CT-e',
      action: 'CT-e número 351234567890123456789012345678901234',
      icon: '📋',
      description: 'Consulta um CT-e específico',
      requiredPermissions: ['read:cte']
    },
    {
      label: 'Rastrear Container',
      action: 'Onde está o container MSKU1234567?',
      icon: '📦',
      description: 'Localiza container por código',
      requiredPermissions: ['read:container']
    },
    {
      label: 'Status de Entrega',
      action: 'Qual o status da minha entrega?',
      icon: '🚚',
      description: 'Verifica status de entrega',
      requiredPermissions: ['read:shipment']
    },
    {
      label: 'Consultar ETA',
      action: 'Quando chega o container ABC123?',
      icon: '⏰',
      description: 'Previsão de chegada',
      requiredPermissions: ['read:container']
    }
  ],
  'gatekeeper': [
    {
      label: 'Validar Usuário',
      action: 'Validar usuário admin_001',
      icon: '🔐',
      description: 'Autentica credenciais',
      requiredPermissions: ['read:auth']
    },
    {
      label: 'Verificar Permissões',
      action: 'Verificar permissões do usuário atual',
      icon: '🔑',
      description: 'Lista permissões ativas',
      requiredPermissions: ['read:auth']
    },
    {
      label: 'Status da Sessão',
      action: 'Status da sessão atual',
      icon: '🕒',
      description: 'Informações da sessão',
      requiredPermissions: ['read:auth']
    },
    {
      label: 'Logs de Acesso',
      action: 'Logs de acesso da última hora',
      icon: '📝',
      description: 'Auditoria de acessos',
      requiredPermissions: ['read:logs']
    }
  ],
  'customs': [
    {
      label: 'Consultar NCM',
      action: 'NCM para smartphones importados',
      icon: '📊',
      description: 'Busca código NCM',
      requiredPermissions: ['read:customs']
    },
    {
      label: 'Calcular Impostos',
      action: 'Impostos sobre eletrônicos importados',
      icon: '💰',
      description: 'Calcula taxas e impostos',
      requiredPermissions: ['read:customs']
    },
    {
      label: 'Status DU-E',
      action: 'Status do DU-E 123456789',
      icon: '🛃',
      description: 'Verifica declaração',
      requiredPermissions: ['read:documents']
    },
    {
      label: 'Documentos Necessários',
      action: 'Documentos necessários para exportação',
      icon: '📄',
      description: 'Lista documentação',
      requiredPermissions: ['read:documents']
    }
  ],
  'financial': [
    {
      label: 'Análise de Custos',
      action: 'Custos da operação último mês',
      icon: '💰',
      description: 'Relatório de custos',
      requiredPermissions: ['read:financial']
    },
    {
      label: 'Faturamento',
      action: 'Faturamento por cliente',
      icon: '📈',
      description: 'Receitas por cliente',
      requiredPermissions: ['read:billing']
    },
    {
      label: 'Margem de Lucro',
      action: 'Análise de margem de containers',
      icon: '📊',
      description: 'Calcula margens',
      requiredPermissions: ['read:financial']
    },
    {
      label: 'KPIs Financeiros',
      action: 'KPIs financeiros do trimestre',
      icon: '🎯',
      description: 'Indicadores chave',
      requiredPermissions: ['read:financial']
    }
  ]
}

export function QuickActions({ agentType, currentUser, onAction }: QuickActionsProps) {
  const actions = QUICK_ACTIONS[agentType] || []

  const hasPermission = (requiredPermissions?: string[]) => {
    if (currentUser.role === 'admin') return true
    if (!requiredPermissions) return true
    
    return requiredPermissions.some(permission => 
      currentUser.permissions.includes(permission)
    )
  }

  return (
    <div className={styles.container}>
      {actions.length === 0 ? (
        <div className={styles.emptyState}>
          <span className={styles.emptyIcon}>🤖</span>
          <p className={styles.emptyText}>
            Nenhuma ação rápida disponível para este agente
          </p>
        </div>
      ) : (
        <div className={styles.actionGrid}>
          {actions.map((action, index) => {
            const canUse = hasPermission(action.requiredPermissions)
            
            return (
              <div key={index} className={styles.actionCard}>
                <button
                  onClick={() => canUse && onAction(action.action)}
                  disabled={!canUse}
                  className={`${styles.actionButton} ${!canUse ? styles.disabled : ''}`}
                  title={action.description}
                >
                  <span className={styles.actionIcon}>{action.icon}</span>
                  <div className={styles.actionContent}>
                    <div className={styles.actionLabel}>{action.label}</div>
                    <div className={styles.actionDescription}>
                      {action.description}
                    </div>
                  </div>
                </button>
                
                {!canUse && action.requiredPermissions && (
                  <div className={styles.permissionWarning}>
                    <span className={styles.warningIcon}>🔒</span>
                    <span className={styles.warningText}>
                      Requer: {action.requiredPermissions.join(', ')}
                    </span>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
      
      <div className={styles.footer}>
        <p className={styles.footerText}>
          💡 Clique em uma ação para executá-la automaticamente
        </p>
      </div>
    </div>
  )
}