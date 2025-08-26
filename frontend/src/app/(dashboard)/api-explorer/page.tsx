'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { CrudManager } from '@/components/features/CrudManager'
import styles from '@/styles/pages/ApiExplorer.module.css'

interface QueryExample {
  name: string
  description: string
  query: string
  variables?: string
}

const QUERY_EXAMPLES: QueryExample[] = [
  {
    name: 'Database Stats',
    description: 'Estatísticas em tempo real do banco MongoDB',
    query: `query {
  databaseStats {
    users
    clients
    containers
    shipments
    trackingEvents
    contexts
    activeUsers
    timestamp
  }
}`
  },
  {
    name: 'Listar Usuários',
    description: 'Lista usuários do sistema com paginação',
    query: `query GetUsers($limit: Int, $skip: Int, $role: String) {
  users(limit: $limit, skip: $skip, role: $role) {
    id
    name
    email
    role
    client
    isActive
    createdAt
    lastLogin
    loginCount
  }
}`,
    variables: `{
  "limit": 10,
  "skip": 0,
  "role": "logistics"
}`
  },
  {
    name: 'Listar Containers',
    description: 'Lista containers do banco com status e localização',
    query: `query GetContainers($limit: Int, $status: String) {
  containersDb(limit: $limit, status: $status) {
    id
    containerNumber
    type
    currentStatus
    location
    createdAt
    updatedAt
  }
}`,
    variables: `{
  "limit": 20,
  "status": "in_transit"
}`
  },
  {
    name: 'Listar CT-es',
    description: 'Busca todos os Conhecimentos de Transporte Eletrônico',
    query: `query {
  ctes {
    numero_cte
    status
    transportadora {
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
    valor_total
    previsao_entrega
  }
}`
  },
  {
    name: 'Buscar Container',
    description: 'Informações detalhadas de um container específico',
    query: `query GetContainer($numero: String!) {
  container(numero: $numero) {
    numero
    status
    localizacao_atual {
      latitude
      longitude
      endereco
    }
    temperatura_atual
    historico_localizacoes {
      timestamp
      latitude
      longitude
      evento
    }
  }
}`,
    variables: `{
  "numero": "ABCD1234567"
}`
  },
  {
    name: 'Listar Transportadoras',
    description: 'Todas as empresas transportadoras cadastradas',
    query: `query {
  transportadoras {
    nome
    cnpj
    frota_total
    especializacoes
    certificacoes
    contato {
      telefone
      email
    }
  }
}`
  },
  {
    name: 'Listar Clientes',
    description: 'Lista clientes com informações completas',
    query: `query GetClients($limit: Int) {
  clients(limit: $limit) {
    id
    name
    cnpj
    address
    contacts
    createdAt
  }
}`,
    variables: `{
  "limit": 15
}`
  },
  {
    name: 'Tracking Events',
    description: 'Eventos de rastreamento por container ou shipment',
    query: `query GetTrackingEvents($limit: Int, $type: String) {
  trackingEvents(limit: $limit, type: $type) {
    id
    containerId
    shipmentId
    type
    description
    timestamp
    location
    source
  }
}`,
    variables: `{
  "limit": 25,
  "type": "arrival"
}`
  },
  {
    name: 'Listar Embarques',
    description: 'Lista shipments com relacionamentos',
    query: `query GetShipments($limit: Int, $status: String) {
  shipments(limit: $limit, status: $status) {
    id
    clientId
    containerIds
    status
    departurePort
    arrivalPort
    etd
    eta
    deliveryDate
    createdAt
  }
}`,
    variables: `{
  "limit": 20,
  "status": "in_transit"
}`
  },
  {
    name: 'Criar Usuário (Mutation)',
    description: 'Exemplo de mutation para criar novo usuário',
    query: `mutation CreateUser($userInput: UserInput!) {
  createUser(userInput: $userInput) {
    id
    name
    email
    role
    isActive
    createdAt
    loginCount
  }
}`,
    variables: `{
  "userInput": {
    "name": "João Silva",
    "email": "joao@exemplo.com",
    "role": "operator"
  }
}`
  },
  {
    name: 'Criar Container (Mutation)',
    description: 'Exemplo de mutation para criar novo container',
    query: `mutation CreateContainer($containerInput: ContainerDBInput!) {
  createContainerDb(containerInput: $containerInput) {
    id
    containerNumber
    type
    currentStatus
    location
    createdAt
    updatedAt
  }
}`,
    variables: `{
  "containerInput": {
    "containerNumber": "TEST123456",
    "type": "40HC",
    "currentStatus": "available",
    "location": "{\\"port\\": \\"Santos\\", \\"coordinates\\": [-23.95, -46.33]}"
  }
}`
  },
  {
    name: 'Bill of Lading',
    description: 'Buscar um conhecimento de embarque marítimo',
    query: `query GetBL($numero: String!) {
  bl(numero: $numero) {
    numero_bl
    status
    armador {
      nome
      iata_code
    }
    porto_origem {
      nome
      pais
    }
    porto_destino {
      nome
      pais
    }
    containers
    eta_destino
  }
}`,
    variables: `{
  "numero": "ABCD240001"
}`
  }
]

