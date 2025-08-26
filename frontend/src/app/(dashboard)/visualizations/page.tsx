'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button, Card, CardContent, CardHeader, CardTitle, Input, Badge, Tabs, TabsContent, TabsList, TabsTrigger, Separator } from '@/components/ui'
import { Search, Network, Map, Loader2, Eye, GitBranch, Maximize2 } from 'lucide-react'
import NetworkGraph from '@/components/visualizations/NetworkGraph'
import SemanticMap from '@/components/visualizations/SemanticMap'
import { GraphModal } from '@/components/visualizations/GraphModal'
import { gatekeeperClient } from '@/lib/api/client'
import { useToast } from "@/hooks/use-toast"
import styles from './visualizations.module.css'

interface GraphNode {
  id: string
  type: 'order' | 'document'
  label: string
  data: any
  highlighted?: boolean
}

interface GraphEdge {
  source: string
  target: string
  type: string
}

interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  stats: {
    total_nodes: number
    total_edges: number
    orders_count: number
    documents_count: number
  }
}

interface SemanticPoint {
  id: string
  x: number
  y: number
  z?: number
  label: string
  category: string
  order_id: string | null
  data: any
}

interface SemanticCluster {
  name: string
  color: string
  documents: string[]
}

interface SemanticMapData {
  points: SemanticPoint[]
  clusters: SemanticCluster[]
  stats: {
    total_documents: number
    dimensions: number
    method: string
    categories_count: number
  }
  method_info: {
    name: string
    description: string
  }
}

