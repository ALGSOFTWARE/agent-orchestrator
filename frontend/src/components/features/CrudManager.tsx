'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { 
  getDatabaseStats, 
  getUsers, 
  getClients, 
  getContainers,
  getShipments,
  getTrackingEvents,
  getContexts,
  createUser,
  updateUser,
  deleteUser,
  type User,
  type Client,
  type Container,
  type Shipment,
  type TrackingEvent,
  type Context,
  type DatabaseStats,
  type CreateUserRequest
} from '@/lib/api/crud'
import styles from '@/styles/modules/CrudManager.module.css'

type EntityType = 'users' | 'clients' | 'containers' | 'shipments' | 'tracking_events' | 'contexts'

interface CrudManagerProps {
  className?: string
}

export function CrudManager({ className }: CrudManagerProps) {
  const [activeEntity, setActiveEntity] = useState<EntityType>('users')
  const [stats, setStats] = useState<DatabaseStats | null>(null)
  const [entities, setEntities] = useState<any[]>([])
  const [selectedEntity, setSelectedEntity] = useState<any | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState({ skip: 0, limit: 20 })

  // Form states for creating/editing
  const [formData, setFormData] = useState<any>({})

  // Load initial stats
  useEffect(() => {
    loadStats()
  }, [])

  // Load entities when active entity changes
  useEffect(() => {
    loadEntities()
  }, [activeEntity, pagination])

  const loadStats = async () => {
    try {
      console.log('🔄 Carregando estatísticas do banco...')
      const data = await getDatabaseStats()
      console.log('✅ Estatísticas carregadas:', data)
      setStats(data)
    } catch (err) {
      console.error('❌ Erro ao carregar estatísticas:', err)
      setError(err instanceof Error ? err.message : 'Erro ao carregar estatísticas')
    }
  }

  const loadEntities = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      let data: any[] = []
      
      console.log(`🔄 Carregando ${activeEntity} com paginação:`, pagination)
      
      switch (activeEntity) {
        case 'users':
          data = await getUsers(pagination)
          console.log('✅ Users carregados:', data?.length || 0, 'itens')
          break
        case 'clients':
          data = await getClients(pagination)
          console.log('✅ Clients carregados:', data?.length || 0, 'itens')
          break
        case 'containers':
          data = await getContainers(pagination)
          console.log('✅ Containers carregados:', data?.length || 0, 'itens')
          break
        case 'shipments':
          data = await getShipments(pagination)
          console.log('✅ Shipments carregados:', data?.length || 0, 'itens')
          break
        case 'tracking_events':
          data = await getTrackingEvents(pagination)
          console.log('✅ Tracking events carregados:', data?.length || 0, 'itens')
          break
        case 'contexts':
          data = await getContexts(pagination)
          console.log('✅ Contexts carregados:', data?.length || 0, 'itens')
          break
      }
      
      if (!Array.isArray(data)) {
        console.warn('⚠️ Dados retornados não são um array:', data)
        setError('Formato de dados inválido retornado pela API')
        setEntities([])
        return
      }
      
      setEntities(data)
      console.log(`✅ Total de ${activeEntity} carregados:`, data.length)
    } catch (err) {
      console.error('❌ Erro ao carregar dados:', err)
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido ao carregar dados'
      setError(`Erro ao carregar ${activeEntity}: ${errorMessage}`)
      setEntities([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreate = async () => {
    if (activeEntity !== 'users') {
      alert('Criação só implementada para usuários no momento')
      return
    }

    try {
      const userData: CreateUserRequest = {
        name: formData.name || '',
        email: formData.email || '',
        role: formData.role || 'operator',
        client_id: formData.client_id || undefined
      }

      await createUser(userData)
      setIsCreating(false)
      setFormData({})
      loadEntities()
      loadStats() // Refresh stats
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar usuário')
    }
  }

  const handleDelete = async (entityId: string) => {
    if (activeEntity !== 'users') {
      alert('Exclusão só implementada para usuários no momento')
      return
    }

    if (!confirm('Tem certeza que deseja remover este usuário?')) return

    try {
      await deleteUser(entityId, true) // Soft delete
      loadEntities()
      loadStats() // Refresh stats
      setSelectedEntity(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao remover usuário')
    }
  }

  const renderEntityList = () => {
    if (isLoading) {
      return <div className={styles.loading}>Carregando...</div>
    }

    if (entities.length === 0) {
      return <div className={styles.empty}>Nenhum registro encontrado</div>
    }

    return (
      <div className={styles.entityList}>
        {entities.map((entity) => (
          <div
            key={entity._id}
            className={`${styles.entityItem} ${selectedEntity?._id === entity._id ? styles.selected : ''}`}
            onClick={() => setSelectedEntity(entity)}
          >
            {renderEntitySummary(entity)}
          </div>
        ))}
      </div>
    )
  }

  const renderEntitySummary = (entity: any) => {
    switch (activeEntity) {
      case 'users':
        const user = entity as User
        return (
          <>
            <div className={styles.entityHeader}>
              <strong>{user.name}</strong>
              <Badge variant={user.is_active ? 'success' : 'error'}>
                {user.is_active ? 'Ativo' : 'Inativo'}
              </Badge>
            </div>
            <div className={styles.entityDetails}>
              <span>{user.email}</span>
              <Badge variant="secondary">{user.role}</Badge>
            </div>
          </>
        )
      case 'clients':
        const client = entity as Client
        return (
          <>
            <div className={styles.entityHeader}>
              <strong>{client.name}</strong>
            </div>
            <div className={styles.entityDetails}>
              <span>{client.cnpj || 'Sem CNPJ'}</span>
            </div>
          </>
        )
      case 'containers':
        const container = entity as Container
        return (
          <>
            <div className={styles.entityHeader}>
              <strong>{container.container_number}</strong>
              <Badge variant="info">{container.current_status}</Badge>
            </div>
            <div className={styles.entityDetails}>
              <span>{container.type || 'Tipo não especificado'}</span>
            </div>
          </>
        )
      default:
        return (
          <div className={styles.entityHeader}>
            <strong>ID: {entity._id}</strong>
          </div>
        )
    }
  }

  const renderEntityDetails = () => {
    if (!selectedEntity) {
      return (
        <div className={styles.noSelection}>
          Selecione um item da lista para ver os detalhes
        </div>
      )
    }

    return (
      <div className={styles.entityDetails}>
        <div className={styles.detailsHeader}>
          <h3>Detalhes do {activeEntity.slice(0, -1)}</h3>
          {activeEntity === 'users' && (
            <Button
              variant="error"
              size="small"
              onClick={() => handleDelete(selectedEntity._id)}
            >
              🗑️ Remover
            </Button>
          )}
        </div>
        
        <pre className={styles.jsonDisplay}>
          {JSON.stringify(selectedEntity, null, 2)}
        </pre>
      </div>
    )
  }

  const renderCreateForm = () => {
    if (activeEntity !== 'users') {
      return (
        <div className={styles.notImplemented}>
          Formulário de criação não implementado para {activeEntity}
        </div>
      )
    }

    return (
      <div className={styles.createForm}>
        <h3>Criar Novo Usuário</h3>
        
        <div className={styles.formRow}>
          <Input
            label="Nome"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Nome do usuário"
          />
        </div>
        
        <div className={styles.formRow}>
          <Input
            label="Email"
            type="email"
            value={formData.email || ''}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="email@exemplo.com"
          />
        </div>
        
        <div className={styles.formRow}>
          <label>Role</label>
          <select
            value={formData.role || 'operator'}
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
            className={styles.select}
          >
            <option value="admin">Admin</option>
            <option value="logistics">Logistics</option>
            <option value="finance">Finance</option>
            <option value="operator">Operator</option>
          </select>
        </div>
        
        <div className={styles.formActions}>
          <Button
            variant="primary"
            onClick={handleCreate}
          >
            Criar Usuário
          </Button>
          <Button
            variant="secondary"
            onClick={() => setIsCreating(false)}
          >
            Cancelar
          </Button>
        </div>
      </div>
    )
  }

  const entityTypes = [
    { key: 'users', label: 'Usuários', count: stats?.users },
    { key: 'clients', label: 'Clientes', count: stats?.clients },
    { key: 'containers', label: 'Containers', count: stats?.containers },
    { key: 'shipments', label: 'Embarques', count: stats?.shipments },
    { key: 'tracking_events', label: 'Eventos', count: stats?.tracking_events },
    { key: 'contexts', label: 'Contextos', count: stats?.contexts },
  ] as const

  return (
    <div className={`${styles.crudManager} ${className || ''}`}>
      {/* Header with Stats */}
      <div className={styles.header}>
        <h2>🗄️ CRUD Manager</h2>
        <div className={styles.stats}>
          {stats && (
            <>
              <Badge variant="info">
                Total: {stats.users + stats.clients + stats.containers + stats.shipments + stats.tracking_events + stats.contexts}
              </Badge>
              <Badge variant="success">
                Usuários Ativos: {stats.active_users}
              </Badge>
            </>
          )}
        </div>
      </div>

      {/* Entity Type Tabs */}
      <div className={styles.entityTabs}>
        {entityTypes.map(({ key, label, count }) => (
          <button
            key={key}
            className={`${styles.entityTab} ${activeEntity === key ? styles.active : ''}`}
            onClick={() => {
              setActiveEntity(key)
              setSelectedEntity(null)
              setPagination({ skip: 0, limit: 20 })
            }}
          >
            {label}
            {count !== undefined && (
              <Badge variant="secondary" size="small">{count}</Badge>
            )}
          </button>
        ))}
      </div>

      {/* Error Display */}
      {error && (
        <div className={styles.error}>
          ⚠️ {error}
        </div>
      )}

      {/* Main Content */}
      <div className={styles.content}>
        {/* Left Panel - Entity List */}
        <div className={styles.leftPanel}>
          <div className={styles.listHeader}>
            <h3>{entityTypes.find(e => e.key === activeEntity)?.label}</h3>
            <Button
              size="small"
              onClick={() => setIsCreating(true)}
              disabled={activeEntity !== 'users'}
            >
              ➕ Criar
            </Button>
          </div>
          
          {renderEntityList()}
          
          {/* Pagination */}
          <div className={styles.pagination}>
            <Button
              size="small"
              disabled={pagination.skip === 0}
              onClick={() => setPagination(prev => ({ ...prev, skip: Math.max(0, prev.skip - prev.limit) }))}
            >
              ← Anterior
            </Button>
            <span>
              {pagination.skip + 1} - {Math.min(pagination.skip + pagination.limit, entities.length + pagination.skip)}
            </span>
            <Button
              size="small"
              disabled={entities.length < pagination.limit}
              onClick={() => setPagination(prev => ({ ...prev, skip: prev.skip + prev.limit }))}
            >
              Próximo →
            </Button>
          </div>
        </div>

        {/* Right Panel - Details/Form */}
        <div className={styles.rightPanel}>
          {isCreating ? renderCreateForm() : renderEntityDetails()}
        </div>
      </div>
    </div>
  )
}

export default CrudManager