// ⏳ MIT Logistics Frontend - Loading Component

'use client'

import { forwardRef } from 'react'
import styles from '@/styles/modules/Loading.module.css'

interface LoadingProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'spinner' | 'dots' | 'pulse' | 'skeleton'
  text?: string
  fullPage?: boolean
}

export const Loading = forwardRef<HTMLDivElement, LoadingProps>(
  ({ 
    className, 
    size = 'md', 
    variant = 'spinner', 
    text, 
    fullPage = false,
    ...props 
  }, ref) => {
    const containerClass = fullPage ? styles.fullPage : styles.container

    return (
      <div
        ref={ref}
        className={`${containerClass} ${className || ''}`}
        {...props}
      >
        <div className={`${styles.loading} ${styles[variant]} ${styles[size]}`}>
          {variant === 'spinner' && (
            <div className={styles.spinner} />
          )}
          
          {variant === 'dots' && (
            <div className={styles.dots}>
              <div className={styles.dot} />
              <div className={styles.dot} />
              <div className={styles.dot} />
            </div>
          )}
          
          {variant === 'pulse' && (
            <div className={styles.pulse} />
          )}
          
          {variant === 'skeleton' && (
            <div className={styles.skeleton}>
              <div className={styles.skeletonLine} />
              <div className={styles.skeletonLine} />
              <div className={styles.skeletonLine} />
            </div>
          )}
        </div>
        
        {text && (
          <div className={styles.text}>{text}</div>
        )}
      </div>
    )
  }
)

Loading.displayName = 'Loading'

// Skeleton component for loading states
interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string | number
  height?: string | number
  variant?: 'text' | 'circular' | 'rectangular'
}

export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>(
  ({ 
    className, 
    width, 
    height, 
    variant = 'rectangular',
    style,
    ...props 
  }, ref) => {
    const skeletonStyle = {
      width,
      height,
      ...style
    }

    return (
      <div
        ref={ref}
        className={`${styles.skeletonBase} ${styles[`skeleton${variant.charAt(0).toUpperCase() + variant.slice(1)}`]} ${className || ''}`}
        style={skeletonStyle}
        {...props}
      />
    )
  }
)

Skeleton.displayName = 'Skeleton'