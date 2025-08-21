'use client'

import { useEffect } from 'react'
import { createPortal } from 'react-dom'
import styles from '@/styles/modules/Modal.module.css'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  className?: string
}

export function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'lg',
  className = '' 
}: ModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        console.log('🔍 ESC pressionado - fechando modal')
        onClose()
      }
    }

    if (isOpen) {
      console.log('🔍 Modal aberto - configurando eventos')
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    } else {
      console.log('🔍 Modal fechado - limpando eventos')
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'auto'
    }
  }, [isOpen, onClose])

  if (!isOpen) {
    console.log('🔍 Modal não deve ser renderizado (isOpen = false)')
    return null
  }

  console.log('🔍 Renderizando modal com size:', size)
  console.log('🔍 Styles objeto:', styles)
  console.log('🔍 Document body existe:', !!document.body)

  const sizeClass = {
    sm: styles.sizeSm,
    md: styles.sizeMd,
    lg: styles.sizeLg,
    xl: styles.sizeXl,
    full: styles.sizeFull
  }[size]

  const maxHeightClass = size === 'full' ? '' : styles.maxHeightNormal
  
  console.log('🔍 SizeClass aplicada:', sizeClass)
  console.log('🔍 MaxHeightClass aplicada:', maxHeightClass)

  const modalContent = (
    <div className={styles.modalOverlay}>
      {/* Backdrop */}
      <div 
        className={styles.modalBackdrop}
        onClick={() => {
          console.log('🔍 Backdrop clicado - fechando modal')
          onClose()
        }}
      />
      
      {/* Modal */}
      <div 
        className={`
          ${styles.modalContainer} 
          ${sizeClass} 
          ${maxHeightClass}
          ${className}
        `}
      >
        {/* Header */}
        {title && (
          <div className={styles.modalHeader}>
            <h2 className={styles.modalTitle}>{title}</h2>
            <button
              onClick={() => {
                console.log('🔍 Botão X clicado - fechando modal')
                onClose()
              }}
              className={styles.closeButton}
            >
              <svg className={styles.closeIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
        
        {/* Content */}
        <div className={`
          ${styles.modalContent} 
          ${size === 'full' ? styles.modalContentFixed : styles.modalContentScrollable}
        `}>
          {children}
        </div>
      </div>
    </div>
  )

  // Use portal to render modal at the end of the document body
  if (typeof window !== 'undefined' && document.body) {
    return createPortal(modalContent, document.body)
  }

  // Fallback for SSR
  return modalContent
}