# 🧪 MIT Tracking - Guia de Testes

Este documento detalha a estrutura de testes do projeto MIT Tracking Agent.

## 📁 Estrutura de Testes

```
tests/
├── unit/                          # Testes unitários
│   ├── mitTrackingAgent.test.js    # Testes do agente principal
│   ├── interactive-interface.test.js # Testes da interface
│   └── smoke.test.js              # Testes básicos de smoke
├── integration/                    # Testes de integração
│   └── ollama-connection.test.js   # Testes de conexão Ollama
├── mocks/                         # Mocks e utilitários
│   └── ollama-mock.js             # Mock do ChatOllama
├── setup.js                       # Configuração global dos testes
└── .env.test                      # Variáveis de ambiente para testes
```

## 🚀 Executando os Testes

### Comandos Básicos

```bash
# Todos os testes
npm test

# Com cobertura de código
npm run test:coverage

# Modo watch (re-executa ao modificar arquivos)
npm run test:watch

# Saída detalhada
npm run test:verbose
```

### Executar Categorias Específicas

```bash
# Apenas testes unitários
npm test tests/unit

# Apenas testes de integração
npm test tests/integration

# Teste específico
npm test tests/unit/mitTrackingAgent.test.js
```

## 📊 Tipos de Teste

### 1. Testes Unitários

**Arquivo**: `tests/unit/mitTrackingAgent.test.js`
- ✅ Inicialização do agente
- ✅ Consultas sobre CT-e
- ✅ Consultas sobre BL (Bill of Lading)
- ✅ Status de containers
- ✅ Consultas ETA/ETD
- ✅ Gerenciamento de histórico
- ✅ Tratamento de erros
- ✅ Performance e limites

**Cobertura**: 18 testes, ~90% de cobertura de código

### 2. Testes de Interface

**Arquivo**: `tests/unit/interactive-interface.test.js`
- ✅ Comandos especiais (`/menu`, `/sair`, `/limpar`)
- ✅ Processamento de consultas normais
- ✅ Formatação de saída
- ✅ Tratamento de entrada de usuário
- ✅ Integração com agente

**Cobertura**: 25 testes, interface completamente testada

### 3. Testes de Integração

**Arquivo**: `tests/integration/ollama-connection.test.js`
- ✅ Conexão com servidor Ollama
- ✅ Respostas em português
- ✅ Consultas específicas de logística
- ✅ Performance e timeouts
- ✅ Tratamento de erros de conexão

**Nota**: Requer Ollama rodando localmente

### 4. Smoke Tests

**Arquivo**: `tests/unit/smoke.test.js`
- ✅ Importação de módulos
- ✅ Configurações de ambiente
- ✅ Estrutura do projeto
- ✅ Mocks e utilidades
- ✅ Performance básica

## 🎭 Sistema de Mocks

### ChatOllama Mock

O projeto usa um mock completo do ChatOllama que:
- Simula respostas realistas baseadas na entrada
- Mantém histórico de chamadas
- Simula delays realistas (100ms)
- Suporta diferentes tipos de consulta

**Respostas Mock Disponíveis**:
- `cteConsulta`: Para consultas sobre CT-e
- `blConsulta`: Para consultas sobre BL
- `containerStatus`: Para status de containers
- `etaConsulta`: Para consultas ETA/ETD

### Exemplo de Uso do Mock

```javascript
import { MockChatOllama, MockHumanMessage } from '../mocks/ollama-mock.js';

const mockLLM = new MockChatOllama({ model: 'test' });
const response = await mockLLM.invoke([
  new MockHumanMessage('Como consultar CT-e?')
]);
```

## ⚙️ Configuração

### Variables de Ambiente de Teste

**.env.test**:
```bash
NODE_ENV=test
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
MOCK_LLM_RESPONSES=true
LOG_LEVEL=error
```

### Jest Configuration

**jest.config.js**:
- Suporte para ES modules
- Timeout de 30s para testes com LLM
- Cobertura de código configurada
- Setup automático de mocks

## 📈 Métricas de Cobertura

### Metas de Cobertura

- **Lines**: 70%
- **Functions**: 70%
- **Branches**: 60%
- **Statements**: 70%

### Arquivos Cobertos

- `*.js` (arquivos raiz)
- `agents/**/*.js`
- Exclusões: `node_modules`, `tests`, `jest.config.js`

## 🔧 Troubleshooting

### Problemas Comuns

**1. Testes de Integração Falhando**
```bash
# Verificar se Ollama está rodando
ollama serve

# Verificar modelos disponíveis  
ollama list
```

**2. ES Modules Issues**
```bash
# Os testes usam experimental VM modules
node --experimental-vm-modules node_modules/jest/bin/jest.js
```

**3. Timeout em Testes**
```bash
# Aumentar timeout no jest.config.js
testTimeout: 45000  // 45 segundos
```

### Logs de Debug

Para debug detalhado:
```bash
# Habilitar logs verbosos
export VERBOSE_LOGS=true
npm run test:verbose
```

## 🚀 Adicionando Novos Testes

### Template de Teste Unitário

```javascript
import { jest } from '@jest/globals';
import { MockChatOllama } from '../mocks/ollama-mock.js';

describe('Nome do Componente', () => {
  let component;

  beforeEach(() => {
    component = new Component();
  });

  test('deve fazer algo específico', () => {
    // Arrange
    const input = 'test input';
    
    // Act
    const result = component.method(input);
    
    // Assert
    expect(result).toBe('expected output');
  });
});
```

### Boas Práticas

1. **Um teste = um comportamento específico**
2. **Nomes descritivos** ("deve fazer X quando Y")
3. **Arrange-Act-Assert** pattern
4. **Mocks para dependências externas**
5. **Cleanup em afterEach/beforeEach**

## 📊 Relatório de Cobertura

Para gerar relatório detalhado:
```bash
npm run test:coverage
```

O relatório é gerado em `coverage/lcov-report/index.html`