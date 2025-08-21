'use client'

import { useEffect, useState } from 'react'
import { gatekeeperClient } from '@/lib/api/client'

export default function DebugPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()} - ${message}`])
  }

  const testAPIs = async () => {
    setLoading(true)
    setLogs([])
    
    try {
      addLog('🔍 Iniciando testes das APIs...')
      addLog(`📍 Gatekeeper Base URL: ${gatekeeperClient.getBaseURL()}`)
      
      // Test Health
      addLog('🏥 Testando health...')
      const health = await gatekeeperClient.getRaw('/health')
      addLog(`✅ Health OK: ${health.status}`)
      
      // Test Orders
      addLog('📋 Testando orders...')
      const orders = await gatekeeperClient.getRaw('/orders/')
      addLog(`✅ Orders: ${orders?.length || 0} encontradas`)
      
      // Test Graph
      addLog('🔗 Testando graph...')
      const graph = await gatekeeperClient.getRaw('/visualizations/graph/order-documents')
      addLog(`✅ Graph: ${graph?.stats?.total_nodes || 0} nodes, ${graph?.stats?.total_edges || 0} edges`)
      
      // Test Semantic Map
      addLog('🗺️ Testando semantic map...')
      const semantic = await gatekeeperClient.getRaw('/visualizations/semantic-map/documents?limit=5')
      addLog(`✅ Semantic: ${semantic?.stats?.total_documents || 0} documentos, ${semantic?.stats?.categories_count || 0} categorias`)
      
      addLog('🎉 Todos os testes passaram!')
      
    } catch (error: any) {
      addLog(`❌ Erro: ${error?.message || error}`)
      console.error('Debug error:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    testAPIs()
  }, [])

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">🔧 Diagnóstico de APIs</h1>
      
      <div className="mb-4">
        <button 
          onClick={testAPIs}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Testando...' : 'Testar APIs Novamente'}
        </button>
      </div>

      <div className="bg-black text-green-400 p-4 rounded-lg h-96 overflow-y-auto font-mono text-sm">
        {logs.length === 0 && !loading && (
          <p className="text-gray-500">Clique em "Testar APIs" para iniciar os testes...</p>
        )}
        {logs.map((log, index) => (
          <div key={index} className="mb-1">
            {log}
          </div>
        ))}
        {loading && (
          <div className="animate-pulse">⏳ Executando testes...</div>
        )}
      </div>
    </div>
  )
}