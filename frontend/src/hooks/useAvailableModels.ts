// 🔄 MIT Logistics Frontend - Available Models Hook

'use client'

import { useState, useEffect, useCallback } from 'react'

interface Model {
  id: string
  name: string
  [key: string]: any
}

interface ModelsResponse {
  models: Model[]
  cached: boolean
  timestamp: number
  total: number
}

interface UseAvailableModelsReturn {
  openaiModels: Model[]
  geminiModels: Model[]
  isLoading: boolean
  error: string | null
  lastUpdated: Date | null
  refresh: () => void
}

export function useAvailableModels(): UseAvailableModelsReturn {
  const [openaiModels, setOpenaiModels] = useState<Model[]>([])
  const [geminiModels, setGeminiModels] = useState<Model[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchModels = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Fetch both OpenAI and Gemini models in parallel
      const [openaiResponse, geminiResponse] = await Promise.allSettled([
        fetch('/api/models/openai').then(res => res.json()),
        fetch('/api/models/gemini').then(res => res.json())
      ])

      // Handle OpenAI response
      if (openaiResponse.status === 'fulfilled' && !openaiResponse.value.error) {
        const openaiData: ModelsResponse = openaiResponse.value
        setOpenaiModels(openaiData.models)
      } else {
        console.warn('Failed to fetch OpenAI models:', 
          openaiResponse.status === 'rejected' 
            ? openaiResponse.reason 
            : openaiResponse.value.error
        )
        // Fallback to default models
        setOpenaiModels([
          { id: 'gpt-4o', name: 'GPT-4o' },
          { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
          { id: 'gpt-4-turbo', name: 'GPT-4 Turbo' },
          { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' }
        ])
      }

      // Handle Gemini response
      if (geminiResponse.status === 'fulfilled' && !geminiResponse.value.error) {
        const geminiData: ModelsResponse = geminiResponse.value
        setGeminiModels(geminiData.models)
      } else {
        console.warn('Failed to fetch Gemini models:', 
          geminiResponse.status === 'rejected' 
            ? geminiResponse.reason 
            : geminiResponse.value.error
        )
        // Fallback to default models
        setGeminiModels([
          { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro' },
          { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash' },
          { id: 'gemini-1.0-pro', name: 'Gemini 1.0 Pro' }
        ])
      }

      setLastUpdated(new Date())

    } catch (err) {
      console.error('Error fetching models:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch models')
      
      // Set fallback models on error
      setOpenaiModels([
        { id: 'gpt-4o', name: 'GPT-4o' },
        { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
        { id: 'gpt-4-turbo', name: 'GPT-4 Turbo' },
        { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' }
      ])
      setGeminiModels([
        { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro' },
        { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash' },
        { id: 'gemini-1.0-pro', name: 'Gemini 1.0 Pro' }
      ])
    } finally {
      setIsLoading(false)
    }
  }, [])

  const refresh = useCallback(() => {
    fetchModels()
  }, [fetchModels])

  // Fetch models on mount
  useEffect(() => {
    fetchModels()
  }, [fetchModels])

  return {
    openaiModels,
    geminiModels,
    isLoading,
    error,
    lastUpdated,
    refresh
  }
}