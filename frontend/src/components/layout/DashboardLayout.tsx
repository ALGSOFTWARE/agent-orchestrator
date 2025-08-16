// 📱 MIT Logistics Frontend - Dashboard Layout Component

'use client'

import { ReactNode, useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
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
  { href: '/monitoring', label: 'Monitoramento', icon: '📊', badge: 'Live' },
  { href: '/api-explorer', label: 'API Explorer', icon: '🔍' },
  { href: '/documents', label: 'Documentos', icon: '📁' },
  { href: '/settings', label: 'Configurações', icon: '⚙️' }
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const pathname = usePathname()

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [pathname])

  // Handle escape key to close mobile menu
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMobileMenuOpen(false)
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [])

  return (
    <div className={styles.layout}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
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

          {/* Logo */}
          <Link href="/" className={styles.logo}>
            <span className={styles.logoIcon}>🚛</span>
            <span className={styles.logoText}>
              MIT <strong>Logistics</strong>
            </span>
          </Link>

          {/* Desktop sidebar toggle */}
          <button
            className={styles.sidebarToggle}
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            aria-label="Toggle sidebar"
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>

          {/* Header actions */}
          <div className={styles.headerActions}>
            {/* System status indicator */}
            <div className={styles.statusIndicator} title="System Status">
              <div className={styles.statusDot} data-status="checking">
                <div className={styles.pulse}></div>
              </div>
              <span className={styles.statusText}>Sistema</span>
            </div>

            {/* Theme toggle */}
            <button
              className={styles.themeToggle}
              aria-label="Toggle theme"
              onClick={() => {
                const html = document.documentElement
                const currentTheme = html.getAttribute('data-theme')
                html.setAttribute('data-theme', currentTheme === 'dark' ? 'light' : 'dark')
              }}
            >
              🌙
            </button>

            {/* User info */}
            <div className={styles.userInfo}>
              <div className={styles.userAvatar}>👤</div>
              <div className={styles.userDetails}>
                <span className={styles.userName}>Teste User</span>
                <span className={styles.userRole}>Admin</span>
              </div>
            </div>
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
                href="/agents/playground"
                className={styles.quickAction}
                title="Teste rápido de agentes"
              >
                <span className={styles.quickActionIcon}>⚡</span>
                {!sidebarCollapsed && (
                  <span className={styles.quickActionLabel}>Teste Rápido</span>
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
                <div className={styles.version}>v1.0.0</div>
                <div className={styles.environment}>Development</div>
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