// 🔐 MIT Logistics Frontend - Authentication Modal

'use client'

import { useState } from 'react'
import { useAuthStore, useCurrentUser, useAuthLoading, useAuthError } from '@/lib/store/auth'
import { TEST_USERS } from '@/lib/api/gatekeeper'
import type { UserRole, AuthPayload } from '@/types'
import styles from '@/styles/modules/AuthModal.module.css'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
}

export function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [activeTab, setActiveTab] = useState<'quick' | 'custom'>('quick')
  const [customForm, setCustomForm] = useState({
    userId: '',
    role: 'logistics' as UserRole,
    permissions: [] as string[]
  })

  const { login, loginWithTestUser, clearError } = useAuthStore()
  const currentUser = useCurrentUser()
  const isLoading = useAuthLoading()
  const error = useAuthError()

  // Close modal if user is authenticated
  if (currentUser && isOpen) {
    onClose()
  }

  const handleQuickLogin = async (userType: keyof typeof TEST_USERS) => {
    try {
      await loginWithTestUser(userType)
      onClose()
    } catch (error) {
      // Error is handled by store
    }
  }

  const handleCustomLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!customForm.userId.trim()) {
      return
    }

    try {
      const payload: AuthPayload = {
        userId: customForm.userId.trim(),
        role: customForm.role,
        permissions: customForm.permissions,
        sessionId: `custom_session_${Date.now()}`,
        timestamp: new Date().toISOString()
      }

      await login(payload)
      onClose()
    } catch (error) {
      // Error is handled by store
    }
  }

  const addPermission = (permission: string) => {
    if (!customForm.permissions.includes(permission)) {
      setCustomForm(prev => ({
        ...prev,
        permissions: [...prev.permissions, permission]
      }))
    }
  }

  const removePermission = (permission: string) => {
    setCustomForm(prev => ({
      ...prev,
      permissions: prev.permissions.filter(p => p !== permission)
    }))
  }

  const commonPermissions = {
    admin: ['*'],
    logistics: ['read:cte', 'write:document', 'read:container', 'write:tracking', 'read:shipment'],
    finance: ['read:financial', 'write:financial', 'read:payment', 'write:payment', 'read:billing'],
    operator: ['read:cte', 'write:document', 'read:container']
  }

  if (!isOpen) return null

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h2 className={styles.title}>🔐 Autenticação do Sistema</h2>
          <p className={styles.subtitle}>
            Teste diferentes usuários e permissões com o Gatekeeper Agent
          </p>
          <button 
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Fechar modal"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className={styles.error}>
            <span className={styles.errorIcon}>⚠️</span>
            {error}
            <button 
              className={styles.errorClose}
              onClick={clearError}
            >
              ✕
            </button>
          </div>
        )}

        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${activeTab === 'quick' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('quick')}
          >
            ⚡ Usuários de Teste
          </button>
          <button
            className={`${styles.tab} ${activeTab === 'custom' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('custom')}
          >
            🛠️ Usuário Personalizado
          </button>
        </div>

        <div className={styles.content}>
          {activeTab === 'quick' && (
            <div className={styles.quickTab}>
              <p className={styles.tabDescription}>
                Usuários pré-configurados para teste rápido dos agentes
              </p>
              
              <div className={styles.userGrid}>
                {Object.entries(TEST_USERS).map(([key, user]) => (
                  <div key={key} className={styles.userCard}>
                    <div className={styles.userHeader}>
                      <div className={styles.userIcon}>
                        {key === 'admin' && '👑'}
                        {key === 'logistics' && '📦'}
                        {key === 'finance' && '💰'}
                        {key === 'operator' && '🔧'}
                        {key === 'invalid' && '❌'}
                      </div>
                      <div className={styles.userInfo}>
                        <h4 className={styles.userTitle}>
                          {key.charAt(0).toUpperCase() + key.slice(1)}
                        </h4>
                        <p className={styles.userRole}>{user.role}</p>
                      </div>
                    </div>
                    
                    <div className={styles.userPermissions}>
                      {user.permissions.slice(0, 3).map(permission => (
                        <span key={permission} className={styles.permission}>
                          {permission}
                        </span>
                      ))}
                      {user.permissions.length > 3 && (
                        <span className={styles.permissionMore}>
                          +{user.permissions.length - 3}
                        </span>
                      )}
                    </div>

                    <button
                      className={styles.loginButton}
                      onClick={() => handleQuickLogin(key as keyof typeof TEST_USERS)}
                      disabled={isLoading}
                    >
                      {isLoading ? '🔄 Autenticando...' : '🚀 Entrar'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'custom' && (
            <div className={styles.customTab}>
              <p className={styles.tabDescription}>
                Crie um usuário personalizado para testes específicos
              </p>

              <form onSubmit={handleCustomLogin} className={styles.form}>
                <div className={styles.field}>
                  <label className={styles.label}>
                    👤 User ID
                  </label>
                  <input
                    type="text"
                    className={styles.input}
                    value={customForm.userId}
                    onChange={(e) => setCustomForm(prev => ({ ...prev, userId: e.target.value }))}
                    placeholder="Ex: test_user_001"
                    required
                  />
                </div>

                <div className={styles.field}>
                  <label className={styles.label}>
                    🎭 Role
                  </label>
                  <select
                    className={styles.select}
                    value={customForm.role}
                    onChange={(e) => {
                      const newRole = e.target.value as UserRole
                      setCustomForm(prev => ({
                        ...prev,
                        role: newRole,
                        permissions: commonPermissions[newRole] || []
                      }))
                    }}
                  >
                    <option value="admin">Admin</option>
                    <option value="logistics">Logistics</option>
                    <option value="finance">Finance</option>
                    <option value="operator">Operator</option>
                  </select>
                </div>

                <div className={styles.field}>
                  <label className={styles.label}>
                    🔑 Permissões
                  </label>
                  <div className={styles.permissionsContainer}>
                    <div className={styles.currentPermissions}>
                      {customForm.permissions.map(permission => (
                        <span key={permission} className={styles.permissionTag}>
                          {permission}
                          <button
                            type="button"
                            onClick={() => removePermission(permission)}
                            className={styles.permissionRemove}
                          >
                            ✕
                          </button>
                        </span>
                      ))}
                    </div>
                    
                    <div className={styles.permissionSuggestions}>
                      <p className={styles.suggestionsLabel}>Sugestões para {customForm.role}:</p>
                      <div className={styles.suggestions}>
                        {commonPermissions[customForm.role]?.map(permission => (
                          !customForm.permissions.includes(permission) && (
                            <button
                              key={permission}
                              type="button"
                              className={styles.suggestionButton}
                              onClick={() => addPermission(permission)}
                            >
                              + {permission}
                            </button>
                          )
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  className={styles.submitButton}
                  disabled={isLoading || !customForm.userId.trim()}
                >
                  {isLoading ? '🔄 Autenticando...' : '🚀 Entrar com Usuário Personalizado'}
                </button>
              </form>
            </div>
          )}
        </div>

        <div className={styles.footer}>
          <p className={styles.footerText}>
            🔒 Esta é uma simulação para testes. Em produção, a autenticação seria feita por uma API externa.
          </p>
        </div>
      </div>
    </div>
  )
}