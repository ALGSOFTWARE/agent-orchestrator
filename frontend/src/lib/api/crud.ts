// 🗄️ MIT Logistics Frontend - CRUD API Client

import { gatekeeperClient } from './client'

// === TYPESCRIPT TYPES === //
export interface User {
  _id: string
  name: string
  email: string
  role: 'admin' | 'logistics' | 'finance' | 'operator'
  client?: { id: string; collection: string } | null
  is_active: boolean
  created_at: string
  last_login?: string | null
  login_count: number
}

export interface Client {
  _id: string
  name: string
  cnpj?: string | null
  address?: string | null
  contacts: any[]
  created_at: string
}

export interface Container {
  _id: string
  container_number: string
  type?: string | null
  current_status: string
  location?: any | null
  created_at: string
  updated_at: string
}

export interface Shipment {
  _id: string
  client: { id: string; collection: string }
  containers: { id: string; collection: string }[]
  status: string
  departure_port?: string | null
  arrival_port?: string | null
  etd?: string | null
  eta?: string | null
  delivery_date?: string | null
  created_at: string
}

export interface TrackingEvent {
  _id: string
  container?: { id: string; collection: string } | null
  shipment?: { id: string; collection: string } | null
  type: string
  description?: string | null
  timestamp: string
  location?: any | null
  source: string
}

export interface Context {
  _id: string
  user_id: string
  session_id?: string | null
  input: string
  output: string
  agents_involved: string[]
  timestamp: string
  metadata?: any
  response_time?: number | null
}

export interface DatabaseStats {
  users: number
  clients: number
  containers: number
  shipments: number
  tracking_events: number
  contexts: number
  active_users: number
  timestamp: string
}

// Request types for creating/updating
export interface CreateUserRequest {
  name: string
  email: string
  role: 'admin' | 'logistics' | 'finance' | 'operator'
  client_id?: string
}

export interface CreateClientRequest {
  name: string
  cnpj?: string
  address?: string
  contacts?: any[]
}

export interface CreateContainerRequest {
  container_number: string
  type?: string
  current_status: string
  location?: any
}

export interface CreateShipmentRequest {
  client_id: string
  container_ids?: string[]
  status?: string
  departure_port?: string
  arrival_port?: string
  etd?: string
  eta?: string
}

export interface CreateTrackingEventRequest {
  container_id?: string
  shipment_id?: string
  type: string
  description?: string
  location?: any
  source?: string
}

export interface CreateContextRequest {
  user_id: string
  session_id?: string
  input: string
  output: string
  agents_involved?: string[]
  metadata?: any
  response_time?: number
}

// === CRUD API FUNCTIONS === //

// === USERS === //
export async function getUsers(params?: {
  skip?: number
  limit?: number
  role?: string
  active_only?: boolean
}): Promise<User[]> {
  try {
    const searchParams = new URLSearchParams()
    if (params?.skip) searchParams.set('skip', params.skip.toString())
    if (params?.limit) searchParams.set('limit', params.limit.toString())
    if (params?.role) searchParams.set('role', params.role)
    if (params?.active_only !== undefined) searchParams.set('active_only', params.active_only.toString())

    const url = `/api/crud/users?${searchParams}`
    console.log('🔄 Chamando API users:', url)
    const result = await gatekeeperClient.getRaw<User[]>(url)
    console.log('✅ Resposta da API users:', result?.length || 0, 'usuários')
    return result
  } catch (error) {
    console.error('❌ Erro na API users:', error)
    throw error
  }
}

export async function getUser(userId: string): Promise<User> {
  return gatekeeperClient.getRaw<User>(`/api/crud/users/${userId}`)
}

export async function createUser(data: CreateUserRequest): Promise<User> {
  return gatekeeperClient.postRaw<User>('/api/crud/users', data)
}

export async function updateUser(userId: string, data: Partial<CreateUserRequest>): Promise<User> {
  return gatekeeperClient.putRaw<User>(`/api/crud/users/${userId}`, data)
}

