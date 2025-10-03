// 🔐 MIT Logistics Frontend - Authentication Store

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { 
  type UserContext, 
  type AuthPayload, 
  type UserRole,
  type GatekeeperResponse 
} from '@/types'
import { authenticateUser, TEST_USERS, loginWithGatekeeper, logoutFromGatekeeper } from '@/lib/api/gatekeeper'

interface AuthState {
  // Current user state
  user: UserContext | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Authentication session
  sessionId: string | null
  authenticatedAgent: string | null
  lastAuthResponse: GatekeeperResponse | null

  // JWT token
  token: string | null
  tokenExpires: number | null

  // Actions
  login: (payload: AuthPayload) => Promise<void>
  loginWithTestUser: (userType: keyof typeof TEST_USERS) => Promise<void>
  loginWithJWT: (email: string, password?: string) => Promise<void>
  logout: () => void
  clearError: () => void
  refreshSession: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      sessionId: null,
      authenticatedAgent: null,
      lastAuthResponse: null,
      token: null,
      tokenExpires: null,

      // Login with custom payload
      login: async (payload: AuthPayload) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await authenticateUser(payload)
          
          if (response.status === 'success') {
            const userContext: UserContext = {
              userId: payload.userId,
              role: payload.role,
              permissions: payload.permissions,
              sessionId: payload.sessionId || `session_${Date.now()}`,
              timestamp: new Date().toISOString()
            }
            
            set({
              user: userContext,
              isAuthenticated: true,
              isLoading: false,
              error: null,
              sessionId: userContext.sessionId || null,
              authenticatedAgent: response.agent || null,
              lastAuthResponse: response
            })
          } else {
            throw new Error(response.message || 'Authentication failed')
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Authentication failed'
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: errorMessage,
            sessionId: null,
            authenticatedAgent: null,
            lastAuthResponse: null
          })
          throw error
        }
      },

      // Login with predefined test user
      loginWithTestUser: async (userType: keyof typeof TEST_USERS) => {
        const testUser = TEST_USERS[userType]
        const payload: AuthPayload = {
          ...testUser,
          timestamp: new Date().toISOString(),
          sessionId: `test_session_${userType}_${Date.now()}`
        }

        await get().login(payload)
      },

      // Login with JWT real do Gatekeeper
      loginWithJWT: async (email: string, password?: string) => {
        set({ isLoading: true, error: null })

        try {
          const response = await loginWithGatekeeper(email, password)

          if (response.success) {
            const userContext: UserContext = {
              userId: response.user.id,
              userName: response.user.name,
              role: response.user.role as UserRole,
              permissions: response.context?.permissions || [],
              sessionId: `jwt_session_${Date.now()}`,
              timestamp: new Date().toISOString()
            }

            const tokenExpires = Date.now() + (response.expiresIn * 1000)

            set({
              user: userContext,
              isAuthenticated: true,
              isLoading: false,
              error: null,
              sessionId: userContext.sessionId || null,
              authenticatedAgent: 'LogisticsAgent', // Default agent
              lastAuthResponse: null,
              token: response.token,
              tokenExpires
            })
          } else {
            throw new Error('Falha na autenticação com JWT')
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Falha na autenticação JWT'
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: errorMessage,
            sessionId: null,
            authenticatedAgent: null,
            lastAuthResponse: null,
            token: null,
            tokenExpires: null
          })
          throw error
        }
      },

      // Logout
      logout: async () => {
        try {
          await logoutFromGatekeeper()
        } catch (error) {
          console.warn('⚠️ Erro no logout do Gatekeeper:', error)
        }

        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
          sessionId: null,
          authenticatedAgent: null,
          lastAuthResponse: null,
          token: null,
          tokenExpires: null
        })
      },

      // Clear error
      clearError: () => {
        set({ error: null })
      },

      // Refresh session
      refreshSession: async () => {
        const { user } = get()
        if (!user) return
        
        const payload: AuthPayload = {
          userId: user.userId,
          role: user.role as UserRole,
          permissions: user.permissions,
          sessionId: user.sessionId || `session_${Date.now()}`,
          timestamp: new Date().toISOString()
        }
        
        await get().login(payload)
      }
    }),
    {
      name: 'mit-auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        sessionId: state.sessionId,
        authenticatedAgent: state.authenticatedAgent,
        token: state.token,
        tokenExpires: state.tokenExpires
      })
    }
  )
)

// === HELPER FUNCTIONS === //

export function useCurrentUser() {
  return useAuthStore((state) => state.user)
}

export function useIsAuthenticated() {
  return useAuthStore((state) => state.isAuthenticated)
}

export function useAuthLoading() {
  return useAuthStore((state) => state.isLoading)
}

export function useAuthError() {
  return useAuthStore((state) => state.error)
}

export function useAuthenticatedAgent() {
  return useAuthStore((state) => state.authenticatedAgent)
}

// Check if user has specific permission
export function useHasPermission(permission: string) {
  return useAuthStore((state) => {
    if (!state.user || !state.isAuthenticated) return false
    if (state.user.role === 'admin') return true // Admin has all permissions
    return state.user.permissions.includes(permission)
  })
}

// Check if user has specific role
export function useHasRole(role: UserRole) {
  return useAuthStore((state) => {
    if (!state.user || !state.isAuthenticated) return false
    return state.user.role === role
  })
}

// Get user role
export function useUserRole() {
  return useAuthStore((state) => state.user?.role as UserRole | null)
}

// Get JWT token
export function useAuthToken() {
  return useAuthStore((state) => state.token)
}

// Check if token is expired
export function useIsTokenExpired() {
  return useAuthStore((state) => {
    if (!state.token || !state.tokenExpires) return true
    return Date.now() >= state.tokenExpires
  })
}

// Get token expiration time
export function useTokenExpiresIn() {
  return useAuthStore((state) => {
    if (!state.tokenExpires) return null
    return Math.max(0, state.tokenExpires - Date.now())
  })
}