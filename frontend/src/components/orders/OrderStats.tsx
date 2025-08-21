// 📊 Order Statistics Component
'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { 
  Package, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Truck,
  Ship,
  Warehouse,
  FileText
} from 'lucide-react'

interface OrdersStats {
  total_orders: number
  by_status: Record<string, number>
  by_type: Record<string, number>
}

interface OrderStatsProps {
  stats: OrdersStats
}

export function OrderStats({ stats }: OrderStatsProps) {
  const statusConfig = {
    created: { label: 'Criadas', icon: Clock, color: 'bg-gray-100 text-gray-800' },
    in_progress: { label: 'Em Andamento', icon: TrendingUp, color: 'bg-blue-100 text-blue-800' },
    shipped: { label: 'Embarcadas', icon: Ship, color: 'bg-indigo-100 text-indigo-800' },
    in_transit: { label: 'Em Trânsito', icon: Truck, color: 'bg-yellow-100 text-yellow-800' },
    delivered: { label: 'Entregues', icon: CheckCircle, color: 'bg-green-100 text-green-800' },
    completed: { label: 'Concluídas', icon: CheckCircle, color: 'bg-emerald-100 text-emerald-800' },
    cancelled: { label: 'Canceladas', icon: XCircle, color: 'bg-red-100 text-red-800' }
  }

  const typeConfig = {
    import: { label: 'Importação', icon: Ship, color: 'bg-blue-100 text-blue-800' },
    export: { label: 'Exportação', icon: Ship, color: 'bg-green-100 text-green-800' },
    domestic_freight: { label: 'Frete Nacional', icon: Truck, color: 'bg-orange-100 text-orange-800' },
    international_freight: { label: 'Frete Internacional', icon: Truck, color: 'bg-purple-100 text-purple-800' },
    warehousing: { label: 'Armazenagem', icon: Warehouse, color: 'bg-gray-100 text-gray-800' },
    customs_clearance: { label: 'Desembaraço', icon: FileText, color: 'bg-indigo-100 text-indigo-800' }
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Total Orders */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total de Orders</CardTitle>
          <Package className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total_orders}</div>
          <p className="text-xs text-muted-foreground">
            Super-contêineres ativos
          </p>
        </CardContent>
      </Card>

      {/* Active Orders */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Em Andamento</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {(stats.by_status.in_progress || 0) + (stats.by_status.shipped || 0) + (stats.by_status.in_transit || 0)}
          </div>
          <p className="text-xs text-muted-foreground">
            Orders ativas no sistema
          </p>
        </CardContent>
      </Card>

      {/* Completed Orders */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Concluídas</CardTitle>
          <CheckCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {(stats.by_status.completed || 0) + (stats.by_status.delivered || 0)}
          </div>
          <p className="text-xs text-muted-foreground">
            Orders finalizadas
          </p>
        </CardContent>
      </Card>

      {/* Pending Orders */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Aguardando</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {stats.by_status.created || 0}
          </div>
          <p className="text-xs text-muted-foreground">
            Orders criadas recentemente
          </p>
        </CardContent>
      </Card>

      {/* Status Breakdown */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Distribuição por Status</CardTitle>
          <CardDescription>
            Visão geral do status das orders
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(stats.by_status).map(([status, count]) => {
              const config = statusConfig[status as keyof typeof statusConfig]
              if (!config || count === 0) return null
              
              const Icon = config.icon
              return (
                <div key={status} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Icon className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{config.label}</span>
                  </div>
                  <Badge variant="secondary" className={config.color}>
                    {count}
                  </Badge>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Type Breakdown */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Distribuição por Tipo</CardTitle>
          <CardDescription>
            Tipos de operações logísticas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(stats.by_type).map(([type, count]) => {
              const config = typeConfig[type as keyof typeof typeConfig]
              if (!config || count === 0) return null
              
              const Icon = config.icon
              return (
                <div key={type} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Icon className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{config.label}</span>
                  </div>
                  <Badge variant="secondary" className={config.color}>
                    {count}
                  </Badge>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}