import * as React from "react"

interface DropdownMenuProps {
  children: React.ReactNode
}

export function DropdownMenu({ children }: DropdownMenuProps) {
  const [isOpen, setIsOpen] = React.useState(false)

  return (
    <div className="relative inline-block text-left">
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          if (child.type === DropdownMenuTrigger) {
            return React.cloneElement(child, { 
              onClick: () => setIsOpen(!isOpen) 
            } as any)
          }
          if (child.type === DropdownMenuContent) {
            return isOpen ? React.cloneElement(child, { 
              onClose: () => setIsOpen(false) 
            } as any) : null
          }
        }
        return child
      })}
    </div>
  )
}

interface DropdownMenuTriggerProps {
  children: React.ReactNode
  asChild?: boolean
  onClick?: () => void
}

export function DropdownMenuTrigger({ children, asChild, onClick }: DropdownMenuTriggerProps) {
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, { 
      onClick: onClick 
    } as any)
  }

  return (
    <button onClick={onClick}>
      {children}
    </button>
  )
}

interface DropdownMenuContentProps {
  children: React.ReactNode
  align?: 'start' | 'center' | 'end'
  onClose?: () => void
}

export function DropdownMenuContent({ children, align = 'start', onClose }: DropdownMenuContentProps) {
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (onClose) {
        onClose()
      }
    }

    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [onClose])

  const alignClass = {
    start: 'left-0',
    center: 'left-1/2 transform -translate-x-1/2',
    end: 'right-0'
  }[align]

  return (
    <div className={`absolute top-full mt-1 ${alignClass} w-48 bg-white border border-gray-200 rounded-md shadow-lg z-50`}>
      <div className="py-1">
        {children}
      </div>
    </div>
  )
}

interface DropdownMenuItemProps {
  children: React.ReactNode
  onClick?: () => void
}

export function DropdownMenuItem({ children, onClick }: DropdownMenuItemProps) {
  return (
    <button
      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
      onClick={onClick}
    >
      {children}
    </button>
  )
}