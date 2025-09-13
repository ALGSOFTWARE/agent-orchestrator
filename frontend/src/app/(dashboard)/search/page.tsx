'use client'

import { useState, useEffect } from 'react'
import { Search, FileText, Package, Clock, TrendingUp, Settings } from 'lucide-react'

interface SearchResult {
  document: {
    file_id: string
    original_name: string
    category: string
    file_type: string
    size_bytes: number
    uploaded_at: string
    order_id: string
    tags: string[]
    text_preview?: string
  }
  order: {
    order_id: string
    title: string
    customer_name: string
  }
  similarity_score: number
  relevance: 'alta' | 'média' | 'baixa'
  search_method: string
}

interface SearchStats {
  vector_search: {
    documents_total: number
    documents_with_embeddings: number
    embedding_coverage: string
    vector_search_available: boolean
  }
  embedding_service: {
    current_provider: string
    available: boolean
  }
}

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [stats, setStats] = useState<SearchStats | null>(null)
  const [selectedOrder, setSelectedOrder] = useState('')
  const [minSimilarity, setMinSimilarity] = useState(0.7)

  // Carregar estatísticas na inicialização
  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const response = await fetch('/api/files/search/vector/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!query.trim()) {
      setError('Digite uma consulta')
      return
    }

    setLoading(true)
    setError('')
    setResults([])

    try {
      const params = new URLSearchParams({
        query: query.trim(),
        limit: '10',
        min_similarity: minSimilarity.toString(),
        ...(selectedOrder && { order_id: selectedOrder })
      })

      const response = await fetch(`/api/files/search/semantic?${params}`)
      
      if (!response.ok) {
        throw new Error('Erro na busca semântica')
      }

      const data = await response.json()
      setResults(data.results || [])
      
    } catch (error) {
      setError('Erro ao realizar busca. Verifique se os serviços estão funcionando.')
      console.error('Erro na busca:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getRelevanceColor = (relevance: string) => {
    switch (relevance) {
      case 'alta': return 'text-green-600 bg-green-50'
      case 'média': return 'text-yellow-600 bg-yellow-50'
      case 'baixa': return 'text-gray-600 bg-gray-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🔍 Busca Semântica de Documentos
        </h1>
        <p className="text-gray-600">
          Encontre documentos usando linguagem natural - powered by AI
        </p>
      </div>

      {/* Stats Card */}
      {stats && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {stats.vector_search.documents_total}
              </div>
              <div className="text-sm text-gray-600">Documentos Total</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {stats.vector_search.embedding_coverage}
              </div>
              <div className="text-sm text-gray-600">Cobertura de Embeddings</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {stats.embedding_service.current_provider}
              </div>
              <div className="text-sm text-gray-600">Provider de Embeddings</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${stats.vector_search.vector_search_available ? 'text-green-600' : 'text-yellow-600'}`}>
                {stats.vector_search.vector_search_available ? '✅' : '🔄'}
              </div>
              <div className="text-sm text-gray-600">
                {stats.vector_search.vector_search_available ? 'Vector Search' : 'Fallback Mode'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ex: 'container com eletrônicos para Santos', 'CT-e da transportadora ABC', 'documentos com avarias'"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Buscando...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Buscar
                </>
              )}
            </button>
          </div>

          {/* Advanced Options */}
          <div className="flex gap-4 items-center text-sm">
            <div className="flex items-center gap-2">
              <label className="text-gray-600">Similaridade mínima:</label>
              <select
                value={minSimilarity}
                onChange={(e) => setMinSimilarity(parseFloat(e.target.value))}
                className="border border-gray-300 rounded px-2 py-1"
              >
                <option value={0.5}>50% (mais resultados)</option>
                <option value={0.7}>70% (balanceado)</option>
                <option value={0.8}>80% (mais precisão)</option>
              </select>
            </div>
            
            <div className="flex items-center gap-2">
              <label className="text-gray-600">Filtrar por Order:</label>
              <input
                type="text"
                value={selectedOrder}
                onChange={(e) => setSelectedOrder(e.target.value)}
                placeholder="ID da Order (opcional)"
                className="border border-gray-300 rounded px-2 py-1 w-40"
              />
            </div>
          </div>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="text-red-800">{error}</div>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Resultados ({results.length})
            </h2>
          </div>

          {results.map((result, index) => (
            <div key={result.document.file_id} className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-3">
                  <FileText className="w-6 h-6 text-blue-600 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {result.document.original_name}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Package className="w-4 h-4" />
                        {result.order.title}
                      </span>
                      <span>{result.order.customer_name}</span>
                      <span>{formatFileSize(result.document.size_bytes)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRelevanceColor(result.relevance)}`}>
                    {Math.round(result.similarity_score * 100)}% similaridade
                  </span>
                  <span className="text-xs text-gray-500">
                    {result.search_method}
                  </span>
                </div>
              </div>

              {/* Text Preview */}
              {result.document.text_preview && (
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <div className="text-sm text-gray-700 leading-relaxed">
                    {result.document.text_preview}
                  </div>
                </div>
              )}

              {/* Tags */}
              {result.document.tags && result.document.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {result.document.tags.slice(0, 5).map((tag, tagIndex) => (
                    <span
                      key={tagIndex}
                      className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                <button className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded border border-blue-200">
                  Ver Documento
                </button>
                <button className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-50 rounded border border-gray-200">
                  Ver Order
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No Results */}
      {!loading && query && results.length === 0 && (
        <div className="text-center py-12">
          <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Nenhum resultado encontrado
          </h3>
          <p className="text-gray-600 mb-4">
            Tente ajustar sua consulta ou diminuir a similaridade mínima
          </p>
        </div>
      )}

      {/* Instructions */}
      {!query && (
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-3">
            💡 Como usar a Busca Semântica
          </h3>
          <div className="space-y-2 text-blue-800">
            <p>• <strong>Linguagem natural:</strong> "containers com eletrônicos para Santos"</p>
            <p>• <strong>Conceitos:</strong> "documentos com avarias", "exportação urgente"</p>
            <p>• <strong>Entidades:</strong> "CT-e 351234567890", "transportadora ABC"</p>
            <p>• <strong>Contexto:</strong> "embarques atrasados", "mercadoria refrigerada"</p>
          </div>
        </div>
      )}
    </div>
  )
}