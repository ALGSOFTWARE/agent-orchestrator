'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import styles from '@/styles/pages/ApiExplorer.module.css'

interface QueryExample {
  name: string
  description: string
  query: string
  variables?: string
}

const QUERY_EXAMPLES: QueryExample[] = [
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

export default function ApiExplorerPage() {
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
    
    // Simular delay de API
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Mock response baseado na query
    let mockResponse = {}
    
    if (query.includes('ctes')) {
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
        <p>Explore as APIs GraphQL do MIT Logistics</p>
      </div>

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
  )
}