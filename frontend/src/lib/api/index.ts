// 🌐 MIT Logistics Frontend - API Index

// Re-export all API functions and clients
export * from './client'
export * from './gatekeeper'
export * from './graphql'

// Main API client instances
export { 
  apiClient, 
  gatekeeperClient, 
  ollamaClient,
  graphqlQuery,
  checkServiceHealth,
  uploadFile
} from './client'

// Gatekeeper API
export {
  authenticateUser,
  getRolesAndPermissions,
  getGatekeeperInfo,
  getGatekeeperHealth,
  testAuthentication,
  runAuthenticationTests,
  sendMessageToAgent,
  startGatekeeperMonitoring,
  TEST_USERS
} from './gatekeeper'

// GraphQL API  
export {
  getCtes,
  getCteByNumber,
  getContainers,
  getContainerByNumber,
  getContainersInTransit,
  getBls,
  getBlByNumber,
  getLogisticsStats,
  updateCteStatus,
  updateContainerPosition,
  searchCtes,
  searchContainers,
  getGraphQLHealth,
  subscribeToContainerUpdates,
  QUERIES,
  MUTATIONS
} from './graphql'
import { checkServiceHealth } from './client'

// === COMBINED API FUNCTIONS === //

/**
 * Get complete system health status
 */
export async function getSystemHealth() {
  const [gatekeeperHealth, graphqlHealth] = await Promise.allSettled([
    checkServiceHealth('gatekeeper'),
    checkServiceHealth('api')
  ])

  return {
    gatekeeper: gatekeeperHealth.status === 'fulfilled' ? gatekeeperHealth.value : {
      service: 'gatekeeper',
      status: 'unhealthy',
      error: gatekeeperHealth.reason?.message || 'Unknown error'
    },
    graphql: graphqlHealth.status === 'fulfilled' ? graphqlHealth.value : {
      service: 'api', 
      status: 'unhealthy',
      error: graphqlHealth.reason?.message || 'Unknown error'
    },
    overall: gatekeeperHealth.status === 'fulfilled' && graphqlHealth.status === 'fulfilled' ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString()
  }
}

/**
 * Initialize API monitoring for all services
 */
export function startSystemMonitoring(
  onUpdate: (status: any) => void,
  interval: number = 30000
): () => void {
  const checkSystemHealth = async () => {
    try {
      const health = await getSystemHealth()
      onUpdate({
        type: 'system_health',
        data: health,
        timestamp: new Date().toISOString()
      })
    } catch (error) {
      onUpdate({
        type: 'system_error',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      })
    }
  }

  // Initial check
  checkSystemHealth()

  // Set up interval
  const intervalId = setInterval(checkSystemHealth, interval)

  // Return cleanup function
  return () => clearInterval(intervalId)
}