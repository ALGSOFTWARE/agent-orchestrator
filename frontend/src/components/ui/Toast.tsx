// 🍞 MIT Logistics Frontend - Toast Component

'use client'

import { useEffect } from 'react'
import { useToasts } from '@/lib/store/app'
import type { ToastMessage } from '@/types'
import styles from '@/styles/modules/Toast.module.css'

interface ToastProps {
  toast: ToastMessage
  onRemove: (id: string) => void
}

function Toast({ toast, onRemove }: ToastProps) {
  useEffect(() => {
    if (toast.duration && toast.duration > 0) {
      const timer = setTimeout(() => {
        onRemove(toast.id)
      }, toast.duration)
      
      return () => clearTimeout(timer)
    }
  }, [toast.id, toast.duration, onRemove])

  const getIcon = () => {
    switch (toast.type) {
      case 'success': return '✅'
      case 'error': return '❌'
      case 'warning': return '⚠️'
      case 'info': return 'ℹ️'
      default: return '📢'
    }
  }

  return (
    <div 
      className={`${styles.toast} ${styles[toast.type]}`}
      role="alert"
      aria-live="polite"
    >
      <div className={styles.icon}>
        {getIcon()}
      </div>
      
      <div className={styles.content}>
        <div className={styles.title}>{toast.title}</div>
        {toast.description && (
          <div className={styles.message}>{toast.description}</div>
        )}
      </div>
      
      <button
        onClick={() => onRemove(toast.id)}
        className={styles.closeButton}
        aria-label="Fechar notificação"
      >
        ✕
      </button>
    </div>
  )
}

export function ToastContainer() {
  const { toasts, removeToast } = useToasts()

  if (toasts.length === 0) return null

  return (
    <div className={styles.container}>
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          toast={toast}
          onRemove={removeToast}
        />
      ))}
    </div>
  )
}

// Helper hook for easy toast usage
export function useToast() {
  const { addToast } = useToasts()

  const toast = {
    success: (title: string, description?: string) => 
      addToast({ type: 'success', title, ...(description && { description }) }),
    
    error: (title: string, description?: string) => 
      addToast({ type: 'error', title, ...(description && { description }) }),
    
    warning: (title: string, description?: string) => 
      addToast({ type: 'warning', title, ...(description && { description }) }),
    
    info: (title: string, description?: string) => 
      addToast({ type: 'info', title, ...(description && { description }) }),
  }

  return toast
}