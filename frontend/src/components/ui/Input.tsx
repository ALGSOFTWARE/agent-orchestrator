// ⌨️ MIT Logistics Frontend - Input Component

'use client'

import { forwardRef } from 'react'
import styles from '@/styles/modules/Input.module.css'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  isLoading?: boolean
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className, 
    type = 'text', 
    label, 
    error, 
    leftIcon, 
    rightIcon, 
    isLoading = false,
    disabled,
    ...props 
  }, ref) => {
    const hasError = !!error
    const isDisabled = disabled || isLoading
    
    return (
      <div className={styles.container}>
        {label && (
          <label className={styles.label}>
            {label}
            {props.required && <span className={styles.required}>*</span>}
          </label>
        )}
        
        <div className={`${styles.inputWrapper} ${hasError ? styles.error : ''}`}>
          {leftIcon && (
            <div className={styles.leftIcon}>
              {leftIcon}
            </div>
          )}
          
          <input
            type={type}
            className={`
              ${styles.input} 
              ${leftIcon ? styles.hasLeftIcon : ''} 
              ${rightIcon || isLoading ? styles.hasRightIcon : ''}
              ${className || ''}
            `}
            ref={ref}
            disabled={isDisabled}
            {...props}
          />
          
          {(rightIcon || isLoading) && (
            <div className={styles.rightIcon}>
              {isLoading ? (
                <span className={styles.loadingIcon}>⏳</span>
              ) : (
                rightIcon
              )}
            </div>
          )}
        </div>
        
        {error && (
          <div className={styles.errorMessage}>
            <span className={styles.errorIcon}>⚠️</span>
            {error}
          </div>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  isLoading?: boolean
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ 
    className, 
    label, 
    error, 
    isLoading = false,
    disabled,
    ...props 
  }, ref) => {
    const hasError = !!error
    const isDisabled = disabled || isLoading
    
    return (
      <div className={styles.container}>
        {label && (
          <label className={styles.label}>
            {label}
            {props.required && <span className={styles.required}>*</span>}
          </label>
        )}
        
        <div className={`${styles.textareaWrapper} ${hasError ? styles.error : ''}`}>
          <textarea
            className={`${styles.textarea} ${className || ''}`}
            ref={ref}
            disabled={isDisabled}
            {...props}
          />
          
          {isLoading && (
            <div className={styles.textareaLoading}>
              <span className={styles.loadingIcon}>⏳</span>
            </div>
          )}
        </div>
        
        {error && (
          <div className={styles.errorMessage}>
            <span className={styles.errorIcon}>⚠️</span>
            {error}
          </div>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'