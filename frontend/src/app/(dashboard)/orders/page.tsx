// 📋 Orders Management Page - Super-container Interface
'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Plus, Search, FileText, Package, Calendar, User } from 'lucide-react'
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

  // Fetch orders from API
  const fetchOrders = async () => {
    try {
      setIsLoading(true)
      const params = new URLSearchParams()
      if (selectedStatus) params.append('status', selectedStatus)
      if (selectedType) params.append('order_type', selectedType)
      
      const response = await fetch(`http://localhost:8001/orders/?${params}`)
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

  useEffect(() => {
    fetchOrders()
    fetchStats()
  }, [selectedStatus, selectedType])

  // Filter orders based on search term
  const filteredOrders = orders.filter(order =>
    order.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  const handleOrderCreated = (newOrder: Order) => {
    setOrders(prev => [newOrder, ...prev])
    fetchStats() // Refresh stats
    setIsCreateDialogOpen(false)
  }

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
        </CardContent>
      </Card>

          {/* Orders List */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 min-h-[500px]">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-16">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mb-4"></div>
                <span className="text-gray-600 font-medium">Carregando orders...</span>
                <span className="text-gray-400 text-sm mt-1">Buscando dados no servidor</span>
              </div>
            ) : filteredOrders.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 px-6">
                <div className="bg-gray-100 rounded-full p-6 mb-6">
                  <Package className="h-16 w-16 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {searchTerm || selectedStatus || selectedType 
                    ? 'Nenhuma order encontrada' 
                    : 'Nenhuma order criada ainda'
                  }
                </h3>
                <p className="text-gray-500 text-center max-w-md mb-6">
                  {searchTerm || selectedStatus || selectedType 
                    ? 'Tente ajustar os filtros de busca ou criar uma nova order'
                    : 'Crie sua primeira order para começar a organizar documentos de suas operações logísticas'
                  }
                </p>
                <Button 
                  onClick={() => setIsCreateDialogOpen(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3"
                >
                  <Plus className="mr-2 h-5 w-5" />
                  {searchTerm || selectedStatus || selectedType ? 'Nova Order' : 'Criar Primeira Order'}
                </Button>
              </div>
            ) : (
              <>
                {/* Results Header */}
                <div className="border-b border-gray-200 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Orders Encontradas
                      </h3>
                      <p className="text-sm text-gray-500">
                        {filteredOrders.length} de {orders.length} orders
                        {(searchTerm || selectedStatus || selectedType) && ' (filtradas)'}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <span>Ordenar por:</span>
                      <select className="border border-gray-300 rounded px-2 py-1 text-sm">
                        <option>Atividade recente</option>
                        <option>Data de criação</option>
                        <option>Nome do cliente</option>
                        <option>Prioridade</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Scrollable Orders List */}
                <div className="max-h-[600px] overflow-y-auto">
                  <div className="p-6 space-y-4">
                    {filteredOrders.map((order) => (
                      <OrderCard 
                        key={order._id} 
                        order={order} 
                        onOrderUpdated={fetchOrders}
                      />
                    ))}
                  </div>
                </div>

                {/* Pagination (Future) */}
                <div className="border-t border-gray-200 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">
                      Mostrando {filteredOrders.length} orders
                    </span>
                    <div className="text-sm text-gray-500">
                      {filteredOrders.length >= 50 && (
                        <span>Carregue mais para ver todas as orders</span>
                      )}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Create Order Dialog */}
      <CreateOrderDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onOrderCreated={handleOrderCreated}
      />
    </div>
  )
}