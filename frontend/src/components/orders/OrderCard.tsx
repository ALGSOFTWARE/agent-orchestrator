// 📋 Order Card Component - Individual Order Display
'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { 
  MoreHorizontal, 
  FileText, 
  Calendar, 
  MapPin, 
  User, 
  DollarSign,
  Package,
  ArrowRight,
  Clock
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

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

interface OrderCardProps {
  order: Order
  onOrderUpdated: () => void
}

export function OrderCard({ order, onOrderUpdated }: OrderCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Status configuration
  const statusConfig = {
    created: { label: 'Criada', color: 'bg-gray-100 text-gray-800 border-gray-200' },
    in_progress: { label: 'Em Andamento', color: 'bg-blue-100 text-blue-800 border-blue-200' },
    shipped: { label: 'Embarcada', color: 'bg-indigo-100 text-indigo-800 border-indigo-200' },
    in_transit: { label: 'Em Trânsito', color: 'bg-yellow-100 text-yellow-800 border-yellow-200' },
    delivered: { label: 'Entregue', color: 'bg-green-100 text-green-800 border-green-200' },
    completed: { label: 'Concluída', color: 'bg-emerald-100 text-emerald-800 border-emerald-200' },
    cancelled: { label: 'Cancelada', color: 'bg-red-100 text-red-800 border-red-200' }
  }

  // Type configuration
  const typeConfig = {
    import: { label: 'Importação', icon: '🚢' },
    export: { label: 'Exportação', icon: '📦' },
    domestic_freight: { label: 'Frete Nacional', icon: '🚛' },
    international_freight: { label: 'Frete Internacional', icon: '✈️' },
    warehousing: { label: 'Armazenagem', icon: '🏪' },
    customs_clearance: { label: 'Desembaraço', icon: '📋' }
  }

  // Priority colors
  const priorityConfig = {
    1: { label: 'Baixa', color: 'bg-gray-100 text-gray-600' },
    2: { label: 'Baixa', color: 'bg-gray-100 text-gray-600' },
    3: { label: 'Normal', color: 'bg-blue-100 text-blue-600' },
    4: { label: 'Alta', color: 'bg-orange-100 text-orange-600' },
    5: { label: 'Crítica', color: 'bg-red-100 text-red-600' }
  }

  const status = statusConfig[order.status as keyof typeof statusConfig]
  const type = typeConfig[order.order_type as keyof typeof typeConfig]
  const priority = priorityConfig[order.priority as keyof typeof priorityConfig]

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatValue = (value?: number, currency?: string) => {
    if (!value) return null
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: currency || 'BRL'
    }).format(value)
  }

  const handleViewDetails = () => {
    // Navigate to order details page
    window.location.href = `/orders/${order.order_id}`
  }

  const handleChangeStatus = async (newStatus: string) => {
    try {
      const response = await fetch(`http://localhost:8001/orders/${order.order_id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_status: newStatus, user_id: 'current_user' })
      })
      
      if (response.ok) {
        onOrderUpdated()
      }
    } catch (error) {
      console.error('Erro ao alterar status:', error)
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 hover:border-gray-300">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-3 mb-2">
              <div className="flex-shrink-0">
                <span className="text-2xl">{type?.icon}</span>
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-lg font-semibold text-gray-900 truncate">
                  {order.title}
                </h3>
                <div className="flex items-center space-x-3 text-sm text-gray-500 mt-1">
                  <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
                    {order.order_id.split('-')[0]}...
                  </span>
                  <span>•</span>
                  <span className="flex items-center">
                    <User className="h-3 w-3 mr-1" />
                    {order.customer_name}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 ml-4">
            {/* Priority Badge */}
            {priority && order.priority > 3 && (
              <Badge variant="secondary" className={`${priority.color} text-xs font-medium`}>
                {priority.label}
              </Badge>
            )}
            
            {/* Status Badge */}
            <Badge variant="secondary" className={`${status?.color} text-xs font-medium`}>
              {status?.label}
            </Badge>
            
            {/* Actions Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0 hover:bg-gray-100">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={handleViewDetails} className="flex items-center">
                  <ArrowRight className="h-4 w-4 mr-2" />
                  Ver Detalhes
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleChangeStatus('in_progress')} className="flex items-center">
                  <Clock className="h-4 w-4 mr-2" />
                  Marcar Em Andamento
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleChangeStatus('completed')} className="flex items-center">
                  <Package className="h-4 w-4 mr-2" />
                  Marcar Concluída
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        
        {/* Description */}
        {order.description && (
          <div className="mb-4">
            <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
              {order.description}
            </p>
          </div>
        )}
        
        {/* Key Information Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          {/* Origin/Destination */}
          {(order.origin || order.destination) && (
            <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
              <MapPin className="h-4 w-4 text-gray-500 flex-shrink-0" />
              <div className="min-w-0">
                <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Rota</p>
                <p className="text-sm text-gray-900 truncate">
                  {order.origin && order.destination 
                    ? `${order.origin} → ${order.destination}`
                    : order.origin || order.destination
                  }
                </p>
              </div>
            </div>
          )}
          
          {/* Document Count */}
          <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
            <FileText className="h-4 w-4 text-gray-500 flex-shrink-0" />
            <div>
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Documentos</p>
              <p className="text-sm text-gray-900 font-medium">
                {order.document_count} arquivos
              </p>
            </div>
          </div>
          
          {/* Estimated Value */}
          {order.estimated_value && (
            <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
              <DollarSign className="h-4 w-4 text-gray-500 flex-shrink-0" />
              <div>
                <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Valor</p>
                <p className="text-sm text-gray-900 font-medium">
                  {formatValue(order.estimated_value, order.currency)}
                </p>
              </div>
            </div>
          )}
        </div>
        
        {/* Tags */}
        {order.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {order.tags.slice(0, 4).map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {tag}
              </span>
            ))}
            {order.tags.length > 4 && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                +{order.tags.length - 4} mais
              </span>
            )}
          </div>
        )}
        
        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <div className="flex items-center space-x-1">
              <Calendar className="h-3 w-3" />
              <span>Criada {formatDate(order.created_at)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="h-3 w-3" />
              <span>Atividade {formatDate(order.last_activity)}</span>
            </div>
          </div>
          
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleViewDetails}
            className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-3 py-1.5"
          >
            Ver Detalhes
            <ArrowRight className="ml-1 h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}