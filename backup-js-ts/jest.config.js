export default {
  testEnvironment: 'node',
  
  // Padrões para encontrar arquivos de teste
  testMatch: [
    '**/tests/**/*.test.js',
    '**/tests/**/*.spec.js'
  ],
  
  // Diretórios a serem ignorados
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/coverage/'
  ],
  
  // Configuração de cobertura
  collectCoverageFrom: [
    '*.js',
    'agents/**/*.js',
    '!node_modules/**',
    '!tests/**',
    '!test-interaction.js',
    '!jest.config.js'
  ],
  
  // Diretório de saída da cobertura
  coverageDirectory: 'coverage',
  
  // Formatos de relatório de cobertura
  coverageReporters: [
    'text',
    'html',
    'lcov'
  ],
  
  // Limite mínimo de cobertura
  coverageThreshold: {
    global: {
      branches: 60,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  
  // Timeout para testes (importante para testes com LLM)
  testTimeout: 30000,
  
  // Configurações de verbose
  verbose: false,
  
  // Configurações de cache
  clearMocks: true,
  restoreMocks: true,
  
  // Suporte para ES modules
  transform: {}
};