type ExplorerTab = 'graphql' | 'crud'

export default function ApiExplorerPage() {
  const [activeTab, setActiveTab] = useState<ExplorerTab>('graphql')
  const [selectedExample, setSelectedExample] = useState<QueryExample>(QUERY_EXAMPLES[0]!)
  const [query, setQuery] = useState(QUERY_EXAMPLES[0]!.query)
  const [variables, setVariables] = useState(QUERY_EXAMPLES[0]!.variables || '{}')
  const [response, setResponse] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleExampleSelect = (example: QueryExample) => {
    setSelectedExample(example)
    setQuery(example.query)
    setVariables(example.variables || '{}')
    setResponse('')
  }

  const executeQuery = async () => {
    setIsLoading(true)
    
    try {
      // Tentar executar query real no GraphQL
      const graphqlEndpoint = 'http://localhost:8000/graphql'
      
      const response = await fetch(graphqlEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          variables: variables ? JSON.parse(variables) : undefined
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        setResponse(JSON.stringify(result, null, 2))
        setIsLoading(false)
        return
      } else {
        // Se falhar, usar dados mockados como fallback
        console.warn('GraphQL API não disponível, usando dados mockados')
      }
    } catch (error) {
      console.warn('Erro ao conectar com GraphQL API, usando dados mockados:', error)
    }
    
    // Fallback para dados mockados
    await new Promise(resolve => setTimeout(resolve, 1000))
    let mockResponse = {}
    
    if (query.includes('databaseStats')) {
      mockResponse = {
        data: {
          databaseStats: {
            users: 50,
            clients: 30,
            containers: 40,
            shipments: 35,
            trackingEvents: 150,
            contexts: 100,
            activeUsers: 37,
            timestamp: new Date().toISOString()
          }
        }
      }
    } else if (query.includes('users')) {
      mockResponse = {
        data: {
          users: [
            {
              id: "68a35ffee00a7b046febebfb",
              name: "Sra. Marina Sá",
              email: "zabreu@example.net", 
              role: "logistics",
              client: "68a35ffde00a7b046febebe8",
              isActive: true,
              createdAt: "2025-06-01T02:16:11.016Z",
              lastLogin: "2025-08-06T15:31:02.275Z",
              loginCount: 37
            },
            {
              id: "68a35ffee00a7b046febebfe",
              name: "Dra. Alexia Cunha",
              email: "rda-luz@example.org",
              role: "finance",
              client: "68a35ffde00a7b046febebf2",
              isActive: true,
              createdAt: "2025-06-06T09:52:06.585Z",
              lastLogin: null,
              loginCount: 104
            }
          ]
        }
      }
    } else if (query.includes('containersDb')) {
      mockResponse = {
        data: {
          containersDb: [
            {
              id: "68a36000e00a7b046febec2d",
              containerNumber: "RBHC3078575",
              type: "40RF",
              currentStatus: "loaded",
              location: JSON.stringify({
                lat: -22.832746744490496,
                lng: -43.21228208069578,
                portCode: "BRRIO",
                address: "Terminal 6, Rio de Janeiro/RJ"
              }),
              createdAt: "2024-09-30T20:38:36.438Z",
              updatedAt: "2025-08-18T08:27:25.572Z"
            },
            {
              id: "68a36000e00a7b046febec2e",
              containerNumber: "IPUU7453404",
              type: "45HC",
              currentStatus: "damage_inspection",
              location: null,
              createdAt: "2025-03-26T05:08:25.871Z",
              updatedAt: "2025-08-17T22:20:37.758Z"
            }
          ]
        }
      }
    } else if (query.includes('clients')) {
      mockResponse = {
        data: {
          clients: [
            {
              id: "68a35ffde00a7b046febebdd",
              name: "SeaPort Cargo Solutions",
              cnpj: "09.144.001/6994-80",
              address: "Condomínio de Freitas\nVila Novo São Lucas\n93158222 Pereira / AP",
              contacts: [
                JSON.stringify({
                  name: "Hellena Santos",
                  email: "afogaca@example.org",
                  phone: "(051) 9981 2890",
                  role: "coordinator"
                })
              ],
              createdAt: "2025-07-19T23:10:08.665Z"
            }
          ]
        }
      }
    } else if (query.includes('trackingEvents')) {
      mockResponse = {
        data: {
          trackingEvents: [
            {
              id: "68a36002e00a7b046febec78",
              containerId: "68a36000e00a7b046febec36",
              shipmentId: null,
              type: "delayed",
              description: "Congestionamento portuário - nova ETA em análise",
              timestamp: "2025-08-18T14:15:53.817Z",
              location: null,
              source: "system"
            }
          ]
        }
      }
    } else if (query.includes('shipments')) {
      mockResponse = {
        data: {
          shipments: [
            {
              id: "68a36001e00a7b046febec5a",
              clientId: "68a35ffde00a7b046febebdd",
              containerIds: ["68a36000e00a7b046febec2d"],
              status: "in_transit",
              departurePort: "Santos",
              arrivalPort: "Hamburg",
              etd: "2025-08-10T09:00:00Z",
              eta: "2025-09-15T14:00:00Z",
              deliveryDate: null,
              createdAt: "2025-08-01T10:30:00Z"
            }
          ]
        }
      }
    } else if (query.includes('createUser')) {
      mockResponse = {
        data: {
          createUser: {
            id: `user_${Date.now()}`,
            name: "João Silva",
            email: "joao@exemplo.com",
            role: "operator",
            isActive: true,
            createdAt: new Date().toISOString(),
            loginCount: 0
          }
        }
      }
    } else if (query.includes('createContainerDb')) {
      mockResponse = {
        data: {
          createContainerDb: {
            id: `container_${Date.now()}`,
            containerNumber: "TEST123456",
            type: "40HC",
            currentStatus: "available",
            location: JSON.stringify({port: "Santos", coordinates: [-23.95, -46.33]}),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        }
      }
    } else if (query.includes('ctes')) {
      mockResponse = {
        data: {
          ctes: [
            {
              numero_cte: '35240512345678901234567890123456789012',
              status: 'EM_TRANSITO',
              transportadora: {
                nome: 'Rápido Express Ltda',
                cnpj: '12.345.678/0001-90'
              },
              origem: {
                municipio: 'São Paulo',
                uf: 'SP'
              },
              destino: {
                municipio: 'Rio de Janeiro',
                uf: 'RJ'
              },
              valor_total: 2500.00,
              previsao_entrega: '2024-08-20T18:00:00Z'
            },
            {
              numero_cte: '35240612345678901234567890123456789013',
              status: 'ENTREGUE',
              transportadora: {
                nome: 'Logística Sul',
                cnpj: '98.765.432/0001-10'
              },
              origem: {
                municipio: 'Porto Alegre',
                uf: 'RS'
              },
              destino: {
                municipio: 'Curitiba',
                uf: 'PR'
              },
              valor_total: 1800.00,
              previsao_entrega: '2024-08-15T14:30:00Z'
            }
          ]
        }
      }
    } else if (query.includes('container')) {
      mockResponse = {
        data: {
          container: {
            numero: 'ABCD1234567',
            status: 'EM_TRANSITO',
            localizacao_atual: {
              latitude: -23.5505,
              longitude: -46.6333,
              endereco: 'Porto de Santos, SP'
            },
            temperatura_atual: 18.5,
            historico_localizacoes: [
              {
                timestamp: '2024-08-18T10:00:00Z',
                latitude: -23.5505,
                longitude: -46.6333,
                evento: 'Saída do Porto de Santos'
              },
              {
                timestamp: '2024-08-17T15:30:00Z',
                latitude: -23.5505,
                longitude: -46.6333,
                evento: 'Chegada ao Porto de Santos'
              }
            ]
          }
        }
      }
    } else if (query.includes('transportadoras')) {
      mockResponse = {
        data: {
          transportadoras: [
            {
              nome: 'Rápido Express Ltda',
              cnpj: '12.345.678/0001-90',
              frota_total: 250,
              especializacoes: ['Carga Seca', 'Refrigerada', 'Perigosa'],
              certificacoes: ['ISO 9001', 'PBQP-H', 'OEA'],
              contato: {
                telefone: '+55 11 3333-4444',
                email: 'operacoes@rapidoexpress.com.br'
              }
            },
            {
              nome: 'Logística Sul',
              cnpj: '98.765.432/0001-10',
              frota_total: 120,
              especializacoes: ['Carga Geral', 'Mudanças'],
              certificacoes: ['ISO 14001', 'SASSMAQ'],
              contato: {
                telefone: '+55 51 2222-3333',
                email: 'contato@logisticasul.com.br'
              }
            }
          ]
        }
      }
    } else if (query.includes('bl')) {
      mockResponse = {
        data: {
          bl: {
            numero_bl: 'ABCD240001',
            status: 'EM_TRANSITO',
            armador: {
              nome: 'Maersk Line',
              iata_code: 'MAEU'
            },
            porto_origem: {
              nome: 'Porto de Santos',
              pais: 'Brasil'
            },
            porto_destino: {
              nome: 'Puerto de Buenos Aires',
              pais: 'Argentina'
            },
            containers: ['MSKU1234567', 'MSKU1234568'],
            eta_destino: '2024-08-25T08:00:00Z'
          }
        }
      }
    } else {
      mockResponse = {
        data: null,
        errors: [
          {
            message: 'Query não reconhecida no sistema mock',
            extensions: {
              code: 'MOCK_ERROR'
            }
          }
        ]
      }
    }
    
    setResponse(JSON.stringify(mockResponse, null, 2))
    setIsLoading(false)
  }

  return (
    <div className={styles.apiExplorer}>
      <div className={styles.header}>
        <h1>🔍 API Explorer</h1>
        <p>Explore as APIs GraphQL e CRUD do MIT Logistics</p>
      </div>

      {/* Tab Navigation */}
      <div className={styles.tabNavigation}>
        <button
          className={`${styles.tab} ${activeTab === 'graphql' ? styles.active : ''}`}
          onClick={() => setActiveTab('graphql')}
        >
          📊 GraphQL Playground
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'crud' ? styles.active : ''}`}
          onClick={() => setActiveTab('crud')}
        >
          🗄️ CRUD Manager
        </button>
      </div>

      {activeTab === 'graphql' ? (
        <div className={styles.content}>
        {/* Examples Sidebar */}
        <div className={styles.sidebar}>
          <h3>📚 Exemplos de Queries</h3>
          <div className={styles.examples}>
            {QUERY_EXAMPLES.map((example) => (
              <div
                key={example.name}
                className={`${styles.exampleItem} ${
                  selectedExample.name === example.name ? styles.active : ''
                }`}
                onClick={() => handleExampleSelect(example)}
              >
                <h4>{example.name}</h4>
                <p>{example.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Playground */}
        <div className={styles.playground}>
          <div className={styles.querySection}>
            <div className={styles.inputGroup}>
              <label htmlFor="query">GraphQL Query</label>
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className={styles.queryInput}
                rows={15}
                placeholder="Digite sua query GraphQL aqui..."
              />
            </div>

            <div className={styles.inputGroup}>
              <label htmlFor="variables">Variables (JSON)</label>
              <textarea
                id="variables"
                value={variables}
                onChange={(e) => setVariables(e.target.value)}
                className={styles.variablesInput}
                rows={5}
                placeholder='{"variavel": "valor"}'
              />
            </div>

            <Button
              onClick={executeQuery}
              isLoading={isLoading}
              className={styles.executeButton}
              leftIcon="▶️"
            >
              Executar Query
            </Button>
          </div>

          <div className={styles.responseSection}>
            <h3>📊 Resposta</h3>
            <Card className={styles.responseCard}>
              {response ? (
                <pre className={styles.responseContent}>{response}</pre>
              ) : (
                <div className={styles.emptyResponse}>
                  <p>👆 Execute uma query para ver a resposta aqui</p>
                </div>
              )}
            </Card>
          </div>
        </div>
        
        {/* Documentation */}
        <div className={styles.documentation}>
          <Card>
            <h3>📋 Documentação da API</h3>
            <div className={styles.docContent}>
              <h4>🔗 Endpoints Disponíveis:</h4>
              <ul>
                <li><strong>GraphQL:</strong> http://localhost:8001/graphql</li>
                <li><strong>REST API:</strong> http://localhost:8001/api/</li>
                <li><strong>Health Check:</strong> http://localhost:8001/health</li>
              </ul>

              <h4>📊 Tipos de Dados:</h4>
              <ul>
                <li><strong>CTe:</strong> Conhecimento de Transporte Eletrônico</li>
                <li><strong>Container:</strong> Informações de rastreamento</li>
                <li><strong>BL:</strong> Bill of Lading (conhecimento de embarque)</li>
                <li><strong>Transportadora:</strong> Empresas de transporte</li>
                <li><strong>Viagem:</strong> Rotas multi-modais</li>
              </ul>

              <h4>⚠️ Nota sobre Mock:</h4>
              <p>
                Este playground está usando dados mockados. Para conectar com a API real, 
                certifique-se de que o backend esteja rodando em http://localhost:8001
              </p>
            </div>
          </Card>
        </div>
        </div>
      ) : (
        <CrudManager className={styles.crudSection || ''} />
      )}
    </div>
  )
}