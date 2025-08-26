import * as React from "react"

interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  children: React.ReactNode
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onOpenChange(false)
      }
    }

    if (open) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [open, onOpenChange])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={() => onOpenChange(false)}
      />
      {/* Dialog Content */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-hidden">
        {children}
      </div>
    </div>
  )
}

interface DialogContentProps {
  children: React.ReactNode
  className?: string
}

export function DialogContent({ children, className }: DialogContentProps) {
  return (
    <div className={`p-6 ${className || ''}`}>
      {children}
    </div>
  )
}

interface DialogHeaderProps {
  children: React.ReactNode
  className?: string // Added className
}

export function DialogHeader({ children, className }: DialogHeaderProps) {
  return (
    <div className={`mb-6 ${className || ''}`}> // Added className
      {children}
    </div>
  )
}

interface DialogTitleProps {
  children: React.ReactNode
  className?: string // Added className
}

export function DialogTitle({ children, className }: DialogTitleProps) {
  return (
    <h2 className={`text-lg font-semibold text-gray-900 mb-2 ${className || ''}`}> // Added className
      {children}
    </h2>
  )
}

interface DialogDescriptionProps {
  children: React.ReactNode
  className?: string // Added className
}

export function DialogDescription({ children, className }: DialogDescriptionProps) {
  return (
    <p className={`text-sm text-gray-600 ${className || ''}`}> // Added className
      {children}
    </p>
  )
}

interface DialogFooterProps {
  children: React.ReactNode
  className?: string // Added className
}

export function DialogFooter({ children, className }: DialogFooterProps) {
  return (
    <div className={`flex justify-end space-x-2 pt-4 border-t ${className || ''}`}> // Added className
      {children}
    </div>
  )
}