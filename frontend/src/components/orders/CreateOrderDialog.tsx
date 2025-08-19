// 🆕 Create Order Dialog Component
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/Label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
// Using native select elements for better compatibility

interface CreateOrderDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onOrderCreated: (order: any) => void
}

interface CreateOrderFormData {
  title: string
  description: string
  order_type: string
  customer_name: string
  origin: string
  destination: string
  estimated_value: string
  currency: string
  tags: string
  priority: number
}

export function CreateOrderDialog({ open, onOpenChange, onOrderCreated }: CreateOrderDialogProps) {
  const [formData, setFormData] = useState<CreateOrderFormData>({
    title: '',
    description: '',
    order_type: '',
    customer_name: '',
    origin: '',
    destination: '',
    estimated_value: '',
    currency: 'BRL',
    tags: '',
    priority: 3
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const orderTypes = [
    { value: 'import', label: 'Importação' },
    { value: 'export', label: 'Exportação' },
    { value: 'domestic_freight', label: 'Frete Nacional' },
    { value: 'international_freight', label: 'Frete Internacional' },
    { value: 'warehousing', label: 'Armazenagem' },
    { value: 'customs_clearance', label: 'Desembaraço Aduaneiro' }
  ]

  const priorities = [
    { value: 1, label: '1 - Baixa' },
    { value: 2, label: '2 - Baixa' },
    { value: 3, label: '3 - Normal' },
    { value: 4, label: '4 - Alta' },
    { value: 5, label: '5 - Crítica' }
  ]

  const currencies = [
    { value: 'BRL', label: 'Real (BRL)' },
    { value: 'USD', label: 'Dólar (USD)' },
    { value: 'EUR', label: 'Euro (EUR)' }
  ]

  const handleInputChange = (field: keyof CreateOrderFormData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Título é obrigatório'
    }
    if (!formData.order_type) {
      newErrors.order_type = 'Tipo de operação é obrigatório'
    }
    if (!formData.customer_name.trim()) {
      newErrors.customer_name = 'Nome do cliente é obrigatório'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      // Prepare data for API
      const submitData = {
        title: formData.title.trim(),
        description: formData.description.trim() || undefined,
        order_type: formData.order_type,
        customer_name: formData.customer_name.trim(),
        origin: formData.origin.trim() || undefined,
        destination: formData.destination.trim() || undefined,
        estimated_value: formData.estimated_value ? parseFloat(formData.estimated_value) : undefined,
        currency: formData.currency,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(Boolean),
        priority: formData.priority
      }

      const response = await fetch('http://localhost:8001/orders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData)
      })

      if (!response.ok) {
        throw new Error('Erro ao criar order')
      }

      const newOrder = await response.json()
      onOrderCreated(newOrder)
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        order_type: '',
        customer_name: '',
        origin: '',
        destination: '',
        estimated_value: '',
        currency: 'BRL',
        tags: '',
        priority: 3
      })
      
    } catch (error) {
      console.error('Erro ao criar order:', error)
      setErrors({ submit: 'Erro ao criar order. Tente novamente.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      title: '',
      description: '',
      order_type: '',
      customer_name: '',
      origin: '',
      destination: '',
      estimated_value: '',
      currency: 'BRL',
      tags: '',
      priority: 3
    })
    setErrors({})
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader className="border-b border-gray-200 pb-4">
          <DialogTitle className="text-2xl font-bold text-gray-900 flex items-center gap-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              📋
            </div>
            Criar Nova Order
          </DialogTitle>
          <DialogDescription className="text-gray-600 mt-2">
            Crie um novo super-contêiner para organizar todos os documentos de uma operação logística. 
            Todas as informações podem ser editadas posteriormente.
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto py-6">{/* Form will go here */}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Information */}
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="flex items-center gap-2 mb-4">
                <div className="bg-blue-500 w-1 h-6 rounded"></div>
                <h3 className="text-lg font-semibold text-gray-900">Informações Básicas</h3>
              </div>
              
              <div className="grid gap-6">
                <div>
                  <Label htmlFor="title" className="text-sm font-medium text-gray-700 mb-2 block">
                    Título da Operação *
                  </Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    placeholder="Ex: Importação de Eletrônicos - Cliente ABC"
                    className={`h-11 ${errors.title ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-blue-500'}`}
                  />
                  {errors.title && (
                    <div className="flex items-center gap-1 mt-2">
                      <span className="text-red-500 text-xs">⚠</span>
                      <p className="text-sm text-red-600">{errors.title}</p>
                    </div>
                  )}
                </div>

                <div>
                  <Label htmlFor="description" className="text-sm font-medium text-gray-700 mb-2 block">
                    Descrição
                  </Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="Descrição detalhada da operação..."
                    rows={3}
                    className="border-gray-300 focus:border-blue-500 resize-none"
                  />
                  <p className="text-xs text-gray-500 mt-1">Opcional - você pode adicionar mais detalhes depois</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="order_type" className="text-sm font-medium text-gray-700 mb-2 block">
                      Tipo de Operação *
                    </Label>
                    <select
                      id="order_type"
                      value={formData.order_type}
                      onChange={(e) => handleInputChange('order_type', e.target.value)}
                      className={`w-full h-11 px-3 py-2 border bg-white rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.order_type ? 'border-red-500' : 'border-gray-300'}`}
                    >
                      <option value="" disabled>Selecione o tipo</option>
                      {orderTypes.map(type => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                    {errors.order_type && (
                      <div className="flex items-center gap-1 mt-2">
                        <span className="text-red-500 text-xs">⚠</span>
                        <p className="text-sm text-red-600">{errors.order_type}</p>
                      </div>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="priority" className="text-sm font-medium text-gray-700 mb-2 block">
                      Prioridade
                    </Label>
                    <select
                      id="priority"
                      value={formData.priority.toString()}
                      onChange={(e) => handleInputChange('priority', parseInt(e.target.value))}
                      className="w-full h-11 px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {priorities.map(priority => (
                        <option key={priority.value} value={priority.value.toString()}>
                          {priority.label}
                        </option>
                      ))}
                    </select>
                    <p className="text-xs text-gray-500 mt-1">Nível de urgência da operação</p>
                  </div>
                </div>
              </div>
            </div>

          {/* Customer and Logistics */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-muted-foreground">Cliente e Logística</h3>
            
            <div>
              <Label htmlFor="customer_name">Nome do Cliente *</Label>
              <Input
                id="customer_name"
                value={formData.customer_name}
                onChange={(e) => handleInputChange('customer_name', e.target.value)}
                placeholder="Nome da empresa ou cliente"
                className={errors.customer_name ? 'border-red-500' : ''}
              />
              {errors.customer_name && <p className="text-sm text-red-500 mt-1">{errors.customer_name}</p>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="origin">Origem</Label>
                <Input
                  id="origin"
                  value={formData.origin}
                  onChange={(e) => handleInputChange('origin', e.target.value)}
                  placeholder="Porto de Santos, São Paulo..."
                />
              </div>

              <div>
                <Label htmlFor="destination">Destino</Label>
                <Input
                  id="destination"
                  value={formData.destination}
                  onChange={(e) => handleInputChange('destination', e.target.value)}
                  placeholder="São Paulo/SP, Rio de Janeiro..."
                />
              </div>
            </div>
          </div>

          {/* Financial and Additional */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-muted-foreground">Financeiro e Extras</h3>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-2">
                <Label htmlFor="estimated_value">Valor Estimado</Label>
                <Input
                  id="estimated_value"
                  type="number"
                  step="0.01"
                  value={formData.estimated_value}
                  onChange={(e) => handleInputChange('estimated_value', e.target.value)}
                  placeholder="150000.00"
                />
              </div>

              <div>
                <Label htmlFor="currency">Moeda</Label>
                <select
                  id="currency"
                  value={formData.currency}
                  onChange={(e) => handleInputChange('currency', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {currencies.map(currency => (
                    <option key={currency.value} value={currency.value}>
                      {currency.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <Label htmlFor="tags">Tags</Label>
              <Input
                id="tags"
                value={formData.tags}
                onChange={(e) => handleInputChange('tags', e.target.value)}
                placeholder="eletrônicos, importação, santos (separados por vírgula)"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Separe as tags com vírgulas para melhor organização
              </p>
            </div>
          </div>

            {/* Error Message */}
            {errors.submit && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="bg-red-100 p-1 rounded-full">
                    <span className="text-red-600 text-sm">⚠</span>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-red-800">Erro ao criar order</h4>
                    <p className="text-sm text-red-600 mt-1">{errors.submit}</p>
                  </div>
                </div>
              </div>
            )}
          </form>
        </div>

        <DialogFooter className="border-t border-gray-200 pt-4 bg-gray-50">
          <div className="flex justify-between items-center w-full">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span className="w-2 h-2 bg-green-400 rounded-full"></span>
              <span>Dados salvos automaticamente</span>
            </div>
            <div className="flex gap-3">
              <Button 
                type="button" 
                variant="outline" 
                onClick={handleCancel}
                disabled={isSubmitting}
                className="px-6 py-2 border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </Button>
              <Button 
                type="submit" 
                disabled={isSubmitting}
                onClick={handleSubmit}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
              >
                {isSubmitting ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Criando...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <span>✨</span>
                    Criar Order
                  </div>
                )}
              </Button>
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}