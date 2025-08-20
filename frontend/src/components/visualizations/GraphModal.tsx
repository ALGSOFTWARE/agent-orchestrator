'use client'

import { useState } from 'react'
import { Modal } from '@/components/ui/Modal'
import NetworkGraph from './NetworkGraph'
import { Search, Loader2, X, FileText, Target } from 'lucide-react'
import { gatekeeperClient } from '@/lib/api/client'
import styles from '@/styles/modules/GraphModal.module.css'

interface GraphNode {
  id: string
  type: 'order' | 'document'
  label: string
  data: any
}

interface GraphEdge {
  source: string
  target: string
  type: string
}

interface SearchResult {
  id: string
  label: string
  type: 'document'
  data: {
    similarity: number
    extracted_text_preview?: string
    category?: string
    order_id?: string
  }
}

interface GraphModalProps {
  isOpen: boolean
  onClose: () => void
  nodes: GraphNode[]
  edges: GraphEdge[]
  title?: string
}

export function GraphModal({ isOpen, onClose, nodes, edges, title }: GraphModalProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [loadingSearch, setLoadingSearch] = useState(false)
  const [showSearch, setShowSearch] = useState(false)
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set())

  const handleSemanticSearch = async () => {
    if (!searchQuery.trim()) return
    
    setLoadingSearch(true)
    try {
      const params = new URLSearchParams({
        query: searchQuery,
        limit: '10',
        min_similarity: '0.6'
      })
      const response = await gatekeeperClient.getRaw(`/visualizations/semantic-search/similar?${params}`)
      setSearchResults(response.similar_documents || [])
      
      // Highlight matched document nodes in the graph
      const matchedIds = new Set<string>()
      response.similar_documents?.forEach((doc: SearchResult) => {
        // Match with existing nodes by document name/id
        nodes.forEach(node => {
          if (node.type === 'document' && (
            node.label.includes(doc.label) ||
            node.id.includes(doc.id.replace('doc_', '')) ||
            doc.label.includes(node.label)
          )) {
            matchedIds.add(node.id)
          }
        })
      })
      setHighlightedNodes(matchedIds)
      
    } catch (error) {
      console.error('Erro na busca semântica:', error)
    } finally {
      setLoadingSearch(false)
    }
  }

  const clearSearch = () => {
    setSearchQuery('')
    setSearchResults([])
    setHighlightedNodes(new Set())
  }
  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      size="full"
      title={title || `🔗 Grafo de Relacionamentos - ${nodes.length} nós, ${edges.length} conexões`}
    >
      <div className="w-full h-full p-4 relative">
        {/* Search Panel */}
        {showSearch && (
          <div className={styles.searchPanel}>
            <div className={styles.searchHeader}>
              <div className={styles.searchHeaderTitle}>
                <Search className="h-5 w-5" />
                <span>Busca Semântica nos Documentos</span>
              </div>
              <button 
                onClick={() => setShowSearch(false)}
                className={styles.searchCloseBtn}
                title="Fechar busca"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            
            <div className={styles.searchInputContainer}>
              <input
                type="text"
                placeholder="Ex: faturas, CT-e, mercadorias refrigeradas..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSemanticSearch()}
                className={styles.searchInput}
              />
              <button 
                onClick={handleSemanticSearch}
                disabled={loadingSearch || !searchQuery.trim()}
                className={styles.searchBtn}
              >
                {loadingSearch ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </button>
              {(searchQuery || searchResults.length > 0) && (
                <button 
                  onClick={clearSearch}
                  className={styles.clearBtn}
                  title="Limpar busca"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
            
            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className={styles.searchResults}>
                <div className={styles.searchResultsHeader}>
                  <span>📊 {searchResults.length} documentos encontrados</span>
                  <span className={styles.highlightInfo}>
                    {highlightedNodes.size > 0 
                      ? `🎯 ${highlightedNodes.size} nós destacados no grafo`
                      : '💡 Nenhum nó correspondente no grafo atual'
                    }
                  </span>
                </div>
                <div className={styles.searchResultsList}>
                  {searchResults.map((result) => (
                    <div key={result.id} className={styles.searchResultItem}>
                      <div className={styles.resultHeader}>
                        <FileText className="h-4 w-4 text-blue-500" />
                        <span className={styles.resultTitle}>{result.label}</span>
                        <div className={styles.similarityBadge}>
                          {Math.round(result.data.similarity * 100)}%
                        </div>
                      </div>
                      {result.data.extracted_text_preview && (
                        <p className={styles.resultPreview}>
                          {result.data.extracted_text_preview}...
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        
        <div className={`${styles.graphContainer} ${showSearch ? styles.graphWithSearch : ''}`}>
          <NetworkGraph 
            nodes={nodes.map(node => ({
              ...node,
              highlighted: highlightedNodes.has(node.id)
            }))} 
            edges={edges} 
            height={typeof window !== 'undefined' ? window.innerHeight - (showSearch ? 250 : 200) : 800}
          />
        </div>
        
        {/* Search Toggle Button */}
        <div className="absolute top-6 left-6 z-10">
          <button
            onClick={() => setShowSearch(!showSearch)}
            className={`${styles.toggleSearchBtn} ${showSearch ? styles.toggleSearchBtnActive : ''}`}
            title={showSearch ? 'Fechar busca semântica' : 'Abrir busca semântica'}
          >
            <Search className="w-5 h-5" />
            <span>{showSearch ? 'Fechar Busca' : 'Buscar Documentos'}</span>
            {highlightedNodes.size > 0 && (
              <div className={styles.searchBadge}>{highlightedNodes.size}</div>
            )}
          </button>
        </div>
        
        {/* Modal Help */}
        <div className={`${styles.helpPanel} ${showSearch ? styles.helpPanelWithSearch : ''}`}>
          <div className="flex items-center gap-2 mb-1">
            <span>🖱️</span>
            <span className="font-medium">Controles:</span>
          </div>
          <div className="space-y-1 text-xs">
            <div>• <strong>Arraste</strong> para mover</div>
            <div>• <strong>Zoom</strong> com roda do mouse</div>
            <div>• <strong>Clique nos nós</strong> para ações</div>
            {highlightedNodes.size > 0 && (
              <div className="text-yellow-300">🎯 <strong>{highlightedNodes.size} nós</strong> destacados pela busca</div>
            )}
          </div>
        </div>
        
        {/* Close button (alternative) */}
        <div className="absolute top-6 right-6 z-10">
          <button
            onClick={onClose}
            className="bg-white shadow-lg border border-gray-200 rounded-full p-2 hover:bg-gray-50 transition-colors"
            title="Fechar visualização (ESC)"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </Modal>
  )
}