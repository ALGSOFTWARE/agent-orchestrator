// 💬 MIT Logistics Frontend - Authenticated Chat Page
// Rota exclusivamente autenticada para chat com agentes IA

'use client'

import { useIsAuthenticated, useCurrentUser } from '@/lib/store/auth'
import AuthenticatedChat from '@/components/chat/AuthenticatedChat'
import styles from '@/styles/pages/ChatPlayground.module.css'

export default function AuthenticatedChatPage() {
  // Estado de autenticação
  const isAuthenticated = useIsAuthenticated()
  const user = useCurrentUser()

  // === PROTEÇÃO DE ROTA === //
  // Se não autenticado, mostrar tela de login necessário
  if (!isAuthenticated || !user) {
    return (
      <div className={styles.container}>
        <div className={styles.authRequired}>
          <h2>🔐 Autenticação Necessária</h2>
          <p>Para acessar o chat com agentes IA, você precisa estar logado no sistema.</p>
          <p>Faça login através do painel de autenticação para continuar.</p>

          <div className={styles.authActions}>
            <button
              onClick={() => window.location.href = '/auth'}
              className={styles.loginButton}
            >
              🚪 Ir para Login
            </button>
            <button
              onClick={() => window.location.href = '/'}
              className={styles.homeButton}
            >
              🏠 Voltar ao Início
            </button>
          </div>
        </div>
      </div>
    )
  }

  // === CHAT AUTENTICADO === //
  return (
    <div className={styles.container}>
      {/* Header de identificação */}
      <div className={styles.authHeader}>
        <div className={styles.userInfo}>
          <h1>🤖 Chat Inteligente MIT Logistics</h1>
          <p>
            Conectado como <strong>{user.userName}</strong> ({user.role}) •
            Agentes IA especializados em logística
          </p>
        </div>

        <div className={styles.authBadge}>
          <span className={styles.statusDot}></span>
          Autenticado
        </div>
      </div>

      {/* Componente de chat autenticado */}
      <AuthenticatedChat
        className={styles.authenticatedChatContainer || ''}
        showHeader={false} // Header já está acima
        showSidebar={true}
      />
    </div>
  )
}