// 📋 Orders Management Page - Super-container Interface
'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Plus, Search, FileText, Package, Calendar, User, Eye, ArrowRight, MapPin, Truck, ExternalLink } from 'lucide-react'
import { CreateOrderDialog } from '@/components/orders/CreateOrderDialog'
import { OrderCard } from '@/components/orders/OrderCard'
import { OrderStats } from '@/components/orders/OrderStats'

interface Order {
  _id: string
  order_id: string
  title: string
  description?: string
  order_type: string
  status: string
  customer_name: string
  origin?: string
  destination?: string
  created_at: string
  last_activity: string
  document_count: number
  estimated_value?: number
  currency?: string
  priority: number
  tags: string[]
}

interface OrdersStats {
  total_orders: number
  by_status: Record<string, number>
  by_type: Record<string, number>
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [stats, setStats] = useState<OrdersStats | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedStatus, setSelectedStatus] = useState<string>('')
  const [selectedType, setSelectedType] = useState<string>('')
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [isOrderModalOpen, setIsOrderModalOpen] = useState(false)

  // Fetch orders from API
  const fetchOrders = async () => {
    try {
      setIsLoading(true)
      const params = new URLSearchParams()
      if (selectedStatus) params.append('status', selectedStatus)
      if (selectedType) params.append('order_type', selectedType)
      if (searchTerm) params.append('search', searchTerm)
      
      const url = `http://localhost:8001/orders/?${params}`
      
      const response = await fetch(url)
      const data = await response.json()
      setOrders(data)
    } catch (error) {
      console.error('Erro ao buscar orders:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Fetch statistics
  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8001/orders/stats/overview')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error)
    }
  }

  // Single effect that handles all changes with appropriate debouncing
  useEffect(() => {
    // Debounce only search term changes
    if (searchTerm !== undefined) {
      const timeoutId = setTimeout(() => {
        fetchOrders()
      }, searchTerm ? 300 : 0)
      
      return () => clearTimeout(timeoutId)
    } else {
      // Immediate for status/type changes or initial load
      fetchOrders()
    }
  }, [searchTerm, selectedStatus, selectedType])

  // Load stats on initial mount and filter changes
  useEffect(() => {
    fetchStats()
  }, [selectedStatus, selectedType])

  // Cleanup: restore body scroll on component unmount
  useEffect(() => {
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  // Orders are now filtered on the server-side via API
  const filteredOrders = orders

  const handleOrderCreated = (newOrder: Order) => {
    setOrders(prev => [newOrder, ...prev])
    fetchStats() // Refresh stats
    setIsCreateDialogOpen(false)
  }

  const openOrderModal = (order: Order) => {
    setSelectedOrder(order)
    setIsOrderModalOpen(true)
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden'
  }

  const closeOrderModal = () => {
    setSelectedOrder(null)
    setIsOrderModalOpen(false)
    // Restore body scroll
    document.body.style.overflow = 'unset'
  }

  // Handle escape key press to close modal
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOrderModalOpen) {
        closeOrderModal()
      }
    }

    if (isOrderModalOpen) {
      document.addEventListener('keydown', handleEscapeKey)
      return () => {
        document.removeEventListener('keydown', handleEscapeKey)
      }
    }
  }, [isOrderModalOpen])

  const statusOptions = [
    { value: '', label: 'Todos os Status' },
    { value: 'created', label: 'Criado' },
    { value: 'in_progress', label: 'Em Andamento' },
    { value: 'shipped', label: 'Embarcado' },
    { value: 'in_transit', label: 'Em Trânsito' },
    { value: 'delivered', label: 'Entregue' },
    { value: 'completed', label: 'Concluído' },
    { value: 'cancelled', label: 'Cancelado' }
  ]

  const typeOptions = [
    { value: '', label: 'Todos os Tipos' },
    { value: 'import', label: 'Importação' },
    { value: 'export', label: 'Exportação' },
    { value: 'domestic_freight', label: 'Frete Nacional' },
    { value: 'international_freight', label: 'Frete Internacional' },
    { value: 'warehousing', label: 'Armazenagem' },
    { value: 'customs_clearance', label: 'Desembaraço' }
  ]

  return (
    <div className="min-h-screen bg-gray-50 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Page Header */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  📋 Gerenciamento de Orders
                </h1>
                <p className="text-gray-600 max-w-2xl">
                  Super-contêineres que agrupam todos os documentos de uma operação logística. 
                  Organize, rastreie e gerencie todas as suas operações em um só lugar.
                </p>
              </div>
              <Button 
                onClick={() => setIsCreateDialogOpen(true)} 
                size="lg"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 h-auto whitespace-nowrap"
              >
                <Plus className="mr-2 h-5 w-5" />
                Nova Order
              </Button>
            </div>
          </div>

      {/* Statistics Overview */}
      {stats && <OrderStats stats={stats} />}

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Filtros e Busca
          </CardTitle>
          <CardDescription>
            Encontre rapidamente as orders que você precisa
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="md:col-span-1">
              <label className="block text-sm font-medium mb-2">Buscar Orders</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Título, cliente ou tags..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 h-11 border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full h-11 px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 focus:outline-none"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Type Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Tipo de Operação</label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full h-11 px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 focus:outline-none"
              >
                {typeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Filter Summary */}
          {(searchTerm || selectedStatus || selectedType) && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-blue-900">Filtros ativos:</span>
                  <div className="flex gap-2">
                    {searchTerm && (
                      <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                        Busca: "{searchTerm}"
                      </Badge>
                    )}
                    {selectedStatus && (
                      <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                        Status: {statusOptions.find(s => s.value === selectedStatus)?.label}
                      </Badge>
                    )}
                    {selectedType && (
                      <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                        Tipo: {typeOptions.find(t => t.value === selectedType)?.label}
                      </Badge>
                    )}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSearchTerm('')
                    setSelectedStatus('')
                    setSelectedType('')
                  }}
                  className="text-blue-600 hover:text-blue-800"
                >
                  Limpar filtros
                </Button>
              </div>
            </div>
          )}

          {/* Results Section */}
          <div className="border-t border-gray-100 mt-6 pt-6">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600 mb-3"></div>
                <span className="text-gray-600 font-medium">Buscando orders...</span>
              </div>
            ) : filteredOrders.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="bg-gray-100 rounded-full p-4 mb-4">
                  <Package className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {searchTerm || selectedStatus || selectedType 
                    ? 'Nenhuma order encontrada' 
                    : 'Nenhuma order disponível'
                  }
                </h3>
                <p className="text-gray-500 text-center max-w-md mb-4">
                  {searchTerm || selectedStatus || selectedType 
                    ? 'Tente ajustar os filtros de busca ou criar uma nova order'
                    : 'Crie sua primeira order para começar a organizar documentos'
                  }
                </p>
                <Button 
                  onClick={() => setIsCreateDialogOpen(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  {searchTerm || selectedStatus || selectedType ? 'Nova Order' : 'Criar Primeira Order'}
                </Button>
              </div>
            ) : (
              <>
                {/* Results Header */}
                <div className="flex items-center justify-between py-4 px-1 mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {searchTerm || selectedStatus || selectedType 
                        ? 'Resultados da Busca' 
                        : 'Todas as Orders'
                      }
                    </h3>
                    <p className="text-sm text-gray-600">
                      {filteredOrders.length} order{filteredOrders.length !== 1 ? 's' : ''} 
                      {searchTerm || selectedStatus || selectedType ? ' encontrada' : ' disponível'}{filteredOrders.length !== 1 ? 's' : ''}
                      {(searchTerm || selectedStatus || selectedType) && (
                        <span className="ml-1 text-blue-600 font-medium">
                          • filtros aplicados
                        </span>
                      )}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span>Ordenar por:</span>
                    <select className="border border-gray-300 rounded px-2 py-1 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500">
                      <option>Atividade recente</option>
                      <option>Data de criação</option>
                      <option>Nome do cliente</option>
                      <option>Prioridade</option>
                    </select>
                  </div>
                </div>

                {/* Orders Grid */}
                <div className="grid gap-3 pb-6">
                  {filteredOrders.map((order) => (
                    <div
                      key={order._id}
                      onClick={() => openOrderModal(order)}
                      className="group relative bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-400 hover:shadow-lg hover:shadow-blue-100 hover:-translate-y-1 transition-all duration-300 cursor-pointer transform"
                      title="Clique para ver detalhes completos"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          {/* Title and Status */}
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="font-semibold text-gray-900 truncate flex-1">
                              {order.title}
                            </h3>
                            <Badge 
                              variant="secondary" 
                              className={`
                                ${order.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
                                ${order.status === 'in_progress' ? 'bg-blue-100 text-blue-800' : ''}
                                ${order.status === 'created' ? 'bg-yellow-100 text-yellow-800' : ''}
                                ${order.status === 'cancelled' ? 'bg-red-100 text-red-800' : ''}
                                ${order.status === 'delivered' ? 'bg-emerald-100 text-emerald-800' : ''}
                                ${order.status === 'shipped' ? 'bg-indigo-100 text-indigo-800' : ''}
                                ${order.status === 'in_transit' ? 'bg-purple-100 text-purple-800' : ''}
                              `}
                            >
                              {order.status === 'completed' && '✅ Concluído'}
                              {order.status === 'in_progress' && '🔄 Em Andamento'}
                              {order.status === 'created' && '📝 Criado'}
                              {order.status === 'cancelled' && '❌ Cancelado'}
                              {order.status === 'delivered' && '🚚 Entregue'}
                              {order.status === 'shipped' && '📦 Embarcado'}
                              {order.status === 'in_transit' && '🚛 Em Trânsito'}
                            </Badge>
                          </div>

                          {/* Customer and Route */}
                          <div className="flex items-center justify-between text-sm text-gray-600">
                            <div className="flex items-center gap-4">
                              <span className="flex items-center gap-1">
                                <User className="h-4 w-4" />
                                {order.customer_name}
                              </span>
                              {(order.origin || order.destination) && (
                                <span className="flex items-center gap-1">
                                  <MapPin className="h-4 w-4" />
                                  {order.origin && order.destination 
                                    ? `${order.origin} → ${order.destination}`
                                    : order.origin || order.destination
                                  }
                                </span>
                              )}
                            </div>
                            
                            <div className="flex items-center gap-3">
                              {order.document_count > 0 && (
                                <span className="flex items-center gap-1 text-blue-600">
                                  <FileText className="h-4 w-4" />
                                  {order.document_count}
                                </span>
                              )}
                              <div className="flex items-center gap-1 text-gray-400 group-hover:text-blue-500 transition-colors">
                                <Eye className="h-4 w-4" />
                                <span className="text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                                  Ver detalhes
                                </span>
                                <ExternalLink className="h-4 w-4" />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination Footer */}
                {filteredOrders.length >= 50 && (
                  <div className="border-t border-gray-200 pt-4 pb-2">
                    <div className="flex items-center justify-center">
                      <span className="text-sm text-gray-500">
                        Mostrando primeiras 50 orders - carregue mais para ver todas
                      </span>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </CardContent>
      </Card>

        </div>
      </div>

      {/* Order Details Modal */}
      {selectedOrder && isOrderModalOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[9999] backdrop-blur-sm"
          onClick={closeOrderModal}
        >
          <div 
            className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto relative transform transition-all duration-300 scale-100 opacity-100"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedOrder.title}
                </h2>
                <p className="text-gray-600 mt-1">
                  Order ID: {selectedOrder.order_id}
                </p>
              </div>
              <button
                onClick={closeOrderModal}
                className="text-gray-400 hover:text-gray-600 text-xl p-2 hover:bg-gray-100 rounded-full transition-colors duration-200 flex items-center justify-center w-10 h-10"
                title="Fechar modal (ESC)"
              >
                ✕
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Status and Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Status</h3>
                  <Badge 
                    className={`
                      ${selectedOrder.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
                      ${selectedOrder.status === 'in_progress' ? 'bg-blue-100 text-blue-800' : ''}
                      ${selectedOrder.status === 'created' ? 'bg-yellow-100 text-yellow-800' : ''}
                      ${selectedOrder.status === 'cancelled' ? 'bg-red-100 text-red-800' : ''}
                      ${selectedOrder.status === 'delivered' ? 'bg-emerald-100 text-emerald-800' : ''}
                      ${selectedOrder.status === 'shipped' ? 'bg-indigo-100 text-indigo-800' : ''}
                      ${selectedOrder.status === 'in_transit' ? 'bg-purple-100 text-purple-800' : ''}
                    `}
                  >
                    {selectedOrder.status === 'completed' && '✅ Concluído'}
                    {selectedOrder.status === 'in_progress' && '🔄 Em Andamento'}
                    {selectedOrder.status === 'created' && '📝 Criado'}
                    {selectedOrder.status === 'cancelled' && '❌ Cancelado'}
                    {selectedOrder.status === 'delivered' && '🚚 Entregue'}
                    {selectedOrder.status === 'shipped' && '📦 Embarcado'}
                    {selectedOrder.status === 'in_transit' && '🚛 Em Trânsito'}
                  </Badge>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Tipo</h3>
                  <span className="inline-flex items-center gap-1">
                    <Truck className="h-4 w-4 text-blue-600" />
                    {selectedOrder.order_type === 'import' && 'Importação'}
                    {selectedOrder.order_type === 'export' && 'Exportação'}
                    {selectedOrder.order_type === 'domestic_freight' && 'Frete Nacional'}
                    {selectedOrder.order_type === 'international_freight' && 'Frete Internacional'}
                    {selectedOrder.order_type === 'warehousing' && 'Armazenagem'}
                    {selectedOrder.order_type === 'customs_clearance' && 'Desembaraço'}
                  </span>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Prioridade</h3>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: 5 }, (_, i) => (
                      <div
                        key={i}
                        className={`w-3 h-3 rounded-full ${
                          i < selectedOrder.priority 
                            ? 'bg-yellow-400' 
                            : 'bg-gray-200'
                        }`}
                      />
                    ))}
                    <span className="ml-2 text-sm text-gray-600">
                      {selectedOrder.priority}/5
                    </span>
                  </div>
                </div>
              </div>

              {/* Customer Information */}
              <div className="bg-blue-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <User className="h-5 w-5 text-blue-600" />
                  Informações do Cliente
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Nome:</span>
                    <p className="font-medium">{selectedOrder.customer_name}</p>
                  </div>
                  {selectedOrder.customer_id && (
                    <div>
                      <span className="text-sm text-gray-600">ID:</span>
                      <p className="font-medium">{selectedOrder.customer_id}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Route Information */}
              {(selectedOrder.origin || selectedOrder.destination) && (
                <div className="bg-green-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-green-600" />
                    Rota
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {selectedOrder.origin && (
                      <div>
                        <span className="text-sm text-gray-600">Origem:</span>
                        <p className="font-medium">{selectedOrder.origin}</p>
                      </div>
                    )}
                    {selectedOrder.destination && (
                      <div>
                        <span className="text-sm text-gray-600">Destino:</span>
                        <p className="font-medium">{selectedOrder.destination}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Description */}
              {selectedOrder.description && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Descrição</h3>
                  <p className="text-gray-700 bg-gray-50 rounded-lg p-4">
                    {selectedOrder.description}
                  </p>
                </div>
              )}

              {/* Financial Information */}
              {(selectedOrder.estimated_value || selectedOrder.actual_cost) && (
                <div className="bg-yellow-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-3">Informações Financeiras</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {selectedOrder.estimated_value && (
                      <div>
                        <span className="text-sm text-gray-600">Valor Estimado:</span>
                        <p className="font-medium">
                          {selectedOrder.currency} {selectedOrder.estimated_value.toLocaleString()}
                        </p>
                      </div>
                    )}
                    {selectedOrder.actual_cost && (
                      <div>
                        <span className="text-sm text-gray-600">Custo Real:</span>
                        <p className="font-medium">
                          {selectedOrder.currency} {selectedOrder.actual_cost.toLocaleString()}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Documents */}
              <div className="bg-purple-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-purple-600" />
                  Documentos
                </h3>
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">
                    {selectedOrder.document_count} documento{selectedOrder.document_count !== 1 ? 's' : ''} anexado{selectedOrder.document_count !== 1 ? 's' : ''}
                  </span>
                  {selectedOrder.document_count > 0 && (
                    <Button variant="outline" size="sm">
                      Ver Documentos
                    </Button>
                  )}
                </div>
              </div>

              {/* Tags */}
              {selectedOrder.tags.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedOrder.tags.map((tag, index) => (
                      <Badge key={index} variant="outline">
                        #{tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Dates */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-gray-600" />
                  Datas
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Criado em:</span>
                    <p className="font-medium">
                      {new Date(selectedOrder.created_at).toLocaleDateString('pt-BR')} às{' '}
                      {new Date(selectedOrder.created_at).toLocaleTimeString('pt-BR')}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600">Última atividade:</span>
                    <p className="font-medium">
                      {new Date(selectedOrder.last_activity).toLocaleDateString('pt-BR')} às{' '}
                      {new Date(selectedOrder.last_activity).toLocaleTimeString('pt-BR')}
                    </p>
                  </div>
                  {selectedOrder.expected_delivery && (
                    <div>
                      <span className="text-gray-600">Entrega prevista:</span>
                      <p className="font-medium">
                        {new Date(selectedOrder.expected_delivery).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  )}
                  {selectedOrder.actual_delivery && (
                    <div>
                      <span className="text-gray-600">Entrega realizada:</span>
                      <p className="font-medium">
                        {new Date(selectedOrder.actual_delivery).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 flex justify-between">
              <Button variant="outline" onClick={closeOrderModal}>
                Fechar
              </Button>
              <div className="flex gap-2">
                <Button variant="outline">
                  Editar Order
                </Button>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  Ver Documentos
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Order Dialog */}
      <CreateOrderDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onOrderCreated={handleOrderCreated}
      />
    </div>
  )
}