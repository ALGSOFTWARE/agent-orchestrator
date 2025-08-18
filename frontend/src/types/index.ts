// 🔧 MIT Logistics Frontend - TypeScript Definitions

// === GATEKEEPER & AUTHENTICATION === //
export interface AuthPayload {
  userId: string
  role: UserRole
  permissions: string[]
  sessionId?: string
  timestamp?: string
}

export type UserRole = 'admin' | 'logistics' | 'finance' | 'operator'
export type AgentType = 'mit-tracking' | 'gatekeeper' | 'customs' | 'financial'

export interface GatekeeperResponse {
  status: 'success' | 'error'
  agent?: string
  message: string
  userId?: string
  timestamp: string
  data?: {
    agent_response: AgentResponse
    user_context: UserContext
    routing_success: boolean
  }
}

export interface UserContext {
  userId: string
  role: string
  permissions: string[]
  sessionId?: string
  timestamp: string
}

// === AGENTS === //
export interface AgentResponse {
  agent: string
  status: 'success' | 'error'
  response: string
  capabilities?: string[]
  specialization?: string
  error?: string
}

export interface AgentCapability {
  id: string
  name: string
  description: string
  permissions: string[]
}

export interface AgentInfo {
  name: string
  type: 'AdminAgent' | 'LogisticsAgent' | 'FinanceAgent'
  description: string
  capabilities: AgentCapability[]
  icon: string
  color: string
}

// === CHAT & MESSAGES === //
export interface ChatMessage {
  id: string
  role: 'user' | 'agent'
  content: string
  timestamp: string
  agent?: string
  attachments?: FileAttachment[]
  metadata?: Record<string, unknown>
}

export interface ChatSession {
  id: string
  userId: string
  agentType: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
  status: 'active' | 'ended'
}

export interface FileAttachment {
  id: string
  name: string
  type: string
  size: number
  url: string
  uploadedAt: string
}

// === MONITORING & METRICS === //
export interface ServiceStatus {
  name: string
  status: 'healthy' | 'unhealthy' | 'degraded'
  url: string
  responseTime?: number
  lastCheck: string
  details?: Record<string, unknown>
}

export interface SystemMetrics {
  timestamp: string
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_io: {
    bytes_sent: number
    bytes_received: number
  }
  active_connections: number
  requests_per_minute: number
  error_rate: number
}

export interface LogEntry {
  id: string
  timestamp: string
  level: 'info' | 'warn' | 'error' | 'debug'
  source: string
  message: string
  metadata?: Record<string, unknown>
}

// === AGENT TESTING === //
export interface AgentTestResult {
  status: 'success' | 'error'
  responseTime: number
  agentType: AgentType
  confidence?: number
  tokensUsed?: number
  error?: string
  metadata?: Record<string, unknown>
}

// === API EXPLORER === //
export interface GraphQLQuery {
  id: string
  name: string
  query: string
  variables?: Record<string, unknown>
  description?: string
  tags?: string[]
}

export interface RESTEndpoint {
  id: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  path: string
  description: string
  parameters?: Parameter[]
  requestBody?: RequestBody
  responses?: Response[]
  tags?: string[]
}

export interface Parameter {
  name: string
  in: 'query' | 'path' | 'header' | 'cookie'
  required: boolean
  type: string
  description?: string
  example?: unknown
}

export interface RequestBody {
  contentType: string
  schema: Record<string, unknown>
  example?: unknown
}

export interface Response {
  status: number
  description: string
  contentType?: string
  schema?: Record<string, unknown>
  example?: unknown
}

// === UI & COMPONENTS === //
export interface ToastMessage {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  description?: string
  duration?: number
}

export interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
}

export interface TableColumn<T> {
  key: keyof T
  title: string
  width?: string
  render?: (value: T[keyof T], record: T) => React.ReactNode
  sortable?: boolean
}

export interface PaginationInfo {
  current: number
  pageSize: number
  total: number
  totalPages: number
}

// === LOGISTICS DOMAIN === //
export interface CTe {
  id: string
  numero_cte: string
  status: string
  data_emissao: string
  transportadora: Transportadora
  origem: Endereco
  destino: Endereco
  valor_frete: number
  peso_bruto: number
  containers: string[]
  previsao_entrega?: string
  observacoes?: string
}

export interface Container {
  id: string
  numero: string
  tipo: string
  status: string
  posicao_atual?: PosicaoGPS
  temperatura_atual?: number
  historico_posicoes: PosicaoGPS[]
  cte_associado?: string
  peso_bruto?: number
  observacoes?: string
}

export interface BL {
  id: string
  numero_bl: string
  status: string
  data_embarque: string
  porto_origem: string
  porto_destino: string
  navio: string
  containers: string[]
  peso_total: number
  valor_mercadorias: number
  eta_destino?: string
  observacoes?: string
}

export interface Transportadora {
  id: string
  nome: string
  cnpj: string
  email?: string
  telefone?: string
}

export interface Endereco {
  logradouro: string
  numero: string
  complemento?: string
  bairro: string
  municipio: string
  uf: string
  cep: string
  pais: string
}

export interface PosicaoGPS {
  latitude: number
  longitude: number
  timestamp: string
  endereco?: string
  velocidade?: number
  precisao?: number
}

// === STORE TYPES === //
export interface AppStore {
  // Auth state
  user: UserContext | null
  isAuthenticated: boolean
  setUser: (user: UserContext | null) => void
  logout: () => void
  
  // UI state
  theme: 'light' | 'dark'
  toggleTheme: () => void
  sidebarCollapsed: boolean
  toggleSidebar: () => void
  
  // Chat state
  activeChatSession: ChatSession | null
  chatHistory: ChatSession[]
  setActiveChatSession: (session: ChatSession | null) => void
  addChatSession: (session: ChatSession) => void
  updateChatSession: (sessionId: string, updates: Partial<ChatSession>) => void
  
  // Monitoring state
  services: ServiceStatus[]
  metrics: SystemMetrics[]
  logs: LogEntry[]
  updateServiceStatus: (service: ServiceStatus) => void
  addMetrics: (metrics: SystemMetrics) => void
  addLog: (log: LogEntry) => void
  
  // Toast state
  toasts: ToastMessage[]
  addToast: (toast: Omit<ToastMessage, 'id'>) => void
  removeToast: (id: string) => void
}

// === API RESPONSE TYPES === //
export interface ApiResponse<T = unknown> {
  data: T
  message?: string
  status: 'success' | 'error'
  timestamp: string
}

export interface ApiError {
  code: number
  message: string
  details?: string
  timestamp: string
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: PaginationInfo
  message?: string
  status: 'success' | 'error'
  timestamp: string
}

// === FORM TYPES === //
export interface LoginForm {
  userId: string
  role: UserRole
  permissions: string[]
}

export interface ChatMessageForm {
  message: string
  attachments?: File[]
}

export interface TestScenarioForm {
  name: string
  description: string
  steps: TestStep[]
}

export interface TestStep {
  id: string
  type: 'auth' | 'message' | 'upload' | 'assertion'
  description: string
  data: Record<string, unknown>
  expectedResult?: Record<string, unknown>
}

// === UTILITY TYPES === //
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export type Prettify<T> = {
  [K in keyof T]: T[K]
} & {}

export type NonEmptyArray<T> = [T, ...T[]]

export type ValueOf<T> = T[keyof T]

export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

export type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>