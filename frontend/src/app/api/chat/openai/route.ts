// 🤖 MIT Logistics Frontend - OpenAI Chat API Route

import { NextRequest, NextResponse } from 'next/server'

const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { messages, model = 'gpt-4o-mini', temperature = 0.3, max_tokens = 1000 } = body

    // Validate required fields
    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'Messages array is required' },
        { status: 400 }
      )
    }

    // Get OpenAI API key from environment 
    // Use NEXT_PUBLIC version as fallback since system env vars might interfere
    const apiKey = process.env.OPENAI_API_KEY?.startsWith('sk-') 
      ? process.env.OPENAI_API_KEY 
      : process.env.NEXT_PUBLIC_OPENAI_API_KEY
    
    if (!apiKey) {
      return NextResponse.json(
        { error: 'OpenAI API key not configured' },
        { status: 500 }
      )
    }

    // Make request to OpenAI
    const response = await fetch(OPENAI_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        messages,
        temperature,
        max_tokens,
        stream: false
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('OpenAI API Error:', errorData)
      
      return NextResponse.json(
        { 
          error: `OpenAI API Error: ${response.status} ${response.statusText}`,
          details: errorData
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    // Extract the response content
    const content = data.choices?.[0]?.message?.content || 'Erro: Resposta vazia do OpenAI'

    return NextResponse.json({
      content,
      model,
      usage: data.usage,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('OpenAI Chat Error:', error)
    
    return NextResponse.json(
      { 
        error: 'Erro interno do servidor',
        details: error instanceof Error ? error.message : 'Erro desconhecido'
      },
      { status: 500 }
    )
  }
}