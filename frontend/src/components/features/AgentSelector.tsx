// 🎯 MIT Logistics Frontend - Agent Selector Component

'use client'

import { Card, CardHeader, CardTitle, CardDescription, CardContent, Badge } from '@/components/ui'
import type { UserContext, AgentType } from '@/types'
import styles from '@/styles/modules/AgentSelector.module.css'

interface AgentSelectorProps {
  currentUser: UserContext
  onSelect: (agentType: AgentType) => void
}

interface AgentConfig {
  id: AgentType
  name: string
  icon: string
  description: string
  capabilities: string[]
  requiredPermissions: string[]
  examples: string[]
}

const AVAILABLE_AGENTS: AgentConfig[] = [
  {
    id: 'mit-tracking',
    name: 'MIT Tracking Agent',
    icon: '📍',
    description: 'Especialista em rastreamento de cargas, containers e documentos logísticos',
    capabilities: [
      'Consulta CT-e por número',
      'Rastreamento de containers',
      'Status de entregas',
      'ETA/ETD de cargas',
      'Eventos de rota'
    ],
    requiredPermissions: ['read:cte', 'read:container', 'read:shipment'],
    examples: [
      'Onde está o meu BL ABC123?',
      'CT-e número 351234567890123456789012345678901234',
      'Qual o status da minha entrega?',
      'Quando chega o container MSKU1234567?'
    ]
  },
  {
    id: 'gatekeeper',
    name: 'Gatekeeper Agent',
    icon: '🛡️',
    description: 'Sistema de autenticação e controle de acesso aos recursos',
    capabilities: [
      'Validação de credenciais',
      'Controle de permissões',
      'Auditoria de acesso',
      'Gestão de sessões',
      'Logs de segurança'
    ],
    requiredPermissions: ['read:auth', 'write:auth'],
    examples: [
      'Validar usuário admin_001',
      'Verificar permissões do usuário',
      'Logs de acesso da última hora',
      'Renovar sessão ativa'
    ]
  },
  {
    id: 'customs',
    name: 'Customs Agent',
    icon: '🛃',
    description: 'Especialista em documentação aduaneira e regulamentações',
    capabilities: [
      'Validação de documentos',
      'Consulta NCM/HS',
      'Cálculo de impostos',
      'Status aduaneiro',
      'Conformidade regulatória'
    ],
    requiredPermissions: ['read:customs', 'read:documents'],
    examples: [
      'NCM para smartphones importados',
      'Documentos necessários para exportação',
      'Status do DU-E 123456789',
      'Impostos sobre eletrônicos'
    ]
  },
  {
    id: 'financial',
    name: 'Financial Agent',
    icon: '💳',
    description: 'Análise financeira e gestão de custos logísticos',
    capabilities: [
      'Análise de custos',
      'Conciliação financeira',
      'Relatórios de faturamento',
      'Gestão de pagamentos',
      'KPIs financeiros'
    ],
    requiredPermissions: ['read:financial', 'read:billing'],
    examples: [
      'Custos da operação último mês',
      'Faturamento por cliente',
      'Análise de margem de containers',
      'Pendências financeiras'
    ]
  }
]

export function AgentSelector({ currentUser, onSelect }: AgentSelectorProps) {
  const hasPermission = (requiredPermissions: string[]) => {
    if (currentUser.role === 'admin') return true
    return requiredPermissions.some(permission => 
      currentUser.permissions.includes(permission)
    )
  }

  const getAccessLevel = (requiredPermissions: string[]) => {
    if (currentUser.role === 'admin') return 'full'
    if (hasPermission(requiredPermissions)) return 'partial'
    return 'none'
  }

  return (
    <div className={styles.container}>
      <div className={styles.grid}>
        {AVAILABLE_AGENTS.map((agent) => {
          const accessLevel = getAccessLevel(agent.requiredPermissions)
          const canAccess = accessLevel !== 'none'
          
          return (
            <Card
              key={agent.id}
              className={`${styles.agentCard} ${!canAccess ? styles.disabled : ''}`}
              hoverable={canAccess}
              onClick={() => canAccess && onSelect(agent.id)}
            >
              <CardHeader>
                <div className={styles.agentHeader}>
                  <span className={styles.agentIcon}>{agent.icon}</span>
                  <div className={styles.agentInfo}>
                    <CardTitle level={4}>{agent.name}</CardTitle>
                    <div className={styles.accessBadge}>
                      {accessLevel === 'full' && (
                        <Badge variant="success" size="sm">
                          Acesso Total
                        </Badge>
                      )}
                      {accessLevel === 'partial' && (
                        <Badge variant="warning" size="sm">
                          Acesso Limitado
                        </Badge>
                      )}
                      {accessLevel === 'none' && (
                        <Badge variant="error" size="sm">
                          Sem Acesso
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
                <CardDescription>{agent.description}</CardDescription>
              </CardHeader>
              
              <CardContent>
                <div className={styles.section}>
                  <h5 className={styles.sectionTitle}>🎯 Capacidades</h5>
                  <ul className={styles.capabilityList}>
                    {agent.capabilities.slice(0, 3).map((capability, index) => (
                      <li key={index} className={styles.capabilityItem}>
                        {capability}
                      </li>
                    ))}
                    {agent.capabilities.length > 3 && (
                      <li className={styles.capabilityMore}>
                        +{agent.capabilities.length - 3} mais
                      </li>
                    )}
                  </ul>
                </div>

                <div className={styles.section}>
                  <h5 className={styles.sectionTitle}>💬 Exemplos de uso</h5>
                  <div className={styles.examples}>
                    {agent.examples.slice(0, 2).map((example, index) => (
                      <div key={index} className={styles.example}>
                        &quot;{example}&quot;
                      </div>
                    ))}
                  </div>
                </div>

                {!canAccess && (
                  <div className={styles.permissionWarning}>
                    <span className={styles.warningIcon}>⚠️</span>
                    <div className={styles.warningText}>
                      Você precisa das seguintes permissões:
                      <div className={styles.requiredPermissions}>
                        {agent.requiredPermissions.map(permission => (
                          <Badge key={permission} variant="outline" size="sm">
                            {permission}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}