// 📊 MIT Logistics Frontend - GraphQL API

import { graphqlQuery, apiClient } from './client'
import { 
  type CTe, 
  type Container, 
  type BL, 
  type PaginatedResponse 
} from '@/types'

// === GRAPHQL QUERIES === //

// Basic GraphQL queries for the logistics system
export const QUERIES = {
  // Get all CT-e documents
  GET_CTES: `
    query GetCtes($limit: Int, $offset: Int) {
      ctes(limit: $limit, offset: $offset) {
        id
        numero_cte
        status
        data_emissao
        transportadora {
          id
          nome
          cnpj
        }
        origem {
          municipio
          uf
        }
        destino {
          municipio
          uf
        }
        valor_frete
        peso_bruto
        containers
        previsao_entrega
        observacoes
      }
    }
  `,

  // Get specific CT-e by number
  GET_CTE_BY_NUMBER: `
    query GetCteByNumber($numero: String!) {
      cteByNumber(numero: $numero) {
        id
        numero_cte
        status
        data_emissao
        transportadora {
          id
          nome
          cnpj
          email
          telefone
        }
        origem {
          logradouro
          numero
          bairro
          municipio
          uf
          cep
        }
        destino {
          logradouro
          numero
          bairro
          municipio
          uf
          cep
        }
        valor_frete
        peso_bruto
        containers
        previsao_entrega
        observacoes
      }
    }
  `,

  // Get all containers
  GET_CONTAINERS: `
    query GetContainers($limit: Int, $offset: Int) {
      containers(limit: $limit, offset: $offset) {
        id
        numero
        tipo
        status
        posicao_atual {
          latitude
          longitude
          timestamp
          endereco
        }
        temperatura_atual
        cte_associado
        peso_bruto
        observacoes
      }
    }
  `,

  // Get container by number with tracking history
  GET_CONTAINER_BY_NUMBER: `
    query GetContainerByNumber($numero: String!) {
      containerByNumber(numero: $numero) {
        id
        numero
        tipo
        status
        posicao_atual {
          latitude
          longitude
          timestamp
          endereco
          velocidade
          precisao
        }
        temperatura_atual
        historico_posicoes {
          latitude
          longitude
          timestamp
          endereco
          velocidade
        }
        cte_associado
        peso_bruto
        observacoes
      }
    }
  `,

  // Get containers in transit
  GET_CONTAINERS_IN_TRANSIT: `
    query GetContainersInTransit {
      containersEmTransito {
        id
        numero
        tipo
        status
        posicao_atual {
          latitude
          longitude
          timestamp
          endereco
        }
        temperatura_atual
        cte_associado
      }
    }
  `,

  // Get all BL documents
  GET_BLS: `
    query GetBls($limit: Int, $offset: Int) {
      bls(limit: $limit, offset: $offset) {
        id
        numero_bl
        status
        data_embarque
        porto_origem
        porto_destino
        navio
        containers
        peso_total
        valor_mercadorias
        eta_destino
        observacoes
      }
    }
  `,

  // Get BL by number
  GET_BL_BY_NUMBER: `
    query GetBlByNumber($numero: String!) {
      blByNumber(numero: $numero) {
        id
        numero_bl
        status
        data_embarque
        porto_origem
        porto_destino
        navio
        containers
        peso_total
        valor_mercadorias
        eta_destino
        observacoes
      }
    }
  `,

  // Get logistics statistics
  GET_LOGISTICS_STATS: `
    query GetLogisticsStats {
      logisticsStats {
        total_ctes
        total_containers
        containers_em_transito
        valor_total_fretes
        containers_por_status {
          status
          count
        }
        ctes_por_status {
          status
          count
        }
      }
    }
  `
}

// === MUTATIONS === //
export const MUTATIONS = {
  // Create new CT-e
  CREATE_CTE: `
    mutation CreateCte($cteInput: CteInput!) {
      createCte(cteInput: $cteInput) {
        id
        numero_cte
        status
        data_emissao
      }
    }
  `,

  // Update CT-e status
  UPDATE_CTE_STATUS: `
    mutation UpdateCteStatus($numero: String!, $novo_status: String!) {
      updateCteStatus(numero: $numero, novo_status: $novo_status) {
        numero_cte
        status
      }
    }
  `,

  // Update container position
  UPDATE_CONTAINER_POSITION: `
    mutation UpdateContainerPosition($numero: String!, $posicao: PosicaoInput!) {
      updateContainerPosition(numero: $numero, posicao: $posicao) {
        numero
        posicao_atual {
          latitude
          longitude
          timestamp
          endereco
        }
      }
    }
  `,

  // Create new container
  CREATE_CONTAINER: `
    mutation CreateContainer($containerInput: ContainerInput!) {
      createContainer(containerInput: $containerInput) {
        id
        numero
        tipo
        status
      }
    }
  `
}

// === API FUNCTIONS === //

/**
 * Get all CT-e documents with pagination
 */
export async function getCtes(limit?: number, offset?: number): Promise<CTe[]> {
  const data = await graphqlQuery<{ ctes: CTe[] }>(
    QUERIES.GET_CTES,
    { limit, offset }
  )
  return data.ctes
}

/**
 * Get specific CT-e by number
 */
export async function getCteByNumber(numero: string): Promise<CTe | null> {
  try {
    const data = await graphqlQuery<{ cteByNumber: CTe }>(
      QUERIES.GET_CTE_BY_NUMBER,
      { numero }
    )
    return data.cteByNumber
  } catch (error) {
    if (error instanceof Error && error.message.includes('not found')) {
      return null
    }
    throw error
  }
}

