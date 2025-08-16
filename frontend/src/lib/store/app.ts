// 🎛️ MIT Logistics Frontend - App Store

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { 
  type ToastMessage, 
  type ChatSession, 
  type ServiceStatus, 
  type SystemMetrics, 
  type LogEntry 
} from '@/types'

interface AppState {
  // UI State
  theme: 'light' | 'dark'
  sidebarCollapsed: boolean
  
  // Toast notifications
  toasts: ToastMessage[]
  
  // Chat sessions
  activeChatSession: ChatSession | null
  chatHistory: ChatSession[]
  
  // Monitoring data
  services: ServiceStatus[]
  metrics: SystemMetrics[]
  logs: LogEntry[]
  
  // System state
  systemInitialized: boolean
  lastHealthCheck: string | null
  
  // Actions
  toggleTheme: () => void
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  
  // Toast actions
  addToast: (toast: Omit<ToastMessage, 'id'>) => void
  removeToast: (id: string) => void
  clearToasts: () => void
  
  // Chat actions
  setActiveChatSession: (session: ChatSession | null) => void
  addChatSession: (session: ChatSession) => void
  updateChatSession: (sessionId: string, updates: Partial<ChatSession>) => void
  removeChatSession: (sessionId: string) => void
  clearChatHistory: () => void
  
  // Monitoring actions
  updateServiceStatus: (service: ServiceStatus) => void
  updateServices: (services: ServiceStatus[]) => void
  addMetrics: (metrics: SystemMetrics) => void
  addLog: (log: LogEntry) => void
  clearLogs: () => void
  
  // System actions
  setSystemInitialized: (initialized: boolean) => void
  setLastHealthCheck: (timestamp: string) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      theme: 'light',
      sidebarCollapsed: false,
      toasts: [],
      activeChatSession: null,
      chatHistory: [],
      services: [],
      metrics: [],
      logs: [],
      systemInitialized: false,
      lastHealthCheck: null,

      // UI Actions
      toggleTheme: () => {
        set((state) => {
          const newTheme = state.theme === 'light' ? 'dark' : 'light'
          
          // Update DOM immediately
          if (typeof document !== 'undefined') {
            document.documentElement.setAttribute('data-theme', newTheme)
          }
          
          return { theme: newTheme }
        })
      },

      toggleSidebar: () => {
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }))
      },

      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed })
      },

      // Toast Actions
      addToast: (toast) => {
        const id = `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        const newToast: ToastMessage = {
          ...toast,
          id,
          duration: toast.duration || 5000
        }
        
        set((state) => ({
          toasts: [...state.toasts, newToast]
        }))

        // Auto remove toast after duration
        if (newToast.duration && newToast.duration > 0) {
          setTimeout(() => {
            get().removeToast(id)
          }, newToast.duration)
        }
      },

      removeToast: (id: string) => {
        set((state) => ({
          toasts: state.toasts.filter(toast => toast.id !== id)
        }))
      },

      clearToasts: () => {
        set({ toasts: [] })
      },

      // Chat Actions
      setActiveChatSession: (session: ChatSession | null) => {
        set({ activeChatSession: session })
      },

      addChatSession: (session: ChatSession) => {
        set((state) => ({
          chatHistory: [session, ...state.chatHistory],
          activeChatSession: session
        }))
      },

      updateChatSession: (sessionId: string, updates: Partial<ChatSession>) => {
        set((state) => ({
          chatHistory: state.chatHistory.map(session =>
            session.id === sessionId 
              ? { ...session, ...updates, updatedAt: new Date().toISOString() }
              : session
          ),
          activeChatSession: state.activeChatSession?.id === sessionId
            ? { ...state.activeChatSession, ...updates, updatedAt: new Date().toISOString() }
            : state.activeChatSession
        }))
      },

      removeChatSession: (sessionId: string) => {
        set((state) => ({
          chatHistory: state.chatHistory.filter(session => session.id !== sessionId),
          activeChatSession: state.activeChatSession?.id === sessionId 
            ? null 
            : state.activeChatSession
        }))
      },

      clearChatHistory: () => {
        set({ chatHistory: [], activeChatSession: null })
      },

      // Monitoring Actions
      updateServiceStatus: (service: ServiceStatus) => {
        set((state) => {
          const existingIndex = state.services.findIndex(s => s.name === service.name)
          
          if (existingIndex >= 0) {
            const updatedServices = [...state.services]
            updatedServices[existingIndex] = service
            return { services: updatedServices }
          } else {
            return { services: [...state.services, service] }
          }
        })
      },

      updateServices: (services: ServiceStatus[]) => {
        set({ services })
      },

      addMetrics: (metrics: SystemMetrics) => {
        set((state) => ({
          metrics: [metrics, ...state.metrics].slice(0, 100) // Keep last 100 metrics
        }))
      },

      addLog: (log: LogEntry) => {
        set((state) => ({
          logs: [log, ...state.logs].slice(0, 1000) // Keep last 1000 logs
        }))
      },

      clearLogs: () => {
        set({ logs: [] })
      },

      // System Actions
      setSystemInitialized: (initialized: boolean) => {
        set({ systemInitialized: initialized })
      },

      setLastHealthCheck: (timestamp: string) => {
        set({ lastHealthCheck: timestamp })
      }
    }),
    {
      name: 'mit-app-storage',
      partialize: (state) => ({
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
        chatHistory: state.chatHistory.slice(0, 10), // Persist only last 10 chat sessions
        systemInitialized: state.systemInitialized
      })
    }
  )
)

// === HELPER HOOKS === //

export function useTheme() {
  return useAppStore((state) => state.theme)
}

export function useSidebar() {
  return {
    collapsed: useAppStore((state) => state.sidebarCollapsed),
    toggle: useAppStore((state) => state.toggleSidebar),
    setCollapsed: useAppStore((state) => state.setSidebarCollapsed)
  }
}

export function useToasts() {
  return {
    toasts: useAppStore((state) => state.toasts),
    addToast: useAppStore((state) => state.addToast),
    removeToast: useAppStore((state) => state.removeToast),
    clearToasts: useAppStore((state) => state.clearToasts)
  }
}

export function useChat() {
  return {
    activeSession: useAppStore((state) => state.activeChatSession),
    history: useAppStore((state) => state.chatHistory),
    setActiveSession: useAppStore((state) => state.setActiveChatSession),
    addSession: useAppStore((state) => state.addChatSession),
    updateSession: useAppStore((state) => state.updateChatSession),
    removeSession: useAppStore((state) => state.removeChatSession),
    clearHistory: useAppStore((state) => state.clearChatHistory)
  }
}

export function useMonitoring() {
  return {
    services: useAppStore((state) => state.services),
    metrics: useAppStore((state) => state.metrics),
    logs: useAppStore((state) => state.logs),
    updateService: useAppStore((state) => state.updateServiceStatus),
    updateServices: useAppStore((state) => state.updateServices),
    addMetrics: useAppStore((state) => state.addMetrics),
    addLog: useAppStore((state) => state.addLog),
    clearLogs: useAppStore((state) => state.clearLogs),
    lastHealthCheck: useAppStore((state) => state.lastHealthCheck),
    setLastHealthCheck: useAppStore((state) => state.setLastHealthCheck)
  }
}

export function useSystem() {
  return {
    initialized: useAppStore((state) => state.systemInitialized),
    setInitialized: useAppStore((state) => state.setSystemInitialized)
  }
}