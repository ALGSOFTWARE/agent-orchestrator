#!/usr/bin/env tsx

import dotenv from 'dotenv';
import { InterfaceInterativa } from '@/utils/InterfaceInterativa';

// Carrega variáveis de ambiente
dotenv.config();

// Tratamento para encerramento gracioso
process.on('SIGINT', () => {
  console.log('\n\n👋 Programa encerrado pelo usuário. Até logo!');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n\n👋 Programa encerrado. Até logo!');
  process.exit(0);
});

async function main(): Promise<void> {
  try {
    const interfaceChat = new InterfaceInterativa();
    
    // Event listeners para melhor monitoramento
    interfaceChat.on('commandProcessed', (result) => {
      if (process.env.NODE_ENV === 'development') {
        console.log(`[DEBUG] Comando processado: ${result.tipo}`);
      }
    });

    interfaceChat.on('error', (error) => {
      console.error('[ERRO] Erro na interface:', error.message);
    });

    interfaceChat.on('exit', () => {
      console.log('[INFO] Interface encerrada');
    });

    await interfaceChat.iniciar();
  } catch (error) {
    console.error('❌ Erro ao executar o agente MIT Tracking:', error instanceof Error ? error.message : error);
    
    if (error instanceof Error && (error.message.includes('ECONNREFUSED') || error.message.includes('fetch'))) {
      console.log('\n🔧 Possíveis soluções:');
      console.log('1. Verifique se o Ollama está rodando: ollama serve');
      console.log('2. Confirme se o modelo llama3.2:3b está disponível: ollama list');
      console.log('3. Teste a conexão: curl http://localhost:11434/api/tags');
    }
    
    process.exit(1);
  }
}

// Executa o programa
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error('Erro fatal:', error);
    process.exit(1);
  });
}