// 🏷️ MIT Logistics Frontend - Badge Component

'use client'

import { forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import styles from '@/styles/modules/Badge.module.css'

const badgeVariants = cva(styles.badge, {
  variants: {
    variant: {
      default: styles.default,
      secondary: styles.secondary,
      success: styles.success,
      warning: styles.warning,
      error: styles.error,
      outline: styles.outline,
      info: styles.info // Added info variant
    },
    size: {
      sm: styles.sizeSmall,
      md: styles.sizeMedium,
      lg: styles.sizeLarge,
      small: styles.sizeSmall // Added small size, mapping to sm
    }
  },
  defaultVariants: {
    variant: 'default',
    size: 'md'
  }
})

interface BadgeProps 
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  icon?: React.ReactNode
  removable?: boolean
  onRemove?: () => void
}

export const Badge = forwardRef<HTMLDivElement, BadgeProps>(
  ({ 
    className, 
    variant, 
    size, 
    icon, 
    removable = false, 
    onRemove, 
    children, 
    ...props 
  }, ref) => {
    return (
      <div
        className={`${badgeVariants({ variant, size })} ${className || ''}`}
        ref={ref}
        {...props}
      >
        {icon && (
          <span className={styles.icon}>{icon}</span>
        )}
        
        <span className={styles.content}>{children}</span>
        
        {removable && onRemove && (
          <button
            type="button"
            onClick={onRemove}
            className={styles.removeButton}
            aria-label="Remove badge"
          >
            ✕
          </button>
        )}
      </div>
    )
  }
)

Badge.displayName = 'Badge'

// Status Badge for common use cases
interface StatusBadgeProps extends Omit<BadgeProps, 'variant'> {
  status: 'online' | 'offline' | 'pending' | 'success' | 'error' | 'warning'
}

export const StatusBadge = forwardRef<HTMLDivElement, StatusBadgeProps>(
  ({ status, children, ...props }, ref) => {
    const statusConfig = {
      online: { variant: 'success' as const, icon: '🟢', text: children || 'Online' },
      offline: { variant: 'error' as const, icon: '🔴', text: children || 'Offline' },
      pending: { variant: 'warning' as const, icon: '🟡', text: children || 'Pending' },
      success: { variant: 'success' as const, icon: '✅', text: children || 'Success' },
      error: { variant: 'error' as const, icon: '❌', text: children || 'Error' },
      warning: { variant: 'warning' as const, icon: '⚠️', text: children || 'Warning' }
    }

    const config = statusConfig[status]

    return (
      <Badge
        ref={ref}
        variant={config.variant}
        icon={config.icon}
        {...props}
      >
        {config.text}
      </Badge>
    )
  }
)

StatusBadge.displayName = 'StatusBadge'