export default function VisualizationsPage() {
  const { toast } = useToast()
  // States para Graph
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [selectedOrderId, setSelectedOrderId] = useState<string>('')
  const [loadingGraph, setLoadingGraph] = useState(false)
  const [orders, setOrders] = useState<any[]>([])
  const [isGraphModalOpen, setIsGraphModalOpen] = useState(false)

  // States para Semantic Map  
  const [semanticData, setSemanticData] = useState<SemanticMapData | null>(null)
  const [loadingSemanticMap, setLoadingSemanticMap] = useState(false)
  const [semanticMethod, setSemanticMethod] = useState<'tsne' | 'pca'>('tsne')
  const [semanticDimensions, setSemanticDimensions] = useState<2 | 3>(2)
  const [semanticLimit, setSemanticLimit] = useState(200)

  // States para busca semântica visual
  const [searchQuery, setSearchQuery] = useState('')
  const [similarDocuments, setSimilarDocuments] = useState<any[]>([])
  const [loadingSimilar, setLoadingSimilar] = useState(false)

  // Carregar dados do grafo
  const loadGraphData = useCallback(async () => {
    setLoadingGraph(true)
    try {
      const params = selectedOrderId ? `?order_id=${selectedOrderId}` : ''
      const url = `/visualizations/graph/order-documents${params}`
      console.log('🔍 [GRAPH] Fazendo requisição para:', url)
      console.log('🔍 [GRAPH] Base URL do gatekeeper:', gatekeeperClient.getBaseURL())
      
      const response = await gatekeeperClient.getRaw(url)
      console.log('✅ [GRAPH] Resposta recebida:', response)
      console.log('📊 [GRAPH] Tipo da resposta:', typeof response)
      console.log('📊 [GRAPH] Nodes:', response?.nodes?.length || 0)
      console.log('📊 [GRAPH] Edges:', response?.edges?.length || 0)
      
      // Debug: log first document node data
      const docNodes = response?.nodes?.filter((n: any) => n.type === 'document') || []
      if (docNodes.length > 0) {
        console.log('📄 [GRAPH] First document node:', docNodes[0])
        console.log('📄 [GRAPH] First document data:', docNodes[0]?.data)
        console.log('📄 [GRAPH] Has file_id?', !!docNodes[0]?.data?.file_id)
      }
      
      setGraphData(response)
    } catch (error) {
      console.error('❌ [GRAPH] Erro ao carregar dados do grafo:', error)
      toast({
        title: "Erro no Grafo",
        description: `Não foi possível carregar os dados do grafo: ${error instanceof Error ? error.message : error}`,
        variant: "destructive",
      })
    } finally {
      setLoadingGraph(false)
    }
  }, [selectedOrderId, toast])

  // Carregar dados do mapa semântico
  const loadSemanticMapData = useCallback(async () => {
    setLoadingSemanticMap(true)
    try {
      const params = new URLSearchParams({
        limit: semanticLimit.toString(),
        method: semanticMethod,
        dimensions: semanticDimensions.toString()
      })
      const url = `/visualizations/semantic-map/documents?${params}`
      console.log('🗺️ [SEMANTIC] Fazendo requisição para:', url)
      console.log('🗺️ [SEMANTIC] Base URL do gatekeeper:', gatekeeperClient.getBaseURL())
      
      const response = await gatekeeperClient.getRaw(url)
      console.log('✅ [SEMANTIC] Resposta recebida:', response)
      console.log('📊 [SEMANTIC] Tipo da resposta:', typeof response)
      console.log('📊 [SEMANTIC] Points:', response?.points?.length || 0)
      console.log('📊 [SEMANTIC] Clusters:', response?.clusters?.length || 0)
      
      setSemanticData(response)
    } catch (error) {
      console.error('❌ [SEMANTIC] Erro ao carregar mapa semântico:', error)
      toast({
        title: "Erro no Mapa Semântico",
        description: `Não foi possível carregar os dados do mapa: ${error instanceof Error ? error.message : error}`,
        variant: "destructive",
      })
    } finally {
      setLoadingSemanticMap(false)
    }
  }, [semanticMethod, semanticDimensions, semanticLimit, toast])

  // Buscar documentos similares
  const searchSimilarDocuments = async () => {
    if (!searchQuery.trim()) return
    
    setLoadingSimilar(true)
    try {
      const params = new URLSearchParams({
        query: searchQuery,
        limit: '20',
        min_similarity: '0.5'
      })
      const response = await gatekeeperClient.getRaw(`/visualizations/semantic-search/similar?${params}`)
      setSimilarDocuments(response.similar_documents || [])
      if ((response.similar_documents || []).length === 0) {
        toast({
          title: "Busca Concluída",
          description: "Nenhum documento similar encontrado.",
        })
      }
    } catch (error) {
      console.error('Erro na busca semântica:', error)
      toast({
        title: "Erro na Busca",
        description: "Ocorreu um erro ao realizar a busca semântica.",
        variant: "destructive",
      })
    } finally {
      setLoadingSimilar(false)
    }
  }

  const loadOrders = useCallback(async () => {
    try {
      const url = `/orders/`
      console.log('📋 [ORDERS] Fazendo requisição para:', url)
      console.log('📋 [ORDERS] Base URL do gatekeeper:', gatekeeperClient.getBaseURL())
      
      const response = await gatekeeperClient.getRaw(url);
      console.log('✅ [ORDERS] Resposta recebida:', response)
      console.log('📊 [ORDERS] Quantidade de orders:', response?.length || 0)
      
      setOrders(response);
    } catch (error) {
      console.error('❌ [ORDERS] Erro ao carregar orders:', error);
      toast({
        title: "Erro de Conexão",
        description: `Não foi possível carregar a lista de pedidos: ${error instanceof Error ? error.message : error}`,
        variant: "destructive",
      })
    }
  }, [toast]);

  // Carregar dados iniciais
  useEffect(() => {
    loadGraphData()
    loadSemanticMapData()
    loadOrders()
  }, [loadGraphData, loadSemanticMapData, loadOrders])

  return (
    <div className={styles.visualizationsContainer}>
      {/* Header */}
      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>
          <Network className="h-8 w-8" />
          Visualizações Inteligentes
        </h1>
        <p className={styles.pageDescription}>
          Mapeamento visual de relacionamentos entre orders e documentos + busca semântica em tempo real
        </p>
      </div>

      <Tabs defaultValue="graph" className={styles.tabsContainer}>
        <TabsList className={styles.tabsList}>
          <TabsTrigger value="graph" className={styles.tabsTrigger}>
            <GitBranch className="h-4 w-4" />
            Grafo de Relacionamentos
          </TabsTrigger>
          <TabsTrigger value="semantic" className={styles.tabsTrigger}>
            <Map className="h-4 w-4" />
            Mapa Semântico
          </TabsTrigger>
          <TabsTrigger value="search" className={styles.tabsTrigger}>
            <Search className="h-4 w-4" />
            Busca Visual
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Grafo de Relacionamentos */}
        <TabsContent value="graph" className={styles.tabContent}>
          <Card className={styles.visualizationCard}>
            <CardHeader className={styles.cardHeader}>
              <CardTitle className={styles.cardTitle}>
                <span>Grafo Order → Documents</span>
                <div className={styles.cardControls}>
                  <select 
                    className="w-48 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={selectedOrderId} 
                    onChange={(e) => setSelectedOrderId(e.target.value)}
                  >
                    <option value="">Todas as Orders</option>
                    {orders.map((order) => (
                      <option key={order.order_id} value={order.order_id}>
                        {order.title} - {order.customer_name}
                      </option>
                    ))}
                  </select>
                  <Button onClick={loadGraphData} disabled={loadingGraph} className="flex items-center gap-2">
                    {loadingGraph ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                    Atualizar
                  </Button>
                  <Button 
                    onClick={() => {
                      console.log('🔍 Botão Expandir clicado!')
                      console.log('📊 GraphData existe:', !!graphData)
                      console.log('📊 GraphData content:', graphData)
                      console.log('📊 Nodes:', graphData?.nodes?.length || 0)
                      console.log('📊 Edges:', graphData?.edges?.length || 0)
                      console.log('📊 Loading:', loadingGraph)
                      setIsGraphModalOpen(true)
                    }} 
                    disabled={!graphData || loadingGraph}
                    variant="outline" 
                    className="flex items-center gap-2"
                  >
                    <Maximize2 className="h-4 w-4" />
                    Expandir
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className={styles.cardContent}>
              {loadingGraph ? (
                <div className={styles.loadingState}>
                  <Loader2 className="h-8 w-8 animate-spin" />
                  <span>Carregando grafo...</span>
                </div>
              ) : graphData ? (
                <div>
                  {/* Stats do grafo */}
                  <div className={styles.statsContainer}>
                    <div className={styles.statsBadge}>
                      {graphData?.stats?.orders_count ?? 0} Orders
                    </div>
                    <div className={styles.statsBadge}>
                      {graphData?.stats?.documents_count ?? 0} Documentos
                    </div>
                    <div className={styles.statsBadge}>
                      {graphData?.stats?.total_edges ?? 0} Relacionamentos
                    </div>
                  </div>
                  
                  {/* Grafo Network */}
                  <div className={styles.visualizationWrapper}>
                    <div className={styles.graphContainer}>
                      <NetworkGraph
                        nodes={graphData?.nodes ?? []}
                        edges={graphData?.edges ?? []}
                        height={600}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className={styles.emptyState}>
                  Nenhum dado de grafo carregado
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Mapa Semântico */}
        <TabsContent value="semantic" className={styles.tabContent}>
          <Card className={styles.visualizationCard}>
            <CardHeader className={styles.cardHeader}>
              <CardTitle className={styles.cardTitle}>
                <span>Mapa Semântico dos Documentos</span>
                <div className={styles.cardControls}>
                  <select 
                    className="w-32 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={semanticMethod} 
                    onChange={(e) => setSemanticMethod(e.target.value as 'tsne' | 'pca')}
                  >
                    <option value="tsne">t-SNE</option>
                    <option value="pca">PCA</option>
                  </select>
                  
                  <select 
                    className="w-20 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={semanticDimensions.toString()} 
                    onChange={(e) => setSemanticDimensions(parseInt(e.target.value) as 2 | 3)}
                  >
                    <option value="2">2D</option>
                    <option value="3">3D</option>
                  </select>

                  <Button onClick={loadSemanticMapData} disabled={loadingSemanticMap} className="flex items-center gap-2">
                    {loadingSemanticMap ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                    Regenerar
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className={styles.cardContent}>
              {loadingSemanticMap ? (
                <div className={styles.loadingState}>
                  <Loader2 className="h-8 w-8 animate-spin" />
                  <span>Processando embeddings...</span>
                </div>
              ) : semanticData ? (
                <div>
                  {/* Stats e Info do método */}
                  <div className={styles.methodInfo}>
                    <div className={styles.statsContainer}>
                      <div className={styles.statsBadge}>
                        {semanticData?.stats?.total_documents ?? 0} documentos
                      </div>
                      <div className={styles.statsBadge}>
                        {semanticData?.stats?.categories_count ?? 0} categorias
                      </div>
                      <div className={styles.statsBadge}>
                        {semanticData?.method_info?.name ?? 'N/A'}
                      </div>
                    </div>
                    <p className={styles.methodDescription}>
                      {semanticData?.method_info?.description ?? 'Carregando informações do método...'}
                    </p>
                  </div>

                  {/* Clusters legendas */}
                  <div className={styles.clustersLegend}>
                    {semanticData?.clusters?.map((cluster) => (
                      <div
                        key={cluster.name}
                        className={styles.clusterBadge}
                        style={{ backgroundColor: cluster.color }}
                      >
                        {cluster.name} ({cluster.documents.length})
                      </div>
                    ))}
                  </div>
                  
                  {/* Mapa Semântico */}
                  <div className={styles.visualizationWrapper}>
                    <div className={styles.mapContainer}>
                      <SemanticMap
                        points={semanticData?.points ?? []}
                        clusters={semanticData?.clusters ?? []}
                        dimensions={semanticData?.stats?.dimensions ?? 2}
                        height={600}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className={styles.emptyState}>
                  Nenhum dado semântico carregado
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Busca Visual */}
        <TabsContent value="search" className={styles.tabContent}>
          <Card className={styles.visualizationCard}>
            <CardHeader className={styles.cardHeader}>
              <CardTitle className={styles.cardTitle}>
                <span>Busca Semântica Visual</span>
              </CardTitle>
            </CardHeader>
            <CardContent className={styles.cardContent}>
              <div className={styles.searchControls}>
                <input
                  className={styles.searchInput}
                  placeholder="Digite sua busca (ex: faturas, CT-e, mercadorias refrigeradas...)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchSimilarDocuments()}
                />
                <button 
                  className={styles.searchButton}
                  onClick={searchSimilarDocuments} 
                  disabled={loadingSimilar || !searchQuery.trim()}
                >
                  {loadingSimilar ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                  Buscar
                </button>
              </div>

              {/* Resultados */}
              {similarDocuments.length > 0 && (
                <div className={styles.resultsContainer}>
                  <h3 className={styles.resultsTitle}>Documentos similares encontrados:</h3>
                  <div className={styles.resultsGrid}>
                    {similarDocuments.map((doc) => (
                      <div key={doc.id} className={styles.resultItem}>
                        <div className={styles.resultHeader}>
                          <span className={styles.resultTitle}>{doc.label}</span>
                          <div className={styles.similarityBadge}>
                            {Math.round(doc.data.similarity * 100)}% similar
                          </div>
                        </div>
                        {doc.data.extracted_text_preview && (
                          <p className={styles.resultPreview}>
                            {doc.data.extracted_text_preview}...
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      
      {/* Graph Modal */}
      {graphData && (
        <GraphModal
          isOpen={isGraphModalOpen}
          onClose={() => {
            console.log('🔍 Fechando modal do grafo')
            setIsGraphModalOpen(false)
          }}
          nodes={graphData.nodes}
          edges={graphData.edges}
          title={selectedOrderId 
            ? `Grafo de Relacionamentos - Order: ${orders.find(o => o.order_id === selectedOrderId)?.title || 'Selecionada'}` 
            : 'Grafo de Relacionamentos - Todas as Orders'
          }
        />
      )}
      
      {/* Debug Info */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{ position: 'fixed', bottom: '10px', right: '10px', background: 'black', color: 'white', padding: '5px', fontSize: '10px', zIndex: 10000 }}>
          Modal Open: {isGraphModalOpen ? 'SIM' : 'NÃO'} | 
          GraphData: {graphData ? 'SIM' : 'NÃO'} | 
          Nodes: {graphData?.nodes?.length || 0}
        </div>
      )}
    </div>
  )
}