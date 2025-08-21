// 💎 MIT Logistics Frontend - Gemini Chat API Route

import { NextRequest, NextResponse } from 'next/server'

const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { messages, model = 'gemini-1.5-flash', temperature = 0.3, max_tokens = 1000 } = body

    // Validate required fields
    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'Messages array is required' },
        { status: 400 }
      )
    }

    // Get Gemini API key from environment
    // Use NEXT_PUBLIC version as fallback since system env vars might interfere
    const apiKey = process.env.GEMINI_API_KEY?.startsWith('AIza') 
      ? process.env.GEMINI_API_KEY 
      : process.env.NEXT_PUBLIC_GEMINI_API_KEY
      
    if (!apiKey) {
      return NextResponse.json(
        { error: 'Gemini API key not configured' },
        { status: 500 }
      )
    }

    // Convert messages to Gemini format
    const geminiMessages = convertMessagesToGeminiFormat(messages)

    // Make request to Gemini
    const response = await fetch(`${GEMINI_API_URL}/${model}:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: geminiMessages,
        generationConfig: {
          temperature,
          maxOutputTokens: max_tokens,
          topP: 0.8,
          topK: 10
        }
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('Gemini API Error:', errorData)
      
      return NextResponse.json(
        { 
          error: `Gemini API Error: ${response.status} ${response.statusText}`,
          details: errorData
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    // Extract the response content
    const content = data.candidates?.[0]?.content?.parts?.[0]?.text || 'Erro: Resposta vazia do Gemini'

    return NextResponse.json({
      content,
      model,
      usage: data.usageMetadata,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Gemini Chat Error:', error)
    
    return NextResponse.json(
      { 
        error: 'Erro interno do servidor',
        details: error instanceof Error ? error.message : 'Erro desconhecido'
      },
      { status: 500 }
    )
  }
}

function convertMessagesToGeminiFormat(messages: any[]) {
  const geminiMessages: any[] = []
  
  for (const message of messages) {
    if (message.role === 'system') {
      // Gemini doesn't have a system role, so we'll prepend it to the first user message
      continue
    }
    
    const role = message.role === 'user' ? 'user' : 'model'
    
    geminiMessages.push({
      role,
      parts: [{ text: message.content }]
    })
  }
  
  // If there was a system message, prepend it to the first user message
  const systemMessage = messages.find(m => m.role === 'system')
  if (systemMessage && geminiMessages.length > 0 && geminiMessages[0].role === 'user') {
    geminiMessages[0].parts[0].text = `${systemMessage.content}\n\nUser: ${geminiMessages[0].parts[0].text}`
  }
  
  return geminiMessages
}