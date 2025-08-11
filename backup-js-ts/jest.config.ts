import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  
  // Padrões para encontrar arquivos de teste
  testMatch: [
    '**/tests/**/*.test.ts',
    '**/tests/**/*.spec.ts'
  ],
  
  // Diretórios a serem ignorados
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/coverage/',
    '**/*.js'
  ],
  
  // Configuração de cobertura
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/index.ts',
    '!node_modules/**',
    '!tests/**'
  ],
  
  // Diretório de saída da cobertura
  coverageDirectory: 'coverage',
  
  // Formatos de relatório de cobertura
  coverageReporters: [
    'text',
    'html',
    'lcov',
    'json-summary'
  ],
  
  // Limite mínimo de cobertura
  coverageThreshold: {
    global: {
      branches: 65,
      functions: 75,
      lines: 75,
      statements: 75
    }
  },
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  
  // Timeout para testes (importante para testes com LLM)
  testTimeout: 30000,
  
  // Configurações de verbose
  verbose: false,
  
  // Configurações de cache
  clearMocks: true,
  restoreMocks: true,
  
  // Módulos e transformações
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  
  // Configuração do ts-jest
  globals: {
    'ts-jest': {
      useESM: true,
      tsconfig: {
        module: 'ESNext'
      }
    }
  },
  
  // Transformações
  transform: {
    '^.+\\.ts$': ['ts-jest', {
      useESM: true
    }]
  },
  
  // Resolver módulos
  moduleFileExtensions: ['ts', 'js', 'json']
};

export default config;