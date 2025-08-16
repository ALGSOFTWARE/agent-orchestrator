"""
Exemplos de uso da MIT Tracking GraphQL API
Queries e Mutations para demonstração
"""

# GraphQL Queries Examples

EXAMPLE_QUERIES = {
    "basic": {
        "title": "Query básica - Listar CT-e",
        "query": """
        query {
          ctes {
            id
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
            valor_frete
            previsao_entrega
          }
        }
        """,
        "description": "Lista todos os CT-e com informações básicas"
    },
    
    "specific_cte": {
        "title": "Buscar CT-e específico",
        "query": """
        query {
          cteByNumber(numero: "35240512345678901234567890123456789012") {
            id
            numero_cte
            status
            data_emissao
            transportadora {
              nome
              cnpj
              telefone
            }
            containers
            observacoes
          }
        }
        """,
        "description": "Busca CT-e por número específico"
    },
    
    "containers_tracking": {
        "title": "Rastreamento de Containers",
        "query": """
        query {
          containers {
            id
            numero
            status
            tipo
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
        """,
        "description": "Lista containers com posição GPS atual"
    },
    
    "container_history": {
        "title": "Histórico de Container",
        "query": """
        query {
          containerByNumber(numero: "ABCD1234567") {
            id
            numero
            status
            historico_posicoes {
              latitude
              longitude
              timestamp
              velocidade
              endereco
            }
          }
        }
        """,
        "description": "Busca container com histórico completo de posições"
    },
    
    "bls_maritime": {
        "title": "Bills of Lading Marítimos",
        "query": """
        query {
          bls {
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
          }
        }
        """,
        "description": "Lista conhecimentos de embarque marítimo"
    },
    
    "containers_in_transit": {
        "title": "Containers em Trânsito",
        "query": """
        query {
          containersEmTransito {
            numero
            status
            posicao_atual {
              latitude
              longitude
              endereco
            }
            cte_associado
          }
        }
        """,
        "description": "Containers atualmente em trânsito"
    },
    
    "logistics_dashboard": {
        "title": "Dashboard Logístico",
        "query": """
        query {
          logisticsStats {
            total_ctes
            total_containers
            total_bls
            containers_em_transito
            ctes_entregues
            valor_total_fretes
          }
        }
        """,
        "description": "Estatísticas gerais para dashboard"
    }
}

EXAMPLE_MUTATIONS = {
    "create_cte": {
        "title": "Criar novo CT-e",
        "mutation": """
        mutation {
          createCte(cteInput: {
            numero_cte: "35240812345678901234567890123456789999"
            status: "EM_TRANSITO"
            transportadora: {
              nome: "Nova Transportadora Ltda"
              cnpj: "12345678000199"
              telefone: "(11) 99999-9999"
            }
            origem: {
              municipio: "São Paulo"
              uf: "SP"
              cep: "01000-000"
            }
            destino: {
              municipio: "Rio de Janeiro"  
              uf: "RJ"
              cep: "20000-000"
            }
            valor_frete: 1500.00
            peso_bruto: 2500.50
            containers: ["NOVO1234567"]
          }) {
            id
            numero_cte
            status
            transportadora {
              nome
            }
          }
        }
        """,
        "description": "Cria novo CT-e no sistema"
    },
    
    "update_container_position": {
        "title": "Atualizar Posição de Container",
        "mutation": """
        mutation {
          updateContainerPosition(
            numero: "ABCD1234567"
            posicao: {
              latitude: -23.5505
              longitude: -46.6333
              velocidade: 80.5
              endereco: "Rodovia Presidente Dutra, Km 150"
            }
          ) {
            numero
            status
            posicao_atual {
              latitude
              longitude
              timestamp
              endereco
            }
          }
        }
        """,
        "description": "Atualiza posição GPS de um container"
    },
    
    "update_cte_status": {
        "title": "Atualizar Status CT-e",
        "mutation": """
        mutation {
          updateCteStatus(
            numero: "35240512345678901234567890123456789012"
            novo_status: "ENTREGUE"
          ) {
            numero_cte
            status
          }
        }
        """,
        "description": "Atualiza status de entrega de um CT-e"
    }
}

# REST API Examples (compatibilidade)
REST_EXAMPLES = {
    "list_ctes": {
        "method": "GET",
        "url": "/api/v1/ctes",
        "description": "Lista CT-e via REST",
        "curl": "curl -X GET http://localhost:8000/api/v1/ctes"
    },
    
    "list_containers": {
        "method": "GET", 
        "url": "/api/v1/containers",
        "description": "Lista containers via REST",
        "curl": "curl -X GET http://localhost:8000/api/v1/containers"
    },
    
    "health_check": {
        "method": "GET",
        "url": "/health",
        "description": "Verificar saúde da API",
        "curl": "curl -X GET http://localhost:8000/health"
    }
}

