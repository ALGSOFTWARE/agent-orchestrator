// 🤖 MIT Logistics Frontend - Agent Tester Page

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui'
import { AgentTester } from '@/components/features/AgentTester'
import { AgentSelector } from '@/components/features/AgentSelector'
import { useCurrentUser } from '@/lib/store/auth'
import type { AgentType } from '@/types'
import styles from '@/styles/pages/AgentsPage.module.css'

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<AgentType | null>(null)
  const currentUser = useCurrentUser()
  const router = useRouter()

  // Show login prompt if not authenticated
  if (!currentUser) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.headerContent}>
            <h1 className={styles.title}>🤖 Agent Tester</h1>
            <p className={styles.description}>
              Faça login para testar os agentes de IA especializados em logística.
            </p>
          </div>
        </div>
        <div className={styles.content}>
          <Card className={styles.selectionCard}>
            <CardHeader>
              <CardTitle>Login Necessário</CardTitle>
              <CardDescription>
                Você precisa fazer login para acessar os agentes. Volte à página inicial e faça login.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>🤖 Agent Tester</h1>
          <p className={styles.description}>
            Teste e interaja com os agentes de IA especializados em logística.
            Simule consultas reais e veja como os agentes processam diferentes tipos de dados.
          </p>
        </div>
        
        <div className={styles.userInfo}>
          <div className={styles.userBadge}>
            <span className={styles.userIcon}>
              {currentUser.role === 'admin' && '👑'}
              {currentUser.role === 'logistics' && '📦'}
              {currentUser.role === 'finance' && '💰'}
              {currentUser.role === 'operator' && '🔧'}
            </span>
            <div className={styles.userDetails}>
              <div className={styles.userName}>{currentUser.userId}</div>
              <div className={styles.userRole}>{currentUser.role}</div>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.content}>
        {!selectedAgent ? (
          <div className={styles.selectionView}>
            <Card className={styles.selectionCard}>
              <CardHeader>
                <CardTitle>Escolha um Agente</CardTitle>
                <CardDescription>
                  Selecione um agente especializado para começar os testes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AgentSelector
                  currentUser={currentUser}
                  onSelect={setSelectedAgent}
                />
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className={styles.testerView}>
            <div className={styles.testerHeader}>
              <button
                onClick={() => setSelectedAgent(null)}
                className={styles.backButton}
              >
                ← Voltar
              </button>
              <div className={styles.selectedAgent}>
                <span className={styles.agentIcon}>
                  {selectedAgent === 'mit-tracking' && '📍'}
                  {selectedAgent === 'gatekeeper' && '🛡️'}
                  {selectedAgent === 'customs' && '🛃'}
                  {selectedAgent === 'financial' && '💳'}
                </span>
                <div className={styles.agentName}>
                  {selectedAgent.charAt(0).toUpperCase() + selectedAgent.slice(1)} Agent
                </div>
              </div>
            </div>
            
            <AgentTester
              agentType={selectedAgent}
              currentUser={currentUser}
            />
          </div>
        )}
      </div>
    </div>
  )
}