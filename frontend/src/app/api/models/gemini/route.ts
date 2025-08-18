// 💎 MIT Logistics Frontend - Gemini Models API Route

import { NextResponse } from 'next/server'

const GEMINI_MODELS_URL = 'https://generativelanguage.googleapis.com/v1beta/models'

// Cache for 5 minutes
let modelsCache: { data: any[], timestamp: number } | null = null
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

export async function GET() {
  try {
    // Check cache first
    if (modelsCache && Date.now() - modelsCache.timestamp < CACHE_DURATION) {
      return NextResponse.json({
        models: modelsCache.data,
        cached: true,
        timestamp: modelsCache.timestamp
      })
    }

    // Get Gemini API key
    const apiKey = process.env.GEMINI_API_KEY?.startsWith('AIza') 
      ? process.env.GEMINI_API_KEY 
      : process.env.NEXT_PUBLIC_GEMINI_API_KEY

    if (!apiKey) {
      return NextResponse.json(
        { error: 'Gemini API key not configured' },
        { status: 500 }
      )
    }

    // Fetch models from Gemini
    const response = await fetch(`${GEMINI_MODELS_URL}?key=${apiKey}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store'
    })

    if (!response.ok) {
      console.error('Gemini Models API Error:', response.status, response.statusText)
      return NextResponse.json(
        { error: `Failed to fetch Gemini models: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    // Filter for generative models only and format
    const generativeModels = data.models
      .filter((model: any) => {
        const name = model.name.toLowerCase()
        return (
          model.supportedGenerationMethods?.includes('generateContent') &&
          (name.includes('gemini') || name.includes('bison'))
        )
      })
      .map((model: any) => {
        // Extract model ID from name (e.g., "models/gemini-1.5-pro" -> "gemini-1.5-pro")
        const id = model.name.split('/').pop()
        return {
          id,
          name: model.displayName || id,
          description: model.description,
          inputTokenLimit: model.inputTokenLimit,
          outputTokenLimit: model.outputTokenLimit,
          supportedGenerationMethods: model.supportedGenerationMethods,
          temperature: model.temperature,
          topP: model.topP,
          topK: model.topK
        }
      })
      .sort((a: any, b: any) => {
        // Sort by version (higher versions first)
        const aVersion = parseFloat(a.id.match(/\d+\.\d+/)?.[0] || '0')
        const bVersion = parseFloat(b.id.match(/\d+\.\d+/)?.[0] || '0')
        return bVersion - aVersion
      })

    // Update cache
    modelsCache = {
      data: generativeModels,
      timestamp: Date.now()
    }

    return NextResponse.json({
      models: generativeModels,
      cached: false,
      timestamp: modelsCache.timestamp,
      total: generativeModels.length
    })

  } catch (error) {
    console.error('Gemini Models fetch error:', error)
    
    return NextResponse.json(
      { 
        error: 'Failed to fetch Gemini models',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}