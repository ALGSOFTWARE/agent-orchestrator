// 🤖 MIT Logistics Frontend - OpenAI Models API Route

import { NextResponse } from 'next/server'

const OPENAI_MODELS_URL = 'https://api.openai.com/v1/models'

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

    // Get OpenAI API key
    const apiKey = process.env.OPENAI_API_KEY?.startsWith('sk-') 
      ? process.env.OPENAI_API_KEY 
      : process.env.NEXT_PUBLIC_OPENAI_API_KEY

    if (!apiKey) {
      return NextResponse.json(
        { error: 'OpenAI API key not configured' },
        { status: 500 }
      )
    }

    // Fetch models from OpenAI
    const response = await fetch(OPENAI_MODELS_URL, {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      cache: 'no-store'
    })

    if (!response.ok) {
      console.error('OpenAI Models API Error:', response.status, response.statusText)
      return NextResponse.json(
        { error: `Failed to fetch OpenAI models: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    // Filter for chat models only and sort by creation date
    const chatModels = data.data
      .filter((model: any) => {
        const id = model.id.toLowerCase()
        return (
          (id.includes('gpt') || id.includes('chatgpt')) &&
          !id.includes('instruct') &&
          !id.includes('edit') &&
          !id.includes('search') &&
          !id.includes('similarity') &&
          !id.includes('davinci') &&
          !id.includes('curie') &&
          !id.includes('babbage') &&
          !id.includes('ada')
        )
      })
      .sort((a: any, b: any) => b.created - a.created)
      .map((model: any) => ({
        id: model.id,
        name: model.id,
        created: model.created,
        owned_by: model.owned_by
      }))

    // Update cache
    modelsCache = {
      data: chatModels,
      timestamp: Date.now()
    }

    return NextResponse.json({
      models: chatModels,
      cached: false,
      timestamp: modelsCache.timestamp,
      total: chatModels.length
    })

  } catch (error) {
    console.error('OpenAI Models fetch error:', error)
    
    return NextResponse.json(
      { 
        error: 'Failed to fetch OpenAI models',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}