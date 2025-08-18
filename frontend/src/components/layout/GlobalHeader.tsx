// 🌐 MIT Logistics Frontend - Global Header Component

'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useAuthStore, useCurrentUser } from '@/lib/store/auth'
import { useApiStatus } from '@/hooks/useApiStatus'
import styles from '@/styles/modules/GlobalHeader.module.css'

export function GlobalHeader() {
  const [showUserMenu, setShowUserMenu] = useState(false)
  const pathname = usePathname()
  const router = useRouter()
  const currentUser = useCurrentUser()
  const { logout } = useAuthStore()
  const { status: apiStatus, refresh: refreshApiStatus } = useApiStatus()

  // Handle escape key to close menus
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setShowUserMenu(false)
      }
    }

    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Element
      if (!target.closest(`.${styles.userInfo}`)) {
        setShowUserMenu(false)
      }
    }

    document.addEventListener('keydown', handleEscape)
    document.addEventListener('click', handleClickOutside)
    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.removeEventListener('click', handleClickOutside)
    }
  }, [])

  const handleLogout = () => {
    logout()
    setShowUserMenu(false)
    router.push('/')
  }

  // Get status label for tooltip
  const getStatusLabel = (status: 'healthy' | 'unhealthy' | 'checking') => {
    switch (status) {
      case 'healthy': return 'OK'
      case 'unhealthy': return 'Error'
      case 'checking': return 'Checking'
      default: return 'Unknown'
    }
  }

  // Only show header if user is authenticated
  if (!currentUser) {
    return null
  }

  return (
    <header className={styles.header}>
      <div className={styles.headerContent}>
        {/* Left section */}
        <div className={styles.headerLeft}>
          {/* Logo */}
          <Link href="/" className={styles.logo}>
            <span className={styles.logoIcon}>🚛</span>
            <span className={styles.logoText}>
              MIT <strong>Logistics</strong>
            </span>
          </Link>
        </div>

        {/* Center section - API Status */}
        <div className={styles.headerCenter}>
          <div className={styles.statusRow}>
            <span className={styles.statusLabel}>Status:</span>
            <div className={styles.statusItems}>
              {Object.entries(apiStatus).map(([key, status]) => {
                if (key === 'lastUpdate') return null
                const serviceStatus = status as any
                const statusLabel = getStatusLabel(serviceStatus.status)
                
                return (
                  <div 
                    key={key} 
                    className={styles.statusBadge}
                    title={`${serviceStatus.service}: ${statusLabel}${serviceStatus.responseTime ? ` (${Math.round(serviceStatus.responseTime)}ms)` : ''}`}
                  >
                    <div 
                      className={styles.statusDot} 
                      data-status={serviceStatus.status}
                    ></div>
                    <span>{serviceStatus.service}</span>
                  </div>
                )
              })}
            </div>
            <button
              className={styles.refreshButton}
              onClick={refreshApiStatus}
              title="Atualizar status"
            >
              🔄
            </button>
          </div>
        </div>

        {/* Right section */}
        <div className={styles.headerRight}>
          {/* Current user info */}
          <div className={styles.currentUserInfo}>
            <div className={styles.userBadge}>
              <span className={styles.userIcon}>👤</span>
              <div className={styles.userDetails}>
                <span className={styles.userName}>{currentUser?.userId || 'Usuário'}</span>
                <span className={styles.userRole}>{currentUser?.role || 'Sem role'}</span>
              </div>
            </div>
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
            title="Alternar tema"
          >
            🌙
          </button>

          {/* Logout button */}
          <button
            className={styles.logoutButton}
            onClick={handleLogout}
            title="Sair do sistema"
          >
            <span className={styles.logoutIcon}>🚪</span>
            <span className={styles.logoutText}>Sair</span>
          </button>

          {/* Navigation link to dashboard if not already there */}
          {!pathname.startsWith('/agents') && !pathname.startsWith('/monitoring') && !pathname.startsWith('/api-explorer') && !pathname.startsWith('/documents') && !pathname.startsWith('/settings') && (
            <Link href="/agents" className={styles.dashboardLink} title="Ir para Dashboard">
              <span className={styles.dashboardIcon}>🎛️</span>
              <span className={styles.dashboardText}>Dashboard</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}