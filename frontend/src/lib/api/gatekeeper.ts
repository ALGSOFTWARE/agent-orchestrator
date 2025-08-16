// 🚪 MIT Logistics Frontend - Gatekeeper API

import { gatekeeperClient } from './client'
import { 
  type AuthPayload, 
  type GatekeeperResponse, 
  type UserRole 
} from '@/types'

// === GATEKEEPER API FUNCTIONS === //

/**
 * Simulate authentication callback to Gatekeeper
 */
export async function authenticateUser(payload: AuthPayload): Promise<GatekeeperResponse> {
  try {
    const response = await gatekeeperClient.postRaw<GatekeeperResponse>(
      '/auth-callback',
      payload
    )
    return response
  } catch (error) {
    // Handle specific Gatekeeper errors
    if (error && typeof error === 'object' && 'code' in error) {
      const apiError = error as { code: number; message: string }
      
      if (apiError.code === 403) {
        throw new Error('Acesso negado: Role ou permissões inválidas')
      } else if (apiError.code === 422) {
        throw new Error('Dados de autenticação inválidos')
      }
    }
    
    throw new Error('Erro na autenticação com Gatekeeper')
  }
}

/**
 * Get available roles and their permissions
 */
export async function getRolesAndPermissions() {
  try {
    const response = await gatekeeperClient.getRaw<{
      available_roles: UserRole[]
      role_permissions: Record<UserRole, string[]>
    }>('/roles')
    
    return response
  } catch (error) {
    throw new Error('Erro ao obter roles disponíveis')
  }
}

/**
 * Get Gatekeeper system information
 */
export async function getGatekeeperInfo() {
  try {
    const response = await gatekeeperClient.getRaw<{
      service: string
      version: string
      description: string
      supported_roles: UserRole[]
      agent_mapping: Record<string, string>
      endpoints: string[]
    }>('/info')
    
    return response
  } catch (error) {
    throw new Error('Erro ao obter informações do Gatekeeper')
  }
}

/**
 * Check Gatekeeper health status
 */
export async function getGatekeeperHealth() {
  try {
    const response = await gatekeeperClient.getRaw<{
      status: string
      service: string
      timestamp: string
      version: string
    }>('/health')
    
    return {
      ...response,
      healthy: response.status === 'healthy'
    }
  } catch (error) {
    return {
      status: 'unhealthy',
      service: 'Gatekeeper Agent',
      timestamp: new Date().toISOString(),
      version: 'unknown',
      healthy: false,
      error: error instanceof Error ? error.message : 'Connection failed'
    }
  }
}

// === PREDEFINED TEST SCENARIOS === //

export const TEST_USERS = {
  admin: {
    userId: 'admin_001',
    role: 'admin' as UserRole,
    permissions: ['*'],
    sessionId: 'admin_session_001'
  },
  logistics: {
    userId: 'logistics_002',
    role: 'logistics' as UserRole,
    permissions: ['read:cte', 'write:document', 'read:container', 'write:tracking'],
    sessionId: 'logistics_session_002'
  },
  finance: {
    userId: 'finance_003',
    role: 'finance' as UserRole,
    permissions: ['read:financial', 'write:financial', 'read:payment', 'write:payment'],
    sessionId: 'finance_session_003'
  },
  operator: {
    userId: 'operator_004',
    role: 'operator' as UserRole,
    permissions: ['read:cte', 'write:document', 'read:container'],
    sessionId: 'operator_session_004'
  },
  invalid: {
    userId: 'invalid_005',
    role: 'logistics' as UserRole,
    permissions: ['read:financial', 'write:admin'], // Invalid permissions for logistics
    sessionId: 'invalid_session_005'
  }
}

/**
 * Quick test authentication with predefined user
 */
export async function testAuthentication(userType: keyof typeof TEST_USERS): Promise<GatekeeperResponse> {
  const userData = TEST_USERS[userType]
  const payload: AuthPayload = {
    ...userData,
    timestamp: new Date().toISOString()
  }
  
  return authenticateUser(payload)
}

/**
 * Test all predefined users and return results
 */
export async function runAuthenticationTests() {
  const results: Record<string, { success: boolean; response?: GatekeeperResponse; error?: string }> = {}
  
  for (const [userType, userData] of Object.entries(TEST_USERS)) {
    try {
      const response = await testAuthentication(userType as keyof typeof TEST_USERS)
      results[userType] = { success: true, response }
    } catch (error) {
      results[userType] = { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      }
    }
  }
  
  return results
}

// === AGENT COMMUNICATION HELPERS === //

/**
 * Send message to specific agent through authenticated session
 */
export async function sendMessageToAgent(
  userContext: AuthPayload,
  message: string,
  attachments?: File[]
): Promise<any> {
  // First authenticate user
  const authResponse = await authenticateUser(userContext)
  
  if (authResponse.status !== 'success') {
    throw new Error('Authentication failed')
  }
  
  // Extract agent info from auth response
  const agentName = authResponse.agent
  if (!agentName) {
    throw new Error('No agent assigned to user')
  }
  
  // Prepare message payload
  const messagePayload = {
    userContext: authResponse.data?.user_context,
    message,
    timestamp: new Date().toISOString(),
    attachments: attachments ? attachments.map(f => ({ name: f.name, size: f.size, type: f.type })) : []
  }
  
  // For now, simulate agent response (until we have direct agent endpoints)
  // In a real implementation, this would call the specific agent
  return {
    agent: agentName,
    response: `${agentName} processed: "${message}"`,
    timestamp: new Date().toISOString(),
    userContext: authResponse.data?.user_context
  }
}

// === REAL-TIME MONITORING === //

/**
 * Start monitoring Gatekeeper status
 */
export function startGatekeeperMonitoring(
  onUpdate: (status: any) => void,
  interval: number = 30000
): () => void {
  const checkStatus = async () => {
    try {
      const health = await getGatekeeperHealth()
      onUpdate({
        type: 'health',
        data: health,
        timestamp: new Date().toISOString()
      })
    } catch (error) {
      onUpdate({
        type: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      })
    }
  }
  
  // Initial check
  checkStatus()
  
  // Set up interval
  const intervalId = setInterval(checkStatus, interval)
  
  // Return cleanup function
  return () => clearInterval(intervalId)
}

// === EXPORTS === //
export default {
  authenticateUser,
  getRolesAndPermissions,
  getGatekeeperInfo,
  getGatekeeperHealth,
  testAuthentication,
  runAuthenticationTests,
  sendMessageToAgent,
  startGatekeeperMonitoring,
  TEST_USERS
}