// 🃏 MIT Logistics Frontend - Card Component

'use client'

import { forwardRef } from 'react'
import styles from '@/styles/modules/Card.module.css'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined'
  padding?: 'sm' | 'md' | 'lg' | 'xl'
  hoverable?: boolean
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', padding = 'lg', hoverable = false, ...props }, ref) => {
    const classes = [
      styles.card,
      styles[variant],
      styles[`padding${padding.charAt(0).toUpperCase() + padding.slice(1)}`],
      hoverable ? styles.hoverable : '',
      className || ''
    ].filter(Boolean).join(' ')

    return (
      <div 
        ref={ref} 
        className={classes}
        {...props} 
      />
    )
  }
)

Card.displayName = 'Card'

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, ...props }, ref) => (
    <div 
      ref={ref} 
      className={`${styles.header} ${className || ''}`}
      {...props} 
    />
  )
)

CardHeader.displayName = 'CardHeader'

interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  level?: 1 | 2 | 3 | 4 | 5 | 6
}

export const CardTitle = forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ className, level = 3, ...props }, ref) => {
    switch (level) {
      case 1:
        return <h1 ref={ref} className={`${styles.title} ${className || ''}`} {...props} />
      case 2:
        return <h2 ref={ref} className={`${styles.title} ${className || ''}`} {...props} />
      case 3:
        return <h3 ref={ref} className={`${styles.title} ${className || ''}`} {...props} />
      case 4:
        return <h4 ref={ref} className={`${styles.title} ${className || ''}`} {...props} />
      case 5:
        return <h5 ref={ref} className={`${styles.title} ${className || ''}`} {...props} />
      case 6:
        return <h6 ref={ref} className={`${styles.title} ${className || ''}`} {...props} />
      default:
        return <h3 ref={ref} className={`${styles.title} ${className || ''}`} {...props} />
    }
  }
)

CardTitle.displayName = 'CardTitle'

interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {}

export const CardDescription = forwardRef<HTMLParagraphElement, CardDescriptionProps>(
  ({ className, ...props }, ref) => (
    <p 
      ref={ref} 
      className={`${styles.description} ${className || ''}`}
      {...props} 
    />
  )
)

CardDescription.displayName = 'CardDescription'

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardContent = forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, ...props }, ref) => (
    <div 
      ref={ref} 
      className={`${styles.content} ${className || ''}`}
      {...props} 
    />
  )
)

CardContent.displayName = 'CardContent'

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardFooter = forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, ...props }, ref) => (
    <div 
      ref={ref} 
      className={`${styles.footer} ${className || ''}`}
      {...props} 
    />
  )
)

CardFooter.displayName = 'CardFooter'