/**
 * Get all containers with pagination
 */
export async function getContainers(limit?: number, offset?: number): Promise<Container[]> {
  const data = await graphqlQuery<{ containers: Container[] }>(
    QUERIES.GET_CONTAINERS,
    { limit, offset }
  )
  return data.containers
}

/**
 * Get specific container by number with full tracking history
 */
export async function getContainerByNumber(numero: string): Promise<Container | null> {
  try {
    const data = await graphqlQuery<{ containerByNumber: Container }>(
      QUERIES.GET_CONTAINER_BY_NUMBER,
      { numero }
    )
    return data.containerByNumber
  } catch (error) {
    if (error instanceof Error && error.message.includes('not found')) {
      return null
    }
    throw error
  }
}

/**
 * Get containers currently in transit
 */
export async function getContainersInTransit(): Promise<Container[]> {
  const data = await graphqlQuery<{ containersEmTransito: Container[] }>(
    QUERIES.GET_CONTAINERS_IN_TRANSIT
  )
  return data.containersEmTransito
}

/**
 * Get all BL documents with pagination
 */
export async function getBls(limit?: number, offset?: number): Promise<BL[]> {
  const data = await graphqlQuery<{ bls: BL[] }>(
    QUERIES.GET_BLS,
    { limit, offset }
  )
  return data.bls
}

/**
 * Get specific BL by number
 */
export async function getBlByNumber(numero: string): Promise<BL | null> {
  try {
    const data = await graphqlQuery<{ blByNumber: BL }>(
      QUERIES.GET_BL_BY_NUMBER,
      { numero }
    )
    return data.blByNumber
  } catch (error) {
    if (error instanceof Error && error.message.includes('not found')) {
      return null
    }
    throw error
  }
}

/**
 * Get logistics dashboard statistics
 */
export async function getLogisticsStats() {
  const data = await graphqlQuery<{ 
    logisticsStats: {
      total_ctes: number
      total_containers: number
      containers_em_transito: number
      valor_total_fretes: number
      containers_por_status: Array<{ status: string; count: number }>
      ctes_por_status: Array<{ status: string; count: number }>
    }
  }>(QUERIES.GET_LOGISTICS_STATS)
  
  return data.logisticsStats
}

/**
 * Update CT-e status
 */
export async function updateCteStatus(numero: string, novo_status: string) {
  const data = await graphqlQuery<{ 
    updateCteStatus: { numero_cte: string; status: string }
  }>(MUTATIONS.UPDATE_CTE_STATUS, { numero, novo_status })
  
  return data.updateCteStatus
}

/**
 * Update container position
 */
export async function updateContainerPosition(
  numero: string, 
  posicao: { latitude: number; longitude: number; endereco?: string }
) {
  const data = await graphqlQuery<{
    updateContainerPosition: Container
  }>(MUTATIONS.UPDATE_CONTAINER_POSITION, { numero, posicao })
  
  return data.updateContainerPosition
}

// === SEARCH FUNCTIONS === //

/**
 * Search CT-e documents by various criteria
 */
export async function searchCtes(query: string): Promise<CTe[]> {
  // For now, get all CTes and filter client-side
  // In a real implementation, this would be a server-side search
  const allCtes = await getCtes()
  
  const lowercaseQuery = query.toLowerCase()
  
  return allCtes.filter(cte => 
    cte.numero_cte.toLowerCase().includes(lowercaseQuery) ||
    cte.transportadora.nome.toLowerCase().includes(lowercaseQuery) ||
    cte.origem.municipio.toLowerCase().includes(lowercaseQuery) ||
    cte.destino.municipio.toLowerCase().includes(lowercaseQuery) ||
    cte.status.toLowerCase().includes(lowercaseQuery)
  )
}

/**
 * Search containers by various criteria
 */
export async function searchContainers(query: string): Promise<Container[]> {
  const allContainers = await getContainers()
  
  const lowercaseQuery = query.toLowerCase()
  
  return allContainers.filter(container =>
    container.numero.toLowerCase().includes(lowercaseQuery) ||
    container.tipo.toLowerCase().includes(lowercaseQuery) ||
    container.status.toLowerCase().includes(lowercaseQuery) ||
    (container.cte_associado && container.cte_associado.toLowerCase().includes(lowercaseQuery))
  )
}

// === HEALTH CHECK === //

/**
 * Check GraphQL API health
 */
export async function getGraphQLHealth() {
  try {
    const response = await apiClient.getRaw<{
      status: string
      database: any
      mit_agent: any
    }>('/health')
    
    return {
      ...response,
      healthy: response.status === 'healthy'
    }
  } catch (error) {
    return {
      status: 'unhealthy',
      healthy: false,
      error: error instanceof Error ? error.message : 'Connection failed',
      timestamp: new Date().toISOString()
    }
  }
}

// === REAL-TIME SUBSCRIPTIONS (Future) === //

/**
 * Subscribe to real-time container position updates
 * This would use WebSockets in a real implementation
 */
export function subscribeToContainerUpdates(
  containerId: string,
  onUpdate: (container: Container) => void
): () => void {
  // Simulate real-time updates for now
  const interval = setInterval(async () => {
    try {
      const container = await getContainerByNumber(containerId)
      if (container) {
        onUpdate(container)
      }
    } catch (error) {
      console.error('Error fetching container updates:', error)
    }
  }, 30000) // Check every 30 seconds
  
  // Return cleanup function
  return () => clearInterval(interval)
}

// === EXPORTS === //
export default {
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
}