# Python Client Examples
PYTHON_CLIENT_EXAMPLES = """
# Exemplo de cliente Python para GraphQL API

import requests
import json

# Configuração
API_URL = "http://localhost:8000/graphql"
headers = {"Content-Type": "application/json"}

# Query básica
def list_ctes():
    query = '''
    query {
      ctes {
        numero_cte
        status
        transportadora { nome }
      }
    }
    '''
    
    response = requests.post(
        API_URL,
        json={"query": query},
        headers=headers
    )
    
    return response.json()

# Busca específica
def get_container(numero):
    query = '''
    query GetContainer($numero: String!) {
      containerByNumber(numero: $numero) {
        numero
        status
        posicao_atual {
          latitude
          longitude
          endereco
        }
      }
    }
    '''
    
    response = requests.post(
        API_URL,
        json={
            "query": query,
            "variables": {"numero": numero}
        },
        headers=headers
    )
    
    return response.json()

# Mutation - atualizar posição
def update_position(numero, lat, lng):
    mutation = '''
    mutation UpdatePosition($numero: String!, $lat: Float!, $lng: Float!) {
      updateContainerPosition(
        numero: $numero
        posicao: {
          latitude: $lat
          longitude: $lng
        }
      ) {
        numero
        posicao_atual {
          latitude
          longitude
          timestamp
        }
      }
    }
    '''
    
    response = requests.post(
        API_URL,
        json={
            "query": mutation,
            "variables": {
                "numero": numero,
                "lat": lat, 
                "lng": lng
            }
        },
        headers=headers
    )
    
    return response.json()

# Uso
if __name__ == "__main__":
    # Listar CT-e
    ctes = list_ctes()
    print("CT-e:", json.dumps(ctes, indent=2))
    
    # Buscar container
    container = get_container("ABCD1234567")
    print("Container:", json.dumps(container, indent=2))
    
    # Atualizar posição
    result = update_position("ABCD1234567", -23.5505, -46.6333)
    print("Atualização:", json.dumps(result, indent=2))
"""

# JavaScript Client Examples  
JAVASCRIPT_CLIENT_EXAMPLES = """
// Exemplo de cliente JavaScript para GraphQL API

const API_URL = 'http://localhost:8000/graphql';

// Função helper para GraphQL
async function graphqlRequest(query, variables = {}) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      variables,
    }),
  });
  
  return response.json();
}

// Listar CT-e
async function listCtes() {
  const query = `
    query {
      ctes {
        numero_cte
        status
        transportadora { nome }
        origem { municipio, uf }
        destino { municipio, uf }
        valor_frete
      }
    }
  `;
  
  const result = await graphqlRequest(query);
  return result.data.ctes;
}

// Buscar container específico
async function getContainer(numero) {
  const query = `
    query GetContainer($numero: String!) {
      containerByNumber(numero: $numero) {
        numero
        status
        tipo
        posicao_atual {
          latitude
          longitude
          timestamp
          endereco
        }
        temperatura_atual
      }
    }
  `;
  
  const result = await graphqlRequest(query, { numero });
  return result.data.containerByNumber;
}

// Atualizar posição de container
async function updateContainerPosition(numero, latitude, longitude, endereco) {
  const mutation = `
    mutation UpdatePosition($numero: String!, $posicao: PosicaoGPSInput!) {
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
  `;
  
  const variables = {
    numero,
    posicao: {
      latitude,
      longitude,
      endereco
    }
  };
  
  const result = await graphqlRequest(mutation, variables);
  return result.data.updateContainerPosition;
}

// Uso
async function exemplo() {
  try {
    // Listar CT-e
    const ctes = await listCtes();
    console.log('CT-e:', ctes);
    
    // Buscar container
    const container = await getContainer('ABCD1234567');
    console.log('Container:', container);
    
    // Atualizar posição
    const updated = await updateContainerPosition(
      'ABCD1234567',
      -23.5505,
      -46.6333,
      'São Paulo, SP'
    );
    console.log('Posição atualizada:', updated);
    
  } catch (error) {
    console.error('Erro:', error);
  }
}

exemplo();
"""


def get_all_examples():
    """Retorna todos os exemplos organizados"""
    return {
        "graphql_queries": EXAMPLE_QUERIES,
        "graphql_mutations": EXAMPLE_MUTATIONS,
        "rest_endpoints": REST_EXAMPLES,
        "python_client": PYTHON_CLIENT_EXAMPLES,
        "javascript_client": JAVASCRIPT_CLIENT_EXAMPLES
    }