// 🛠️ MIT Logistics Frontend - Utility Functions

import { type ClassValue, clsx } from 'clsx'

// === CLASS NAME UTILITIES === //
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

// === DATE & TIME UTILITIES === //
export function formatDate(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

export function formatDateTime(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatTimeAgo(date: string | Date): string {
  const now = new Date()
  const then = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000)

  if (diffInSeconds < 60) {
    return 'agora mesmo'
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60)
  if (diffInMinutes < 60) {
    return `${diffInMinutes}m atrás`
  }

  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) {
    return `${diffInHours}h atrás`
  }

  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) {
    return `${diffInDays}d atrás`
  }

  return formatDate(date)
}

export function isToday(date: string | Date): boolean {
  const today = new Date()
  const checkDate = new Date(date)
  
  return today.toDateString() === checkDate.toDateString()
}

// === STRING UTILITIES === //
export function truncate(str: string, length: number, suffix: string = '...'): string {
  if (str.length <= length) return str
  return str.slice(0, length - suffix.length) + suffix
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

export function kebabToTitle(str: string): string {
  return str
    .split('-')
    .map(word => capitalize(word))
    .join(' ')
}

export function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

// === NUMBER UTILITIES === //
export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('pt-BR').format(num)
}

export function formatCurrency(value: number, currency: string = 'BRL'): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency,
  }).format(value)
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value / 100)
}

// === VALIDATION UTILITIES === //
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function isValidCNPJ(cnpj: string): boolean {
  // Remove formatting
  const cleanCNPJ = cnpj.replace(/[^\d]/g, '')
  
  if (cleanCNPJ.length !== 14) return false
  
  // Check if all digits are the same
  if (/^(\d)\1{13}$/.test(cleanCNPJ)) return false
  
  // CNPJ validation algorithm
  let sum = 0
  let weight = 5
  
  for (let i = 0; i < 12; i++) {
    sum += parseInt(cleanCNPJ.charAt(i)) * weight
    weight = weight === 2 ? 9 : weight - 1
  }
  
  const digit1 = sum % 11 < 2 ? 0 : 11 - (sum % 11)
  
  sum = 0
  weight = 6
  
  for (let i = 0; i < 13; i++) {
    sum += parseInt(cleanCNPJ.charAt(i)) * weight
    weight = weight === 2 ? 9 : weight - 1
  }
  
  const digit2 = sum % 11 < 2 ? 0 : 11 - (sum % 11)
  
  return parseInt(cleanCNPJ.charAt(12)) === digit1 && parseInt(cleanCNPJ.charAt(13)) === digit2
}

export function isValidCEP(cep: string): boolean {
  const cleanCEP = cep.replace(/[^\d]/g, '')
  return /^\d{8}$/.test(cleanCEP)
}

// === ARRAY UTILITIES === //
export function groupBy<T, K extends keyof T>(array: T[], key: K): Record<string, T[]> {
  return array.reduce((groups, item) => {
    const group = String(item[key])
    groups[group] = groups[group] || []
    groups[group].push(item)
    return groups
  }, {} as Record<string, T[]>)
}

export function sortBy<T>(array: T[], key: keyof T, direction: 'asc' | 'desc' = 'asc'): T[] {
  return [...array].sort((a, b) => {
    const aVal = a[key]
    const bVal = b[key]
    
    if (aVal < bVal) return direction === 'asc' ? -1 : 1
    if (aVal > bVal) return direction === 'asc' ? 1 : -1
    return 0
  })
}

export function uniqueBy<T, K extends keyof T>(array: T[], key: K): T[] {
  const seen = new Set()
  return array.filter(item => {
    const keyValue = item[key]
    if (seen.has(keyValue)) {
      return false
    }
    seen.add(keyValue)
    return true
  })
}

// === URL UTILITIES === //
export function buildSearchParams(params: Record<string, string | number | boolean | undefined>): string {
  const searchParams = new URLSearchParams()
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value))
    }
  })
  
  return searchParams.toString()
}

export function parseSearchParams(search: string): Record<string, string> {
  const params = new URLSearchParams(search)
  const result: Record<string, string> = {}
  
  params.forEach((value, key) => {
    result[key] = value
  })
  
  return result
}

// === LOCAL STORAGE UTILITIES === //
export function getFromStorage<T>(key: string, defaultValue: T): T {
  if (typeof window === 'undefined') return defaultValue
  
  try {
    const item = window.localStorage.getItem(key)
    return item ? JSON.parse(item) : defaultValue
  } catch (error) {
    console.warn(`Error reading localStorage key "${key}":`, error)
    return defaultValue
  }
}

export function setToStorage<T>(key: string, value: T): void {
  if (typeof window === 'undefined') return
  
  try {
    window.localStorage.setItem(key, JSON.stringify(value))
  } catch (error) {
    console.warn(`Error setting localStorage key "${key}":`, error)
  }
}

export function removeFromStorage(key: string): void {
  if (typeof window === 'undefined') return
  
  try {
    window.localStorage.removeItem(key)
  } catch (error) {
    console.warn(`Error removing localStorage key "${key}":`, error)
  }
}

// === ERROR HANDLING === //
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  if (typeof error === 'string') return error
  return 'Ocorreu um erro inesperado'
}

export function isApiError(error: unknown): error is { code: number; message: string } {
  return (
    typeof error === 'object' &&
    error !== null &&
    'code' in error &&
    'message' in error &&
    typeof (error as any).code === 'number' &&
    typeof (error as any).message === 'string'
  )
}

// === DEBOUNCE & THROTTLE === //
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let lastFunc: NodeJS.Timeout | null = null
  let lastRan: number | null = null
  
  return (...args: Parameters<T>) => {
    if (!lastRan) {
      func(...args)
      lastRan = Date.now()
    } else {
      if (lastFunc) clearTimeout(lastFunc)
      lastFunc = setTimeout(() => {
        if (Date.now() - (lastRan || 0) >= limit) {
          func(...args)
          lastRan = Date.now()
        }
      }, limit - (Date.now() - lastRan))
    }
  }
}

// === COPY TO CLIPBOARD === //
export async function copyToClipboard(text: string): Promise<boolean> {
  if (typeof window === 'undefined') return false
  
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (error) {
    // Fallback for older browsers
    try {
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      const successful = document.execCommand('copy')
      document.body.removeChild(textArea)
      return successful
    } catch (fallbackError) {
      console.warn('Failed to copy to clipboard:', fallbackError)
      return false
    }
  }
}

// === FILE UTILITIES === //
export function getFileExtension(filename: string): string {
  return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2)
}

export function isImageFile(file: File): boolean {
  return file.type.startsWith('image/')
}

export function isPDFFile(file: File): boolean {
  return file.type === 'application/pdf'
}

export function isValidFileSize(file: File, maxSizeInMB: number): boolean {
  const maxSizeInBytes = maxSizeInMB * 1024 * 1024
  return file.size <= maxSizeInBytes
}