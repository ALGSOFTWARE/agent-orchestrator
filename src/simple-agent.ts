#!/usr/bin/env tsx

import dotenv from 'dotenv';
import { MITTrackingAgent } from '@/agents/MITTrackingAgent';
import type { LogisticsQuery, DocumentType } from '@/types';

// Carrega variáveis de ambiente
dotenv.config();

async function main(): Promise<void> {
  try {
    console.log('🚀 Iniciando MIT Tracking - Agente Conversacional de Logística...\n');

    const agent = new MITTrackingAgent();
    
    console.log('✅ Agente MIT Tracking inicializado com sucesso!');
    console.log('🎯 Especialização: Consultas de CT-e, rastreamento de containers e logística\n');
    
    // Consulta de demonstração tipada
    const consultaDemo: LogisticsQuery = {
      content: `Preciso consultar o status do meu CT-e número 351234567890123456789012345678901234. 
                Onde posso encontrar informações sobre esta carga e qual o ETA previsto?
                         
                Forneça uma resposta profissional e técnica, explicando:
                1. Como consultar CT-e no sistema MIT Tracking
                2. Tipos de informações disponíveis 
                3. Como interpretar status de carga
                4. Processo para obter ETA/ETD atualizados`,
      type: 'CTE' as DocumentType,
      documentNumber: '351234567890123456789012345678901234',
      timestamp: new Date()
    };

    console.log('📋 Executando consulta de demonstração sobre CT-e...\n');
    
    const agentResponse = await agent.processLogisticsQuery(consultaDemo);
    
    console.log('🎯 Resposta do Assistente MIT Tracking:');
    console.log('='.repeat(50));
    console.log(agentResponse.content);
    console.log('='.repeat(50));
    
    console.log(`\n📊 Métricas da consulta:`);
    console.log(`   • Tempo de resposta: ${agentResponse.responseTime}ms`);
    console.log(`   • Confiança: ${(agentResponse.confidence * 100).toFixed(1)}%`);
    console.log(`   • Fontes: ${agentResponse.sources?.join(', ') || 'N/A'}`);
    
    console.log('\n✅ Demonstração concluída com sucesso!');
    console.log('🔄 O agente está pronto para consultas de CT-e, BL, containers e logística.');

    // Exemplos de consultas interativas
    console.log('\n📝 Exemplos de consultas que você pode fazer:');
    console.log('- "Onde está o meu BL?"');
    console.log('- "Me mostre o CT-e da carga X"');
    console.log('- "Qual o status da minha entrega?"');
    console.log('- "CT-e número [número específico]"');
    
    // Mostra estatísticas finais
    console.log(`\n📈 Estatísticas da sessão:`);
    console.log(`   • ID da sessão: ${agent.getSessionId()}`);
    console.log(`   • Estado do agente: ${agent.getState()}`);
    console.log(`   • Taxa de sucesso: ${agent.successRate.toFixed(1)}%`);
    console.log(`   • Histórico: ${agent.getHistoryLength()} mensagens`);

    await agent.shutdown();
    
  } catch (error) {
    console.error('❌ Erro ao executar o agente MIT Tracking:', error instanceof Error ? error.message : error);
    console.error('📋 Detalhes do erro:', error instanceof Error ? error.stack : 'Erro desconhecido');
    
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