export async function deleteUser(userId: string, softDelete: boolean = true): Promise<void> {
  const searchParams = new URLSearchParams()
  searchParams.set('soft_delete', softDelete.toString())
  return gatekeeperClient.deleteRaw(`/api/crud/users/${userId}?${searchParams}`)
}

// === CLIENTS === //
export async function getClients(params?: {
  skip?: number
  limit?: number
}): Promise<Client[]> {
  const searchParams = new URLSearchParams()
  if (params?.skip) searchParams.set('skip', params.skip.toString())
  if (params?.limit) searchParams.set('limit', params.limit.toString())

  return gatekeeperClient.getRaw<Client[]>(`/api/crud/clients?${searchParams}`)
}

export async function getClient(clientId: string): Promise<Client> {
  return gatekeeperClient.getRaw<Client>(`/api/crud/clients/${clientId}`)
}

export async function createClient(data: CreateClientRequest): Promise<Client> {
  return gatekeeperClient.postRaw<Client>('/api/crud/clients', data)
}

export async function updateClient(clientId: string, data: Partial<CreateClientRequest>): Promise<Client> {
  return gatekeeperClient.putRaw<Client>(`/api/crud/clients/${clientId}`, data)
}

export async function deleteClient(clientId: string): Promise<void> {
  return gatekeeperClient.deleteRaw(`/api/crud/clients/${clientId}`)
}

// === CONTAINERS === //
export async function getContainers(params?: {
  skip?: number
  limit?: number
  status?: string
}): Promise<Container[]> {
  const searchParams = new URLSearchParams()
  if (params?.skip) searchParams.set('skip', params.skip.toString())
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.status) searchParams.set('status', params.status)

  return gatekeeperClient.getRaw<Container[]>(`/api/crud/containers?${searchParams}`)
}

export async function getContainer(containerId: string): Promise<Container> {
  return gatekeeperClient.getRaw<Container>(`/api/crud/containers/${containerId}`)
}

export async function createContainer(data: CreateContainerRequest): Promise<Container> {
  return gatekeeperClient.postRaw<Container>('/api/crud/containers', data)
}

export async function updateContainer(containerId: string, data: Partial<CreateContainerRequest>): Promise<Container> {
  return gatekeeperClient.putRaw<Container>(`/api/crud/containers/${containerId}`, data)
}

export async function deleteContainer(containerId: string): Promise<void> {
  return gatekeeperClient.deleteRaw(`/api/crud/containers/${containerId}`)
}

// === SHIPMENTS === //
export async function getShipments(params?: {
  skip?: number
  limit?: number
  status?: string
  client_id?: string
}): Promise<Shipment[]> {
  const searchParams = new URLSearchParams()
  if (params?.skip) searchParams.set('skip', params.skip.toString())
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.status) searchParams.set('status', params.status)
  if (params?.client_id) searchParams.set('client_id', params.client_id)

  return gatekeeperClient.getRaw<Shipment[]>(`/api/crud/shipments?${searchParams}`)
}

export async function getShipment(shipmentId: string): Promise<Shipment> {
  return gatekeeperClient.getRaw<Shipment>(`/api/crud/shipments/${shipmentId}`)
}

export async function createShipment(data: CreateShipmentRequest): Promise<Shipment> {
  return gatekeeperClient.postRaw<Shipment>('/api/crud/shipments', data)
}

export async function updateShipment(shipmentId: string, data: Partial<CreateShipmentRequest>): Promise<Shipment> {
  return gatekeeperClient.putRaw<Shipment>(`/api/crud/shipments/${shipmentId}`, data)
}

export async function deleteShipment(shipmentId: string): Promise<void> {
  return gatekeeperClient.deleteRaw(`/api/crud/shipments/${shipmentId}`)
}

