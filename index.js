import { Crew, Task } from 'crewai-js';
import { ConversationalAgent } from './agents/conversationalAgent.js';
import dotenv from 'dotenv';

// Carrega variáveis de ambiente
dotenv.config();

async function main() {
  try {
    console.log('🚀 Iniciando MIT Tracking - Agente Conversacional de Logística...\n');

    // Instancia o agente conversacional especializado em logística
    const conversationalAgent = new ConversationalAgent();
    const agent = conversationalAgent.getAgent();

    console.log('✅ Agente MIT Tracking inicializado com sucesso!');
    console.log('🎯 Especialização: Consultas de CT-e, rastreamento de containers e logística\n');

    // Cria uma tarefa de demonstração focada em logística
    const logisticsTask = new Task({
      description: `Como assistente especializado da plataforma MIT Tracking, responda a seguinte consulta logística:
                    
                    "Preciso consultar o status do meu CT-e número 351234567890123456789012345678901234. 
                     Onde posso encontrar informações sobre esta carga e qual o ETA previsto?"
                    
                    Forneça uma resposta profissional e técnica, explicando:
                    1. Como consultar CT-e no sistema MIT Tracking
                    2. Tipos de informações disponíveis 
                    3. Como interpretar status de carga
                    4. Processo para obter ETA/ETD atualizados`,
      agent: agent,
      expectedOutput: 'Resposta técnica e detalhada sobre consulta de CT-e e rastreamento logístico'
    });

    // Cria o crew com o agente
    const crew = new Crew({
      name: 'MIT Tracking Logistics Crew',
      agents: [agent],
      tasks: [logisticsTask],
      verbose: true
    });

    console.log('📋 Executando consulta de demonstração sobre CT-e...\n');

    // Executa a tarefa
    const result = await crew.kickoff();

    console.log('\n🎯 Resposta do Assistente MIT Tracking:');
    console.log('=' * 50);
    console.log(result);
    console.log('=' * 50);

    console.log('\n✅ Demonstração concluída com sucesso!');
    console.log('🔄 O agente está pronto para consultas de CT-e, BL, containers e logística.');
    
  } catch (error) {
    console.error('❌ Erro ao executar o agente MIT Tracking:', error.message);
    console.error('📋 Detalhes do erro:', error.stack);
    
    // Verifica se é erro de conexão com Ollama
    if (error.message.includes('ECONNREFUSED') || error.message.includes('fetch')) {
      console.log('\n🔧 Possíveis soluções:');
      console.log('1. Verifique se o Ollama está rodando: ollama serve');
      console.log('2. Confirme se o modelo mistral está instalado: ollama pull mistral');
      console.log('3. Verifique se o Docker consegue acessar host.docker.internal:11434');
    }
    
    process.exit(1);
  }
}

// Executa o programa principal
main();