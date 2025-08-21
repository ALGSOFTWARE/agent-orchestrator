// 📱 MIT Logistics Frontend - Dashboard Layout Component

'use client'

import { ReactNode, useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useCurrentUser } from '@/lib/store/auth'
import styles from '@/styles/modules/DashboardLayout.module.css'

interface DashboardLayoutProps {
  children: ReactNode
}

interface NavItem {
  href: string
  label: string
  icon: string
  badge?: string
}

const navigationItems: NavItem[] = [
  { href: '/agents', label: 'Agentes de IA', icon: '🤖' },
  { href: '/chat', label: 'Sandbox de Agentes', icon: '💬', badge: 'Público' },
  { href: '/orders', label: 'Orders', icon: '📋', badge: 'Super-contêiner' },
  { href: '/visualizations', label: 'Visualizações Inteligentes', icon: '🗺️', badge: 'Graph+Map+Search' },
  { href: '/search', label: 'Busca de Documentos', icon: '🔍', badge: 'Clássica' },
  { href: '/monitoring', label: 'Monitoramento', icon: '📊', badge: 'Live' },
  { href: '/api-explorer', label: 'API Explorer', icon: '🛠️' },
  { href: '/documents', label: 'Documentos', icon: '📁' },
  { href: '/settings', label: 'Configurações', icon: '⚙️' }
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const pathname = usePathname()
  const router = useRouter()
  const currentUser = useCurrentUser()

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [pathname])

  // Handle escape key to close menus
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMobileMenuOpen(false)
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }, [])

  // Redirect if not authenticated - only for sensitive routes
  useEffect(() => {
    const sensitiveRoutes = ['/settings/admin', '/api-explorer/admin']
    const isSensitiveRoute = sensitiveRoutes.some(route => pathname.startsWith(route))
    
    if (!currentUser && isSensitiveRoute) {
      router.push('/')
    }
  }, [currentUser, router, pathname])


  return (
    <div className={styles.layout}>
      {/* Dashboard Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          {/* Left section */}
          <div className={styles.headerLeft}>
            {/* Mobile menu button */}
            <button
              className={styles.mobileMenuButton}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              <span className={styles.hamburger}>
                <span></span>
                <span></span>
                <span></span>
              </span>
            </button>

            {/* Dashboard title */}
            <div className={styles.dashboardTitle}>
              <span className={styles.dashboardIcon}>🎛️</span>
              <span className={styles.dashboardText}>Dashboard</span>
            </div>

            {/* Desktop sidebar toggle */}
            <button
              className={styles.sidebarToggle}
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              aria-label="Toggle sidebar"
            >
              {sidebarCollapsed ? '→' : '←'}
            </button>
          </div>

          {/* Right section - Just return to home link */}
          <div className={styles.headerRight}>
            <Link href="/" className={styles.backToHome} title="Voltar à página inicial">
              ← Início
            </Link>
          </div>
        </div>
      </header>

      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div
          className={styles.mobileOverlay}
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`${styles.sidebar} ${
          sidebarCollapsed ? styles.sidebarCollapsed : ''
        } ${mobileMenuOpen ? styles.sidebarMobileOpen : ''}`}
      >
        <nav className={styles.navigation}>
          <ul className={styles.navList}>
            {navigationItems.map((item) => {
              const isActive = pathname.startsWith(item.href)
              
              return (
                <li key={item.href} className={styles.navItem}>
                  <Link
                    href={item.href}
                    className={`${styles.navLink} ${
                      isActive ? styles.navLinkActive : ''
                    }`}
                  >
                    <span className={styles.navIcon}>{item.icon}</span>
                    <span className={styles.navLabel}>{item.label}</span>
                    {item.badge && (
                      <span className={styles.navBadge}>{item.badge}</span>
                    )}
                  </Link>
                </li>
              )
            })}
          </ul>

          {/* Quick actions */}
          <div className={styles.quickActions}>
            <div className={styles.quickActionsTitle}>
              {!sidebarCollapsed && 'Ações Rápidas'}
            </div>
            <div className={styles.quickActionsList}>
              <Link
                href="/visualizations"
                className={styles.quickAction}
                title="Visualizações inteligentes com busca semântica"
              >
                <span className={styles.quickActionIcon}>🔍</span>
                {!sidebarCollapsed && (
                  <span className={styles.quickActionLabel}>Busca Visual</span>
                )}
              </Link>
              <Link
                href="/api-explorer/graphql"
                className={styles.quickAction}
                title="GraphQL Playground"
              >
                <span className={styles.quickActionIcon}>🎮</span>
                {!sidebarCollapsed && (
                  <span className={styles.quickActionLabel}>GraphQL</span>
                )}
              </Link>
              <Link
                href="/settings/llm"
                className={styles.quickAction}
                title="Configurar LLM"
              >
                <span className={styles.quickActionIcon}>🧠</span>
                {!sidebarCollapsed && (
                  <span className={styles.quickActionLabel}>LLM Config</span>
                )}
              </Link>
              <Link
                href="/monitoring/logs"
                className={styles.quickAction}
                title="Logs do sistema"
              >
                <span className={styles.quickActionIcon}>📝</span>
                {!sidebarCollapsed && (
                  <span className={styles.quickActionLabel}>Logs</span>
                )}
              </Link>
            </div>
          </div>
        </nav>

        {/* Sidebar footer */}
        <div className={styles.sidebarFooter}>
          {!sidebarCollapsed && (
            <>
              <div className={styles.sidebarFooterInfo}>
                <div className={styles.version}>v2.0.0</div>
                <div className={styles.environment}>OpenAI + Gemini</div>
              </div>
              <Link
                href="/"
                className={styles.backToHome}
                title="Voltar à página inicial"
              >
                ← Início
              </Link>
            </>
          )}
        </div>
      </aside>

      {/* Main content */}
      <main
        className={`${styles.main} ${
          sidebarCollapsed ? styles.mainExpanded : ''
        }`}
      >
        <div className={styles.content}>
          {children}
        </div>
      </main>
    </div>
  )
}