// === TRACKING EVENTS === //
export async function getTrackingEvents(params?: {
  skip?: number
  limit?: number
  type?: string
  container_id?: string
  shipment_id?: string
}): Promise<TrackingEvent[]> {
  const searchParams = new URLSearchParams()
  if (params?.skip) searchParams.set('skip', params.skip.toString())
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.type) searchParams.set('type', params.type)
  if (params?.container_id) searchParams.set('container_id', params.container_id)
  if (params?.shipment_id) searchParams.set('shipment_id', params.shipment_id)

  return gatekeeperClient.getRaw<TrackingEvent[]>(`/api/crud/tracking-events?${searchParams}`)
}

export async function getTrackingEvent(eventId: string): Promise<TrackingEvent> {
  return gatekeeperClient.getRaw<TrackingEvent>(`/api/crud/tracking-events/${eventId}`)
}

export async function createTrackingEvent(data: CreateTrackingEventRequest): Promise<TrackingEvent> {
  return gatekeeperClient.postRaw<TrackingEvent>('/api/crud/tracking-events', data)
}

export async function updateTrackingEvent(eventId: string, data: Partial<CreateTrackingEventRequest>): Promise<TrackingEvent> {
  return gatekeeperClient.putRaw<TrackingEvent>(`/api/crud/tracking-events/${eventId}`, data)
}

export async function deleteTrackingEvent(eventId: string): Promise<void> {
  return gatekeeperClient.deleteRaw(`/api/crud/tracking-events/${eventId}`)
}

// === CONTEXTS === //
export async function getContexts(params?: {
  skip?: number
  limit?: number
  user_id?: string
  session_id?: string
}): Promise<Context[]> {
  const searchParams = new URLSearchParams()
  if (params?.skip) searchParams.set('skip', params.skip.toString())
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.user_id) searchParams.set('user_id', params.user_id)
  if (params?.session_id) searchParams.set('session_id', params.session_id)

  return gatekeeperClient.getRaw<Context[]>(`/api/crud/contexts?${searchParams}`)
}

export async function getContext(contextId: string): Promise<Context> {
  return gatekeeperClient.getRaw<Context>(`/api/crud/contexts/${contextId}`)
}

export async function createContext(data: CreateContextRequest): Promise<Context> {
  return gatekeeperClient.postRaw<Context>('/api/crud/contexts', data)
}

export async function updateContext(contextId: string, data: Partial<CreateContextRequest>): Promise<Context> {
  return gatekeeperClient.putRaw<Context>(`/api/crud/contexts/${contextId}`, data)
}

export async function deleteContext(contextId: string): Promise<void> {
  return gatekeeperClient.deleteRaw(`/api/crud/contexts/${contextId}`)
}

// === STATISTICS === //
export async function getDatabaseStats(): Promise<DatabaseStats> {
  try {
    console.log('🔄 Chamando API CRUD stats...')
    const result = await gatekeeperClient.getRaw<DatabaseStats>('/api/crud/stats')
    console.log('✅ Resposta da API stats:', result)
    return result
  } catch (error) {
    console.error('❌ Erro na API stats:', error)
    throw error
  }
}

// === BULK OPERATIONS === //
export async function bulkDelete(filters: any): Promise<any> {
  return gatekeeperClient.postRaw('/api/crud/bulk-delete', filters)
}

// === EXPORT === //
export default {
  users: {
    getAll: getUsers,
    getById: getUser,
    create: createUser,
    update: updateUser,
    delete: deleteUser
  },
  clients: {
    getAll: getClients,
    getById: getClient,
    create: createClient,
    update: updateClient,
    delete: deleteClient
  },
  containers: {
    getAll: getContainers,
    getById: getContainer,
    create: createContainer,
    update: updateContainer,
    delete: deleteContainer
  },
  shipments: {
    getAll: getShipments,
    getById: getShipment,
    create: createShipment,
    update: updateShipment,
    delete: deleteShipment
  },
  trackingEvents: {
    getAll: getTrackingEvents,
    getById: getTrackingEvent,
    create: createTrackingEvent,
    update: updateTrackingEvent,
    delete: deleteTrackingEvent
  },
  contexts: {
    getAll: getContexts,
    getById: getContext,
    create: createContext,
    update: updateContext,
    delete: deleteContext
  },
  stats: getDatabaseStats,
  bulkDelete
}